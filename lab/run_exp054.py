"""EXP-054 -- Q-44. Does the polarity constraint earn adoption, from rung 1?

EXP-053 found the constraint changes 42 verdict-bearing results across the whole
record, nearly all in this project's favour, including un-retracting a
retraction. The predeclared band refused adoption on that evidence and sent it
back to rung 1 with nothing inherited. This is that validation.

THE TRAP. Every design choice here is one I would be tempted to make in the
constraint's favour, because the constraint makes my results better. So the
centrepiece is PART C, built so the constraint can fail it, and part C has veto
power over everything else:

    If an ARBITRARY restriction of equal severity reproduces the same
    improvement, then the gain comes from restricting the search AT ALL rather
    than from restricting it CORRECTLY -- and the 42 changes are an artifact of
    search restriction, not a discovery about polarity.

That is the question. Parts A, B and D are worth running, and none of them
matters if C goes the wrong way.

Plan locked at external/plans/EXP-054.json before this file ran.
"""

from __future__ import annotations

import ast
import json
import random
import re
import statistics
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import CODES, DEFAULT_CODE, matching_is_profitable      # noqa: E402
from corpus import QUERIES, docs_for, query_doc                    # noqa: E402
from corpus_holdout import HOLDOUT_QUERIES, holdout_docs_for, holdout_query  # noqa: E402
from corpus_independent import (INDEPENDENT_QUERIES,               # noqa: E402
                                independent_docs_for, independent_query)
from evaluate import evaluate_margins                              # noqa: E402
from measures import mdl_correspondence                            # noqa: E402
from protocol2 import (ProtocolViolation, Stage2Result,            # noqa: E402
                       check_capacity_to_fail, require_locked_plan)
from ranking import rank_with_ties, strictly_above                 # noqa: E402
from relalgebra import FAMILY_OF, POLARITY                         # noqa: E402
from run_exp052 import polarity_preserving                         # noqa: E402
from structure import Relation, Structure                          # noqa: E402

ADMISSIBLE = tuple(c for c in CODES if matching_is_profitable(c))

CORPORA = (
    ("dev", QUERIES, query_doc, docs_for),
    ("holdout", HOLDOUT_QUERIES, holdout_query, holdout_docs_for),
    ("independent", INDEPENDENT_QUERIES, independent_query, independent_docs_for),
)


# ===========================================================================
# PART A -- impostors, including one built to be flattered by this constraint
# ===========================================================================

def m_constrained(q, d, code=DEFAULT_CODE):
    return mdl_correspondence(q, d, code, type_filter=polarity_preserving).ratio


def m_free(q, d, code=DEFAULT_CODE):
    return mdl_correspondence(q, d, code).ratio


def m_polarity_overlap(q, d, code=None):
    """THE IMPOSTOR THAT MATTERS. Ranks purely by how similar the two polarity
    profiles are, ignoring structure completely.

    If this does as well as the constrained measure, the constraint has turned
    a structural measure into a polarity counter, and the 42 improvements are
    bookkeeping rather than correspondence.
    """
    def prof(s):
        pols = [POLARITY.get(r.rtype, 0) for r in s.relations]
        n = len(pols) or 1
        return sum(1 for p in pols if p > 0) / n
    return 1.0 - abs(prof(q) - prof(d))


def m_wordmatch(q, d, code=None):
    a, b = set(q.nodes), set(d.nodes)
    return len(a & b) / len(a | b) if a | b else 0.0


def m_size(q, d, code=None):
    return 1.0 - abs(q.m - d.m) / max(q.m, d.m, 1)


PART_A_METHODS = {
    "F-06a constrained": m_constrained,
    "F-06a unconstrained": m_free,
    "polarity overlap (impostor)": m_polarity_overlap,
    "word overlap (impostor)": m_wordmatch,
    "size match (impostor)": m_size,
}
IMPOSTORS = {k for k in PART_A_METHODS if "impostor" in k}


