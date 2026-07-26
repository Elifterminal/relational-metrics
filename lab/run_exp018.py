"""EXP-018 -- retention re-reported per participant.

EXP-017 found that best-case and worst-case retention rank structures
ANTI-correlated (-0.117). Every finding from EXP-013 onward summarised
retention with a best case. The law itself is per-participant and exact, so
the mathematics was never wrong -- but every CONCLUSION drawn from a best-case
summary now has to be re-checked against the full per-participant picture.

This is not a re-wording. The question is whether the conclusions survive:

  1. Is retention still QUANTISED under worst-case and pooled reporting?
  2. Is parity still the UNIQUE zero, or do others reach zero when you lose
     your most important participant?
  3. Is 0.5 still a real class?
  4. HOW MUCH does it matter which participant you lose -- the within-function
     spread? If that spread is large, no single summary is defensible and
     retention must always be reported as a vector.
  5. Does EXP-013's structure-type conclusion (parity cliffs, others keep
     about half) survive worst-case reporting?

PREDICTION: quantisation survives (same formula, different j). Parity stays at
zero either way since all its influences are maximal. But the ZERO CLASS
should GROW under worst-case -- any balanced function with a fully-influential
participant hits zero when that participant is the one you lose. If so, the
claim "parity is the unique structure that vanishes" was an artifact of
best-case reporting, and the honest statement is narrower.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from run_exp015 import h, influences                     # noqa: E402


def per_participant(table, k):
    """Retention for each choice of hidden participant. Noiseless."""
    hy = h(sum(table) / len(table))
    if hy <= 1e-12:
        return None
    return [1.0 - i / hy for i in influences(table, k)]


def census(k: int) -> dict:
    n_fun = 1 << (1 << k)
    best_c, worst_c, pooled_c = Counter(), Counter(), Counter()
    spreads = []
    zero_best = zero_worst = 0
    scored = 0
    for f in range(n_fun):
        t = tuple((f >> i) & 1 for i in range(1 << k))
        vals = per_participant(t, k)
        if vals is None:
            continue
        scored += 1
        b, w = max(vals), min(vals)
        best_c[round(b, 9)] += 1
        worst_c[round(w, 9)] += 1
        for v in vals:
            pooled_c[round(v, 9)] += 1
        spreads.append(b - w)
        if abs(b) < 1e-12:
            zero_best += 1
        if abs(w) < 1e-12:
            zero_worst += 1
    spreads.sort()
    return {
        "k": k, "scored": scored,
        "distinct_best": len(best_c), "distinct_worst": len(worst_c),
        "distinct_pooled": len(pooled_c),
        "at_zero_best": zero_best, "at_zero_worst": zero_worst,
        "at_half_best": best_c.get(0.5, 0), "at_half_worst": worst_c.get(0.5, 0),
        "at_half_pooled": pooled_c.get(0.5, 0),
        "spread_mean": round(sum(spreads) / len(spreads), 4),
        "spread_median": round(spreads[len(spreads) // 2], 4),
        "spread_max": round(spreads[-1], 4),
        "frac_with_zero_spread": round(
            sum(1 for s in spreads if s < 1e-12) / len(spreads), 4),
    }


def families(k: int):
    n = 1 << k
    def tt(fn): return tuple(fn(tuple((i >> b) & 1 for b in range(k))) for i in range(n))
    out = {"parity": tt(lambda v: eval("^".join(map(str, v)) if v else "0")),
           "and": tt(lambda v: int(all(v))),
           "or": tt(lambda v: int(any(v))),
           "threshold2": tt(lambda v: int(sum(v) >= 2))}
    if k % 2 == 1:
        out["majority"] = tt(lambda v: int(sum(v) * 2 > k))
    return out


def main() -> None:
    report = {"experiment": "EXP-018",
              "question": "do the retention conclusions survive per-participant reporting?"}

    report["census"] = {f"k={k}": census(k) for k in (3, 4)}

    # -- EXP-013's structure table, re-reported ---------------------------
    table = {}
    for k in (3, 4):
        for name, t in families(k).items():
            vals = per_participant(t, k)
            if vals is None:
                continue
            table[f"{name}_k{k}"] = {
                "per_participant": [round(v, 4) for v in vals],
                "best": round(max(vals), 4),
                "worst": round(min(vals), 4),
                "spread": round(max(vals) - min(vals), 4),
            }
    report["structure_families_reported_properly"] = table

    c3, c4 = report["census"]["k=3"], report["census"]["k=4"]
    report["verdicts"] = {
        "quantisation_survives": (c3["distinct_pooled"] < 50
                                  and c4["distinct_pooled"] < 200),
        "parity_still_unique_zero_best_case": c3["at_zero_best"] == 2,
        "zero_class_grows_under_worst_case": c3["at_zero_worst"] > c3["at_zero_best"],
        "half_survives_worst_case": c3["at_half_worst"] > 0,
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp018.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-018  written to {out}\n")
    print("CENSUS, reported three ways")
    print(f"  {'':<22}{'k=3':>12}{'k=4':>12}")
    for label, key in (("functions scored", "scored"),
                       ("distinct (best case)", "distinct_best"),
                       ("distinct (worst case)", "distinct_worst"),
                       ("distinct (pooled)", "distinct_pooled"),
                       ("at zero, best case", "at_zero_best"),
                       ("at zero, WORST case", "at_zero_worst"),
                       ("at 0.5, best case", "at_half_best"),
                       ("at 0.5, worst case", "at_half_worst")):
        print(f"  {label:<22}{c3[key]:>12,}{c4[key]:>12,}")

    print(f"\nWITHIN-FUNCTION SPREAD (best minus worst)")
    for tag, c in (("k=3", c3), ("k=4", c4)):
        print(f"  {tag}: mean {c['spread_mean']}, median {c['spread_median']}, "
              f"max {c['spread_max']}, "
              f"{c['frac_with_zero_spread']*100:.1f}% have no spread at all")

    print("\nEXP-013's STRUCTURE TABLE, RE-REPORTED")
    print(f"  {'family':<16}{'per participant':<34}{'best':>8}{'worst':>8}{'spread':>9}")
    for k, v in table.items():
        pp = str(v["per_participant"])
        print(f"  {k:<16}{pp:<34}{v['best']:>8.4f}{v['worst']:>8.4f}{v['spread']:>9.4f}")

    print("\nVERDICTS")
    for k, v in report["verdicts"].items():
        print(f"  {k:<42}{v}")


if __name__ == "__main__":
    main()
