"""EXP-000b -- criticality blindness.

EXP-000a showed MDL correspondence ranks the near-miss E below the true
analogue B, and locates the differing edge. Good. But locating a difference
is not the same as registering that the difference MATTERS.

CLAIM UNDER TEST:
    MDL correspondence charges the same number of bits for every single-edge
    change, regardless of whether that change inverts the system's behaviour.

GROUND TRUTH (constructed, therefore exact):
    A contains one directed cycle:  flow -> erosion -> capacity -> flow.
    The sign of the loop is the product of its edge signs. All three are POS,
    so the loop is REINFORCING -- runaway.
    Flip any ONE of those three edges and the loop becomes SELF-LIMITING.
    Flip any of the other three edges and the loop is untouched.

    So: 3 of 6 single-edge flips are behaviour-critical, 3 are not. A measure
    that cannot separate those two groups is measuring topology, not
    organisation.

FALSIFICATION:
    If MDL gain differs between the critical and non-critical groups, the
    claim is wrong and the measure is more capable than expected.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                       # noqa: E402
from measures import mdl_correspondence, tunable_K   # noqa: E402
from structure import Structure                      # noqa: E402
from worlds import A, POS, NEG                       # noqa: E402

LOOP = [("flow", "erosion"), ("erosion", "capacity"), ("capacity", "flow")]


def flip(struct: Structure, i: int) -> Structure:
    """Return a copy with relation i's type inverted. Nothing else moves."""
    rels = list(struct.relations)
    r = rels[i]
    rels[i] = replace(r, rtype=NEG if r.rtype == POS else POS)
    return Structure(name=f"{struct.name}~flip{i}", nodes=struct.nodes,
                     relations=tuple(rels), domain=struct.domain)


def loop_sign(struct: Structure) -> str:
    """Product of signs around the reinforcing cycle."""
    lookup = {(r.src, r.dst): r.rtype for r in struct.relations}
    sign = 1
    for edge in LOOP:
        t = lookup.get(edge)
        if t is None:
            return "broken"
        sign *= 1 if t == POS else -1
    return "reinforcing" if sign > 0 else "self-limiting"


def main() -> None:
    base_behaviour = loop_sign(A)
    rows = []
    for i, r in enumerate(A.relations):
        variant = flip(A, i)
        mdl = mdl_correspondence(A, variant, DEFAULT_CODE)
        k = tunable_K(A, variant, 0.5)
        behaviour = loop_sign(variant)
        rows.append({
            "edge": f"{r.src} -{r.rtype}-> {r.dst}",
            "on_loop": (r.src, r.dst) in LOOP,
            "behaviour_after_flip": behaviour,
            "behaviour_changed": behaviour != base_behaviour,
            "mdl_gain_bits": round(mdl.gain_bits, 3),
            "tunable_K_eta0.5": round(k.score, 6),
            "matched": mdl.matched,
        })

    critical = [r for r in rows if r["behaviour_changed"]]
    benign = [r for r in rows if not r["behaviour_changed"]]

    mdl_crit = sorted({r["mdl_gain_bits"] for r in critical})
    mdl_benign = sorted({r["mdl_gain_bits"] for r in benign})
    separable = not (set(mdl_crit) & set(mdl_benign))

    report = {
        "experiment": "EXP-000b",
        "claim": "MDL charges the same bits for behaviour-critical and "
                 "behaviour-neutral single-edge changes",
        "base_behaviour": base_behaviour,
        "rows": rows,
        "n_critical": len(critical),
        "n_benign": len(benign),
        "mdl_gains_critical": mdl_crit,
        "mdl_gains_benign": mdl_benign,
        "mdl_separates_critical_from_benign": separable,
        "tunable_gains_critical": sorted({r["tunable_K_eta0.5"] for r in critical}),
        "tunable_gains_benign": sorted({r["tunable_K_eta0.5"] for r in benign}),
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp000b.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-000b  written to {out}\n")
    print(f"A's loop is {base_behaviour}\n")
    print(f"{'edge':<32} {'on loop':<9} {'after flip':<15} {'MDL bits':>9}")
    print("-" * 70)
    for r in rows:
        mark = "  <-- CRITICAL" if r["behaviour_changed"] else ""
        print(f"{r['edge']:<32} {str(r['on_loop']):<9} "
              f"{r['behaviour_after_flip']:<15} {r['mdl_gain_bits']:>9.2f}{mark}")
    print()
    print(f"critical flips ({len(critical)}): MDL gains {mdl_crit}")
    print(f"benign flips   ({len(benign)}): MDL gains {mdl_benign}")
    print(f"\nDoes MDL separate them? {separable}")


if __name__ == "__main__":
    main()
