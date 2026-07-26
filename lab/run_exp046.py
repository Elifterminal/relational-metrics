"""EXP-046 -- is the signal BURIED in the prose annotations, or ABSENT?

Run to the plan locked at 645eb67a. This is the real Q-40 test: a hedge channel
can only help if useful structure is present and obscured. If no subset of what
the reader wrote carries signal, filtering cannot help however well it is done.

THE HAZARD IS THE WHOLE DESIGN. Searching subsets for one that produces signal
WILL find one -- that is guaranteed, not a risk. So the observed best-subset
margin means nothing on its own. It is compared against the identical search run
on label-permuted data, and only the excess counts.
"""

from __future__ import annotations

import ast
import csv
import itertools
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from codes import DEFAULT_CODE                                    # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from protocol2 import require_locked_plan                         # noqa: E402
from run_exp043 import build, parse_all                           # noqa: E402
from structure import Structure                                   # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MAX_Q = 8
RNG = random.Random(46460726)


def subsets(s: Structure):
    rel = s.relations
    for k in range(1, len(rel) + 1):
        for combo in itertools.combinations(range(len(rel)), k):
            sub = tuple(rel[i] for i in combo)
            nodes = tuple(sorted({n for r in sub for n in (r.src, r.dst)}))
            yield len(combo), Structure(s.name, nodes, sub, s.domain)


def margin_extremes(q: Structure, good: Structure, bad: Structure):
    """Max and min margin over subsets of the QUERY's relations, in one pass.

    EXACT OPTIMISATION, not an approximation. Swapping the labels negates every
    subset's margin, so the best-subset margin under a swap is exactly
    -min(margin). Computing max and min once per item makes the permutation a
    choice between two known numbers instead of 2000 repeated searches. The
    statistic is identical; only the cost changes.
    """
    hi, lo, hi_k = None, None, None
    for k, sub in subsets(q):
        m = (mdl_correspondence(sub, good, DEFAULT_CODE).ratio
             - mdl_correspondence(sub, bad, DEFAULT_CODE).ratio)
        if hi is None or m > hi:
            hi, hi_k = m, k
        if lo is None or m < lo:
            lo = m
    return hi, lo, hi_k


def main() -> None:
    plan = require_locked_plan("EXP-046")
    ann = parse_all()
    idmap = json.loads((ROOT / "external" / "q43_idmap.json").read_text())
    key = json.loads((ROOT / "external" / "q43_key.json").read_text())
    truth = {r["id"]: int(r["correct_answer"])
             for r in csv.DictReader((ROOT / "external" / "arn.csv").open())}

    items = {}
    for tag, edges in ann.items():
        k = key[idmap[tag]]
        items.setdefault(k["item"], {})[k["role"]] = build(tag, edges)

    triples, excluded = [], []
    for iid, v in sorted(items.items()):
        if len(v) != 3:
            continue
        if v["Q"].m > MAX_Q:
            excluded.append(iid)
            continue
        good = v["A"] if truth[iid] == 1 else v["B"]
        bad = v["B"] if truth[iid] == 1 else v["A"]
        triples.append((iid, v["Q"], good, bad))

    obs, swapped, full_wins, rows = [], [], 0, []
    for iid, q, good, bad in triples:
        hi, lo, k = margin_extremes(q, good, bad)
        obs.append(hi)
        swapped.append(-lo)          # best subset margin if the labels were swapped
        full_wins += (k == q.m)
        rows.append({"item": iid, "query_relations": q.m,
                     "best_subset_size": k, "best_margin": round(hi, 4)})
    obs_mean = statistics.fmean(obs)

    # NULL: identical search, labels permuted. Swapping good/bad per item is the
    # exact permutation of the thing being tested.
    n_perm = 20000
    null = []
    for _ in range(n_perm):
        tot = sum(obs[i] if RNG.random() < 0.5 else swapped[i]
                  for i in range(len(triples)))
        null.append(tot / len(triples))
    ge = sum(1 for x in null if x >= obs_mean - 1e-12)
    p = (ge + 1) / (n_perm + 1)
    null_mean = statistics.fmean(null)

    if full_wins * 2 > len(triples):
        verdict = ("NOTHING TO FILTER -- the full set of query relations is already "
                   "the best subset on most items, so there is no buried signal for "
                   "a hedge channel to surface")
    elif p >= 0.05:
        verdict = ("SIGNAL IS ABSENT, NOT BURIED -- the best subset does no better "
                   "than the same search on permuted labels. No hedge channel can "
                   "recover what is not there. Q-40 is dead")
    else:
        verdict = ("SIGNAL IS BURIED -- subset selection beats the permuted null, so "
                   "filtering could in principle recover it. Q-40 lives and a "
                   "commission is justified")

    report = {
        "experiment": "EXP-046", "question": "Q-40, the real test",
        "plan_locked_at": plan["_locked_at"], "plan_sha256": plan["_sha256"],
        "items": len(triples), "excluded_for_search_size": excluded,
        "observed_mean_best_subset_margin": round(obs_mean, 4),
        "permuted_null_mean": round(null_mean, 4),
        "excess_over_null": round(obs_mean - null_mean, 4),
        "permutation_p": round(p, 4), "n_permutations": n_perm,
        "best_subset_was_full_set": f"{full_wins}/{len(triples)}",
        "search_note": ("subsets of the QUERY only; candidates left whole. A negative "
                        "does not rule out that filtering the CANDIDATES would help"),
        "rows": rows, "verdict": verdict,
    }
    (ROOT / "results" / "exp046.json").write_text(json.dumps(report, indent=2))
    print(f"\nEXP-046   plan locked at {plan['_locked_at'][:8]}\n")
    print(f"items {len(triples)}   excluded for search size {len(excluded)}\n")
    print(f"   observed mean best-subset margin : {obs_mean:+.4f}")
    print(f"   same search on permuted labels   : {null_mean:+.4f}")
    print(f"   excess over the null             : {obs_mean - null_mean:+.4f}")
    print(f"   permutation p ({n_perm} shuffles)   : {p:.4f}")
    print(f"   best subset was the full set     : {full_wins}/{len(triples)}\n")
    print(f">>> {verdict}")


if __name__ == "__main__":
    main()
