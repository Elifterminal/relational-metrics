"""EXP-051 -- does relational structure have the SECOND holographic property?

Run to the plan locked at 9ea05492.

Holography has two properties. The first is that interference records what
intensity discards -- verified as C-01, structure no pairwise view contains.
The second is DISTRIBUTEDNESS: cut a hologram in half and you get the whole
scene at reduced resolution, not half a scene.

This tests the second, which nobody has, and which is the sharper claim.

    intensity recording  = each thing's own properties (single-variable terms)
    interference record  = the relations (subset-indexed invariant, all orders)
    a fragment           = a random subset of those measurements
    the claim            = a fragment of the interference record still describes
                           the WHOLE object, degrading in resolution not coverage
"""

from __future__ import annotations

import itertools
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protocol2 import require_locked_plan                         # noqa: E402

K = 4
N = 1 << K
RNG = random.Random(51510727)


def subset_invariant(f):
    """The complete invariant from C-06: one number per subset of variables.

    For a Boolean function f (a tuple of N outputs), the coefficient on subset S
    is its Walsh-Hadamard coefficient -- exactly the standard complete
    description, one term per subset.
    """
    out = {}
    for S in range(N):
        acc = 0
        for x in range(N):
            par = bin(x & S).count("1") & 1
            acc += (1 - 2 * f[x]) * (1 - 2 * par)
        out[S] = acc / N
    return out


def order_of(S):
    return bin(S).count("1")


def main() -> None:
    plan = require_locked_plan("EXP-051")

    # a sample of Boolean functions of 4 variables
    funcs = []
    seen = set()
    while len(funcs) < 400:
        f = tuple(RNG.randrange(2) for _ in range(N))
        if f in seen:
            continue
        seen.add(f)
        funcs.append(f)

    inv = {f: subset_invariant(f) for f in funcs}
    degenerate = [f for f in funcs if all(abs(v) < 1e-12 for k, v in inv[f].items() if k)]
    funcs = [f for f in funcs if f not in set(degenerate)]

    ALL = [S for S in range(N) if S != 0]                # every non-empty subset
    ORDER1 = [S for S in ALL if order_of(S) == 1]        # single-variable terms

    def classes(fragment):
        """how many distinct systems this fragment can tell apart"""
        sig = {}
        for f in funcs:
            key = tuple(round(inv[f][S], 9) for S in fragment)
            sig.setdefault(key, []).append(f)
        return len(sig)

    full = classes(ALL)
    fractions = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)
    rows = []
    for fr in fractions:
        k_rel = max(1, round(fr * len(ALL)))
        k_prop = max(1, round(fr * len(ORDER1)))
        rel = statistics.fmean(classes(RNG.sample(ALL, k_rel)) / full for _ in range(40))
        prop = statistics.fmean(classes(RNG.sample(ORDER1, k_prop)) / full for _ in range(40))
        rows.append({"fraction": fr, "n_relational_terms": k_rel,
                     "n_property_terms": k_prop,
                     "relational_discrimination": round(rel, 4),
                     "property_discrimination": round(prop, 4)})

    prop_ceiling = classes(ORDER1) / full
    rel_at_half = next(r["relational_discrimination"] for r in rows if r["fraction"] == 0.5)
    graceful = rel_at_half > 0.5 * 1.0 and rows[-1]["relational_discrimination"] > 0.95
    ceiling_real = prop_ceiling < 0.95

    if not ceiling_real:
        verdict = ("NO CONTRAST -- property measurements discriminate nearly as well as "
                   "relational ones on this class, so the analogy has nothing to bite on here")
    elif graceful and ceiling_real:
        verdict = ("DISTRIBUTED -- relational fragments degrade gracefully toward full "
                   "discrimination while property measurements hit a hard ceiling. The "
                   "second holographic property holds on this class of systems")
    else:
        verdict = ("NOT DISTRIBUTED -- relational fragments do not degrade gracefully. "
                   "Discrimination sits concentrated rather than spread, and the "
                   "holographic analogy fails at its second property")

    report = {"experiment": "EXP-051",
              "plan_locked_at": plan["_locked_at"], "plan_sha256": plan["_sha256"],
              "systems": len(funcs), "excluded_degenerate": len(degenerate),
              "distinct_under_full_invariant": full,
              "property_ceiling": round(prop_ceiling, 4),
              "rows": rows, "verdict": verdict}
    (Path(__file__).resolve().parents[1] / "results" / "exp051.json").write_text(
        json.dumps(report, indent=2))

    print(f"\nEXP-051   plan locked at {plan['_locked_at'][:8]}\n")
    print(f"{len(funcs)} systems, {len(degenerate)} degenerate excluded, "
          f"{full} distinguishable under the full invariant\n")
    print(f"  {'fragment':>10}{'relational terms':>19}{'RELATIONAL':>13}{'PROPERTY':>11}")
    for r in rows:
        print(f"  {r['fraction']:>10.0%}{r['n_relational_terms']:>19}"
              f"{r['relational_discrimination']:>13.3f}{r['property_discrimination']:>11.3f}")
    print(f"\n  property measurements, ALL of them : {prop_ceiling:.3f}   <- the ceiling")
    print(f"\n>>> {verdict}")


if __name__ == "__main__":
    main()
