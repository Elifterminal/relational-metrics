"""A deterministic annotator, for Q-31.

Every blind-vs-sighted comparison so far confounds two things: whether the
annotator knew each document's role, and how many relations they felt like
writing down. EXP-033 could not separate them, so R-18 has a confirmed
direction and an unmeasured size.

A program fixes both at once. It has no role knowledge, and its effort cannot
vary -- the same sentence always yields the same relations. The second-annotator
commission is the better control and is still outstanding; this is the part that
does not need anyone else.

HOW IT WORKS, and it is deliberately crude:
  * split each sentence into clauses on punctuation and a small set of
    connectives
  * find a verb from a DECLARED lexicon in each clause
  * take the noun phrase before it as source, after it as target
  * polarity comes from the lexicon, never from context

WHAT THIS CANNOT DO, stated before any result is read. It is much worse at
language than a person. So a drop in performance under mechanical annotation is
ambiguous between "the corpus was inflated" and "the extractor is stupid".

WHY IT IS STILL INFORMATIVE. Its stupidity is applied UNIFORMLY and is
uncorrelated with role -- it cannot tell an analogue from a false friend, so it
cannot be stupid in a way that favours either. Absolute rates will fall; the
ORDERING test is what stays meaningful.

Residual worry, declared: the extractor may handle simple chains better than
loops or mutual inhibition, and document kinds are not uniformly distributed
across those shapes. That is a surface-form bias, not a role bias, and it is
measured in EXP-036 rather than assumed away.
"""

from __future__ import annotations

import re

# Declared once, from the vocabularies already in the corpora. Not tuned per
# sentence and not extended after seeing results.
POS_VERBS = (
    "increases", "increase", "raises", "raise", "raising", "improves", "improve",
    "improving", "drives", "drive", "draws", "draw", "gives", "give", "gains",
    "gain", "supports", "support", "attracts", "attract", "attracting",
    "promotes", "promote", "strengthens", "strengthen", "extends", "extend",
    "extending", "expands", "expand", "expanding", "feeds", "feed", "builds",
    "build", "carries", "carry", "produces", "produce", "concentrates",
    "deepens", "deepen", "widens", "widen", "accelerates", "accelerating",
    "triggers", "trigger", "favours", "favour", "arise from", "arises from",
    "depends on", "reinforces", "reinforce", "reinforced by", "leads to",
    "lead to", "pushes", "push", "sustains", "sustain", "sustaining",
    "preserves", "preserve", "preserving", "maintains", "maintain",
    "maintaining", "protects", "protect", "protecting", "supporting", "adds",
    "add", "make", "makes", "extracts", "extract", "dries", "dry",
    # added after inspecting extractor OUTPUT ONLY -- before any comparative
    # result was computed, so the lexicon cannot have been steered by which
    # document kind it happened to favour. Recorded because "I fixed it first"
    # is only meaningful if the order is on the record.
    "offer", "offers", "receive", "receives", "gets", "get", "brings", "bring",
    "permutes", "permute", "adjusts", "adjust", "dated by", "filed by",
    "accumulates", "accumulate", "shifts", "shift", "moves", "move",
    "reroutes", "reroute", "fails over", "ices", "extending",
)
NEG_VERBS = (
    "decreases", "decrease", "reduces", "reduce", "reducing", "lowers", "lower",
    "lowering", "limits", "limit", "limiting", "suppresses", "suppress",
    "suppressing", "inhibits", "inhibit", "blocks", "block", "blocking",
    "prevents", "prevent", "preventing", "removes", "remove", "removing",
    "discourages", "discourage", "depressing", "depresses", "chokes", "choke",
    "empties", "empty", "releases", "release", "resets", "reset", "cancels",
    "cancelled", "displace", "displaces", "excludes", "exclude", "stops",
    "stop", "falls", "fall", "shut", "tighten", "tightens",
)

_SPLIT = re.compile(r",\s*|;\s*|\s+while\s+|\s+and\s+|\s+which\s+|\s+so\s+|\s+until\s+|\s+whose\s+")
_STOP = {"a", "an", "the", "more", "greater", "less", "of", "in", "to", "its",
         "their", "his", "her", "it", "that", "this", "than", "further",
         "back", "down", "up", "own", "into", "on", "at", "by", "for", "with",
         "from", "as", "one", "two", "may", "can", "must", "will", "is", "are",
         "was", "were", "be", "been", "and", "or", "but"}


def _phrase(words: list[str]) -> str | None:
    kept = [w.strip(".,;:'\"").lower() for w in words]
    kept = [w for w in kept if w and w not in _STOP and w.isalpha()]
    if not kept:
        return None
    return "_".join(kept[-2:])          # last two content words


def extract(sentence: str) -> list[tuple[str, str, str]]:
    """Relations from one sentence. Deterministic: same input, same output."""
    out: list[tuple[str, str, str]] = []
    carry: str | None = None
    subject: str | None = None
    for clause in _SPLIT.split(sentence):
        clause = clause.strip()
        if not clause:
            continue
        low = " " + clause.lower() + " "
        # A clause with no lexicon verb still names something. Keep it as the
        # subject so a later clause can attach to it -- otherwise a sentence
        # whose first clause opens with an unlisted verb yields nothing at all.
        hit = None
        for v in sorted(POS_VERBS + NEG_VERBS, key=len, reverse=True):
            i = low.find(" " + v + " ")
            if i >= 0:
                hit = (v, i, v in NEG_VERBS)
                break
        if hit is None:
            subject = _phrase(clause.split()) or subject
            continue
        verb, idx, neg = hit
        before = clause[:max(idx - 1, 0)].split()
        after = clause[idx + len(verb) + 1:].split()
        src = _phrase(before) or carry or subject
        dst = _phrase(after)
        if src and dst and src != dst:
            out.append((src, dst, "NEG" if neg else "POS"))
            carry = dst                  # chain continuation across clauses
    return out
