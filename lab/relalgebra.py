"""The declared partial algebra on relation types.

EXP-029 needs to know when two relations compose, and into what. That is a
DECLARATION about the vocabularies, made once, here -- not a fact the measure
may infer, and not something an experiment may choose.

Each vocabulary supplies an amplifying and a damping type. Composition stays
inside a vocabulary and multiplies polarity, which is F-14's rule generalised
from the sign vocabulary to all of them:

    INCREASES o DECREASES = DECREASES        (+1 * -1 = -1)
    DECREASES o DECREASES = INCREASES        (-1 * -1 = +1)

Composition across vocabularies is deliberately UNDEFINED. A geological
"builds" followed by an ecological "suppresses" has no declared meaning, and
inventing one would be exactly the kind of quiet modelling choice this project
exists to catch. Undefined blocks contraction rather than guessing.
"""

from __future__ import annotations

# (amplifying, damping) per vocabulary. Enumerated from the three corpora --
# every relation type in use appears exactly once.
FAMILIES: tuple[tuple[str, str], ...] = (
    ("POS", "NEG"),
    ("INCREASES", "DECREASES"),
    ("GROWS", "PRUNES"),
    ("RAISES", "LOWERS"),
    ("FEEDS", "SUPPRESSES"),
    ("BUILDS", "RELIEVES"),
    ("CARRIES", "BLOCKS"),
    ("DRIVES", "DECREASES"),          # finance shares the general damping type
    ("FAVOURS", "STARVES"),           # traffic, from F-14
)

POLARITY: dict[str, int] = {}
FAMILY_OF: dict[str, tuple[str, str]] = {}
for _pos, _neg in FAMILIES:
    POLARITY.setdefault(_pos, +1)
    POLARITY.setdefault(_neg, -1)
    FAMILY_OF.setdefault(_pos, (_pos, _neg))
    FAMILY_OF.setdefault(_neg, (_pos, _neg))


def compose(t1: str, t2: str) -> str | None:
    """The type of t1 followed by t2, or None when not declared."""
    f1, f2 = FAMILY_OF.get(t1), FAMILY_OF.get(t2)
    if f1 is None or f2 is None or f1 != f2:
        return None
    return f1[0] if POLARITY[t1] * POLARITY[t2] > 0 else f1[1]


def decompose(t: str) -> tuple[str, str]:
    """A pair whose composition is `t`.

    Splitting "A decreases B" into "A decreases M, M decreases B" says A
    INCREASES B -- two sign flips cancel. Subdivision has to preserve what the
    relation says, so the second half is always the amplifying type.
    """
    fam = FAMILY_OF.get(t)
    if fam is None:
        raise KeyError(
            f"no declared family for relation type {t!r}. Subdividing or "
            f"contracting it would silently change what it says -- declare it "
            f"in FAMILIES rather than letting the transform corrupt content.")
    return (t, fam[0])


def check() -> list[str]:
    """decompose then compose must be the identity, for every declared type."""
    bad = []
    for t in POLARITY:
        a, b = decompose(t)
        if compose(a, b) != t:
            bad.append(f"{t}: decompose->{a},{b} composes to {compose(a, b)}")
    return bad
