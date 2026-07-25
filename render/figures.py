"""Render EXP-000 results as standalone SVGs plus one self-contained page.

No plotting library. The charts are small enough that hand-emitted SVG is
less code than a dependency, and it means the figures are theme-aware and
open in any browser with nothing installed.
"""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

PALETTE = {"B": "#2563eb", "C": "#d97706", "D": "#64748b", "E": "#dc2626"}
LABELS = {
    "B": "B — different surface, same structure",
    "C": "C — same surface, different structure",
    "D": "D — matched random",
    "E": "E — near-miss, one edge flipped",
}

STYLE = """
<style>
  :root { --fg:#1a1a1a; --mut:#6b7280; --grid:#e5e7eb; --bg:#ffffff; --accent:#111827; }
  @media (prefers-color-scheme: dark) {
    :root { --fg:#e8e8ea; --mut:#9ca3af; --grid:#2f3542; --bg:#0f1115; --accent:#f3f4f6; }
  }
  :root[data-theme="dark"] { --fg:#e8e8ea; --mut:#9ca3af; --grid:#2f3542; --bg:#0f1115; --accent:#f3f4f6; }
  :root[data-theme="light"] { --fg:#1a1a1a; --mut:#6b7280; --grid:#e5e7eb; --bg:#ffffff; --accent:#111827; }
  .bg { fill: var(--bg); }
  .ax { stroke: var(--grid); stroke-width: 1; }
  .tick { fill: var(--mut); font: 11px ui-sans-serif, system-ui, sans-serif; }
  .lbl { fill: var(--fg); font: 12px ui-sans-serif, system-ui, sans-serif; }
  .ttl { fill: var(--fg); font: 600 14px ui-sans-serif, system-ui, sans-serif; }
  .sub { fill: var(--mut); font: 11px ui-sans-serif, system-ui, sans-serif; }
  .node { fill: var(--bg); stroke: var(--fg); stroke-width: 1.5; }
  .ntxt { fill: var(--fg); font: 10px ui-sans-serif, system-ui, sans-serif; text-anchor: middle; }
</style>
"""


def svg(w: int, h: int, body: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'{STYLE}<rect class="bg" width="{w}" height="{h}"/>{body}</svg>')


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# Figure 1 — the eta curves
# ---------------------------------------------------------------------------

def fig_eta_curves(data: dict) -> str:
    W, H = 760, 430
    L, R, T, B = 62, 250, 54, 52
    pw, ph = W - L - R, H - T - B
    etas = data["tunable"]["etas"]
    curves = data["tunable"]["curves"]
    xmax = max(etas)
    ymax = 1.0

    def px(e): return L + (e / xmax) * pw
    def py(v): return T + ph - (v / ymax) * ph

    out = ['<text class="ttl" x="24" y="26">F-06 tunable correspondence: the penalty sets the ranking</text>',
           '<text class="sub" x="24" y="43">K(A, ·) as the mapping-complexity penalty η varies. '
           'Crossings are rank reversals — not magnitude changes.</text>']

    for i in range(6):
        v = i / 5 * ymax
        y = py(v)
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v:.1f}</text>')
    for i in range(7):
        e = i / 6 * xmax
        x = px(e)
        out.append(f'<line class="ax" x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{T+ph}"/>')
        out.append(f'<text class="tick" x="{x:.1f}" y="{T+ph+18}" text-anchor="middle">{e:.2f}</text>')
    out.append(f'<text class="lbl" x="{L+pw/2:.0f}" y="{H-14}" text-anchor="middle">'
               'mapping-complexity penalty η</text>')
    out.append(f'<text class="lbl" transform="translate(18,{T+ph/2:.0f}) rotate(-90)" '
               'text-anchor="middle">correspondence K</text>')

    for rev in data["reversals"]:
        x = px(rev["eta"])
        out.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{T+ph}" '
                   'stroke="#dc2626" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.75"/>')
        out.append(f'<text class="tick" x="{x+5:.1f}" y="{T+13}" fill="#dc2626">'
                   f'η={rev["eta"]}</text>')

    for key in ("B", "E", "C", "D"):
        pts = " ".join(f"{px(e):.1f},{py(v):.1f}" for e, v in zip(etas, curves[key]))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{PALETTE[key]}" '
                   'stroke-width="2.4" stroke-linejoin="round"/>')

    ly = T + 6
    for key in ("B", "E", "C", "D"):
        out.append(f'<line x1="{L+pw+22}" y1="{ly}" x2="{L+pw+48}" y2="{ly}" '
                   f'stroke="{PALETTE[key]}" stroke-width="2.6"/>')
        out.append(f'<text class="lbl" x="{L+pw+54}" y="{ly+4}">{esc(LABELS[key])}</text>')
        ly += 24

    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+14}">Below η=0.22 the true</text>')
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+30}">cross-domain analogue wins.</text>')
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+46}">Above it, the near-miss does.</text>')
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+62}">Nothing about the structures</text>')
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+78}">changed — only the dial.</text>')

    return svg(W, H, "".join(out), "Tunable correspondence eta curves")


