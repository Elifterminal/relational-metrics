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
# Figure 7 — arity: what the pairs can see vs what the triple can see
# ---------------------------------------------------------------------------

def fig_arity(data: dict) -> str:
    W, H = 780, 430
    L, R, T, B = 62, 176, 58, 74
    pw, ph = W - L - R, H - T - B
    big = str(data["sample_sizes"][-1])
    worlds = list(data["results"])
    series = [("best pair", "#94a3b8"), ("all three", "#2563eb"), ("Omega", "#dc2626")]
    vals = []
    for w in worlds:
        d = data["results"][w]["by_n"][big]
        vals += [d["profile"]["best_pair"], d["profile"]["triple"], d["omega_raw"]]
    vmax = math.ceil(max(vals + [0]) * 10) / 10
    vmin = min(math.floor(min(vals + [0]) * 10) / 10, 0.0)
    span = (vmax - vmin) or 1

    def py(v): return T + ph - ((v - vmin) / span) * ph
    zero = py(0.0)

    out = ['<text class="ttl" x="24" y="26">Arity: information visible to the pairs vs to the whole triple</text>',
           '<text class="sub" x="24" y="43">Mutual information with the outcome, in bits. '
           'Omega is the remainder after subtracting everything the subsets already explain.</text>']

    for i in range(6):
        v = vmin + i / 5 * span
        y = py(v)
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v:.1f}</text>')
    out.append(f'<line x1="{L}" y1="{zero:.1f}" x2="{L+pw}" y2="{zero:.1f}" '
               'stroke="var(--fg)" stroke-width="1.3" opacity="0.65"/>')

    gw = pw / len(worlds)
    bw = gw / (len(series) + 1.3)
    for wi, w in enumerate(worlds):
        d = data["results"][w]["by_n"][big]
        gx = L + wi * gw
        vv = [d["profile"]["best_pair"], d["profile"]["triple"], d["omega_raw"]]
        for si, ((lbl, col), v) in enumerate(zip(series, vv)):
            x = gx + bw * 0.65 + si * bw
            y = py(v)
            out.append(f'<rect x="{x:.1f}" y="{min(y,zero):.1f}" width="{bw*0.8:.1f}" '
                       f'height="{abs(zero-y):.1f}" fill="{col}" rx="2"/>')
        arity = data["results"][w]["true_arity"]
        out.append(f'<text class="lbl" x="{gx+gw/2:.1f}" y="{T+ph+20}" '
                   f'text-anchor="middle">{esc(w)}</text>')
        out.append(f'<text class="sub" x="{gx+gw/2:.1f}" y="{T+ph+35}" '
                   f'text-anchor="middle">true arity {arity}</text>')

    ly = T + 8
    for lbl, col in series:
        out.append(f'<rect x="{L+pw+20}" y="{ly-9}" width="13" height="12" fill="{col}" rx="2"/>')
        out.append(f'<text class="lbl" x="{L+pw+39}" y="{ly+1}">{esc(lbl)}</text>')
        ly += 21
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+16}">order3: the pairs see</text>')
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+31}">NOTHING (0.0008) while</text>')
    out.append(f'<text class="sub" x="{L+pw+31}" y="{ly+46}">the triple sees 0.734.</text>')
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+68}">redundant: Omega fires</text>')
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+83}">positive with ZERO</text>')
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+98}">synergy present.</text>')
    out.append(f'<text class="sub" x="24" y="{H-14}">'
               'The claim the project rests on is visible in `order3`. The defect that '
               'demotes the statistic is visible in `redundant`.</text>')
    return svg(W, H, "".join(out), "Arity: pairs vs triple")


# ---------------------------------------------------------------------------
# Figure 8 — connected information by order (F-04a)
# ---------------------------------------------------------------------------

def fig_orders(data: dict) -> str:
    W, H = 780, 420
    L, R, T, B = 62, 200, 58, 74
    pw, ph = W - L - R, H - T - B
    worlds = list(data["results"])
    orders = [("order 2 (pairwise)", "#94a3b8", "order2"),
              ("order 3", "#2563eb", "order3"),
              ("order 4 (all three + outcome)", "#dc2626", "order4")]
    vmax = math.ceil(max(sum(max(data["results"][w][k], 0) for _, _, k in orders)
                         for w in worlds) * 4) / 4

    out = ['<text class="ttl" x="24" y="26">F-04a: structure lands at the order it actually belongs to</text>',
           '<text class="sub" x="24" y="43">Connected information in bits — how much the maximum '
           'possible entropy drops once marginals of that order are known.</text>']
    for i in range(6):
        v = i / 5 * vmax
        y = T + ph - (v / vmax) * ph
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v:.2f}</text>')

    gw = pw / len(worlds)
    bw = gw * 0.5
    for wi, w in enumerate(worlds):
        d = data["results"][w]
        gx = L + wi * gw + (gw - bw) / 2
        acc = 0.0
        for lbl, col, key in orders:
            v = max(d[key], 0.0)
            if v <= 0:
                continue
            h = (v / vmax) * ph
            y = T + ph - (acc / vmax) * ph - h
            out.append(f'<rect x="{gx:.1f}" y="{y:.1f}" width="{bw:.1f}" '
                       f'height="{h:.1f}" fill="{col}" rx="1.5"/>')
            acc += v
        sig = " *" if d["significant"] else ""
        out.append(f'<text class="lbl" x="{gx+bw/2:.1f}" y="{T+ph+20}" '
                   f'text-anchor="middle">{esc(w)}</text>')
        out.append(f'<text class="sub" x="{gx+bw/2:.1f}" y="{T+ph+35}" '
                   f'text-anchor="middle">arity {d["true_arity"]}{sig}</text>')

    ly = T + 8
    for lbl, col, _ in orders:
        out.append(f'<rect x="{L+pw+20}" y="{ly-9}" width="13" height="12" fill="{col}" rx="2"/>')
        out.append(f'<text class="lbl" x="{L+pw+39}" y="{ly+1}">{esc(lbl)}</text>')
        ly += 21
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+16}">order2 -&gt; order 3.</text>')
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+31}">order3 -&gt; order 4.</text>')
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+52}">redundant puts ALL of</text>')
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+67}">its 1.23 bits at order 2</text>')
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+82}">— where it belongs.</text>')
    out.append(f'<text class="sub" x="{L+pw+20}" y="{ly+97}">F-04 called it 3-way.</text>')
    out.append(f'<text class="sub" x="24" y="{H-14}">'
               '* marks a significant order-4 term against a 120-permutation null. '
               'Every term is non-negative by construction, and they sum to the total.</text>')
    return svg(W, H, "".join(out), "Connected information by order")


