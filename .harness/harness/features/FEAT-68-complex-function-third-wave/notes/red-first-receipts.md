# FEAT-68 — red-first receipts

Written after the implementation pin `9ab1813e` (`9ab1813e86067ca4a21a84f49364cf4f453055b4`; this file is not inside it; `0c15bad6` was a
superseded candidate — its first full unit run failed the bar-4 lock, ledger D-13). Base
`e655f14a56a14bf1777cae55a19195c9af10505d` = origin/main at the signed plan.

## Baseline suite receipts (before any production edit)

Captured in the clean detached baseline checkout
`.claude/worktrees/harness/feat68-base-e655f14a` (`git status --porcelain` empty) by
`/tmp/feat68-baseline.py` → `/tmp/feat68-baseline.json` (raw stdout/stderr retained; sha1 per
stream). An earlier capture in the feature worktree at the same SHA was superseded by this one
(validate c0 VF-01). The 57 owning
suites are every `tests/**/test-*.py` whose source, or whose `*_support.py` helper, names one
of the five changed modules (harness_boundary alone is imported by half the tree). All 57 exit
0 at the base; per-suite exit and byte sizes are in the json and repeated in
`notes/clean-pin-byte-receipts.md` beside the pin's.

## SC-01 red: the plan's inline grade assertion at the base

Run at `e655f14a` before any production edit (the verify block's first `python3 -c`
extracted verbatim to `/tmp/feat68-grade-assert.py`); the same run in the clean detached
baseline checkout is in `notes/clean-pin-byte-receipts.md`:

```
AssertionError: [('.claude/skills/harness/bin/check-plan-routes.py', 'process_plan_yaml', 1), ('.claude/skills/harness/bin/harness_boundary.py', 'classify', 1), ('.claude/skills/harness/bin/board_lifecycle.py', '_audit_findings', 1), ('.claude/skills/harness/bin/layout_migration.py', 'scan', 1), ('.claude/skills/harness/bin/check-domain.py', 'domain_check', 1)]
exit=1
```

Exactly the five targets, all grade 1. Re-run in a clean detached checkout of the base is
reproduced in `notes/clean-pin-byte-receipts.md` beside the green run at the pin.

## SC-05 red: the renderer's presence at the base

At `e655f14a`, `git grep -n -E "render-brief|md_to_html"` outside notes/logs/decisions/
feature-history matches `bin/render-brief.py`, `tests/unit/test-render-brief.py`,
`references/briefing.md:42`, `.omp/commands/harness.md:132`, `test-gen-decisions-index.py:44`
and `canonical-reader-classification.json:2218`; 102 tracked `notes/*.html` files exist. At the
pin the same grep matches nothing and no `.html` remains (the verify block's second and third
`python3 -c` lines).

## SC-02 fail-first

Byte identity has no pre-fix red form; the baseline-versus-pin comparison is this criterion's
fail-first equivalent (operator ruling 2026-09-26; BRIEF SC-02).
