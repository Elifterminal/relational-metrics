"""EXP-000a -- the penalty pathology.

CLAIM UNDER TEST (protocol section 1.1):
    In the tunable correspondence measure F-06, the penalty parameter eta
    determines the ORDERING of results, not merely their magnitude. There
    exists a value of eta at which a structurally identical cross-domain
    analogue is ranked below a same-vocabulary structure that does not share
    its organisation.

INTENDED SIGNAL (1.2):
    A crossing in the eta-curves. Not a difference in scores -- a reversal of
    rank.

FALSIFICATION (1.6):
    If no crossing exists anywhere in eta >= 0, the hazard described in Q-06
    is not real for this measure and Q-06 should be downgraded.

STATUS: this is a hazard demonstration, not a validation of anything. It
tests a METHOD for a known failure, which is what protocol section 6 asks
for before any result is trusted. Rung: 1 (mathematically coherent) at most.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import CODES, DEFAULT_CODE                    # noqa: E402
from measures import mdl_correspondence, tunable_K       # noqa: E402
from structure import Structure                          # noqa: E402
from worlds import A, CONDITIONS                         # noqa: E402

ETAS = [round(0.02 * i, 3) for i in range(0, 76)]        # 0.00 .. 1.50


def eta_curves() -> dict:
    """F-06 across the penalty range, for every condition against A."""
    out: dict[str, list[float]] = {}
    detail: dict[str, dict] = {}
    for key, (struct, _, _) in CONDITIONS.items():
        if key == "A":
            continue
        scores = []
        for eta in ETAS:
            r = tunable_K(A, struct, eta)
            scores.append(round(r.score, 6))
        out[key] = scores
        r0 = tunable_K(A, struct, 0.0)
        detail[key] = {"matched_at_eta0": r0.matched, "of": r0.total,
                       "complexity": r0.complexity}
    return {"etas": ETAS, "curves": out, "detail": detail}


def find_reversals(curves: dict) -> list[dict]:
    """Where does the ranking of two conditions swap as eta moves?"""
    etas, cur = curves["etas"], curves["curves"]
    keys = sorted(cur)
    found = []
    for i, k1 in enumerate(keys):
        for k2 in keys[i + 1:]:
            a, b = cur[k1], cur[k2]
            for j in range(1, len(etas)):
                before = a[j - 1] - b[j - 1]
                after = a[j] - b[j]
                if before > 1e-9 > after or before < -1e-9 < after:
                    found.append({
                        "pair": [k1, k2],
                        "eta": etas[j],
                        "winner_below": k1 if before > 0 else k2,
                        "winner_above": k1 if after > 0 else k2,
                    })
                    break
    return found


def mdl_table() -> dict:
    """F-06a across every declared code. If the ranking moves between codes,
    MDL has merely relocated the dial and Q-06 is not answered."""
    rows: dict[str, dict] = {}
    for code in CODES:
        per_code = {}
        for key, (struct, _, _) in CONDITIONS.items():
            if key == "A":
                continue
            r = mdl_correspondence(A, struct, code)
            per_code[key] = {
                "gain_bits": round(r.gain_bits, 3),
                "baseline_bits": round(r.baseline_bits, 3),
                "mapping_bits": round(r.mapping_bits, 3),
                "conditional_bits": round(r.conditional_bits, 3),
                "matched": r.matched, "of": r.total,
                "ranking_key": round(r.gain_bits, 6),
            }
        ranked = sorted(per_code, key=lambda k: -per_code[k]["ranking_key"])
        rows[code.name] = {"scores": per_code, "ranking": ranked}
    rankings = {c: rows[c]["ranking"] for c in rows}
    stable = len({tuple(v) for v in rankings.values()}) == 1
    return {"by_code": rows, "ranking_stable_across_codes": stable}


def _control_can_fail(name: str) -> bool:
    """Perturb the property this variant holds fixed; the measure must move.

    Only `rescale` has a property that could be silently ignored -- the others
    permute labels or ordering, which the measure demonstrably reads. For
    rescale: change ONE weight (not all of them, which is the invariance) and
    require a different answer.
    """
    if name != "rescale_x1000":
        return True
    from dataclasses import replace as _replace
    perturbed = Structure(
        A.name, A.nodes,
        tuple(_replace(r, weight=(50.0 if i == 0 else r.weight))
              for i, r in enumerate(A.relations)), A.domain)
    base = mdl_correspondence(A, A, DEFAULT_CODE).gain_bits
    moved = mdl_correspondence(A, perturbed, DEFAULT_CODE).gain_bits
    return abs(base - moved) > 1e-9


def invariance_battery() -> dict:
    """F-07. Change only the DESCRIPTION and require the measure not to move.

    Any movement beyond floating-point tolerance is a finding: the measure is
    reading its own encoding rather than the structure (P-08).
    """
    relabel = {v: f"z{i}" for i, v in enumerate(A.nodes)}
    variants: dict[str, Structure] = {
        "identity": A,
        "relabel": A.relabel(relabel),
        "reorder": A.reorder([4, 0, 3, 1, 2]),
        "reserialize": A.reserialize([5, 2, 0, 4, 1, 3]),
        "rescale_x1000": A.rescale(1000.0),
    }
    base_mdl = mdl_correspondence(A, A, DEFAULT_CODE).gain_bits
    base_k = tunable_K(A, A, 0.5).score

    results = {}
    for name, var in variants.items():
        g = mdl_correspondence(A, var, DEFAULT_CODE).gain_bits
        k = tunable_K(A, var, 0.5).score
        # Is this control capable of failing? EXP-031 found `rescale` was not:
        # F-06a dropped weights entirely, so no weight change could move it, and
        # blindness had been published as invariance since this file first ran.
        # Q-28 added the weight channel, so rather than hardcode the answer --
        # which would go stale exactly as the last note did -- vacuity is now
        # MEASURED: perturb the property under test and require the measure to
        # notice. A control that cannot fail is not a control (protocol 4b).
        vacuous = not _control_can_fail(name)
        results[name] = {
            "vacuous_for_mdl": vacuous,
            "vacuity_note": ("the measure does not respond to the property this "
                             "control varies, so passing proves nothing "
                             "-- see EXP-031") if vacuous else "",
            "mdl_gain_bits": round(g, 6),
            "mdl_delta": round(g - base_mdl, 9),
            "tunable_K_eta0.5": round(k, 6),
            "tunable_delta": round(k - base_k, 9),
            "mdl_invariant": abs(g - base_mdl) < 1e-6,
            "tunable_invariant": abs(k - base_k) < 1e-6,
        }
    return {"baseline_mdl_bits": round(base_mdl, 6),
            "baseline_tunable": round(base_k, 6),
            "variants": results,
            "all_mdl_invariant": all(v["mdl_invariant"] for v in results.values()),
            "all_tunable_invariant": all(v["tunable_invariant"] for v in results.values())}


def near_miss_localisation() -> dict:
    """Condition E asks more than 'is it different'. It asks whether the
    measure can say WHERE, and whether it registers that the difference
    matters. Magnitude and significance are not the same question."""
    r = mdl_correspondence(A, CONDITIONS["E"][0], DEFAULT_CODE)
    nm, tm = dict(r.node_map), dict(r.type_map)
    predicted = {(nm[e.src], nm[e.dst], tm[e.rtype]) for e in A.relations}
    actual = CONDITIONS["E"][0].edge_set()
    return {
        "gain_bits": round(r.gain_bits, 3),
        "matched": r.matched, "of": r.total,
        "predicted_but_absent": sorted(map(list, predicted - actual)),
        "present_but_unpredicted": sorted(map(list, actual - predicted)),
        "located": bool(predicted - actual),
    }


def main() -> None:
    curves = eta_curves()
    report = {
        "experiment": "EXP-000a",
        "claim": "eta determines RANK, not only magnitude, in F-06",
        "conditions": {k: {"description": v[1], "requirement": v[2],
                           "n": v[0].n, "m": v[0].m, "domain": v[0].domain}
                       for k, v in CONDITIONS.items()},
        "tunable": curves,
        "reversals": find_reversals(curves),
        "mdl": mdl_table(),
        "invariance": invariance_battery(),
        "near_miss": near_miss_localisation(),
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp000a.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    # -- console summary ---------------------------------------------------
    print(f"\nEXP-000a  written to {out}\n")
    print("REVERSALS FOUND:", len(report["reversals"]))
    for r in report["reversals"]:
        print(f"  {r['pair'][0]} vs {r['pair'][1]}: "
              f"{r['winner_below']} wins below eta={r['eta']}, "
              f"{r['winner_above']} wins above")

    print("\nMDL gain (bits), default code 'gamma':")
    for k, v in report["mdl"]["by_code"]["gamma"]["scores"].items():
        print(f"  A -> {k}: {v['gain_bits']:>8.2f} bits   "
              f"matched {v['matched']}/{v['of']}")
    print("  ranking:", " > ".join(report["mdl"]["by_code"]["gamma"]["ranking"]))
    print("  stable across codes:", report["mdl"]["ranking_stable_across_codes"])
    for c in report["mdl"]["by_code"]:
        print(f"    {c:8s} ->", " > ".join(report["mdl"]["by_code"][c]["ranking"]))

    print("\nInvariance (F-07):")
    print("  MDL invariant across all description changes:",
          report["invariance"]["all_mdl_invariant"])
    print("  tunable K invariant across all description changes:",
          report["invariance"]["all_tunable_invariant"])

    print("\nNear-miss (condition E):")
    nm = report["near_miss"]
    print(f"  matched {nm['matched']}/{nm['of']}, gain {nm['gain_bits']} bits")
    print(f"  difference located: {nm['located']}")
    print(f"  predicted but absent:      {nm['predicted_but_absent']}")
    print(f"  present but unpredicted:   {nm['present_but_unpredicted']}")


if __name__ == "__main__":
    main()
