# BRIEF — FEAT-05 PyYAML file parsers

## Problem

Six harness scripts read `.yaml` state with hand-rolled regex, and a regex encodes one serialization
of a format that has many. Issue #11 is the live instance: `check-state.sh:109`'s run parser requires
`\s*\n` after the `id:` and `squad:` captures, so a trailing `#` comment — legal YAML, and the house
style elsewhere in the same file — makes the match fail and drops the **entire run** from `runs`. That
silently fails open on INV-6, INV-7 and INV-8 at once, exit 0, no message. It has not fired only
because those two lines happen to carry no comments today; one author who hit the class wrote a
warning into the data file (`FEAT-03-subissue-mirror/feature.yaml:63-64`) rather than fix the parser.
The same defect class is documented five more times in `validate-digest.py:247-272` and twice in
`check-state.sh:105-107`. The scripts whose whole job is catching fail-open bugs are themselves a
recurring source of them.

## Goal

Every harness script that reads a `.yaml` file gets its values from a real YAML parser, so a legal-YAML
variant an author writes can never again silently void an invariant. PyYAML stops being optional: it
becomes a stated prerequisite that init enforces, with no second code path anywhere, so the brittle
regex leaves the tree instead of living on as a fallback nobody exercises. Issue #11 closes as a
consequence of the sweep, not as its point.

**Non-goal (one line):** the DIGEST ```` ```yaml ```` fence and the `validate-digest.py` conversion are
Feature 2 (DEC-172), which is blocked on this feature and is not planned here.

## Requirements

- REQ-01: Every `.yaml` read in `check-state.sh`, `gh-sync.py`, `cost-report.py`, `upgrade-config.py`,
  `check-domain.sh` and `bash-write-guard.sh` gets its values from a real YAML parser, and no
  hand-rolled YAML key/value regex is left behind in those scripts.
- REQ-02: A run entry whose `id:` or `squad:` line carries a trailing `#` comment is read correctly and
  its invariants are evaluated, instead of the run vanishing from `runs`.
- REQ-03: PyYAML is a stated, enforced prerequisite of running the harness: a machine without it is
  told so loudly, at install time, together with the exact action that fixes it.
- REQ-04: When PyYAML is absent, the two PreToolUse write hooks refuse the write rather than allowing
  it with enforcement silently off.
- REQ-05: An existing checkout that pulls this change without PyYAML can still recover from inside the
  tool — the first session that hits the missing library is told how to fix it and is not prevented
  from doing so; the permissive state does not persist beyond that session.
- REQ-06: Values that a real parser returns as non-strings are handled correctly by every consumer of
  them, so the conversion does not trade a silent fail-open for a new crash.
- REQ-07: The harness's own state check still passes on this repo after the conversion, with no
  invariant newly firing and none newly silenced.

## Constraints

- **PyYAML is required. No fallback path.** No line-scan alternative, no guarded import that continues,
  no degraded mode in any converted script. This reverses DEC-171's graceful-degradation clause; DEC-171
  amendment 1 is the operative text, not the original body.
- **The requirement is enforced as a seventh entry in `harness-init`'s existing six-prerequisite HARD
  GATE** (`.claude/skills/harness-init/SKILL.md:38`). Not a `requirements.txt` — nothing in the harness
  would read one, and it would be the first dependency manifest in a files-only repo. No
  `requirements.txt`, `pyproject.toml` or `package.json` exists at repo root today.
- **The hooks fail CLOSED on a missing PyYAML**, a deliberate exception to DEC-101's fail-open rule
  (DEC-171 am.1). The bootstrap escape is the only exception, and it is one session wide.
- **Do not pin `/usr/bin/python3`.** Apple's Python ships PyYAML 6.0.1, which makes pinning look free;
  it is macOS-only and deprecated for scripting, and pinning it breaks Linux, CI and the distributable
  package. The hooks invoke a bare `python3` resolved off PATH and must keep doing so.
- **PEP 668 rejects a plain `pip install` on the Homebrew interpreter** (`--dry-run` names
  `--break-system-packages` as the override). Whatever install command the gate prints has to actually
  work on a PEP 668 interpreter — see Q2.
- **This repo is self-hosted.** The moment these scripts `import yaml` they gate every agent write on
  the build machine, and DEC-171 am.1 removed the fail-open that used to absorb a breakage there.
  PyYAML must be importable by the hooks' `python3` before the converted hooks land.
