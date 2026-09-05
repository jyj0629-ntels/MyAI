import asyncio

from app.core.config import settings

from app.ai.models.request import AIRequest

from app.ai.services.response_collector import ResponseCollector
from app.ai.services.consensus_engine import ConsensusEngine
from app.ai.services.local_consensus_service import LocalConsensusService
from app.ai.services.response_summary_service import ResponseSummaryService
from app.services.performance_tracker import PerformanceTracker

class MultiProviderOrchestrator:

    def __init__(
        self,
        registry
    ):
        self.registry = registry

    @staticmethod
    def normalize_text(value):
        if value is None:
            return ""
        text = str(value).lower()
        text = text.replace("\n", " ")
        text = text.replace("-", " ")
        text = text.replace("/", " ")
        text = text.replace(".", " ")
        text = text.replace(",", " ")
        text = text.replace("?", " ")
        text = text.replace("!", " ")
        text = " ".join(text.split())
        return text

    @classmethod
    def keyword_tokens(cls, value):
        text = cls.normalize_text(value)
        return [token for token in text.split() if len(token) > 1]

    @classmethod
    def semantic_similarity(cls, a, b):
        left = set(cls.keyword_tokens(a))
        right = set(cls.keyword_tokens(b))
        if not left and not right:
            return 1.0
        if not left or not right:
            return 0.0
        intersection = len(left & right)
        union = len(left | right)
        return round((intersection / union) if union else 0.0, 4)

    @classmethod
    def build_combined_summary(cls, responses):
        if not responses:
            return "공급자 응답이 없어 요약할 수 없습니다."

        sections = []
        for item in responses:
            provider = item.get("provider", "provider")
            summary = (item.get("summary") or item.get("answer") or "").strip()
            if summary:
                sections.append(f"[{provider}] {summary[:500]}")

        combined = "\n".join(sections)
        if len(combined) > 1800:
            combined = combined[:1800] + "..."
        return combined

    @classmethod
    def compare_responses(cls, responses):
        if not responses:
            return {
                "average_score": 0,
                "consensus_score": 0,
                "combined_summary": "공급자 응답이 없어 요약할 수 없습니다.",
                "common_claims": [],
                "conflicting_claims": [],
                "cluster_count": 0,
                "response_count": 0,
            }

        items = []
        for response in responses:
            summary = (response.get("summary") or response.get("answer") or "").strip()
            items.append({
                "provider": response.get("provider"),
                "summary": summary,
                "keywords": cls.keyword_tokens(summary),
            })

        groups = []
        used = set()
        for idx, item in enumerate(items):
            if idx in used:
                continue
            group = [idx]
            used.add(idx)
            for jdx in range(idx + 1, len(items)):
                if jdx in used:
                    continue
                similarity = cls.semantic_similarity(item["summary"], items[jdx]["summary"])
                if similarity >= 0.45:
                    group.append(jdx)
                    used.add(jdx)
            groups.append(group)

        grouped_claims = []
        for group in groups:
            providers = [items[index]["provider"] for index in group]
            joined_summary = " ".join(items[index]["summary"] for index in group if items[index]["summary"])
            grouped_claims.append({
                "providers": providers,
                "summary": joined_summary,
                "score": round((len(group) / len(items)) * 100, 2),
            })

        grouped_claims.sort(key=lambda item: item["score"], reverse=True)
        average_score = round(sum(item["score"] for item in grouped_claims) / len(grouped_claims), 2) if grouped_claims else 0
        combined_summary = cls.build_combined_summary(responses)

        return {
            "average_score": average_score,
            "consensus_score": round(average_score, 2),
            "combined_summary": combined_summary,
            "common_claims": [item["summary"] for item in grouped_claims[:3]],
            "conflicting_claims": [item["summary"] for item in grouped_claims[1:]],
            "cluster_count": len(groups),
            "response_count": len(responses),
            "groups": grouped_claims,
        }

    async def ask_all(
        self,
        request: AIRequest
    ):

        tracker = PerformanceTracker()
        tracker.start("provider_dispatch", {"question_length": len(str(request.question or ""))})

        providers = (
            self.registry.list()
        )

        excluded_providers = [
            provider.strip()
            for provider in
            settings.MULTI_PROVIDER_EXCLUDE.split(",")
            if provider.strip()
        ]

        tasks = []

        for provider_name in providers:

            provider = (
                self.registry.get(
                    provider_name
                )
            )

            print(
                f"[PROVIDER CHECK] "
                f"{provider_name}"
            )

            if provider_name in excluded_providers: 
                print(
                    f"[PROVIDER SKIPPED] "
                    f"{provider_name}"
                )

                continue

            print(
                f"[PARALLEL START] "
                f"{provider_name}"
            )

            provider_started_at = tracker.start(
                f"provider_call:{provider_name}",
                {"provider": provider_name, "question_length": len(str(request.question or ""))}
            )

            async def _ask_with_timing(provider_instance, provider_name_value, request_payload, started_at):
                try:
                    result = await provider_instance.ask(request_payload)
                    tracker.finish(
                        f"provider_call:{provider_name_value}",
                        started_at,
                        {"provider": provider_name_value, "status": "completed" if getattr(result, "success", False) else "failed"}
                    )
                    return result
                except Exception as exc:
                    tracker.finish(
                        f"provider_call:{provider_name_value}",
                        started_at,
                        {"provider": provider_name_value, "status": "error", "error": str(exc)}
                    )
                    raise

            tasks.append(
                _ask_with_timing(
                    provider,
                    provider_name,
                    request,
                    provider_started_at
                )
            )

        results = await (
            asyncio.gather(
                *tasks,
                return_exceptions=True
            )
        )

        responses = []

        for result in results:

            if isinstance(
                result,
                Exception
            ):

                print()
                print("# --------------------------------")
                print("# PROVIDER EXCEPTION")
                print("# --------------------------------")
                print(str(result))
                print("# --------------------------------")
                print()

                continue

            if not getattr(
                result,
                "success",
                True
            ):
                print()
                print("# --------------------------------")
                print("# PROVIDER FAILED")
                print("# --------------------------------")
                print(result.provider)
                print(result.error)
                print("# --------------------------------")
                print()

                continue

            responses.append(
                result
            )

        print()
        print("# --------------------------------")
        print("# PROVIDER RESPONSES")
        print("# --------------------------------")

        for response in responses:

            print()
            print(
                f"[{response.provider}]"
            )

            print(
                response.answer[:300]
            )

            print("# --------------------------------")
            print()

        tracker.start("public_response_summary")
        collector = (
            ResponseCollector()
        )

        collected = (
            collector.collect(
                responses
            )
        )
        tracker.finish("public_response_summary", metadata={"response_count": len(collected)})

        comparison = self.compare_responses(collected)
        tracker.add_log("provider_comparison_summary", comparison)

        selected = (
            {
                "mode": "multi",
                "response_count": len(collected),
                "comparison_score": comparison.get("consensus_score", 0)
            }
            if len(collected) >= 2
            else None
        )

        if len(collected) == 0:

            print()
            print("# --------------------------------")
            print("# NO PROVIDER RESPONSE")
            print("# --------------------------------")
            print("# --------------------------------")
            print()

            selected = None

        elif len(collected) == 1:

            print()
            print("# --------------------------------")
            print("# SINGLE PROVIDER MODE")
            print("# --------------------------------")
            print(
                collected[0]["provider"]
            )
            print("# --------------------------------")
            print()

            if settings.ALLOW_SINGLE_PROVIDER:

                selected = {
                    "mode": "single",
                    "response": collected[0]
                }

            else:

                selected = None

        print()
        print("# --------------------------------")
        print("# PROVIDER SUMMARY")
        print("# --------------------------------")
        print(
            f"consensus_threshold="
            f"{settings.CONSENSUS_THRESHOLD}"
        )
        print(
            f"selected="
            f"{selected}"
        )
        print(
            f"response_count="
            f"{len(collected)}"
        )

        print("# --------------------------------")
        print()

        print()
        print("# --------------------------------")
        print("# CONSENSUS RESULT")
        print("# --------------------------------")
        print("Handled by Local LLM Judge")
        print("# --------------------------------")
        print()

        judge_request = None

        if len(collected) >= 2 and settings.ENABLE_LOCAL_CONSENSUS:

            judge_request = (
                LocalConsensusService()
                .build_request(
                    request.question,
                    collected
                )
            )

        tracker.finish("provider_dispatch")
        tracker.add_log("provider_dispatch_summary", {
            "response_count": len(collected),
            "selected_mode": selected["mode"] if selected else "single_default",
            "judge_enabled": judge_request is not None
        })

        return {
            "responses": collected,
            "selected": selected,
            "judge_request": judge_request,
            "comparison": comparison,
            "joint_summary": comparison.get("combined_summary", "")
        }
