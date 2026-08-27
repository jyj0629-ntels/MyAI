class MemoryPromptService:

    def build(
        self,
        summary: str
    ):

        return f"""
You are a memory extraction engine.

Extract only durable memories.

Return JSON.

Memory Types:

- PREFERENCE
- GOAL
- PROJECT
- INTEREST

Conversation Summary:

{summary}

Output Example:

{{
  "memories": [
    {{
      "type": "PREFERENCE",
      "key": "answer_quality_priority",
      "content": "사용자는 정확도를 우선한다.",
      "importance": 0.9,
      "confidence": 0.9
    }}
  ]
}}
"""
