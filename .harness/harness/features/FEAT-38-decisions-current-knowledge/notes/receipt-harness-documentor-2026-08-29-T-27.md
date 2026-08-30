# Receipt — harness-documentor — FEAT-38 T-27

**All eleven `<!-- claim: ... -->` markers are gone from `.harness/harness/docs/DECISIONS.md`. The diff is
deletions only — 20 lines, ZERO insertions — and every removed line is either a marker comment or a
blank line. No prose line was removed, changed, or added.** The verify block quoted from `plan.yaml`
T-27 `verify:` (lines 1997-2006) exits 0. Cross-checked against the plan before running: identical.

## Per-entry marker counts (measured, not inherited)

Attributed by walking `^## DEC-` headings above each marker, not by remembered line number:

| Entry | Markers | Pre-edit lines |
|---|---|---|
| DEC-145 | 1 | 3229 |
| DEC-157 | 1 | 3582 |
| DEC-181 | 3 | 4775, 4776, 4782 |
| DEC-183 | 3 | 4912, 4933, 4977 |
| DEC-193 | 1 | 5310 |
| DEC-205 | 2 | 6290, 6291 |
| **total** | **11** | |

Matches the plan's stated distribution exactly. Baseline positive control: `git show 48bbe7e:$D |
grep -c '<!-- claim:'` = 11. Working tree at spawn was clean for this file (HEAD `c9b85a4`), so the
whole diff below is mine.

## Verbatim diff (`git diff -- <D> | grep -E '^[-+]' | grep -v '^[-+][-+][-+]'`)

```
-<!-- claim: grep -F "CRAFT_LINE_BUDGET = 150" .claude/skills/harness/bin/check-expertise.sh :: CRAFT_LINE_BUDGET = 150 -->
-
-<!-- claim: grep -F "\"max_total_cycles\": 10" .harness/harness.json :: "max_total_cycles": 10 -->
-
-<!-- claim: grep -F "budget is 80 (DEC-181)" .claude/skills/harness/bin/check-domain.sh :: budget is 80 (DEC-181) -->
-<!-- claim: grep -c -m 81 -e "" CLAUDE.md :: 12 -->
-
-<!-- claim: grep -F "budget is 300" .claude/skills/harness/bin/check-domain.sh :: budget is 300 -->
-
-<!-- claim: grep -F "name: Plan-route gate" .github/workflows/tests.yml :: name: Plan-route gate -->
-
-<!-- claim: grep -F "violation(s) across" .claude/skills/harness/bin/check-plan-routes.py :: violation(s) across {processed} plan(s) -->
-
-<!-- claim: grep -F "run-unit-tests.sh" .github/CODEOWNERS :: run-unit-tests.sh  @mruangutai -->
-
-<!-- claim: grep -F "WORKTREES_SEGMENT = " .claude/skills/harness/bin/harness_boundary.py :: WORKTREES_SEGMENT = ".claude/worktrees" -->
-
-<!-- claim: grep -F "ALLOWED_FIRST_TOKENS = " .claude/skills/harness/bin/check-decision-claims.py :: ALLOWED_FIRST_TOKENS = {"git", "grep"} -->
-<!-- claim: grep -F "test-check-decision-claims.py" .claude/skills/harness/bin/run-unit-tests.sh :: test-check-decision-claims.py -->
-
```

11 marker lines + 9 blank lines = 20. `git diff --stat`: `1 file changed, 20 deletions(-)`.

**SC-13's operator PASS stands: no prose was touched, so the assumption it rests on is not void.**

## Blank-line handling

Every marker sat in a `text / BLANK / marker(s) / BLANK / text` sandwich, so each of the 9 marker
groups (two are adjacent pairs — DEC-181's 4775/4776 and DEC-205's 6290/6291) needed exactly one
blank deleted with it; hence 9 blanks, not 11.

Proof no double blank was introduced or left: the file's double-blank count and its full anchor
sequence are byte-identical to `HEAD` (52 both sides, `identical anchor sequence: True`) — the 52
pre-existing ones sit inside fenced blocks and are untouched. All nine former sites now read
`TEXT/BLANK/TEXT`, checked by content anchor rather than line number (P-04).

## Scope held

- Markers **deleted, not translated.** Zero insertions is the mechanical proof no successor
  vocabulary entered the prose. None exists; the declarative replacement was rejected by the operator.
- **Over-deletion guard clear.** `check-decision-anchors.py` and `test-check-decision-anchors.py`
  both still exist and are unmodified — they only share a filename prefix with the deleted mechanism.
  `check-decision-claims.py` / `test-check-decision-claims.py` remain on disk; they are T-24's.
- **Not touched:** DEC-205 rule 6b, its heading, its enumeration sentence (T-28); `DECISIONS-INDEX.md`
  (T-28 owns the single regeneration); `plan.yaml`, `BRIEF.md`, `feature.json`, `STATE.md`. No commit
  made — the edit is left in the working tree (DEC-153).
- `git status` shows only `M .harness/harness/docs/DECISIONS.md` (plus an unrelated untracked
  `.harness/logs/2026-08-29.md` I did not create).

## Note for T-28, not a defect

`DECISIONS.md` item 2 under DEC-205 still opens *"**Executable claims.** Where an entry states
something a command can check, it records the command…"* (post-edit line 6265). That sentence is
inside T-28's declared scope (rule 6b and the enumeration), so I left it verbatim — but it now
describes a mechanism with no markers behind it. **T-28 must land, or the document describes a
convention that no longer appears in it.** Index rows for the six edited entries will recompute
their anchor offsets when T-28 regenerates (P-14) — an effect of this edit, not a generator defect.

## Open questions

None blocking.
