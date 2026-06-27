"""Service d'analyse de sentiment financier via FinBERT."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache

from transformers import pipeline

log = logging.getLogger(__name__)

MODEL_NAME = "ProsusAI/finbert"


@dataclass
class SentimentResult:
    label: str  # "positive" / "neutral" / "negative"
    score: float  # probabilité 0..1
    text_preview: str


@lru_cache(maxsize=1)
def get_pipeline():
    """Charge le modèle une seule fois (singleton)."""
    log.info("Loading FinBERT model (first call)...")

    pipe = pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
    )

    log.info("FinBERT model loaded.")
    return pipe


def analyze(text: str) -> SentimentResult:
    """Analyse le sentiment d'un texte."""

    if not text or not text.strip():
        raise ValueError("Texte vide")

    pipe = get_pipeline()

    # FinBERT accepte au maximum 512 tokens
    out = pipe(text[:512])[0]

    return SentimentResult(
        label=out["label"].lower(),
        score=round(float(out["score"]), 4),
        text_preview=text[:80] + ("..." if len(text) > 80 else ""),
    )


def analyze_batch(texts: list[str]) -> list[SentimentResult]:
    """Analyse une liste de textes."""

    if not texts:
        return []

    pipe = get_pipeline()

    truncated = [text[:512] for text in texts if text and text.strip()]

    outputs = pipe(
        truncated,
        batch_size=16,
    )

    return [
        SentimentResult(
            label=output["label"].lower(),
            score=round(float(output["score"]), 4),
            text_preview=text[:80] + ("..." if len(text) > 80 else ""),
        )
        for text, output in zip(truncated, outputs)
    ]
