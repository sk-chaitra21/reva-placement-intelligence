from datetime import date

from pydantic import BaseModel, Field


class PlacementDriveCreate(BaseModel):
    company_id: int
    academic_year: str = Field(min_length=4, max_length=20)
    drive_date: date | None = None
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None