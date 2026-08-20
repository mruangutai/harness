# Distillation — harness-security-reviewer — FEAT-29-graphql-budget

## Source

No mid-run observations were logged this feature. Source is my own review artifact
(`notes/review-harness-security-reviewer-costlog-c472a02.md`) plus the three lead-relayed
candidates in the dispatch. All three accepted, none rejected — each passed the six-spawns test
and each earned its slot without displacing a judged-weaker survivor (one legitimate merge,
otherwise inserted into section headroom).

## Candidate 1 — scope test conflates "delta relevant" with "surface ever reviewed"

**Accepted → craft, Outcomes, O-06 (add).** The lesson generalizes beyond this feature: a
diff-shaped scope test answers "does this delta need review," not "has this surface ever had
one," and only the second licenses a safe decline. Actionable for how I write `scope_reason` on
every future spawn, wherever I run. Not repository-specific — no path, decision ID, or file name
survives into the entry.

## Candidate 2 — my own recommendation contradicted my own findings section

**Accepted → craft, Gotchas, G-15 (add).** Verified against my source artifact: §3 states
"sibling files (`.harness/logs/2026-07-27.md` etc.) are already tracked (`git ls-files`
confirms)" (line 47-48), and the recommendations list at line 88 then offers "(or all of
`.harness/logs/`)" — the blanket form would gitignore those already-tracked files, contradicting
the evidence three lines above it in my own artifact. Real, sourced, and a repeatable trap: check
each remediation against your own findings before listing it, especially an alternative offered
as "or the broader form."

## Candidate 3 — severity axis doesn't carry irreversibility

**Accepted → craft, Patterns, P-17 (add, via freed slot).** My §3/§4 correctly graded low
because no call site puts a secret in argv today (reachability-based), but reachability-based
severity doesn't communicate that a credential commit, if it ever happened, cannot be undone —
a different axis from likelihood. Also folds in the distinct point that an opt-in/time-window
control (§4) and a containment control (gitignore/chmod, §3) are not substitutes for each other —
verified against my own artifact's rationale (line 57-63) which draws exactly this line against
the prior ship review's "moot" framing.

## Mechanics — how three candidates fit into a full-15 Patterns section

Patterns was at cap (15/15). Rather than force a displacement, I re-read the two closest
existing entries, P-08 and P-13, and found them genuinely redundant: both say "diff against the
pre-change state, not zero" for a data-exposure question (P-08: rewrap discarding a raw-error
field; P-13: one more instance of a pre-existing exposure). Merged into one P-08 entry (45
words, ≤ the longer input's 45, satisfying the merge-length rule) — this is condensation of a
real duplicate, not a forced fit. That freed exactly one Patterns slot, used for candidate 3.
Candidate 1 went to Outcomes (5/10 → 6/10, headroom, no merge needed) and candidate 2 to
Gotchas (14/15 → 15/15, exactly the one open slot). No entry was displaced as "weaker" — the
math worked out via one honest merge plus existing headroom, so nothing was judged inferior and
discarded.

## Repository tier

No changes. None of the three candidates turn on a fact true of only this repository — all
generalize to "how a security reviewer works," which is the craft-tier test. Repository file
(`P-01`–`P-03`, 3/15 Patterns, 21 lines) is unmodified and still passes `check-expertise.sh`.

## Rejections

None. All three candidates passed the six-spawns-from-now test on inspection; no candidate was
dropped.
