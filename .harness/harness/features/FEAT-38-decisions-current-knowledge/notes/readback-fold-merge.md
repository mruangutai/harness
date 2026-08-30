# Read-back — the three amendments FEAT-44 merged in

**Three of three PASS.** DEC-159, DEC-198 and DEC-201 each survive SC-11's two-part test: the
governing belief is recoverable as a recorded superseded claim, and what falsified it is present as
a clause of the entry's current truth. No claim was dropped that the read-back judged load-bearing.

The fold was written by `harness-documentor` (run `runs/fold-merge-product/`). The read-back was
performed by `harness-code-reviewer`, which did not write it (run `runs/readback-fold-validator/`),
with `harness-validator-lead` independently re-deriving the three highest-risk claims at source.
Method as SC-11 states it: pre-fold text from `git show 141eca6:.harness/harness/docs/DECISIONS.md`
read beside the folded form, per entry, with a file pointer each.

Reviewer's own note: `notes/review-harness-code-reviewer-readback-fold.md`.

## Per-entry verdicts

| entry | verdict | governing belief | what falsified it |
|---|---|---|---|
| DEC-159 | **PASS** | `DECISIONS.md:3728-3731` | `:3727-3728`, `:3731-3732` |
| DEC-198 | **PASS** | `:5608-5611` (claim a), `:5620-5621` (claim b) | `:5609-5614` (claim a), `:5620-5621` (claim b) |
| DEC-201 | **PASS** | `:5872-5875` | `:5866-5871`, nuance clause `:5875-5878` |

DEC-198 carried **two** falsified claims, not one: the `200000` default sourced to the retired
`context-watch.py`, and an earlier amendment draft's assertion that `.harness/harness.json` lacked
the key. Both earned a clause.

## DEC-201 — the six evidence bounds, item by item

All six **PRESENT**. This entry was the one at risk: its amendment carried measured evidence with
stated limits, and a summarising fold would have kept the finding and lost the bounds.

1. Measured on ONE OMP build, twice, on one machine (2026-08-28 and 2026-08-29). PRESENT.
2. Probe and raw output committed at
   `.harness/harness/features/FEAT-44-omp-context-advisory/evidence/README.md`. PRESENT; path
   confirmed to exist in the tree.
3. Version-floor risk — a later OMP may rename or drop the accessor. PRESENT.
4. `.claude/skills/harness/bin/probe-omp-session-accessor.py` dispatches a real subagent under the
   committed probe and fails, never skips. PRESENT; path confirmed to exist.
5. It is a MANUAL check, not a CI gate — it needs the omp binary and live model credentials, and CI
   has neither, so the risk is watched by something a human must run. PRESENT.
6. One build's observed behaviour, not a timeless property of the OMP API. PRESENT.

**The nuance held.** The retired nonce scheme's two-call constraint was CORRECT and *died with the
mechanism rather than being found wrong* — the folded clause at `:5875-5878` says so in those terms
and closes "a claim that was right and became inapplicable is not a claim that was refuted." A fold
that flattened that into "was wrong" would have let the nonce scheme be re-proposed as a fresh idea.
It is the single most likely thing to have been lost and it was not.

**No new supersession** (`:5870-5872`): DEC-204's existing supersession of DEC-201's host-specific
mechanics is restated, not extended. The never-wait ruling, the `echo hold` incident numbers, the
three 2026-08-23 probes, the 1057.1s data point with its dispatch-level-override limit, the threshold
bands and the lineage paragraph all sit outside every diff hunk.

## Dropped details, and the judgement on each

Three corroborating details of retired mechanisms did not survive. Each was judged DEFENSIBLE by the
reviewer, and each is recorded here so the judgement is visible rather than implicit.

- **DEC-159** — the retired hook's exit-2 / PostToolUse-timing plumbing sentence. Internals of a
  mechanism the folded entry now explicitly forbids re-proposing; neither the falsified claim nor its
  falsifier.
- **DEC-159** — the literal quote *"this advises only; the orchestrator decides"*. Survives
  paraphrased at `:3727` as "advises and never refuses; the orchestrator decides".
- **DEC-201** — the `569d417` commit anchor, the "about a second" duration, and the
  zero-or-two-or-more-matches SKIP behaviour. **The closest call.** The claim they corroborated — the
  two-call constraint was right — survives explicitly with its reasoning at `:5875-5878`; a commit
  SHA for a deleted mechanism is not a stated limit on a live claim.
- **DEC-198** — nothing dropped; semantically identical, relocated only.

## Anchor check

DEC-198 cites `.harness/harness.json` line 169 for the key and line 170 for its rationale sibling.
The merge changed that file, so both were re-measured after it:

- `:169` — `"orchestrator_context_warn_tokens": 200000,`
- `:170` — `"_orchestrator_context_warn_tokens_rationale": "INFORMATIONAL, NOT A GATE. …"`

No anchor rot. DEC-205's one mechanical check is satisfied here and by
`test-check-decision-anchors.py::test_live_authority_anchors_all_resolve` in the suite.

## A dispatch premise that was wrong, corrected here rather than buried

The orchestrator's dispatch asserted that both `context-watch-hook.py` **and** `.claude/settings.json`
are absent from this tree. **`.claude/settings.json` is present** and still registers a PostToolUse
hook on the `Write|Edit|Bash` matcher — `check-domain.sh --post`, not the retired watchdog. Verified
directly: the file parses and carries six registrations. DEC-159's folded clause is scoped "No Claude
hook is registered **for this** any more", so it is true as written; an unscoped fold would now be
false, and the scoping was the documentor's own.

## Bound

A read-back establishes that meaning survived the fold. It does **not** establish that the surviving
claims are true today — that is SC-13's question and it was answered separately. The un-amended
remainder of these three entries was deliberately not re-audited; one staleness item found in passing
is carried to the backlog rather than edited (`DEC-159` still says the handoff shape gate denies at
>40 lines while the same entry records the cap raised to ~60 at DEC-160).
