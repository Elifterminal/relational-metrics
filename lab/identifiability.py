"""Representation-relative non-identifiability, as a test you run BEFORE building.

This project hit the same wall twice, from unrelated directions, and named it
twice as a surprise:

  EXP-027  a vacuous document isomorphic to the query cannot be separated from
           a genuine analogue by any function of structure alone
  EXP-029  whether a vertex is a real participant or an inserted mediator is not
           determined by the structure

Both are one thing. The name for it is REPRESENTATION-RELATIVE
NON-IDENTIFIABILITY, and the statement is a factorisation condition:

    let  r : X -> R      be the representation (text/world -> typed structure)
    let  x ~ y           iff  r(x) is isomorphic to r(y)
    let  f : X -> Y      be the distinction you want

    f is recoverable from structure alone  <=>  f is constant on every ~ class
    equivalently, f = f_bar o q  for some f_bar on the quotient

A single WITNESS PAIR -- two items whose structures are isomorphic but whose
required answers differ -- proves no measure on that representation can work.
Not "has not worked yet". Cannot.

WHAT THIS CORRECTS IN MY OWN WRITING. I had been concluding that similarity is
not definable on the quotient by isomorphism. That is wrong, and the error
matters: EVERY purely structural similarity is naturally a function on that
quotient -- that is what makes it structural. What is not definable there is any
distinction that VARIES INSIDE an isomorphism class. So the fix is not to
abandon quotienting and keep raw encodings, which would drag node names and
other irrelevant artifacts back in. The fix is to REFINE the represented object:

    (G, ontology_roles, referents, specificity, provenance, evidence, context)

and then quotient that. Related term in database theory: GENERICITY -- a query
must commute with isomorphisms (Chandra & Harel, JCSS 21, 1980, 156-178).

THREE LEVELS, which this project had been running together:
  1 representation equivalence -- the encoded structures ARE isomorphic.
    No isomorphism-invariant method can separate them. Both of my cases.
  2 logical equivalence -- structures differ, the chosen logic cannot see it.
  3 algorithmic equivalence -- a stronger procedure could see it; k-WL cannot
    (Cai, Furer & Immerman, Combinatorica 12(4), 1992, 389-410).
Levels 2 and 3 are limits of a chosen observer. Level 1 is absence from the
representation, and no observer fixes it.

NOT the Ugly Duckling theorem, though it is a cousin. Watanabe says similarity
needs predicate weighting because all predicates counted equally makes every
pair equally similar. That is about which available distinction matters. This is
about a distinction not being available at all. Weighting cannot help when both
cases occupy the same point.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

from codes import weight_levels
from structure import Structure


def isomorphic(a: Structure, b: Structure) -> bool:
    """Exhaustive. Small structures only, which is what witness pairs are.

    MUST reflect everything the representation actually carries, or the audit
    gives wrong verdicts. Q-28 put relation weights into the comparison, and
    this test still compared edge_set() -- which drops them -- so it declared
    weight-distinguishable pairs non-identifiable while the measure was busy
    distinguishing them. Caught in EXP-034.

    Weights enter as their normalised LEVELS, not raw values, so a unit
    conversion is still correctly treated as the same structure.
    """
    if len(a.nodes) != len(b.nodes) or a.m != b.m:
        return False
    la = weight_levels(tuple(r.weight for r in a.relations))
    lb = weight_levels(tuple(r.weight for r in b.relations))
    ea = {(r.src, r.dst, r.rtype): lv for r, lv in zip(a.relations, la)}
    eb = {(r.src, r.dst, r.rtype): lv for r, lv in zip(b.relations, lb)}
    na, nb = sorted(a.nodes), sorted(b.nodes)
    for f in (dict(zip(na, p)) for p in itertools.permutations(nb)):
        if {(f[x], f[y], t): v for (x, y, t), v in ea.items()} == eb:
            return True
    return False


@dataclass(frozen=True)
class Audit:
    distinction: str
    identifiable: bool
    witness_a: str
    witness_b: str
    structures_equivalent: bool
    answers_differ: bool
    required_channel: str
    note: str = ""

    def as_dict(self) -> dict:
        return {"distinction": self.distinction,
                "identifiable_from_structure": self.identifiable,
                "witness": [self.witness_a, self.witness_b],
                "structures_equivalent": self.structures_equivalent,
                "answers_differ": self.answers_differ,
                "required_channel": self.required_channel,
                "note": self.note}


def audit(distinction: str, a: Structure, b: Structure,
          answer_a, answer_b, required_channel: str, note: str = "") -> Audit:
    """Run the boundary test on one desired distinction.

    NOT identifiable exactly when the structures are equivalent and the required
    answers differ. If the structures differ, this witness pair proves nothing
    either way -- it is not evidence FOR identifiability, only a failed attempt
    to refute it, and the verdict says so.
    """
    equiv = isomorphic(a, b)
    differ = answer_a != answer_b
    return Audit(distinction=distinction,
                 identifiable=not (equiv and differ),
                 witness_a=a.name, witness_b=b.name,
                 structures_equivalent=equiv, answers_differ=differ,
                 required_channel=required_channel,
                 note=note or ("witness pair refutes identifiability"
                               if equiv and differ else
                               "this witness pair does not refute it; "
                               "absence of a witness is not a proof"))
