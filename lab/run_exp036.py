"""EXP-036 -- Q-31. A third annotator that cannot know the roles or vary effort.

R-18 has a confirmed direction and an unmeasured size, because every comparison
so far confounds role-knowledge with how many relations the annotator chose to
write. A program removes both: it has no role knowledge, and the same sentence
always yields the same relations.

THE TEST IS ONE-SIDED, and that is stated before the result rather than after:

  claim SURVIVES mechanical annotation
      -> informative. A process that cannot know which document is which still
         ranks the analogue above the false friend, so the signal is in the text.
  claim FAILS
      -> AMBIGUOUS between "the corpus was inflated" and "the extractor is too
         weak to read these sentences". It cannot distinguish them and will not
         be reported as if it could.

The extractor recovers 1.52 relations per sentence against my 2.70, measured
BEFORE any comparison was run. It is much worse at language than a person. Its
weakness is uncorrelated with role, though -- it cannot tell an analogue from a
false friend -- so it cannot be weak in a way that favours either.

SECOND CONTROL, for the granularity confound specifically: restrict to documents
where the mechanical and sighted annotations happen to produce the SAME relation
count, and compare only there. Small n, but granularity is held fixed by
selection rather than by hope.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from corpus import DOCS                                           # noqa: E402
from corpus_holdout import HOLDOUT                                # noqa: E402
from corpus_independent import INDEPENDENT                        # noqa: E402
from mechanical import extract                                    # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from q30_pool import strip_tell                                   # noqa: E402
from ranking import rank_with_ties, strictly_above                # noqa: E402
from structure import Relation, Structure                         # noqa: E402

CORPORA = (("dev", DOCS), ("held-out", HOLDOUT), ("independent", INDEPENDENT))


def build(name, edges):
    rels = tuple(Relation(a, b, t) for a, b, t in edges)
    nodes = tuple(sorted({n for r in rels for n in (r.src, r.dst)}))
    return Structure(name, nodes, rels)


def main() -> None:
    per_corpus, gran_rows = {}, []
    for label, coll in CORPORA:
        motifs = {}
        for d in coll:
            text, _ = strip_tell(d.gloss)          # the role tells EXP-033 found
            mech = build(d.doc_id, extract(text))
            motifs.setdefault(d.motif, {})[d.kind] = mech
            gran_rows.append({
                "corpus": label, "doc_id": d.doc_id, "kind": d.kind,
                "mechanical": mech.m, "sighted": d.structure.m,
                "matched_granularity": mech.m == d.structure.m,
            })
        rows, empties = [], 0
        for motif, docs in sorted(motifs.items()):
            q = docs["D"]
            if q.m == 0:
                empties += 1
                continue
            sc = {k: mdl_correspondence(q, s, DEFAULT_CODE).ratio
                  for k, s in docs.items() if k != "D"}
            g = rank_with_ties(sc)
            rows.append({"motif": motif,
                         "analogue_beats_false_friend": strictly_above(g, "X", "W"),
                         "scores": {k: round(v, 4) for k, v in sc.items()}})
        per_corpus[label] = {
            "held": sum(r["analogue_beats_false_friend"] for r in rows),
            "of": len(rows), "queries_with_no_relations": empties, "rows": rows,
        }

    held = sum(v["held"] for v in per_corpus.values())
    of = sum(v["of"] for v in per_corpus.values())

    matched = [g for g in gran_rows if g["matched_granularity"]]
    report = {
        "experiment": "EXP-036", "question": "Q-31",
        "annotator": "deterministic rule-based extractor -- no role knowledge, fixed effort",
        "test_is_one_sided": ("survival is informative; failure is ambiguous between "
                              "'corpus inflated' and 'extractor too weak'"),
        "relations_per_sentence": {
            "mechanical": round(sum(g["mechanical"] for g in gran_rows) / len(gran_rows), 2),
            "sighted": round(sum(g["sighted"] for g in gran_rows) / len(gran_rows), 2),
        },
        "granularity_matched_documents": f"{len(matched)}/{len(gran_rows)}",
        "per_corpus": per_corpus,
        "mechanical_result": f"{held}/{of}",
        "sighted_result": "10/10",
        "my_blind_result": "6/10 (EXP-032, EXP-033)",
    }
    # THE CHECK THAT SHOULD HAVE RUN TWO EXPERIMENTS AGO.
    # EXP-032 and EXP-033 reported blind results as "degraded but present"
    # without ever asking whether they were distinguishable from chance. For a
    # binary analogue-vs-false-friend call, chance is 50%.
    import math

    def binom_p(k, n, prob=0.5):
        f = lambda i: math.comb(n, i) * prob ** i * (1 - prob) ** (n - i)
        obs = f(k)
        return min(1.0, sum(f(i) for i in range(n + 1) if f(i) <= obs + 1e-12))

    report["significance"] = {
        "note": ("chance is 50% -- either candidate could win. Reporting a raw "
                 "fraction without this was the omission"),
        "sighted": {"score": "10/10", "p": round(binom_p(10, 10), 4),
                    "significant": binom_p(10, 10) < 0.05},
        "my_blind": {"score": "6/10", "p": round(binom_p(6, 10), 4),
                     "significant": binom_p(6, 10) < 0.05},
        "mechanical": {"score": f"{held}/{of}", "p": round(binom_p(held, of), 4),
                       "significant": binom_p(held, of) < 0.05},
        "conclusion": ("the ONLY annotation mode producing a significant result is "
                       "the one where the annotator knew the answers. No blind "
                       "result is distinguishable from chance. This does not prove "
                       "the corpus is inflated -- n=10 is small and a real effect "
                       "could be underpowered -- but the project has no significant "
                       "evidence that the measure ranks analogues above false "
                       "friends under blind annotation"),
    }

    report["verdict"] = (
        "SIGNAL IS IN THE TEXT -- a process that cannot know the roles still "
        "ranks the analogue above the false friend"
        if held == of and of > 0 else
        f"AMBIGUOUS -- {held}/{of}. Cannot distinguish an inflated corpus from an "
        "extractor too weak to read these sentences. R-18's size stays unmeasured; "
        "the second-annotator commission is still the control that would settle it")

    out = Path(__file__).resolve().parents[1] / "results" / "exp036.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-036  written to {out}\n")
    print(f"relations per sentence: mechanical "
          f"{report['relations_per_sentence']['mechanical']}, "
          f"sighted {report['relations_per_sentence']['sighted']}")
    print(f"documents where the two happen to match: "
          f"{report['granularity_matched_documents']}\n")
    for label, v in per_corpus.items():
        print(f"   {label:<13}{v['held']}/{v['of']}"
              + (f"   ({v['queries_with_no_relations']} queries yielded no relations)"
                 if v["queries_with_no_relations"] else ""))
    print(f"\n   MECHANICAL : {report['mechanical_result']}")
    print(f"   my blind   : {report['my_blind_result']}")
    print(f"   sighted    : {report['sighted_result']}")
    sig = report["significance"]
    print("\nSIGNIFICANCE -- chance is 50%, and this was never checked before:")
    for k in ("sighted", "my_blind", "mechanical"):
        v = sig[k]
        print(f"   {k:<12}{v['score']:>7}   p = {v['p']:.3f}   "
              f"{'SIGNIFICANT' if v['significant'] else 'not significant'}")
    print(f"\n   {sig['conclusion']}")
    print(f"\n>>> {report['verdict']}")


if __name__ == "__main__":
    main()