# ---------------------------------------------------------------------------
# Figure 2 — MDL gain across codes
# ---------------------------------------------------------------------------

def fig_mdl_bars(data: dict) -> str:
    W, H = 700, 380
    L, R, T, B = 62, 190, 54, 60
    pw, ph = W - L - R, H - T - B
    by_code = data["mdl"]["by_code"]
    codes = list(by_code)
    keys = ("B", "E", "C", "D")
    vals = [by_code[c]["scores"][k]["gain_bits"] for c in codes for k in keys]
    vmax = math.ceil(max(vals + [0]) / 10) * 10
    vmin = math.floor(min(vals + [0]) / 10) * 10
    span = (vmax - vmin) or 1

    def py(v): return T + ph - ((v - vmin) / span) * ph

    zero = py(0.0)
    out = ['<text class="ttl" x="24" y="26">F-06a MDL correspondence: the order holds, the sign does not</text>',
           '<text class="sub" x="24" y="43">Compression gain in bits. Above zero = knowing A lets you '
           'describe the other structure more cheaply.</text>']

    for i in range(7):
        v = vmin + i / 6 * span
        y = py(v)
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v:.0f}</text>')
    out.append(f'<line x1="{L}" y1="{zero:.1f}" x2="{L+pw}" y2="{zero:.1f}" '
               'stroke="var(--fg)" stroke-width="1.4" opacity="0.7"/>')
    out.append(f'<text class="lbl" transform="translate(18,{T+ph/2:.0f}) rotate(-90)" '
               'text-anchor="middle">compression gain (bits)</text>')

    gw = pw / len(codes)
    bw = gw / (len(keys) + 1.2)
    for ci, code in enumerate(codes):
        gx = L + ci * gw
        for ki, k in enumerate(keys):
            v = by_code[code]["scores"][k]["gain_bits"]
            x = gx + bw * 0.6 + ki * bw
            y = py(v)
            top, hgt = min(y, zero), abs(zero - y)
            out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw*0.82:.1f}" '
                       f'height="{hgt:.1f}" fill="{PALETTE[k]}" rx="2"/>')
            ty = (y - 5) if v >= 0 else (y + 13)
            out.append(f'<text class="tick" x="{x+bw*0.41:.1f}" y="{ty:.1f}" '
                       f'text-anchor="middle">{v:.0f}</text>')
        out.append(f'<text class="lbl" x="{gx+gw/2:.1f}" y="{T+ph+20}" '
                   f'text-anchor="middle">{code}</text>')
        out.append(f'<text class="sub" x="{gx+gw/2:.1f}" y="{T+ph+36}" text-anchor="middle">'
                   f'{esc(" > ".join(by_code[code]["ranking"]))}</text>')

    ly = T + 6
    for k in keys:
        out.append(f'<rect x="{L+pw+22}" y="{ly-9}" width="14" height="12" '
                   f'fill="{PALETTE[k]}" rx="2"/>')
        out.append(f'<text class="lbl" x="{L+pw+42}" y="{ly+1}">{k}</text>')
        out.append(f'<text class="sub" x="{L+pw+58}" y="{ly+1}">{esc(LABELS[k][4:])}</text>')
        ly += 22
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+16}">Ranking identical under all</text>')
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+32}">three codes. But flat32 puts</text>')
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+48}">every pair below zero — it</text>')
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+64}">rejects even the true analogue.</text>')
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+80}">Order is robust. The accept/</text>')
    out.append(f'<text class="sub" x="{L+pw+22}" y="{ly+96}">reject line is not.</text>')
    out.append(f'<text class="lbl" x="{L+pw/2:.0f}" y="{H-12}" text-anchor="middle">'
               'description-length code</text>')
    return svg(W, H, "".join(out), "MDL correspondence gain by code")


# ---------------------------------------------------------------------------
# Figure 3 — criticality blindness
# ---------------------------------------------------------------------------

