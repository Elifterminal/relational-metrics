# Relational Metrics

A measurement theory where the thing being measured is a **relational configuration** — participants, typed relations, context, higher-order structure, uncertainty — rather than a property of an isolated object.

**📊 [Read the study page →](https://elif1203terminal.github.io/relational-metrics/)**

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

### The three findings worth your time

**A tunable penalty doesn't scale results, it reorders them.** The inherited formula divides match quality by a mapping-complexity penalty. That penalty charges for asserting correspondence *across vocabularies* — so it charges most for exactly the cross-domain analogy the whole thing exists to find. Above η=0.22 a near-miss beats a true analogue. Nobody would blink at η=0.22.

**Description length removes the dial, structurally.** Reframe as: *does knowing A, plus a mapping, let me describe B in fewer bits than describing B from scratch?* The penalty stops being chosen and becomes the bits the mapping costs. Labels are never encoded at all, so cross-vocabulary translation **cannot** be charged for even in principle. Not tuned away — unavailable.

**A controlled experiment is blind exactly where it controls.** This one generalises past the project. Every condition in `EXP-000a` was matched on size, deliberately, to remove a confound. That control is what made a size bias in the replacement measure invisible — it was winning on volume, not on shared organisation — *and* made one cheating method undetectable. Both defects were found by widening a control. Neither was found by reasoning, and both formulas had been reasoned about at length.

## Honest limits

- One motif family. 5 nodes, 6 relations, **binary relations only**. The higher-arity structure the theory is actually about is completely untested.
- Four of five conditions hand-authored by the same party running the measure.
- Exhaustive mapping search. Nothing here speaks to whether any of it computes at scale.
- Rung 1 of 7 on the project's own evidence ladder ("mathematically coherent"). Rung 7 is "supports a broader physical interpretation" and is not currently reachable.
- One ground truth in here was **wrong** and is corrected in place rather than quietly fixed. How the error happened matters more than the row it corrupted.

## Running it

Python 3.12, standard library only. No dependencies, no network, no API calls.

```bash
cd lab
python3 run_exp000a.py     # the penalty pathology
python3 run_exp000b.py     # criticality blindness
python3 run_exp000c.py     # harness self-test — run this before trusting anything
python3 run_exp009.py      # cycle sign by typed composition

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
