"""Credibility scoring for claims and sources."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


LOADED_TERMS = {
    "shocking", "exposed", "secret", "everyone lies", "never", "always",
    "destroyed", "scam", "guaranteed", "you won't believe",
}

SOURCE_WEIGHTS = {
    "primary": 20,
    "official": 18,
    "research": 16,
    "reputable_media": 12,
    "expert": 10,
    "blog": 5,
    "social": 2,
    "unknown": 0,
}


@dataclass(frozen=True)
class CredibilityReport:
    score: int
    status: str
    unsupported_claims: tuple[str, ...]
    source_types: tuple[str, ...]
    emotional_language_flags: tuple[str, ...]
    recommendations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def analyze_content(payload: dict[str, Any]) -> CredibilityReport:
    claims = payload.get("claims", [])
    sources = payload.get("sources", [])
    transcript = payload.get("transcript", "")

    source_types = tuple(sorted({source.get("type", "unknown") for source in sources}))
    support_map = _claim_support_map(claims, sources)
    unsupported = tuple(claim["text"] for claim in claims if not support_map.get(claim.get("id", "")))
    loaded = tuple(term for term in sorted(LOADED_TERMS) if term in transcript.lower())

    score = 55
    score += min(30, sum(SOURCE_WEIGHTS.get(source_type, 0) for source_type in set(source_types)) // 2)
    score -= len(unsupported) * 14
    score -= len(loaded) * 5
    if len(source_types) >= 3:
        score += 8
    score = max(0, min(100, score))

    status = "publishable" if score >= 80 and not unsupported else "review" if score >= 50 else "high-risk"
    recommendations = _recommendations(unsupported, loaded, source_types)
    return CredibilityReport(
        score=score,
        status=status,
        unsupported_claims=unsupported,
        source_types=source_types,
        emotional_language_flags=loaded,
        recommendations=tuple(recommendations),
    )


def _claim_support_map(claims: list[dict[str, Any]], sources: list[dict[str, Any]]) -> dict[str, bool]:
    source_claim_ids = {claim_id for source in sources for claim_id in source.get("supports", [])}
    return {claim.get("id", ""): claim.get("id", "") in source_claim_ids for claim in claims}


def _recommendations(unsupported: tuple[str, ...], loaded: tuple[str, ...], source_types: tuple[str, ...]) -> list[str]:
    recs: list[str] = []
    if unsupported:
        recs.append("Add source evidence for unsupported claims before publishing or sharing.")
    if loaded:
        recs.append("Rewrite emotionally loaded language into neutral wording.")
    if "primary" not in source_types and "official" not in source_types:
        recs.append("Add at least one primary or official source.")
    if not recs:
        recs.append("Ready for human editorial review.")
    return recs

