"""Fail the build when the published material disagrees with the manifest.

Written after an external review found the site header still saying "four runs"
at experiment twenty-seven, and the README still presenting a claim that had
been retracted the day before. Both were hand-maintained copies of facts that
live in one place, so both drifted -- and the retraction was the second time a
wrong statement stayed visible because nothing checked.

The rule this enforces: `manifest.json` is the only place an experiment or a
claim is described. Everything else is generated. This script is what makes
that true rather than aspirational.

Checks:
  1. every lab/run_*.py has a manifest entry, and every entry has its runner
  2. every entry's result_file exists
  3. no retracted claim appears in README or the site except next to its retraction
  4. the experiment count in the site header matches the manifest
  5. README's generated block matches what the generator would emit now
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
EXPS = MANIFEST["experiments"]
CLAIMS = MANIFEST["claims"]

# How far from a retracted claim a retraction marker has to appear for the
# mention to count as properly labelled rather than presented as current.
RETRACTION_WINDOW = 700
RETRACTION_MARKERS = ("retract", "RETRACT", "Retract", "superseded", "no longer")


def _committed_at(relpath: str) -> int:
    """Author timestamp of the commit that last changed `relpath`, or 0."""
    import subprocess
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%at", "--", relpath],
                             cwd=ROOT, capture_output=True, text=True, timeout=20)
        return int(out.stdout.strip() or 0)
    except Exception:
        return 0


def fail(msgs: list[str], check: str, problems: list[str]) -> None:
    if problems:
        msgs.append(f"  {check}:")
        msgs.extend(f"    - {p}" for p in problems)


def main() -> int:
    errs: list[str] = []

    # 1. runners <-> entries
    runners = {p.name for p in (ROOT / "lab").glob("run_exp*.py")}
    declared = {Path(e["entry_point"]).name for e in EXPS}
    fail(errs, "runner with no manifest entry", sorted(runners - declared))
    fail(errs, "manifest entry with no runner", sorted(declared - runners))

    # 2. result files
    fail(errs, "missing result file",
         [f'{e["id"]} -> {e["result_file"]}' for e in EXPS
          if not (ROOT / e["result_file"]).exists()])

    # 2b. result files must not be OLDER than the measure that produced them.
    #
    # EXP-053 found four committed results that no longer reproduce from their
    # own runners -- exp009.json stores an MDL ratio of 1.727 where its code now
    # produces 1.4059, almost certainly left behind by EXP-024's relation-type
    # encoding correction. This script checked that a result file EXISTS. It
    # never checked the file was CURRENT, so the drift was invisible.
    #
    # Fourth instance of P-26 in one session, and the one that generalises: the
    # manifest machinery had the same defect as the experiments it polices. It
    # enforced that every claim has a file and every file has a runner, never
    # that the file is what the runner produces.
    #
    # Re-running everything here would make the check too slow to run often, so
    # this asks the one cheap question that is actually actionable: HAS A
    # REPRODUCIBILITY SWEEP BEEN RUN SINCE THE MEASURE LAST CHANGED?
    #
    # The first version of this flagged every result older than the measure.
    # That fires on all fifty files the moment anyone touches measures.py --
    # including for an inert optional parameter -- so it would have been ignored
    # within a day, and a check that gets ignored is worse than no check. One
    # actionable line beats fifty accurate ones.
    core = ["lab/measures.py", "lab/codes.py", "lab/mapping.py", "lab/structure.py"]
    core_t = max([t for t in (_committed_at(p) for p in core) if t] or [0])
    sweep = ROOT / "results" / "reproducibility.json"
    sweep_t = _committed_at("results/reproducibility.json")
    if core_t:
        if not sweep.exists():
            fail(errs, "reproducibility never verified",
                 ["no results/reproducibility.json -- run check_reproducible.py"])
        elif sweep_t and sweep_t < core_t:
            fail(errs, "reproducibility sweep predates the measure",
                 ["the measure changed after the last sweep; "
                  "run check_reproducible.py and commit the result"])
        else:
            data = json.loads(sweep.read_text()) if sweep.exists() else {}
            bad = sorted(data.get("stale", [])) + sorted(data.get("broken", []))
            fail(errs, "results that do not reproduce", bad)

    # 3. retracted claims must never read as current
    targets = [ROOT / "README.md", ROOT / "docs" / "index.html"]
    stale = []
    for e in EXPS:
        rc = e.get("retracted_claim")
        if not rc:
            continue
        # match on the distinctive tail, so light rewording still trips it
        needle = rc.split(" ", 2)[-1].lower()
        for t in targets:
            if not t.exists():
                continue
            body = t.read_text()
            for m in re.finditer(re.escape(needle), body.lower()):
                lo = max(0, m.start() - RETRACTION_WINDOW)
                window = body[lo:m.end() + RETRACTION_WINDOW]
                if not any(k in window for k in RETRACTION_MARKERS):
                    stale.append(f'{t.name}: "{needle}" ({e["id"]}) with no retraction nearby')
    fail(errs, "retracted claim presented as current", stale)

    # 4. header count
    site = ROOT / "docs" / "index.html"
    if site.exists():
        body = site.read_text()
        n = len(EXPS)
        if f"{n} runs" not in body and f"{n} experiments" not in body:
            errs.append("  site header count:")
            errs.append(f"    - manifest has {n} experiments; docs/index.html states neither "
                        f'"{n} runs" nor "{n} experiments"')

    # 5. Stage 2 experiments must have a committed analysis plan.
    #    Stage 1's mechanisms worked when a program checked them and failed when
    #    they relied on memory. This is that lesson, enforced.
    plans = ROOT / "external" / "plans"
    fail(errs, "Stage 2 experiment with no committed analysis plan",
         [f'{e["id"]} -> external/plans/{e["id"]}.json missing'
          for e in EXPS if e.get("stage") == 2
          and not (plans / f'{e["id"]}.json').exists()])

    # 6. README generated block is current
    sys.path.insert(0, str(ROOT))
    from gen_docs import readme_table                                  # noqa: E402
    rd = (ROOT / "README.md").read_text()
    want = readme_table()
    if want.strip() not in rd:
        errs.append("  README generated block is stale:")
        errs.append("    - run `python3 gen_docs.py` and commit the result")

    if errs:
        print("MANIFEST CHECK FAILED\n")
        print("\n".join(errs))
        print(f"\n{len(EXPS)} experiments, {len(CLAIMS)} claims in manifest.json")
        return 1

    live = [c for c in CLAIMS if c["status"] == "ACTIVE_WITHIN_TESTED_SCOPE"]
    print(f"manifest check OK — {len(EXPS)} experiments, {len(CLAIMS)} claims "
          f"({len(live)} active, "
          f"{sum(1 for c in CLAIMS if c['status'] in ('REFUTED', 'DEMOTED'))} refuted/demoted, "
          f"{sum(1 for c in CLAIMS if c['status'] == 'UNTESTED')} untested)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
