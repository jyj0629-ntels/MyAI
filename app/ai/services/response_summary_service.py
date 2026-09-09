import asyncio
import re

from app.ai.models.request import AIRequest
from app.core.config import settings


class ResponseSummaryService:

    @staticmethod
    def _local_provider_instance():
        provider_name = str(settings.LOCAL_LLM_PROVIDER or "ollama").strip().lower()
        if provider_name == "ollama":
            from app.ai.providers.ollama_provider import OllamaProvider
            return OllamaProvider()

        module_name = f"app.ai.providers.{provider_name}_provider"
        try:
            module = __import__(module_name, fromlist=["*"])
            provider_cls = next(
                obj for obj in vars(module).values()
                if isinstance(obj, type) and obj.__name__.lower() == f"{provider_name}provider"
            )
            return provider_cls()
        except Exception as exc:
            raise ValueError(f"Unsupported local LLM provider: {provider_name}") from exc

    @staticmethod
    def _is_important_line(line: str) -> bool:
        text = line.strip()
        if not text:
            return False
        if len(text) < 12:
            return False
        if re.fullmatch(r"[\W_]+", text):
            return False
        if re.fullmatch(r"(?:[#>*\-•\s]+)", text):
            return False
        if text.count(" ") < 2:
            return False
        if any(ch.isalpha() for ch in text):
            return True
        return False

    @staticmethod
    def _clean_sentence(sentence: str) -> str:
        text = str(sentence).strip()
        if not text:
            return ""
        text = re.sub(r"^[\-\*•\s]+", "", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    @staticmethod
    def _fallback_summary(answer: str) -> str:
        if not answer:
            return ""

        answer = answer.strip()
        candidates = []

        for raw_line in answer.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("##"):
                continue
            if line.startswith("---"):
                continue
            if "------" in line:
                continue
            if line.startswith("[") and line.endswith("]"):
                continue

            line = ResponseSummaryService._clean_sentence(line)
            if not line:
                continue

            lowered = line.lower()
            if re.fullmatch(r"(?:안녕하세요|반갑습니다|hello|hi)[^가-힣a-z0-9]*", lowered):
                continue
            if "장식 문장" in lowered or "의미 없는" in lowered or "잡담" in lowered:
                continue
            if len(line) < 10:
                continue
            if re.fullmatch(r"[\W_]+", line):
                continue
            if ResponseSummaryService._is_important_line(line):
                candidates.append(line)

        if not candidates:
            for raw_line in re.split(r"(?<=[.!?])\s+", answer):
                sentence = ResponseSummaryService._clean_sentence(raw_line)
                if sentence and len(sentence) >= 18 and not re.fullmatch(r"[\W_]+", sentence):
                    lowered = sentence.lower()
                    if re.fullmatch(r"(?:안녕하세요|반갑습니다|hello|hi)[^가-힣a-z0-9]*", lowered):
                        continue
                    if "장식 문장" in lowered or "의미 없는" in lowered or "잡담" in lowered:
                        continue
                    candidates.append(sentence)

        deduped = []
        seen = set()
        for item in candidates:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)

        summary = "\n".join(deduped)
        return summary.strip()

    @staticmethod
    async def summarize_async(answer: str) -> str:
        if not answer:
            return ""

        cleaned = str(answer).strip()
        if not cleaned:
            return ""

        prompt = f"""
아래 응답은 한 AI 제공자가 작성한 답변이다.
이것은 현재 요청에 대한 응답 텍스트만이며, 과거 또는 다른 질문의 문맥을 사용하지 않는다.
반드시 현재 답변의 핵심 사실만 추출해 요약하라.
- 인사, 반복, 잡담, 장황한 배경 설명은 제거
- 중요 주장, 근거, 숫자, 조건, 제한, 장점/단점, 추천/리스크만 남김
- 전체 내용을 이해한 뒤, 의미 있는 사실만 남겨라
- 절대로 문장 끝에서 자르지 말고, 핵심 사실을 누락하지 않고 정리하라
- 출력은 한국어로만 작성하고, 불필요한 마크다운/헤더는 사용하지 않는다

응답:
{cleaned}
"""

        try:
            request = AIRequest(
                question=prompt,
                provider=settings.LOCAL_LLM_PROVIDER or "ollama",
                think=True,
            )
            response = await ResponseSummaryService._local_provider_instance().ask(request)
            if getattr(response, "success", False) and getattr(response, "answer", "").strip():
                text = str(response.answer).strip()
                text = re.sub(r"^\s*[-*•]\s*", "", text, flags=re.M)
                text = re.sub(r"\n{3,}", "\n\n", text)
                return text.strip()
        except Exception:
            pass

        return ResponseSummaryService._fallback_summary(cleaned)

    def summarize(self, answer: str):
        if not answer:
            return ""

        try:
            loop = asyncio.get_running_loop()
            if loop and loop.is_running():
                return self._fallback_summary(str(answer))
        except RuntimeError:
            try:
                return asyncio.run(self.summarize_async(answer))
            except RuntimeError:
                return self._fallback_summary(str(answer))

        return self._fallback_summary(str(answer))
