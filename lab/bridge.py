"""F-09 -- bridge value: correspondence discounted by genericness.

Sketched on day one as the defence against R-01, never built, and R-01 duly
fired in EXP-026: a deliberately vacuous document -- "a growing deviation
produces a stronger control signal, increasing corrective action and a
counteracting effect" -- is STRUCTURALLY ISOMORPHIC to a real query and
outranks the genuine cross-domain analogue. The correspondence measure is not
wrong about it. A vacuous statement can have perfect structure, because it
describes nothing else.

So genericness cannot be found inside the correspondence. It has to come from
somewhere else, and the day-one sketch never said where.

WHAT GENERICNESS IS, OPERATIONALLY. A generic thing is one that matches
EVERYTHING. That is not a property of the pair (query, document) at all -- it
is a property of the document against a background. Which makes it measurable
with machinery that already exists:

    genericness(D)  =  how well D corresponds to structures in general
    bridge(Q, D)    =  correspondence(Q, D)  -  genericness(D)

Read: how much better does D match THIS query than it matches things at large.
A vacuous document scores well against everything, so the subtraction removes
most of its score. A specific document scores well against its analogues and
poorly against the rest, so the subtraction leaves it nearly intact.

THIS IS THE SAME MOVE AS THE OUTCOME CALIBRATION IN F-04a, and that is a
reason to trust it rather than a coincidence. EXP-012 found that the raw
higher-order statistic reports structure that is real and irrelevant, and that
the observer enters through a CALIBRATION rather than through the statistic.
Genericness is the same shape of problem -- a real correspondence that answers
nothing -- and it takes the same shape of fix. The background sample is where
"compared to what?" enters the mathematics.

WHAT THIS DOES NOT DO. It does not make the measure understand meaning. A
document that is specific but wrong is still not detected. It removes
promiscuity, not falsehood.
"""

from __future__ import annotations

from dataclasses import dataclass

from codes import DEFAULT_CODE
from measures import mdl_correspondence
from structure import Structure


@dataclass(frozen=True)
class Bridge:
    raw: float            # correspondence(Q, D)
    genericness: float    # mean correspondence of D against the background
    bridge: float         # raw - genericness
    n_background: int

    def as_dict(self) -> dict:
        return {"raw": round(self.raw, 4),
                "genericness": round(self.genericness, 4),
                "bridge": round(self.bridge, 4)}


def genericness(doc: Structure, background: list[Structure]) -> float:
    """How well this structure corresponds to structures in general.

    The background must NOT contain the query or its candidate set, or the
    quantity being subtracted would include the very comparison being scored.
    """
    if not background:
        return 0.0
    return sum(mdl_correspondence(b, doc, DEFAULT_CODE).ratio
               for b in background) / len(background)


def bridge_value(query: Structure, doc: Structure,
                 background: list[Structure]) -> Bridge:
    raw = mdl_correspondence(query, doc, DEFAULT_CODE).ratio
    g = genericness(doc, background)
    return Bridge(raw=raw, genericness=g, bridge=raw - g,
                  n_background=len(background))
