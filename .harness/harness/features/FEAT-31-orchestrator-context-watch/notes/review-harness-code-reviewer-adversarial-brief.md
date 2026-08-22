# Adversarial review — FEAT-31-orchestrator-context-watch BRIEF.md

Verdict: DO NOT SIGN as-is. Two must-fix defects (SC-07's ground truth is undefined; SC-01
conflicts with SC-02 on real production data). Everything else is fixable in place or advisory.

## Must-fix

### 1. SC-07 has no disk-only signal to test against, and no determinate ground truth for its fixture

`feature-schema.json`'s `runs[]` item schema is `additionalProperties:false` with exactly three
keys — `id`, `squad`, `verdict` (confirmed by reading the file). No field records which
orchestrator/session/agent executed a run. The Problem section itself says cycles and runs "are
the only counters left, and neither is a proxy for context" (i.e. neither proves an orchestrator
was carried past a seam). So SC-07 — "check-state.sh reports a feature whose runs show an
orchestrator carried across a phase seam" — names a signal (`runs`) that structurally cannot carry
the fact being tested, without a schema change nowhere disclosed as a needed decision (DEC-191
closes the top-level 11 keys; the `runs[]` sub-schema is separately closed and untouched by any
Constraint/Supplies entry here).

Worse: SC-07's second half asks the test to determine whether FEAT-29's real history is
"genuinely compliant" and assert that determination rather than assume it — but DEC-159, as
written today (`DECISIONS.md:3937-3986`), sets no numeric bound on the sanctioned fix-loop
exception ("a fix loop that runs long is what monitoring is for... deferred until a live fix loop
actually produces the degraded-relay case"). There is no rule to grade FEAT-29 against until
SC-09 supplies one — and SC-09 is a sibling SC in the *same* feature, creating an undisclosed
ordering dependency.

FEAT-29 is also a moving, internally inconsistent target as of 2026-08-20 (today):
`feature.json` shows `status: Building`, `cycles_used: 12/12`, `runs: 19/20`, last run
`2026-08-20-16-product BLOCKED` — while `STATE.md`'s own `## Current` narrates `status: Review`,
"close-out complete", "panel PASS". The brief's cited numbers ("10 of 10 cycles and 17 of 20
runs") are already stale (verified via `feature.json` read just now). SC-07's fixture needs a
pinned snapshot (a commit sha), not "FEAT-29's recorded history" as a live reference.

**This is exactly the SC the task flagged as possibly having no determinate verdict — confirmed.**

Minimum fix: either (a) add an explicit field to a *new*, separately-versioned artifact (not the
closed `runs[]`) that records orchestrator/session identity per run — and disclose that as a
decision this brief needs — or (b) drop SC-07's "from disk, per feature" framing for something
weaker that the existing schema can actually support, and pin the FEAT-29 fixture to a frozen
commit sha rather than "recorded history."

### 2. SC-01 and SC-02 make incompatible demands on the same real data

SC-01: the tool's peak "matches an independent hand computation over the same file to the token."
SC-02: the tool must *exclude* a specific real record type as "unusable" so its reported peak
*differs* from the naive sum.

I reproduced the docs-migration planner's transcript
(`070b3f94-b495-4deb-b352-6896cfb60ad3/subagents/agent-a93ac10cf0f7b033d.jsonl`, line 989) and
found the actual mechanism: the anomalous top-level `usage.cache_read_input_tokens: 1494870` is
the **sum of two nested `usage.iterations` sub-calls** (746,878 + 747,992 = 1,494,870, exact),
produced by Claude Code's own advisor/sub-call feature (`content_types=['tool_use']`, an
`advisor_message` iteration with `model: claude-fable-5` sits between them). This is a real,
structural, reproducible double-count in production data, not a hypothetical.

If SC-01's live-orchestrator run happens to hit a transcript with this shape (confirmed real and
not rare — it's a shipped Claude Code feature, "advisor"), a **naive** hand computation and the
tool's SC-02-correct output cannot both be "the same value" — unless "hand computation" is
defined to already apply SC-02's exclusion rule, at which point SC-01 no longer independently
validates anything; it just checks the tool agrees with itself. The brief never resolves this,
and never specifies what "hand computation" means precisely enough to know which reading is
intended.

