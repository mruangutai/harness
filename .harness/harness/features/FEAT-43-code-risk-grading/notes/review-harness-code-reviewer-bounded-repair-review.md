# Code review — bounded CI reconciliation (test-check-plan-routes.py hermeticity + feature.json cleanup)

**Pin reviewed:** `d94f611..41d9afec139cdb50eae490330620c590068b23ed`
(two commits: `14c6100` "test: make route regression hermetic", `41d9afe` "test: encode retired
boundary fixture" — both authored by the operator directly, no `[harness:human]` tag, but
explicitly the assigned review scope). No production source touched — 4 files total: the test
file, three `fixtures/prior-*` files, and `feature.json`.

**BLUF: PASS.** All four contract clauses hold, each independently verified (not just read):

## 1. No runtime dependence on repository history

`write_prior_route_validator` (`test-check-plan-routes.py:1519-1538`) no longer calls
`git … show <PRE_FEATURE_REVISION>:<path>`; `grep -n "PRE_FEATURE_REVISION\|git.*show"` over the
whole file returns only an unrelated docstring mention of `git status`. The three prior-source
files are read from `.claude/skills/harness/bin/fixtures/*.fixture[.b64]`, committed, tracked
(`git ls-files` confirms all three + the pre-existing unrelated `prior-validate-digest.py.fixture`).
`case_27b_prior_revision_false_ok` (`:1576-1583`) still exercises the real subprocess against the
fixture-written file named `check-plan-routes.py`, same assertion shape as before the fix.

## 2. Fixture decoding does not silently change the intended bytes

Independently reproduced, not trusted from the code: `git show
df63193f7ec9798d9660904e0e4e7c78d52358f5:<path>` for all three original files, `diff`'d against
what the test now materializes at runtime —
- `prior-check-plan-routes.py.fixture` — byte-identical (plain text).
- `prior-harness_yaml.py.fixture` — byte-identical (plain text).
- `prior-harness_boundary.py.fixture.b64` — `base64.b64decode(...).decode("utf-8")` reproduces the
  original file byte-for-byte (`diff` empty).

## 3. Retired distribution tokens are not exposed to repository-wide scanners

`test-no-distribution.py` case 6 scans every tracked file (excluding `test-*` basenames,
`harness_boundary.py` itself, `*.md`, and the record-tree prefixes) for the literal retired chain
name `HARNESS_PROJECT_DIR`. The three new fixture files live under
`.claude/skills/harness/bin/fixtures/` — none of the four exclusions apply to them, so they are
in-scope for that scan. Grepped directly: the decoded `harness_boundary.py` fixture contains
`HARNESS_PROJECT_DIR` five times (lines 56/65/70/78/296 of the decoded source — it is the resolver
module, the historical predecessor of the file the scan exempts by basename only for the *current*
copy). The other two fixtures contain zero occurrences of that token, or of the deploy-mechanism
tokens case 2 separately bans (`harness-deploy`, `deploy.sh`, `harness-registry`, `registry.json`).
Base64-encoding is applied to exactly the one fixture that needed it — confirmed necessary, not
decorative: as plain text it would be an undeclared, un-excluded literal-string site and would fail
`case6_absence_the_env_chain_occurs_nowhere`. The commit history corroborates this was found the
hard way: `14c6100` first vendored `harness_boundary.py` as plain text (606 lines), and `41d9afe`
immediately re-encoded it to `.b64` in the very next commit, replacing the plaintext file 1:1 with
no orphaned duplicate left behind.

## 4. `feature.json` is schema-valid

The prior state had a top-level `"briefing"` key not declared in `feature-schema.json`'s
`properties` (`additionalProperties: false` at the top level, confirmed by reading the schema) — an
invalid document. `41d9afe`'s predecessor commit deleted it; validating the current
`feature.json` against `feature-schema.json` with `jsonschema.validate` passes. No reader of
`feature.json`'s top-level `briefing` key exists in `.claude` (only `validate-digest.py`'s
*digest*-schema `briefing` field, an unrelated per-run key nested under `runs[]`, not this key) —
removal drops nothing anything consumes.

## Also checked (fail-open hunt)

- `write_prior_route_validator` fails **closed**: a missing/renamed fixture raises
  `FileNotFoundError`; a mis-decoded `.b64` payload would not be valid Python and the subprocess
  in `case_27b` would exit non-zero, tripping the check rather than silently passing.
- The two fixtures scanned by `test-no-distribution.py` case 6's `DELETED_NAMES` sub-check (they
  live under `.claude/skills/harness/bin/` and don't start with `test-`, so are in-scope for that
  loop too) contain none of `harness_root` / `_repo_root_from_script` / `_root_from` /
  `_resolve_repo_root` — no false trip there either.
- `code_grade.py`'s self-grading only considers changed paths ending `.py`
  (`code_grade.py:341`); `*.fixture` / `*.fixture.b64` are excluded from the graded set,
  consistent with the precedent already shipped for `prior-validate-digest.py.fixture` in cycle 27.

## Note (does not gate)

`write_prior_route_validator`'s `fixture.endswith(".b64")` dispatch has no inline comment
explaining *why* `harness_boundary.py`'s fixture alone is base64-encoded while its two siblings are
plain text. The reason is real and load-bearing (§3 above) but lives only in the commit message and
in `test-no-distribution.py`'s case 6, not at the call site — a future edit could "simplify" it back
to uniform plain text and silently reopen the scanner exposure. Worth a one-line comment; `info`,
non-blocking.

```yaml
VERDICT: PASS
DIGEST:
  headline: "test-check-plan-routes.py hermeticity fix, boundary-fixture encoding, and feature.json cleanup all verified correct; no substantive findings"
  severity_max: info
  findings: 1
  must_fix: []
  spec_violations: []
  reviewed: "d94f611..41d9afec139cdb50eae490330620c590068b23ed"
  human_commits_in_scope: [14c6100, 41d9afe]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-bounded-repair-review.md
```
