"""Deliberately cheating methods.

Protocol section 6: before the laboratory is trusted to evaluate a real
measure, it must demonstrate it can catch a fake one. Each method below
produces a number that looks like a correspondence score and is computed from
something that is not correspondence.

Every one of these is a shortcut a real implementation could take by accident.
That is the point -- they are not strawmen, they are the failure modes.
"""

from __future__ import annotations

from collections import Counter
from typing import Callable

from codes import DEFAULT_CODE
from measures import mdl_correspondence, tunable_K
from structure import Structure

Method = Callable[[Structure, Structure], float]


# -- the impostors ----------------------------------------------------------

def name_reader(a: Structure, b: Structure) -> float:
    """Jaccard overlap of node LABELS. Reads vocabulary, calls it structure."""
    sa, sb = set(a.nodes), set(b.nodes)
    return len(sa & sb) / len(sa | sb) if (sa | sb) else 0.0


def size_matcher(a: Structure, b: Structure) -> float:
    """Similarity of node and edge counts. Nothing else."""
    dn = 1.0 - abs(a.n - b.n) / max(a.n, b.n, 1)
    dm = 1.0 - abs(a.m - b.m) / max(a.m, b.m, 1)
    return (dn + dm) / 2.0


def density_matcher(a: Structure, b: Structure) -> float:
    def dens(s: Structure) -> float:
        return s.m / (s.n * (s.n - 1)) if s.n > 1 else 0.0
    return 1.0 - abs(dens(a) - dens(b))


def degree_matcher(a: Structure, b: Structure) -> float:
    """Compares sorted degree sequences. A classic near-miss for structure --
    it feels topological and is blind to how anything is wired."""
    def degs(s: Structure) -> list[int]:
        c: Counter = Counter()
        for r in s.relations:
            c[r.src] += 1
            c[r.dst] += 1
        return sorted((c[v] for v in s.nodes), reverse=True)
    da, db = degs(a), degs(b)
    n = max(len(da), len(db))
    da += [0] * (n - len(da))
    db += [0] * (n - len(db))
    total = sum(max(x, y) for x, y in zip(da, db)) or 1
    return 1.0 - sum(abs(x - y) for x, y in zip(da, db)) / total


def constant(a: Structure, b: Structure) -> float:
    """Predicts the majority class. Discriminates nothing, fails nothing
    loudly, and will quietly sit at chance forever."""
    return 0.5


class SeedMemoriser:
    """Recognises exact structures it was shown during development and looks
    up the answer. Perfect on the dev set, worthless on anything else."""

    def __init__(self) -> None:
        self.table: dict[frozenset, float] = {}

    def prime(self, pairs: list[tuple[Structure, float]]) -> None:
        for struct, score in pairs:
            self.table[struct.edge_set()] = score

    def __call__(self, a: Structure, b: Structure) -> float:
        return self.table.get(b.edge_set(), 0.0)


def penalty_fitter(a: Structure, b: Structure) -> float:
    """Refits the penalty per pair to maximise the score.

    This is the attack EXP-000a proved is live: if eta is a free parameter,
    nothing stops it being chosen after seeing the pair.
    """
    return max(tunable_K(a, b, e / 50.0).score for e in range(0, 76))


# -- the honest measures, for contrast --------------------------------------

def mdl_gain(a: Structure, b: Structure) -> float:
    """F-06a as originally proposed: absolute compression gain in bits."""
    return mdl_correspondence(a, b, DEFAULT_CODE).gain_bits


def mdl_ratio(a: Structure, b: Structure) -> float:
    """F-06a corrected: compression RATIO.

    Absolute gain scales with the size of the target -- a bigger structure
    has more bits available to save, so it wins on volume rather than on
    shared organisation. The ratio normalises that out. Found by EXP-000c,
    invisible to EXP-000a because every condition there was size-matched.
    """
    return mdl_correspondence(a, b, DEFAULT_CODE).ratio


def tunable_fixed(a: Structure, b: Structure) -> float:
    """F-06 used honestly -- one eta, declared in advance, applied to every
    pair. Still broken, because the declared value decides the answer."""
    return tunable_K(a, b, 0.5).score


def build_registry(dev_conditions: list[tuple[Structure, float]]) -> dict[str, Method]:
    memoriser = SeedMemoriser()
    memoriser.prime(dev_conditions)
    return {
        # impostors
        "name_reader": name_reader,
        "size_matcher": size_matcher,
        "density_matcher": density_matcher,
        "degree_matcher": degree_matcher,
        "constant": constant,
        "seed_memoriser": memoriser,
        "penalty_fitter": penalty_fitter,
        # candidates under test
        "tunable_eta_0.5": tunable_fixed,
        "mdl_gain_bits": mdl_gain,
        "mdl_ratio_F06a": mdl_ratio,
    }


IMPOSTOR_NAMES = frozenset({
    "name_reader", "size_matcher", "density_matcher", "degree_matcher",
    "constant", "seed_memoriser", "penalty_fitter",
})
