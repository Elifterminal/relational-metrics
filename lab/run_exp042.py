"""EXP-042 -- can a fully automatic annotator read real prose?

Run strictly to the plan locked at e50590d6. The plan predicts FAILURE, in
advance and in writing. It is run anyway because it is automatic, costs nothing,
and establishes the floor any better annotator has to beat.

The annotator satisfies all three Stage 2 rules: it is not me (S2-1), it has no
floor and can abstain (S2-2, established in Q-39), and it is applied to real
narratives rather than tidy glosses (S2-3).
"""

from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from arn_blind import hard_cell, reveal                           # noqa: E402
from codes import DEFAULT_CODE                                    # noqa: E402
from evaluate import evaluate_margins                             # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from mechanical import extract                                    # noqa: E402
from protocol2 import Stage2Result, require_locked_plan           # noqa: E402
from structure import Relation, Structure                         # noqa: E402

SEED = 42420726


def build(name, edges):
    rels = tuple(Relation(a, b, t) for a, b, t in edges)
    nodes = tuple(sorted({n for r in rels for n in (r.src, r.dst)}))
    return Structure(name, nodes, rels)


def main() -> None:
    plan = require_locked_plan("EXP-042")

    burned = {k["item_id"] for k in reveal()["key"] if "item_id" in k}
    pool = [r for r in hard_cell() if r["id"] not in burned]
    sample = random.Random(SEED).sample(pool, plan["data"]["sample"])

    rows, excluded, empties = [], [], 0
    for it in sample:
        parts = {
            "Q": extract(it["query_narrative"]),
            "A": extract(it["first_choice"]),
            "B": extract(it["second_choice"]),
        }
        empties += sum(1 for v in parts.values() if not v)
        if any(not v for v in parts.values()):
            excluded.append({"item": it["id"],
                             "empty": [k for k, v in parts.items() if not v]})
            continue
        q = build(it["id"] + "Q", parts["Q"])
        good = build("g", parts["A"] if int(it["correct_answer"]) == 1 else parts["B"])
        bad = build("b", parts["B"] if int(it["correct_answer"]) == 1 else parts["A"])
        rows.append({
            "item": it["id"],
            "relations": [len(parts["Q"]), good.m, bad.m],
            "margin": round(mdl_correspondence(q, good, DEFAULT_CODE).ratio
                            - mdl_correspondence(q, bad, DEFAULT_CODE).ratio, 4),
        })

    n_sample = len(sample)
    abstention = round(empties / (3 * n_sample), 3)

    if len(rows) * 2 < n_sample:
        payload = {
            "margin_stats": None, "leave_one_out": None,
            "abstention_rate": abstention,
            "verdict": (f"TEST DID NOT RUN -- {len(excluded)} of {n_sample} items "
                        f"excluded because the annotator produced nothing for at "
                        f"least one of the three passages. Charter falsification 3. "
                        f"No claim either way about the measure"),
        }
    else:
        res = evaluate_margins([r["margin"] for r in rows])
        loo = sum(1 for i in range(len(rows))
                  if evaluate_margins([r["margin"] for j, r in enumerate(rows)
                                       if j != i]).t_p < 0.05)
        both = res.t_p < 0.05 and res.wilcoxon_p < 0.05
        payload = {
            "margin_stats": res.as_dict(),
            "leave_one_out": f"{loo}/{len(rows)}",
            "abstention_rate": abstention,
            "verdict": ("FAILED -- margin interval includes zero. Charter "
                        "falsification 1: the mechanical annotator cannot read prose"
                        if res.ci95[0] <= 0 <= res.ci95[1] else
                        "FRAGILE" if not both or loo * 2 < len(rows) else "SUPPORTED"),
        }

    payload.update({
        "sampled": n_sample, "scored": len(rows),
        "excluded": excluded,
        "relations_per_passage": round(
            sum(sum(r["relations"]) for r in rows) / (3 * len(rows)), 2) if rows else 0.0,
        "rows": rows,
        "predicted": plan["predictions"][0]["claim"],
    })

    out = Stage2Result("EXP-042", plan, payload).write()
    print(f"\nEXP-042  written to {out}")
    print(f"plan locked at {plan['_locked_at'][:8]}, predicting failure\n")
    print(f"sampled {n_sample} fresh ARN items (burned ones excluded)")
    print(f"   passages the annotator produced nothing for : "
          f"{payload['abstention_rate']:.0%}")
    print(f"   items excluded for an empty passage         : "
          f"{len(excluded)}/{n_sample}")
    print(f"   items scored                                : {len(rows)}")
    if rows:
        print(f"   relations per passage                       : "
              f"{payload['relations_per_passage']}")
    if payload["margin_stats"]:
        d = payload["margin_stats"]
        print(f"\n   mean margin  : {d['mean_margin_bits']:+.4f} bits")
        print(f"   95% CI       : [{d['ci95_on_mean'][0]:+.4f}, {d['ci95_on_mean'][1]:+.4f}]")
        print(f"   t p / Wilcoxon: {d['t_test_p']:.4f} / {d['wilcoxon_p']:.4f}")
        print(f"   leave-one-out: {payload['leave_one_out']}")
    print(f"\n>>> {payload['verdict']}")
    print(f"\nPREDICTED IN ADVANCE: {payload['predicted']}")


if __name__ == "__main__":
    main()
