class ClaimMatcher:

    def match(
        self,
        claim_sets
    ):

        frequency = {}

        total_sources = len(
            claim_sets
        )

        for claims in claim_sets:

            unique_claims = set()

            for claim in claims:

                normalized = (
                    claim.strip()
                    .lower()
                )

                unique_claims.add(
                    normalized
                )

            for claim in unique_claims:

                frequency[
                    claim
                ] = (
                    frequency.get(
                        claim,
                        0
                    ) + 1
                )

        result = []

        for claim, count in (
            frequency.items()
        ):

            score = round(
                (
                    count
                    / total_sources
                ) * 100,
                2
            )

            result.append(
                {
                    "claim": claim,
                    "count": count,
                    "score": score
                }
            )

        result.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return result
