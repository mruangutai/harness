# Receipt — harness-dev-ops — FEAT-27 FIX-01 (fixture-c1)

## Task

FIX-01: refresh stale `COLLECT_FIXTURE` in
`.claude/skills/harness/bin/test-harness-yaml.py` after T-01 (`c4d5bc5`) added a
repository-tier grant line to six agents in `.harness/team-config.yaml`.

## Diagnosis confirmed independently

Read `.harness/team-config.yaml` directly (not the parser under test) for each of the
six named agents. In every case the new grant `.harness/*/expertise/<agent>.md` sits
immediately beneath that agent's craft grant `.harness/expertise/<agent>.md`, above the
`observations/<agent>.md` line — confirmed with `sed -n` over the exact line ranges for
harness-orchestrator (L24-35), harness-pm (L84-100), harness-documentor (L116-133),
harness-backend-dev (L160-173), harness-dev-ops (L203-217), harness-eng-lead (L295-302).

## Fix

Inserted `.harness/*/expertise/<agent>.md` at that exact position in each of the six
`COLLECT_FIXTURE` entries in `test-harness-yaml.py`. `.harness/team-config.yaml` was not
touched. No other file was modified.

## Verify — both suites, full output scanned (not tailed)

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```
Exit: 0. `grep -c '^FAIL '` over the full captured output: **0**.

```
.claude/skills/harness/bin/run-unit-tests.sh --kind integration
```
Exit: 0. `grep -c '^FAIL '` over the full captured output: **0**.
`PASS test-harness-yaml.py` present. Final line: `106/106 checks passed. PASS
test-factory-integration.py`.

Re-ran both suites a second time after the redden-proof restore (below) to confirm the
restored file is still green — same result: exit 0, 0 `^FAIL ` lines, both suites.

## Redden-proof

Removed the `.harness/*/expertise/harness-dev-ops.md` line from the harness-dev-ops
entry only, re-ran `--kind integration`:

```
FAIL test_manifest_domains_matches_the_regex_walk_on_the_real_manifest: harness-dev-ops: mine mismatch
  got:      [..., '.harness/expertise/harness-dev-ops.md', '.harness/*/expertise/harness-dev-ops.md', '.harness/*/features/*/observations/harness-dev-ops.md']
  expected: [..., '.harness/expertise/harness-dev-ops.md', '.harness/*/features/*/observations/harness-dev-ops.md']
FAIL test-harness-yaml.py
```

Confirmed FAIL, as expected — the test still discriminates. Restored the line, then:

```
git diff --stat .claude/skills/harness/bin/test-harness-yaml.py
 .claude/skills/harness/bin/test-harness-yaml.py | 6 ++++++
 1 file changed, 6 insertions(+)
```

`git diff` (full) shows exactly six added lines, one per agent, each the single
repository-tier fixture entry — no other change, no deletions, no unintended edits. Both
suites re-run green after restore (see Verify section above).

## Git status (unfiltered, both before and after)

Before and after this cycle, `git status --short` showed only
`.claude/skills/harness/bin/test-harness-yaml.py` as modified by me. Other modified/
untracked entries belong to other in-flight agents on FEAT-27/26/28/29 and were left
untouched.

## Advisory finding (not fixed, per dispatch instruction)

`test-harness-yaml.py`'s docstring around line 27-30 and the test's own docstring
("D-03 equivalence proof: manifest_domains() must equal the pre-change collect() logic")
describe `COLLECT_FIXTURE` as proving equivalence to a `collect()` function. That function
was deleted under DEC-171 (regex-based YAML parsing removed). The fixture is now a
hand-maintained frozen snapshot with nothing left to prove equivalence to — every
legitimate manifest change (like T-01's) reddens it, and someone must hand-derive the new
expected value each time, exactly as done in this cycle. The docstring is misleading about
what the test currently protects. Whether the fixture should exist in this form, be
regenerated some other way, or be retired is a plan question — not touched here, per
dispatch instruction not to rewrite the test's purpose or docstring.
