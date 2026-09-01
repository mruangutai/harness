# FEAT-51 · plan fix cycle 2 — the plan.yaml quarantine route hole is closed

**Home chosen: candidate 3 — a second rule inside the already-registered `plan-sign-gate.sh` /
`plan-sign-gate.py`.** It is the only candidate that needs no `.claude/settings.json` entry and no
new test-file registration, and it inherits a tokenizer already hardened through five measured
evasion classes (F-03, H-02, C2-03, MF-1, HIGH-2). Recorded as **D-12**; the new work is **T-07**;
**D-13** and **D-14** record the two design choices inside it.

## The hole, and what FEAT-41 already buys

Measured at `ad93d43e`: `.claude/settings.json:19` registers `check-domain.sh` on `PreToolUse` for
`Write|Edit` **only**; the `Bash` matcher at `:27` runs `branch-create-gate.sh`,
`bash-write-guard.sh`, `gh-close-gate.sh`, `plan-sign-gate.sh`; `check-domain.sh --post` at `:62`
is a POST sweep. `plan.yaml`'s only writer is `plan-merge.py`, invoked through `Bash`. So T-03's
branch covers `BRIEF.md`, `feature.json`, `STATE.md` and **cannot reach `plan.yaml`**.

FEAT-41 buys the **deletion** half only: the locked union merge stops a one-task orphan shrinking a
fourteen-task plan. It buys nothing for REQ-05 — an orphan can still land **new** canonical plan
content with no parent, no wake and no adoption, and `apply` prints `APPLIED` at exit 0.

## Why not the other two

- **Candidate 1, a new `PreToolUse` Bash gate — rejected.** It needs a new `settings.json` entry
  (`--resolve` answers NOBODY, so that surface joins as `main-session-direct`) plus a new test file
  that must be appended to **both** `run-unit-tests.sh` `INTEGRATION_SCRIPTS` and `harness.json`
  `test_kinds.integration.detect` — surfaces that are `team`/`harness-dev-ops` while the gate is
  `main-session-direct`, which is exactly the stranding D-08 already records. It buys nothing
  candidate 3 does not: same hook event, same tokenizer, one more file to keep in step.
- **Candidate 2, a check inside `plan-merge.py`'s mutating verbs — rejected, and the reason is
  structural rather than DEC-174's circularity.** D-07 makes `quarantine.py adopt` delegate to
  `plan-merge.py apply`. A check inside `apply` therefore sits inside the one command adoption must
  travel, so adoption would have to be **exempted from its own gate** — and that exemption, not the
  check, becomes the hole. (It does close the shell-expansion blind spot candidate 3 keeps; that is
  the trade-off, and it is recorded in D-12 rather than hidden.)

## What T-07 does (`plan-sign-gate.py`, `plan-sign-gate.sh`, `test-plan-sign-gate.py`)

A sibling `quarantines(line, agent, session)` beside the untouched `denies()` at `:256`. It matches
`plan-merge.py` + one of `apply | add-tasks | set-task-station | set-feature-station`
(`plan-merge.py:932`), **or** `quarantine.py adopt` — **D-13**, because `adopt` is the only other
command that turns a quarantined file canonical, so REQ-05 is otherwise unreachable on this route.
`discard` and `list` are deliberately uncovered and the rule says so. It reads the `--file` value,
normalises from its last `.harness/` segment, and reuses **T-02's** `canonical_artifact`,
`orphan_write` and `quarantine_rel` — no second predicate. The root is the one the wrapper already
resolves from its own directory, which is the same root `check-domain.sh:154` resolves — **D-14**,
so both routes read one registry. D-04's OMP carve-out holds because `orphan_write` itself carries
it. `inflight_registry` is imported only *after* a match, because this hook runs ahead of every
`Bash` call in the session.

**It fails OPEN** on an unlexable line and on a `--file` value with no `.harness/` segment (D-13).
That is not tidiness: the three existing negative controls at `test-plan-sign-gate.py:150`, `:320`
and `:366` assert that `--file p`, `--file $PLAN` and `--file $(ls p.yaml)` stay allowed, and it
matches `orphan_write`'s own fail-open on a missing registry. Stated as a blind spot, as the
module docstring already states the `$P` one.

**T-04 needs no change.** Its `adopt` already delegates `plan.yaml` to `plan-merge.py apply` and
already resolves the canonical target from the quarantined basename; the new rule allows a resumed
parent's `adopt` (it holds its own live claim, so `orphan_write` is False) and refuses an orphan's.

## Gate output (run from the main checkout `/Users/molchairuangutai/GitHub/harness/`)

- `plan-merge.py apply` → `ADDED D-12 / D-13 / D-14 / T-07`, `APPLIED …/plan.yaml`, exit 0.
- `check-plan-routes.py <plan.yaml>` → **0 violation(s) across 1 plan(s)**, exit 0. Three
  `DEVIATION` lines, on **T-01, T-02, T-07** — the DEC-174 carve-out (T-07 is the new one).
- `yaml.safe_load` → `YAML_OK`, exit 0. Every scalar tail survives the load.
- `status: plan` intact; all seven tasks `status: ready`; `DEC-208` occurrences **0**; `approval`
  key **absent** before and after, unchanged by the apply.
- REQ↔task coverage bidirectionally complete: REQ-01 T-05 · REQ-02 T-01,T-06 · REQ-03 T-03,T-05 ·
  REQ-04 T-02,T-03,**T-07** · REQ-05 T-04,T-06,**T-07** · REQ-06 T-01,T-05 · REQ-07 T-02,T-06. No
  task traces zero live REQs. 7 tasks, 14 decisions.
- T-07's `verify` block run verbatim pre-change: **exit 1** (first grep fails, work not done). The
  tail conjunct alone — `python3 .agents/skills/harness/bin/test-plan-sign-gate.py` — passes today
  at exit 0 (`all checks passed.`), so the three greps are the whole discriminator and no earlier
  conjunct masks them. Both runs together: 2.05s.

## BRIEF.md — SC-11 added, SC-04 kept coherent

**SC-11** grades `plan-sign-gate.sh` **by name** as the `PreToolUse` `Bash` hook, not a fact both
routes happen to satisfy. **The mutation that turns it red:** delete the `quarantines()` call from
the two-rule decision at the foot of `plan-sign-gate.py` (or point the suite at a pre-change copy
via `PLAN_SIGN_GATE_BIN`, which `test-plan-sign-gate.py:22` already reads) — the orphan `apply`,
`set-task-station` and `adopt` calls then return exit 0 instead of 2. `evidence: integration` is
correct: the assertions land in `test-plan-sign-gate.py`, which is in `run-unit-tests.sh`
`INTEGRATION_SCRIPTS` at `:31` and in `harness.json` `test_kinds.integration.detect` (verified, 29
entries). SC-04 gained four lines saying it is silent about the `Bash` route and pointing at SC-11.
No REQ added or reworded.

## Open questions

- **Q1 (carried, blocking, not mine):** a plan created by `plan-merge.py apply` can never acquire
  an `approval:` mapping. Untouched, as dispatched.
- **Q2 (non-blocking):** `quarantine.py discard` is left uncovered by the Bash rule. An orphan can
  therefore discard its own quarantined result. It can make nothing canonical, so no REQ is
  violated, but the operator loses a recoverable artifact silently. If that matters, it is one more
  verb in the same tuple — not a new task.

Proposal applied: `notes/research-proposal-route-hole-c2.md` (a YAML proposal carrying the `.md`
name because `check-domain.sh` grants `harness-pm` only `notes/research-*.md`).
