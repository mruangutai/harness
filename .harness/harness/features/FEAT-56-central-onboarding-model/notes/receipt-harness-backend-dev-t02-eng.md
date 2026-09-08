# Receipt — harness-backend-dev — T-02 (FEAT-56-central-onboarding-model)

## BLUF

All six edits are made and each of the 12 file-scoped grep conjuncts named in T-02's `verify:`
passes. `bash -n` / `ast.parse` are clean on all six files. The full literal `verify:` command
still exits 1 — **not because of anything in the six files**, but because its
`python3 check-instruction-paths.py` conjunct scans the whole repo and the main session's
concurrent, uncommitted edit to `.claude/skills/harness/templates/README.md` (explicitly out of
my domain, per this dispatch's CONCURRENCY note) currently leaves two unanchored instruction
paths there. Re-running the same command once that file lands its own anchoring will go green;
nothing further is needed on the six files this task owns.

## Cross-check (step 1)

`plan.yaml` T-02 `intent:` and `verify:` are byte-identical to the dispatch's pasted blocks. No
mismatch.

## RED run (step 2, unedited tree)

```
$ bash -c '<verify block, verbatim>'
(exit 1)
```
First failing conjunct (checked individually): `grep -qF 'anchor rule' .claude/skills/harness/bin/check-instruction-paths.py` — absent pre-edit, as expected, since none of the six sites had been touched yet. All twelve individual conjuncts checked one at a time pre-edit:
1a pass / 1b **FAIL** / 1c(neg) pass / 2a **FAIL** / 2b(neg) pass / 3a **FAIL** / 3b(neg) pass /
4a **FAIL** / 4b **FAIL** / 5a **FAIL** / 5b(neg) pass / 6a **FAIL** / 6b(neg) pass.

## Edits made (step 3), one file at a time

1. `check-instruction-paths.py:12-18` — two-line comment above `MAIN_SESSION_ONLY` naming the
   anchor rule as the reason for exclusion (not ownership); `"harness-init"` entry's trailing
   comment now states both the anchor-rule reason and the main-session-only fact in one clause.
2. `check-state.sh`:
   a. `:111` — no-`.harness/` message now names "this clone" and directs `/harness-init` "in
      the control-plane clone".
   b. `:287` — `.harness/harness.json missing` remedy gains ", in this clone".
   c. `:405-409` — INV-32 `panel_era_start` remedy keeps `/harness-init --upgrade
      (upgrade-config.py)` and adds "against this clone's own harness.json".
   d. `:2434-2436` — INV-31 rationale gains "whose subject is the control-plane clone".
3. `check-domain.sh:383-388` — fail-open message now reads "enforcement OFF. That path is the
   control plane's own manifest; a product repository never carries one. Run /harness-init in
   the control-plane clone." `_run_domain` flag/exit behaviour and the f-string are untouched.
4. `upgrade-config.py`:
   - `:2-7` (docstring) — states the subject: control-plane clone's own harness.json vs. a
     fleet member's own harness.json in a checkout, which must reach the repository's default
     branch to be read.
   - `:191-193` — no-`harness.json` remedy names "this control-plane clone" and "in this
     clone".
   - `:233-237` — team-config.yaml MISSING remedy adds that a team-config.yaml exists only in
     the control plane, so the message is about this clone.
5. `gh-sync.py:255-256` — skip message now reads "github.repo is not pinned in this project's
   harness.json; for a fleet member, that file lives in the member's own repository on its
   default branch". `skip()` and surrounding control flow untouched.
6. `layout_migration.py:121-126` — MARKER rationale's false "harness-init installs the whole
   bin/ into product repos" sentence replaced with: any copy/worktree of the control plane
   carries every reader file, and only the control plane carries the fleet declaration —
   onboarding installs no bin/ into a product repository at all. `MARKER`, the D-04 reference,
   and every following sentence about applicability/segment authority are unchanged.

## GREEN run — the six file-scoped conjuncts (step 4)

```
$ bash -c '<all 12 grep conjuncts for the six files, no python3/bash calls>'
(exit 0)
```
All 12 conjuncts (present-and-absent pairs across the six files) pass individually and jointly.

`bash .claude/skills/harness/bin/check-domain.sh --resolve "$PWD/README.md"` → prints
`harness-documentor`, exit 0.

## Full literal `verify:` (still red, cause external)

```
$ bash -c '<full verify block verbatim>'
VIOLATION .claude/skills/harness/templates/README.md:4: unanchored instruction path: .harness/harness.json
VIOLATION .claude/skills/harness/templates/README.md:10: unanchored instruction path: .harness/harness.json
scanned 62 file(s), 2 violation(s)
(exit 1)
```
`git diff HEAD -- .claude/skills/harness/templates/README.md` confirms this is the main
session's own in-progress, uncommitted edit (adding fleet-member language, not yet anchored) —
a file this dispatch explicitly names as concurrently owned by the main session and forbidden
to me. None of the six files this task owns are implicated in either violation line.

## Syntax gates (step 5)

- `bash -n check-state.sh` — OK
- `bash -n check-domain.sh` — OK
- `python3 -c "import ast; [ast.parse(...) for the four .py files]"` — OK

## git status --porcelain (step 6)

Names the six owned files, plus `.claude/commands/harness-grilling.md`,
`.claude/commands/harness-plan.md`, `.claude/commands/harness.md`,
`.claude/skills/harness/references/github-mirror.md`,
`.claude/skills/harness/templates/{BRIEF.md,README.md,harness.json,team-config.yaml}`, and
`.harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml` — all the main session's
concurrent work (templates/**, commands/**, references/github-mirror.md) plus plan.yaml, none of
which I touched or reverted.

## Disposition

The six-file correction is complete and independently verified. The literal `verify:` command's
current failure is caused solely by the concurrently-edited `templates/README.md`, not by this
task's files. Re-running the identical verify command once that file's anchoring is finished
will go green without any further change here.
