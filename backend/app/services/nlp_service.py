"""spaCy-based text preprocessing and skill extraction.

Uses a curated skill dictionary matched with spaCy's PhraseMatcher so we get
reliable, case-insensitive multi-word skill detection (e.g. "machine learning",
"react native"). Also does lemmatised keyword extraction as a fallback signal.
"""
from __future__ import annotations

import functools

import spacy
from spacy.matcher import PhraseMatcher

from app.config import settings

# A pragmatic, extensible skills vocabulary. Extend freely for your domain.
SKILL_VOCAB: list[str] = [
    # languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql",
    # web / frontend
    "react", "react native", "next.js", "vue", "angular", "svelte", "redux",
    "html", "css", "tailwind", "tailwind css", "sass", "bootstrap",
    # backend / frameworks
    "node.js", "express", "fastapi", "flask", "django", "spring", "spring boot",
    ".net", "rails", "graphql", "rest", "grpc", "microservices",
    # data / ml
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "pytorch", "tensorflow", "keras", "scikit-learn",
    "pandas", "numpy", "spacy", "hugging face", "transformers",
    "sentence transformers", "llm", "ollama", "faiss", "vector database",
    "data analysis", "data science", "statistics", "etl", "spark", "hadoop",
    # databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite",
    "dynamodb", "cassandra", "snowflake", "bigquery",
    # cloud / devops
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "ansible", "jenkins", "github actions", "ci/cd", "linux", "bash",
    "serverless", "lambda",
    # tools / misc
    "git", "jira", "agile", "scrum", "kafka", "rabbitmq", "celery",
    "unit testing", "pytest", "selenium", "figma", "power bi", "tableau",
]


@functools.lru_cache(maxsize=1)
def _load_pipeline() -> tuple[spacy.language.Language, PhraseMatcher]:
    """Load spaCy model + build the PhraseMatcher once (cached)."""
    try:
        nlp = spacy.load(settings.spacy_model, disable=["ner", "parser"])
    except OSError as exc:  # model not downloaded
        raise RuntimeError(
            f"spaCy model '{settings.spacy_model}' not found. "
            f"Run: python -m spacy download {settings.spacy_model}"
        ) from exc

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in SKILL_VOCAB]
    matcher.add("SKILLS", patterns)
    return nlp, matcher


def extract_skills(text: str) -> set[str]:
    """Return the set of known skills present in the text (normalised, lower)."""
    if not text.strip():
        return set()
    nlp, matcher = _load_pipeline()
    doc = nlp(text.lower())
    found: set[str] = set()
    for _match_id, start, end in matcher(doc):
        found.add(doc[start:end].text.strip())
    return found


def preprocess(text: str) -> str:
    """Lemmatise and drop stopwords/punctuation for cleaner embeddings."""
    if not text.strip():
        return ""
    nlp, _ = _load_pipeline()
    doc = nlp(text)
    tokens = [
        tok.lemma_.lower()
        for tok in doc
        if not tok.is_stop and not tok.is_punct and not tok.is_space
    ]
    return " ".join(tokens)


def skill_overlap_score(resume_skills: set[str], jd_skills: set[str]) -> float:
    """Fraction of JD skills present in the resume (0..1)."""
    if not jd_skills:
        return 0.0
    return len(resume_skills & jd_skills) / len(jd_skills)
