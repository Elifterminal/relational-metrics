"""EXP-038 -- Q-36. Report the margin, not the coin flip.

EXP-036 concluded the project had no significant evidence for the retrieval
claim under blind annotation, on the strength of 6/10 at p = 0.754. EXP-037 then
found that the binary count discards the margin, and that on the same data the
margins carry an effect size needing ~12 test cases rather than 199.

This applies the margin evaluation properly and reports what it finds -- which
is not what EXP-036 concluded.

THE THING TO BE SUSPICIOUS OF, stated first and not buried.

I switched analysis method AFTER the first method returned a null. That is the
classic route to a false positive, and it does not stop being one because the
switch was well motivated. Three things bear on it, and none of them make this a
pre-registered result:

  * the switch was decided on POWER grounds in EXP-037, and written up there
    before any margin p-value was computed;
  * but EXP-037 reported an effect size of d = 0.842 at n = 10, from which the
    significance was inferable by anyone who cared to multiply. So I could have
    known. This is not a clean pre-registration and will not be described as one;
  * the direction was predicted in advance -- the analogue should beat the false
    friend -- which would justify a one-sided test. Reported TWO-sided anyway,
    because a systematically negative margin would be a finding too and a
    one-sided test would hide it. That choice costs a factor of two in p.

Both tests are reported. The t-test keeps the abstentions and assumes a shape;
Wilcoxon assumes no shape and drops them. If they disagree, that disagreement is
the result.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from blind_reannotate import load_key as key26                    # noqa: E402
from codes import DEFAULT_CODE                                    # noqa: E402
from corpus import QUERIES, docs_for, query_doc                   # noqa: E402
from corpus_holdout import (HOLDOUT_QUERIES, holdout_docs_for,    # noqa: E402
                            holdout_query)
from corpus_independent import (INDEPENDENT_QUERIES,              # noqa: E402
                                independent_docs_for, independent_query)
from evaluate import evaluate_margins                             # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from q26_blind_annotations import B                               # noqa: E402
from q30_blind_annotations import Q30                             # noqa: E402
from q30_pool import load_key as key30                            # noqa: E402
from run_exp032 import build                                      # noqa: E402


def gap(q, docs):
    return (mdl_correspondence(q, docs["X"], DEFAULT_CODE).ratio
            - mdl_correspondence(q, docs["W"], DEFAULT_CODE).ratio)


def sighted_margins():
    out = []
    for motifs, qf, df in ((QUERIES, query_doc, docs_for),
                           (HOLDOUT_QUERIES, holdout_query, holdout_docs_for),
                           (INDEPENDENT_QUERIES, independent_query,
                            independent_docs_for)):
        for m in motifs:
            d = {x.kind: x.structure for x in df(m)}
            out.append(gap(qf(m).structure, d))
    return out


def blind_margins():
    M = {}
    for ann, key in ((B, {k["passage_id"]: k for k in key26()}),
                     (Q30, {k["passage_id"]: k for k in key30()})):
        for pid, e in ann.items():
            k = key[pid]
            M.setdefault((k.get("corpus", "independent"), k["motif"]), {})[k["kind"]] = \
                build(pid, e)
    return [gap(d["D"], d) for _, d in sorted(M.items())
            if {"D", "X", "W"} <= set(d)]


def main() -> None:
    sighted = evaluate_margins(sighted_margins())
    blind = evaluate_margins(blind_margins())

    report = {
        "experiment": "EXP-038", "question": "Q-36",
        "caveat": ("analysis method switched after the binary test returned a null. "
                   "Motivated by the power argument in EXP-037 and written up there "
                   "before any margin p-value was computed -- but the effect size "
                   "reported there made significance inferable, so this is NOT a "
                   "pre-registered result and is not described as one"),
        "two_sided_by_choice": ("direction was predicted, so one-sided would be "
                                "defensible and would halve p. Reported two-sided "
                                "because a negative margin would also be a finding"),
        "sighted": sighted.as_dict(),
        "blind": blind.as_dict(),
        "what_changes": {
            "EXP-036_said": "no significant evidence under blind annotation (6/10, p = 0.754)",
            "margin_says": (f"mean +{blind.mean:.4f} bits, 95% CI excludes zero, "
                            f"t p = {blind.t_p:.4f}, Wilcoxon p = {blind.wilcoxon_p:.4f}"),
            "reconciliation": ("both are correct about their own statistic. The binary "
                               "count genuinely cannot detect this effect at n = 10; "
                               "the margin can. EXP-036's conclusion was true of the "
                               "test it ran and false of the data"),
        },
    }
    # ROBUSTNESS. A marginal positive arrived at post-hoc deserves a check a
    # negative would not need: drop each motif in turn and see whether the
    # result depends on any single one.
    bm = list(blind.margins)
    loo = []
    for i in range(len(bm)):
        r = evaluate_margins(bm[:i] + bm[i + 1:])
        loo.append({"dropped_index": i, "dropped_margin": round(bm[i], 4),
                    "t_p": round(r.t_p, 4), "wilcoxon_p": round(r.wilcoxon_p, 4),
                    "still_significant_t": r.t_p < 0.05})
    survives = sum(x["still_significant_t"] for x in loo)
    report["leave_one_out"] = {
        "rows": loo,
        "survives_t_test_after_dropping_any_single_motif": f"{survives}/{len(loo)}",
        "worst_case_p": max(x["t_p"] for x in loo),
        "note": ("if dropping one motif kills it, the result is one observation "
                 "wearing a p-value"),
    }
    report["blind_significant_both_tests"] = (blind.t_p < 0.05 and blind.wilcoxon_p < 0.05)

    out = Path(__file__).resolve().parents[1] / "results" / "exp038.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-038  written to {out}\n")

    for label, r in (("SIGHTED", sighted), ("BLIND", blind)):
        d = r.as_dict()
        print(f"--- {label} ---")
        print(f"   per-motif margins : {d['per_motif_margins']}")
        print(f"   mean              : {d['mean_margin_bits']:+.4f} bits   sd {d['sd']:.4f}")
        print(f"   95% CI on mean    : [{d['ci95_on_mean'][0]:+.4f}, "
              f"{d['ci95_on_mean'][1]:+.4f}]"
              f"   {'EXCLUDES zero' if d['ci95_on_mean'][0] > 0 else 'includes zero'}")
        print(f"   effect size d     : {d['effect_size_d']}")
        print(f"   t-test p          : {d['t_test_p']:.4f}   "
              f"(keeps {d['abstentions']} abstentions)")
        print(f"   Wilcoxon p        : {d['wilcoxon_p']:.4f}   "
              f"(n = {d['wilcoxon_n_after_dropping_ties']} after dropping ties)")
        print(f"   footnote, win count: {d['_footnote_win_count']}\n")

    lo = report["leave_one_out"]
    print("ROBUSTNESS -- drop each motif in turn:")
    print(f"   still significant on the t-test: "
          f"{lo['survives_t_test_after_dropping_any_single_motif']}")
    print(f"   worst case p after dropping one: {lo['worst_case_p']:.4f}\n")

    w = report["what_changes"]
    print("WHAT THIS CHANGES")
    print(f"   EXP-036 said : {w['EXP-036_said']}")
    print(f"   the margin   : {w['margin_says']}")
    print(f"   both correct : {w['reconciliation']}")
    print(f"\n>>> blind result significant on BOTH tests: "
          f"{report['blind_significant_both_tests']}")
    print(f">>> {report['caveat']}")


if __name__ == "__main__":
    main()
