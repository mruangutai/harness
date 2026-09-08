# STATE

## Current

- feature: BUG-124-run-dir-squad-suffix
- run: [.]harness/harness/features/BUG-124-run-dir-squad-suffix/runs/2026-09-07-4-validator/state.yaml
- squad: validator
- status: in_progress

**THE BLOCKING QA GATE IS CLOSED.** `matrix_ok: true`, `must_fix: []`, at `418a9eb6`. Eng and qa
segments are both complete. Station `building`; T-01 and T-02 `building`; T-03 still `ready` and
correctly undone. `cycles_used: 7` against budget 10; eleven runs against budget 20. No
`review_sha` exists and none is owed until the seam, AFTER simplify.

**Next (cited to plan.yaml):** the SIMPLIFY segment — to `harness-eng-lead`, NOT the validator lead.
Its dispatch MUST tell the lead to read `.agents/skills/harness-simplify/SKILL.md` first; it is not
preloaded, and the four angles, the apply rules and the one-fix ceiling all live there. Re-run the
suites after any apply. An empty pass is a real outcome. THEN, and only after simplify, pin
`review_sha` and run `gh-sync.py status <feature-dir> review` before the panel is dispatched — an
apply commit after the pin moves the tip and invalidates the panel's verdict.

**The cycle-3 defect and its fix, settled.** qa c3 ruled `matrix_ok: false`: four integration
suites red, root-caused to T-01's bare top-level `import harness_yaml` at `harness_boundary.py:22`
crashing under `python3 -I` in synthetic fixtures that copy `harness_boundary.py` without
`harness_yaml.py`. Run `2026-09-07-3-eng` made the import lazy inside `run_dir_grant_globs`'s
pre-existing `try:`/`except Exception: return []`. That run also SUPERSEDED qa c3's attribution of
the fourth file (`test-check-domain.py` sweep/clean-tracked): it was a fourth masked instance of the
one defect, not an independent pre-existing failure. Four files, one cause. `qa-c3.md` was
deliberately NOT rewritten — the supersession is recorded in the 3-eng digest and in `qa-c4.md`.

Trust (claim — pointer — verified-at `418a9eb6`, ORCHESTRATOR-MEASURED unless attributed):
- **The fix holds. I re-ran the full sweep myself rather than trusting the prior claim:**
  `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh` from the worktree
  root → `RUNNER_EXIT=0`, `grep -c '^FAIL '` = 0, 5403 output lines, pool `8 workers, 80 files`.
  Exit status captured into a variable, not tail-read; discovery volume checked, not just the code.
- **The suite CAN report red — re-derived BY ME at this commit**, closing the one adequacy gap qa
  named. `tests/integration/test-dispatch-guard.py` exits 0 with 0 FAIL against the current guard;
  against the main checkout's pre-change copy (`DISPATCH_GUARD_BIN=...`, md5
  `ca904b2906ad8d44662db428cb2dbc89`) it exits 1 with exactly 8 FAIL: 18a (x2), 18b, 18g,
  21-message, 22 (x2), 23-message. qa's adequacy note called this carried-forward from cycle 1; it
  is no longer carried forward.
- qa's own gate (`notes/qa-c4.md`, 116 lines; `runs/2026-09-07-4-validator/digest.md`): both
  required kinds satisfied by their configured commands, all four cycle-3-red files individually
  green, 80/80 files discovered. Run state.yaml reads `status: complete`, step `qa-gate-c4`
  `complete`/`PASS` — disk-confirmed, not taken from the digest.
- ATTRIBUTED (eng lead, `2026-09-07-3-eng`): `import harness_yaml` matches exactly once in
  `harness_boundary.py`, at the lazy site inside the `try:`. `run_dir_grant_globs`'s signature,
  return and never-raises promise are unchanged. House precedent is `bash-write-guard.sh:45`.
- Earlier trust from the eng segment stands unchanged at this commit: T-01 and T-02 `verify:` both
  exit 0; both test files purely additive (183/0 and 115/0); `harness_boundary.py` gained no
  changed symbol at T-01; operator signature on disk at `80ce35d1` (BRIEF `approved`, plan
  `approval.status: approved` with five `rulings` overruling R-1..R-5).
