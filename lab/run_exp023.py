"""EXP-023 -- Q-19: what is the MINIMAL sufficient invariant?

EXP-022 left a gap. The pair (influence profile, level profile) is complete at
three participants and fails at four; the full subset-indexed spectrum is
complete but is 2^k numbers. What sits between?

SETTING IT UP EXPOSED THE STRUCTURE. Define

    M[j][d]  =  sum of fhat(S)^2 over all S with |S| = d and j in S

-- how much of participant j's importance lives at interaction order d. Then

    row sums     : sum over d of M[j][d]  =  I_j          (influence profile)
    column sums  : sum over j of M[j][d]  =  d * W_d      (level profile)

THE PAIR IS EXACTLY THE TWO MARGINALS OF M. So EXP-022's finding -- that the
pair is insufficient -- is the statement that these marginals lose the joint.
Which is this project's own thesis arriving one level up, about its own
instruments. That is either a pleasing coincidence or a sign the shape is
general; either way it makes M the obvious next candidate rather than a guess.

CANDIDATES, in increasing information:
  A  influence profile alone
  B  level profile alone
  C  the pair          (marginals of M)          -- known: fails at k=4
  D  M itself          (the joint)
  E  spectrum multiset (sorted squared coefficients, NPN-invariant)
  F  D and E together
  G  full labelled spectrum up to NPN            -- complete by construction

GROUND TRUTH is the NPN orbit partition, computed by enumerating orbits rather
than canonicalising each function -- 222-ish orbits x 768 transforms instead of
65,536 x 768. Same answer, roughly 300x less work.

PREDICTIONS:
  * D beats C, because a joint beats its marginals.
  * D still incomplete -- it is a summary and summaries lose things.
  * E incomplete too; distinct functions can share a spectrum multiset.
  * so the minimal sufficient invariant is close to the labelled spectrum, and
    "relational structure" resists compression more than one would like.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from itertools import permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fourier import level_weights, spectrum          # noqa: E402
from run_exp015 import h, influences                 # noqa: E402
from run_exp022 import transform                     # noqa: E402


def npn_orbits(k: int) -> tuple[dict, int]:
    """Partition all functions into NPN orbits by orbit enumeration."""
    n_fun = 1 << (1 << k)
    cls = [-1] * n_fun
    transforms = [(p, ng, on)
                  for p in permutations(range(k))
                  for ng in range(1 << k)
                  for on in (0, 1)]
    n_classes = 0
    for f in range(n_fun):
        if cls[f] != -1:
            continue
        t = tuple((f >> i) & 1 for i in range(1 << k))
        for (p, ng, on) in transforms:
            g = transform(t, k, p, ng, on)
            idx = sum(b << i for i, b in enumerate(g))
            cls[idx] = n_classes
        n_classes += 1
    return cls, n_classes


def invariants(table, k):
    spec = spectrum(table, k)
    infl = tuple(sorted(round(x, 9) for x in influences(table, k)))
    lvl = tuple(round(x, 9) for x in level_weights(spec, k))

    # M[j][d]: participant j's weight at interaction order d
    M = [[0.0] * (k + 1) for _ in range(k)]
    for S, c in spec.items():
        for j in S:
            M[j][len(S)] += c * c
    Mcanon = tuple(sorted(tuple(round(x, 9) for x in row) for row in M))

    ms = tuple(sorted(round(c * c, 9) for c in spec.values()))
    return {
        "A_influence": infl,
        "B_level": lvl,
        "C_pair": (infl, lvl),
        "D_matrix": Mcanon,
        "E_multiset": ms,
        "F_matrix_and_multiset": (Mcanon, ms),
    }


def main() -> None:
    report = {"experiment": "EXP-023", "question": "minimal sufficient invariant"}

    for k in (3, 4):
        cls, n_classes = npn_orbits(k)
        n_fun = 1 << (1 << k)
        buckets = defaultdict(lambda: defaultdict(set))
        scored = 0
        for f in range(n_fun):
            t = tuple((f >> i) & 1 for i in range(1 << k))
            if h(sum(t) / len(t)) <= 1e-12:
                continue
            scored += 1
            inv = invariants(t, k)
            for name, val in inv.items():
                buckets[name][val].add(cls[f])

        res = {}
        for name, groups in buckets.items():
            split = sum(1 for v in groups.values() if len(v) > 1)
            res[name] = {
                "distinct_values": len(groups),
                "values_spanning_multiple_structures": split,
                "complete": split == 0,
                "worst_collision": max(len(v) for v in groups.values()),
            }
        order = ["A_influence", "B_level", "C_pair", "D_matrix",
                 "E_multiset", "F_matrix_and_multiset"]
        first_complete = next((n for n in order if res[n]["complete"]), None)
        report[f"k={k}"] = {
            "functions_scored": scored,
            "npn_classes_total": n_classes,
            "candidates": res,
            "first_complete_candidate": first_complete,
        }

    out = Path(__file__).resolve().parents[1] / "results" / "exp023.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-023  written to {out}\n")
    print("THE PAIR IS THE TWO MARGINALS OF M[j][d]:")
    print("   row sums    -> influence profile")
    print("   column sums -> level profile")
    print("   so 'the pair is insufficient' == 'these marginals lose the joint'\n")

    for k in (3, 4):
        r = report[f"k={k}"]
        print(f"k={k}: {r['functions_scored']:,} functions, "
              f"{r['npn_classes_total']} NPN classes")
        print(f"   {'candidate':<26}{'distinct':>10}{'collisions':>12}{'worst':>8}  complete")
        for name in ["A_influence", "B_level", "C_pair", "D_matrix",
                     "E_multiset", "F_matrix_and_multiset"]:
            c = r["candidates"][name]
            print(f"   {name:<26}{c['distinct_values']:>10}"
                  f"{c['values_spanning_multiple_structures']:>12}"
                  f"{c['worst_collision']:>8}  {c['complete']}")
        print(f"   -> first complete: {r['first_complete_candidate']}\n")


if __name__ == "__main__":
    main()
