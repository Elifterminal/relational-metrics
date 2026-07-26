"""EXP-026 -- the independent corpus. The last doubt in A-01.

Both previous corpora were written by the party that wrote the measure, so
annotation bias was untested and was named as the largest remaining doubt. This
corpus was commissioned from a separate system given only a format
specification: no description of what was being tested, no mention of how
correspondence is computed, and an instruction to refuse if asked what it was
for. Frozen at 4966e1e before this file ran.

The measure is UNCHANGED. Nothing has been tuned since EXP-025.

CLAIM: the cross-domain analogue outranks the false friend on all four motifs.

WHY THIS IS THE REAL TEST. The false friends here were written by someone who
did not know what a false friend is for. They share the query's field and
vocabulary and are wired differently -- but the specific way they differ was
chosen by an author with no stake in whether the measure survives it. In my own
corpora I chose those differences, and could have chosen them convenient
without ever noticing.

TWO GROUND TRUTHS, SCORED SEPARATELY, BECAUSE THEY DISAGREE:
  * AUTHOR'S    -- PARAPHRASE most similar, UNRELATED least, middle unranked.
    Only the endpoints are externally supplied, so only the endpoints are
    scored against it.
  * MINE (EXP-025) -- {PARAPHRASE, ANALOGUE} tied, then false friend, generic,
    unrelated.
The author thinks staying in the same field is worth something. My correction
says it cannot be, if structure is what counts. Reporting both, and reporting
the disagreement, rather than quietly adopting the one that flatters the
measure.

FALSIFICATION: analogue below false friend on two or more motifs means the
earlier results were an artifact of my own annotation and A-01 is not viable
as specified.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from corpus import IDEAL_ORDER, IDEAL_TIERS, RELATION_CLASS       # noqa: E402
from corpus_independent import (AUTHOR_LEAST_SIMILAR,             # noqa: E402
                                AUTHOR_MOST_SIMILAR,
                                INDEPENDENT_QUERIES,
                                independent_docs_for,
                                independent_malformed,
                                independent_query)
from d_a import evaluate                                          # noqa: E402
from measures import mdl_correspondence                           # noqa: E402

_SEED = 7717


def main() -> None:
    per_motif = {}
    for motif in INDEPENDENT_QUERIES:
        q = independent_query(motif)
        cands = list(independent_docs_for(motif))
        random.Random(_SEED).shuffle(cands)
        scores = {d.kind: mdl_correspondence(q.structure, d.structure,
                                             DEFAULT_CODE).ratio for d in cands}
        tb = {d.kind: hash((d.doc_id, _SEED)) for d in cands}
        order = sorted(scores, key=lambda k: (-scores[k], tb[k]))
        da = evaluate(order, IDEAL_ORDER,
                      returned_class={k: RELATION_CLASS[k] for k in order},
                      ideal_class=RELATION_CLASS, tiers=IDEAL_TIERS)
        per_motif[motif] = {
            "ranking": order,
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "analogue_beats_false_friend": order.index("X") < order.index("W"),
            "margin_X_over_W": round(scores["X"] - scores["W"], 4),
            "P_equals_X": abs(scores["P"] - scores["X"]) < 1e-9,
            "author_most_similar_is_top": order[0] == AUTHOR_MOST_SIMILAR[motif],
            "author_least_similar_is_bottom": order[-1] == AUTHOR_LEAST_SIMILAR[motif],
            "d_A_vs_my_tiers": da.as_dict(),
        }

    n = len(INDEPENDENT_QUERIES)
    wins = sum(1 for v in per_motif.values() if v["analogue_beats_false_friend"])
    ties = sum(1 for v in per_motif.values() if v["P_equals_X"])
    a_top = sum(1 for v in per_motif.values() if v["author_most_similar_is_top"])
    a_bot = sum(1 for v in per_motif.values() if v["author_least_similar_is_bottom"])

    report = {
        "experiment": "EXP-026",
        "corpus": "independent, commissioned, frozen at 4966e1e",
        "measure": "unchanged since EXP-025",
        "malformed": independent_malformed(),
        "by_motif": per_motif,
        "analogue_beats_false_friend": f"{wins}/{n}",
        "paraphrase_ties_analogue": f"{ties}/{n}",
        "author_endpoint_top_agrees": f"{a_top}/{n}",
        "author_endpoint_bottom_agrees": f"{a_bot}/{n}",
        "claim_holds": wins == n,
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp026.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-026  written to {out}")
    print("corpus frozen at 4966e1e; measure unchanged since EXP-025; "
          f"malformed: {report['malformed'] or 'none'}\n")

    hdr = f"{'motif':<14}{'ranking':<24}{'X>W':>5}{'margin':>9}{'P==X':>7}"
    print(hdr); print("-" * len(hdr))
    for motif, v in per_motif.items():
        print(f"{motif:<14}{' > '.join(v['ranking']):<24}"
              f"{('yes' if v['analogue_beats_false_friend'] else 'NO'):>5}"
              f"{v['margin_X_over_W']:>9.4f}{str(v['P_equals_X']):>7}")

    print(f"\n>>> analogue beats false friend : {report['analogue_beats_false_friend']}")
    print(f">>> paraphrase ties analogue    : {report['paraphrase_ties_analogue']}")
    print()
    print("AGAINST THE AUTHOR'S OWN JUDGEMENT (the only external ground truth):")
    print(f"   their 'most similar' ranked first : {report['author_endpoint_top_agrees']}")
    print(f"   their 'least similar' ranked last : {report['author_endpoint_bottom_agrees']}")
    print(f"\n>>> CLAIM HOLDS: {report['claim_holds']}")


if __name__ == "__main__":
    main()