def fig_criticality(data: dict) -> str:
    W, H = 700, 400
    L, R, T, B = 250, 40, 62, 46
    pw, ph = W - L - R, H - T - B
    rows = data["rows"]
    vmax = math.ceil(max(r["mdl_gain_bits"] for r in rows) / 5) * 5

    out = ['<text class="ttl" x="24" y="26">MDL is blind to which change matters</text>',
           '<text class="sub" x="24" y="43">Every single-edge flip in A, scored in bits. '
           'Red = flip inverts the feedback loop (runaway → self-limiting).</text>']

    bh = ph / len(rows)
    for i, r in enumerate(rows):
        y = T + i * bh
        crit = r["behaviour_changed"]
        col = "#dc2626" if crit else "#64748b"
        w = (r["mdl_gain_bits"] / vmax) * pw
        out.append(f'<text class="lbl" x="{L-10}" y="{y+bh/2+4:.1f}" text-anchor="end">'
                   f'{esc(r["edge"])}</text>')
        out.append(f'<rect x="{L}" y="{y+bh*0.18:.1f}" width="{w:.1f}" '
                   f'height="{bh*0.64:.1f}" fill="{col}" rx="2" opacity="0.9"/>')
        out.append(f'<text class="tick" x="{L+w+8:.1f}" y="{y+bh/2+4:.1f}">'
                   f'{r["mdl_gain_bits"]:.2f} bits'
                   f'{"  ← inverts behaviour" if crit else ""}</text>')

    xline = L + (19.727 / vmax) * pw
    out.append(f'<line x1="{xline:.1f}" y1="{T-6}" x2="{xline:.1f}" y2="{T+ph+4}" '
               'stroke="var(--fg)" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.6"/>')
    out.append(f'<text class="sub" x="{xline+6:.1f}" y="{T-10}">'
               'five of six flips score identically</text>')
    out.append(f'<text class="sub" x="24" y="{H-14}">The one outlier (22.96) is a benign flip. '
               'It scores highest only because it leaves the target with a single relation type — '
               'an alphabet artifact, not structure.</text>')
    return svg(W, H, "".join(out), "Criticality blindness")



# ---------------------------------------------------------------------------
# Figure 5 — the harness self-test matrix
# ---------------------------------------------------------------------------

def fig_harness(data: dict) -> str:
    res = data["results"]
    names = list(res)
    checks = list(next(iter(res.values()))["checks"])
    short = ["C1 ranks\ntrue analogue", "C2 sees past\nvocabulary",
             "C3 rejects\nrandom", "C4 discriminates\nat all",
             "C5 held-out\nstructure", "C6 rejects\nsuperset"]
    L, T = 190, 96
    cw, rh = 108, 30
    W, H = L + cw * len(checks) + 150, T + rh * len(names) + 54

    out = ['<text class="ttl" x="24" y="26">Harness self-test: can the laboratory catch a cheat?</text>',
           '<text class="sub" x="24" y="43">Seven deliberately fake methods and three real candidates, '
           'against six controls. A method is admitted only by passing all six.</text>']

    for i, lbl in enumerate(short):
        x = L + i * cw + cw / 2
        for j, line in enumerate(lbl.split("\n")):
            out.append(f'<text class="sub" x="{x:.0f}" y="{T - 22 + j * 12}" '
                       f'text-anchor="middle">{esc(line)}</text>')

    for r, name in enumerate(names):
        y = T + r * rh
        info = res[name]
        imp = info["is_impostor"]
        col = "#dc2626" if imp else "#2563eb"
        if r % 2 == 0:
            out.append(f'<rect x="{L-176}" y="{y-1}" width="{cw*len(checks)+300:.0f}" '
                       f'height="{rh-2}" fill="var(--fg)" opacity="0.035"/>')
        out.append(f'<text class="lbl" x="{L-16}" y="{y+rh/2+4:.0f}" '
                   f'text-anchor="end" fill="{col}">{esc(name)}</text>')
        for c, ck in enumerate(checks):
            ok = info["checks"][ck]
            cx, cy = L + c * cw + cw / 2, y + rh / 2
            out.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="8.5" '
                       f'fill="{"#15803d" if ok else "#dc2626"}" opacity="0.88"/>')
            out.append(f'<text x="{cx:.0f}" y="{cy+3.5:.0f}" text-anchor="middle" '
                       f'fill="#fff" font-size="11" font-family="sans-serif">'
                       f'{"OK" if ok else "X"}</text>')
        if imp:
            verdict, vc = ("CAUGHT", "#15803d") if not info["passed_all"] else ("MISSED", "#dc2626")
        else:
            verdict, vc = ("ADMITTED", "#15803d") if info["passed_all"] else ("rejected", "#6b7280")
        out.append(f'<text class="lbl" x="{L+cw*len(checks)+16}" y="{y+rh/2+4:.0f}" '
                   f'fill="{vc}">{verdict}</text>')

    out.append(f'<text class="sub" x="24" y="{H-14}">'
               'Red names are impostors, blue are real candidates. '
               f'{data["n_impostors_caught"]}/{data["n_impostors"]} impostors caught; '
               f'admitted: {esc(", ".join(data["candidates_passing"]) or "none")}.</text>')
    return svg(W, H, "".join(out), "Harness self-test matrix")


# ---------------------------------------------------------------------------
# Figure 4 — the five conditions as motifs
# ---------------------------------------------------------------------------

