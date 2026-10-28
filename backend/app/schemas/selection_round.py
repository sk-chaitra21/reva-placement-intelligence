from pydantic import BaseModel, Field


class SelectionRoundCreate(BaseModel):
    placement_drive_id: int
    round_number: int = Field(ge=1)
    round_type: str = Field(min_length=2, max_length=50)
    description: str | None = None


class SelectionRoundResponse(SelectionRoundCreate):
    id: int

    model_config = {
        "from_attributes": True,
    }