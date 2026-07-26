"""Her time-warp, our structural correspondence as the ground.

The composition her A2 invites: grounds are pluggable, so plug ours in. A system
becomes a SEQUENCE of typed structures, one per timestep, and two systems are
compared by aligning them in time and summing a structural distance at aligned
moments.

Uses her A1 -- minimise the TOTAL aligned cost, then divide by the optimising
path's length. NOT her A1b (min-mean), which she retired because the path length
in the denominator makes it gameable by padding; verified independently before
using anything of hers.

The ground is our correspondence in the metric form produced by applying her B9
debiasing and B4 symmetrisation:

    d(a,b) = ½[raw(a,b) + raw(b,a)] − ½raw(a,a) − ½raw(b,b)

which satisfies all four metric axioms on random and real structures. Her v2
theorems require a metric base; this is what makes ours eligible.
"""

from __future__ import annotations

from codes import DEFAULT_CODE
from measures import mdl_correspondence
from structure import Structure

_CACHE: dict = {}


def _key(s: Structure):
    """Content key, NOT id().

    The first version of this cache keyed on (id(a), id(b)). Python reuses ids
    after garbage collection, so transient structures collided and the cache
    returned one structure's distance for another's -- visible as a control that
    gave three different answers for the same pair of structures. Caught by the
    control being impossible rather than merely wrong, which is the argument for
    having one.
    """
    return (s.n, s.m, tuple(sorted(s.edge_set())),
            tuple(round(r.weight, 12) for r in s.relations))


def _raw(a: Structure, b: Structure) -> float:
    key = (_key(a), _key(b))
    if key not in _CACHE:
        r = mdl_correspondence(a, b, DEFAULT_CODE)
        _CACHE[key] = r.mapping_bits + r.conditional_bits
    return _CACHE[key]


def ground(a: Structure, b: Structure) -> float:
    """Our correspondence, made a metric by her two corrections."""
    return 0.5 * (_raw(a, b) + _raw(b, a)) - 0.5 * _raw(a, a) - 0.5 * _raw(b, b)


def warped(A: list[Structure], B: list[Structure], band: int | None = None) -> float:
    """Her A1: min TOTAL aligned ground cost over monotone alignments in a
    Sakoe-Chiba band, divided by the optimising path's length."""
    n, m = len(A), len(B)
    if n == 0 or m == 0:
        return float("inf")
    if band is None:
        band = max(n, m)
    INF = float("inf")
    # (total cost, path length) carried together so the division happens after
    best = [[(INF, 0)] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            if abs(i - j) > band:
                continue
            c = ground(A[i], B[j])
            if i == 0 and j == 0:
                best[i][j] = (c, 1)
                continue
            cands = []
            for di, dj in ((1, 0), (0, 1), (1, 1)):
                pi, pj = i - di, j - dj
                if 0 <= pi < n and 0 <= pj < m and best[pi][pj][0] < INF:
                    t, L = best[pi][pj]
                    cands.append((t + c, L + 1))
            if cands:
                best[i][j] = min(cands, key=lambda x: x[0])
    tot, L = best[n - 1][m - 1]
    return tot / L if L else INF


def rigid(A: list[Structure], B: list[Structure]) -> float:
    """No warp -- compare timestep i against timestep i. The control that tests
    whether the WARP earns its keep, as opposed to merely having a sequence.
    Her own summary says the ground is the transferable win, not the warp."""
    k = min(len(A), len(B))
    if k == 0:
        return float("inf")
    return sum(ground(A[i], B[i]) for i in range(k)) / k


def static(A: list[Structure], B: list[Structure]) -> float:
    """Our measure on the final structure alone -- the EXP-031 baseline that
    provably cannot see delay."""
    return ground(A[-1], B[-1])
