"""EXP-045 -- does the hedge-channel hypothesis leave a trace in data we have?

Run to the plan locked at ec59b8e2, before any commission is spent.

EXP-043 failed because the reader never declined on prose. Q-40 proposes letting
it mark relations as INFERRED rather than STATED so noise becomes separable.
That is a format change and it needs a commission -- so first, cheaply: if
manufactured relations are noise, the noise is already in the EXP-043 data and
should leave a trace.

Prediction direction fixed from the floor finding, not from inspecting margins.
"""

from __future__ import annotations

import ast
import csv
import json
import random
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from protocol2 import require_locked_plan                         # noqa: E402
from run_exp043 import build, parse_all                           # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RNG = random.Random(45450726)


def spearman(a, b):
    def rank(xs):
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0.0] * len(xs)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = rank(a), rank(b)
    ma, mb = statistics.fmean(ra), statistics.fmean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else 0.0


def perm_p(a, b, stat, n=20000):
    obs = stat(a, b)
    bb = list(b)
    hits = 0
    for _ in range(n):
        RNG.shuffle(bb)
        if abs(stat(a, bb)) >= abs(obs) - 1e-12:
            hits += 1
    return obs, (hits + 1) / (n + 1)


def main() -> None:
    plan = require_locked_plan("EXP-045")

    ann = parse_all()
    idmap = json.loads((ROOT / "external" / "q43_idmap.json").read_text())
    key = json.loads((ROOT / "external" / "q43_key.json").read_text())
    truth = {r["id"]: int(r["correct_answer"])
             for r in csv.DictReader((ROOT / "external" / "arn.csv").open())}

    items = {}
    for tag, edges in ann.items():
        k = key[idmap[tag]]
        items.setdefault(k["item"], {})[k["role"]] = build(tag, edges)

    counts, margins, rows = [], [], []
    for iid, v in sorted(items.items()):
        if len(v) != 3:
            continue
        good = v["A"] if truth[iid] == 1 else v["B"]
        bad = v["B"] if truth[iid] == 1 else v["A"]
        c = v["Q"].m + good.m + bad.m
        m = (mdl_correspondence(v["Q"], good, DEFAULT_CODE).ratio
             - mdl_correspondence(v["Q"], bad, DEFAULT_CODE).ratio)
        counts.append(c)
        margins.append(m)
        rows.append({"item": iid, "total_relations": c, "margin": round(m, 4)})

    rho, p = perm_p(counts, margins, spearman)

    # leave-one-out on the correlation
    signs = []
    for i in range(len(counts)):
        r = spearman(counts[:i] + counts[i + 1:], margins[:i] + margins[i + 1:])
        signs.append(r)
    flips = sum(1 for r in signs if (r > 0) != (rho > 0))

    # secondary: median split
    med = statistics.median(counts)
    lo = [m for c, m in zip(counts, margins) if c <= med]
    hi = [m for c, m in zip(counts, margins) if c > med]
    diff = statistics.fmean(lo) - statistics.fmean(hi) if lo and hi else 0.0
    pooled = margins[:]
    hits = 0
    for _ in range(20000):
        RNG.shuffle(pooled)
        d = statistics.fmean(pooled[:len(lo)]) - statistics.fmean(pooled[len(lo):])
        if abs(d) >= abs(diff) - 1e-12:
            hits += 1
    p_split = (hits + 1) / 20001

    if p >= 0.05:
        verdict = ("HYPOTHESIS UNSUPPORTED -- no relationship between how much the "
                   "reader wrote and how much signal survived. Q-40 loses its main "
                   "quantitative support. Per the plan: do NOT spend a commission "
                   "on it without a different reason")
    elif rho > 0:
        verdict = ("HYPOTHESIS BACKWARDS -- more relations go with MORE signal, so "
                   "manufactured structure is not what is hurting us")
    elif flips:
        verdict = (f"SUGGESTIVE, NOT ESTABLISHED -- negative as predicted but "
                   f"leave-one-out flips the sign on {flips} of {len(signs)}")
    else:
        verdict = ("SUPPORTS THE HYPOTHESIS -- fewer relations, more signal, robust "
                   "to leave-one-out. A hedge channel is worth commissioning")

    report = {
        "experiment": "EXP-045", "question": "Q-40 pre-test",
        "plan_locked_at": plan["_locked_at"], "plan_sha256": plan["_sha256"],
        "n_items": len(rows),
        "spearman_rho": round(rho, 4), "permutation_p": round(p, 5),
        "leave_one_out_sign_flips": f"{flips}/{len(signs)}",
        "median_split": {
            "median_relations": med,
            "mean_margin_low_count": round(statistics.fmean(lo), 4) if lo else None,
            "mean_margin_high_count": round(statistics.fmean(hi), 4) if hi else None,
            "difference": round(diff, 4), "permutation_p": round(p_split, 5),
        },
        "relation_counts": {"min": min(counts), "max": max(counts),
                            "mean": round(statistics.fmean(counts), 1)},
        "what_a_positive_would_license": plan["what_a_positive_result_would_and_would_not_license"],
        "rows": rows, "verdict": verdict,
    }
    (ROOT / "results" / "exp045.json").write_text(json.dumps(report, indent=2))
    print(f"\nEXP-045   plan locked at {plan['_locked_at'][:8]}\n")
    print(f"items {len(rows)}   relations per item "
          f"{report['relation_counts']['min']}–{report['relation_counts']['max']} "
          f"(mean {report['relation_counts']['mean']})\n")
    print(f"   Spearman rho (relations vs margin) : {rho:+.4f}")
    print(f"   permutation p (20000 shuffles)     : {p:.4f}")
    print(f"   leave-one-out sign flips           : {flips}/{len(signs)}\n")
    ms = report["median_split"]
    print(f"   median split at {ms['median_relations']} relations")
    print(f"      fewer relations : mean margin {ms['mean_margin_low_count']:+.4f}")
    print(f"      more relations  : mean margin {ms['mean_margin_high_count']:+.4f}")
    print(f"      difference {ms['difference']:+.4f}, p = {ms['permutation_p']:.4f}")
    print(f"\n>>> {verdict}")


if __name__ == "__main__":
    main()
