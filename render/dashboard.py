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



PROJECT_PANEL = """
<h2 style="margin-top:26px">What this is trying to be</h2>
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
<button class="tab active" data-panel="findings">Findings</button>
<button class="tab" data-panel="project">The Project</button>
</nav>

<div class="panel active" id="findings">

<div class="card">
<h3 style="margin-top:0">What you are looking at</h3>
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
<div class="q"><b>Two ground truths were wrong, both mine, both found by widening a control.</b>
Size-matching every condition hid a size bias in the measure. Hand-identifying one loop instead
of enumerating produced a critical/benign split that doesn't exist. Neither was caught by
reasoning — both were caught by building the case that would expose them. That is the whole
argument for the laboratory.</div>
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
