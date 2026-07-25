"""EXP-009 -- criticality recovery.

CLAIM UNDER TEST:
    F-14 (cycle sign by typed composition) separates behaviour-critical
    single-edge changes from behaviour-neutral ones, where F-06a cannot.

GUARD AGAINST THE OBVIOUS CHEAT:
    Sign awareness must be DERIVED by composing relation polarities along
    cycles the structure actually contains. Polarity is declared per relation
    TYPE with the vocabulary; nothing declares which EDGE matters. If this
    passes by being told the answer, it is an impostor and belongs in
    EXP-000c, not here.

SECOND CLAIM, equally important:
    Adding sign awareness must not break the cross-domain result. A measure
    that separates critical changes but can no longer see that A and B share
    an organisation has traded one blindness for another.

NOTE ON EXP-000b's GROUND TRUTH:
    That run defined criticality against ONE cycle, hand-identified. This run
    enumerates every cycle instead of assuming. If the enumeration disagrees
    with the earlier hand-count, the earlier ground truth was wrong and says
    so here rather than being quietly kept.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from composition import cycle_signature, signature_divergence     # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from run_exp000b import LOOP, flip                                # noqa: E402
from worlds import A, B, B2, C, D, E, F                           # noqa: E402


def sig_str(sig) -> str:
    return "{" + ", ".join(f"len{k[0]}:{'+' if k[1] > 0 else '-'}×{v}"
                           for k, v in sorted(sig.items())) + "}"


def main() -> None:
    base_sig = cycle_signature(A)

    # -- 1. what cycles does A actually contain? -------------------------
    cycles_found = sum(base_sig.values())

    # -- 2. the six single-edge flips ------------------------------------
    rows = []
    for i, r in enumerate(A.relations):
        var = flip(A, i)
        div = signature_divergence(A, var)
        mdl = mdl_correspondence(A, var, DEFAULT_CODE)
        rows.append({
            "edge": f"{r.src} -{r.rtype}-> {r.dst}",
            "on_hand_identified_3cycle": (r.src, r.dst) in LOOP,
            "f14_signature_divergence": div,
            "f14_flags_as_critical": div > 0,
            "signature_after": sig_str(cycle_signature(var)),
            "mdl_ratio": round(mdl.ratio, 4),
            "mdl_gain_bits": round(mdl.gain_bits, 3),
        })

    old_truth = [r["on_hand_identified_3cycle"] for r in rows]
    new_flags = [r["f14_flags_as_critical"] for r in rows]
    agrees_with_exp000b = old_truth == new_flags

    f14_vals = {r["f14_signature_divergence"] for r in rows}
    f14_discriminates = len(f14_vals) > 1
    mdl_vals = {r["mdl_ratio"] for r in rows}
    mdl_discriminates = len(mdl_vals) > 1

    # -- 3. does sign awareness survive going cross-domain? --------------
    cross = {}
    for name, s in (("B", B), ("B2", B2), ("C", C), ("D", D), ("E", E), ("F", F)):
        cross[name] = {
            "signature": sig_str(cycle_signature(s)),
            "divergence_from_A": signature_divergence(A, s),
        }

    report = {
        "experiment": "EXP-009",
        "claim": "F-14 separates behaviour-critical from behaviour-neutral changes",
        "A_signature": sig_str(base_sig),
        "A_cycles_found": cycles_found,
        "rows": rows,
        "f14_discriminates_among_flips": f14_discriminates,
        "mdl_discriminates_among_flips": mdl_discriminates,
        "f14_agrees_with_exp000b_ground_truth": agrees_with_exp000b,
        "cross_domain": cross,
        "sign_survives_translation": cross["B"]["divergence_from_A"] == 0
                                     and cross["B2"]["divergence_from_A"] == 0,
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp009.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-009  written to {out}\n")
    print(f"A contains {cycles_found} simple cycle(s): {sig_str(base_sig)}\n")
    print(f"{'edge flipped':<32}{'EXP-000b said':>15}{'F-14 div':>10}{'MDL ratio':>11}")
    print("-" * 68)
    for r in rows:
        print(f"{r['edge']:<32}"
              f"{('critical' if r['on_hand_identified_3cycle'] else 'benign'):>15}"
              f"{r['f14_signature_divergence']:>10}"
              f"{r['mdl_ratio']:>11.4f}")

    print(f"\nF-14 discriminates among the flips: {f14_discriminates}")
    print(f"MDL  discriminates among the flips: {mdl_discriminates}")
    print(f"F-14 agrees with EXP-000b's hand-identified ground truth: {agrees_with_exp000b}")

    print("\ncross-domain -- does sign survive translation?")
    for k, v in cross.items():
        print(f"  A vs {k:<3} divergence {v['divergence_from_A']:>2}   {v['signature']}")
    print(f"\nsign survives translation (B and B2 both 0): "
          f"{report['sign_survives_translation']}")


if __name__ == "__main__":
    main()
