"""EXP-011 -- F-04a against F-04's acceptance test.

F-04 was demoted by EXP-002 for conflating synergy with redundancy at
arity >= 3. The acceptance test for any replacement was written down then,
before the replacement existed:

    <= 0 (or negligible) on `redundant`, and ~0.73 on `order3`.

F-04a is connected information via the maximum-entropy hierarchy. The route
through partial information decomposition was closed by reading it: for three
or more sources, antichain-lattice PID is provably impossible.

CLAIM 1 -- the acceptance test passes.
CLAIM 2 -- the ORDER is read off, not assumed. `Y = a XOR b` should show its
           structure at order 3 and nothing at order 4; `Y = a XOR b XOR c`
           should show it at order 4. If both look the same, the measure
           reports "not pairwise" and nothing more, which is not enough.
CLAIM 3 -- the same permutation discipline as EXP-002. A statistic that has
           not been calibrated against a null is not a result.

FALSIFICATION:
    If `redundant` produces order-4 connected information comparable to
    `order3`, F-04a has inherited F-04's defect and should be demoted too.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hyperworlds import WORLDS                                    # noqa: E402
from interaction import omega                                     # noqa: E402
from maxent import (connected_information, empirical_joint,       # noqa: E402
                    synergy_at_full_order)

DRIVERS = ("a", "b", "c")
N = 5000
NOISE = 0.05
SEED = 20260725
N_PERM = 120        # fewer than EXP-002: each draw runs IPF at four orders


def perm_null(rows, ys, n_perm: int, seed: int) -> dict:
    rng = random.Random(seed)
    shuffled = list(ys)
    vals = []
    for _ in range(n_perm):
        rng.shuffle(shuffled)
        p = empirical_joint(rows, shuffled, DRIVERS)
        vals.append(connected_information(p)[4])
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / max(len(vals) - 1, 1)
    return {"mean": mean, "sd": var ** 0.5, "values": vals}


def main() -> None:
    results = {}
    for world in WORLDS:
        rows, ys = world.sample(N, NOISE, SEED + N)
        prof = synergy_at_full_order(rows, ys, DRIVERS)
        null = perm_null(rows, ys, N_PERM, SEED)
        obs = prof["connected"]["4"]
        n_ge = sum(1 for v in null["values"] if v >= obs)
        p_val = (n_ge + 1) / (N_PERM + 1)
        results[world.name] = {
            "true_arity": world.true_arity,
            "connected": prof["connected"],
            "order4": obs,
            "order3": prof["connected"]["3"],
            "order2": prof["connected"]["2"],
            "null_mean_order4": round(null["mean"], 4),
            "order4_calibrated": round(obs - null["mean"], 4),
            "p_value": round(p_val, 4),
            "significant": p_val < 0.05,
            "omega_F04": round(omega(rows, ys, DRIVERS), 4),
        }

    r = results
    acceptance = (r["order3"]["order4_calibrated"] > 0.5
                  and r["redundant"]["order4_calibrated"] < 0.05)
    reads_order = (r["order2"]["order3"] > r["order2"]["order4"]
                   and r["order3"]["order4"] > r["order3"]["order3"])
    fixes_f04 = (r["redundant"]["omega_F04"] > 0.05
                 and r["redundant"]["order4_calibrated"] < 0.05)

    report = {
        "experiment": "EXP-011",
        "claim": "F-04a passes the acceptance test F-04 failed",
        "n": N, "noise": NOISE, "n_permutations": N_PERM,
        "results": results,
        "acceptance_test_passes": acceptance,
        "reads_off_the_order": reads_order,
        "fixes_the_F04_defect": fixes_f04,
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp011.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-011  written to {out}")
    print(f"n={N}, noise={NOISE}, {N_PERM} permutations\n")
    hdr = (f"{'world':<12}{'arity':>6}{'I_C(2)':>9}{'I_C(3)':>9}{'I_C(4)':>9}"
           f"{'calib':>9}{'p':>8}{'F-04 Om':>10}")
    print(hdr); print("-" * len(hdr))
    for name, d in results.items():
        star = " *" if d["significant"] else ""
        print(f"{name:<12}{d['true_arity']:>6}{d['order2']:>9.4f}"
              f"{d['order3']:>9.4f}{d['order4']:>9.4f}"
              f"{d['order4_calibrated']:>9.4f}{d['p_value']:>8.4f}"
              f"{d['omega_F04']:>10.4f}{star}")

    print(f"\nacceptance test (order3 high, redundant ~0): {acceptance}")
    print(f"reads off the ORDER of the dependence      : {reads_order}")
    print(f"fixes the exact defect that demoted F-04   : {fixes_f04}")
    print(f"\n  redundant: F-04 Omega = {r['redundant']['omega_F04']:.4f}  ->  "
          f"F-04a I_C(4) = {r['redundant']['order4_calibrated']:.4f}")
    print(f"  order3   : F-04 Omega = {r['order3']['omega_F04']:.4f}  ->  "
          f"F-04a I_C(4) = {r['order3']['order4_calibrated']:.4f}")


if __name__ == "__main__":
    main()
