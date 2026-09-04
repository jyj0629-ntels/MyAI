from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider
from app.schemas.brain_result import BrainResult

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

사용자 성향:
{user_profile}

프로젝트 정보:
{project_context}

당신은 MyAI Brain 이다.

사용자 성향과 프로젝트 상태를 분석하라.

반드시 JSON만 반환하라.

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

            payload.setdefault(
                "provider",
                ""
            )

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
