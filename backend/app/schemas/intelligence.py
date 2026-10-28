
from pydantic import BaseModel, Field


class IntelligenceQuery(BaseModel):
    question: str = Field(
        min_length=5,
        max_length=1000,
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=10,
    )
    demo_mode: bool = Field(
        default=False,
        description=(
            "Use fictional demo placement records for testing. "
            "Demo results must never be presented as real outcomes."
        ),
    )