# ---------------------------------------------------------------------------
# Figure 9 — raw structure vs outcome-relevant structure
# ---------------------------------------------------------------------------

def fig_relevance(data: dict) -> str:
    W, H = 800, 400
    L, R, T, B = 210, 190, 62, 56
    pw, ph = W - L - R, H - T - B
    picks = [
        ("driver_only_3way", "order3", "p_order3"),
        ("driver_only_pairwise", "order2", None),
        ("mixed", "order3", "p_order3"),
        ("mixed", "order2", None),
        ("deterministic", "order4", "p_order4"),
        ("synergy_100", "order4", "p_order4"),
        ("synergy_050", "order4", "p_order4"),
        ("synergy_000", "order4", "p_order4"),
    ]
    rows = []
    for w, key, pk in picks:
        r = data["results"][w]
        pv = r[pk] if pk else 1.0
        rows.append((f"{w}  ·  I_C({key[-1]})", r[key], pv < 0.05))
    vmax = max(v for _, v, _ in rows) * 1.05 or 1.0

    out = ['<text class="ttl" x="24" y="26">Structure is objective. Relevance is not.</text>',
           '<text class="sub" x="24" y="44">Bar length is the raw connected information — '
           'how much structure is there. Colour is whether it survives shuffling the '
           'outcome.</text>']
    bh = ph / len(rows)
    for i, (lbl, v, sig) in enumerate(rows):
        y = T + i * bh
        col = "#2563eb" if sig else "#94a3b8"
        w = (v / vmax) * pw
        out.append(f'<text class="lbl" x="{L-12}" y="{y+bh/2+4:.1f}" '
                   f'text-anchor="end">{esc(lbl)}</text>')
        out.append(f'<rect x="{L}" y="{y+bh*0.2:.1f}" width="{max(w,1):.1f}" '
                   f'height="{bh*0.6:.1f}" fill="{col}" rx="2"/>')
        tag = "about the outcome" if sig else "NOT about the outcome"
        out.append(f'<text class="tick" x="{L+max(w,1)+9:.1f}" y="{y+bh/2+4:.1f}" '
                   f'fill="{col}">{v:.4f}  —  {tag}</text>')

    out.append(f'<text class="sub" x="24" y="{H-30}">'
               'The top two rows carry a FULL BIT of genuine structure and say nothing '
               'whatever about the outcome. The raw statistic cannot tell the difference;</text>')
    out.append(f'<text class="sub" x="24" y="{H-14}">'
               'the calibration can, because shuffling only the outcome leaves structure '
               'among the participants intact in the null.</text>')
    return svg(W, H, "".join(out), "Structure versus relevance")


# ---------------------------------------------------------------------------
# Figure 10 — the cliff: what partial observation does to higher-order structure
# ---------------------------------------------------------------------------

def fig_cliff(data: dict) -> str:
    W, H = 760, 380
    L, R, T, B = 250, 150, 66, 62
    pw, ph = W - L - R, H - T - B
    b = data["probe_b_which_participants"]
    rows = [
        ("all three participants", b["all_three_participants"]["I_C(4)"], True),
        ("missing one (c)", b["missing_c"]["I_C(3)"], False),
        ("missing one (b)", b["missing_b"]["I_C(3)"], False),
        ("missing one, 5x the data", b["more_data_rescue"]["40000"]["I_C_top"], False),
    ]
    vmax = max(v for _, v, _ in rows) or 1.0

    out = ['<text class="ttl" x="24" y="26">Partial observation does not weaken higher-order structure. It erases it.</text>',
           '<text class="sub" x="24" y="45">The same three-way dependence, measured with every '
           'participant visible and with one hidden.</text>']
    bh = ph / len(rows)
    for i, (lbl, v, full) in enumerate(rows):
        y = T + i * bh
        col = "#2563eb" if full else "#dc2626"
        w = max((v / vmax) * pw, 1.2)
        out.append(f'<text class="lbl" x="{L-12}" y="{y+bh/2+4:.1f}" '
                   f'text-anchor="end">{esc(lbl)}</text>')
        out.append(f'<rect x="{L}" y="{y+bh*0.22:.1f}" width="{w:.1f}" '
                   f'height="{bh*0.56:.1f}" fill="{col}" rx="2"/>')
        txt = f"{v:.5f}" if v < 0.01 else f"{v:.4f}"
        out.append(f'<text class="tick" x="{L+w+9:.1f}" y="{y+bh/2+4:.1f}" '
                   f'fill="{col}">{txt}</text>')

    out.append(f'<text class="sub" x="24" y="{H-40}">'
               'A three-way dependence marginalised over one of its three participants is '
               'uniform. There is nothing left to detect —</text>')
    out.append(f'<text class="sub" x="24" y="{H-24}">'
               'not a faint signal, nothing. Five times the data moves it from 0.00005 to '
               '0.00006. This is an identifiability limit,</text>')
    out.append(f'<text class="sub" x="24" y="{H-8}">'
               'not a power limit: no quantity of observation recovers it.</text>')
    return svg(W, H, "".join(out), "The partial observation cliff")


