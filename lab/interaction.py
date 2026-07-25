"""F-04 -- the higher-order remainder.

    Omega(S) = sum over T subset of S of (-1)^(|S|-|T|) * F(T)

Subtract everything the smaller subsets already explain; whatever is left
needed the whole configuration at once. Omega != 0 is the candidate evidence
that structure exists at arity |S| and is not recoverable from the parts.

F here is mutual information between the outcome and the variables in T,
estimated plug-in from counts. That choice matters and is stated rather than
buried: plug-in MI is UPWARD biased, and the bias grows with the number of
cells, which is exponential in |T|. So the bias does not enter Omega equally
at every subset size and does not cancel. Whether that produces false
positives is not something to reason about -- it is EXP-002's job to measure.
"""

from __future__ import annotations

import math
from collections import Counter
from itertools import combinations

_LOG2 = math.log(2.0)


def mutual_information(rows: list[dict], ys: list[int], subset: tuple[str, ...]) -> float:
    """I(Y; X_subset) in bits, plug-in estimator. Empty subset gives 0."""
    if not subset:
        return 0.0
    n = len(ys)
    if n == 0:
        return 0.0

    joint: Counter = Counter()
    px: Counter = Counter()
    py: Counter = Counter()
    for row, y in zip(rows, ys):
        key = tuple(row[v] for v in subset)
        joint[(key, y)] += 1
        px[key] += 1
        py[y] += 1

    total = 0.0
    for (key, y), c in joint.items():
        p_xy = c / n
        p_x = px[key] / n
        p_y = py[y] / n
        if p_xy > 0 and p_x > 0 and p_y > 0:
            total += p_xy * math.log(p_xy / (p_x * p_y)) / _LOG2
    return total


def omega(rows: list[dict], ys: list[int], s: tuple[str, ...]) -> float:
    """The higher-order remainder over the participant set `s`."""
    k = len(s)
    total = 0.0
    for size in range(0, k + 1):
        sign = (-1) ** (k - size)
        for subset in combinations(s, size):
            total += sign * mutual_information(rows, ys, subset)
    return total


def permutation_test(rows: list[dict], ys: list[int], s: tuple[str, ...],
                     n_perm: int, seed: int) -> dict:
    """Calibrate Omega against a null that carries the SAME estimation bias.

    Shuffling the outcome destroys every real dependence while leaving sample
    size, cell counts and subset structure identical. So whatever bias the
    estimator contributes appears in the null too, and comparing against it
    removes exactly the thing raw Omega cannot distinguish from signal.
    """
    import random
    rng = random.Random(seed)
    observed = omega(rows, ys, s)

    shuffled = list(ys)
    null: list[float] = []
    for _ in range(n_perm):
        rng.shuffle(shuffled)
        null.append(omega(rows, shuffled, s))

    n_ge = sum(1 for v in null if v >= observed)
    p = (n_ge + 1) / (n_perm + 1)          # add-one, never reports p = 0
    mean = sum(null) / len(null)
    var = sum((v - mean) ** 2 for v in null) / max(len(null) - 1, 1)
    sd = math.sqrt(var)
    return {
        "observed": observed,
        "null_mean": mean,
        "null_sd": sd,
        "p_value": p,
        "z": (observed - mean) / sd if sd > 0 else 0.0,
        "calibrated": observed - mean,
    }
