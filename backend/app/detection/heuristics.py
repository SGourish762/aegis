"""Non-signature scoring heuristics: statistical/structural signals that are
individually weak but useful in combination or against novel phrasing that
signature rules haven't seen yet.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass

HEURISTIC = "heuristic"

IMPERATIVE_VERBS = {
    "ignore", "disregard", "forget", "override", "bypass", "disable",
    "reveal", "repeat", "print", "output", "show", "tell", "act", "pretend",
    "become", "roleplay", "execute", "run", "decode", "translate", "write",
    "generate", "unlock", "enable", "grant", "provide",
}

SUSPICIOUS_TOKENS = {
    "jailbreak", "jailbroken", "unfiltered", "uncensored", "unrestricted",
    "bypass", "restriction", "restrictions", "guardrail", "guardrails",
    "safeguard", "safeguards", "exploit", "payload", "override",
}

_WORD_RE = re.compile(r"[A-Za-z']+")


@dataclass(frozen=True)
class HeuristicSignal:
    name: str
    category: str
    weight: float
    reason: str


def _imperative_density(text: str) -> HeuristicSignal | None:
    words = [w.lower() for w in _WORD_RE.findall(text)]
    if len(words) < 3:
        return None
    hits = sum(1 for w in words if w in IMPERATIVE_VERBS)
    density = hits / len(words)
    if density >= 0.12 and hits >= 2:
        weight = min(0.5, 0.2 + density)
        return HeuristicSignal(
            "imperative_density",
            HEURISTIC,
            weight,
            f"High density of imperative/override verbs ({hits} in {len(words)} words)",
        )
    return None


def _suspicious_vocab(text: str) -> HeuristicSignal | None:
    words = {w.lower() for w in _WORD_RE.findall(text)}
    hits = words & SUSPICIOUS_TOKENS
    if hits:
        weight = min(0.5, 0.15 * len(hits))
        return HeuristicSignal(
            "suspicious_vocab",
            HEURISTIC,
            weight,
            f"Contains security-bypass vocabulary: {', '.join(sorted(hits))}",
        )
    return None


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _entropy_anomaly(text: str) -> HeuristicSignal | None:
    stripped = text.strip()
    if len(stripped) < 40:
        return None
    entropy = _shannon_entropy(stripped)
    # Natural-language English text sits ~3.5-4.5 bits/char; dense
    # random-looking payloads (encoded data, obfuscated strings) run higher.
    if entropy >= 4.6:
        return HeuristicSignal(
            "entropy_anomaly",
            HEURISTIC,
            0.35,
            f"Unusually high character entropy ({entropy:.2f} bits/char), possible obfuscated payload",
        )
    return None


def _unicode_anomaly(text: str) -> HeuristicSignal | None:
    non_ascii = [c for c in text if ord(c) > 0x2000]
    if len(text) < 10:
        return None
    ratio = len(non_ascii) / len(text)
    if ratio >= 0.15:
        return HeuristicSignal(
            "unicode_anomaly",
            HEURISTIC,
            0.3,
            f"High ratio of unusual unicode characters ({ratio:.0%}), possible homoglyph evasion",
        )
    return None


def run_heuristics(text: str) -> list[HeuristicSignal]:
    signals = [
        _imperative_density(text),
        _suspicious_vocab(text),
        _entropy_anomaly(text),
        _unicode_anomaly(text),
    ]
    return [s for s in signals if s is not None]
