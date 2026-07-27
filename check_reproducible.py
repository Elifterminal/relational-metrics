"""Does every committed result still reproduce from its own runner?

`check_manifest.py` verifies that a result file EXISTS, and now warns when one
predates the last change to the measure. Neither proves the file is what the
code produces. This does, by running everything.

WHY IT EXISTS. EXP-053 audited the record for an unrelated reason and found four
committed results that no longer reproduce. `exp009.json` stores an MDL ratio of
1.727 where its own code produces 1.4059 -- almost certainly left behind by
EXP-024's correction to the relation-type encoding, the correction that demoted
F-06. Nothing re-ran them and nothing checked, for twenty-nine experiments.

That is P-26 for the fourth time in one session, and the most damning of the
four: the manifest machinery -- this project's proudest apparatus -- had exactly
the defect it was built to catch in the experiments. It enforced that every
claim has a file and every file has a runner. It never enforced that the file is
what the runner produces.

THIS SCRIPT NEVER EDITS THE RECORD. A result that fails to reproduce is
restored to its committed content and reported. Silently regenerating it would
overwrite the published number with a new one and destroy the evidence that they
differ, which is the whole finding.

Slow by design -- minutes, not seconds. Run it before publishing a consolidation
or a stage close, not on every commit.

    python3 check_reproducible.py            # all runners
    python3 check_reproducible.py exp009     # one, by result stem
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAB = ROOT / "lab"
RESULTS = ROOT / "results"
TIMEOUT = 2400

# The audit instrument from EXP-053. If it leaks into this run every result
# looks stale, so it is cleared rather than assumed absent (P-26, again).
CLEARED = ("RM_POLARITY_PRESERVING",)

SKIP = {"run_exp053"}          # the audit itself; running it re-runs everything


def main(argv: list[str]) -> int:
    want = set(argv[1:])
    env = dict(os.environ)
    for k in CLEARED:
        env.pop(k, None)

    report: dict[str, str] = {}
    for runner in sorted(LAB.glob("run_exp*.py")):
        if runner.stem in SKIP:
            continue
        stem = runner.stem.replace("run_", "")
        if want and stem not in want:
            continue
        rp = RESULTS / f"{stem}.json"
        if not rp.exists():
            report[stem] = "no result file"
            print(f"  {stem:<10} no result file", flush=True)
            continue

        published = rp.read_text()
        try:
            proc = subprocess.run([sys.executable, str(runner)], cwd=ROOT,
                                  env=env, capture_output=True, text=True,
                                  timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            rp.write_text(published)
            report[stem] = "timeout"
            print(f"  {stem:<10} TIMEOUT", flush=True)
            continue

        if proc.returncode != 0:
            rp.write_text(published)
            tail = (proc.stderr or "").strip().splitlines()[-1:] or [""]
            report[stem] = f"error: {tail[0][:120]}"
            print(f"  {stem:<10} ERROR  {tail[0][:80]}", flush=True)
            continue

        produced = rp.read_text()
        if produced == published:
            report[stem] = "reproduces"
        else:
            # Restore. The published number stays published; the discrepancy is
            # the finding and overwriting it would erase the evidence.
            rp.write_text(published)
            report[stem] = "STALE"
        print(f"  {stem:<10} {report[stem]}", flush=True)

    stale = sorted(k for k, v in report.items() if v == "STALE")
    broken = sorted(k for k, v in report.items()
                    if v.startswith("error") or v in ("timeout", "no result file"))

    print(f"\n{len(report)} checked   "
          f"{sum(1 for v in report.values() if v == 'reproduces')} reproduce   "
          f"{len(stale)} stale   {len(broken)} would not run")
    if stale:
        print(f"  stale : {', '.join(stale)}")
    if broken:
        print(f"  broken: {', '.join(broken)}")

    # A SUBSET RUN MUST NOT LOOK LIKE A FULL ONE. The first version wrote the
    # whole report every time, so `check_reproducible.py exp009` replaced a
    # 47-experiment sweep with a 5-entry file and check_manifest would then have
    # passed on the strength of it. Same species as everything EXP-053 found:
    # a check that silently stopped covering what it claimed to cover.
    out = RESULTS / "reproducibility.json"
    merged = report
    if want and out.exists():
        prior = json.loads(out.read_text()).get("by_experiment", {})
        merged = {**prior, **report}
    all_stale = sorted(k for k, v in merged.items() if v == "STALE")
    all_broken = sorted(k for k, v in merged.items()
                        if v.startswith("error") or v in ("timeout", "no result file"))
    total_runners = len([p for p in LAB.glob("run_exp*.py") if p.stem not in SKIP])
    out.write_text(json.dumps(
        {"checked": len(merged),
         "runners_present": total_runners,
         "full_sweep": len(merged) == total_runners and not want,
         "partial_run_of": sorted(want) or None,
         "stale": all_stale, "broken": all_broken,
         "by_experiment": merged}, indent=2) + "\n")
    if want:
        print(f"  (partial run merged into the existing report: "
              f"{len(merged)}/{total_runners} experiments now covered)")

    return 1 if (stale or broken) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
