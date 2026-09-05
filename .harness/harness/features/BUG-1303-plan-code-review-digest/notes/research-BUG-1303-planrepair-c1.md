# Plan repair c1 — BUG-1303 — the four goal-check rulings applied

**All four cycle-0 findings are closed in `BRIEF.md` and `plan.yaml`. Both acceptance commands are
green, `approval.status` is still `pending`, and no REQ/SC/T/D id moved.** One new decision, `D-06`.
Two artifacts touched, plus this note and my observations log.

## Disposition, per finding

- **G-1 (high) — widened T-02, not split.** T-02's `intent:` now enumerates FOUR edits to both persona
  copies: `code_grade`, the `reviewed: plan:` form, the `artifact:` line rewritten to
  `<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/review-harness-code-reviewer-<runid>.md`,
  and the stale `Write`-grant sentence in the same file rewritten to that same path — with the reason
  it is in scope stated inline so a later reviewer does not read it as creep. The closing sentence no
  longer says "no other field"; it now forbids everything *except* those four. `files:` unchanged
  (the two persona copies); no lane row touched. `BRIEF.md` REQ-01/REQ-02 widened so the documented
  block explicitly spans the DIGEST fields, the `artifact:` path and the stated write grant.
- **G-2 (med) — every automated SC now has a producing task.** SC-08 → new T-01 case (6), a named
  `[reviewer persona copies]` ok line; it stays `automated/integration`. SC-04 and SC-06 → re-declared
  `verify: inspection`, each naming in its own text the command output it is graded from (SC-04: the
  reviewer's own `git diff --name-only <base>..<review_sha>` plus T-03's full-suite verify; SC-06:
  T-04's verify — the `documented output block` grep and the `gen-decisions-index.py --stdout | diff`
  idempotence check — plus a `file:line` citation at the pin). Reason: SC-08 is a two-file byte
  comparison a test can make; SC-04 and SC-06 are claims *about the change set and the pinned tree*
  that the change set's own tests cannot make without hard-coding a `review_sha`.
- **G-3 (med) — the floor is gone, not relocated.** T-01 step (2) is now a path map only, explicitly
  forbidden from doubling as the roster; step (3) derives the roster from `sorted(validator.ALIAS)`
  (16 keys at `c369fb1f`, verified by loading the module) and emits a named FAIL for any registry
  persona `CONTRACT_SOURCES` does not map. Every "explicit expected floor" phrase is removed
  (`'explicit expected floor' in intent` → `False`). `BRIEF.md` SC-05 rewritten to require the
  registry derivation and the per-persona named failure instead of a count against a floor.
- **G-4 (low) — recorded, not re-run.** The measured baseline (exit 0, zero `^FAIL `, `ALL PASSED.`,
  18.9s, sha `c369fb1f`, worktree `BUG-1303-plan-code-review-digest`, before any task landed) is now
  on `BRIEF.md` SC-01 and at the end of T-03's `intent:`, with the instruction not to re-run it and to
  escalate rather than absorb a red in a section none of T-01..T-03 touches.

## Acceptance evidence

```
$ python3 -c "import yaml,sys;..." plan.yaml
YAML OK
approval: {'status': 'pending'}
tasks: ['T-01', 'T-02', 'T-03', 'T-04']
decisions: ['D-01', 'D-02', 'D-03', 'D-04', 'D-05', 'D-06']

$ python3 .claude/skills/harness/bin/check-plan-routes.py <FEATDIR>/plan.yaml
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
DEVIATION T-01 tests/integration/test-validate-digest.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-02: declared main-session-direct (.claude/agents/harness-code-reviewer.md, .omp/agents/harness-code-reviewer.md ungranted)
OK T-03: declared main-session-direct (.claude/skills/harness-code-review/SKILL.md ungranted)
OK T-04 granted to harness-documentor
0 violation(s) across 1 plan(s)     rc=0
```

The single `DEVIATION` is the expected DEC-174 carve-out output, unchanged from cycle 0.

## Verify-string proofs (acceptance 4 and 5)

- **Fragment identity, character by character.** T-02's intent instructs the literal line
  `artifact: <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/review-harness-code-reviewer-<runid>.md`;
  T-02's verify greps `-qF "features/<FEAT>/notes/review-harness-code-reviewer-"`, twice (one per
  copy). Checked mechanically: the fragment is in T-02's `intent:` and appears twice in its `verify:`;
  a positive control `grep -qF <fragment>` against that exact artifact line returns rc 0. The whole
  T-02 verify returns rc 1 on the pre-fix tree, so it discriminates.
- **T-01's verify runs the suite ONCE** and pipes it into a python filter requiring both ok lines —
  two piped `grep` runs would have cost ~38s of the 60s budget. Proved offline: both lines present →
  rc 0; only the first line → rc 1. `bash -n` is clean on all four tasks' verify strings.

## Open items for the panel

- T-01 remains deliberately RED at task end (code_grade in both trees + the three plan-mode
  assertions); its verify checks only the two ever-green ok lines. Unchanged from cycle 0, restated
  in step (7) of the new intent.
- SC-04 and SC-06 now depend on a reviewer actually running the two commands their text names. That
  is an inspection SC by construction; if the panel wants them mechanical, they need a task that
  knows `review_sha`, which does not exist before the pin.
