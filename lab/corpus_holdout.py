"""A-01 -- the HELD-OUT search corpus.

Written BEFORE the fix to F-06a exists, and frozen by committing it before the
code change lands. That ordering is the whole point: the development corpus
(corpus.py) has been looked at, a failure diagnosed on it, and a fix designed
against that diagnosis. Testing the fix on the same three motifs would measure
how well the fix was fitted to them.

RULES FOLLOWED IN WRITING IT:
  * Three motifs again, structurally distinct from each other AND from the
    development set. Not another positive-feedback story.
  * Same six-document schema, so the comparison is like for like.
  * Analogues use a different domain's relation vocabulary -- which is not
    gaming the known weak point, it is simply what a cross-domain analogue
    looks like. The development set did the same.
  * Authored without checking which motifs the current code happens to pass.

The development set's motifs were: positive cycle, negative cycle, acyclic
cascade. These are: mutual inhibition (bistable pair), threshold accumulation
with discharge and reset, and substitution under blockage. Different shapes,
different failure surfaces.
"""

from __future__ import annotations

from corpus import Doc
from structure import build

POS, NEG = "POS", "NEG"


def _s(name, domain, edges):
    return build(name, domain, edges)


HOLDOUT: tuple[Doc, ...] = (
    # ---- motif 4: mutual inhibition (bistable pair) -----------------------
    Doc("m4_D", "inhibition", "D", "neuroscience",
        "Each population suppresses the other; whichever leads wins outright.",
        _s("m4_D", "neuroscience", [
            ("pop_a", "pop_b", NEG), ("pop_b", "pop_a", NEG),
            ("drive", "pop_a", POS), ("drive", "pop_b", POS)])),
    Doc("m4_P", "inhibition", "P", "neuroscience",
        "Two assemblies inhibit one another under common drive; one dominates.",
        _s("m4_P", "neuroscience", [
            ("assembly_x", "assembly_y", NEG), ("assembly_y", "assembly_x", NEG),
            ("input", "assembly_x", POS), ("input", "assembly_y", POS)])),
    Doc("m4_X", "inhibition", "X", "ecology",
        "Two species suppress each other for one niche; one excludes the other.",
        _s("m4_X", "ecology", [
            ("species_1", "species_2", "SUPPRESSES"),
            ("species_2", "species_1", "SUPPRESSES"),
            ("resource", "species_1", "FEEDS"), ("resource", "species_2", "FEEDS")])),
    Doc("m4_W", "inhibition", "W", "neuroscience",
        "Same words, cooperative wiring: the populations reinforce each other.",
        _s("m4_W", "neuroscience", [
            ("pop_a", "pop_b", POS), ("pop_b", "pop_a", POS),
            ("drive", "pop_a", POS), ("drive", "pop_b", NEG)])),
    Doc("m4_V", "inhibition", "V", "general",
        "Components in a system influence one another.",
        _s("m4_V", "general", [
            ("component", "influence", POS), ("influence", "component", POS),
            ("system", "component", POS), ("influence", "system", POS)])),
    Doc("m4_U", "inhibition", "U", "typography",
        "Optical sizing adjusts stroke contrast at small point sizes.",
        _s("m4_U", "typography", [
            ("point_size", "contrast", NEG), ("contrast", "legibility", POS),
            ("master", "point_size", POS), ("legibility", "reading_rate", POS)])),

    # ---- motif 5: threshold accumulation, discharge, reset ---------------
    Doc("m5_D", "threshold", "D", "electronics",
        "Charge accumulates until breakdown, which discharges and resets it.",
        _s("m5_D", "electronics", [
            ("current", "charge", POS), ("charge", "breakdown", POS),
            ("breakdown", "discharge", POS), ("discharge", "charge", NEG)])),
    Doc("m5_P", "threshold", "P", "electronics",
        "Stored potential builds to a firing point, dumps, and the store empties.",
        _s("m5_P", "electronics", [
            ("supply", "store", POS), ("store", "firing_point", POS),
            ("firing_point", "dump", POS), ("dump", "store", NEG)])),
    Doc("m5_X", "threshold", "X", "geology",
        "Strain accumulates on a fault until rupture releases it and resets stress.",
        _s("m5_X", "geology", [
            ("plate_motion", "strain", "BUILDS"), ("strain", "rupture", "BUILDS"),
            ("rupture", "slip", "BUILDS"), ("slip", "strain", "RELIEVES")])),
    Doc("m5_W", "threshold", "W", "electronics",
        "Same words, no reset: discharge feeds charge and it never empties.",
        _s("m5_W", "electronics", [
            ("current", "charge", POS), ("charge", "breakdown", POS),
            ("breakdown", "discharge", POS), ("discharge", "charge", POS)])),
    Doc("m5_V", "threshold", "V", "general",
        "Quantities can increase and decrease over time.",
        _s("m5_V", "general", [
            ("quantity", "level", POS), ("level", "quantity", POS),
            ("time", "quantity", POS), ("level", "time", POS)])),
    Doc("m5_U", "threshold", "U", "lexicography",
        "Citation slips are filed by headword before sense division.",
        _s("m5_U", "lexicography", [
            ("slip", "headword", POS), ("headword", "sense", POS),
            ("editor", "slip", POS), ("sense", "entry", POS)])),

    # ---- motif 6: substitution under blockage ----------------------------
    Doc("m6_D", "substitution", "D", "metabolism",
        "The main pathway is blocked, so flux reroutes through a bypass.",
        _s("m6_D", "metabolism", [
            ("inhibitor", "main_path", NEG), ("main_path", "product", POS),
            ("bypass", "product", POS), ("main_path", "bypass", NEG)])),
    Doc("m6_P", "substitution", "P", "metabolism",
        "With the primary route shut, throughput moves to the secondary route.",
        _s("m6_P", "metabolism", [
            ("blocker", "primary", NEG), ("primary", "output", POS),
            ("secondary", "output", POS), ("primary", "secondary", NEG)])),
    Doc("m6_X", "substitution", "X", "networking",
        "The preferred link fails, so traffic fails over to the backup path.",
        _s("m6_X", "networking", [
            ("fault", "preferred_link", "BLOCKS"),
            ("preferred_link", "delivery", "CARRIES"),
            ("backup_link", "delivery", "CARRIES"),
            ("preferred_link", "backup_link", "BLOCKS")])),
    Doc("m6_W", "substitution", "W", "metabolism",
        "Same words, no substitution: blocking the main path just stops output.",
        _s("m6_W", "metabolism", [
            ("inhibitor", "main_path", NEG), ("main_path", "product", POS),
            ("bypass", "product", NEG), ("bypass", "main_path", POS)])),
    Doc("m6_V", "substitution", "V", "general",
        "When something stops working, other things may happen.",
        _s("m6_V", "general", [
            ("thing", "state", POS), ("state", "outcome", POS),
            ("outcome", "thing", POS), ("state", "thing", POS)])),
    Doc("m6_U", "substitution", "U", "campanology",
        "Method ringing permutes bell order by fixed transposition rules.",
        _s("m6_U", "campanology", [
            ("rule", "permutation", POS), ("permutation", "row", POS),
            ("band", "rule", POS), ("row", "peal", POS)])),
)

HOLDOUT_QUERIES = {"inhibition": "m4_D", "threshold": "m5_D", "substitution": "m6_D"}


def holdout_docs_for(motif: str) -> list[Doc]:
    return [d for d in HOLDOUT if d.motif == motif and d.kind != "D"]


def holdout_query(motif: str) -> Doc:
    return next(d for d in HOLDOUT if d.doc_id == HOLDOUT_QUERIES[motif])


def holdout_malformed() -> list[str]:
    return [d.doc_id for d in HOLDOUT if not d.structure.is_well_formed]