def part_a(code=DEFAULT_CODE):
    out = {}
    for name, fn in PART_A_METHODS.items():
        wins, total, margins, constant = 0, 0, [], 0
        for _, motifs, q_fn, d_fn in CORPORA:
            for mo in motifs:
                q = q_fn(mo).structure
                docs = {d.kind: d.structure for d in d_fn(mo)}
                scores = {k: fn(q, s, code) for k, s in docs.items()}
                if len(set(round(v, 12) for v in scores.values())) == 1:
                    constant += 1
                g = rank_with_ties(scores)
                wins += strictly_above(g, "X", "W")
                total += 1
                margins.append(scores.get("X", 0.0) - scores.get("W", 0.0))
        out[name] = {
            "analogue_above_false_friend": f"{wins}/{total}",
            "wins": wins, "n": total,
            "mean_margin": round(statistics.fmean(margins), 6),
            "motifs_scored_flat": constant,
            "is_impostor": name in IMPOSTORS,
        }
    return out


# ===========================================================================
# PART B -- the re-encoding question as a FRESH claim, new seeds
# ===========================================================================

def _rand_struct(rng, m=6, n=6, fam=("POS", "NEG")):
    nodes = tuple(f"v{i}" for i in range(n))
    seen, rels = set(), []
    while len(rels) < m:
        s, d = rng.sample(nodes, 2)
        if (s, d) in seen:
            continue
        seen.add((s, d))
        rels.append(Relation(s, d, rng.choice(fam)))
    return Structure("base", nodes, tuple(rels))


def _mediate(s, rng):
    """Equivalence-preserving: insert a mediator on one edge, polarity-correct."""
    i = rng.randrange(s.m)
    r = s.relations[i]
    mid = "mid0"
    fam = FAMILY_OF.get(r.rtype)
    second = fam[0] if fam else r.rtype          # amplifying, so composition holds
    rels = list(s.relations)
    rels[i:i + 1] = [Relation(r.src, mid, r.rtype), Relation(mid, r.dst, second)]
    return Structure(s.name + "+med", s.nodes + (mid,), tuple(rels), s.domain)


def _relabel(s, rng):
    """Equivalence-preserving: rename participants."""
    mapping = {n: f"z{i}" for i, n in enumerate(s.nodes)}
    return Structure(s.name + "+rel", tuple(mapping[n] for n in s.nodes),
                     tuple(r.relabel(mapping) for r in s.relations), s.domain)


def _flip_one(s, rng):
    """CONTENT CHANGE: invert one relation's sign."""
    i = rng.randrange(s.m)
    r = s.relations[i]
    fam = FAMILY_OF.get(r.rtype)
    new = (fam[1] if r.rtype == fam[0] else fam[0]) if fam else r.rtype
    rels = list(s.relations)
    rels[i] = Relation(r.src, r.dst, new)
    return Structure(s.name + "+flip", s.nodes, tuple(rels), s.domain)


def _rewire_one(s, rng):
    """CONTENT CHANGE: move one relation's endpoint."""
    i = rng.randrange(s.m)
    r = s.relations[i]
    cands = [n for n in s.nodes if n not in (r.src, r.dst)]
    rels = list(s.relations)
    rels[i] = Relation(r.src, rng.choice(cands), r.rtype)
    return Structure(s.name + "+rew", s.nodes, tuple(rels), s.domain)


PRESERVING = {"mediate": _mediate, "relabel": _relabel}
CHANGING = {"flip_sign": _flip_one, "rewire": _rewire_one}

# Seeds never used by EXP-028 or any prior experiment (project rule 4).
PART_B_SEED_BASE = 540_000