(The live orchestrator I could test against right now — `agent-aebb8688976e006c9`, FEAT-30's
planner, currently at 927 lines — happens to have zero multi-iteration usage entries, so SC-01
would pass against *it* today. That's luck, not a guarantee; nothing in the brief bounds which
orchestrator SC-01 is run against, and the anomaly is real elsewhere in this same machine's data.)

Minimum fix: define "hand computation" precisely (does it include the SC-02 exclusion rule or
not?), or require SC-01's fixture to be a transcript verified free of multi-iteration usage
entries.

## Numbers — re-derived from `/Users/molchairuangutai/.claude/projects/-Users-molchairuangutai-GitHub-harness*/*/subagents/`

Exact matches (command output cited):
- 76 orchestrator transcripts (`agentType == "harness-orchestrator"` with a matching `.jsonl`) —
  exact match.
- peak > 400k: 24 of 76 — exact match.
- docs-migration planner (`agent-a93ac10cf0f7b033d.jsonl`, 992 entries): top reading 1,497,025,
  `cache_read` component 1,494,870; next-highest 750,837 with `cache_read` 749,029 — all four
  numbers match to the token.
- FEAT-29's orchestrator (`agent-a7783f0ec41e6a8c6.jsonl`, 1,046 entries): peak 696,472, and
  peak == last entry's value — exact match. ("Monotonic" is loose, not literal: one entry-to-entry
  dip of 391,432→388,386 exists, 668 of 669 steps non-decreasing — immaterial, not worth gating.)
- SC-06's cited worktree directory
  `-Users-molchairuangutai-GitHub-harness--claude-worktrees-fix-harness-tooling-backlog` exists —
  confirmed via `ls`.
- `log_retention_days: 30` — confirmed, `harness.json:163`.
- feature-schema.json: 11 top-level properties, `additionalProperties: false`, 8 required, no
  `phase` key, `status` enum present — all confirmed.
- INV-17 at `check-state.sh:462` — confirmed exact line.
- DEC-159's sentence "the watchdog remains the post-hoc audit" — confirmed verbatim,
  `DECISIONS.md` (DEC-159 block).
- DEC-174 am.1–am.4 names `check-state.sh` in the enforcement-layer list and am.4 (2026-08-19)
  makes the enumeration non-exhaustive — confirmed.
- `cost-report.py:338` — confirmed via `git show <parent-of-deletion-commit>` — the line is
  `cpt_threshold = int(budgets.get("context_per_turn_tokens") or 200_000)`. Nuance: this line
  *does* read a would-be config key, falling back to a hardcoded 200k default; `harness.json` at
  that commit never populated the key, so the effective value was always the hardcoded fallback.
  The brief's phrasing ("never a config key... hardcoded") matches FEAT-08's own handoff note
  verbatim (`notes/handoff-plan.md:26`, confirmed) and is a fair characterization of the *effective*
  behavior, not a fabrication — flagging only because it slightly overstates a nuance, not because
  it's wrong.
