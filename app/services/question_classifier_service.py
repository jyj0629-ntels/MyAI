from __future__ import annotations

from typing import Any


class QuestionClassifierService:
    """Classify a user question into a theme and intent."""

    def __init__(self):
        self.keywords = {
            "finance": ["주식", "예금", "이자", "연말정산", "투자", "재테크"],
            "shopping": ["가격", "최저가", "쿠폰", "구매", "쇼핑", "최저"],
            "schedule": ["일정", "캘린더", "회의", "약속", "미팅"],
            "travel": ["여행", "출장", "비행기", "숙소", "일정"],
            "work": ["업무", "보고", "계획", "프로젝트", "검토"],
            "personal": ["나", "성향", "취향", "생활", "일기", "기분"],
        }

    def classify(self, question: str) -> dict[str, Any]:
        text = (question or "").strip()
        if not text:
            return {
                "theme": "general",
                "intent": "ask",
                "urgency": "normal",
                "complexity": "medium",
            }

        lower = text.lower()
        matched_theme = "general"

        for theme, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in lower or keyword in text:
                    matched_theme = theme
                    break
            if matched_theme != "general":
                break

        urgency = "normal"
        if any(word in lower for word in ["즉시", "오늘", "급함", "지금", "빨리"]):
            urgency = "high"

        complexity = "medium"
        if any(word in lower for word in ["비교", "분석", "검토", "전략", "설계", "종합"]):
            complexity = "high"

        intent = "ask"
        if any(word in lower for word in ["확인", "찾아", "검색", "비교", "정리", "계획"]):
            intent = "research"

        return {
            "theme": matched_theme,
            "intent": intent,
            "urgency": urgency,
            "complexity": complexity,
        }
