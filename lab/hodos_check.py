"""Verification of Vanta's Hodos mathematics, checked rather than assumed.

The Stage 3 charter originally called for restating her work and having it
checked by her. Lee corrected that: equations are self-verifying in a way
documents are not, and we care whether the mathematics transfers, not what the
project is for. So this implements her claims from the equation sheet and tests
them.

WHAT THIS IS AND IS NOT. It is a check that I have READ her mathematics
correctly, and a check of the claims that are checkable in closed form. It is
NOT an audit of her novelty tags (ASSEMBLED / KNOWN / OURS) -- those are
provenance claims, not mathematical ones, and auditing them is not our business.

Implemented from the equation sheet only. No access to her code.
"""

from __future__ import annotations

import math
import random

RNG = random.Random(20260726)


def simplex(F, rng=RNG):
    v = [rng.random() + 1e-6 for _ in range(F)]
    s = sum(v)
    return [x / s for x in v]


def BC(p, q):
    """Bhattacharyya coefficient."""
    return sum(math.sqrt(a * b) for a, b in zip(p, q))


# --- A2: the ground metrics, as written on her sheet ---------------------
def chi2(p, q):
    return 0.5 * sum((a - b) ** 2 / (a + b) for a, b in zip(p, q) if (a + b) > 0)


def sqrt_chi2(p, q):
    return math.sqrt(chi2(p, q))


def fisher_rao(p, q):
    return 2.0 * math.acos(min(1.0, max(-1.0, BC(p, q))))


def hellinger(p, q):
    return math.sqrt(max(0.0, 1.0 - BC(p, q)))


def wasserstein1(p, q):
    cp = cq = 0.0
    tot = 0.0
    for a, b in zip(p, q):
        cp += a
        cq += b
        tot += abs(cp - cq)
    return tot


GROUNDS = {"chi2": chi2, "sqrt_chi2": sqrt_chi2, "fisher_rao": fisher_rao,
           "hellinger": hellinger, "wasserstein1": wasserstein1}


