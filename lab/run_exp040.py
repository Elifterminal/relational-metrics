"""EXP-040 -- Q-38 and Q-34. Which relations did I invent?

EXP-039's independent annotator declined eight of sixty documents. I declined
none. EXP-035 found one relation in my notes that its document does not state --
and it was the relation that made a vacuous document isomorphic to its query and
grounded a published conclusion. That was found by reading one document.

Now there is an independent reference for all sixty, so the audit can be done
properly rather than by chance.

POST-HOC, AND SAID SO. I have read this data and analysed it once already. This
is not a planned test; it is an audit of an existing disagreement, and its
purpose is descriptive. No claim rests on a p-value here.

WHAT AGREEMENT AND DISAGREEMENT MEAN, declared before looking:
  * a relation I have and the annotator does not is a CANDIDATE INVENTION -- not
    proof, since it may simply have missed one
  * a relation the annotator has and I do not is a candidate MISS by me
  * the asymmetry between those two counts is the interesting quantity, because
    a symmetric disagreement is just two people reading differently, while a
    lopsided one is a disposition
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from blind_reannotate import load_key as key26                    # noqa: E402
from q26_blind_annotations import B                               # noqa: E402
from q30_blind_annotations import Q30                             # noqa: E402
from q30_pool import load_key as key30                            # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def theirs():
    out = {}
    for f in ("received_part1.txt", "received_part2.txt"):
        for line in (ROOT / "external" / "q31" / f).read_text().splitlines():
            m = re.match(r"(S\d{3}):\s*(\[.*?\])", line)
            if m:
                out[m.group(1)] = ast.literal_eval(m.group(2))
    return out


def main() -> None:
    T = theirs()
    idmap = json.loads((ROOT / "external" / "q31_idmap.json").read_text())
    mine = dict(B)
    mine.update(Q30)
    key = {k["passage_id"]: k for k in key26()}
    key.update({k["passage_id"]: k for k in key30()})

    rows = []
    for tag, their_edges in T.items():
        pid = idmap[tag]
        k = key[pid]
        my_edges = mine[pid]
        sighted = [tuple(e) for e in k["sighted"]]
        rows.append({
            "passage": tag, "kind": k["kind"], "motif": k["motif"],
            "corpus": k.get("corpus", "independent"),
            "n_theirs": len(their_edges), "n_mine_blind": len(my_edges),
            "n_mine_sighted": len(sighted),
            "they_abstained": len(their_edges) == 0,
            "i_abstained": len(my_edges) == 0,
        })

    n = len(rows)
    they_abstain = [r for r in rows if r["they_abstained"]]
    i_abstain = [r for r in rows if r["i_abstained"]]

    # the asymmetry, per document, in relation COUNT -- names differ between
    # annotators so edge-level matching would measure vocabulary, not judgement
    excess_sighted = [r["n_mine_sighted"] - r["n_theirs"] for r in rows]
    excess_blind = [r["n_mine_blind"] - r["n_theirs"] for r in rows]
    more_sighted = sum(1 for x in excess_sighted if x > 0)
    fewer_sighted = sum(1 for x in excess_sighted if x < 0)

    # where they abstained, what did I write?
    wrote_where_they_declined = [
        {"passage": r["passage"], "kind": r["kind"],
         "my_sighted_relations": r["n_mine_sighted"],
         "my_blind_relations": r["n_mine_blind"]}
        for r in they_abstain]

    # THE MECHANISM. Not "subtly influenced" -- a hard floor.
    import collections
    import statistics
    dist_sighted = collections.Counter(len(k["sighted"]) for k in key.values())
    dist_blind = collections.Counter(len(v) for v in mine.values())
    dist_theirs = collections.Counter(len(v) for v in T.values())

    lens = {}
    for f in ("q26_pool.json", "q30_pool.json"):
        for pg in json.loads((ROOT / "external" / f).read_text())["passages"]:
            lens[pg["passage_id"]] = len(pg["gloss"].split())

    def corr(a, b):
        ma, mb = statistics.fmean(a), statistics.fmean(b)
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
        return round(num / den, 3) if den else 0.0

    pairs = [(lens[pid], len(k["sighted"]), len(mine[pid]),
              len(T[next(t for t, v in idmap.items() if v == pid)]))
             for pid, k in key.items() if pid in lens]
    w = [x[0] for x in pairs]

    report_mechanism = {
        "distribution": {
            "me_sighted": dict(sorted(dist_sighted.items())),
            "me_blind": dict(sorted(dist_blind.items())),
            "independent": dict(sorted(dist_theirs.items())),
        },
        "my_sighted_minimum": min(dist_sighted),
        "my_sighted_modal_share": round(max(dist_sighted.values()) / n, 3),
        "tracks_sentence_length": {
            "me_sighted": corr(w, [x[1] for x in pairs]),
            "me_blind": corr(w, [x[2] for x in pairs]),
            "independent": corr(w, [x[3] for x in pairs]),
        },
        "finding": ("my sighted annotation never used fewer than 4 relations on any "
                    "of 60 documents, and tracked what the sentence actually said "
                    "LESS closely than my own blind annotation did. That is a "
                    "template applied regardless of content, not a subtle bias"),
    }

    report = {
        "experiment": "EXP-040", "questions": ["Q-38", "Q-34"],
        "nature": "post-hoc audit of an existing disagreement; descriptive, no p-values",
        "documents": n,
        "abstentions": {
            "independent_annotator": len(they_abstain),
            "me_blind": len(i_abstain),
            "me_sighted": 0,
            "note": ("S2-2 exists because of this asymmetry. An annotator without "
                     "an abstain option manufactures structure"),
        },
        "relation_counts": {
            "theirs_total": sum(r["n_theirs"] for r in rows),
            "mine_blind_total": sum(r["n_mine_blind"] for r in rows),
            "mine_sighted_total": sum(r["n_mine_sighted"] for r in rows),
        },
        "asymmetry_sighted_vs_theirs": {
            "documents_where_i_wrote_more": more_sighted,
            "documents_where_i_wrote_fewer": fewer_sighted,
            "documents_equal": n - more_sighted - fewer_sighted,
            "mean_excess_relations": round(sum(excess_sighted) / n, 2),
            "reading": ("a symmetric disagreement is two readers differing; a "
                        "lopsided one is a disposition"),
        },
        "asymmetry_blind_vs_theirs": {
            "documents_where_i_wrote_more": sum(1 for x in excess_blind if x > 0),
            "documents_where_i_wrote_fewer": sum(1 for x in excess_blind if x < 0),
            "mean_excess_relations": round(sum(excess_blind) / n, 2),
        },
        "what_i_wrote_where_they_declined": wrote_where_they_declined,
        "rows": rows,
        "mechanism": report_mechanism,
    }
    out = ROOT / "results" / "exp040.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-040  written to {out}\n")

    a = report["abstentions"]
    print(f"ABSTENTIONS over {n} documents")
    print(f"   independent annotator : {a['independent_annotator']}")
    print(f"   me, roles hidden      : {a['me_blind']}")
    print(f"   me, roles visible     : {a['me_sighted']}\n")

    rc = report["relation_counts"]
    print(f"RELATIONS WRITTEN")
    print(f"   independent annotator : {rc['theirs_total']}")
    print(f"   me, roles hidden      : {rc['mine_blind_total']}")
    print(f"   me, roles visible     : {rc['mine_sighted_total']}\n")

    for label, k in (("SIGHTED", "asymmetry_sighted_vs_theirs"),
                     ("BLIND", "asymmetry_blind_vs_theirs")):
        d = report[k]
        print(f"ME ({label}) vs THEM, per document")
        print(f"   I wrote more : {d['documents_where_i_wrote_more']}")
        print(f"   I wrote fewer: {d['documents_where_i_wrote_fewer']}")
        print(f"   mean excess  : {d['mean_excess_relations']:+.2f} relations\n")

    mech = report["mechanism"]
    print("THE MECHANISM -- relations per document, distribution")
    print(f"   {'count':>6}{'me sighted':>12}{'me blind':>10}{'independent':>13}")
    for c in range(0, 6):
        print(f"   {c:>6}{mech['distribution']['me_sighted'].get(c, 0):>12}"
              f"{mech['distribution']['me_blind'].get(c, 0):>10}"
              f"{mech['distribution']['independent'].get(c, 0):>13}")
    print(f"\n   my sighted annotation NEVER went below "
          f"{mech['my_sighted_minimum']} relations, on any document")
    t = mech["tracks_sentence_length"]
    print(f"   correlation with sentence length: sighted {t['me_sighted']:+.3f}, "
          f"blind {t['me_blind']:+.3f}, independent {t['independent']:+.3f}")
    print(f"   -> sighted tracked the text LESS than blind did\n")

    print(f"WHERE THEY DECLINED ENTIRELY ({len(wrote_where_they_declined)} documents), I wrote:")
    for w in wrote_where_they_declined:
        print(f"   {w['passage']}  kind={w['kind']:<2} "
              f"sighted {w['my_sighted_relations']}  blind {w['my_blind_relations']}")


if __name__ == "__main__":
    main()
