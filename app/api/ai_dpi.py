"""demo_dpi 전용 AI 엔드포인트.

기존 /ai/chat 과의 차이점:
- 선호도(PREFERENCE) DB를 읽어 프롬프트를 개인화하지 않는다.
- 대신 금지어/금지문장 DB(forbidden_terms)를 읽어, 로컬 LLM(Ollama)이
  사용자 입력을 문맥 유지하며 금지어가 노출되지 않도록 재작성한다.
- 재작성된 프롬프트를 Public AI 들에게 전송하고, 응답을 저장한 뒤
  provider_responses(공급자별 응답)를 반환한다. 프론트는 이를 팝업으로 보여준다.
"""

import json

from fastapi import APIRouter, Body, Depends, HTTPException, Request

from sqlalchemy.orm import Session

from app.ai.models.request import AIRequest
from app.ai.models.response import AIResponse
from app.ai.services.registry import create_orchestrator
from app.ai.services.multi_provider_orchestrator import MultiProviderOrchestrator

from app.core.config import settings

from app.db.dependencies import get_db

from app.repositories.forbidden_term_repository import ForbiddenTermRepository
from app.repositories.memory_item_repository import MemoryItemRepository

from app.services.chat_orchestrator_service import ChatOrchestratorService
from app.services.dpi_rewrite_service import DpiRewriteService
from app.services.memory_item_service import MemoryItemService
from app.services.performance_tracker import PerformanceTracker

router = APIRouter(
    prefix="/ai_dpi",
    tags=["ai_dpi"],
)

orchestrator = create_orchestrator()


