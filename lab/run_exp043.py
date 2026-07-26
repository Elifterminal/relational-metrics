"""EXP-043 -- an independent reader on real narrative prose.

WRITTEN BEFORE THE DATA ARRIVES, deliberately, alongside the plan locked at
9707f5f0. Both the analysis plan and the code that implements it are fixed and
committed before a single annotation exists.

Why that matters more than usual here. The annotations arrive through a channel
I read, so I will see them -- that is unavoidable and is not pretended
otherwise. What CAN be removed is any freedom to act on having seen them:

  * the plan is locked, so the statistic, tests, exclusion rule, robustness
    threshold and falsification bands cannot be chosen after the fact
  * this file is locked, so the code path cannot be adjusted either
  * the passages are anonymous and shuffled, so seeing an annotation does not
    tell me whether it belongs to a query, a correct answer or a distractor --
    that requires the key, which is only opened inside this script
  * it runs end to end and prints only the final report, so I never inspect an
    intermediate value that could tempt a second look

Seeing the data is a weaker problem than being able to respond to it. This
removes the second.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from evaluate import evaluate_margins                             # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from protocol2 import Stage2Result, require_locked_plan           # noqa: E402
from structure import Relation, Structure                         # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "external" / "q43"


def parse_all() -> dict:
    """Every N### line found in anything dropped into external/q43/."""
    out = {}
    for f in sorted(INBOX.glob("*.txt")):
        for line in f.read_text().splitlines():
            m = re.match(r"\s*(N\d{3})\s*:\s*(\[.*?\])", line)
            if m:
                out[m.group(1)] = ast.literal_eval(m.group(2))
    return out


def build(name, edges):
    rels = tuple(Relation(a, b, t) for a, b, t in edges)
    nodes = tuple(sorted({n for r in rels for n in (r.src, r.dst)}))
    return Structure(name, nodes, rels)


def main() -> None:
    plan = require_locked_plan("EXP-043")
    ann = parse_all()
    idmap = json.loads((ROOT / "external" / "q43_idmap.json").read_text())
    key = json.loads((ROOT / "external" / "q43_key.json").read_text())

    missing = [t for t in idmap if t not in ann]
    if len(ann) < 0.9 * len(idmap):
        print(f"only {len(ann)}/{len(idmap)} passages present -- waiting for the rest")
        print(f"missing: {missing[:10]}{' ...' if len(missing) > 10 else ''}")
        return

    # FLOOR CHECK -- required before scoring, per the Stage 2 charter addition
    dist = Counter(len(v) for v in ann.values())
    floor = min(dist)
    floor_ok = floor == 0
    abstention = round(dist.get(0, 0) / len(ann), 3)

    items = {}
    for tag, edges in ann.items():
        k = key[idmap[tag]]
        items.setdefault(k["item"], {})[k["role"]] = build(tag, edges)

    import csv
    truth = {r["id"]: int(r["correct_answer"])
             for r in csv.DictReader((ROOT / "external" / "arn.csv").open())}

    rows, excluded = [], []
    for iid, v in sorted(items.items()):
        if len(v) != 3 or any(v[r].m == 0 for r in ("Q", "A", "B")):
            excluded.append(iid)
            continue
        good = v["A"] if truth[iid] == 1 else v["B"]
        bad = v["B"] if truth[iid] == 1 else v["A"]
        rows.append({"item": iid,
                     "margin": round(mdl_correspondence(v["Q"], good, DEFAULT_CODE).ratio
                                     - mdl_correspondence(v["Q"], bad, DEFAULT_CODE).ratio, 4)})

    n_items = len(items)
    if len(rows) * 2 < n_items:
        payload = {"margin_stats": None, "leave_one_out": None,
                   "abstention_rate": abstention,
                   "verdict": (f"TEST DID NOT RUN -- {len(excluded)}/{n_items} items "
                               f"excluded. Charter falsification 3, no claim either way")}
    else:
        res = evaluate_margins([r["margin"] for r in rows])
        loo = sum(1 for i in range(len(rows))
                  if evaluate_margins([r["margin"] for j, r in enumerate(rows)
                                       if j != i]).t_p < 0.05)
        both = res.t_p < 0.05 and res.wilcoxon_p < 0.05
        if res.ci95[0] <= 0 <= res.ci95[1]:
            v = ("FAILED -- margin interval includes zero. Charter falsification 1: "
                 "automatic annotation of prose produces no signal")
        elif not both:
            v = "SUGGESTIVE ONLY -- one test above 0.05; the plan says this is not supported"
        elif loo * 2 < len(rows):
            v = "FRAGILE, NOT ESTABLISHED -- significant but leave-one-out under half"
        else:
            v = "SUPPORTED -- significant on both tests and robust to leave-one-out"
        if not floor_ok:
            v += (f" | FLOOR WARNING: the annotator never returned fewer than {floor} "
                  f"relations, so its output is suspect exactly as mine was in EXP-040")
        payload = {"margin_stats": res.as_dict(),
                   "leave_one_out": f"{loo}/{len(rows)}",
                   "abstention_rate": abstention, "verdict": v}

    payload.update({
        "passages": len(ann), "items": n_items, "scored": len(rows),
        "excluded": excluded,
        "floor_check": {"distribution": dict(sorted(dist.items())),
                        "minimum": floor, "can_abstain": floor_ok},
        "comparison": {"mechanical_on_same_text": "69% blank, 0/30 scored (EXP-042)",
                       "this_annotator_on_glosses": "effect size 0.788 (EXP-039)"},
        "rows": rows,
    })

    out = Stage2Result("EXP-043", plan, payload).write()
    print(f"\nEXP-043  written to {out}")
    print(f"plan locked at {plan['_locked_at'][:8]}, code committed before the data\n")
    print(f"passages {len(ann)}   items {n_items}   scored {len(rows)}   "
          f"excluded {len(excluded)}")
    print(f"floor check: min {floor} relations, can abstain: {floor_ok}, "
          f"blank {abstention:.0%}")
    print(f"   distribution {dict(sorted(dist.items()))}")
    if payload["margin_stats"]:
        d = payload["margin_stats"]
        print(f"\nmean margin {d['mean_margin_bits']:+.4f} bits   "
              f"95% CI [{d['ci95_on_mean'][0]:+.4f}, {d['ci95_on_mean'][1]:+.4f}]")
        print(f"effect size {d['effect_size_d']}   t {d['t_test_p']:.4f}   "
              f"Wilcoxon {d['wilcoxon_p']:.4f}   LOO {payload['leave_one_out']}")
    print(f"\n>>> {payload['verdict']}")
    print("\nPREDICTED IN ADVANCE:")
    for p in plan["predictions"]:
        print(f"   - {p['claim']}")


if __name__ == "__main__":
    main()
