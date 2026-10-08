"""Agreement of one decision across identical repeats. No model calls.

Same ticker, same day, N fresh runs. The score is the modal share of the
parsed label (BUY / SELL / HOLD): the most common label divided by N. A tie
has no mode and fails. An 80% share on 10 runs is the pass line the user set.
The Wilson lower bound is reported beside it, because 8/10 does not show that
the true rate is at least 80%.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional, Sequence


def wilson_interval(hits: int, n: int, *, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson interval for ``hits`` successes in ``n`` trials."""
    if n <= 0:
        raise ValueError("n must be positive")
    if hits < 0 or hits > n:
        raise ValueError("hits must be between 0 and n")
    p = hits / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = p + z2 / (2.0 * n)
    margin = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return ((centre - margin) / denom, (centre + margin) / denom)


@dataclass(frozen=True)
class ModalAgreement:
    n: int
    mode: Optional[str]
    counts: Dict[str, int]
    modal_share: float
    wilson_low: float
    wilson_high: float
    passes_bar: bool
    proven_bar: bool
    bar: float

    def as_dict(self) -> Dict[str, object]:
        return {
            "n": self.n,
            "mode": self.mode,
            "counts": dict(self.counts),
            "modal_share": self.modal_share,
            "wilson_low": self.wilson_low,
            "wilson_high": self.wilson_high,
            "bar": self.bar,
            "passes_bar": self.passes_bar,
            "proven_bar": self.proven_bar,
        }


def modal_agreement(labels: Sequence[object], *, bar: float = 0.80) -> ModalAgreement:
    """Modal share of parsed labels. A tie fails. Blank labels are rejected."""
    if not labels:
        raise ValueError("labels must not be empty")
    if not 0.0 < bar <= 1.0:
        raise ValueError("bar must be in (0, 1]")
    parsed = []
    for raw in labels:
        token = str(raw).strip().upper()
        if not token:
            raise ValueError("blank label")
        parsed.append(token)
    counts: Dict[str, int] = {}
    for token in parsed:
        counts[token] = counts.get(token, 0) + 1
    ranking = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    leading, hits = ranking[0]
    tied = len(ranking) > 1 and ranking[1][1] == hits
    n = len(parsed)
    low, high = wilson_interval(hits, n)
    share = 0.0 if tied else hits / n
    return ModalAgreement(
        n=n,
        mode=None if tied else leading,
        counts=counts,
        modal_share=share,
        wilson_low=low,
        wilson_high=high,
        passes_bar=share >= bar,
        proven_bar=(not tied) and low >= bar,
        bar=bar,
    )
