# REVA Placement Intelligence

An AI-powered placement intelligence platform designed to help students explore placement experiences and understand recruitment trends using verified evidence.

## Features

- FastAPI backend with REST APIs
- PostgreSQL database with SQLAlchemy and Alembic migrations
- AI-powered question answering using Gemini
- Retrieval-Augmented Generation (RAG) for evidence-grounded responses
- Demo mode that clearly identifies fictional test data
- Source-aware responses designed to avoid unsupported placement claims

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, Alembic  
**Database:** PostgreSQL  
**AI:** Google Gemini, embeddings, RAG  
**Frontend:** See the `frontend` directory for implementation details.

## Project Structure

- `backend/` — API, database models, migrations, and AI services
- `frontend/` — User interface
- `docs/` — Project documentation

## Local Setup

1. Clone this repository.
2. Configure the backend environment using the provided `.env.example`.
3. Create a PostgreSQL database and configure the database connection.
4. Install backend dependencies using the project's setup instructions.
5. Apply database migrations using Alembic.
6. Start the FastAPI server and run the frontend using its configured development commands.

## Data Integrity

Demo records are fictional test data and are distinguished from real placement evidence. The project is designed not to present demo records as verified real-world placement outcomes.

## Status

Development and deployment preparation in progress.