- **Out of scope, hard:** `validate-digest.py` and the DIGEST fence (Feature 2); issue #10 (a
  `change_type` vocabulary gap, same file, different defect); and the non-YAML regex in
  `check-state.sh` — the `CHECKPOINT_KEYS` whitelist at `:279` and the `T-\d+` markdown scan at `:89`.
- Budget: `per_feature_usd` 120, unraised. Cost is reported, not gated (DEC-134).

## Success Criteria

- SC-01: A run entry whose `id:` line and a run entry whose `squad:` line each carry a trailing `#`
  comment both appear in `runs` and have INV-6/INV-7/INV-8 evaluated against them; the identical
  fixture is shown to drop the run and exit 0 on the pre-change parser.
  verify: automated        evidence: unit
- SC-02: `.claude/skills/harness/bin/check-state.sh` run against this repo's real `.harness/` exits 0
  with zero violations after the conversion, matching the pre-change baseline (exit 0, zero violations,
  output is INV-8 notes about pruned run dirs only).
  verify: inspection
- SC-03: Each of the six named scripts reaches PyYAML on every one of its `.yaml` read paths, and the
  only regex calls remaining in `check-state.sh` are the two out-of-scope non-YAML ones
  (`CHECKPOINT_KEYS` at `:279`, the `T-\d+` markdown scan at `:89`). Reviewer cites each remaining
  regex call in the six files by `file:line` and classifies it.
  verify: inspection
- SC-04: No converted script contains a second parse path for the same data — no `try: import yaml /
  except ImportError:` that continues, no line-scan fallback, no branch selected on parser
  availability. (The absence half of SC-03; both are required, per DEC-169.)
  verify: inspection
- SC-05: Invoked exactly as the PreToolUse hook is invoked — subprocess, inherited PATH, bare `python3`,
  no venv activation and no `PYTHONPATH` override — `check-domain.sh` **allows** a manifest-permitted
  write **and blocks** a manifest-forbidden write in that same invocation context. Both outcomes are
  required: either one alone is also produced by a bootstrap-escape allow-all or a fail-closed
  block-all, and only a real parse of the manifest produces the pair.
  verify: automated        evidence: unit
- SC-06: The same paired assertion holds for `bash-write-guard.sh`: a permitted `bash`-issued write is
  allowed and a forbidden one is blocked, in the hook's own invocation context.
  verify: automated        evidence: unit
- SC-07: `harness-init`'s step-1 HARD GATE carries a seventh prerequisite that checks the PyYAML import
  and STOPs with an exact, runnable install command when it fails; and no dependency-manifest file
  (`requirements.txt`, `pyproject.toml`, `package.json`) has been added at repo root by this feature.
  The second half is a guard-rail against this feature's own regression, not evidence on its own —
  none exists today.
  verify: inspection
- SC-08: On a machine whose hook `python3` cannot import yaml, the **first** hook invocation permits the
  write and emits the install command on a channel the user sees. No write is blocked in that session.
  verify: automated        evidence: unit
- SC-09: With PyYAML still absent, a **later** session's hook invocation blocks the write instead of
  permitting it. The escape expires; the steady state is closed.
  verify: uat
- SC-10: No consumer of a parsed value assumes `str`. Named regressions: a `cycles_used` that parses as
  an `int` does not raise at the `.isdigit()` call (`check-state.sh:120`), and a run id that is exactly
  a date-shaped scalar (`2026-07-31`) still joins to its run directory as a string rather than a
  `datetime.date`.
  verify: automated        evidence: unit
- SC-11: Every test in `.claude/skills/harness/bin/test-gh-sync.py` invokes the subcommand its label
  names. (Issue #12 is filed as unverified — this criterion is falsifiable whether or not the defect is
  real.)
  verify: inspection
- SC-12: `.claude/skills/harness/bin/run-unit-tests.sh` exits 0, with at least the pre-change baseline
  of 9 test files reporting `PASS`, 0 reporting `FAIL`, and 0 `skip` lines — measured on this branch
  before any conversion work.
  verify: automated        evidence: unit
