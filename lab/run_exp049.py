"""EXP-049 -- impossibility screen across the Stage 3 candidate domains.

Run to the plan locked at 8e48f026.

For each (domain, question): construct two cases a practitioner would need
DIFFERENT answers for, encode both under the current representation, and test
isomorphism. Isomorphic + different answers = the question is not identifiable
and no measure on this representation can answer it.

ONE-DIRECTIONAL. A witness pair is a proof. Failing to construct one proves
nothing. Every "identifiable" below means only "not ruled out here".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from identifiability import audit                                 # noqa: E402
from protocol2 import require_locked_plan                         # noqa: E402
from structure import Relation, Structure                         # noqa: E402


def S(name, edges):
    """edges: (src, dst, type) or (src, dst, type, weight)"""
    rels = tuple(Relation(e[0], e[1], e[2], e[3] if len(e) > 3 else 1.0) for e in edges)
    nodes = tuple(sorted({n for r in rels for n in (r.src, r.dst)}))
    return Structure(name, nodes, rels)


def cases():
    """Every (domain, question, case A, case B, answers, channel) tested."""
    out = []

    # ---------------- causal / systems models ----------------
    # A regulating loop that oscillates vs one that settles. Identical signed
    # topology; the difference is delay around the loop.
    fast = S("settles", [("level", "signal", "POS"), ("signal", "correction", "POS"),
                         ("correction", "level", "NEG")])
    slow = S("oscillates", [("level", "signal", "POS"), ("signal", "correction", "POS"),
                            ("correction", "level", "NEG")])
    out.append(("causal / systems models",
                "will this feedback loop settle or oscillate?",
                fast, slow, "settles", "oscillates", "temporal order and delay"))

    # Weak vs strong coupling -- magnitude, which EXP-034 added
    weak = S("weak_loop", [("a", "b", "POS", 10.0), ("b", "a", "NEG", 0.01)])
    strong = S("strong_loop", [("a", "b", "POS", 0.01), ("b", "a", "NEG", 10.0)])
    out.append(("causal / systems models",
                "which link dominates this loop's behaviour?",
                weak, strong, "first link", "second link", "magnitude (added EXP-034)"))

    # Structural analogy between two systems -- the EXP-048 capability
    sysA = S("sys_a", [("x", "y", "POS"), ("y", "z", "POS"), ("z", "x", "NEG")])
    sysB = S("sys_b", [("x", "y", "POS"), ("y", "z", "NEG"), ("z", "x", "NEG")])
    out.append(("causal / systems models",
                "are these two systems structurally analogous?",
                sysA, sysB, "reinforcing-dominant", "balancing-dominant", "none needed"))

    # ---------------- biological pathways ----------------
    # Catalytic vs consumed: identical topology if the ontology does not type it
    cat_untyped = S("catalyst_untyped", [("e", "p", "POS"), ("s", "p", "POS")])
    con_untyped = S("consumed_untyped", [("e", "p", "POS"), ("s", "p", "POS")])
    out.append(("biological pathways",
                "is this participant catalytic or consumed? (ontology does NOT type it)",
                cat_untyped, con_untyped, "catalytic", "consumed",
                "relation typing the domain must declare"))

    cat_typed = S("catalyst_typed", [("e", "p", "CATALYSES"), ("s", "p", "CONSUMED_INTO")])
    con_typed = S("consumed_typed", [("e", "p", "CONSUMED_INTO"), ("s", "p", "CONSUMED_INTO")])
    out.append(("biological pathways",
                "is this participant catalytic or consumed? (ontology DOES type it)",
                cat_typed, con_typed, "catalytic", "consumed", "none needed"))

    # Real intermediate vs modelling convenience -- the EXP-029 wall
    real = S("real_intermediate", [("a", "m", "POS"), ("m", "b", "POS")])
    artefact = S("lumped_step", [("a", "m", "POS"), ("m", "b", "POS")])
    out.append(("biological pathways",
                "is this intermediate a real metabolite or a modelling convenience?",
                real, artefact, "real", "artefact", "ontological role declaration"))

    # ---------------- dependency / provenance graphs ----------------
    # Does a change propagate? Pure reachability.
    reach = S("reaches", [("a", "b", "DEPENDS"), ("b", "c", "DEPENDS")])
    noreach = S("does_not_reach", [("a", "b", "DEPENDS"), ("c", "b", "DEPENDS")])
    out.append(("dependency / provenance graphs",
                "will a change here propagate to there?",
                reach, noreach, "propagates", "does not", "none needed"))

    # Which identical-looking dependency actually caused the outage?
    culprit = S("culprit", [("lib", "svc", "DEPENDS"), ("svc", "outage", "POS")])
    bystander = S("bystander", [("lib", "svc", "DEPENDS"), ("svc", "outage", "POS")])
    out.append(("dependency / provenance graphs",
                "which of two identical dependencies actually caused the outage?",
                culprit, bystander, "culprit", "bystander", "provenance / evidence"))

    # ---------------- knowledge graphs ----------------
    # Meaningful analogy vs generic pattern -- EXP-027 exactly
    meaningful = S("specific_pattern", [("p", "q", "POS"), ("q", "r", "POS"), ("r", "p", "POS")])
    generic = S("generic_pattern", [("p", "q", "POS"), ("q", "r", "POS"), ("r", "p", "POS")])
    out.append(("knowledge graphs",
                "is this subgraph a meaningful analogy or a generic pattern that matches everything?",
                meaningful, generic, "meaningful", "generic", "specificity / referential content"))

    # Do these two entities play the same structural role?
    roleA = S("role_a", [("e", "x", "REL"), ("y", "e", "REL")])
    roleB = S("role_b", [("e", "x", "REL"), ("e", "y", "REL")])
    out.append(("knowledge graphs",
                "do these two entities play the same structural role?",
                roleA, roleB, "sink-ish", "source-ish", "none needed"))

    return out


def main() -> None:
    plan = require_locked_plan("EXP-049")
    rows = []
    for domain, question, a, b, ans_a, ans_b, channel in cases():
        r = audit(question, a, b, ans_a, ans_b, channel).as_dict()
        r["domain"] = domain
        rows.append(r)

    by_domain = {}
    for r in rows:
        d = by_domain.setdefault(r["domain"], {"identifiable": 0, "blocked": 0, "questions": []})
        (d["identifiable"] if r["identifiable_from_structure"] else d.__setitem__("blocked", d["blocked"] + 1)) \
            if r["identifiable_from_structure"] else None
        if r["identifiable_from_structure"]:
            d["identifiable"] += 1
        d["questions"].append({"question": r["distinction"],
                               "identifiable": r["identifiable_from_structure"],
                               "channel_required": r["required_channel"]})

    # SECOND FILTER, added while writing up: "not ruled out" is not "worth doing".
    # A question can survive the impossibility screen and still be a bad target
    # because it is trivial, is not a measurement problem at all, or has mature
    # incumbents that solve it better. Assessed per surviving question.
    INCUMBENT = {
        "which link dominates this loop's behaviour?":
            ("MATURE INCUMBENTS", "sensitivity and eigenvalue analysis in system "
             "dynamics answer this directly and are well established"),
        "are these two systems structurally analogous?":
            ("THE REAL CANDIDATE", "this is the capability EXP-048 established. "
             "Incumbents exist (graph edit distance, graph kernels) but an MDL "
             "framing is a genuine alternative rather than a reimplementation"),
        "is this participant catalytic or consumed? (ontology DOES type it)":
            ("TRIVIAL", "once the ontology types it, this is a lookup, not a "
             "measurement"),
        "will a change here propagate to there?":
            ("NOT A MEASUREMENT PROBLEM", "reachability. Breadth-first search "
             "solves it exactly and in linear time"),
        "do these two entities play the same structural role?":
            ("MATURE INCUMBENTS", "role and regular equivalence, blockmodelling in "
             "social network analysis. Decades of work"),
    }

    blocked = [r for r in rows if not r["identifiable_from_structure"]]
    for r in rows:
        if r["identifiable_from_structure"]:
            verdict2, why = INCUMBENT.get(r["distinction"], ("UNASSESSED", ""))
            r["second_filter"] = verdict2
            r["second_filter_note"] = why
    all_ident = len(blocked) == 0
    none_ident = len(blocked) == len(rows)
    if all_ident:
        verdict = ("SCREEN FAILED -- every question came back identifiable, which most "
                   "likely means my witness pairs are too weak rather than that every "
                   "domain is viable")
    elif none_ident:
        verdict = ("NO VIABLE DOMAIN ON THIS LIST -- every question tested is outside "
                   "the representation")
    else:
        verdict = (f"MAP PRODUCED -- {len(rows) - len(blocked)} of {len(rows)} questions "
                   f"are not ruled out; {len(blocked)} are provably outside the "
                   f"representation. Viability is per QUESTION, not per domain")

    survivors = [r for r in rows if r["identifiable_from_structure"]]
    real_candidates = [r for r in survivors if r.get("second_filter") == "THE REAL CANDIDATE"]

    report = {"experiment": "EXP-049",
              "second_filter": {
                  "why": ("'not ruled out' is not 'worth doing'. A surviving question can "
                          "still be trivial, not a measurement problem, or already solved "
                          "better by mature incumbents"),
                  "survivors_assessed": len(survivors),
                  "real_candidates": [r["distinction"] for r in real_candidates],
                  "conclusion": (f"of {len(survivors)} questions that survive the "
                                 f"impossibility screen, {len(real_candidates)} is a "
                                 f"genuine target. The rest are trivial, not measurement "
                                 f"problems, or have decades of incumbent work"),
              },
              "plan_locked_at": plan["_locked_at"], "plan_sha256": plan["_sha256"],
              "soundness": plan["soundness_is_one_directional"],
              "bias_declared": plan["the_bias_i_control_and_cannot_remove"],
              "questions_tested": len(rows), "blocked": len(blocked),
              "by_domain": by_domain, "rows": rows,
              "channels_that_block": sorted({r["required_channel"] for r in blocked}),
              "verdict": verdict}
    (Path(__file__).resolve().parents[1] / "results" / "exp049.json").write_text(
        json.dumps(report, indent=2))

    print(f"\nEXP-049   plan locked at {plan['_locked_at'][:8]}\n")
    cur = None
    for r in rows:
        if r["domain"] != cur:
            cur = r["domain"]
            print(f"\n{cur.upper()}")
        mark = "OK " if r["identifiable_from_structure"] else "OUT"
        q = r["distinction"][:70]
        print(f"   [{mark}] {q}")
        if not r["identifiable_from_structure"]:
            print(f"         needs: {r['required_channel']}")
    print(f"\n\nchannels doing the ruling-out:")
    for c in report["channels_that_block"]:
        print(f"   - {c}")
    print(f"\n\nSECOND FILTER -- of the {len(survivors)} that survived, is each worth doing?")
    for r in survivors:
        print(f"   [{r.get('second_filter','?'):<26}] {r['distinction'][:56]}")
        if r.get("second_filter_note"):
            print(f"      {r['second_filter_note'][:88]}")
    print(f"\n>>> {verdict}")
    print(f">>> AFTER THE SECOND FILTER: {report['second_filter']['conclusion']}")


if __name__ == "__main__":
    main()
