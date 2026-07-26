"""EXP-039 -- Q-31/Q-37. The second annotator.

Every retrieval result in this project has rested on annotation by an interested
party. This is the first not to. A second system was given a format
specification, told nothing about what the annotations were for, and handed 60
sentences shuffled across all three corpora with roles, motifs and corpus origin
stripped.

RUN STRICTLY TO THE PLAN COMMITTED AT 6a9aa8e, external/q31/ANALYSIS_PLAN.md,
before any number was computed. Nothing below was chosen after seeing a result.
The plan is honest that this is not pre-registration on unseen data -- the raw
annotations had been read, though no key had been looked up and no statistic
run.
"""

from __future__ import annotations

import ast
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from blind_reannotate import load_key as key26                    # noqa: E402
from codes import DEFAULT_CODE                                    # noqa: E402
from evaluate import evaluate_margins                             # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from q30_pool import load_key as key30                            # noqa: E402
from run_exp032 import build                                      # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
Q31 = ROOT / "external" / "q31"


def parse():
    out = {}
    for f in ("received_part1.txt", "received_part2.txt"):
        for line in (Q31 / f).read_text().splitlines():
            m = re.match(r"(S\d{3}):\s*(\[.*?\])", line)
            if m:
                out[m.group(1)] = ast.literal_eval(m.group(2))
    return out


def main() -> None:
    ann = parse()
    idmap = json.loads((ROOT / "external" / "q31_idmap.json").read_text())
    key = {k["passage_id"]: k for k in key26()}
    key.update({k["passage_id"]: k for k in key30()})

    motifs, rel_counts = {}, []
    for tag, edges in ann.items():
        pid = idmap[tag]
        k = key[pid]
        motifs.setdefault((k.get("corpus", "independent"), k["motif"]), {})[k["kind"]] = \
            build(pid, edges)
        rel_counts.append(len(edges))

    # exclusion rule, declared in the plan before any of this was computed
    kept, excluded = {}, []
    for tag, docs in sorted(motifs.items()):
        missing = [r for r in ("D", "X", "W") if r not in docs or docs[r].m == 0]
        if missing:
            excluded.append({"motif": f"{tag[0]}/{tag[1]}", "empty_or_absent": missing})
        else:
            kept[tag] = docs

    margins = [mdl_correspondence(d["D"], d["X"], DEFAULT_CODE).ratio
               - mdl_correspondence(d["D"], d["W"], DEFAULT_CODE).ratio
               for _, d in sorted(kept.items())]

    n_total = len(motifs)
    if len(kept) * 2 < n_total:
        verdict = ("TEST DID NOT RUN -- more than half the motifs excluded for empty "
                   "annotations. No claim either way, per the plan")
        res = None
    else:
        res = evaluate_margins(margins)
        loo = []
        for i in range(len(margins)):
            r = evaluate_margins(margins[:i] + margins[i + 1:])
            loo.append(r.t_p < 0.05)
        survive = sum(loo)
        both = res.t_p < 0.05 and res.wilcoxon_p < 0.05
        if res.mean <= 0:
            verdict = "FALSIFIED -- mean margin is not positive under independent annotation"
        elif not both:
            verdict = ("SUGGESTIVE ONLY -- one test above 0.05, which the plan says "
                       "does not count as supported")
        elif survive * 2 < len(loo):
            verdict = ("FRAGILE, NOT ESTABLISHED -- significant but leave-one-out "
                       "survives under half")
        else:
            verdict = "SUPPORTED -- significant on both tests and robust to leave-one-out"

    report = {
        "experiment": "EXP-039", "questions": ["Q-31", "Q-37"],
        "plan_committed_at": "6a9aa8e",
        "plan_sha256_prefix": "efcab218bd95139600b2bb9801df76d5",
        "annotator": "second system, format spec only, roles/motifs/corpus stripped",
        "motifs_total": n_total, "motifs_kept": len(kept),
        "excluded": excluded,
        "relations_per_document": {
            "second_annotator": round(statistics.fmean(rel_counts), 2),
            "my_sighted": 4.2, "my_blind": 2.70,
        },
        "margins": [round(m, 4) for m in margins],
        "result": res.as_dict() if res else None,
        "comparison_effect_size": {
            "second_annotator": round(res.effect_size_d, 3) if res else None,
            "my_sighted": 2.045, "my_blind": 0.799,
        },
        "verdict": verdict,
    }
    if res:
        report["leave_one_out_survives"] = f"{sum(loo)}/{len(loo)}"

    out = ROOT / "results" / "exp039.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nEXP-039  written to {out}")
    print(f"plan locked at {report['plan_committed_at']} before any computation\n")

    print(f"motifs: {len(kept)} kept of {n_total}")
    for e in excluded:
        print(f"   excluded {e['motif']:<26} empty/absent: {e['empty_or_absent']}")
    r = report["relations_per_document"]
    print(f"\nrelations per document: second annotator {r['second_annotator']}, "
          f"my sighted {r['my_sighted']}, my blind {r['my_blind']}")

    if res:
        d = res.as_dict()
        print(f"\nmargins        : {d['per_motif_margins']}")
        print(f"mean           : {d['mean_margin_bits']:+.4f} bits   sd {d['sd']:.4f}")
        print(f"95% CI         : [{d['ci95_on_mean'][0]:+.4f}, {d['ci95_on_mean'][1]:+.4f}]"
              f"   {'excludes zero' if d['ci95_on_mean'][0] > 0 else 'INCLUDES ZERO'}")
        print(f"effect size d  : {d['effect_size_d']}   "
              f"(my sighted 2.045, my blind 0.799)")
        print(f"t-test p       : {d['t_test_p']:.4f}")
        print(f"Wilcoxon p     : {d['wilcoxon_p']:.4f}   "
              f"(n={d['wilcoxon_n_after_dropping_ties']} after ties)")
        print(f"leave-one-out  : {report['leave_one_out_survives']}")
        print(f"footnote wins  : {d['_footnote_win_count']}")

    print(f"\n>>> {verdict}")


if __name__ == "__main__":
    main()
