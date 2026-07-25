"""EXP-015 -- does the retention quantisation survive at k=4? (Q-16)

EXP-014 found that across all 256 Boolean functions of THREE variables,
retention under partial observation takes only seven distinct values. The
obvious worry is that this is a property of a very small world.

k=4 is 65,536 functions -- still exhaustive, not a sample.

A CLOSED FORM, DERIVED AND THEN CHECKED. Setting this up, the algebra
collapses. For a deterministic Boolean f with uniform inputs and symmetric
noise e, hiding variable j groups the 2^k input patterns into 2^(k-1) pairs
differing only in bit j. Within a pair the outcome is either constant or split
50/50, so

    I(Y; visible) = H(Y) - [ m_j + (2^(k-1) - m_j) * h(e) ] / 2^(k-1)

where m_j counts the pairs on which f actually changes. In the noiseless case
that second term is exactly m_j / 2^(k-1) -- which is the INFLUENCE of
variable j, a standard quantity in Boolean function analysis. So

    retention_j = 1 - Influence_j(f) / H(f)

and since we report the best case over which variable is hidden,

    retention = 1 - min_j Influence_j(f) / H(f)

If that holds it is a much stronger result than "the values are quantised": it
says what you lose to hiding a participant is exactly the influence of that
participant divided by the entropy of the outcome -- computable in advance,
from the shape of the structure, without measuring anything.

DERIVATIONS ARE NOT RESULTS. The formula is checked against brute-force exact
mutual information on every function at k=3 and on a large sample at k=4
before any of it is believed.

PREDICTIONS:
  1. The closed form matches brute force to floating-point tolerance.
  2. Quantisation survives at k=4 -- far fewer distinct values than functions.
  3. Parity remains the unique zero.
  4. There is still a class at exactly 0.5.
"""

from __future__ import annotations

import json
import math
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

_LOG2 = math.log(2.0)


def h(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log(p) + (1 - p) * math.log(1 - p)) / _LOG2


def brute_mi(table, K, visible, noise):
    """Exact I(Y; X_visible), computed the slow honest way."""
    inputs = list(product((0, 1), repeat=K))
    groups = {}
    for i, pat in enumerate(inputs):
        key = tuple(pat[j] for j in visible)
        groups.setdefault(key, []).append(table[i])
    p1 = sum(table) / len(table)
    p1 = p1 * (1 - noise) + (1 - p1) * noise
    hy = h(p1)
    cond = 0.0
    for vals in groups.values():
        w = len(vals) / len(inputs)
        f1 = sum(vals) / len(vals)
        cond += w * h(f1 * (1 - noise) + (1 - f1) * noise)
    return hy - cond


