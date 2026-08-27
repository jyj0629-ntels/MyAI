from fastapi import APIRouter

from app.repositories.markdown_memory_repository import \
    MarkdownMemoryRepository

from app.services.markdown_memory_service import \
    MarkdownMemoryService


router = APIRouter(
    prefix="/markdown-memory",
    tags=["markdown-memory"]
)


@router.get("/{file_name}")
def get_markdown_memory(
    file_name: str
):

    service = MarkdownMemoryService(
        MarkdownMemoryRepository()
    )

    return {
        "content": service.load_memory(
            file_name
        )
    }


@router.post("/{file_name}")
def save_markdown_memory(
    file_name: str,
    content: str
):

    service = MarkdownMemoryService(
        MarkdownMemoryRepository()
    )

    service.save_memory(
        file_name,
        content
    )

    return {
        "success": True
    }