- Sidecar shapes: scoping to the same single checkout the brief measured (excluding the separate
  FEAT-30 worktree checkout's own project directory), I get exactly **10 distinct key shapes**,
  and **39 sidecars with `worktreePath`/`worktreeBranch`, of which exactly 38 also carry
  `spawnedWithWorktree`** — both match the brief exactly.

Discrepancies found (checkable, reported per instructions):
- Total sidecar count: brief says "1,390 sidecars," I count **1,401** in the same directory right
  now. Given the shape-count and worktree-key splits above match exactly, this reads as organic
  growth between the brief's measurement and my check, not a computation error — same class as
  the live-agent caveat the task pre-disclosed. Not a defect; worth naming because the brief
  doesn't flag its own supporting evidence as time-sensitive (see SC-08 tie-in below).
- Oldest transcript: brief says "oldest file Jul 26"; I measure **2026-07-25T16:10:30** as the
  oldest `.meta.json`/`.jsonl` mtime in the checkout. Off by one day. Low severity, possibly a
  timezone artifact, but wrong as stated and checkable.
- Median peak: brief says 232,844; my full recomputation over all 76 gives **243,080.5**.
  peak > 200k: brief says 47 of 76; I get **48 of 76**. Two transcripts sit close to the boundary
  (196,189 and 205,833), and — as with the live FEAT-30 planner (which grew from the brief's cited
  89,587 tokens/87 entries to **343,943 tokens/896 entries** by the time I checked, same session,
  same day) — several of these 76 orchestrators are demonstrably still-growing live processes.
  The qualitative claims ("median already above threshold," "top of distribution 3-4x it") hold
  under either number. Reporting as verified-with-drift, not a defect — but see the meta-point
  below.
- "Verification gaps" section: the brief says "four kinds carry `cmd: null`" and names functional,
  component, ui, eval. `harness.json`'s `test_kinds` actually has **five**: those four plus
  `typecheck` (`cmd: null`, `status: "unresolved"`, `harness.json:145-150`). The conclusion ("no
  criterion rests on any of them") still holds since no SC touches typecheck either — but the
  count is wrong and was checkable.

**Meta-point tying several of the above together:** SC-08 requires the *shipped tool* to disclose
that its own figures "go stale silently rather than erroring." The brief's own supporting
evidence — the 76-transcript distribution, the sidecar counts, the live-agent reading — is subject
to the exact same failure mode and isn't flagged as such anywhere in the brief's own prose. That's
consistent, not hypocritical, but worth the operator's attention: this brief's numbers have a
measured half-life of hours, not days.

## Decision citations — all verified against DECISIONS.md / DECISIONS-INDEX.md

DEC-148, DEC-159, DEC-178, DEC-174 (am.1-am.4), DEC-188, DEC-150, DEC-90, DEC-191 all check out as
cited. One thing not cited that arguably should be: **DEC-192** ("`phase` and `status` collapse
into one `status` field...") is the decision that actually retired DEC-159's proposed `phase:`
field — the brief states the *fact* correctly (no `phase` key in the schema) but attributes it to
DEC-191/DEC-159 tension rather than naming DEC-192, the decision that resolved it. Low severity —
informational, not a misstatement.

## The thing nobody named

1. **The tool can be the thing that consumes the context it's measuring.** The Goal frames this as
   "the operator can ask... while it is still running" — nothing bars an orchestrator or lead from
   invoking the same tool on *itself* as self-monitoring, which the Goal's framing actively invites.
   Reading a long-lived orchestrator's own still-growing JSONL (FEAT-30's planner is already 896
   lines and climbing, mid-review) costs the caller context/tokens precisely when the orchestrator
   is already the one most at risk. Not addressed anywhere in Requirements or Constraints.

2. **A pull-based warning with no wired escalation reproduces the exact failure this brief
   diagnoses.** DEC-159's relay rule failed specifically because it was "advisory prose... with
   nothing reading either fact" (Problem section, re: FEAT-29's six resumes). REQ-03's warning is
   likewise manually invoked: a nonzero exit code that matters only if something checks it. The
   brief names no caller obligated to run it routinely. Without that, the same class of silent
   drift recurs one layer up.

3. **A token threshold risks displacing DEC-159's phase-boundary rule rather than supporting it.**
   DEC-159 explicitly replaced DEC-148's threshold judgment with a phase-boundary judgment because
   the threshold was "advisory... a threshold judgment" that didn't hold operators. REQ-03
   reintroduces a threshold as the visible, actionable signal. Nothing in the brief states whether
   "under threshold" is ever license to keep an orchestrator running past a natural phase seam —
   SC-09's DEC-159 edit is the natural place to say so, and doesn't.

## Advisory (not gating)

- **REQ-01's "with one command"** bakes in a CLI-shape choice. Swap the implementation (two thin
  flags on one command vs. one command) and the actual outcome — operator gets current/peak/entry
  count without hand-parsing JSONL — is unchanged. Reads as an implementation decision wearing a
  requirement's clothes (harness-principles rule 6). Not worth blocking on.
- **SC-02's detection rule** ("cache_read exceeds previous total by more than that request could
  have added") is a magnitude heuristic with no stated bound, tested only against the one real
  fixture pair (1,497,025 / 749,029). The root mechanism I found — additive nested
  `usage.iterations` from advisor sub-calls — is directly inspectable in the same record; a rule
  that reads `iterations` when present would be more robust than a delta-magnitude guess, and
  would not have the false-negative failure mode of two consecutive inflated records (both large,
  looking "stable" relative to each other) or the false-positive risk of one legitimately huge
  tool-result turn. Recommend the SC name the mechanism, not just the symptom.
- **SC-05's "asserts... absent before... exists, then present after"** is ambiguous between a
  same-run differential unit test (two code paths in the finished tool — matches `verify:
  automated evidence: unit`) and a literal claim about commit ordering during development (which
  cannot be graded post-hoc unless the brief separately mandates committing the test before the
  implementation, which it does not). Reword to state which is meant.
- SC-03, SC-04, SC-06, SC-08, SC-09, SC-10, SC-11 read as well-formed and testable; SC-11's
  "deleting the unmeasured branch must make this test fail" is exactly the discriminating-mutant
  shape that avoids a green-and-incapable-of-going-red test. No finding.
- Coverage: every REQ-01..07 traces to at least one SC; no SC quantifies past what this feature
  can touch. No omission found in that sweep beyond the SC-07 gap above.

## What I did not chase further

FEAT-29's own `feature.json`/`STATE.md` inconsistency (schema `status: Building` vs. STATE.md's
prose `status: Review`, "close-out complete") is real and reproducible, but it is FEAT-29's own
defect, not FEAT-31's brief. I used it only as evidence that SC-07's fixture source is unstable;
I did not investigate FEAT-29 further.
