import re
import time
from typing import Any


class PerformanceTracker:
    def __init__(self):
        self._steps: list[dict[str, Any]] = []

    @staticmethod
    def normalize_step_name(step_name: str) -> str:
        value = str(step_name or "").strip()
        if not value:
            return "[STEP] unnamed_step"
        if value.startswith("[STEP"):
            return value

        match = re.match(r"^(\d+(?:\.\d+)*)\s*[:.-]?\s*(.*)$", value)
        if match:
            step_number, tail = match.groups()
            suffix = tail.strip()
            if suffix:
                return f"[STEP {step_number}] {suffix}"
            return f"[STEP {step_number}]"

        return f"[STEP] {value}"

    def start(self, step_name: str, metadata: dict[str, Any] | None = None):
        started_at = time.perf_counter()
        normalized_name = self.normalize_step_name(step_name)
        step = {
            "name": normalized_name,
            "start": started_at,
            "end": None,
            "elapsed": None,
            "metadata": metadata or {},
        }
        self._steps.append(step)
        print(f"[STEP START] {normalized_name} metadata={metadata or {}}")
        return started_at

    def finish(self, step_name: str, started_at: float | None = None, metadata: dict[str, Any] | None = None):
        end_at = time.perf_counter()
        normalized_name = self.normalize_step_name(step_name)

        if started_at is None:
            for step in reversed(self._steps):
                if step["name"] == normalized_name and step["end"] is None:
                    started_at = step["start"]
                    break

        if started_at is None:
            started_at = end_at

        for step in reversed(self._steps):
            if step["name"] == normalized_name and step["end"] is None:
                step["end"] = end_at
                step["elapsed"] = round(end_at - started_at, 4)
                if metadata:
                    step["metadata"].update(metadata)
                print(f"[STEP END] {normalized_name} elapsed={step['elapsed']}s metadata={step['metadata']}")
                return step["elapsed"]

        elapsed = round(end_at - started_at, 4)
        step = {
            "name": normalized_name,
            "start": started_at,
            "end": end_at,
            "elapsed": elapsed,
            "metadata": metadata or {},
        }
        self._steps.append(step)
        print(f"[STEP END] {normalized_name} elapsed={elapsed}s metadata={step['metadata']}")
        return elapsed

    def print_summary(self):
        print()
        print("# --------------------------------")
        print("# PERFORMANCE SUMMARY")
        print("# --------------------------------")
        for step in self._steps:
            name = step["name"]
            elapsed = step["elapsed"]
            if elapsed is None:
                elapsed = "incomplete"
            else:
                elapsed = f"{elapsed}s"
            metadata = step.get("metadata") or {}
            print(f"{name} {elapsed} metadata={metadata}")
        print("# --------------------------------")
        print()

    def final_report(self):
        report = self.as_dict()
        print()
        print("# --------------------------------")
        print("# FINAL PERFORMANCE REPORT")
        print("# --------------------------------")
        for step in report["steps"]:
            elapsed = step["elapsed"]
            if elapsed is None:
                elapsed = "incomplete"
            else:
                elapsed = f"{elapsed}s"
            print(f"{step['name']} {elapsed} metadata={step['metadata']}")
        print("# --------------------------------")
        print()
        return report

    def as_dict(self):
        return {
            "steps": [
                {
                    "name": step["name"],
                    "elapsed": step["elapsed"],
                    "metadata": step.get("metadata") or {},
                }
                for step in self._steps
            ]
        }

    def add_log(self, label: str, payload: Any):
        print(f"[TRACE] {label}: {payload}")
