# Research — BUG-1286 repository-wide test-tree enforcement

**All four blocking planning questions are settled, plus the FEAT-44 classification.** The design is
additive: `suite_layout.violations()` keeps every clause it has and gains one index-driven clause for
everything outside `tests/`, one exception registry with self-policing rules, and one fail-closed
enumeration path. No existing test needs to change its expectation; no runner edit is required.

## Census re-measured at 1977ebd68d34cc0308968b03ad2d24399c0b5335

Run from the feature worktree, `git ls-files` + basename globs `test-* test_* *_test.* *.test.* probe-*`:
2,670 tracked paths, 85 broad matches, 76 under `tests/`, **9 outside**. Of the 9, exactly **one**
carries a source extension:

| outside match | disposition |
|---|---|
| `.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts` | documented exception (D-05) |
| `.../evidence/probe-session-accessors-out.jsonl` | out of vocabulary (captured data) |
| 6 × `.harness/harness/features/FEAT-*/notes/probe-*.md` | out of vocabulary (probe write-ups) |
| `.harness/notes/probe-746-foreground-dispatch-2026-08-26.md` | out of vocabulary (probe write-up) |

The count reproduces the ticket's figure. `layout_fixtures.py` does not match any pattern, so it is
accepted without an exception — confirming the ticket's warning that it cannot exercise the
exception path.

## The decisions, and the evidence behind each

**D-01 vocabulary.** Basename globs `test-*`, `test_*`, `*_test.*`, `*.test.*`, `probe-*`, restricted
to source extensions `.py .sh .ts .tsx .js .mjs .cjs`. Markdown, JSONL and other captured data are
out of scope: 8 of the 9 outside matches are records of probes, not executables, and enforcing over
them would make a feature's honest record a layout violation. Cost accepted: `probe-*.md` dropped
under `bin/` would no longer be refused — bin's own clause keeps its current shape set, so nothing
regresses there (see D-04's split).

**D-02 exception contract.** A module-level `DOCUMENTED_EXCEPTIONS` tuple of `(exact relative path,
reason)` in `suite_layout.py` — no globs, and the registry polices itself: a glob character, a
duplicate, a path the index does not carry, or a path the vocabulary would never have flagged is each
its own violation. That makes stale, broadened and unnecessary entries fail loudly instead of rotting.
It lives in `suite_layout.py` rather than a new data file because a new module would land in the
`sole_implementations` sweep's blast radius (`tests/unit/test-suite-layout.py:111-117`) for no gain.

**D-03 tracked authority and fail-closed semantics.** `git ls-files -z` in `root`, i.e. the current
index — a staged addition is scanned, a staged deletion is not. Gating: the clause runs only when
`root/.git` exists **and** `git rev-parse --show-toplevel` equals `root` **and** the index carries
`.claude/skills/harness/bin/suite_layout.py`. The last condition scopes repository-wide enforcement to
the repository that ships the rule, so pointing the runner at a product checkout (possible: the root
comes from `harness_boundary.resolve_root`, which honours `HARNESS_PROJECT_DIR`) cannot enforce
Harness's vocabulary on product files. Absent `root/.git` → no-index mode, clause inapplicable, other
clauses unchanged: this is what the synthetic fixtures in `tests/unit/test-suite-layout.py:53-60` and
`tests/integration/test-run-unit-tests-layout.py:15-23` need, and it is why "no index" and "index
unreadable" must be different answers. `root/.git` present but enumeration failing (git missing,
non-zero, timeout, toplevel mismatch) → a violation line, fail closed.

**D-04 the bin clause stays.** The existing `bin/` clause is filesystem-based and therefore catches
*untracked* plants; the new clause is index-based. Keeping both closes a hole the ticket does not
mention (`bin/foo_test.py` is in neither the old bin shape set nor a tracked-only scan) and keeps
`tests/unit/test-suite-layout.py:76,91-94` and `tests/integration/test-run-unit-tests-layout.py:42`
green as written. A path reported by the bin clause is not reported twice.

