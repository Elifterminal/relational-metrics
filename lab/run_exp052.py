"""EXP-052 -- Q-41. The type-substitution search can invert polarity. Does it matter?

EXP-050 found `mdl_correspondence` matching a REINFORCING loop to a BALANCING
loop at exactly 0 distance, by choosing the type map {POS->NEG, NEG->POS}. A
reinforcing loop and a balancing loop are the canonical case of "same
participants, different relationship", so a measure that cannot separate them
has a hole where the central claim is.

The awkward part is that type-blindness is not a bug. It is the mechanism that
lets a geological POS correspond to an ecological GROWS, and it produces the
P==X vocabulary-blindness signature running through the entire corpus record.
Removing it to fix the sign flip could remove the thing the project exists to
find.

So the instrument is POLARITY-preserving rather than name-preserving --
strictly weaker, permits POS->GROWS, forbids POS->NEG -- and part D exists to
check that it actually keeps what it is supposed to keep. `relalgebra.POLARITY`
already declares a sign for every relation type in all three corpora, so
nothing is invented here.

ARITHMETIC BEFORE EVIDENCE: filtering can only remove mappings, and every score
is a max over mappings, so a constrained score is <= its unconstrained score
ALWAYS. Score drops are not findings. Only ranking changes carry information,
and the reporting below is built so a drop cannot be mistaken for one.

Plan locked at external/plans/EXP-052.json before this file ran.
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import CODES, DEFAULT_CODE                              # noqa: E402
from corpus import QUERIES, docs_for, query_doc                    # noqa: E402
from corpus_holdout import HOLDOUT_QUERIES, holdout_docs_for, holdout_query   # noqa: E402
from corpus_independent import (INDEPENDENT_QUERIES,               # noqa: E402
                                independent_docs_for, independent_query)
from measures import mdl_correspondence                            # noqa: E402
from protocol2 import Stage2Result, check_capacity_to_fail, require_locked_plan  # noqa: E402
from ranking import format_ranking, rank_with_ties, strictly_above, tied  # noqa: E402
from relalgebra import FAMILY_OF, POLARITY                         # noqa: E402
from structure import Relation, Structure                          # noqa: E402


# -- the instrument ---------------------------------------------------------

def polarity_preserving(src_type: str, dst_type: str) -> bool:
    """Permit a type substitution only when it keeps the declared sign.

    POS -> GROWS  ok   (both amplifying: cross-vocabulary correspondence lives here)
    POS -> NEG    no   (a global flip turns reinforcement into balance)

    An undeclared type is permitted through unchanged rather than silently
    blocked -- blocking on absence would make the constraint depend on how
    complete FAMILIES happens to be, which is a different experiment.
    """
    ps, pd = POLARITY.get(src_type), POLARITY.get(dst_type)
    if ps is None or pd is None:
        return True
    return ps == pd


def inverts(type_map) -> bool:
    """Does this chosen map flip the sign of at least one relation type?"""
    return any(not polarity_preserving(s, t) for s, t in type_map)


def flip(t: str) -> str:
    """A type's family opposite. Identity if undeclared."""
    fam = FAMILY_OF.get(t)
    if fam is None:
        return t
    return fam[1] if t == fam[0] else fam[0]


# -- Clopper-Pearson --------------------------------------------------------