- SC-13: The set of runs the converted `check-state.sh` builds from this repo's real `.harness/` is
  identical — same count, same ids — to the set the pre-change parser builds from the same tree. SC-02
  cannot show this: exit 0 with zero violations is exactly what a silently dropped run produces today,
  so only the inventory comparison distinguishes "nothing fired" from "nothing was checked". Reviewer
  cites both listings.
  verify: inspection

**Note for whoever builds SC-08's harness:** simulating an absent PyYAML will almost certainly need an
interpreter-environment override (a shadowing module on `PYTHONPATH` is the obvious shape). That is not
a violation of SC-05's "no `PYTHONPATH` override" clause — SC-05 asserts fidelity to the real hook
context on a healthy machine, SC-08 deliberately breaks that machine. Different paths, different
harnesses.

## Verification gaps

- **SC-09 rests on `uat` and nothing else.** "Blocks from the next session onward" needs a genuinely
  new session on a PyYAML-less machine; no test kind in `harness.json` can create that honestly. Until
  the user runs it, the expiry of the bootstrap escape is **not proven** — SC-08 proves only that the
  first session is permissive.
- The kinds with `cmd: null` (`functional`, `integration`, `component`, `ui`, `eval`, `typecheck`) do
  not bind here: this feature's surface is `.claude/skills/harness/bin/*`, which the `unit` kind's
  detect glob matches directly (`.claude/skills/harness/bin/test-*.py`) and whose runner exists.

## Backlog disposition — all four said out loud

Absorbed issues are **cited, never closed** (DEC-138 am.7); the `absorbs:` annotation itself is a task
field and lands on a `T-NN` in the PLAN run, not here.

- **#11 — absorbed.** The anchor defect. Closes as a consequence of REQ-02 / SC-01.
- **#12 — absorbed** ("a gh-sync abandon test label claims the new subcommand but invokes an old one",
  filed unverified). `test-gh-sync.py` is the regression net this feature's `gh-sync.py` conversion
  will be read against; a test whose label misdescribes what it invokes makes that evidence
  unreadable. Confirm-or-refute is in scope, as SC-11.
- **#13 — NOT absorbed** ("no test covers gh-sync abandon against a failing API call"). An
  error-handling coverage gap on the network path, with no YAML parse in it. Absorbing it would widen
  the sweep into general test-debt work.
- **#14 — NOT absorbed** ("wayfind.py has no test coverage"). `wayfind.py` is not one of the six
  scripts, and it neither parses YAML nor uses regex at all — verified at `37a8a66`:
  `grep -cE 're\.(search|findall|match|finditer)'` returns 0 and `grep -n 'yaml'` returns nothing.
  Unrelated to this feature.
- **#10 — NOT absorbed**, restated from the grilling artifact: a `change_type` vocabulary gap in
  `validate-digest.py`. Same file as Feature 2, different defect class.

## Deferred — open here, not settled here

Recorded so the PLAN run does not treat silence as a decision. This BRIEF is written so that no
criterion presupposes any of these answers.

- **Architecture, for eng-lead:** whether the six converted scripts share one YAML helper module or each
  `import yaml` directly. SC-03/SC-04 are worded to hold either way.
- **Architecture, for eng-lead:** how the two hooks detect "same session" for the one-time bootstrap
  escape. SC-08 and SC-09 name only the observable behaviour, never a mechanism.
- **Plan-level:** whether `check-state.sh` correctly gets **no** bootstrap escape while the hooks do. On
  a PyYAML-less machine that makes the `/harness` door refuse to open while writes are still permitted
  for one session, so the recovery path runs outside the harness. That may be intended; it is currently
  unstated, and it is the PLAN run's call.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-03
