"""EXP-027 -- F-09 bridge value, and a correction to EXP-026.

Two results, and the correction comes first because it is against my own
published claim.

=== PART 1: CORRECTION TO EXP-026 ===

EXP-026 published: "the vacuous document outranks the genuine analogue on 3 of
4 motifs." That is false. On all four motifs the paraphrase, the analogue and
the generic score IDENTICALLY -- equal to the last bit, not merely close. The
ordering came from sorted() breaking the tie on Python's hash(), which is
salted per process. Three processes gave three different orderings; one of
them got written down as a finding.

Two faults, and the second is the one worth learning from:
  1. The tie-break was not reproducible.
  2. A total order was imposed on tied items at all. A stable tie-break would
     have made the artifact REPRODUCIBLE, not CORRECT. Ranking now returns tied
     groups (ranking.py), so the measure has to admit when it cannot separate
     two documents.

What survives, and it is the load-bearing claim: the analogue is STRICTLY
above the false friend on 10/10 motifs across all three corpora. That never
depended on a tie-break.

=== PART 2: F-09 IS REFUTED, AND NOT BY A NARROW MARGIN ===

F-09 proposed bridge(Q,D) = correspondence(Q,D) - genericness(D), where
genericness is D's mean correspondence against a background. It cannot work
here, for a reason that is arithmetic rather than empirical:

    The independent author -- not told what a generic distractor was for --
    wrote generic documents ISOMORPHIC to the query. Verified by exhaustive
    bijection search on all four motifs.

    Isomorphic structures are indistinguishable to any function of structure
    alone. So corr(B,X) == corr(B,V) for every background B, hence
    genericness(X) == genericness(V) exactly, hence bridge subtracts the SAME
    number from both.

No strength of discount, and no cleverer structural statistic, can separate
them. The distinction between "a real cross-domain analogue" and "a vacuous
sentence with the same shape" is NOT PRESENT in the relational structure. It
is not a measurement failure. It is an absence in the representation.

FALSIFICATION MET: F-09 was predeclared to fail if the generic still outranked
the analogue. It fails harder -- it cannot move them relative to each other at
all. Recorded as REFUTED, not "needs tuning."
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bridge import bridge_value                                   # noqa: E402
from codes import DEFAULT_CODE                                    # noqa: E402
from corpus import QUERIES, docs_for, query_doc                   # noqa: E402
from corpus_holdout import (HOLDOUT, HOLDOUT_QUERIES,             # noqa: E402
                            holdout_docs_for, holdout_query)
from corpus_independent import (INDEPENDENT, INDEPENDENT_QUERIES, # noqa: E402
                                independent_docs_for,
                                independent_query)
from measures import mdl_correspondence                           # noqa: E402
from ranking import (format_ranking, rank_with_ties,              # noqa: E402
                     strictly_above, tied)

KINDS = ("P", "X", "V", "W", "U")


def isomorphic(a, b) -> bool:
    """Exhaustive bijection search. Corpora are small enough that this is exact."""
    if len(a.nodes) != len(b.nodes) or a.m != b.m:
        return False
    na, nb = sorted(a.nodes), sorted(b.nodes)
    return any({(f[s], f[d], t) for s, d, t in a.edge_set()} == b.edge_set()
               for f in (dict(zip(na, p)) for p in itertools.permutations(nb)))


def score_corpus(motifs, q_fn, d_fn, label):
    out = {}
    for m in motifs:
        q = q_fn(m)
        docs = {d.kind: d.structure for d in d_fn(m)}
        scores = {k: mdl_correspondence(q.structure, s, DEFAULT_CODE).ratio
                  for k, s in docs.items()}
        groups = rank_with_ties(scores)
        out[m] = {
            "ranking": format_ranking(groups),
            "groups": groups,
            "scores": {k: round(v, 6) for k, v in scores.items()},
            "analogue_strictly_above_false_friend": strictly_above(groups, "X", "W"),
            "generic_strictly_above_analogue": strictly_above(groups, "V", "X"),
            "generic_tied_with_analogue": tied(groups, "V", "X"),
            "isomorphic_to_query": {k: isomorphic(q.structure, s)
                                    for k, s in docs.items()},
        }
    n = len(motifs)
    return {
        "corpus": label, "n": n, "by_motif": out,
        "analogue_beats_false_friend":
            sum(v["analogue_strictly_above_false_friend"] for v in out.values()),
        "generic_beats_analogue":
            sum(v["generic_strictly_above_analogue"] for v in out.values()),
        "generic_ties_analogue":
            sum(v["generic_tied_with_analogue"] for v in out.values()),
        "generic_isomorphic_to_query":
            sum(v["isomorphic_to_query"]["V"] for v in out.values()),
    }


def f09_can_separate(all_docs, motifs, d_fn):
    """Can the F-09 discount move X and V relative to each other? Max gap."""
    background = [d.structure for d in all_docs]
    worst = 0.0
    detail = {}
    for m in motifs:
        docs = {d.kind: d.structure for d in d_fn(m)}
        bg = [s for s in background if s not in docs.values()]
        bx = bridge_value(docs["X"], docs["X"], bg)   # genericness is query-free
        bv = bridge_value(docs["V"], docs["V"], bg)
        gap = abs(bx.genericness - bv.genericness)
        worst = max(worst, gap)
        detail[m] = {"genericness_X": round(bx.genericness, 6),
                     "genericness_V": round(bv.genericness, 6),
                     "gap": gap, "n_background": len(bg)}
    return {"max_genericness_gap_X_vs_V": worst,
            "discount_can_separate": worst > 0.0, "by_motif": detail}


def main() -> None:
    corpora = [
        score_corpus(INDEPENDENT_QUERIES, independent_query,
                     independent_docs_for, "independent (externally written)"),
        score_corpus(HOLDOUT_QUERIES, holdout_query, holdout_docs_for,
                     "held-out (mine)"),
        score_corpus(QUERIES, query_doc, docs_for, "dev (mine)"),
    ]
    sep = f09_can_separate(INDEPENDENT, INDEPENDENT_QUERIES, independent_docs_for)

    total_n = sum(c["n"] for c in corpora)
    report = {
        "experiment": "EXP-027",
        "part1_correction": {
            "retracted_claim": "EXP-026: generic outranks analogue on 3 of 4 motifs",
            "cause": "sorted() tie-break on hash(), salted per process",
            "truth": "generic TIES analogue exactly on 4 of 4 motifs",
            "surviving_claim": "analogue strictly above false friend",
            "surviving_claim_score":
                f"{sum(c['analogue_beats_false_friend'] for c in corpora)}/{total_n}",
        },
        "part2_f09": {
            "verdict": "REFUTED",
            "reason": "generic documents are isomorphic to the query, so any "
                      "function of structure alone scores them identically",
            "separation_test": sep,
        },
        "corpora": corpora,
    }
    report["generic_beats_analogue_anywhere"] = \
        sum(c["generic_beats_analogue"] for c in corpora)

    out = Path(__file__).resolve().parents[1] / "results" / "exp027.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-027  written to {out}\n")

    print("PART 1 -- tie-aware rankings ({braces} = an unbroken tie)\n")
    for c in corpora:
        print(f"  {c['corpus']}")
        for m, v in c["by_motif"].items():
            iso = "".join(k for k in KINDS if v["isomorphic_to_query"][k])
            print(f"    {m:<14}{v['ranking']:<26}iso to query: {iso}")
        print(f"    analogue > false friend : {c['analogue_beats_false_friend']}/{c['n']}"
              f"    generic > analogue : {c['generic_beats_analogue']}/{c['n']}"
              f"    generic == analogue : {c['generic_ties_analogue']}/{c['n']}\n")

    print(f">>> RETRACTED: 'generic outranks analogue 3/4'. True count across all "
          f"{total_n} motifs: {report['generic_beats_analogue_anywhere']}")
    print(f">>> SURVIVES : analogue strictly above false friend "
          f"{report['part1_correction']['surviving_claim_score']}\n")

    print("PART 2 -- can the F-09 discount separate analogue from generic?\n")
    for m, d in sep["by_motif"].items():
        print(f"    {m:<14}genericness(X)={d['genericness_X']:.6f}   "
              f"genericness(V)={d['genericness_V']:.6f}   gap={d['gap']:.2e}")
    print(f"\n    max gap over all motifs: {sep['max_genericness_gap_X_vs_V']:.2e}")
    print(f">>> F-09 VERDICT: {report['part2_f09']['verdict']} -- "
          f"discount can separate: {sep['discount_can_separate']}")
    print("    The distinction is absent from the structure, so no structural")
    print("    correction can recover it.")


if __name__ == "__main__":
    main()
