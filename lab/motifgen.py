"""Generate query / analogue / false-friend triples with no annotation involved.

Every corpus in this project was written by me and annotated by hand. EXP-033
found my documents announce their roles in the prose; EXP-040 found my
annotation applies a four-relation template regardless of content. Rebuilding
the corpus would rebuild both.

Generating the structures directly removes the annotation step entirely. What
that buys is a test of the MEASURE. What it costs is realism -- these are not
documents anyone wrote, and the analogue/false-friend distinction is true by
construction rather than by judgement. Both halves stated, because the second
is the reason this cannot replace a corpus test.

    query          a random typed directed structure
    analogue       every node renamed (a different vocabulary), a fraction of
                   relations perturbed -- a correspondent, not a copy
    false friend   the query's OWN node names, the same number of relations
                   rewired -- shares vocabulary, differs in structure
    unrelated      matched size, independently generated -- the control that
                   would expose a measure rewarding renaming rather than shape
"""

from __future__ import annotations

import random

from structure import Relation, Structure

TYPES = ("POS", "NEG")


def _mk(name, edges, domain):
    rels = tuple(Relation(a, b, t) for a, b, t in edges)
    nodes = tuple(sorted({n for r in rels for n in (r.src, r.dst)}))
    return Structure(name, nodes, rels, domain)


def _random_edges(nodes, m, rng):
    seen, out = set(), []
    tries = 0
    while len(out) < m and tries < 200:
        tries += 1
        a, b = rng.sample(nodes, 2)
        t = rng.choice(TYPES)
        if (a, b, t) in seen:
            continue
        seen.add((a, b, t))
        out.append((a, b, t))
    return out


def _perturb(edges, frac, nodes, rng):
    """Rewire a fraction of relations. Returns new edge list."""
    k = max(1, round(len(edges) * frac)) if frac > 0 else 0
    idx = rng.sample(range(len(edges)), min(k, len(edges)))
    out = list(edges)
    cur = set(out)
    for i in idx:
        for _ in range(40):
            a, b = rng.sample(nodes, 2)
            t = rng.choice(TYPES)
            if (a, b, t) not in cur:
                cur.discard(out[i])
                out[i] = (a, b, t)
                cur.add(out[i])
                break
    return out


def _rewire_n(edges, k, nodes, rng):
    """Rewire exactly k relations. Absolute counts, not fractions.

    EXP-047 used fractions and its sweep silently collapsed: with 5 relations,
    every level from 0.1 to 0.2 rounded to the same single rewire, so the
    analogue and the false friend ended up EQUALLY damaged and there was nothing
    for the measure to prefer. The apparent boundary was the rounding.
    """
    if k <= 0:
        return list(edges)
    idx = rng.sample(range(len(edges)), min(k, len(edges)))
    out = list(edges)
    cur = set(out)
    for i in idx:
        for _ in range(40):
            a, b = rng.sample(nodes, 2)
            t = rng.choice(TYPES)
            if (a, b, t) not in cur:
                cur.discard(out[i])
                out[i] = (a, b, t)
                cur.add(out[i])
                break
    return out


def triple_k(seed: int, k_analogue: int, gap: int = 2,
             n_nodes: int = 6, n_rel: int = 8):
    """(query, analogue, false_friend, unrelated) with EXPLICIT damage counts.

    The false friend is always rewired `gap` relations MORE than the analogue,
    so the analogue has a real and constant advantage at every point of a sweep.
    The question the sweep then asks is: how much absolute damage can the
    analogue take before that advantage stops being detectable?
    """
    rng = random.Random(seed)
    qn = [f"q{i}" for i in range(n_nodes)]
    an = [f"a{i}" for i in range(n_nodes)]
    q_edges = _random_edges(qn, n_rel, rng)

    ren = dict(zip(qn, an))
    a_edges = _rewire_n([(ren[a], ren[b], t) for a, b, t in q_edges],
                        k_analogue, an, rng)
    w_edges = _rewire_n(list(q_edges), k_analogue + gap, qn, rng)
    u_edges = _random_edges([f"u{i}" for i in range(n_nodes)], n_rel, rng)

    return (_mk(f"q{seed}", q_edges, "query_domain"),
            _mk(f"a{seed}", a_edges, "other_domain"),
            _mk(f"w{seed}", w_edges, "query_domain"),
            _mk(f"u{seed}", u_edges, "unrelated_domain"))


def triple(seed: int, perturb: float, n_nodes: int = 5, n_rel: int = 5):
    """One (query, analogue, false_friend, unrelated) set.

    RETAINED AS EXP-047 RAN IT, flaw and all, so that experiment stays
    reproducible. Use triple_k for anything new.
    """
    rng = random.Random(seed)
    qn = [f"q{i}" for i in range(n_nodes)]
    an = [f"a{i}" for i in range(n_nodes)]
    q_edges = _random_edges(qn, n_rel, rng)

    ren = dict(zip(qn, an))
    a_edges = [(ren[a], ren[b], t) for a, b, t in q_edges]
    a_edges = _perturb(a_edges, perturb, an, rng)
    w_edges = _perturb(list(q_edges), max(perturb, 0.2), qn, rng)

    u_edges = _random_edges([f"u{i}" for i in range(n_nodes)], n_rel, rng)

    return (_mk(f"q{seed}", q_edges, "query_domain"),
            _mk(f"a{seed}", a_edges, "other_domain"),
            _mk(f"w{seed}", w_edges, "query_domain"),
            _mk(f"u{seed}", u_edges, "unrelated_domain"))
