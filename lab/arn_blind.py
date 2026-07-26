"""ARN benchmark -- the blind-annotation harness.

254 items in exactly this project's design: a query narrative, a cross-domain
analogue, and a surface-similar distractor, with ground truth supplied by
someone else entirely (Zenodo 11044026, CC-BY 4.0). This is the first test in
the project where the answers were not produced by anyone involved in it.

WHY A HARNESS AND NOT JUST "DON'T LOOK".

Hiding `correct_answer` is the obvious blind and it is not sufficient. The real
hazard is subtler: if I annotate a candidate while looking at the query, I will
shape its structure toward the query without deciding to. That is not
label-peeking, it is the ordinary pull of having the target in view, and no
amount of good intent removes it -- EXP-026 exists because that class of bias
had never been tested.

So the blind here is stronger than the labels:

  1. Every narrative is annotated ALONE, and its ROLE is hidden -- while
     annotating I cannot tell whether a passage is a query, an analogue or a
     distractor.
  2. Passages are ordered in item-contiguous blocks of three with the roles
     shuffled INSIDE each block. Blocks are shuffled too. This is a deliberate
     weakening of a first design that shuffled all 180 passages flat: that hid
     item membership as well, but then annotating a prefix of the pool would
     have completed only about two whole items out of sixty. Item membership
     carries no information about role or answer, so hiding it bought nothing
     and cost the ability to stage the work.
  3. `correct_answer` is not readable until the annotations are committed and
     hashed.

`reveal()` refuses to run until the annotation file exists and its hash is
recorded, so the ordering is enforced by the code rather than by my memory of
having intended it.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "external" / "arn.csv"
POOL = ROOT / "external" / "arn_pool.json"          # blind: passages only
KEY = ROOT / "external" / "arn_key.json"            # sealed: roles + answers
ANNOT = ROOT / "external" / "arn_annotations.json"  # what I produce, blind

SEED = 20260726
N_ITEMS = 60


def hard_cell() -> list[dict]:
    rows = list(csv.DictReader(RAW.open()))
    return [r for r in rows
            if r["analogy_level"] == "far" and r["distractor_similarity"] == "high"]


def build(n: int = N_ITEMS) -> dict:
    """Split the benchmark into a blind pool and a sealed key."""
    items = hard_cell()
    rng = random.Random(SEED)
    chosen = rng.sample(items, n)

    blocks, key = [], []
    for it in chosen:
        iid = it["id"]
        passages = [("Q", it["query_narrative"]),
                    ("A", it["first_choice"]),
                    ("B", it["second_choice"])]
        rng.shuffle(passages)          # role order inside the block is scrambled
        block = []
        for role, text in passages:
            pid = hashlib.sha256(f"{iid}:{role}:{SEED}".encode()).hexdigest()[:16]
            block.append({"passage_id": pid, "text": text.strip()})
            key.append({"passage_id": pid, "item_id": iid, "role": role})
        key.append({"item_id": iid, "correct_answer": it["correct_answer"],
                    "proverb": it["proverb"]})
        blocks.append(block)

    rng.shuffle(blocks)                # block order carries nothing either
    pool = [pg for b in blocks for pg in b]
    POOL.write_text(json.dumps({"seed": SEED, "n_items": n,
                                "passages": pool}, indent=2))
    KEY.write_text(json.dumps({"seed": SEED, "key": key}, indent=2))
    return {"passages": len(pool), "items": n}


def load_pool() -> list[dict]:
    return json.loads(POOL.read_text())["passages"]


def annotation_hash() -> str:
    return hashlib.sha256(ANNOT.read_bytes()).hexdigest()[:16]


def reveal() -> dict:
    """Unseal the key. Refuses until annotations are committed."""
    if not ANNOT.exists():
        raise RuntimeError(
            "annotations not committed -- reveal() would let the labels inform "
            "the annotation, which is the whole thing this harness prevents")
    seal = ROOT / "external" / "arn_seal.txt"
    h = annotation_hash()
    if not seal.exists():
        seal.write_text(h)
    elif seal.read_text().strip() != h:
        raise RuntimeError(
            f"annotations changed after sealing: sealed {seal.read_text().strip()}, "
            f"now {h}. Re-annotating after seeing labels is not a blind test.")
    return json.loads(KEY.read_text())


if __name__ == "__main__":
    print(build())
