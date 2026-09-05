import time
from typing import Any


class PerformanceTracker:
    def __init__(self):
        self._steps: list[dict[str, Any]] = []

    def start(self, step_name: str, metadata: dict[str, Any] | None = None):
        started_at = time.perf_counter()
        step = {
            "name": step_name,
            "start": started_at,
            "end": None,
            "elapsed": None,
            "metadata": metadata or {},
        }
        self._steps.append(step)
        print(f"[STEP START] {step_name} metadata={metadata or {}}")
        return started_at

    def finish(self, step_name: str, started_at: float | None = None, metadata: dict[str, Any] | None = None):
        end_at = time.perf_counter()

        if started_at is None:
            for step in reversed(self._steps):
                if step["name"] == step_name and step["end"] is None:
                    started_at = step["start"]
                    break

        if started_at is None:
            started_at = end_at

        for step in reversed(self._steps):
            if step["name"] == step_name and step["end"] is None:
                step["end"] = end_at
                step["elapsed"] = round(end_at - started_at, 4)
                if metadata:
                    step["metadata"].update(metadata)
                print(f"[STEP END] {step_name} elapsed={step['elapsed']}s metadata={step['metadata']}")
                return step["elapsed"]

        elapsed = round(end_at - started_at, 4)
        step = {
            "name": step_name,
            "start": started_at,
            "end": end_at,
            "elapsed": elapsed,
            "metadata": metadata or {},
        }
        self._steps.append(step)
        print(f"[STEP END] {step_name} elapsed={elapsed}s metadata={step['metadata']}")
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
            print(f"[{name}] {elapsed} metadata={metadata}")
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
            print(f"[{step['name']}] {elapsed} metadata={step['metadata']}")
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
