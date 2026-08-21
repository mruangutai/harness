# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **plan**, at its terminus. The amend round is **complete**: all seven operator rulings and the
DEC-197 item landed in one pm pass. `approval.status` is `pending` on `plan.yaml` and `## Approval` is
`pending` in `BRIEF.md` — verified untouched immediately before each commit. Nothing here signs.

`plan.yaml` is **1692 lines / 108804 bytes, 15 tasks, 10 decisions**, committed on `feat/FEAT-32` at
**`7463b80`** as `+632/−152` against `6d83e91`, with `BRIEF.md` at `+118/−52`, pm's
`notes/research-FEAT-32-ruling-amendments.md` and both observation logs. It grew from 13 tasks / 8
decisions because R3 and R4 ruled two surfaces IN: **T-14** makes the approval-block exclusion real in
`check-domain.sh`, **T-15** makes the signer artifacts agree, and **D-09/D-10** carry the reasoning.
Execution modes: 8 `main-session-direct` (T-01, T-07, T-08, T-09, T-11, T-12, T-14, T-15 — every gate
script and its test) and 7 `team` (T-02..T-06, T-10, T-13 — the libraries and the docs), which is
DEC-174 am.4's category test: a module a gate imports is not itself a gate.

**Run `2026-08-21-2-product`: lead ESCALATE, pm PASS, exactly one pm spawned.** The `SubagentStop` hook
forced the lead terminal mid-run with its pm in flight — **#551 occurrence 7**, one round after
occurrences 5 and 6 were ruled in for recording. That first digest reported pm's work
`files_touched: []` and "unrecoverable". **Both were wrong, and the lead corrected them itself**: it was
resumed, pm ran to completion, and the final digest (rewritten 12:05) carries pm `PASS`. The forced
close is real and belongs in the record; the loss did not happen. Before dispatching, that lead had
caught this worktree being behind `main` and redirected pm's three doc reads to the main checkout —
which is what kept the amend from being "corrected" in the wrong direction on DEC-90 and DEC-197.

**Ruling-by-ruling, verified by the orchestrator against the artifact, not the digest.** R1 — D-01's
precondition records DISCHARGED, `47a9935` confirmed an ancestor of `c32f332`; the two-lock-dialect
shape recorded rejected. R2 — no strike task; T-13 item 5 inverted to an explicit do-not-touch naming
`16b30c6`, and `BRIEF.md` now credits **FEAT-30**, not this feature, with falsifying DEC-90; SC-16
**WITHDRAWN** for loss of subject rather than left unmet. R3 — D-09 records the wait as an
**impossibility** and ships two mechanisms instead. R4 — D-10 rules the **main session** the signer, on
`.claude/skills/harness/SKILL.md:34-35`, which already said so. R5(a) — the lock-absence assertions
replaced, plus a verify that FAILS if one survives. R5(b) — 13 `CLAUDE_PROJECT_DIR` pins, well beyond
the two anchors named. R5(c) — D-04 now reads THE MAIN SESSION. R5(d) — T-01 narrows to one key and its
verify FAILS on re-measuring the settled `agent_type`. R6 — occurrences 5 and 6 recorded in three
places, anchored to run dir `2026-08-21-1-product`, with the gitignore caveat. R7 — **this one did need
work, contrary to the dispatch**: the plan named only #627, so #560 and #605 would not have survived
into the build. Now at D-08, all three.

**pm overturned one ruling's premise and I accept it.** R5(a) said T-05 makes `test-expertise-merge.py`
cases 4/5/6 pass *vacuously*. They go **RED**: D-02 puts flock on a **sibling** `.lock`
(`plan.yaml:112`) never removed (`:432`), while today's `expertise-merge.py` creates that sibling with
`O_EXCL` (`:214-215`) and removes it (`:290`) — which is why they pass now. The remedy is unaffected and
was applied verbatim. The distinction matters because a build agent told to expect a silent pass instead
hits a crash.

`cycles_used` **0** of 10, 2 runs of 20. A forced close is not rework, and charging it would hide the
defect (DEC-157, rule 15).

Route check at `eea6f53`: `check-plan-routes.py` exits 0, **zero VIOLATIONs**, 12 DEVIATIONs of which
**5 are FEAT-32's** — T-01, T-07, T-08, T-09 and the new T-14, each the deliberate DEC-174 shape under
DEC-179. (At `c32f332` it was 11 and 4.) Attribution is per item: a grep of that output for "FEAT-32"
returns **1**, because seven lines name only `bin/` paths. `check-state.sh` exits 1 with FEAT-32's sole
violation being "BRIEF.md is NOT approved" — the terminus, not a defect.

