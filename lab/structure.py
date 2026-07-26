"""Immutable typed relational structures.

Scope note (EXP-000a): binary directed typed relations only. Higher arity is
the point of the theory but not of this experiment, and pretending otherwise
would make the code look more general than the result.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable


@dataclass(frozen=True)
class Relation:
    """One typed, directed, weighted relation between two participants."""

    src: str
    dst: str
    rtype: str
    weight: float = 1.0

    def relabel(self, mapping: dict[str, str]) -> "Relation":
        return replace(self, src=mapping.get(self.src, self.src),
                       dst=mapping.get(self.dst, self.dst))


@dataclass(frozen=True)
class Structure:
    """A relational configuration.

    `domain` tags each node with its surface vocabulary. It is deliberately
    NOT part of the structure — it exists so we can measure what a penalty
    charges for cross-vocabulary translation, which is the whole point of
    EXP-000a.
    """

    name: str
    nodes: tuple[str, ...]
    relations: tuple[Relation, ...]
    domain: str = "generic"

    # -- basic accessors -------------------------------------------------

    @property
    def n(self) -> int:
        return len(self.nodes)

    @property
    def m(self) -> int:
        return len(self.relations)

    @property
    def types(self) -> tuple[str, ...]:
        return tuple(sorted({r.rtype for r in self.relations}))

    def edge_set(self) -> frozenset[tuple[str, str, str]]:
        return frozenset((r.src, r.dst, r.rtype) for r in self.relations)

    @property
    def is_well_formed(self) -> bool:
        """`m` must equal the number of DISTINCT relations.

        edge_set() is a frozenset, so two identical (src, dst, type) triples
        collapse into one and the structure silently has fewer relations than
        it reports. EXP-005 hit exactly this: a generator emitted parallel
        edges differing only in type, a near-miss flipped one of them into a
        duplicate, and the collapsed structure scored ABOVE a perfect isomorph
        because it had become cheaper to describe.

        Nothing checked this for twenty-three experiments. It never fired
        because every earlier world was hand-built without parallel edges --
        which is the condition-set blindness R-11 describes, arriving in the
        container rather than in a measure.
        """
        return len(self.edge_set()) == self.m

    def index(self) -> dict[str, int]:
        """Canonical node indexing. Used by the codes so that node *labels*
        never enter a description length — that is what makes the measure
        label-invariant by construction (P-08)."""
        return {name: i for i, name in enumerate(self.nodes)}

    # -- representation-preserving transforms (the F-07 battery) ---------

    def relabel(self, mapping: dict[str, str]) -> "Structure":
        """Rename participants. Structure preserved exactly."""
        return Structure(
            name=f"{self.name}~relabel",
            nodes=tuple(mapping.get(v, v) for v in self.nodes),
            relations=tuple(r.relabel(mapping) for r in self.relations),
            domain=self.domain,
        )

    def reorder(self, order: Iterable[int]) -> "Structure":
        """Permute node listing order. Nothing structural changes."""
        order = tuple(order)
        return Structure(
            name=f"{self.name}~reorder",
            nodes=tuple(self.nodes[i] for i in order),
            relations=self.relations,
            domain=self.domain,
        )

    def reserialize(self, order: Iterable[int]) -> "Structure":
        """Permute relation listing order. Nothing structural changes."""
        order = tuple(order)
        return Structure(
            name=f"{self.name}~reserialize",
            nodes=self.nodes,
            relations=tuple(self.relations[i] for i in order),
            domain=self.domain,
        )

    def rescale(self, factor: float) -> "Structure":
        """Multiply every weight by a constant. A unit conversion."""
        return Structure(
            name=f"{self.name}~rescale",
            nodes=self.nodes,
            relations=tuple(replace(r, weight=r.weight * factor)
                            for r in self.relations),
            domain=self.domain,
        )


def build(name: str, domain: str, edges: list[tuple[str, str, str]]) -> Structure:
    """Convenience builder. Node set is inferred from the edges, in first-seen
    order, so construction order is the only thing that fixes the indexing."""
    nodes: list[str] = []
    for src, dst, _ in edges:
        for v in (src, dst):
            if v not in nodes:
                nodes.append(v)
    return Structure(
        name=name,
        nodes=tuple(nodes),
        relations=tuple(Relation(s, d, t) for s, d, t in edges),
        domain=domain,
    )
