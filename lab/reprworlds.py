"""Q-21 -- equivalent re-encodings of the same process.

Everything the project has shown about invariance concerns VOCABULARY (what the
participants are called) and LABELS (which node is which). Nobody has asked
whether the measure survives a change of REPRESENTATION: the same process
written down a different but equally legitimate way.

That gap matters more than it sounds. If the measure recognises the graph
encoding rather than the relational content, then every cross-domain claim in
this project is really a claim about structures that happen to share MY
modelling conventions -- and the whole thing needs re-scoping before it goes
anywhere near LiDAR, hydraulics or physics, where equivalent realities are
routinely written in very different forms.

TWO CLASSES, DECLARED BEFORE ANYTHING RAN.

CONTENT-PRESERVING -- a competent modeller could hand in either version:
  relabel            rename every participant
  retype             rename every relation type, consistently
  converse           flip every edge and rename each type to its converse
                     (A increases B  ==  B is-increased-by A)
  mediate_one        insert a mediator on one edge: A->B becomes A->M->B
  subdivide_all      insert a mediator on every edge
  reify_one          replace one relation by a node standing for the relation,
                     the factor-node encoding

CONTENT-CHANGING -- these say something different, and the measure SHOULD
notice. They are the controls. Without them "invariant" is unfalsifiable,
because a measure that returns a constant would pass the first class perfectly.
  flip_type_one      one relation's type inverted -- changes the loop's sign
  reverse_one        one edge reversed WITHOUT renaming the type
  rewire_one         one edge moved to a different endpoint
  delete_one         one relation removed

THE TEST is not "does the score stay identical". Re-encoding genuinely changes
the object -- subdividing adds nodes and edges, and an MDL code is right to
charge for them. The honest question is comparative:

    Does an equivalence-preserving re-encoding cost LESS than a genuine
    change of content?

If a mediator node costs more than inverting a causal sign, the measure is
tracking the encoding rather than the process, whatever its absolute numbers.
"""

from __future__ import annotations

from dataclasses import replace

from structure import Relation, Structure

# A subdivision must COMPOSE back to the relation it replaced. Splitting
# "A decreases B" into "A decreases M, M decreases B" says A *increases* B --
# two sign flips cancel. EXP-028 shipped with that error and called the result
# content-preserving; caught by the canonicaliser in EXP-029, ninth instance of
# R-12 and mine again. DECOMPOSE gives a pair whose composition is the original.
from relalgebra import decompose as halves


CONVERSE = {
    "POS": "POS_conv", "POS_conv": "POS", "NEG": "NEG_conv", "NEG_conv": "NEG",
    "increases": "is_increased_by", "is_increased_by": "increases",
    "decreases": "is_decreased_by", "is_decreased_by": "decreases",
    "enables": "is_enabled_by", "is_enabled_by": "enables",
    "inhibits": "is_inhibited_by", "is_inhibited_by": "inhibits",
    "precedes": "follows", "follows": "precedes",
}
INVERSE = {
    "POS": "NEG", "NEG": "POS",
    "increases": "decreases", "decreases": "increases",
    "enables": "inhibits", "inhibits": "enables",
}


def _mk(base: Structure, name: str, nodes, rels) -> Structure:
    return Structure(name=name, nodes=tuple(nodes),
                     relations=tuple(rels), domain=base.domain)


# ---------------------------------------------------------------------------
# content-preserving
# ---------------------------------------------------------------------------

def relabel(s: Structure) -> Structure:
    m = {n: f"z{i}" for i, n in enumerate(s.nodes)}
    return _mk(s, s.name + "+relabel", [m[n] for n in s.nodes],
               [r.relabel(m) for r in s.relations])


def retype(s: Structure) -> Structure:
    m = {t: f"rel{i}" for i, t in enumerate(s.types)}
    return _mk(s, s.name + "+retype", s.nodes,
               [replace(r, rtype=m[r.rtype]) for r in s.relations])


def converse(s: Structure) -> Structure:
    """A increases B  ==  B is-increased-by A. Same claim, opposite encoding."""
    return _mk(s, s.name + "+converse", s.nodes,
               [Relation(r.dst, r.src, CONVERSE.get(r.rtype, r.rtype + "_conv"),
                         r.weight) for r in s.relations])


