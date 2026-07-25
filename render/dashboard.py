"""Build the self-contained study page for the Desktop folder.

One file, no network, opens in any browser. Inlines every figure so the page
survives being moved or emailed.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DESKTOP = Path("/home/lee/Desktop/RelationalMetrics")

CSS = """
:root{--bg:#fbfbfc;--panel:#fff;--fg:#16181d;--mut:#636a76;--line:#e3e5ea;
      --accent:#2563eb;--warn:#dc2626;--ok:#15803d;--code:#f3f4f6;}
@media (prefers-color-scheme:dark){
 :root{--bg:#0d0f13;--panel:#14171d;--fg:#e9eaee;--mut:#98a0ad;--line:#262b34;
       --accent:#6ea0ff;--warn:#ff7a70;--ok:#68d391;--code:#1b1f26;}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font:15px/1.62 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;}
.wrap{max-width:1120px;margin:0 auto;padding:48px 28px 96px}
header{border-bottom:1px solid var(--line);padding-bottom:22px;margin-bottom:34px}
h1{font-size:27px;margin:0 0 8px;letter-spacing:-.02em}
h2{font-size:20px;margin:44px 0 10px;letter-spacing:-.01em}
h3{font-size:15px;margin:26px 0 8px}
.sub{color:var(--mut);font-size:14px;margin:0}
.tag{display:inline-block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;
 padding:3px 9px;border-radius:99px;border:1px solid var(--line);color:var(--mut);margin-right:6px}
.tag.warn{color:var(--warn);border-color:var(--warn)}
.tag.ok{color:var(--ok);border-color:var(--ok)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;
 padding:22px 24px;margin:18px 0}
.fig{overflow-x:auto;margin:14px 0 6px;padding-bottom:4px}
.fig svg{display:block;min-width:640px;max-width:100%;height:auto}
.fig.wide svg{min-width:1060px}
.read{border-left:3px solid var(--accent);padding:2px 0 2px 15px;margin:16px 0;color:var(--fg)}
.read.warn{border-color:var(--warn)}
.read.ok{border-color:var(--ok)}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:12px 0}
th,td{text-align:left;padding:8px 11px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
code{background:var(--code);padding:1.5px 5px;border-radius:4px;font-size:13px;
 font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
ul{padding-left:20px}li{margin:5px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px;margin:16px 0}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:15px 17px}
.stat .n{font-size:24px;font-weight:650;letter-spacing:-.02em}
.stat .k{color:var(--mut);font-size:12.5px;margin-top:3px}
.q{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--warn);
 border-radius:8px;padding:15px 18px;margin:12px 0}
footer{margin-top:64px;padding-top:20px;border-top:1px solid var(--line);
 color:var(--mut);font-size:13px}
.tabs{display:flex;gap:4px;margin:26px 0 8px;border-bottom:1px solid var(--line);flex-wrap:wrap}
.tab{background:none;border:none;border-bottom:2px solid transparent;color:var(--mut);
 font:600 14.5px ui-sans-serif,system-ui,sans-serif;padding:10px 16px;cursor:pointer;
 margin-bottom:-1px;border-radius:6px 6px 0 0}
.tab:hover{color:var(--fg);background:var(--panel)}
.tab.active{color:var(--fg);border-bottom-color:var(--accent)}
.panel{display:none}.panel.active{display:block}
.pred{border-left:3px solid var(--mut);padding:2px 0 2px 15px;margin:14px 0}
.pred b{color:var(--fg)}
.conf{display:inline-block;font-size:11px;letter-spacing:.05em;text-transform:uppercase;
 padding:2px 8px;border-radius:99px;border:1px solid var(--line);color:var(--mut);margin-left:8px}
"""



METHOD_PANEL = """
<h2 style="margin-top:26px">How the tests work</h2>
<p class="sub">The rules every experiment here follows, and why they exist. The
<b>Thesis</b> tab is what the project is for; <b>Tests &amp; results</b> is the running log.</p>

<p>A relational framework can relate anything to anything if the criteria are loose enough.
That is the characteristic failure of this family of ideas, and it usually kills the project
<i>by succeeding</i> — producing striking, plausible, well-visualised connections that are
worthless. Everything below exists to make that failure detectable.</p>

<h3>1. Six statements before anything runs</h3>
<p>No experiment starts without these on paper. If any is missing the result isn't admissible.</p>
<table><thead><tr><th>#</th><th>what</th><th>why</th></tr></thead><tbody>
<tr><td>1</td><td><b>Exact claim</b></td><td>One test, one sharply defined claim. Not "does this
work" — "can it identify equivalent organisation when labels, coordinates and vocabulary all
differ?"</td></tr>
<tr><td>2</td><td><b>Intended signal</b></td><td>The specific feature that should cause success.
If you can't name it, you can't tell success from luck.</td></tr>
<tr><td>3</td><td><b>Rival explanations</b></td><td>Everything <i>else</i> that could produce
the same result — listed before seeing any output.</td></tr>
<tr><td>4</td><td><b>Positive control</b></td><td>A case where the signal is definitely there.</td></tr>
<tr><td>5</td><td><b>Adversarial control</b></td><td>A case built to look convincing while
lacking the signal.</td></tr>
<tr><td>6</td><td><b>Falsification condition</b></td><td>The specific result that would make us
reject the idea — written down first, so it can't be renegotiated afterwards.</td></tr>
</tbody></table>

<h3>2. The condition matrix</h3>
<p>Comparing two things is not one test, it is five.</p>
<table><thead><tr><th></th><th>surface</th><th>structure</th><th>required result</th></tr></thead>
<tbody>
<tr><td><b>A</b></td><td>same</td><td>same</td><td>high</td></tr>
<tr><td><b>B</b></td><td>different</td><td>same</td><td><b>high</b> — can it see past vocabulary</td></tr>
<tr><td><b>C</b></td><td>same</td><td>different</td><td><b>low</b> — is it just reading words</td></tr>
<tr><td><b>D</b></td><td>different</td><td>different</td><td>low</td></tr>
<tr><td><b>E</b></td><td>persuasively similar</td><td><i>almost</i>, critically different</td>
<td><b>must locate the mismatch</b></td></tr>
</tbody></table>
<p>B and C are the real tests. <b>E matters most</b>: two systems both containing feedback, where
one settles and one runs away. A vague measure calls them identical. A useful one keeps them
apart and says where.</p>

<h3>3. The impostors</h3>
<p>Before a measure is trusted, methods that <i>cheat</i> get built and the controls have to
catch all of them: ones that read node names, count edges, compare densities or degree
sequences, predict a constant, memorise the development set, or refit a parameter after seeing
each pair. They aren't strawmen — each is a shortcut a real implementation could take by
accident.</p>
<p>This has already paid for itself twice. The first version of the battery caught six of seven,
and fixing the seventh is what exposed a defect in the <i>real</i> measure.</p>

<h3>4. Evidence rungs</h3>
<p>Every claim states its rung. They are not interchangeable, and nothing here is above rung 1.</p>
<table><thead><tr><th>rung</th><th>means</th></tr></thead><tbody>
<tr><td>1</td><td>mathematically coherent — well-formed, behaves consistently</td></tr>
<tr><td>2</td><td>recovers planted ground truth in synthetic worlds</td></tr>
<tr><td>3</td><td>transfers across independently written generators</td></tr>
<tr><td>4</td><td>works on natural data</td></tr>
<tr><td>5</td><td>improves a real application against relevant baselines</td></tr>
<tr><td>6</td><td>predicts something withheld</td></tr>
<tr><td>7</td><td>supports a broader physical interpretation — <i>not currently reachable</i></td></tr>
</tbody></table>

<h3>5. Two rules learned the hard way</h3>
<div class="read warn"><b>A controlled experiment is blind exactly where it controls.</b>
Matching every condition on some property removes it as a confound <i>and</i> makes every defect
that operates through it undetectable. Measured twice here. Practice: for every property a
condition set holds fixed, keep one condition where it varies.</div>
<div class="read warn"><b>Never state a synthetic ground truth from inspection.</b> In a world
you built yourself it feels certain — which is the trap. Twice now a "known" answer written
from looking at it turned out wrong when enumerated: a structure had two feedback loops rather
than one, and a function assumed to be decomposable wasn't. Compute the ground truth with code,
from the same object the measure sees.</div>

<h3>6. What gets reported</h3>
<ul>
<li>Never a single number as the outcome — a profile, not a score.</li>
<li>Which rung, which controls survived, and <b>which rival explanations are still live</b>.</li>
<li>Failures written up with the same care as successes. Two of the results in this log are
failures of the author's own proposals, and one is a correction to an earlier entry.</li>
<li>The question is never "did it work". It is: <i>which precise claim survived which controls,
and what else could still explain this?</i></li>
</ul>
"""


PROJECT_PANEL = """
<h2 style="margin-top:26px">What this is trying to be</h2>
<p class="sub">The standing explanation: goals, architecture, predictions, applications.
<b>Tests &amp; results</b> is the experimental log — every test and result as it lands.</p>
<p>A small set of <b>general, domain-neutral relational quantities</b> — the kind of compact
reusable relationship you can carry into a new field by supplying units and relation types.
Not one giant master equation. The comparison is E=mc²: you don't need to compute an entire
relativistic spacetime to use the mass–energy relation, because it isolates one reusable
relationship between particular quantities.</p>
<p>Three layers, and keeping them apart is the whole discipline:</p>
<table><thead><tr><th>layer</th><th>what lives there</th><th>rule</th></tr></thead><tbody>
<tr><td><b>General relational language</b></td><td>participants, typed relations of any arity,
relations among relations, transformations</td><td>no application terms — if "search", "time",
"pitch" or "token" appears in a general law, the law is mis-specified</td></tr>
<tr><td><b>Application projection</b></td><td>which relation classes a domain can use and
afford</td><td>discarding is a budget decision, never a claim that something doesn't exist</td></tr>
<tr><td><b>Operational function</b></td><td>the actual deliverable — a map, a point cloud, a
prediction, a chord</td><td>domain-specific, and that's fine</td></tr>
</tbody></table>
<p>The one-line commitment underneath all of it: <b>relational completeness belongs to reality;
relational selectivity belongs to observers.</b> Reality contains the whole structure. Any
instrument receives a projection. The map's edge is the instrument's edge — never reality's.</p>

<h2>Arity — the claim everything rests on</h2>
<p>An ordinary graph records relations between <b>pairs</b>. A relation's <b>arity</b> is how
many participants it involves: <code>causes(erosion, capacity)</code> has arity 2,
<code>evidence(claim, observation, method)</code> has arity 3.</p>
<p>The load-bearing claim of this whole project is that <b>some structure exists only in
configurations of three or more participants, and is not recoverable from any collection of the
pairs inside it.</b></p>
<p>A concrete case. Suppose an outcome happens only when three conditions hold together —
<code>Y = a AND b AND c</code>. Look at any single condition: no signal. Look at any pair: still
no reliable signal, because the third is missing half the time. Only the full triple predicts
anything. Decompose that into pairwise relations and the thing you were trying to measure is
gone — not approximated, <i>gone</i>. The same shape shows up in evidence (a statement becomes
evidence only in the presence of a claim, an observation and a method), in chemistry, in
epistasis between genes, and in most of what people mean informally by "context".</p>
<p>This is why the project can't just be graph similarity with better vocabulary. If everything
interesting were pairwise, existing graph methods would already do it and there would be nothing
here to build.</p>
<div class="read warn"><b>And it is the biggest untested gap.</b> Every experiment on the
Findings tab so far uses <b>arity 2 only</b>. Binary relations, five participants, one motif.
So everything demonstrated to date could in principle be done by ordinary graph methods — the
findings are about measurement hygiene, which is real and necessary, but they are not yet
evidence for the distinctive claim. The statistic meant to detect higher-arity structure
(subtract everything the smaller subsets already explain; whatever remains needed the whole
configuration) is written down and has never been run.</p>
<p>Two ways it can fail, and they need separating. It might miss interactions that are really
there. Or it might fire on interactions that aren't — because the residual it measures also
appears when the model is simply wrong about something else. A statistic that cannot tell
"genuine higher-order structure" from "my model is misspecified" is not measuring what it
claims to.</div>

<h2>Predictions</h2>
<p>Written down in advance so they can be wrong in public. A prediction that gets quietly
revised after the result isn't a prediction. Each has a stated confidence and the thing that
would falsify it.</p>

<div class="pred"><b>P1 — the compression-ratio measure survives cross-generator transfer.</b>
<span class="conf">moderate</span><br>
Right now it's validated on one hand-built condition set of six structures, all written by the
same party running the measure. Three independently written world generators should not break
it. <i>Falsified by:</i> the ranking degrading on generators it wasn't developed against —
which would mean it learned our world-builder, not structure.</div>

<div class="pred"><b>P2 — genuine three-way interactions will be detectable, and fragile.</b>
<span class="conf">high / low</span><br>
High confidence that the higher-order remainder fires on cleanly planted interactions where
no pair suffices. Low confidence it survives realistic noise, redundancy, or a misspecified
output function. <i>Falsified by:</i> the same statistic firing on a null where nothing
higher-order was planted — which would mean it detects bad models, not structure.</div>

<div class="pred"><b>P3 — "significance" will turn out to be relative to a declared output,
not intrinsic to a structure.</b><span class="conf">moderate-high</span><br>
The current blindness — no measure can say whether a change <i>matters</i> — looks like a
missing feature. I think it's a missing definition. A structure with several interacting loops
has no single behaviour to invert, so significance probably can't be read off the structure
alone; it needs someone to say what output they care about. <i>Falsified by:</i> a purely
structural criterion that separates behaviour-inverting changes from cosmetic ones without
naming an output.</div>

<div class="pred"><b>P4 — relation-class typing will matter more than any single formula.</b>
<span class="conf">moderate</span><br>
Keeping causal, structural, historical and analogical relations distinct is doing quiet work
everywhere. Collapse them and the framework becomes a machine for producing attractive
nonsense — plausible cross-domain connections that mean nothing. <i>Falsified by:</i> an
ablation showing untyped relations perform as well across tasks.</div>

<div class="pred"><b>P5 — applications will win on the weird results and lose on the obvious
ones.</b><span class="conf">moderate</span><br>
If a relational search engine beats keyword and embedding baselines, it should beat them on
cross-domain structural analogy and roughly tie on direct topical relevance. That's the whole
proposition. <i>Falsified by:</i> uniform improvement, which would suggest we built a better
ordinary search engine and mislabelled it.</div>

<div class="pred"><b>P6 — this will not reach a physical claim.</b><span class="conf">high</span><br>
The evidence ladder has seven rungs, ending at "supports a broader physical interpretation."
That requires a distinctive prediction competing methods don't make, and there isn't one.
This is instrument design and measurement theory. Physical interpretation is a hope and stays
labelled as one. <i>Falsified by:</i> being wrong, which would be the best outcome here.</div>

<h2>Where the formulas could plug in</h2>

<h3>Relational search</h3>
<p>The query stops being a bag of words and becomes a <b>motif</b> — a small relational
configuration. Ask about erosion on an alluvial fan and get back blood-vessel channel
formation, current finding the low-resistance path, traffic consolidating onto one route.
Not because they share vocabulary; they share an organisation. The output should be a map with
one visual channel per measurement — distance for relational distance, colour for relation
class, opacity for confidence, dashed for inferred — and it must fade into unresolved
remainder at its edge rather than terminating cleanly, because a clean edge reads as
"this is everything."</p>

<h3>Music</h3>
<p>Possibly the best test case anywhere, because in music the objects are already known to be
secondary to the relations. A pitch has almost no musical content alone. C is nothing; C inside
an F major chord resolving to B♭ is a specific thing. Transposition changes every surface value
while preserving structure — an invariance test whose ground truth wasn't invented by us, it's
what musicians already agree on. And a chord's function isn't recoverable from its pairwise
intervals, so there's real higher-order structure to find with centuries of independent
analysis to check against.</p>

<h3>Language models</h3>
<p>Three genuinely different questions that get conflated: is there relational structure
<i>inside</i> a model beyond what pairwise probing finds; can a model reliably <i>extract</i>
typed relations from prose at scale; does supplying a resolved relational map improve reasoning
over the same content served flat. The third is the most testable and least interesting, which
makes it the right one to do first. The trap in the second: if the extractor and the measurer
are the same model, the "structure" found may be structure the model imposed.</p>

<h3>Physical and measured domains</h3>
<p>Terrain and fluid flow are where the ground truth was measured by someone else, with
instruments, before any of this existed. Public LiDAR comes with survey-grade checkpoints;
public flume datasets come with measured velocities. Rotation and unit conversion have
unambiguous meanings there, which makes it the cleanest invariance test available anywhere in
the project. Candidate question with a real answer: is a <i>relationally selected</i> subset of
points better than uniform random sampling at the same budget?</p>

<h3>Further out</h3>
<p>Anywhere the interesting thing is coordination rather than composition — biological
regulation, failure propagation through infrastructure, how a supply chain reorganises under
stress, historical reconstruction from partial traces. These are speculative. Listing them is
not a claim that any of them work.</p>

<h2>What would make me drop it</h2>
<ul>
<li>Every law needing a different arbitrary definition per domain — that means we renamed
existing domain methods rather than finding anything reusable.</li>
<li>Random structures scoring as highly as intended analogues, after the controls.</li>
<li>The framework explaining results it has seen and predicting nothing it hasn't.</li>
<li>The correspondence measure rewarding elaborate mappings over simple accurate ones — the
signature of a machine for producing attractive nonsense.</li>
</ul>
"""


def build() -> str:
    a = json.loads((RESULTS / "exp000a.json").read_text())
    b = json.loads((RESULTS / "exp000b.json").read_text())
    figs = json.loads((RESULTS / "figures_inline.json").read_text())
    c = json.loads((RESULTS / "exp000c.json").read_text())
    e9 = json.loads((RESULTS / "exp009.json").read_text())
    e2 = json.loads((RESULTS / "exp002.json").read_text())
    e11 = json.loads((RESULTS / "exp011.json").read_text())
    e12 = json.loads((RESULTS / "exp012.json").read_text())
    sweep_rows = "".join(
        f"<tr><td><code>{n}</code></td><td>{v:.4f}</td></tr>"
        for n, v in e12["power_sweep"])
    e11_rows = "".join(
        f"<tr><td><code>{w}</code></td><td>{d['true_arity']}</td>"
        f"<td>{d['order2']:.4f}</td><td>{d['order3']:.4f}</td>"
        f"<td><b>{d['order4']:.4f}</b></td><td>{d['p_value']:.4f}</td>"
        f"<td>{d['omega_F04']:.4f}</td></tr>" for w, d in e11["results"].items())
    big2 = str(e2["sample_sizes"][-1])
    e2_rows = "".join(
        f"<tr><td><code>{w}</code></td><td>{r['true_arity']}</td>"
        f"<td>{r['by_n'][big2]['profile']['best_pair']:.4f}</td>"
        f"<td>{r['by_n'][big2]['profile']['triple']:.4f}</td>"
        f"<td><b>{r['by_n'][big2]['omega_raw']:.4f}</b></td>"
        f"<td>{r['by_n'][big2]['p_value']:.4f}</td></tr>"
        for w, r in e2["results"].items())
    a2 = e2["arity2_control"]
    a2_rows = "".join(
        f"<tr><td><code>{w}</code></td><td>{v['omega_ab']:+.4f}</td>"
        f"<td>{v['omega_abc']:+.4f}</td></tr>" for w, v in a2.items())

    e9_rows = "".join(
        f"<tr><td><code>{r['edge']}</code></td>"
        f"<td>{'critical' if r['on_hand_identified_3cycle'] else 'benign'}</td>"
        f"<td>{r['f14_signature_divergence']}</td>"
        f"<td>{r['mdl_ratio']:.4f}</td></tr>" for r in e9["rows"])
    cross_rows = "".join(
        f"<tr><td>A vs {k}</td><td>{v['divergence_from_A']}</td>"
        f"<td><code>{v['signature']}</code></td></tr>"
        for k, v in e9["cross_domain"].items())

    gamma = a["mdl"]["by_code"]["gamma"]["scores"]
    rev = a["reversals"]
    first_rev = min(r["eta"] for r in rev)

    rows = "".join(
        f"<tr><td><code>{r['edge']}</code></td>"
        f"<td>{'yes' if r['on_loop'] else 'no'}</td>"
        f"<td>{r['behaviour_after_flip']}</td>"
        f"<td>{r['mdl_gain_bits']:.2f}</td>"
        f"<td>{'<b style=color:var(--warn)>inverts behaviour</b>' if r['behaviour_changed'] else '—'}</td></tr>"
        for r in b["rows"])

    mdl_rows = "".join(
        f"<tr><td>A → {k}</td><td>{v['matched']}/{v['of']}</td>"
        f"<td>{v['mapping_bits']:.1f}</td><td>{v['conditional_bits']:.1f}</td>"
        f"<td><b>{v['gain_bits']:.2f}</b></td></tr>"
        for k, v in gamma.items())

    inv = a["invariance"]["variants"]
    inv_rows = "".join(
        f"<tr><td><code>{k}</code></td><td>{v['mdl_gain_bits']:.3f}</td>"
        f"<td>{v['mdl_delta']:+.1e}</td>"
        f"<td>{'PASS' if v['mdl_invariant'] else 'FAIL'}</td>"
        f"<td>{'PASS' if v['tunable_invariant'] else 'FAIL'}</td></tr>"
        for k, v in inv.items())

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Relational Metrics — findings</title><style>{CSS}</style></head><body><div class="wrap">

<header>
<h1>Relational Metrics</h1>
<p class="sub">Four runs, 2026-07-25. All of them findings about <i>method</i> — how to build a
measurement you can trust — not evidence that relational measurement works.</p>
<p style="margin-top:14px"><span class="tag">rung 1 — mathematically coherent</span>
<span class="tag warn">hazard confirmed</span><span class="tag ok">one fix validated</span></p>
</header>

<nav class="tabs">
<button class="tab active" data-panel="method">How the tests work</button>
<button class="tab" data-panel="project">The thesis</button>
<button class="tab" data-panel="findings">Tests &amp; results</button>
</nav>

<div class="panel active" id="method">{METHOD_PANEL}</div>

<div class="panel" id="findings">

<div class="card">
<h3 style="margin-top:0">What you are looking at</h3>
<p class="sub" style="margin-bottom:12px"><b>This tab is the running record of tests and their
results</b> — one section per experiment, added as they run, including the ones that failed and
the three that caught errors in my own work. For the rules every experiment follows see
<b>How the tests work</b>; for what the project is <i>for</i> see <b>The thesis</b>.</p>
<p>Before trusting a relational measure, the protocol requires showing the laboratory can
catch a method that cheats. These two runs do something slightly stronger: they take the
correspondence formula we inherited from the founding conversation and show it contains a
dial that decides the answer — then test a replacement that has no dial.</p>
<p class="sub">Everything below comes from code in <code>~/relational-metrics/lab/</code>.
Raw numbers are in the JSON files next to this page.</p>
</div>

<div class="grid">
<div class="stat"><div class="n" style="color:var(--warn)">{len(rev)}</div>
<div class="k">rank reversals found in the tunable measure</div></div>
<div class="stat"><div class="n" style="color:var(--warn)">η ≈ {first_rev}</div>
<div class="k">where a near-miss overtakes a true analogue</div></div>
<div class="stat"><div class="n" style="color:var(--ok)">3 / 3</div>
<div class="k">codes agree on the MDL ranking</div></div>
<div class="stat"><div class="n" style="color:var(--ok)">7 / 7</div>
<div class="k">cheating methods the harness catches</div></div>
</div>

<h2>The five conditions</h2>
<p>One motif — the reinforcing channel that shows up in erosion, blood vessels, traffic and
current finding the low-resistance path. Then four variations, each built to catch a
different way of being wrong.</p>
<div class="fig wide">{figs['fig4_conditions.svg']}</div>
<p class="sub"><b>B</b> is the result we actually want a relational search to find: the same
organisation wearing completely different words. <b>C</b> and <b>D</b> must score low or the
measure is reading vocabulary. <b>E</b> is the trap — identical to A except one edge, but that
edge inverts what the system does.</p>

<h2>Finding 1 — the penalty decides the ranking</h2>
<p>The inherited formula divides match quality by a mapping-complexity penalty, scaled by a
parameter η. That penalty charges for asserting that one thing corresponds to another across
vocabularies. Which means it charges most for exactly the cross-domain analogy the theory
exists to find.</p>
<div class="fig">{figs['fig1_eta_curves.svg']}</div>
<div class="read warn"><b>Reading.</b> At η below 0.22, the true structural analogue B wins,
as it should. Above 0.22, the near-miss E wins. Above 0.76, even C — same words, no shared
organisation — beats B. Nothing about the structures changed between those regimes. Only the
dial moved. Whoever sets η decides whether the system can see analogy at all, and 0.22 is not
an exotic setting; it is the kind of number anyone would pick.</div>

<h2>Finding 2 — description length removes the dial</h2>
<p>The replacement asks a different question: <i>does knowing A, plus a mapping, let me write
the other structure down in fewer bits than writing it from scratch?</i> The complexity
penalty stops being chosen and becomes the number of bits the mapping costs. Counted, not set.</p>
<div class="fig">{figs['fig2_mdl_gain.svg']}</div>
<table><thead><tr><th>pair</th><th>relations matched</th><th>mapping bits</th>
<th>correction bits</th><th>gain</th></tr></thead><tbody>{mdl_rows}</tbody></table>
<div class="read ok"><b>Reading.</b> The order is B &gt; E &gt; C &gt; D — correct — and it
holds under all three description codes. The deep reason it works: surface labels are never
encoded at all, so the measure <i>cannot</i> charge for cross-vocabulary translation even in
principle. The pathology in Finding 1 isn't tuned away here; it's structurally unavailable.</div>
<div class="read warn"><b>But look at the sign.</b> Under <code>flat32</code> — deliberately
crude, 32 bits for every integer — all four gains go <i>negative</i>. That code rejects every
pair, including the true analogue B, while ranking them in exactly the same order. So the
choice of code does not move the ranking, but it does move the accept/reject line. The usable
rule that falls out: <b>MDL gain is safe to rank with and not safe to threshold with</b> unless
the code is separately justified. That is a much narrower hole than η — and unlike η, it's a
question with a right answer you can argue about in public.</div>

<h3>Invariance check</h3>
<p>Change only the description — rename every participant, reorder the nodes, reshuffle the
serialization, multiply every weight by 1000 — and require the number not to move.</p>
<table><thead><tr><th>description change</th><th>MDL gain (bits)</th><th>drift</th>
<th>MDL</th><th>tunable K</th></tr></thead><tbody>{inv_rows}</tbody></table>
<div class="read"><b>Worth noticing.</b> The tunable measure passes this battery too. So
invariance testing — the thing I'd have reached for first — would never have caught Finding 1.
Two independent failure modes; surviving one says nothing about the other. That's a lesson
about the test suite, not about the formula.</div>

<h2>Finding 3 — neither measure knows which change matters</h2>
<p>A contains one feedback loop: <code>flow → erosion → capacity → flow</code>, all
reinforcing. Flip any one of those three edges and the loop becomes self-limiting — the system
stops running away and settles. Flip any of the other three and behaviour is untouched. So
three of six single-edge changes are critical and three are harmless, and we know exactly
which because we built it.</p>
<div class="fig">{figs['fig3_criticality.svg']}</div>
<table><thead><tr><th>edge flipped</th><th>on the loop</th><th>behaviour after</th>
<th>MDL bits</th><th>verdict</th></tr></thead><tbody>{rows}</tbody></table>
<div class="read warn"><b>Reading.</b> Five of six flips score <b>19.727 bits</b> — identical
to three decimal places. Critical and harmless are indistinguishable. The one outlier, 22.96,
is a <i>harmless</i> flip that scores highest, and only because it leaves the target with a
single relation type, making it cheaper to describe. An alphabet artifact. So the single case
where the measure discriminates, it discriminates for the wrong reason and points the wrong
way.</div>
<p>This is the real gap. MDL measures <i>how much</i> two structures differ. It has nothing to
say about <i>whether the difference matters</i>, because significance is a fact about the
system's behaviour and the measure only sees topology and type labels.</p>
<div class="read warn"><b>Correction, added after Finding 5.</b> The ground truth in this table
is wrong. It was built by hand-identifying <i>one</i> feedback loop. Enumerating properly, A
contains <b>two</b> cycles — a positive 3-cycle and a negative 5-cycle — and every one of the
six edges lies on at least one of them. So "3 critical, 3 benign" was an artifact of not
counting. The blindness finding survives (five of six still score identically); the labels
don't. Left visible rather than quietly fixed, because how the error happened matters more
than the row it corrupted.</div>

<h2>Finding 4 — the laboratory checks itself, and catches its own author</h2>
<p>Before any of the above is allowed to count, the protocol requires proving the laboratory can
catch a method that cheats. Seven deliberately fake measures were built — ones that read node
names, count edges, compare densities and degree sequences, predict a constant, memorise the
development set, or refit the penalty after seeing each pair. Every one is a shortcut a real
implementation could take by accident.</p>
<div class="fig wide">{figs['fig5_harness.svg']}</div>
<div class="read ok"><b>Reading.</b> All seven caught. Exactly one candidate admitted. But the
first run caught only six — the penalty-refitter passed everything, because refitting to
maximise degenerates to ignoring the penalty, and on a condition set where every structure has
the same size, raw match count happens to sort correctly. The gap was in the <i>conditions</i>,
not the formula.</div>
<p>So a sixth condition was added: <b>F</b>, a superset containing every one of A's relations
plus eight more. The encyclopedia that answers every query because it contains everything.</p>
<div class="fig">{figs['fig6_superset.svg']}</div>
<div class="read warn"><b>And then it caught me.</b> With F in place, the MDL measure failed
too. Absolute compression gain scales with the size of the target — F has 14 relations, so
there are simply more bits available to save (baseline 94.0 vs 46.9), and it beat the true
analogue on volume rather than on shared organisation. <b>The fix is to use the compression
ratio rather than the absolute gain</b>, which restores the correct order with F safely below
the near-miss. The earlier experiment could not have found this: every condition in it was
size-matched, so the confound had been controlled away. A control that hides a defect is still
a control doing its job — on the wrong variable.</div>

<h2>Finding 5 — a candidate for the blindness, and a correction to Finding 3</h2>
<p>If a measure can't see which change matters, maybe the information is there and nothing ever
composed it. A relation type carries a polarity; compose polarities around a cycle and you get
its sign — positive loops run away, negative loops settle. That's derived from the structure,
not hand-fed, which is the difference between a result and an impostor.</p>
<table><thead><tr><th>edge flipped</th><th>Finding 3 called it</th>
<th>cycle-sign divergence</th><th>MDL ratio</th></tr></thead><tbody>{e9_rows}</tbody></table>
<div class="read warn"><b>Reading — the claim is not established.</b> Composition does add
information the MDL ratio lacks: it separates 4 from 2 where MDL is flat at 1.7270. But it
separates along <i>how many cycles a flip touches</i>, not <i>whether behaviour inverted</i>.
And enumerating cycles properly showed Finding 3's ground truth was wrong — A has two cycles,
every edge is on one, so every flip perturbs something. The question "did behaviour invert?"
may not even be well posed for a system with a reinforcing loop and a self-limiting loop
interacting. It doesn't have one behaviour to invert.</div>
<h3>The second claim, which does hold</h3>
<p>Adding sign awareness must not cost the cross-domain result. A measure that spots critical
changes but can no longer tell that erosion and blood vessels share an organisation has traded
one blindness for another.</p>
<table><thead><tr><th>pair</th><th>divergence</th><th>cycle signature</th></tr></thead>
<tbody>{cross_rows}</tbody></table>
<div class="read ok"><b>Reading.</b> Zero divergence for both the vascular analogue and the
held-out traffic one — polarity travels with the relation type, not the vocabulary. The two
structures agree about every reinforcing and self-limiting loop they contain despite sharing
no words. Sign survives translation.</div>

<h2>Finding 6 — the central claim demonstrated, and the statistic for it demoted</h2>
<p>Everything above uses <b>arity 2</b>. So none of it touched the one claim that makes this
project different from ordinary graph similarity: that some structure exists only in
configurations of three or more participants and cannot be recovered from the pairs inside it.</p>
<p>Six synthetic worlds where the true arity of the dependence is generated by an explicit rule,
not identified by eye. Five drivers, only some matter, 5% outcome noise, 400-permutation
calibration.</p>
<div class="fig">{figs['fig7_arity.svg']}</div>
<table><thead><tr><th>world</th><th>true arity</th><th>best pair</th><th>all three</th>
<th>Ω</th><th>p</th></tr></thead><tbody>{e2_rows}</tbody></table>
<div class="read ok"><b>The claim is real.</b> Look at <code>order3</code>
(<code>Y = a XOR b XOR c</code>). The best pair carries <b>0.0008 bits</b> — nothing at all —
while the three together carry <b>0.7340</b>. Structure completely invisible to every pair
inside it, and the remainder recovers essentially all of it (0.7328, p=0.0025). This is the
thing the theory is about, and it exists.</div>
<div class="read warn"><b>And the statistic meant to detect it does not work.</b> The
falsification condition was: if Ω can't separate genuine three-way structure from a world where
three variables are involved but contribute no synergy, it should be demoted. It can't.
<code>redundant</code> — where <code>b</code> and <code>c</code> are just noisy copies of
<code>a</code>, so there is zero synergy by construction — fires at Ω = 0.0876, p = 0.0025.</div>
<h3>Why, exactly</h3>
<p>Pushed to the clean case: make <code>b</code> and <code>c</code> <i>exact</i> copies of
<code>a</code>. Every subset then carries the same information H, and the alternating sum
becomes</p>
<p style="text-align:center"><code>Ω = H − 3H + 3H = +H</code></p>
<p>Measured: <b>Ω = 1.0000</b> on perfect redundancy — the maximum possible, identical to what
perfect synergy would give. The statistic is reporting <i>how much information is present among
these participants</i>, not <i>how much required all of them at once</i>.</p>
<h3>Where it breaks — and where it doesn't</h3>
<table><thead><tr><th>world</th><th>Ω over the pair</th><th>Ω over the triple</th></tr></thead>
<tbody>{a2_rows}</tbody></table>
<div class="read"><b>Reading.</b> At arity 2 the sign convention is correct:
<code>redundant</code> gives <b>−0.2118</b> — negative, properly marking redundancy — while pure
pairwise synergy gives +0.7329. At arity 3 the same redundancy flips to <b>+0.0876</b> and
becomes indistinguishable from synergy. The failure isn't "the statistic is broken." It is
specific to arity ≥ 3, which is exactly the regime the theory needs it for.</div>
<p>This is a known hazard in information theory rather than a novel discovery — interaction
information conflates synergy and redundancy above two variables, which is why partial
information decomposition exists. What's new here is only that it was measured against a
predeclared falsification condition rather than assumed away, and the formula is demoted
accordingly.</p>

<h2>Finding 7 — a replacement that works, found by reading instead of inventing</h2>
<p>The obvious replacement was <b>partial information decomposition</b>, which exists precisely
because interaction information conflates synergy with redundancy. Reading it first turned out to
matter: for <b>three or more sources, antichain-lattice PID is provably impossible</b>. The
desired axioms — whole-equals-sum-of-parts, commutativity, monotonicity, self-redundancy,
independent identity — are mutually incompatible, and the obstruction is structural rather than
axiomatic. There exist two systems carrying <i>identical atoms but different mutual
information</i>, so no universal reconstruction function can exist. Building there would have
been building on a proved dead end.</p>
<p>That impossibility is scoped to antichain-indexed decompositions. A different construction sits
outside it: <b>connected information</b> via the maximum-entropy hierarchy. Let <code>p̃(k)</code>
be the maximum-entropy distribution matching every marginal of order ≤ k. Then</p>
<p style="text-align:center"><code>I_C(k) = H[p̃(k−1)] − H[p̃(k)]</code></p>
<p>— how much the maximum possible entropy drops once order-k marginals are also known. The
reason this fixes the exact defect: <b>redundancy is entirely visible in low-order marginals.</b>
If two variables are copies of a third, the pairwise marginals already pin the joint, so the
maximum-entropy distribution matching them reproduces the data and every higher order contributes
nothing. Genuine higher-order structure is precisely what low-order marginals cannot reproduce.</p>
<div class="fig">{figs['fig8_orders.svg']}</div>
<table><thead><tr><th>world</th><th>true arity</th><th>I_C(2)</th><th>I_C(3)</th>
<th>I_C(4)</th><th>p</th><th>old Ω</th></tr></thead><tbody>{e11_rows}</tbody></table>
<div class="read ok"><b>Reading.</b> The acceptance test written when Ω was demoted — near zero
on <code>redundant</code>, ≈0.73 on <code>order3</code> — passes. <code>redundant</code> goes from
Ω = 0.0876 (a false positive) to <b>I_C(4) = 0.0003, not significant</b>, with all 1.23 bits of
its structure correctly placed at order 2. And the <i>order is read off rather than assumed</i>:
<code>Y = a XOR b</code> puts its structure at order 3, <code>Y = a XOR b XOR c</code> at order 4.
Every term is non-negative by construction and they sum to the total, so this is a real
decomposition rather than a residual.</div>
<div class="read"><b>What it costs.</b> Iterative proportional fitting over the full joint —
exponential in the number of variables. Trivial at four binary variables, a hard limit at scale,
and the continuous case needs a different estimator entirely. This is a working instrument for
small configurations, not a general one.</div>
<div class="read warn"><b>And a fourth ground truth was wrong.</b> The pure-noise control turned
out to be a <i>deterministic function</i> of the very variables it was meant to be independent
of — a pseudo-random generator seeded on them. It showed 0.36 bits of "structure" and I nearly
reported it. Caught only because this measure separates orders and the number looked wrong in a
place it shouldn't. Fixed, both experiments re-run, everything else unchanged. Four instances now
of the same error: asserting a property from how code reads rather than computing it.</div>

<h2>Finding 8 — attacking the thing that worked, and what broke</h2>
<p>F-04a passed its acceptance test on the first attempt, on worlds written by the same person who
wrote the measure. That is a reason for suspicion, not confidence — it is the exact shape of a
measure fitted to its own test. So the next step was to try to break it, including with one case
I expected to fail.</p>

<h3>The case I expected to fail — and it did</h3>
<p>Connected information is a property of a <i>joint distribution</i>. It does not privilege any
variable. So what happens when structure exists purely among the participants and has nothing
to do with the outcome? Built two such worlds: a hard three-way constraint among the drivers with
the outcome an independent coin, and the same one order down.</p>
<div class="fig">{figs['fig9_relevance.svg']}</div>
<div class="read warn"><b>The raw statistic fires, hard.</b> <code>driver_only_3way</code> reports
<b>I_C(3) = 0.9994</b> — a full bit of structure — with an outcome that is a coin flip.
<code>driver_only_pairwise</code> reports <b>I_C(2) = 1.0000</b>. Both are <i>correct</i> about
the structure and <i>useless</i> as answers to a question. Anyone reading raw connected
information as "relational structure detected" gets confident irrelevance.</div>
<div class="read ok"><b>The calibration is what saves it, and that is not a detail.</b> The
permutation test shuffles <i>only the outcome</i>, which leaves structure among the participants
intact in the null. So driver-only structure appears in the null distribution too, and comes back
non-significant (p = 0.25, p = 0.30). The <code>mixed</code> world confirms the separation
directly: redundancy among the drivers sits at order 2 (1.0003, not outcome-significant) while
genuine outcome-synergy sits at order 3 (0.7060, p = 0.0083).</div>
<p><b>So the formula has been amended.</b> F-04a is no longer the statistic — it is the statistic
<i>plus</i> the outcome-permutation calibration, as one object. The statistic alone answers a
different question than the one being asked.</p>

<h3>Which lands on the thesis, not just the method</h3>
<div class="read"><b>The observer enters through the calibration, not through the statistic.</b>
Whether structure is <i>present</i> is a fact about the joint distribution — objective, and
provably indifferent to which variable you nominate as the outcome (measured: symmetry drift
8.9×10⁻¹⁶). Whether that structure <i>counts as an answer</i> depends entirely on the question
being asked. Those are two different operations and the mathematics separates them cleanly.
<br><br>That is the project's founding axiom — <i>relational completeness belongs to reality,
relational selectivity belongs to observers</i> — arrived at from the arithmetic rather than
assumed. It was written as a philosophical commitment. It came back as a measurement.</div>

<h3>What survived the rest of the attack</h3>
<table><thead><tr><th>test</th><th>result</th></tr></thead><tbody>
<tr><td><b>Implementation symmetry</b> — is I_C really indifferent to which variable is called the
outcome, or is there an axis bug?</td><td>Indifferent. Drift 8.9×10⁻¹⁶ across permutations.</td></tr>
<tr><td><b>Monotone power</b> — is it a measure of degree or a threshold detector?</td>
<td>Monotone and smooth across the strength sweep (below).</td></tr>
<tr><td><b>Numerical robustness</b> — iterative fitting fails on hard zeros and skewed
marginals.</td><td>Converged everywhere. Worst marginal residual 0.0, including a deterministic
world with structural zeros and one with a driver at 97:3.</td></tr>
<tr><td><b>Null calibration vs sample size</b> — where does the permutation test stop
protecting?</td><td>Held down to n=200, where raw bias is 0.0047 and p = 0.29.</td></tr>
</tbody></table>
<table><thead><tr><th>synergy strength</th><th>I_C(4)</th></tr></thead><tbody>{sweep_rows}</tbody></table>
<p>One further honest note: <code>skewed_marginal</code> puts most of its weight at order 3 rather
than order 4. That is correct rather than a failure — when a driver is 97% constant, a nominal
three-way rule <i>is</i> effectively a two-way one. The measure tracks the structure that is
actually there, not the rule that generated it.</p>
<div class="read warn"><b>Fifth wrong construction.</b> The world meant to test redundancy and
synergy together placed the redundant copy in a variable that was not in the tested set, so it
tested nothing it claimed to. Caught by reading an output that disagreed with the intent — 0.0004
where a full bit was planted. Fixed and re-run. The running count stands at five.</div>

<h2>Where this leaves the theory</h2>
<div class="q"><b>Q-06 — the penalty problem.</b> Narrowed, not closed, and the residual is now
stated precisely rather than vaguely. The hazard is real and measured: η reorders results. A
parameter-free replacement ranks correctly, holds its ranking across three codes, and passes
invariance. What survives: the code still sets the accept/reject boundary even though it does
not set the order. So the operating rule is <b>rank with it, don't threshold with it</b> — and
"is this code reasonable" is a question that can be settled by argument, which "is η = 0.22
reasonable" never could be.</div>
<div class="q"><b>Q-12 — criticality is not magnitude. Still open, now better posed.</b>
Composition buys real information and costs nothing cross-domain, so it stays. But it answers
"how many loops did this disturb", not "does this matter". The harder discovery is that the
question itself was sloppy: a structure with several interacting loops has no single behaviour
to invert. Significance needs a sharper definition before a measure can be built for it.</div>
<div class="q"><b>Structure and relevance are different measurements, and the mathematics knows
it.</b> Connected information says what structure is present — objectively, indifferent to any
question. The outcome-permutation calibration says whether that structure bears on what you
asked. Using the first without the second produces true statements that are not answers. This is
the founding axiom recovered from arithmetic rather than asserted, and it is the strongest result
the project has.</div>
<div class="q"><b>The central claim is demonstrated and there is now an instrument for it.</b>
Structure that no pair can see exists, is measurable, and connected information places it at the
right order while correctly assigning redundancy to the low orders where it belongs. Bounded to
small discrete configurations. That is the first thing in this project that actually works.</div>
<div class="q"><b>Reading beat inventing, measurably.</b> The replacement was found by reading the
literature rather than deriving it, and the reading is what revealed that the obvious route was
provably closed. The project's own vocabulary hides its connections to existing work, which is
now a standing risk with a standing mitigation: before building a formula, find the established
name of the problem.</div>
<div class="q"><b>Four ground truths were wrong, all mine.</b>
Size-matching every condition hid a size bias in the measure. Hand-identifying one loop instead
of enumerating produced a critical/benign split that doesn't exist. And a function assumed
decomposable because it's called "majority" turned out to be genuinely synergistic — whenever
the first two disagree, the third decides alone. And the pure-noise control was a deterministic
function of the variables it was supposed to be independent of. None was caught by reasoning; all
four were caught by building the thing that would expose them. That is the whole argument for the
laboratory — and the running count is the honest measure of how often careful reasoning about
one's own constructions is simply wrong.</div>
<div class="q"><b>Methodological.</b> The tunable measure passed invariance. Batteries do not
substitute for one another, and a suite that only tests what we thought of will keep clearing
formulas that fail in ways we didn't.</div>

</div><!-- /findings -->

<div class="panel" id="project">{PROJECT_PANEL}</div>

<footer>
Generated from <code>~/relational-metrics/</code> · figures also in <code>figures/</code> ·
raw results in <code>exp000a.json</code> and <code>exp000b.json</code><br>
Rung 1 on the evidence ladder. These are hazard demonstrations about method — not evidence
that relational measurement works.
</footer>
</div>
<script>
document.querySelectorAll('.tab').forEach(function (t) {{
  t.addEventListener('click', function () {{
    document.querySelectorAll('.tab').forEach(function (x) {{ x.classList.remove('active'); }});
    document.querySelectorAll('.panel').forEach(function (p) {{ p.classList.remove('active'); }});
    t.classList.add('active');
    document.getElementById(t.dataset.panel).classList.add('active');
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }});
}});
</script>
</body></html>"""


if __name__ == "__main__":
    DESKTOP.mkdir(parents=True, exist_ok=True)
    out = DESKTOP / "index.html"
    out.write_text(build())
    print(f"wrote {out}  ({out.stat().st_size // 1024} KB)")
