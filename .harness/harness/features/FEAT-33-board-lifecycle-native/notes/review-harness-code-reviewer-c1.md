# Code review — FEAT-33 board-lifecycle-native — c1 (re-check)

**VERDICT: PASS.** `severity_max: medium`. Reviewed `e8a6058..<worktree, uncommitted>` (`feature.json`'s
`review_sha` is still `e8a6058`; the fix cycle's changes are unstaged edits on top of it — no new
commit, no `[harness:human]` commit since the pin). All three c0 findings are closed, each verified
against the code and the new tests, not against the receipt's prose. Two new, non-blocking findings
surfaced during the adversarial re-check (below) — neither gates.

## c0 findings — status

### 1. `cmd_provision` create-then-link ordering (was high) — **CLOSED**

`board_lifecycle.py:517-533`. `_out("... created project {number} ...")` now runs immediately
after `project_create` returns, before `project_link_repository`. A link failure is caught locally
and exits **4** (never 2, never 3), with a stderr line naming the created number and instructing
the operator to record it now. Verified by reading the code directly (not the receipt) and by the
new case at `test-board-lifecycle.py:485-509` ("MUST-FIX 2"), which passes: `rc=4`, `"created
project 42"` present in stdout, `42` and `acme/widget` present in stderr. The RED claim (pre-fix:
`rc=2`, empty stdout) is independently derivable from the pre-fix diff hunk itself — the old code
had exactly one `_out(...)` call, positioned *after* `project_link_repository`, so a raised
`GhError` there skips that print entirely and reaches `factory_cli.run`'s generic trap (exit 2).
No need to swap files and re-run to trust this; the control-flow difference is sufficient.

### 2. `cmd_retitle` apply loop uncaught (was high) — **CLOSED**

`board_lifecycle.py:933-944`. Each `run_gh(["issue", "edit", ...])` call is now wrapped in
`try/except factory_gh.GhError`, counted as `failed`, printed to stderr, and the loop continues.
`--apply` exits 1 iff `failed > 0`. Verified against `test-board-lifecycle.py`'s "MUST-FIX 3" case
(`fail_match="401"`, two renamable tickets): #402 is still renamed despite #401's failure, `rc=1`,
summary reports `renamed: 1` and `failed: 1`. Ran this test directly — passes. The dry-run path
(`if not apply: ... return`, above the fix) is untouched by the diff (confirmed by `git diff`
hunk boundaries) and still exits 0 unconditionally once detection succeeds.

### 3. SC-15 `SKILL.md` naming gap (was medium) — **CLOSED**

`.claude/skills/harness/SKILL.md:199` (diffed against `e8a6058`) now reads: *"by `execution_mode`
of the phase's own work: the **orchestrator** for a phase it is running, the **main session** for
a phase it holds itself — plan, ship acceptance, and any `main-session-direct` segment."* Matches
every other row's naming convention in the same table. Confirmed by direct `git diff`, not by
re-reading the receipt's claim.

## Answers to the five questions

**Q1 — is exit 4 the right code, and unambiguous?** Within `board_lifecycle.py` itself, yes: 4 is
reused consistently for "a `GhError` this module could not swallow," and `reconcile`'s own
*residual* re-check (`board_lifecycle.py:830-834`) already fires exit 4 *after* the apply loop has
attempted real writes — so the fix's new use (exit 4 after a real mutation landed) is not a novel
meaning inside this file; it already existed. This is a distinction without a difference at the
`board_lifecycle.py` level.

