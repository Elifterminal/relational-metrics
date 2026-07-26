"""EXP-021 -- the interaction structure census.

EXP-020 censused how much each participant matters ON ITS OWN (influence
profile). That is a first-order quantity. It says nothing about how
participants interact WITH EACH OTHER, and the Fourier expansion shows
influence is literally a MARGINAL of the interaction structure:

    I_j = sum of fhat(S)^2 over all S containing j.

Marginals lose information. So the questions are whether the lost information
is real, and whether anything this project measures can see it.

  1. VERIFY THE MACHINERY. Fourier influence must equal the combinatorial
     influence used everywhere else. A derivation is not a result.

  2. Is interaction structure QUANTISED, like influence and retention were?

  3. ARE THE AXES INDEPENDENT? Group functions by influence profile; count
     distinct interaction profiles within each group. If more than one, then
     two structures can distribute their participant-importance identically
     while interacting completely differently.

  4. THE SHARP ONE. Retention = 1 - I_j / H depends on influence and outcome
     entropy and NOTHING ELSE. So if two functions share an influence profile
     AND an entropy, they have IDENTICAL retention vectors regardless of their
     interaction structure. Do such pairs exist, and how different can their
     interaction structure be? If they exist, the retention law -- the
     project's one predictive equation -- is PROVABLY BLIND to an entire axis
     of relational structure.

That last would matter. The whole thesis is that configurations carry
structure their parts do not, and a law that cannot see interaction structure
is measuring something narrower than the theory claims to care about. Better to
establish it deliberately than to have it surface later as a surprise.

PREDICTIONS:
  1. exact agreement.
  2. quantised, more profiles than influence had.
  3. yes, independent.
  4. yes, such pairs exist, and the blindness is total rather than partial.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fourier import (fourier_influence, interaction_profile,      # noqa: E402
                     level_weights, pair_weights, spectrum)
from run_exp015 import h, influences                              # noqa: E402


def analyse(k: int) -> dict:
    n_fun = 1 << (1 << k)
    max_infl_err = 0.0
    by_infl: dict = defaultdict(set)
    by_infl_and_H: dict = defaultdict(list)
    interaction_profiles = set()
    level_profiles = set()
    scored = 0

    for f in range(n_fun):
        t = tuple((f >> i) & 1 for i in range(1 << k))
        hy = h(sum(t) / len(t))
        spec = spectrum(t, k)

        # 1. verification
        comb = influences(t, k)
        for j in range(k):
            max_infl_err = max(max_infl_err,
                               abs(comb[j] - fourier_influence(spec, j)))

        if hy <= 1e-12:
            continue
        scored += 1
        ip = interaction_profile(spec, k)
        interaction_profiles.add(ip)
        level_profiles.add(ip[0])

        infl_prof = tuple(sorted(round(x, 9) for x in comb))
        by_infl[infl_prof].add(ip)
        by_infl_and_H[(infl_prof, round(hy, 9))].append((t, ip))

    # 3. independence of the axes
    multi = {p: len(v) for p, v in by_infl.items() if len(v) > 1}

    # 4. retention-blind witness pairs
    blind_groups = 0
    witness = None
    worst_gap = -1.0
    for (prof, hy), members in by_infl_and_H.items():
        ips = {m[1] for m in members}
        if len(ips) > 1:
            blind_groups += 1
            # how DIFFERENT can the interaction structure be, at equal retention?
            lw = [m[1][0] for m in members]
            for a in range(len(lw)):
                for b in range(a + 1, len(lw)):
                    gap = max(abs(x - y) for x, y in zip(lw[a], lw[b]))
                    if gap > worst_gap:
                        worst_gap = gap
                        ta, tb = members[a][0], members[b][0]
                        witness = {
                            "influence_profile": [round(x, 4) for x in prof],
                            "H": round(hy, 4),
                            "retention_vector": [round(1 - i / hy, 4)
                                                 for i in influences(ta, k)],
                            "fn_a_truth_table": list(ta),
                            "fn_a_level_weights": [round(x, 4) for x in
                                                   level_weights(spectrum(ta, k), k)],
                            "fn_b_truth_table": list(tb),
                            "fn_b_level_weights": [round(x, 4) for x in
                                                   level_weights(spectrum(tb, k), k)],
                            "max_level_weight_gap": round(gap, 4),
                        }

    return {
        "k": k, "scored": scored,
        "fourier_vs_combinatorial_max_error": max_infl_err,
        "machinery_verified": max_infl_err < 1e-9,
        "distinct_interaction_profiles": len(interaction_profiles),
        "distinct_level_profiles": len(level_profiles),
        "distinct_influence_profiles": len(by_infl),
        "influence_profiles_with_multiple_interaction_profiles": len(multi),
        "max_interaction_profiles_per_influence_profile":
            max(len(v) for v in by_infl.values()),
        "retention_blind_groups": blind_groups,
        "worst_witness": witness,
    }


def main() -> None:
    report = {"experiment": "EXP-021",
              "question": "can anything we measure see interaction structure?"}
    for k in (3, 4):
        report[f"k={k}"] = analyse(k)

    c3, c4 = report["k=3"], report["k=4"]
    report["axes_are_independent"] = (
        c3["influence_profiles_with_multiple_interaction_profiles"] > 0)
    report["retention_is_blind_to_interaction_structure"] = (
        c3["retention_blind_groups"] > 0)

    out = Path(__file__).resolve().parents[1] / "results" / "exp021.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-021  written to {out}\n")
    print("1. MACHINERY CHECK -- Fourier influence vs combinatorial influence")
    for k, c in (("k=3", c3), ("k=4", c4)):
        print(f"   {k}: max error {c['fourier_vs_combinatorial_max_error']:.2e}  "
              f"verified={c['machinery_verified']}")

    print("\n2/3. CENSUS")
    print(f"   {'':<44}{'k=3':>10}{'k=4':>10}")
    for lbl, key in (("functions scored", "scored"),
                     ("distinct INFLUENCE profiles", "distinct_influence_profiles"),
                     ("distinct INTERACTION profiles", "distinct_interaction_profiles"),
                     ("distinct level (order) profiles", "distinct_level_profiles"),
                     ("influence profiles with >1 interaction",
                      "influence_profiles_with_multiple_interaction_profiles"),
                     ("max interaction profiles per influence",
                      "max_interaction_profiles_per_influence_profile")):
        print(f"   {lbl:<44}{c3[key]:>10,}{c4[key]:>10,}")

    print("\n4. IS RETENTION BLIND TO INTERACTION STRUCTURE?")
    for k, c in (("k=3", c3), ("k=4", c4)):
        print(f"   {k}: {c['retention_blind_groups']:,} groups share an influence "
              f"profile AND entropy -- i.e. identical retention -- "
              f"while differing in interaction structure")
    w = c3["worst_witness"] or c4["worst_witness"]
    if w:
        print("\n   worst k=3 witness pair:")
        print(f"     identical retention vector : {w['retention_vector']}")
        print(f"     influence profile          : {w['influence_profile']}   H={w['H']}")
        print(f"     function A level weights   : {w['fn_a_level_weights']}")
        print(f"     function B level weights   : {w['fn_b_level_weights']}")
        print(f"     max level-weight gap       : {w['max_level_weight_gap']}")

    print(f"\n>>> axes independent                       : {report['axes_are_independent']}")
    print(f">>> retention blind to interaction structure: "
          f"{report['retention_is_blind_to_interaction_structure']}")


if __name__ == "__main__":
    main()
