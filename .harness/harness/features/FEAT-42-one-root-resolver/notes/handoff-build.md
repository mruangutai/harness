# Handoff — build → validation, FEAT-42, 2026-08-27

## Next

- Run the QA gate and the review panel over the diff from `ea71a1c` to HEAD. Nothing has
  reviewed this build: every task was executed and verified by the main session alone under
  DEC-174, which removes the squad but not the need for independent eyes.
- Read `notes/verify-technique-2026-08-27.md` first. Three of the six parity proofs passed for
  the wrong reason before it was written, and the same three traps are the ones a reviewer
  should re-derive rather than take on trust.
- The two red receipts are `notes/receipt-main-session-T-17.md` and
  `notes/receipt-main-session-T-18.md`. Both were taken against sha-`8439002` copies through
  the test seams, so no live hook was ever in an intermediate state. Re-run them.

## Trust

- The full suite: `run-unit-tests.sh --kind all` exits 0 with 1040 verdict lines and zero
  failures, against 1013 and zero at the pre-feature baseline `a1658c2`.
- The zero-occurrence invariant is real, not decorative. `test-no-distribution.py` case 6
  scans every tracked source file from `git ls-files`, and its mutation proof plants a chain
  line in `docs/invalid-states-audit.html` — outside `bin/` deliberately, so only the widened
  scan root can see it. The mutant is asserted on disk before the suite runs and the failure
  must name that file.
- `check-state.sh` and `check-plan-routes.py` both report zero violations.

## Dead ends

- Adding `HARNESS_PROJECT_DIR` to a fixture and stopping there. `resolve_root` honours the
  override ONLY when `.harness/team-config.yaml` is readable underneath it, so a fixture
  without the marker silently falls back to the live checkout. Nine test files hit this.
- Grading a parity proof with `test -s`. Six blocks captured `^(PASS|FAIL)` while those suites
  print `ok`, so a ONE-LINE before-set satisfied the check and the diff compared one line
  against one line.
- Exporting a root override around a suite that sets its own per case. It is inherited through
  `dict(os.environ)` and outranks each case's redirect; 40 of 87 cases failed that way.
- Writing the dispatch rule into `.claude/agents/*.md`. Those are generated adapters; running
  `sync-agent-adapters.py` deletes anything not in `.omp/agents/`.

## Working set

- The resolver: `.claude/skills/harness/bin/harness_boundary.py` — `MARKER`, `resolve_root`,
  `root_above`, `root_from_script`.
- The nine gates that were cut over, all in `.claude/skills/harness/bin/`.
- The invariant: `test-no-distribution.py` case 6.
- `STATE.md` carries five open questions, three of which are harness defects this feature
  surfaced and does not fix: `bash-write-guard`'s angle-bracket refusal, `gh-sync`'s missing
  per-task finish command, and `validate-digest` releasing a claim before refusing the return.
