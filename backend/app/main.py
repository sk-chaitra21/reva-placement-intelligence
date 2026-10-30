from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import (
    auth,
    claim,
    company,
    eligibility,
    embeddings,
    experience,
    intelligence,
    placement_drive,
    selection_round,
    verification,
)

app = FastAPI(
    title="REVA Placement Intelligence",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://reva-placement-intelligence.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(
    auth.router,
    prefix="/api/v1",
)

app.include_router(
    company.router,
    prefix="/api/v1",
)

app.include_router(
    placement_drive.router,
    prefix="/api/v1",
)

app.include_router(
    experience.router,
    prefix="/api/v1",
)

app.include_router(
    claim.router,
    prefix="/api/v1",
)

app.include_router(
    eligibility.router,
    prefix="/api/v1",
)

app.include_router(
    selection_round.router,
    prefix="/api/v1",
)

app.include_router(
    intelligence.router,
    prefix="/api/v1",
)

app.include_router(
    embeddings.router,
    prefix="/api/v1",
)

app.include_router(
    verification.router,
    prefix="/api/v1",
)


@app.get("/")
async def root():
    return {
        "message": "REVA Placement Intelligence API is running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }