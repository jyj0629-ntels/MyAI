import asyncio
import re
import time

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

    @staticmethod
    def stopwords():
        return {
            "그리고", "하지만", "또한", "그래서", "그러므로", "이유", "문제", "정리", "결론", "대해",
            "대한", "같다", "다음", "이상", "이하", "무엇", "어떤", "하는", "합니다", "있다", "없다",
            "보다", "우리", "사용자", "질문", "답변", "것", "수", "중", "등", "때", "이", "그", "저",
        }

    @classmethod
    def summarize_key_points(cls, value):
        if value is None:
            return ""
        text = re.sub(r"```.*?```", " ", str(value), flags=re.S)
        text = text.replace("\n", " ")
        sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]
        if not sentences:
            return text.strip()

        selected = []
        for sentence in sentences:
            if len(sentence) < 20:
                continue
            if re.fullmatch(r"[\W_]+", sentence):
                continue
            selected.append(sentence)

        if not selected:
            selected = sentences[:3]

        summary = " ".join(selected[:3])
        return summary.strip()

    @classmethod
    def keyword_tokens(cls, value):
        text = cls.normalize_text(value)
        tokens = [token for token in text.split() if len(token) > 1 and token not in cls.stopwords()]
        return tokens

    @classmethod
    def semantic_similarity(cls, a, b):
        left_summary = cls.summarize_key_points(a)
        right_summary = cls.summarize_key_points(b)

        left = set(cls.keyword_tokens(left_summary))
        right = set(cls.keyword_tokens(right_summary))
        if not left and not right:
            return 1.0
        if not left or not right:
            return 0.0

        intersection = len(left & right)
        union = len(left | right)
        return round((intersection / union) if union else 0.0, 4)

    @classmethod
    def format_final_answer(cls, text):
        if not text:
            return ""

        cleaned = str(text).replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ").strip()
        cleaned = re.sub(r"\[(?:gemini|groq|openai|chatgpt|deepseek|meta|ollama|provider)\]\s*", "\n\n", cleaned, flags=re.I)
        cleaned = re.sub(r"\s*[-–—]\s*\*\*(핵심 요약|불확실성 명시|다음 행동|비교표|최종 추천|근거|결론|추천|리스크|주의점)\*\*", "\n\n**\\1**", cleaned)
        cleaned = re.sub(r"(?<!\n)\*\*(핵심 요약|불확실성 명시|다음 행동|비교표|최종 추천|근거|결론|추천|리스크|주의점)\*\*", "\n\n**\\1**", cleaned)
        cleaned = re.sub(r"(?<!\n)\|\s*구분\s*\|", "\n\n| 구분 |", cleaned)
        cleaned = re.sub(r"(?<=[.!?])\s+(?=(?:\*\*|[가-힣A-Z]))", "\n\n", cleaned)
        cleaned = re.sub(r"(?<=[가-힣])\s+(?=(?:[-•·]|\d+\.|\* ))", "\n", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r"[ ]{2,}", " ", cleaned)
        cleaned = cleaned.strip()
        return cleaned

    @staticmethod
    def build_human_readable_result(responses, comparison=None, judge_result=None, threshold=None):
        providers = []
        for item in responses or []:
            provider_name = str(item.get("provider") or "").strip()
            if provider_name and provider_name not in providers:
                providers.append(provider_name)

        if not providers:
            providers = ["비교 대상 없음"]

        score_value = 0.0
        if comparison and comparison.get("consensus_score") is not None:
            score_value = float(comparison.get("consensus_score", 0) or 0)
        elif judge_result and judge_result.get("consensus_score") is not None:
            score_value = float(judge_result.get("consensus_score", 0) or 0)

        baseline = float(threshold if threshold is not None else settings.CONSENSUS_THRESHOLD)
        summary_source = None
        if judge_result and judge_result.get("final_answer"):
            summary_source = judge_result.get("final_answer")
        elif comparison and comparison.get("combined_summary"):
            summary_source = comparison.get("combined_summary")
        elif responses:
            summary_source = "\n\n".join(str(item.get("summary") or item.get("answer") or "").strip() for item in responses if (item.get("summary") or item.get("answer")))

        summary_text = MultiProviderOrchestrator.format_final_answer(summary_source or "요약 결과를 생성할 수 없습니다.")
        provider_line = f"(1) 비교 대상 AI : {', '.join(providers)}"
        consensus_line = f"(2) Consensus : 기준 {int(baseline)}% / 현재 결과 : {score_value:.0f}%"
        summary_line = "(3) 최종 요약 결과."
        return f"{provider_line}\n{consensus_line}\n\n{summary_line}\n\n{summary_text}"

    @classmethod
    def build_combined_summary(cls, responses):
        if not responses:
            return "공급자 응답이 없어 요약할 수 없습니다."

        providers = []
        claims = []
        seen = set()

        for item in responses:
            provider_name = str(item.get("provider") or "").strip()
            if provider_name and provider_name not in providers:
                providers.append(provider_name)

            raw = (item.get("summary") or item.get("answer") or "").strip()
            if not raw:
                continue

            segments = re.split(r"(?<=[.!?])\s+", raw)
            for segment in segments:
                sentence = str(segment).strip()
                sentence = re.sub(r"^[\-\*•\s]+", "", sentence)
                sentence = sentence.strip()

                if not sentence or len(sentence) < 10:
                    continue
                if re.fullmatch(r"[\W_]+", sentence):
                    continue

                normalized = re.sub(r"\s+", " ", sentence)
                key = normalized.lower()
                if key in seen:
                    continue
                seen.add(key)
                claims.append(normalized)

        if not claims:
            fallback = [
                (item.get("summary") or item.get("answer") or "").strip()
                for item in responses
            ]
            fallback = [text for text in fallback if text]
            return cls.format_final_answer("\n\n".join(fallback))

        if not providers:
            providers = ["비교 대상"]

        summary_header = f"비교 대상: {', '.join(providers[:3])}"
        claim_lines = [f"- {claim}" for claim in claims]
        final_text = "\n\n".join([summary_header, *claim_lines])
        return cls.format_final_answer(final_text)

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
            raw_summary = (response.get("summary") or response.get("answer") or "").strip()
            summary = cls.summarize_key_points(raw_summary)
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
        combined_summary = cls.format_final_answer(cls.build_combined_summary(responses))

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
        tracker.start("4.1 provider_dispatch", {"question_length": len(str(request.question or ""))})

        providers = (
            self.registry.list()
        )

        if getattr(request, "selected_providers", None):
            selected_providers = [
                str(item).strip().lower()
                for item in request.selected_providers
                if str(item).strip()
            ]
            if selected_providers:
                providers = [
                    provider_name for provider_name in providers
                    if provider_name.lower() in selected_providers
                ]

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
                f"4.2 provider_call:{provider_name}",
                {"provider": provider_name, "question_length": len(str(request.question or ""))}
            )

            print()
            PerformanceTracker.print_section(
                "provider",
                f"PUBLIC PROVIDER PROMPT: {provider_name}",
                request.prompt or request.question
            )
            print()

            async def _ask_with_timing(provider_instance, provider_name_value, request_payload, started_at):
                call_started_at = time.perf_counter()
                try:
                    result = await provider_instance.ask(request_payload)
                    elapsed_ms = round((time.perf_counter() - call_started_at) * 1000.0, 2)
                    result.response_time_ms = getattr(result, "response_time_ms", None) or elapsed_ms
                    tracker.finish(
                        f"4.2 provider_call:{provider_name_value}",
                        started_at,
                        {"provider": provider_name_value, "status": "completed" if getattr(result, "success", False) else "failed", "response_time_ms": elapsed_ms}
                    )
                    return result
                except Exception as exc:
                    elapsed_ms = round((time.perf_counter() - call_started_at) * 1000.0, 2)
                    tracker.finish(
                        f"4.2 provider_call:{provider_name_value}",
                        started_at,
                        {"provider": provider_name_value, "status": "error", "error": str(exc), "response_time_ms": elapsed_ms}
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
        PerformanceTracker.print_section(
            "response",
            "PROVIDER RESPONSES",
            ""
        )

        for response in responses:

            print()
            print(
                f"[{response.provider}]"
            )
            print(response.answer)
            print()

        tracker.start("4.3 public_response_summary")
        collector = (
            ResponseCollector()
        )

        collected = await (
            collector.collect_async(
                responses
            )
        )
        tracker.finish("4.3 public_response_summary", metadata={"response_count": len(collected)})

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
        PerformanceTracker.print_section(
            "summary",
            "PROVIDER SUMMARY",
            f"consensus_threshold={settings.CONSENSUS_THRESHOLD}\nselected={selected}\nresponse_count={len(collected)}"
        )
        print()

        print()
        PerformanceTracker.print_section(
            "consensus",
            "CONSENSUS RESULT",
            "Handled by Local LLM Judge"
        )
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

        tracker.finish("4.1 provider_dispatch")
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