def part_b(n_cases=60, code=DEFAULT_CODE, tf=polarity_preserving):
    """Does an equivalence-preserving re-encoding cost LESS than a content change?

    Reported as MARGINS with an effect size, never as a binary count (P-25). A
    retraction reversed by a measure change needs more evidence than the
    retraction did, so agreeing with the old boolean is not sufficient.
    """
    rows, paired = [], []
    for i in range(n_cases):
        rng = random.Random(PART_B_SEED_BASE + i)
        base = _rand_struct(rng)
        pres = {k: mdl_correspondence(base, f(base, random.Random(PART_B_SEED_BASE + i + 7)),
                                      code, type_filter=tf).ratio
                for k, f in PRESERVING.items()}
        chg = {k: mdl_correspondence(base, f(base, random.Random(PART_B_SEED_BASE + i + 13)),
                                     code, type_filter=tf).ratio
               for k, f in CHANGING.items()}
        # cost = how much correspondence is LOST. Preserving should lose less.
        worst_pres = min(pres.values())
        best_chg = max(chg.values())
        paired.append(worst_pres - best_chg)
        rows.append({"case": i, "preserving": {k: round(v, 5) for k, v in pres.items()},
                     "changing": {k: round(v, 5) for k, v in chg.items()},
                     "margin": round(worst_pres - best_chg, 5)})
    res = evaluate_margins(paired)
    return {
        "n": len(paired),
        "mean_margin": round(res.mean, 5),
        "sd": round(res.sd, 5),
        "effect_size_d": round(res.effect_size_d, 4),
        "ci95": [round(x, 5) for x in res.ci95],
        "t_p": round(res.t_p, 6),
        "wilcoxon_p": round(res.wilcoxon_p, 6),
        "ci_excludes_zero": res.ci95[0] > 0 or res.ci95[1] < 0,
        "passes": (res.ci95[0] > 0 and res.t_p < 0.05 and res.wilcoxon_p < 0.05),
        "sample_rows": rows[:6],
    }


# ===========================================================================
# PART C -- THE DECIDING CONTROL
# ===========================================================================

def _allowed_pairs(t1, t2, pred):
    return {(a, b) for a in t1 for b in t2 if pred(a, b)}


def make_random_filter(t1, t2, k, rng, tries=50):
    """A filter permitting exactly k of the |t1|x|t2| substitutions, at random.

    Resampled until it admits at least one COMPLETE type map, so the arms are
    comparable; the resampling rate is reported because it biases the control
    toward restrictions that function.
    """
    allp = [(a, b) for a in t1 for b in t2]
    k = max(1, min(k, len(allp)))
    for attempt in range(tries):
        chosen = set(rng.sample(allp, k))
        if all(any((a, b) in chosen for b in t2) for a in t1):
            return (lambda s, d: (s, d) in chosen), attempt
    return (lambda s, d: (s, d) in chosen), tries


def exp039_margins(tf, code=DEFAULT_CODE):
    """EXP-039's nine margins under an arbitrary type filter."""
    from blind_reannotate import load_key as key26
    from q30_pool import load_key as key30
    from run_exp032 import build
    ROOT = Path(__file__).resolve().parents[1]
    Q31 = ROOT / "external" / "q31"

    ann = {}
    for f in ("received_part1.txt", "received_part2.txt"):
        for line in (Q31 / f).read_text().splitlines():
            m = re.match(r"(S\d{3}):\s*(\[.*?\])", line)
            if m:
                ann[m.group(1)] = ast.literal_eval(m.group(2))
    idmap = json.loads((ROOT / "external" / "q31_idmap.json").read_text())
    key = {k["passage_id"]: k for k in key26()}
    key.update({k["passage_id"]: k for k in key30()})

    motifs = {}
    for tag, edges in ann.items():
        pid = idmap[tag]
        k = key[pid]
        motifs.setdefault((k.get("corpus", "independent"), k["motif"]), {})[k["kind"]] = \
            build(pid, edges)
    kept = {t: d for t, d in sorted(motifs.items())
            if all(r in d and d[r].m > 0 for r in ("D", "X", "W"))}
    return [mdl_correspondence(d["D"], d["X"], code, type_filter=tf).ratio
            - mdl_correspondence(d["D"], d["W"], code, type_filter=tf).ratio
            for _, d in sorted(kept.items())]


