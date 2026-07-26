"""Q-26 -- re-annotate an existing corpus BLIND, and see whether the result holds.

R-18: every corpus result in this project rests on hand annotation performed
KNOWING each document's designated role. EXP-026 cleared my ground-truth
ORDERING of bias; it never tested whether the STRUCTURAL ANNOTATION encodes the
role. If it does, F-06a has been reading back what annotation put in.

THE CONTAMINATION, STATED UP FRONT because it decides how the result may be read.
I have already annotated these documents sighted. Shuffling and stripping the
labels hides the roles, but it cannot erase my memory of the corpus. So this is
not a clean blind annotation and cannot be reported as one.

WHICH MAKES STRUCTURAL DIVERGENCE THE INTERPRETIVE KEY, not a side statistic:

  blind structures DIFFER from sighted AND the ranking survives
      -> strong. Different annotations, same answer, so the signal is in the
         text rather than in one particular annotation. R-18 weakened.
  blind structures NEARLY IDENTICAL to sighted
      -> UNINFORMATIVE. Consistent with "annotation is reproducible" and with
         "I remembered the corpus", and this experiment cannot separate them.
  blind structures DIFFER AND the ranking collapses
      -> R-18 fires. The corpus record measured annotation fidelity.

So divergence must be MEASURED and reported before the ranking is looked at,
and the ranking is only interpretable in the light of it. A result that comes
out identical is a null result here, not a confirmation.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "external" / "q26_pool.json"
KEY = ROOT / "external" / "q26_key.json"

SEED = 26260726


def build() -> dict:
    sys.path.insert(0, str(Path(__file__).parent))
    from corpus_independent import INDEPENDENT

    rng = random.Random(SEED)
    pool, key = [], []
    for d in INDEPENDENT:
        pid = hashlib.sha256(f"{d.doc_id}:{SEED}".encode()).hexdigest()[:12]
        pool.append({"passage_id": pid, "gloss": d.gloss})
        key.append({"passage_id": pid, "doc_id": d.doc_id,
                    "motif": d.motif, "kind": d.kind,
                    "sighted": sorted(tuple(e) for e in d.structure.edge_set())})
    rng.shuffle(pool)
    POOL.write_text(json.dumps({"seed": SEED, "passages": pool}, indent=2))
    KEY.write_text(json.dumps({"seed": SEED, "key": key}, indent=2))
    return {"passages": len(pool)}


def load_pool():
    return json.loads(POOL.read_text())["passages"]


def load_key():
    return json.loads(KEY.read_text())["key"]


if __name__ == "__main__":
    print(build())
