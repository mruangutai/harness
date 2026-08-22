# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch
- run: runs/fix1-eng (IN FLIGHT) · squad: eng · phase: build (DEC-192 deleted `phase` from
  feature.json; Q5 is issue #635)
- status: Building — cycle 4, fixing T-01's two confirmed defects
- budget: **cycles 4/10**, runs 8/20. Runs are INFORMATIONAL (INV-22); cycles are the hard bound.

**BOTH GATES PASS** — `BRIEF.md` and `plan.yaml` read `approved` / `operator` / `2026-08-21`. Q-SIGN
CLOSED: `notes/signature-reaffirmed-18-tasks.md` is the only record distinguishing a signature taken
at 14 tasks from one re-affirmed at 18, since `approval:` is byte-identical by design.

### THE OPERATOR'S TWO BLOCKERS ARE CLEARED — verified independently, not taken from the digest

- **T-18** — `harness.json` diffed key-by-key against HEAD: exactly ONE key changed
  (`test_kinds.integration.detect`), one path added (`.../test-context-watch-hook.py`), nothing
  removed, 17 entries to 18. `absent from detect 0`, `wrongly in detect 0`. **T-17 unblocked.**
- **T-16** — all 21 named cases pass (H1-H11, I1-I3, J-anchor/J-RED/J1-J3, K1-K7).
  `.claude/settings.json` **zero-diff**, so D-24 holds and the team lane is intact. **T-17 unblocked.**

### build2-eng: six tasks PASS first-pass, zero send-backs. THEN TWO REAL DEFECTS SURFACED

T-06 (14 named cases D-G), T-07 (10/10), T-08 (3 derived blind-spot lines), T-13 (8/8 verify lines)
all re-verified by the orchestrator. **T-07's `run-unit-tests.sh` edit is a clean single append** —
one entry added, nothing removed, order preserved, zero other lines changed.

### THE TWO DEFECTS ARE CONFIRMED AND LOCALIZED. T-01 AND T-02 BACK TO `building`

Sub-issues #642 and #643 REOPENED. `cycles_used` 3 to 4. Full diagnosis:
`notes/finding-discovery-depth-orchestrator.md` (defect 2) and `runs/build2-eng/digest.md`.

1. **`_build_row` contradicts D-11** (`context-watch.py:287-305`). Raised by eng-lead, confirmed by
   reading the source. `:294` appends **0** for a line with no `message.usage`; `:297` takes
   `current` from the file's last LINE, not the measured set's last MEMBER; `:305` counts `entries`
   as all parsed lines. `peak` is right only because zeros cannot affect a max. T-01's own `intent:`
   names this exact case and says "Do not do that."
2. **Discovery is ONE LEVEL TOO SHALLOW** (orchestrator, 4 sites). No-argument run prints `no
   orchestrators found`. At `fbee81f`: one-level glob **0**, two-level **2012**, of which **105** are
   `harness-orchestrator`. `verify-context-watch-live.py a7783f0ec41e6a8c6` says `no such agent`
   while that sidecar exists with a 3,275,314-byte transcript. Sites: `context-watch.py:317-320`,
   `:567-570`, `verify-context-watch-live.py:144-149`, **and every fixture**
   (`test-context-watch.py:103,173,207`, `test-context-watch-cli.py:72`,
   `verify-context-watch-live.py:266`) builds the same one-level shape.

**WHY 65 GREEN CASES SAW NEITHER: the tool, the tests and the fixtures all agree with each other and
all disagree with reality.** Defect 2 was documented days ago at `e5f88c4`; the plan clause was then
corrected and re-signed, **and the code was never rebuilt.**

**THE ORCHESTRATOR'S OWN ERROR, ON THE RECORD.** I re-ran T-01's verify block, saw both lines exit 0,
and recorded T-01 `done` — while this file's own heading said both defects STILL STAND. I trusted a
green gate over the standing record. T-01's verify line 2 is why: a tool that finds nothing ANYWHERE
satisfies `grep -qE "no orchestrator"` exactly as well as a correct one.

**This is a FIX CYCLE, not a plan change.** The lead escalated it as plan-level; that was wrong.
D-11 as corrected IS the approved spec and T-01's `intent:` already specifies the behaviour. Code
contradicting an approved decision is a bug fix; an approved decision being wrong is pm's.

### Three claims CORRECTED — do not act on the old versions

- **The `bash-write-guard.sh` heredoc hazard is FALSE as recorded.** Tested: a read-only `python3`
  heredoc containing `>` and `>=` in Python source runs CLEAN (`:390` masks quoted text, has a
  `(?<![0-9&<])` lookbehind and a `/dev/` skip). Q-GUARD's real half is the `sed -i` variable case.
- **`.harness/teams/build.yaml` DOES NOT EXIST** — only `.claude/skills/harness/teams/` has it.
- **Q-LIVEHALF's premise is FALSE.** A live orchestrator WAS running throughout build2-eng — the
  orchestrator itself. SC-01's live half is undischarged because discovery finds nothing.

### Premises the next cycle must not re-derive

- Worktree CURRENT with main: `feature-worktree.py behind --repo harness --id FEAT-31` exits **0** —
  **run from the PRIMARY checkout**; from inside, `dest_for()` re-inserts the path and exits 3 on a
  tree that is fine.
- **Zero UI surface** — all 21 planned files are Python, shell, JSON or markdown, so ui-reviewer
  self-scopes out of the panel.
- **Three of ten requirements are 100% main-session-direct**: REQ-04 (T-15), REQ-09 (T-14), REQ-10
  (T-10, T-14). The feature cannot reach goal-check without the operator's six tasks.
- **T-04 has NOT landed** — the template lacks `orchestrator_context_warn_tokens`, so T-05 and T-09
  remain blocked on it.
- **Q-ANCHOR re-measured at `fbee81f`, CONFIRMED**: DEC-174 content is at 4859-4862 and 4864-4867;
  the plan cites 4851-4854 and 4856-4859. Content correct, pointers 8 lines stale.
- 14 SCs, SC-01..SC-11 and SC-13..SC-15 — **there is no SC-12**.
- `check-state.sh`: 0 FEAT-31 problems; its one VIOLATION is FEAT-26's unapproved BRIEF.
- MISCONFIGURED cannot coexist with exit 0 (`run-unit-tests.sh:52-53` prints, then exits 2).

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING
SIGNAL, not a note: the orchestrator asks the user, writes the answers to
.harness/harness/features/<FEAT>/notes/answers-<runid>.md, and re-delegates with that path. Clear
each entry when it is answered.>

- **Q-RUTSH, non-blocking, TIME-SENSITIVE.** `run-unit-tests.sh` has THREE writers: T-07 (done,
  append verified clean) plus the operator's T-17 and T-12. The recorded T-18/T-17/T-12 ruling names
  only the latter two. T-07 has landed, so the file is settled and T-17 may proceed — **append
  only**. A rewrite of that array by either side silently drops the other's entry.
- **Q-VACUOUSFLOOR, NEW, non-blocking, GENERAL.** Any `verify:` floor derived from a PREDICTED
  assertion count is vacuous. T-16's `-ge 22` was already satisfied at 29 before T-16 wrote a line,
  because the plan assumed T-06 would add 4 cases when it added 14. Found independently by the lead
  and the orchestrator; T-16 was therefore verified by case NAME. Backlog, not this run.
- **Q-FOOTERCOV, non-blocking, FOLDED INTO fix1-eng.** T-08's three footer lines had zero committed
  coverage — `test-context-watch.py` was not in T-08's `files:`, so RED/GREEN used a throwaway probe.
- **Q-D21, non-blocking.** `D-21`'s `choice` was silently truncated 299 chars because ` ##` opens a
  YAML comment in a plain scalar — invisible to `safe_load` and so to every gate. Worth a corpus
  check for the same shape in other plans.
- **Q-DEC90, non-blocking.** `DEC-90` is STRUCK (`DECISIONS-INDEX.md:109`) but `BRIEF.md:247` cites
  it as a live `BLOCKS` constraint. BRIEF.md is approved; only the operator edits it.
- **Q-BRIEF231, non-blocking.** `BRIEF.md:231-237` says SC-07 changes `check-domain.sh`'s write
  route. Measured false — `:815` already calls `feature_schema.problems_for_text`, so the library
  write IS the cutover. Only a positional rule satisfies both halves of SC-07 (D-23).
- **Q-ANCHOR, non-blocking.** Re-confirmed above. `lanes.resolved_at` is still `7299669`
  (`plan.yaml:10`) while the new tasks resolve at `2cf792f`.
- **Q-GUARD, non-blocking, HARNESS DEFECT — SCOPE CORRECTED ABOVE.** Heredoc half disproven; the
  real defect is `sed -i` with a shell-variable target refused as out-of-domain.
- **Q-HOOKCTX, non-blocking until T-17, THE OPERATOR'S TO SETTLE.** Unverified: that hook stderr
  reaches the model as CONTEXT rather than only as a tool-result error string. If false, SC-13 is not
  met by this design.
- **Q-COLLECT, non-blocking, RECURRED.** A lead was force-closed with its member in flight; the
  member outlived it and wrote an artifact with no lead to assess it. Mitigation: confirm liveness
  from the sidecar transcript, never re-dispatch, verify the artifact mechanically.
