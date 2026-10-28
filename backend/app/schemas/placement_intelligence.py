from pydantic import BaseModel


class PlacementDriveSummary(BaseModel):
    id: int
    company_id: int
    academic_year: str
    drive_date: str | None
    title: str
    description: str | None


class EligibilitySummary(BaseModel):
    id: int
    placement_drive_id: int
    minimum_cgpa: float | None
    eligible_branches: str | None
    graduation_year: str | None
    backlog_allowed: bool | None
    other_criteria: str | None
class CompanySummary(BaseModel):
    id: int
    name: str
    industry: str | None
    description: str | None
    website: str | None

class SelectionRoundSummary(BaseModel):
    id: int
    placement_drive_id: int
    round_number: int
    round_type: str
    description: str | None


class VerifiedExperienceSummary(BaseModel):
    id: int
    contributor_type: str
    content: str
class VerifiedClaimSummary(BaseModel):
    id: int
    experience_id: int
    claim_text: str
    evidence_text: str | None
    claim_type: str
    verification_status: str
    contributor_type: str
    company: str
    academic_year: str
    placement_drive: str

class PlacementIntelligenceResponse(BaseModel):
    company: CompanySummary
    placement_drive: PlacementDriveSummary
    eligibility: EligibilitySummary | None
    selection_rounds: list[SelectionRoundSummary]
    verified_experiences: list[VerifiedExperienceSummary]
    verified_claims: list[VerifiedClaimSummary]