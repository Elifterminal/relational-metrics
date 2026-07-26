"""Stage 2 rigor, enforced rather than remembered.

Stage 1's mechanisms worked when a program checked them (the manifest, the CI
drift check, the vacuity assertion) and failed when they depended on me
remembering (the untested fractions, the post-hoc analysis switch, the
pre-registration I was still writing about when the data arrived).

So the Stage 2 rules are conditions the code refuses to proceed without.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "external" / "plans"


class ProtocolViolation(RuntimeError):
    """Raised instead of producing a result that would not be trustworthy."""


def _committed(path: Path) -> str | None:
    """The commit that last changed `path`, or None if it is uncommitted."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%H", "--", str(path)],
                             cwd=ROOT, capture_output=True, text=True, timeout=20)
        return out.stdout.strip() or None
    except Exception:
        return None


def require_locked_plan(experiment: str) -> dict:
    """A Stage 2 experiment may not compute a result without a committed plan.

    S2 rule. EXP-038 switched analysis after a null and could only flag it;
    EXP-039 locked a plan but only after the data had been read. Neither could be
    fixed retroactively, so this refuses up front.
    """
    p = PLANS / f"{experiment}.json"
    if not p.exists():
        raise ProtocolViolation(
            f"no analysis plan at {p}. Write the statistic, the tests, the "
            f"exclusion rule, the robustness threshold and the falsification "
            f"conditions, commit it, THEN run {experiment}.")
    commit = _committed(p)
    if commit is None:
        raise ProtocolViolation(
            f"{p} exists but is not committed. An uncommitted plan can be edited "
            f"after seeing a result, which is the thing this prevents.")
    plan = json.loads(p.read_text())
    missing = [k for k in ("statistic", "tests", "exclusion_rule",
                           "robustness", "falsification", "predictions")
               if k not in plan]
    if missing:
        raise ProtocolViolation(f"plan is missing required sections: {missing}")
    plan["_locked_at"] = commit
    plan["_sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    return plan


@dataclass(frozen=True)
class Stage2Result:
    experiment: str
    plan: dict
    payload: dict

    def write(self) -> Path:
        """Refuses to write a result that omits the required reporting."""
        need = ("margin_stats", "leave_one_out", "abstention_rate", "verdict")
        missing = [k for k in need if k not in self.payload]
        if missing:
            raise ProtocolViolation(
                f"result omits {missing}. P-24/P-25: a bare fraction is not a "
                f"measurement, a positive without leave-one-out is one observation "
                f"wearing a p-value, and S2-2 makes the abstention rate a reported "
                f"statistic rather than a footnote.")
        out = ROOT / "results" / f"{self.experiment.lower().replace('-', '')}.json"
        out.write_text(json.dumps(
            {"experiment": self.experiment,
             "plan_locked_at": self.plan["_locked_at"],
             "plan_sha256": self.plan["_sha256"],
             **self.payload}, indent=2))
        return out


def check_capacity_to_fail(control_name: str, perturb_and_measure) -> bool:
    """A control that cannot fail is not a control (EXP-031).

    `perturb_and_measure` must change the property the control holds fixed and
    return whether the measure noticed. Returning False is a hard stop, not a
    warning -- EXP-000a published a control that could not fail for thirty
    experiments precisely because nothing objected.
    """
    if not perturb_and_measure():
        raise ProtocolViolation(
            f"control '{control_name}' does not respond when the property it "
            f"tests is perturbed. It cannot fail, so passing it proves nothing.")
    return True
