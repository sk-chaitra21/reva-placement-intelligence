# REVA Placement Intelligence — Architecture

## Architectural style

Modular monolith. One FastAPI application, one PostgreSQL database, clear internal boundaries.

## Current build order

1. Core backend and domain model
2. PostgreSQL + SQLAlchemy + Alembic
3. REST APIs
4. Authentication and RBAC
5. Experience ingestion and moderation
6. AI extraction
7. Embeddings + pgvector
8. Hybrid retrieval + RAG

## Core principle

AI proposes and synthesizes. Backend validates and controls state. Human moderation verifies submitted knowledge. PostgreSQL stores authoritative structured state.

## Domain flow

User → Experience → Claims → Verification → Knowledge → Retrieval → Evidence-grounded answer
