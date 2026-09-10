# FEAT-58 — plan goal-check against the operator's stated intent (c1)

**Does this plan deliver the operator's stated intent? Yes on the bedrock rule and on every settled
ruling in `grilling-worktree-corpus-2026-09-09.md`; NO at four named surfaces, each fixable by an
edit to an existing task. Verdict FAIL — loop back is meaningful and cheap.**

Graded against the grilling artifact only (read end to end, `:1-94`). Its two issue-#1559 comments
(`:5`, `:6`) were **not reachable** from this session — no network read attempted beyond the repo;
everything below rests on the artifact's own text, which restates their conclusions at `:16-32`
and `:48-52`.

## Item verdicts

**1. Bedrock rule, both halves — MET.**
(a) never materialised (`:10`, `:16-18`): T-08 (derived sparse cone at creation), T-09 + T-10
(in-place convergence of the standing set). (b) fully available from outside (`:19-21`): T-01
(`corpus_root`/`corpus_features`/`corpus_read`), T-08 case (c) set-equality + content-search parity,
T-15 (FEAT-57 note paths resolve from a converged worktree), T-03/T-04/T-05/T-06/T-16 (readers
relocate to the corpus root instead of losing the corpus), T-14 (prose). No task trades availability
for bytes. Two availability risks named below (G-3, G-4).

**2. The four "Not yet specified" questions (`:36-44`) — MET, all four DECIDED, none deferred.**
(i) which readers are single-feature → decided by measurement in the arch-eng receipt and recorded
per reader in T-07's intent (3 single-feature, 2 path-logic, 1 fixture-only, 7 sweeps, 1 API-calling
gate, 1 non-reader). (ii) where the derivation lives → **D-01**, `harness_boundary.py` beside
`worktree_owner`. (iii) how a task declares provider/ref → **D-05** + T-12. (iv) enumerated or
derived include-list → **D-03**, derived.
**The OPEN ledger is an honest instrument, not a disguised deferral.** It is bounded by
construction: T-13 enumerates *every* tracked file under `.claude/skills/harness/bin/` from the git
index and T-07's ⊆ scan reuses that enumeration, so an unclassified script is inside the instruments'
scope whether or not anybody names it. Verified independently: `gh-close-gate.sh`,
`plan-sign-gate.sh` and `inject-expertise.sh` contain no `features` reference at all;
`bash-write-guard.sh:701` and `validate-digest.py:790` match a *single*-feature path shape, not an
enumeration. Accounting gap only → **G-1**.

**3. Out-of-scope creep (`:48-52`) — MET, scan clean.** Scanned `plan.yaml` for
`reflink|clonefile|cp -Rc|du|archiv|prune|rewrit|worktree remove|reduce the number`. Zero
reflink/clonefile/archive/prune hits. `du` appears twice, both as prohibitions (T-08 intent, T-10
intent). `git worktree remove` appears four times, three of them prohibitions (T-09, T-10, T-11) and
once in T-08 as rollback of a worktree the same command just created, run from the owner root — not
a reduction of the standing set. State store: no task touches a write path; T-10 only adds a record
file. Read-path-only holds.

**4. The verification trap (`:91-94`) — MET.** Measured criteria checked, each with its mode: SC-01
`ls | wc -l`; SC-02 `find -type f | wc -l` + the zero-files-under-`features/` clause; SC-03 set and
count equality; SC-06 per-worktree `ls` before/after; SC-07 `git log --diff-filter=D` asserting both
exit status and empty stdout; SC-13 `find -type f`; T-08 (b)/(e), T-09 step 1/5, T-10 record rows.
**No criterion a wrong (clone-on-write) implementation would pass:** it leaves SC-01 at 87, SC-02's
file count unchanged, SC-06's after-count ≠ 1 and SC-13's count moving. Advisory: SC-03/T-08 (c)
names no *command* for the "content search" on either side → **G-5**.

