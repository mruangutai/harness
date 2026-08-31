# Receipt — harness-backend-dev — T-12 — run 2026-08-29-07-eng

## Environment incident (read this first)

The `edit`/`write` tool family in this session resolved worktree-relative paths against the
**MAIN checkout** (`/Users/molchairuangutai/GitHub/harness`), not the assigned worktree, while
reporting success and showing plausible-looking diffs on every call (a repeat call on the same
line even reported "byte-identical"). `bash`/`git status` inside the worktree showed zero
change; `git status` inside the MAIN checkout showed my edits landing there instead, plus one
stray probe file from a `write`-tool test. I diffed the main checkout to confirm only my
intended edits were present (nothing else touched), restored the 9 affected files there from
`git show HEAD:<path>` content via plain `cp` (no git command run against the main checkout, per
constraint), deleted the stray probe file, and confirmed the main checkout returned to a clean
`git status` matching its pre-session state. I then redid every edit via `bash`/`python3 -c`
(inline argument, not a heredoc — heredocs targeting out-of-domain scratch paths tripped
`bash-write-guard`) directly against the worktree, verifying with `git status`/`git diff` in the
worktree after each batch. Main checkout is confirmed clean; no HEAD movement, no git commands
run against main. Filed as an `open_questions` item below since it is an environment defect, not
a decision.

## Verify block — VERBATIM, exit 0

Cross-checked against plan.yaml T-12 lines 949-958: identical.

```
cd "$(git rev-parse --show-toplevel)"
B=.claude/skills/harness/bin
X='--exclude-dir=__pycache__'
grep -rnE $X 'am\.[0-9]|DEC-[0-9]+ amendment' "$B" && exit 1
for n in 19 20 37 67 82 88 92 102 103 104 137 140 186 192 196; do
  grep -rnE $X "DEC-$n([^0-9]|$)" "$B" && { echo "cites DEC-$n"; exit 1; }
done
grep -rq $X 'DEC-' "$B" || { echo "sweep deleted all DEC citations - too broad"; exit 1; }
exit 0
```
Result: **exit 0**. No `am.N`/amendment hits, no deleted-id hits, and `DEC-` citations still
present under `bin/` (e.g. DEC-200, DEC-203, DEC-138, DEC-171 among many others) — the breadth
guard did not fire.

`X` correctly excludes `__pycache__`; no stray `.pyc` matches were observed or needed handling.

## Re-derived pre-edit occurrence counts vs. the plan's 7ebfc9e figures