def fig_motifs(structures: list) -> str:
    cols, cw, ch = 5, 212, 282
    W, H = cols * cw, ch + 30
    out = ['<defs>'
           '<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5.5" '
           'markerHeight="5.5" orient="auto-start-reverse">'
           '<path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker>'
           '<marker id="ahn" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5.5" '
           'markerHeight="5.5" orient="auto-start-reverse">'
           '<path d="M 0 0 L 10 5 L 0 10 z" fill="#dc2626"/></marker>'
           '</defs>']

    for ci, (key, s, note) in enumerate(structures):
        ox, oy = ci * cw, 46
        cx, cy, rad = ox + cw / 2, oy + 112, 74
        pos = {}
        for i, v in enumerate(s.nodes):
            ang = -math.pi / 2 + 2 * math.pi * i / len(s.nodes)
            pos[v] = (cx + rad * math.cos(ang), cy + rad * math.sin(ang))

        out.append(f'<text class="ttl" x="{ox+14}" y="26">{key}</text>')
        out.append(f'<text class="sub" x="{ox+14}" y="42">{esc(note)}</text>')

        neg_types = {"NEG", "PRUNES"}
        for r in s.relations:
            x1, y1 = pos[r.src]
            x2, y2 = pos[r.dst]
            dx, dy = x2 - x1, y2 - y1
            d = math.hypot(dx, dy) or 1
            x1 += dx / d * 20; y1 += dy / d * 20
            x2 -= dx / d * 22; y2 -= dy / d * 22
            mx, my = (x1 + x2) / 2 - dy / d * 13, (y1 + y2) / 2 + dx / d * 13
            neg = r.rtype in neg_types
            col = "#dc2626" if neg else "#64748b"
            dash = ' stroke-dasharray="5 3"' if neg else ""
            mk = "ahn" if neg else "ah"
            out.append(f'<path d="M {x1:.1f} {y1:.1f} Q {mx:.1f} {my:.1f} {x2:.1f} {y2:.1f}" '
                       f'fill="none" stroke="{col}" stroke-width="1.7"{dash} '
                       f'marker-end="url(#{mk})" opacity="0.95"/>')

        for v, (x, y) in pos.items():
            out.append(f'<circle class="node" cx="{x:.1f}" cy="{y:.1f}" r="19"/>')
            label = v if len(v) <= 9 else v[:8] + "…"
            out.append(f'<text class="ntxt" x="{x:.1f}" y="{y+3.5:.1f}">{esc(label)}</text>')

    out.append(f'<text class="sub" x="14" y="{H-8}">'
               'Solid grey = reinforcing relation. Dashed red = suppressing relation. '
               'A and E differ by exactly one edge type.</text>')
    return svg(W, H, "".join(out), "Condition motifs A through E")


# ---------------------------------------------------------------------------

def main() -> None:
    import sys
    sys.path.insert(0, str(ROOT / "lab"))
    from worlds import A, B, B2, C, D, E, F  # noqa: E402

    a = json.loads((RESULTS / "exp000a.json").read_text())
    b = json.loads((RESULTS / "exp000b.json").read_text())
    c = json.loads((RESULTS / "exp000c.json").read_text())

    figs = {
        "fig1_eta_curves.svg": fig_eta_curves(a),
        "fig2_mdl_gain.svg": fig_mdl_bars(a),
        "fig3_criticality.svg": fig_criticality(b),
        "fig4_conditions.svg": fig_motifs([
            ("A", A, "reference motif"),
            ("B", B, "same structure, new words"),
            ("C", C, "same words, no loop"),
            ("D", D, "matched random"),
            ("E", E, "one edge flipped"),
        ]),
        "fig5_harness.svg": fig_harness(c),
        "fig6_superset.svg": fig_motifs([
            ("F", F, "superset distractor — contains all of A"),
            ("B2", B2, "held-out analogue, third vocabulary"),
        ]),
    }

    FIGURES.mkdir(parents=True, exist_ok=True)
    targets = [FIGURES,
               Path("/home/lee/Desktop/RelationalMetrics/figures"),
               Path("/home/lee/.claude/projects/-home-lee/memory/projects/"
                    "relational-metrics/assets/figures")]
    for t in targets:
        t.mkdir(parents=True, exist_ok=True)
    for name, content in figs.items():
        for t in targets:
            (t / name).write_text(content)
        print(f"  wrote {name}  ({len(content)//1024} KB) x{len(targets)}")

    (RESULTS / "figures_inline.json").write_text(json.dumps(figs))
    for j in ("exp000a.json", "exp000b.json"):
        shutil.copy(RESULTS / j, Path("/home/lee/Desktop/RelationalMetrics") / j)
    print(f"\n  results JSON copied to Desktop")


if __name__ == "__main__":
    main()
