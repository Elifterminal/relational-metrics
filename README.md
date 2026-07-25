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

A laboratory and four experiments. **Every result so far is a finding about method, not evidence that relational measurement works.** That distinction is load-bearing and the code enforces it.

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
spread sample at four: maximum error 1.1e-16. It explains the quantisation (both terms take
discrete values), why parity is the unique zero (it is the only function where every participant
has maximal influence), why one half is a real class, and the anomalous 0.5401. Not a new
mathematical result — which is the point. It is a bridge from this project's question to work
that already exists, and both terms are computable from the structure *before* any measurement.

## Honest limits

- Small worlds throughout: 5 participants, one motif family for the correspondence work, binary variables for the arity work. Arity 4 and above is untouched and the algebra gets worse there, not better.
- Four of five conditions hand-authored by the same party running the measure.
- Exhaustive mapping search. Nothing here speaks to whether any of it computes at scale.
- Rung 1 of 7 on the project's own evidence ladder ("mathematically coherent"). Rung 7 is "supports a broader physical interpretation" and is not currently reachable.
- **Six** ground truths or test constructions in here were wrong, all mine, all corrected in place rather than quietly fixed — including a pure-noise control that turned out to be a deterministic function of the variables it was meant to be independent of. Each was caught by computing something previously asserted from inspection. The running count is the honest measure of how often careful reasoning about one's own constructions is simply wrong.

## Running it

Python 3.12, standard library only. No dependencies, no network, no API calls.

```bash
cd lab
python3 run_exp000a.py     # the penalty pathology
python3 run_exp000b.py     # criticality blindness
python3 run_exp000c.py     # harness self-test — run this before trusting anything
python3 run_exp009.py      # cycle sign by typed composition
python3 run_exp002.py      # higher-order recovery -- the arity claim
python3 run_exp011.py      # the replacement measure, connected information
python3 run_exp012.py      # adversarial stress test of the replacement
python3 run_exp010.py      # the observer's three choices, measured
python3 run_exp013.py      # is the partial-observation cliff general?
python3 run_exp014.py      # exhaustive census, all 256 functions of 3 variables
python3 run_exp015.py      # k=4 census + the closed form, verified

cd ../render
python3 figures.py         # regenerate the SVGs
python3 dashboard.py       # rebuild the study page
```

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
