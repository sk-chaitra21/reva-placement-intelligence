from pydantic import BaseModel, Field


class ExtractedClaim(BaseModel):
    claim_text: str = Field(min_length=5)
    claim_type: str = Field(min_length=2, max_length=50)
    evidence_text: str = Field(min_length=5)


class ClaimExtractionResult(BaseModel):
    claims: list[ExtractedClaim]