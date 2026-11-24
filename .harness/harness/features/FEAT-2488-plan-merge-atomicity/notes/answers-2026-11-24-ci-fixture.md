# Ruling on the post-ship CI fixture fix — FEAT-2488 — 2026-11-24

Ruled by fable-advisor (AdvisorE8CI) under the operator's delegated approval.

- **Merge on the existing validation, with disclosure.** review_sha stays 45f16cfa and the signature stands. Merge on the PR's own CI going green again.
- **No backlog row.** A sys.stdout object that is already closed at startup can't be produced from outside the process.

## Ship-record addendum
On Linux Python 3.14, CI integration shard 4 failed on 2488/n stdout=closed,stderr=working for both verbs.
- **Cause:** the fixture closed the sys.stdout object before startup, and 3.14 argparse calls isatty() on it for colour while building the parser, unless NO_COLOR or TERM=dumb is set. The CLI crashed before the commit with nothing written.
- **Fix:** b2d5361f, test-only. The fixture now closes the streams after parse_args returns and before the commit.
- **Evidence** in notes/ci-py314-fixture/:
  - 25 closed-cell PASS lines in each green log (3.14 and 3.15, without NO_COLOR);
  - the ValueError-less mutant turns 15 closed-cell checks red, plus the file verdict.

The first report gave 22 and 12. Those counts came from greps that measured something else; the numbers above match the logs.

## Full ruling (verbatim)

Verified in W before ruling: the fixture diff (`git show b2d5361f`, tests/integration/test-plan-merge.py:5284-5297), production parity (`git diff 45f16cfa..HEAD --name-only` → only the test file plus FD notes; plan.yaml untouched), the evidence logs (25 PASS lines containing "closed" per green log on 3.14 and 3.15; the ValueError-less mutant turns 15 closed-cell checks + the file verdict red — the brief's "22"/"12" counts are off, the discriminating-power claim is not), and the only production `runpy.run_path` (harness_boundary.py:637-640, `run_hook_body` — hooks only, never the merge CLI).

# Ruling — post-ship CI fixture correction (b2d5361f on pin 45f16cfa)

## Q1 — Mergeable on the existing validation, with disclosure. No re-pin, no re-validate.

**Authority.** The ship ruling's own evidence basis: validation at 45f16cfa measured the post-commit stdio contract ("after commit, no state of stdout/stderr may change the exit code, double-apply the write, or misroute output"). INV-33 untriggered — plan.yaml untouched, confirmed by the diff file list.

**Gap.** The old fixture closed the stream objects before startup. On the validation hosts (NO_COLOR set) that was a *strictly harsher superset* of the contract window — startup, parse, commit, and post-commit all ran closed, and passed. So the green evidence behind the SHIP ruling remains valid for every production claim; what broke on CI was the harness's accidental dependence on colour-env, not the contract. The new fixture closes after `parse_args` returns — still before the commit, so the post-commit cells assert the same state at the same writes — and the mutant proves the cells still discriminate.

**Ruling.** Test-only, production byte-identical to the validated pin, assertion window still inside the class contract, discrimination re-demonstrated. This is a harness correction, not new evidence about the product: mergeable with disclosure. review_sha stays 45f16cfa; the signature stands.

**Constraints.** (a) The authoritative green is the PR's own CI shard rerunning on the corrected fixture — merge on that, not on the local logs (the local repro/green logs are the fixer's own runs; CI re-green is free and independent). (b) Ship-record addendum, one entry: CI shard-4 failure, cause (3.14 argparse `isatty` colour probe on a pre-startup-closed object), commit b2d5361f, evidence path `FD/notes/ci-py314-fixture/`. (c) Correct the counts in that addendum to what the logs actually show (25 closed-cell PASS lines per green log; 15 checks + file verdict red under the mutant) — the record should match its evidence.

## Q2 — Out of contract, and out of production reach. No backlog row.

**Authority.** The c3 class contract is post-commit by its own words; disclosure #1 already prices the fd-level pre/post-startup family (fd 1 closed after startup → exit 120 after landing, base parity).

**Gap.** Could production ever present a closed `sys.stdout` *object* at startup?

**Ruling.** No. External callers control file descriptors, not Python stream objects; fd 1 closed at exec gives `sys.stdout = None`, which is the matrix's existing "none" cell (produced via `1>&-` in `_stdio_command`, test-plan-merge.py:5315-5319) — green at the pin. A closed object pre-startup exists only for an in-process embedder, and the one production `runpy` embedding path (harness_boundary.py `run_hook_body`) runs hooks, never the merge verbs — verified by grep across the worktree excluding tests. Even in the counterfactual, the failure is pre-commit, nothing written, no journal: the fail-closed side of the atomicity contract, which is the side the feature is allowed to crash on. **No backlog row.** A new ticket here would be work the user doesn't have; the ship-record addendum from Q1(b) is the right and sufficient trace. At most, fold one sentence into the BL-4 ticket text: pre-startup object states are out of contract because they are unreachable from outside the process — so BL-4's matrix additions don't drift into asserting them.

**One adjacent note, distill-grade, not a gate:** the parity miss happened because the local host sets NO_COLOR and TERM=dumb — the parity run's environment silently differed from CI's. The fixture fix removes *this* sensitivity, but the lesson generalizes: a parity run claiming CI equivalence should pin (or diff) the env vars the interpreter consults. That belongs in the fixer-persona distill row, not backlog.

Where the brief is right, briefly: the cause analysis matches the diff and the 3.14 behavior change [the argparse colour-probe mechanism itself I verified only via the repro logs and commit evidence, not CPython source — [unverified] at that level]; "the window the class contract covers" is accurately stated in the new fixture's comment; INV-33 reasoning holds.
