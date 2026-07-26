"""A-01 -- the controlled search corpus.

Manually annotated, deliberately. search.md's standing rule: relation
extraction is a SECOND problem, and testing an extractor and a measure at the
same time makes every result uninterpretable. These are hand-typed structures;
the prose is illustrative only.

THREE motifs, not one -- EXP-005's lesson. And chosen to be structurally
distinct in the way that experiment showed matters: a positive cycle, a
negative cycle, and an acyclic cascade. A corpus of three positive-feedback
stories would be the same n=1 mistake wearing a bigger number.

SIX documents per motif, giving ground truth by construction:
  D  direct         -- the motif in its home domain
  P  paraphrase     -- same domain, reworded, same structure
  X  analogue       -- SAME STRUCTURE, different domain. The result that
                       justifies the whole project.
  W  false friend   -- same vocabulary, DIFFERENT structure. The trap.
  V  vague          -- generic connective tissue, related to everything
  U  unrelated      -- control

W and V exist because they are how a relational search fails in practice: by
rewarding shared words, and by surfacing something that connects to everything
and explains nothing.
"""

from __future__ import annotations

from dataclasses import dataclass

from structure import Structure, build

POS, NEG = "POS", "NEG"


@dataclass(frozen=True)
class Doc:
    doc_id: str
    motif: str
    kind: str            # D P X W V U
    domain: str
    gloss: str
    structure: Structure


def _s(name, domain, edges):
    return build(name, domain, edges)


DOCS: tuple[Doc, ...] = (
    # ---- motif 1: reinforcing channel (positive cycle) --------------------
    Doc("m1_D", "reinforcing", "D", "geomorphology",
        "Flow concentrates in a channel, deepens it, which draws more flow.",
        _s("m1_D", "geomorphology", [
            ("flow", "incision", POS), ("incision", "capacity", POS),
            ("capacity", "flow", POS), ("capacity", "rival_channels", NEG)])),
    Doc("m1_P", "reinforcing", "P", "geomorphology",
        "Erosion widens a gully; the wider gully carries more water still.",
        _s("m1_P", "geomorphology", [
            ("discharge", "scour", POS), ("scour", "crosssection", POS),
            ("crosssection", "discharge", POS), ("crosssection", "adjacent_gullies", NEG)])),
    Doc("m1_X", "reinforcing", "X", "vascular",
        "Perfusion drives remodelling; the wider vessel takes more perfusion.",
        _s("m1_X", "vascular", [
            ("perfusion", "remodelling", "GROWS"), ("remodelling", "caliber", "GROWS"),
            ("caliber", "perfusion", "GROWS"), ("caliber", "collaterals", "PRUNES")])),
    Doc("m1_W", "reinforcing", "W", "geomorphology",
        "Same words, opposite wiring: deposition FILLS the channel and chokes flow.",
        _s("m1_W", "geomorphology", [
            ("flow", "incision", POS), ("incision", "capacity", NEG),
            ("capacity", "flow", NEG), ("rival_channels", "capacity", POS)])),
    Doc("m1_V", "reinforcing", "V", "general",
        "Systems change over time as energy moves through them.",
        _s("m1_V", "general", [
            ("system", "change", POS), ("energy", "system", POS),
            ("change", "state", POS), ("state", "system", POS)])),
    Doc("m1_U", "reinforcing", "U", "philology",
        "Vowel shifts in Middle English are dated by rhyme evidence.",
        _s("m1_U", "philology", [
            ("rhyme", "dating", POS), ("manuscript", "rhyme", POS),
            ("dating", "chronology", POS), ("scribe", "manuscript", POS)])),

    # ---- motif 2: regulated balance (negative cycle) ----------------------
    Doc("m2_D", "regulating", "D", "physiology",
        "Rising temperature triggers sweating, which lowers temperature.",
        _s("m2_D", "physiology", [
            ("temperature", "sensor", POS), ("sensor", "sweating", POS),
            ("sweating", "temperature", NEG), ("setpoint", "sensor", NEG)])),
    Doc("m2_P", "regulating", "P", "physiology",
        "A rise in core heat drives evaporative loss until the rise is cancelled.",
        _s("m2_P", "physiology", [
            ("core_heat", "detector", POS), ("detector", "evaporation", POS),
            ("evaporation", "core_heat", NEG), ("target", "detector", NEG)])),
    Doc("m2_X", "regulating", "X", "economics",
        "Price rises draw supply, and the added supply pushes price back down.",
        _s("m2_X", "economics", [
            ("price", "signal", "RAISES"), ("signal", "supply", "RAISES"),
            ("supply", "price", "LOWERS"), ("expectation", "signal", "LOWERS")])),
    Doc("m2_W", "regulating", "W", "physiology",
        "Same words, runaway wiring: sweating RAISES temperature further.",
        _s("m2_W", "physiology", [
            ("temperature", "sensor", POS), ("sensor", "sweating", POS),
            ("sweating", "temperature", POS), ("setpoint", "sensor", POS)])),
    Doc("m2_V", "regulating", "V", "general",
        "Feedback is important in many systems.",
        _s("m2_V", "general", [
            ("feedback", "system", POS), ("system", "behaviour", POS),
            ("behaviour", "feedback", POS), ("context", "system", POS)])),
    Doc("m2_U", "regulating", "U", "mineralogy",
        "Cleavage planes in mica arise from sheet silicate bonding.",
        _s("m2_U", "mineralogy", [
            ("bonding", "sheets", POS), ("sheets", "cleavage", POS),
            ("pressure", "bonding", POS), ("cleavage", "fracture", POS)])),

    # ---- motif 3: cascade (acyclic chain) --------------------------------
    Doc("m3_D", "cascade", "D", "power_systems",
        "One line trips, load shifts, the next line overloads and trips.",
        _s("m3_D", "power_systems", [
            ("line_a", "load_shift", POS), ("load_shift", "line_b", POS),
            ("line_b", "overload", POS), ("overload", "outage", POS)])),
    Doc("m3_P", "cascade", "P", "power_systems",
        "A failed conductor pushes current onto neighbours until they fail too.",
        _s("m3_P", "power_systems", [
            ("conductor", "redistribution", POS), ("redistribution", "neighbour", POS),
            ("neighbour", "thermal_limit", POS), ("thermal_limit", "blackout", POS)])),
    Doc("m3_X", "cascade", "X", "finance",
        "A default forces asset sales, depressing prices, forcing further defaults.",
        _s("m3_X", "finance", [
            ("default", "forced_sale", "DRIVES"), ("forced_sale", "counterparty", "DRIVES"),
            ("counterparty", "margin_breach", "DRIVES"),
            ("margin_breach", "insolvency", "DRIVES")])),
    Doc("m3_W", "cascade", "W", "power_systems",
        "Same words, no propagation: each line is independently protected.",
        _s("m3_W", "power_systems", [
            ("line_a", "overload", POS), ("line_b", "overload", POS),
            ("load_shift", "outage", NEG), ("overload", "load_shift", NEG)])),
    Doc("m3_V", "cascade", "V", "general",
        "Events can lead to other events.",
        _s("m3_V", "general", [
            ("event", "consequence", POS), ("consequence", "event", POS),
            ("context", "event", POS), ("consequence", "context", POS)])),
    Doc("m3_U", "cascade", "U", "horticulture",
        "Grafting compatibility depends on cambium alignment.",
        _s("m3_U", "horticulture", [
            ("cambium", "alignment", POS), ("alignment", "union", POS),
            ("rootstock", "cambium", POS), ("union", "vigour", POS)])),
)

