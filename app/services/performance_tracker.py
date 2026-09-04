import time
from typing import Any


class PerformanceTracker:
    def __init__(self):
        self._steps: list[dict[str, Any]] = []

    def start(self, step_name: str):
        started_at = time.perf_counter()
        self._steps.append({
            "name": step_name,
            "start": started_at,
            "end": None,
            "elapsed": None,
        })
        print(f"[STEP START] {step_name}")
        return started_at

    def finish(self, step_name: str, started_at: float | None = None):
        end_at = time.perf_counter()
        if started_at is None:
            started_at = end_at

        for step in reversed(self._steps):
            if step["name"] == step_name and step["end"] is None:
                step["end"] = end_at
                step["elapsed"] = round(end_at - started_at, 4)
                print(f"[STEP END] {step_name} elapsed={step['elapsed']}s")
                return step["elapsed"]

        elapsed = round(end_at - started_at, 4)
        print(f"[STEP END] {step_name} elapsed={elapsed}s")
        self._steps.append({
            "name": step_name,
            "start": started_at,
            "end": end_at,
            "elapsed": elapsed,
        })
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
            print(f"[{name}] {elapsed}")
        print("# --------------------------------")
        print()

    def add_log(self, label: str, payload: Any):
        print(f"[TRACE] {label}: {payload}")
