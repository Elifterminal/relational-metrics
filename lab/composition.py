"""F-14 -- path and cycle sign by typed composition.

Q-12 says every measure we have is blind to whether a difference MATTERS.
The candidate answer: significance may already be present in the structure,
recoverable by COMPOSING relation signs along paths, and the measures simply
never composed anything.

Polarity is declared as a property of a relation TYPE, alongside the
vocabulary that defines the type. That is legitimate -- it is part of what a
typed relation is (C-11). What would be cheating is declaring which specific
edge is important, and nothing here does that.
"""

from __future__ import annotations

from collections import Counter

from structure import Structure

# Declared with the vocabularies, not with the experiment.
POLARITY: dict[str, int] = {
    "POS": +1, "NEG": -1,              # geomorphology
    "GROWS": +1, "PRUNES": -1,         # vascular
    "FAVOURS": +1, "STARVES": -1,      # traffic
}


def simple_cycles(struct: Structure, max_len: int = 8) -> list[list[tuple[str, str, str]]]:
    """Every simple directed cycle, each reported once.

    Canonicalised by rotating so the lexicographically smallest node starts,
    so the same cycle found from different entry points counts once.
    """
    adj: dict[str, list[tuple[str, str, str]]] = {v: [] for v in struct.nodes}
    for r in struct.relations:
        adj.setdefault(r.src, []).append((r.src, r.dst, r.rtype))

    found: dict[tuple, list] = {}

    def walk(start: str, node: str, path: list, seen: set) -> None:
        if len(path) > max_len:
            return
        for edge in adj.get(node, []):
            nxt = edge[1]
            if nxt == start and path:
                cycle = path + [edge]
                key = tuple(sorted((e[0], e[1], e[2]) for e in cycle))
                found.setdefault(key, cycle)
            elif nxt not in seen and nxt > start:
                walk(start, nxt, path + [edge], seen | {nxt})

    for v in struct.nodes:
        walk(v, v, [], {v})
    return list(found.values())


def cycle_signature(struct: Structure, max_len: int = 8) -> Counter:
    """Multiset of (cycle length, composed sign).

    The sign of a cycle is the product of its edge polarities. A positive
    cycle reinforces -- it runs away. A negative cycle self-limits.
    This is the one crude behavioural fact composition buys us. It is not a
    behavioural model: magnitudes, delays and thresholds all change what a
    system does and none of them appear here.
    """
    sig: Counter = Counter()
    for cycle in simple_cycles(struct, max_len):
        sign = 1
        for _, _, rtype in cycle:
            sign *= POLARITY.get(rtype, +1)
        sig[(len(cycle), sign)] += 1
    return sig


def signature_divergence(a: Structure, b: Structure, max_len: int = 8) -> int:
    """Multiset symmetric difference between two cycle signatures.

    0 means the two structures agree about every reinforcing and
    self-limiting loop they contain. Works across vocabularies because
    polarity travels with the relation type, not with the label.
    """
    sa, sb = cycle_signature(a, max_len), cycle_signature(b, max_len)
    keys = set(sa) | set(sb)
    return sum(abs(sa.get(k, 0) - sb.get(k, 0)) for k in keys)
