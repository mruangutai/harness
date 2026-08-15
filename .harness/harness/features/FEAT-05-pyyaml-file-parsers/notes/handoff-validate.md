# Handoff — FEAT-05 validate → ship

## Next

- **The branch is NOT pushed and there is no PR.** Both are the user's call (SPEC §12).
  31 commits on `worktree-fix-harness-tooling-backlog` from `37a8a66`.
- **Close issue #11** (fixed, regression-tested at `test-check-state.py` case (e)) and
  **#12** (REFUTED — the goal-check independently audited all 57 `test-gh-sync.py`
  labels against the subcommand each invokes; zero mismatches. Close `not planned`).
- **Issue #16 stays open by design** (D-09): `review_sha: none` is a truthy string, so
  INV-6 passes on an unpinned feature. Deliberately not fixed here — it alters the
  output SC-02/SC-13 compare against.
- **`bash-write-guard.sh` has a real false positive nobody has ticketed:**
  `FOO=bar python3 - <<'PY'` and `env python3 - <<'PY'` fail the `KNOWN_DATA_FEEDERS`
  test, so the heredoc body is scanned and a Python `if a > b:` reads as a redirect.
  Found by review pass 3 and correctly scoped out — untouched by this diff.

## Trust

- **Trust the goal-check over me.** Two cycles, `research-FEAT-05-goal-check.md` and
  `-c1.md`. It found what five code-review passes did not: that my own fix violated the
  signed BRIEF. It also corrected my dispatch twice (13 SCs → 14; SC-02 never hinged on
  the fallback).
- **Trust the tests only where they were proven RED first.** Six of this feature's
  non-discriminating tests were mine — including one where I injected the missing import
  into my own harness, and one that asserted "a position is present" while the position
  was wrong.
- **Distrust line-number citations in receipts.** Counts hold; positions have drifted.
- `cost_usd: 240.82` against a signed `120` is **stale LOW** — it predates the entire
  review-and-fix arc. Cost is reported, never gated (DEC-134).

## Dead ends

- **Do not re-add a line-scan fallback anywhere in `bin/`.** One was added and REMOVED at
  the user's ruling; BRIEF Goal :20-21 and Constraint :48-49 forbid it, and
  `harness-init/SKILL.md:49` + `CLAUDE.md:19` assert its absence. What it bought was
  earlier detection, not correctness — a bad `state.yaml` written during a bootstrap
  grant is still caught at the next `/harness` entry.
- **Do not "resync" the two duplicate-key detectors**, and do not move either hook's
  `import harness_yaml` to the top of its block: both orderings are behaviour, both are
  commented, both were bugs once.
- **Do not test the escape at module level only.** `payload={"session_id": ...}` is a
  DEAD identity path in production; the live one is `CLAUDE_CODE_SESSION_ID`. Two real
  defects hid behind that gap.

## Working set

- **Module:** `harness_yaml.py` — the only `try: import yaml` in the tree (D-12).
  `MissingDependency` and `DuplicateKeyError` subclass `YamlParseError`; callers needing
  the specific message catch it FIRST, and that ordering is load-bearing.
- **Hooks:** `check-domain.sh`, `bash-write-guard.sh` — one shared domain walk (D-03), so
  they cannot drift. Both merged to a single interpreter launch: 80.6→43.5ms and
  64.6→45.0ms, faster than before the feature while doing more.
- **Readers:** `check-state.sh` (closes #11), `gh-sync.py`, `upgrade-config.py`.
- **Gate:** `test-harness-yaml-corpus.py` — walks every `.harness/**/*.yaml` using
  `harness_yaml.load_file`, not `safe_load`; its negative fixtures are load-bearing.
- **UAT:** `uat-bootstrap-escape-expiry.md`, PASSED by the user, and the goal-check
  confirmed the pass still stands (`require_or_bootstrap` byte-identical since).
- **Receipts:** two hook-resolution probes (Q3/Q4/Q6), the typed-value sweep (SC-10),
  both run inventories (SC-13), two goal-checks.
