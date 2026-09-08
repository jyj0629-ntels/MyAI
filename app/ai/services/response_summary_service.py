import asyncio
import re

from app.ai.models.request import AIRequest
from app.ai.providers.ollama_provider import OllamaProvider


class ResponseSummaryService:

    @staticmethod
    def _is_important_line(line: str) -> bool:
        text = line.strip()
        if not text:
            return False

        lowered = text.lower()
        if len(text) < 10:
            return False

        boilerplate = (
            "안녕하세요",
            "hello",
            "도와드릴게요",
            "어떤",
            "결과를",
            "제공",
            "설명드리면",
            "저는",
            "이것은",
            "이번",
            "다음과",
            "여기",
            "이런",
            "이유로",
            "할 수",
            "있습니다",
            "합니다",
            "그리고",
            "또한",
            "하지만",
            "정리하면",
            "요약하면",
            "기본",
        )

        if any(marker in lowered for marker in boilerplate):
            return False

        key_markers = (
            "결론",
            "추천",
            "권장",
            "우선",
            "강점",
            "약점",
            "장점",
            "단점",
            "핵심",
            "비교",
            "차이",
            "특징",
            "리스크",
            "문제",
            "원인",
            "해결",
            "솔루션",
            "이유",
            "근거",
            "점수",
            "평가",
            "예상",
            "특히",
            "효과",
            "영향",
            "비용",
            "가격",
            "품질",
            "안정성",
            "성과",
            "위험",
            "대안",
            "대비",
            "성능",
            "속도",
            "가성비",
            "품질",
            "신뢰성",
            "지원",
            "강하다",
            "좋다",
            "우수하다",
            "강한",
            "좋은",
        )

        if any(marker in lowered for marker in key_markers):
            return True

        if any(marker in lowered for marker in ("skt", "kt", "lg u+", "lg", "sk telecom", "네트워크", "요금제", "유선", "광랜", "브로드밴드")):
            return True

        if any(ch.isdigit() for ch in text):
            return True

        if len(text) >= 30 and any(ch.isalpha() for ch in text) and not any(marker in lowered for marker in ("장식", "잡담", "인사", "반갑", "도와드릴")):
            return True

        return False

    @staticmethod
    def _clean_sentence(sentence: str) -> str:
        text = str(sentence).strip()
        if not text:
            return ""
        text = re.sub(r"^[\-\*•\s]+", "", text)
        text = re.sub(r"^(안녕하세요|반갑습니다|hello|도와드릴게요|저는|여기|다음과|이번|이런|이것은)[^\n]*[\s:]*", "", text)
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
            if ResponseSummaryService._is_important_line(line):
                candidates.append(line)

        if not candidates:
            normalized = []
            for raw_line in re.split(r"(?<=[.!?])\s+", answer):
                sentence = ResponseSummaryService._clean_sentence(raw_line)
                if sentence and len(sentence) >= 18:
                    if not any(phrase in sentence.lower() for phrase in ("안녕하세요", "반갑습니다", "장식", "잡담", "도와드릴게요", "긴 설명", "의미 없는")):
                        normalized.append(sentence)
            candidates = normalized[:6]

        if not candidates:
            cleaned_answer = re.sub(r"^(안녕하세요|반갑습니다|hello|도와드릴게요)[^.!?]*[.!?]\s*", "", answer, flags=re.I)
            for raw_line in re.split(r"(?<=[.!?])\s+", cleaned_answer):
                sentence = ResponseSummaryService._clean_sentence(raw_line)
                if sentence and len(sentence) >= 18:
                    candidates.append(sentence)

        if len(candidates) > 6:
            candidates = candidates[:6]

        deduped = []
        seen = set()
        for item in candidates:
            key = item.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)

        summary = "\n".join(deduped[:8])
        if len(summary) > 1200:
            summary = summary[:1200].rsplit("\n", 1)[0].strip()
        return summary.strip()

    @staticmethod
    async def summarize_async(answer: str) -> str:
        if not answer:
            return ""

        cleaned = str(answer).strip()
        if not cleaned:
            return ""

        prompt = f"""
아래 응답은 한 공공 AI 제공자가 작성한 답변이다.
반드시 의미 단위로 핵심 사실만 추출해 요약하라.
- 인사, 반복, 잡담, 장황한 배경 설명은 제거
- 중요 주장, 근거, 숫자, 조건, 제한, 장점/단점, 추천/리스크만 남김
- 4~8줄 이내로 간결하게 작성
- 절대로 문장 끝에서 자르지 말고, 의미 있는 사실만 남겨라
- 출력은 한국어로만 작성하고, 불필요한 마크다운/헤더는 사용하지 않는다

응답:
{cleaned}
"""

        try:
            request = AIRequest(
                question=prompt,
                provider="ollama",
                think=True,
            )
            response = await OllamaProvider().ask(request)
            if getattr(response, "success", False) and getattr(response, "answer", "").strip():
                text = str(response.answer).strip()
                text = re.sub(r"^\s*[-*•]\s*", "", text, flags=re.M)
                text = re.sub(r"\n{3,}", "\n\n", text)
                return text.strip()[:1200]
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
