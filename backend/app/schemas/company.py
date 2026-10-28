from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    industry: str | None = Field(default=None, max_length=100)
    description: str | None = None
    website: str | None = Field(default=None, max_length=255)