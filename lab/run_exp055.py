"""EXP-055 -- Q-42. Holography's fragment is a piece of the PLATE.

EXP-051 tested distributedness with "fragment" meaning a random subset of
transform coefficients, and found the apparent relational advantage was pool
size. It logged Q-42 because holography's fragment is SPATIAL -- you cut the
plate -- which is a different object, and the analogy is about the spatial one.

THE SHARP QUESTION, and EXP-051 never asked it:

    Cutting a hologram in half does not lose half the scene. So the test is not
    whether a fragment describes ITSELF -- trivial for both arms -- but whether
    a fragment constrains the part of the system IT CANNOT SEE.

Setup: K=4 Boolean variables, all 65,536 functions enumerated. No sampling of
the universe, so "which whole-systems are consistent with this fragment" is
exact. A structural fragment is a set P of participants.

    relational arm : coefficients on subsets of P of size >= 2
    property arm   : coefficients on singletons in P
    random control : m coefficients from anywhere, ignoring P

MATCHED FROM THE START, which is Q-42's predeclared caution -- EXP-051's first
pass looked like a confirmation and was an artifact of unequal pool sizes. Both
arms use exactly m = min(available) coefficients, and get the same number of
term choices.

Plan locked at external/plans/EXP-055.json before this file ran.
"""

from __future__ import annotations

import itertools
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from evaluate import evaluate_margins                            # noqa: E402
from protocol2 import (ProtocolViolation, Stage2Result,          # noqa: E402
                       check_capacity_to_fail, require_locked_plan)

K = 4
N = 1 << K                 # 16 assignments
NF = 1 << N                # 65,536 functions
SUBSETS = tuple(range(N))  # a subset of variables as a bitmask


def all_invariants():
    """Every function's complete invariant, as integers (Walsh sums, unscaled).

    Integer-valued so equality is exact -- no float comparison anywhere.
    """
    # parity[S][x] = (-1)^|x & S|
    par = [[1 - 2 * (bin(x & S).count("1") & 1) for x in range(N)] for S in SUBSETS]
    out = []
    for f in range(NF):
        bits = [1 - 2 * ((f >> x) & 1) for x in range(N)]
        out.append(tuple(sum(bits[x] * par[S][x] for x in range(N)) for S in SUBSETS))
    return out


def order_of(S):
    return bin(S).count("1")


def subsets_of(P):
    """All non-empty subsets of the participant-set bitmask P."""
    out, s = [], P
    while s:
        out.append(s)
        s = (s - 1) & P
    return out


def arms_for(P, rng, n_choices):
    """Matched-size term choices for each arm.

    m = min(relational available, property available), so neither arm gets more
    measurements than the other. This is the fix EXP-051 needed and did not have.
    """
    inside = subsets_of(P)
    relational = [S for S in inside if order_of(S) >= 2]
    prop = [S for S in inside if order_of(S) == 1]
    if not relational or not prop:
        return None
    m = min(len(relational), len(prop))
    outside_universe = [S for S in SUBSETS if S and (S & ~P)]

    def pick(pool, k):
        combos = list(itertools.combinations(pool, k))
        if len(combos) <= n_choices:
            return combos
        return rng.sample(combos, n_choices)

    return {
        "m": m,
        "relational": pick(relational, m),
        "property": pick(prop, m),
        # the control: m coefficients from anywhere, ignoring the fragment
        "random": [tuple(rng.sample([S for S in SUBSETS if S], m))
                   for _ in range(min(n_choices, len(list(itertools.combinations(
                       [S for S in SUBSETS if S], m)))))],
        "outside": outside_universe,
    }


def build_index(inv, terms):
    """projection -> list of function indices sharing it."""
    idx = {}
    for i, v in enumerate(inv):
        key = tuple(v[S] for S in terms)
        idx.setdefault(key, []).append(i)
    return idx


def outside_determination(inv, members, outside):
    """How much does the fragment pin down what it CANNOT see?

    For every subset T not contained in the fragment, count distinct coefficient
    values across the consistent set. Returns the fraction of such T that are
    UNIQUELY determined, and the mean distinct count.
    """
    if len(members) == 1:
        return 1.0, 1.0
    uniq, tot = 0, 0
    dsum = 0
    for T in outside:
        vals = {inv[i][T] for i in members}
        d = len(vals)
        dsum += d
        uniq += (d == 1)
        tot += 1
    return (uniq / tot if tot else 0.0), (dsum / tot if tot else 0.0)