# ---------------------------------------------------------------------------
# Figure 11 — the cliff is a gradient
# ---------------------------------------------------------------------------

def fig_gradient(data: dict) -> str:
    W, H = 800, 400
    L, R, T, B = 62, 250, 62, 58
    pw, ph = W - L - R, H - T - B
    ws = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    curve = []
    for w in ws:
        v = data["sweep_involvement"][f"w_{w:.1f}"]
        full = v["full_bits"]
        curve.append(v["per_hidden"]["c"] / full if full > 1e-9 else 0.0)

    def px(w): return L + w * pw
    def py(v): return T + ph - v * ph

    out = ['<text class="ttl" x="24" y="26">The cliff is the endpoint of a gradient, not a wall</text>',
           '<text class="sub" x="24" y="44">Information retained after hiding one participant, '
           'as that participant goes from irrelevant to essential.</text>']
    for i in range(6):
        v = i / 5
        y = py(v)
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v:.1f}</text>')
    for w in ws:
        x = px(w)
        out.append(f'<text class="tick" x="{x:.1f}" y="{T+ph+18}" text-anchor="middle">{w:.1f}</text>')
    out.append(f'<text class="lbl" x="{L+pw/2:.0f}" y="{H-14}" text-anchor="middle">'
               'how often the hidden participant actually matters</text>')
    out.append(f'<text class="lbl" transform="translate(18,{T+ph/2:.0f}) rotate(-90)" '
               'text-anchor="middle">information retained</text>')

    pts = " ".join(f"{px(w):.1f},{py(v):.1f}" for w, v in zip(ws, curve))
    out.append(f'<polyline points="{pts}" fill="none" stroke="#2563eb" stroke-width="2.6"/>')
    for w, v in zip(ws, curve):
        out.append(f'<circle cx="{px(w):.1f}" cy="{py(v):.1f}" r="4" fill="#2563eb"/>')
        out.append(f'<text class="tick" x="{px(w):.1f}" y="{py(v)-11:.1f}" '
                   f'text-anchor="middle">{v:.2f}</text>')

    # reference band for real structures
    types = data["sweep_structure_type"]
    band = [v["retention_best"] for k, v in types.items() if not k.startswith("parity")]
    lo, hi = min(band), max(band)
    out.append(f'<rect x="{L}" y="{py(hi):.1f}" width="{pw}" height="{py(lo)-py(hi):.1f}" '
               'fill="#15803d" opacity="0.10"/>')
    out.append(f'<text class="sub" x="{L+8}" y="{py(hi)-6:.1f}" fill="#15803d">'
               'where AND / OR / majority / threshold actually sit</text>')

    ly = T + 10
    for lbl in ["parity is the ONLY structure", "that vanishes completely.",
                "It is built so no subset",
                "carries any information —", "the worst case, by",
                "construction.", "",
                "Everything with lower-order",
                "leakage keeps roughly half",
                "of what it had."]:
        out.append(f'<text class="sub" x="{L+pw+22}" y="{ly}">{esc(lbl)}</text>')
        ly += 16
    return svg(W, H, "".join(out), "Retention gradient")


# ---------------------------------------------------------------------------
# Figure 12 — exhaustive census: retention is quantised
# ---------------------------------------------------------------------------

def fig_census(data: dict) -> str:
    W, H = 800, 400
    L, R, T, B = 70, 210, 66, 66
    pw, ph = W - L - R, H - T - B
    classes = data["retention_classes"]
    vals = [c["retention"] for c in classes]
    counts = [c["count"] for c in classes]
    cmax = max(counts)

    out = ['<text class="ttl" x="24" y="26">All 256 Boolean functions of three variables, computed exactly</text>',
           '<text class="sub" x="24" y="45">Retention takes only SEVEN distinct values. It is '
           'quantised, not continuous — and one half is a real class.</text>']
    for i in range(5):
        v = i / 4 * cmax
        y = T + ph - (v / cmax) * ph
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v:.0f}</text>')
    out.append(f'<text class="lbl" transform="translate(22,{T+ph/2:.0f}) rotate(-90)" '
               'text-anchor="middle">how many functions</text>')
    out.append(f'<text class="lbl" x="{L+pw/2:.0f}" y="{H-12}" text-anchor="middle">'
               'information retained after hiding one participant</text>')

    bw = pw / len(classes)
    for i, c in enumerate(classes):
        x = L + i * bw + bw * 0.16
        hgt = (c["count"] / cmax) * ph
        y = T + ph - hgt
        v = c["retention"]
        col = "#2563eb" if abs(v - 0.5) < 1e-6 else ("#dc2626" if v < 1e-6 else "#94a3b8")
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw*0.68:.1f}" '
                   f'height="{hgt:.1f}" fill="{col}" rx="2"/>')
        out.append(f'<text class="tick" x="{x+bw*0.34:.1f}" y="{y-6:.1f}" '
                   f'text-anchor="middle">{c["count"]}</text>')
        out.append(f'<text class="lbl" x="{x+bw*0.34:.1f}" y="{T+ph+20}" '
                   f'text-anchor="middle">{v:.3f}</text>')
        if c.get("label"):
            out.append(f'<text class="sub" x="{x+bw*0.34:.1f}" y="{T+ph+36}" '
                       f'text-anchor="middle" fill="{col}">{esc(c["label"])}</text>')

    ly = T + 12
    for lbl in ["0.500 is a REAL class:", "56 functions, every one of",
                "them balanced (four ones", "in its truth table).",
                "Majority is one of them.", "",
                "But AND and OR sit at",
                "0.540 — a DIFFERENT class.",
                "They only looked like 0.5",
                "because 5% noise pulled",
                "them there.", "",
                "Parity alone reaches zero."]:
        out.append(f'<text class="sub" x="{L+pw+20}" y="{ly}">{esc(lbl)}</text>')
        ly += 15
    return svg(W, H, "".join(out), "Retention census")


