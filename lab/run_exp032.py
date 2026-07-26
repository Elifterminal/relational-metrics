"""EXP-032 -- Q-26. Does the corpus result survive BLIND annotation?

R-18, the risk EXP-030 raised: every corpus result rests on hand annotation
performed KNOWING each document's designated role. EXP-026 cleared my
ground-truth ORDERING of bias; it never tested whether the STRUCTURAL
ANNOTATION encodes the role. If it does, F-06a has been reading back what
annotation put in, and the whole record measures annotation fidelity.

This re-annotates the independent corpus from glosses alone, shuffled, roles and
motif membership stripped, then re-scores.

CONTAMINATION, AND WHY IT DECIDES THE READING. I annotated this corpus sighted.
Shuffling hides the roles; it does not erase memory. So DIVERGENCE from the
sighted annotation is measured FIRST, and the ranking is only interpretable in
its light:

  diverges AND ranking survives   -> strong. Two different annotations, same
                                     answer, so the signal is in the text.
  nearly identical                -> UNINFORMATIVE. Cannot separate "annotation
                                     is reproducible" from "I remembered".
  diverges AND ranking collapses  -> R-18 fires.

An identical result is a NULL result here, not a confirmation. Written down
before the key was opened.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from blind_reannotate import load_key                             # noqa: E402
from codes import DEFAULT_CODE                                    # noqa: E402
from identifiability import isomorphic                            # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from q26_blind_annotations import B as BLIND                      # noqa: E402
from ranking import format_ranking, rank_with_ties, strictly_above  # noqa: E402
from structure import Relation, Structure                         # noqa: E402


def build(pid, edges, domain="blind"):
    rels = tuple(Relation(a, b, t) for a, b, t in edges)
    nodes = tuple(sorted({n for r in rels for n in (r.src, r.dst)}))
    return Structure(pid, nodes, rels, domain)


def jaccard(a, b):
    """Shape overlap, ignoring node names: compare typed degree signatures."""
    def sig(s):
        out = []
        for n in s.nodes:
            outd = sum(1 for r in s.relations if r.src == n)
            ind = sum(1 for r in s.relations if r.dst == n)
            neg = sum(1 for r in s.relations
                      if (r.src == n or r.dst == n) and r.rtype.endswith("NEG"))
            out.append((ind, outd, neg))
        return sorted(out)
    sa, sb = sig(a), sig(b)
    inter = 0
    tmp = list(sb)
    for x in sa:
        if x in tmp:
            tmp.remove(x); inter += 1
    union = len(sa) + len(sb) - inter
    return inter / union if union else 1.0


def main() -> None:
    key = {k["passage_id"]: k for k in load_key()}

    # ---- 1. DIVERGENCE, measured before anything else --------------------
    div = []
    for pid, edges in BLIND.items():
        k = key[pid]
        blind_s = build(pid, edges)
        sighted_s = build(pid + "_s", [tuple(e) for e in k["sighted"]])
        div.append({
            "doc_id": k["doc_id"], "kind": k["kind"], "motif": k["motif"],
            "blind_relations": blind_s.m, "sighted_relations": sighted_s.m,
            "identical_up_to_isomorphism": isomorphic(blind_s, sighted_s),
            "shape_overlap": round(jaccard(blind_s, sighted_s), 3),
        })
    n_iso = sum(d["identical_up_to_isomorphism"] for d in div)
    mean_overlap = sum(d["shape_overlap"] for d in div) / len(div)

    # ---- 2. re-score the claim on the blind annotations -------------------
    motifs = {}
    for pid, edges in BLIND.items():
        k = key[pid]
        motifs.setdefault(k["motif"], {})[k["kind"]] = build(pid, edges)

    rows = []
    for motif, docs in sorted(motifs.items()):
        q = docs["D"]
        scores = {kind: mdl_correspondence(q, s, DEFAULT_CODE).ratio
                  for kind, s in docs.items() if kind != "D"}
        g = rank_with_ties(scores)
        rows.append({
            "motif": motif, "ranking": format_ranking(g),
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "analogue_beats_false_friend": strictly_above(g, "X", "W"),
            "paraphrase_ties_analogue": abs(scores["P"] - scores["X"]) < 1e-9,
        })
    held = sum(r["analogue_beats_false_friend"] for r in rows)
    n = len(rows)

    # ---- 3. THE LEAK, corpus held constant, only annotation mode varying --
    # EXP-030 compared 81.7% (sighted corpora) with 42.8% (real narratives,
    # blind), which confounds annotation mode with corpus. This does not.
    def rate(pairs):
        h = t = 0
        for a, b in pairs:
            r = mdl_correspondence(a, b, DEFAULT_CODE)
            h += r.matched
            t += r.total
        return h / t if t else 0.0

    from corpus_independent import (independent_docs_for,          # noqa: E402
                                    independent_query)
    sighted_pairs = [(independent_query(m).structure, d.structure)
                     for m in motifs for d in independent_docs_for(m)]
    blind_pairs = [(d["D"], sx) for d in motifs.values()
                   for kk, sx in d.items() if kk != "D"]
    r_sighted, r_blind = rate(sighted_pairs), rate(blind_pairs)

    per_kind = {}
    for kind in ("P", "X", "W", "V", "U"):
        sp = [(independent_query(m).structure, d.structure)
              for m in motifs for d in independent_docs_for(m) if d.kind == kind]
        bp = [(d["D"], d[kind]) for d in motifs.values() if kind in d]
        per_kind[kind] = {"sighted": round(rate(sp), 3), "blind": round(rate(bp), 3)}

    # Does the discrimination survive the inflation? That is the question that
    # matters -- inflation alone does not invalidate a gap.
    gap_survives = per_kind["X"]["blind"] > per_kind["W"]["blind"]

    diverged = n_iso < len(div) * 0.5
    # The predeclared buckets were binary (survives / collapses) and the outcome
    # is graded. Recording that the prediction space was mis-specified rather
    # than forcing the result into the nearest label.
    if not diverged:
        verdict = "UNINFORMATIVE -- annotations too similar to rule out recall"
    elif held == n and gap_survives:
        verdict = "R-18 WEAKENED -- different annotations, same answer"
    elif held == 0 or not gap_survives:
        verdict = "R-18 FIRES -- the result was an artifact of sighted annotation"
    else:
        verdict = ("R-18 PARTIALLY CONFIRMED -- sighted annotation measurably "
                   "inflates correspondence, but the analogue/false-friend gap "
                   "survives blind re-annotation and is not an artifact of it")

    report = {
        "experiment": "EXP-032", "question": "Q-26",
        "corpus": "independent (EXP-026), re-annotated blind from glosses",
        "contamination": ("annotator had previously annotated this corpus sighted; "
                          "divergence is the interpretive key, not the ranking"),
        "divergence": {
            "documents": len(div),
            "identical_up_to_isomorphism": n_iso,
            "mean_shape_overlap": round(mean_overlap, 3),
            "materially_diverged": diverged,
            "per_doc": div,
        },
        "leak": {
            "note": "same 24 documents; only the annotation mode differs",
            "best_match_rate_sighted": round(r_sighted, 3),
            "best_match_rate_blind": round(r_blind, 3),
            "inflation_factor": round(r_sighted / r_blind, 3) if r_blind else None,
            "per_kind": per_kind,
            "analogue_gap_survives_blind": gap_survives,
        },
        "predeclaration_note": ("the predeclared readings were binary -- survives "
                                "or collapses -- and the outcome is graded. The "
                                "prediction space was mis-specified; recorded "
                                "rather than rounded to the nearest label"),
        "sighted_result": "4/4 (EXP-026)",
        "blind_result": f"{held}/{n}",
        "rows": rows,
        "verdict": verdict,
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp032.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-032  written to {out}\n")

    print("STEP 1 -- DIVERGENCE (read this before the ranking)")
    print(f"   documents re-annotated                : {len(div)}")
    print(f"   identical to sighted, up to isomorphism: {n_iso}/{len(div)}")
    print(f"   mean shape overlap                     : {mean_overlap:.3f}")
    print(f"   materially diverged                    : {diverged}\n")

    print("STEP 2 -- the claim, re-scored on the blind annotations")
    print(f"   {'motif':<14}{'ranking':<26}{'X>W':>5}{'P==X':>7}")
    for r in rows:
        print(f"   {r['motif']:<14}{r['ranking']:<26}"
              f"{('yes' if r['analogue_beats_false_friend'] else 'NO'):>5}"
              f"{str(r['paraphrase_ties_analogue']):>7}")
    print(f"\n   sighted (EXP-026): 4/4      blind: {held}/{n}")
    print("\nSTEP 3 -- THE LEAK (same documents, only annotation mode differs)")
    print(f"   best-match rate, SIGHTED : {r_sighted:.1%}")
    print(f"   best-match rate, BLIND   : {r_blind:.1%}")
    print(f"   inflation from the labels: {r_sighted / r_blind:.2f}x")
    print(f"\n   {'kind':<6}{'sighted':>9}{'blind':>8}")
    for k, v in per_kind.items():
        print(f"   {k:<6}{v['sighted']:>9.1%}{v['blind']:>8.1%}")
    print(f"\n   analogue still above false friend under blind annotation: "
          f"{gap_survives}")
    print(f"\n>>> {verdict}")


if __name__ == "__main__":
    main()