def loo_score(margins):
    """EXP-039's own robustness statistic: leave-one-out survival count."""
    out = 0
    for i in range(len(margins)):
        r = evaluate_margins(margins[:i] + margins[i + 1:])
        out += r.t_p < 0.05
    return out


def part_c(n_random=200, rerun_at=2000):
    """Is the polarity constraint better than an ARBITRARY restriction of equal severity?"""
    free_m = exp039_margins(None)
    cons_m = exp039_margins(polarity_preserving)
    free_loo, cons_loo = loo_score(free_m), loo_score(cons_m)

    # Severity: what fraction of substitutions does polarity-preserving permit?
    types = sorted({t for t in POLARITY})
    permitted = len(_allowed_pairs(types, types, polarity_preserving))
    severity = permitted / (len(types) ** 2)

    def run(n, exact_k):
        """exact_k=True matches the locked plan literally: exactly `permitted` of
        the |T|x|T| substitutions, chosen at random. exact_k=False draws each
        pair independently at rate `severity`, which matches the plan in
        EXPECTATION only.

        Both are reported. The first implementation was the Bernoulli one, which
        is a deviation from what was locked -- declared here rather than
        quietly corrected, and checked to see whether it changes the verdict.
        """
        scores, degenerate = [], 0
        allp = [(a, b) for a in types for b in types]
        for i in range(n):
            rng = random.Random(770_000 + i)
            if exact_k:
                chosen = set(rng.sample(allp, permitted))
                if not all(any((a, b) in chosen for b in types) for a in types):
                    degenerate += 1
                tf = (lambda s, d, _c=chosen: (s, d) in _c
                      if s in types and d in types else True)
            else:
                cache = {}

                def tf(s, d, _rng=rng, _cache=cache):
                    if (s, d) not in _cache:
                        _cache[(s, d)] = _rng.random() < severity
                    return _cache[(s, d)]
            try:
                scores.append(loo_score(exp039_margins(tf)))
            except Exception:
                degenerate += 1
        return scores, degenerate

    def arm(exact_k, n):
        sc, deg = run(n, exact_k)
        n_used = n
        above = sum(1 for s in sc if s >= cons_loo)
        pct = 1.0 - above / len(sc) if sc else 0.0
        if 0.90 <= pct < 0.99:
            sc, deg = run(rerun_at, exact_k)
            n_used = rerun_at
            above = sum(1 for s in sc if s >= cons_loo)
            pct = 1.0 - above / len(sc) if sc else 0.0
        return {"n": n_used, "median": statistics.median(sc) if sc else 0,
                "max": max(sc) if sc else 0, "at_or_above": above,
                "percentile": round(pct, 4), "degenerate": deg,
                "degenerate_rate": round(deg / max(n_used, 1), 4),
                "passes": pct >= 0.95, "below_median": cons_loo < (statistics.median(sc) if sc else 0)}

    exact = arm(True, n_random)
    bern = arm(False, n_random)
    # The locked plan says EXACTLY k, so that arm decides. The Bernoulli arm is
    # reported alongside so the deviation is visible and its effect measurable.
    scores_pct = exact["percentile"]
    resampled = exact["degenerate"]
    n_used = exact["n"]
    at_or_above = exact["at_or_above"]
    pct = scores_pct
    med = exact["median"]

    return {
        "arms": {"exact_k_matches_locked_plan": exact,
                 "bernoulli_expected_k_first_implementation": bern},
        "arms_agree_on_verdict": exact["passes"] == bern["passes"],
        "deviation_declared": ("the first implementation drew each substitution "
                               "independently at rate `severity`, matching the locked "
                               "plan in expectation only. The exact-k arm is the one the "
                               "plan specified and is the one that decides."),
        "unconstrained_leave_one_out": f"{free_loo}/{len(free_m)}",
        "polarity_constrained_leave_one_out": f"{cons_loo}/{len(cons_m)}",
        "severity_fraction_permitted": round(severity, 4),
        "n_random_restrictions": n_used,
        "random_leave_one_out_median": med,
        "random_leave_one_out_max": exact["max"],
        "random_at_or_above_constrained": at_or_above,
        "percentile_of_polarity_constraint": round(pct, 4),
        "resampled_or_failed": resampled,
        "resample_rate": round(resampled / max(n_used, 1), 4),
        "passes": pct >= 0.95,
        "polarity_below_random_median": cons_loo < med,
    }


