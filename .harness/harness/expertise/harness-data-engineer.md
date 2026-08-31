# Expertise — harness-data-engineer
## Patterns (max 15)
## Gotchas (max 15)
- G-01: WHEN changing the glob in `.claude/skills/harness/bin/inject-expertise.sh` that populates `repo_segments`/`repo_files` DO check the `sort -t: -k2` step nearby — the two share an unenforced assumption that the glob already yields sorted order, and breaking it without revisiting the sort silently reorders repo-tier Expertise segments.
- G-02: WHEN a plan.yaml depends_on edge fails the content-read test DO check for a shared-file write between the two tasks before dropping it — plan-level tasks have no mutates_repo primitive, so depends_on is the only serialization mechanism for such writes; keep the edge, correct its stated reason.
## Outcomes (max 10)
## Open (max 5)
