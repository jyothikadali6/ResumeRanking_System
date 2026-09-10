# AI Resume Ranker

Rank resumes against a job description using semantic AI matching.

Upload N resume PDFs + a job description. The app extracts text, computes
semantic similarity, extracts matched/missing skills, and uses a local LLM
to produce a final ranking with human-readable reasoning.

Rank 1 = best match, Rank N = weakest match.

## Tech Stack

**Backend**
- FastAPI (REST API)
- PostgreSQL + SQLAlchemy (persistence)
- PyMuPDF (PDF text extraction)
- spaCy (text preprocessing + skill extraction)
- Sentence Transformers (embeddings)
- FAISS (vector similarity)
- Ollama + open-source LLM (reasoning & re-ranking)

**Frontend**
- React (Vite)
- Tailwind CSS

## Architecture

```
resume PDFs ──► PyMuPDF ──► raw text
job desc  ─────────────────► raw text
                               │
                    spaCy preprocessing + skill extraction
                               │
              Sentence Transformers embeddings (resume + JD)
                               │
                    FAISS cosine similarity score
                               │
        Ollama LLM re-ranking + reasoning (skills gap analysis)
                               │
                     Final ranked list (1..N) + scores
                               │
                        PostgreSQL persistence
                               │
                     React + Tailwind results table
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ running locally
- [Ollama](https://ollama.com) installed and running (`ollama serve`)
  - Pull a model: `ollama pull llama3.2`

## Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# configure DB + Ollama in .env (copy from .env.example)
cp .env.example .env

# create the database itself (one-time; init_db only creates tables, not the DB)
createdb resume_ranker

# create tables
python -m app.init_db

# run
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## How it works

1. Create a job (paste the job description).
2. Upload resume PDFs for that job.
3. Trigger ranking.
4. View the ranked table: rank, filename, score, matched/missing skills, reasoning.
