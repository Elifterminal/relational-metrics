"""A-01 -- the INDEPENDENT corpus.

Neither the motifs, the documents, the annotations, nor the similarity
judgements were written by the party that wrote the measure. Lee commissioned
it from a separate system given only a format specification -- no description
of what was being tested, no mention of how correspondence is computed, and an
explicit instruction to refuse if asked what it was for.

This is the largest doubt in A-01 being addressed: both previous corpora were
mine, so annotation bias was untested. It is transcribed VERBATIM. Nothing has
been corrected, tidied, or made to fit -- if an annotation is odd, that is a
fact about the corpus and belongs in the result rather than being smoothed away.

FOUR motifs, and the author varied the shapes as the spec asked:
  1 participation-fed diversity   -- reinforcing loop, all INCREASES
  2 correction that shuts itself off -- self-limiting loop
  3 upstream regulator cascade    -- chain with one decisive participant
  4 asymmetric rivalry            -- mutual suppression plus one-sided feedback

Motifs 3 and 4 answer the spec's request for a case where participants are NOT
interchangeable, which is the property EXP-019/EXP-020 showed a naively chosen
test set will not contain.

ONE DISAGREEMENT, RECORDED RATHER THAN RESOLVED. The author judged PARAPHRASE
most similar to the query in all four motifs. EXP-025 concluded the opposite --
that paraphrase and analogue are structurally identical and must TIE, since the
project's thesis is that structure counts and vocabulary does not. So an
independent annotator thinks staying in the same field is worth something.
Both orderings are scored below. The disagreement is the finding; picking my
own would defeat the purpose of commissioning this.
"""

from __future__ import annotations

from corpus import Doc
from structure import build

INC, DEC = "INCREASES", "DECREASES"


def _s(name, domain, edges):
    return build(name, domain, edges)


