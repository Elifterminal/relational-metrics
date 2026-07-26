"""EXP-029 -- Q-24. Canonicalise before measuring, and see what it costs.

EXP-028 left the measure blind across equivalent re-encodings. The route taken
here is to quotient the representational vertices out BEFORE measuring, rather
than to let a relation match a path. That choice is deliberate: EXP-028 showed
that freedom in the alignment space is what destroyed discrimination, so
answering it by enlarging that space treats the symptom with more of the cause.
The invariance should belong to the definition of the measured object.

The standard name for the target invariance is GRAPH HOMEOMORPHISM -- equivalence
under subdivision and suppression of degree-2 vertices (LaPaugh & Rivest, JCSS
20(2), 1980, for the matching version). What this project needs is the typed,
directed, DECLARED variant: suppression is legal only where the vocabulary
declares a composition.

A REWRITE SYSTEM IS ONLY TRUSTWORTHY IF IT TERMINATES AND IS CONFLUENT, so those
are tested here rather than assumed -- if applying legal contractions in
different orders gave different normal forms, the "canonical" form would be a
function of iteration order and every downstream number would be arbitrary. That
is the same class of defect as the hash tie-break EXP-027 had to retract.

PREDECLARED FALSIFICATION: if canonicalisation restores invariance but costs the
analogue-over-false-friend capability on ANY corpus, it is trading one failure for
a worse one and gets recorded as refuted -- not tuned, not scoped, not explained.

THE HONEST LIMIT, declared before running: whether a vertex is a representational
artifact or a real participant is NOT decidable from structure. A pure directed
cycle has in-degree and out-degree 1 everywhere. So two modes are measured:
DECLARED (the real participants are named) and BLIND (suppress anything
suppressible). Blind mode is included to measure the damage, not to recommend it.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from canonical import canonical                                   # noqa: E402
from codes import DEFAULT_CODE                                    # noqa: E402
from corpus import QUERIES, docs_for, query_doc                   # noqa: E402
from corpus_holdout import (HOLDOUT_QUERIES, holdout_docs_for,    # noqa: E402
                            holdout_query)
from corpus_independent import (INDEPENDENT_QUERIES,              # noqa: E402
                                independent_docs_for, independent_query)
from measures import mdl_correspondence                           # noqa: E402
from ranking import rank_with_ties, strictly_above                # noqa: E402
from reprworlds import (CHANGING, PRESERVING,                     # noqa: E402
                        protected_for)

SEED = 7717


def corr(a, b):
    return mdl_correspondence(a, b, DEFAULT_CODE).ratio


def all_bases():
    return ([query_doc(m).structure for m in QUERIES]
            + [holdout_query(m).structure for m in HOLDOUT_QUERIES])


def rewrite_properties(bases):
    """Termination, idempotence, confluence -- tested, not assumed."""
    rng = random.Random(SEED)
    rows = []
    for s in bases:
        subject = PRESERVING["subdivide_all"](s)
        prot = protected_for("subdivide_all", s, subject)
        base_form = canonical(subject, prot)

        # confluence: many rewrite orders, one normal form?
        forms = set()
        for _ in range(24):
            order = list(subject.nodes)
            rng.shuffle(order)
            forms.add(canonical(subject, prot, order=order).edge_set())
        rows.append({
            "base": s.name,
            "terminates": True,                       # reaching here means it halted
            "idempotent": canonical(base_form, prot).edge_set() == base_form.edge_set(),
            "confluent": len(forms) == 1,
            "n_distinct_normal_forms": len(forms),
            "recovers_original": base_form.edge_set() == s.edge_set(),
        })
    return rows


def invariance(bases):
    """After canonicalising both sides, do preserving transforms come out free?"""
    rows = {}
    for name, fn in list(PRESERVING.items()) + list(CHANGING.items()):
        keep = name in PRESERVING
        scores, exact = [], 0
        for s in bases:
            t = fn(s)
            a = canonical(s, frozenset(s.nodes))
            b = canonical(t, protected_for(name, s, t))
            scores.append(corr(a, b))
            exact += a.edge_set() == b.edge_set()
        rows[name] = {
            "preserving": keep,
            "mean": sum(scores) / len(scores),
            "exact_recovery": exact,
            "of": len(bases),
        }
    return rows


def capability(corpora):
    """Does the load-bearing claim survive canonicalisation? And under re-encoding?"""
    out = {}
    for label, motifs, qf, df in corpora:
        plain, canon, canon_sub = 0, 0, 0
        for m in motifs:
            q = qf(m)
            docs = list(df(m))
            prot_q = frozenset(q.structure.nodes)

            g = rank_with_ties({d.kind: corr(q.structure, d.structure) for d in docs})
            plain += strictly_above(g, "X", "W")

            cq = canonical(q.structure, prot_q)
            g2 = rank_with_ties({
                d.kind: corr(cq, canonical(d.structure, frozenset(d.structure.nodes)))
                for d in docs})
            canon += strictly_above(g2, "X", "W")

            # the case EXP-028 broke: documents arrive subdivided
            g3 = rank_with_ties({
                d.kind: corr(cq, canonical(
                    PRESERVING["subdivide_all"](d.structure),
                    protected_for("subdivide_all", d.structure,
                                  PRESERVING["subdivide_all"](d.structure))))
                for d in docs})
            canon_sub += strictly_above(g3, "X", "W")
        out[label] = {"plain": plain, "canonical": canon,
                      "canonical_subdivided": canon_sub, "of": len(motifs)}
    return out


def blind_damage(bases):
    """No declaration available. How much of the structure does blind mode eat?"""
    rows = []
    for s in bases:
        b = canonical(s, frozenset())
        rows.append({"base": s.name, "nodes_before": s.n, "nodes_after": b.n,
                     "relations_before": s.m, "relations_after": b.m,
                     "unchanged": b.edge_set() == s.edge_set()})
    return rows


def main() -> None:
    bases = all_bases()
    props = rewrite_properties(bases)
    inv = invariance(bases)
    cap = capability([
        ("dev", QUERIES, query_doc, docs_for),
        ("held-out", HOLDOUT_QUERIES, holdout_query, holdout_docs_for),
        ("independent", INDEPENDENT_QUERIES, independent_query, independent_docs_for),
    ])
    blind = blind_damage(bases)

    pres = {k: v for k, v in inv.items() if v["preserving"]}
    chng = {k: v for k, v in inv.items() if not v["preserving"]}
    worst_p = min(pres, key=lambda k: pres[k]["mean"])
    best_c = max(chng, key=lambda k: chng[k]["mean"])
    separated = pres[worst_p]["mean"] > chng[best_c]["mean"]

    cap_ok = all(v["canonical"] == v["of"] for v in cap.values())
    cap_sub_ok = all(v["canonical_subdivided"] == v["of"] for v in cap.values())

    # The DECLARED equivalence class is subdivision/suppression -- typed graph
    # homeomorphism. `converse` (reversal) and `reify_one` (factor node) are
    # equally legitimate re-encodings but are NOT in that class, and the
    # canonicaliser declares no rewrite for them. Scoring them as failures of
    # this fix would be scoring it against a claim it never made; scoring them
    # as successes would be hiding two known gaps. They are reported separately.
    IN_CLASS = ("relabel", "retype", "mediate_one", "subdivide_all")
    in_class = {k: v for k, v in pres.items() if k in IN_CLASS}
    out_class = {k: v for k, v in pres.items() if k not in IN_CLASS}
    worst_in = min(in_class, key=lambda k: in_class[k]["mean"])
    separated_in_class = in_class[worst_in]["mean"] > chng[best_c]["mean"]

    report = {
        "experiment": "EXP-029",
        "route": "canonicalise before measuring (declared typed graph homeomorphism)",
        "rewrite_properties": props,
        "all_terminate": all(r["terminates"] for r in props),
        "all_idempotent": all(r["idempotent"] for r in props),
        "all_confluent": all(r["confluent"] for r in props),
        "all_recover_original": all(r["recovers_original"] for r in props),
        "invariance": inv,
        "worst_preserving": worst_p, "best_changing": best_c,
        "separation_holds": separated,
        "capability": cap,
        "capability_preserved": cap_ok,
        "capability_under_subdivision": cap_sub_ok,
        "blind_mode": blind,
        "blind_mode_damages": sum(1 for r in blind if not r["unchanged"]),
        "declared_class": list(IN_CLASS),
        "separation_within_declared_class": separated_in_class,
        "worst_in_class": worst_in,
        "out_of_class_unfixed": sorted(out_class),
        # Predeclared falsification was CAPABILITY LOSS. It did not occur.
        "predeclared_falsification_met": not (cap_ok and cap_sub_ok),
        "verdict": ("SUPPORTED WITHIN DECLARED CLASS"
                    if (separated_in_class and cap_ok and cap_sub_ok)
                    else "REFUTED"),
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp029.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-029  written to {out}\n")

    print("REWRITE SYSTEM -- tested, not assumed")
    print(f"   terminates on all      : {report['all_terminate']}")
    print(f"   idempotent on all      : {report['all_idempotent']}")
    print(f"   confluent on all       : {report['all_confluent']}"
          f"  (24 random orders per structure)")
    print(f"   recovers the original  : {report['all_recover_original']}\n")

    print("AFTER CANONICALISING BOTH SIDES:")
    print(f"   {'transform':<16}{'mean':>9}{'exact':>8}   class")
    for k in sorted(inv, key=lambda k: -inv[k]["mean"]):
        v = inv[k]
        print(f"   {k:<16}{v['mean']:>9.4f}{v['exact_recovery']:>4}/{v['of']}   "
              f"{'preserving' if v['preserving'] else 'CHANGING'}")
    print(f"\n   worst preserving {worst_p} = {pres[worst_p]['mean']:.4f}")
    print(f"   best changing    {best_c} = {chng[best_c]['mean']:.4f}")
    print(f"   >>> separated: {separated}")

    print("\nCAPABILITY -- analogue strictly above false friend:")
    print(f"   {'corpus':<14}{'plain':>7}{'canonical':>11}{'canon+subdivided':>19}")
    for k, v in cap.items():
        print(f"   {k:<14}{v['plain']}/{v['of']:<5}{v['canonical']}/{v['of']:<10}"
              f"{v['canonical_subdivided']}/{v['of']}")

    print(f"\nBLIND MODE (no declaration): damages {report['blind_mode_damages']}"
          f"/{len(blind)} base structures")
    for r in blind:
        if not r["unchanged"]:
            print(f"   {r['base']}: {r['nodes_before']}->{r['nodes_after']} nodes, "
                  f"{r['relations_before']}->{r['relations_after']} relations")

    print("\nSCORED AGAINST THE CLASS IT DECLARES (subdivision / suppression):")
    print(f"   separation within declared class : {separated_in_class}"
          f"   (worst in-class {worst_in} = {in_class[worst_in]['mean']:.4f}"
          f" vs best changing {chng[best_c]['mean']:.4f})")
    print(f"   capability preserved             : {cap_ok}")
    print(f"   capability under subdivision     : {cap_sub_ok}"
          f"   (EXP-028 had this at 2/6)")
    print(f"   predeclared falsification met    : "
          f"{report['predeclared_falsification_met']}  (it was capability loss)")
    print(f"   NOT addressed, no rewrite declared: {', '.join(sorted(out_class))}")
    print(f"\n>>> VERDICT: {report['verdict']}")


if __name__ == "__main__":
    main()