def influences(table, K):
    """m_j / 2^(k-1) for each variable: the fraction of input pairs differing
    only in bit j on which the function actually changes."""
    n = 1 << K
    out = []
    for j in range(K):
        bit = 1 << j
        m = sum(1 for i in range(n) if (i & bit) == 0 and table[i] != table[i | bit])
        out.append(m / (n // 2))
    return out


def closed_form_retention(table, K):
    """1 - min_j Influence_j / H(f). Noiseless."""
    ones = sum(table)
    hy = h(ones / len(table))
    if hy <= 1e-12:
        return None
    return 1.0 - min(influences(table, K)) / hy


def main() -> None:
    report = {"experiment": "EXP-015", "question": "does quantisation survive at k=4?"}

    # -- 1. verify the closed form against brute force ---------------------
    worst = 0.0
    checked = 0
    for f in range(256):
        t = tuple((f >> i) & 1 for i in range(8))
        full = brute_mi(t, 3, (0, 1, 2), 0.0)
        if full <= 1e-12:
            continue
        best = max(brute_mi(t, 3, tuple(j for j in range(3) if j != hide), 0.0)
                   for hide in range(3))
        worst = max(worst, abs(best / full - closed_form_retention(t, 3)))
        checked += 1
    report["closed_form_check_k3"] = {"functions_checked": checked,
                                      "max_abs_error": worst,
                                      "matches": worst < 1e-9}
    print(f"closed form vs brute force at k=3: {checked} functions, "
          f"max error {worst:.2e}")

    # spot-check at k=4 against brute force
    worst4, checked4 = 0.0, 0
    for f in range(0, 65536, 137):          # coprime stride, spread sample
        t = tuple((f >> i) & 1 for i in range(16))
        full = brute_mi(t, 4, (0, 1, 2, 3), 0.0)
        if full <= 1e-12:
            continue
        best = max(brute_mi(t, 4, tuple(j for j in range(4) if j != hide), 0.0)
                   for hide in range(4))
        worst4 = max(worst4, abs(best / full - closed_form_retention(t, 4)))
        checked4 += 1
    report["closed_form_check_k4"] = {"functions_checked": checked4,
                                      "max_abs_error": worst4,
                                      "matches": worst4 < 1e-9}
    print(f"closed form vs brute force at k=4: {checked4} functions, "
          f"max error {worst4:.2e}")
    if worst > 1e-9 or worst4 > 1e-9:
        print("CLOSED FORM DOES NOT MATCH -- stopping.")
        return

    # -- 2. exhaustive census at k=4 --------------------------------------
    from collections import Counter
    counts: Counter = Counter()
    degenerate = 0
    parity_tables = set()
    for f in range(65536):
        t = tuple((f >> i) & 1 for i in range(16))
        r = closed_form_retention(t, 4)
        if r is None:
            degenerate += 1
            continue
        counts[round(r, 9)] += 1
    vals = sorted(counts)
    par = tuple(bin(i).count("1") % 2 for i in range(16))
    parity_ret = closed_form_retention(par, 4)

    census = {
        "n_functions": 65536,
        "n_degenerate": degenerate,
        "n_scored": sum(counts.values()),
        "n_distinct_retention_values": len(vals),
        "min": round(min(vals), 6), "max": round(max(vals), 6),
        "at_exactly_half": counts.get(0.5, 0),
        "at_exactly_zero": counts.get(0.0, 0),
        "parity_retention": round(parity_ret, 9),
        "top_classes": [{"retention": round(v, 6), "count": counts[v]}
                        for v in sorted(vals, key=lambda x: -counts[x])[:12]],
    }
    report["census_k4"] = census

    # -- 3. compare against k=3 -------------------------------------------
    counts3: Counter = Counter()
    for f in range(256):
        t = tuple((f >> i) & 1 for i in range(8))
        r = closed_form_retention(t, 3)
        if r is not None:
            counts3[round(r, 9)] += 1
    report["census_k3"] = {"n_scored": sum(counts3.values()),
                           "n_distinct_retention_values": len(counts3),
                           "at_exactly_half": counts3.get(0.5, 0)}

    report["quantisation_survives"] = len(vals) < 100
    report["parity_still_unique_zero"] = (counts.get(0.0, 0) == 2)
    report["half_still_a_class"] = counts.get(0.5, 0) > 0

    out = Path(__file__).resolve().parents[1] / "results" / "exp015.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-015  written to {out}\n")
    print("CLOSED FORM:  retention = 1 - min_j Influence_j(f) / H(f)")
    print(f"  verified against brute force on all 254 non-degenerate k=3 "
          f"functions and {checked4} at k=4\n")
    print(f"CENSUS at k=3: {report['census_k3']['n_scored']} functions, "
          f"{report['census_k3']['n_distinct_retention_values']} distinct values, "
          f"{report['census_k3']['at_exactly_half']} at exactly 0.5")
    print(f"CENSUS at k=4: {census['n_scored']} functions, "
          f"{census['n_distinct_retention_values']} distinct values, "
          f"{census['at_exactly_half']} at exactly 0.5")
    print(f"  range {census['min']} .. {census['max']}")
    print(f"  functions at exactly 0: {census['at_exactly_zero']}  "
          f"(parity retention = {census['parity_retention']})")
    print("\n  largest classes at k=4:")
    for c in census["top_classes"]:
        print(f"    retention {c['retention']:.6f}  ->  {c['count']} functions")
    print(f"\nquantisation survives   : {report['quantisation_survives']}")
    print(f"parity still unique zero: {report['parity_still_unique_zero']}")
    print(f"0.5 still a class       : {report['half_still_a_class']}")


if __name__ == "__main__":
    main()