# ---------------------------------------------------------------------------
# Figure 13 — quantisation at k=4, and the closed form
# ---------------------------------------------------------------------------

def fig_k4(data: dict) -> str:
    W, H = 800, 400
    L, R, T, B = 70, 210, 100, 64
    pw, ph = W - L - R, H - T - B
    cls = data["census_k4"]["top_classes"]
    cmax = max(c["count"] for c in cls)

    out = ['<text class="ttl" x="24" y="26">Quantisation survives at four variables — and there is a closed form</text>',
           '<text class="sub" x="24" y="45">All 65,536 Boolean functions of four variables, '
           'computed exactly. Only 21 distinct retention values.</text>',
           f'<rect x="24" y="56" width="{W-48}" height="30" fill="var(--fg)" opacity="0.05" rx="6"/>',
           '<text class="ttl" x="{}" y="76" text-anchor="middle">'.format(W // 2) +
           'retention  =  1  −  Influence(hidden participant) / H(outcome)</text>']

    for i in range(5):
        v = i / 4 * cmax
        y = T + ph - (v / cmax) * ph
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v/1000:.0f}k</text>')
    out.append(f'<text class="lbl" transform="translate(22,{T+ph/2:.0f}) rotate(-90)" '
               'text-anchor="middle">functions</text>')

    bw = pw / len(cls)
    for i, c in enumerate(cls):
        x = L + i * bw + bw * 0.14
        hgt = (c["count"] / cmax) * ph
        y = T + ph - hgt
        v = c["retention"]
        col = "#2563eb" if abs(v - 0.5) < 1e-9 else "#94a3b8"
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw*0.72:.1f}" '
                   f'height="{max(hgt,1.5):.1f}" fill="{col}" rx="2"/>')
        out.append(f'<text class="tick" x="{x+bw*0.36:.1f}" y="{T+ph+18}" '
                   f'text-anchor="middle" transform="rotate(-40 {x+bw*0.36:.1f} {T+ph+18})">'
                   f'{v:.3f}</text>')

    ly = T + 6
    for lbl in ["k=3:  7 distinct values", "k=4: 21 distinct values", "",
                "out of 65,534 functions.", "",
                "Parity is still the unique",
                "zero — the only function",
                "where every participant",
                "has maximal influence.", "",
                "5,896 functions sit at",
                "exactly one half."]:
        out.append(f'<text class="sub" x="{L+pw+20}" y="{ly}">{esc(lbl)}</text>')
        ly += 15
    out.append(f'<text class="sub" x="24" y="{H-10}">'
               'Verified against brute-force exact mutual information on every k=3 function and '
               '478 at k=4: maximum error 1.1e-16.</text>')
    return svg(W, H, "".join(out), "k=4 census and closed form")


# ---------------------------------------------------------------------------
# Figure 14 — the law under noise
# ---------------------------------------------------------------------------

