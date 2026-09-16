# Code review — BUG-1756-qa-reverify-bash — c0

Stage 1 **FAIL**: T-01 implements the requested Python launch, named-kind iteration, first-failure stop, real output-tail reporting, and default no-kind invocation, but omits two signed SC-04 regression proofs. Stage 2 was therefore **not performed**, as required by the ordered review protocol. The mechanical pinned-range Python grade was `pass`; it is not a substitute for Stage 2.

Concrete evidence: `_reverify_suite` returns `None` for both a subprocess exception and timeout (`.claude/skills/harness/bin/validate-digest.py:2019-2023`), but the added “spawn error” case supplies a directory and is rejected by the earlier `os.path.isfile` check before `subprocess.run` (`tests/integration/test-validate-digest.py:2318-2325` versus `.claude/skills/harness/bin/validate-digest.py:2013-2014`). No timeout case exists in the integration file. Thus changing the exception path to propagate `OSError` or `TimeoutExpired` would leave this suite green while an unconditional qa PASS could crash the validator instead of returning 0 with “could not independently re-run.” T-01 must add discriminating spawn-error and timeout cases.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 fails because T-01 does not prove preserved spawn-error or timeout semantics; Stage 2 was not run."
  severity_max: med
  findings:
    - kind: substance
      scope: task
      severity: med
      reader: code-reviewer
      summary: "T-01's SC-04 coverage never reaches a real spawn exception and contains no timeout case."
      why: "With OSError or TimeoutExpired propagation regressed, tests/integration/test-validate-digest.py remains green because its directory fixture exits at os.path.isfile before subprocess.run and no timeout fixture exists; the qa hook can then crash instead of failing open loudly."
  must_fix:
    - "T-01: add discriminating integration cases that exercise an actual subprocess spawn exception and timeout and assert exit 0 plus the 'could not independently re-run' diagnostic required by SC-04."
  spec_violations:
    - kind: omission
      path: tests/integration/test-validate-digest.py
      ref: SC-04
  code_grade: pass
  reviewed: "af1c1d88a7e81010fd4902b2144b5cd5eb67f9ef..01dd2ed8eb6802048cf21ef3508e2e9310096695"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1756-qa-reverify-bash/notes/review-harness-code-reviewer-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1756-qa-reverify-bash/.harness/harness/features/BUG-1756-qa-reverify-bash/notes/review-harness-code-reviewer-c0.md
```
