"""EXP-019 -- the asymmetric families, and what they expose.

R-15: every function family used through EXP-013..016 had retention spread of
exactly zero, so a best-case summary looked harmless when it was not. Three
published corrections trace to it. asymworlds.py is the fix; this checks that
the fix actually fixes something.

FOUR QUESTIONS:

  1. Do the new families actually exercise the spread the old ones could not?
     A test set that fails to change the answer is decoration.

  2. Does the closed form still hold on them? It was derived and verified on a
     symmetric-heavy set. If it only worked there, that would be the fourth
     correction of the same shape.

  3. Does the MUX control behave -- permutation-asymmetric, influence-
     symmetric, zero spread? If so, R-15's wording is wrong and needs
     sharpening from "symmetric" to "influence-symmetric".

     NOTE ADDED AFTER THE FIRST RUN: this experiment found a real indexing bug
     on its first execution -- two conventions for "participant j" that
     disagree by a reversal. Aggregating over participants hid it entirely, so
     no published result is affected. The point worth keeping: MUX shows zero
     error under BOTH the correct and the reversed comparison, because all its
     per-participant values are identical. A symmetric test family is
     STRUCTURALLY INCAPABLE of detecting an index reversal. R-15 was not a
     stylistic preference.

  4. Would including these families from the start have caught the error
     earlier? Concretely: does the best-case summary that EXP-013..016 used
     visibly misreport them?

PREDICTIONS:
  1. yes, spreads 0.5 to 0.75.
  2. yes, exactly -- the law is per-participant and makes no symmetry
     assumption anywhere.
  3. yes, and that is the real content of the correction.
  4. yes, badly -- xor_cascade_k4 best-case reads 0.75 while one participant
     loss takes it to 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from asymworlds import FAMILIES                       # noqa: E402
from run_exp015 import brute_mi, h, influences        # noqa: E402
from run_exp018 import per_participant                # noqa: E402


def brute_per_participant(table, k):
    """Brute-force retention per participant, in BIT-POSITION order.

    Two indexing conventions collided here and it took an asymmetric family to
    notice. `influences()` indexes by bit position: participant j is bit
    1<<j of the truth-table index. `brute_mi` builds its patterns with
    itertools.product, which puts the LAST tuple slot on the LOWEST bit -- so
    pattern position p corresponds to bit k-1-p, exactly reversed.

    Aggregating over participants (min, max) hides this completely, which is
    why EXP-015's verification passed and why no published number is affected:
    every result so far was a best or worst case. It would have bitten the
    moment anything was reported per-participant -- which EXP-018 has just
    made mandatory.
    """
    full = brute_mi(table, k, tuple(range(k)), 0.0)
    if full <= 1e-12:
        return None
    out = []
    for j in range(k):                      # j = bit position
        drop = k - 1 - j                    # -> pattern position
        visible = tuple(x for x in range(k) if x != drop)
        out.append(brute_mi(table, k, visible, 0.0) / full)
    return out


def main() -> None:
    rows = {}
    worst_err = 0.0
    for f in FAMILIES:
        closed = per_participant(f.table, f.k)
        brute = brute_per_participant(f.table, f.k)
        err = max(abs(a - b) for a, b in zip(closed, brute))
        worst_err = max(worst_err, err)
        rows[f.name] = {
            "k": f.k, "expression": f.expression,
            "influence_profile": f.influence_profile,
            "why_it_is_here": f.why_it_is_here,
            "retention_per_participant": [round(v, 4) for v in closed],
            "best": round(max(closed), 4),
            "worst": round(min(closed), 4),
            "spread": round(max(closed) - min(closed), 4),
            "vanishes_under_worst_loss": min(closed) < 1e-9,
            "closed_form_error": err,
        }

    exercised = [n for n, r in rows.items() if r["spread"] > 1e-9]
    mux = rows["mux"]
    report = {
        "experiment": "EXP-019",
        "question": "do the asymmetric families expose what the symmetric ones hid?",
        "families": rows,
        "n_with_nonzero_spread": len(exercised),
        "max_spread": max(r["spread"] for r in rows.values()),
        "closed_form_max_error": worst_err,
        "closed_form_still_holds": worst_err < 1e-9,
        "mux_is_permutation_asymmetric_but_influence_symmetric":
            mux["spread"] < 1e-9,
        "families_that_vanish_under_worst_loss":
            [n for n, r in rows.items() if r["vanishes_under_worst_loss"]],
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp019.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-019  written to {out}\n")
    print(f"{'family':<16}{'expression':<26}{'retention per participant':<34}"
          f"{'best':>7}{'worst':>7}{'spread':>8}")
    print("-" * 98)
    for n, r in rows.items():
        print(f"{n:<16}{r['expression']:<26}"
              f"{str(r['retention_per_participant']):<34}"
              f"{r['best']:>7.4f}{r['worst']:>7.4f}{r['spread']:>8.4f}")

    print(f"\n1. families exercising nonzero spread : "
          f"{len(exercised)} of {len(rows)}  (max spread {report['max_spread']})")
    print(f"2. closed form still exact            : "
          f"{report['closed_form_still_holds']}  (max error {worst_err:.2e})")
    print(f"3. MUX permutation-asymmetric yet zero spread: "
          f"{report['mux_is_permutation_asymmetric_but_influence_symmetric']}")
    print(f"4. families that VANISH under the worst loss : "
          f"{report['families_that_vanish_under_worst_loss']}")

    print("\nWHAT A BEST-CASE SUMMARY WOULD HAVE REPORTED:")
    for n, r in rows.items():
        if r["spread"] > 1e-9:
            print(f"  {n:<16} best-case says {r['best']:.4f}  |  "
                  f"true range {r['worst']:.4f} .. {r['best']:.4f}")


if __name__ == "__main__":
    main()
