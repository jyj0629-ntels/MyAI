from pydantic import BaseModel


class ConsensusResult(
    BaseModel
):

    consensus_score: int

    common_claims: list[str]

    conflicting_claims: list

    final_answer: str
