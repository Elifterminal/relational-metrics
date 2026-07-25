"""EXP-000c -- the harness self-test proper.

CLAIM UNDER TEST:
    The condition set plus its controls can separate a genuine correspondence
    measure from methods that cheat.

This is NOT a test of any formula. It is a test of the laboratory. Protocol
section 6: if the harness cannot distinguish a relational method from these
impostors, the harness is not ready and no result from it counts.

FALSIFICATION:
    If any impostor passes every control, the harness is incomplete and the
    specific gap must be named -- not waved at.

Note the asymmetry that makes this honest: I am trying to make the impostors
PASS. A self-test where the author roots for the controls proves nothing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from impostors import IMPOSTOR_NAMES, build_registry     # noqa: E402
from worlds import A, B, B2, C, D, E, F                  # noqa: E402

SPREAD_FLOOR = 0.02      # below this a method is not discriminating at all


def controls(method, name: str) -> dict:
    """Six controls. A method must pass all six to be admitted."""
    s = {k: method(A, v) for k, v in
         {"B": B, "C": C, "D": D, "E": E, "F": F, "B2": B2}.items()}
    dev = {k: s[k] for k in ("B", "C", "D", "E", "F")}
    spread = max(dev.values()) - min(dev.values())

    c1 = s["B"] > max(s["C"], s["D"], s["E"], s["F"])  # ranks the true analogue top
    c2 = s["B"] > s["C"]                                # not reading vocabulary
    c3 = s["D"] == min(dev.values())                    # rejects the null
    c4 = spread > SPREAD_FLOOR                          # discriminates at all
    c5 = s["B2"] > max(s["C"], s["D"])                  # works on a structure never seen
    c6 = s["B"] > s["F"]                                # not fooled by a superset

    checks = {
        "C1_ranks_true_analogue_top": bool(c1),
        "C2_sees_past_vocabulary": bool(c2),
        "C3_rejects_matched_random": bool(c3),
        "C4_discriminates_at_all": bool(c4),
        "C5_generalises_to_heldout": bool(c5),
        "C6_rejects_superset_distractor": bool(c6),
    }
    return {
        "scores": {k: round(v, 4) for k, v in s.items()},
        "spread": round(spread, 4),
        "checks": checks,
        "passed_all": all(checks.values()),
        "failed": [k for k, v in checks.items() if not v],
        "is_impostor": name in IMPOSTOR_NAMES,
    }


def main() -> None:
    # The memoriser is primed on the development conditions only. B2 is held
    # out, exactly as a real leak would leave one case uncovered.
    registry = build_registry([(B, 1.0), (C, 0.3), (D, 0.1), (E, 0.8)])

    results = {name: controls(fn, name) for name, fn in registry.items()}

    impostors_caught = {n: r for n, r in results.items()
                        if r["is_impostor"] and not r["passed_all"]}
    impostors_missed = {n: r for n, r in results.items()
                        if r["is_impostor"] and r["passed_all"]}
    candidates_passed = {n: r for n, r in results.items()
                         if not r["is_impostor"] and r["passed_all"]}

    n_imp = sum(1 for r in results.values() if r["is_impostor"])
    report = {
        "experiment": "EXP-000c",
        "claim": "the condition set separates real measures from cheats",
        "spread_floor": SPREAD_FLOOR,
        "results": results,
        "n_impostors": n_imp,
        "n_impostors_caught": len(impostors_caught),
        "impostors_missed": sorted(impostors_missed),
        "candidates_passing": sorted(candidates_passed),
        "harness_ready": len(impostors_missed) == 0,
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp000c.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-000c  written to {out}\n")
    hdr = f"{'method':<18}{'C1':>4}{'C2':>4}{'C3':>4}{'C4':>4}{'C5':>4}{'C6':>4}   verdict"
    print(hdr)
    print("-" * len(hdr))
    for name, r in results.items():
        marks = "".join(f"{'  ✓' if v else '  ✗':>4}" for v in r["checks"].values())
        kind = "impostor" if r["is_impostor"] else "candidate"
        if r["is_impostor"]:
            verdict = "CAUGHT" if not r["passed_all"] else "*** MISSED ***"
        else:
            verdict = "admitted" if r["passed_all"] else "rejected"
        print(f"{name:<18}{marks}   {verdict} ({kind})")

    print(f"\nimpostors caught: {len(impostors_caught)}/{n_imp}")
    if impostors_missed:
        print(f"MISSED: {sorted(impostors_missed)}")
    print(f"candidates admitted: {sorted(candidates_passed)}")
    print(f"\nHARNESS READY: {report['harness_ready']}")


if __name__ == "__main__":
    main()
