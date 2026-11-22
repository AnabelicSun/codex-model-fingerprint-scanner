"""Classification rules: behavior is primary evidence; response_model is supporting evidence."""
from __future__ import annotations


def classify_sample(*, requested_model: str, behavior_prediction: str | None = None,
                    response_model: str | None = None, http_status: int | None = None,
                    error: str | None = None) -> str:
    """Return a stable class; response_model alone never produces a downgrade."""
    message = (error or "").lower()
    if http_status == 404 or "not supported by any configured account" in message:
        return "model_unavailable"
    if http_status == 429 or "429" in message:
        return "rate_limited"
    if behavior_prediction:
        return ("behavior_matches_requested_model" if behavior_prediction == requested_model
                else "candidate_model_mismatch")
    return "sample_failed"


def summarize(results: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        key = str(result.get("classification", result.get("status", "unknown")))
        counts[key] = counts.get(key, 0) + 1
    return counts