## Open Questions

- Q1 **BLOCKING, main session only.** This worktree is two commits behind `origin/main`:
  `git merge-base --is-ancestor` says `16b30c6` (DEC-90 strike) and `1d2b036` (DEC-197) are **not**
  ancestors of HEAD; `47a9935` is. Both missing commits are **docs-only** (`git show --stat`:
  DECISIONS.md, DECISIONS-INDEX.md, SPEC.md) and `test_kinds` is byte-identical between HEAD and
  `origin/main`, so no code diverged. The bite: T-13 mints the next free DEC number by reading the file,
  and this checkout's highest is **196** against `origin/main`'s **197**, so a build here mints a
  **duplicate DEC-197**. pm defended in prose and T-13 degrades to report-and-change-nothing; the merge
  is the real fix. No tier below the main session can move HEAD.
- Q2 **BLOCKING.** Sign or amend both artifacts. `BRIEF.md` changed this round — new REQ-11, REQ-12,
  SC-17, SC-18, SC-19, and SC-16 withdrawn — so its signature is not a formality.
- Q3 **BLOCKING, and sharper than the original framing.** `plan.yaml`'s `approval:` mapping is granted
  to **nobody**: `check-domain.sh --resolve` prints `harness-orchestrator` **and** `harness-pm` (both
  may write the whole file unrefused), `grep -n approval check-domain.sh` returns one line, `:858`, a
  comment, and `team-config.yaml:18` grants the main session only the pre-DEC-182 **heading** forms.
  T-15 adds the mapping to `main_session.writes` — **but that list is a record no check reads**, and
  `check-domain.sh` never governs the main session (it exits 0 with no `agent_type`). So: record-only
  grant, or make `main_session.writes` something a check actually consults?
- Q4 **NOT blocking, my answer is NO.** The lead asked to approve a clean re-dispatch of one pm.
  Decline: pm returned PASS, its amend is committed and parses. A re-dispatch would be a second pm
  against the same file — the exact #628 shape this feature prevents.
- Q5 **NOT blocking, needs pm.** `dec: DEC-129` on D-04 (`:151`) and D-10 (`:295`) miscites: DEC-129
  spans `DECISIONS.md:2946-2969` and contains **zero** occurrences of "approval" — it is about feature
  folders and `## Problem` before `## Goal`. The authority is **DEC-120 at `:2423`**. Same wrong
  citation at `team-config.yaml:90-91`.
- Q6 **NOT blocking — six files stay exposed, deliberately.** `run-unit-tests.sh:18` lists 14
  `INTEGRATION_SCRIPTS`; `integration.detect` names 6 explicitly, so **8** run as integration while the
  qa matrix reads them as unit — identical at `eea6f53` and on `origin/main`, so DEC-197 recorded the
  rule and fixed nothing. **T-10 closes only 2** — `test-validate-digest.py` (SC-08) and
  `test-check-domain.py` (T-14's criterion) — because those two carry evidence this feature's criteria
  rest on. The other six (`test-check-expertise`, `test-gen-decisions-index`, `test-bash-write-guard`,
  `test-harness-yaml`, `test-upgrade-config`, `test-merge-settings`) are untouched by design. Every
  `evidence: integration` claim elsewhere resting on those six is false today. Own dev-ops task?
- Q7 **NOT blocking.** SC-14's baseline (179 unit / 93 integration lines) was observed at `5d9b428`;
  FEAT-30 then added two runner files, so the counts moved. pm rebound the criterion to exit 0 plus
  absence of lines beginning `FAIL` rather than re-observing. Confirm that binding, or authorise a
  re-observation at the post-merge sha.
- Q8 **NOT blocking, verified at `eea6f53`.** `validate-digest.py:579-580`'s own comment names the
  `stop_hook_active` passthrough as `:838`; it is at **`:845`**. R5(d) inherited the stale anchor from
  the file's own comment and three tiers carried it. One-line comment fix in an enforcement-layer file,
  so `main-session-direct`.
- Q9 **NOT blocking.** DEC-174 am.4's list (`DECISIONS.md:4851-4853`) omits `dispatch-guard.sh`, which
  is demonstrably a gate — it refused this orchestrator's own dispatch this run over a `model:`
  parameter (DEC-152/DEC-155). "The category decides, the list records" makes T-07/T-08 correctly
  `main-session-direct`; the list should record it.
- Q10 **NOT blocking.** The orchestrator playbook says to record the phase in `feature.json` `phase:`,
  but `bin/feature-schema.json` sets `additionalProperties: false` with no `phase` property, so that
  write is invalid. The phase lives here instead.
