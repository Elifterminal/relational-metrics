"""Two correspondence measures, put side by side.

F-06   -- the tunable form from the source conversation. Contains eta, the
          penalty that trades match quality against mapping complexity.
F-06a  -- the MDL form proposed as the answer to Q-06. No free parameter.

Both search the same mapping space with the same code, so any difference in
verdict is a difference in criterion and nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass

from codes import Code, DEFAULT_CODE, weight_levels
from mapping import Mapping, enumerate_mappings
from structure import Structure


# ---------------------------------------------------------------------------
# F-06: tunable correspondence
# ---------------------------------------------------------------------------

def translation_cost(a: Structure, b: Structure, phi: Mapping) -> float:
    """What a complexity penalty naturally charges for.

    Two components, both entirely reasonable-looking:
      1. vocabulary translation -- the structures come from different surface
         domains, so the mapping has to assert cross-domain identifications;
      2. type substitution -- the mapping has to assert that one relation type
         stands in for another.

    Note what this means. A TRUE cross-domain analogue pays both. A same-
    vocabulary structure with nothing in common pays neither. The penalty is
    charging for exactly the thing the theory exists to find.
    """
    cross_domain = phi.k if a.domain != b.domain else 0
    return float(cross_domain + phi.n_substitutions)


def structural_strain(a: Structure, b: Structure, phi: Mapping) -> float:
    """Predicted relations that fail to land."""
    predicted = phi.predicted_edges(a)
    return float(len(predicted - b.edge_set()))


@dataclass(frozen=True)
class TunableResult:
    eta: float
    score: float
    matched: int
    total: int
    complexity: float


def tunable_K(a: Structure, b: Structure, eta: float) -> TunableResult:
    """F-06, maximised over mappings.

        K = sum_e w_e * m(e, phi(e)) / ( sum_e w_e + eta * C(phi) )
    """
    denom_base = sum(r.weight for r in a.relations)
    b_edges = b.edge_set()

    best: TunableResult | None = None
    for phi in enumerate_mappings(a, b):
        nm, tm = phi.node_map, phi.type_map
        matched = 0.0
        n_matched = 0
        for r in a.relations:
            image = (nm.get(r.src), nm.get(r.dst), tm.get(r.rtype))
            if None not in image and image in b_edges:
                matched += r.weight
                n_matched += 1
        cost = translation_cost(a, b, phi) + structural_strain(a, b, phi)
        score = matched / (denom_base + eta * cost)
        if best is None or score > best.score:
            best = TunableResult(eta, score, n_matched, a.m, cost)
    return best or TunableResult(eta, 0.0, 0, a.m, 0.0)


# ---------------------------------------------------------------------------
# F-06a: MDL correspondence
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MDLResult:
    gain_bits: float          # L(B) - [L(phi) + L(B|A,phi)]   >0 means it helps
    baseline_bits: float      # L(B) alone
    mapping_bits: float
    conditional_bits: float
    matched: int
    total: int
    node_map: tuple[tuple[str, str], ...]
    type_map: tuple[tuple[str, str], ...]

    @property
    def ratio(self) -> float:
        """Compression ratio. 1.0 = A tells you nothing about B."""
        used = self.mapping_bits + self.conditional_bits
        return self.baseline_bits / used if used > 0 else 0.0


def mdl_correspondence(a: Structure, b: Structure,
                       code: Code = DEFAULT_CODE,
                       type_filter=None) -> MDLResult:
    """F-06a.

    Question asked: does knowing A, plus a mapping, let me write B down in
    fewer bits than writing B from scratch?

    If yes, A and B share organisation and the gain says how much, in bits.
    If no, there is no correspondence worth claiming. Nothing to tune.

    `type_filter` is EXP-052's instrument for Q-41 and defaults to None, which
    is exactly the behaviour that produced every published result. See
    enumerate_mappings for what it does and for why a filtered score being
    lower is arithmetic rather than a finding.
    """
    b_edges = b.edge_set()
    # Q-28: weights now enter the comparison. Normalised by geometric mean, so
    # a unit conversion is invariant BY CONSTRUCTION rather than by the measure
    # failing to look -- which is what EXP-000a had been publishing since the
    # first experiment (EXP-031 caught it).
    a_levels = weight_levels(tuple(r.weight for r in a.relations))
    b_levels = weight_levels(tuple(r.weight for r in b.relations))
    a_wt = {(r.src, r.dst, r.rtype): lv
            for r, lv in zip(a.relations, a_levels)}
    b_wt = {(r.src, r.dst, r.rtype): lv
            for r, lv in zip(b.relations, b_levels)}
    baseline = code.structure(b.n, b.m, len(b.types), b_levels)

    best: MDLResult | None = None
    for phi in enumerate_mappings(a, b, type_filter=type_filter):
        predicted = phi.predicted_edges(a)
        hits = predicted & b_edges
        deleted = len(predicted) - len(hits)
        inserted = len(b_edges) - len(hits)

        m_bits = code.mapping(a.n, b.n, phi.k,
                              len(a.types), len(b.types), phi.n_substitutions)
        # Weight corrections for the edges that actually landed. Only matched
        # edges are charged -- a deleted or inserted edge already pays for
        # itself in full, so charging its weight too would double-count.
        deltas = tuple(b_wt[img] - a_wt[src]
                       for img, src in phi.predicted_pairs(a) if img in hits)
        c_bits = code.conditional(b.n, len(b.types),
                                  len(predicted), deleted, inserted, deltas)
        gain = baseline - (m_bits + c_bits)

        if best is None or gain > best.gain_bits:
            best = MDLResult(gain, baseline, m_bits, c_bits,
                             len(hits), a.m, phi.nodes, phi.types)

    return best or MDLResult(0.0, baseline, 0.0, baseline, 0, a.m, (), ())
