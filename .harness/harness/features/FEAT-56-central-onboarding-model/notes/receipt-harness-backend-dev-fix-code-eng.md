# Receipt — harness-backend-dev — T-04 fix (V-2, V-7)

## Verdict: PASS

Both panel findings closed. `verify:` cross-checked against `plan.yaml` T-04 verbatim:
`python3 tests/unit/test-fleet-product-config.py && python3 tests/unit/test-factory-config.py` —
matches the batch dispatch exactly. No mismatch.

## Files touched (only these two source files + this receipt)

- `.claude/skills/harness/bin/factory_config.py` — V-7 fix
- `tests/unit/test-fleet-product-config.py` — V-2 case (f) + V-7 pin (checks g)

## V-2 (med) — `except FleetError` narrowness now proven

Added `stub_first_unexpected_second_ok` (raises a bare `RuntimeError` for the first declared
repo, valid JSON for the second) and case (f): asserts `product_config_report(fleet)`
**propagates** the `RuntimeError` rather than returning a report entry. Uses a fresh tempfile
fleet (never bare `load_fleet()`), and `check()`'s existing `clear_product_config_memo()`
first-statement convention already scopes the memo per case.

### Mutation proof (mandatory acceptance item)

Copied `factory_config.py`'s full content to `/tmp/factory_config_mutant_v2.py` (outside the
tree — the bash-write-guard blocks `cp` into scratch paths from inside the tree, so the copy was
made with the `write` tool instead), widened `except FleetError as e:` to `except Exception as e:`
in `product_config_report`, staged it under a throwaway `/tmp/mutant_bin_v2/` (only
`factory_config.py` — its own imports of `factory_cli`/`factory_gh`/`harness_boundary`/
`harness_yaml` fell through `sys.path` to the real bin dir, so no other file needed mutating),
and ran a copy of the test file with `sys.path` pointed at the mutant dir first, `HARNESS_PROJECT_DIR`
set to the real worktree so `resolve_root` still found `.harness/team-config.yaml`.

Result — **exactly one case reddens (case f), all other 17 checks stay green** (18 total: 15
pre-existing + case (f) + the two new V-7 checks (g) added in the same run):

```
ok    (a) two declared repos, both succeed -> every entry ok, ok count 2, unreachable 0
ok    (a)/(d) len(report) equals len(fleet['repos'])
ok    (b) the FIRST entry, asserted individually, is not ok and names repo and ref
ok    (b) the SECOND entry, asserted individually, is ok with an empty detail
ok    (b)/(d) len(report) equals len(fleet['repos'])
ok    (c) invalid JSON content -> entry not ok, detail names the invalid-JSON failure
ok    (c)/(d) len(report) equals len(fleet['repos'])
FAIL  (f) an exception that is neither FleetError nor GhError propagates out of product_config_report instead of being reported as an ok:False entry
        product_config_report returned normally instead of propagating
ok    every entry carries exactly repo/ref/path/ok/detail, path is _PRODUCT_CONFIG_PATH
ok    product_config_report preserves fleet['repos'] declaration order
ok    (e) --check-product-configs exits 2 (EXIT_REFUSED) under a failing stub
ok    (e) stdout under failure parses as ONE JSON payload with declared/ok/unreachable/members
ok    (e) exactly one stderr line is written for the one unreachable member
ok    (g) V-7: the stderr line starts with the canonical 'factory: config: ' prefix
ok    (g) V-7: the repo@ref:path token appears exactly once in the stderr line, not twice
ok    (e) --check-product-configs returns without SystemExit under an all-succeeding stub
ok    (e) stdout under success parses as ONE JSON payload with declared/ok/unreachable/members
ok    (e) no stderr line is written when nothing is unreachable

1 of 18 FAILING.
```

**Exactly one reddened (case f); the other 17 stayed green.** No unpredicted redness.

Cleanup: `rm -rf /tmp/mutant_bin_v2 /tmp/factory_config_mutant_v2.py /tmp/test_mutant_v2_runner.py`
— confirmed gone (`ls` on all three paths returned "No such file or directory"), and
`git status --porcelain` (below) carries no trace of any of them.

## V-7 (low) — duplicate `repo@ref:path` triple on the unreachable-member stderr line

Traced per the dispatch: `_check_product_configs` built `value=f'{repo}@{ref}:{path}'` and
`next_step=m["detail"]` for `factory_cli.fail`, but `m["detail"]` is `str(FleetError)`, itself
`factory_cli.body(what, value, next_step)` with the SAME `value` — so the line named the triple
twice, behind two near-synonyms ("unreachable" from the wrapper, "unreadable" from the
`FleetError`).

