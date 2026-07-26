"""Build the self-contained study page for the Desktop folder.

One file, no network, opens in any browser. Inlines every figure so the page
survives being moved or emailed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_docs  # noqa: E402
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DESKTOP = Path("/home/lee/Desktop/RelationalMetrics")

CSS = """
.survives-card{border-left:4px solid var(--ok);margin-bottom:18px}
.survives-card h2{margin-top:0}
table.survives{width:100%;border-collapse:collapse;margin-top:12px;font-size:13px}
table.survives th{text-align:left;padding:6px 8px;border-bottom:1px solid var(--bd);
  color:var(--mut);font-weight:600}
table.survives td{padding:8px;border-bottom:1px solid var(--bd);vertical-align:top}
table.survives td:first-child{white-space:nowrap;width:1%}
table.survives td:last-child{width:38%}
.tag.mut{background:var(--bd);color:var(--mut)}
.tag.bad{background:#fee2e2;color:#991b1b}
@media (prefers-color-scheme:dark){.tag.bad{background:#4c1d1d;color:#fca5a5}}

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

<h3>5. Rules learned the hard way</h3>
<p>Every one of these was learned by publishing something wrong first. They are listed with the
finding that produced them, because a rule without its scar is easy to forget.</p>
<table><thead><tr><th>rule</th><th>learned from</th></tr></thead><tbody>
<tr><td><b>A controlled experiment is blind exactly where it controls.</b> For every property a
condition set holds fixed, keep one condition where it varies.</td><td>size-matching hid a size
bias in a measure <i>and</i> made an impostor undetectable</td></tr>
<tr><td><b>Never state a ground truth from inspection.</b> Compute it, from the same object the
measure sees.</td><td>eight instances, and counting — the latest found an "unrelated" control that
was isomorphic to its own query</td></tr>
<tr><td><b>Verify test cases are actually distinct</b> before counting them as separate evidence —
compare the objects, not the names.</td><td>four "independent" agreements turned out to be two
functions counted twice</td></tr>
<tr><td><b>Build condition sets by enumerating the property under test, not by collecting
examples.</b></td><td>measured: functions you can name are unrepresentative by 1.8×–6.1×, and the
bias grows with size</td></tr>
<tr><td><b>A condition set can lack not just coverage but the capacity to fail.</b> Ask what class
of error a battery could not possibly surface.</td><td>a bug the old test set was
<i>provably unable</i> to detect</td></tr>
<tr><td><b>Report rankings as a curve over the nuisance parameter</b>, not at a point.</td>
<td>four of five audited parameters change the <i>order</i>, not just the values</td></tr>
<tr><td><b>An unexplained regularity is a debt.</b> Chase it before building on the result that
contains it.</td><td>one sat in the data being used as evidence for two experiments before turning
out to be a theorem</td></tr>
<tr><td><b>Carry the vector.</b> When a quantity has parts, a summary over them is a choice that
can reverse a ranking.</td><td>best-case and worst-case orderings came out
<i>anti</i>-correlated</td></tr>
<tr><td><b>Check the container, not just the measure.</b></td><td>an invariant went unasserted for
twenty-three experiments because every world until then was hand-built</td></tr>
<tr><td><b>A measure that cannot separate two things must say so, not rank them.</b> Report tied
groups. And note that making an arbitrary tie-break <i>stable</i> would only have made the error
reproducible, not correct.</td><td>a published finding turned out to be a sort order read off a
hash that is randomised on every run</td></tr>
</tbody></table>

<h3>6. What gets reported</h3>
<ul>
<li>Never a single number as the outcome — a profile, not a score.</li>
<li>Which rung, which controls survived, and <b>which rival explanations are still live</b>.</li>
<li>Failures written up with the same care as successes. Three of the results in this log are
failures of the author's own proposals, and one is a <b>retraction</b> of a claim published on
this page — left visible, with the original wording, rather than edited away.</li>
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
<div class="read ok"><b>Tested, and it is real.</b> In a world where an outcome is the parity of
three inputs, the best <i>pair</i> carries 0.0008 bits about it and the three together carry
0.7340. Structure completely invisible to every pair inside it, measured. So the distinctive claim
is not a hope — it is the one thing here that ordinary pairwise methods provably cannot do.</div>
<div class="read warn"><b>The first instrument built for it was wrong.</b> The obvious statistic —
subtract everything the smaller subsets explain, and whatever remains needed the whole
configuration — <i>conflates two opposite things</i>. Make three variables exact copies of each
other, so there is no joint structure whatsoever, and it returns the maximum possible value. It
was measuring how much information is present among the participants, not how much required all of
them at once. Demoted.<br><br>The replacement works, and was found by reading rather than
inventing: the obvious route through the literature turned out to be <i>provably impossible</i>
above two sources, and the construction that does work sits just outside that impossibility.</div>

<h2>Predictions — and how they scored</h2>
<p>Written down in advance so they could be wrong in public. Here is what happened to each. The
scoring is the point: a prediction table that never gets marked is decoration, and leaving one
unmarked for fifteen findings is exactly the failure this project keeps catching elsewhere.</p>
<table><thead><tr><th></th><th>prediction</th><th>outcome</th></tr></thead><tbody>
<tr><td><b>P1</b></td><td>the measure survives testing on structures it wasn't developed against</td>
<td><b>CONFIRMED</b> — five of five base topologies, including one with no cycles at all and one
nobody designed</td></tr>
<tr><td><b>P2</b></td><td>three-way structure detectable, and fragile</td>
<td><b>CONFIRMED, and worse than predicted</b> — detectable, but the statistic built to detect it
was invalid and had to be replaced</td></tr>
<tr><td><b>P3</b></td><td>significance turns out to be relative to a declared outcome, not
intrinsic</td><td><b>CONFIRMED</b> — measured three independent ways, and it dissolved a question
this project had been treating as its hardest</td></tr>
<tr><td><b>P4</b></td><td>relation-class typing matters more than any single formula</td>
<td><b>NOT TESTED</b> — the ablation was never run. Recorded as unscored rather than quietly
dropped</td></tr>
<tr><td><b>P5</b></td><td>applications win on the weird results and merely tie on the obvious ones</td>
<td><b>PARTLY, and sharper</b> — it wins decisively on cross-domain analogy where every baseline
gets it backwards, but on ordinary ranking it doesn't tie, it <i>fails</i>, and for a reason
worth knowing</td></tr>
<tr><td><b>P6</b></td><td>this will not reach a physical claim</td><td><b>STANDING</b> — nothing
came close, exactly as expected. Still the prediction I'd most like to lose</td></tr>
</tbody></table>
<p class="sub">Three confirmed, one confirmed but uglier than forecast, one partly, one never
tested. The two I got most wrong along the way aren't in this table at all — I predicted a
suspicious number would evaporate under scrutiny and it turned out structural, and I predicted an
incompleteness result would be general when it is thresholded. Both times the measured answer had
more structure than the guess.</p>

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

<h3>Relational search — now built and tested</h3>
<div class="read ok"><b>Where this actually got to.</b> On a corpus commissioned from someone with
no knowledge of the measure and frozen before it ran, a structural analogue beats a document
sharing the query's <i>entire vocabulary</i> with different wiring, on every motif. Word overlap
gets that backwards every single time. That is the capability described below, working on data
nobody here wrote.<br><br><b>And it cannot yet produce a usable ranking</b>, because a deliberately
vacuous document that happens to share the query's shape ranks near the top — and the measure is
<i>correct</i> that it matches. Genericness is not a structural property. That failure was
predicted in this project's first risk entry and its defence was never built.</div>
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
    e05 = json.loads((RESULTS / "exp005.json").read_text())
    e24 = json.loads((RESULTS / "exp024.json").read_text())
    e25 = json.loads((RESULTS / "exp025.json").read_text())
    e26 = json.loads((RESULTS / "exp026.json").read_text())
    ret_rows = "".join(
        f"<tr><td>{n}{' <i>(impostor)</i>' if r['is_impostor'] else ''}</td>"
        f"<td><b>{r['analogue_beats_false_friend']}</b></td></tr>"
        for n, r in e24["methods"].items())
    tr_rows = "".join(
        f"<tr><td>{n}</td><td>{r['scores']['B']:.4f}</td><td>{r['scores']['E']:.4f}</td>"
        f"<td>{r['scores']['C']:.4f}</td><td>{r['scores']['D']:.4f}</td>"
        f"<td>{'yes' if r['graded_order_holds'] else 'no'}</td></tr>"
        for n, r in e05["results"].items())
    mi_rows = "".join(
        f"<tr><td>{lbl}</td><td>{sz}</td>"
        f"<td>{e23['k=4']['candidates'][key]['distinct_values']}</td>"
        f"<td>{e23['k=4']['candidates'][key]['values_spanning_multiple_structures']}</td>"
        f"<td>{'yes' if e23['k=4']['candidates'][key]['complete'] else 'no'}</td></tr>"
        for lbl, key, sz in (
            ("influence profile", "A_influence", "k"),
            ("interaction-order profile", "B_level", "k+1"),
            ("the pair", "C_pair", "2k+1"),
            ("spectrum multiset", "E_multiset", "2<sup>k</sup>"),
            ("<b>joint matrix M</b>", "D_matrix", "k(k+1)"),
            ("matrix + multiset", "F_matrix_and_multiset", "more")))
    ix_rows = "".join(
        f"<tr><td>{lbl}</td><td>{e21['k=3'][key]:,}</td><td>{e21['k=4'][key]:,}</td></tr>"
        for lbl, key in (
            ("distinct influence profiles", "distinct_influence_profiles"),
            ("distinct interaction profiles", "distinct_interaction_profiles"),
            ("influence profiles with &gt;1 interaction profile",
             "influence_profiles_with_multiple_interaction_profiles"),
            ("most interaction profiles sharing one influence profile",
             "max_interaction_profiles_per_influence_profile"),
            ("groups with identical retention, different interaction structure",
             "retention_blind_groups")))
    nm_rows = "".join(
        f"<tr><td><code>{n}</code></td><td>{v['profile']}</td>"
        f"<td>{v['spread']:.4f}</td>"
        f"<td>{'yes' if v['influence_symmetric'] else '—'}</td></tr>"
        for n, v in e20["k=3"]["nameable"].items())
    asym_rows = "".join(
        f"<tr><td><code>{n}</code></td><td><code>{r['expression']}</code></td>"
        f"<td>{r['retention_per_participant']}</td><td>{r['best']:.4f}</td>"
        f"<td>{r['worst']:.4f}</td><td><b>{r['spread']:.4f}</b></td></tr>"
        for n, r in e19["families"].items())
    fam_rows = "".join(
        f"<tr><td><code>{k}</code></td><td>{v['per_participant']}</td>"
        f"<td>{v['best']:.4f}</td><td>{v['worst']:.4f}</td>"
        f"<td><b>{v['spread']:.4f}</b></td></tr>"
        for k, v in e18["structure_families_reported_properly"].items())
    n16_rows = "".join(
        f"<tr><td><code>{k}</code></td><td>{v['max_error_general_form']:.1e}</td>"
        f"<td>{v['max_error_deterministic_form']:.4f}</td></tr>"
        for k, v in e16["verification_k3"].items())
    r16_rows = "".join(
        f"<tr><td><code>{k}</code></td><td>{v['concordant']}</td>"
        f"<td>{v['discordant']}</td><td>{v['tau_like']:.4f}</td></tr>"
        for k, v in e16["rank_preservation_vs_noiseless"].items())
    k4_rows = "".join(
        f"<tr><td><b>{c['retention']:.6f}</b></td><td>{c['count']:,}</td></tr>"
        for c in e15["census_k4"]["top_classes"][:8])
    cls_rows = "".join(
        f"<tr><td><b>{c['retention']:.4f}</b></td><td>{c['count']}</td>"
        f"<td>{c['ones_in_truth_table']}</td><td>{c['label'] or '—'}</td></tr>"
        for c in e14["retention_classes"])
    np_rows = "".join(
        f"<tr><td><code>{e}</code></td>" + "".join(
            f"<td>{v.get(n, float('nan')):.4f}</td>" for n in ("AND","OR","majority","parity"))
        + "</tr>" for e, v in e14["noise_pull"].items())
    t13_rows = "".join(
        f"<tr><td><code>{k}</code></td><td>{v['full_bits']:.4f}</td>"
        f"<td>{v['best_partial_bits']:.4f}</td>"
        f"<td><b>{v['retention_best']:.4f}</b></td></tr>"
        for k, v in e13["sweep_structure_type"].items())
    a13_rows = "".join(
        f"<tr><td><code>{k}</code></td><td>{v['full_bits']:.4f}</td>"
        f"<td>{v['best_partial_bits']:.4f}</td>"
        f"<td><b>{v['retention_best']:.4f}</b></td></tr>"
        for k, v in e13["sweep_arity_parity"].items())
    qa_rows = "".join(
        f"<tr><td><code>{v['question']}</code></td><td>{v['I_C']['2']:.4f}</td>"
        f"<td>{v['I_C']['3']:.4f}</td><td>{v['I_C']['4']:.4f}</td>"
        f"<td><b>{('order ' + str(v['significant_order'])) if v['significant_order'] else 'none'}</b></td></tr>"
        for v in e10["probe_a_which_question"].values())
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
{gen_docs.site_header()}
</header>

<div class="card survives-card">{gen_docs.site_survives_panel()}</div>

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

<h2>Finding 9 — what the observer actually chooses, and what it costs</h2>
<p>The last gap was that nothing in the mathematics says <i>what to condition on</i>. The
temptation is to answer that philosophically. Instead: the observer makes three concrete choices,
each can be varied while the world is held fixed, and if the answer moves then the size of the
movement <i>is</i> the answer.</p>

<h3>Probe A — which question you ask</h3>
<p>One fixed system of participants. Six legitimate questions asked of it.</p>
<table><thead><tr><th>question</th><th>I_C(2)</th><th>I_C(3)</th><th>I_C(4)</th>
<th>verdict</th></tr></thead><tbody>{qa_rows}</tbody></table>
<div class="read warn"><b>Reading.</b> Identical participants, identical joint distribution over
them — and verdicts of order 4, order 2, order 3, order 4, order 3, and nothing. <b>There is no
such thing as "the structure of this system."</b> Every structural claim is a claim relative to a
question, and changing the question changes the answer by an entire order.</div>

<h3>Probe B — which participants you can see</h3>
<p>Now hold the question fixed and take away a participant. This is the gap between what is
accessible and what gets resolved, made concrete.</p>
<div class="fig">{figs['fig10_cliff.svg']}</div>
<div class="read warn" style="border-color:#dc2626"><b>⚠ CORRECTED by Finding 10.</b> What
follows is true and was <i>over-generalised</i>. It was measured on parity — the maximally
synergistic function there is, built so that no subset of its inputs carries any information at
all. That is the worst case by construction. Finding 10 tests four other structure types and
finds they retain roughly <b>half</b> their information under the same treatment. The cliff is
real and it is the endpoint of a gradient, not a universal wall. The claim as originally written
— "you either observe a configuration whole or you detect nothing" — is <b>false for anything
except pure synergy</b>. Left visible rather than edited away.</div>
<div class="read warn"><b>This is a cliff for parity, and it is the most consequential result
here for anything practical.</b> With all three participants visible the dependence is
unmistakable: <b>0.7246</b>. Hide any one of them and it reads <b>0.00000</b>. Not weakened —
gone. A three-way dependence marginalised over one of its three participants is <i>uniform</i>;
there is nothing left in the data to find.<br><br>And more data does not help: five times the
sample moves it from 0.00005 to 0.00006. <b>This is an identifiability limit, not a power
limit.</b> No quantity of observation recovers structure whose participants you cannot all see
at once.</div>
<div class="read"><b>A caution about our own instrument, from the same table.</b> The
"missing b" case returns p = 0.0165 — nominally significant — on an effect of <b>0.0005</b>,
some 1400× smaller than the real one. At this sample size the permutation test will happily flag
arbitrarily small effects. <b>Significance is not effect size</b>, and any use of this machinery
must report both. Noted because it is exactly the kind of thing that would later be mistaken for
a finding.</div>

<h3>Probe C — is there anything left that does not depend on the observer?</h3>
<p>The participants in this system carry a full bit of genuine three-way structure among
<i>themselves</i> — I_C(3) = 0.9995, computed with no outcome at all. That number is
outcome-invariant by construction. It is also, per the previous finding, exactly what the
calibration correctly rejects as not being an answer to anything.</p>
<div class="read ok"><b>So the picture closes.</b> Participant-internal structure is objective
and outcome-free — and is not an answer. Outcome-relative structure is an answer — and depends
on the question. Across six legitimate questions there was <b>no invariant relevant claim</b>:
the verdicts spanned three different orders. There is no third thing.<br><br><b>Significance
cannot be defined without naming a question.</b> That is not a missing feature of the instrument
to be engineered around. It is a property of the subject matter, and it is now measured from
three independent directions rather than assumed.</div>

<h2>Finding 10 — the cliff is a gradient, and the last finding was over-stated</h2>
<p>Finding 9 concluded that partial observation erases higher-order structure, and turned that
into a governing constraint on applications. But it was measured on <b>parity</b> — a function
built so that no subset of its inputs carries any information whatsoever. That is the worst case
by construction, and generalising a constraint from its worst case is how a true finding becomes
a false rule.</p>

<h3>Parity does cliff, at every arity</h3>
<table><thead><tr><th>world</th><th>all visible</th><th>one hidden</th><th>retained</th></tr>
</thead><tbody>{a13_rows}</tbody></table>
<p>Three, four or five participants — retention stays under 0.2%. That part of Finding 9 holds
without qualification.</p>

<h3>Nothing else does</h3>
<table><thead><tr><th>world</th><th>all visible</th><th>one hidden</th><th>retained</th></tr>
</thead><tbody>{t13_rows}</tbody></table>
<div class="read ok"><b>Reading.</b> AND, OR, majority and threshold functions all retain
<b>roughly half</b> their outcome-relevant information when a participant is hidden — about 50%
at three participants and slightly more at four. They have lower-order leakage: knowing some of
the inputs genuinely tells you something. Parity is the only structure here with none, and it is
the only one that vanishes.</div>

<h3>And the shape between them is smooth</h3>
<p>Take a participant that matters only some of the time, and sweep how often.</p>
<div class="fig">{figs['fig11_gradient.svg']}</div>
<div class="read"><b>A continuum, not a step.</b> 1.00 → 0.89 → 0.60 → 0.26 → 0.05 → 0.00 as the
hidden participant goes from irrelevant to essential. There is no threshold where detection
suddenly fails; there is a slope, and parity sits at the bottom of it.</div>

<h3>The corrected statement</h3>
<div class="read ok"><b>Partial observation destroys higher-order structure in proportion to how
purely synergistic that structure is.</b> Pure synergy — no information in any subset — is erased
completely, at any arity, and no amount of data recovers it. Structures with lower-order leakage
degrade gracefully. Real systems are mostly the second kind.<br><br>This is a <i>better</i>
result for applications than the one it replaces. The constraint is real but bounded: what you
lose to incomplete observation is predictable from how much of the structure lives in the parts.
The pessimistic version would have ruled out most practical work; the measured version tells you
what to expect.</div>
<div class="read warn"><b>One number left unexplained — now resolved in Finding 11, and the
evidence here turned out to be invalid.</b> The four structures land at 0.4965, 0.5028, 0.4996
and 0.4996, suspiciously close to exactly half. Flagged rather than claimed. Finding 11 shows
one half <i>is</i> real — and that these four were not four, and two of them are not in that
class at all.</div>

<h2>Finding 11 — the number was real. The evidence for it was not.</h2>
<p>The previous finding flagged a suspicious result: four structures all retaining almost exactly
half. Flagged, not claimed. Testing it turned up something in both directions.</p>

<h3>First, the four were two</h3>
<div class="read warn"><b>Found before running anything.</b> <code>majority</code> and
<code>threshold2</code> are <b>the same function</b> at three variables — identical truth tables.
And <code>AND</code> and <code>OR</code> are De Morgan duals, related by a transformation that
preserves mutual information exactly. So "four independent structures agreeing on 0.5" was
<b>two structures, each counted twice</b>. The consistency was manufactured by which functions
I happened to pick.</div>

<h3>Then, the exhaustive census</h3>
<p>No sampling. For a Boolean function with uniform inputs and symmetric noise the joint
distribution is known exactly, so the information can be computed in closed form. Which means
every Boolean function of three variables can be checked — all 256 of them, not a sample.</p>
<div class="fig">{figs['fig12_census.svg']}</div>
<table><thead><tr><th>retention</th><th>how many functions</th><th>ones in truth table</th>
<th>what these are</th></tr></thead><tbody>{cls_rows}</tbody></table>
<div class="read ok"><b>Retention is quantised.</b> Across all 256 functions it takes only
<b>seven distinct values</b>. And 0.5 is a genuine class — <b>56 functions, 22% of the
non-degenerate ones</b>, every single one of them <i>balanced</i> (exactly four ones in its truth
table). Majority is one of them, at exactly 0.5000 regardless of noise. <b>So the number is
real.</b></div>

<h3>But not for the reason the last finding suggested</h3>
<table><thead><tr><th>noise</th><th>AND</th><th>OR</th><th>majority</th><th>parity</th></tr>
</thead><tbody>{np_rows}</tbody></table>
<div class="read warn"><b>AND and OR are not in the 0.5 class at all.</b> Their exact retention
is <b>0.5401</b> — a different class entirely, the one-or-seven-ones functions. They appeared to
sit at 0.5 in the previous finding purely because <b>5% noise pulls 0.5401 down to 0.4958</b>.
At 1% they read 0.525; at 20% they read 0.451. The agreement was an artifact of the noise level
I happened to choose.<br><br>So of four reported measurements: two were the same function, two
were duals in a different class, and their apparent agreement came from noise. <b>One genuine
data point, dressed as four.</b></div>

<h3>What I got wrong</h3>
<p>I predicted the distribution would be <i>spread</i> and that 0.5 would evaporate under
scrutiny. It didn't. Retention is sharply quantised and 0.5 is one of its largest classes — a
structural fact about balanced functions, not a coincidence. I was right that noise had moved
AND, and wrong about the headline. The census settled it in a way no amount of further reasoning
would have.</p>
<div class="read"><b>The useful form of the result.</b> Retention under partial observation is
not a continuous property to be estimated — it falls into a small number of exact classes
determined by the shape of the function. Parity alone reaches zero. Balanced non-parity functions
sit at one half. Functions with an idle input lose nothing. If that quantisation survives past
three Boolean variables it is a genuinely useful thing to know before designing any measurement:
what you stand to lose is predictable from the shape of what you are looking at, in advance.</p>
<div class="read warn"><b>Untested and therefore not claimed:</b> whether the quantisation holds
at four or more variables, for non-Boolean participants, or for non-uniform inputs. Three binary
variables is a very small world, and the clean structure found here may be a property of it.</div>

<h2>Finding 12 — it survives at four variables, and there is a closed form</h2>
<p>The obvious worry about the last finding was that seven neat values might be a property of a
very small world. Four variables is 65,536 functions — still exhaustive, still exact.</p>

<h3>The algebra collapses</h3>
<p>Setting this up, the computation turned out not to need computing. Hiding one participant
groups the input patterns into pairs that differ only in that participant. Within a pair the
outcome is either constant or evenly split, and everything else cancels:</p>
<div class="fig">{figs['fig13_k4.svg']}</div>
<p>The quantity in the numerator is the <b>influence</b> of a variable — a standard measure in
Boolean function analysis, the fraction of input pairs on which flipping that one variable
changes the answer. So what you lose by not seeing a participant is <b>exactly that participant's
influence, divided by the entropy of the outcome.</b></p>
<div class="read ok"><b>Both quantities are computable from the structure itself, in advance,
without measuring any loss.</b> This is not a new mathematical result — influence is
well-studied, and the relation follows directly once written down. That is precisely why it is
usable: it is a bridge from this project's question to a body of work that already exists.</div>
<div class="read"><b>Verified, not assumed.</b> Checked against brute-force exact mutual
information on every non-degenerate function at three variables and 478 at four. Maximum
absolute error <b>1.1 × 10⁻¹⁶</b> — floating-point noise. A derivation that had not been checked
would have been the seventh construction error in this log rather than the first clean one.</div>

<h3>And it explains everything that came before</h3>
<table><thead><tr><th>retention at k=4</th><th>functions</th></tr></thead><tbody>{k4_rows}</tbody></table>
<ul>
<li><b>Quantisation survives</b> — 7 distinct values at k=3, <b>21 at k=4</b>, out of 65,534
functions. Because influence takes only the values m/2<sup>k−1</sup> and the outcome entropy only
h(ones/2<sup>k</sup>), retention is a ratio of two discrete sets.</li>
<li><b>Parity is still the unique zero</b> — exactly two functions, parity and its complement. It
is the only function where <i>every</i> participant has maximal influence, so there is no
participant you can afford to lose.</li>
<li><b>One half is still a real class</b> — 5,896 functions, and now with a reason: a balanced
outcome has entropy 1, so any function whose least-influential participant has influence ½ lands
there exactly.</li>
<li><b>The old anomaly resolves</b> — AND at three variables has a least influence of ¼ and an
outcome entropy of 0.5436, giving 1 − 0.25/0.5436 = <b>0.5401</b>. Exactly what was measured, and
now derived rather than observed.</li>
</ul>
<div class="read ok"><b>Which makes the earlier claim concrete.</b> "What you lose to incomplete
observation is predictable from the shape of what you are looking at" is no longer a hopeful
summary of a histogram. It is an equation, verified, with both of its terms computable before any
measurement is taken.</div>
<div class="read warn"><b>Scope, stated plainly.</b> Deterministic Boolean functions, uniform
inputs, hiding exactly one participant, noiseless. Noise adds a term that does not cancel — which
is why AND drifted with noise in the previous finding. Non-Boolean participants, non-uniform
inputs, and hiding several participants at once are all untested.</div>

<h2>Finding 13 — the law under noise: it generalises, but stops being safe to rank with</h2>
<p>The previous finding stated plainly that its derivation assumed no noise, and that the noise
term does not cancel. Carrying it through rather than dropping it gives</p>
<p style="text-align:center"><code>retention<sub>e</sub> = 1 − Influence · (1 − h(e)) / (H<sub>e</sub> − h(e))</code></p>
<p>which reduces to the deterministic form when the noise is zero.</p>
<div class="fig">{figs['fig14_noise.svg']}</div>
<table><thead><tr><th>noise</th><th>error, general form</th><th>error, deterministic form</th>
</tr></thead><tbody>{n16_rows}</tbody></table>
<div class="read ok"><b>The general form holds exactly.</b> Worst-case error against brute-force
mutual information is ~10⁻¹⁶ at every noise level, across all 254 functions, and 4.4×10⁻¹⁶ on a
spread sample at four variables. The deterministic form degrades steadily — 0.015 at 1% noise,
0.089 at 20%, 0.109 at 40%. It was never claimed to survive noise; now the size of the failure
is measured rather than assumed.</div>

<h3>And it explains something that had been sitting unexplained for two findings</h3>
<div class="read ok"><b>Balanced outcomes are <i>exactly</i> noise-invariant.</b> Maximum drift
across every noise level tested: <b>0.00e+00</b>. Not small — zero. A balanced outcome stays
balanced under symmetric noise, so its entropy remains 1, the noise terms cancel completely, and
retention collapses to <code>1 − Influence</code> with no noise term at all. Unbalanced functions
drift by up to 0.109.<br><br>That is why <code>majority</code> sat at exactly 0.5000 at every
noise level while <code>AND</code> slid from 0.5401 to 0.4958. That asymmetry was observed two
findings ago, used as evidence, and never understood. It now falls out of the algebra.</div>

<h3>The part that is a genuine limit</h3>
<table><thead><tr><th>noise</th><th>concordant pairs</th><th>discordant</th><th>rank agreement</th>
</tr></thead><tbody>{r16_rows}</tbody></table>
<div class="read warn"><b>Noise reorders which structures are most fragile.</b> At 1% noise the
ordering is untouched. From 5% upward, discordant pairs appear and rank agreement drops to 0.938
and stays there. So the deterministic law is <b>not a safe proxy for relative fragility once data
is noisy</b> — and data is always noisy.<br><br>Practically: you cannot rank candidate structures
by their clean-case retention and expect that ordering to hold in the field. The general form
needs the actual noise level, and getting that wrong changes the answer's <i>order</i>, not just
its magnitude. This is the same shape of failure as the very first finding in this log, where a
free parameter reordered results — arriving from a completely different direction.</div>
<p class="sub">Rank comparison is over a strided sample of pairs, not all of them, so the counts
are indicative. The existence of discordance is what matters and that is not sample-dependent.</p>
<div class="read"><b>Quantisation is untouched.</b> Exactly seven distinct retention values at
every noise level tested. The values move; the count does not.</div>

<h2>Finding 14 — the reordering audit: it is the norm, not the exception</h2>
<p>Twice a parameter had changed the <i>order</i> of results rather than their size. Rather than
meet it a third time by surprise, every nuisance parameter in the project was audited against one
question: holding everything else fixed, does varying this change the ranking?</p>
<div class="fig">{figs['fig15_audit.svg']}</div>
<p><b>Four of five reorder.</b> Magnitude errors are visible and forgivable. Order errors are
invisible and change decisions, because you act on a ranking, not on an absolute value.</p>

<h3>The one that matters most</h3>
<div class="read warn"><b>Which participant you lose reorders almost everything.</b> Ranking all
254 functions by best-case retention and by worst-case retention gives agreement of
<b>−0.117</b> — slightly <i>anti</i>-correlated, with 12,288 pairs swapping. The structures that
are most robust when you lose your least important participant are close to the structures that
are most fragile when you lose your most important one.<br><br><b>So "retention" is not a
number.</b> It is one number per participant you might lose. The law itself
(<code>1 − Influence<sub>j</sub> / H</code>) is exact and per-participant, so it was always right;
what was wrong was summarising it with a best case, which every previous finding here did. Any
claim of the form "structure X is more fragile than structure Y" is incomplete without saying
<i>which participant is missing</i>.</div>

<h3>And the positive control failed, which is the useful part</h3>
<p>The audit included a parameter believed to be order-preserving — the description code — as a
check that the audit could distinguish stability from noise. It did not come back clean.</p>
<table><thead><tr><th>code</th><th>ranking under the current measure</th></tr></thead><tbody>
<tr><td><code>gamma</code></td><td>B &gt; B2 &gt; E &gt; F &gt; C &gt; D</td></tr>
<tr><td><code>delta</code></td><td>B &gt; B2 &gt; E &gt; F &gt; C &gt; D</td></tr>
<tr><td><code>flat32</code></td><td><b>F</b> &gt; B &gt; B2 &gt; E &gt; C &gt; D</td></tr>
</tbody></table>
<div class="read warn"><b>Under the crude code, the superset distractor ranks first</b> — ahead of
the true analogue. The earlier claim that the ranking was stable across all three codes was tested
on a condition set that <i>did not yet contain the superset</i>, and using the gain form rather
than the ratio. On that narrower set the claim is true. On the full one it is false for the crude
code.<br><br>Same shape as the over-generalisation two findings ago: a claim true within its test
set, extended past it. That is now three occurrences, and it appears to be this project's
characteristic error rather than a series of accidents.</div>
<div class="read ok"><b>The reassuring half.</b> Among the two <i>reasonable</i> codes the order
is identical. And the way <code>flat32</code> breaks — ranking a superset above a true analogue —
is precisely the failure the harness's superset control was built to detect, so a measure built on
it would be rejected before it was ever used. The safeguard caught it; only the write-up had
over-reached.</div>

<h3>What this changes</h3>
<div class="read"><b>New standing rule.</b> Report rankings as a curve over the nuisance
parameter, not at a point — for noise, sample size, code choice, and which participant is
missing. Where a single ordering is needed, state the parameter value it holds at. This stops
being a lesson to rediscover and becomes part of the protocol.<br><br>Arity was the only
parameter that preserved order cleanly. That is worth knowing too: results can be carried between
three and four participants without re-ranking.</div>

<h2>Finding 15 — re-reporting properly, and a claim that does not survive it</h2>
<p>The previous finding showed that best-case and worst-case retention rank structures
anti-correlated. Every result here from Finding 10 onward summarised retention with a best case.
The law is per-participant and exact, so the mathematics was never wrong — but every
<i>conclusion</i> drawn from that summary needed re-checking. This is the re-check, recomputed
rather than re-worded.</p>
<div class="fig">{figs['fig16_vector.svg']}</div>

<h3>What survives</h3>
<ul>
<li><b>Quantisation.</b> Pooling every participant of every function gives the same counts as
before — 7 distinct values at three variables, 21 at four. Robust to how it is reported.</li>
<li><b>One half is still a real class</b>, in every reporting mode.</li>
<li><b>The closed form</b> — untouched. It was always stated per-participant.</li>
</ul>

<h3>What does not survive</h3>
<div class="read warn"><b>"Parity is the only structure that vanishes" was an artifact of
best-case reporting.</b> Under worst-case, the number of functions losing <i>everything</i> goes
from 2 to <b>38</b> at three variables and from 2 to <b>942</b> at four.<br><br>The corrected
claim is narrower and more useful: <b>parity is unique in vanishing no matter which participant
you lose.</b> Plenty of other structures vanish too — if you lose the right one. For anything
practical that is the more alarming version, and it was hidden by taking a best case.</div>
<div class="read warn"><b>And the spread is not small.</b> Within a single function, best minus
worst has a median of <b>0.52</b> at three variables. Only 39% of functions have no spread at all
at k=3, and just 11% at k=4. So for the large majority of structures, <i>which</i> participant
goes missing changes the answer substantially. Retention has to be carried as a vector.</div>

<h3>Why the earlier tables came out unscathed — and what that says</h3>
<table><thead><tr><th>family</th><th>per participant</th><th>best</th><th>worst</th><th>spread</th>
</tr></thead><tbody>{fam_rows}</tbody></table>
<div class="read"><b>Every family previously tested has spread exactly zero.</b> Parity, AND, OR,
threshold, majority — all <i>symmetric</i> functions, where every participant has identical
influence, so best and worst coincide and the best-case summary happened to be harmless.<br><br>
That is lucky rather than sound, and it is the third time the symmetry of my chosen test functions
has produced a misleadingly clean picture. Majority and threshold turned out to be the same
function; AND and OR turned out to be duals; and now every family in the table turns out to be
symmetric. <b>The test set has a systematic bias toward symmetric structures</b>, which are
precisely the ones on which the sloppy summary is safe. Logged as its own thing to check for,
because it has now cost three corrections.</div>

<h3>The rules this produced</h3>
<p>Five hard-won rules from this run of work are now written into the protocol rather than living
in the write-ups where they get rediscovered:</p>
<ol>
<li>Report rankings as a <b>curve over the nuisance parameter</b>, not at a point.</li>
<li>For every variable a condition set holds fixed, keep <b>one condition where it varies</b>.</li>
<li><b>Verify test cases are actually distinct</b> before counting them as separate evidence —
compare the objects, not the names.</li>
<li>State the <b>condition set inside the claim</b>; before generalising, name the case that
would break it and check the test set contains one.</li>
<li>An <b>unexplained regularity is a debt</b>, not a curiosity. Two findings used one as evidence
before understanding it.</li>
</ol>

<h2>Finding 16 — the asymmetric families, and the bug they found immediately</h2>
<p>Three corrections traced to a test set where every structure treated its participants
identically. Adding families that don't was the outstanding fix. It paid for itself on the first
run, in a way worth describing precisely.</p>
<div class="fig">{figs['fig17_asym.svg']}</div>
<table><thead><tr><th>family</th><th>expression</th><th>per participant</th><th>best</th>
<th>worst</th><th>spread</th></tr></thead><tbody>{asym_rows}</tbody></table>
<div class="read"><b>Reading.</b> Two families <b>vanish entirely</b> if you lose one specific
participant while retaining half or three quarters if you lose any other.
<code>a XOR (b AND (c OR d))</code> reads <b>0.75</b> under a best-case summary and
<b>0.00</b> if the wrong participant goes missing. That single number would be true and almost
entirely useless — which is the concrete form of the previous finding's warning.</div>

<h3>The distinction the old set was hiding</h3>
<div class="read ok"><b>The multiplexer is the control, and it corrects the diagnosis.</b>
<code>b if a=0 else c</code> is <i>not</i> permutation-symmetric — a selector is nothing like a
data input, and swapping them gives a different function. Yet all three of its participants have
identical influence, so its spread is <b>exactly zero</b>, indistinguishable from majority.<br><br>
So the property that matters is <b>influence-symmetry, not permutation-symmetry</b>. A test set
could be full of structurally lopsided functions and still be completely blind to this. The
earlier diagnosis said "symmetric" and meant the wrong one.</div>

<h3>And then it found a real bug, on its first execution</h3>
<div class="read warn"><b>The closed form appeared to fail — maximum error 0.75.</b> It hadn't.
Two conventions for "participant <i>j</i>" had been sitting in the codebase disagreeing by a
reversal: one indexes by bit position, the other builds patterns in the opposite order. Comparing
them element-wise exposed it instantly. Corrected, the error is 1.1×10⁻¹⁶ across every
family.<br><br><b>No published result is affected</b> — every number reported so far was a best or
worst case, and aggregating over participants makes a reversal invisible. It would have bitten the
moment anything was reported per-participant, which the previous finding had just made
mandatory.</div>
<div class="read ok"><b>But look at <i>why</i> it was invisible for so long.</b> Under the old test
set, the comparison passes whether or not the indices are reversed — because when every
participant has the same value, reversing the list changes nothing. <b>A symmetric test family is
structurally incapable of detecting an index reversal.</b> The bug could not have been found with
the previous worlds no matter how carefully anyone looked at them.<br><br>That is the strongest
argument for the rule that this run of work has produced: a condition set does not merely fail to
cover cases it omits — it can be <i>provably unable</i> to detect entire classes of error.</div>

<h2>Finding 17 — the census, and the bias measured rather than confessed</h2>
<p>The asymmetric families were <i>chosen</i> to span a range, which is a sample with a taste in
it. The systematic version indexes every Boolean function by its <b>influence profile</b> — the
sorted list of how much each participant matters — because that, together with the outcome
entropy, is exactly what determines fragility.</p>

<h3>Asymmetry is quantised too</h3>
<ul>
<li><b>10 distinct influence profiles</b> at three participants, <b>59</b> at four. The space of
"how unevenly can participants matter" is small and enumerable, like retention itself.</li>
<li><b>The profile alone does not determine fragility.</b> One profile at k=3 and <b>22</b> at k=4
map to several outcome entropies — so two structures can have identical participant-importance and
still differ in how much they lose. Importance and fragility are related but not the same
information.</li>
<li><b>Maximum spread is exactly 1.0</b>, achieved by the <i>dictator</i> — profile [0, 0, 1],
retention [1, 1, 0]. Lose either irrelevant participant and nothing changes; lose the one that
matters and everything goes. The simplest structure has the most extreme spread of all.</li>
</ul>

<h3>And the bias that started this, measured</h3>
<div class="fig">{figs['fig18_naming.svg']}</div>
<table><thead><tr><th>function</th><th>influence profile</th><th>spread</th>
<th>influence-symmetric</th></tr></thead><tbody>{nm_rows}</tbody></table>
<div class="read warn"><b>Functions you can name in English are influence-symmetric far out of
proportion.</b> 70% of the nameable ones against 38.6% of the population at three participants —
and <b>67% against 10.9%</b> at four. An over-representation factor of <b>1.8× rising to
6.1×</b>.<br><br>Worse, <b>the bias grows with arity</b>: symmetric functions get rarer as
participants are added, while the ones that come to mind do not. At three participants the entire
nameable list — parity, AND, OR, majority, multiplexer, NAND — is symmetric. The only asymmetric
entries are a dictator and two functions invented specifically to break the pattern.</div>
<div class="read ok"><b>So the earlier diagnosis was too generous to itself.</b> Calling it a
biased test set implies carelessness that could have been avoided by being more careful. It could
not. <b>Reaching for examples by name is what produces this</b>, and being more thoughtful about
which functions to name would have made it worse, not better — the thoughtful ones are the
canonical ones, and the canonical ones are symmetric.<br><br>The only fix is the one taken here:
build the test set by <b>enumerating the property you care about</b> — influence profile — rather
than by collecting examples. That is a rule with teeth, because it says <i>where</i> the examples
must come from rather than merely asking for more of them.</div>

<h2>Finding 18 — what the predictive equation cannot see</h2>
<p>The census so far measured how much each participant matters <i>on its own</i>. That is a
first-order quantity, and the Fourier expansion of a Boolean function shows exactly how
first-order it is: influence is a <b>marginal</b> of the full interaction structure —
<code>I<sub>j</sub> = Σ<sub>S∋j</sub> f̂(S)²</code>. Marginals lose information. The question is
whether the lost information is real, and whether anything here can see it.</p>
<p class="sub">Machinery verified first: Fourier-derived influence against the combinatorial
influence used everywhere else, maximum error <b>0.00e+00</b> at both arities.</p>

<h3>Interaction structure is a genuinely separate axis</h3>
<table><thead><tr><th></th><th>k=3</th><th>k=4</th></tr></thead><tbody>{ix_rows}</tbody></table>
<p>Quantised again — 13 interaction profiles at three participants, 161 at four. And
<b>independent</b>: at four participants, 30 influence profiles map to more than one interaction
profile, with as many as <b>17</b> distinct interaction structures sharing a single influence
profile. Knowing how much each participant matters tells you substantially less than knowing how
they interact.</p>

<h3>And the law is blind to it — provably, not approximately</h3>
<p>Retention is <code>1 − Influence / H</code>. It depends on influence and outcome entropy and on
nothing else. So any two structures sharing both get <i>identical</i> retention vectors, whatever
their interaction structure. Such pairs exist: <b>2 groups at three participants, 45 at four</b>.</p>
<div class="fig">{figs['fig19_blind.svg']}</div>
<div class="read warn"><b>The witness.</b> Two structures with the same influence profile, the same
entropy, and therefore the same predicted retention down to the last decimal — where one spreads
its organisation evenly across every interaction order and the other puts <b>three quarters of
itself at order 2 with nothing at orders 1 or 3</b>. The law returns the same number for both. Not
approximately the same. The same.</div>

<h3>What that means, stated plainly</h3>
<div class="read"><b>The retention law is a robustness law, not a structure law.</b> It is exact,
verified to 10⁻¹⁶, and it tells you what you stand to <i>lose</i> when a participant goes missing.
It does not tell you what you <i>had</i>. Two systems organised in completely different ways —
one purely pairwise, one distributed across every order — are indistinguishable to it.<br><br>
That lands directly on the thesis rather than off to the side. The project exists because
configurations are supposed to carry structure their parts do not, and the one predictive equation
it has produced <b>cannot see interaction order at all</b>. Both things are true: the law is real
and useful, and it is not a measure of relational organisation. Conflating those would have been
the natural next mistake, and it is better to have it established deliberately than to meet it
later as a surprise.</div>
<div class="read ok"><b>The constructive reading.</b> Connected information already measures
interaction order, and it is blind to which participant carries what. The retention law measures
per-participant importance and is blind to order. They are complementary blindnesses on the same
object, which suggests the honest instrument is the pair rather than either alone — and that a
single scalar for "relational structure" was never going to exist.</div>

<h2>Finding 19 — the two instruments are enough, until they aren't</h2>
<p>The previous finding left the two measures with complementary blind spots and asked whether
together they are sufficient. As originally posed the question is empty — you can always staple
two things together. The version that can be answered is: <b>if two structures agree on both
profiles, must they be the same structure?</b> If not, even both instruments miss something and
there is a third axis.</p>
<p class="sub">The comparison has to be against NPN equivalence — permuting participants, negating
inputs, negating the output — because both profiles are invariant under all of those. Testing
against relabelling alone would manufacture false incompleteness by counting a structure and its
negation as different. Getting the symmetry group wrong is the same error a previous finding
caught in a different guise.</p>

<h3>The answer depends on how many participants there are</h3>
<table><thead><tr><th></th><th>3 participants</th><th>4 participants</th></tr></thead><tbody>
<tr><td>distinct profile pairs</td><td>13</td><td>194</td></tr>
<tr><td>pairs containing more than one structure</td><td><b>0</b></td><td><b>8</b></td></tr>
<tr><td><b>is the pair complete?</b></td><td><b>yes</b></td><td><b>no</b></td></tr>
</tbody></table>
<p>At three participants the two instruments together are <b>sufficient</b> — verified two
independent ways, by full NPN canonicalisation and by a finer NPN-invariant. At four they are
not.</p>

<h3>The witness</h3>
<div class="fig">{figs['fig20_complete.svg']}</div>
<div class="read warn"><b>Two structures where every participant is equally important and the
distribution across interaction orders is identical</b> — and one concentrates its entire
organisation into <b>four</b> subsets while the other spreads the same total across <b>ten</b>.
Both instruments return identical answers for both. The thing that differs is <i>which specific
groups of participants</i> carry the structure, and neither measure looks at that.</div>

<h3>What it settles</h3>
<div class="read ok"><b>"Relational structure = participant importance + interaction order" is a
valid decomposition only for small configurations.</b> Past three participants it is provably
lossy. The complete invariant is the full subset-indexed spectrum — one number per subset of
participants, 2<sup>k</sup> of them — not a scalar, not a pair of profiles.<br><br>Which means
this project's founding rule that a measurement must never be collapsed into a single score is not
a matter of taste. Below a certain size two numbers-per-thing genuinely suffice; above it, no
summary of that shape can. The rule was written as a discipline against premature compression and
turns out to describe a property of the subject matter.</div>
<div class="read"><b>And I predicted this wrong.</b> I expected incompleteness generally and would
have written that up as the finding. It is incompleteness <i>past a threshold</i>, with genuine
sufficiency below it — which is a more useful result and not one that arguing would have reached.
Second prediction of mine to fail in this run of work; both times the measured answer was more
structured than the guess.</div>

<h2>Finding 20 — the search for a minimal summary, and why it fails</h2>
<p>The previous finding left a gap: the pair of profiles is insufficient at four participants, and
the full subset-indexed spectrum is sufficient but is 2<sup>k</sup> numbers. What sits between?</p>

<h3>Setting it up exposed the structure</h3>
<p>Define <code>M[j][d]</code> = how much of participant <i>j</i>'s importance lives at interaction
order <i>d</i>. Then the row sums are the influence profile and the column sums are the
interaction-order profile.</p>
<div class="read ok"><b>The pair is exactly the two marginals of M.</b> So the previous finding —
that the pair is insufficient — is precisely the statement that <i>these marginals lose the
joint</i>. Which is this project's own founding thesis arriving one level up, about its own
instruments. That is either a pleasing coincidence or a sign the shape is general, and either way
it made the joint the obvious next candidate rather than a guess.</div>
<div class="fig">{figs['fig21_minimal.svg']}</div>
<table><thead><tr><th>summary</th><th>size</th><th>distinct values</th><th>collisions</th>
<th>complete?</th></tr></thead><tbody>{mi_rows}</tbody></table>

<h3>The answer</h3>
<ul>
<li><b>At three participants, the interaction-order profile alone is complete</b> — 13 values,
no collisions. Influence alone is not. The instruments are more than sufficient down there.</li>
<li><b>At four participants, nothing tested is complete.</b> The best is the joint matrix M:
<b>217 distinct values against 222 structures — just 2 collisions left.</b> Close, and not
enough.</li>
<li>Both residual collisions are maximally symmetric under M: in the larger one, all four
participants have <i>identical rows</i>, and four genuinely different structures share it. M fails
exactly where its own summary is most even — the same shape that has caught this project three
times now.</li>
</ul>

<h3>The part worth carrying away</h3>
<div class="read warn"><b>More numbers is not more information.</b> The spectrum multiset writes
down <b>16</b> numbers and distinguishes <b>8</b> structures. The joint matrix writes down
<b>20</b> and distinguishes <b>217</b>. And adding the multiset to the matrix changes the answer
by <i>nothing at all</i> — every collision it might have broken, the matrix had already broken.
<br><br>The multiset looks like a lot of information and is almost entirely degenerate: across all
65,536 four-participant structures there are only eight distinct multisets, because Parseval and
integrality constrain them so tightly. Which numbers you keep matters enormously more than how
many.</div>
<div class="read"><b>So Q-19's answer is negative, usefully.</b> There is no compact summary among
the natural candidates. The minimal sufficient invariant sits strictly above the joint matrix and
at or below the labelled spectrum, and the remaining gap is two collisions wide. Relational
structure resists compression harder than the tidy arc of the last few findings suggested — the
law, the profiles, and the census were each real, and none of them adds up to a description of a
configuration.</div>

<h2>Finding 21 — does it work on shapes it was never built for?</h2>
<p>Every result about the correspondence measure so far rested on one structure family: the
reinforcing-channel motif it was developed against. A measure tested only on the worlds it was
built for may have learned those worlds, and every application downstream inherits that doubt.
This is the gate between "works on my worlds" and "works".</p>
<p class="sub">Five base topologies, chosen against a property list rather than by recall — cycles,
branching, degree concentration, path multiplicity, and one nobody designed. The conditions are
derived <i>identically</i> from each base, so the only variable is the shape.</p>
<div class="fig">{figs['fig22_transfer.svg']}</div>
<table><thead><tr><th>topology</th><th>perfect analogue</th><th>near-miss</th>
<th>same words, rewired</th><th>matched random</th><th>graded order?</th></tr></thead>
<tbody>{tr_rows}</tbody></table>
<div class="read ok"><b>It transfers.</b> The graded ordering — perfect analogue above near-miss
above both wrong answers — holds on all five, including a topology with no cycles at all (the one
property the measure was developed around) and one that nobody designed. The ordering is also
stable across all three description codes. <b>The standing doubt that this was an n=1 result is
discharged.</b></div>

<h3>The first version of this test was too easy, and the fix found a real bug</h3>
<div class="read warn"><b>Run one used only the perfect analogue and the two wrong answers, and
passed 4 of 4 — which should have been suspicious.</b> A perfect isomorph of matched size
compresses to essentially the same score on every topology, so the question had degenerated to
"can it spot an exact copy". Adding the near-miss turned it into a question about <i>degrees</i>
of correspondence, and one topology promptly failed: the near-miss outranked the perfect
copy.<br><br><b>The cause was not the measure.</b> The random generator had emitted two relations
between the same pair of participants differing only in type. Flipping one made them identical —
and because relations are held in a set, the duplicate <b>silently collapsed</b>. The structure
reported six relations and had five, which made it cheaper to describe and inflated its
score.</div>
<div class="read"><b>Nothing had checked that invariant in twenty-three experiments.</b> It never
fired because every earlier world was hand-built, and hand-built worlds do not have parallel
edges. That is the same condition-set blindness this log has now hit repeatedly — arriving this
time in the <i>container</i> rather than in a measure, where nobody was looking.<br><br>The
container now asserts that a structure's declared size equals its distinct-relation count, and
every experiment checks it before running. The generator was fixed to match. Re-run:
<b>5 of 5, graded ordering everywhere.</b></div>

<h2>Finding 22 — the search corpus, a real d_A, and the measure falls short</h2>
<p>Two pieces of infrastructure the project has been blocked on since day one, and the first test
that puts the measure in front of something resembling an application.</p>

<h3>d_A, derived rather than invented</h3>
<p>What blocked it was that the obvious answers are all ruled out by things this log has since
measured. A <b>scalar</b> distance is out — relational structure is not a scalar. A <b>single
summary over parts</b> is out — summarising a per-component quantity is a choice that can reverse
a ranking. An <b>observer-free</b> distance is out — significance cannot be defined without naming
a question.</p>
<div class="read ok"><b>What remains is not a gap.</b> The components of d_A should be the ways a
relational answer can be <i>wrong</i> — and this project already had that list, written as
principles before any of it was measured: a real relation <b>missing</b>; a relation
<b>asserted</b> too strongly; an analogy <b>sold as a mechanism</b>; a result placed at the wrong
relational distance. So d_A is a <b>vector over named failure modes</b>, each traceable to a
principle that predates it, and Pareto dominance replaces a fabricated total. Where neither of two
results dominates, saying they are incomparable is more useful than inventing weights.</div>

<h3>The corpus</h3>
<p>Three structurally distinct motifs — a positive cycle, a negative cycle, an acyclic cascade —
six hand-annotated documents each. For every motif: a paraphrase, a <b>cross-domain analogue</b>,
a <b>false friend</b> that shares the query's entire vocabulary with different structure, a generic
connector, and an unrelated control. Ground truth by construction. Relations are annotated by
hand on purpose: testing an extractor and a measure at the same time makes every result
uninterpretable.</p>

<h3>The result</h3>
<div class="fig">{figs['fig23_corpus.svg']}</div>
<table><thead><tr><th>method</th><th>analogue beats false friend</th></tr></thead>
<tbody>{ret_rows}</tbody></table>
<div class="read warn"><b>The measure gets 2 of 3, and the claim was 3 of 3.</b> It is decisively
the best of the four — word overlap puts the false friend <i>first</i> on every query, which is
exactly the baseline this project exists to beat — but beating the baseline was never the claim.
The claim was that a structural analogue outranks something that merely shares vocabulary, and on
one motif in three it does not.</div>

<h3>Why, exactly — and it is a familiar culprit</h3>
<p>On the failing motif the analogue scores <b>1.8586</b> and the false friend <b>1.8608</b>. A
margin of <b>0.0022</b>. Both match all four relations perfectly; the entire difference is the
cost of the mapping — 15.75 bits against 13.58.</p>
<div class="read warn"><b>The analogue pays for two relation-type substitutions and the false
friend pays for one.</b> The analogue uses a different domain's vocabulary for its relations
(<code>RAISES</code>/<code>LOWERS</code> against <code>POS</code>/<code>NEG</code>) and is charged
for saying so.<br><br><b>That is the exact pathology that demoted the original correspondence
formula</b> — charging for asserting correspondence across vocabularies, which penalises precisely
the capability the theory exists to provide. It was fixed for <i>participant</i> labels, which are
never encoded at all. It was never fixed for <i>relation-type</i> labels, and nobody re-examined
that term. It survived twenty-four experiments and only became visible when the analogue and the
false friend were close enough for two bits to decide the answer.</div>
<p class="sub">A second contributor: the false friend collapsed to a single relation type, which
makes it cheaper to describe — the alphabet-size artifact this log first noticed as a curiosity
and has now seen three times.</p>
<div class="read"><b>Not patching it yet.</b> The fix is clear — encode relation types canonically,
as participant labels already are. But the corpus is now the development set, and a fix tuned
until this corpus passes is a fix fitted to three motifs. It needs a held-out corpus written
before the change lands. Publishing the failure and the diagnosis is the honest state; publishing
a same-day fix that makes the number go green would not be.</div>

<h2>Finding 23 — the fix, and the discipline that makes it mean something</h2>
<p>The previous finding diagnosed the shortfall precisely and stopped there, because the corpus
that produced the diagnosis could not also test the cure. The order this was done in is the whole
result:</p>
<ol>
<li>A <b>held-out corpus</b> written — three new motifs, structurally distinct from the
development set and from each other: mutual inhibition, threshold accumulation, substitution
under blockage.</li>
<li><b>Committed and frozen before the fix existed.</b></li>
<li>The fix implemented: charge for <i>specifying</i> the relation-type map, never for whether the
names happen to coincide — exactly as participant labels are already handled.</li>
<li>Regressions re-run: harness self-test, cross-generator transfer.</li>
<li>Both corpora scored, <b>once</b>.</li>
</ol>
<div class="fig">{figs['fig24_fix.svg']}</div>
<div class="read ok"><b>Six of six.</b> The analogue beats the false friend on every motif in both
corpora — including three the measure had never been exposed to, written before the change
existed. Regressions hold: the harness still catches 7/7 impostors, transfer is still 5/5 across
unseen topologies.</div>

<h3>The number that says the fix is real rather than tuned</h3>
<div class="read ok"><b>Paraphrase and analogue now score identically — 0.0000 apart, in all six
motifs across both corpora.</b> That is not a coincidence and it is not something a fitted patch
would produce. A paraphrase and a cross-domain analogue are <i>structurally the same thing wearing
different words</i>, so a measure that genuinely ignores vocabulary must return the same number for
both. It does, to four decimal places, every time.</div>

<h3>Which exposed a seventh wrong ground truth — mine</h3>
<div class="read warn">The corpus declared an ideal ordering of <code>P &gt; X &gt; W &gt; V &gt;
U</code> — asserting that a same-domain paraphrase should outrank a cross-domain analogue.
<b>That contradicts this project's entire thesis.</b> If structure is what counts and vocabulary
is not, two structurally identical documents must tie, and ranking one above the other is not
something a correct measure should do.<br><br>So the ground truth was wrong, not the measure. The
ideal is now stated as <b>tiers</b> — {{paraphrase, analogue}} tied, then false friend, then
generic, then unrelated — and d_A treats within-tier order as free.<br><br><b>Said plainly: I
noticed this from the data, which makes it post-hoc.</b> It is derivable from the thesis without
looking at any result, and it does not touch the headline claim — the analogue beat the false
friend before and after the correction. But the honest label is post-hoc, and this is the seventh
time in this log that a property was asserted where it should have been derived.</div>

<h3>What is still not right</h3>
<p>Only 1 of 3 motifs is <i>perfectly</i> ordered on each corpus. The unrelated control outranks
the generic connector and the false friend in some cases — the measure knows a false friend is
wrong but does not reliably know it is <i>more</i> wrong than an unrelated document. The critical
comparison is fixed; the full ranking is not.</p>
<div class="read"><b>Where this leaves A-01.</b> The measure now does the thing the project was
built to do, on data it had not seen, with the failure mode that has haunted it since the first
experiment finally removed from both places it lived. That is a real result and a narrow one:
eighteen hand-annotated documents, six motifs total, no automatic extraction, no natural text.
The next honest step is a corpus nobody involved in this wrote.</div>

<h2>Finding 24 — a corpus nobody here wrote, and the oldest risk arrives as a measurement</h2>
<p>Both previous corpora were written by the same party as the measure, so annotation bias was
untested and was named as the largest remaining doubt. This one was commissioned from a separate
system given only a format specification — no description of what was being tested, no mention of
how correspondence is computed, and an instruction to refuse if asked what it was for. Frozen
before it was run. The measure is unchanged.</p>
<div class="fig">{figs['fig25_independent.svg']}</div>
<div class="read ok"><b>The claim holds, 4 of 4.</b> The cross-domain analogue outranks the false
friend on every motif — on motifs, documents, annotations and judgements that nobody involved in
building the measure produced. And <b>paraphrase and analogue score identically on all four
again</b>, which is the vocabulary-blindness signature confirmed independently rather than on my
own writing.</div>

<h3 style="text-decoration:line-through;opacity:.55">And the generic document beats the analogue
on three of four</h3>
<div class="read warn" style="border-left-color:#dc2626"><b>RETRACTED — see Finding 25.</b> The
heading above is the original wording and is <b>wrong</b>. The vacuous document does not beat the
analogue; the two score <b>identically</b>, in the last bit, on all four motifs. The apparent win
was a sorting artifact. The reasoning below survives the correction unchanged — the generic is
isomorphic to the query, so an exact tie is the correct answer — but "beats" was noise on top of
it, and the wrong number sat on this page until it was checked.</div>
<div class="read warn"><b>It is structurally right to tie.</b> The generic item for one motif reads
"a growing deviation produces a stronger control signal, increasing corrective action and a
counteracting effect that reduces the deviation" — and its structure is a four-cycle with three
increases and one decrease closing the loop. <b>That is isomorphic to the query</b> — and so, on this
corpus, is the genuine cross-domain analogue. Both match perfectly, so both get the same
score.<br><br>The measure is not wrong. <b>A vacuous statement can have perfect structure.</b>
"Systems change, factors influence outcomes, feedback occurs" describes a feedback loop exactly as
accurately as any real feedback loop does — because it describes nothing else.</div>

<h3>Which is the project's very first logged risk, arriving as data</h3>
<div class="read"><b>Risk one, written before any code existed:</b> <i>a relational framework can
relate anything to anything if the criteria are loose enough — it produces striking, plausible,
well-visualised connections that are worthless, and it kills the project by succeeding.</i> The
defence sketched for it was a bridge measure that discounts genericness, so that vague concepts
connecting everything would be penalised for explaining nothing. <b>It was never built.</b>
Twenty-six experiments later, an independent annotator produced exactly the case it was for, and
the measure walked into it.<br><br><b>Genericness is not a structural property and cannot be
detected structurally.</b> No amount of work on the correspondence measure will fix this, because
the correspondence is real. It needs something outside the structural measure entirely — which is
what the unbuilt bridge measure was for, and the shape of it is now specified by an actual failure
rather than by anticipation.</div>
<div class="read ok"><b>What A-01 can and cannot claim now.</b> It can claim, on independent data,
that a structural analogue is preferred over something sharing the query's whole vocabulary with
different wiring — which is the capability the project exists to provide, and which every baseline
gets backwards. It cannot claim to produce a usable ranking, because a vacuous document that
happens to share the query's shape will sit near the top and nothing in the measure objects.</div>


<h2>Finding 25 — a retraction, and a fix that cannot work</h2>
<p>Two results. The retraction comes first because it is against a claim published on this page.</p>
<div class="fig">{figs['fig26_refutation.svg']}</div>

<h3>What was published, and what is true</h3>
<div class="read warn" style="border-left-color:#dc2626"><b>Retracted:</b> <i>"the vacuous document
beats the genuine analogue on 3 of 4 motifs."</i><br><br>
<b>True:</b> on all four motifs the paraphrase, the analogue and the vacuous document score
<b>identically</b> — 1.98975427279772754 against 1.98975427279772754 against 1.98975427279772754,
equal in the last bit rather than merely close. The ordering came from the sort breaking the tie on
a hash value that Python randomises on every run. Three runs gave three different orders. One of
them got written down as a finding.</div>
<div class="read"><b>Two faults, and the second is the one worth having.</b> The first is that the
tie-break was not reproducible — annoying, and fixable with a stable key. The second is that a
total order was imposed on tied items <b>at all</b>, and that is the real error: a stable tie-break
would have made the artifact <i>reproducible</i> rather than <i>correct</i>, and reproducibility
would have hidden it permanently. Rankings now return tied groups, printed
<code>{{P=V=X}} &gt; W &gt; U</code>, so the measure has to admit when it cannot separate two
things.</div>
<div class="read ok"><b>What survives, and it is the load-bearing claim.</b> The analogue is
strictly above the false friend on <b>10 of 10</b> motifs across all three corpora. That never
depended on a tie-break. And the vacuous document outranks the analogue on <b>0 of 10</b> — nowhere
in the project, not just nowhere in the corrected corpus.</div>
<div class="read ok"><b>The correction also improved agreement with the outside annotator.</b>
Scored against the independent author's own "most similar" judgement, the measure went from
<b>2 of 4 to 4 of 4</b> once ties are reported as ties. The bogus tie-break had been actively
suppressing agreement with the only external ground truth in the project.</div>

<h3>And the defence against the oldest risk is refuted</h3>
<p>The plan for the vacuous-document problem, sketched before any code existed, was to discount a
match by how well the document matches <i>everything</i> — a vague thing that connects to all
topics gets penalised for explaining nothing. It was finally built. It cannot work here, and the
reason is arithmetic rather than experimental.</p>
<div class="read warn" style="border-left-color:#dc2626"><b>PREMISE CORRECTED — see Finding 33.</b>
The paragraph below says the outside author wrote vacuous documents structurally identical to the
query. <b>They didn't — I annotated them into that state.</b> It holds 4 of 4 with the roles visible
and only 2 of 4 blind, and in one motif my annotation contains an edge no sentence states. The
mathematics below is untouched; the claim that authorship forced it is wrong.</div>
<div class="read warn"><b>The vacuous documents are isomorphic to the query in the sighted
annotation.</b>
Confirmed by exhaustive search over every possible relabelling. And isomorphic structures are
indistinguishable to <i>any</i> measure of structure alone, so the genericness of the analogue and
the genericness of the vacuous document are equal <b>exactly</b>: gap 0.00e+00 on every motif. The
discount subtracts the same number from both. <b>No strength of it, and no cleverer structural
statistic, can separate them</b> — where they genuinely are identical. <i>(Finding 33 narrows this:
once annotation stops forcing the match, the discount can act on one motif in four. It still fails to
help on any, so the conclusion holds and the reasoning was too strong.)</i></div>
<div class="read"><b>The distinction is not present in what is being measured.</b> Whether a
sentence is a real cross-domain analogue or a vacuous phrase of the same shape is not a fact about
its relational structure. This is not a measurement failure that better technique would fix — it is
an absence in the representation. Recorded as refuted rather than "needs tuning", because tuning is
exactly what the arithmetic rules out.</div>
<div class="read ok"><b>What a negative result buys.</b> The oldest risk in the project now stands
undefended, which is worse than it looked yesterday. But the requirement on any successor is now
stated precisely instead of hopefully: <b>it must use information from outside the relational
structure</b>, because the structure provably does not contain it. The candidate is whether the
participants denote anything at all — a property of the <i>nodes</i> rather than the relations, and
so genuinely outside the measure. Every hour that would have gone into tuning a structural discount
is saved.</div>
<div class="read"><b>Found in passing, and logged rather than quietly fixed:</b> in one motif of the
project's first corpus, the "unrelated" control is isomorphic to its own query — so that cell never
tested what it claimed to. Eighth instance of the same failure, and the eighth time the wrong
ground truth was the author's own. It changes no published claim; the analogue-over-false-friend
result holds in that motif regardless.</div>


<h2>Finding 26 — the same process, written down differently</h2>
<p>Every invariance shown so far is about <i>vocabulary</i> — what the participants are called — and
<i>labels</i> — which node is which. Nobody had asked whether the measure survives a change of
<b>representation</b>: the same process written down a different but equally legitimate way. A
mediator node instead of a direct link. The passive voice. A relation turned into a node, which is
how the same fact gets written whenever the formalism has no typed edges.</p>
<div class="fig">{figs['fig27_reencoding.svg']}</div>
<div class="read warn" style="border-left-color:#dc2626"><b>It fails, and the two ranges overlap
completely.</b> There is no threshold that separates "wrote it differently" from "said something
different." Writing <i>B is increased by A</i> instead of <i>A increases B</i> costs more than
deleting a relation from the loop outright.</div>

<h3>The obvious objection, and why it doesn't hold</h3>
<p>Deleting a relation keeps the structure small; subdividing every edge doubles it, and the code
charges for size. So the gap could be a size artifact rather than anything about encoding. Removing
size from the comparison — subdividing <i>both</i> sides, so the correct version and a corrupted
version are the same size:</p>
<div class="read warn" style="border-left-color:#dc2626"><b>The measure returns the identical number
for both, on six of six.</b> Not close — identical. And an exhaustive search over every possible
relabelling confirms the two structures are <b>not</b> isomorphic, so an exact tie is not the right
answer here. This is blindness, not bias.</div>

<h3>Why — and it isn't the reason I first wrote down</h3>
<p>My first explanation was that subdivision means none of the original relations land. Checking it:
<b>three of four land.</b> The real mechanism is visible in the mapping the search actually returns,
which isn't even the natural alignment — it's a shifted one that happens to catch three half-edges.</p>
<div class="read"><b>The measure maximises over ways of lining up two structures.</b> Subdivision
roughly doubles the node count, so the search gets more places to try — enough that it finds
<i>some</i> three-of-four alignment in almost any subdivided structure, whether or not that structure
was corrupted first. <b>Maximising over a search space that grows with the target destroys
discrimination.</b> The code already carried a warning about this for partial alignments; the same
effect arrives through complete ones whenever the target is bigger.</div>

<h3>What it costs the main result</h3>
<div class="read warn"><b>The load-bearing claim is re-scoped, not withdrawn.</b> "Analogue beats
false friend" holds 6/6 under the two invariances already known, 5/6 with a mediator, <b>3/6 in the
passive voice</b> and <b>2/6 under subdivision</b>. The correct statement is now: the analogue
outranks the false friend on 10/10 motifs <b>within a fixed representation convention</b> — and
across equivalent re-encodings of those same processes it holds on two to six of six, depending on
how you write them down.</div>
<div class="read"><b>Padding is a related and live weakness.</b> If extra nodes buy the search
freedom, junk should buy score. It does: nonsense nodes added to a false friend raise its score on
two of three motifs. It flips no ranking — padding costs as well as pays — so it lifts a weak
document without promoting it past a strong one. Logged as a live vulnerability rather than a fired
one, because the mechanism is confirmed even though the exploit isn't.</div>
<div class="read ok"><b>What a negative result buys, again.</b> The defect is in the <i>space of
alignments</i>, not in the criterion or the code. The search can map a participant to a participant
but cannot map one relation onto a <i>chain</i> of relations, so any re-encoding that stretches a
link into a path is outside its reach by construction. Two routes out: put structures in a canonical
form first, contracting chains so subdivision becomes a no-op; or let a relation match a path,
priced by length. Taking the first — it's the smaller change, and the second widens exactly the
search space that caused this.</div>


<h2>Finding 27 — declare the equivalence, then measure through it</h2>
<p>The previous finding left the measure unable to tell "written differently" from "says something
different." The problem has a name in graph theory — <b>homeomorphism</b>, equivalence under
subdividing an edge and suppressing the vertex it created — and two standard routes. Either let one
relation match a whole <i>path</i>, or normalise the extra vertices away before comparing.</p>
<div class="read"><b>Took the second, for the reason the previous finding established.</b> What broke
discrimination was giving the search more freedom, so answering it by giving the search still more
freedom would be treating the symptom with more of the cause. An invariance ought to be part of what
you are measuring, not something the search is expected to stumble on.</div>
<div class="fig">{figs['fig28_canonical.svg']}</div>

<h3>Two mistakes of mine, found on the way there</h3>
<div class="read warn"><b>The previous finding's subdivision was corrupting content.</b> Splitting
"A <i>decreases</i> B" into "A decreases M, M decreases B" says A <b>increases</b> B — two sign flips
cancel. Every negative relation in what I had labelled the content-preserving group was being quietly
altered. The canonicaliser caught it by disagreeing with itself. Re-ran the whole thing: the verdict
is unchanged and one number moved. Ninth time the wrong ground truth has been mine.<br><br>
<b>And the first run of this experiment reported a known-good invariance as broken.</b> That is an
alarm about the harness, not a discovery, so I chased it rather than writing it up — I had protected
the wrong set of vertices.</div>

<h3>A canonical form is only worth having if it's actually canonical</h3>
<p>If applying the legal rewrites in a different order gave a different answer, "canonical" would
mean "whatever the loop happened to do first" and every number downstream would be arbitrary — the
same defect as the sorting artifact two findings ago. So it was tested rather than assumed:
<b>terminates 6/6, idempotent 6/6, and confluent 6/6 across 24 random rewrite orders each</b>,
recovering the original structure exactly every time.</p>
<div class="read"><b>Suppression is guarded, not greedy.</b> "Contract every same-typed chain" was my
first plan and it is too broad — a vertex in the middle of something is not automatically meaningless.
A vertex is removed only when it has exactly one relation in and one out, creates no self-loop or
duplicate, and <b>the vocabulary declares what its two relations compose to</b>. Composition across
different vocabularies is deliberately left undefined, so it blocks the rewrite instead of inventing
a meaning.</div>

<h3>It works, exactly</h3>
<div class="read ok"><b>Subdivision and mediation now cost nothing at all</b> — the same score as
comparing a structure with itself, with the original recovered exactly on 6 of 6. Everything that
changes the process stays far below. Clean separation, within the class the rewrite declares.</div>
<div class="read ok"><b>And it costs the main result nothing.</b> Analogue beats false friend 3/3,
3/3 and 4/4 after canonicalisation — including on <i>subdivided</i> documents, the case that scored
2 of 6 before. The falsification condition I wrote down in advance was "if the fix restores
invariance but costs the capability, it is refuted rather than tuned." It didn't.</div>

<h3>What is still broken, said plainly</h3>
<div class="read warn"><b>Writing a relation backwards, and turning a relation into a node, are not
fixed.</b> Both are perfectly legitimate ways to write the same thing, both still score below the
best content-changing transform, and the rewrite declares nothing for either. They aren't
subdivision. Counting them as failures of this fix would judge it against a claim it never made;
counting them as passes would hide two known gaps.</div>
<div class="read warn"><b>And the equivalence has to be declared — it cannot be computed.</b> Whether
a vertex is a bookkeeping artifact or a real participant is not something the structure knows. A
plain feedback loop has exactly one relation in and one out at every vertex. Measured rather than
argued: suppressing blindly, with nothing declared, <b>damages 5 of the 6 test structures</b> — one
of them from five vertices down to two.<br><br>Which is the same shape as the vacuous-document
result: the structure does not contain the distinction, so something outside it has to supply one.
That is now twice this project has hit the same wall from different directions, and it is starting
to look like the actual subject matter rather than a series of accidents.</div>


<h2>Finding 28 — a benchmark nobody here touched, and it moves the problem</h2>
<p>Every corpus so far had this project supplying the annotations, and usually the ground truth too.
This one is published, licensed, and made by other people: 254 items in exactly this design — a
short narrative, a genuine cross-domain analogue, and a deliberately surface-similar distractor —
in its hardest cell. Twenty items scored. <b>Forty more left sealed and unannotated</b>, because a
benchmark spent all at once cannot be spent twice.</p>
<div class="read"><b>The blind is stronger than hiding the answers.</b> Hiding which one is correct
is the obvious control and it isn't enough — the real hazard is that annotating a candidate while
looking at the query bends it toward a match, which is not cheating, just the pull of having the
target in view. So every passage was annotated <i>alone</i>, with its role hidden: I could not tell
query from analogue from distractor while working. The answers were unreadable until the annotations
were committed and hashed, and the code refuses to reveal them if the annotations change afterwards.
Blocked by the program, not by my intention to behave.</div>
<div class="fig">{figs['fig29_arn.svg']}</div>

<h3>No signal</h3>
<div class="read warn" style="border-left-color:#dc2626"><b>The measure abstains on 9 of the 20
items</b> — exact ties, most of them at the floor where one structure says nothing at all about
another. Where it does commit, it gets 4 of 11. Both honest readings sit on chance.<br><br>
There is a third reading — count the abstentions as wrong and you get 20%, which is
<i>significant</i>. I am not using that as the headline, because it would claim the measure is
reliably <b>anti</b>-correlated with the truth and the data does not support that. A tie is an
abstention, not a wrong answer.</div>

<h3>But the interesting part is whose failure it is</h3>
<p>I wrote down the worry before running it: <i>I am the annotator, and the annotation is where this
could go wrong.</i> There's a clean way to check. Throw away the scoring entirely and just count how
many of the query's relations can be made to land in each candidate. If my annotation captured the
analogy at all, the human-judged right answer should win on raw overlap even if the score fails to
reward it.</p>
<div class="read warn" style="border-left-color:#dc2626"><b>3 favour the correct answer. 13 show no
difference. 4 favour the distractor.</b> Chance. The distinction was never in the annotation, so the
measure had nothing to work with. <b>This experiment measured the annotator, not the measure</b> —
and calling it a failure of the correspondence measure would be blaming the wrong component.</div>
<div class="read"><b>One number explains the whole thing.</b> On this project's own corpora, a
candidate shares <b>81.7%</b> of its relational shape with the query. On real analogies annotated
blind, <b>42.8%</b>. It isn't a size effect — the structures are the same size. The corpora that
produced a 10-out-of-10 record contained candidates that were near structural copies of their
queries. Real analogies, annotated without knowing which is which, are not.</div>

<h3>Where this leaves the strongest claim</h3>
<div class="read ok"><b>Not withdrawn, and not weakened as stated.</b> On structures with high shared
shape the analogue does outrank the false friend, ten times out of ten, including on data written by
someone else. What this adds is where that claim stops:<br><br>
<b>The measure works on relational structures. Getting from text to a relational structure is
unsolved, is doing more of the work than the measure is, and is where the difficulty actually
lives.</b></div>

<h3>And a retroactive worry I'd rather log than deflect</h3>
<div class="read warn"><b>Every corpus in this project was annotated by someone who knew each
document's role.</b> The documents were written to be a paraphrase, an analogue, a false friend — and
then turned into structures by a person who knew which was which. An earlier finding tested whether
my <i>ranking</i> was biased and cleared it. It never tested whether the <b>structural annotation
itself encodes the role</b>. If it does, the measure has been reading back what annotation put in.
That wouldn't make the earlier results fake — the structures are real and the arithmetic is right —
but it would make them a measure of annotation fidelity rather than analogy detection.<br><br>
I don't know which it is, and this experiment can't settle it. The decisive test is cheap: take a
corpus already in hand, strip the labels, re-annotate it blind, and see whether ten out of ten
survives. <b>That control costs an afternoon and tests something more fundamental than the
independent corpus did — and I built the expensive one first, because it was the one I had thought
of.</b> Running it next, before spending the forty sealed items.</div>


<h2>Finding 29 — the wall has a name, and it can be checked before you build</h2>
<p>Twice now this project has discovered, by failing, that a distinction it wanted simply wasn't in
its representation: the vacuous document that's structurally identical to a real analogue, and the
vertex that might be a real participant or might be bookkeeping. Both were written up as surprises.
They are one thing, and the condition is a single line:</p>
<div class="read"><b>A distinction is recoverable from a representation only if it is the same for
every pair of items the representation treats as identical.</b> So the test is: find two cases that
need <i>different</i> answers and whose structures are <i>the same</i>. One such pair — a
<b>witness pair</b> — proves that no measure using only that representation can ever work. Not
"hasn't yet". Cannot. No cleverer score, no better algorithm, no post-processing.<br><br>
Database theory has been living with the useful half of this for decades under the name
<b>genericity</b>: a query must give the same answer for structurally identical inputs, so it can't
depend on arbitrary internal identifiers. That's normally a virtue. The cost is exactly what bit us.</div>
<div class="fig">{figs['fig30_identifiability.svg']}</div>

<h3>Three things I had wrong</h3>
<div class="read warn"><b>I'd been saying similarity isn't definable on structures-up-to-isomorphism.
That's backwards.</b> Every purely structural similarity is naturally defined there — that's what
makes it structural. What isn't definable is a distinction that <i>varies between</i> two things the
structure treats as identical. So the fix is not to abandon the abstraction and keep raw encodings,
which would drag node names and other irrelevant junk back in. The fix is to put more into the
represented object — roles, referents, specificity, provenance — and abstract <i>that</i>.<br><br>
<b>And this isn't the "ugly duckling" result</b>, which I'd assumed it might be. That one says
similarity needs you to decide which features matter, because counting all of them equally makes
every pair equally similar. It's about choosing among available distinctions. Ours is about a
distinction not being available. Interestingly, the project's <i>other</i> recurring result — that
significance only exists once you name an outcome — is the ugly-duckling-shaped one. Two different
obstacles that I'd been treating as one.</div>

<h3>Turned into a test, it immediately found three more dead ends</h3>
<p>The audit is only worth having if it predicts a failure nobody has paid for. It found three, and
one of them settles a question that was queued for later: a difference between a reinforcing and a
regulating system that comes from <i>timing</i> is invisible by construction, because there is
nowhere in the representation to record what happened first. So a temporal extension is necessary
rather than optional — established without building anything.</p>
<div class="read"><b>The last row of the table is a control</b>, and it comes back
<i>identifiable</i>. That matters: it's how you know the audit is capable of returning both answers.
A test that can only give one result isn't a test — a rule this project learned the hard way and now
applies to its own tests.</div>

<h3>And it found something embarrassing in the very first experiment</h3>
<div class="read warn" style="border-left-color:#dc2626"><b>The measure never reads relation
strength.</b> Structures carry a weight on every relation; the comparison throws it away. Two
structures whose coupling differs by a factor of a thousand score identically — the same number you
get comparing a structure with itself. The <i>old</i> measure, the one that was demoted, did read
weights. The replacement silently stopped, and nothing noticed because every weight in every corpus
is 1.<br><br>
<b>Worse: the first experiment's invariance battery has published "invariant to unit conversion"
ever since, as evidence the measure ignores arbitrary scaling.</b> It cannot fail that test. It never
looks at the quantity being changed. That's blindness reported as a virtue, sitting inside the
control set built to catch exactly this kind of thing, for thirty experiments. The row is now marked
vacuous rather than quietly deleted.</div>

<h3>The rule, adopted</h3>
<div class="read ok"><b>Before building a measure for a distinction, try to construct a witness
pair.</b> If two items that need different answers have equivalent representations, stop — name the
missing channel or narrow the claim, and don't write the measure. It works in one direction only:
finding a pair is a proof, failing to find one is not. Two experiments were spent learning this the
expensive way; the cheap version took an afternoon and found three more.</div>


<h2>Finding 30 — how much did knowing the answer help?</h2>
<p>The previous finding raised a worry I couldn't dismiss: every corpus in this project was turned
into structures by someone who <i>knew</i> which document was the paraphrase, which was the genuine
analogue, and which was the decoy. An earlier test checked that my <i>ranking</i> wasn't biased. None
of them checked whether the structures themselves quietly encoded the answer.</p>
<div class="read"><b>This is the control that should have been built before the independent corpus,
not after it.</b> It's cheaper and it tests something more fundamental. I built the expensive one
first because it was the one I'd thought of.</div>

<h3>The problem with running it myself</h3>
<div class="read warn"><b>I've already seen these documents.</b> Hiding the labels stops me knowing
which is which; it doesn't erase memory. So this isn't a clean blind test and I'm not reporting it as
one.<br><br>Which makes <b>divergence</b> the thing that decides whether the result means anything,
and it has to be measured <i>before</i> looking at the score. If the blind annotations came out
nearly identical to the sighted ones, that would be uninformative — equally consistent with "my
annotation is reproducible" and with "I remembered." An identical result would have been a null here,
not a confirmation. Written down before the answers were unsealed.<br><br>
<b>They diverged: 0 of 24 identical, mean shape overlap 0.40.</b> Memory did not reproduce the
earlier pass, so the comparison is readable.</div>
<div class="fig">{figs['fig31_blind.svg']}</div>

<h3>The answer: the ordering survives, the magnitude doesn't</h3>
<div class="read warn"><b>Knowing a document was the paraphrase or the analogue, I annotated it into
a perfect match with the query.</b> Both score 100% sighted. Blind, both fall to 65%. Overall the
labels inflate correspondence by <b>1.34×</b> — same documents, only the annotator's knowledge
changed. That is the worry, made concrete instead of argued about.</div>
<div class="read ok"><b>But the gap that matters holds up.</b> Blind, the analogue still sits well
clear of the decoy — 65% against 35% — and the headline claim survives on three motifs of four
instead of four of four.<br><br><b>So the record was flattered, not fabricated.</b> The structures
are real and the ordering is real; the numbers attached to it were generous.</div>
<div class="read"><b>What changes:</b> corpus results should be quoted at the blind rate from now on.
The sighted figures are an upper bound produced by an annotator who knew the answer, and quoting them
as though they were neutral measurements would be the same error in a new place.</div>

<h3>A defect in my own prediction, worth more than the result</h3>
<div class="read warn"><b>I predeclared two outcomes — survives, or collapses — and got neither.</b>
Three out of four is graded, and my prediction space had no bucket for it. The automated verdict
initially rounded it to "the worry is confirmed," which overstates: the gap survived, and that's the
part the claim depends on.<br><br>Rounding a graded result to the nearest predeclared label is
exactly how a mis-specified prediction turns into a false confirmation. The mis-specification is
recorded rather than tidied away, and the verdict now has a bucket for "partly."</div>
<div class="read"><b>One outright failure worth chasing.</b> The <i>diversity</i> motif inverts
completely under blind annotation — the unrelated and generic documents come out on top. One motif in
four is thin evidence, but it's the only clean failure, and it has two possible explanations that
need separating: my blind annotation of it is poor, or that motif's analogue was being carried
entirely by sighted annotation and never had structure of its own.</div>


<h2>Finding 31 — the same test on the other two corpora, and two defects in the corpora themselves</h2>
<p>One corpus at four motifs is thin evidence for restating a claim, so the blind protocol was
repeated on the other two — pooled and shuffled together, so I couldn't tell which corpus a
description came from either.</p>

<h3>Found while building it, and worth more than the scores</h3>
<div class="read warn" style="border-left-color:#dc2626"><b>Six of the thirty-six documents announce
their role in their own text.</b> "Same words, opposite wiring:". "Same words, no reset:". "Same
words, cooperative wiring:". And all six are the <b>decoys</b> — the exact comparison being
tested.<br><br>So the worry reaches a stage further back than I'd checked. Not just an annotator who
knew the roles: <b>corpus text that states them</b>. Any annotation from these was never blind for
the documents that matter most. I stripped the prefixes before annotating and I'm reporting it
rather than quietly cleaning it up.</div>
<div class="fig">{figs['fig32_blind_all.svg']}</div>

<h3>The result, and why I can't cleanly interpret it</h3>
<div class="read warn"><b>Blind, the claim holds 6 times out of 10 across all three corpora — against
10 out of 10 when annotated by someone who knew the answers.</b> The annotations genuinely diverged
(1 of 36 identical to the sighted pass), so that isn't memory reproducing the old work.</div>
<div class="read warn" style="border-left-color:#dc2626"><b>But there's a confound I have to report,
because it blocks the obvious conclusion.</b> On two of the corpora my blind pass wrote down roughly
<b>half</b> as many relations as the sighted pass did, from the same text. Fewer relations means less
to match, whether or not I knew the roles. Only the independent corpus had comparable detail in both
passes — and that's the one with the smallest drop.<br><br>So the direction is confirmed: knowing the
answer helps. <b>The size is not measured</b>, and the cleanest number in the project remains the
1.34× from the corpus where the detail happened to match.</div>

<h3>Except the confound points somewhere worse than it excuses</h3>
<div class="read warn" style="border-left-color:#dc2626">Those documents average <b>nine words</b>.
The sighted annotation gives each of them <b>four relations</b>. A nine-word sentence doesn't support
four typed relations — and the sentence <i>is</i> the whole document; there's no longer text I was
working from.<br><br><b>So those structures contain organisation that isn't in the documents.</b>
Whether that came from knowing the role or from ordinary over-elaboration, it means two of the three
corpora were never testing whether structure can be read out of text. They were testing whether the
measure can score structures I supplied.</div>
<div class="read"><b>What I genuinely can't separate:</b> "I annotated richly because I knew the
role" versus "I annotate more richly when I'm not working through thirty-six terse one-liners at
speed." Both are effects of the annotator, and this run doesn't distinguish them. My blind pass may
simply have been less thorough. Saying so isn't hedging — it's the actual state of the evidence, and
the next control has to fix the granularity before the size of this can be known.</div>

<h3>A pattern in my own predictions</h3>
<div class="read"><b>Three times today a predeclared rule had no bucket for the result that
arrived</b>, and each time the automated verdict overstated: counting abstentions as wrong implied
the measure was reliably backwards; a binary survives-or-collapses met a graded three-out-of-four;
and a "below half means it fires" rule met a number that was confounded.<br><br>Predeclaring a
threshold doesn't make the threshold right — it makes it <i>fixed</i>, which only helps if the space
of possible outcomes was mapped properly first. A result that lands outside every declared bucket is
evidence the buckets were wrong, not a result to be rounded to the nearest one.</div>


<h2>Finding 32 — the missing channel, and a control that can fail again</h2>
<p>The previous finding turned up something awkward: the measure never looked at how <i>strong</i> a
relation was. Every structure carries a weight on every link, and the comparison threw them all away
— so a thousandfold difference in coupling was invisible. Worse, the very first experiment had been
publishing "invariant to unit conversion" ever since, on the strength of that blindness.</p>

<h3>First, a correction to the finding that caught it</h3>
<div class="read warn"><b>My witness pair for that was wrong.</b> I'd used two structures whose
weights were 0.01, 0.01 against 10.0, 10.0 — but those differ only by a single global factor, which
is a change of units, and a change of units is exactly what the measure is <i>supposed</i> to ignore.
So the pair demonstrated a property it should have, not a defect. The verdict came out right for the
wrong reason, because at that point weights were being ignored entirely.<br><br>A proper test needs
the weights to differ <i>relative to each other</i>: one link dominant versus the other link
dominant, same shape, not related by any rescaling.</div>

<h3>The fix, and why it's built this way</h3>
<div class="read"><b>Weights are recorded on a log scale, measured against their own average.</b>
Multiply every weight by the same number and each one shifts by the same amount, so their positions
relative to the average don't move at all — <b>a change of units is invariant because of how the
quantity is defined, not because the measure failed to look.</b> That's the rule the project arrived
at two findings ago: build the invariance into the definition of what's being measured rather than
hoping the search stumbles on it.<br><br>Log scale because coupling is multiplicative — going from
0.1 to 1 is the same size of step as going from 1 to 10, and a linear scale would disagree.</div>
<div class="read ok"><b>It works in both directions.</b> Two structures with the same shape but
opposite coupling now score differently. The same structure with every weight multiplied by a
thousand scores <i>identically</i>, to the last digit.</div>

<h3>The check I wrote down in advance</h3>
<p>Every weight in every corpus is 1. So the prediction was: <b>nothing should move</b>, and if
anything did, that would mean the new encoding was wrong rather than the old results. Re-ran every
experiment that carries a claim — the retrieval result, the held-out and independent corpora, the
re-encoding findings, the blind re-annotations.</p>
<div class="read ok"><b>Nothing moved.</b> Not one claim-bearing number. The channel is inert where
weights are uniform and active where they aren't, which is exactly the contract.</div>

<h3>The control is a control again — and it now checks itself</h3>
<div class="read ok">The rescaling test still passes, and it can now <b>fail</b>: perturbing a single
weight moves the answer by four bits.<br><br>Rather than just flipping the "this test is vacuous"
note I'd added, the file now <b>measures</b> it — on every run it perturbs the property the control
holds fixed and requires the measure to notice. The old note would have gone stale the moment the
channel was built, exactly as the thing it replaced did. A control that cannot fail is not a control,
and the file now asserts that about itself instead of relying on anyone remembering.</div>

<h3>And the audit had the very bug it was built to find</h3>
<div class="read warn"><b>With the channel working, the audit still insisted relative coupling was
impossible to detect</b> — while the measure was visibly detecting it. Its notion of "these two
structures are the same" also ignored weights, because it predated the change.<br><br>So a tool that
tests what a representation can express had gone out of date with the representation, and would have
kept certifying impossibility for a distinction the project had just acquired. Same failure as the
vacuous control, one level up. Fixed, and the audit re-run: magnitude moves from impossible to
available, and four distinctions remain genuinely outside.</div>
<div class="read"><b>Worth being plain about the limit:</b> no corpus in this project uses a weight
other than 1, so the channel has never been exercised on real data. It's a capability, not a result,
and shouldn't be described as more than that until there's a corpus where coupling strength actually
carries information.</div>


<h2>Finding 33 — the one motif that inverted, and the edge that wasn't there</h2>
<p>The blind re-annotation left exactly one clean failure: a motif where hiding the roles flipped the
result completely, with the vacuous and unrelated documents beating everything. Two possible
explanations were on the table — my blind annotation of it was simply poor, or its genuine analogue
had been carried entirely by the sighted pass. It's the second, and chasing it turned up a mistake in
something published two findings earlier.</p>

<h3>What happened</h3>
<div class="read"><b>Annotated with the roles visible, every document in that motif has exactly five
relations.</b> Annotated blind, the query has five and the analogue has four — so the analogue drops
to the floor, the value meaning "this tells you nothing about that", and the vacuous document's
partial chain wins by default.<br><br>Not mysterious. The sighted pass had given every candidate the
query's own relation count.</div>

<h3>And it's systematic</h3>
<div class="read warn" style="border-left-color:#dc2626">Checking all four motifs on the two most
obvious structural properties — how many relations, and whether the loop closes — <b>the vacuous
document matches its query exactly on both, four times out of four.</b> That is not what independent
faithful annotation produces.</div>
<div class="read warn" style="border-left-color:#dc2626"><b>And in one case the extra structure can
be pointed at directly.</b> The vacuous document reads: <i>"A system with more diversity may offer
better options, improve outcomes, attract participants and receive resources."</i> That's a chain.
<b>It never says resources increase diversity.</b><br><br>My annotation of it contains exactly that
relation — and it's the one that closes the loop and makes the vacuous document structurally
identical to the query. <b>I added an edge the text doesn't state.</b></div>

<h3>Which corrects something published earlier</h3>
<p>Two findings ago I reported that the outside author — never told what a vague distractor was for —
had written vacuous documents that were structurally identical to the query, and used that to show a
proposed fix could never work.</p>
<div class="read warn" style="border-left-color:#dc2626"><b>The author didn't do that. I did.</b>
Measured: the vacuous document is structurally identical to the query in <b>four of four</b> motifs
when annotated with the roles visible, and <b>two of four</b> when annotated blind.</div>
<div class="read ok"><b>What survives: the mathematics.</b> If two things really are structurally
identical, no measure that reads only structure can tell them apart. That's a theorem and it's
untouched — it's also the general principle the next finding builds on.</div>
<div class="read warn"><b>What doesn't: the strength of the refutation.</b> I said the fix could
<i>never</i> act, by arithmetic. The truth is narrower — once annotation stops forcing the two
structures to match, the discount <i>can</i> act on one motif in four. It just doesn't help: it
demotes the vacuous document below the real analogue in zero of four, and on the motif where it acts
it makes matters worse. So the fix stays refuted, on weaker grounds than I published.</div>

<h3>And the headline is halved, not deleted</h3>
<div class="read"><i>"A vacuous statement can have perfect structure, because it describes nothing
else."</i> That's still real — it holds in two of the four motifs when annotated blind. But it was
published at four of four, and <b>half of it was mine</b>.<br><br>This is the annotation problem
caught in the act, at the resolution of a single missing edge rather than a statistical average. And
it explains the shape of everything else: if annotating with the answer visible reliably hands each
candidate the query's own relation count and loop topology, then the measure is being given the
answer inside its input — and the total absence of signal when a genuinely external benchmark was
annotated blind is what that looks like once the help is withdrawn.</div>


<h2>Finding 34 — a control that didn't work, and the check I should have run first</h2>
<p>Two results here. The control I built failed, and while writing that up I ran a test that should
have run two findings ago — and it changes how the whole record reads.</p>

<h3>Part one: the control failed</h3>
<p>Every comparison so far has mixed up two things — whether I knew each document's role, and how many
relations I felt like writing down. A program removes both: it can't know the roles, and it produces
identical output every time. So I wrote a deterministic extractor: split each sentence into clauses,
look for a verb from a fixed list, take what's before it as source and after it as target.</p>
<div class="read"><b>I wrote down in advance that this test only works in one direction.</b> If the
result survived, that would mean something — a process that can't know which document is which still
picks the right one. If it failed, it would be ambiguous between "the corpus was inflated" and "the
extractor is too stupid to read these sentences."<br><br>It failed, so it's ambiguous. And the
granularity comparison got <b>no data at all</b>: across sixty documents, the program and I never once
produced the same number of relations. It manages 1.5 relations per sentence where I write 4.2, and
it couldn't parse two of the ten queries at all.<br><br><b>So the control I built can't answer the
question I built it for.</b> That's a failure of my method, not a finding about the corpus.</div>

<h3>Part two: the test I should have run two findings ago</h3>
<p>I've been reporting blind results as "degraded but present" — three out of four, then six out of
ten. I never asked whether those are distinguishable from chance. For a straight choice between two
candidates, <b>chance is fifty percent</b>.</p>
<div class="read warn" style="border-left-color:#dc2626">
<b>sighted &nbsp;&nbsp;10/10 &nbsp; p = 0.002 &nbsp; significant</b><br>
blind &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6/10 &nbsp; p = 0.754 &nbsp; not significant<br>
mechanical &nbsp;5/8 &nbsp;&nbsp; p = 0.727 &nbsp; not significant<br><br>
<b>The only annotation mode that produces a significant result is the one where the annotator knew
the answers.</b></div>
<div class="read"><b>What that does and doesn't license.</b> It does <i>not</i> prove the corpus is
inflated — ten motifs is a small sample, and a real effect could simply be too small to detect.
Absence of significance isn't evidence of absence.<br><br>What it does mean is this: <b>the project
has no statistically significant evidence that the measure ranks genuine analogues above decoys under
blind annotation.</b> Every significant result it holds rests on annotation done by someone who knew
which document was which. That's a harder statement than "the ordering survives but the magnitude
doesn't", and it replaces it.</div>
<div class="read warn"><b>Why I missed it.</b> Two findings earlier, on an outside benchmark, I ran
exactly this test and used it correctly — I refused to headline a significant-looking number I didn't
trust. Then on the project's own corpora I reported raw fractions with no test at all, because six out
of ten <i>looks</i> like a weakened version of ten out of ten rather than like noise. That resemblance
is precisely when the test matters most.</div>
<div class="read ok"><b>What changes.</b> The blind figure can't be quoted as a measurement — it's a
null result at this sample size. The sighted result stands as significant and is exactly the one the
annotation worry says to distrust. And before running another blind test, the right move is to work
out how many motifs would be needed to detect the effect actually being claimed, and build to that
number — because at ten, the design can only ever confirm, never measure.</div>


<h2>Finding 35 — the evidence wasn't weak, the summary was</h2>
<p>The previous finding established that our blind results can't be told apart from chance. Before
building a bigger corpus, the obvious question: how big would it have to be?</p>

<h3>Ten test cases can see almost nothing</h3>
<div class="read warn"><b>Nothing below nine out of ten reaches statistical significance.</b> The
design can confirm a near-perfect measure and measure nothing else.<br><br>
A measure that genuinely got three out of four right would be <b>missed three times in four</b>. We
have been running a test that mostly cannot find what it's looking for.</div>
<div class="read"><b>And our own result is even less informative than "not significant" suggests.</b>
Six out of ten puts the true ability somewhere between <b>26% and 88%</b>. That range contains pure
chance and it contains a strong effect. The experiment simply didn't discriminate between them.</div>
<div class="read warn">To settle it with a yes/no test at the rate we actually observed would take
<b>199 test cases</b>. We have ten.</div>

<h3>Then the useful part</h3>
<p>The test throws away nearly all of its own information. "Did the right answer win?" is a single
bit per test case — squeezed out of a continuous number, the <i>margin</i> by which it won or lost,
which the corpus already contains and which gets discarded at the moment of reporting.</p>
<div class="read ok"><b>Testing the margins instead needs about twelve test cases, against 199 for
the yes/no version — on exactly the same data.</b> We have ten. A question that looked like it needed
a corpus twenty times bigger may need one or two more cases, tested properly.</div>
<div class="read"><b>Caveats, because that number is tempting.</b> The effect size comes from the same
ten observations you'd plan the study around, and pilot estimates are biased upward — so twelve is a
floor, not a forecast. Three of the ten margins are exactly zero. And the equivalent figure on the
<i>sighted</i> annotations is far more flattering, which is precisely why it isn't quoted anywhere:
that's the data already shown to be inflated.</div>

<h3>The uncomfortable bit</h3>
<div class="read warn"><b>This project has a standing principle that collapsing something to a single
number hides structure and can reverse a ranking.</b> It has enforced that rigorously on the measure
for thirty-seven experiments — refusing to produce one score, insisting on profiles, proving that no
scalar suffices.<br><br>And its own evaluation was reducing a continuous result to one bit per test
case, and then reporting that the evidence was weak.<br><br><b>The evidence wasn't weak. The summary
was.</b> Whatever discipline you hold the thing you're studying to, hold the ruler to it as well.</div>

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
<div class="q"><b>Partial observation costs you in proportion to how purely synergistic the
structure is.</b> Pure synergy is erased completely at any arity and no amount of data recovers
it — an identifiability limit, not a power limit. Everything with lower-order leakage degrades
smoothly and keeps roughly half. That is the corrected form of a claim this log made one finding
earlier and over-stated; the correction is left visible above rather than edited away. It still
means an absent higher-order result is uninformative — the project's own principle that omission
is never a claim of nonexistence, arriving as a measurement.</div>
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
<div class="q"><b>The evidence was not weak — the summary was.</b> Ten test cases can only detect a
near-perfect measure, and our six-out-of-ten spans everything from chance to a strong effect. But the
yes/no test discards the margin by which each comparison is won, and on the same blind data those
margins need about twelve cases where the yes/no version needs one hundred and ninety-nine. The
project spent thirty-seven experiments insisting that a single number hides structure, while its own
evaluation reduced a continuous result to one bit.</div>
<div class="q"><b>The only significant result in the project is the one produced by an annotator who
knew the answers.</b> Ten out of ten sighted is significant; six out of ten blind is not
distinguishable from chance, and neither is a mechanical annotator's five out of eight. That does not
prove the corpus is inflated — ten motifs is too few to detect anything but a very large effect — but
it does mean there is currently no significant evidence for the retrieval claim under blind
annotation. Reported as "degraded but present" for two findings because a weakened-looking fraction
reads like a smaller real effect rather than like noise.</div>
<div class="q"><b>A published conclusion rested on an edge that appears in no sentence.</b>
Annotating with the roles visible gave every vacuous document its query's exact relation count and
loop topology, four times out of four — and in one case that meant adding a relation the text never
states. So the claim that an outside author had written structurally perfect vacuous documents was
wrong: I made them that way, and it holds on only half of them once the roles are hidden. The theorem
survives, the refutation built on it was too strong, and the headline is halved rather than
deleted.</div>
<div class="q"><b>A control that had been passing since the first experiment could not have
failed.</b> The measure never read relation strength, so "invariant to unit conversion" was
blindness reported as a virtue. Building the channel — with the invariance defined into the quantity
rather than left for the search to find — makes the control real, and it now tests its own capacity
to fail on every run. The audit built to catch this class of problem had the same problem itself,
one level up, and would have kept certifying impossibility for a distinction the project had just
gained.</div>
<div class="q"><b>Across all three corpora the blind score is 6 of 10, against 10 of 10 sighted —
and the size of that gap is not yet measurable.</b> On two corpora the blind pass recorded half as
many relations as the sighted one, which lowers the score independently of role-knowledge. Direction
confirmed, magnitude unknown, and the control that would settle it is the cheap one I still haven't
built. Two defects in the corpora also surfaced: decoy documents that state their role in their own
text, and sighted structures with four relations to a nine-word sentence — organisation the documents
do not contain.</div>
<div class="q"><b>Knowing the answer while annotating inflated the results by about a third — and
the ordering survived anyway.</b> Re-annotating a corpus with the roles hidden, the same documents
score 1.34× lower, and the paraphrase and analogue lose a perfect match they never deserved. But the
analogue still clears the decoy by a wide margin and the claim holds on three motifs of four. The
record was flattered, not fabricated. Corpus results are quoted at the blind rate from here.</div>
<div class="q"><b>The recurring obstacle has a name, and it is now a pre-test rather than a
discovery.</b> A distinction is recoverable only if it is constant across everything the
representation treats as identical, so a single witness pair settles it in advance. Two failures were
paid for before this was noticed; converting it into a test found three more dead ends and one
vacuous control immediately. The proper response to hitting it is never a cleverer structural score —
it is to declare the missing channel, or to narrow the claim.</div>
<div class="q"><b>The hard part is not the measure — it is getting from text to structure.</b>
On the first benchmark this project did not build, with every passage annotated blind, there is no
signal. But the annotation carries no signal either, by a test written down in advance, so what
failed is the step before the measure. Candidates share 82% of their shape with the query in the
corpora built here and 43% in real analogies. The measure ranks structures well; nobody has shown
that text reliably becomes the right structure, and that step has been done by hand throughout.</div>
<div class="q"><b>And the corpus record now has a control it never had.</b> Every corpus was
annotated by someone who knew each document's designated role. That the ranking was unbiased has
been tested; that the <i>annotation</i> does not encode the role has not. Until it is, the safe claim
is that the measure ranks structures — not that it retrieves analogies.</div>
<div class="q"><b>Declaring an invariance works where asking the search to find it did not.</b>
Normalising representational vertices away before comparing makes subdivision cost exactly nothing,
recovers the original structure every time, and costs the main result nothing — it even restores the
subdivided case from 2 of 6 to 10 of 10. The rewrite is proven terminating and confluent rather than
assumed to be. Two re-encodings remain unhandled and are named rather than absorbed, and the
equivalence must be <i>declared</i>: suppressing blindly damages five of six structures, because
"is this vertex real?" is not a question a structure can answer.</div>
<div class="q"><b>The measure sees the encoding, not only the process — and this is the largest
re-scoping the project has taken.</b> Vocabulary invariance and label invariance hold. Invariance
across equivalent re-encodings does not, and at matched size the measure cannot tell a correct
re-encoding from a corrupted one at all. Everything the search results claim is therefore true
within a fixed representation convention, which is a real limit and one that gates any application
to domains that write the same reality in different forms. The successor is specified: canonicalise
before comparing, rather than widening the space of alignments.</div>
<div class="q"><b>A published claim on this page was wrong, and the correction is on it.</b>
"The vacuous document beats the analogue on 3 of 4" was a sort order read off a randomised hash.
The truth is an exact tie, and the vacuous document outranks the analogue nowhere in the project.
The rule that came out of it: a measure that cannot separate two things has to say so rather than
rank them — and note that making the tie-break <i>stable</i> would have preserved the error under
a coat of reproducibility.</div>
<div class="q"><b>The defence against the oldest risk is refuted, by arithmetic rather than by
experiment.</b> Discounting a match by its genericness cannot separate a real analogue from a
vacuous phrase of the same shape, because the two are isomorphic and every measure of structure
alone must score isomorphic things equally. The risk stands undefended — but the requirement on
any successor is now exact: it has to use information from outside the structure.</div>
<div class="q"><b>The core claim survives an independent corpus — and the oldest risk in the
project arrives as a measurement.</b> Analogue beats false friend 4/4 on motifs, annotations and
judgements nobody here wrote, with paraphrase and analogue tying again. But the generic connector
outranks the analogue on three of four, and it is structurally right to: a vacuous statement can
have perfect structure. That is risk one — the attractive-nonsense machine — logged before any code
existed, whose defence was sketched and never built. Genericness is not a structural property, so
no work on the correspondence measure can fix it.</div>
<div class="q"><b>The fix holds on data frozen before it existed.</b> Six of six, regressions
intact, and paraphrase and analogue now score identically to four decimals in every case — which
is what a genuinely vocabulary-blind measure must do and is not what a fitted patch produces. The
pathology that demoted the original formula is now removed from both places it lived. It also
exposed a seventh wrong ground truth of mine: the corpus had asserted that a same-domain
paraphrase should outrank a cross-domain analogue, which contradicts the project's own thesis.</div>
<div class="q"><b>On something resembling an application, the measure fell short — and the
culprit was a term nobody re-examined.</b> It beats every baseline on the search corpus but gets
2 of 3 on the comparison that matters, losing by 0.0022 because it charges the cross-domain
analogue for using a different domain's relation vocabulary. That is the same failure that
demoted the original formula, fixed for participant labels and never for relation-type labels,
surviving twenty-four experiments until two structures came close enough for two bits to decide
it.</div>
<div class="q"><b>The correspondence measure transfers — the n=1 doubt is discharged.</b> Graded
ordering holds on five base topologies including an acyclic one and an undesigned one, stable
across all three codes. Getting there required making the test harder, and the harder test
immediately exposed an unchecked invariant in the structure container that had survived
twenty-three experiments because every previous world was hand-built.</div>
<div class="q"><b>And no compact summary replaces it.</b> Searching the natural candidates found
nothing complete at four participants — the best, the joint matrix, leaves 2 collisions out of 222
structures. Meanwhile the spectrum multiset writes down 16 numbers to distinguish 8 structures and
adds literally nothing when combined with the matrix. Which numbers you keep matters far more than
how many, and relational structure resists compression harder than the last few findings
suggested.</div>
<div class="q"><b>Relational structure is not a scalar, and past three participants it is not a
pair of profiles either.</b> The two instruments together are provably sufficient at three
participants and provably insufficient at four — the complete invariant is one number per subset
of participants. This project's founding rule against collapsing a measurement into a single score
was written as a discipline. It turns out to be a description of the subject matter, with an arity
threshold attached.</div>
<div class="q"><b>The predictive equation is a robustness law, not a structure law — and that is
now proved, not suspected.</b> Two structures can share an influence profile and an entropy, and
therefore an identical retention prediction, while one is three-quarters pure pairwise
organisation and the other is spread evenly across every order. The law cannot distinguish them at
all. It says what you stand to lose, never what you had. Connected information has the mirror-image
blindness — it sees order and not which participant carries what — which suggests the instrument
is the pair, and that a single scalar for "relational structure" was never available.</div>
<div class="q"><b>The test-set bias was structural, not careless.</b> Functions nameable in
English are influence-symmetric 1.8× more often than the population at three participants and
6.1× more often at four — and the factor grows with arity. Being more thoughtful about which
examples to pick would have made it worse, since the thoughtful choices are the canonical ones and
the canonical ones are symmetric. The fix is to build condition sets by enumerating the property
under test, not by collecting examples.</div>
<div class="q"><b>A test set can be provably unable to detect a whole class of error.</b> The
asymmetric families found an index-reversal bug on their first run — one the previous worlds could
not have caught however carefully they were inspected, because reversing a list of identical
values changes nothing. Coverage is not the only thing a condition set can lack; it can lack the
<i>capacity</i> to fail. And the diagnosis sharpened in the process: what matters is
influence-symmetry, not permutation-symmetry, which the multiplexer control makes plain.</div>
<div class="q"><b>Retention is a vector and the test set was biased toward hiding that.</b> Under
worst-case reporting the number of structures that lose everything goes from 2 to 38 at three
participants and 942 at four — so "only parity vanishes" was an artifact of a best-case summary.
The corrected claim, that parity is unique in vanishing <i>whichever</i> participant you lose, is
both narrower and more alarming. The earlier tables survived only because every family in them was
symmetric, which is now the third correction traceable to symmetric test choices.</div>
<div class="q"><b>Reordering is this project's default, not its exception.</b> Four of five
audited parameters change the ranking rather than just the values — including one believed safe.
The most consequential is that "retention" turns out to be one number per participant you might
lose, not one number: best-case and worst-case orderings are slightly anti-correlated. Reporting
rankings as curves over the nuisance parameter is now a protocol rule rather than a lesson to be
relearned.</div>
<div class="q"><b>The predictive equation survives noise, with a caveat that bites.</b> The
general form is exact at every noise level, and balanced outcomes turn out to be exactly
noise-invariant — which retroactively explains an asymmetry the log had used as evidence without
understanding. But noise <i>reorders</i> which structures are most fragile above about 5%, so the
clean-case law cannot be used to rank candidates in the field. A free parameter reordering results
was the very first failure this project found; it has now arrived a second time from an entirely
different direction, which suggests it is a shape of error worth watching for by default.</div>
<div class="q"><b>The project has its first equation that predicts rather than describes.</b>
Retention = 1 − influence of the hidden participant / entropy of the outcome. Verified to 1e-16
against brute force, exhaustive at two arities, and it explains every earlier retention number
including the anomalous one. Both terms are computable from the structure in advance. Everything
else in this log measures what happened; this one says what will.</div>
<div class="q"><b>A suspicious number was worth chasing, and the chase went both ways.</b> The
~0.5 retention flagged as "not claimed" turned out to be a real structural class — 56 of 256
functions, all balanced — while the four measurements offered as evidence for it were two
functions counted twice plus a noise artifact. Right answer, invalid evidence. Flagging it rather
than claiming it was the thing that made the difference; had it been asserted, it would have been
asserted correctly and for entirely the wrong reason.</div>
<div class="q"><b>Six wrong constructions, all mine.</b>
Size-matching every condition hid a size bias in the measure. Hand-identifying one loop instead
of enumerating produced a critical/benign split that doesn't exist. And a function assumed
decomposable because it's called "majority" turned out to be genuinely synergistic — whenever
the first two disagree, the third decides alone. The pure-noise control was a deterministic
function of the variables it was supposed to be independent of. And two of four "independent"
test structures were the same function, with the other two being duals of each other. None was caught by reasoning; all
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
