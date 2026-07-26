"""Independent world generators for EXP-005.

F-06a was developed against ONE structure family -- the reinforcing-channel
motif in worlds.py -- and validated on conditions derived from it. That is
R-04, flagged since the day the measure was proposed and never discharged:
a measure tested only on the worlds it was built for may have learned those
worlds.

These generators build structurally DIFFERENT base topologies. The derivation
of the condition set from a base (relabel for B, rewire for C, randomise for D)
is deliberately SHARED across generators, so the only thing varying is the
shape of the structure itself. If F-06a learned the feedback motif, it will
show up as failure on shapes that are not feedback motifs.

The families were chosen to differ in the properties that plausibly matter to
a correspondence measure -- cycles, branching, degree concentration, path
multiplicity -- rather than by picking topologies that came to mind. EXP-020
measured what "picking what comes to mind" does to a test set.
"""

from __future__ import annotations

import random

from structure import Structure, build

POS, NEG = "POS", "NEG"


# -- base topologies, structurally distinct ---------------------------------

def gen_motif(rng) -> Structure:
    """The development family: a reinforcing cycle with a suppression edge.
    Included as the known case, so failure elsewhere is legible against it."""
    return build("motif", "dev", [
        ("paths", "advantage", POS), ("advantage", "flow", POS),
        ("flow", "erosion", POS), ("erosion", "capacity", POS),
        ("capacity", "flow", POS), ("capacity", "paths", NEG),
    ])


def gen_chain(rng) -> Structure:
    """A linear causal chain with one branch. No cycles at all -- the property
    the development family was built around is simply absent."""
    return build("chain", "dev", [
        ("source", "stage1", POS), ("stage1", "stage2", POS),
        ("stage2", "stage3", POS), ("stage3", "sink", POS),
        ("stage2", "sink", NEG), ("source", "stage2", POS),
    ])


def gen_hub(rng) -> Structure:
    """A star: one participant connected to everything, the others to nothing
    else. Degree is maximally concentrated -- the opposite of the motif, where
    it is nearly uniform."""
    return build("hub", "dev", [
        ("core", "n1", POS), ("core", "n2", POS), ("core", "n3", NEG),
        ("n1", "core", POS), ("n2", "core", NEG), ("n3", "core", POS),
    ])


def gen_lattice(rng) -> Structure:
    """Parallel paths between the same endpoints -- multiple routes rather
    than one dominant one. Path multiplicity is the distinguishing feature."""
    return build("lattice", "dev", [
        ("inlet", "left", POS), ("inlet", "right", POS),
        ("left", "outlet", POS), ("right", "outlet", POS),
        ("left", "right", NEG), ("outlet", "inlet", NEG),
    ])


def gen_random_dag(rng) -> Structure:
    """A random acyclic structure with a fixed seed. No designed shape at all;
    included so at least one base is not the product of anyone's intent."""
    names = ["v0", "v1", "v2", "v3", "v4"]
    edges, pairs = [], set()
    while len(edges) < 6:
        i = rng.randrange(0, 4)
        j = rng.randrange(i + 1, 5)
        if (i, j) in pairs:                 # no PARALLEL edges: the original
            continue                        # dedup compared full triples, so
        pairs.add((i, j))                   # (v2,v3,NEG) and (v2,v3,POS) both
        edges.append((names[i], names[j],   # passed -- and flipping one made a
                      rng.choice([POS, NEG])))   # duplicate that silently
    return build("random_dag", "dev", sorted(edges))


GENERATORS = {
    "motif (development family)": gen_motif,
    "chain (acyclic)": gen_chain,
    "hub (concentrated degree)": gen_hub,
    "lattice (parallel paths)": gen_lattice,
    "random_dag (unshaped)": gen_random_dag,
}


# -- shared condition derivation --------------------------------------------
# Identical for every generator, so the only variable is the base topology.

def make_B(a: Structure, rng) -> Structure:
    """Same structure, different everything else: new participant names, new
    relation-type names, different declared domain."""
    nm = {v: f"x{i}" for i, v in enumerate(a.nodes)}
    tm = {POS: "GROWS", NEG: "PRUNES"}
    return build("B", "other", [(nm[r.src], nm[r.dst], tm[r.rtype])
                                for r in a.relations])


def make_C(a: Structure, rng) -> Structure:
    """Same surface, different structure: identical names and types, edges
    rewired. Must score LOW or the measure is reading vocabulary."""
    nodes = list(a.nodes)
    types = [r.rtype for r in a.relations]
    edges, seen = [], set()
    r2 = random.Random(99)
    while len(edges) < a.m:
        s, d = r2.sample(nodes, 2)
        if (s, d) in seen:
            continue
        seen.add((s, d))
        edges.append((s, d, types[len(edges)]))
    return build("C", a.domain, edges)


def make_D(a: Structure, rng) -> Structure:
    """Different surface AND different structure, size matched."""
    nodes = [f"z{i}" for i in range(a.n)]
    edges, seen = [], set()
    r3 = random.Random(4242)
    while len(edges) < a.m:
        s, d = r3.sample(nodes, 2)
        if (s, d) in seen:
            continue
        seen.add((s, d))
        edges.append((s, d, r3.choice(["GROWS", "PRUNES"])))
    return build("D", "other", edges)


def make_E(a: Structure, rng) -> Structure:
    """The near-miss: identical to A except ONE relation type flipped.

    Added after the first run of EXP-005, where B, C and D alone made the test
    too easy -- B is a perfect isomorph of matched size, so it compresses to
    essentially the same score on every topology and the question degenerates
    to "can it spot a perfect copy". E asks the harder and more useful thing:
    does the measure rank DEGREES of correspondence correctly on a shape it
    was never developed against? B > E > C, D is the ordering that would mean
    something.
    """
    rels = list(a.relations)
    i = len(rels) // 2
    r = rels[i]
    from dataclasses import replace as _replace
    rels[i] = _replace(r, rtype=NEG if r.rtype == POS else POS)
    return Structure(name="E", nodes=a.nodes, relations=tuple(rels),
                     domain=a.domain)


def conditions_for(name: str, seed: int) -> dict[str, Structure]:
    rng = random.Random(seed)
    a = GENERATORS[name](rng)
    return {"A": a, "B": make_B(a, rng), "C": make_C(a, rng),
            "D": make_D(a, rng), "E": make_E(a, rng)}