INDEPENDENT: tuple[Doc, ...] = (
    # ---- motif 1: participation-fed diversity ----------------------------
    Doc("i1_D", "diversity", "D", "seed_exchange",
        "Greater variety availability improves planting fit, raising success, "
        "participation and contributions, expanding variety further.",
        _s("i1_D", "seed_exchange", [
            ("variety availability", "planting fit", INC),
            ("planting fit", "gardener success", INC),
            ("gardener success", "exchange participation", INC),
            ("exchange participation", "seed contributions", INC),
            ("seed contributions", "variety availability", INC)])),
    Doc("i1_P", "diversity", "P", "seed_exchange",
        "A seed library carrying more suitable seeds gives reliable harvests, "
        "drawing members who donate more packets.",
        _s("i1_P", "seed_exchange", [
            ("local seed range", "garden suitability", INC),
            ("garden suitability", "harvest reliability", INC),
            ("harvest reliability", "member turnout", INC),
            ("member turnout", "donated seed packets", INC),
            ("donated seed packets", "local seed range", INC)])),
    Doc("i1_X", "diversity", "X", "open_source",
        "A driver project supporting more devices gains users, whose adoption "
        "and bug reports attract maintainers who add more device support.",
        _s("i1_X", "open_source", [
            ("supported device models", "user compatibility", INC),
            ("user compatibility", "project adoption", INC),
            ("project adoption", "bug reports", INC),
            ("bug reports", "maintainer activity", INC),
            ("maintainer activity", "supported device models", INC)])),
    Doc("i1_W", "diversity", "W", "seed_exchange",
        "In a poorly curated exchange, excessive variety discourages "
        "participation and mixed contributions reduce planting fit.",
        _s("i1_W", "seed_exchange", [
            ("variety availability", "exchange participation", DEC),
            ("exchange participation", "seed contributions", INC),
            ("seed contributions", "planting fit", DEC),
            ("planting fit", "gardener success", INC),
            ("gardener success", "variety availability", DEC)])),
    Doc("i1_V", "diversity", "V", "general",
        "A system with more diversity may offer better options, improve "
        "outcomes, attract participants and receive resources.",
        _s("i1_V", "general", [
            ("system diversity", "process options", INC),
            ("process options", "outcome quality", INC),
            ("outcome quality", "participant interest", INC),
            ("participant interest", "resource input", INC),
            ("resource input", "system diversity", INC)])),
    Doc("i1_U", "diversity", "U", "conservation",
        "Display-lamp heat dries a parchment manuscript until fibres embrittle, "
        "pages crack and conservators must repair more.",
        _s("i1_U", "conservation", [
            ("lamp heat", "case temperature", INC),
            ("case temperature", "parchment dryness", INC),
            ("parchment dryness", "fiber brittleness", INC),
            ("fiber brittleness", "page cracking", INC),
            ("page cracking", "conservation repairs", INC)])),

    # ---- motif 2: correction that shuts itself off -----------------------
    Doc("i2_D", "correction", "D", "gallery_climate",
        "Rising humidity strengthens the humidistat signal, extending "
        "dehumidifier runtime and moisture removal until humidity falls.",
        _s("i2_D", "gallery_climate", [
            ("gallery humidity", "humidistat signal", INC),
            ("humidistat signal", "dehumidifier runtime", INC),
            ("dehumidifier runtime", "moisture removal", INC),
            ("moisture removal", "gallery humidity", DEC)])),
    Doc("i2_P", "correction", "P", "gallery_climate",
        "Wetter gallery air makes the sensor demand more from the drying unit, "
        "which extracts water and brings moisture back down.",
        _s("i2_P", "gallery_climate", [
            ("air moisture", "sensor demand", INC),
            ("sensor demand", "drying-unit operation", INC),
            ("drying-unit operation", "water extraction", INC),
            ("water extraction", "air moisture", DEC)])),
    Doc("i2_X", "correction", "X", "fisheries",
        "As a stock depletes, regulators tighten quotas, reducing effort and "
        "harvest pressure so depletion slows.",
        _s("i2_X", "fisheries", [
            ("stock depletion", "quota restriction", INC),
            ("quota restriction", "fishing effort", DEC),
            ("fishing effort", "harvest pressure", INC),
            ("harvest pressure", "stock depletion", INC)])),
    Doc("i2_W", "correction", "W", "gallery_climate",
        "In a malfunctioning unit, excessive runtime ices the coils and "
        "reduces moisture removal.",
        _s("i2_W", "gallery_climate", [
            ("gallery humidity", "humidistat signal", INC),
            ("humidistat signal", "dehumidifier runtime", INC),
            ("dehumidifier runtime", "moisture removal", DEC),
            ("moisture removal", "gallery humidity", DEC)])),
    Doc("i2_V", "correction", "V", "general",
        "A growing deviation produces a stronger control signal, increasing "
        "corrective action and a counteracting effect.",
        _s("i2_V", "general", [
            ("system deviation", "control signal", INC),
            ("control signal", "corrective action", INC),
            ("corrective action", "counteracting effect", INC),
            ("counteracting effect", "system deviation", DEC)])),
    Doc("i2_U", "correction", "U", "aviation",
        "Volcanic ash on a runway increases abrasion, accelerating tyre wear, "
        "raising landing risk and closures.",
        _s("i2_U", "aviation", [
            ("volcanic ash", "runway abrasion", INC),
            ("runway abrasion", "tire wear", INC),
            ("tire wear", "landing risk", INC),
            ("landing risk", "airport closures", INC)])),

    # ---- motif 3: upstream regulator cascade -----------------------------
    Doc("i3_D", "regulator", "D", "orchard",
        "Greater bat activity reduces insects, limiting leaf damage and tree "
        "stress while preserving fruit yield.",
        _s("i3_D", "orchard", [
            ("bat activity", "insect abundance", DEC),
            ("insect abundance", "leaf damage", INC),
            ("leaf damage", "tree stress", INC),
            ("tree stress", "fruit yield", DEC)])),
    Doc("i3_P", "regulator", "P", "orchard",
        "More bat foraging suppresses moths, reducing canopy feeding and "
        "orchard stress, protecting fruit set.",
        _s("i3_P", "orchard", [
            ("nighttime bat foraging", "moth population", DEC),
            ("moth population", "canopy feeding", INC),
            ("canopy feeding", "orchard stress", INC),
            ("orchard stress", "fruit set", DEC)])),
    Doc("i3_X", "regulator", "X", "software",
        "Greater lint coverage removes latent defects, preventing incidents "
        "and operator fatigue while sustaining release frequency.",
        _s("i3_X", "software", [
            ("lint coverage", "latent defects", DEC),
            ("latent defects", "production incidents", INC),
            ("production incidents", "operator fatigue", INC),
            ("operator fatigue", "release frequency", DEC)])),
    Doc("i3_W", "regulator", "W", "orchard",
        "A heavy fruit yield supports more insects, attracting bats that "
        "reduce leaf damage and one source of tree stress.",
        _s("i3_W", "orchard", [
            ("fruit yield", "insect abundance", INC),
            ("insect abundance", "bat activity", INC),
            ("bat activity", "leaf damage", DEC),
            ("leaf damage", "tree stress", INC)])),
    Doc("i3_V", "regulator", "V", "general",
        "A stronger early safeguard reduces hidden problems, preventing later "
        "disruption and strain while maintaining output.",
        _s("i3_V", "general", [
            ("early safeguard", "hidden problems", DEC),
            ("hidden problems", "later disruption", INC),
            ("later disruption", "staff strain", INC),
            ("staff strain", "output pace", DEC)])),
    Doc("i3_U", "regulator", "U", "ceramics",
        "Kiln temperature increases glaze fluidity and edge pooling, while "
        "faster cooling independently increases crazing.",
        _s("i3_U", "ceramics", [
            ("kiln temperature", "glaze fluidity", INC),
            ("glaze fluidity", "edge pooling", INC),
            ("edge pooling", "color depth", INC),
            ("cooling speed", "surface crazing", INC)])),

    # ---- motif 4: asymmetric rivalry with self-reinforcement -------------
    Doc("i4_D", "rivalry", "D", "education",
        "Institutional exposure favours standard spelling; standard and "
        "dialect displace one another; teacher approval reinforces standard.",
        _s("i4_D", "education", [
            ("institutional exposure", "standard spelling", INC),
            ("standard spelling", "dialect spelling", DEC),
            ("dialect spelling", "standard spelling", DEC),
            ("standard spelling", "teacher approval", INC),
            ("teacher approval", "standard spelling", INC)])),
    Doc("i4_P", "rivalry", "P", "education",
        "School contact promotes formal orthography, competing with vernacular "
        "and reinforced by instructor praise.",
        _s("i4_P", "education", [
            ("school contact", "formal orthography", INC),
            ("formal orthography", "vernacular orthography", DEC),
            ("vernacular orthography", "formal orthography", DEC),
            ("formal orthography", "instructor praise", INC),
            ("instructor praise", "formal orthography", INC)])),
    Doc("i4_X", "rivalry", "X", "roadside_ecology",
        "Road salt favours salt-tolerant grass over native sedge, while saline "
        "litter from the grass strengthens its own advantage.",
        _s("i4_X", "roadside_ecology", [
            ("road salt", "salt-tolerant grass", INC),
            ("salt-tolerant grass", "native sedge", DEC),
            ("native sedge", "salt-tolerant grass", DEC),
            ("salt-tolerant grass", "saline litter", INC),
            ("saline litter", "salt-tolerant grass", INC)])),
    Doc("i4_W", "rivalry", "W", "education",
        "In a dialect-inclusive programme, exposure raises approval of dialect "
        "spelling and the two varieties reinforce rather than suppress.",
        _s("i4_W", "education", [
            ("institutional exposure", "teacher approval", INC),
            ("teacher approval", "dialect spelling", INC),
            ("dialect spelling", "standard spelling", INC),
            ("standard spelling", "dialect spelling", INC),
            ("institutional exposure", "standard spelling", DEC)])),
    Doc("i4_V", "rivalry", "V", "general",
        "An external influence favours option A over B, while a reinforcing "
        "response gives A a further advantage.",
        _s("i4_V", "general", [
            ("external influence", "option A", INC),
            ("option A", "option B", DEC),
            ("option B", "option A", DEC),
            ("option A", "reinforcing response", INC),
            ("reinforcing response", "option A", INC)])),
    Doc("i4_U", "rivalry", "U", "radio_astronomy",
        "Dish alignment raises gain and resolution, while cloud water raises "
        "noise and lowers confidence in the source.",
        _s("i4_U", "rivalry_radio", [
            ("dish alignment", "signal gain", INC),
            ("signal gain", "spectral resolution", INC),
            ("cloud water", "atmospheric noise", INC),
            ("atmospheric noise", "source confidence", DEC),
            ("spectral resolution", "source confidence", INC)])),
)

INDEPENDENT_QUERIES = {"diversity": "i1_D", "correction": "i2_D",
                       "regulator": "i3_D", "rivalry": "i4_D"}

# The author's own judgement, transcribed. It named PARAPHRASE most similar and
# UNRELATED least in all four motifs, and did not rank the middle. So the only
# externally-supplied constraints are the two endpoints.
AUTHOR_MOST_SIMILAR = {m: "P" for m in INDEPENDENT_QUERIES}
AUTHOR_LEAST_SIMILAR = {m: "U" for m in INDEPENDENT_QUERIES}


def independent_docs_for(motif: str) -> list[Doc]:
    return [d for d in INDEPENDENT if d.motif == motif and d.kind != "D"]


def independent_query(motif: str) -> Doc:
    return next(d for d in INDEPENDENT if d.doc_id == INDEPENDENT_QUERIES[motif])


def independent_malformed() -> list[str]:
    return [d.doc_id for d in INDEPENDENT if not d.structure.is_well_formed]
