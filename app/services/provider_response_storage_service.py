from __future__ import annotations

import re
from pathlib import Path
from typing import Any


class ProviderResponseStorageService:
    def __init__(self, base_dir: str | Path | None = None):
        if base_dir is not None:
            self.base_dir = Path(base_dir)
        else:
            repo_root = Path(__file__).resolve().parents[2]
            self.base_dir = repo_root / "data" / "provider_responses"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _safe_provider_name(self, value: Any) -> str:
        name = str(value or "unknown").strip().lower()
        return re.sub(r"[^a-z0-9_-]+", "_", name) if name else "unknown"

    def format_markdown(self, conversation_id: int | str, provider_responses: list[dict[str, Any]]) -> str:
        lines: list[str] = []
        lines.append("# Public AI Response Log")
        lines.append("")
        lines.append(f"- conversation_id: {conversation_id}")
        lines.append(f"- total_responses: {len(provider_responses or [])}")
        lines.append("")

        for index, item in enumerate(provider_responses or [], start=1):
            provider = str(item.get("provider") or "unknown").strip() or "unknown"
            model = str(item.get("model") or item.get("provider") or "unknown").strip() or "unknown"
            answer = str(item.get("answer") or item.get("summary") or "").strip()
            lines.append(f"## {index}. {provider} ({model})")
            lines.append("")
            lines.append(f"**provider:** {provider}")
            lines.append(f"**model:** {model}")
            lines.append("")
            lines.append("```text")
            lines.append(answer if answer else "(empty response)")
            lines.append("```")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def write_markdown(self, conversation_id: int | str, provider_responses: list[dict[str, Any]]) -> Path:
        safe_name = self._safe_provider_name(conversation_id)
        suffix = abs(hash(f"{conversation_id}-{len(provider_responses or [])}-{id(provider_responses)}")) % 1000000
        file_name = f"conversation_{safe_name}_{suffix}.md"
        file_path = self.base_dir / file_name
        file_path.write_text(self.format_markdown(conversation_id, provider_responses), encoding="utf-8")
        return file_path

    def read_markdown(self, file_name: str) -> str:
        file_path = self.base_dir / file_name
        if not file_path.exists():
            return ""
        return file_path.read_text(encoding="utf-8")

    @staticmethod
    def parse_markdown_responses(markdown: str) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        blocks = re.split(r"^##\s*", markdown, flags=re.MULTILINE)
        for block in blocks[1:]:
            raw_lines = block.strip().splitlines()
            if not raw_lines:
                continue

            heading = raw_lines[0].strip()
            provider = "unknown"
            model = "unknown"
            if "(" in heading and heading.endswith(")"):
                base = heading.rsplit("(", 1)
                provider = base[0].strip().split(".", 1)[-1].strip()
                model = base[1][:-1].strip()
            else:
                provider = heading.split(".", 1)[-1].strip() if "." in heading else heading

            answer_lines: list[str] = []
            capture = False
            for line in raw_lines[1:]:
                if line.strip() == "```text":
                    capture = True
                    continue
                if line.strip() == "```":
                    capture = False
                    continue
                if capture:
                    answer_lines.append(line)

            result.append({
                "provider": provider,
                "model": model,
                "answer": "\n".join(answer_lines).strip() or "(empty response)"
            })

        return result