@router.post("/chat", response_model=AIResponse)
async def dpi_chat(
    request: AIRequest = Body(
        ...,
        description="사용자 질문. 금지어 재작성 후 Public AI로 전송됩니다.",
    ),
    http_request: Request = None,
    db: Session = Depends(get_db),
):
    tracker = PerformanceTracker()
    tracker.start("1. request_parse")

    # ------------------------------------------------------------------
    # 요청 파싱 (JSON / form 모두 지원)
    # ------------------------------------------------------------------
    try:
        if http_request is not None:
            content_type = http_request.headers.get("content-type", "").lower()
            if "application/json" not in content_type and (
                "application/x-www-form-urlencoded" in content_type
                or "multipart/form-data" in content_type
            ):
                form_data = await http_request.form()
                payload = {key: value for key, value in form_data.items()}
                request = AIRequest.from_payload(payload or {})

        if not request.question or not str(request.question).strip():
            raise ValueError("question is required and must be a non-empty string.")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"Invalid request body: {str(exc)}") from exc

    original_question = str(request.question).strip()
    tracker.finish("1. request_parse")

    # ------------------------------------------------------------------
    # 2. 금지어 DB 로드 + 로컬 LLM(Ollama) 재작성
    # ------------------------------------------------------------------
    tracker.start("2. dpi_rewrite")
    forbidden_terms = ForbiddenTermRepository(db).get_active()

    rewrite_result = await DpiRewriteService(forbidden_terms).rewrite(original_question)

    print()
    print("# --------------------------------")
    print("# DPI REWRITE")
    print("# --------------------------------")
    print(f"detected_terms = {[t['term'] for t in rewrite_result.detected_terms]}")
    print(f"rewrite_applied = {rewrite_result.rewrite_applied}")
    print(f"used_llm = {rewrite_result.used_llm}")
    print("# ORIGINAL --------------------------------")
    print(original_question)
    print("# REWRITTEN -------------------------------")
    print(rewrite_result.rewritten_prompt)
    print("# --------------------------------")
    print()

    tracker.finish(
        "2. dpi_rewrite",
        metadata={
            "detected_count": len(rewrite_result.detected_terms),
            "rewrite_applied": rewrite_result.rewrite_applied,
            "used_llm": rewrite_result.used_llm,
        },
    )

    # 재작성된 프롬프트를 Public AI 전송용으로 세팅.
    # NOTE: request.question 은 저장/표시에 쓰이므로 원문 유지, 전송 프롬프트만 교체.
    sanitized_prompt = rewrite_result.rewritten_prompt or original_question

    response_format_text = request.response_format_text
    if response_format_text:
        public_prompt = f"{sanitized_prompt}\n\n{response_format_text}"
    else:
        public_prompt = sanitized_prompt

    request.prompt = public_prompt
    request.system_prompt = public_prompt

    # ------------------------------------------------------------------
    # 3. Public AI 병렬 호출
    # ------------------------------------------------------------------
    tracker.start("3. provider_fanout")
    multi_result = await MultiProviderOrchestrator(orchestrator.registry).ask_all(request)
    tracker.finish(
        "3. provider_fanout",
        metadata={"response_count": len(multi_result.get("responses", []))},
    )

    comparison = multi_result.get("comparison")
    judge_request = multi_result.get("judge_request")
    judge_result = None

    # ------------------------------------------------------------------
    # 4. 로컬 LLM 합의(judge) - 기존 흐름과 동일하게 재사용
    # ------------------------------------------------------------------
    if judge_request and settings.ENABLE_LOCAL_CONSENSUS:
        tracker.start("4. consensus_judge")
        try:
            judge_response = await orchestrator.ask(
                provider_name=settings.LOCAL_CONSENSUS_PROVIDER,
                request=judge_request,
            )
            judge_answer = str(getattr(judge_response, "answer", "") or "").strip()
            if judge_answer:
                clean_json = (
                    judge_answer.replace("```json", "").replace("```", "").strip()
                )
                try:
                    judge_result = json.loads(clean_json)
                except Exception as exc:  # noqa: BLE001
                    print(f"[WARN] DPI judge JSON parse error: {exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] DPI consensus judge failed: {exc}")
        tracker.finish("4. consensus_judge")

    # 로컬 judge 의 consensus_score 를 comparison 에 반영 (기존 /ai/chat 과 동일 동작)
    if judge_result and comparison:
        try:
            llm_consensus_score = float(judge_result.get("consensus_score"))
        except (TypeError, ValueError):
            llm_consensus_score = None
        if llm_consensus_score is not None:
            comparison["consensus_score"] = llm_consensus_score
            comparison["average_score"] = llm_consensus_score

    # ------------------------------------------------------------------
    # 5. 응답 조립
    # ------------------------------------------------------------------
    responses = multi_result.get("responses", [])

    if not responses:
        raise HTTPException(
            status_code=502,
            detail="Public AI 응답을 받지 못했습니다. Provider 설정/API 키를 확인하세요.",
        )

    best = responses[0]
    response = AIResponse(
        provider=best.get("provider", "unknown"),
        model=best.get("model"),
        answer=best.get("answer") or "",
        success=True,
    )

    consensus_score = comparison.get("consensus_score", 0) if comparison else 0

    provider_responses = [
        {
            "provider": item["provider"],
            "model": item.get("model"),
            "answer": item.get("answer") or "",
            "summary": item.get("summary") or item.get("answer") or "",
            "score": consensus_score,
        }
        for item in responses
    ]
    response.provider_responses = provider_responses
    response.sources = [
        {
            "provider": item["provider"],
            "model": item.get("model"),
            "summary": item.get("summary") or item.get("answer") or "",
            "score": consensus_score,
        }
        for item in responses
    ]

    if comparison:
        response.comparison = comparison
        response.summary = MultiProviderOrchestrator.format_final_answer(
            comparison.get("combined_summary")
        )
        response.requires_confirmation = consensus_score < settings.CONSENSUS_THRESHOLD

    final_text = MultiProviderOrchestrator.build_human_readable_result(
        responses=responses,
        comparison=comparison or {},
        judge_result=judge_result,
        threshold=settings.CONSENSUS_THRESHOLD,
    )
    response.answer = MultiProviderOrchestrator.format_final_answer(
        final_text or response.answer or ""
    )

    # demo_dpi 부가 정보(프론트에서 재작성 배지 표시용)
    response.performance = {
        "dpi": {
            "original_question": original_question,
            "rewritten_prompt": rewrite_result.rewritten_prompt,
            "detected_terms": rewrite_result.detected_terms,
            "rewrite_applied": rewrite_result.rewrite_applied,
            "used_llm": rewrite_result.used_llm,
            "fallback_used": rewrite_result.fallback_used,
            "still_contains_forbidden": rewrite_result.still_contains_forbidden,
            "note": rewrite_result.note,
        }
    }

    # ------------------------------------------------------------------
    # 6. 저장 (chat_history + provider_responses markdown) - 기존 서비스 재사용
    # ------------------------------------------------------------------
    tracker.start("5. persist")
    memory_service = MemoryItemService(MemoryItemRepository(db))
    try:
        await ChatOrchestratorService().post_process(
            request=request,
            response=response,
            db=db,
            memory_service=memory_service,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] DPI post_process failed: {exc}")
    tracker.finish("5. persist")

    return response
