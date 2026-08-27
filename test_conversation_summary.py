from app.services.conversation_summary_service import \
    ConversationSummaryService


service = (
    ConversationSummaryService()
)

result = service.summarize(
    [
        "########################",
        "질문1",
        "------------------------",
        "답변1",
        "########################",
        "질문2",
        "------------------------",
        "답변2"
        "########################",
    ]
)

print(result)
