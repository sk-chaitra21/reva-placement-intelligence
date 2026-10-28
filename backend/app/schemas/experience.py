from pydantic import BaseModel, Field


class ExperienceCreate(BaseModel):
    placement_drive_id: int

    experience_type: str = Field(
        min_length=2,
        max_length=50,
    )

    content: str = Field(
        min_length=10,
    )