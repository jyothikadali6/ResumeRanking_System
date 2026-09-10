# AI Resume Ranker — backend image (FastAPI + ML stack)
# Uses the CPU-only PyTorch wheels so the image stays as small as possible
# while still supporting sentence-transformers / spaCy / faiss.
FROM python:3.12-slim

# System deps: build tools for some wheels, curl for healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Cache HF / sentence-transformers models on the persistent disk at runtime.
    HF_HOME=/data/hf \
    SENTENCE_TRANSFORMERS_HOME=/data/hf

WORKDIR /app

# Install CPU-only torch first (much smaller than the default CUDA build),
# then the rest of the requirements.
COPY requirements.txt ./
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch \
    && pip install -r requirements.txt \
    && python -m spacy download en_core_web_sm

# App source
COPY app ./app

# Render/Railway/Fly inject $PORT. Default to 8000 for local runs.
ENV PORT=8000
EXPOSE 8000

# Create tables (idempotent) then start the server.
CMD ["sh", "-c", "python -m app.init_db && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
