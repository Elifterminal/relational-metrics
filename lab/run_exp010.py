"""EXP-010 -- the observer's moves, measured.

EXP-012 left one gap: the calibration protects against outcome-IRRELEVANT
structure but not against a badly CHOSEN outcome. Nothing in the mathematics
says what to condition on. That is the last unexamined observer move.

The temptation is to answer it philosophically. Instead: the observer makes
three concrete choices, and each can be varied while holding the world fixed.
If the answer moves, the size of the movement IS the answer.

  PROBE A -- WHICH QUESTION.  One fixed system of participants; several
      legitimate outcomes to ask about. How much does the structural verdict
      depend on which one you pick?

  PROBE B -- WHICH PARTICIPANTS YOU CAN SEE.  The same dependence, observed
      with one participant missing. This is the projection stack made
      concrete (C-30..C-32): the gap between accessible and resolved.

  PROBE C -- IS THERE AN INVARIANT CORE?  Any structural claim that survives
      every legitimate choice of outcome. If one exists it is the
      observer-free residue the theory has been reaching for.

PREDICTIONS, written before running:

  A -- verdicts vary a lot. There is no such thing as "the structure of this
       system" without naming a question.
  B -- a CLIFF, not a slope. Three-way structure observed with two of its
       three participants should be not merely weakened but ERASED, because
       marginalising parity over one variable leaves it uniform. If so, no
       amount of data recovers it: an identifiability limit (P-06), not a
       power limit.
  C -- the only outcome-invariant structure is participant-internal, which
       EXP-012 showed the calibration correctly rejects as non-answers. So:
       no observer-free RELEVANT structure. If that holds, relational claims
       must always name their question, and that is a property of the theory
       rather than a shortcoming of the instrument.

FALSIFICATION:
  If B is a slope rather than a cliff, partial observation degrades gracefully
  and the projection stack's second arrow is far less dangerous than claimed.
  If C finds an invariant relevant core, the theory admits observer-free
  structure after all and P-01 needs rewriting.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from maxent import connected_information, empirical_joint      # noqa: E402

N = 8000
NOISE = 0.05
SEED = 20260726
N_PERM = 120
DRIVERS = ("a", "b", "c")


def world(n: int, seed: int) -> list[dict]:
    """ONE fixed system of participants, shared by every probe.

    a, b, c independent. d is a XOR b, so the participants carry genuine
    three-way structure among THEMSELVES, independent of any question.
    """
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        a, b, c = rng.randint(0, 1), rng.randint(0, 1), rng.randint(0, 1)
        rows.append({"a": a, "b": b, "c": c, "d": a ^ b})
    return rows


def noisy(y: int, rng: random.Random) -> int:
    return 1 - y if rng.random() < NOISE else y


QUESTIONS = {
    "parity_abc": ("Y = a XOR b XOR c", lambda r: r["a"] ^ r["b"] ^ r["c"]),
    "just_a":     ("Y = a", lambda r: r["a"]),
    "and_ab":     ("Y = a AND b", lambda r: r["a"] & r["b"]),
    "majority":   ("Y = majority(a,b,c)", lambda r: 1 if r["a"] + r["b"] + r["c"] >= 2 else 0),
    "parity_ab":  ("Y = a XOR b", lambda r: r["a"] ^ r["b"]),
    "unrelated":  ("Y = an independent coin", lambda r: None),
}


def outcomes(rows: list[dict], key: str, seed: int) -> list[int]:
    _, fn = QUESTIONS[key]
    rng = random.Random(seed)
    if key == "unrelated":
        return [rng.randint(0, 1) for _ in rows]
    return [noisy(fn(r), rng) for r in rows]


def calibrated(rows, ys, drivers, order, n_perm, seed) -> tuple[float, float]:
    p = empirical_joint(rows, ys, drivers)
    obs = connected_information(p)[order]
    rng = random.Random(seed)
    sh = list(ys)
    ge = 0
    for _ in range(n_perm):
        rng.shuffle(sh)
        if connected_information(empirical_joint(rows, sh, drivers))[order] >= obs:
            ge += 1
    return obs, (ge + 1) / (n_perm + 1)


def main() -> None:
    rows = world(N, SEED)

    # -- participant-internal structure: computed with NO outcome at all ---
    p_only = {}
    joint = {}
    for r in rows:
        key = (r["a"], r["b"], r["d"])
        joint[key] = joint.get(key, 0) + 1 / N
    for k in [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]:
        joint.setdefault(k, 0.0)
    ic_participants = connected_information(joint)
    p_only = {str(k): round(v, 4) for k, v in ic_participants.items()}

    # -- PROBE A: which question --------------------------------------------
    probe_a = {}
    for key, (desc, _) in QUESTIONS.items():
        ys = outcomes(rows, key, SEED)
        p = empirical_joint(rows, ys, DRIVERS)
        ic = connected_information(p)
        verdict_order, verdict_p = None, 1.0
        for order in (4, 3, 2):
            v, pv = calibrated(rows, ys, DRIVERS, order, N_PERM, SEED)
            if pv < 0.05 and (verdict_order is None or order > verdict_order):
                verdict_order, verdict_p = order, pv
        probe_a[key] = {
            "question": desc,
            "I_C": {str(k): round(v, 4) for k, v in ic.items()},
            "significant_order": verdict_order,
            "p": round(verdict_p, 4),
        }

    # -- PROBE B: which participants you can see ---------------------------
    ys3 = outcomes(rows, "parity_abc", SEED)
    full_obs, full_p = calibrated(rows, ys3, DRIVERS, 4, N_PERM, SEED)
    partial_obs, partial_p = calibrated(rows, ys3, ("a", "b"), 3, N_PERM, SEED)
    partial2_obs, partial2_p = calibrated(rows, ys3, ("a", "c"), 3, N_PERM, SEED)

    # does MORE DATA rescue the partial view? the identifiability question
    rescue = {}
    for big_n in (8000, 40000):
        r2 = world(big_n, SEED + big_n)
        y2 = outcomes(r2, "parity_abc", SEED)
        o, pv = calibrated(r2, y2, ("a", "b"), 3, 60, SEED)
        rescue[str(big_n)] = {"I_C_top": round(o, 5), "p": round(pv, 4)}

    probe_b = {
        "all_three_participants": {"I_C(4)": round(full_obs, 4), "p": round(full_p, 4)},
        "missing_c": {"I_C(3)": round(partial_obs, 5), "p": round(partial_p, 4)},
        "missing_b": {"I_C(3)": round(partial2_obs, 5), "p": round(partial2_p, 4)},
        "more_data_rescue": rescue,
        "is_a_cliff": partial_obs < 0.01 and partial_p >= 0.05,
    }

    # -- PROBE C: invariant core -------------------------------------------
    orders = [v["significant_order"] for v in probe_a.values()]
    distinct = sorted({o for o in orders if o is not None})
    any_invariant = len(distinct) == 1 and None not in orders
    probe_c = {
        "significant_orders_across_questions": orders,
        "distinct_verdicts": distinct,
        "any_outcome_invariant_relevant_claim": any_invariant,
        "participant_internal_I_C": p_only,
        "note": "participant-internal structure is outcome-invariant by "
                "construction and is exactly what EXP-012 showed the "
                "calibration rejects as a non-answer",
    }

    report = {"experiment": "EXP-010", "n": N, "n_permutations": N_PERM,
              "probe_a_which_question": probe_a,
              "probe_b_which_participants": probe_b,
              "probe_c_invariant_core": probe_c}
    out = Path(__file__).resolve().parents[1] / "results" / "exp010.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-010  written to {out}\n")
    print("PROBE A -- one system, different questions")
    print(f"  {'question':<26}{'I_C(2)':>9}{'I_C(3)':>9}{'I_C(4)':>9}{'verdict':>12}")
    for k, v in probe_a.items():
        vo = v["significant_order"]
        print(f"  {v['question']:<26}{v['I_C']['2']:>9.4f}{v['I_C']['3']:>9.4f}"
              f"{v['I_C']['4']:>9.4f}{('order ' + str(vo)) if vo else 'none':>12}")

    print("\nPROBE B -- the same dependence, one participant missing")
    print(f"  all three : I_C(4) = {full_obs:.4f}   p = {full_p:.4f}")
    print(f"  missing c : I_C(3) = {partial_obs:.5f}   p = {partial_p:.4f}")
    print(f"  missing b : I_C(3) = {partial2_obs:.5f}   p = {partial2_p:.4f}")
    print("  does more data rescue the partial view?")
    for n, v in rescue.items():
        print(f"    n={n:<7} I_C_top = {v['I_C_top']:.5f}  p = {v['p']:.4f}")
    print(f"  CLIFF (erased, not weakened): {probe_b['is_a_cliff']}")

    print("\nPROBE C -- is there an outcome-invariant relevant claim?")
    print(f"  significant orders across questions: {orders}")
    print(f"  distinct verdicts: {distinct}")
    print(f"  any invariant relevant claim: {any_invariant}")
    print(f"  participant-internal I_C (no outcome at all): {p_only}")


if __name__ == "__main__":
    main()
