"""Adversarial worlds for F-04a.

F-04a passed its acceptance test on the first attempt, on worlds written by
the same party that wrote the measure. That is R-04 exactly, and a first-try
pass is a reason for suspicion rather than confidence.

These worlds are built to BREAK it. The most important one is
`driver_only_3way`: structure that is entirely internal to the participants
and says nothing whatever about the outcome. Connected information is computed
on the joint over all variables and does not privilege any of them, so there
is a specific reason to expect it to fire there -- and if it does, the measure
reports "these things are structured together" when the honest answer is
"these things are structured together and it is irrelevant to your question".

For an application that distinction is not academic. It is the difference
between a useful result and a confident irrelevance.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

VARS = ("a", "b", "c", "d", "e")


@dataclass(frozen=True)
class StressWorld:
    name: str
    expectation: str        # what SHOULD happen, written before running
    description: str
    build: Callable[[random.Random], tuple[dict[str, int], int]]

    def sample(self, n: int, seed: int) -> tuple[list[dict], list[int]]:
        rng = random.Random(seed)
        rows, ys = [], []
        for _ in range(n):
            row, y = self.build(rng)
            rows.append(row)
            ys.append(y)
        return rows, ys


def _base(rng: random.Random) -> dict[str, int]:
    return {v: rng.randint(0, 1) for v in VARS}


def _noisy(y: int, rng: random.Random, p: float = 0.05) -> int:
    return 1 - y if rng.random() < p else y


# -- THE CRITICAL ADVERSARIAL CASE ------------------------------------------

def _driver_only_3way(rng):
    """a, b, c carry a hard three-way constraint among THEMSELVES.
    The outcome is an independent coin. Nothing about the drivers predicts it.

    Connected information sees a joint distribution, not a question. There is
    no reason built into it to care that the structure it finds is orthogonal
    to the outcome."""
    row = _base(rng)
    a, b = rng.randint(0, 1), rng.randint(0, 1)
    row["a"], row["b"], row["c"] = a, b, a ^ b      # a^b^c == 0 always
    return row, row["e"]                            # outcome unrelated


def _driver_only_pairwise(rng):
    """Same idea, one order down: b is a copy of a, outcome independent."""
    row = _base(rng)
    row["b"] = row["a"]
    return row, row["e"]


# -- mixtures and gradations ------------------------------------------------

def _mixed(rng):
    """Redundancy AND synergy in the same world, both INSIDE the tested
    variable set.

    First written with the redundant copy in `d`, which is not among the
    drivers under test -- so the joint never saw it and the world tested
    nothing it claimed to. Caught by reading the output rather than the
    intent: I_C(2) came back at 0.0004 when redundancy was supposedly
    planted. Fifth instance of asserting a property instead of checking it.

    Now: c copies a (order-2 redundancy among the drivers) and the outcome is
    the parity of a and b (order-3 synergy with the outcome). Both live in the
    joint, and they should land at different orders.
    """
    row = _base(rng)
    row["c"] = row["a"]
    return row, _noisy(row["a"] ^ row["b"], rng)


def _partial_synergy(strength: float):
    """Outcome is the three-way parity with probability `strength`, otherwise
    an independent coin. Sweeping this gives a power curve rather than a
    single pass/fail."""
    def build(rng):
        row = _base(rng)
        if rng.random() < strength:
            return row, row["a"] ^ row["b"] ^ row["c"]
        return row, rng.randint(0, 1)
    return build


def _deterministic(rng):
    """Three-way parity with NO noise. The joint has hard zeros, which is
    where iterative proportional fitting is most likely to misbehave."""
    row = _base(rng)
    return row, row["a"] ^ row["b"] ^ row["c"]


def _nearly_deterministic_marginal(rng):
    """A driver that is almost always 1. Rare cells make marginal estimates
    unstable and IPF slow -- a realistic data pathology rather than a
    contrived one."""
    row = _base(rng)
    row["c"] = 1 if rng.random() < 0.97 else 0
    return row, _noisy(row["a"] ^ row["b"] ^ row["c"], rng)


STRESS: tuple[StressWorld, ...] = (
    StressWorld("driver_only_3way",
                "MUST NOT report outcome-relevant structure",
                "a^b^c==0 among the drivers; outcome is an independent coin.",
                _driver_only_3way),
    StressWorld("driver_only_pairwise",
                "MUST NOT report outcome-relevant structure",
                "b copies a; outcome is an independent coin.",
                _driver_only_pairwise),
    StressWorld("mixed",
                "order 2 carries the redundancy, order 3 the synergy, "
                "and only the order-3 term is outcome-significant",
                "c copies a (redundancy among drivers) AND outcome is the "
                "parity of a and b (synergy with the outcome).",
                _mixed),
    StressWorld("deterministic",
                "order 4 fires; IPF must not break on hard zeros",
                "3-way parity, no noise. Joint contains structural zeros.",
                _deterministic),
    StressWorld("skewed_marginal",
                "order 4 fires despite an unbalanced driver",
                "c is 1 about 97% of the time; rare cells destabilise fitting.",
                _nearly_deterministic_marginal),
) + tuple(
    StressWorld(f"synergy_{int(s*100):03d}",
                "order 4 should scale with strength, monotonically",
                f"3-way parity with probability {s:.2f}, else a coin.",
                _partial_synergy(s))
    for s in (0.0, 0.25, 0.5, 0.75, 1.0)
)