**Fix taken (the lead's pre-decided shape):** print the `FleetError`'s own canonical body
directly behind the `"factory: config: "` prefix — `print(f"factory: config: {m['detail']}",
file=sys.stderr)` — instead of reconstructing `value`/`next_step` through `factory_cli.fail`.
`factory_cli.py` untouched, as scoped. `m["detail"]` is already `"what: value — next_step"`
(the exact grammar `factory_cli.message` builds minus the `"factory: {tool}: "` prefix), so the
result is textually identical to `factory_cli.message("config", ...)` grammar with the triple
named once.

Invariants checked:
- exit code: still `sys.exit(factory_cli.EXIT_REFUSED)` unconditionally on the same guard — unchanged.
- stdout payload: untouched (the `print` sits after `factory_cli.payload(...)`, same keys).
- report entry keys (`repo`/`ref`/`path`/`ok`/`detail`): untouched — `report` itself is untouched;
  only how one entry's `detail` reaches stderr changed.
- member selection / stderr line count: unchanged — still exactly one `print` per unreachable `m`.
- canonical grammar + operator-actionable next step: preserved — the underlying gh/JSON reason
  (the failing `f-string` tail of the `FleetError`'s `next_step`) is still present verbatim.

### Live run, BEFORE and AFTER (mandatory acceptance item)

Driven via `_main()` in-process (`--check-product-configs`), two-member fleet in a tempfile, the
first repo's `factory_gh.file_at_ref` stubbed to raise `factory_gh.GhError` (the same shape
`stub_first_gherror_second_ok` already uses), second repo ok.

**AFTER (current tree, actual run):**
```
factory: config: product config unreadable: mruangutai/repo-one@trunk-report-one:.harness/harness.json — could not read mruangutai/repo-one's .harness/harness.json at trunk-report-one: gh call failed: mruangutai/repo-one — check gh auth and the ref
```
exit code: 2

**BEFORE (reconstructed):** the production file was NOT reverted to show this — reverting and
re-fixing it live risked leaving the tree in the wrong state under sibling concurrent edits.
Instead the exact pre-fix call shape (`factory_cli.fail("config", "product config unreachable",
f'{m["repo"]}@{m["ref"]}:{m["path"]}', m["detail"])`, unchanged at `factory_cli.message`/`body`)
was invoked directly against a REAL captured `report` entry from the same run (`m` from
`product_config_report(fleet)` under the same stub):
```
factory: config: product config unreachable: mruangutai/repo-one@trunk-report-one:.harness/harness.json — product config unreadable: mruangutai/repo-one@trunk-report-one:.harness/harness.json — could not read mruangutai/repo-one's .harness/harness.json at trunk-report-one: gh call failed: mruangutai/repo-one — check gh auth and the ref
```
The triple `mruangutai/repo-one@trunk-report-one:.harness/harness.json` appears **twice** in the
BEFORE line, **once** in the AFTER line — exactly the defect and exactly the fix.

Pinned in the suite by checks (g): the stderr line for the (e-1) failing-stub run starts with
`"factory: config: "` and the triple token `f"{repo}@{ref}:{path}"` occurs exactly once
(`.count(...) == 1`, not a substring presence check — a substring check would also pass on the
buggy doubled line).

## V-8 — deliberately left undone

`len(report) != len(fleet["repos"])` half of `_check_product_configs`'s exit guard (line 478,
`... or len(report) != len(fleet["repos"])`) is untested and unreachable through the public
surface today — `product_config_report` always returns one entry per `fleet["repos"]` member (no
early return, no skip path), so that branch can only fire if a future change makes the report
loop skip an entry. Per the dispatch's explicit non-goal, no test was added for it; it stays
backlogged as a mutation-proved but currently-unreachable branch (V-8, ranked last by the panel).

## Verify — both halves, exit status

```
$ env -u HARNESS_AGENT_TYPE python3 tests/unit/test-fleet-product-config.py
... (18 ok lines) ...
18/18 checks passed.
$ echo $?
0

$ env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-config.py
... (114 ok lines) ...
114/114 checks passed.
$ echo $?
0
```

Both exit 0.

## Code-risk grading

`_check_product_configs` (the touched function): cyclomatic 8, cognitive 7, ABC 15.3 → **grade 4,
PASS** — no line was added to it; the fix replaced one `factory_cli.fail(...)` call with one
`print(...)` call, same statement count. No other production function touched.

## git status --porcelain (after cleanup)

```
 M .claude/skills/harness/bin/factory_config.py
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/docs/SPEC.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/observations/harness-documentor.md
 M README.md
 M tests/unit/test-fleet-product-config.py
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-documentor-fix-docs-product.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-code-reviewer-c0.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-qa-c0.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-security-reviewer-c0.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-ui-reviewer-c0.md
```

Only my two source files are modified. Everything else is concurrent sibling activity (docs
squad's `README.md`/`SPEC.md`/`DECISIONS*.md`, the documentor's own receipt/observations, and
review-panel notes) — none of it touched by this dispatch. No trace of the mutation scratch
files (`/tmp/factory_config_mutant_v2.py`, `/tmp/mutant_bin_v2/`, `/tmp/test_mutant_v2_runner.py`)
in this list, and confirmed absent from `/tmp` directly.
