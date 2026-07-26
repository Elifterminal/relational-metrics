"""EXP-017 -- the reordering audit (Q-17)

Twice a parameter has changed the ORDER of results rather than their size:
  * EXP-000a -- the correspondence penalty eta reordered which structures
    counted as most similar.
  * EXP-016 -- noise reordered which structures counted as most fragile.

Two independent instances from unrelated directions is enough to stop
rediscovering it. This audits every nuisance parameter and environmental
condition in the project against one question:

    Holding everything else fixed, does varying this change the ORDER?

Magnitude errors are visible and forgivable. Order errors are invisible and
change decisions -- you act on a ranking, not on an absolute value.

METHOD. For each (measure, nuisance parameter) pair: rank a fixed set of items
at a reference parameter value and at each other value, then count discordant
pairs. Zero discordant means order-preserving. Anything above zero means the
parameter is a decision-changer and results must be reported as a curve over
it, not at a point.

AUDITS:
  A  retention  vs  arity (k=3 -> k=4), across structure families
  B  retention  vs  WHICH participant is hidden (best vs worst case)
  C  connected information  vs  sample size
  D  connected information  vs  noise level
  E  MDL correspondence  vs  description code   [known stable -- control]

E is included deliberately as a POSITIVE CONTROL. If the audit cannot show a
parameter that is order-preserving, the audit is measuring its own noise.

PREDICTIONS:
  A  stable -- the families are structurally analogous across arity.
  B  REORDERS heavily. Which participant you lose should matter enormously,
     and if so "retention" needs to be reported per-participant, not as one
     number.
  C  reorders at small n, stabilising as n grows.
  D  reorders -- consistent with EXP-016.
  E  stable, by construction (control).
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import CODES                                        # noqa: E402
from hyperworlds import WORLDS                                 # noqa: E402
from maxent import connected_information, empirical_joint      # noqa: E402
from measures import mdl_correspondence                        # noqa: E402
from run_exp015 import h, influences                           # noqa: E402
from run_exp016 import general_retention                       # noqa: E402
from worlds import A as WA, B, B2, C, D, E, F                  # noqa: E402

SEED = 20260726
TOL = 1e-9


def discordance(ref: list[float], alt: list[float]) -> dict:
    """How many pairs swap order between two scorings of the same items."""
    n = len(ref)
    conc = disc = ties = 0
    for i, j in combinations(range(n), 2):
        a, b = ref[i] - ref[j], alt[i] - alt[j]
        if abs(a) < TOL or abs(b) < TOL:
            ties += 1
            continue
        if a * b > 0:
            conc += 1
        else:
            disc += 1
    total = conc + disc
    return {"concordant": conc, "discordant": disc, "ties": ties,
            "agreement": round((conc - disc) / total, 4) if total else 1.0,
            "order_preserved": disc == 0}


def families(k: int):
    """Structure families defined at any arity, so k=3 and k=4 are comparable."""
    n = 1 << k
    def tt(fn): return tuple(fn(tuple((i >> b) & 1 for b in range(k))) for i in range(n))
    fams = {
        "parity": tt(lambda v: eval("^".join(map(str, v)))),
        "and": tt(lambda v: int(all(v))),
        "or": tt(lambda v: int(any(v))),
        "threshold2": tt(lambda v: int(sum(v) >= 2)),
        "threshold_half": tt(lambda v: int(sum(v) * 2 >= k)),
        "first_var": tt(lambda v: v[0]),
        "xor_first_two": tt(lambda v: v[0] ^ v[1]),
    }
    return fams


def main() -> None:
    report = {"experiment": "EXP-017", "question": "which parameters reorder results?"}
    audits = {}

    # -- A. retention vs arity -------------------------------------------
    f3, f4 = families(3), families(4)
    names = sorted(f3)
    r3 = [general_retention(f3[n], 3, 0.0) for n in names]
    r4 = [general_retention(f4[n], 4, 0.0) for n in names]
    keep = [i for i in range(len(names)) if r3[i] is not None and r4[i] is not None]
    audits["A_retention_vs_arity"] = {
        "items": [names[i] for i in keep],
        "reference": "k=3", "varied": "k=4",
        **discordance([r3[i] for i in keep], [r4[i] for i in keep]),
    }

    # -- B. retention vs WHICH participant is hidden ----------------------
    tables = [tuple((f >> i) & 1 for i in range(8)) for f in range(256)]
    best, worst = [], []
    for t in tables:
        ones = sum(t)
        hy = h(ones / 8)
        if hy <= 1e-12:
            continue
        infl = influences(t, 3)
        best.append(1 - min(infl) / hy)
        worst.append(1 - max(infl) / hy)
    audits["B_retention_vs_which_hidden"] = {
        "items": f"{len(best)} Boolean functions of 3 variables",
        "reference": "best case (least influential hidden)",
        "varied": "worst case (most influential hidden)",
        **discordance(best, worst),
    }

    # -- C. connected information vs sample size --------------------------
    wnames = [w.name for w in WORLDS]
    by_n = {}
    for n in (500, 2000, 8000):
        vals = []
        for w in WORLDS:
            rows, ys = w.sample(n, 0.05, SEED + n)
            vals.append(connected_information(empirical_joint(rows, ys, ("a", "b", "c")))[4])
        by_n[n] = vals
    audits["C_connected_info_vs_sample_size"] = {
        "items": wnames, "reference": "n=8000",
        "comparisons": {
            f"n={n}": discordance(by_n[8000], by_n[n]) for n in (500, 2000)
        },
    }

    # -- D. connected information vs noise --------------------------------
    by_noise = {}
    for e in (0.0, 0.05, 0.15, 0.30):
        vals = []
        for w in WORLDS:
            rows, ys = w.sample(4000, e, SEED)
            vals.append(connected_information(empirical_joint(rows, ys, ("a", "b", "c")))[4])
        by_noise[e] = vals
    audits["D_connected_info_vs_noise"] = {
        "items": wnames, "reference": "noise=0.0",
        "comparisons": {
            f"noise={e}": discordance(by_noise[0.0], by_noise[e])
            for e in (0.05, 0.15, 0.30)
        },
    }

    # -- E. MDL correspondence vs description code (POSITIVE CONTROL) -----
    targets = [("B", B), ("C", C), ("D", D), ("E", E), ("F", F), ("B2", B2)]
    by_code = {}
    for code in CODES:
        by_code[code.name] = [mdl_correspondence(WA, t, code).ratio for _, t in targets]
    ref = by_code[CODES[0].name]
    audits["E_mdl_vs_code_CONTROL"] = {
        "items": [n for n, _ in targets], "reference": CODES[0].name,
        "comparisons": {
            c.name: discordance(ref, by_code[c.name]) for c in CODES[1:]
        },
    }

    report["audits"] = audits

    # -- summary -----------------------------------------------------------
    def worst_of(a):
        if "comparisons" in a:
            return max(v["discordant"] for v in a["comparisons"].values())
        return a["discordant"]
    verdicts = {k: ("REORDERS" if worst_of(v) > 0 else "order-preserving")
                for k, v in audits.items()}
    report["verdicts"] = verdicts
    report["n_reordering"] = sum(1 for v in verdicts.values() if v == "REORDERS")
    report["control_behaved"] = verdicts["E_mdl_vs_code_CONTROL"] == "order-preserving"

    out = Path(__file__).resolve().parents[1] / "results" / "exp017.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-017  written to {out}\n")
    print("THE REORDERING AUDIT -- does varying this change the ORDER?\n")
    print(f"{'audit':<38}{'verdict':>20}{'worst discord':>16}")
    print("-" * 74)
    for k, v in audits.items():
        print(f"{k:<38}{verdicts[k]:>20}{worst_of(v):>16}")

    print("\ndetail:")
    a = audits["A_retention_vs_arity"]
    print(f"  A  k=3 vs k=4 over {len(a['items'])} families: "
          f"{a['discordant']} discordant, agreement {a['agreement']}")
    b = audits["B_retention_vs_which_hidden"]
    print(f"  B  best vs worst hidden participant: "
          f"{b['discordant']} discordant, agreement {b['agreement']}")
    for tag in ("C_connected_info_vs_sample_size", "D_connected_info_vs_noise",
                "E_mdl_vs_code_CONTROL"):
        print(f"  {tag[0]}  {tag}")
        for cmpname, v in audits[tag]["comparisons"].items():
            print(f"       {cmpname:<14} discordant {v['discordant']:>4}  "
                  f"agreement {v['agreement']:>7}")

    print(f"\n>>> parameters that reorder: {report['n_reordering']} of {len(verdicts)}")
    print(f">>> positive control behaved: {report['control_behaved']}")


if __name__ == "__main__":
    main()
