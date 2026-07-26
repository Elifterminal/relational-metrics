"""Asymmetric test families -- closing R-15.

Every function family used through EXP-013..EXP-016 turned out to have
retention spread of exactly zero, so a best-case summary looked harmless when
it was not. Three published corrections trace to that. This is the fix: a set
of families whose participants genuinely differ in how much they matter.

A DISTINCTION THAT R-15 GOT WRONG. "Symmetric" is ambiguous, and the two
readings come apart. The multiplexer `b if a=0 else c` is NOT permutation-
symmetric -- you cannot swap the selector with a data input and get the same
function -- yet all three of its influences are 0.5, so its retention spread
is exactly zero, identical to majority.

    The property that matters is INFLUENCE-symmetry, not permutation-symmetry.

A test set could be full of permutation-asymmetric functions and still be
completely blind to the spread problem. MUX is included below precisely as the
control that demonstrates this, so the distinction cannot quietly be lost
again.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


def truth_table(k: int, fn: Callable[[tuple[int, ...]], int]) -> tuple[int, ...]:
    return tuple(fn(tuple((i >> b) & 1 for b in range(k))) for i in range(1 << k))


@dataclass(frozen=True)
class AsymFamily:
    name: str
    k: int
    expression: str
    influence_profile: str
    why_it_is_here: str
    table: tuple[int, ...]


FAMILIES: tuple[AsymFamily, ...] = (
    AsymFamily(
        "and_or", 3, "a AND (b OR c)", "0.75 / 0.25 / 0.25",
        "Plain graded asymmetry: one participant matters three times as much "
        "as the others. Retention 0.214 if you lose a, 0.738 if you lose b "
        "or c -- a spread of 0.524 that a best-case summary reports as 0.738.",
        truth_table(3, lambda v: v[0] & (v[1] | v[2]))),

    AsymFamily(
        "xor_and", 3, "a XOR (b AND c)", "1.00 / 0.50 / 0.50",
        "THE DEMONSTRATOR. Retention is 0.0 if you lose a and 0.5 if you lose "
        "b or c. This structure VANISHES under the wrong loss and survives at "
        "half under the right one -- exactly the case EXP-018 found (2 -> 38 "
        "functions vanish at k=3) and which no symmetric family could show.",
        truth_table(3, lambda v: v[0] ^ (v[1] & v[2]))),

    AsymFamily(
        "mux", 3, "b if a=0 else c", "0.50 / 0.50 / 0.50",
        "THE CONTROL, and the reason R-15 needed sharpening. Not permutation-"
        "symmetric at all -- the selector is nothing like the data inputs -- "
        "yet influence-symmetric, so spread is exactly zero. Proves that "
        "permutation-asymmetry is NOT sufficient to exercise the spread.",
        truth_table(3, lambda v: v[1] if v[0] == 0 else v[2])),

    AsymFamily(
        "graded_k4", 4, "a AND (b OR (c AND d))", "0.625 / 0.375 / 0.125 / 0.125",
        "Three distinct influence levels in one function. Spread 0.558. The "
        "k=4 case where 'which participant' is not a binary question but a "
        "graded one.",
        truth_table(4, lambda v: v[0] & (v[1] | (v[2] & v[3])))),

    AsymFamily(
        "xor_cascade_k4", 4, "a XOR (b AND (c OR d))", "1.00 / 0.75 / 0.25 / 0.25",
        "Widest spread found at k=4: 0.750. Vanishes entirely if you lose a, "
        "retains three quarters if you lose c or d. The single number 'this "
        "structure retains 0.75' would be true and almost entirely useless.",
        truth_table(4, lambda v: v[0] ^ (v[1] & (v[2] | v[3])))),
)


def by_arity(k: int) -> dict[str, tuple[int, ...]]:
    return {f.name: f.table for f in FAMILIES if f.k == k}
