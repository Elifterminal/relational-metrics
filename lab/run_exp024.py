"""EXP-024 -- A-01 goes live: the corpus, d_A, and does F-06a actually retrieve?

Two deliverables and one real test.

  1. THE CORPUS. Three structurally distinct motifs (positive cycle, negative
     cycle, acyclic cascade), six documents each, hand-annotated. Ground truth
     by construction.

  2. d_A. A VECTOR over named failure modes, each traceable to a principle
     that predates it. Not a scalar -- P-17 rules that out -- and not a single
     summary over parts, which EXP-017 measured can reverse a ranking.

  3. THE TEST. Does F-06a, unchanged and now at rung 3, retrieve correctly on
     text-derived structures it has never seen?

CLAIM: for each motif, F-06a ranks paraphrase and cross-domain ANALOGUE above
false friend, generic and unrelated.

THE ONE THAT MATTERS: analogue above FALSE FRIEND. The false friend shares the
query's entire vocabulary and has different structure. Any method that reads
words puts it first. This is the single comparison the whole project exists to
get right, and it has never been run on anything but hand-built graphs.

d_A IS ITSELF A MEASURE, so it gets the EXP-000 treatment rather than being
trusted: three deliberately bad retrievers are scored alongside, and d_A must
separate them from the real one. A distance measure that cannot tell a good
answer from a vocabulary-matcher is not a distance measure.

FALSIFICATION: if the analogue does not outrank the false friend on the
majority of motifs, the retrieval claim fails on real text structure and A-01
is not viable as specified.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                   # noqa: E402
from corpus import (DOCS, IDEAL_ORDER, QUERIES, RELATION_CLASS,  # noqa: E402
                    all_well_formed, docs_for, query_doc)
from d_a import evaluate                                         # noqa: E402
from measures import mdl_correspondence                          # noqa: E402
from ranking import (format_ranking, rank_with_ties,              # noqa: E402
                     strictly_above, tied)


# Candidate order must never leak into a ranking. The corpus lists documents
# in ideal order for readability, and a method that scores everything equally
# would otherwise inherit that order from a stable sort and look perfect while
# measuring nothing. Caught on the first run: a size-matcher scored 3/3 because
# every document has the same relation count. Candidates are therefore shuffled
# with a fixed seed before scoring, and ties are broken by a hash rather than
# by position.
_SHUFFLE_SEED = 7717


def _tiebreak(doc_id: str, seed: int = 7717) -> str:
    """Deterministic tie-break.

    Python's built-in hash() is salted per process, so ties broke differently
    on every run and a ranking among equal-scoring items was not reproducible.
    EXP-026 reported "the generic document outranks the analogue on 3 of 4
    motifs" on the strength of one such ordering; the items were in fact
    exactly tied. Corrected in EXP-027.
    """
    import hashlib
    return hashlib.md5(f"{doc_id}:{seed}".encode()).hexdigest()



def rank_by(scorer, motif):
    import random
    q = query_doc(motif)
    cands = list(docs_for(motif))
    random.Random(_SHUFFLE_SEED).shuffle(cands)
    scored = {d.kind: scorer(q, d) for d in cands}
    groups = rank_with_ties(scored)
    # Linear form kept ONLY for d_A, which needs a sequence. Ties are broken by
    # a stable key so d_A is reproducible, but no CLAIM is read off the
    # within-group order -- that is what EXP-027 had to retract. See P-18.
    order = [k for g in groups for k in sorted(g, key=_tiebreak)]
    return order, scored, groups


# -- the real method and three impostors ------------------------------------

def m_f06a(q, d):
    return mdl_correspondence(q.structure, d.structure, DEFAULT_CODE).ratio


def m_wordmatch(q, d):
    a, b = set(q.structure.nodes), set(d.structure.nodes)
    return len(a & b) / len(a | b) if a | b else 0.0


def m_domain(q, d):
    return 1.0 if d.domain == q.structure.domain else 0.0


def m_size(q, d):
    return 1.0 - abs(q.structure.m - d.structure.m) / max(q.structure.m, d.structure.m)


METHODS = {"F-06a (the measure)": m_f06a,
           "word overlap": m_wordmatch,
           "same domain": m_domain,
           "size match": m_size}
IMPOSTORS = {"word overlap", "same domain", "size match"}


def main() -> None:
    malformed = all_well_formed()
    report = {"experiment": "EXP-024",
              "corpus_size": len(DOCS),
              "corpus_well_formed": not malformed,
              "malformed": malformed,
              "ideal_order": IDEAL_ORDER}

    per_method = {}
    for mname, fn in METHODS.items():
        per_motif = {}
        for motif in QUERIES:
            order, scores, groups = rank_by(fn, motif)
            da = evaluate(order, IDEAL_ORDER,
                          returned_class={k: RELATION_CLASS[k] for k in order},
                          ideal_class=RELATION_CLASS)
            per_motif[motif] = {
                "ranking": format_ranking(groups),
            "groups": groups,
            "order_for_d_A": order,
                "scores": {k: round(v, 4) for k, v in scores.items()},
                "analogue_beats_false_friend": strictly_above(groups, "X", "W"),
                "d_A": da.as_dict(),
                "perfect": da.is_perfect,
            }
        wins = sum(1 for v in per_motif.values() if v["analogue_beats_false_friend"])
        per_method[mname] = {
            "by_motif": per_motif,
            "analogue_beats_false_friend": f"{wins}/{len(QUERIES)}",
            "motifs_perfect": sum(1 for v in per_motif.values() if v["perfect"]),
            "is_impostor": mname in IMPOSTORS,
        }
    report["methods"] = per_method

    real = per_method["F-06a (the measure)"]
    report["retrieval_claim_holds"] = real["analogue_beats_false_friend"] == f"{len(QUERIES)}/{len(QUERIES)}"
    report["candidate_order_shuffled"] = True
    report["d_A_separates_impostors"] = all(
        per_method[m]["motifs_perfect"] < real["motifs_perfect"]
        or per_method[m]["analogue_beats_false_friend"] != real["analogue_beats_false_friend"]
        for m in IMPOSTORS)

    out = Path(__file__).resolve().parents[1] / "results" / "exp024.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-024  written to {out}\n")
    print(f"corpus: {len(DOCS)} documents, well-formed: {not malformed}")
    print(f"ideal order: {' > '.join(IDEAL_ORDER)}   "
          f"(P paraphrase, X analogue, W false friend, V generic, U unrelated)\n")

    hdr = f"{'method':<22}{'motif':<14}{'ranking':<22}{'X>W':>5}  d_A"
    print(hdr); print("-" * 86)
    for mname, r in per_method.items():
        for motif, v in r["by_motif"].items():
            d = v["d_A"]
            flag = "yes" if v["analogue_beats_false_friend"] else "NO"
            print(f"{mname:<22}{motif:<14}{v['ranking']:<22}{flag:>5}  "
                  f"misord={d['misordered']} disp={d['rank_displacement']}")
        print()

    print(f"{'method':<22}{'analogue beats false friend':>30}{'perfect motifs':>18}")
    for mname, r in per_method.items():
        tag = "  (impostor)" if r["is_impostor"] else ""
        print(f"{mname:<22}{r['analogue_beats_false_friend']:>30}"
              f"{r['motifs_perfect']:>18}{tag}")

    print(f"\n>>> retrieval claim holds       : {report['retrieval_claim_holds']}")
    print(f">>> d_A separates the impostors : {report['d_A_separates_impostors']}")


if __name__ == "__main__":
    main()
