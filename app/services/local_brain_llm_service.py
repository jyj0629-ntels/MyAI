from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider
from app.schemas.brain_result import BrainResult
from app.core.config import settings

import json
import re


class LocalBrainLLMService:

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

        response = await (
            OllamaProvider().ask(
                request
            )
        )

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
