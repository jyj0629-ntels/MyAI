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
