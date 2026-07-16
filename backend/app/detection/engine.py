"""Detection engine: orchestrates signature rules + heuristics into a single
verdict.

Scoring: signals are combined with a noisy-OR (``1 - prod(1 - w_i)``) rather
than a plain sum. This means a single high-confidence rule (e.g. weight 0.85)
can push a message straight to "block" on its own, while several weak
heuristic signals only add up to something significant when they co-occur —
which keeps benign text that trips one low-weight heuristic from being
over-penalized.

Thresholds (see app.config): score >= BLOCK_THRESHOLD -> "block",
score >= FLAG_THRESHOLD -> "flag", else "allow".
"""

from dataclasses import dataclass

from app.config import BLOCK_THRESHOLD, FLAG_THRESHOLD
from app.detection.heuristics import run_heuristics
from app.detection.rules import run_rules
from app.schemas import ScreenResponse, Verdict


@dataclass(frozen=True)
class Signal:
    name: str
    category: str
    weight: float
    reason: str


def _combine(weights: list[float]) -> float:
    score = 1.0
    for w in weights:
        score *= 1.0 - max(0.0, min(1.0, w))
    return round(1.0 - score, 4)


def _verdict_for(score: float) -> Verdict:
    if score >= BLOCK_THRESHOLD:
        return "block"
    if score >= FLAG_THRESHOLD:
        return "flag"
    return "allow"


def collect_signals(text: str) -> list[Signal]:
    signals: list[Signal] = []
    for m in run_rules(text):
        signals.append(Signal(m.rule_name, m.category, m.weight, m.reason))
    for h in run_heuristics(text):
        signals.append(Signal(h.name, h.category, h.weight, h.reason))
    return signals


def screen(text: str) -> ScreenResponse:
    signals = collect_signals(text)
    score = _combine([s.weight for s in signals])
    verdict = _verdict_for(score)
    categories = sorted({s.category for s in signals})
    reasons = [s.reason for s in signals]
    return ScreenResponse(
        verdict=verdict,
        risk_score=score,
        categories=categories,
        reasons=reasons,
    )