Re-measured against the CURRENT tree (before my edits, after T-05/T-07/T-08/T-10 had already
landed in this feature's build) using the verify script's own grep shape:

| id/pattern | 7ebfc9e (plan) | current tree (re-derived) | explanation |
|---|---|---|---|
| `am.N`/amendment | 22 across 14 files | 15 across 12 files | T-10 removed `gen-decisions-index.py`'s 3 (not in my list); some of the remainder had already migrated off `am.N` wording in T-05/T-07/T-08 product-lane commits that predate this dispatch. |
| DEC-19 | 8 | 5 | T-05/T-07/T-08 (my task's own dependencies) already repointed 3 of the 8 elsewhere in the tree before T-12 ran. |
| DEC-20/37/67/88 | 0/0/0/0 | 0/0/0/0 | matches |
| DEC-82/92 | 1/1 | 0/0 | already cleared by T-05/T-07/T-08 before T-12 ran |
| DEC-102 | 14 | 0 | already cleared by T-05/T-07/T-08 before T-12 ran |
| DEC-103 | 0 | 0 | matches |
| DEC-104 | 3 | 1 | 2 of the 3 already cleared upstream; the 1 remaining is `test-gen-decisions-index.py`'s historical-narrative comment (the special-case rewrite) |
| DEC-137 | 4 | 1 | 3 already cleared upstream; 1 remaining in `test-no-distribution.py` |
| DEC-140 | 0 | 0 | matches |
| DEC-186 | 7 | 7 | matches |
| DEC-192 | 16 | 13 | 3 already cleared upstream |
| DEC-196 | 0 | 0 | matches |

Git log confirms the mechanism: commits `57a3bf3`/`6efc88d`/`09e3d7b` (T-01–T-09, T-15, product
lane) and `204b469` (T-06/T-17, eng lane A) already repointed a number of citations across the
tree, including inside files on T-12's own list, before this dispatch ran — consistent with
"15 entries have been deleted since 7ebfc9e" and T-12's `depends_on: [T-05, T-07, T-08, T-10]`.

## Rewrite census (42 sites total, 0 outright deletions)

- **Case 1 — am.N fold into bare DEC-N**: 15 sites (`harness_yaml.py`, `test-harness-yaml-corpus.py`,
  `upgrade-config.py`, `factory_decompose.py`, `test-dispatch-guard.py`, `test-no-distribution.py`,
  `plan-merge.py`, `test-check-state.py`, `test-team-catalog.py`, `check-state.sh`,
  `check-domain.sh`, `gh-sync.py` x4). Every fold checked against DEC-171/DEC-138/DEC-174's
  current (post-fold) body for continued truth.
- **Case 2 — successor swap**: 21 sites. DEC-137→DEC-162 (1), DEC-186→DEC-203 (7, including the
  two INV-24 identifier renames), DEC-192→DEC-203 (13).
- **Case 3 — pattern name restated in words, citation dropped**: 5 sites, all DEC-19
  (`gh-sync.py:34` "unenforced write path around a guarded surface"; `test-validate-digest.py:315`
  and `validate-digest.py:722` — dropped from a `DEC-19/DEC-110/DEC-119` / `DEC-19 / DEC-110 /
  DEC-119` list, leaving the still-valid DEC-110/DEC-119 citations, since the pattern is already
  spelled out in the surrounding prose; `check-state.sh:6` and `validate-digest.py:872` —
  restated as standalone prose since each already carries its own in-line explanation).
- **Special rewrite — historical narrative → current arrangement**: 1 site
  (`test-gen-decisions-index.py`), per the dispatch's explicit instruction: dropped the DEC-104/
  DEC-188 historical narrative, kept the "assert the relationship, never a frozen total" framing
  and stated the test now checks that harvested ids never exceed the raw count and never repeat.
- **Outright deletions with no replacement text**: **0**, individually justified above — every
  site got a bare-DEC citation, a successor citation, or a standalone prose restatement.

15 + 21 + 5 + 1 = 42, matching the re-derived pre-edit total (15 am.N + 5 DEC-19 + 1 DEC-104 +
1 DEC-137 + 7 DEC-186 + 13 DEC-192 = 42).

## INV-24 rename

Renamed the identifier in both `check-state.sh:943` (`# --- INV-24 (DEC-186):` →
`# --- INV-24 (DEC-203):`) and `test-check-state.py:995` (`"""INV-24 (DEC-186):` →
`"""INV-24 (DEC-203):`) in the same batch. Invariant NUMBER (`INV-24`) unchanged; only the
parenthetical citation changed. The actual runtime match in `test-check-state.py`'s `case_s`
check is `"INV-24" in l` (substring on stdout lines), which never includes the `(DEC-...)`
parenthetical — so this identifier is not load-bearing for the assertion, but I renamed both
per the dispatch instruction regardless.

```
$ python3 .claude/skills/harness/bin/test-check-state.py
```
Exit status: **0**. Census: **145 `ok`, 0 `FAIL`** (full suite, all cases including the 14
`INV-24` cases in `case_s`, all passing).

## check-domain.sh anchor line

`out.append(_head(f"CLAUDE.md is {len(lines)} lines — budget is 80 (DEC-181)."))`

- Before edit: line **1335** (grepped)
- After edit: line **1335** (grepped, unchanged)

My only edit to `check-domain.sh` was at line 775 (`DEC-171 am.1's logic` → `DEC-171's logic`),
a single-line in-place rewrite with no line added or removed (`git diff --stat`: `1 file
changed, 1 insertion(+), 1 deletion(-)`), so nothing above line 1335 shifted. The DECISIONS.md
anchor `check-domain.sh:1335` remains correct.

## Scope

Touched exactly the 20 files in T-12's `files:` list, plus this receipt and the observations
log. Did not touch `gen-decisions-index.py` (T-10's file, not mine — confirmed its `am.1`
occurrences are already gone, so T-10 has landed and the verify's coverage of that file is
clean). Did not touch `.harness/logs` or any other feature's notes.

## Open questions

- { id: Q1, question: "The `edit`/`write`/`read` tool family in this session resolved
  worktree-relative paths against the MAIN checkout instead of the assigned worktree while
  reporting success on every call (see incident note above). I recovered without moving HEAD or
  running git commands against the main checkout, and confirmed the main checkout's git status
  is clean of my edits. This looks like a harness/tooling environment defect rather than
  anything task-specific — flagging for whoever owns the OMP/tool-routing layer.",
  blocking: false }
