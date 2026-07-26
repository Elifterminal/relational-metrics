"""d_A for relational search -- derived from the principles, not invented.

d_A has blocked A-01 since day one, and the reason it stayed blocked is that
the obvious moves are all wrong in ways the project has since measured:

  * A SCALAR is ruled out. P-17: relational structure is not a scalar and past
    three participants not even a pair of profiles. A one-number distance
    between two relational maps discards exactly what makes them relational.

  * A SINGLE SUMMARY OVER PARTS is ruled out. EXP-017 measured that
    summarising a per-component quantity is a CHOICE that can REVERSE the
    ranking -- best-case and worst-case orderings came out anti-correlated.

  * AN OBSERVER-FREE DISTANCE is ruled out. EXP-010: significance cannot be
    defined without naming a question. So d_A is always d_A(map1, map2 | Q).

What is left is not a gap. The components of d_A should be the ways a
relational answer can be WRONG -- and the project already has that list, in
its own principles, written before any of this was measured:

  missing        P-10 relational exclusion: a real relation absent from the map
  spurious       P-11 relational overstatement: a relation asserted too strongly
  misclassified  P-07 correspondence reported as transmission -- analogy sold
                 as mechanism. The attractive-nonsense failure.
  misordered     the map places a result at the wrong relational distance
  undirected     P-09 direction lost or reversed
  unprovenanced  C-16 inferred material presented as documented

So d_A is a VECTOR over named failure modes, each one traceable to a
principle that predates it. That is a derivation. Inventing six plausible
error terms and calling them a metric would not be.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DA:
    """d_A(returned, ideal | Q). Every component is a count or a rate, and
    NONE of them is combined into a total -- deliberately."""
    missing: int
    spurious: int
    misclassified: int
    misordered: int
    rank_displacement: float
    n_ideal: int

    def as_dict(self) -> dict:
        return {
            "missing": self.missing,
            "spurious": self.spurious,
            "misclassified": self.misclassified,
            "misordered": self.misordered,
            "rank_displacement": round(self.rank_displacement, 4),
        }

    @property
    def is_perfect(self) -> bool:
        return (self.missing == 0 and self.spurious == 0
                and self.misclassified == 0 and self.misordered == 0)

    def dominates(self, other: "DA") -> bool:
        """Pareto dominance -- better or equal on every component and strictly
        better on one. This is how two results are compared WITHOUT inventing
        weights. Where neither dominates, the honest answer is that they are
        incomparable, and saying so is more useful than a fabricated total."""
        comps = ["missing", "spurious", "misclassified", "misordered"]
        vals = [(getattr(self, c), getattr(other, c)) for c in comps]
        vals.append((self.rank_displacement, other.rank_displacement))
        return all(a <= b for a, b in vals) and any(a < b for a, b in vals)


def evaluate(returned: list[str], ideal: list[str],
             returned_class: dict[str, str] | None = None,
             ideal_class: dict[str, str] | None = None) -> DA:
    """Compare a returned ordering against the ideal one for a query.

    `returned`/`ideal` are ordered lists of document kinds or ids.
    The class maps carry what relation class the system CLAIMED versus what
    the corpus says -- the misclassification channel, which is where analogy
    gets sold as mechanism.
    """
    ret_set, ide_set = set(returned), set(ideal)
    missing = len(ide_set - ret_set)
    spurious = len(ret_set - ide_set)

    misclassified = 0
    if returned_class and ideal_class:
        for k in ret_set & ide_set:
            if returned_class.get(k) != ideal_class.get(k):
                misclassified += 1

    pos_ret = {k: i for i, k in enumerate(returned)}
    pos_ide = {k: i for i, k in enumerate(ideal)}
    shared = [k for k in ideal if k in pos_ret]

    misordered = 0
    for i in range(len(shared)):
        for j in range(i + 1, len(shared)):
            a, b = shared[i], shared[j]
            if (pos_ide[a] - pos_ide[b]) * (pos_ret[a] - pos_ret[b]) < 0:
                misordered += 1

    disp = 0.0
    if shared:
        disp = sum(abs(pos_ret[k] - pos_ide[k]) for k in shared) / len(shared)

    return DA(missing, spurious, misclassified, misordered, disp, len(ideal))
