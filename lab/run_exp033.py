"""EXP-033 -- Q-30. The blind protocol on the other two corpora.

EXP-032 ran this on the independent corpus: ordering survived (3/4), sighted
annotation inflated correspondence 1.34x. One corpus at n=4 is thin evidence for
restating a claim, so this repeats it on dev and held-out, pooled and shuffled
together so the corpus itself is also hidden during annotation.

FOUND WHILE BUILDING THE POOL, and it matters more than the scores. Six of the
thirty-six glosses ANNOUNCE THE ROLE IN THE PROSE -- "Same words, opposite
wiring:", "Same words, no reset:" -- and all six are the FALSE FRIENDS, which is
exactly the comparison being tested. So R-18's concern reaches one stage further
back than EXP-032 examined: not merely an annotator who knew the roles, but
corpus text that states them. The prefixes are stripped before annotation and the
fact is reported rather than quietly cleaned.

PREDECLARED (from Q-30): if the blind rate holds near 3/4 across all three
corpora, restate C-03 at the blind figure permanently and close R-18. If it drops
below half on either, R-18 fires properly.

The contamination caveat from EXP-032 carries over unchanged: I annotated these
sighted, so divergence is measured first and decides how the ranking reads.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from identifiability import isomorphic                            # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from q30_blind_annotations import Q30                             # noqa: E402
from q30_pool import load_key                                     # noqa: E402
from ranking import format_ranking, rank_with_ties, strictly_above  # noqa: E402
from run_exp032 import build, jaccard                             # noqa: E402


def rate(pairs):
    h = t = 0
    for a, b in pairs:
        r = mdl_correspondence(a, b, DEFAULT_CODE)
        h += r.matched
        t += r.total
    return h / t if t else 0.0


def main() -> None:
    key = {k["passage_id"]: k for k in load_key()}

    # group blind structures by corpus + motif
    grouped: dict[str, dict[str, dict[str, object]]] = {}
    sighted_s: dict[str, dict[str, dict[str, object]]] = {}
    div = []
    for pid, edges in Q30.items():
        k = key[pid]
        b = build(pid, edges)
        sg = build(pid + "_s", [tuple(e) for e in k["sighted"]])
        grouped.setdefault(k["corpus"], {}).setdefault(k["motif"], {})[k["kind"]] = b
        sighted_s.setdefault(k["corpus"], {}).setdefault(k["motif"], {})[k["kind"]] = sg
        div.append({
            "corpus": k["corpus"], "doc_id": k["doc_id"], "kind": k["kind"],
            "gloss_announced_role": k["gloss_announced_role"],
            "blind_relations": b.m, "sighted_relations": sg.m,
            "identical_up_to_isomorphism": isomorphic(b, sg),
            "shape_overlap": round(jaccard(b, sg), 3),
        })

    n_iso = sum(d["identical_up_to_isomorphism"] for d in div)
    mean_overlap = sum(d["shape_overlap"] for d in div) / len(div)
    diverged = n_iso < len(div) * 0.5

    per_corpus = {}
    for corpus, motifs in sorted(grouped.items()):
        rows = []
        for motif, docs in sorted(motifs.items()):
            q = docs["D"]
            sc = {kk: mdl_correspondence(q, s, DEFAULT_CODE).ratio
                  for kk, s in docs.items() if kk != "D"}
            g = rank_with_ties(sc)
            rows.append({"motif": motif, "ranking": format_ranking(g),
                         "analogue_beats_false_friend": strictly_above(g, "X", "W")})
        bp = [(d["D"], s) for d in motifs.values() for kk, s in d.items() if kk != "D"]
        sp = [(d["D"], s) for d in sighted_s[corpus].values()
              for kk, s in d.items() if kk != "D"]
        rb, rs = rate(bp), rate(sp)
        per_corpus[corpus] = {
            "rows": rows,
            "held": sum(r["analogue_beats_false_friend"] for r in rows),
            "of": len(rows),
            "best_match_sighted": round(rs, 3),
            "best_match_blind": round(rb, 3),
            "inflation": round(rs / rb, 3) if rb else None,
            "relations_sighted": sum(d["sighted_relations"] for d in div
                                     if d["corpus"] == corpus),
            "relations_blind": sum(d["blind_relations"] for d in div
                                   if d["corpus"] == corpus),
        }

    # ---- THE CONFOUND, measured before any verdict is drawn ---------------
    # My blind annotations of dev/holdout carry roughly HALF the relations of
    # the sighted ones, from the same text. Fewer relations means less to match
    # regardless of role-knowledge, so inflation here is not cleanly R-18.
    #
    # But the confound points at something worse rather than exonerating the
    # corpus. The dev/holdout glosses average 9 words, and the SIGHTED
    # annotation gives each 4 relations. A 9-word sentence does not support 4
    # typed relations, and the gloss IS the whole document -- there is no richer
    # text the annotator was working from. So the sighted structures contain
    # organisation that is not in the documents.
    #
    # What cannot be separated here: "I annotated richly because I knew the
    # role" versus "I annotate more richly when not working through 36 terse
    # glosses at speed". Both are annotator effects. Stated rather than resolved.
    for corpus, v in per_corpus.items():
        v["relation_ratio_blind_over_sighted"] = round(
            v["relations_blind"] / v["relations_sighted"], 3)

    total_held = sum(v["held"] for v in per_corpus.values())
    total_of = sum(v["of"] for v in per_corpus.values())
    # combined with EXP-032's independent corpus
    combined_held, combined_of = total_held + 3, total_of + 4
    below_half = any(v["held"] * 2 < v["of"] for v in per_corpus.values())

    report = {
        "experiment": "EXP-033", "question": "Q-30",
        "corpus_defect_found": {
            "glosses_announcing_their_role": sum(
                1 for d in div if d["gloss_announced_role"]),
            "all_of_kind": sorted({d["kind"] for d in div if d["gloss_announced_role"]}),
            "note": ("the false-friend documents STATE their role in the prose. "
                     "R-18 reaches back into the corpus text, not just the "
                     "annotation. Prefixes stripped before annotating"),
        },
        "divergence": {"documents": len(div),
                       "identical_up_to_isomorphism": n_iso,
                       "mean_shape_overlap": round(mean_overlap, 3),
                       "materially_diverged": diverged},
        "per_corpus": per_corpus,
        "blind_this_run": f"{total_held}/{total_of}",
        "blind_all_three_corpora": f"{combined_held}/{combined_of}",
        "sighted_all_three_corpora": "10/10",
        "any_corpus_below_half": below_half,
        "confound": {
            "note": ("blind annotations of dev/holdout carry ~half the relations "
                     "of the sighted ones, so inflation here mixes role-knowledge "
                     "with annotation granularity and cannot be attributed cleanly"),
            "relation_ratio": {c: v["relation_ratio_blind_over_sighted"]
                               for c, v in per_corpus.items()},
            "cleanest_estimate": ("the independent corpus (EXP-032), where blind and "
                                  "sighted granularity are comparable at 0.85: 3/4 "
                                  "with 1.34x inflation"),
            "secondary_finding": ("dev/holdout glosses average 9 words and their "
                                  "SIGHTED annotation gives each 4 relations. The "
                                  "gloss is the whole document, so those structures "
                                  "encode organisation the text does not contain"),
        },
        "verdict": ("R-18 CONFIRMED AND ENLARGED, but the size is not cleanly "
                    "measured here. Blind rate falls to "
                    f"{combined_held}/{combined_of} from 10/10 sighted. The drop is "
                    "real; how much of it is role-knowledge versus annotation "
                    "granularity is NOT separable from this run. Cleanest number "
                    "remains EXP-032's 1.34x on the corpus where granularity "
                    "matched. Two corpus defects found: false-friend glosses state "
                    "their role, and sighted structures over-annotate relative to "
                    "their text"),
        "per_doc": div,
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp033.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-033  written to {out}\n")

    d = report["corpus_defect_found"]
    print(f"CORPUS DEFECT: {d['glosses_announcing_their_role']} glosses announce their role "
          f"in the prose, all of kind {d['all_of_kind']}.")
    print("   Those are the false friends -- the exact comparison under test.\n")

    print("STEP 1 -- DIVERGENCE")
    print(f"   identical to sighted: {n_iso}/{len(div)}   mean shape overlap "
          f"{mean_overlap:.3f}   diverged: {diverged}\n")

    print("STEP 2 -- the claim, re-scored blind")
    for corpus, v in per_corpus.items():
        print(f"   {corpus}:")
        for r in v["rows"]:
            print(f"      {r['motif']:<14}{r['ranking']:<24}"
                  f"{'yes' if r['analogue_beats_false_friend'] else 'NO'}")
        print(f"      -> {v['held']}/{v['of']}   best-match sighted "
              f"{v['best_match_sighted']:.1%} vs blind {v['best_match_blind']:.1%}"
              f"   inflation {v['inflation']}x")
        print(f"      -> relations annotated: sighted {v['relations_sighted']}, "
              f"blind {v['relations_blind']}")

    print(f"\n   this run: {report['blind_this_run']}")
    print(f"   ALL THREE CORPORA, blind: {report['blind_all_three_corpora']}  "
          f"(sighted was {report['sighted_all_three_corpora']})")
    print("\nSTEP 3 -- THE CONFOUND (read before the verdict)")
    for c, v in per_corpus.items():
        print(f"   {c:<12} blind/sighted relations = "
              f"{v['relation_ratio_blind_over_sighted']}   inflation {v['inflation']}x")
    print("   independent (EXP-032) ratio 0.85, inflation 1.339x  <- granularity matched")
    print("   Half the relations means less to match regardless of role-knowledge.")
    print("   And a 9-word gloss does not support the 4 relations the SIGHTED")
    print("   annotation gives it -- the gloss is the whole document.")
    print(f"\n>>> {report['verdict']}")


if __name__ == "__main__":
    main()
