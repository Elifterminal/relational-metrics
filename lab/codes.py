"""Description-length codes.

This is the answer being tested for Q-06. The tunable form of correspondence
(F-06) contains a penalty parameter that trades match quality against mapping
complexity, and whoever sets that parameter decides the answer. MDL removes
the dial: the penalty becomes *the number of bits needed to write the mapping
down*, which is counted, not chosen.

Honest residual: MDL replaces "choose lambda" with "choose the code". That is
a much smaller hole -- the code is fixed once, declared in advance, and
applied identically to every pair -- but it is not zero. Hence CODES below:
several defensible codes, so we can measure whether the verdict depends on
which one we picked.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

_LOG2 = math.log(2.0)


def log2(x: float) -> float:
    return math.log(x) / _LOG2 if x > 0 else 0.0


def log2_choose(n: int, k: int) -> float:
    if k < 0 or k > n or n <= 0:
        return 0.0
    return math.lgamma(n + 1) / _LOG2 - math.lgamma(k + 1) / _LOG2 \
        - math.lgamma(n - k + 1) / _LOG2


def log2_perm(n: int, k: int) -> float:
    """Bits to name an ordered selection of k distinct items from n."""
    if k <= 0 or n <= 0 or k > n:
        return 0.0
    return math.lgamma(n + 1) / _LOG2 - math.lgamma(n - k + 1) / _LOG2


# -- universal integer codes ------------------------------------------------

def elias_gamma(x: int) -> float:
    """Bits for a non-negative integer under Elias gamma (shifted)."""
    v = x + 1
    return 2.0 * math.floor(log2(v)) + 1.0


def elias_delta(x: int) -> float:
    """Bits for a non-negative integer under Elias delta (shifted)."""
    v = x + 1
    lg = math.floor(log2(v))
    return lg + 2.0 * math.floor(log2(lg + 1)) + 1.0


def flat32(x: int) -> float:
    """Deliberately crude: a fixed-width machine integer. Included as a
    stress case -- if the verdict flips under this, the verdict was fragile."""
    return 32.0


@dataclass(frozen=True)
class Code:
    """A complete, fixed description-length scheme.

    Declared before use and applied identically to every pair compared. That
    uniformity is what distinguishes this from a tuned parameter.
    """

    name: str
    integer: callable

    # -- L(R): describe a structure from scratch -------------------------

    def structure(self, n: int, m: int, n_types: int) -> float:
        """Bits to describe a typed directed structure with no help.

        Node LABELS are never encoded -- only a canonical index -- so the
        length is invariant to renaming by construction (P-08).
        """
        per_edge = 2.0 * log2(max(n, 1)) + log2(max(n_types, 1))
        return self.integer(n) + self.integer(m) + self.integer(n_types) \
            + m * per_edge

    # -- L(phi): describe the mapping ------------------------------------

    def mapping(self, n1: int, n2: int, k: int,
                n_types1: int, n_types2: int, n_subs: int = 0) -> float:
        """Bits to specify a partial injective node map plus a relation-type map.

        This is the derived complexity penalty -- the reason an elaborate
        mapping loses to a simple one (P-15) without anyone choosing how much
        elaboration should cost.

        RELATION-TYPE ENCODING, corrected 2026-07-26 after EXP-024.

        The earlier version charged `n_subs * log2(T2+1)`, where n_subs counted
        the type pairs whose NAMES differ. That made the cost depend on whether
        two domains happened to use the same word for a relation -- so a genuine
        cross-domain analogue, which by definition does not, paid more than a
        same-vocabulary structure with different wiring. EXP-024 measured it:
        the analogue lost to the false friend by 0.0022 bits, entirely from this
        term.

        THAT IS THE PATHOLOGY THAT DEMOTED F-06. It was removed for participant
        labels -- which are never encoded at all, only a canonical index -- and
        was never removed here. It survived twenty-four experiments because it
        only bites when two candidates are close enough for a couple of bits to
        decide between them.

        The correction is to charge for SPECIFYING the map, exactly as the node
        map does, and never for what the names happen to be: assigning each of
        T1 source types to one of T2 target types costs T1*log2(T2) bits,
        whether or not any of them coincide. `n_subs` is retained in the
        signature and ignored, so that any caller still passing it is a visible
        no-op rather than a silent behaviour change.
        """
        node_map = self.integer(k) + log2_choose(n1, k) + log2_perm(n2, k)
        type_map = self.integer(n_types1) + n_types1 * log2(max(n_types2, 1))
        return node_map + type_map

    # -- L(R2 | R1, phi): describe the target as corrections -------------

    def conditional(self, n2: int, n_types2: int,
                    n_predicted: int, n_deleted: int, n_inserted: int) -> float:
        per_edge = 2.0 * log2(max(n2, 1)) + log2(max(n_types2, 1))
        dels = self.integer(n_deleted) + log2_choose(n_predicted, n_deleted)
        ins = self.integer(n_inserted) + n_inserted * per_edge
        return dels + ins


CODES: tuple[Code, ...] = (
    Code("gamma", elias_gamma),
    Code("delta", elias_delta),
    Code("flat32", flat32),
)

DEFAULT_CODE = CODES[0]
