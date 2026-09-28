"""DPI(Data-loss / forbidden-term) 재작성 서비스.

demo_dpi 기능의 핵심. 사용자가 입력한 질문을 우선 로컬 LLM(Ollama)에게 전달하여,
DB에 수동 등록된 금지어/금지 문장(사내 보안 단어/문장)이 포함된 경우
- 문맥과 핵심 의미는 그대로 유지하되
- 금지 문자/단어가 그대로 노출되지 않도록 유사 표현으로 재작성한
Prompt를 생성한다. 이 재작성된 Prompt가 Public AI들에게 전송된다.

기존 MyAI의 "선호도 기반 프롬프트 생성"과 달리, 선호도 DB는 전혀 읽지 않고
오직 금지어 DB만 읽어 재작성한다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider
from app.core.config import settings


@dataclass
class DpiRewriteResult:
    original_question: str
    rewritten_prompt: str
    detected_terms: list[dict] = field(default_factory=list)
    rewrite_applied: bool = False
    used_llm: bool = False
    fallback_used: bool = False
    still_contains_forbidden: bool = False
    note: str = ""


class DpiRewriteService:
    """금지어 DB를 읽어 Ollama로 사용자 입력을 재작성한다."""

    def __init__(self, forbidden_terms: list | None = None):
        # forbidden_terms: ForbiddenTerm ORM 객체 리스트
        self.forbidden_terms = forbidden_terms or []

    # ------------------------------------------------------------------
    # 금지어 탐지 (LLM 호출 전 1차 필터: 실제 포함된 금지어만 재작성 대상으로)
    # ------------------------------------------------------------------
    def detect_terms(self, question: str) -> list[dict]:
        text = question or ""
        lowered = text.lower()
        detected: list[dict] = []

        for item in self.forbidden_terms:
            term = (getattr(item, "term", "") or "").strip()
            if not term:
                continue

            if term.lower() in lowered:
                detected.append(
                    {
                        "id": getattr(item, "id", None),
                        "term": term,
                        "term_type": getattr(item, "term_type", "WORD"),
                        "replacement_hint": getattr(item, "replacement_hint", None),
                        "category": getattr(item, "category", None),
                    }
                )

        return detected

    # ------------------------------------------------------------------
    # 재작성 프롬프트(Ollama 지시문) 생성
    # ------------------------------------------------------------------
    def _build_rewrite_instruction(self, question: str, detected: list[dict]) -> str:
        forbidden_lines = []
        for idx, item in enumerate(detected, start=1):
            hint = item.get("replacement_hint")
            hint_text = f" (권장 대체 방향: {hint})" if hint else ""
            forbidden_lines.append(f"{idx}. \"{item['term']}\"{hint_text}")

        forbidden_block = "\n".join(forbidden_lines) if forbidden_lines else "(없음)"

        instruction = f"""너는 사내 보안 정책을 준수하도록 사용자 질문을 다시 쓰는 편집기다.

[목표]
아래 '사용자 질문'을 외부 Public AI에게 전달할 수 있도록 다시 작성하라.
질문의 핵심 의도, 문맥, 요청 내용은 반드시 동일하게 유지해야 한다.
단, 아래 '금지어 목록'에 있는 단어/문장은 그대로 노출되면 안 된다.
금지어를 의미가 통하는 일반적인 유사 표현(일반 명사, 범용 용어)으로 자연스럽게 바꿔라.

[규칙]
- 금지어를 절대 그대로 쓰지 말 것. 약어, 오타 변형, 띄어쓰기 우회로도 노출하지 말 것.
- 핵심 질문 의도는 100% 보존할 것. 정보 손실 없이 의미만 일반화할 것.
- 재작성된 문장은 그 자체로 자연스러운 하나의 질문/요청이어야 한다.
- 설명, 주석, 따옴표, 머리말 없이 '재작성된 질문 본문'만 출력하라.
- 금지어가 실제로 없다면 원문을 의미 그대로 자연스럽게 다듬어 출력하라.

[금지어 목록]
{forbidden_block}

[사용자 질문]
{question}

