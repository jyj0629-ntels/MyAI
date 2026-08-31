class ClaimExtractor:

    def extract(
        self,
        answer: str
    ):

        claims = []

        lines = (
            answer.splitlines()
        )

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if len(line) < 10:
                continue

            claims.append(
                line
            )

        return claims
