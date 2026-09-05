# Expertise — harness-code-reviewer
## Patterns (max 15)
## Gotchas (max 15)
- G-01: WHEN reviewing check-expertise.sh's REPO_TIER_RE alongside inject-expertise.sh's segment filter DO diff both regexes together — REPO_TIER_RE accepts any `[^/]+` segment but the hook silently drops non-lowercase-alnum-hyphen segments, so checker OK does not mean the hook injects.
- G-02: WHEN reviewing inject-expertise.sh's cap_body DO test a fixture missing its trailing newline at the 40- and 150-line boundaries — its `wc -l` vs `head -n` comparison undercounts by one there and silently drops the over-budget tail with no truncation notice.
- G-03: WHEN reviewing check-expertise.sh's directory-sweep mode over `.harness/*/expertise/` DO build a dangling-symlink fixture — its unguarded `open()` crashes and aborts the sweep, reusing exit 1 with "violations found", so later-sorted files go silently unaudited.
- G-04: WHEN judging whether a test actually runs in a Harness gate DO confirm it sits under `tests/unit/` or `tests/integration/` — a test-shaped file elsewhere is discovered by no runner, and one left under bin makes the layout guard reject every invocation.
- G-05: WHEN writing a feature artifact from inside this repo's FEAT worktree DO use an absolute path — feature.json/plan.yaml/STATE.md live only in the worktree copy while notes/ and runs/ also sync to the main checkout, so a relative write can land in the main checkout and later fail code_grade binding.
- G-06: WHEN reading a code-grade.py report DO remember it only lists functions with no pre-image (new) or a worsened grade versus base — it never emits an 'inherited, unrelated, unchanged' record, so a partition claiming that shape for any listed record is definitionally wrong.
- G-07: WHEN reviewing run_pool.py's --mutation-check snapshot DO note `_record`'s `except OSError` swallows every OSError, not only FileNotFoundError — removing a watched directory's execute bit mid-run hides any file created inside it from both snapshots (open backlog row, unresolved as of this build).
- G-08: WHEN reviewing suite_layout.py violations() DO check whether _registry_findings runs unconditionally on any successful git enumeration, independent of the self-ownership test -- it misfires on a checkout that does not itself ship suite_layout.py, past a narrower one-prefix assertion that misses it (open, unresolved).
## Outcomes (max 10)
## Open (max 5)
