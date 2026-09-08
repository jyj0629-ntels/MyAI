class ResponseSummaryService:

    @staticmethod
    def _is_important_line(line: str) -> bool:
        text = line.strip()
        if not text:
            return False

        lowered = text.lower()
        if len(text) < 18:
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
        )

        if any(marker in lowered for marker in key_markers):
            return True

        if any(ch.isdigit() for ch in text):
            return True

        return False

    def summarize(
        self,
        answer: str
    ):

        if not answer:
            return ""

        answer = answer.strip()

        selected = []
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
            if self._is_important_line(line):
                selected.append(line)

        if not selected:
            cleaned = []
            for raw_line in answer.splitlines():
                line = raw_line.strip()
                if line and len(line) >= 18 and not line.startswith("#"):
                    cleaned.append(line)
            selected = cleaned[:6]

        summary = "\n".join(selected[:8])
        max_length = 1200
        if len(summary) > max_length:
            summary = summary[:max_length].rsplit("\n", 1)[0].strip()
        return summary.strip()
