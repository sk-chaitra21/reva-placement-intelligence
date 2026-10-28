from pydantic import BaseModel, EmailStr, Field


class VerificationRequestCreate(BaseModel):
    verification_type: str = Field(
        min_length=6,
        max_length=30,
    )

    institutional_email: EmailStr | None = None

    evidence: str | None = Field(
        default=None,
        max_length=2000,
    )