# --- A3: the sphere lemma ------------------------------------------------
def sphere_lemma(F=12, trials=4000):
    """phi(p)=sqrt(p) lands on the unit sphere; d_FR = 2*arccos(BC);
    chi2 ~ 1/4 d_FR^2 near the diagonal."""
    worst_norm = 0.0
    for _ in range(trials):
        p = simplex(F)
        worst_norm = max(worst_norm, abs(sum(math.sqrt(x) ** 2 for x in p) - 1.0))
    # correlation of chi2 against (1/4) d_FR^2, over NEARBY pairs
    xs, ys = [], []
    for _ in range(trials):
        p = simplex(F)
        q = [max(1e-12, x + RNG.gauss(0, 0.004)) for x in p]
        s = sum(q)
        q = [x / s for x in q]
        xs.append(chi2(p, q))
        ys.append(0.25 * fisher_rao(p, q) ** 2)
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = (sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5
    return {"max_deviation_from_unit_sphere": worst_norm,
            "corr_chi2_vs_quarter_dFR2_near_diagonal": num / den if den else 0.0}


# --- A2/A6: which grounds satisfy the triangle inequality ----------------
def triangle(name, g, F=10, trials=60000):
    worst, viol = 0.0, 0
    for _ in range(trials):
        p, q, r = simplex(F), simplex(F), simplex(F)
        slack = g(p, r) - (g(p, q) + g(q, r))
        if slack > 1e-12:
            viol += 1
            worst = max(worst, slack)
    return {"violations": viol, "trials": trials, "worst_excess": worst,
            "behaves_as_metric": viol == 0}


# --- A6 Theorem 1: cyclic roll is an exact isometry ----------------------
def roll(p, s):
    F = len(p)
    return [p[(i - s) % F] for i in range(F)]


def shift_isometry(F=12, trials=3000):
    out = {}
    for name, g in GROUNDS.items():
        worst = 0.0
        for _ in range(trials):
            p, q = simplex(F), simplex(F)
            s = RNG.randrange(F)
            worst = max(worst, abs(g(roll(p, s), roll(q, s)) - g(p, q)))
        out[name] = {"max_abs_deviation": worst, "exactly_invariant": worst < 1e-12}
    return out


# --- A5: the temporal-pooling theorem, slopes in rho ---------------------
def pooling_slopes(F=12, rhos=(0.02, 0.05, 0.1, 0.2, 0.4)):
    """Two processes agree on 1-rho and differ on a terminal rho fraction.
    Claim: aligned distance ~ Theta(rho) (slope 1), pooled ground ~ O(rho^2)
    (slope 2) under the interior/support condition."""
    base = simplex(F)
    s_a, s_b = simplex(F), simplex(F)
    d_pts, g_pts = [], []
    for rho in rhos:
        # aligned distance: pays g(s_a,s_b) on a rho fraction of the path
        d = rho * fisher_rao(s_a, s_b)
        # pooled: time-average each process, then compare the averages
        abar = [(1 - rho) * base[i] + rho * s_a[i] for i in range(F)]
        bbar = [(1 - rho) * base[i] + rho * s_b[i] for i in range(F)]
        d_pts.append((math.log(rho), math.log(d)))
        g_pts.append((math.log(rho), math.log(chi2(abar, bbar))))

    def slope(pts):
        n = len(pts)
        mx = sum(a for a, _ in pts) / n
        my = sum(b for _, b in pts) / n
        return (sum((a - mx) * (b - my) for a, b in pts)
                / sum((a - mx) ** 2 for a, _ in pts))
    return {"aligned_distance_slope": slope(d_pts),
            "pooled_ground_slope": slope(g_pts),
            "her_reported": {"aligned": 1.00, "pooled": 1.90}}


# --- A1b: does the min-MEAN objective actually pad itself? ---------------
def padding_check(T=14, F=8):
    """Her claim: minimising the MEAN aligned cost is gamed by padding the path
    with cheap steps, because |pi| is in the denominator. Checked directly."""
    A = [simplex(F) for _ in range(T)]
    B = [simplex(F) for _ in range(T)]
    C = [[fisher_rao(a, b) for b in B] for a in A]
    INF = float("inf")
    # best TOTAL cost, and the mean along that same path
    best = [[(INF, 0)] * T for _ in range(T)]
    best[0][0] = (C[0][0], 1)
    for i in range(T):
        for j in range(T):
            if i == 0 and j == 0:
                continue
            cands = []
            for di, dj in ((1, 0), (0, 1), (1, 1)):
                pi, pj = i - di, j - dj
                if 0 <= pi < T and 0 <= pj < T and best[pi][pj][0] < INF:
                    c, L = best[pi][pj]
                    cands.append((c + C[i][j], L + 1))
            if cands:
                best[i][j] = min(cands, key=lambda x: x[0])
    tot, L = best[T - 1][T - 1]
    mean_on_total_path = tot / L
    # now minimise the MEAN directly, via Dinkelbach on lambda
    lo, hi = 0.0, max(max(r) for r in C)
    for _ in range(60):
        lam = (lo + hi) / 2
        d = [[INF] * T for _ in range(T)]
        steps = [[0] * T for _ in range(T)]
        d[0][0] = C[0][0] - lam
        steps[0][0] = 1
        for i in range(T):
            for j in range(T):
                if i == 0 and j == 0:
                    continue
                cands = []
                for di, dj in ((1, 0), (0, 1), (1, 1)):
                    pi, pj = i - di, j - dj
                    if 0 <= pi < T and 0 <= pj < T and d[pi][pj] < INF:
                        cands.append((d[pi][pj] + C[i][j] - lam, steps[pi][pj] + 1))
                if cands:
                    d[i][j], steps[i][j] = min(cands, key=lambda x: x[0])
        if d[T - 1][T - 1] > 0:
            lo = lam
        else:
            hi = lam
    return {"path_length_min_total": L,
            "mean_along_min_total_path": mean_on_total_path,
            "min_mean_value": hi,
            "min_mean_is_lower": hi < mean_on_total_path - 1e-9,
            "max_possible_path_length": 2 * T - 1}


# --- B2: is the warp derivative a probability distribution? -------------
def warp_derivative_is_distribution(n=200):
    """gamma_dot >= 0 and integrates to 1, so it lives on the simplex --
    the claim that makes 'the square root of time' possible."""
    inc = [RNG.random() for _ in range(n)]
    s = sum(inc)
    gdot = [x / s * n for x in inc]              # sampled at n points on [0,1]
    integral = sum(g * (1.0 / n) for g in gdot)
    return {"all_non_negative": all(g >= 0 for g in gdot),
            "integral": integral,
            "integrates_to_one": abs(integral - 1.0) < 1e-12}
