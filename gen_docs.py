"""Generate the README experiment table and the site panels from manifest.json.

Everything here was previously hand-maintained in two places, and drifted in
both. See check_manifest.py for what enforces this.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
EXPS = MANIFEST["experiments"]
CLAIMS = MANIFEST["claims"]

BEGIN = "<!-- BEGIN GENERATED: experiments -->"
END = "<!-- END GENERATED: experiments -->"

LABEL = {
    "ACTIVE_WITHIN_TESTED_SCOPE": ("active within tested scope", "ok"),
    "PROVISIONAL": ("provisional", "warn"),
    "UNTESTED": ("untested", "mut"),
    "DEMOTED": ("demoted / replaced", "bad"),
    "REFUTED": ("refuted / retracted", "bad"),
}
ORDER = ["ACTIVE_WITHIN_TESTED_SCOPE", "PROVISIONAL", "UNTESTED", "DEMOTED", "REFUTED"]


def readme_table() -> str:
    rows = ["| Run | Question | Result |", "|---|---|---|"]
    for e in EXPS:
        note = ""
        if e.get("retracted_claim"):
            note = (f' <br>*(a sub-claim of this run — "{e["retracted_claim"]}" — was '
                    f'**RETRACTED** by `{e["superseded_by"]}`)*')
        rows.append(f'| `{e["id"]}` | {e["question"]} | {e["result"]}{note} |')
    return "\n".join(rows)


def readme_survives() -> str:
    out = ["### What currently survives", "",
           "*Present tense, generated from `manifest.json`. The table above is the history; "
           "this is the state.*", ""]
    for st in ORDER:
        cs = [c for c in CLAIMS if c["status"] == st]
        if not cs:
            continue
        out.append(f"**{LABEL[st][0].upper()}**")
        out.append("")
        for c in cs:
            rung = f" · rung {c['rung']}" if c["rung"] else ""
            ev = ", ".join(f"`{e}`" for e in c["evidence"]) or "—"
            out.append(f"- **{c['claim']}**{rung}  ")
            out.append(f"  *scope*: {c['scope']}  ")
            out.append(f"  *evidence*: {ev}")
        out.append("")
    return "\n".join(out)


def readme_runlist() -> str:
    w = max(len(Path(e["entry_point"]).name) for e in EXPS)
    lines = ["```bash", "cd lab"]
    for e in EXPS:
        name = Path(e["entry_point"]).name
        lines.append(f'python3 {name:<{w}}   # {e["blurb"]}'.rstrip(" #").rstrip())
    lines.append("")
    lines.append("cd ..")
    lines.append("python3 render/figures.py     # regenerate the SVGs")
    lines.append("python3 render/dashboard.py   # rebuild the study page")
    lines.append("python3 gen_docs.py           # regenerate this README from manifest.json")
    lines.append("python3 check_manifest.py     # FAILS if any of the above has drifted")
    lines.append("```")
    return "\n".join(lines)


def site_survives_panel() -> str:
    """The present-tense map a new reader needs before entering the history."""
    out = ['<h2>What currently survives</h2>',
           '<p>The log below is a history and reads as one. This is the present tense: every claim '
           'the project is currently making, what scope it holds within, and what killed the ones '
           'that died. Generated from the same manifest that generates the README, so the two '
           'cannot disagree.</p>',
           '<table class="survives"><thead><tr><th>status</th><th>claim</th>'
           '<th>scope it holds within</th></tr></thead><tbody>']
    for st in ORDER:
        for c in [c for c in CLAIMS if c["status"] == st]:
            lbl, cls = LABEL[st]
            rung = f'<span class="conf">rung {c["rung"]}</span>' if c["rung"] else ""
            ev = " ".join(f'<code>{e}</code>' for e in c["evidence"]) or "<i>none yet</i>"
            out.append(f'<tr><td><span class="tag {cls}">{lbl}</span>{rung}</td>'
                       f'<td><b>{c["claim"]}</b><br><span class="sub">{ev}</span></td>'
                       f'<td class="sub">{c["scope"]}</td></tr>')
    out.append('</tbody></table>')
    return "".join(out)


def site_header() -> str:
    n = len(EXPS)
    live = sum(1 for c in CLAIMS if c["status"] == "ACTIVE_WITHIN_TESTED_SCOPE")
    dead = sum(1 for c in CLAIMS if c["status"] in ("REFUTED", "DEMOTED"))
    untested = sum(1 for c in CLAIMS if c["status"] == "UNTESTED")
    retracted = sum(1 for e in EXPS if e.get("retracted_claim"))
    return (f'<p class="sub">{n} runs. '
            f'<b>{live}</b> claims active within a stated scope, '
            f'<b>{dead}</b> refuted or demoted, '
            f'<b>{untested}</b> untested — and <b>{retracted}</b> published claim retracted by a '
            f'later run. Counts generated from the manifest, so this line cannot go stale.</p>')


def _splice(body: str, begin: str, end: str, new: str) -> str:
    if begin not in body:
        raise SystemExit(f"marker {begin!r} not found")
    return re.sub(re.escape(begin) + r".*?" + re.escape(end),
                  f"{begin}\n{new}\n{end}", body, flags=re.S)


def main() -> None:
    p = ROOT / "README.md"
    body = p.read_text()
    body = _splice(body, BEGIN, END,
                   readme_table() + "\n\n" + readme_survives() + "\n" + readme_runlist())
    p.write_text(body)
    print(f"README.md regenerated — {len(EXPS)} experiments, {len(CLAIMS)} claims")


if __name__ == "__main__":
    main()
