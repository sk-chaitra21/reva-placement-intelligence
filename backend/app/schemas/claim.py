from pydantic import BaseModel, Field


class ClaimCreate(BaseModel):
    experience_id: int
    claim_text: str = Field(min_length=5)
    claim_type: str = Field(min_length=2, max_length=50)
    evidence_text: str = Field(min_length=5)
 