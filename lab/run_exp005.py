"""EXP-005 -- cross-generator transfer. Discharging R-04.

F-06a was developed against ONE structure family and validated on conditions
derived from it. R-04 has been flagged since the measure was proposed and never
discharged: a measure tested only on the worlds it was built for may have
learned those worlds rather than the thing it claims to measure. Every
application downstream inherits that doubt, which is why this is the gate
between "works on my worlds" and "works".

CLAIM UNDER TEST:
    F-06a ranks a structurally identical, surface-different analogue above both
    a same-surface-different-structure case and a matched random one, on base
    topologies it was NOT developed against.

THE DESIGN CONTROLS THE OBVIOUS CONFOUND. The derivation of B, C and D from a
base A is IDENTICAL for every generator. The only thing that varies is the
shape of A. So a failure cannot be blamed on how the conditions were built --
it is about the topology.

The families differ in properties that plausibly matter to a correspondence
measure: presence of cycles, branching, degree concentration, path
multiplicity. One is unshaped. EXP-020 measured what happens when a test set is
assembled from whatever comes to mind, so the families were chosen against a
property list rather than by recall.

FALSIFICATION:
    If B fails to rank first on any generator other than the development one,
    F-06a learned its development family and every downstream application is
    built on n=1. That would be a demotion, not a caveat.

PREDECLARED WORRIES:
  * `hub` is highly symmetric and its rewiring may be near-isomorphic to
    itself, so C could score high for a legitimate reason rather than a
    failure. Reported separately if it happens.
  * `chain` has no cycles, which is the one property the development family was
    built around. It is the most likely genuine failure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import CODES, DEFAULT_CODE                 # noqa: E402
from generators import GENERATORS, conditions_for     # noqa: E402
from measures import mdl_correspondence               # noqa: E402

SEED = 20260726


def main() -> None:
    results = {}
    malformed = []
    for name in GENERATORS:
        cond = conditions_for(name, SEED)
        for label, st in cond.items():
            if not st.is_well_formed:
                malformed.append(f"{name}/{label}")
        a = cond["A"]
        scores = {k: mdl_correspondence(a, v, DEFAULT_CODE).ratio
                  for k, v in cond.items() if k != "A"}
        ranked = sorted(scores, key=lambda k: -scores[k])
        # stability of the ORDER across declared codes (EXP-017's standing rule)
        per_code = {}
        for c in CODES:
            sc = {k: mdl_correspondence(a, v, c).ratio
                  for k, v in cond.items() if k != "A"}
            per_code[c.name] = sorted(sc, key=lambda k: -sc[k])
        results[name] = {
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "ranking": ranked,
            "B_ranks_first": ranked[0] == "B",
            "B_beats_C": scores["B"] > scores["C"],
            "B_beats_D": scores["B"] > scores["D"],
            "graded_order_holds": (scores["B"] > scores["E"]
                                   > max(scores["C"], scores["D"])),
            "margin_over_next": round(scores[ranked[0]] - scores[ranked[1]], 4),
            "ranking_by_code": per_code,
            "ranking_stable_across_codes": len({tuple(v) for v in per_code.values()}) == 1,
        }

    dev = "motif (development family)"
    novel = [n for n in results if n != dev]
    passed = [n for n in novel if results[n]["B_ranks_first"]]
    failed = [n for n in novel if not results[n]["B_ranks_first"]]

    report = {
        "experiment": "EXP-005",
        "claim": "F-06a transfers to base topologies it was not developed against",
        "results": results,
        "development_family_passes": results[dev]["B_ranks_first"],
        "novel_families_total": len(novel),
        "novel_families_passed": len(passed),
        "novel_families_failed": failed,
        "malformed_conditions": malformed,
        "all_conditions_well_formed": not malformed,
        "transfers": len(failed) == 0,
        "graded_order_holds_everywhere":
            all(r["graded_order_holds"] for r in results.values()),
        "generators_with_graded_order":
            [n for n, r in results.items() if r["graded_order_holds"]],
        "order_stable_across_codes_everywhere":
            all(r["ranking_stable_across_codes"] for r in results.values()),
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp005.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-005  written to {out}\n")
    hdr = (f"{'generator':<30}{'B':>8}{'E':>8}{'C':>8}{'D':>8}"
           f"{'ranking':>20}{'graded':>8}")
    print(hdr); print("-" * len(hdr))
    for n, r in results.items():
        s = r["scores"]
        mark = "" if r["B_ranks_first"] else "  <-- FAILS"
        print(f"{n:<30}{s['B']:>8.4f}{s['E']:>8.4f}{s['C']:>8.4f}{s['D']:>8.4f}"
              f"{' > '.join(r['ranking']):>20}"
              f"{str(r['graded_order_holds']):>8}{mark}")

    print(f"\nall conditions well-formed       : "
          f"{report['all_conditions_well_formed']}"
          f"{'  MALFORMED: ' + str(malformed) if malformed else ''}")
    print(f"development family passes        : {report['development_family_passes']}")
    print(f"novel families passing           : {len(passed)}/{len(novel)}")
    if failed:
        print(f"FAILURES                         : {failed}")
    print(f"order stable across codes        : "
          f"{report['order_stable_across_codes_everywhere']}")
    graded = [n for n, r in results.items() if r["graded_order_holds"]]
    print(f"GRADED order B > E > C,D holds   : {len(graded)}/{len(results)}  {graded}")
    print(f"\n>>> TRANSFERS TO UNSEEN TOPOLOGIES: {report['transfers']}")


if __name__ == "__main__":
    main()
