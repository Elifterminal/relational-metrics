"""EXP-037 -- Q-35. How many test cases would actually settle this?

EXP-036 found that 6/10 blind is p = 0.754 -- a null result that had been
reported as "degraded but present" for two experiments. At ten motifs the design
can only confirm a near-perfect score; it cannot measure anything smaller. So
before building another corpus, work out what size would be needed.

Three things computed here:

  1. WHAT n=10 CAN SEE. The smallest score at ten motifs that reaches p<0.05,
     and the power to detect various true abilities.
  2. WHAT THE DATA ACTUALLY SAYS. A confidence interval on 6/10 -- the range of
     true abilities consistent with what we observed.
  3. WHAT WOULD BE NEEDED. Motifs required for 80% and 90% power against
     several plausible effect sizes.

And a fourth thing that turned out to matter more: the test throws away
information by construction. "Did the analogue beat the false friend" is one bit
per motif, discarding the MARGIN by which it won or lost. A test on the margins
needs far fewer motifs for the same confidence, and the corpora already contain
the numbers -- they were being thrown away at the reporting step.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from corpus import QUERIES, docs_for, query_doc                   # noqa: E402
from corpus_holdout import (HOLDOUT_QUERIES, holdout_docs_for,    # noqa: E402
                            holdout_query)
from corpus_independent import (INDEPENDENT_QUERIES,              # noqa: E402
                                independent_docs_for, independent_query)
from measures import mdl_correspondence                           # noqa: E402

ALPHA = 0.05


def pmf(k, n, p):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def p_two_sided(k, n, p0=0.5):
    obs = pmf(k, n, p0)
    return min(1.0, sum(pmf(i, n, p0) for i in range(n + 1) if pmf(i, n, p0) <= obs + 1e-12))


def critical_k(n, p0=0.5, alpha=ALPHA):
    """Smallest k whose two-sided p is below alpha."""
    for k in range(n, -1, -1):
        if p_two_sided(k, n, p0) >= alpha:
            return k + 1
    return 0


def power(n, p_true, p0=0.5, alpha=ALPHA):
    kc = critical_k(n, p0, alpha)
    return sum(pmf(k, n, p_true) for k in range(kc, n + 1))


def required_n(p_true, target=0.80, p0=0.5, alpha=ALPHA, cap=400):
    for n in range(4, cap + 1):
        if power(n, p_true, p0, alpha) >= target:
            return n
    return None


def clopper_pearson(k, n, conf=0.95):
    """Exact binomial confidence interval, by search rather than by beta fn."""
    a = (1 - conf) / 2
    lo, hi = 0.0, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        if sum(pmf(i, n, m) for i in range(k, n + 1)) < a:
            lo = m
        else:
            hi = m
    low = lo if k > 0 else 0.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        if sum(pmf(i, n, m) for i in range(0, k + 1)) < a:
            hi = m
        else:
            lo = m
    high = hi if k < n else 1.0
    return round(low, 3), round(high, 3)


def margins(blind: bool = True):
    """The information the binary test discards: how much X beats W by.

    Computed on the BLIND annotations. The sighted margins give d = 2.155 and a
    required n of 2, and neither number should be quoted: the sighted corpus is
    the one EXP-032 showed to be inflated, and the normal approximation is not
    reliable at that size.
    """
    if not blind:
        out = []
        for motifs, qf, df in ((QUERIES, query_doc, docs_for),
                               (HOLDOUT_QUERIES, holdout_query, holdout_docs_for),
                               (INDEPENDENT_QUERIES, independent_query,
                                independent_docs_for)):
            for m in motifs:
                q = qf(m)
                d = {x.kind: x.structure for x in df(m)}
                out.append(
                    mdl_correspondence(q.structure, d["X"], DEFAULT_CODE).ratio
                    - mdl_correspondence(q.structure, d["W"], DEFAULT_CODE).ratio)
        return out

    from blind_reannotate import load_key as k26
    from q26_blind_annotations import B
    from q30_blind_annotations import Q30
    from q30_pool import load_key as k30
    from run_exp032 import build

    M = {}
    for ann, key in ((B, {k["passage_id"]: k for k in k26()}),
                     (Q30, {k["passage_id"]: k for k in k30()})):
        for pid, e in ann.items():
            k = key[pid]
            M.setdefault((k.get("corpus", "independent"), k["motif"]), {})[k["kind"]] = \
                build(pid, e)
    out = []
    for _, d in sorted(M.items()):
        if {"D", "X", "W"} <= set(d):
            out.append(mdl_correspondence(d["D"], d["X"], DEFAULT_CODE).ratio
                       - mdl_correspondence(d["D"], d["W"], DEFAULT_CODE).ratio)
    return out


def main() -> None:
    n_now = 10
    kc = critical_k(n_now)
    ci = clopper_pearson(6, 10)

    grid = [0.60, 0.65, 0.70, 0.75, 0.80, 0.90]
    need80 = {p: required_n(p, 0.80) for p in grid}
    need90 = {p: required_n(p, 0.90) for p in grid}
    pow10 = {p: round(power(n_now, p), 3) for p in grid}

    mg = margins(blind=True)
    mean_m, sd_m = statistics.fmean(mg), statistics.pstdev(mg)
    # paired t-style effect size on the margins, sighted corpora
    d = mean_m / sd_m if sd_m else float("inf")
    # n for a one-sample t-test at 80% power, normal approximation
    n_margin = math.ceil(((1.96 + 0.84) / d) ** 2) if d else None

    report = {
        "experiment": "EXP-037", "question": "Q-35",
        "current_design": {
            "motifs": n_now,
            "smallest_significant_score": f"{kc}/{n_now}",
            "note": (f"at {n_now} motifs nothing below {kc}/{n_now} reaches p<0.05, so the "
                     "design can confirm a near-perfect measure and measure nothing else"),
            "power_to_detect": pow10,
        },
        "what_the_data_says": {
            "observed": "6/10",
            "confidence_interval_95": ci,
            "reading": (f"true ability anywhere from {ci[0]:.0%} to {ci[1]:.0%} is consistent "
                        "with what we saw -- which includes chance and includes a strong effect. "
                        "The experiment did not discriminate"),
        },
        "motifs_required": {"power_0.80": need80, "power_0.90": need90},
        "margin_test": {
            "note": ("the binary test discards the margin by which the analogue wins or "
                     "loses -- one bit per motif from a continuous number the corpus "
                     "already contains"),
            "mean_margin_bits": round(mean_m, 4),
            "sd_margin_bits": round(sd_m, 4),
            "effect_size_d": round(d, 3),
            "motifs_for_80pct_power_on_margins": n_margin,
            "computed_on": "BLIND annotations",
            "caveat": ("the effect size comes from the same 10 observations the "
                       "test would be planned around. Pilot-derived effect sizes "
                       "are biased upward, so treat this n as a FLOOR, not an "
                       "estimate. Three of the ten margins are exactly zero -- "
                       "abstentions counted as no-difference"),
        },
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp037.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-037  written to {out}\n")

    print(f"WHAT 10 MOTIFS CAN SEE")
    print(f"   nothing below {kc}/10 reaches p<0.05 -- the design confirms or says nothing\n")
    print(f"   {'if the measure is really right':<32}{'power at n=10':>14}")
    for p in grid:
        print(f"   {p:>28.0%}  {pow10[p]:>14.0%}")

    print(f"\nWHAT OUR DATA ACTUALLY SAYS")
    print(f"   observed 6/10, 95% interval on true ability: {ci[0]:.0%} to {ci[1]:.0%}")
    print(f"   -> consistent with chance AND with a strong effect. It did not discriminate.\n")

    print(f"MOTIFS NEEDED")
    print(f"   {'true ability':<16}{'80% power':>11}{'90% power':>11}")
    for p in grid:
        a, b = need80[p], need90[p]
        print(f"   {p:<16.0%}{(a if a else '>400'):>11}{(b if b else '>400'):>11}")

    m = report["margin_test"]
    print(f"\nAND THE TEST IS THROWING AWAY MOST OF ITS OWN INFORMATION")
    print(f"   mean margin {m['mean_margin_bits']:+.4f} bits, sd {m['sd_margin_bits']:.4f}, "
          f"effect size d = {m['effect_size_d']}")
    print(f"   motifs needed if we test the MARGIN instead of the yes/no: "
          f"{m['motifs_for_80pct_power_on_margins']}")
    print(f"   -- against {need80[0.75]} for a yes/no test at 75% ability, "
          f"or {need80[0.60]} at the 60% we actually observed.")
    print(f"\n   CAVEAT: {m['caveat']}")


if __name__ == "__main__":
    main()
