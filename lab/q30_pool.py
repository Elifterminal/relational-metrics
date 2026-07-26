"""Q-30 -- blind re-annotation of the dev and held-out corpora.

EXP-032 did this for the independent corpus: the ordering survived (3/4) but
sighted annotation inflated correspondence 1.34x. One corpus at n=4 is thin
evidence for restating a claim, so this repeats it on the other two.

Both corpora are pooled and shuffled TOGETHER, so while annotating I cannot tell
which corpus a gloss came from, let alone its motif or role. That is a slightly
stronger blind than EXP-032 had.

The contamination caveat carries over unchanged and must be restated wherever
this is reported: I annotated both of these sighted. Divergence is measured
first and decides whether the ranking means anything.
"""

from __future__ import annotations

import re

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "external" / "q30_pool.json"
KEY = ROOT / "external" / "q30_key.json"
SEED = 30300726

# The glosses in these two corpora ANNOUNCE THE ROLE IN THE PROSE. Six of the
# thirty-six begin "Same words, opposite wiring:", "Same words, no reset:" and
# so on -- and those six are exactly the false-friend documents, which is the
# precise comparison Q-30 tests. Annotating from the raw glosses would not have
# been blind at all for the documents that matter most.
#
# This is worth more than the inconvenience. The false friends were WRITTEN with
# their role stated in the text, not merely annotated by someone who knew it. So
# R-18's concern reaches one stage further back than EXP-032 tested: into the
# corpus prose itself.
#
# The prefix is stripped so the rest of the sentence -- the actual content -- is
# what gets annotated. Recorded, not silently cleaned.
_TELL = re.compile(r"^Same words,[^:]*:\s*", re.I)


def strip_tell(gloss: str) -> tuple[str, bool]:
    stripped = _TELL.sub("", gloss)
    return stripped, stripped != gloss


def build() -> dict:
    sys.path.insert(0, str(Path(__file__).parent))
    from corpus import DOCS
    from corpus_holdout import HOLDOUT

    rng = random.Random(SEED)
    pool, key = [], []
    for corpus_name, coll in (("dev", DOCS), ("holdout", HOLDOUT)):
        for d in coll:
            pid = hashlib.sha256(f"{corpus_name}:{d.doc_id}:{SEED}".encode()).hexdigest()[:12]
            text, had_tell = strip_tell(d.gloss)
            pool.append({"passage_id": pid, "gloss": text})
            key.append({"passage_id": pid, "corpus": corpus_name,
                        "doc_id": d.doc_id, "motif": d.motif, "kind": d.kind,
                        "gloss_announced_role": had_tell, "original_gloss": d.gloss,
                        "sighted": sorted(tuple(e) for e in d.structure.edge_set())})
    rng.shuffle(pool)
    POOL.write_text(json.dumps({"seed": SEED, "passages": pool}, indent=2))
    KEY.write_text(json.dumps({"seed": SEED, "key": key}, indent=2))
    return {"passages": len(pool),
            "glosses_that_announced_their_role": sum(
                1 for k in key if k["gloss_announced_role"]),
            "and_their_kinds": sorted({k["kind"] for k in key
                                       if k["gloss_announced_role"]})}


def load_pool():
    return json.loads(POOL.read_text())["passages"]


def load_key():
    return json.loads(KEY.read_text())["key"]


if __name__ == "__main__":
    print(build())
