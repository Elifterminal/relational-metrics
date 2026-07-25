"""The condition set for EXP-000a.

Protocol section 3 requires five conditions. Built here around one motif:
the reinforcing-channel pattern that shows up in erosion, vasculature,
traffic, and current finding the low-resistance path.

    many paths -> small advantage -> more flow -> more capacity -> more flow
                                                        `-> alternatives suppressed

Relation types are deliberately coarse (POS / NEG) so the type-substitution
space stays enumerable. Two types is enough to build the near-miss, which is
the condition that matters.
"""

from __future__ import annotations

import random

from structure import Structure, build

POS, NEG = "POS", "NEG"

# -- A: the reference -------------------------------------------------------

A = build("A_erosion", "geomorphology", [
    ("paths",     "advantage", POS),
    ("advantage", "flow",      POS),
    ("flow",      "erosion",   POS),
    ("erosion",   "capacity",  POS),
    ("capacity",  "flow",      POS),   # closes the reinforcing loop
    ("capacity",  "paths",     NEG),   # alternatives are abandoned
])

# -- B: same structure, different everything else ---------------------------
# A true cross-domain analogue. Isomorphic to A. No shared vocabulary, and
# even the relation TYPE names differ, so any mapping must assert a
# translation.

B = build("B_vascular", "vascular", [
    ("vessels",   "patency",    "GROWS"),
    ("patency",   "perfusion",  "GROWS"),
    ("perfusion", "remodeling", "GROWS"),
    ("remodeling","caliber",    "GROWS"),
    ("caliber",   "perfusion",  "GROWS"),
    ("caliber",   "vessels",    "PRUNES"),
])

# -- C: same surface, different structure -----------------------------------
# Identical vocabulary to A. The reinforcing loop is gone -- capacity no
# longer feeds back into flow. Should score LOW or the measure is reading
# vocabulary.

C = build("C_same_words", "geomorphology", [
    ("paths",     "advantage", POS),
    ("advantage", "flow",      POS),
    ("flow",      "erosion",   POS),
    ("erosion",   "capacity",  POS),
    ("paths",     "capacity",  POS),   # no return path to flow
    ("advantage", "paths",     NEG),
])

# -- E: the persuasive near-miss --------------------------------------------
# Identical to A in every respect except ONE edge type. capacity now DAMPS
# flow instead of amplifying it. The loop is negative: the system self-limits
# instead of running away. Same words, same topology, opposite behaviour.

E = build("E_near_miss", "geomorphology", [
    ("paths",     "advantage", POS),
    ("advantage", "flow",      POS),
    ("flow",      "erosion",   POS),
    ("erosion",   "capacity",  POS),
    ("capacity",  "flow",      NEG),   # <-- the only difference from A
    ("capacity",  "paths",     NEG),
])


# -- D: matched random ------------------------------------------------------

def make_D(seed: int = 20260725) -> Structure:
    """Same vocabulary, same node count, same edge count as A. No shared
    organisation. Generated with a fixed seed so the condition is stable
    across runs but was not hand-picked to fail."""
    rng = random.Random(seed)
    nodes = list(A.nodes)
    edges: set[tuple[str, str, str]] = set()
    while len(edges) < A.m:
        s, d = rng.sample(nodes, 2)
        edges.add((s, d, rng.choice([POS, NEG])))
    return build("D_random", "geomorphology", sorted(edges))


D = make_D()


# -- B2: HELD OUT ------------------------------------------------------------
# A third vocabulary, isomorphic to A like B is. Deliberately NOT part of the
# development condition set: it exists so a method that memorised the others
# has something it has never seen. Any measure that scores B highly and B2
# poorly is recognising instances, not structure.

B2 = build("B2_traffic_heldout", "traffic", [
    ("routes",    "shortcut",   "FAVOURS"),
    ("shortcut",  "volume",     "FAVOURS"),
    ("volume",    "widening",   "FAVOURS"),
    ("widening",  "throughput", "FAVOURS"),
    ("throughput","volume",     "FAVOURS"),
    ("throughput","routes",     "STARVES"),
])


# -- F: the superset distractor ---------------------------------------------
# Added 2026-07-25 after EXP-000c caught a gap in the condition set, not in a
# formula. Every other condition has exactly A's node and edge count, which
# was meant to control confounds -- but it also means raw match count alone
# sorts them correctly, so a method that ignores mapping cost entirely scores
# as well as one that doesn't.
#
# F contains ALL of A's relations plus eight more. Any measure that rewards
# "how many of A's relations can I find in here" scores it perfectly. It is
# the encyclopedia that answers every query because it contains everything,
# and it must NOT outrank a true analogue.

F = build("F_superset", "geomorphology", [
    # all six of A, verbatim
    ("paths",     "advantage", POS),
    ("advantage", "flow",      POS),
    ("flow",      "erosion",   POS),
    ("erosion",   "capacity",  POS),
    ("capacity",  "flow",      POS),
    ("capacity",  "paths",     NEG),
    # eight more, drowning the motif in unrelated organisation
    ("paths",     "flow",      NEG),
    ("paths",     "erosion",   POS),
    ("advantage", "erosion",   NEG),
    ("advantage", "capacity",  POS),
    ("flow",      "paths",     POS),
    ("flow",      "capacity",  NEG),
    ("erosion",   "advantage", POS),
    ("erosion",   "paths",     NEG),
])


CONDITIONS: dict[str, tuple[Structure, str, str]] = {
    "A": (A, "reference", "the motif itself"),
    "B": (B, "different surface / same structure", "must score HIGH"),
    "C": (C, "same surface / different structure", "must score LOW"),
    "D": (D, "different structure / matched size", "must score LOW"),
    "E": (E, "persuasive near-miss, one edge flipped",
          "must be separated from A -- and the difference located"),
}