QUERIES = {"reinforcing": "m1_D", "regulating": "m2_D", "cascade": "m3_D"}

# Ground truth by construction. The ONLY judgement call is that an analogue
# should outrank a false friend, which is the project's whole claim -- if that
# ordering is wrong, the thesis is wrong, not the corpus.
# CORRECTED 2026-07-26 (EXP-025). This originally read ["P","X","W","V","U"],
# asserting that a same-domain paraphrase should outrank a cross-domain
# analogue. That assumption CONTRADICTS THE PROJECT'S OWN THESIS: both are
# structurally identical to the query, and the entire claim is that structure
# is what counts and vocabulary is not. A structure-only measure MUST tie them.
#
# It does -- exactly. Once relation-type encoding was made name-independent,
# P and X score identically to 0.0000 in all six motifs across both corpora.
# So the ground truth was wrong, not the measure.
#
# Noticed from the data, which makes it post-hoc, and said plainly for that
# reason. It is nevertheless derivable from the thesis without looking at any
# result, and it does NOT affect the headline claim (analogue beats false
# friend), only the secondary ordering counts. Seventh instance of asserting a
# property instead of deriving it (R-12).
IDEAL_TIERS = [{"P", "X"}, {"W"}, {"V"}, {"U"}]
IDEAL_ORDER = ["P", "X", "W", "V", "U"]      # a linearisation, for display

RELATION_CLASS = {
    "P": "paraphrase",      # same structure, same domain
    "X": "analogical",      # same structure, different domain
    "W": "false_friend",    # shared vocabulary, different structure
    "V": "generic",         # connects to everything, explains nothing
    "U": "unrelated",
}


def docs_for(motif: str) -> list[Doc]:
    return [d for d in DOCS if d.motif == motif and d.kind != "D"]


def query_doc(motif: str) -> Doc:
    return next(d for d in DOCS if d.doc_id == QUERIES[motif])


def all_well_formed() -> list[str]:
    return [d.doc_id for d in DOCS if not d.structure.is_well_formed]
