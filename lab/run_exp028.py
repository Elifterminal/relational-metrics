"""EXP-028 -- Q-21. Does the measure see the process, or my encoding of it?

Every invariance this project has demonstrated is about VOCABULARY (what the
participants are called) and LABELS (which node is which). Representation
invariance -- the same process written down a different but equally legitimate
way -- has never been tested. If it fails, the cross-domain results are really
results about structures that share my modelling conventions, and everything
downstream needs re-scoping before it goes near a domain that writes equivalent
realities in different forms.

THE TEST IS COMPARATIVE, NOT ABSOLUTE. Re-encoding genuinely changes the
object: subdividing an edge adds nodes and relations, and an MDL code is right
to charge for them. Demanding an identical score would be demanding the measure
ignore real differences. The question that actually matters is:

    Does an equivalence-preserving re-encoding cost LESS than a genuine
    change of content?

If inserting a mediator costs more than inverting a causal sign, the measure
tracks the encoding rather than the process, whatever its absolute numbers.

PREDICTIONS, WRITTEN BEFORE THE FIRST RUN (protocol §1.7):
  1. relabel and retype cost ~0. These are the known invariances; if they cost
     anything the harness is broken, not the theory. Confidence: high.
  2. converse costs ~0. Confidence: medium. The mapping searches type
     substitutions, so renaming a type to its converse should be absorbed --
     but the DIRECTION flip is not something the mapping can undo, so this may
     fail, and if it does that is a real limitation and not a bug.
  3. mediate_one, subdivide_all and reify_one cost MORE than the content
     changes. Confidence: high -- and this is a prediction of FAILURE. The MDL
     code charges by size, and these transforms change size while the content
     controls do not. I expect the measure to be encoding-sensitive here.
  4. Therefore the headline verdict will be FAIL. Predicting failure in advance
     so that a pass would be the surprising outcome rather than a relief.

FALSIFICATION / what would make me wrong about my own measure: if the
size-changing re-encodings sit above every content control, the measure sees
the process, Q-21 closes clean, and prediction 3 is wrong.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from corpus import QUERIES, docs_for, query_doc                   # noqa: E402
from corpus_holdout import (HOLDOUT_QUERIES, holdout_docs_for,    # noqa: E402
                            holdout_query)
from measures import mdl_correspondence                           # noqa: E402
from ranking import format_ranking, rank_with_ties, strictly_above  # noqa: E402
from reprworlds import CHANGING, PRESERVING                       # noqa: E402
from structure import Relation, Structure                          # noqa: E402
import itertools                                                   # noqa: E402


def corr(a, b) -> float:
    return mdl_correspondence(a, b, DEFAULT_CODE).ratio


def transform_costs(base):
    """Correspondence of the base against each of its re-encodings."""
    self_score = corr(base, base)
    out = {"self": self_score, "preserving": {}, "changing": {}}
    for name, fn in PRESERVING.items():
        out["preserving"][name] = corr(base, fn(base))
    for name, fn in CHANGING.items():
        out["changing"][name] = corr(base, fn(base))
    return out


def ranking_survives(q, docs, transform):
    """Application-level: re-encode every document, does the claim survive?"""
    before = rank_with_ties({d.kind: corr(q.structure, d.structure) for d in docs})
    after = rank_with_ties({d.kind: corr(q.structure, transform(d.structure))
                            for d in docs})
    return {
        "before": format_ranking(before), "after": format_ranking(after),
        "claim_before": strictly_above(before, "X", "W"),
        "claim_after": strictly_above(after, "X", "W"),
    }


def isomorphic(a, b) -> bool:
    if len(a.nodes) != len(b.nodes) or a.m != b.m:
        return False
    na, nb = sorted(a.nodes), sorted(b.nodes)
    return any({(f[x], f[y], t) for x, y, t in a.edge_set()} == b.edge_set()
               for f in (dict(zip(na, p)) for p in itertools.permutations(nb)))


def size_matched(bases):
    """The rival explanation: is the effect just size?

    `delete_one` keeps the structure small; `subdivide_all` doubles it, and the
    MDL baseline grows with size. So the headline gap could be a size artifact
    rather than encoding sensitivity. This removes size from the comparison by
    subdividing BOTH sides -- content preserved vs content changed, at
    identical size.

    Also checks whether the two subdivided structures are isomorphic. If they
    were, equal scores would be CORRECT and "blind" would be the wrong word.
    """
    rows = []
    for _, s0 in bases:
        pure = corr(s0, subdivide := PRESERVING["subdivide_all"](s0))
        rew_s = PRESERVING["subdivide_all"](CHANGING["rewire_one"](s0))
        flp_s = PRESERVING["subdivide_all"](CHANGING["flip_type_one"](s0))
        rows.append({
            "base": s0.name,
            "preserved": pure,
            "rewired": corr(s0, rew_s),
            "flipped": corr(s0, flp_s),
            "discriminates": pure > corr(s0, rew_s) and pure > corr(s0, flp_s),
            "tie_is_correct_isomorphism": isomorphic(subdivide, rew_s),
        })
    return rows


def pad(s0, k):
    """k junk nodes in a ring. Says nothing whatever about any query."""
    nodes = list(s0.nodes) + [f"pad{i}" for i in range(k)]
    rels = list(s0.relations)
    if k > 1:
        rels += [Relation(f"pad{i}", f"pad{(i + 1) % k}", "POS") for i in range(k)]
    return Structure(s0.name + f"+pad{k}", tuple(nodes), tuple(rels), s0.domain)


def padding_probe():
    """If extra nodes buy the maximiser freedom, padding is an ATTACK: add junk,
    rank higher. Tested on the false friend, the document the measure is meant
    to rank BELOW the analogue."""
    out = []
    for m in QUERIES:
        q = query_doc(m).structure
        dd = {d.kind: d.structure for d in docs_for(m)}
        base_w = corr(q, dd["W"])
        best = max((corr(q, pad(dd["W"], k)), k) for k in (2, 4, 6, 8))
        out.append({
            "motif": m,
            "false_friend_unpadded": round(base_w, 4),
            "false_friend_best_padded": round(best[0], 4),
            "at_k": best[1],
            "padding_raises_score": best[0] > base_w + 1e-9,
            "analogue": round(corr(q, dd["X"]), 4),
            "padding_flips_ranking": best[0] > corr(q, dd["X"]),
        })
    return out


def main() -> None:
    bases = ([(m, query_doc(m).structure) for m in QUERIES]
             + [(m, holdout_query(m).structure) for m in HOLDOUT_QUERIES])

    per_base = {m: transform_costs(s) for m, s in bases}

    # aggregate: for each transform, its mean score across all base structures
    def mean_of(cls, name):
        return statistics.fmean(per_base[m][cls][name] for m, _ in bases)

    pres = {k: mean_of("preserving", k) for k in PRESERVING}
    chng = {k: mean_of("changing", k) for k in CHANGING}

    worst_preserving = min(pres, key=pres.get)
    best_changing = max(chng, key=chng.get)
    separated = pres[worst_preserving] > chng[best_changing]

    # which individual preserving transforms are free, and which are not
    self_mean = statistics.fmean(per_base[m]["self"] for m, _ in bases)
    free = {k: abs(v - self_mean) < 1e-9 for k, v in pres.items()}

    # application level: does the corpus claim survive re-encoding?
    app = {}
    for name, fn in PRESERVING.items():
        rows = []
        for m in QUERIES:
            rows.append(ranking_survives(query_doc(m), docs_for(m), fn))
        for m in HOLDOUT_QUERIES:
            rows.append(ranking_survives(holdout_query(m), holdout_docs_for(m), fn))
        app[name] = {
            "held": sum(r["claim_after"] for r in rows),
            "of": len(rows),
            "rows": rows,
        }

    sm = size_matched(bases)
    probe = padding_probe()

    report = {
        "experiment": "EXP-028",
        "size_matched_control": {
            "rows": sm,
            "discriminates": sum(r["discriminates"] for r in sm),
            "of": len(sm),
            "any_tie_explained_by_isomorphism":
                any(r["tie_is_correct_isomorphism"] for r in sm),
        },
        "padding_probe": {
            "rows": probe,
            "raises_score": sum(r["padding_raises_score"] for r in probe),
            "flips_ranking": sum(r["padding_flips_ranking"] for r in probe),
            "of": len(probe),
        },
        "question": "Q-21 -- is the measure invariant across equivalent re-encodings?",
        "n_base_structures": len(bases),
        "self_correspondence_mean": round(self_mean, 4),
        "preserving_mean": {k: round(v, 4) for k, v in pres.items()},
        "changing_mean": {k: round(v, 4) for k, v in chng.items()},
        "exactly_free": free,
        "worst_preserving": worst_preserving,
        "best_changing": best_changing,
        "separation_holds": separated,
        "verdict": "INVARIANT" if separated else "ENCODING-SENSITIVE",
        "application": {k: {"held": v["held"], "of": v["of"]} for k, v in app.items()},
        "by_base": per_base,
        "application_detail": app,
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp028.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-028  written to {out}")
    print(f"{len(bases)} base structures; self-correspondence = {self_mean:.4f}\n")

    print("CONTENT-PRESERVING re-encodings (should be cheap):")
    for k in sorted(pres, key=pres.get, reverse=True):
        tag = "exactly free" if free[k] else f"costs {self_mean - pres[k]:+.4f}"
        print(f"   {k:<16}{pres[k]:>9.4f}   {tag}")
    print("\nCONTENT-CHANGING controls (should be expensive):")
    for k in sorted(chng, key=chng.get, reverse=True):
        print(f"   {k:<16}{chng[k]:>9.4f}   costs {self_mean - chng[k]:+.4f}")

    print(f"\nworst preserving : {worst_preserving} at {pres[worst_preserving]:.4f}")
    print(f"best changing    : {best_changing} at {chng[best_changing]:.4f}")
    print(f"\n>>> VERDICT: {report['verdict']}")
    if not separated:
        print(f"    '{worst_preserving}' -- which changes nothing about the process --")
        print(f"    scores BELOW '{best_changing}', which changes the process.")

    print("\nSIZE-MATCHED CONTROL -- both sides subdivided, so size cannot explain it:")
    print(f"   {'base':<9}{'preserved':>11}{'rewired':>10}{'flipped':>10}   discriminates?")
    for r in sm:
        print(f"   {r['base']:<9}{r['preserved']:>11.4f}{r['rewired']:>10.4f}"
              f"{r['flipped']:>10.4f}   {'yes' if r['discriminates'] else 'NO'}")
    print(f"   -> discriminates on {report['size_matched_control']['discriminates']}"
          f"/{len(sm)}; ties explained by isomorphism: "
          f"{report['size_matched_control']['any_tie_explained_by_isomorphism']}")

    print("\nPADDING PROBE -- can junk nodes buy a false friend a better score?")
    for r in probe:
        print(f"   {r['motif']:<13}{r['false_friend_unpadded']:>8.4f} -> "
              f"{r['false_friend_best_padded']:>7.4f} at k={r['at_k']}   "
              f"{'RISES' if r['padding_raises_score'] else 'no gain'}"
              f"{'  AND FLIPS THE RANKING' if r['padding_flips_ranking'] else ''}")
    print(f"   -> raises the score on {report['padding_probe']['raises_score']}/{len(probe)}, "
          f"flips the ranking on {report['padding_probe']['flips_ranking']}/{len(probe)}")

    print("\nAPPLICATION LEVEL -- does 'analogue beats false friend' survive re-encoding?")
    for k, v in app.items():
        mark = "ok " if v["held"] == v["of"] else "LOST"
        print(f"   {k:<16}{v['held']}/{v['of']}   {mark}")


if __name__ == "__main__":
    main()
