# Pre-specified analysis plan — second-annotator data (Q-37)

**Written**: 2026-07-26, after all 60 annotations were received, **before any computation.**

## Exactly what is and is not compromised

Honest statement of position, because overstating this would be worse than not having it:

- I **have seen** all 60 raw annotation strings.
- I have **not** looked up which passage id corresponds to which document, role or motif.
- I have **not** computed a single correspondence, margin, test or count.
- This file is committed **before** the first line of analysis code runs.

**This is therefore NOT pre-registration on unseen data.** It is an analysis plan locked before
computation, with the raw text seen. That is weaker, and it is the strongest position still available
once the data has arrived. `Q-37` asked for the stronger version and I did not get it in time —
the annotations landed while I was still writing about intending to.

## Primary statistic

**Mean margin in bits**, per motif:

```
margin = correspondence(query, analogue) − correspondence(query, false_friend)
```

Chosen because `EXP-037` showed the binary win count needs ~199 motifs where margins need ~12, and
`EXP-038` applied it. The win count is reported as a **footnote only**.

## Tests, fixed in advance

- **two-sided** one-sample t-test against zero, and **two-sided Wilcoxon signed-rank**
- **both** must give *p* < 0.05 for the result to count as supported. Either alone is "suggestive"
- two-sided although the direction is predicted, matching `EXP-038`, and costing a factor of two
- 95% confidence interval on the mean margin reported regardless of *p*

## Exclusions, declared now because they will matter

Several annotations are empty (`no influence stated`). Declared before looking at which:

- a motif is **excluded** if the query, the analogue **or** the false friend has zero relations
- the number excluded, and which kinds they were, is **reported**
- exclusions are **not** replaced, and the reduced n is used in every test

## Robustness, required not optional

**Leave-one-out** on the surviving motifs. Reported as "significance survives k of n".

- survives **< 50%** → reported as **fragile, not established**, whatever the headline *p*
- this is the check that tempered `EXP-038` and it applies identically here

## Comparisons

Second annotator's margins against: my **sighted** margins (d = 2.045) and my **blind** margins
(d = 0.799). Both already published, so neither can be adjusted after the fact.

## What would falsify the retrieval claim

Any of the following, and each is a real outcome I am committing to report as such:

1. mean margin **≤ 0** — the analogue does not beat the false friend under independent annotation
2. either test at *p* ≥ 0.05 — not supported, only suggestive
3. leave-one-out survival below half — fragile
4. more than half the motifs excluded for empty annotations — **the test did not run**, and no
   claim either way

## My predictions, so they can be wrong

1. mean margin **positive but smaller** than my sighted 2.045 effect size. *Confidence: high* — the
   whole point of `R-18` is that my sighted numbers are inflated.
2. effect size **comparable to or below** my blind 0.799. *Confidence: medium.*
3. significance **marginal or absent**, because n will be ~10 minus exclusions and `EXP-037` said 12
   is the floor. *Confidence: medium-high.*
4. the second annotator will produce **fewer relations per document** than my sighted annotation and
   roughly as many as my blind. *Confidence: medium.*

If the margin comes out *larger* than my sighted annotation, something is wrong with my
understanding and I will say so rather than celebrate.

## Nothing here changes after the first number is computed.
