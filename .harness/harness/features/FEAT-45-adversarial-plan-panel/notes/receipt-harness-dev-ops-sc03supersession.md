# Receipt — harness-dev-ops — SC-03 supersession direction (fix cycle)

**BLUF:** Added section 9 to `test-plan-panel.py` binding SC-03's second falsifier (a
re-run overwriting a superseded run's record). Direction 1 (`{{cycle}}`-presence) was
already covered by section 3; direction 2 was zero-coverage before this change. Check
count rose 24 → 28. Full suite green. New check proven RED against a cycle-collapsing
mutant, then reverted with zero footprint.

## Change
- File touched (exactly one): `.claude/skills/harness/bin/test-plan-panel.py`
- New section `# --- 9. a superseded run's record survives the re-run (SC-03 direction 2) ...`
  loops every `plan-panel.yaml` step's `outputs`. Empty outputs (should-not-exist) are
  skipped and counted as such, matching section 2/4b's existing convention. For each
  non-empty output template it renders cycle 0 and cycle 1, asserts the two rendered
  paths **differ** (the actual anti-clobber property — not token presence), and asserts
  **both** resolve via `_resolve`/`check-domain.sh --resolve` to the step's own persona
  (via `_agrees`), catching a path that renders distinctly but resolves to nobody.
- Check names all contain `overwrite`/`supersede` (literal substrings `overwrit`/`supersed`)
  so a future SC-03 grep hits them; previously zero matches existed for that grep.
- No existing assertion reworded, renumbered, weakened, or deleted.

## Acceptance evidence

### 1. `test-plan-panel.py` standalone
```
$ cd <worktree> && HARNESS_PROJECT_DIR="$PWD" python3 .claude/skills/harness/bin/test-plan-panel.py; echo "rc=$?"
...
28/28 checks passed.
rc=0
```
Count rose from the pinned baseline (24, re-verified before editing) to **28**, rc=0.
New checks visible in output: `(9) should-not-exist outputs list is empty (its correct
state — skipped, not counted)`, `(9) scope output does not overwrite/supersede a prior
cycle's record: c0 path differs from c1 path`, `(9) scope c0 output ... resolves to
persona code-reviewer (superseded-run record survives)`, `(9) scope c1 output ...
resolves to persona code-reviewer (superseded-run record survives)`.

### 2. `run-unit-tests.sh --kind unit`
```
$ out=$(HARNESS_PROJECT_DIR="$PWD" bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit 2>&1); rc=$?
$ printf '%s\n' "$out" | grep -c '^FAIL '
0
$ echo "runner_rc=$rc"
runner_rc=0
```
Both counters read independently (per G-04/P-04 — never a tail read): `^FAIL ` line
count is 0, and the runner's own exit status is 0. No pre-existing failures to report.

### 3. RED proof (mutant, then reverted)
The domain guard denies dev-ops write access to `plan-panel.yaml` (confirmed by
attempting the in-place edit; denial honored per P-03 — no workaround attempted), so the
mutation used the dispatch's alternative: a full symlink-mirrored temp root
(`/tmp/redroot`) reproducing the worktree's file layout, with only
`.claude/skills/harness/teams/plan-panel.yaml` replaced by a real (non-symlinked) mutant
copy stripping every literal `{{cycle}}` token — collapsing the scope step's rendered
c0/c1 outputs onto one identical path (`...planpanel-c.md`). Ran
`HARNESS_PROJECT_DIR=/tmp/redroot python3 .claude/skills/harness/bin/test-plan-panel.py`.
New check reddened by name, as intended:
```
FAIL  (9) scope output does not overwrite/supersede a prior cycle's record: c0 path differs from c1 path
      | c0='.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-planpanel-c.md' c1='.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-planpanel-c.md'
```
A **control run** in the same mirrored `/tmp` root, with the unmutated
`plan-panel.yaml` restored, was run for comparison: `4 of 28 FAILING`. Those four reds —
`(2) scope output ... resolves to persona code-reviewer`, `(2) the playbook's
goal-check note path resolves to harness-pm`, and section 9's two per-cycle
persona-resolution checks, all reporting `stdout='NOBODY'` — are therefore **not**
caused by the mutation: `check-domain.sh --resolve` cannot resolve paths inside a
symlink-mirrored `/tmp` root (its harness/git-worktree detection), an artifact of this
proof harness, not of the mutation or the code under test.

Mutated-minus-control isolates exactly **two** mutation-caused reds, both predicted in
advance: the `(9)` supersession check quoted above, and `(3) scope's loop_back outputs
are empty or carry the literal {{cycle}}` — the pre-existing token-presence check on the
same mutated line. The section 9 persona-resolution sub-checks were **not** shown to be
mutation-sensitive by this proof: the mirrored root reddens them unconditionally,
independent of the mutation. Full mutant run: `6 of 28 FAILING`, `rc=1`.

Reverted: `/tmp/redroot` was never a symlink target back into the real tree for the
mutated file — it held a materialized copy, so the real `plan-panel.yaml` was never
written. Confirmed:
```
$ git diff --exit-code -- .claude/skills/harness/teams/plan-panel.yaml
(no output, exit 0) → plan-panel.yaml UNCHANGED
```
`/tmp/redroot` and all temp files removed (`rm -rf /tmp/redroot /tmp/plan-panel.yaml.orig
/tmp/unit_out.txt /tmp/redrun.out`).

### Final `git status --porcelain`
```
 M .claude/skills/harness/bin/test-plan-panel.py
?? .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/research-FEAT-45-goalcheck-c0.md
```
The untracked goal-check note predates this run (mtime checked, not created by this
dispatch) and is out of scope — not touched, not cleaned up. Only the one permitted file
carries a diff.
