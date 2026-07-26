"""EXP-041 -- Q-27. Can the representation express an ARN analogy at all?

Run strictly to the plan locked at 83ad980c, external/plans/EXP-041.json.

P-22: before building a measure, construct a witness pair. Stage 2 proposes to
build an automatic annotator for natural prose. If, on this benchmark, the
correct answer and the distractor routinely come out ISOMORPHIC, then no
annotator can separate them and Stage 2 is closed before it starts.

The plan declares in advance that the data is reused (the 20 items burned in
EXP-030), why that is legitimate for a representational question, and that my
own template floor (EXP-040) is the main confound.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from arn_annotations_raw import A as ANNOT                        # noqa: E402
from arn_blind import reveal                                      # noqa: E402
from identifiability import isomorphic                            # noqa: E402
from protocol2 import require_locked_plan                         # noqa: E402
from run_exp030 import build                                      # noqa: E402
from structure import Relation, Structure                         # noqa: E402


def untyped(s: Structure) -> Structure:
    """Same shape, one relation type. Dropping types can only merge classes."""
    return Structure(s.name + "|untyped", s.nodes,
                     tuple(Relation(r.src, r.dst, "R", r.weight) for r in s.relations),
                     s.domain)


def cp(k, n, conf=0.95):
    def pmf(i, p):
        return math.comb(n, i) * p ** i * (1 - p) ** (n - i)
    a = (1 - conf) / 2
    lo, hi = 0.0, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        if sum(pmf(i, m) for i in range(k, n + 1)) < a:
            lo = m
        else:
            hi = m
    low = lo if k > 0 else 0.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        m = (lo + hi) / 2
        if sum(pmf(i, m) for i in range(0, k + 1)) < a:
            hi = m
        else:
            lo = m
    return round(low, 3), round(hi if k < n else 1.0, 3)


def main() -> None:
    plan = require_locked_plan("EXP-041")
    key = reveal()
    roles = {k["passage_id"]: (k["item_id"], k["role"])
             for k in key["key"] if "passage_id" in k}
    answers = {k["item_id"]: int(k["correct_answer"])
               for k in key["key"] if "correct_answer" in k}

    items = {}
    for pid in ANNOT:
        iid, role = roles[pid]
        items.setdefault(iid, {})[role] = build(pid)

    rows, excluded = [], []
    for iid, v in sorted(items.items()):
        if len(v) != 3 or any(v[r].m == 0 for r in ("Q", "A", "B")):
            excluded.append(iid)
            continue
        good = v["A"] if answers[iid] == 1 else v["B"]
        bad = v["B"] if answers[iid] == 1 else v["A"]
        rows.append({
            "item": iid,
            "relations": [v["Q"].m, good.m, bad.m],
            "typed_isomorphic": isomorphic(good, bad),
            "untyped_isomorphic": isomorphic(untyped(good), untyped(bad)),
        })

    n = len(rows)
    typed = sum(r["typed_isomorphic"] for r in rows)
    untyp = sum(r["untyped_isomorphic"] for r in rows)
    rate = typed / n if n else 0.0

    if rate > 0.5:
        verdict = ("CLOSED -- the representation cannot express these analogies. "
                   "More than half the correct/distractor pairs are isomorphic, so "
                   "no annotator can separate them")
    elif rate < 0.25:
        verdict = ("PROCEED -- the representation is adequate. Correct and "
                   "distractor are structurally distinct on the great majority of "
                   "items, so EXP-030's failure was the ANNOTATOR, not the "
                   "representation")
    else:
        verdict = ("AMBIGUOUS -- between a quarter and a half. Per the plan, do "
                   "not proceed on the strength of this")

    report = {
        "experiment": "EXP-041", "question": "Q-27",
        "plan_locked_at": plan["_locked_at"], "plan_sha256": plan["_sha256"],
        "items_scored": n, "excluded": excluded,
        "typed_isomorphic": typed,
        "typed_isomorphism_rate": round(rate, 3),
        "ci95": cp(typed, n) if n else None,
        "untyped_isomorphic": untyp,
        "untyped_isomorphism_rate": round(untyp / n, 3) if n else None,
        "confound": ("annotations are mine and EXP-040 established I annotate to a "
                     "floor of four relations. A LOW isomorphism rate is safe from "
                     "this -- a template would flatten structures together, not "
                     "push them apart. A HIGH rate would be ambiguous"),
        "what_this_does_not_show": plan["what_this_does_not_show"],
        "rows": rows, "verdict": verdict,
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp041.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-041  written to {out}")
    print(f"plan locked at {plan['_locked_at'][:8]}\n")

    print(f"items scored: {n}   excluded: {len(excluded)}\n")
    print(f"   correct vs distractor, TYPED isomorphic   : {typed}/{n} = {rate:.0%}"
          f"   95% CI {report['ci95']}")
    print(f"   correct vs distractor, UNTYPED isomorphic : {untyp}/{n} = "
          f"{untyp/n:.0%}   (types dropped)")
    print(f"\n   relation counts per item [query, correct, distractor]:")
    for r in rows[:6]:
        print(f"      {r['item']:<6}{r['relations']}")
    print(f"      ... {n} items\n")
    print(f">>> {verdict}")
    print(f"\nCONFOUND: {report['confound']}")


if __name__ == "__main__":
    main()
