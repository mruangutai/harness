# Expertise — harness-code-reviewer
## Patterns (max 15)
## Gotchas (max 15)
- G-01: WHEN reviewing check-expertise.sh's REPO_TIER_RE alongside inject-expertise.sh's segment filter DO diff both regexes together — REPO_TIER_RE accepts any `[^/]+` segment but the hook silently drops non-lowercase-alnum-hyphen segments, so checker OK does not mean the hook injects.
- G-02: WHEN reviewing inject-expertise.sh's cap_body DO test a fixture missing its trailing newline at the 40- and 150-line boundaries — its `wc -l` vs `head -n` comparison undercounts by one there and silently drops the over-budget tail with no truncation notice.
- G-03: WHEN reviewing check-expertise.sh's directory-sweep mode over `.harness/*/expertise/` DO build a dangling-symlink fixture — its unguarded `open()` crashes and aborts the sweep, reusing exit 1 with "violations found", so later-sorted files go silently unaudited.
- G-04: WHEN judging whether a script in `.claude/skills/harness/bin/` actually runs in any gate DO check both `run-unit-tests.sh`'s UNIT_SCRIPTS and INTEGRATION_SCRIPTS arrays by exact name — absence from both means even a real-data self-test never executes, however green its own internal logic reads.
- G-05: WHEN writing a feature artifact from inside this repo's FEAT worktree DO use an absolute path — feature.json/plan.yaml/STATE.md live only in the worktree copy while notes/ and runs/ also sync to the main checkout, so a relative write can land in the main checkout and later fail code_grade binding.
## Outcomes (max 10)
## Open (max 5)
