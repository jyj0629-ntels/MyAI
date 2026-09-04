from __future__ import annotations

from typing import Any


class WorkflowEngineService:
    """Minimal workflow engine used for step-by-step personal task execution."""

    def __init__(self):
        self.steps: list[dict[str, Any]] = []

    def register_step(self, name: str, handler: Any, **config: Any) -> None:
        self.steps.append({
            "name": name,
            "handler": handler,
            "config": config,
        })

    def execute(self, workflow_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
        result = {
            "workflow_name": workflow_name,
            "status": "success",
            "steps": [],
            "final_data": input_data,
        }

        for step in self.steps:
            step_name = step["name"]
            handler = step["handler"]
            step_result = handler(input_data)
            result["steps"].append({
                "name": step_name,
                "result": step_result,
            })
            input_data = step_result if isinstance(step_result, dict) else input_data

        return result
