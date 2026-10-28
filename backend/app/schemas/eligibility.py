from pydantic import BaseModel, Field


class EligibilityCriteriaCreate(BaseModel):
    placement_drive_id: int
    minimum_cgpa: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )
    eligible_branches: str | None = None
    graduation_year: str | None = None
    backlog_allowed: bool | None = None
    other_criteria: str | None = None


class EligibilityCriteriaResponse(EligibilityCriteriaCreate):
    id: int

    model_config = {
        "from_attributes": True,
    }