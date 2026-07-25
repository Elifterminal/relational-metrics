"""F-04a -- connected information via the maximum-entropy hierarchy.

WHY NOT PID. The obvious replacement for F-04 was partial information
decomposition (Williams & Beer 2010 and successors), which exists precisely
because interaction information conflates synergy with redundancy. Reading it
first was the right call: for THREE OR MORE SOURCES, antichain-lattice PID is
provably impossible. The desired axioms -- whole-equals-sum-of-parts,
commutativity, monotonicity, self-redundancy, independent identity -- are
mutually incompatible, and the obstruction is representational rather than
axiomatic. Two systems can carry identical atoms and different mutual
information, so no universal reconstruction function exists. Building on that
lattice would have been building on a proved dead end.

The impossibility is scoped to antichain-indexed decompositions. This is not
one.

WHAT THIS IS. Connected information (Schneidman, Still, Berry & Bialek,
PRL 91 238701, 2003; the same object appears as stochastic interaction in
Amari's and Ay's information geometry). Let p~(k) be the MAXIMUM ENTROPY
distribution matching every marginal of order <= k. Then

    I_C(k) = H[p~(k-1)] - H[p~(k)]

-- how much the maximum possible entropy drops once order-k marginals are
also known. Equivalently a difference of KL divergences from the data to
successive maximum-entropy projections.

WHY IT FIXES F-04's CAUSE OF DEATH. Redundancy is entirely visible in
low-order marginals: if b and c are copies of a, the PAIRWISE marginals
already pin the joint, so the maximum-entropy distribution matching them
reproduces the data exactly and every higher order contributes zero. Genuine
higher-order structure is exactly what low-order marginals CANNOT reproduce.
So the thing F-04 confused -- "several participants carry information" versus
"the configuration does something the parts cannot" -- is the difference this
construction is built on.

Properties, all of which F-04 lacked:
  * non-negative at every order, by construction (I-projection);
  * sums exactly to the total multi-information, so it is a real
    decomposition rather than a residual;
  * defined at any arity without the antichain problem.

Cost: iterative proportional fitting over the full joint, exponential in the
number of variables. Fine at four binary variables (16 cells); a real limit at
scale, and stated as one.
"""

from __future__ import annotations

import math
from collections import Counter
from itertools import combinations, product

_LOG2 = math.log(2.0)
TOL = 1e-11
MAX_SWEEPS = 4000


def empirical_joint(rows: list[dict], ys: list[int],
                    variables: tuple[str, ...]) -> dict[tuple, float]:
    """Full joint over (Y, *variables) from samples. Y is index 0."""
    counts: Counter = Counter()
    for row, y in zip(rows, ys):
        counts[(y,) + tuple(row[v] for v in variables)] += 1
    n = len(ys)
    states = list(product((0, 1), repeat=len(variables) + 1))
    return {s: counts.get(s, 0) / n for s in states}


def entropy(p: dict[tuple, float]) -> float:
    return -sum(v * math.log(v) / _LOG2 for v in p.values() if v > 0)


def marginal(p: dict[tuple, float], idx: tuple[int, ...]) -> dict[tuple, float]:
    out: dict[tuple, float] = {}
    for state, v in p.items():
        key = tuple(state[i] for i in idx)
        out[key] = out.get(key, 0.0) + v
    return out


def maxent_matching(p: dict[tuple, float], order: int) -> dict[tuple, float]:
    """Maximum-entropy distribution matching every marginal of size `order`.

    Iterative proportional fitting from uniform. Matching all size-k marginals
    implies all smaller ones, so constraining on size exactly k is enough.

    IPF converges to the I-projection of the uniform distribution onto the
    constraint set -- which, because uniform is the maximum-entropy prior, is
    the maximum-entropy distribution satisfying those marginals.
    """
    n_vars = len(next(iter(p)))
    if order >= n_vars:
        return dict(p)
    if order <= 0:
        u = 1.0 / len(p)
        return {s: u for s in p}

    targets = [(idx, marginal(p, idx))
               for idx in combinations(range(n_vars), order)]

    q = {s: 1.0 / len(p) for s in p}
    for _ in range(MAX_SWEEPS):
        shift = 0.0
        for idx, target in targets:
            current = marginal(q, idx)
            scale = {}
            for key, want in target.items():
                have = current.get(key, 0.0)
                if want <= 0.0:
                    scale[key] = 0.0
                elif have <= 0.0:
                    scale[key] = 0.0        # unreachable cell; IPF leaves it
                else:
                    scale[key] = want / have
            for state in q:
                key = tuple(state[i] for i in idx)
                f = scale.get(key, 1.0)
                if f != 1.0:
                    new = q[state] * f
                    shift += abs(new - q[state])
                    q[state] = new
        total = sum(q.values())
        if total > 0:
            q = {s: v / total for s, v in q.items()}
        if shift < TOL:
            break
    return q


def connected_information(p: dict[tuple, float]) -> dict[int, float]:
    """I_C(k) for k = 1 .. n_vars.

    I_C(1) is the information explained by single-variable marginals alone
    (relative to uniform); I_C(k) for k >= 2 is the genuine order-k structure.
    Every term is >= 0 and they sum to H[uniform] - H[p].
    """
    n_vars = len(next(iter(p)))
    entropies = {0: math.log(len(p)) / _LOG2}
    for k in range(1, n_vars + 1):
        entropies[k] = entropy(maxent_matching(p, k))
    return {k: entropies[k - 1] - entropies[k] for k in range(1, n_vars + 1)}


def synergy_at_full_order(rows: list[dict], ys: list[int],
                          variables: tuple[str, ...]) -> dict:
    """F-04a applied to an outcome and its candidate drivers.

    The outcome counts as a variable, so a dependence of Y on k drivers is a
    structure of order k+1. `Y = a XOR b` is order 3; `Y = a XOR b XOR c` is
    order 4. Reported per order so the arity of the dependence is read off
    rather than assumed.
    """
    p = empirical_joint(rows, ys, variables)
    ic = connected_information(p)
    n = len(variables) + 1
    return {
        "connected": {str(k): round(v, 4) for k, v in ic.items()},
        "highest_order": round(ic[n], 4),
        "total_beyond_pairwise": round(sum(ic[k] for k in range(3, n + 1)), 4),
        "n_variables": n,
    }
