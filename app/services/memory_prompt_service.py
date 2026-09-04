class MemoryPromptService:

    def build(
        self,
        summary: str
    ):

        return f"""
You are a memory extraction engine.

Your job is to extract only durable user memories.

Rules:

1. Extract only long-term useful information.

2. Ignore temporary information.

3. Ignore one-time requests.

4. Ignore current conversation tasks.

5. Ignore implementation details.

6. Ignore generated AI responses.

7. Avoid duplicated memories.

8. Keep memory content concise.

Memory Types:

PREFERENCE
- User preferences
- Working style
- Communication style
- Answer style

GOAL
- Long-term goals
- Ongoing objectives

PROJECT
- Long-running projects
- Products being developed

INTEREST
- Persistent interests

Do NOT extract:

- Temporary questions
- Debug logs
- Error messages
- Current task requests
- One-time instructions
- AI generated conclusions

Conversation Summary:

{summary}

Return JSON only.

Output Example:

{{
  "memories": [
    {{
      "type": "PREFERENCE",
      "key": "implementation_first",
      "content": "사용자는 설명보다 구현 중심 진행을 선호한다.",
      "importance": 0.95,
      "confidence": 0.95
    }},
    {{
      "type": "PROJECT",
      "key": "myai_platform",
      "content": "사용자는 MyAI 플랫폼을 개발 중이다.",
      "importance": 0.95,
      "confidence": 0.95
    }}
  ]
}}
"""