def fig_noise(data: dict) -> str:
    W, H = 800, 400
    L, R, T, B = 70, 230, 62, 60
    pw, ph = W - L - R, H - T - B
    ver = data["verification_k3"]
    noises = [float(k) for k in ver]
    det_err = [ver[k]["max_error_deterministic_form"] for k in ver]
    emax = max(det_err) * 1.15 or 1.0

    def px(i): return L + (i / (len(noises) - 1)) * pw
    def py(v): return T + ph - (v / emax) * ph

    out = ['<text class="ttl" x="24" y="26">The deterministic law breaks under noise. The general one does not.</text>',
           '<text class="sub" x="24" y="44">Worst-case error against brute-force exact mutual '
           'information, across all 254 functions at each noise level.</text>']
    for i in range(5):
        v = i / 4 * emax
        y = py(v)
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v:.02f}</text>')
    for i, e in enumerate(noises):
        out.append(f'<text class="tick" x="{px(i):.1f}" y="{T+ph+18}" '
                   f'text-anchor="middle">{e:.2f}</text>')
    out.append(f'<text class="lbl" x="{L+pw/2:.0f}" y="{H-14}" text-anchor="middle">'
               'noise level</text>')
    out.append(f'<text class="lbl" transform="translate(22,{T+ph/2:.0f}) rotate(-90)" '
               'text-anchor="middle">worst-case error</text>')

    pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(det_err))
    out.append(f'<polyline points="{pts}" fill="none" stroke="#dc2626" stroke-width="2.6"/>')
    for i, v in enumerate(det_err):
        out.append(f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="4" fill="#dc2626"/>')
        if v > 0:
            out.append(f'<text class="tick" x="{px(i):.1f}" y="{py(v)-11:.1f}" '
                       f'text-anchor="middle" fill="#dc2626">{v:.3f}</text>')
    out.append(f'<line x1="{L}" y1="{py(0):.1f}" x2="{L+pw}" y2="{py(0):.1f}" '
               'stroke="#15803d" stroke-width="2.6"/>')
    out.append(f'<text class="tick" x="{L+8}" y="{py(0)-8:.1f}" fill="#15803d">'
               'general form — error ~1e-16 everywhere</text>')

    ly = T + 8
    for lbl in ["retention_e =",
                "  1 - I(1-h(e)) / (H_e - h(e))", "",
                "Balanced outcomes are",
                "EXACTLY noise-invariant:",
                "drift 0.00e+00. H_e stays 1,",
                "the noise term cancels, and",
                "retention = 1 - Influence.", "",
                "That is why majority never",
                "moved and AND did — an",
                "observation that sat",
                "unexplained for two",
                "experiments."]:
        out.append(f'<text class="sub" x="{L+pw+20}" y="{ly}">{esc(lbl)}</text>')
        ly += 15
    return svg(W, H, "".join(out), "The law under noise")


# ---------------------------------------------------------------------------
# Figure 15 — the reordering audit
# ---------------------------------------------------------------------------

def fig_audit(data: dict) -> str:
    W, H = 800, 360
    L, R, T, B = 290, 170, 66, 56
    pw, ph = W - L - R, H - T - B
    a = data["audits"]
    rows = [
        ("arity  (k=3 vs k=4)", a["A_retention_vs_arity"]["agreement"], a["A_retention_vs_arity"]["discordant"]),
        ("which participant is hidden", a["B_retention_vs_which_hidden"]["agreement"], a["B_retention_vs_which_hidden"]["discordant"]),
        ("sample size", min(v["agreement"] for v in a["C_connected_info_vs_sample_size"]["comparisons"].values()),
         max(v["discordant"] for v in a["C_connected_info_vs_sample_size"]["comparisons"].values())),
        ("noise level", min(v["agreement"] for v in a["D_connected_info_vs_noise"]["comparisons"].values()),
         max(v["discordant"] for v in a["D_connected_info_vs_noise"]["comparisons"].values())),
        ("description code  (control)", min(v["agreement"] for v in a["E_mdl_vs_code_CONTROL"]["comparisons"].values()),
         max(v["discordant"] for v in a["E_mdl_vs_code_CONTROL"]["comparisons"].values())),
    ]

    out = ['<text class="ttl" x="24" y="26">Does varying this change the ORDER of the answer?</text>',
           '<text class="sub" x="24" y="44">Rank agreement with the reference setting. 1.0 means '
           'nothing swapped; below 1.0 means decisions change.</text>']

    def px(v): return L + ((v + 0.25) / 1.25) * pw
    for tick in (-0.25, 0.0, 0.25, 0.5, 0.75, 1.0):
        x = px(tick)
        out.append(f'<line class="ax" x1="{x:.1f}" y1="{T-6}" x2="{x:.1f}" y2="{T+ph}"/>')
        out.append(f'<text class="tick" x="{x:.1f}" y="{T+ph+18}" '
                   f'text-anchor="middle">{tick:.2f}</text>')
    x1 = px(1.0)
    out.append(f'<line x1="{x1:.1f}" y1="{T-6}" x2="{x1:.1f}" y2="{T+ph}" '
               'stroke="#15803d" stroke-width="1.6" stroke-dasharray="4 3"/>')

    bh = ph / len(rows)
    for i, (lbl, agr, disc) in enumerate(rows):
        y = T + i * bh
        col = "#15803d" if disc == 0 else ("#dc2626" if agr < 0.5 else "#d97706")
        out.append(f'<text class="lbl" x="{L-14}" y="{y+bh/2+4:.1f}" '
                   f'text-anchor="end">{esc(lbl)}</text>')
        x0, xe = px(-0.25), px(agr)
        out.append(f'<rect x="{min(x0,xe):.1f}" y="{y+bh*0.24:.1f}" '
                   f'width="{abs(xe-x0):.1f}" height="{bh*0.52:.1f}" fill="{col}" rx="2"/>')
        tag = "order preserved" if disc == 0 else f"{disc:,} pairs swap"
        out.append(f'<text class="tick" x="{xe+9:.1f}" y="{y+bh/2+4:.1f}" '
                   f'fill="{col}">{agr:.3f} — {tag}</text>')

    out.append(f'<text class="sub" x="24" y="{H-30}">'
               '"Which participant is hidden" comes out slightly ANTI-correlated: best-case and '
               'worst-case retention rank structures</text>')
    out.append(f'<text class="sub" x="24" y="{H-14}">'
               'almost oppositely. Retention is not one number — it is one number per '
               'participant you might lose.</text>')
    return svg(W, H, "".join(out), "Reordering audit")


# ---------------------------------------------------------------------------
# Figure 16 — retention is a vector, not a number
# ---------------------------------------------------------------------------

def fig_vector(data: dict) -> str:
    W, H = 800, 360
    L, R, T, B = 74, 200, 78, 58
    pw, ph = W - L - R, H - T - B
    c3 = data["census"]["k=3"]; c4 = data["census"]["k=4"]
    groups = [("functions that vanish\n(lose everything)", c3["at_zero_best"], c3["at_zero_worst"], c3["scored"]),
              ("functions at exactly 0.5", c3["at_half_best"], c3["at_half_worst"], c3["scored"])]

    out = ['<text class="ttl" x="24" y="26">Which participant you lose changes the answer — often completely</text>',
           '<text class="sub" x="24" y="45">Same functions, same law. Only the choice of which '
           'participant is missing differs.</text>']
    bh = ph / 2
    vmax = max(max(a, b) for _, a, b, _ in groups) * 1.25
    for i, (lbl, best, worst, tot) in enumerate(groups):
        y = T + i * bh
        for j, (tag, v, col) in enumerate((("best case  (lose your least important)", best, "#2563eb"),
                                           ("WORST case (lose your most important)", worst, "#dc2626"))):
            yy = y + j * (bh * 0.42) + 6
            w = max((v / vmax) * pw, 1.5)
            out.append(f'<text class="sub" x="{L-12}" y="{yy+11:.1f}" text-anchor="end">{esc(tag)}</text>')
            out.append(f'<rect x="{L}" y="{yy:.1f}" width="{w:.1f}" height="{bh*0.3:.1f}" '
                       f'fill="{col}" rx="2"/>')
            out.append(f'<text class="tick" x="{L+w+9:.1f}" y="{yy+bh*0.21:.1f}" '
                       f'fill="{col}">{v} of {tot}</text>')
        out.append(f'<text class="lbl" x="24" y="{y+16:.0f}">{esc(lbl.split(chr(10))[0])}</text>')

    ly = T + 4
    for lbl in ["Parity is unique in", "vanishing NO MATTER which",
                "participant you lose.", "",
                "38 functions at k=3 and 942",
                "at k=4 vanish if you lose",
                "the WRONG one.", "",
                "Median spread within a",
                "function: 0.52 at k=3.",
                "Only 39% have no spread."]:
        out.append(f'<text class="sub" x="{L+pw+18}" y="{ly}">{esc(lbl)}</text>')
        ly += 15
    out.append(f'<text class="sub" x="24" y="{H-12}">'
               'Every earlier finding here summarised retention with the best case. The law was '
               'always per-participant; the summary was the error.</text>')
    return svg(W, H, "".join(out), "Retention is a vector")


# ---------------------------------------------------------------------------
# Figure 17 — asymmetric families: the spread the old set could not show
# ---------------------------------------------------------------------------

def fig_asym(data: dict) -> str:
    W, H = 800, 380
    L, R, T, B = 168, 190, 66, 60
    pw, ph = W - L - R, H - T - B
    fams = data["families"]
    names = list(fams)

    out = ['<text class="ttl" x="24" y="26">Asymmetric families — retention is a range, not a point</text>',
           '<text class="sub" x="24" y="45">Each dot is one participant. The blue marker is what a '
           'best-case summary would have reported.</text>']
    for i in range(6):
        v = i / 5
        x = L + v * pw
        out.append(f'<line class="ax" x1="{x:.1f}" y1="{T-4}" x2="{x:.1f}" y2="{T+ph}"/>')
        out.append(f'<text class="tick" x="{x:.1f}" y="{T+ph+18}" '
                   f'text-anchor="middle">{v:.1f}</text>')
    out.append(f'<text class="lbl" x="{L+pw/2:.0f}" y="{H-14}" text-anchor="middle">'
               'information retained after losing that participant</text>')

    bh = ph / len(names)
    for i, n in enumerate(names):
        r = fams[n]
        y = T + i * bh + bh / 2
        vals = r["retention_per_participant"]
        lo, hi = min(vals), max(vals)
        sym = r["spread"] < 1e-9
        out.append(f'<text class="lbl" x="{L-14}" y="{y+4:.1f}" text-anchor="end">{esc(n)}</text>')
        if not sym:
            out.append(f'<line x1="{L+lo*pw:.1f}" y1="{y:.1f}" x2="{L+hi*pw:.1f}" '
                       f'y2="{y:.1f}" stroke="var(--fg)" stroke-width="2" opacity="0.3"/>')
        for v in vals:
            col = "#dc2626" if v < 1e-9 else "#64748b"
            out.append(f'<circle cx="{L+v*pw:.1f}" cy="{y:.1f}" r="5" fill="{col}"/>')
        out.append(f'<circle cx="{L+hi*pw:.1f}" cy="{y:.1f}" r="7" fill="none" '
                   'stroke="#2563eb" stroke-width="2.2"/>')
        tag = "influence-symmetric — spread 0" if sym else f"spread {r['spread']:.3f}"
        out.append(f'<text class="tick" x="{L+pw+14}" y="{y+4:.1f}" '
                   f'fill="{"#15803d" if sym else "var(--mut)"}">{esc(tag)}</text>')

    out.append(f'<text class="sub" x="24" y="{H-38}">'
               'Red dots are total loss. Two families VANISH if you lose one particular '
               'participant while retaining half or three quarters</text>')
    out.append(f'<text class="sub" x="24" y="{H-24}">'
               'if you lose any other. `mux` is the control: not permutation-symmetric at all, '
               'yet every participant matters equally — which is why</text>')
    out.append(f'<text class="sub" x="24" y="{H-10}">'
               'the property that matters is INFLUENCE-symmetry, not permutation-symmetry.</text>')
    return svg(W, H, "".join(out), "Asymmetric families")


# ---------------------------------------------------------------------------
# Figure 18 — the naming bias, quantified
# ---------------------------------------------------------------------------

def fig_naming(data: dict) -> str:
    W, H = 780, 360
    L, R, T, B = 150, 240, 74, 60
    pw, ph = W - L - R, H - T - B
    rows = []
    for k in ("k=3", "k=4"):
        c = data[k]
        rows.append((f"{k}  functions you can name", c["nameable_symmetric_fraction"], "#dc2626"))
        rows.append((f"{k}  all functions", c["influence_symmetric_fraction"], "#2563eb"))

    out = ['<text class="ttl" x="24" y="26">Naming a function biases you toward the ones that hide the problem</text>',
           '<text class="sub" x="24" y="45">Share that is influence-symmetric — every participant '
           'matters equally, so a careless summary looks safe.</text>']
    for i in range(6):
        v = i / 5
        x = L + v * pw
        out.append(f'<line class="ax" x1="{x:.1f}" y1="{T-4}" x2="{x:.1f}" y2="{T+ph}"/>')
        out.append(f'<text class="tick" x="{x:.1f}" y="{T+ph+18}" '
                   f'text-anchor="middle">{int(v*100)}%</text>')

    bh = ph / len(rows)
    for i, (lbl, v, col) in enumerate(rows):
        y = T + i * bh
        w = max(v * pw, 1.5)
        out.append(f'<text class="lbl" x="{L-12}" y="{y+bh/2+4:.1f}" '
                   f'text-anchor="end">{esc(lbl)}</text>')
        out.append(f'<rect x="{L}" y="{y+bh*0.24:.1f}" width="{w:.1f}" '
                   f'height="{bh*0.52:.1f}" fill="{col}" rx="2"/>')
        out.append(f'<text class="tick" x="{L+w+9:.1f}" y="{y+bh/2+4:.1f}" '
                   f'fill="{col}">{v*100:.1f}%</text>')

    ly = T + 6
    for lbl in ["Over-representation:",
                f"  {data['bias_factor_k3']}x at three participants",
                f"  {data['bias_factor_k4']}x at four", "",
                "And it GROWS with arity —",
                "symmetric functions get",
                "rarer while the ones that",
                "come to mind do not.", "",
                "At k=3 the nameable list is",
                "parity, and, or, majority,",
                "mux, nand — every one of",
                "them symmetric."]:
        out.append(f'<text class="sub" x="{L+pw+18}" y="{ly}">{esc(lbl)}</text>')
        ly += 15
    out.append(f'<text class="sub" x="24" y="{H-12}">'
               'This is not carelessness. It is what naming does — and it is why the test set had '
               'to be built by influence profile rather than by example.</text>')
    return svg(W, H, "".join(out), "Naming bias")


# ---------------------------------------------------------------------------
# Figure 19 — two structures the retention law cannot tell apart
# ---------------------------------------------------------------------------

def fig_blind(data: dict) -> str:
    W, H = 780, 380
    L, R, T, B = 96, 250, 96, 62
    pw, ph = W - L - R, H - T - B
    w = data["k=3"]["worst_witness"]
    a, b = w["fn_a_level_weights"], w["fn_b_level_weights"]
    n = len(a)

    out = ['<text class="ttl" x="24" y="26">Two structures with identical predictions and opposite organisation</text>',
           '<text class="sub" x="24" y="45">Same influence profile, same outcome entropy — so the '
           'retention law gives them the same answer, exactly.</text>',
           f'<text class="sub" x="24" y="66">Identical retention vector: '
           f'<tspan font-weight="600">{esc(str(w["retention_vector"]))}</tspan>'
           f'   ·   influence {esc(str(w["influence_profile"]))}   ·   H={w["H"]}</text>']

    gw = pw / n
    for d in range(n):
        x = L + d * gw
        out.append(f'<text class="lbl" x="{x+gw/2:.1f}" y="{T+ph+20}" '
                   f'text-anchor="middle">order {d}</text>')
    for i in range(5):
        v = i / 4
        y = T + ph - v * ph
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v:.2f}</text>')
    out.append(f'<text class="lbl" transform="translate(26,{T+ph/2:.0f}) rotate(-90)" '
               'text-anchor="middle">share of the structure</text>')

    bw = gw * 0.34
    for d in range(n):
        x = L + d * gw + gw * 0.14
        for k, (v, col) in enumerate(((a[d], "#2563eb"), (b[d], "#dc2626"))):
            hgt = v * ph
            out.append(f'<rect x="{x + k*bw:.1f}" y="{T+ph-hgt:.1f}" '
                       f'width="{bw*0.86:.1f}" height="{max(hgt,1):.1f}" '
                       f'fill="{col}" rx="2"/>')
            if v > 0:
                out.append(f'<text class="tick" x="{x + k*bw + bw*0.43:.1f}" '
                           f'y="{T+ph-hgt-6:.1f}" text-anchor="middle" '
                           f'fill="{col}">{v:.2f}</text>')

    ly = T + 6
    for lbl, col in (("structure A", "#2563eb"), ("structure B", "#dc2626")):
        out.append(f'<rect x="{L+pw+20}" y="{ly-9}" width="13" height="12" '
                   f'fill="{col}" rx="2"/>')
        out.append(f'<text class="lbl" x="{L+pw+39}" y="{ly+1}">{esc(lbl)}</text>')
        ly += 22
    for lbl in ["", "A spreads its organisation",
                "evenly across every order.", "",
                "B puts THREE QUARTERS of",
                "itself at order 2 and has",
                "NOTHING at orders 1 or 3.", "",
                "The law returns the same",
                "number for both — not",
                "approximately, exactly."]:
        out.append(f'<text class="sub" x="{L+pw+20}" y="{ly}">{esc(lbl)}</text>')
        ly += 15
    return svg(W, H, "".join(out), "Retention blindness witness")


