from pathlib import Path


class MarkdownMemoryRepository:

    def __init__(
        self,
        base_path: str = "/opt/MyAI/data/memory"
    ):
        self.base_path = Path(base_path)

        self.base_path.mkdir(
            parents=True,
            exist_ok=True
        )

    def read(
        self,
        file_name: str
    ):

        file_path = self.base_path / file_name

        if not file_path.exists():
            return ""

        return file_path.read_text(
            encoding="utf-8"
        )

    def write(
        self,
        file_name: str,
        content: str
    ):

        file_path = self.base_path / file_name

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return file_path

    def exists(
        self,
        file_name: str
    ):

        return (
            self.base_path / file_name
        ).exists()
