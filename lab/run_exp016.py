"""EXP-016 -- does the retention law survive noise? (scope test on EXP-015)

EXP-015 derived and verified

    retention = 1 - Influence_j(f) / H(f)

for DETERMINISTIC functions. The scope note said plainly that noise adds a
term which does not cancel -- and EXP-013/EXP-014 had already seen the
consequence without understanding it: AND drifted from 0.5401 to 0.4958 as 5%
noise was applied, while majority sat at exactly 0.5000 at every noise level.
That asymmetry was observed and never explained.

Carrying the noise term through instead of dropping it:

    I(Y; visible) = H_e(f) - [ I_j + (1 - I_j) h(e) ]
    I(Y; all)     = H_e(f) - h(e)

so

    retention_e = 1 - I_j (1 - h(e)) / ( H_e(f) - h(e) )          [GENERAL]

where H_e is the entropy of the NOISY outcome and h(e) the binary entropy of
the noise. At e=0 this reduces to the EXP-015 form.

PREDICTIONS, written before running:

  1. The EXP-015 form FAILS under noise -- it was never claimed otherwise, but
     the size of the failure matters and has never been measured.
  2. The general form holds EXACTLY at every noise level.
  3. BALANCED functions are exactly noise-INVARIANT. A balanced outcome stays
     balanced under symmetric noise, so H_e = 1 and the whole expression
     collapses to retention = 1 - I_j, with no e in it at all. If true, this
     explains why majority never moved and AND did -- an observation that has
     been sitting unexplained in the log for two experiments.
  4. Quantisation survives at each fixed noise level, but the VALUES move for
     unbalanced functions.
  5. The RANKING of functions by fragility is preserved across noise levels --
     the practically important one. If noise reorders which structures are
     most fragile, the deterministic law is misleading whenever data is noisy,
     which is always.

FALSIFICATION: if the general form does not match brute force, the derivation
is wrong and the noiseless one is suspect too, since it is a special case.
"""

from __future__ import annotations

import json
import math
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from run_exp015 import brute_mi, h, influences        # noqa: E402

NOISES = (0.0, 0.01, 0.05, 0.10, 0.20, 0.40)


def general_retention(table, K, e):
    """1 - I_j (1 - h(e)) / (H_e - h(e)), best over hidden j."""
    n = len(table)
    p1 = sum(table) / n
    p1 = p1 * (1 - e) + (1 - p1) * e
    he, hn = h(p1), h(e)
    denom = he - hn
    if denom <= 1e-12:
        return None
    return 1.0 - min(influences(table, K)) * (1 - hn) / denom


def noiseless_form(table, K):
    ones = sum(table)
    hy = h(ones / len(table))
    if hy <= 1e-12:
        return None
    return 1.0 - min(influences(table, K)) / hy


def brute_retention(table, K, e):
    full = brute_mi(table, K, tuple(range(K)), e)
    if full <= 1e-12:
        return None
    best = max(brute_mi(table, K, tuple(j for j in range(K) if j != hide), e)
               for hide in range(K))
    return best / full


