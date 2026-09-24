# FEAT-65 build — main-session-direct (DEC-174)

```yaml
VERDICT: PASS
DIGEST:
  headline: "All eleven hooks end at zero broad catches (77 → 0): every boundary catches its producer's class, the rule-level absorbers are deleted, and each classified own-failure path prints harness_boundary.hook_guard's one template (check-domain, bash-write-guard, dispatch-guard through the new run_hook_body; validate-digest's hook mode; merge-gate CLOSED); BROAD_CATCH_CEILINGS is {harness_boundary.py: 2}; the five DEC-234 prologues are byte-identical and locked; feature-record and inflight_registry stay unwrapped and loud."
  tests_added: 55
  suite: pass
  task: T-04
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .claude/skills/harness/bin/bash-write-guard.py
    - .claude/skills/harness/bin/branch-create-gate.py
    - .claude/skills/harness/bin/check-domain.py
    - .claude/skills/harness/bin/check-plan-routes.py
    - .claude/skills/harness/bin/dispatch-guard.py
    - .claude/skills/harness/bin/feature-record.py
    - .claude/skills/harness/bin/gh-close-gate.py
    - .claude/skills/harness/bin/harness_boundary.py
    - .claude/skills/harness/bin/inflight_registry.py
    - .claude/skills/harness/bin/inject-expertise.py
    - .claude/skills/harness/bin/merge-gate.py
    - .claude/skills/harness/bin/plan-sign-gate.py
    - .claude/skills/harness/bin/validate-digest.py
    - tests/integration/test-bash-write-guard.py
    - tests/integration/test-branch-create-gate.py
    - tests/integration/test-check-domain-post.py
    - tests/integration/test-check-domain-worktree.py
    - tests/integration/test-check-domain.py
    - tests/integration/test-check-plan-routes.py
    - tests/integration/test-dispatch-guard.py
    - tests/integration/test-gh-close-gate.py
    - tests/integration/test-harness-yaml.py
    - tests/integration/test-inflight-registry.py
    - tests/integration/test-inject-expertise.py
    - tests/integration/test-merge-gate.py
    - tests/integration/test-plan-sign-gate.py
    - tests/integration/test-validate-digest.py
    - tests/unit/test-broad-catch-census.py
    - tests/unit/test-feature-record.py
    - tests/unit/test-harness-boundary.py
  expertise_update: []
artifact: .harness/harness/features/FEAT-65-broad-exception-hooks/notes/clean-pin-byte-receipts.md
```

One run covers T-01..T-04 in order: `e10c56de` (T-01), `ec0996cb` (T-02), `48ed17bc` (T-03 + T-04 red),
`1bb39948` (T-04 ceiling), `56031323` + `fbdb2319` (grade and lock re-pins), `79b7c268` (simplify: `run_hook_body`) — the implementation pin —
then `af1f1d3f` for the receipts. Each task's own verify chain ran green at its commit; the full unit and
integration runners ran green at the pin (119 / 75 suites). Evidence: `notes/clean-pin-byte-receipts.md`
(all 21 verify suites exit 0 at a clean checkout of the pin; census 0/2; five-way prologue identity),
`notes/byte-evidence-vs-baseline.md` (per-suite normalised diffs vs `4e8c73c0`), and the ledger of every
replaced or deleted operator-visible line, `notes/build-divergences.md` (D-01..D-14).

Two things the panel should weigh that the plan did not spell out:
1. A harness_boundary.py that is PRESENT BUT BROKEN (SyntaxError) still takes the closed BLOCKED path in
   check-domain/bash-write-guard (`except (ImportError, SyntaxError)` at the entry and the two fail-closed
   loads); a module that raises while executing is loud (traceback, exit 1) — there is no guard without the
   module that defines it. Ledgered as a no-byte-change narrowing.
2. merge-gate's two "could not evaluate … receipt" denials moved channel: from a decision JSON on stdout to
   hook_guard's CLOSED form on stderr at exit 2. Same blocked verdict (the host treats exit 2 as blocked);
   `(ImportError, OSError)` keeps the JSON denial for the real classes. D-13.
