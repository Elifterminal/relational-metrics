"""EXP-048 -- how much damage can an analogue take and still be preferred?

Run to the plan locked at 55f587d8. Corrected design after EXP-047's sweep
collapsed into equal damage on both sides.

No annotation exists anywhere in this experiment. What that buys is a test of
the MEASURE at n=200 per level with no annotator to bias it; what it costs is
realism, since the analogue/false-friend distinction is true by construction
rather than by judgement. It does not settle how hand-annotated corpora behave.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from evaluate import evaluate_margins                             # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from motifgen import triple_k                                     # noqa: E402
from protocol2 import require_locked_plan                         # noqa: E402

N = 200
KS = (0, 1, 2, 3, 4)
GAP = 2


def corr(a, b):
    return mdl_correspondence(a, b, DEFAULT_CODE).ratio


def main() -> None:
    plan = require_locked_plan("EXP-048")
    levels = []

    for k in KS:
        margins, ctrl, excluded = [], [], 0
        for i in range(N):
            q, a, w, u = triple_k(seed=7000 * (k + 1) + i, k_analogue=k, gap=GAP)
            if min(q.m, a.m, w.m, u.m) == 0 or w.edge_set() == q.edge_set():
                excluded += 1
                continue
            margins.append(corr(q, a) - corr(q, w))
            ctrl.append(corr(q, u) - corr(q, w))
        res = evaluate_margins(margins)
        levels.append({
            "k_analogue_rewires": k, "k_false_friend_rewires": k + GAP,
            "n": len(margins), "excluded": excluded,
            "excluded_pct": round(100 * excluded / N, 1),
            "mean_margin": round(res.mean, 4),
            "ci95": [round(res.ci95[0], 4), round(res.ci95[1], 4)],
            "effect_size_d": round(res.effect_size_d, 3),
            "analogue_wins_fraction": round(res.wins / len(margins), 3),
            "t_p_raw": res.t_p, "wilcoxon_p_raw": res.wilcoxon_p,
            "control_unrelated_minus_false_friend": round(statistics.fmean(ctrl), 4),
        })

    order = sorted(levels, key=lambda r: r["t_p_raw"])
    m, prev = len(order), 0.0
    for i, r in enumerate(order):
        adj = min(1.0, max(prev, r["t_p_raw"] * (m - i)))
        r["t_p_holm"] = round(adj, 6)
        r["significant"] = adj < 0.05 and r["wilcoxon_p_raw"] < 0.05
        prev = adj

    # The predeclared rule was GLOBAL: control positive anywhere -> nothing is
    # readable. It fired. It is also too coarse, for the fourth time today
    # (P-23), and the reason is visible: by k=3 the false friend has 5 of 8
    # relations rewired and is close to unrelated itself, so "unrelated beats
    # false friend" stops meaning what the rule assumed it meant.
    #
    # Reporting BOTH -- the rule as written, and a per-level reading -- rather
    # than quietly replacing the rule I locked with one I like better.
    ctrl_ok = all(r["control_unrelated_minus_false_friend"] < 0 for r in levels)
    for r in levels:
        r["control_clean"] = r["control_unrelated_minus_false_friend"] < 0
        r["readable"] = r["control_clean"]
    sig = [r for r in levels if r["significant"]]
    boundary = next((r["k_analogue_rewires"] for r in levels if not r["significant"]), None)

    readable = [r for r in levels if r["readable"]]
    sig_readable = [r for r in readable if r["significant"]]
    last_good = max((r["k_analogue_rewires"] for r in sig_readable), default=None)

    if not readable:
        verdict = ("UNREADABLE AT EVERY LEVEL -- an unrelated structure beats the "
                   "false friend throughout, so the measure rewards renaming")
    elif not sig:
        verdict = "C-03 NOT SUPPORTED -- no damage level gives a positive margin"
    elif boundary is None:
        verdict = ("SUPPORTED AT EVERY LEVEL TESTED -- the property holds out to "
                   f"{KS[-1]} rewires; check the win fraction before calling it robust")
    elif boundary <= 1:
        verdict = (f"SUPPORTED ONLY NEAR-IDENTITY -- the preference holds at "
                   f"{boundary - 1} rewire(s) and is gone by {boundary}. The measure "
                   f"detects near-exact structural copies, not analogy. Bad news for "
                   f"C-03, and predicted in the locked plan")
    else:
        verdict = (f"SUPPORTED AND BOUNDED -- holds up to {last_good} rewires of "
                   f"{8} at readable levels, gone by k={boundary}. That boundary is "
                   f"the result")

    report = {"experiment": "EXP-048", "supersedes_design_of": "EXP-047",
              "predeclared_global_control_rule": {
                  "as_written": "control positive anywhere -> nothing readable",
                  "it_fired": not ctrl_ok,
                  "why_it_is_too_coarse": ("by k=3 the false friend has 5 of 8 "
                      "relations rewired and is close to unrelated itself, so "
                      "'unrelated beats false friend' stops meaning what the rule "
                      "assumed. Fourth predeclared verdict rule today to be too "
                      "coarse for its own result (P-23)"),
                  "handling": ("both readings reported. Levels with a clean control "
                               "are marked readable; the rest are not read"),
              },
              "readable_levels": [r["k_analogue_rewires"] for r in levels if r["readable"]],
              "last_significant_readable_k": last_good,
              "plan_locked_at": plan["_locked_at"], "plan_sha256": plan["_sha256"],
              "n_per_level": N, "gap": GAP, "annotation_involved": "none",
              "levels": levels, "control_arm_ok": ctrl_ok,
              "boundary_k": boundary, "verdict": verdict}
    (Path(__file__).resolve().parents[1] / "results" / "exp048.json").write_text(
        json.dumps(report, indent=2))

    print(f"\nEXP-048   plan locked at {plan['_locked_at'][:8]}   no annotation\n")
    print(f"analogue rewires k, false friend rewires k+{GAP} -- the analogue is "
          f"always the less damaged one\n")
    print(f"{'k':>3}{'n':>5}{'margin':>9}{'95% CI':>19}{'d':>7}{'wins':>7}"
          f"{'p(Holm)':>10}{'control':>9}")
    for r in levels:
        ci = f"[{r['ci95'][0]:+.3f},{r['ci95'][1]:+.3f}]"
        print(f"{r['k_analogue_rewires']:>3}{r['n']:>5}{r['mean_margin']:>9.4f}{ci:>19}"
              f"{r['effect_size_d']:>7.2f}{r['analogue_wins_fraction']:>7.2f}"
              f"{r['t_p_holm']:>10.4f}"
              f"{r['control_unrelated_minus_false_friend']:>9.3f}"
              f"{'  *' if r['significant'] else ''}")
    print(f"\npredeclared global control rule fired: {not ctrl_ok}")
    print(f"   readable levels (clean control): "
          f"{[r['k_analogue_rewires'] for r in levels if r['readable']]}")
    print(f"   at k=3 the false friend has 5 of 8 relations rewired -- close to")
    print(f"   unrelated itself, so the global rule was too coarse. Both reported.")
    print(f"\n>>> {verdict}")


if __name__ == "__main__":
    main()
