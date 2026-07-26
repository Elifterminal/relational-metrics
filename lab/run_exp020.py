"""EXP-020 -- the principled asymmetric census.

EXP-019's five families were CHOSEN to span influence profiles, not
enumerated. That is a sample with a taste in it, and this project has been
burned three times by test sets whose bias was invisible from inside them.

This is the systematic version: enumerate every Boolean function and classify
it by its INFLUENCE PROFILE -- the sorted tuple of per-participant influences
-- rather than by truth-table count. The profile is the right index because
retention_j = 1 - I_j / H is a function of the profile and the outcome
entropy, and of nothing else.

QUESTIONS:

  1. How many distinct influence profiles exist? If few, asymmetry is
     quantised the way retention was, and the space of "how unevenly can
     participants matter" is small and enumerable.

  2. What fraction of all functions are INFLUENCE-SYMMETRIC (spread zero)?
     This is the number that says how lucky or unlucky a careless test set
     would be.

  3. Does the influence profile ALONE determine the retention vector, or is
     the outcome entropy independent information? If profiles map to several
     H values, then two structures can have identical participant importance
     and different fragility.

  4. What is the MAXIMUM achievable spread, and what achieves it?

  5. THE BIAS, QUANTIFIED. Are the functions one can name in English
     disproportionately influence-symmetric compared with the population? If
     so, R-15 was not carelessness -- it is what naming does.

PREDICTIONS:
  1. few profiles.
  2. a minority -- symmetric functions should be rare in the population.
  3. no, H is independent information.
  4. spread 1.0, achieved by a dictator: one participant carries everything
     and at least one other is irrelevant, so losing the right one costs
     nothing and losing the wrong one costs all of it.
  5. yes, and starkly. That is the whole content of R-15.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from run_exp015 import h, influences                  # noqa: E402

NAMEABLE = {
    3: {
        "parity": lambda v: v[0] ^ v[1] ^ v[2],
        "and": lambda v: v[0] & v[1] & v[2],
        "or": lambda v: v[0] | v[1] | v[2],
        "majority": lambda v: int(sum(v) >= 2),
        "mux": lambda v: v[1] if v[0] == 0 else v[2],
        "dictator": lambda v: v[0],
        "and_or": lambda v: v[0] & (v[1] | v[2]),
        "xor_and": lambda v: v[0] ^ (v[1] & v[2]),
        "nand": lambda v: 1 - (v[0] & v[1] & v[2]),
        "at_least_one_pair": lambda v: int(sum(v) >= 2),
    },
    4: {
        "parity": lambda v: v[0] ^ v[1] ^ v[2] ^ v[3],
        "and": lambda v: v[0] & v[1] & v[2] & v[3],
        "or": lambda v: v[0] | v[1] | v[2] | v[3],
        "threshold2": lambda v: int(sum(v) >= 2),
        "threshold3": lambda v: int(sum(v) >= 3),
        "dictator": lambda v: v[0],
        "two_pairs": lambda v: (v[0] & v[1]) | (v[2] & v[3]),
        "graded": lambda v: v[0] & (v[1] | (v[2] & v[3])),
        "xor_cascade": lambda v: v[0] ^ (v[1] & (v[2] | v[3])),
    },
}


def profile_of(table, k):
    return tuple(sorted(round(i, 9) for i in influences(table, k)))


def retention_vector(table, k):
    hy = h(sum(table) / len(table))
    if hy <= 1e-12:
        return None, hy
    return [1.0 - i / hy for i in influences(table, k)], hy


def census(k: int) -> dict:
    n_fun = 1 << (1 << k)
    by_profile: dict = defaultdict(lambda: {"count": 0, "H": set(), "spreads": set()})
    sym_functions = 0
    scored = 0
    best_spread = (-1.0, None)
    for f in range(n_fun):
        t = tuple((f >> i) & 1 for i in range(1 << k))
        vec, hy = retention_vector(t, k)
        if vec is None:
            continue
        scored += 1
        prof = profile_of(t, k)
        spread = max(vec) - min(vec)
        e = by_profile[prof]
        e["count"] += 1
        e["H"].add(round(hy, 6))
        e["spreads"].add(round(spread, 6))
        if spread < 1e-12:
            sym_functions += 1
        if spread > best_spread[0]:
            best_spread = (spread, (t, prof, round(hy, 4),
                                    [round(v, 4) for v in vec]))

    profiles = {}
    multi_h = 0
    for prof, e in by_profile.items():
        if len(e["H"]) > 1:
            multi_h += 1
        profiles[str(list(prof))] = {
            "count": e["count"],
            "distinct_H": len(e["H"]),
            "distinct_spreads": sorted(e["spreads"]),
        }

    # the nameable functions
    named = {}
    for name, fn in NAMEABLE[k].items():
        t = tuple(fn(tuple((i >> b) & 1 for b in range(k))) for i in range(1 << k))
        vec, hy = retention_vector(t, k)
        if vec is None:
            continue
        named[name] = {
            "profile": [round(x, 4) for x in profile_of(t, k)],
            "spread": round(max(vec) - min(vec), 4),
            "influence_symmetric": (max(vec) - min(vec)) < 1e-12,
        }
    named_sym = sum(1 for v in named.values() if v["influence_symmetric"])

    return {
        "k": k, "scored": scored,
        "distinct_profiles": len(by_profile),
        "profiles_with_multiple_H": multi_h,
        "influence_symmetric_functions": sym_functions,
        "influence_symmetric_fraction": round(sym_functions / scored, 4),
        "max_spread": round(best_spread[0], 4),
        "max_spread_witness": {
            "profile": [round(x, 4) for x in best_spread[1][1]],
            "H": best_spread[1][2],
            "retention_vector": best_spread[1][3],
        },
        "nameable": named,
        "nameable_symmetric": named_sym,
        "nameable_total": len(named),
        "nameable_symmetric_fraction": round(named_sym / len(named), 4),
        "top_profiles": sorted(
            ({"profile": k2, **v} for k2, v in profiles.items()),
            key=lambda d: -d["count"])[:10],
    }


def main() -> None:
    report = {"experiment": "EXP-020",
              "question": "systematic census of asymmetry by influence profile"}
    for k in (3, 4):
        report[f"k={k}"] = census(k)

    c3, c4 = report["k=3"], report["k=4"]
    report["bias_factor_k3"] = round(
        c3["nameable_symmetric_fraction"] / max(c3["influence_symmetric_fraction"], 1e-9), 2)
    report["bias_factor_k4"] = round(
        c4["nameable_symmetric_fraction"] / max(c4["influence_symmetric_fraction"], 1e-9), 2)

    out = Path(__file__).resolve().parents[1] / "results" / "exp020.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-020  written to {out}\n")
    for k, c in (("k=3", c3), ("k=4", c4)):
        print(f"{k}: {c['scored']:,} functions")
        print(f"   distinct influence profiles      : {c['distinct_profiles']}")
        print(f"   profiles mapping to several H    : {c['profiles_with_multiple_H']}")
        print(f"   INFLUENCE-SYMMETRIC functions    : {c['influence_symmetric_functions']:,} "
              f"({c['influence_symmetric_fraction']*100:.1f}%)")
        print(f"   max spread                       : {c['max_spread']}  "
              f"witness profile {c['max_spread_witness']['profile']} "
              f"-> retention {c['max_spread_witness']['retention_vector']}")
        print()

    print("THE BIAS, QUANTIFIED -- functions you can name in English:")
    for k, c in (("k=3", c3), ("k=4", c4)):
        print(f"  {k}: {c['nameable_symmetric']}/{c['nameable_total']} nameable are "
              f"influence-symmetric ({c['nameable_symmetric_fraction']*100:.0f}%), "
              f"vs {c['influence_symmetric_fraction']*100:.1f}% of the population")
    print(f"  over-representation factor: {report['bias_factor_k3']}x at k=3, "
          f"{report['bias_factor_k4']}x at k=4")

    print("\n  nameable functions at k=3:")
    for n, v in c3["nameable"].items():
        mark = "  <- influence-symmetric" if v["influence_symmetric"] else ""
        print(f"    {n:<20}{str(v['profile']):<26}spread {v['spread']:.4f}{mark}")


if __name__ == "__main__":
    main()
