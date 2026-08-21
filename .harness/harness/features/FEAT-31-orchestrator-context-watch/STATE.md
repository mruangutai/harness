# STATE

## Current

- feature: FEAT-31-orchestrator-context-watch
- run: .harness/harness/features/FEAT-31-orchestrator-context-watch/runs/plan4-product/state.yaml
- squad: product
- status: plan-amended-awaiting-signature

**Round 3's six rulings have LANDED. `plan.yaml` is amended and UNSIGNED. The next act is the
operator's signature, and nobody below layer 0 may write it.**

plan.yaml went from 10 tasks / 16 decisions at 7299669 to **14 tasks / 22 decisions**, 81508 bytes.
`approval:` is byte-identical to 7299669 — verified by sha256 of the extracted block, not by claim
(`96666915d78504ef…` before and after). `BRIEF.md`'s `## Approval` likewise unchanged
(`4fac2b8b5d832525…` before and after); only SC-14's mechanism clause changed, -2/+4 lines.

Four new tasks, every one carrying `execution_mode`, and `T-10.depends_on: [T-14]` really encodes
the ordering the decisions declare:

- **T-11** `team`/`harness-dev-ops` — appends TEN explicit paths to `test_kinds.integration.detect`
  (the eight measured absent at 7299669, plus `test-context-watch-cli.py` for F-1's instance and
  `test-run-unit-tests-kinds.py` for T-12's own test). Closes the CLASS, not the instance.
- **T-12** `main-session-direct` — D-4's cross-check inside `run-unit-tests.sh` plus `--check-kinds`
  and a new test. Its red proof asserts a `KIND-DRIFT` line NAMING the file, and treats a bare
  non-zero exit as INCONCLUSIVE.
- **T-13** `team` — SC-01's live half, `verify-context-watch-live.py`, deliberately NOT named
  `test-*.py` so the drift detector's `for f in "$BIN_DIR"/test-*.py` never reaches it (C-1's door).
- **T-14** `main-session-direct` — INV-17 shape-checks every `notes/handoff-*.md` by glob, with the
  shape check MOVED OUT of the `SEAM_NOTES` loop so C-3's double-report is impossible by
  construction. Runs BEFORE T-10.

Independently verified by the orchestrator, not taken from the pm's receipt: plan.yaml parses via
`harness_yaml.load_file`; `check-plan-routes.py` exits **0** with **0 violations across 4 plans**,
30 feature dirs examined, and FEAT-31's T-01..T-14 all enumerated; T-11's own `verify` executed
today exits **1** naming exactly the eight files, so it is discriminating rather than vacuous; and
all **69** handoff notes in this worktree pass the four headings, the 60-line cap and T-10's
empty-body rule, so T-14's widened glob adds zero violations.

`check-state.sh`'s only FEAT-31 line is now the expected `plan.yaml approval is pending — awaiting
the user`. The two orphaned-run-dir notes were closed by recording plan3-product and plan4-product
in feature.json.

**Do not dispatch another `harness-pm`.** The single-writer constraint (issue #628) held this round,
but only barely: the product lead spawned a SECOND pm by mistake and logged it itself as
"LEAD ERROR". It returned BLOCKED with 0 tool uses and wrote nothing — verified at the time,
plan.yaml still 41503 bytes and clean-tracked. The constraint held because that spawn declined to
act, NOT because any mechanism stopped it.

## Open Questions

<The channel from subagents to the user. A non-empty entry is an ACTIVE ROUTING
SIGNAL, not a note: the orchestrator asks the user, writes the answers to
.harness/harness/features/<FEAT>/notes/answers-<runid>.md, and re-delegates with that path. Clear
each entry when it is answered.>

- Q-A, non-blocking, DEFAULT ADOPTED and overrulable in one read. Is `harness.json`'s `test_kinds`
  enforcement layer under DEC-174? Adopted in D-22: the data entries are `team`/`harness-dev-ops`
  (T-11), the new check and its test are `main-session-direct` (T-12). Rests on `DECISIONS.md:4851`
  ("So the enforcement layer is … and the test file of each … the category decides, the list
  records") and `:4856` ("a module a gate imports is not itself a gate"). Three corroborations:
  `check-domain.sh --resolve .harness/harness.json` returns `harness-dev-ops` alone; T-03 already
  edits that file as `team`; and ruling otherwise retroactively invalidates T-03's lane.
- Q-B, non-blocking. Is "explicit list beats catch-all glob" written down anywhere? Four files sit
  in both `unit.detect` and `integration.detect` at 7299669 and are treated as integration, so
  precedent is clear, but it is stated nowhere and there is no programmatic classifier. T-12 was
  deliberately designed so its CORRECTNESS does not rest on it (a set comparison, no glob matching)
  — but the FIX's meaning still does. Recommend writing it down as a decision.
- Q1, non-blocking. An orchestrator cannot collect a lead that outlives its turn: this persona holds
  Read/Glob/Grep/Agent/Write/Bash — no message tool and no wait that terminates. Two rounds died to
  exactly that. The working mitigation is ORDERING: dispatch early, spend the wait on read-only
  verification. Still wants the operator's ruling on a collection protocol.
- Q2, non-blocking. `check-domain.sh`'s feature.json schema REJECTS a `phase` key
  ("undeclared key 'phase'"), while the orchestrator playbook instructs recording the phase there.
  One of the two is wrong. Not blocking; the phase is recorded in this file instead.
