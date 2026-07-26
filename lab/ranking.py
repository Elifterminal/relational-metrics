"""Tie-aware ranking. Written after EXP-027 caught a published artifact.

EXP-026 reported "the generic document outranks the true analogue on 3 of 4
motifs." It does not. On all four motifs the paraphrase, the analogue and the
generic score IDENTICALLY -- equal in the last bit, not merely close. The
"ranking" among them came from `sorted()` breaking ties on Python's hash(),
which is salted per process, so the result differed on every run and was
reported once as though it were a measurement.

Two separate faults, and the second is the one that matters:
  1. The tie-break was not reproducible.  (Annoying. Fixable with a stable key.)
  2. A total order was imposed on tied items AT ALL.  (The actual error. A
     stable tie-break would have made the artifact reproducible, not correct.)

So ranking returns TIED GROUPS. If the measure cannot separate two documents,
the output says so instead of inventing a winner.
"""

from __future__ import annotations

# Exact equality is the right test here: these are deterministic code lengths
# computed by the same path, not statistical estimates. A tolerance would
# invent ties that do not exist. Kept explicit so the choice is visible.
def rank_with_ties(scores: dict[str, float]) -> list[list[str]]:
    """Descending groups of exactly-equal scores. Members sorted for stability."""
    groups: dict[float, list[str]] = {}
    for k, v in scores.items():
        groups.setdefault(v, []).append(k)
    return [sorted(groups[v]) for v in sorted(groups, reverse=True)]


def format_ranking(groups: list[list[str]]) -> str:
    """'{P=V=X} > W > U' -- braces mark an unbroken tie."""
    return " > ".join(g[0] if len(g) == 1 else "{" + "=".join(g) + "}"
                      for g in groups)


def tier_of(groups: list[list[str]], kind: str) -> int:
    for i, g in enumerate(groups):
        if kind in g:
            return i
    raise KeyError(kind)


def strictly_above(groups: list[list[str]], a: str, b: str) -> bool:
    """True only if a is in a STRICTLY higher tie-group than b."""
    return tier_of(groups, a) < tier_of(groups, b)


def tied(groups: list[list[str]], a: str, b: str) -> bool:
    return tier_of(groups, a) == tier_of(groups, b)
