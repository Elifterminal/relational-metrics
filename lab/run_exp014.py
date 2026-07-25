"""EXP-014 -- is the 0.5 retention real?

EXP-013 reported that four structures with lower-order leakage all retained
about half their outcome-relevant information under partial observation:
0.4965, 0.5028, 0.4996, 0.4996. That was flagged as suggestive and explicitly
NOT claimed. This settles it.

FIRST, A DEFLATION FOUND BEFORE RUNNING ANYTHING. The four were not four:
  * `majority` and `threshold2` are THE SAME FUNCTION at k=3 -- identical
    truth tables (0,0,0,1,0,1,1,1).
  * `AND` and `OR` are De Morgan duals, related by complementing inputs and
    output, which preserves mutual information exactly.
So the "four independent structures agreeing" were TWO structures, each
counted twice. The consistency was manufactured by the choice of functions.

METHOD. No sampling. For a Boolean function f of k inputs with uniform inputs
and symmetric noise e, the joint over (inputs, outcome) is known exactly, so
mutual information is computed in closed form. Then enumerate ALL 256 Boolean
functions of three variables -- exhaustive, not a sample -- and look at the
distribution of

    retention = I(Y; visible) / I(Y; all),  best over which input is hidden.

If 0.5 is a real attractor it should show as a spike in an exhaustive census.
If it is a coincidence of two hand-picked functions, it will not.

PREDICTIONS, written before running:
  1. The distribution is SPREAD, not spiked at 0.5.
  2. The noiseless value for AND is about 0.54, not 0.50 -- meaning the 5%
     noise in EXP-013 pulled it toward a half and the roundness was partly a
     noise artifact rather than a property of the function.
  3. Therefore 0.5 is NOT real, and EXP-013's flag was the correct call.

FALSIFICATION: a genuine spike at 0.5 across the census -- a large fraction of
all functions landing within a narrow band of one half -- would mean there is
something structural to explain and it deserves its own theory.
"""

from __future__ import annotations

import json
import math
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

_LOG2 = math.log(2.0)
K = 3
NOISE = 0.05


def h(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log(p) + (1 - p) * math.log(1 - p)) / _LOG2


def exact_mi(table: tuple[int, ...], visible: tuple[int, ...], noise: float) -> float:
    """I(Y; X_visible) in closed form.

    Inputs uniform over 2^K, outcome is f(inputs) flipped with probability
    `noise`. Grouping input patterns by their visible part gives, for each
    group, the fraction of patterns whose f-value is 1 -- and from that the
    conditional distribution of Y exactly.
    """
    inputs = list(product((0, 1), repeat=K))
    groups: dict[tuple, list[int]] = {}
    for i, pat in enumerate(inputs):
        key = tuple(pat[j] for j in visible)
        groups.setdefault(key, []).append(table[i])

    p_y1 = sum(table) / len(table)
    p_y1 = p_y1 * (1 - noise) + (1 - p_y1) * noise
    h_y = h(p_y1)

    h_y_given = 0.0
    for key, vals in groups.items():
        w = len(vals) / len(inputs)
        frac1 = sum(vals) / len(vals)
        cond = frac1 * (1 - noise) + (1 - frac1) * noise
        h_y_given += w * h(cond)
    return h_y - h_y_given


def retention_of(table: tuple[int, ...], noise: float) -> dict:
    full = exact_mi(table, tuple(range(K)), noise)
    if full < 1e-9:
        return {"full": full, "retention": None, "degenerate": True}
    best = max(exact_mi(table, tuple(j for j in range(K) if j != hide), noise)
               for hide in range(K))
    return {"full": full, "best_partial": best,
            "retention": best / full, "degenerate": False}


