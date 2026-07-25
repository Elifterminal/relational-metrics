"""EXP-002 -- planted higher-order recovery.

THE CLAIM THE PROJECT RESTS ON:
    Some structure exists only in configurations of three or more
    participants and is not recoverable from the pairs inside it. F-04's
    remainder is supposed to detect it.

Everything on the Findings tab so far uses arity 2. So nothing yet tests the
one claim that distinguishes this from ordinary graph similarity.

CLAIM 1 -- RECOVERY:
    Omega over {a,b,c} is large in worlds where the outcome genuinely needs
    all three, and small where it doesn't.

CLAIM 2 -- THE Q-08 NULL, which matters more:
    Omega does NOT fire where no higher-order structure was planted. Two
    nulls, and they fail differently:
      * `null`      -- outcome independent of everything.
      * `redundant` -- THREE variables all carry information about the
                       outcome and none of it is synergistic (b and c are
                       noisy copies of a). This is the hard null. Any
                       statistic that merely notices "several things are
                       involved" fires here and is worthless.

    NOTE: the first run used `majority(a,b,c)` as this null and it fired.
    Checking the truth table rather than the name showed majority is
    genuinely synergistic -- when the first two disagree the third decides
    alone -- so the null was mis-constructed, not the statistic. Reclassified
    to arity 3; `redundant` is the replacement. The error is left visible.

FALSIFICATION:
    If Omega cannot separate order3 from redundant, F-04 does not measure
    higher-order structure and should be demoted regardless of how well it
    scores on the easy cases.

PREDECLARED (before running):
    Raw Omega will fire on the nulls, because plug-in MI is upward biased and
    the bias grows with subset size, so it does not cancel across the
    alternating sum. The permutation calibration should remove it. Recording
    this here so that if it turns out wrong, it is visibly wrong.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hyperworlds import WORLDS                                  # noqa: E402
from interaction import mutual_information, omega, permutation_test  # noqa: E402

TRIPLE = ("a", "b", "c")
SAMPLE_SIZES = (200, 1000, 5000)
NOISE = 0.05
N_PERM = 400
SEED = 20260725


def subset_profile(rows, ys) -> dict:
    """What each level of the subset lattice sees on its own. This is the
    thing a pairwise-only method would have to work from."""
    singles = {v: mutual_information(rows, ys, (v,)) for v in TRIPLE}
    pairs = {f"{x}{y}": mutual_information(rows, ys, (x, y))
             for x, y in (("a", "b"), ("a", "c"), ("b", "c"))}
    triple = mutual_information(rows, ys, TRIPLE)
    return {
        "singles": {k: round(v, 4) for k, v in singles.items()},
        "pairs": {k: round(v, 4) for k, v in pairs.items()},
        "triple": round(triple, 4),
        "best_single": round(max(singles.values()), 4),
        "best_pair": round(max(pairs.values()), 4),
        "pairwise_ceiling_gap": round(triple - max(pairs.values()), 4),
    }


def main() -> None:
    results = {}
    for world in WORLDS:
        per_n = {}
        for n in SAMPLE_SIZES:
            rows, ys = world.sample(n, NOISE, SEED + n)
            test = permutation_test(rows, ys, TRIPLE, N_PERM, SEED)
            per_n[str(n)] = {
                "omega_raw": round(test["observed"], 4),
                "null_mean": round(test["null_mean"], 4),
                "omega_calibrated": round(test["calibrated"], 4),
                "z": round(test["z"], 2),
                "p_value": round(test["p_value"], 4),
                "significant": test["p_value"] < 0.05,
                "profile": subset_profile(rows, ys),
            }
        results[world.name] = {
            "true_arity": world.true_arity,
            "drivers": list(world.drivers),
            "description": world.description,
            "by_n": per_n,
        }

    # -- arity-2 control --------------------------------------------------
    # Where does the statistic break? At arity 2 the alternating sum is
    # I(ab) - I(a) - I(b), which for redundancy gives H - 2H = -H: negative,
    # correct sign. At arity 3 the same construction gives H - 3H + 3H = +H.
    # So the failure is not "Omega is broken", it is specific to arity >= 3.
    arity2 = {}
    for world in WORLDS:
        rows, ys = world.sample(SAMPLE_SIZES[-1], NOISE, SEED + SAMPLE_SIZES[-1])
        arity2[world.name] = {
            "omega_ab": round(omega(rows, ys, ("a", "b")), 4),
            "omega_abc": round(omega(rows, ys, ("a", "b", "c")), 4),
        }

    # -- verdicts ---------------------------------------------------------
    big = str(SAMPLE_SIZES[-1])
    genuine3 = ("order3", "order3_and", "majority")
    nulls = ("null", "order1", "order2", "redundant")

    raw_fires_on_nulls = [w for w in nulls
                          if results[w]["by_n"][big]["omega_raw"] > 0.01]
    cal_fires_on_nulls = [w for w in nulls
                          if results[w]["by_n"][big]["significant"]]
    detects_genuine = [w for w in genuine3
                       if results[w]["by_n"][big]["significant"]]
    separates_hard_null = (results["order3"]["by_n"][big]["significant"]
                           and not results["redundant"]["by_n"][big]["significant"])

    report = {
        "experiment": "EXP-002",
        "claim": "Omega detects planted higher-order structure and not its absence",
        "noise": NOISE, "n_permutations": N_PERM, "sample_sizes": list(SAMPLE_SIZES),
        "results": results,
        "raw_omega_fires_on_nulls": raw_fires_on_nulls,
        "calibrated_fires_on_nulls": cal_fires_on_nulls,
        "detects_genuine_higher_order": detects_genuine,
        "separates_order3_from_redundant": separates_hard_null,
        "arity2_control": arity2,
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp002.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-002  written to {out}")
    print(f"n={big}, noise={NOISE}, {N_PERM} permutations\n")
    hdr = (f"{'world':<12}{'arity':>6}{'best pair':>11}{'triple':>9}"
           f"{'raw Om':>9}{'null mu':>9}{'calib':>9}{'z':>8}{'p':>8}")
    print(hdr); print("-" * len(hdr))
    for name, r in results.items():
        d = r["by_n"][big]
        pr = d["profile"]
        star = " *" if d["significant"] else ""
        print(f"{name:<12}{r['true_arity']:>6}{pr['best_pair']:>11.4f}"
              f"{pr['triple']:>9.4f}{d['omega_raw']:>9.4f}{d['null_mean']:>9.4f}"
              f"{d['omega_calibrated']:>9.4f}{d['z']:>8.2f}{d['p_value']:>8.4f}{star}")

    print("\nraw Omega > 0.01 on nulls :", raw_fires_on_nulls or "none")
    print("calibrated significant on nulls:", cal_fires_on_nulls or "none")
    print("detects genuine 3-way     :", detects_genuine or "none")
    print("separates order3 from redundant:", separates_hard_null)

    print("\narity-2 control -- where does the sign convention break?")
    print(f"  {'world':<12}{'Omega(a,b)':>12}{'Omega(a,b,c)':>14}")
    for name, v in arity2.items():
        print(f"  {name:<12}{v['omega_ab']:>12.4f}{v['omega_abc']:>14.4f}")

    print("\nsample-size dependence of raw Omega (the estimator bias):")
    print(f"  {'world':<12}" + "".join(f"{('n=' + str(n)):>12}" for n in SAMPLE_SIZES))
    for name, r in results.items():
        vals = "".join(f"{r['by_n'][str(n)]['omega_raw']:>12.4f}" for n in SAMPLE_SIZES)
        print(f"  {name:<12}{vals}")


if __name__ == "__main__":
    main()
