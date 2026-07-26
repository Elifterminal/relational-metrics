"""EXP-025 -- the relation-type encoding fix, tested on held-out data.

EXP-024 found F-06a losing a cross-domain analogue to a false friend by 0.0022
bits, entirely because it charged the analogue for using a different domain's
RELATION vocabulary -- the pathology that demoted F-06, removed for participant
labels and never removed for relation types.

THE ORDER THIS WAS DONE IN IS THE POINT:
  1. held-out corpus written -- three new motifs, structurally distinct from
     the development set and from each other
  2. committed and frozen (63c6231) BEFORE the fix existed
  3. fix implemented: charge for SPECIFYING the type map, never for whether
     the names coincide
  4. regressions re-run (harness, cross-generator transfer)
  5. this -- both corpora scored, once

PREDECLARED, before running:
  SUCCESS  3/3 on the held-out corpus AND 3/3 on the development corpus.
  PARTIAL  development fixed, held-out not -- the fix was fitted to the
           diagnosis and does not generalise. Report as a failure of the fix.
  FAILURE  held-out below 2/3, or any regression in the harness or transfer.

The development corpus is no longer evidence -- the fix was designed against
its failure. It is reported as a sanity check only. THE HELD-OUT NUMBER IS THE
RESULT.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                   # noqa: E402
from corpus import (IDEAL_ORDER, IDEAL_TIERS, QUERIES,          # noqa: E402
                    RELATION_CLASS, docs_for, query_doc)
from corpus_holdout import (HOLDOUT_QUERIES, holdout_docs_for,   # noqa: E402
                            holdout_malformed, holdout_query)
from d_a import evaluate                                         # noqa: E402
from measures import mdl_correspondence                          # noqa: E402

_SEED = 7717


def score_corpus(queries, q_fn, d_fn, label):
    out = {}
    for motif in queries:
        q = q_fn(motif)
        cands = list(d_fn(motif))
        random.Random(_SEED).shuffle(cands)
        scores = {d.kind: mdl_correspondence(q.structure, d.structure,
                                             DEFAULT_CODE).ratio for d in cands}
        tb = {d.kind: hash((d.doc_id, _SEED)) for d in cands}
        order = sorted(scores, key=lambda k: (-scores[k], tb[k]))
        da = evaluate(order, IDEAL_ORDER,
                      returned_class={k: RELATION_CLASS[k] for k in order},
                      ideal_class=RELATION_CLASS, tiers=IDEAL_TIERS)
        out[motif] = {
            "ranking": order,
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "analogue_beats_false_friend": order.index("X") < order.index("W"),
            "margin_X_over_W": round(scores["X"] - scores["W"], 4),
            "d_A": da.as_dict(),
            "perfect": da.is_perfect,
        }
    wins = sum(1 for v in out.values() if v["analogue_beats_false_friend"])
    return {"corpus": label, "by_motif": out,
            "analogue_beats_false_friend": f"{wins}/{len(queries)}",
            "wins": wins, "n": len(queries),
            "perfect_motifs": sum(1 for v in out.values() if v["perfect"])}


def main() -> None:
    dev = score_corpus(QUERIES, query_doc, docs_for, "development (already seen)")
    held = score_corpus(HOLDOUT_QUERIES, holdout_query, holdout_docs_for,
                        "HELD-OUT (frozen before the fix)")

    report = {
        "experiment": "EXP-025",
        "ideal_tiers": [sorted(t) for t in IDEAL_TIERS],
        "fix": "relation-type map cost is now name-independent",
        "holdout_frozen_at_commit": "63c6231",
        "holdout_malformed": holdout_malformed(),
        "development": dev,
        "holdout": held,
        "holdout_passes": held["wins"] == held["n"],
        "development_passes": dev["wins"] == dev["n"],
        "verdict": ("SUCCESS" if held["wins"] == held["n"] and dev["wins"] == dev["n"]
                    else "PARTIAL" if dev["wins"] == dev["n"]
                    else "FAILURE"),
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp025.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-025  written to {out}")
    print(f"held-out corpus frozen at commit {report['holdout_frozen_at_commit']}, "
          f"malformed: {report['holdout_malformed'] or 'none'}\n")

    for tag, r in (("DEVELOPMENT (already seen -- sanity check only)", dev),
                   ("HELD-OUT (the result)", held)):
        print(tag)
        print(f"  {'motif':<16}{'ranking':<24}{'X>W':>5}{'margin':>10}  d_A")
        for motif, v in r["by_motif"].items():
            d = v["d_A"]
            print(f"  {motif:<16}{' > '.join(v['ranking']):<24}"
                  f"{('yes' if v['analogue_beats_false_friend'] else 'NO'):>5}"
                  f"{v['margin_X_over_W']:>10.4f}  "
                  f"misord={d['misordered']} disp={d['rank_displacement']}")
        print(f"  -> analogue beats false friend: {r['analogue_beats_false_friend']}"
              f"   perfect motifs: {r['perfect_motifs']}/{r['n']}\n")

    print(f">>> held-out passes     : {report['holdout_passes']}")
    print(f">>> development passes  : {report['development_passes']}")
    print(f">>> VERDICT             : {report['verdict']}")


if __name__ == "__main__":
    main()
