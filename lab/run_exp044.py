"""EXP-044 -- what specifically makes narrative prose hard?

Run to the plan locked at f0a14b10. Reads no correct-answer label at any point:
this measures properties of the TEXT, so it cannot be steered by a score and is
not the forbidden move of tuning a reader against a benchmark I have seen.

EXP-042 established that a rule-based reader fails on prose. "Prose is harder"
is not actionable. If the gap is one or two specific properties, that says what
any Stage 2 reader must handle.
"""

from __future__ import annotations

import json
import math
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mechanical import NEG_VERBS, POS_VERBS                       # noqa: E402
from protocol2 import require_locked_plan                         # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LEX = set(POS_VERBS) | set(NEG_VERBS)
PRONOUNS = {"he", "she", "it", "they", "him", "her", "them", "his", "hers",
            "their", "theirs", "its", "we", "us", "our", "i", "me", "my", "you"}


def sentences(t):
    return [s for s in re.split(r"[.!?]+", t) if s.strip()]


def measure(text: str) -> dict:
    words = re.findall(r"[A-Za-z']+", text)
    low = [w.lower() for w in words]
    sents = sentences(text)
    verbs = sum(1 for w in low if w in LEX)
    no_verb = sum(1 for s in sents
                  if not any(w.lower() in LEX for w in re.findall(r"[A-Za-z']+", s)))
    proper = sum(1 for w in words[1:] if w[:1].isupper())
    clauses = sum(1 + len(re.findall(r",|;| and | which | who | because | so ", s))
                  for s in sents)
    n = max(len(words), 1)
    return {
        "words": len(words),
        "sentences": max(len(sents), 1),
        "causal_verbs_per_100_words": 100 * verbs / n,
        "pct_sentences_without_a_causal_verb": 100 * no_verb / max(len(sents), 1),
        "pronouns_per_100_words": 100 * sum(1 for w in low if w in PRONOUNS) / n,
        "proper_nouns_per_100_words": 100 * proper / n,
        "clauses_per_sentence": clauses / max(len(sents), 1),
    }


def welch(a, b):
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    na, nb = len(a), len(b)
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return 0.0, 1.0
    t = (ma - mb) / se
    df = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    z = abs(t) / math.sqrt(1 + t * t / df)          # normal approx, adequate at these n
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2 * (1 + 2 / df)))))
    return t, max(min(p, 1.0), 0.0)


def main() -> None:
    plan = require_locked_plan("EXP-044")

    easy = [p["gloss"] for f in ("q26_pool.json", "q30_pool.json")
            for p in json.loads((ROOT / "external" / f).read_text())["passages"]]
    hard = [b.split(". ", 1)[1] for b in
            (Path("/tmp/claude-1000/-home-lee/f289a166-f2fd-494b-95a4-0c004dd290e6/"
                  "scratchpad/arn_passages.txt").read_text().split("\n\n"))
            if ". " in b]

    E = [measure(t) for t in easy]
    H = [measure(t) for t in hard]
    keys = [k for k in E[0] if k not in ("words", "sentences")] + ["words", "sentences"]

    raw = []
    for k in keys:
        a = [x[k] for x in E]
        b = [x[k] for x in H]
        t, p = welch(a, b)
        raw.append({"measure": k, "easy_mean": round(statistics.fmean(a), 2),
                    "hard_mean": round(statistics.fmean(b), 2),
                    "ratio_hard_over_easy": round(
                        statistics.fmean(b) / statistics.fmean(a), 2)
                    if statistics.fmean(a) else None,
                    "t": round(t, 2), "p_raw": p})

    # Holm correction over the six planned measures (length pair excluded --
    # they are context, declared as such, not among the six)
    planned = [r for r in raw if r["measure"] not in ("words", "sentences")]
    order = sorted(planned, key=lambda r: r["p_raw"])
    m = len(order)
    prev = 0.0
    for i, r in enumerate(order):
        adj = min(1.0, max(prev, r["p_raw"] * (m - i)))
        r["p_holm"] = round(adj, 5)
        r["significant"] = adj < 0.05
        prev = adj

    # robustness: is the top separator just length in disguise?
    top = min(planned, key=lambda r: r["p_holm"])
    lo, hi = 20, 60
    eL = [x for x in E if lo <= x["words"] <= hi]
    hL = [x for x in H if lo <= x["words"] <= hi]
    if len(eL) >= 5 and len(hL) >= 5:
        t2, p2 = welch([x[top["measure"]] for x in eL], [x[top["measure"]] for x in hL])
        lm = {"window_words": [lo, hi], "n_easy": len(eL), "n_hard": len(hL),
              "t": round(t2, 2), "p": round(p2, 5), "survives": p2 < 0.05}
    else:
        lm = {"window_words": [lo, hi], "n_easy": len(eL), "n_hard": len(hL),
              "survives": None, "note": "too few passages overlap in length to test"}

    sig = [r for r in planned if r["significant"]]
    verdict = ("NO SURFACE MEASURE SEPARATES THEM -- this diagnostic failed"
               if not sig else
               f"{len(sig)} of {m} measures separate the sets; largest is "
               f"'{top['measure']}' at {top['ratio_hard_over_easy']}x")

    report = {"experiment": "EXP-044",
              "plan_locked_at": plan["_locked_at"], "plan_sha256": plan["_sha256"],
              "labels_read": "none",
              "n_easy": len(E), "n_hard": len(H),
              "measures": raw, "length_matched_check": lm, "verdict": verdict}
    (ROOT / "results" / "exp044.json").write_text(json.dumps(report, indent=2))

    print(f"\nEXP-044   plan locked at {plan['_locked_at'][:8]}, no labels read\n")
    print(f"{'measure':<42}{'glosses':>9}{'prose':>9}{'ratio':>8}{'p(Holm)':>10}")
    for r in sorted(planned, key=lambda r: r["p_holm"]):
        print(f"{r['measure']:<42}{r['easy_mean']:>9.2f}{r['hard_mean']:>9.2f}"
              f"{(r['ratio_hard_over_easy'] or 0):>8.2f}{r['p_holm']:>10.4f}"
              f"{'  *' if r['significant'] else ''}")
    for r in raw:
        if r["measure"] in ("words", "sentences"):
            print(f"{r['measure'] + ' (context)':<42}{r['easy_mean']:>9.2f}"
                  f"{r['hard_mean']:>9.2f}{(r['ratio_hard_over_easy'] or 0):>8.2f}")
    print(f"\nlength-matched check on '{top['measure']}': {lm}")
    print(f"\n>>> {verdict}")


if __name__ == "__main__":
    main()