def mediate_one(s: Structure, idx: int = 0) -> Structure:
    """A -t-> B becomes A -t-> M -t-> B. The mediator carries the same type."""
    r = s.relations[idx]
    med = f"{r.src}_{r.dst}_via"
    t1, t2 = halves(r.rtype)
    rest = [x for i, x in enumerate(s.relations) if i != idx]
    return _mk(s, s.name + "+mediate", list(s.nodes) + [med],
               rest + [Relation(r.src, med, t1, r.weight),
                       Relation(med, r.dst, t2, r.weight)])


def subdivide_all(s: Structure) -> Structure:
    nodes, rels = list(s.nodes), []
    for i, r in enumerate(s.relations):
        med = f"m{i}"
        t1, t2 = halves(r.rtype)
        nodes.append(med)
        rels += [Relation(r.src, med, t1, r.weight),
                 Relation(med, r.dst, t2, r.weight)]
    return _mk(s, s.name + "+subdivide", nodes, rels)


def reify_one(s: Structure, idx: int = 0) -> Structure:
    """The factor-node encoding: the relation becomes a node with a role edge
    in and a role edge out. This is how the same fact gets written when the
    formalism has no typed edges -- an extremely common re-encoding."""
    r = s.relations[idx]
    fac = f"{r.rtype}_node"
    rest = [x for i, x in enumerate(s.relations) if i != idx]
    return _mk(s, s.name + "+reify", list(s.nodes) + [fac],
               rest + [Relation(r.src, fac, "role_source", r.weight),
                       Relation(fac, r.dst, "role_target", r.weight)])


# ---------------------------------------------------------------------------
# content-changing controls
# ---------------------------------------------------------------------------

def flip_type_one(s: Structure, idx: int = 0) -> Structure:
    r = s.relations[idx]
    new = INVERSE.get(r.rtype)
    if new is None:
        # Returning `s` unchanged here would make this control vacuous: it would
        # "pass" by testing nothing. That failure mode is why EXP-019 exists.
        raise KeyError(f"no inverse declared for relation type {r.rtype!r} -- "
                       f"add it to INVERSE rather than letting the control no-op")
    return _mk(s, s.name + "+fliptype", s.nodes,
               [replace(x, rtype=new) if i == idx else x
                for i, x in enumerate(s.relations)])


def reverse_one(s: Structure, idx: int = 0) -> Structure:
    r = s.relations[idx]
    return _mk(s, s.name + "+reverse", s.nodes,
               [Relation(x.dst, x.src, x.rtype, x.weight) if i == idx else x
                for i, x in enumerate(s.relations)])


def rewire_one(s: Structure, idx: int = 0) -> Structure:
    r = s.relations[idx]
    alt = next((n for n in s.nodes if n not in (r.src, r.dst)), None)
    if alt is None:
        raise ValueError("no third node to rewire to -- control would no-op")
    return _mk(s, s.name + "+rewire", s.nodes,
               [replace(x, dst=alt) if i == idx else x
                for i, x in enumerate(s.relations)])


def delete_one(s: Structure, idx: int = 0) -> Structure:
    return _mk(s, s.name + "+delete", s.nodes,
               [x for i, x in enumerate(s.relations) if i != idx])


# Which transforms introduce REPRESENTATIONAL vertices. Declared per transform
# rather than inferred as "nodes that are new", because `relabel` renames every
# node and would look like it introduced all of them -- which is how EXP-029's
# first run blind-canonicalised the relabelled structures and reported the known
# invariance as broken. The declaration is the honest form anyway: whether a
# vertex is an artifact is a statement about the encoding, not a computation.
INTRODUCES_ARTIFACTS = frozenset({"mediate_one", "subdivide_all", "reify_one"})


def artifacts(name: str, before, after) -> frozenset[str]:
    if name not in INTRODUCES_ARTIFACTS:
        return frozenset()
    return frozenset(after.nodes) - frozenset(before.nodes)


def protected_for(name: str, before, after) -> frozenset[str]:
    """Everything that is a real participant of the transformed structure."""
    return frozenset(after.nodes) - artifacts(name, before, after)


PRESERVING = {
    "relabel": relabel, "retype": retype, "converse": converse,
    "mediate_one": mediate_one, "subdivide_all": subdivide_all,
    "reify_one": reify_one,
}
CHANGING = {
    "flip_type_one": flip_type_one, "reverse_one": reverse_one,
    "rewire_one": rewire_one, "delete_one": delete_one,
}