It is **not** unambiguous one level up. `harness-init/SKILL.md:217-220` is the one place in the
codebase that documents `provision`'s exit codes for an operator running onboarding: *"0
provisioned or already correct. 2 the declaration is unusable... 3 a NEW project was created, and
its number must be written into `harness.json` **before anything else runs**."* This text predates
the fix (last touched by commit `7d3c539`, T-13) and was **not updated** by this fix cycle — `git
diff e8a6058 -- .claude/skills/harness-init/` is empty. Exit 4 is now a real, reachable outcome of
`provision` that carries the exact same "record the number now" urgency as exit 3, and the one
document written to walk an operator through this exit code contract doesn't mention it. The
critical instruction still reaches stderr (the fix's own message names the number), so this
doesn't reopen the duplicate-board disaster by itself — but it is a genuine completeness gap in the
surface meant to prevent that disaster. **Medium**, non-blocking.

**Q2 — is the print-before-mutation ordering complete?** One more class of the same defect shape
remains, at lower severity than the fixed one. `project_single_select_create`
(`board_lifecycle.py:562`) and `project_single_select_extend` (`:580`) are still unwrapped: if
either raises a `GhError` after the mutation actually landed server-side (lost response), the run
exits 2 ("nothing mutated" — false) with no success line. Unlike the fixed `project_create` +
`project_link_repository` pair, this does **not** amplify into a duplicate on retry: both paths are
gated by a live re-probe (`_field_probe`, `project_field_options`) rather than a number an operator
must manually copy into `harness.json`, so a retry finds the field already present/extended and
self-corrects (recomputes `missing` as empty, or takes the extend branch instead of create). Real,
same-class, bounded blast radius. **Low**, non-blocking — noted because the dispatch asked
specifically whether a second instance exists, and it does, just not the disaster-amplifying kind.

**Q3 — does retitle's exit-1-on-failure collide with anything?** No new collision. `--dry-run`
(default) is untouched — confirmed by diff, exits 0 unconditionally once detection succeeds, zero
writes. `--apply` with a mix: `renamed` and `failed` are independent counters: some renamed + zero
failed → exit 0; any failed → exit 1, regardless of how many renamed or refused-for-no-milestone.
This exactly mirrors `reconcile`'s own precedent (`cmd_reconcile:842-843`, `if fixable_residual:
sys.exit(1)`) — both already override `factory_cli`'s canonical "exit 1 = nothing to do" meaning
for this control-plane tool, which DEC-186 already licenses as this tool's inverse-of-the-mirror
posture. Not a new deviation.

**Q4 — do the three failure-injection tests discriminate for the right reason?** Yes, confirmed
structurally, not merely by trusting the receipt's RED transcript. Ran the current suite directly:
`test-board-lifecycle.py` all cases PASS (including the three new ones), `test-factory-integration.py`
131/131. For each new case, the pre-fix control flow (visible in the `-` lines of `git diff e8a6058`)
makes the RED outcome the receipt reports the only possible outcome, not an artifact of a stale
file: MUST-FIX 2's old code had its one success-print positioned after the risky call, so a raised
exception skips it entirely (stdout empty); MUST-FIX 3's old loop had no per-iteration catch, so an
exception at #401 aborts before #402 is attempted at all; MUST-FIX 1 has no pre-fix analogue
(`_project_linked_repos` didn't exist), so of course the mutation reached the fake with no guard.
None of these are "the file is merely older" — each hinges on a specific control-flow fact that a
diff read, not an execution, already settles.

**Q5 — did the fix weaken anything confirmed sound in c0?** No. Re-ran the relevant cases directly:
`project_single_select_extend`'s union case (`test-board-lifecycle.py`, "missing options" case) and
the SC-08 no-"Abandoned"-substring case both still PASS, unaffected by the new linkage guard sitting
upstream of them. `audit`/`reconcile`'s exit-4 `GhError` cases still PASS. Both #783 cross-repo
self-skip regression guards (audit + reconcile) still PASS. SC-20/INV-26 is untouched — no
`check-state.sh` change appears anywhere in `git diff e8a6058 --stat`.

## New findings (non-blocking)

1. **[medium]** `harness-init/SKILL.md:217-220`'s documented exit-code contract for `provision`
   (0/2/3) was not updated for the new exit 4 introduced by this fix cycle. See Q1.
2. **[low]** `project_single_select_create`/`project_single_select_extend` remain unwrapped inside
   `cmd_provision`; a lost-response `GhError` after either lands still reports exit 2 falsely, though
   self-correcting on retry. See Q2.

Neither is a `must_fix`: both are real but bounded, and the code review protocol's own gating rule
(`must_fix` non-empty or `severity_max >= high`) is not met by either.

## Out of scope for this re-check (flagged for the record only)

- `.harness/harness/features/FEAT-33-board-lifecycle-native/feature.json`'s `status`/`review_sha`
  transition and `.harness/harness/features/FEAT-34-worktree-act3-enforced/BRIEF.md`'s approval
  stamp are both in the working tree but unrelated to `board_lifecycle.py` — orchestration
  bookkeeping and a different feature's approval, not this fix cycle's surface.
- QA's c0 note (`review-harness-qa-c0.md`) raised a live `check-state.sh` INV-17 finding (missing
  `notes/handoff-build.md`) against this feature's own `feature.json` state. Not something my three
  c0 findings named, not something this fix cycle addressed, and not board-lifecycle code — belongs
  to the orchestrator/build-lead, not to this review.
- The security reviewer's own c0 `open_questions` (trust-domain acceptance for the confused-deputy
  gap) is that reviewer's item to close, not mine; the fix (MUST-FIX 1 in the receipt) is the code
  change they asked for and it verified sound above.