**D-05 FEAT-44 probe.** Allowed documented exception, not relocated. Relocation would force edits to
a shipped feature's `evidence/README.md:13` and `notes/review-harness-qa-c1.md:157-158` — rewriting
the record of a landed feature to satisfy a layout rule. The consumer reference at
`tests/manual/probe-omp-session-accessor.py:54-55` therefore stays as it is. The upside is that the
registry has one live entry, so the repository itself is positive coverage: remove the entry and the
real root must report the path.

## Facts that shaped the plan

- The runner already checks layout before dispatch — `run-unit-tests.sh:33-42` prints
  `MISCONFIGURED:` per line and exits 2 before any `tests/*/test-*.py` runs. **No runner edit is
  needed**; the ordering guarantee is a test assertion, not a code change.
- `harness.json` `test_kinds.unit.detect` already globs `**/*.test.*|**/*_test.*|**/test_*.py`
  repository-wide while the runner selects by directory. That mismatch is the concrete drift the
  guard closes, and it is why the fix must not touch `test_kinds` (SC-11).
- Suite timings: `tests/unit/test-suite-layout.py` 0.10s, `tests/integration/test-run-unit-tests-layout.py`
  1.4s at this SHA — each task's `verify:` runs the single file, well inside 60s.
- Amendment convention for DEC-213 is in-place: `**Amended by <FEAT> — <clause>**`
  (`DECISIONS.md:4908,5296,6174`). `DECISIONS-INDEX.md:213` stores the source line `@6651`, so
  lengthening the entry shifts later anchors and regeneration is mandatory; the ` :: ` tail is
  hand-written and regeneration alone will not update it.

## Lane resolution (check-domain.sh --resolve, at the pinned SHA)

`suite_layout.py` → backend-dev/dev-ops · `tests/**` → backend-dev/dev-ops/qa ·
`DECISIONS.md` and `DECISIONS-INDEX.md` → documentor · feature `notes/qa-*.md` → qa/orchestrator.
**No path resolved to an ungranted surface, so no lane row is `main-session-direct`.**

## Validation run on the written plan

```text
$ python3 .agents/skills/harness/bin/plan-merge.py apply --file <feature>/plan.yaml \
    --proposal /tmp/bug1286-plan-proposal.yaml
APPLIED .../features/BUG-1286-test-tree-enforcement/plan.yaml            (exit 0)

$ python3 .agents/skills/harness/bin/plan-merge.py set-feature-station --file <feature>/plan.yaml \
    --station plan
STATION ... -> plan / APPLIED ...                                        (exit 0)

$ python3 .claude/skills/harness/bin/check-plan-routes.py <feature>/plan.yaml
OK T-01..T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-04 granted to harness-orchestrator, harness-qa
OK T-05 granted to harness-documentor
0 violation(s) across 1 plan(s)                                          (exit 0)

$ yaml.safe_load(plan.yaml)   ->  8 top-level keys, approval {status: pending},
  6 decisions D-01..D-06, 5 tasks T-01..T-05, every verify a literal block
```

`apply` seeded the `approval:` mapping itself (plan-merge.py:602-630): a proposal carrying one is
refused with exit 8, so the proposal deliberately omitted both `approval:` and `status:`.
Baselines re-measured at the pinned SHA before writing the verify commands:
`gen-decisions-index.py --stdout | diff -` clean, `check-decision-anchors.py` 30 anchors 0 failed,
`tests/unit/test-suite-layout.py` 0.10s exit 0, `tests/integration/test-run-unit-tests-layout.py`
1.4s exit 0.

## Open questions

None blocking. One advisory: the vocabulary deliberately excludes Markdown probe write-ups, so a
future *executable* probe committed as an extensionless script would slip the net — extensionless
files were left out because the tracked tree has none and a mode-bit rule would be a second reader.