# ---------------------------------------------------------------------------
# Figure 20 — where the pair of instruments stops being enough
# ---------------------------------------------------------------------------

def fig_complete(data: dict) -> str:
    W, H = 800, 400
    L, R, T, B = 120, 244, 96, 62
    pw, ph = W - L - R, H - T - B
    w = data["k=4"]["witness"]
    a, b = w["spectrum_multiset_a"], w["spectrum_multiset_b"]
    n = len(a)

    out = ['<text class="ttl" x="24" y="26">Two structures both instruments agree on, that are not the same structure</text>',
           '<text class="sub" x="24" y="45">Same importance for every participant. Same '
           'distribution across interaction orders. Different organisation.</text>',
           f'<text class="sub" x="24" y="66">influence '
           f'<tspan font-weight="600">{esc(str(w["influence_profile"]))}</tspan>'
           f'   ·   order profile '
           f'<tspan font-weight="600">{esc(str(w["level_profile"]))}</tspan></text>']

    vmax = max(max(a), max(b)) * 1.2
    gw = pw / n
    for i in range(4):
        v = i / 3 * vmax
        y = T + ph - (v / vmax) * ph
        out.append(f'<line class="ax" x1="{L}" y1="{y:.1f}" x2="{L+pw}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L-9}" y="{y+4:.1f}" text-anchor="end">{v:.2f}</text>')
    out.append(f'<text class="lbl" x="{L+pw/2:.0f}" y="{H-14}" text-anchor="middle">'
               'the 16 possible participant subsets, sorted by weight</text>')
    out.append(f'<text class="lbl" transform="translate(26,{T+ph/2:.0f}) rotate(-90)" '
               'text-anchor="middle">weight carried</text>')

    bw = gw * 0.38
    for i in range(n):
        x = L + i * gw + gw * 0.1
        for kk, (v, col) in enumerate(((a[i], "#2563eb"), (b[i], "#dc2626"))):
            hgt = (v / vmax) * ph
            out.append(f'<rect x="{x + kk*bw:.1f}" y="{T+ph-hgt:.1f}" '
                       f'width="{bw*0.85:.1f}" height="{max(hgt,1):.1f}" '
                       f'fill="{col}" rx="1.5"/>')

    ly = T + 6
    for lbl, col in (("structure A", "#2563eb"), ("structure B", "#dc2626")):
        out.append(f'<rect x="{L+pw+18}" y="{ly-9}" width="13" height="12" '
                   f'fill="{col}" rx="2"/>')
        out.append(f'<text class="lbl" x="{L+pw+37}" y="{ly+1}">{esc(lbl)}</text>')
        ly += 22
    for lbl in ["", "A concentrates everything",
                "into FOUR subsets and", "leaves twelve empty.", "",
                "B spreads the same total",
                "across TEN.", "",
                "Every summary either",
                "instrument computes is",
                "identical for both."]:
        out.append(f'<text class="sub" x="{L+pw+18}" y="{ly}">{esc(lbl)}</text>')
        ly += 15
    return svg(W, H, "".join(out), "Completeness witness")


