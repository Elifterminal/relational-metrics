"""EXP-053 -- the migration audit. If we adopt the polarity constraint, what moves?

EXP-052 established that the unconstrained type search never tells a structure
from its sign-flipped twin, exercises that freedom on a third to a half of real
corpus pairs, and that constraining it changes no corpus verdict. It then
REFUSED to adopt the constraint on that evidence, because twenty-six runners
call mdl_correspondence and only one family of them had been checked. Changing
one thing while checks elsewhere go unre-run is exactly the failure EXP-052 had
just caught in flat32.

So this runs the entire record under both regimes and diffs it.

Three ways this audit could lie to itself, all checked before any comparison:

  1. The instrument might not reach the measure, making every "identical"
     verdict vacuous -- the EXP-000a error. Checked first, and it is a hard stop.
  2. A runner might be non-deterministic, making a diff against it meaningless.
     Checked by running it twice under the SAME regime.
  3. A numeric drop might be mistaken for a finding. It cannot be: constraining
     removes mappings from a maximum, so scores can only fall. Only
     verdict-bearing keys count, and the classifier for those is in the plan.

Plan locked at external/plans/EXP-053.json before this file ran.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protocol2 import (ProtocolViolation, Stage2Result,           # noqa: E402
                       require_locked_plan)

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "lab"
RESULTS = ROOT / "results"

VERDICT_WORDS = ("claim", "holds", "verdict", "survives", "refuted", "retracted",
                 "ranking", "beats", "above", "wins", "identifiable",
                 "separates", "passes", "fails")

# Normalisations, listed here because the plan requires them listed.
NORMALISERS = (
    ("absolute paths", re.compile(re.escape(str(ROOT)))),
    ("plan commit hashes", re.compile(r'"plan_locked_at":\s*"[0-9a-f]{40}"')),
)


def runners():
    out = []
    for p in sorted(LAB.glob("run_exp*.py")):
        if p.name == "run_exp053.py":
            continue
        if "mdl_correspondence" in p.read_text():
            out.append(p)
    return out


def result_path_for(runner: Path) -> Path | None:
    stem = runner.stem.replace("run_", "")
    for cand in (RESULTS / f"{stem}.json", RESULTS / f"{stem.replace('exp', 'exp')}.json"):
        if cand.exists():
            return cand
    hits = sorted(RESULTS.glob(f"{stem}*.json"))
    return hits[0] if hits else None


def normalise(text: str) -> str:
    for _, rx in NORMALISERS:
        text = rx.sub("<NORM>", text)
    return text


def run_one(runner: Path, constrained: bool, timeout=1800):
    env = dict(os.environ)
    if constrained:
        env["RM_POLARITY_PRESERVING"] = "1"
    else:
        env.pop("RM_POLARITY_PRESERVING", None)
    rp = result_path_for(runner)
    before = rp.read_text() if rp and rp.exists() else None
    try:
        proc = subprocess.run([sys.executable, str(runner)], cwd=ROOT, env=env,
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "json": None}
    if proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-4:]
        # Leave the file as we found it so an erroring runner cannot corrupt
        # the record it failed to produce.
        if before is not None and rp:
            rp.write_text(before)
        return {"status": "error", "json": None, "stderr": "\n".join(tail)}
    if rp is None or not rp.exists():
        return {"status": "no_result_file", "json": None}
    return {"status": "ok", "json": normalise(rp.read_text()), "path": str(rp)}


def diff_keys(a: str, b: str):
    """Top-level keys whose values differ, split into verdict-bearing or not."""
    try:
        da, db = json.loads(a), json.loads(b)
    except json.JSONDecodeError:
        return {"parse_failed": True}
    if not isinstance(da, dict) or not isinstance(db, dict):
        return {"not_an_object": True}
    changed = [k for k in set(da) | set(db)
               if json.dumps(da.get(k), sort_keys=True) != json.dumps(db.get(k), sort_keys=True)]

    def bearing(k):
        if isinstance(da.get(k), bool) or isinstance(db.get(k), bool):
            return True
        return any(w in k.lower() for w in VERDICT_WORDS)

    v = sorted(k for k in changed if bearing(k))
    return {
        "changed_keys": sorted(changed),
        "verdict_bearing": v,
        "verdict_before": {k: da.get(k) for k in v},
        "verdict_after": {k: db.get(k) for k in v},
        "numeric_only": sorted(k for k in changed if not bearing(k)),
    }


def deep_verdict_scan(a: str, b: str, path="", acc=None):
    """Verdict-bearing keys at ANY depth, not just top level.

    Top-level-only would have missed every corpus claim, which live three
    levels down inside by_motif. A boolean that flips anywhere in the tree is
    the thing this audit exists to find.
    """
    if acc is None:
        acc = []
    try:
        da, db = json.loads(a), json.loads(b)
    except json.JSONDecodeError:
        return acc

    def walk(x, y, p):
        if isinstance(x, dict) and isinstance(y, dict):
            for k in set(x) | set(y):
                walk(x.get(k), y.get(k), f"{p}/{k}")
        elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            for i, (u, w) in enumerate(zip(x, y)):
                walk(u, w, f"{p}[{i}]")
        else:
            if x == y:
                return
            key = p.rsplit("/", 1)[-1].split("[")[0].lower()
            is_bool = isinstance(x, bool) or isinstance(y, bool)
            if is_bool or any(w in key for w in VERDICT_WORDS):
                if not (isinstance(x, (int, float)) and isinstance(y, (int, float))
                        and not is_bool):
                    acc.append({"path": p, "before": x, "after": y})

    walk(da, db, path)
    return acc


def main() -> None:
    plan = require_locked_plan("EXP-053")
    rs = runners()
    print(f"EXP-053 -- auditing {len(rs)} runners that call the measure\n")

    # -- capacity to fail: does the instrument reach the measure at all? ----
    probe = LAB / "run_exp024.py"
    free0 = run_one(probe, False)
    cons0 = run_one(probe, True)
    reached = (free0["status"] == "ok" and cons0["status"] == "ok"
               and free0["json"] != cons0["json"])
    if not reached:
        raise ProtocolViolation(
            "RM_POLARITY_PRESERVING does not change EXP-024's output. EXP-052 "
            "measured a 0.467 inversion rate on that corpus, so identical output "
            "means the instrument is not reaching the measure and every "
            "'identical' verdict this audit produced would be vacuous.")
    print(f"instrument reaches the measure: yes (EXP-024 output differs)\n")

    per = {}
    nondet, errored = [], []
    for r in rs:
        name = r.stem.replace("run_", "").upper().replace("EXP", "EXP-")
        a1 = run_one(r, False)
        if a1["status"] != "ok":
            per[name] = {"status": a1["status"], "stderr": a1.get("stderr")}
            errored.append(name)
            print(f"  {name:<10} {a1['status'].upper()}")
            continue
        a2 = run_one(r, False)
        if a2["status"] != "ok" or a1["json"] != a2["json"]:
            per[name] = {"status": "non_deterministic"}
            nondet.append(name)
            print(f"  {name:<10} NON-DETERMINISTIC -- excluded")
            continue
        c = run_one(r, True)
        if c["status"] != "ok":
            per[name] = {"status": f"constrained_{c['status']}", "stderr": c.get("stderr")}
            errored.append(name)
            print(f"  {name:<10} {c['status'].upper()} under constraint")
            continue

        identical = a1["json"] == c["json"]
        d = diff_keys(a1["json"], c["json"]) if not identical else {}
        deep = deep_verdict_scan(a1["json"], c["json"]) if not identical else []
        per[name] = {"status": "ok", "identical": identical,
                     "top_level": d, "verdict_changes_any_depth": deep,
                     "n_verdict_changes": len(deep)}
        flag = "identical" if identical else f"moved ({len(deep)} verdict changes)"
        print(f"  {name:<10} {flag}")
        # Restore the unconstrained result -- the published record stays the
        # published record until adoption is actually decided.
        run_one(r, False)

    ok = {k: v for k, v in per.items() if v.get("status") == "ok"}
    total_verdict = sum(v["n_verdict_changes"] for v in ok.values())
    moved = [k for k, v in ok.items() if not v["identical"]]

    if len(nondet) + len(errored) > 3:
        band = "AUDIT CANNOT ANSWER -- too much of the record will not re-run"
        statement = (f"{len(nondet)} non-deterministic and {len(errored)} erroring "
                     f"runners. A record that cannot be re-run is not a record, and "
                     f"that is the finding rather than any verdict about adoption.")
    elif total_verdict == 0:
        band = "0 verdict changes -- ADOPT"
        statement = ("The migration is safe across the whole record. Every published "
                     "claim survives verbatim and the semantic argument for the "
                     "constraint stands unopposed.")
    elif total_verdict <= 3:
        band = f"{total_verdict} verdict changes -- ADOPT AFTER REPUBLISHING"
        statement = ("The affected experiments are re-run, re-written and their "
                     "manifest entries amended BEFORE the default flips. The changed "
                     "verdicts are published as changes.")
    else:
        band = f"{total_verdict} verdict changes -- DO NOT ADOPT ON THIS EVIDENCE"
        statement = ("A constraint that moves this much of the record is not a "
                     "correction, it is a different measure, and it needs its own "
                     "validation from rung 1.")

    payload = {
        "question": "adoption migration for the Q-41 polarity constraint",
        "instrument_reached_the_measure": True,
        "normalisations_applied": [n for n, _ in NORMALISERS],
        "runners_audited": len(rs),
        "non_deterministic": nondet,
        "errored": errored,
        "experiments_with_any_movement": moved,
        "total_verdict_changes": total_verdict,
        "by_experiment": per,
        "verdict": {"band": band, "statement": statement},
        "margin_stats": {
            "experiments_compared": len(ok),
            "experiments_whose_numbers_moved": len(moved),
            "experiments_byte_identical": len(ok) - len(moved),
            "note": "numeric movement is arithmetic -- constraining removes "
                    "mappings from a maximum so scores can only fall. Only "
                    "verdict-bearing keys are evidence.",
        },
        "leave_one_out": {
            "unit": "experiment",
            "verdict_changes_excluding_each":
                {k: total_verdict - v["n_verdict_changes"] for k, v in ok.items()},
        },
        "abstention_rate": {
            "excluded_non_deterministic": len(nondet) / len(rs),
            "excluded_errored": len(errored) / len(rs),
            "audited_successfully": len(ok) / len(rs),
        },
    }
    out = Stage2Result("EXP-053", plan, payload).write()

    print(f"\nwritten to {out}")
    print(f"\n  audited            {len(ok)}/{len(rs)}")
    print(f"  numbers moved      {len(moved)}")
    print(f"  verdict changes    {total_verdict}")
    if moved:
        print(f"  moved: {', '.join(moved)}")
    for k, v in ok.items():
        for ch in v["verdict_changes_any_depth"]:
            print(f"    {k} {ch['path']}: {ch['before']} -> {ch['after']}")
    print(f"\n>>> {band}\n    {statement}")


if __name__ == "__main__":
    main()
