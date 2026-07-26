"""EXP-031 -- the expressivity boundary audit, run BEFORE building anything.

Twice this project discovered, by failing, that a distinction it wanted was not
present in its representation. Both times the discovery cost an experiment. The
condition is a one-line factorisation test, so it can be run in advance:

    f is recoverable from structure  <=>  f is constant on isomorphism classes

A WITNESS PAIR -- isomorphic structures, different required answers -- proves no
measure on that representation can work. This experiment does two things:

  PART 1  certifies the two known failures with explicit witness pairs, so they
          are recorded as proofs rather than as observations
  PART 2  runs the same audit on distinctions the project has NOT yet tried to
          measure, to find the dead ends before building measures for them

Part 2 is the point. If the audit is any use it must predict a failure nobody
has paid for yet.

NOTE ON WHAT A PASS MEANS. Failing to find a witness pair is not a proof of
identifiability -- it is one failed refutation. The audit is sound in one
direction only, and the output says so rather than implying more.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from corpus_independent import (INDEPENDENT_QUERIES,              # noqa: E402
                                independent_docs_for)
from identifiability import audit, isomorphic                     # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from reprworlds import mediate_one                                # noqa: E402
from structure import Relation, Structure                         # noqa: E402


def s(name, edges, weights=None):
    ws = weights or [1.0] * len(edges)
    rels = tuple(Relation(a, b, t, w) for (a, b, t), w in zip(edges, ws))
    nodes = tuple(sorted({n for r in rels for n in (r.src, r.dst)}))
    return Structure(name, nodes, rels)


def main() -> None:
    audits = []

    # ---- PART 1: certify the two failures already paid for -----------------

    # EXP-027: a vacuous document isomorphic to the query vs the real analogue
    docs = {d.kind: d.structure for d in independent_docs_for(
        list(INDEPENDENT_QUERIES)[1])}
    audits.append(audit(
        "genuine analogue vs vacuous restatement",
        docs["X"], docs["V"], "analogue", "vacuous",
        "specificity / referential content",
        "certifies EXP-027. Real documents from the independent corpus, not "
        "constructed for this test").as_dict())

    # EXP-029: a real participant vs an inserted mediator
    base = s("cycle_real", [("a", "b", "POS"), ("b", "c", "POS"),
                            ("c", "a", "POS")])
    med = mediate_one(s("cycle_pre", [("a", "c", "POS"), ("c", "a", "POS")]), 0)
    audits.append(audit(
        "real participant vs inserted mediator",
        base, Structure("cycle_mediated", med.nodes, med.relations),
        "participant", "artifact",
        "ontological role declaration",
        "certifies EXP-029. A 3-cycle of real participants against a 2-cycle "
        "with a mediator spliced in -- identical typed topology, opposite "
        "modelling status").as_dict())

    # ---- PART 2: distinctions nobody has built a measure for yet ----------

    # relation STRENGTH. Structure carries `weight`, but edge_set() -- which is
    # what the measure compares -- drops it.
    weak = s("weak_link", [("a", "b", "POS"), ("b", "c", "POS")], [0.01, 0.01])
    strong = s("strong_link", [("a", "b", "POS"), ("b", "c", "POS")], [10.0, 10.0])
    audits.append(audit(
        "strong coupling vs negligible coupling",
        weak, strong, "strong", "negligible",
        "magnitude channel (weights must enter the comparison)",
        "weight IS carried on Relation but edge_set() returns only "
        "(src, dst, type), so the measure never sees it").as_dict())

    # TEMPORAL ORDER. The signature has no time.
    early = s("a_then_b", [("cause", "effect", "POS"), ("effect", "state", "POS")])
    late = s("b_then_a", [("cause", "effect", "POS"), ("effect", "state", "POS")])
    audits.append(audit(
        "reinforcing vs regulating by DELAY, same static graph",
        early, late, "reinforcing", "regulating",
        "temporal channel (order and delay)",
        "the two are the same object in this signature -- there is nowhere to "
        "record which happened first, so a delay-driven difference in behaviour "
        "is invisible by construction").as_dict())

    # PROVENANCE. Not in the signature at all.
    claimed = s("asserted", [("x", "y", "POS")])
    observed = s("observed", [("x", "y", "POS")])
    audits.append(audit(
        "asserted claim vs empirically observed relation",
        claimed, observed, "asserted", "observed",
        "provenance / evidence channel",
        "identical structures; the difference is where the relation came "
        "from, which the signature does not carry").as_dict())

    # A CONTROL: a distinction that SHOULD be identifiable, so the audit is
    # capable of returning both answers. Without this the test cannot fail.
    pos = s("amplifying", [("a", "b", "POS"), ("b", "a", "POS")])
    neg = s("damping", [("a", "b", "POS"), ("b", "a", "NEG")])
    audits.append(audit(
        "reinforcing vs balancing loop (CONTROL -- should be identifiable)",
        pos, neg, "reinforcing", "balancing",
        "none needed",
        "control. Relation polarity IS in the signature, so the structures "
        "differ and no witness pair can exist. If this came back "
        "non-identifiable the audit would be broken").as_dict())

    # ---- does the measure actually confirm the weight blindness? ----------
    w_ratio = mdl_correspondence(weak, strong, DEFAULT_CODE).ratio
    w_self = mdl_correspondence(weak, weak, DEFAULT_CODE).ratio

    not_ident = [a for a in audits if not a["identifiable_from_structure"]]
    report = {
        "experiment": "EXP-031",
        "principle": "representation-relative non-identifiability",
        "test": "f recoverable from structure <=> f constant on isomorphism classes",
        "soundness": ("one-directional: a witness pair PROVES non-identifiability; "
                      "failing to find one proves nothing"),
        "audits": audits,
        "n_audited": len(audits),
        "n_not_identifiable": len(not_ident),
        "weight_blindness_check": {
            "corr(weak, strong)": round(w_ratio, 6),
            "corr(weak, weak)": round(w_self, 6),
            "identical": abs(w_ratio - w_self) < 1e-12,
            "note": ("weights differ by 1000x and the measure returns the "
                     "self-correspondence value -- confirms the audit"),
        },
        "channels_required": sorted({a["required_channel"] for a in not_ident}),
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp031.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-031  written to {out}\n")

    print(f"{'distinction':<52}{'iso?':>6}{'verdict':>18}")
    print("-" * 76)
    for a in audits:
        v = "identifiable" if a["identifiable_from_structure"] else "NOT IDENTIFIABLE"
        print(f"{a['distinction'][:51]:<52}{str(a['structures_equivalent']):>6}{v:>18}")

    print(f"\n{report['n_not_identifiable']} of {report['n_audited']} distinctions are "
          f"provably outside the current representation.\n")
    print("CHANNELS THE REPRESENTATION WOULD HAVE TO ADD:")
    for c in report["channels_required"]:
        print(f"   - {c}")

    wc = report["weight_blindness_check"]
    print(f"\nCONFIRMATION on the new finding -- relation strength:")
    print(f"   corr(weak, strong) = {wc['corr(weak, strong)']:.6f}")
    print(f"   corr(weak, weak)   = {wc['corr(weak, weak)']:.6f}")
    print(f"   identical: {wc['identical']}  -- a 1000x difference in coupling is invisible")


if __name__ == "__main__":
    main()
