"""Search over candidate mappings between two structures.

Exhaustive. NP-hard in general (a known objection to F-06), but these
structures are deliberately tiny -- we are testing whether a *criterion*
behaves, not whether a search scales. Using an approximate search here would
confound the criterion's behaviour with the search's behaviour, which is
exactly the kind of muddle the protocol exists to prevent.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product
from typing import Iterator

from structure import Structure


@dataclass(frozen=True)
class Mapping:
    """A candidate correspondence: which node goes to which, and which
    relation type stands in for which."""

    nodes: tuple[tuple[str, str], ...]      # (src_node, dst_node) pairs
    types: tuple[tuple[str, str], ...]      # (src_type, dst_type) pairs

    @property
    def node_map(self) -> dict[str, str]:
        return dict(self.nodes)

    @property
    def type_map(self) -> dict[str, str]:
        return dict(self.types)

    @property
    def k(self) -> int:
        return len(self.nodes)

    @property
    def n_substitutions(self) -> int:
        """Type pairs where the type actually had to change. A same-type
        mapping is free; a translation costs."""
        return sum(1 for a, b in self.types if a != b)

    def predicted_edges(self, source: Structure) -> frozenset[tuple[str, str, str]]:
        nm, tm = self.node_map, self.type_map
        out = set()
        for r in source.relations:
            if r.src in nm and r.dst in nm and r.rtype in tm:
                out.add((nm[r.src], nm[r.dst], tm[r.rtype]))
        return frozenset(out)


def enumerate_mappings(a: Structure, b: Structure,
                       total_only: bool = True) -> Iterator[Mapping]:
    """All node injections from `a` into `b`, crossed with all relation-type
    substitutions.

    `total_only` restricts to mappings covering every node of `a`. Partial
    mappings are where a permissive search finds contrived correspondences,
    so they matter to the theory -- but for equal-sized structures the total
    maps are the honest comparison and keep the enumeration finite.
    """
    a_nodes, b_nodes = a.nodes, b.nodes
    if total_only and len(a_nodes) > len(b_nodes):
        return

    a_types, b_types = a.types, b.types
    type_options = list(product(b_types, repeat=len(a_types)))

    for target in permutations(b_nodes, len(a_nodes)):
        node_pairs = tuple(zip(a_nodes, target))
        for combo in type_options:
            yield Mapping(nodes=node_pairs,
                          types=tuple(zip(a_types, combo)))


def count_mappings(a: Structure, b: Structure) -> int:
    from math import factorial
    n1, n2 = a.n, b.n
    if n1 > n2:
        return 0
    perms = factorial(n2) // factorial(n2 - n1)
    return perms * (len(b.types) ** len(a.types))