[재작성된 질문]
"""
        return instruction

    # ------------------------------------------------------------------
    # LLM 응답 후처리
    # ------------------------------------------------------------------
    @staticmethod
    def _clean_llm_output(text: str) -> str:
        if not text:
            return ""

        cleaned = text.strip()

        # <think> ... </think> 블록 제거 (qwen 계열 reasoning)
        cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.S | re.I).strip()

        # 흔한 머리말 제거
        cleaned = re.sub(r"^(재작성된?\s*(질문|프롬프트)\s*[:：]?\s*)", "", cleaned, flags=re.I).strip()

        # 감싸는 따옴표 제거
        if len(cleaned) >= 2 and cleaned[0] in "\"'“”" and cleaned[-1] in "\"'“”":
            cleaned = cleaned[1:-1].strip()

        return cleaned

    def _still_contains_forbidden(self, text: str, detected: list[dict]) -> bool:
        lowered = (text or "").lower()
        return any(item["term"].lower() in lowered for item in detected)

    # ------------------------------------------------------------------
    # 메인 진입점
    # ------------------------------------------------------------------
    async def rewrite(self, question: str) -> DpiRewriteResult:
        question = (question or "").strip()

        detected = self.detect_terms(question)

        # 금지어가 하나도 없으면 LLM 재작성 없이 원문 그대로 사용 (비용/지연 절감)
        if not detected:
            return DpiRewriteResult(
                original_question=question,
                rewritten_prompt=question,
                detected_terms=[],
                rewrite_applied=False,
                used_llm=False,
                note="금지어가 감지되지 않아 원문을 그대로 사용합니다.",
            )

        instruction = self._build_rewrite_instruction(question, detected)

        request = AIRequest(
            question=instruction,
            prompt=instruction,
            provider=(settings.LOCAL_LLM_PROVIDER or "ollama"),
        )
        request.think = False
        request.max_tokens = settings.OLLAMA_NUM_PREDICT

        rewritten = ""
        used_llm = False
        note = ""

        try:
            response = await OllamaProvider().ask(request)
            used_llm = True

            if getattr(response, "success", False):
                rewritten = self._clean_llm_output(getattr(response, "answer", "") or "")
            else:
                note = f"로컬 LLM 재작성 실패: {getattr(response, 'error', 'unknown')}"
        except Exception as exc:  # noqa: BLE001
            note = f"로컬 LLM 호출 예외: {exc}"

        # LLM 결과가 비었거나, 여전히 금지어가 남아 있으면 규칙 기반으로 마스킹 대체
        fallback_used = False
        if not rewritten or self._still_contains_forbidden(rewritten, detected):
            rewritten = self._fallback_mask(question, detected)
            fallback_used = True
            if not note:
                note = "로컬 LLM 재작성 결과가 불완전하여 규칙 기반 대체를 적용했습니다."

        # 최종 안전 점검: 규칙 기반 대체 후에도 금지어가 그대로 남아 있는지 확인.
        # (LLM 이 잡아야 할 우회 표현은 규칙 기반으로는 못 잡을 수 있으므로 플래그로 노출)
        still_forbidden = self._still_contains_forbidden(rewritten, detected)
        if still_forbidden:
            note = (
                (note + " " if note else "")
                + "경고: 재작성 후에도 금지어가 남아 있을 수 있습니다. 전송 전 확인이 필요합니다."
            )

        return DpiRewriteResult(
            original_question=question,
            rewritten_prompt=rewritten,
            detected_terms=detected,
            rewrite_applied=True,
            used_llm=used_llm,
            fallback_used=fallback_used,
            still_contains_forbidden=still_forbidden,
            note=note or "로컬 LLM이 금지어를 유사 표현으로 재작성했습니다.",
        )

    # ------------------------------------------------------------------
    # LLM 실패 시 최소 안전장치: 금지어를 대체 힌트/일반 표현으로 치환
    # ------------------------------------------------------------------
    @staticmethod
    def _fallback_mask(question: str, detected: list[dict]) -> str:
        result = question
        for item in detected:
            term = item["term"]
            replacement = item.get("replacement_hint")
            if not replacement:
                term_type = (item.get("term_type") or "WORD").upper()
                replacement = "해당 내용" if term_type == "SENTENCE" else "관련 항목"
            # 대소문자 무시 치환
            result = re.sub(re.escape(term), replacement, result, flags=re.I)
        return result.strip()
