# Relational Metrics

A measurement theory where the thing being measured is a **relational configuration** — participants, typed relations, context, higher-order structure, uncertainty — rather than a property of an isolated object.

**📊 [Read the study page →](https://elifterminal.github.io/relational-metrics/)**

---

## The idea

Most measurement records properties of things. Temperature, mass, word count, embedding distance. Even when two things get compared, the comparison usually collapses into one number.

The motivating analogy is holography. A hologram beats a photograph not by collecting more light but by preserving *phase relationships* a photo throws away. Generalise that:

> A measurement gets deeper by preserving relations that conventional instruments collapse — not by adding sensors.

The second framing is a cadaver. Anatomy survives death; coordination doesn't. Most instruments measure the anatomy of a system and lose the conversation between its parts.

What that would buy, if it worked: ask about water erosion on an alluvial fan and get back not just geology, but blood-vessel channel formation, current finding the low-resistance path, traffic consolidating onto one route — because they share an organisation:

```
many paths → small advantage → more flow → more capacity → more flow
                                                └→ alternatives abandoned
```

Not because they share words. They don't.

## What's actually here

A laboratory and twenty-four experiments. Most results are findings about *method*; a few are
results about the subject matter, and the difference is tracked per claim rather than asserted for
the project as a whole — see **What currently survives** below.

Everything in this section is generated from [`manifest.json`](manifest.json), which is the single
source of truth for what has been run and what is currently claimed. `check_manifest.py` fails the
build if this file and the study page ever disagree, or if a retracted claim is presented as
current. That check exists because both happened.

<!-- BEGIN GENERATED: experiments -->
| Run | Question | Result |
|---|---|---|
| `EXP-000a` | Does the correspondence formula's penalty parameter matter? | It decides the **ranking**, not just the magnitude. Two reversals, first at η=0.22 |
| `EXP-000b` | Can the replacement tell which changes matter? | No. Five of six single-edge changes score identically |
| `EXP-000c` | Can the laboratory catch a cheat? | Yes — 7/7. And it caught a defect in the author's own measure |
| `EXP-009` | Can composing relation signs recover significance? | Not as asked. The question was malformed. But sign survives translation |
| `EXP-002` | **Does structure exist that no pair can see — and can we detect it?** | **It exists.** Best pair 0.0008 bits vs 0.7340 for the triple. But the statistic for it is demoted |
| `EXP-011` | Can a replacement separate synergy from redundancy? | **Yes.** Connected information places structure at the right order; redundancy drops from a false positive to 0.0003 |
| `EXP-012` | Can the replacement be broken? | Partly. The raw statistic reports a full bit of structure that has nothing to do with the question. The calibration is what makes it an answer |
| `EXP-010` | What does the observer actually choose, and what does it cost? | Everything. Six questions of one system give verdicts spanning three different orders — and hiding one participant erases a three-way dependence outright |
| `EXP-013` | Is that erasure general? | **No — and it corrects the previous entry.** Parity vanishes at every arity; AND, OR, majority and threshold all keep ~half. A gradient, not a wall |
| `EXP-014` | Is that "~half" real, or a coincidence? | **Both.** Exhaustive census of all 256 Boolean functions: retention is quantised to 7 values and 0.5 is a real class of 56. But the four measurements offered as evidence were two functions plus a noise artifact |
| `EXP-015` | Does it survive at four variables? | **Yes, and it has a closed form.** `retention = 1 − influence(hidden) / H(outcome)`, verified to 1e-16. 21 distinct values across all 65,536 functions |
| `EXP-016` | Does the law survive noise? | **The equation does; the ranking doesn't.** A general form is exact at every noise level, and balanced outcomes are exactly noise-invariant. But above ~5% noise the *order* of fragility changes |
| `EXP-017` | Which parameters reorder results? | **Four of five, including one believed safe.** "Retention" turns out to be one number *per participant you might lose* — best- and worst-case orderings are anti-correlated |
| `EXP-018` | Do the retention conclusions survive proper reporting? | **Mostly — one doesn't.** Quantisation and the 0.5 class hold. "Only parity vanishes" was a best-case artifact: 2 → 38 structures vanish under worst case |
| `EXP-019` | Add asymmetric test families | **Found an index-reversal bug on the first run** — one the old worlds were *provably unable* to detect. Also sharpened the diagnosis: influence-symmetry, not permutation-symmetry |
| `EXP-020` | Census asymmetry systematically | Asymmetry is quantised (10 profiles at k=3, 59 at k=4). **Nameable functions are influence-symmetric 1.8×–6.1× more often than the population, and the bias grows with arity** |
| `EXP-021` | Can anything here see *interaction* structure? | **The predictive law cannot — provably.** Two structures with identical retention predictions, one three-quarters pure pairwise, the other spread across every order |
| `EXP-022` | Are the two instruments *together* enough? | **At three participants yes, at four no.** The complete invariant is one number per subset — so "no single score" turns out to describe the subject matter |
| `EXP-023` | Is there a compact summary that *is* enough? | **No.** Best candidate leaves 2 collisions in 222. And a 16-number summary distinguishes 8 structures where a 20-number one distinguishes 217 |
| `EXP-005` | Does the correspondence measure work on shapes it wasn't built for? | **Yes, 5/5** — including an acyclic topology and an undesigned one. Making the test harder first exposed an unchecked container invariant |
| `EXP-024` | Search corpus + a real `d_A`. Does it retrieve? | **2 of 3 — best of four methods, short of the claim.** Loses by 0.0022 because it still charges the analogue for using a different domain's relation vocabulary |
| `EXP-025` | Fix it, and test on data frozen beforehand | **6 of 6.** Paraphrase and analogue now score *identically* — which is what a vocabulary-blind measure must do, and not what a fitted patch produces |
| `EXP-026` | A corpus nobody involved in the project wrote | **4 of 4 — the claim survives independent annotation.** And the *generic* document ties the analogue exactly, because it is isomorphic to the query <br>*(a sub-claim of this run — "generic document outranks the analogue on 3 of 4" — was **RETRACTED** by `EXP-027`)* |
| `EXP-027` | Does the genericness discount rescue the ranking? | **No — refuted by arithmetic.** Isomorphic structures have identical genericness (gap 0.00e+00), so no structural discount can separate them. Also **retracts** EXP-026's ranking sub-claim: it was a `hash()` tie-break, and the scores tie exactly. *(Premise corrected by EXP-035: the generics were isomorphic in MY annotation, not by authorship — 4/4 sighted but 2/4 blind)* |
| `EXP-028` | Q-21 — is the measure invariant across equivalent *re-encodings* of the same process? | **No — and blind, not merely biased.** At matched size it scores a correct re-encoding and a corrupted one **identically** (0/6 discriminated; the pairs are not isomorphic). The load-bearing claim survives 6/6 under the two known invariances and **2/6** under subdivision. Re-scopes `C-03` |
| `EXP-029` | Q-24 — does canonicalising before measuring restore representation invariance? | **Yes, exactly, within the class it declares.** Subdivision and mediation cost *nothing* after canonicalisation (6/6 exact recovery) and capability is preserved on all three corpora **including under subdivision, where EXP-028 had 2/6**. Rewrite system proven terminating, idempotent and confluent (24 orders each). `converse` and reification remain unaddressed. Also corrects two bugs of mine: EXP-028's subdivision was corrupting negative relations, and the first run blind-canonicalised relabelled structures |
| `EXP-030` | Does it work on an external benchmark — real narratives, outside ground truth, annotated blind? | **No signal** — abstains on 9/20 items, and 4/11 where it discriminates (p = 0.55). But the predeclared diagnostic settles whose failure it is: stripping MDL pricing entirely, the *annotation* favours the correct answer 3/20, ties 13/20, favours the distractor 4/20. **This measured the annotator, not the measure.** Shared shape is 42.8% on real analogies vs 81.7% on the project's own corpora |
| `EXP-031` | Does the recurring wall have a name — and can it be tested before building a measure? | **Yes to both.** Representation-relative non-identifiability: a *witness pair* — isomorphic structures, different required answers — proves no measure on that representation can work. Certified EXP-027 and EXP-029 as proofs, then found **three dead ends nobody had paid for** (magnitude, temporal order, provenance) and **one vacuous control**: EXP-000a has published weight-invariance since the first experiment, and F-06a never reads weights |
| `EXP-032` | Q-26 — does the corpus result survive BLIND re-annotation? | **The ordering survives; the magnitude does not.** Blind re-annotation (0/24 identical to sighted, so genuinely divergent) gives **3/4** against sighted 4/4. Corpus held constant, sighted annotation **inflates correspondence 1.34×** and drove paraphrase and analogue to a *perfect* 100% match vs 64.7% blind. But X (64.7%) still clears W (35.3%) — the record was flattered, not fabricated |
| `EXP-033` | Q-30 — does the blind result hold on the dev and held-out corpora too? | **Blind rate falls to 6/10 across all three corpora, from 10/10 sighted** (dev 2/3, held-out 1/3). But blind annotations of those two carry ~half the relations of the sighted ones, so the drop **mixes role-knowledge with annotation granularity and is not cleanly attributable**. Found two corpus defects: six false-friend glosses **announce their role in the prose**, and sighted structures give 4 relations to 9-word glosses — encoding organisation the documents do not contain |
| `EXP-034` | Q-28 — put relation weights into the comparison, and make the rescale control real | **Built.** Weights enter as log-weights normalised by geometric mean, so unit conversion is invariant *by construction* while relative coupling is visible (2.1168 vs 1.7160). **No claim-bearing result moved** — the predeclared requirement, since all corpus weights are 1.0. EXP-000a's rescale control can fail again and now **measures its own vacuity** each run. Also corrected EXP-031's witness pair (it differed only by a global factor) and the audit's own weight-blind equivalence test |
| `EXP-035` | Q-29 — why did the `diversity` motif invert under blind annotation? | **Its analogue was being carried by the sighted annotation — and this corrects EXP-027.** In 4/4 motifs the sighted vacuous document matches its query *exactly* on relation count and loop closure. In `diversity` my sighted annotation contains an edge **no sentence states**, and it is the one closing the loop. Vacuous ≅ query: **4/4 sighted, 2/4 blind** — so EXP-027's premise that the *author* wrote isomorphic generics was wrong. The theorem survives; F-09 stays refuted empirically rather than by impossibility (it can act on 1/4 blind, helps on 0/4) |
| `EXP-036` | Q-31 — control annotation granularity with a deterministic annotator | **My control failed** — the extractor was too weak (1.52 relations/sentence vs 4.2, couldn't parse 2 of 10 queries, **0 of 60** granularity matches), so 5/8 is uninformative exactly as predeclared. **But the check it prompted is the finding**: blind 6/10 is **p = 0.754, not significant**; 3/4 is p = 0.63. The only annotation mode producing a significant result (p = 0.002) is the one where the annotator knew the answers. *(Conclusion amended by EXP-038: on the MARGIN rather than the win count the blind result is significant, though fragile. EXP-036 was true of the test it ran and false of the data)* |
| `EXP-037` | Q-35 — how many test cases would actually settle the retrieval claim? | **At n=10 nothing below 9/10 is significant**, and a genuinely 75%-accurate measure would be missed 3 times in 4. Our 6/10 spans **26–88%** — it contains chance and a strong effect alike. A yes/no test at the observed rate needs **199 motifs**. **But the binary count discards the margin the corpus already holds**: on blind data those margins give d = 0.842 and need about **12 motifs**. The evidence was not weak — the summary was |
| `EXP-038` | Q-36 — report the margin instead of the win count | **Partly un-says EXP-036.** Same blind data: mean margin **+0.1808 bits**, 95% CI **[+0.019, +0.343]** excluding zero, t *p* = 0.032, Wilcoxon *p* = 0.043 — significant on both. **But fragile**: leave-one-out survives only 5/10, worst case *p* = 0.070. Sighted effect size 2.045 vs blind 0.799 — inflation of **2.6×**, larger than the 1.34× measured on rates. So the effect is real AND it was inflated. Analysis chosen **post-hoc**; flagged, not excused |
| `EXP-039` | Does an independent annotator, told nothing, reproduce the retrieval effect? | **Effect size 0.788 — within 1.5% of my blind 0.799 and 39% of my sighted 2.045.** So `R-18` is confirmed from outside at **~2.6× inflation**, and the effect underneath is **real**. Both tests significant (t 0.046, Wilcoxon 0.043), CI excludes zero — **but leave-one-out survives 3/9, so FRAGILE, NOT ESTABLISHED** per the plan locked at `6a9aa8e` before any computation. Four advance predictions, four correct. The annotator declined 8 documents outright; I never once did across the same 60 |
| `EXP-040` | Q-38/Q-34 — which relations did I invent, measured against an independent annotator? | **I was annotating to a template.** My sighted pass **never used fewer than 4 relations on any of 60 documents** (80% exactly 4); the independent annotator ranged 0–5 with its mode at 25%. I wrote more on **49 of 60** and fewer on **zero**. My sighted counts tracked sentence length *less* (+0.57) than my own blind counts (+0.79). On all 6 documents they refused entirely, I wrote exactly 4. One measured mechanism behind EXP-035's invented edge, EXP-032's 2.6× inflation and EXP-033's 9-word glosses |
| `EXP-041` | Q-27 — can the representation express an ARN analogy at all, before building an annotator? | **Yes — PROCEED.** Correct answer and distractor are typed-isomorphic on **0 of 20** items (95% CI 0–0.168); untyped 2/20. And the confound points the safe way: a four-relation template *flattens* structures together, so a low rate is trustworthy where a high one would not be. **EXP-030's failure was the annotator, not the representation** — agreeing with EXP-040. But distinctness is a weak bar: it clears identifiability and shows nothing about whether a good annotator exists. 3/3 predictions |
| `EXP-042` | Can a fully automatic rule-based annotator read real narrative prose? | **No — and the test did not even run.** 69% of passages produced nothing; **30 of 30 items excluded**. Charter falsification 3, no claim either way about the measure. I predicted failure in writing beforehand but predicted the *wrong mode* — expected a signal-free result, got one with no result at all. Establishes the floor any Stage 2 annotator must beat. Deliberately NOT hand-tuning the extractor against a benchmark whose answers I know — that would be the same bias in a new costume |
| `EXP-044` | What specifically makes narrative prose hard to annotate, versus the glosses that worked? | **The causation isn't written down.** In these narratives **88% of sentences contain no causal verb at all**, and explicit causal vocabulary is **22× rarer per word** than in the glosses. Pronouns 10× denser, names 5× denser. **Clauses per sentence does NOT separate them** — the difficulty is not syntactic. A reader must infer unmarked causation, resolve reference across sentences, and abstract named individuals into roles. Explains EXP-042 completely. The planned length-matched arm **could not run** (2 glosses in the overlap window) and is reported as untested |

### What currently survives

*Present tense, generated from `manifest.json`. The table above is the history; this is the state.*

**ACTIVE WITHIN TESTED SCOPE**

- **Higher-order dependence can exist that no pairwise view contains, and it is detectable.** · rung 2  
  *scope*: small discrete Boolean configurations, exhaustively enumerated  
  *evidence*: `EXP-002`, `EXP-011`, `EXP-012`
- **Connected information locates the order at which dependence appears.** · rung 2  
  *scope*: k<=4 discrete variables; requires an outcome-permutation calibration to be an answer  
  *evidence*: `EXP-011`, `EXP-012`
- **Structural correspondence cannot distinguish cases whose representations are isomorphic — a general limit, not a defect of this measure.** · rung 3  
  *scope*: representation-relative non-identifiability (EXP-031). Proved by witness pair for: analogue vs vacuous restatement, participant vs mediator, strong vs negligible coupling, delay-driven behaviour, asserted vs observed. Level 1 in the three-level hierarchy — no stronger observer or algorithm helps. Distinct from the Ugly Duckling / observer-relative shape of C-02 and P-01  
  *evidence*: `EXP-026`, `EXP-027`, `EXP-029`, `EXP-031`
- **Retention obeys an exact closed form: 1 - influence(hidden)/H(outcome).** · rung 2  
  *scope*: verified to 1e-16 over all 65,536 functions at k=4; a robustness law, NOT a measure of how participants jointly organise  
  *evidence*: `EXP-015`, `EXP-016`, `EXP-021`
- **Relational structure is not reducible to a scalar, nor to a pair of profiles.** · rung 2  
  *scope*: at k=3 the two profiles suffice; at k=4 they do not. The complete invariant is one number per subset  
  *evidence*: `EXP-022`, `EXP-023`
- **Canonicalising before measuring restores exact invariance under a DECLARED typed graph-homeomorphism relation, at no cost to capability.** · rung 2  
  *scope*: subdivision and suppression of degree-2 vertices only. Exact (cost 0, 6/6 recovery); capability 3/3, 3/3, 4/4 including under subdivision. Rewrite terminating, idempotent, confluent. NOT converse or reification (Q-25). And the equivalence must be DECLARED — blind suppression damages 5/6 structures, because whether a vertex is representational is not decidable from structure  
  *evidence*: `EXP-029`
- **The corpus results measure a real analogy-detection effect AND were inflated by annotation — both, now separably.** · rung 3  
  *scope*: SETTLED by EXP-039. An independent annotator with no stake recovers effect size 0.788 against my sighted 2.045, so there is a real effect and my sighted annotation inflated it ~2.6×. The answer was never one or the other. What remains unsettled is whether the effect is large enough to be useful — 9 motifs is fragile under leave-one-out  
  *evidence*: `EXP-030`, `EXP-032`, `EXP-033`, `EXP-039`
- **The measure is invariant to unit conversion of relation weights.** · rung 2  
  *scope*: REPAIRED by EXP-034. Was vacuous — the measure did not read weights, so it could not fail the test. Weights now enter normalised by geometric mean, making rescaling invariant by construction while relative coupling is visible. The control now measures its own capacity to fail each run. Untested on data where weights actually vary (Q-33) — a capability, not yet a result  
  *evidence*: `EXP-031`, `EXP-034`

**PROVISIONAL**

- **MDL correspondence ranks a cross-domain analogue above a same-vocabulary false friend.** · rung 3  
  *scope*: INDEPENDENTLY ANNOTATED (EXP-039): effect size 0.788, mean margin +0.165 bits, 95% CI excluding zero, both tests p<0.05 — but leave-one-act survives 3/9, so **fragile, not established** by the pre-locked rule. Sighted annotation inflates 2.6× (2.045 vs 0.788), confirmed from outside. Remaining exposure is SAMPLE SIZE not bias: 9 motifs where EXP-037 called for ~30 (Q-32). Holds within a fixed representation convention (EXP-028), restored under subdivision once canonicalised (EXP-029). No signal on an external benchmark annotated blind, because that annotation carries none (EXP-030)  
  *evidence*: `EXP-024`, `EXP-025`, `EXP-026`, `EXP-027`, `EXP-028`, `EXP-029`, `EXP-030`, `EXP-032`, `EXP-033`, `EXP-036`, `EXP-037`, `EXP-038`, `EXP-039`
- **The correspondence measure transfers to topologies it was not developed against.** · rung 2  
  *scope*: 5/5 base topologies including one acyclic and one undesigned. Untested across SCALE and across equivalent re-encodings of the same process  
  *evidence*: `EXP-005`

**UNTESTED**

- **Any of this reaches a claim about physical reality.**  
  *scope*: unsupported and not currently testable. Prediction P6 says it will not, and P6 stands  
  *evidence*: —

**DEMOTED / REPLACED**

- **The higher-order remainder statistic measures synergy.**  
  *scope*: conflated synergy with redundancy; replaced by connected information (C-02)  
  *evidence*: `EXP-002`, `EXP-011`

**REFUTED / RETRACTED**

- **The measure is invariant to how the same process is legitimately re-encoded (mediator nodes, hyperedge vs factor node, subdivision, converse relations).**  
  *scope*: refuted. Content-preserving and content-changing transforms produce OVERLAPPING score ranges, and at matched size the measure returns identical values for a correct re-encoding and a corrupted one. Cause: the mapping space cannot match a relation to a path, and gains freedom as the target grows. Partially repaired by EXP-029 for the subdivision class via canonicalisation (C-12); converse and reification still unaddressed  
  *evidence*: `EXP-028`
- **F-09 bridge value: discounting a match by genericness defends against the attractive-nonsense failure.**  
  *scope*: refuted EMPIRICALLY, not by impossibility. EXP-027 argued the discount can never act because the structures are isomorphic; EXP-035 showed that isomorphism was largely annotator-supplied (4/4 sighted, 2/4 blind). Blind, the discount CAN act on 1/4 motifs — and helps on 0/4, making one motif worse. So: still refuted, on weaker grounds than published  
  *evidence*: `EXP-027`, `EXP-035`

```bash
cd lab
python3 run_exp000a.py   # the penalty pathology
python3 run_exp000b.py   # criticality blindness
python3 run_exp000c.py   # harness self-test — run this before trusting anything
python3 run_exp009.py    # cycle sign by typed composition
python3 run_exp002.py    # higher-order recovery -- the arity claim
python3 run_exp011.py    # the replacement measure, connected information
python3 run_exp012.py    # adversarial stress test of the replacement
python3 run_exp010.py    # the observer's three choices, measured
python3 run_exp013.py    # is the partial-observation cliff general?
python3 run_exp014.py    # exhaustive census, all 256 functions of 3 variables
python3 run_exp015.py    # k=4 census + the closed form, verified
python3 run_exp016.py    # the law under noise, and where it stops being safe
python3 run_exp017.py    # the reordering audit -- which parameters change the ranking
python3 run_exp018.py    # retention re-reported per participant
python3 run_exp019.py    # asymmetric families -- and the bug they caught
python3 run_exp020.py    # systematic census by influence profile
python3 run_exp021.py    # interaction structure census -- what the law cannot see
python3 run_exp022.py    # are the two instruments together complete?
python3 run_exp023.py    # is there a minimal sufficient summary? (no)
python3 run_exp005.py    # cross-generator transfer -- does it work on unseen shapes?
python3 run_exp024.py    # the search corpus, d_A, and does it actually retrieve?
python3 run_exp025.py    # the fix, tested on a corpus frozen before it existed
python3 run_exp026.py    # the independent corpus -- nobody here wrote it
python3 run_exp027.py    # the retraction, and F-09 refuted by arithmetic
python3 run_exp028.py    # representation invariance -- the measure sees the encoding
python3 run_exp029.py    # canonicalise before measuring -- subdivision invariance, exactly
python3 run_exp030.py    # ARN benchmark, annotated blind -- and what it reveals about annotation
python3 run_exp031.py    # the expressivity boundary audit -- test before you build
python3 run_exp032.py    # blind re-annotation -- how much did knowing the answer help?
python3 run_exp033.py    # blind protocol on dev + held-out, and two corpus defects
python3 run_exp031.py    # the magnitude channel, and a control that can fail again
python3 run_exp032.py    # why diversity inverted -- and an edge the text never stated
python3 run_exp036.py    # a failed control, and the significance test that mattered
python3 run_exp037.py    # power analysis -- and the information the binary test threw away
python3 run_exp038.py    # margins, not coin flips -- and a fragile positive
python3 run_exp039.py    # the second annotator -- real, inflated, and fragile
python3 run_exp040.py    # the template floor -- one mechanism behind four findings
python3 run_exp041.py    # Stage 2 pre-test -- is the distinction even in the representation?
python3 run_exp042.py    # rule-based reader on real prose -- predicted failure, run anyway
python3 run_exp044.py    # why prose is hard -- the causation is never stated

cd ..
python3 render/figures.py     # regenerate the SVGs
python3 render/dashboard.py   # rebuild the study page
python3 gen_docs.py           # regenerate this README from manifest.json
python3 check_manifest.py     # FAILS if any of the above has drifted
```
<!-- END GENERATED: experiments -->

### The findings worth your time

**Structure that no pair can see is real.** In a world where the outcome is `a XOR b XOR c`,
every pair of variables carries **0.0008 bits** about the outcome — nothing — while the three
together carry **0.7340**. Decompose that into pairwise relations and the thing you were
measuring is gone, not approximated. This is the claim the whole project rests on and it is now
measured rather than argued.

**The statistic written down to detect it didn't work.** Predeclared falsification condition,
fired. Above two variables the remainder conflates *synergy* (the configuration does something
the parts can't) with *redundancy* (several parts carry the same information). Make three
variables exact copies of each other — zero synergy by construction — and it returns the maximum
possible value.

**Reading the literature beat inventing a fix.** The obvious replacement was partial information
decomposition. Reading it first revealed that for three or more sources, antichain-lattice PID is
*provably impossible* — the desired axioms are mutually incompatible and two systems can carry
identical atoms with different mutual information. That route was a proved dead end. The
construction that does work sits outside the impossibility: connected information via a
maximum-entropy hierarchy. Redundancy is fully visible in low-order marginals, so it lands at
order 2 where it belongs; genuine higher-order structure is exactly what low-order marginals
cannot reproduce. The false positive drops from 0.0876 to 0.0003, and the *order* of a dependence
is read off rather than assumed.

**A tunable penalty doesn't scale results, it reorders them.** The inherited formula divides match quality by a mapping-complexity penalty. That penalty charges for asserting correspondence *across vocabularies* — so it charges most for exactly the cross-domain analogy the whole thing exists to find. Above η=0.22 a near-miss beats a true analogue. Nobody would blink at η=0.22.

**Description length removes the dial, structurally.** Reframe as: *does knowing A, plus a mapping, let me describe B in fewer bits than describing B from scratch?* The penalty stops being chosen and becomes the bits the mapping costs. Labels are never encoded at all, so cross-vocabulary translation **cannot** be charged for even in principle. Not tuned away — unavailable.

**A controlled experiment is blind exactly where it controls.** This one generalises past the project. Every condition in `EXP-000a` was matched on size, deliberately, to remove a confound. That control is what made a size bias in the replacement measure invisible — it was winning on volume, not on shared organisation — *and* made one cheating method undetectable. Both defects were found by widening a control. Neither was found by reasoning, and both formulas had been reasoned about at length.

**Structure is objective; relevance is not.** Attacking the new measure found that it fires
at full strength on structure existing purely among the participants, with the outcome an
independent coin flip — true statements that are not answers. What separates them is the
permutation calibration, which shuffles only the outcome and so leaves participant structure in
the null. Whether structure is *present* is a fact about the joint distribution, provably
indifferent to which variable you nominate as the outcome. Whether it *counts as an answer*
depends on the question. The project's founding axiom — relational completeness belongs to
reality, relational selectivity belongs to observers — was written as a philosophical commitment
and came back out of the arithmetic as a measurement.

**Partial observation costs you in proportion to how purely synergistic the structure is.**
Hide one participant of a *parity* dependence and the measured structure goes from 0.7246 to
**0.00000** — not weakened, gone — and five times the data moves it to 0.00006. That is an
identifiability limit, not a power limit, and it holds at three, four and five participants.

But parity is the worst case *by construction*: it is built so that no subset of its inputs
carries any information. AND, OR, majority and threshold functions all retain roughly **half**
their information under identical treatment, and sweeping a participant from irrelevant to
essential traces a smooth curve rather than a step. So the constraint is real but bounded, and
what you lose to incomplete observation is predictable from how much of the structure lives in
the parts. This log first stated the pessimistic version and then corrected it; both are left
visible.

**And significance cannot be defined without naming a question.** One fixed system of
participants, asked six legitimate questions, returns verdicts spanning three different orders.
The only outcome-invariant structure is the participants' internal structure — which is exactly
what the calibration correctly rejects as not being an answer to anything. There is no third
thing. That is a property of the subject matter, not a gap in the instrument.

**And it reduces to an equation.** What you lose by not observing a participant turns out to be
exactly that participant's *influence* — a standard quantity in Boolean function analysis, the
fraction of input pairs on which flipping it changes the answer — divided by the entropy of the
outcome:

```
retention  =  1  −  Influence(hidden participant) / H(outcome)
```

Verified against brute-force exact mutual information on every function at three variables and a
spread sample at four: maximum error 1.1e-16. Under noise it generalises to
`retention = 1 − Influence·(1−h(e)) / (H_e − h(e))`, also exact to ~1e-16 — and **balanced
outcomes turn out to be exactly noise-invariant** (drift 0.00e+00), which is why some structures
held steady across noise levels and others drifted. The catch: above about 5% noise the *ordering*
of which structures are most fragile changes, so the clean-case law is not a safe proxy for
ranking candidates in the field. It explains the quantisation (both terms take
discrete values), why parity is the unique zero (it is the only function where every participant
has maximal influence), why one half is a real class, and the anomalous 0.5401. Not a new
mathematical result — which is the point. It is a bridge from this project's question to work
that already exists, and both terms are computable from the structure *before* any measurement.

**Reordering is the default here, not the exception.** Auditing every nuisance parameter for
whether it changes the *ranking* rather than the values: four of five do. The sharpest is that
best-case and worst-case retention rank structures slightly **anti**-correlated (−0.117), so
"retention" is one number per participant you might lose, not one number — and any claim that one
structure is more fragile than another is incomplete without saying which participant is missing.
The audit also broke its own positive control, showing an earlier code-stability claim had been
tested on a condition set that lacked the case which breaks it. Rankings are now reported as
curves over the nuisance parameter by default.

**And one conclusion didn't survive being re-reported properly.** "Parity is the only structure
that vanishes" was an artifact of taking a best case. Under worst-case reporting, the number of
structures losing *everything* goes from 2 to 38 at three participants and 2 to 942 at four. The
corrected claim — parity is unique in vanishing *whichever* participant you lose — is narrower and
considerably more alarming. The earlier tables came out unscathed only because every function
family tested was **symmetric**, which is now the third correction traceable to symmetric test
choices.

**A test set can be provably unable to detect a class of error.** Adding function families whose
participants genuinely differ in importance exposed an index-reversal bug on the first run — two
conventions for "participant *j*" that disagreed. No published number was affected, because every
result so far was a best or worst case and aggregating over participants makes a reversal
invisible. But that is the point: under the old worlds, the check passes whether or not the
indices are reversed, because reversing a list of identical values changes nothing. Coverage isn't
the only thing a condition set can lack — it can lack the *capacity to fail*.

The diagnosis sharpened too. A multiplexer is not permutation-symmetric at all, yet all its
participants have equal influence and its spread is exactly zero. **What matters is
influence-symmetry, not permutation-symmetry.**

And a systematic census showed the bias was **structural, not careless**. Functions you can name
in English are influence-symmetric 70% of the time against 38.6% of the population at three
participants, and 67% against **10.9%** at four — an over-representation of 1.8× rising to 6.1×,
growing with arity. At three participants the entire nameable list is symmetric. Being more
thoughtful about which examples to choose would have made it *worse*, because the thoughtful
choices are the canonical ones. The fix is to build condition sets by **enumerating the property
under test** rather than by collecting examples.

**And the predictive law turns out to be a robustness law, not a structure law.** Influence is a
*marginal* of the full interaction structure, so retention — which depends on influence and
outcome entropy and nothing else — is blind to how participants interact with each other. Two
structures can share an influence profile and an entropy, giving *identical* retention predictions
to the last decimal, while one puts three quarters of its organisation at order 2 with nothing at
orders 1 or 3 and the other spreads evenly across all of them. There are 2 such groups at three
participants and 45 at four.

That lands on the thesis rather than beside it: this project exists because configurations are
supposed to carry structure their parts do not, and its one predictive equation cannot see
interaction order at all. Both things are true — the law is exact and useful, and it is not a
measure of relational organisation. Connected information has the mirror-image blindness (it sees
order, not which participant carries what), which suggests the honest instrument is the pair, and
that a single scalar for "relational structure" was never available.

**And together they are sufficient only below a threshold.** If two structures agree on both the
influence profile and the interaction-order profile, must they be the same structure? At three
participants: **yes**, verified two independent ways. At four: **no** — 8 of 194 profile pairs
contain more than one genuinely distinct structure. The witness has every participant equally
important and an identical order distribution, while one concentrates its whole organisation into
four participant-subsets and the other spreads the same total across ten.

So *"relational structure = participant importance + interaction order"* is a valid decomposition
only for small configurations. Past that it is provably lossy, and the complete invariant is the
full subset-indexed spectrum — one number per subset of participants, 2^k of them.

Which makes this project's founding rule — that a measurement must never be collapsed into a
single score — **not a matter of taste**. It was written as a discipline against premature
compression, and it turns out to describe a property of the subject matter, with an arity
threshold attached.

**And no compact summary replaces it.** The pair turns out to be exactly the two *marginals* of a
joint matrix — how much of each participant's importance sits at each interaction order — so
"the pair is insufficient" is precisely "these marginals lose the joint", which is this project's
own thesis arriving one level up about its own instruments. The joint gets to 217 distinct values
against 222 real structures: **2 collisions left, and still not complete.**

The lesson that generalises: **more numbers is not more information.** The spectrum multiset
writes down 16 numbers and distinguishes 8 structures; the joint matrix writes down 20 and
distinguishes 217. Combining them changes the answer by nothing at all. Which numbers you keep
matters enormously more than how many.

**The correspondence measure transfers.** Every earlier result about it rested on the one
structure family it was developed against — an n=1 doubt that every downstream application would
have inherited. Tested on five base topologies chosen against a property list (cycles, branching,
degree concentration, path multiplicity, and one nobody designed), with conditions derived
identically from each so the only variable is the shape: **the graded ordering holds on all five**,
stable across all three description codes.

Getting there took making the test harder. The first version used only a perfect analogue and two
wrong answers and passed 4/4 — which should have been suspicious, since a perfect isomorph of
matched size compresses the same way on any topology. Adding a near-miss turned it into a question
about *degrees* of correspondence, and one topology promptly failed. The cause wasn't the measure:
a generator had emitted two relations between the same pair differing only in type, flipping one
made them identical, and because relations live in a set the duplicate **silently collapsed** —
the structure reported six relations and had five. **Nothing had checked that invariant in
twenty-three experiments**, because every earlier world was hand-built and hand-built worlds don't
have parallel edges. The container now asserts it.

**And on something resembling an application, it falls short.** A hand-annotated corpus — three
structurally distinct motifs, six documents each, including a *false friend* that shares the
query's entire vocabulary with different structure. The measure beats every baseline (word overlap
puts the false friend **first** on every query) but gets **2 of 3** on the comparison that matters.

The cause is exact: on the failing motif the analogue scores 1.8586 and the false friend 1.8608 —
a margin of **0.0022**, entirely from mapping cost. The analogue pays for two relation-type
substitutions because it uses a different domain's vocabulary for its relations, and is charged
for saying so. **That is the same pathology that demoted the original formula**, fixed for
participant labels (never encoded at all) and never fixed for relation-type labels. It survived
twenty-four experiments and only surfaced when two structures came close enough for two bits to
decide the answer.

**The fix now holds on held-out data.** A second corpus — three new motifs, structurally distinct
from the first — was written and **committed before the fix existed**, then the change landed
(charge for *specifying* the relation-type map, never for whether the names coincide), regressions
were re-run, and both corpora were scored once. **Six of six.** Harness still catches 7/7
impostors; transfer still 5/5.

The number that says it's real rather than tuned: **paraphrase and analogue now score identically
— 0.0000 apart, in all six motifs.** They are structurally the same thing wearing different words,
so a measure that genuinely ignores vocabulary *must* return the same number for both. A fitted
patch would not produce that.

It also exposed a seventh wrong ground truth: the corpus had declared that a same-domain
paraphrase should outrank a cross-domain analogue, which **contradicts this project's own thesis**.
The ideal is now stated as tiers with those two tied. Noticed from the data, so labelled post-hoc,
though derivable from the thesis without looking at any result — and it doesn't touch the headline,
which held before and after.

Still imperfect: only 1 of 3 motifs is *fully* ordered on each corpus. The measure knows a false
friend is wrong but doesn't reliably know it's *more* wrong than an unrelated document.

**Then an independent corpus.** Commissioned from a separate system given only a format spec — no
hint of what was being tested — and frozen before it ran. **The claim holds 4 of 4**, with
paraphrase and analogue tying again on annotations nobody here produced.

**And the generic document ties the analogue exactly — structurally correctly.**
*(This originally read "outranks the analogue on 3 of 4". That was **RETRACTED** by
`EXP-027`: the ordering came from a `sorted()` tie-break on Python's per-process-salted
`hash()`, and the scores are equal in the last bit. The reasoning below is unchanged — the
generic is isomorphic to the query, so an exact tie is the correct answer.)* Its
structure is a four-cycle with three increases and one decrease closing the loop, which is
*isomorphic to the query*; the real analogue has its decrease in a different position and matches
slightly less exactly. A vacuous statement can have perfect structure. "Systems change, factors
influence outcomes" describes a feedback loop exactly as accurately as any real one, because it
describes nothing else.

That is **risk one**, logged before any code existed — *a relational framework can relate anything
to anything and kills the project by succeeding*. Its defence was a bridge measure discounting
genericness. It was never built. **Genericness is not a structural property and cannot be detected
structurally**, so no further work on correspondence can fix it.

`d_A` itself is a **vector over named failure modes**, each traceable to a principle that predates
it — a real relation missing, a relation asserted too strongly, an analogy sold as a mechanism, a
result at the wrong relational distance. Pareto dominance replaces a fabricated total, and where
neither of two results dominates, saying they are incomparable beats inventing weights.

## Honest limits

- Small worlds throughout: 5 participants, one motif family for the correspondence work, binary variables for the arity work. Arity 4 and above is untouched and the algebra gets worse there, not better.
- Four of five conditions hand-authored by the same party running the measure.
- Exhaustive mapping search. Nothing here speaks to whether any of it computes at scale.
- Rung 1 of 7 on the project's own evidence ladder ("mathematically coherent"). Rung 7 is "supports a broader physical interpretation" and is not currently reachable.
- **Six** ground truths or test constructions in here were wrong, all mine, all corrected in place rather than quietly fixed — including a pure-noise control that turned out to be a deterministic function of the variables it was meant to be independent of. Each was caught by computing something previously asserted from inspection. The running count is the honest measure of how often careful reasoning about one's own constructions is simply wrong.

## Running it

Python 3.12, standard library only. No dependencies, no network, no API calls.
The run list is generated above, in **What currently survives**.


Any new measure enters through `run_exp000c.py`'s six controls before it gets discussed.

## Layout

```
lab/
  structure.py       immutable typed relational structures
  codes.py           description-length codes (three variants, declared in advance)
  mapping.py         exhaustive search over candidate correspondences
  measures.py        the two correspondence measures, side by side
  composition.py     cycle sign by composing relation polarity
  interaction.py     the higher-order remainder + permutation calibration
  maxent.py          connected information via maximum-entropy hierarchy (IPF)
  stressworlds.py    adversarial worlds built to break the measure
  asymworlds.py      families whose participants differ in importance
  fourier.py         Walsh-Fourier spectrum: interaction structure by order
  generators.py      five structurally distinct base topologies
  corpus.py          the annotated search corpus -- 3 motifs, 18 documents
  d_a.py             d_A: a vector over named failure modes
  corpus_holdout.py  held-out corpus, frozen before the fix landed
  corpus_independent.py  independent corpus, commissioned and frozen
  hyperworlds.py     synthetic worlds with a KNOWN interaction order
  worlds.py          the condition set — A/B/C/D/E/F plus a held-out case
  impostors.py       seven deliberately cheating methods
  run_exp*.py        the experiments
render/              SVG + study page generators (no plotting library)
results/             raw JSON output
docs/                the published study page
```

## Why the impostors exist

A relational framework can relate anything to anything if the criteria are loose enough. That's the characteristic failure of this family of ideas, and it usually kills the project *by succeeding* — producing striking, plausible, well-visualised connections that are worthless.

So before any measure is trusted, seven methods that cheat get built and the controls have to catch all of them. They aren't strawmen; each is a shortcut a real implementation could take by accident. The first version of the battery caught six, and fixing the seventh is what exposed the defect in the real measure.

## License

MIT. See [LICENSE](LICENSE).
