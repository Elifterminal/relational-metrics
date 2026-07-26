"""EXP-047 -- settle C-03 at a sample size that can actually settle it.

Run to the plan locked at 440c4452.

Lee asked to settle the small result at thirty cases. Rebuilding thirty
hand-made motifs would rebuild both biases Stage 1 identified, so the structures
are generated instead and no annotation exists anywhere in this experiment.

WHAT THAT BUYS AND WHAT IT COSTS, from the plan and repeated here because it
decides how the result may be read:
  buys  -- a test of the MEASURE at n=120 per level, with no annotator to bias it
  costs -- realism. These are not documents anyone wrote, and the
           analogue/false-friend distinction is true by construction rather than
           by judgement. This does NOT settle how hand-annotated corpora behave.
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
from motifgen import triple                                       # noqa: E402
from protocol2 import require_locked_plan                         # noqa: E402

N = 120
LEVELS = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)


def corr(a, b):
    return mdl_correspondence(a, b, DEFAULT_CODE).ratio


def main() -> None:
    plan = require_locked_plan("EXP-047")
    out_levels = []

    for lv in LEVELS:
        margins, ctrl, excluded = [], [], 0
        for i in range(N):
            q, a, w, u = triple(seed=hash((round(lv * 100), i)) % 10**6, perturb=lv)
            if min(q.m, a.m, w.m, u.m) == 0 or w.edge_set() == q.edge_set():
                excluded += 1
                continue
            margins.append(corr(q, a) - corr(q, w))
            ctrl.append(corr(q, u) - corr(q, w))     # control: unrelated vs false friend
        res = evaluate_margins(margins)
        out_levels.append({
            "perturbation": lv, "n": len(margins), "excluded": excluded,
            "mean_margin": round(res.mean, 4),
            "ci95": [round(res.ci95[0], 4), round(res.ci95[1], 4)],
            "effect_size_d": round(res.effect_size_d, 3),
            "t_p_raw": res.t_p, "wilcoxon_p_raw": res.wilcoxon_p,
            "analogue_wins_fraction": round(res.wins / len(margins), 3),
            "control_mean_unrelated_minus_false_friend": round(
                statistics.fmean(ctrl), 4),
        })

    # Holm across the sweep, on the t-test, because a sweep is many chances
    order = sorted(out_levels, key=lambda r: r["t_p_raw"])
    m, prev = len(order), 0.0
    for i, r in enumerate(order):
        adj = min(1.0, max(prev, r["t_p_raw"] * (m - i)))
        r["t_p_holm"] = round(adj, 6)
        r["significant"] = adj < 0.05 and r["wilcoxon_p_raw"] < 0.05
        prev = adj

    sig = [r for r in out_levels if r["significant"]]
    ctrl_ok = all(r["control_mean_unrelated_minus_false_friend"] < 0 for r in out_levels)
    boundary = next((r["perturbation"] for r in out_levels if not r["significant"]), None)

    if not sig:
        verdict = ("C-03 NOT SUPPORTED BY THE MEASURE ALONE -- no perturbation level "
                   "gives a positive margin. The corpus result was an artifact")
    elif not ctrl_ok:
        verdict = ("SUSPECT -- an unrelated structure outscores the false friend at "
                   "some level, so the measure may be rewarding renaming rather than "
                   "shape. The main result cannot be read until this is explained")
    elif len(sig) == len(out_levels):
        verdict = ("SUPPORTED AT EVERY LEVEL -- and per the plan that is suspicious "
                   "rather than reassuring; check the false friend is genuinely "
                   "being made different")
    else:
        verdict = (f"SUPPORTED AND BOUNDED -- the property holds and stops holding at "
                   f"perturbation {boundary}. That boundary is the result")

    report = {"experiment": "EXP-047", "question": "settle C-03 at adequate n",
              "plan_locked_at": plan["_locked_at"], "plan_sha256": plan["_sha256"],
              "n_per_level": N, "annotation_involved": "none",
              "does_not_settle": plan["what_this_settles_and_what_it_does_not"]["does_not_settle"],
              "levels": out_levels, "control_arm_ok": ctrl_ok,
              "significant_levels": len(sig), "boundary": boundary,
              "verdict": verdict}
    (Path(__file__).resolve().parents[1] / "results" / "exp047.json").write_text(
        json.dumps(report, indent=2))

    print(f"\nEXP-047   plan locked at {plan['_locked_at'][:8]}   no annotation involved\n")
    print(f"{'perturb':>8}{'n':>5}{'margin':>9}{'95% CI':>20}{'d':>7}"
          f"{'p(Holm)':>10}{'wins':>7}{'control':>9}")
    for r in out_levels:
        ci = f"[{r['ci95'][0]:+.3f},{r['ci95'][1]:+.3f}]"
        print(f"{r['perturbation']:>8.1f}{r['n']:>5}{r['mean_margin']:>9.4f}{ci:>20}"
              f"{r['effect_size_d']:>7.2f}{r['t_p_holm']:>10.4f}"
              f"{r['analogue_wins_fraction']:>7.2f}"
              f"{r['control_mean_unrelated_minus_false_friend']:>9.3f}"
              f"{'  *' if r['significant'] else ''}")
    print(f"\ncontrol arm (unrelated should score BELOW the false friend everywhere): "
          f"{ctrl_ok}")
    print(f"\n>>> {verdict}")


if __name__ == "__main__":
    main()