**5. Constraints (`:86-90`) — PARTIAL.** `check-state.sh` serialisation against FEAT-57 T-19:
present and correct, T-03 intent first paragraph, with the standing order to re-read rather than
trust line numbers. DEC-174: present and correct — `lanes:` row 3 plus a per-task
`execution_reason` on every enforcement-path task (T-01, T-03–T-06, T-08–T-10, T-12, T-14, T-16).
FEAT-57 replay-manifest/dataset freeze: **narrowed**. The operator gated *execution* (`:87-88`); the
plan gates only T-15's own assertions (in-file hard gate, correctly never skipping). Nothing tells
the build to hold. → **G-2**.

**6. Asked for, not done — PARTIAL. Four gaps, each with an owner.**

- **G-1 (T-07, low).** The ledger's OPEN reason names three unclassified hook-registered scripts;
  `.claude/settings.json` registers **nine** hook commands and five are unnamed by the plan
  (`inject-expertise.sh` and `validate-digest.py` additionally). Add both names with their
  inspection clearance to T-07's reader record. Grades `:11-12` ("no gate able to report clean on a
  partial view").
- **G-2 (T-01, med).** Carry `:87-88` into the first executed task's intent as a hard execution
  precondition, so the freeze binds the build and not only T-15's assertions.
- **G-3 (T-09, med).** Nothing forbids the migration from sparsifying **the owner root itself**.
  T-09 says "per linked worktree", but no case asserts the main worktree is never passed to
  `git sparse-checkout set`, and T-01 refusal state (C) is a post-hoc detector, not a guard —
  a mistargeted run destroys availability (`:19-21`) for every reader at once. Add the exclusion
  assertion to `tests/unit/test-corpus-migration-order.py`.
- **G-4 (T-14, med — the one live violating artifact).** `.claude/commands/harness.md:45` instructs
  the reader to "list in-flight features from `.harness/harness/features/*/feature.json`" — exactly
  the checkout-relative enumeration `:11-12` and REQ-11 forbid, and post-convergence it reports one
  flow. T-14's sweep globs `.claude/skills/**/SKILL.md` and `.claude/agents/*.md` only, so the
  `.claude/commands/` surface is unreachable by the plan's own open-set sweep. Widen the glob and
  fix that line.
- **G-5 (T-08, low).** Name the content-search command and the ref used on both sides of the
  SC-03/T-08 (c) parity assertion; "a content search" is the one measured claim without a mode
  (`:93-94`).
- **G-6 (T-06, med).** `check-domain.sh` holds a **second** corpus enumeration beyond
  `_hardlink_plan`: `SWEEP_GLOBS` (`:1053-1061`, consumed `:2147-2151`), five literal
  `.harness/*/features/*` patterns. T-06 converts only `_hardlink_plan` and T-13 deliberately does
  not allow-list this file, so T-13's own pattern ("a literal `.harness/*/features/*` string") trips
  on it at build time. Either convert the sweep too or record the deliberate exemption with its
  reason. Mitigation already present: the sweep extends over `linked_worktrees(root)` from the
  owner root, so its fail-open risk is low; the collision is not.

## Facts re-derived or contradicted (`:54-82`)

None contradicted. Two notes, neither a gap: **D-11**'s rejection rationale cites per-call
`git show` latency (13.69 ms; ~13–14 s per run) while the operator settled that sweep latency is
"not an argument either way" (`:82`) and that the git-served view is *faster and less stale*
(`:68-72`) — different measurements, and D-11's load-bearing argument is the ~25-site fail-open, not
latency. T-03 deliberately re-derives the glob-site count at execution time rather than trusting a
recorded one; that is a re-derivation the plan orders on purpose, not a rot.

## Open question

- **Q1 (non-blocking).** Under D-11 the five relocated sweeps resolve their *set* through
  `corpus_features(root)` (provider `history`, at the default ref) but read their *bytes* from the
  owner root's working tree via `bases[feat]`. The frame T-03 records ("provider and ref") therefore
  names history while the content came from a path. REQ-05 / `:41-42` ask a sweep to state the frame
  it read. Owner **T-03 and T-04**: state the content read's base alongside the enumeration ref, or
  call the path provider for those readers. Not raised in any prior cycle.

`plan.yaml` and `BRIEF.md` unmodified; no worktree created or removed; no suite, formatter or linter run.
