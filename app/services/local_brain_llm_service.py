from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider
from app.schemas.brain_result import BrainResult

import json


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

        if not response.success:
            raise Exception(
                response.error
            )

        payload = json.loads(
            response.answer.strip()
        )

        return BrainResult(
            **payload
        )
