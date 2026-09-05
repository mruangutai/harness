# Security review — BUG-1306 — review-c0 (pin da05ea28)

## Verdict: PASS, severity_max: info

No exploitable security surface in this diff. The one source file touched
(`tests/integration/test-plan-merge.py`) is test-only, and the identity-variable removal it adds
does not weaken the production guard it targets.

## Census

| Path | In/out | Why |
|---|---|---|
| `tests/integration/test-plan-merge.py` | IN | touches an identity variable (`HARNESS_AGENT_TYPE`) that gates a production write path — the one thing worth auditing |
| `.claude/skills/harness/bin/plan-merge.py` | OUT | `git diff <merge-base>..da05ea28 -- .claude/skills/harness/bin/plan-merge.py` is 0 lines — confirmed untouched |
| `.harness/harness/features/BUG-1306-agent-type-hermetic-tests/*` (BRIEF, STATE, plan.yaml, notes, observations, feature.json) | OUT | Harness lifecycle bookkeeping, no runtime/input surface |

## The identity-variable question, answered

**Claim to verify:** does popping `HARNESS_AGENT_TYPE` from the test process's own `os.environ` at
module import (`tests/integration/test-plan-merge.py:38`) weaken the REQ-05/DEC-120 guard in
`cmd_sign_approval` (production, `.claude/skills/harness/bin/plan-merge.py:1188`) for any caller
outside this test file?

**No. Four independent reasons, each checked directly:**

1. **Production line is untouched.** `git diff $(git merge-base main da05ea28) da05ea28 --
   .claude/skills/harness/bin/plan-merge.py` returns 0 lines. `cmd_sign_approval` still does
   `_signing_agent = os.environ.get("HARNESS_AGENT_TYPE") or ""` and `sys.exit(10)` on any
   non-empty value (plan-merge.py:1188-1196), reading from whatever env the OMP host actually
   injected into the real caller's shell. The pop lives in a different file and a different
   process.

2. **A test-process env mutation cannot reach a non-test caller.** `.agents/skills/harness/bin/run_pool.py:61-62`
   spawns each test file as its own `subprocess.run([sys.executable, path], ...)` — no shared
   memory, no env passed back to the parent. `os.environ.pop(...)` mutates only that one spawned
   process's own environment table; it dies with the process when the file finishes. It cannot
   leak into a sibling test file's process, into `run_pool.py`'s own environment, or into any
   process started outside this test run.

3. **The two guard-verifying cases are unaffected by the module-level pop, because they
   never rely on it.** Both build their own explicit `env=` mapping, independent of whatever the
   pop left in `os.environ`:
   - `case_1103_sign_approval_refuses_a_governed_agent` (test-plan-merge.py:1097-1116) passes
     `env = dict(os.environs, HARNESS_AGENT_TYPE="harness-pm")` and asserts `returncode == 10` —
     the refusal is still exercised, positively, every run.
   - `case_1103_sign_approval_negative_control_absent_is_main_session` (test-plan-merge.py:1119-1136)
     passes `env = {k: v for k, v in os.environ.items() if k != "HARNESS_AGENT_TYPE"}` and asserts
     `returncode == 0` — the negative control was *already* scrubbing the variable itself before
     this diff; the module-level pop is redundant with it, not a replacement for it.
   Neither case is disabled, weakened, or skipped. The refusal path (exit 10, REQ-05/DEC-120) and
   the negative control (absence ⇒ main session, matching plan-sign-gate.py's own hook) both still
   fire on every run of this suite.

4. **Every other subprocess call site in this file invokes a verb that never reads
   `HARNESS_AGENT_TYPE`.** `grep -n "HARNESS_AGENT_TYPE" plan-merge.py` returns exactly one line —
   inside `cmd_sign_approval`, a function body, not a module-level read. `run_apply` (line 130,
   `apply` verb), the `run_verb` calls for `set-task-station`/`amend`/`set-panel`/etc., and the
   two `Popen` calls in `case_concurrency_real` (lines 305-311, also `apply`) never reach that
   check regardless of what `os.environ` holds. The pop changes their inherited environment but
   has zero observable effect on them, because nothing in those code paths reads the variable.
   `_load_pm()` (line ~1205) imports `plan-merge.py` as an in-process module for `_verify_signature`
   unit tests, not `cmd_sign_approval` — no module-level read of the variable exists to be affected
   by import-time state either.

**Conclusion:** the fix corrects a test-hermeticity bug (ambient `HARNESS_AGENT_TYPE` in a
governed agent's own shell was causing 13 checks across six *unrelated, non-1103* cases — ones
that call `sign-approval` expecting success as the main session — to fail for the wrong reason).
It does so by scoping the fix to the one process that needs it, without touching, weakening, or
bypassing the production guard, and without disabling the two cases whose entire job is to
exercise that guard.

## STRIDE / OWASP sweep (secondary, no findings)

- **Injection / shell**: all `subprocess.run`/`Popen` calls use list-form argv
  (`[sys.executable, CLI, *argv]`), no `shell=True`, no string interpolation into a shell — no
  change from base, and the diff adds no new call site.
- **Secrets**: no credentials, tokens, or committed fixtures added; grepped the full diff text,
  nothing secret-shaped.
- **Auth / Tampering**: the sole auth-relevant check (REQ-05/DEC-120, `cmd_sign_approval`) is
  unchanged in production and still positively exercised in tests (see above). Rated Tampering-
  relevant per my own P-03 (a diff touching a validation invariant is in scope even without new
  input/auth surface) — audited, mitigated: true.
- **Data exposure**: no logging or export path touched; test assertions read only fixture
  tempfiles created and destroyed within the same test run (`fixture_root()` uses
  `tempfile.mkdtemp()`, cleaned up in every case's `finally: shutil.rmtree(...)`).
- **Dependencies**: no new import, no new dependency.

## Threat model

| boundary | stride | mitigated |
|---|---|---|
| `cmd_sign_approval`'s REQ-05/DEC-120 identity check (production, unchanged) | Tampering / Elevation of privilege | true — production code untouched, guard-exercising test cases unaffected by the diff |
| test-process env mutation reaching outside its own subprocess | Tampering (env leak) | true — `run_pool.py` process isolation confirmed; module-level pop provably scoped to one spawned process |

## Open questions

None. The identity-variable question was fully answerable from the diff, `run_pool.py`, and the
two case bodies — no residual uncertainty.
