"""Blind re-annotation of the independent corpus (Q-26).

Produced from the glosses alone, shuffled, with roles and motif membership
stripped. Same vocabulary as the sighted pass (POS / NEG) so the two are
comparable -- a vocabulary change would confound the thing being tested.

CONTAMINATION, restated where it will be read: I annotated this corpus sighted
some time ago. Hiding the labels does not erase that. The result is only
informative in the light of how far these structures DIVERGE from the sighted
ones, which is measured before the ranking is looked at.
"""

B = {
 "ffbff3371575": [("alignment", "gain", "POS"), ("gain", "resolution", "POS"),
                  ("cloud_water", "noise", "POS"), ("noise", "confidence", "NEG")],
 "a7296cf061b7": [("lamp_heat", "drying", "POS"), ("drying", "embrittlement", "POS"),
                  ("embrittlement", "cracking", "POS"), ("cracking", "repair", "POS")],
 "36415b02a2f4": [("lint_coverage", "defects", "NEG"), ("defects", "incidents", "POS"),
                  ("incidents", "fatigue", "POS"), ("fatigue", "release_frequency", "NEG")],
 "bbf892544cad": [("salt", "grass", "POS"), ("grass", "sedge", "NEG"),
                  ("grass", "saline_litter", "POS"), ("saline_litter", "grass", "POS")],
 "5476ae8f86a4": [("bats", "insects", "NEG"), ("insects", "leaf_damage", "POS"),
                  ("leaf_damage", "tree_stress", "POS"), ("tree_stress", "fruit_yield", "NEG")],
 "ce986e067c6b": [("influence", "option_a", "POS"), ("option_a", "option_b", "NEG"),
                  ("option_a", "response", "POS"), ("response", "option_a", "POS")],
 "c274ce9dc53d": [("temperature", "fluidity", "POS"), ("fluidity", "pooling", "POS"),
                  ("cooling", "crazing", "POS")],
 "12f36dd84141": [("foraging", "moths", "NEG"), ("moths", "canopy_feeding", "POS"),
                  ("canopy_feeding", "orchard_stress", "POS"),
                  ("orchard_stress", "fruit_set", "NEG")],
 "ae1222c0b638": [("runtime", "icing", "POS"), ("icing", "moisture_removal", "NEG")],
 "df02f0de27d6": [("suitable_seeds", "harvest_reliability", "POS"),
                  ("harvest_reliability", "members", "POS"),
                  ("members", "donations", "POS"), ("donations", "suitable_seeds", "POS")],
 "6bd7a643ca99": [("variety", "planting_fit", "POS"), ("planting_fit", "success", "POS"),
                  ("success", "participation", "POS"),
                  ("participation", "contributions", "POS"),
                  ("contributions", "variety", "POS")],
 "0dcd00e61d2f": [("deviation", "signal", "POS"), ("signal", "corrective_action", "POS"),
                  ("corrective_action", "counteracting_effect", "POS"),
                  ("counteracting_effect", "deviation", "NEG")],
 "9a620c750213": [("diversity", "options", "POS"), ("options", "outcomes", "POS"),
                  ("outcomes", "participants", "POS"), ("participants", "resources", "POS")],
 "7ff4863fdcb2": [("variety", "participation", "NEG"),
                  ("participation", "contributions", "POS"),
                  ("contributions", "planting_fit", "NEG")],
 "61228c752702": [("school_contact", "formal_orthography", "POS"),
                  ("formal_orthography", "vernacular", "NEG"),
                  ("praise", "formal_orthography", "POS")],
 "7bc1fb03d96e": [("exposure", "standard", "POS"), ("standard", "dialect", "NEG"),
                  ("dialect", "standard", "NEG"), ("approval", "standard", "POS")],
 "70e8f4350a5a": [("exposure", "approval", "POS"), ("approval", "dialect", "POS"),
                  ("dialect", "standard", "POS"), ("standard", "dialect", "POS")],
 "436a536e5623": [("safeguard", "hidden_problems", "NEG"),
                  ("hidden_problems", "disruption", "POS"),
                  ("disruption", "strain", "POS"), ("strain", "output", "NEG")],
 "1474ed1bb63c": [("humidity", "signal", "POS"), ("signal", "runtime", "POS"),
                  ("runtime", "moisture_removal", "POS"),
                  ("moisture_removal", "humidity", "NEG")],
 "8415b6ab55cf": [("humidity", "sensor_demand", "POS"),
                  ("sensor_demand", "drying", "POS"), ("drying", "extraction", "POS"),
                  ("extraction", "humidity", "NEG")],
 "e691d6ac79e4": [("fruit_yield", "insects", "POS"), ("insects", "bats", "POS"),
                  ("bats", "leaf_damage", "NEG"), ("leaf_damage", "tree_stress", "POS")],
 "a90e04254bd4": [("depletion", "quotas", "POS"), ("quotas", "effort", "NEG"),
                  ("effort", "harvest_pressure", "POS"),
                  ("harvest_pressure", "depletion", "POS")],
 "44b23f83a880": [("device_support", "users", "POS"), ("users", "bug_reports", "POS"),
                  ("bug_reports", "maintainers", "POS"),
                  ("maintainers", "device_support", "POS")],
 "c819a2dc1d16": [("ash", "abrasion", "POS"), ("abrasion", "tyre_wear", "POS"),
                  ("tyre_wear", "landing_risk", "POS"), ("landing_risk", "closures", "POS")],
}