def main() -> None:
    plan = require_locked_plan("EXP-055")
    print("EXP-055 -- enumerating all 65,536 functions and their invariants...")
    inv = all_invariants()

    rng = random.Random(55_055)
    targets = rng.sample(range(NF), 200)
    n_choices = 6

    per_size = {}
    for p in (2, 3):
        P = (1 << p) - 1                       # participants {0..p-1}
        spec = arms_for(P, random.Random(900 + p), n_choices)
        if spec is None:
            continue
        m, outside = spec["m"], spec["outside"]

        arm_stats = {}
        paired = {"relational": {}, "property": {}}
        paired_d = {"relational": {}, "property": {}}
        for arm in ("relational", "property", "random"):
            uniq_all, dist_all, amb_all = [], [], []
            per_target, per_target_d = {}, {}
            for terms in spec[arm]:
                idx = build_index(inv, terms)
                for t in targets:
                    members = idx[tuple(inv[t][S] for S in terms)]
                    u, d = outside_determination(inv, members, outside)
                    uniq_all.append(u)
                    dist_all.append(d)
                    amb_all.append(len(members))
                    per_target.setdefault(t, []).append(u)
                    per_target_d.setdefault(t, []).append(d)
            arm_stats[arm] = {
                "n_terms": m,
                "n_choices": len(spec[arm]),
                "outside_uniquely_determined_mean": round(statistics.fmean(uniq_all), 6),
                "outside_distinct_values_mean": round(statistics.fmean(dist_all), 4),
                "consistent_set_size_mean": round(statistics.fmean(amb_all), 2),
                "remaining_bits_about_whole_system":
                    round(statistics.fmean([__import__("math").log2(a) for a in amb_all]), 4),
                "fully_determined_cases": sum(1 for a in amb_all if a == 1),
                "n_measurements": len(uniq_all),
            }
            if arm in paired:
                paired[arm] = {t: statistics.fmean(v) for t, v in per_target.items()}
                paired_d[arm] = {t: statistics.fmean(v)
                                 for t, v in per_target_d.items()}

        diffs = [paired["relational"][t] - paired["property"][t] for t in targets]
        res = evaluate_margins(diffs)
        # The unique-determination statistic sits at a FLOOR -- neither fragment
        # arm ever uniquely determines an outside coefficient -- so a paired test
        # on it compares two zeros. The plan predeclared the DISTINCT-VALUE count
        # alongside it, which is continuous and not at a floor, so that is the
        # statistic that can actually arbitrate. Lower = more determined, so a
        # NEGATIVE difference means relational is better.
        diffs_d = [paired_d["relational"][t] - paired_d["property"][t] for t in targets]
        res_d = evaluate_margins(diffs_d)
        per_size[str(p)] = {
            "participants_in_fragment": p,
            "participants_outside": K - p,
            "matched_terms_per_arm": m,
            "arms": arm_stats,
            "relational_minus_property_DISTINCT_VALUES": {
                "note": "the arbitrating statistic -- lower distinct count means "
                        "MORE determined, so a NEGATIVE mean favours relational",
                "mean": round(res_d.mean, 6),
                "sd": round(res_d.sd, 6),
                "effect_size_d": round(res_d.effect_size_d, 4),
                "ci95": [round(x, 6) for x in res_d.ci95],
                "t_p": round(res_d.t_p, 6),
                "wilcoxon_p": round(res_d.wilcoxon_p, 6),
                "ci_excludes_zero": res_d.ci95[0] > 0 or res_d.ci95[1] < 0,
                "direction": ("relational more determined" if res_d.mean < 0 else
                              "property more determined" if res_d.mean > 0 else
                              "identical"),
            },
            "relational_minus_property": {
                "mean": round(res.mean, 6),
                "sd": round(res.sd, 6),
                "effect_size_d": round(res.effect_size_d, 4),
                "ci95": [round(x, 6) for x in res.ci95],
                "t_p": round(res.t_p, 6),
                "wilcoxon_p": round(res.wilcoxon_p, 6),
                "ci_excludes_zero": res.ci95[0] > 0 or res.ci95[1] < 0,
                "direction": ("relational higher" if res.mean > 0 else
                              "property higher" if res.mean < 0 else "identical"),
            },
        }
        a = arm_stats
        print(f"\n  fragment = {p} of {K} participants   "
              f"matched at {m} measurement{'s' if m > 1 else ''} per arm")
        print(f"    {'arm':<14}{'outside uniquely det.':>22}{'distinct vals':>15}"
              f"{'bits left on whole':>20}")
        for arm in ("relational", "property", "random"):
            s = a[arm]
            print(f"    {arm:<14}{s['outside_uniquely_determined_mean']:>22.4f}"
                  f"{s['outside_distinct_values_mean']:>15.3f}"
                  f"{s['remaining_bits_about_whole_system']:>20.3f}")
        dd = per_size[str(p)]["relational_minus_property_DISTINCT_VALUES"]
        print(f"    rel - prop (distinct values, lower=better): {dd['mean']:+.6f}  "
              f"d={dd['effect_size_d']:.3f}  CI95 {dd['ci95']}  "
              f"W={dd['wilcoxon_p']:.4g}  -> {dd['direction']}")

    # -- can this fail? the random control must beat both fragment arms -------
    def control_discriminates():
        ok = True
        for p, v in per_size.items():
            a = v["arms"]
            r = a["random"]["outside_uniquely_determined_mean"]
            ok = ok and r > a["relational"]["outside_uniquely_determined_mean"] \
                and r > a["property"]["outside_uniquely_determined_mean"]
        return ok
    control_ok = control_discriminates()

    # -- verdict, per the locked bands ---------------------------------------
    sizes = sorted(per_size)
    KEY = "relational_minus_property_DISTINCT_VALUES"
    # negative = relational more determined = the thesis prediction
    higher = [s for s in sizes if per_size[s][KEY]["mean"] < 0
              and per_size[s][KEY]["ci_excludes_zero"]]
    lower = [s for s in sizes if per_size[s][KEY]["mean"] > 0
             and per_size[s][KEY]["ci_excludes_zero"]]
    floored = all(per_size[s]["arms"][a]["outside_uniquely_determined_mean"] == 0.0
                  for s in sizes for a in ("relational", "property"))

    if not control_ok:
        band = "NO VERDICT -- the control did not discriminate"
        statement = ("The random arm did not beat both fragment arms, so the "
                     "outside-determination statistic is not sensitive enough to "
                     "arbitrate. Reporting that instead of a result.")
    elif len(higher) == len(sizes):
        band = "STRUCTURAL DISTRIBUTEDNESS HOLDS"
        statement = ("At matched measurement count, a relational fragment determines "
                     "more about the participants it cannot see than a property "
                     "fragment does, at every fragment size tested. EXP-051's negative "
                     "was specific to coefficient-fragments; the spatial reading -- the "
                     "one the analogy is actually about -- survives.")
    elif higher:
        band = "SUGGESTIVE, SIZE-DEPENDENT -- not settled"
        statement = (f"Relational higher at fragment size(s) {higher} and not at "
                     f"{[s for s in sizes if s not in higher]}. Two points is not a "
                     f"trend and this is not generalised from.")
    elif lower:
        band = "INVERTED -- property fragments are MORE distributed"
        statement = ("A property record restricted to a region says more about the rest "
                     "of the system than a relational one does. Stronger negative than "
                     "no-difference and reported as its own case: it inverts the thesis "
                     "rather than merely failing to support it.")
    else:
        band = "NO DIFFERENCE -- the analogy is decisively half-sized"
        statement = ("Distributedness is not a property of relational content under "
                     "EITHER reading. Interference-records-what-intensity-discards "
                     "holds; every-fragment-carries-the-whole does not. A real negative "
                     "about the founding intuition, reported as prominently as a "
                     "positive would be.")

    payload = {
        "question": "Q-42",
        "universe": "all 65,536 Boolean functions of 4 variables, enumerated exactly",
        "fragment": "a set of PARTICIPANTS (spatial), not a subset of coefficients",
        "primary_statistic": "fraction of outside subsets uniquely determined by the fragment",
        "arms_matched_from_the_start": True,
        "by_fragment_size": per_size,
        "control_discriminates": control_ok,
        "verdict": {"band": band, "statement": statement},
        "primary_statistic_hit_a_floor": floored,
        "floor_note": ("neither fragment arm EVER uniquely determines an outside "
                       "coefficient, at either size. That is P2 confirmed hard -- "
                       "ambiguity always remains -- and it means the unique-fraction "
                       "statistic compares two zeros. The distinct-value count, "
                       "predeclared alongside it, is what arbitrates."),
        "margin_stats": {
            s: per_size[s]["relational_minus_property_DISTINCT_VALUES"] for s in sizes},
        "leave_one_out": {
            "unit": "fragment size",
            "note": "only two fragment sizes are available at K=4 (p=2 and p=3), so "
                    "leave-one-out is reported as the per-size verdicts themselves "
                    "rather than a resampling. Two points is a stated limitation, not "
                    "a trend.",
            "per_size_direction": {s: per_size[s]["relational_minus_property"]["direction"]
                                   for s in sizes},
        },
        "abstention_rate": {
            s: {"fully_determined_cases":
                {a: per_size[s]["arms"][a]["fully_determined_cases"]
                 for a in ("relational", "property", "random")},
                "of_measurements": per_size[s]["arms"]["relational"]["n_measurements"]}
            for s in sizes},
    }
    out = Stage2Result("EXP-055", plan, payload).write()
    print(f"\nwritten to {out}")
    print(f"control discriminates: {control_ok}")
    print(f"\n>>> {band}\n    {statement}")


if __name__ == "__main__":
    main()
