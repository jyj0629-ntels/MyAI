from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider
from app.schemas.brain_result import BrainResult
from app.core.config import settings
from app.services.performance_tracker import PerformanceTracker

import json
import re


class LocalBrainLLMService:

    @staticmethod
    def should_use_fast_path(question) -> bool:
        if not settings.LOCAL_LLM_FAST_PATH_ENABLED:
            return False

        if question is None:
            return False

        text = str(question).strip()
        if not text:
            return True

        normalized = text.lower()

        if len(text) <= 32:
            return True

        if len(text) <= settings.LOCAL_LLM_FAST_PATH_MAX_CHARS and "?" in text:
            return True

        simple_patterns = (
            "오늘",
            "지금",
            "어때",
            "뭐야",
            "뭐",
            "추천",
            "예상",
            "얼마",
            "언제",
            "누구",
            "어디",
            "날씨",
            "상태",
            "비교",
            "간단",
            "요약",
        )

        if any(pattern in normalized for pattern in simple_patterns):
            return True

        return False

    def build_fast_path_result(
        self,
        question,
        user_profile,
        project_context
    ) -> BrainResult:
        provider_name = (
            settings.PRIMARY_PROVIDER
            or settings.LOCAL_LLM_PROVIDER
            or "gemini"
        )

        return BrainResult(
            task_type="GENERAL",
            role="assistant",
            provider=provider_name,
            reason="fast_path_simple_question",
            prompt=question
        )

    @staticmethod
    def get_provider_specialty(provider_name: str) -> str:
        provider_name = (provider_name or "").strip().lower()
        specialties = {
            "gemini": "당신은 전략적 분석, 긴 맥락 이해, 질문의 본질을 파악하고 종합적인 비교를 잘하는 역할을 수행합니다.",
            "groq": "당신은 빠른 응답과 실용적 요약, 구조화된 결론 작성에 강합니다.",
            "openai": "당신은 명확하고 정교한 답변, 문서형 설명, 사용자 맞춤형 판단을 잘합니다.",
            "deepseek": "당신은 실무적이고 간결한 결론과 우선순위 정렬에 강합니다.",
            "ollama": "당신은 로컬 추론과 장기 사용자 맥락을 반영해 맞춤형 요약을 제공합니다.",
        }
        return specialties.get(provider_name, "당신은 사용자의 질문을 분석해 가장 정확하고 개인화된 결론을 전달하는 AI입니다.")

    @classmethod
    def build_provider_prompt(
        cls,
        question: str,
        user_profile: str,
        project_context,
        provider_name: str,
        task_type: str = "GENERAL",
        response_format: str | None = None
    ) -> str:
        profile_block = user_profile or "없음"
        project_block = str(project_context or "없음")
        provider_role = cls.get_provider_specialty(provider_name)

        provider_style = {
            "gemini": "전략적 분석, 장기 맥락 이해, 사용자 목적과 전체 그림을 종합해 답변한다. 과도한 세부 추론보다 구조적 판단을 우선한다.",
            "groq": "응답은 간결하고 실용적이며, 표/목록/우선순위 중심으로 정리한다. 불필요한 장문과 난잡한 표는 피하고 핵심만 깔끔하게 요약한다.",
            "openai": "정확한 문장 구조, 사용자 중심 설명, 문서형 서술을 우선한다. 충분한 근거와 제안사항을 포함하되 과장 없이 답한다.",
            "deepseek": "추론은 최소화하고 사실 근거를 우선한다. 출처를 명시하고, 불확실한 주장에는 반드시 근거와 한계를 제시한다. 링크/출처 3개 이상을 포함한다.",
            "ollama": "사용자의 과거 선호와 현재 맥락을 반영해 맞춤형 조언을 제공한다. 최종 답변은 실무적으로 바로 실행 가능한 형태로 구성한다.",
        }.get((provider_name or "").strip().lower(), "사용자의 목적에 맞춰 실질적이고 구체적인 답변을 제공한다.")

        response_instruction = response_format or """
- 핵심 결론
- 이유와 근거
- 사용자 맞춤 추천
- 잠재 리스크 또는 주의점
- 다음 행동 제안
"""

        return f"""
[역할]
{provider_role}

[공급자별 특성]
{provider_style}

[업무 유형]
{task_type}

[사용자 질문]
{question}

[사용자 성향 및 선호]
{profile_block}

[프로젝트 및 맥락]
{project_block}

[중요 규칙]
1. 질문을 그대로 반복하지 말고, 사용자 정보와 DB 기억을 반영해 재구성하라.
2. 중복된 내용은 제거하고 가장 중요한 사실만 남기도록 답변하라.
3. 사용자 선호와 프로젝트 맥락을 반영한 맞춤형 결론을 제시하라.
4. 가능하면 근거, 우선순위, 리스크, 다음 행동을 포함하라.
5. 답변은 사실 기반이며, 불확실한 부분은 명시적으로 표시하라.
6. 최종 응답은 제공된 출력 형식을 엄격히 준수하라.

[출력 형식]
{response_instruction}
"""

    def build_request(
        self,
        question,
        user_profile,
        project_context
    ):

        return AIRequest(
            question=f"""
사용자 질문:
{question}

사용자_성향:
{user_profile or '없음'}

프로젝트_정보:
{project_context or '없음'}

당신은 MyAI Brain이다. 사용자 질문을 분석해 다음 JSON만 반환하라.
{{
  "task_type":"",
  "role":"",
  "provider":"",
  "reason":"",
  "prompt":""
}}
"""
        )

    async def analyze(
        self,
        question,
        user_profile,
        project_context
    ):

        tracker = PerformanceTracker()
        tracker.start("local_llm_context_learning", {"question_length": len(str(question or ""))})

        if self.should_use_fast_path(question):
            print()
            print("# --------------------------------")
            print("# LOCAL BRAIN FAST PATH")
            print("# --------------------------------")
            print(f"question={str(question)[:200]}")
            print("reason=simple_question")
            print("# --------------------------------")
            print()
            return self.build_fast_path_result(
                question=question,
                user_profile=user_profile,
                project_context=project_context
            )

        if not settings.LOCAL_LLM_DEEP_ANALYSIS_ENABLED:
            print()
            print("# --------------------------------")
            print("# LOCAL BRAIN DEEP ANALYSIS DISABLED")
            print("# --------------------------------")
            print("reason=deep_analysis_disabled")
            print("# --------------------------------")
            print()
            result = self.build_fast_path_result(
                question=question,
                user_profile=user_profile,
                project_context=project_context
            )
            tracker.finish("local_llm_context_learning", metadata={"path": "disabled", "task_type": result.task_type})
            return result

        request = self.build_request(
            question=question,
            user_profile=user_profile,
            project_context=project_context
        )

        request.think = True

        print()
        print("# --------------------------------")
        print("# LOCAL BRAIN INPUT")
        print("# --------------------------------")
        print(f"question={question[:200]}")
        print(f"user_profile={str(user_profile)[:300]}")
        print(f"project_context={str(project_context)[:300]}")
        print("# --------------------------------")
        print()

        tracker.start("local_llm_provider_call", {"provider": "ollama"})
        response = await (
            OllamaProvider().ask(
                request
            )
        )
        tracker.finish("local_llm_provider_call", metadata={"provider": "ollama", "success": bool(getattr(response, "success", False))})

        print()
        print("# --------------------------------")
        print("# LOCAL BRAIN RAW RESPONSE")
        print("# --------------------------------")
        print(response.answer)
        print("# --------------------------------")
        print()

        if not response.success:
            raise Exception(
                response.error
            )

        try:

            raw_response = (
                response.answer.strip()
            )

            clean_json = (
                raw_response
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            json_start = clean_json.find("{")
            json_end = clean_json.rfind("}")

            if (
                json_start == -1
                or json_end == -1
                or json_end <= json_start
            ):
                raise ValueError(
                    "JSON block not found"
                )

            json_text = clean_json[
                json_start:json_end + 1
            ]

            payload = json.loads(
                json_text
            )

            tracker.add_log("local_llm_decision_payload", payload)

            payload.setdefault(
                "task_type",
                "GENERAL"
            )

            payload.setdefault(
                "role",
                "assistant"
            )

            raw_provider = str(payload.get("provider", "")).strip()
            if not raw_provider or raw_provider.lower() in {"unknown", "none", "null"}:
                raw_provider = settings.PRIMARY_PROVIDER
            payload["provider"] = raw_provider

            payload.setdefault(
                "reason",
                ""
            )

            payload.setdefault(
                "prompt",
                question
            )

            print()
            print("# --------------------------------")
            print("# LOCAL BRAIN PARSED RESULT")
            print("# --------------------------------")
            print(payload)
            print("# --------------------------------")
            print()

            return BrainResult(
                task_type=payload["task_type"],
                role=payload["role"],
                provider=payload["provider"],
                reason=payload["reason"],
                prompt=payload["prompt"]
            )

        except Exception as e:

            print()
            print("# --------------------------------")
            print("# LOCAL BRAIN JSON ERROR")
            print("# --------------------------------")
            print(str(e))
            print("# --------------------------------")
            print()

            return BrainResult(
                task_type="GENERAL",
                role="assistant",
                provider="",
                reason="brain_parse_fail",
                prompt=question
            )
