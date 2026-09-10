# Deployment Guide

This app is split into two deployable pieces:

- **Frontend** (React + Vite) → **Vercel**
- **Backend** (FastAPI + spaCy + sentence-transformers + FAISS) → **Render** (Docker)

The backend cannot run on Vercel: its ML dependencies (torch, spaCy,
faiss) bundle to several GB, far over Vercel's 250 MB function limit. Render
(or Railway / Fly.io) runs it as a normal long-lived container instead.

---

## 1. Deploy the backend to Render

The repo ships a `render.yaml` blueprint and `backend/Dockerfile`.

1. Push this repo to GitHub (see bottom of this file if not done yet).
2. Go to <https://dashboard.render.com> → **New +** → **Blueprint**.
3. Select your repo. Render reads `render.yaml` and provisions:
   - a Docker web service (`resume-ranker-api`)
   - a managed Postgres database (`resume-ranker-db`)
   - a 2 GB persistent disk mounted at `/data` (caches the embedding model
     and stores uploaded PDFs).
4. Click **Apply**. The first build takes a while — it installs CPU torch and
   downloads the spaCy model.
5. When it's live, note the service URL, e.g.
   `https://resume-ranker-api.onrender.com`.
6. Open `/api/health` on that URL to confirm it returns `{"status":"ok",...}`.

> **Plan note:** torch needs more than the 512 MB free tier. Use at least the
> **Starter** instance. If ranking is slow/killed, bump to Standard.

> **LLM note:** Ollama isn't reachable from Render, so `USE_LLM=false` is set
> in the blueprint. Ranking still works — it falls back to semantic + skill
> scoring and generates heuristic reasoning. To use an LLM, point
> `OLLAMA_BASE_URL` at a reachable Ollama host and set `USE_LLM=true`.

You'll set `CORS_ORIGINS` after the frontend is deployed (step 3).

---

## 2. Deploy the frontend to Vercel

1. Go to <https://vercel.com> → **Add New** → **Project** → import your repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset auto-detects **Vite** (build `npm run build`, output `dist`).
4. Under **Environment Variables**, add:

   | Name           | Value                                        |
   | -------------- | -------------------------------------------- |
   | `VITE_API_URL` | `https://resume-ranker-api.onrender.com`     |

   (Use your actual Render URL, no trailing slash.)
5. Click **Deploy**. Note the resulting URL, e.g.
   `https://resume-ranking-system.vercel.app`.

---

## 3. Wire CORS back to the frontend

1. In Render → `resume-ranker-api` → **Environment**, set:

   ```
   CORS_ORIGINS = https://resume-ranking-system.vercel.app
   ```

   (Your actual Vercel URL. Add multiple comma-separated if needed.)
2. Save — Render redeploys automatically.

Now the frontend on Vercel talks to the backend on Render. Done.

---

## Local development (unchanged)

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env          # adjust DATABASE_URL etc.
python -m app.init_db
uvicorn app.main:app --reload

# frontend (separate terminal)
cd frontend
npm install
npm run dev                   # proxies /api -> http://localhost:8000
```

In dev, leave `VITE_API_URL` unset — the Vite proxy handles `/api`.

---

## Pushing to GitHub (if needed)

```bash
git add .
git commit -m "Add Vercel + Render deployment config"
git push origin main
```
