"""EXP-012 -- adversarial stress test of F-04a.

F-04a passed EXP-011 on the first attempt, on worlds written by the same
party that wrote the measure. A first-try pass is grounds for suspicion, not
confidence (R-04). This tries to break it.

FIVE THINGS UNDER TEST, each with the expectation written before running.

  1. OUTCOME IRRELEVANCE -- the one I expect to FAIL.
     Connected information is a property of a JOINT DISTRIBUTION and does not
     privilege any variable. So structure existing purely among the drivers,
     orthogonal to the outcome, has no reason not to register. If it does,
     F-04a answers "are these things structured together" rather than "does
     their configuration bear on the question", and for an application those
     are very different claims.

  2. IMPLEMENTATION SYMMETRY -- I_C should be invariant to which variable is
     nominated "the outcome", since it is computed on the joint. If it is
     not, there is an axis-ordering bug.

  3. MONOTONE POWER -- a synergy-strength sweep should produce a monotone
     curve, not a threshold or a step. Otherwise the number is not a measure.

  4. NUMERICAL ROBUSTNESS -- hard zeros and skewed marginals are where IPF
     fails. Convergence residuals reported, not assumed.

  5. NULL CALIBRATION vs SAMPLE SIZE -- where does the permutation test stop
     protecting us?

FALSIFICATION:
    If (1) fires, F-04a as used is measuring the wrong thing and its scope
    claim must be rewritten or the measure conditioned. If (3) is
    non-monotone, it is not a measure of degree. If (4) diverges, results on
    sparse data are meaningless.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from maxent import (connected_information, empirical_joint,   # noqa: E402
                    entropy, marginal, maxent_matching)
from stressworlds import STRESS                               # noqa: E402

DRIVERS = ("a", "b", "c")
N = 8000
SEED = 20260726
N_PERM = 120


def perm_p(rows, ys, observed: float, order: int, n_perm: int, seed: int) -> float:
    rng = random.Random(seed)
    shuffled = list(ys)
    ge = 0
    for _ in range(n_perm):
        rng.shuffle(shuffled)
        v = connected_information(empirical_joint(rows, shuffled, DRIVERS))[order]
        if v >= observed:
            ge += 1
    return (ge + 1) / (n_perm + 1)


def ipf_residual(p, order: int) -> float:
    """Largest absolute mismatch between the fitted distribution's marginals
    and the target ones. If this is not tiny, IPF did not converge and every
    number downstream of it is noise."""
    q = maxent_matching(p, order)
    n_vars = len(next(iter(p)))
    worst = 0.0
    from itertools import combinations
    for idx in combinations(range(n_vars), order):
        tgt, got = marginal(p, idx), marginal(q, idx)
        for k, v in tgt.items():
            worst = max(worst, abs(v - got.get(k, 0.0)))
    return worst


def main() -> None:
    results = {}
    for w in STRESS:
        rows, ys = w.sample(N, SEED)
        p = empirical_joint(rows, ys, DRIVERS)
        ic = connected_information(p)
        obs4 = ic[4]
        results[w.name] = {
            "expectation": w.expectation,
            "description": w.description,
            "I_C": {str(k): round(v, 4) for k, v in ic.items()},
            "order4": round(obs4, 4),
            "order3": round(ic[3], 4),
            "order2": round(ic[2], 4),
            "p_order4": round(perm_p(rows, ys, obs4, 4, N_PERM, SEED), 4),
            "p_order3": round(perm_p(rows, ys, ic[3], 3, N_PERM, SEED), 4),
            "ipf_residual_order2": round(ipf_residual(p, 2), 8),
            "ipf_residual_order3": round(ipf_residual(p, 3), 8),
        }

    # -- 2. implementation symmetry --------------------------------------
    rows, ys = STRESS[0].sample(N, SEED)
    p = empirical_joint(rows, ys, DRIVERS)
    base = connected_information(p)
    sym = []
    for perm in list(permutations(range(4)))[:8]:
        pp = {tuple(s[i] for i in perm): v for s, v in p.items()}
        ic = connected_information(pp)
        sym.append(max(abs(ic[k] - base[k]) for k in ic))
    symmetric = max(sym) < 1e-6

    # -- 3. monotone power -----------------------------------------------
    sweep = [(w.name, results[w.name]["order4"])
             for w in STRESS if w.name.startswith("synergy_")]
    monotone = all(sweep[i][1] <= sweep[i + 1][1] + 1e-6
                   for i in range(len(sweep) - 1))

    # -- 5. null calibration vs sample size ------------------------------
    calib = {}
    null_world = [w for w in STRESS if w.name == "synergy_000"][0]
    for n in (200, 800, 3200, 8000):
        r2, y2 = null_world.sample(n, SEED + n)
        p2 = empirical_joint(r2, y2, DRIVERS)
        obs = connected_information(p2)[4]
        calib[str(n)] = {
            "order4_raw": round(obs, 4),
            "p_value": round(perm_p(r2, y2, obs, 4, N_PERM, SEED), 4),
        }

    # -- verdicts ---------------------------------------------------------
    d3 = results["driver_only_3way"]
    d2 = results["driver_only_pairwise"]
    outcome_irrelevance_ok = (d3["p_order3"] >= 0.05 and d3["p_order4"] >= 0.05
                              and d2["p_order4"] >= 0.05)
    max_resid = max(max(r["ipf_residual_order2"], r["ipf_residual_order3"])
                    for r in results.values())

    report = {
        "experiment": "EXP-012",
        "claim": "F-04a survives adversarial worlds it was not designed against",
        "n": N, "n_permutations": N_PERM,
        "results": results,
        "outcome_irrelevance_survives": outcome_irrelevance_ok,
        "implementation_symmetric": symmetric,
        "max_symmetry_drift": max(sym),
        "power_monotone": monotone,
        "power_sweep": sweep,
        "max_ipf_residual": max_resid,
        "ipf_converged": max_resid < 1e-6,
        "null_calibration_by_n": calib,
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp012.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-012  written to {out}")
    print(f"n={N}, {N_PERM} permutations\n")
    hdr = (f"{'world':<22}{'I_C(2)':>9}{'I_C(3)':>9}{'I_C(4)':>9}"
           f"{'p(3)':>8}{'p(4)':>8}")
    print(hdr); print("-" * len(hdr))
    for name, r in results.items():
        print(f"{name:<22}{r['order2']:>9.4f}{r['order3']:>9.4f}"
              f"{r['order4']:>9.4f}{r['p_order3']:>8.4f}{r['p_order4']:>8.4f}")

    print(f"\n1. outcome-irrelevance survives : {outcome_irrelevance_ok}")
    print(f"     driver_only_3way     I_C(3)={d3['order3']:.4f} p={d3['p_order3']:.4f}")
    print(f"     driver_only_pairwise I_C(2)={d2['order2']:.4f} p(4)={d2['p_order4']:.4f}")
    print(f"2. implementation symmetric     : {symmetric}  (drift {max(sym):.2e})")
    print(f"3. power monotone in strength   : {monotone}")
    for nm, v in sweep:
        print(f"     {nm:<16}{v:.4f}")
    print(f"4. IPF converged everywhere     : {max_resid < 1e-6}  (worst {max_resid:.2e})")
    print("5. null calibration by sample size:")
    for n, v in calib.items():
        print(f"     n={n:<6} raw I_C(4)={v['order4_raw']:.4f}  p={v['p_value']:.4f}")


if __name__ == "__main__":
    main()
