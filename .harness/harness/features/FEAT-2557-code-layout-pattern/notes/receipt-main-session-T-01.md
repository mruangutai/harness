# Receipt — T-01, main session (DEC-174 direct) — 2026-11-27

Executed at the worktree tip before the T-01 commit (base ef69b397), with all five files written. Exit 0.

## verify (verbatim from plan.yaml)

```sh
set -eu
unset HARNESS_AGENT_TYPE
f=.claude/skills/harness/bin/LAYOUT.md; b=.claude/skills/harness/bin; s=.claude/skills/harness-codebase-design/SKILL.md; d=.harness/harness/docs/DECISIONS.md
test -f "$f"
for t in check-state.py check_state/ plan-merge.py plan_merge/ __init__.py sys.path harness_boundary.py harness_merge.py; do grep -qF -- "$t" "$f" || { echo "MISSING $t"; exit 1; }; done
for p in check-state.py check_state/__init__.py plan-merge.py plan_merge/__init__.py harness_boundary.py harness_merge.py; do test -f "$b/$p" || { echo "ABSENT $p"; exit 1; }; done
test ! -s "$b/check_state/__init__.py" && test ! -s "$b/plan_merge/__init__.py"
if grep -Eqiw 'lines|size|grade|graded' "$f"; then echo "FORBIDDEN size/grade wording"; exit 1; fi
if grep -Eq '^#{1,6} +A split|FEAT-|DEC-174' "$f"; then echo "FORBIDDEN section/provenance"; exit 1; fi
test "$(grep -c '^## Layout — where a split lands$' "$s")" = 1
sec=$(awk '/^## Layout — where a split lands$/{f=1;next} /^## /{f=0} f' "$s")
for t in delete-first utils helpers common shim review; do printf '%s\n' "$sec" | grep -qF -- "$t" || { echo "LAYOUT MISSING $t"; exit 1; }; done
if printf '%s\n' "$sec" | grep -Eq 'bin/|\.py|__init__|LAYOUT'; then echo "LAYOUT NOT LANGUAGE-NEUTRAL"; exit 1; fi
app=$(awk '/^## Applying it$/{f=1;next} /^## /{f=0} f' "$s")
for t in 'prefixed siblings' shim 'project map' AGENTS.md; do printf '%s\n' "$app" | grep -qF -- "$t" || { echo "APPLYING MISSING $t"; exit 1; }; done
test "$(grep -cF '.claude/skills/harness/bin/LAYOUT.md' AGENTS.md)" = 1
map=$(awk '/^## Project map$/{f=1;next} /^## /{f=0} f' AGENTS.md); printf '%s\n' "$map" | grep -qF '.claude/skills/harness/bin/LAYOUT.md'
conv=$(awk '/^## Conventions$/{f=1;next} /^## /{f=0} f' AGENTS.md); printf '%s\n' "$conv" | grep -qxF -- '- Before writing code, read the harness-codebase-design skill and, for Harness `bin/`, the layout entry in the project map.'
git diff --quiet HEAD -- .claude/skills/harness-craft/references/delete-first.md
test "$(grep -c '^## DEC-259 — ' "$d")" = 1
dsec=$(awk '/^## DEC-259 — /{f=1} f' "$d")
for t in FEAT-69 FEAT-70 FEAT-71 harness-codebase-design LAYOUT.md AGENTS.md D-01; do printf '%s\n' "$dsec" | grep -qF -- "$t" || { echo "DEC-259 MISSING $t"; exit 1; }; done
grep -Eq '^- DEC-259 @[0-9]+ .* :: .{20,}' .harness/harness/docs/DECISIONS-INDEX.md
python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
python3 .claude/skills/harness/bin/check-decision-anchors.py
python3 tests/integration/test-gen-decisions-index.py
base=$(git merge-base HEAD main)
got=$( { git diff --name-only "$base" -- . ':!.harness/harness/features/FEAT-2557-code-layout-pattern'; git ls-files --others --exclude-standard -- . ':!.harness/harness/features/FEAT-2557-code-layout-pattern'; } | sort -u)
want=$(printf '%s\n' .claude/skills/harness-codebase-design/SKILL.md .claude/skills/harness/bin/LAYOUT.md .harness/harness/docs/DECISIONS-INDEX.md .harness/harness/docs/DECISIONS.md AGENTS.md | sort -u)
test "$got" = "$want" || { echo "SCOPE DRIFT"; printf '%s\n' "$got"; exit 1; }
echo LAYOUT-SKILL-AGENTS-DEC-OK

```

## Output (complete, 14 lines)

```text
examined 25 anchor(s), 0 failed
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_refs_graph_omits_ids_with_no_live_heading
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
ok - test_committed_index_matches_a_fresh_regeneration
ok - test_committed_index_is_complete_and_within_budget
ok - test_orphaned_ruling_is_reported_not_silently_dropped
ok - test_root_resolves_through_harness_boundary_not_the_retired_variable
ok - test_no_amendment_construct_survives_in_the_authority
ok - test_dec_233_entry_names_every_removed_enforcement_point
LAYOUT-SKILL-AGENTS-DEC-OK
```