def main() -> None:
    tables = [tuple((f >> i) & 1 for i in range(2 ** K)) for f in range(2 ** (2 ** K))]

    census = {}
    for noise in (0.0, NOISE):
        vals, degenerate = [], 0
        for t in tables:
            r = retention_of(t, noise)
            if r["degenerate"]:
                degenerate += 1
            else:
                vals.append(r["retention"])
        vals.sort()
        near_half = sum(1 for v in vals if abs(v - 0.5) < 0.01)
        # how wide a band around 0.5 is needed to hold a quarter of them?
        buckets = {}
        for v in vals:
            b = round(v, 1)
            buckets[f"{b:.1f}"] = buckets.get(f"{b:.1f}", 0) + 1
        census[f"noise_{noise}"] = {
            "n_functions": len(tables),
            "n_degenerate": degenerate,
            "n_scored": len(vals),
            "within_0.01_of_half": near_half,
            "fraction_within_0.01_of_half": round(near_half / max(len(vals), 1), 4),
            "distinct_values": len(set(round(v, 6) for v in vals)),
            "min": round(min(vals), 4), "max": round(max(vals), 4),
            "median": round(vals[len(vals) // 2], 4),
            "histogram_rounded_to_0.1": dict(sorted(buckets.items())),
        }

    named = {
        "AND": (0, 0, 0, 0, 0, 0, 0, 1),
        "OR": (0, 1, 1, 1, 1, 1, 1, 1),
        "majority": (0, 0, 0, 1, 0, 1, 1, 1),
        "parity": tuple(1 if bin(i).count("1") % 2 else 0 for i in range(8)),
    }
    exact_named = {}
    for name, t in named.items():
        exact_named[name] = {
            "retention_noiseless": round(retention_of(t, 0.0)["retention"], 4)
            if not retention_of(t, 0.0)["degenerate"] else None,
            "retention_at_5pct_noise": round(retention_of(t, NOISE)["retention"], 4)
            if not retention_of(t, NOISE)["degenerate"] else None,
        }

    # how does noise itself move the number?
    noise_pull = {}
    for e in (0.0, 0.01, 0.05, 0.10, 0.20):
        noise_pull[f"{e:.2f}"] = {
            n: round(retention_of(t, e)["retention"], 4)
            for n, t in named.items() if not retention_of(t, e)["degenerate"]
        }

    c0 = census["noise_0.0"]
    c5 = census[f"noise_{NOISE}"]
    spike = c5["fraction_within_0.01_of_half"] > 0.25

    report = {
        "experiment": "EXP-014",
        "question": "is the ~0.5 retention from EXP-013 a real attractor?",
        "deflation": {
            "majority_equals_threshold2": True,
            "and_or_are_de_morgan_duals": True,
            "distinct_structures_in_exp013": 2,
            "reported_as": 4,
        },
        "census": census,
        "named_functions_exact": exact_named,
        "noise_pull": noise_pull,
        "is_half_a_real_attractor": spike,
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp014.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-014  written to {out}\n")
    print("DEFLATION FOUND BEFORE RUNNING:")
    print("  majority and threshold2 are the SAME function at k=3")
    print("  AND and OR are De Morgan duals (MI-preserving)")
    print("  -> EXP-013's 'four independent structures' were TWO\n")

    print(f"EXHAUSTIVE CENSUS of all {2**(2**K)} Boolean functions of {K} variables")
    for tag, c in census.items():
        print(f"\n  {tag}:  {c['n_scored']} non-degenerate, "
              f"{c['n_degenerate']} degenerate")
        print(f"    range {c['min']} .. {c['max']}   median {c['median']}")
        print(f"    distinct retention values: {c['distinct_values']}")
        print(f"    within 0.01 of exactly 0.5: {c['within_0.01_of_half']} "
              f"({c['fraction_within_0.01_of_half']*100:.1f}%)")
        print(f"    histogram: {c['histogram_rounded_to_0.1']}")

    print("\nTHE NAMED FUNCTIONS, EXACTLY:")
    print(f"  {'function':<12}{'noiseless':>12}{'at 5% noise':>14}")
    for n, v in exact_named.items():
        a = f"{v['retention_noiseless']:.4f}" if v['retention_noiseless'] is not None else "-"
        b = f"{v['retention_at_5pct_noise']:.4f}" if v['retention_at_5pct_noise'] is not None else "-"
        print(f"  {n:<12}{a:>12}{b:>14}")

    print("\nHOW MUCH IS NOISE MOVING IT?")
    print(f"  {'noise':<8}" + "".join(f"{n:>12}" for n in named))
    for e, row in noise_pull.items():
        print(f"  {e:<8}" + "".join(f"{row.get(n, float('nan')):>12.4f}" for n in named))

    print(f"\n>>> IS 0.5 A REAL ATTRACTOR?  {spike}")


if __name__ == "__main__":
    main()
