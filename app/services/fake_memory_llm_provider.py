class FakeMemoryLLMProvider:

    async def ask(
        self,
        prompt: str
    ):

        return """
{
  "memories": [
    {
      "type": "PREFERENCE",
      "key": "answer_quality_priority",
      "content": "사용자는 빠른 답변보다 정확한 답변을 선호한다.",
      "importance": 0.95,
      "confidence": 0.90
    }
  ]
}
"""
