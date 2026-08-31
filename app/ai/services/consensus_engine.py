from app.core.config import settings

class ConsensusEngine:

    def calculate(
        self,
        grouped_answers
    ):

        total = 0

        for providers in grouped_answers.values():

            total += len(
                providers
            )

        results = []

        for answer, providers in (
            grouped_answers.items()
        ):

            score = (
                len(providers)
                / total
            ) * 100

            results.append(
                {
                    "answer": answer,
                    "providers": providers,
                    "score": round(
                        score,
                        2
                    )
                }
            )

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results

    def select(
        self,
        consensus_results,
        threshold=None
    ):

        threshold = (
            threshold
            or settings.CONSENSUS_THRESHOLD 
        )

        if not consensus_results:
            return None

        best = (
            consensus_results[0]
        )

        if (
            best["score"]
            >= threshold
        ):
            return best

        return None
