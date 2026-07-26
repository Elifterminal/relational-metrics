"""Margin-based evaluation. Q-36.

The project spent thirty-seven experiments proving that a scalar summary hides
structure and can reverse a ranking (P-17), and enforced that on the MEASURE
while its own EVALUATION reduced every comparison to one bit: "did the analogue
beat the false friend". EXP-037 costed that choice -- on the same blind data the
margins need about twelve test cases where the binary count needs one hundred
and ninety-nine.

So: report the margin, its spread, and the per-motif values. The win count is a
footnote.

WHY TWO TESTS. The margin distribution is not known to be normal and n is small,
so a t-test alone would be assuming what it cannot check. Wilcoxon signed-rank
makes no distributional assumption but discards exact ties, which here are
abstentions -- the measure declining to separate two documents. Neither test is
right on its own:

    t-test      keeps the abstentions, assumes a shape
    Wilcoxon    assumes no shape, drops the abstentions

Reporting both, and reporting the disagreement if there is one, rather than
picking whichever is kinder.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass


def _norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _t_sf(t: float, df: int) -> float:
    """Upper tail of Student's t, via the regularised incomplete beta."""
    if df <= 0:
        return float("nan")
    x = df / (df + t * t)

    def betacf(a, b, x, it=200):
        qab, qap, qam = a + b, a + 1.0, a - 1.0
        c, d = 1.0, 1.0 - qab * x / qap
        d = 1e-30 if abs(d) < 1e-30 else d
        d = 1.0 / d
        h = d
        for m in range(1, it):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1.0 + aa * d
            c = 1.0 + aa / c
            d = 1e-30 if abs(d) < 1e-30 else d
            c = 1e-30 if abs(c) < 1e-30 else c
            d = 1.0 / d
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1.0 + aa * d
            c = 1.0 + aa / c
            d = 1e-30 if abs(d) < 1e-30 else d
            c = 1e-30 if abs(c) < 1e-30 else c
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 3e-9:
                break
        return h

    a, b = df / 2.0, 0.5
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    ib = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) * betacf(a, b, x) / a
    p = 0.5 * min(1.0, max(0.0, ib))
    return p if t > 0 else 1.0 - p


@dataclass(frozen=True)
class MarginResult:
    n: int
    margins: tuple[float, ...]
    mean: float
    sd: float
    effect_size_d: float
    ci95: tuple[float, float]
    t_p: float
    wilcoxon_p: float
    wilcoxon_n: int
    ties: int
    wins: int

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "per_motif_margins": [round(m, 4) for m in self.margins],
            "mean_margin_bits": round(self.mean, 4),
            "sd": round(self.sd, 4),
            "effect_size_d": round(self.effect_size_d, 3),
            "ci95_on_mean": [round(self.ci95[0], 4), round(self.ci95[1], 4)],
            "t_test_p": round(self.t_p, 4),
            "wilcoxon_p": round(self.wilcoxon_p, 4),
            "wilcoxon_n_after_dropping_ties": self.wilcoxon_n,
            "abstentions": self.ties,
            "_footnote_win_count": f"{self.wins}/{self.n}",
        }


def evaluate_margins(margins) -> MarginResult:
    """One-sided question -- is the analogue above the false friend on average?
    Reported two-sided, because a systematically NEGATIVE margin would be a
    finding too and a one-sided test would hide it."""
    xs = list(margins)
    n = len(xs)
    mean = statistics.fmean(xs)
    sd = statistics.stdev(xs) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 1 and sd else 0.0
    t = mean / se if se else float("inf") if mean else 0.0
    t_p = 2.0 * min(_t_sf(abs(t), n - 1), 1.0) if se else (0.0 if mean else 1.0)
    tcrit = 2.262 if n == 10 else 2.0
    ci = (mean - tcrit * se, mean + tcrit * se)

    nz = [x for x in xs if x != 0.0]
    wn = len(nz)
    if wn:
        order = sorted(range(wn), key=lambda i: abs(nz[i]))
        ranks = [0.0] * wn
        for r, i in enumerate(order, start=1):
            ranks[i] = float(r)
        wplus = sum(ranks[i] for i in range(wn) if nz[i] > 0)
        mu = wn * (wn + 1) / 4.0
        sig = math.sqrt(wn * (wn + 1) * (2 * wn + 1) / 24.0)
        z = (wplus - mu) / sig if sig else 0.0
        w_p = 2.0 * (1.0 - _norm_cdf(abs(z)))
    else:
        w_p = 1.0

    return MarginResult(n=n, margins=tuple(xs), mean=mean, sd=sd,
                        effect_size_d=(mean / sd if sd else 0.0), ci95=ci,
                        t_p=t_p, wilcoxon_p=w_p, wilcoxon_n=wn,
                        ties=n - wn, wins=sum(1 for x in xs if x > 0))
