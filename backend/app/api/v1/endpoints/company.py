from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_reviewer
from app.db.session import get_db
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyCreate

router = APIRouter(
    prefix="/companies",
    tags=["companies"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    request: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    reviewer: User = Depends(require_reviewer),
):
    result = await db.execute(
        select(Company).where(
            Company.name == request.name
        )
    )

    existing_company = result.scalar_one_or_none()

    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company already exists",
        )

    company = Company(
        name=request.name,
        industry=request.industry,
        description=request.description,
        website=request.website,
    )

    db.add(company)
    await db.commit()
    await db.refresh(company)

    return {
        "message": "Company created successfully",
        "company_id": company.id,
        "name": company.name,
    }
@router.get("/")
async def get_companies(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).order_by(Company.name)
    )

    companies = result.scalars().all()

    return [
        {
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "description": company.description,
            "website": company.website,
        }
        for company in companies
    ]
@router.get("/{company_id}")
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Company).where(
            Company.id == company_id
        )
    )

    company = result.scalar_one_or_none()

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return {
        "id": company.id,
        "name": company.name,
        "industry": company.industry,
        "description": company.description,
        "website": company.website,
    }