# Architecture Decisions

## ADR-001: Modular monolith

We will not split the system into microservices for the MVP. The project is being built by one developer and needs strong internal boundaries without distributed-system overhead.

## ADR-002: PostgreSQL + pgvector

PostgreSQL is the primary store for structured placement knowledge. pgvector will later provide semantic retrieval without introducing a separate vector database in the MVP.

## ADR-003: Backend owns truth

Eligibility, drive state, permissions, verification state, relationships, and transactions remain deterministic backend/database responsibilities.

## ADR-004: AI is an intelligence layer

LLMs are used for unstructured information extraction, semantic interpretation, and grounded synthesis—not as the source of truth.
