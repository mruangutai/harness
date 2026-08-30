# SIMPLIFY pass — EFFICIENCY angle — FEAT-38 — harness-dev-ops

**Verdict: zero findings.** Both new checkers and both new test scripts are cheap
in isolation and are invoked only at boundary steps (task-verify, CI, the qa-gate
integration run) — never at session entry or on every write. Measured, not
estimated, below.

## 1. Invocation sites, by file:line

Neither `check-decision-anchors.py` nor `check-decision-claims.py` is wired into
any `.claude/settings.json` hook (`SubagentStart`, `PreToolUse`, `PostToolUse` —
read whole; only `check-domain.sh`, `branch-create-gate.sh`, `dispatch-guard.sh`,
`validate-digest.py` are registered). Grep of the whole tree for the two names
outside `bin/` turns up exactly:

- `plan.yaml:1173` — `check-decision-anchors.py` in T-16's verify block (one-shot,
  task-verify time only).
- `plan.yaml:1219` — `check-decision-anchors.py --file /dev/null` in T-17's own
  verify block (one-shot).
- `.harness/harness.json:119` — `test-check-decision-anchors.py` and
  `test-check-decision-claims.py` (the TEST files, not the checkers) appended to
  `test_kinds.integration.detect`. This is what makes `run-unit-tests.sh --kind
  integration` pick them up.
- `.claude/skills/harness/bin/run-unit-tests.sh:31` — both test scripts registered
  by bare name in `INTEGRATION_SCRIPTS`. Each test file itself invokes the
  checker binary via `subprocess.run` once per test case (6 cases for anchors, 7
  for claims) against a synthetic temp fixture, never the live `DECISIONS.md`.
- `.github/workflows/tests.yml:89-92` — `run-unit-tests.sh --kind integration`
  runs on every `push` to `main` and every `pull_request` (not on every commit to
  a feature branch without a PR, per the file's own asymmetric-trigger design).
  This is the only place the checkers run per-PR, and it runs them indirectly via
  their tests, not directly.
- `DECISIONS.md:6290-6291` — two `<!-- claim: ... -->` markers that
  `check-decision-claims.py` executes when it walks the live document; these are
  data the checker consumes, not a second invocation site of the checker itself.

**No session-entry hook, no pre-write hook, no per-write gate.** Everything above
is either a one-shot task-verify command or a per-push/per-PR CI step — the
categories the skill says earn less scrutiny than an every-write or
every-session-entry gate.

## 2. Timings — measured, worktree, this session

| What | Wall clock | Detail |
|---|---|---|
| `check-decision-anchors.py` (default target, live DECISIONS.md) | **0.076s** | `examined 20 anchor(s), 0 failed` |
| `check-decision-claims.py` (default target, live DECISIONS.md) | **0.074s** | `examined 11 claim(s), 0 failed` |
| `test-check-decision-anchors.py` | **0.289s** | 6/6 ok |
| `test-check-decision-claims.py` | **0.245s** | 7/7 ok |
| `run-unit-tests.sh --kind integration` (30 scripts incl. both new tests) | **2m31.6s** | exit 0, 700 PASS, 0 FAIL; `PASS test-check-decision-anchors.py` at output line 1959, `PASS test-check-decision-claims.py` at 1967 |
| `run-unit-tests.sh` (all kinds, no `--kind`) | **2m53.1s** | exit 0, 1285 ok/PASS lines, 0 FAIL |

The two new checkers' own runtime (0.076s + 0.074s = 0.15s) and their tests'
runtime (0.289s + 0.245s = 0.53s) are each roughly 0.02–0.3% of the 2m31–2m53
whole-suite figure — noise against a suite this size, not a measurable
contribution to it.

## 3. Repeated I/O

Read both checkers' full source (`check-decision-anchors.py:125-155`,
`check-decision-claims.py:144-174`). Each opens `DECISIONS.md` **exactly once**
per process (`with open(target...) as f: text = f.read()`), parses it in memory,
and never re-opens it. `check-decision-anchors.py` additionally opens each
*cited* file (not `DECISIONS.md`) once per anchor via `count_lines()` — 20 small
opens against small source files, already inside the measured 0.076s. No
line-by-line double-parse in either script. `gen-decisions-index.py:273,277,307`
(the T-06/T-10 refs-graph change) is likewise one read of `DECISIONS.md`, one
read of the existing index, one write — unchanged shape, not touched by this
angle's findings.

Both scripts independently open `DECISIONS.md` when run back-to-back (as they
are, e.g., in a hand check) — two reads of a 6299-line file, ~2ms class of cost
per the 0.075s single-process figures above. This is the direct, settled
consequence of "standalone scripts under `bin/`" (named explicitly as settled in
this dispatch's non-goals) and is not worth re-litigating for a sub-millisecond
difference.

## 4. Startup / closures

Neither checker does import-time work beyond module-level constant assignment
(`DOCS_DIR`, `ANCHOR_RE`/`CLAIM_RE`/`HEADING_RE`, `ALLOWED_FIRST_TOKENS`,
`TIMEOUT_SECONDS` — all cheap literals). `default_target()` resolves
`harness_boundary.resolve_root()` at **call time** inside `main()`, not at
import time (confirmed by reading both files end-to-end) — this was itself a
design point noted in T-17/T-20's receipts, so it is already right, not a new
finding. No closures capturing a scope for later reuse in either file.

## 5. `run-unit-tests.sh --kind integration`/full-suite runs at CI/qa-gate boundaries

These are deliberate full-suite runs at boundary steps (CI on push/PR, the qa
gate's own integration run) — the skill names this explicitly as evidence the
boundary exists, not waste. Not flagged.

## `git diff --stat` — DECISIONS.md / DECISIONS-INDEX.md, verbatim

```
 .harness/harness/docs/DECISIONS-INDEX.md |  395 +++--
 .harness/harness/docs/DECISIONS.md       | 2379 ++++++++----------------------
 2 files changed, 821 insertions(+), 1953 deletions(-)
```

## Findings

None. Every measured figure is well under a second at the unit level and the
two-new-scripts' marginal contribution to the whole-suite wall clock is not
separable from run-to-run noise. Nothing runs at session entry or on every
write.
