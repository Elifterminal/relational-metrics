"""Q-24 -- quotient out representational vertices before measuring.

EXP-028 found the correspondence measure blind across equivalent re-encodings.
The standard name for the invariance wanted here is GRAPH HOMEOMORPHISM --
equivalence under subdivision and suppression of degree-2 vertices. The
asymmetric containment version is the topological minor; the edge-to-path
matching version is subgraph homeomorphism (LaPaugh & Rivest, JCSS 20, 1980).

DESIGN DECISION, and it is the whole point: canonicalise BEFORE measuring
rather than widening the search. EXP-028 showed that freedom in the alignment
space is what destroyed discrimination, so answering it by enlarging that space
would be treating the symptom with more of the cause. The invariance belongs to
the definition of the measured object, not to something the maximiser is meant
to stumble on.

WHY NOT "CONTRACT EVERY SAME-TYPED CHAIN". That rule is too broad, and it was
my first plan. A degree-2 vertex is not semantically meaningless merely because
graph theory permits its suppression -- it may be a real participant that
happens to sit in the middle. Suppression is therefore GUARDED by a declared
partial algebra on relation types, and contracts only where composition is
declared:

    COMPOSE[(t1, t2)] -> t   or undefined

For the sign vocabulary this is polarity multiplication, which the project
already declared for F-14 -- so the algebra is inherited, not invented here.

GUARDS, each one a named edge case:
  * in-degree 1 and out-degree 1, counting ALL incident relations
  * no self-loop on the vertex
  * contraction must not create a self-loop (u == v)
  * contraction must not create a duplicate relation (the container invariant
    from EXP-005 -- parallel edges silently collapse in a frozenset)
  * COMPOSE must be declared for the incident type pair
  * the vertex must not be PROTECTED (see below)

THE HONEST LIMIT, and it is the same shape as EXP-027's. Whether a vertex is a
representational artifact or a genuine participant is NOT decidable from the
structure. A pure directed cycle has in-degree 1 and out-degree 1 at every
vertex; blind suppression eats the entire cycle. So this module offers two
modes, and the difference between them is a declaration, not a computation:

  declared mode  -- `protected` names the real participants. Invariance holds
                    with respect to a DECLARED homeomorphism relation.
  blind mode     -- suppress anything suppressible, with a floor to keep the
                    rewrite terminating. Included to MEASURE the damage, not
                    because it is recommended.
"""

from __future__ import annotations

from relalgebra import compose
from structure import Relation, Structure

# Inherited from F-14's declared polarity, not invented for this experiment.
# Composition of signs is multiplication; anything not listed is UNDEFINED and
# therefore blocks contraction rather than guessing.

MIN_NODES = 2   # floor for blind mode, so a cycle cannot be eaten to nothing


def _incident(s: Structure, v: str):
    ins = [r for r in s.relations if r.dst == v]
    outs = [r for r in s.relations if r.src == v]
    return ins, outs


def suppressible(s: Structure, v: str, protected: frozenset[str]) -> Relation | None:
    """The composed relation if v may be suppressed, else None.

    Every guard here is a named failure mode, not defensive padding.
    """
    if v in protected:
        return None
    ins, outs = _incident(s, v)
    if len(ins) != 1 or len(outs) != 1:
        return None
    a, b = ins[0], outs[0]
    if a.src == v or b.dst == v:            # self-loop on v
        return None
    if a.src == b.dst:                       # would create a self-loop
        return None
    t = compose(a.rtype, b.rtype)
    if t is None:                            # composition not declared
        return None
    new = Relation(a.src, b.dst, t, min(a.weight, b.weight))
    if (new.src, new.dst, new.rtype) in s.edge_set():
        return None                          # would create a parallel edge
    return new


def canonical(s: Structure, protected: frozenset[str] | None = None,
              order: list[str] | None = None) -> Structure:
    """Suppress until no vertex qualifies. Deterministic given `order`.

    `order` exists so confluence can be TESTED rather than assumed: run the
    rewrite under many orders and compare normal forms.
    """
    if protected is None:
        protected = frozenset()
    nodes = list(s.nodes)
    rels = list(s.relations)
    cur = Structure(s.name, tuple(nodes), tuple(rels), s.domain)

    changed = True
    while changed:
        changed = False
        cand = order if order is not None else sorted(cur.nodes)
        for v in cand:
            if v not in cur.nodes or len(cur.nodes) <= MIN_NODES:
                continue
            new = suppressible(cur, v, protected)
            if new is None:
                continue
            keep = [r for r in cur.relations if r.src != v and r.dst != v]
            cur = Structure(cur.name, tuple(n for n in cur.nodes if n != v),
                            tuple(keep + [new]), cur.domain)
            changed = True
            break
    return Structure(s.name + "|canon", cur.nodes, cur.relations, s.domain)
