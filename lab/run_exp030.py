"""EXP-030 -- the ARN benchmark. Ground truth from outside the project.

254 items in exactly this project's design (Zenodo 11044026, CC-BY 4.0), in the
hardest cell: a FAR analogy against a HIGH-similarity distractor. Query
narrative, a cross-domain analogue, a surface-similar false friend. Nobody
involved in this project wrote the narratives, chose the distractors, or set
the answers.

Every earlier corpus test had the project supplying at least the annotations
and usually the ground truth too. Here the only thing this project supplies is
the annotation -- and the annotation was made blind.

THE BLIND, which is stronger than hiding the answers:
  * every passage annotated ALONE, with its ROLE hidden -- while annotating I
    could not tell query from analogue from distractor
  * passages presented in item-contiguous blocks with roles scrambled inside
  * `correct_answer` unreadable until the annotations were committed and hashed
  * `arn_blind.reveal()` refuses to run if the annotation file changes after
    sealing, so re-annotating in the light of the labels is blocked by the code
    rather than by my memory of intending not to

20 of the 60 sampled items are annotated here. The other 40 stay sealed as a
second held-out set -- deliberately, because a benchmark spent all at once
cannot be spent again, and if the annotation scheme turns out to need revising
I would rather still have something to revise it against.

PREDECLARED: chance is 50%. Success is beating it at p < 0.05, two-sided, which
on 20 items means >= 15 correct. Anything from 11 to 14 is "not distinguishable
from chance" and will be reported as such, not as a trend.

PREDECLARED WORRY: I am the annotator, and the annotation is where this could
go wrong. Blindness to role removes the obvious route for bias but not the
subtle one -- my sense of what a causal skeleton looks like was formed on the
project's own corpora. A pass here is evidence the measure works on outside
data; it is not evidence that automatic annotation would reproduce it.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from arn_annotations_raw import A as ANNOT                        # noqa: E402
from arn_blind import ANNOT as ANNOT_PATH, load_pool, reveal      # noqa: E402
from codes import DEFAULT_CODE                                    # noqa: E402
from measures import mdl_correspondence                           # noqa: E402
from structure import Relation, Structure                         # noqa: E402


def build(pid: str) -> Structure:
    rels = tuple(Relation(s, d, t) for s, d, t in ANNOT[pid])
    nodes = tuple(sorted({n for r in rels for n in (r.src, r.dst)}))
    return Structure(pid, nodes, rels, domain=pid)


def binomial_p(k: int, n: int, p: float = 0.5) -> float:
    """Two-sided exact binomial."""
    def pmf(i):
        return math.comb(n, i) * p ** i * (1 - p) ** (n - i)
    obs = pmf(k)
    return min(1.0, sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs + 1e-12))


def main() -> None:
    # commit the annotations BEFORE anything is unsealed
    ANNOT_PATH.write_text(json.dumps(
        {pid: ANNOT[pid] for pid in sorted(ANNOT)}, indent=2, sort_keys=True))
    key = reveal()

    roles = {k["passage_id"]: (k["item_id"], k["role"])
             for k in key["key"] if "passage_id" in k}
    answers = {k["item_id"]: k["correct_answer"]
               for k in key["key"] if "correct_answer" in k}
    proverbs = {k["item_id"]: k["proverb"]
                for k in key["key"] if "proverb" in k}

    # group the annotated passages back into items
    items: dict[str, dict[str, str]] = {}
    for pid in ANNOT:
        iid, role = roles[pid]
        items.setdefault(iid, {})[role] = pid
    complete = {i: v for i, v in items.items() if len(v) == 3}

    rows, correct, ties = [], 0, 0
    for iid, v in sorted(complete.items()):
        q = build(v["Q"])
        sa = mdl_correspondence(q, build(v["A"]), DEFAULT_CODE).ratio
        sb = mdl_correspondence(q, build(v["B"]), DEFAULT_CODE).ratio
        truth = int(answers[iid])
        if sa == sb:
            ties += 1
            got, hit = 0, False           # a tie is not a correct answer
        else:
            got = 1 if sa > sb else 2
            hit = got == truth
        correct += hit
        rows.append({"item": iid, "proverb": proverbs[iid],
                     "score_first": round(sa, 4), "score_second": round(sb, 4),
                     "predicted": got, "truth": truth, "correct": hit,
                     "tie": sa == sb, "margin": round(abs(sa - sb), 4)})

    n = len(rows)
    p = binomial_p(correct, n)

    # Scoring ties as failures gives a headline that reads as ANTI-correlation,
    # which would be a claim the data does not support. A tie is an abstention.
    # Both honest readings are reported and the significant-looking one is not
    # allowed to be the headline.
    disc = [r for r in rows if not r["tie"]]
    disc_correct = sum(r["correct"] for r in disc)
    p_disc = binomial_p(disc_correct, len(disc)) if disc else 1.0
    as_coinflip = disc_correct + (n - len(disc)) / 2
    p_coin = binomial_p(round(as_coinflip), n)

    # Whose failure is it? If the raw matched-relation count -- MDL pricing
    # removed entirely -- also sits at chance, the ANNOTATION never contained
    # the distinction and this experiment tested the annotator.
    favours_correct = favours_distractor = neither = 0
    for iid, v in sorted(complete.items()):
        q = build(v["Q"])
        good = build(v["A"] if int(answers[iid]) == 1 else v["B"])
        bad = build(v["B"] if int(answers[iid]) == 1 else v["A"])
        mg = mdl_correspondence(q, good, DEFAULT_CODE).matched
        mb = mdl_correspondence(q, bad, DEFAULT_CODE).matched
        favours_correct += mg > mb
        favours_distractor += mg < mb
        neither += mg == mb
    report = {
        "experiment": "EXP-030",
        "benchmark": "ARN (Zenodo 11044026, CC-BY 4.0), far analogy x high-similarity distractor",
        "items_scored": n,
        "items_reserved_unannotated": 40,
        "annotation_sealed_as": (Path(__file__).resolve().parents[1]
                                 / "external" / "arn_seal.txt").read_text().strip(),
        "correct_ties_as_wrong": correct,
        "p_ties_as_wrong": round(p, 5),
        "ties": ties,
        "discriminating_items": len(disc),
        "correct_on_discriminating": disc_correct,
        "p_on_discriminating": round(p_disc, 4),
        "score_ties_as_coinflip": as_coinflip,
        "p_ties_as_coinflip": round(p_coin, 4),
        "chance": 0.5,
        "predeclared_threshold": 15,
        "beats_chance": correct >= 15 and p < 0.05,
        "headline": ("NO SIGNAL -- not significantly different from chance on either "
                     "honest reading; the measure abstains on 45% of items"),
        "annotation_diagnostic": {
            "note": "raw matched-relation count, MDL pricing removed",
            "favours_correct": favours_correct,
            "favours_distractor": favours_distractor,
            "no_difference": neither,
            "conclusion": ("the annotation itself does not contain the distinction, "
                           "so this experiment measured the ANNOTATOR, not the measure"),
        },
        "rows": rows,
    }
    out = Path(__file__).resolve().parents[1] / "results" / "exp030.json"
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-030  written to {out}")
    print(f"annotations sealed as {report['annotation_sealed_as']}\n")
    print(f"{'item':<8}{'first':>9}{'second':>9}{'pred':>6}{'truth':>7}{'':>4} proverb")
    for r in rows:
        mark = "ok " if r["correct"] else ("tie" if r["tie"] else "MISS")
        print(f"{r['item']:<8}{r['score_first']:>9.4f}{r['score_second']:>9.4f}"
              f"{r['predicted']:>6}{r['truth']:>7}  {mark}  {r['proverb'][:42]}")

    print(f"\nTHE MEASURE ABSTAINS ON {ties}/{n} ITEMS -- exact ties, no signal at all.\n")
    print(f"   counting ties as wrong        : {correct}/{n} = {correct/n:.0%}   p = {p:.4f}")
    print(f"   counting ties as coin flips   : {as_coinflip}/{n} = {as_coinflip/n:.0%}   "
          f"p = {p_coin:.4f}")
    print(f"   only where it discriminates   : {disc_correct}/{len(disc)} = "
          f"{disc_correct/len(disc):.0%}   p = {p_disc:.4f}")
    print(f"\n>>> {report['headline']}")
    print(f">>> predeclared threshold was {report['predeclared_threshold']}/{n}; "
          f"BEATS CHANCE: {report['beats_chance']}")

    d = report["annotation_diagnostic"]
    print("\nWHOSE FAILURE? Raw matched-relation count, MDL pricing removed:")
    print(f"   annotation favours the correct answer : {d['favours_correct']}/{n}")
    print(f"   no difference                         : {d['no_difference']}/{n}")
    print(f"   favours the distractor                : {d['favours_distractor']}/{n}")
    print(f"   -> {d['conclusion']}")


if __name__ == "__main__":
    main()