note: |
  Signed WITH the three amendments planning measured FALSE (Q1/Q2/Q3). All three correct the
  record toward accuracy; none expands scope.

  Q1 — REQ-01 names `cost-report.py` as a YAML parser. It is not one: it does a targeted
  line-scan REPLACEMENT of the `cost:` block (`cost-report.py:189`), parsing nothing into
  values. USER RULED: it STAYS IN SCOPE. It still hand-rolls YAML manipulation with a regex,
  which is the defect class being eliminated; a brittle writer left behind a fixed reader is
  the seam where the next silent shadowing appears (it is B-4's own history). REQ-01's
  characterisation is corrected, its scope is not.

  Q2 — SC-03's parenthetical undercounts the surviving regex calls. 7 of the 17 in
  `check-state.sh` legitimately remain, six of them parsing MARKDOWN, not YAML. The criterion
  stands; its count is corrected. A reviewer must judge SC-03 against the census, not the
  parenthetical.

  Q3 — SC-02's exit-0 baseline is stale: `check-state.sh` exits 1 TODAY, on this feature's own
  unsigned BRIEF. That is now signed, so re-baseline at build open rather than trusting the
  recorded value.

  Q7, ROUTING WALL, third recurrence (FEAT-03 Q13, FEAT-04 T-09 are the same wall). USER
  RULED: T-10 and T-11 stay MAIN-SESSION steps inside the build spine; `team-config.yaml` is
  NOT widened. `dev-ops` is granted neither `.gitignore`, nor `templates/**`, nor
  `harness-init/SKILL.md`. The build spine therefore STALLS on the main session at T-10, and
  T-12 blocks on it — the orchestrator must return for those steps, not attempt them. Three
  recurrences of one wall is a signal about the domain model; it is deliberately not acted on
  inside this feature.

  BUDGET: held at 120 with the overrun ACCEPTED, not raised. 92 of 120 was spent in the plan
  phase alone; build, validate and ship inherit ~28. Cost is reported, never gated (DEC-134).
  The real number is expected in the ship briefing.

  PROTOTYPE: not required. `bin/` scripts and hooks, no end-user surface.

### Amendment 1 — a corpus-validity gate, added at the user's instruction, 2026-08-03

**New scope on a signed artifact, authorised by the user in-session.** Recorded here rather than
carried as an informal note, because a signed BRIEF is the thing reviewers judge against.

**What forced it.** The build's own T-02 RED gate surfaced that **four `.harness` YAML files do not
parse** under PyYAML: `team-config.yaml:18` (a space-`#` inside a flow sequence, which silently made
**every key from `orchestrator:` onward unreachable** — the whole manifest, not one line),
`FEAT-03/feature.yaml:97` (a backtick, a YAML reserved indicator), and `FEAT-04:77` plus `FEAT-05:55`
(`: ` in prose read as a mapping key). `FEAT-01`, `FEAT-02` and `harness.json` were fine.

One root cause: **unquoted prose in plain scalars.** Every hand-rolled line scanner tolerated it for
the entire life of the project — which is the strongest evidence for this feature's thesis, and also
a blocker the signed plan did not anticipate.

**Why a repair alone is insufficient.** `FEAT-05/feature.yaml` was written **today**, by this
feature's own orchestrator. So this is live, ongoing production of invalid YAML by agents, not
historical debt. Repair without a gate means the next run reintroduces it, and the next real-parser
conversion fails the same way.

**REQ-08 (new).** The `.harness` YAML corpus stays parseable by a real parser. A change that makes any
`.harness/**/*.yaml` unloadable fails the unit gate rather than being discovered by a downstream
conversion.

**SC-14 (new).** `verify: unit`. A test under `.claude/skills/harness/bin/` walks every
`.harness/**/*.yaml`, calls `yaml.safe_load` on each, and fails naming file, line and column for any
that does not load. It is listed in `run-unit-tests.sh`'s `SCRIPTS` array — otherwise it gates
nothing, which was issue #5's exact failure mode. Proof it is a real gate: it must be shown RED
against a deliberately malformed fixture, then GREEN on the repaired corpus.

**Deliberately NOT required:** a `PreToolUse` hook. The unit runner is sufficient and adds no
mechanism, no `harness.json` change, and no per-write latency. Rejected as over-engineering.

**Scope ruling the user made alongside this (recorded so a reviewer does not read it as drift):** the
orchestrator's repair of **FEAT-03's and FEAT-04's** `feature.yaml` — shipped features' records,
touched under its `.harness/features/**` grant and disclosed rather than hidden — **STANDS**. Its
reasoning holds: SC-02 and SC-13 read the whole `.harness/features/*/` tree, so those files sit inside
this feature's evidence path. Verified independently: all five `feature.yaml` now parse, and
top-level keys are identical before and after in both files. Note the honest limit — the pre-repair
files **cannot parse**, so a data-level equality proof is impossible by construction; the load-bearing
evidence is that the T-01 run-inventory receipt diffs to zero rows, which is what keeps SC-13's
baseline valid rather than silently stale.
