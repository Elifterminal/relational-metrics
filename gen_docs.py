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

# Which claims rest on exhaustive computation and which on hand annotation.
# From the consolidation audit of 2026-07-26. Kept here rather than in prose so
# the site and the README cannot disagree about it.
TIER = {
    "C-01": "computation", "C-02": "computation", "C-05": "computation",
    "C-06": "computation", "C-08": "computation", "C-10": "computation",
    "C-14": "computation", "C-07": "computation",
    "C-04": "theorem (instances were annotation)",
    "C-12": "computation + annotation",
    "C-03": "hand annotation", "C-13": "hand annotation", "C-09": "hand annotation",
    "C-11": "untested",
}

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
    out = ["### What this project established", "",
           "*Consolidated after 43 experiments, generated from `manifest.json`. Sorted by what each "
           "claim RESTS ON — six come from exhaustive computation with no annotation involved; three "
           "depend on hand annotation, which this project spent a day showing was biased and is the "
           "bottleneck.*", ""]
    for st in ORDER:
        cs = [c for c in CLAIMS if c["status"] == st]
        if not cs:
            continue
        out.append(f"**{LABEL[st][0].upper()}**")
        out.append("")
        for c in cs:
            rung = f" · rung {c['rung']}" if c["rung"] else ""
            tier = TIER.get(c["id"], "")
            ev = ", ".join(f"`{e}`" for e in c["evidence"]) or "—"
            out.append(f"- **{c['claim']}**{rung} · *rests on: {tier}*  ")
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
    out = ['<h2>What this project established</h2>',
           '<p>Consolidated after 43 experiments. Claims are sorted by <b>what they rest on</b> '
           'rather than by how interesting they are — that division is the most useful thing here, '
           'and conflating the two groups is how a project like this fools itself.</p>',
           '<div class="read"><b>Six results come from exhaustive computation over enumerated '
           'systems.</b> No annotation, no corpus, no human judgement enters them at any point; they '
           'are checked over every case in a finite space rather than sampled.<br><br>'
           '<b>Three depend on somebody turning text into structures by hand</b> — and this project '
           'spent a day establishing that the somebody was biased and that this step is the '
           'bottleneck. Those two groups deserve very different confidence.</div>',
           '<div class="read ok"><b>What the whole thing amounts to: a working instrument with a '
           'hand-prepared input.</b> The comparison engine does what it claims on formalised '
           'relational descriptions, confirmed by someone with no stake in the outcome. The step '
           'from text to structure is unsolved, was doing more of the work than the engine was, and '
           'on real prose appears not to be solvable in this representation at all.<br><br>'
           'Smaller than the goal, and genuinely a result — most projects that fail here never learn '
           'which half was broken.</div>',
           '<table class="survives"><thead><tr><th>status</th><th>claim</th>'
           '<th>scope it holds within</th></tr></thead><tbody>']
    for st in ORDER:
        for c in [c for c in CLAIMS if c["status"] == st]:
            lbl, cls = LABEL[st]
            rung = f'<span class="conf">rung {c["rung"]}</span>' if c["rung"] else ""
            ev = " ".join(f'<code>{e}</code>' for e in c["evidence"]) or "<i>none yet</i>"
            tier = TIER.get(c["id"], "")
            tcol = ("#15803d" if tier.startswith("computation") or tier.startswith("theorem")
                    else "#d97706" if tier == "hand annotation" else "var(--mut)")
            out.append(f'<tr><td><span class="tag {cls}">{lbl}</span>{rung}'
                       f'<br><span class="sub" style="color:{tcol}">rests on: {tier}</span></td>'
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
