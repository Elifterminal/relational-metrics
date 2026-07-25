"""EXP-013 -- is the partial-observation cliff general? (Q-15)

EXP-010 found that hiding one participant of a three-way dependence takes the
measured structure from 0.7246 to 0.00000, and that five times the data does
not recover it. That was stated as a governing constraint on applications.

But it was measured on PARITY -- the maximally synergistic function there is,
built so that no subset of its inputs carries ANY information. Parity is the
worst case by construction. Generalising a constraint from its worst case is
how a true finding becomes a false rule.

THREE SWEEPS, holding the question fixed and varying what the world is like.

  1. ARITY -- does the cliff hold at 4 participants as well as 3?
  2. STRUCTURE TYPE -- parity has no lower-order leakage. AND, OR, majority
     and threshold functions do. Do they degrade instead of vanishing?
  3. INVOLVEMENT STRENGTH -- a participant that matters only sometimes.
     Sweeping that from irrelevant to essential gives the SHAPE of the
     degradation directly.

PRIMARY METRIC is retention of outcome-relevant information, not a p-value:

    retention = I(Y ; visible participants) / I(Y ; all participants)

0 means erased, 1 means nothing lost. EXP-010 taught that significance is not
effect size and at these sample sizes a permutation test will flag arbitrarily
small effects, so effect size leads here and p-values are reported alongside
rather than instead.

PREDICTIONS, written before running:

  1. Parity cliffs at every arity. Retention 0 regardless of k.
  2. AND / OR / majority DEGRADE rather than vanish -- retention well above 0
     -- because their lower-order marginals carry real signal.
  3. Involvement sweep is a SMOOTH CURVE, not a step.
  4. THEREFORE THE CLIFF IS NOT GENERAL. The honest statement becomes: the
     more purely synergistic a structure, the more completely partial
     observation destroys it. A gradient, with parity at one end. If that
     holds, EXP-010's claim was true and over-generalised, and it needs
     narrowing on the study page.

FALSIFICATION: if AND / OR / majority also retain ~0, the cliff IS general and
EXP-010's stronger claim stands as written.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from interaction import mutual_information                    # noqa: E402

N = 20000
NOISE = 0.05
SEED = 20260726


def sample(drivers: tuple[str, ...], rule, n: int, seed: int):
    rng = random.Random(seed)
    rows, ys = [], []
    for _ in range(n):
        row = {v: rng.randint(0, 1) for v in drivers}
        y = rule(row, rng)
        if rng.random() < NOISE:
            y = 1 - y
        rows.append(row)
        ys.append(y)
    return rows, ys


def retention(rows, ys, drivers: tuple[str, ...]) -> dict:
    """How much outcome-relevant information survives hiding one participant.

    Reported as the BEST case over which participant is hidden -- the most
    favourable reading available, so a low number cannot be an artifact of
    having hidden the single most important variable.
    """
    full = mutual_information(rows, ys, drivers)
    per_hidden = {}
    for hide in drivers:
        visible = tuple(v for v in drivers if v != hide)
        per_hidden[hide] = mutual_information(rows, ys, visible)
    best = max(per_hidden.values()) if per_hidden else 0.0
    worst = min(per_hidden.values()) if per_hidden else 0.0
    return {
        "full_bits": round(full, 4),
        "best_partial_bits": round(best, 4),
        "worst_partial_bits": round(worst, 4),
        "retention_best": round(best / full, 4) if full > 1e-9 else 0.0,
        "retention_worst": round(worst / full, 4) if full > 1e-9 else 0.0,
        "per_hidden": {k: round(v, 4) for k, v in per_hidden.items()},
    }


# -- rules ------------------------------------------------------------------

def r_parity(row, rng):
    v = 0
    for x in row.values():
        v ^= x
    return v


def r_and(row, rng):
    v = 1
    for x in row.values():
        v &= x
    return v


def r_or(row, rng):
    v = 0
    for x in row.values():
        v |= x
    return v


def r_majority(row, rng):
    vals = list(row.values())
    return 1 if sum(vals) * 2 > len(vals) else 0


def r_threshold2(row, rng):
    return 1 if sum(row.values()) >= 2 else 0


def make_leaky(w: float):
    """`c` participates only a fraction `w` of the time. At w=0 it is
    irrelevant; at w=1 this is pure three-way parity."""
    def rule(row, rng):
        if rng.random() < w:
            return row["a"] ^ row["b"] ^ row["c"]
        return row["a"] ^ row["b"]
    return rule


def main() -> None:
    report = {"experiment": "EXP-013", "n": N, "noise": NOISE,
              "metric": "retention = I(Y; visible) / I(Y; all)"}

    # -- 1. arity sweep, parity ------------------------------------------
    arity = {}
    for k in (3, 4, 5):
        drivers = tuple("abcde"[:k])
        rows, ys = sample(drivers, r_parity, N, SEED)
        arity[f"parity_k{k}"] = retention(rows, ys, drivers)
    report["sweep_arity_parity"] = arity

    # -- 2. structure-type sweep at k=3 and k=4 --------------------------
    types = {}
    for k in (3, 4):
        drivers = tuple("abcde"[:k])
        for name, rule in (("parity", r_parity), ("and", r_and), ("or", r_or),
                           ("majority", r_majority), ("threshold2", r_threshold2)):
            if name == "majority" and k % 2 == 0:
                continue                       # undefined for even k
            rows, ys = sample(drivers, rule, N, SEED)
            types[f"{name}_k{k}"] = retention(rows, ys, drivers)
    report["sweep_structure_type"] = types

    # -- 3. involvement sweep --------------------------------------------
    involvement = {}
    for w in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        rows, ys = sample(("a", "b", "c"), make_leaky(w), N, SEED)
        r = retention(rows, ys, ("a", "b", "c"))
        r["hiding_c_bits"] = r["per_hidden"]["c"]
        involvement[f"w_{w:.1f}"] = r
    report["sweep_involvement"] = involvement

    # -- verdicts ---------------------------------------------------------
    parity_all_cliff = all(v["retention_best"] < 0.02
                           for k, v in arity.items())
    nonparity = {k: v for k, v in types.items() if not k.startswith("parity")}
    nonparity_retains = all(v["retention_best"] > 0.10 for v in nonparity.values())
    inv = [involvement[f"w_{w:.1f}"]["per_hidden"]["c"]
           for w in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
    smooth = all(inv[i] >= inv[i + 1] - 1e-9 for i in range(len(inv) - 1))

    report["parity_cliffs_at_every_arity"] = parity_all_cliff
    report["non_parity_structures_retain"] = nonparity_retains
    report["involvement_curve_monotone"] = smooth
    report["involvement_curve"] = [round(v, 4) for v in inv]
    report["cliff_is_general"] = parity_all_cliff and not nonparity_retains

    out = Path(__file__).resolve().parents[1] / "results" / "exp013.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-013  written to {out}")
    print(f"n={N}, noise={NOISE}\n")

    print("1. ARITY SWEEP (parity) -- does the cliff hold as participants grow?")
    print(f"   {'world':<14}{'full':>9}{'best partial':>14}{'retention':>11}")
    for k, v in arity.items():
        print(f"   {k:<14}{v['full_bits']:>9.4f}{v['best_partial_bits']:>14.4f}"
              f"{v['retention_best']:>11.4f}")

    print("\n2. STRUCTURE TYPE -- does anything without parity's purity survive?")
    print(f"   {'world':<16}{'full':>9}{'best partial':>14}{'retention':>11}")
    for k, v in types.items():
        print(f"   {k:<16}{v['full_bits']:>9.4f}{v['best_partial_bits']:>14.4f}"
              f"{v['retention_best']:>11.4f}")

    print("\n3. INVOLVEMENT SWEEP -- c matters a fraction w of the time.")
    print(f"   {'w':<8}{'full':>9}{'hiding c':>11}{'retention':>11}")
    for w in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        v = involvement[f"w_{w:.1f}"]
        ret = v["per_hidden"]["c"] / v["full_bits"] if v["full_bits"] > 1e-9 else 0.0
        print(f"   {w:<8.1f}{v['full_bits']:>9.4f}{v['per_hidden']['c']:>11.4f}"
              f"{ret:>11.4f}")

    print(f"\nparity cliffs at every arity      : {parity_all_cliff}")
    print(f"non-parity structures retain      : {nonparity_retains}")
    print(f"involvement curve monotone/smooth : {smooth}")
    print(f"\n>>> IS THE CLIFF GENERAL?  {report['cliff_is_general']}")


if __name__ == "__main__":
    main()
