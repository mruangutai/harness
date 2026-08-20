# FEAT-28 plan fix cycle 2 — what I found and what I changed

**BLUF.** All four fixes are landed in `plan.yaml`, but **most of them were landed by a
concurrent writer, not by me.** `plan.yaml` and `BRIEF.md` were both rewritten under my feet
during this run (plan.yaml mtime 06:52 then 06:54; BRIEF.md 06:54) while my own first read
showed the pre-fix text. Two agents were editing the same two files. That is the finding that
matters most — a lost-update window on the only artifacts this role writes.

I did not clobber the other version of `plan.yaml`: every write to it was guarded by an mtime
equality assert, and the two files stood unchanged at my write times when I re-checked afterwards.
`BRIEF.md` is weaker — I read and wrote it in one process with **no** mtime guard, so its
lost-update window is small (surgical replaces on text read milliseconds earlier) but unproven.
I verified the other version against the four defects, found it correct on all four, and added
only the two gaps it left.

## The four fixes — state at the end of this run

- **Fix 1 (resolver rule).** Landed, plan.yaml item 3 `phantom_citations(text)`.
  Before: collect `case_[0-9][0-9a-z_]*`, truncate to leading `case_NN`, look for `"def " + base`.
  After: no truncation — id `X` resolves only if some `test-*.py` carries a definition site whose
  name **is** `X` or **begins with** `X + "_"`, and a definition site is a `def` name **or** a
  `check("` label. Both outcomes are stated in the task text.
- **Fix 1b (composition).** Decided **sibling function**, not an item of `ci_wiring_violations`.
  Stated reason in the task text: `case_26a` asserts `ci_wiring_violations(real doc) == []`, and
  `tests.yml:44` still cites the phantom at T-01 time, so folding the scan in would redden T-01 on
  a file T-01 is forbidden to touch. `phantom_citations` also needs raw text, which `safe_load`
  discards. T-02 adds `case_26o_real_workflow_text_has_zero_phantom_citations` — the task that
  makes it true owns the assertion. DAG unchanged.
- **Fix 1c (coverage).** Enumeration run by me at this tree, complete, not a sample:
  `.github/workflows/tests.yml` cites exactly two ids — `case_25b9` (line 44) and `case_19a3b`
  (line 177). Under the new rule, over a name set of 66 definition sites built from all
  `.claude/skills/harness/bin/test-*.py`: `case_25b9` → **False** (violation, correct);
  `case_19a3b` → **True** (clean). `case_19a3b` resolves **only** through its `check("` label at
  `test-check-plan-routes.py:366` — it has no `def`. A `def`-only rule would have reddened
  `case_26a` for the second, unpredicted reason the dispatch warned about, and would also have
  rejected every full label T-02 writes, since those are `check()` literals.
- **Fix 2 (mutation proof).** Landed, and the injected id is `case_25zz9`, not `case_25b9`. This
  departs from the dispatch's literal instruction and I judged it **stronger**: `case_25zz9` has
  base `case_25` (real `def case_25()` at `test-check-plan-routes.py:1030`), so it is reported
  ONLY under the fixed rule — the discriminating property Fix 2 demanded — while being absent from
  the real text, so the case's third assertion ("not reported on the unmutated text") holds both
  before and after T-02. Injecting `case_25b9` itself would make that third assertion false at
  T-01, when the real text still carries it.
- **Fix 3 (`git diff --stat`).** Landed. T-03's verify is now
  `cp` the committed index aside → run `gen-decisions-index.py` → `diff -q`. The task text states
  the direction: exit 0 is the pass, meaning the committed index is byte-identical to what the
  generator produces. It deliberately does not copy T-01's `git diff --exit-code`, because T-03
  MUST change the index, so an empty diff against HEAD would be the failure there.
- **Fix 4 (three restored assertions).** Landed as `case_26l` (Unit suite step deleted),
  `case_26m` (`continue-on-error` on a guarded step), `case_26n` (step-level `if:`). Measured here:
  the `integration` job has seven steps, none carries `if:` or `continue-on-error:`, and the job
  mapping has only `runs-on` and `steps` — so the new checks report nothing on the real workflow.

## Counts — all three enumeration sites moved together

Fourteen cases at T-01; fifteen after T-02 adds `case_26o`. T-01's list (14), T-02 RULE B's list
(15), T-03's amendment list (15, and the word "eleven" is gone). SITE 1 grew from six labels to
eight — `case_26m` and `case_26n` were added because the site's own sentence claims the step is
"unneutered", which is exactly what those two assert.

## What I changed myself

1. **T-02 `change_type: docs` → `logic`.** T-02 now edits
   `.claude/skills/harness/bin/test-check-plan-routes.py` (Part 2 adds `case_26o`). `docs` carries
   no required test kind in `harness.json` `test_matrix`, so the old value would have exempted the
   one assertion that runs against the real workflow from the qa gate meant to demand it. Title
   updated to match the two surfaces; the reason is written into the intent so the doer sees it.
2. **BRIEF SC-10 added.** `case_26l`, `case_26m` and `case_26n` had no success criterion — SC-04
   covers only the Layout gate and the container ban. Without SC-10 the goal-check has nothing to
   grade Fix 4's restored assertions by. Also enumerated the automated-SC list in `## Constraints`
   individually instead of the range `SC-01..SC-05`, which had silently excluded SC-10.

## Open

- The concurrent-writer window. Nothing in the harness detected it; I found it only because a
  string replacement asserted uniqueness and failed.
- The BRIEF gaps bullet 3 rewrite is present and does state the reconciliation (union name set,
  complete two-id enumeration, and the two residues: prefix matching still lets a bare `case_25`
  resolve, and the scan reads `tests.yml` only). Bullet 2 left untouched, as instructed.

## Gate

`python3 .claude/skills/harness/bin/check-plan-routes.py` → exit 0, 0 violations across 4 plans.
It covers routing only — it says nothing about Fix 1, 1b, 1c or 2.