def main() -> None:
    tables3 = [tuple((f >> i) & 1 for i in range(8)) for f in range(256)]
    report = {"experiment": "EXP-016", "question": "does the retention law survive noise?",
              "general_form": "retention_e = 1 - I_j(1-h(e)) / (H_e - h(e))"}

    # -- 1 & 2. verify both forms against brute force, per noise level ----
    per_noise = {}
    for e in NOISES:
        worst_gen, worst_det, n = 0.0, 0.0, 0
        for t in tables3:
            b = brute_retention(t, 3, e)
            if b is None:
                continue
            g = general_retention(t, 3, e)
            d = noiseless_form(t, 3)
            worst_gen = max(worst_gen, abs(b - g))
            worst_det = max(worst_det, abs(b - d))
            n += 1
        per_noise[f"{e:.2f}"] = {
            "functions": n,
            "max_error_general_form": worst_gen,
            "max_error_deterministic_form": round(worst_det, 6),
            "general_form_holds": worst_gen < 1e-9,
        }
    report["verification_k3"] = per_noise

    # k=4 spot check of the general form
    worst4, n4 = 0.0, 0
    for f in range(0, 65536, 211):
        t = tuple((f >> i) & 1 for i in range(16))
        for e in (0.05, 0.20):
            b = brute_retention(t, 4, e)
            if b is None:
                continue
            worst4 = max(worst4, abs(b - general_retention(t, 4, e)))
            n4 += 1
    report["verification_k4"] = {"checks": n4, "max_error": worst4,
                                 "holds": worst4 < 1e-9}

    # -- 3. balanced functions noise-invariant? --------------------------
    balanced = [t for t in tables3 if sum(t) == 4]
    unbalanced = [t for t in tables3 if sum(t) not in (0, 8) and sum(t) != 4]
    def drift(group):
        d = 0.0
        for t in group:
            vals = [general_retention(t, 3, e) for e in NOISES]
            vals = [v for v in vals if v is not None]
            if len(vals) > 1:
                d = max(d, max(vals) - min(vals))
        return d
    report["balanced_max_drift_across_noise"] = round(drift(balanced), 12)
    report["unbalanced_max_drift_across_noise"] = round(drift(unbalanced), 6)
    report["balanced_are_noise_invariant"] = drift(balanced) < 1e-12

    # -- 4. quantisation per noise level ---------------------------------
    quant = {}
    for e in NOISES:
        vals = set()
        for t in tables3:
            g = general_retention(t, 3, e)
            if g is not None:
                vals.add(round(g, 9))
        quant[f"{e:.2f}"] = len(vals)
    report["distinct_values_by_noise"] = quant

    # -- 5. rank preservation --------------------------------------------
    base = []
    for t in tables3:
        g = general_retention(t, 3, 0.0)
        if g is not None:
            base.append((t, g))
    ranks = {}
    for e in NOISES[1:]:
        pairs = [(g0, general_retention(t, 3, e)) for t, g0 in base]
        pairs = [(a, b) for a, b in pairs if b is not None]
        conc = disc = 0
        for i in range(0, len(pairs), 3):           # strided pair sample
            for j in range(i + 1, min(i + 40, len(pairs))):
                a0, a1 = pairs[i]
                b0, b1 = pairs[j]
                if abs(a0 - b0) < 1e-12 or abs(a1 - b1) < 1e-12:
                    continue
                if (a0 - b0) * (a1 - b1) > 0:
                    conc += 1
                else:
                    disc += 1
        ranks[f"{e:.2f}"] = {"concordant": conc, "discordant": disc,
                             "tau_like": round((conc - disc) / max(conc + disc, 1), 4)}
    report["rank_preservation_vs_noiseless"] = ranks
    report["ranking_preserved"] = all(v["discordant"] == 0 for v in ranks.values())

    out = Path(__file__).resolve().parents[1] / "results" / "exp016.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-016  written to {out}\n")
    print("GENERAL FORM:  retention_e = 1 - I_j(1-h(e)) / (H_e - h(e))\n")
    print(f"{'noise':<8}{'fns':>6}{'err(general)':>15}{'err(EXP-015 form)':>20}")
    for e, v in per_noise.items():
        print(f"{e:<8}{v['functions']:>6}{v['max_error_general_form']:>15.2e}"
              f"{v['max_error_deterministic_form']:>20.6f}")
    print(f"\nk=4 spot check: {n4} checks, max error {worst4:.2e}, "
          f"holds={report['verification_k4']['holds']}")

    print(f"\nBALANCED functions, max drift across all noise levels : "
          f"{report['balanced_max_drift_across_noise']:.2e}")
    print(f"UNBALANCED functions, max drift across all noise levels: "
          f"{report['unbalanced_max_drift_across_noise']:.4f}")
    print(f"  -> balanced are exactly noise-invariant: "
          f"{report['balanced_are_noise_invariant']}")

    print(f"\nDistinct retention values by noise level: {quant}")
    print("\nRank preservation vs the noiseless ordering:")
    for e, v in ranks.items():
        print(f"  noise {e}: concordant {v['concordant']}, "
              f"discordant {v['discordant']}, tau-like {v['tau_like']}")
    print(f"\n>>> general form holds at every noise level: "
          f"{all(v['general_form_holds'] for v in per_noise.values())}")
    print(f">>> ranking preserved under noise           : {report['ranking_preserved']}")


if __name__ == "__main__":
    main()
