# Superseded result files — regenerated 2026-07-27

These are the **published** contents of five result files that no longer reproduced from their own
runners, kept verbatim so the discrepancy stays visible after the live files were brought current.

Found by `EXP-053` while auditing something else. `check_manifest.py` verified that a result file
*exists*; it never verified the file was *current*, so the drift was invisible. Fourth instance of
`P-26` in one session, and the one that generalises: the checking machinery had the defect it was
built to catch.

| file | what moved | claim affected? |
|---|---|---|
| `exp000b.json` | MDL gain 19.727 → 18.727 | no |
| `exp009.json` | MDL ratio 1.727 → 1.4059 | no |
| `exp014.json` | numeric only | no |
| `exp017.json` | agreement 0.5714 → 0.2, ties 1 → 10 | no |
| `exp030.json` | correct 4 → 5, p 0.5488 → 1.0 | **no** — headline stays `NO SIGNAL`, `beats_chance` stays false |

**No published claim changes.** The most likely cause is `EXP-024`'s correction to the relation-type
encoding — the one that demoted `F-06` — which changed mapping costs for every pair. These five were
never regenerated afterwards.

Kept rather than deleted because overwriting a stale number with a fresh one destroys the evidence
that they differed, and that evidence *is* the finding.
