# Plan-panel review — harness-code-reviewer, cycle c0 (BUG-1309-mirror-build-entry)

**BLUF: REQ→task coverage is complete (no orphan REQ, no orphan task, no phantom trace to a
non-existent id, no dependency cycle/inversion). Two findings, both traceability/verification
gaps, neither a functional defect. R1/R2 confirmed closed at source, not re-raised.**

## REQ→task coverage map (built independently against BRIEF.md REQ-01..REQ-10 and plan.yaml traces:)

| REQ | Traced by | Verdict |
|---|---|---|
| REQ-01 | T-02, T-04, T-08, T-09 | covered |
| REQ-02 | T-03, T-07, T-08, T-09 | covered |
| REQ-03 | T-01, T-02 | covered |
| REQ-04 | T-01, T-02 | covered |
| REQ-05 | T-01, T-02 | covered |
| REQ-06 | T-02, T-04 | covered |
| REQ-07 | T-05 | covered (see finding 2) |
| REQ-08 | T-03, T-09 | covered |
| REQ-09 | T-07 | covered (see finding 2) |
| REQ-10 | T-06 | covered |

**Every REQ-01..REQ-10 is traced by at least one task. This is a finding-free result, not
"not checked" — I built the map myself from `traces:` on every task, not from the c3 goal-check's
unverified claim.** No REQ id used in any `traces:` list is absent from BRIEF.md (all cite
REQ-01..REQ-10, none out of range). No task (T-01..T-09) traces zero REQs, so no task serves "no
live requirement at all."

## depends_on: valid DAG, no cycle, no forward reference

`T-01→[]`, `T-02→[T-01]`, `T-03→[T-02]`, `T-04→[T-03,T-06]`, `T-05→[T-02,T-06]`, `T-06→[T-01]`,
`T-07→[T-03,T-06]`, `T-08→[]`, `T-09→[T-04,T-05,T-06,T-07,T-08]`. One valid order:
T-01,T-08 → T-02,T-06 → T-03 → T-04,T-05,T-07 → T-09. Every same-file collision (T-02/T-03/T-04 all
touch `gh-sync.py`) is serialized by an explicit or transitive `depends_on` chain; no task reads an
artifact (e.g. `feature_schema.recovery_command_for`, `record_build_entry`) without a declared
(possibly transitive) dependency on the task that creates it. No `verify:` block greps a case name a
later task's task text renames or removes — confirms the c3/c6 finding, not a new one.

## Findings

**F1 (med) — SC-02's "caller or contract error" clause is never exercised by any declared test
case.** `BRIEF.md` SC-02 (`verify: automated`, `evidence: integration`) requires TWO things left
unrecorded: (a) a run that fails after a remote object was created, and (b) "a run that exits on a
caller or contract error." T-02's `intent:` states the mechanism for (b) in prose only — "`die()`
and `refuse()` record nothing at all: a caller or contract error is not an outcome"
(`plan.yaml:207-208`) — but T-02's own `verify:` `for n in` list names seven cases and none of them
drives `cmd_open` through a `die()`/`refuse()` path: `"T-02 open records opened"`, `"T-02 sync false
records not-applicable"`, `"T-02 unpinned repo records nothing"` (via `skip(_NO_RECORD)`, not
`die`/`refuse`), `"T-02 first-call failure records recovery-required"` (a remote-call failure via
`skip()`, not a caller/contract error), `"T-02 partial remote write records nothing"` (covers half
(a) only), `"T-02 second open stays opened"`, `"T-02 opened never downgrades"`. I grepped the whole
plan for `die()`/`refuse(`/"contract error" (`plan.yaml:93-95,137-139,206-208,278-282,322-328,
374-378,431-457,1176-1178`) and found no other task naming a case for this clause either — T-03's
`"T-03 parent contract error refuses"` exercises `recover-terminal`'s own contract error, not
`open`'s. **Consequence: at ship, SC-02's second clause has no automated evidence at all** — it is
true today only because the code structure happens to make it true by construction (no call path
between a `die()`/`refuse()` exit and `record_build_entry`), and a later refactor that moves a
`record_build_entry` call earlier in `cmd_open`, or adds a new `die()`/`refuse()` site after a
partial write, would silently violate SC-02 with nothing to catch it. This is the ORPHAN
SUCCESS CRITERION shape named in my dispatch, not a restatement of R1/R2 (neither residual concerns
SC-02 or T-02's die/refuse paths).

**F2 (low) — REQ-07 and REQ-09 are each split across two tasks functionally, but only one task
cites the REQ.** REQ-07 ("... re-running the mirror open is idempotent") is traced only by T-05
(the merge gate, which does not touch `open`'s idempotence at all); the idempotence behavior is
actually implemented and tested by T-02 (`"T-02 second open stays opened"`,
`"T-02 opened never downgrades"`), but T-02's `traces:` list (`[REQ-01, REQ-03, REQ-04, REQ-05,
REQ-06]`) omits REQ-07. Symmetrically, REQ-09 ("a legacy recovery attempted while GitHub is
unavailable leaves the feature non-terminal...") is traced only by T-07 (worktree retention), but
the "recovery attempted while GitHub is unavailable" half is T-03's own stated behavior — "If gh is
unavailable the existing skip() funnel fires: nothing is recorded... the feature stays non-terminal"
(`plan.yaml:332-337`, case `"T-03 gh failure records nothing"`) — and T-03's `traces:` (`[REQ-02,
REQ-08]`) omits REQ-09. Neither is a functional gap (the behavior ships and is tested); it's a
traceability precision gap. **Consequence: an auditor tracing REQ-07 or REQ-09 by `traces:` alone
would open only T-05 or only T-07, find no idempotence/gh-outage logic there, and could
mistakenly conclude the clause is untested or (worse) modify/remove the actual proof in T-02/T-03
during an unrelated refactor of a task that "isn't traced to" that REQ.**

## R1/R2 status (not re-raised)

Both confirmed closed at source, re-read directly rather than taken on the closure note's word:
R1 — `T-05.intent` (`plan.yaml:630-655`) branches PINNED vs UNPINNED `github.repo`, the unpinned
reason carries no `open` token and names the configuration fix; case
`"T-05 unpinned repo absent build_entry denies naming the configuration fix"` is present in T-05's
`verify:` gate. R2 — `T-07.intent`'s WHY paragraph (`plan.yaml` era section) states the pre-existing
`gh-sync: SKIP`/`gh-sync: FAILED` gates deliver settled bullet 8 for the era corpus and return
before the new build-entry block. No finding here restates either.

## Not challenged

No orchestrator ruling challenged — none of D-01..D-09 (era-exempt set, retention-on-value,
DEC-138 fail-open posture, D-09's unpinned-repo Build/merge double-block) produced a concrete new
consequence beyond what's already disclosed and signed against in the plan.

## Stage 2 (code quality)

n/a — this is a plan-phase review (`approval.status: pending`, no `review_sha`); no diff, no code
exists to grade. `code_grade: n_a` per DEC-207.