# ===========================================================================
# PART D
# ===========================================================================

def part_d(n_perm=10_000):
    m = exp039_margins(polarity_preserving)
    obs = statistics.fmean(m)
    rng = random.Random(54_054)
    hits = 0
    for _ in range(n_perm):
        flipped = [x if rng.random() < 0.5 else -x for x in m]
        if statistics.fmean(flipped) >= obs:
            hits += 1
    p = (hits + 1) / (n_perm + 1)
    return {
        "n_motifs": len(m),
        "observed_mean_margin": round(obs, 5),
        "permutation_p": round(p, 5),
        "n_permutations": n_perm,
        "passes": p < 0.05,
        "what_this_cannot_establish":
            "Re-uses the same nine observations EXP-039 used. A sign-permutation "
            "test says the observed mean is unlikely under a symmetric null; it "
            "says nothing about whether a DIFFERENT independent annotator would "
            "reproduce it. That needs new material and is not available here.",
    }


# ===========================================================================

def main() -> None:
    plan = require_locked_plan("EXP-054")

    # capacity to fail: the impostor must produce non-constant rankings, or
    # passing part A would be vacuous (EXP-000a's error, and EXP-024 already
    # caught a size-matcher scoring 3/3 on equal-sized documents).
    def impostor_discriminates():
        flat = 0
        for _, motifs, q_fn, d_fn in CORPORA:
            for mo in motifs:
                q = q_fn(mo).structure
                sc = {d.kind: m_polarity_overlap(q, d.structure) for d in d_fn(mo)}
                flat += len(set(round(v, 12) for v in sc.values())) == 1
        return flat < len(QUERIES) + len(HOLDOUT_QUERIES) + len(INDEPENDENT_QUERIES)
    check_capacity_to_fail("polarity-overlap impostor discriminates",
                           impostor_discriminates)

    print("EXP-054 -- rung-1 validation of the polarity constraint\n")
    a = {c.name: part_a(c) for c in ADMISSIBLE}
    print("PART A -- impostors")
    for name, r in a[DEFAULT_CODE.name].items():
        tag = "  <-- impostor" if r["is_impostor"] else ""
        print(f"  {name:<30}{r['analogue_above_false_friend']:>7}   "
              f"mean margin {r['mean_margin']:+.5f}   flat on {r['motifs_scored_flat']}{tag}")

    b = {c.name: part_b(code=c) for c in ADMISSIBLE}
    bb = b[DEFAULT_CODE.name]
    print(f"\nPART B -- re-encoding as a fresh claim ({bb['n']} new cases, unused seeds)")
    print(f"  mean margin {bb['mean_margin']:+.5f}   d={bb['effect_size_d']:.3f}   "
          f"CI95 {bb['ci95']}   t={bb['t_p']:.4g}  W={bb['wilcoxon_p']:.4g}")
    print(f"  passes: {bb['passes']}")

    print("\nPART C -- the deciding control: severity-matched random restrictions")
    c = part_c()
    print(f"  unconstrained leave-one-out   {c['unconstrained_leave_one_out']}")
    print(f"  polarity-constrained          {c['polarity_constrained_leave_one_out']}")
    print(f"  random restrictions, median   {c['random_leave_one_out_median']}"
          f"   max {c['random_leave_one_out_max']}")
    print(f"  polarity at percentile        {c['percentile_of_polarity_constraint']:.3f}"
          f"   ({c['random_at_or_above_constrained']} of "
          f"{c['n_random_restrictions']} random matched or beat it)")
    print(f"  passes: {c['passes']}")

    d = part_d()
    print(f"\nPART D -- permutation, p={d['permutation_p']:.4g}   passes: {d['passes']}")

    # ---- verdict, per the locked bands ------------------------------------
    passes = {"A": (a[DEFAULT_CODE.name]["F-06a constrained"]["wins"]
                    > max(r["wins"] for k, r in a[DEFAULT_CODE.name].items()
                          if r["is_impostor"])),
              "B": bb["passes"], "C": c["passes"], "D": d["passes"]}
    n_pass = sum(passes.values())

    if not passes["C"]:
        if c["polarity_below_random_median"]:
            band = ("ADOPTION REFUSED -- and worse: the polarity constraint performs "
                    "BELOW the median arbitrary restriction")
            statement = ("Predeclared prediction_space_wrong (i). The EXP-053 "
                         "improvements came from restriction severity, and the polarity "
                         "structure was actively unhelpful. A stronger negative than "
                         "mere non-adoption.")
        else:
            band = "ADOPTION REFUSED -- part C veto"
            statement = ("An arbitrary restriction of equal severity reproduces the "
                         "improvement, so the gain is from restricting the search at all, "
                         "not from restricting it correctly. The polarity degeneracy is "
                         "still a real defect; this is not the demonstrated fix, and "
                         "EXP-053's 42 changes are an artifact of search restriction.")
    elif n_pass == 4:
        band = "ADOPT"
        statement = ("Validated at rung 1 on its own evidence. The default flips and the "
                     "affected experiments are re-run and republished as changes.")
    elif n_pass == 3:
        band = "ADOPT NARROWLY"
        statement = (f"Passes C plus two others; {[k for k,v in passes.items() if not v]} "
                     f"becomes a declared scope limit named explicitly on every claim "
                     f"that depends on it.")
    else:
        band = "DO NOT ADOPT YET"
        statement = ("Survives its hardest control but has not earned the rest. Default "
                     "stays unconstrained, defect stays documented, and the failing parts "
                     "define the next experiment.")

    payload = {
        "question": "Q-44",
        "parts_passed": passes,
        "n_passed": n_pass,
        "part_a_impostors": a,
        "part_b_reencoding_fresh": b,
        "part_c_severity_matched_random": c,
        "part_d_permutation": d,
        "codes_used": [c_.name for c_ in ADMISSIBLE],
        "verdict": {"band": band, "statement": statement},
        "margin_stats": {
            "part_b_mean_margin": bb["mean_margin"],
            "part_b_effect_size": bb["effect_size_d"],
            "part_b_ci95": bb["ci95"],
            "part_a_mean_margins": {k: v["mean_margin"]
                                    for k, v in a[DEFAULT_CODE.name].items()},
        },
        "leave_one_out": {
            "unit": "EXP-039 motif",
            "unconstrained": c["unconstrained_leave_one_out"],
            "constrained": c["polarity_constrained_leave_one_out"],
            "random_restriction_median": c["random_leave_one_out_median"],
            "note": "the random-restriction median is the number that decides this, "
                    "not the constrained score on its own",
        },
        "abstention_rate": {
            "part_a_motifs_scored_flat":
                {k: v["motifs_scored_flat"] for k, v in a[DEFAULT_CODE.name].items()},
            "part_c_resample_rate": c["resample_rate"],
        },
    }
    out = Stage2Result("EXP-054", plan, payload).write()
    print(f"\nwritten to {out}")
    print(f"\n>>> {band}\n    {statement}")


if __name__ == "__main__":
    main()
