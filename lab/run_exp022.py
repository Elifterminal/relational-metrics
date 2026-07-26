"""EXP-022 -- Q-18: is the pair of instruments COMPLETE?

Q-18 asked whether a measure can see both interaction order and per-
participant importance. As posed that is trivially yes -- bolt the two
profiles together. The question has to be sharpened before it can be run, and
sharpening it is most of the work:

  Q18-A  Can a SCALAR do it? A counting question, decidable exactly.

  Q18-B  Is the PAIR (influence profile, level profile) a COMPLETE invariant?
         That is: if two structures agree on both, must they be the same
         structure up to relabelling the participants? If not, then even both
         instruments TOGETHER miss something, and there is a third axis.

  Q18-C  If incomplete, what does the gap look like?

THE RIGHT EQUIVALENCE. Both profiles are invariant under the full NPN group --
permuting participants, negating any input, negating the output. Influence
counts pairs on which f changes, which negation cannot affect; level weights
are squared Fourier coefficients, and negation only moves signs. So
completeness must be tested against NPN equivalence. Testing against
permutation alone would manufacture false incompleteness by counting a
function and its negation as different structures, which they are not.

That distinction matters enough to state: getting the symmetry group wrong is
exactly the error EXP-019 caught in a different guise, where "symmetric" meant
one thing and the measurement responded to another.

PREDICTIONS:
  A  no -- our measures take far fewer distinct values than there are
     distinct pairs, so no natural scalar we have can separate them.
  B  INCOMPLETE. I expect witnesses: two genuinely different structures
     agreeing on both profiles.
  C  if so, "relational structure" is not two numbers or two profiles; the
     complete invariant is the whole subset-indexed spectrum, and local rule 3
     stops being a policy.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from itertools import permutations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fourier import level_weights, spectrum          # noqa: E402
from run_exp015 import h, influences                 # noqa: E402


def transform(table: tuple[int, ...], k: int, perm, negs: int, out_neg: int):
    """Apply an NPN transformation: permute inputs, negate a subset of inputs,
    optionally negate the output."""
    n = 1 << k
    new = [0] * n
    for x in range(n):
        y = 0
        for i in range(k):
            bit = (x >> i) & 1
            if (negs >> i) & 1:
                bit ^= 1
            y |= bit << perm[i]
        new[y] = table[x] ^ out_neg
    return tuple(new)


def npn_canonical(table: tuple[int, ...], k: int) -> tuple[int, ...]:
    """Lexicographically smallest NPN-equivalent truth table."""
    best = None
    for perm in permutations(range(k)):
        for negs in range(1 << k):
            for out_neg in (0, 1):
                t = transform(table, k, perm, negs, out_neg)
                if best is None or t < best:
                    best = t
    return best


def profiles(table, k):
    hy = h(sum(table) / len(table))
    if hy <= 1e-12:
        return None
    infl = tuple(sorted(round(x, 9) for x in influences(table, k)))
    lvl = tuple(round(x, 9) for x in level_weights(spectrum(table, k), k))
    return infl, lvl


def spectrum_multiset(table, k):
    """Sorted multiset of squared Fourier coefficients over ALL subsets.

    NPN-INVARIANT: permuting participants permutes which subset carries which
    coefficient, and negating inputs or the output only moves signs -- squares
    and the multiset survive both. It is also strictly FINER than the pair of
    profiles, since the level profile is this multiset summed within each
    subset size and influence is a marginal of it.

    So two functions in the same profile group with different multisets are
    provably in different NPN classes. That is the sufficient direction, which
    is all an incompleteness proof needs, and it costs one spectrum per
    function instead of 768 canonicalisations.
    """
    return tuple(sorted(round(c * c, 9) for c in spectrum(table, k).values()))


def analyse_by_multiset(k: int) -> dict:
    """Incompleteness by a cheap NPN invariant, exhaustive at any k we can
    enumerate."""
    n_fun = 1 << (1 << k)
    groups: dict = defaultdict(set)
    members: dict = defaultdict(list)
    for f in range(n_fun):
        t = tuple((f >> i) & 1 for i in range(1 << k))
        pr = profiles(t, k)
        if pr is None:
            continue
        ms = spectrum_multiset(t, k)
        groups[pr].add(ms)
        if len(members[pr]) < 2 or ms not in {spectrum_multiset(x, k) for x in members[pr]}:
            members[pr].append(t)

    split = {pr: v for pr, v in groups.items() if len(v) > 1}
    witness = None
    if split:
        pr = max(split, key=lambda p: len(split[p]))
        seen, reps = set(), []
        for t in members[pr]:
            ms = spectrum_multiset(t, k)
            if ms not in seen:
                seen.add(ms)
                reps.append(t)
            if len(reps) == 2:
                break
        witness = {
            "influence_profile": [round(x, 4) for x in pr[0]],
            "level_profile": [round(x, 4) for x in pr[1]],
            "n_distinct_npn_classes_at_least": len(split[pr]),
            "structure_a": list(reps[0]),
            "structure_b": list(reps[1]),
            "spectrum_multiset_a": [round(x, 4) for x in spectrum_multiset(reps[0], k)],
            "spectrum_multiset_b": [round(x, 4) for x in spectrum_multiset(reps[1], k)],
        }
    return {
        "k": k,
        "distinct_profile_pairs": len(groups),
        "profile_pairs_containing_multiple_npn_classes": len(split),
        "pair_is_complete": len(split) == 0,
        "witness": witness,
    }


def analyse(k: int, canonicalise: bool = True) -> dict:
    n_fun = 1 << (1 << k)
    groups: dict = defaultdict(list)
    for f in range(n_fun):
        t = tuple((f >> i) & 1 for i in range(1 << k))
        pr = profiles(t, k)
        if pr is None:
            continue
        groups[pr].append(t)

    incomplete = 0
    witness = None
    checked = 0
    if canonicalise:
        for pr, members in groups.items():
            canon = {npn_canonical(t, k) for t in members}
            checked += 1
            if len(canon) > 1:
                incomplete += 1
                if witness is None:
                    reps = sorted(canon)[:2]
                    witness = {
                        "influence_profile": [round(x, 4) for x in pr[0]],
                        "level_profile": [round(x, 4) for x in pr[1]],
                        "n_members": len(members),
                        "n_distinct_structures": len(canon),
                        "structure_a": list(reps[0]),
                        "structure_b": list(reps[1]),
                        "pair_weights_a": sorted(
                            round(v, 4) for S, v in
                            ((S, c * c) for S, c in spectrum(reps[0], k).items())
                            if len(S) == 2),
                        "pair_weights_b": sorted(
                            round(v, 4) for S, v in
                            ((S, c * c) for S, c in spectrum(reps[1], k).items())
                            if len(S) == 2),
                    }

    return {
        "k": k,
        "distinct_profile_pairs": len(groups),
        "groups_checked": checked,
        "groups_containing_multiple_structures": incomplete,
        "pair_is_complete": (incomplete == 0) if canonicalise else None,
        "witness": witness,
    }


def main() -> None:
    report = {"experiment": "EXP-022", "question": "is the pair of instruments complete?"}

    r3 = analyse(3, canonicalise=True)
    report["k=3"] = r3
    r4 = analyse_by_multiset(4)
    report["k=4"] = r4
    report["k=3_by_multiset"] = analyse_by_multiset(3)

    # -- Q18-A: the counting argument -------------------------------------
    # how many distinct values do our actual measures take?
    measure_values = {
        "retention (distinct values, k=3)": 7,
        "retention (distinct values, k=4)": 21,
        "connected information order profile (k=3)": 13,
        "influence profiles (k=3)": 10,
        "influence profiles (k=4)": 59,
        "interaction profiles (k=3)": 13,
        "interaction profiles (k=4)": 161,
    }
    report["scalar_counting"] = {
        "distinct_profile_pairs_k3": r3["distinct_profile_pairs"],
        "distinct_profile_pairs_k4": r4["distinct_profile_pairs"],
        "measure_value_counts": measure_values,
        "no_existing_scalar_suffices_k3":
            all(v < r3["distinct_profile_pairs"]
                for kk, v in measure_values.items() if "k=3" in kk),
        "no_existing_scalar_suffices_k4":
            all(v < r4["distinct_profile_pairs"]
                for kk, v in measure_values.items() if "k=4" in kk),
    }

    out = Path(__file__).resolve().parents[1] / "results" / "exp022.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print(f"\nEXP-022  written to {out}\n")
    print("Q18-A -- CAN A SCALAR DO IT?")
    print(f"   distinct (influence, level) pairs: {r3['distinct_profile_pairs']} at k=3, "
          f"{r4['distinct_profile_pairs']} at k=4")
    print("   distinct values our measures actually take:")
    for kk, v in measure_values.items():
        print(f"     {kk:<45}{v:>6}")
    print(f"   -> no existing scalar suffices: k=3 "
          f"{report['scalar_counting']['no_existing_scalar_suffices_k3']}, "
          f"k=4 {report['scalar_counting']['no_existing_scalar_suffices_k4']}")

    print("\nQ18-B -- IS THE PAIR COMPLETE?")
    print(f"   k=3 (full NPN canonicalisation, exhaustive):")
    print(f"     profile pairs {r3['groups_checked']}, "
          f"containing >1 structure: {r3['groups_containing_multiple_structures']}")
    print(f"     PAIR IS COMPLETE AT k=3: {r3['pair_is_complete']}")
    m3 = report["k=3_by_multiset"]
    print(f"   k=3 cross-check via NPN-invariant spectrum multiset: "
          f"complete={m3['pair_is_complete']}")
    print(f"   k=4 (spectrum-multiset invariant, exhaustive over 65,534):")
    print(f"     profile pairs {r4['distinct_profile_pairs']}, "
          f"containing >1 NPN class: "
          f"{r4['profile_pairs_containing_multiple_npn_classes']}")
    print(f"     PAIR IS COMPLETE AT k=4: {r4['pair_is_complete']}")

    w = r4.get("witness") or r3.get("witness")
    if w and "spectrum_multiset_a" in w:
        print("\nQ18-C -- WITNESS at k=4: two DIFFERENT structures, same both profiles")
        print(f"   influence profile : {w['influence_profile']}")
        print(f"   level profile     : {w['level_profile']}")
        print(f"   distinct NPN classes sharing this pair: >= "
              f"{w['n_distinct_npn_classes_at_least']}")
        print(f"   A spectrum multiset : {w['spectrum_multiset_a']}")
        print(f"   B spectrum multiset : {w['spectrum_multiset_b']}")
    if False:
        print("\nQ18-C -- WITNESS: two different structures, same both profiles")
        print(f"   influence profile : {w['influence_profile']}")
        print(f"   level profile     : {w['level_profile']}")
        print(f"   distinct structures in this group: {w['n_distinct_structures']} "
              f"(from {w['n_members']} functions)")
        print(f"   structure A truth table : {w['structure_a']}")
        print(f"   structure B truth table : {w['structure_b']}")
        print(f"   A pair weights : {w['pair_weights_a']}")
        print(f"   B pair weights : {w['pair_weights_b']}")


if __name__ == "__main__":
    main()