- Record reconciled this cycle: three runs executed on disk were absent from `feature.json`
  (`2026-09-07-02-eng`, `2026-09-07-3-eng`, `2026-09-07-4-validator`) and are now appended.
  `cycles_used` 5 → 7, which reconciles exactly: 1 (plan-panel FAIL routed) + 1 (2-validator FAIL
  routed) + 3 (3-validator: 2 internal send-backs + 1 routed) + 2 (3-eng lead-reported send-backs).
  The c4 gate reported 0.

Dead ends for the next phase:
- Do NOT re-litigate R-1..R-5 (operator `approval.rulings`), the Q1 test-first ordering ruling, the
  `unit` kind ruling, the three `bugfix` predicate evaluations, the assertion-strength review, or
  the four behavioural-equivalence rulings. All closed across cycles 1–4.
- Do NOT rewrite `qa-c3.md` to reflect the corrected attribution. Rewriting a recorded artifact to
  look better falsifies the record; the supersession lives in the 3-eng digest and `qa-c4.md`.
- Do NOT hand T-03 to a squad: `execution_mode: main-session-direct`, and `check-domain --resolve`
  answers NOBODY for `.claude/skills/harness/SKILL.md`. It is a pre-ship main-session step, not a
  matrix gap and not incomplete work.
- Do NOT `cp` a fixture into `/tmp` or a scratch worktree to build an A/B — `bash-write-guard.sh`
  refuses it, and cycle 3 already burned a step discovering that. Pointing `DISPATCH_GUARD_BIN` at
  the main checkout's pre-change guard is the working route.
- Do NOT pin `review_sha` before simplify lands; an apply commit after the pin invalidates the pin.
- Do NOT edit `plan.yaml` by hand; `plan-merge.py` is the only write route and `approval:` is the
  main session's alone.
- Do NOT run the suites without `env -u HARNESS_AGENT_TYPE`; the tool's env leaks into test
  subprocesses and reddens the plan-merge approval checks as a phantom regression.
- The plan-phase handoff note still cannot be written (Q2b below). This `## Current` is the
  supported disk-only substitute.

Working set: plan.yaml (tasks at 231; T-03 at 491), notes/qa-c4.md,
runs/2026-09-07-3-eng/digest.md, .claude/skills/harness/bin/harness_boundary.py,
.claude/skills/harness/bin/dispatch-guard.sh

## Open Questions

- Q2 (harness defect, one class, two symptoms, both diagnosed, both for the harness owner):
  worktree-hosted features are graded against the OWNER checkout root. (a)
  `handoff_done_when.problems()` receives the owner root while the note's feature-dir prefix comes
  from its own worktree-relative path (handoff_done_when.py:11,51-54), and an absolute pointer is
  separately refused as "is absolute" (:69-70), so there is NO legal spelling and no handoff note
  can be written at all. (b) `check-state.sh` globs the owner checkout's `.harness/*/features/*`
  (:118-120), so a full run from inside this worktree cannot grade this feature.
- Q5 (harness defect, raised by qa at the c4 gate, non-blocking, NOT a BUG-124 fix cycle):
  `test_matrix.bugfix`'s third leg `{__bug_class__, if: match_bug_class}` is structurally
  unresolvable in this project — no bug-class taxonomy exists for the predicate to match against,
  so the leg contributed nothing to any of the four BUG-124 gates. Pre-existing harness-config
  condition; belongs to the harness owner.
- Q3 (advisory, no task): three pre-D-05 artifacts keep raw anchored `eng-t01` paths
  (`runs/goalcheck-plan-product/digest.md:11`, `runs/planpanel-validator/digest.md:19`,
  `notes/research-BUG-124-goalcheck-plan-c0.md:67`). Pasting one verbatim into a dispatch will be
  refused once the change reaches the main checkout — recoverable in one re-spelling. Left as-is on
  purpose: rewriting a recorded artifact to look better falsifies the record.
- Q4 (operator, already accepted at signature): T-02's SECOND parse of `team-config.yaml` inside the
  derivation subprocess. It shipped as designed and is what makes case 23 distinguishable from
  case 21.
- CLOSED this cycle: Q1 (T-02 test-first authoring order) — ruled in cycle 3, stands. The eng lead's
  Q1 (should qa-c3.md carry a superseding note) — answered NO, see Dead ends.