def _beta_inv(p, a, b, lo=0.0, hi=1.0):
    for _ in range(200):
        mid = (lo + hi) / 2
        if _beta_cdf(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _beta_cdf(x, a, b, n=4000):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lc = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    h, s = x / n, 0.0
    for i in range(n + 1):
        t = min(max(i * h, 1e-12), 1 - 1e-12)
        w = 1 if i in (0, n) else (4 if i % 2 else 2)
        s += w * math.exp(lc + (a - 1) * math.log(t) + (b - 1) * math.log(1 - t))
    return min(1.0, s * h / 3)


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return (0.0, 1.0)
    lo = 0.0 if k == 0 else _beta_inv(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else _beta_inv(1 - alpha / 2, k + 1, n - k)
    return (round(lo, 4), round(hi, 4))


# -- corpora ----------------------------------------------------------------

CORPORA = (
    ("dev (mine)", QUERIES, query_doc, docs_for),
    ("held-out (mine)", HOLDOUT_QUERIES, holdout_query, holdout_docs_for),
    ("independent (externally written)", INDEPENDENT_QUERIES,
     independent_query, independent_docs_for),
)


def score_motif(q, docs, code, tf):
    return {k: mdl_correspondence(q.structure, s, code, type_filter=tf).ratio
            for k, s in docs.items()}


def part_a_prevalence():
    """How often does the UNCONSTRAINED search actually choose to invert?"""
    out = {}
    for label, motifs, q_fn, d_fn in CORPORA:
        pairs, inverting, detail = 0, 0, []
        for m in motifs:
            q = q_fn(m)
            for d in d_fn(m):
                res = mdl_correspondence(q.structure, d.structure, DEFAULT_CODE)
                pairs += 1
                if inverts(res.type_map):
                    inverting += 1
                    detail.append({"motif": m, "kind": d.kind,
                                   "type_map": dict(res.type_map),
                                   "ratio": round(res.ratio, 6)})
        out[label] = {"pairs": pairs, "inverting": inverting,
                      "rate": round(inverting / pairs, 4) if pairs else 0.0,
                      "families_in_play": sorted({FAMILY_OF.get(t, (t,))[0]
                                                  for m in motifs
                                                  for d in d_fn(m)
                                                  for t in d.structure.types}),
                      "examples": detail[:8]}
    return out


def part_b_impact():
    """Rerun the published record under the constraint. Rankings only."""
    by_code = {}
    for code in CODES:
        rows, changed = [], 0
        for label, motifs, q_fn, d_fn in CORPORA:
            for m in motifs:
                q = q_fn(m)
                docs = {d.kind: d.structure for d in d_fn(m)}
                free = score_motif(q, docs, code, None)
                cons = score_motif(q, docs, code, polarity_preserving)
                gf, gc = rank_with_ties(free), rank_with_ties(cons)
                xw_f, xw_c = strictly_above(gf, "X", "W"), strictly_above(gc, "X", "W")
                px_f, px_c = tied(gf, "P", "X"), tied(gc, "P", "X")
                # Two published verdicts per motif. Score changes are excluded
                # from this count on purpose -- see the module docstring.
                delta = int(xw_f != xw_c) + int(px_f != px_c)
                changed += delta
                rows.append({
                    "corpus": label, "motif": m,
                    "ranking_free": format_ranking(gf),
                    "ranking_constrained": format_ranking(gc),
                    "ranking_identical": gf == gc,
                    "X_above_W_free": xw_f, "X_above_W_constrained": xw_c,
                    "P_ties_X_free": px_f, "P_ties_X_constrained": px_c,
                    "verdicts_changed": delta,
                    "max_score_drop": round(max(free[k] - cons[k] for k in free), 6),
                })
        n_motifs = len(rows)
        by_code[code.name] = {
            "rows": rows,
            "motifs": n_motifs,
            "published_verdicts": 2 * n_motifs,
            "verdicts_changed": changed,
            "rankings_identical": sum(r["ranking_identical"] for r in rows),
            "X_above_W_free": f"{sum(r['X_above_W_free'] for r in rows)}/{n_motifs}",
            "X_above_W_constrained": f"{sum(r['X_above_W_constrained'] for r in rows)}/{n_motifs}",
            "P_ties_X_free": f"{sum(r['P_ties_X_free'] for r in rows)}/{n_motifs}",
            "P_ties_X_constrained": f"{sum(r['P_ties_X_constrained'] for r in rows)}/{n_motifs}",
            "any_score_moved": any(r["max_score_drop"] > 1e-12 for r in rows),
            "motifs_with_score_movement": sum(1 for r in rows if r["max_score_drop"] > 1e-12),
        }
    return by_code


# -- part C: the degeneracy itself ------------------------------------------

def random_structure(rng, m, n_nodes=5, family=("POS", "NEG")):
    nodes = tuple(f"n{i}" for i in range(n_nodes))
    seen, rels = set(), []
    while len(rels) < m:
        s, d = rng.sample(nodes, 2)
        t = rng.choice(family)
        if (s, d) in seen:
            continue
        seen.add((s, d))
        rels.append(Relation(s, d, t))
    return Structure(f"s{m}", nodes, tuple(rels))


def inverted_twin(s: Structure) -> Structure:
    """Same wiring, every relation's sign flipped. Reinforcing <-> balancing."""
    return Structure(s.name + "_flip", s.nodes,
                     tuple(Relation(r.src, r.dst, flip(r.rtype), r.weight)
                           for r in s.relations), s.domain)


def part_c_sweep(seeds_per_m=40, rerun_seeds=200):
    def run(m, n_seeds):
        bites_free = bites_cons = 0
        sym = 0
        for i in range(n_seeds):
            rng = random.Random(90_000 + m * 1000 + i)
            s = random_structure(rng, m)
            t = inverted_twin(s)
            # "Bites" == the flipped twin is scored as indistinguishable from
            # the structure compared with itself. Exact equality, not close.
            self_free = mdl_correspondence(s, s, DEFAULT_CODE).ratio
            twin_free = mdl_correspondence(s, t, DEFAULT_CODE).ratio
            self_c = mdl_correspondence(s, s, DEFAULT_CODE,
                                        type_filter=polarity_preserving).ratio
            twin_c = mdl_correspondence(s, t, DEFAULT_CODE,
                                        type_filter=polarity_preserving).ratio
            if abs(self_free - twin_free) < 1e-12:
                bites_free += 1
            if abs(self_c - twin_c) < 1e-12:
                bites_cons += 1
            pols = [POLARITY[r.rtype] for r in s.relations]
            if pols.count(1) == pols.count(-1):
                sym += 1
        return bites_free, bites_cons, sym, n_seeds

    out = {}
    for m in range(2, 9):
        bf, bc, sym, n = run(m, seeds_per_m)
        rate = bf / n
        reran = False
        # Predeclared: an intermediate rate gets more seeds before it is reported.
        if 0.15 < rate < 0.85:
            bf, bc, sym, n = run(m, rerun_seeds)
            rate, reran = bf / n, True
        out[str(m)] = {
            "seeds": n, "reran_at_higher_n": reran,
            "degeneracy_rate_unconstrained": round(rate, 4),
            "ci95_unconstrained": clopper_pearson(bf, n),
            "degeneracy_rate_constrained": round(bc / n, 4),
            "ci95_constrained": clopper_pearson(bc, n),
            "symmetric_polarity_multiset_rate": round(sym / n, 4),
        }
    return out


# -- part D: the control that must be able to fail --------------------------

VOCAB_A = ("POS", "NEG")
VOCAB_B = ("GROWS", "PRUNES")


def _translate(s: Structure, faithful: bool) -> Structure:
    """Render s in the GROWS/PRUNES vocabulary.

    faithful=True  : amplifying -> amplifying, damping -> damping
    faithful=False : the perturbation -- sign inverted in translation
    """
    def t(rt):
        i = VOCAB_A.index(rt)
        return VOCAB_B[i] if faithful else VOCAB_B[1 - i]
    return Structure(s.name + "_tr", s.nodes,
                     tuple(Relation(r.src, r.dst, t(r.rtype), r.weight)
                           for r in s.relations), "other")


def part_d_admissibility():
    rng = random.Random(5252)
    src = random_structure(rng, 5)
    faithful = _translate(src, True)
    inverted = _translate(src, False)

    self_ratio = mdl_correspondence(src, src, DEFAULT_CODE,
                                    type_filter=polarity_preserving).ratio
    good = mdl_correspondence(src, faithful, DEFAULT_CODE,
                              type_filter=polarity_preserving)
    bad = mdl_correspondence(src, inverted, DEFAULT_CODE,
                             type_filter=polarity_preserving)

    preserved = abs(good.ratio - self_ratio) < 1e-9 and good.matched == src.m

    # protocol2: the control must demonstrate it CAN fail. Perturbation =
    # inverting the translation. The constrained measure must notice.
    check_capacity_to_fail(
        "polarity-preserving keeps cross-vocabulary correspondence",
        lambda: bad.ratio < good.ratio - 1e-9 or bad.matched < good.matched)

    return {
        "self_ratio": round(self_ratio, 6),
        "faithful_translation_ratio": round(good.ratio, 6),
        "faithful_matched": f"{good.matched}/{src.m}",
        "faithful_type_map": dict(good.type_map),
        "inverted_translation_ratio": round(bad.ratio, 6),
        "inverted_matched": f"{bad.matched}/{src.m}",
        "cross_vocabulary_preserved": preserved,
        "constraint_admissible": preserved,
        "control_can_fail": True,
    }


# -- verdict ----------------------------------------------------------------

def decide(a, b, c, d):
    changed = b[DEFAULT_CODE.name]["verdicts_changed"]
    code_agree = len({v["verdicts_changed"] for v in b.values()}) == 1
    moved = b[DEFAULT_CODE.name]["motifs_with_score_movement"]
    n_motifs = b[DEFAULT_CODE.name]["motifs"]
    ever_bites = any(v["degeneracy_rate_unconstrained"] > 0 for v in c.values())

    if not d["constraint_admissible"]:
        band = "constraint inadmissible"
        text = ("Part D failed: polarity-preserving breaks cross-vocabulary "
                "correspondence, so the freedom is load-bearing and the "
                "degeneracy is an accepted cost of the mechanism that makes "
                "the measure work at all.")
    elif changed == 0 and moved > 0:
        band = "prediction space wrong (ii) -- margins moved, verdicts did not"
        text = (f"The constraint moved scores on {moved}/{n_motifs} motifs and "
                f"changed no verdict anywhere. Q-41 is a question about "
                f"CONFIDENCE, not about verdicts. Reporting it as '0 changes' "
                f"would say nothing happened, and something did.")
    elif changed == 0:
        band = "0 changes -- scope limit, constraint not adopted"
        text = ("The freedom is real and never exercised on this corpus. Every "
                "corpus claim gains a scope note rather than a correction, and "
                "the constraint is NOT adopted: an intervention that changes "
                "nothing is a modelling choice bought with no evidence.")
    elif changed <= 2:
        band = "1-2 changes -- semantic, not empirical"
        text = ("The freedom does work on a minority of cases and neither "
                "regime is empirically privileged. Q-41 stays open until the "
                "semantic argument is made and declared.")
    else:
        band = "3+ changes -- retraction-level"
        text = ("Published results depend on polarity inversion. The affected "
                "claims are demoted and re-run under both regimes.")

    if not ever_bites:
        band += " | prediction space wrong (i): degeneracy never reproduced"
        text += (" Separately, part C never reproduced the degeneracy, which "
                 "would make EXP-050's observation narrower than Q-41 assumed.")

    return {"band": band, "verdicts_changed": changed,
            "codes_agree": code_agree, "statement": text}


def main() -> None:
    plan = require_locked_plan("EXP-052")

    a = part_a_prevalence()
    b = part_b_impact()
    c = part_c_sweep()
    d = part_d_admissibility()
    v = decide(a, b, c, d)

    rows = b[DEFAULT_CODE.name]["rows"]
    payload = {
        "question": "Q-41",
        "instrument": "polarity-preserving type map (weaker than name-preserving)",
        "monotonicity": "constrained ratio <= unconstrained ratio by construction; "
                        "only ranking changes are evidence",
        "part_a_prevalence": a,
        "part_b_impact": b,
        "part_c_degeneracy_sweep": c,
        "part_d_admissibility": d,
        "verdict": v,
        # protocol2 required reporting
        "margin_stats": {
            "n_motifs": len(rows),
            "max_score_drop_over_all_motifs":
                round(max(r["max_score_drop"] for r in rows), 6),
            "mean_score_drop": round(sum(r["max_score_drop"] for r in rows) / len(rows), 6),
            "motifs_with_any_movement": b[DEFAULT_CODE.name]["motifs_with_score_movement"],
            "note": "drops are arithmetic, not effect sizes -- reported so the "
                    "claim 'nothing changed' can be checked against 'nothing moved'",
        },
        "leave_one_out": {
            "unit": "motif",
            "verdicts_changed_excluding_each_motif":
                {r["motif"]: b[DEFAULT_CODE.name]["verdicts_changed"] - r["verdicts_changed"]
                 for r in rows},
            "note": "part B enumerates the whole published record rather than "
                    "sampling it, so leave-one-out shows dependence on any single "
                    "motif rather than estimating variance",
        },
        "abstention_rate": {
            "unconstrained_ties_in_top_group":
                sum(1 for r in rows if r["P_ties_X_free"]) / len(rows),
            "constrained_ties_in_top_group":
                sum(1 for r in rows if r["P_ties_X_constrained"]) / len(rows),
        },
    }

    out = Stage2Result("EXP-052", plan, payload).write()

    print(f"\nEXP-052  written to {out}")
    print(f"plan locked at {plan['_locked_at'][:8]}  sha {plan['_sha256']}\n")

    print("PART A -- does the unconstrained search actually choose to invert?")
    for label, r in a.items():
        print(f"  {label:<36}{r['inverting']:>4}/{r['pairs']:<5} pairs  "
              f"rate={r['rate']:.3f}")
    print()

    print("PART B -- published verdicts under the constraint (gamma code)")
    g = b[DEFAULT_CODE.name]
    print(f"  analogue > false friend   free {g['X_above_W_free']:>8}"
          f"     constrained {g['X_above_W_constrained']:>8}")
    print(f"  paraphrase ties analogue  free {g['P_ties_X_free']:>8}"
          f"     constrained {g['P_ties_X_constrained']:>8}")
    print(f"  rankings identical        {g['rankings_identical']}/{g['motifs']}")
    print(f"  verdicts changed          {g['verdicts_changed']}/{g['published_verdicts']}")
    print(f"  motifs where a score moved{g['motifs_with_score_movement']:>4}/{g['motifs']}")
    print(f"  all three codes agree     {v['codes_agree']}\n")

    print("PART C -- can a structure and its sign-flipped twin be told apart?")
    print(f"  {'m':>3}{'unconstrained':>16}{'constrained':>14}{'sym multiset':>14}")
    for m, r in c.items():
        print(f"  {m:>3}{r['degeneracy_rate_unconstrained']:>16.3f}"
              f"{r['degeneracy_rate_constrained']:>14.3f}"
              f"{r['symmetric_polarity_multiset_rate']:>14.3f}")
    print()

    print("PART D -- does the constraint keep cross-vocabulary correspondence?")
    print(f"  self                  {d['self_ratio']:.6f}")
    print(f"  faithful translation  {d['faithful_translation_ratio']:.6f}"
          f"   matched {d['faithful_matched']}  {d['faithful_type_map']}")
    print(f"  inverted translation  {d['inverted_translation_ratio']:.6f}"
          f"   matched {d['inverted_matched']}")
    print(f"  admissible: {d['constraint_admissible']}\n")

    print(f">>> {v['band']}")
    print(f"    {v['statement']}")


if __name__ == "__main__":
    main()
