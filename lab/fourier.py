"""Walsh-Fourier spectrum of Boolean functions.

Influence says how much each participant matters ON ITS OWN. It says nothing
about how participants interact WITH EACH OTHER. The Fourier expansion
separates the two cleanly:

    F(x) = sum over S of  fhat(S) * chi_S(x),     chi_S(x) = (-1)^(sum of x_i for i in S)

with F the +-1 encoding of f. Then:

  * fhat(S)^2 is the weight carried by the interaction among exactly the
    participants in S;
  * the LEVEL weight W_d = sum of fhat(S)^2 over |S| = d is how much of the
    function lives at interaction order d;
  * influence I_j = sum of fhat(S)^2 over all S containing j -- a MARGINAL of
    the spectrum.

So influence is a projection of the interaction structure, and two functions
can share an influence profile while distributing weight across subsets
completely differently. Whether that happens, and whether anything we measure
can see it, is EXP-021.

Everything here is checked against the independently-implemented combinatorial
influence in run_exp015 before use (protocol: a derivation is not a result).
"""

from __future__ import annotations

from itertools import combinations


def spectrum(table: tuple[int, ...], k: int) -> dict[tuple[int, ...], float]:
    """fhat(S) for every subset S of participants, keyed by sorted tuple."""
    n = 1 << k
    pm = [1 - 2 * b for b in table]          # {0,1} -> {+1,-1}
    out: dict[tuple[int, ...], float] = {}
    for size in range(k + 1):
        for S in combinations(range(k), size):
            acc = 0
            for x in range(n):
                par = 0
                for i in S:
                    par ^= (x >> i) & 1
                acc += pm[x] * (1 if par == 0 else -1)
            out[S] = acc / n
    return out


def level_weights(spec: dict, k: int) -> list[float]:
    """W_d for d = 0..k. Sums to 1 for a Boolean function (Parseval)."""
    w = [0.0] * (k + 1)
    for S, c in spec.items():
        w[len(S)] += c * c
    return w


def pair_weights(spec: dict, k: int) -> dict[tuple[int, int], float]:
    """Weight on each PAIR of participants -- the first genuinely
    interactional quantity, invisible to any per-participant summary."""
    return {S: spec[S] ** 2 for S in spec if len(S) == 2}


def fourier_influence(spec: dict, j: int) -> float:
    """I_j as a marginal of the spectrum: total weight on subsets containing j."""
    return sum(c * c for S, c in spec.items() if j in S)


def interaction_profile(spec: dict, k: int) -> tuple:
    """A canonical, participant-relabelling-invariant summary of HOW the
    participants interact -- sorted pair weights plus the level profile.

    Sorted so that two functions differing only by which participant is which
    are counted as the same interaction structure, exactly as the influence
    profile does for the first-order case.
    """
    pw = tuple(sorted(round(v, 9) for v in pair_weights(spec, k).values()))
    lw = tuple(round(v, 9) for v in level_weights(spec, k))
    return (lw, pw)