# ---------------------------------------------------------------------------
# Figure 21 — how far each summary gets
# ---------------------------------------------------------------------------

def fig_minimal(data: dict) -> str:
    W, H = 800, 380
    L, R, T, B = 214, 176, 74, 58
    pw, ph = W - L - R, H - T - B
    r = data["k=4"]
    total = r["npn_classes_total"]
    order = [("influence profile", "A_influence", "k numbers"),
             ("interaction-order profile", "B_level", "k+1 numbers"),
             ("the pair (both marginals)", "C_pair", "2k+1 numbers"),
             ("spectrum multiset", "E_multiset", "2^k numbers"),
             ("the JOINT matrix M", "D_matrix", "k(k+1) numbers"),
             ("matrix + multiset", "F_matrix_and_multiset", "more numbers")]

    out = ['<text class="ttl" x="24" y="26">How much structure each summary can actually distinguish</text>',
           f'<text class="sub" x="24" y="45">Distinct values each invariant takes, against the '
           f'{total} genuinely different structures at four participants.</text>']
    for i in range(5):
        v = i / 4 * total
        x = L + (v / total) * pw
        out.append(f'<line class="ax" x1="{x:.1f}" y1="{T-4}" x2="{x:.1f}" y2="{T+ph}"/>')
        out.append(f'<text class="tick" x="{x:.1f}" y="{T+ph+18}" '
                   f'text-anchor="middle">{v:.0f}</text>')
    xf = L + pw
    out.append(f'<line x1="{xf:.1f}" y1="{T-8}" x2="{xf:.1f}" y2="{T+ph}" '
               'stroke="#15803d" stroke-width="1.8" stroke-dasharray="4 3"/>')
    out.append(f'<text class="tick" x="{xf-6:.1f}" y="{T-12}" text-anchor="end" '
               f'fill="#15803d">complete = {total}</text>')

    bh = ph / len(order)
    for i, (lbl, key, size) in enumerate(order):
        c = r["candidates"][key]
        y = T + i * bh
        v = c["distinct_values"]
        w = max((v / total) * pw, 1.5)
        col = "#15803d" if c["complete"] else ("#2563eb" if v > total * 0.9 else "#dc2626")
        out.append(f'<text class="lbl" x="{L-14}" y="{y+bh/2:.1f}" '
                   f'text-anchor="end">{esc(lbl)}</text>')
        out.append(f'<text class="sub" x="{L-14}" y="{y+bh/2+14:.1f}" '
                   f'text-anchor="end">{esc(size)}</text>')
        out.append(f'<rect x="{L}" y="{y+bh*0.22:.1f}" width="{w:.1f}" '
                   f'height="{bh*0.5:.1f}" fill="{col}" rx="2"/>')
        out.append(f'<text class="tick" x="{L+w+9:.1f}" y="{y+bh/2+4:.1f}" '
                   f'fill="{col}">{v}  ({c["values_spanning_multiple_structures"]} collisions)</text>')

    out.append(f'<text class="sub" x="24" y="{H-30}">'
               'The spectrum multiset writes down 16 numbers and distinguishes 8 structures. The '
               'joint matrix writes down 20 and distinguishes 217.</text>')
    out.append(f'<text class="sub" x="24" y="{H-14}">'
               'Adding the multiset to the matrix changes nothing at all. More numbers is not '
               'more information — which numbers is what matters.</text>')
    return svg(W, H, "".join(out), "Minimal invariant search")


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
    e2 = json.loads((RESULTS / "exp002.json").read_text())
    e11 = json.loads((RESULTS / "exp011.json").read_text())
    e12 = json.loads((RESULTS / "exp012.json").read_text())
    e10 = json.loads((RESULTS / "exp010.json").read_text())
    e13 = json.loads((RESULTS / "exp013.json").read_text())
    e14 = json.loads((RESULTS / "exp014.json").read_text())
    e15 = json.loads((RESULTS / "exp015.json").read_text())
    e16 = json.loads((RESULTS / "exp016.json").read_text())
    e17 = json.loads((RESULTS / "exp017.json").read_text())
    e18 = json.loads((RESULTS / "exp018.json").read_text())
    e19 = json.loads((RESULTS / "exp019.json").read_text())
    e20 = json.loads((RESULTS / "exp020.json").read_text())
    e21 = json.loads((RESULTS / "exp021.json").read_text())
    e22 = json.loads((RESULTS / "exp022.json").read_text())
    e23 = json.loads((RESULTS / "exp023.json").read_text())

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
        "fig7_arity.svg": fig_arity(e2),
        "fig8_orders.svg": fig_orders(e11),
        "fig9_relevance.svg": fig_relevance(e12),
        "fig10_cliff.svg": fig_cliff(e10),
        "fig11_gradient.svg": fig_gradient(e13),
        "fig12_census.svg": fig_census(e14),
        "fig13_k4.svg": fig_k4(e15),
        "fig14_noise.svg": fig_noise(e16),
        "fig15_audit.svg": fig_audit(e17),
        "fig16_vector.svg": fig_vector(e18),
        "fig17_asym.svg": fig_asym(e19),
        "fig18_naming.svg": fig_naming(e20),
        "fig19_blind.svg": fig_blind(e21),
        "fig20_complete.svg": fig_complete(e22),
        "fig21_minimal.svg": fig_minimal(e23),
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
