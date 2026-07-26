"""EXP-050 -- her warp, our ground, over sequences of structures.

Run to the plan locked at 0ea78954. Targets the one channel EXP-031 proved
absent: temporal order.

Three arms, and the third is the one that matters:
  static  -- our measure on the final structure. Provably blind to delay.
  warped  -- her A1 alignment with our metric ground.
  rigid   -- elementwise, no warp. Tests whether the WARP earns its keep, as
             opposed to merely having a sequence. Her own summary says the
             ground is the transferable win and NOT the warp.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from protocol2 import require_locked_plan                         # noqa: E402
from structure import Relation, Structure                         # noqa: E402
from temporal import rigid, static, warped                        # noqa: E402

E = [("level", "signal", "POS"), ("signal", "correction", "POS"),
     ("correction", "level", "NEG")]
# CONTROL CORRECTED mid-run, and the reason is recorded rather than tidied away.
# The first control differed from E only by relation TYPE (POS<->NEG on one
# edge). Our measure searches node bijections CROSSED WITH type substitutions,
# so a type map sending POS->NEG matched them perfectly -- by design, that is
# what makes it blind to a domain's vocabulary. The control was testing a
# property the measure deliberately has, not a failure. See EXP-051 for the
# separate finding that fell out of this.
#
# A proper control needs a different SHAPE, not different labels.
ALT = [("level", "signal", "POS"), ("level", "correction", "POS"),
       ("correction", "signal", "NEG"), ("signal", "level", "NEG")]


def S(name, edges):
    rels = tuple(Relation(a, b, t) for a, b, t in edges)
    nodes = tuple(sorted({n for r in rels for n in (r.src, r.dst)}))
    return Structure(name, nodes, rels)


def seq(edges, delay, T):
    """the third relation engages only from timestep `delay`"""
    return [S(f"x{t}", edges[:2] if t < delay else edges) for t in range(T)]


def main() -> None:
    plan = require_locked_plan("EXP-050")
    rows, excluded = [], 0

    # --- delay sweep: same final structure, different timing -------------
    for T in (6, 10, 16):
        for delay in (1, 2, 3, 5):
            if delay >= T:
                continue
            A, B = seq(E, 0, T), seq(E, delay, T)
            if A[-1].edge_set() != B[-1].edge_set():
                excluded += 1
                continue
            rows.append({"kind": "delay", "T": T, "delay": delay,
                         "static": round(static(A, B), 6),
                         "warped": round(warped(A, B), 6),
                         "rigid": round(rigid(A, B), 6)})

    # --- control: genuinely different topology, no delay ----------------
    ctrl = []
    for T in (6, 10, 16):
        A, B = seq(E, 0, T), seq(ALT, 0, T)
        ctrl.append({"kind": "topology", "T": T,
                     "static": round(static(A, B), 6),
                     "warped": round(warped(A, B), 6),
                     "rigid": round(rigid(A, B), 6)})

    delay_static = [r["static"] for r in rows]
    delay_warped = [r["warped"] for r in rows]
    delay_rigid = [r["rigid"] for r in rows]

    static_blind = max(delay_static) < 1e-9
    warped_sees = min(delay_warped) > 1e-9
    rigid_sees = min(delay_rigid) > 1e-9
    topo_preserved = all(c["warped"] > 1e-9 for c in ctrl)
    warp_beats_rigid = statistics.fmean(delay_warped) > statistics.fmean(delay_rigid) + 1e-9

    if not warped_sees:
        verdict = ("FAILS AT ITS MOST PROMISING POINT -- the composition still "
                   "cannot see delay")
    elif not topo_preserved:
        verdict = ("TRADES ONE CAPABILITY FOR ANOTHER -- it sees delay but loses "
                   "topology discrimination")
    elif rigid_sees and not warp_beats_rigid:
        verdict = ("THE SEQUENCE DID THE WORK, NOT THE WARP -- rigid elementwise "
                   "comparison sees delay just as well. This reproduces HER own "
                   "finding (the ground transfers, the warp does not) rather than "
                   "being a discovery of ours")
    else:
        verdict = ("THE WARP ADDS SOMETHING -- warped separation exceeds rigid on "
                   "these sequences")

    report = {
        "experiment": "EXP-050",
        "plan_locked_at": plan["_locked_at"], "plan_sha256": plan["_sha256"],
        "excluded": excluded,
        "delay_rows": rows, "topology_control": ctrl,
        "static_is_blind_to_delay": static_blind,
        "warped_sees_delay": warped_sees,
        "rigid_sees_delay": rigid_sees,
        "topology_discrimination_preserved": topo_preserved,
        "warp_beats_rigid": warp_beats_rigid,
        "means": {"static": statistics.fmean(delay_static),
                  "warped": statistics.fmean(delay_warped),
                  "rigid": statistics.fmean(delay_rigid)},
        "verdict": verdict,
    }
    (Path(__file__).resolve().parents[1] / "results" / "exp050.json").write_text(
        json.dumps(report, indent=2))

    print(f"\nEXP-050   plan locked at {plan['_locked_at'][:8]}\n")
    print("DELAY -- same final structure, different timing")
    print(f"  {'T':>4}{'delay':>7}{'static':>10}{'warped':>10}{'rigid':>10}")
    for r in rows:
        print(f"  {r['T']:>4}{r['delay']:>7}{r['static']:>10.4f}"
              f"{r['warped']:>10.4f}{r['rigid']:>10.4f}")
    print("\nCONTROL -- genuinely different topology")
    print(f"  {'T':>4}{'':>7}{'static':>10}{'warped':>10}{'rigid':>10}")
    for c in ctrl:
        print(f"  {c['T']:>4}{'':>7}{c['static']:>10.4f}"
              f"{c['warped']:>10.4f}{c['rigid']:>10.4f}")
    print(f"\n  static blind to delay          : {static_blind}")
    print(f"  warped sees delay              : {warped_sees}")
    print(f"  rigid sees delay               : {rigid_sees}")
    print(f"  topology discrimination kept   : {topo_preserved}")
    print(f"  warp beats rigid               : {warp_beats_rigid}")
    print(f"\n>>> {verdict}")


if __name__ == "__main__":
    main()
