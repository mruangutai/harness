# T-07 re-laned to main-session-direct — done, verified at disk

**Conclusion.** T-07 now reads `execution_mode: main-session-direct` with an `execution_reason` that
names the real cause (no agent domain grants the mutant target), and its `intent` now forecloses the
`is_excluded_from_scan` trap. Nothing else in the plan moved. `approval:` is still `pending`.

## Edit 1 — the lane (T-07's execution block)

- `execution_mode: team` becomes `main-session-direct`
- `execution_agent: harness-backend-dev` — DELETED
- `execution_reason:` — ADDED, one line, in T-10/T-11's position:

  `the mutation proof writes docs/invalid-states-audit.html; check-domain.sh --resolve returns NOBODY
  for that path at sha 3952814, so no agent domain grants the mutant target`

Shape matches T-10 and T-11 field-for-field: mode, reason, no `execution_agent`. Wording follows
T-19 / T-20, not DEC-174 am.4 — `test-no-distribution.py` is not in the am.4 enumeration, so an
am.4 citation here would be a false entry in the record.

**Verdict verified before the sha was written.** At HEAD `3952814` in this worktree,
`check-domain.sh --resolve docs/invalid-states-audit.html` returned `NOBODY` (rc 0). For contrast,
`--resolve .claude/skills/harness/bin/test-no-distribution.py` returned `harness-backend-dev` and
`harness-dev-ops` — which is why `check-plan-routes.py` now reports T-07 as a DEVIATION, exactly as
it does for T-03 and T-08 through T-18. That checker exits 0: 0 violations across the plan.

## Edit 2 — the `is_excluded_from_scan` caveat

Added to `intent:` immediately after "Follow all three.", where the "existing idiom" instruction sets
the trap:

> Do NOT reuse that file's is_excluded_from_scan helper: the EXCLUDED_EXACT and EXCLUDED_PREFIXES
> sets it reads at :92-93 are case2's, not this case's - they exclude only DECISIONS.md among
> markdown, so every other tracked *.md inflates the count past the 21 baseline, and they drop
> .harness/notes/ and the .harness/harness/features/ tree, which this case's repo-wide scan root
> must keep. Write this case's own three-exclusion filter.

Re-derived at disk before writing it: `test-no-distribution.py:91` is
`EXCLUDED_EXACT = {".harness/harness/docs/DECISIONS.md"}`, `:92` is
`EXCLUDED_PREFIXES = (".harness/logs/", ".harness/notes/", ".harness/harness/features/")`, and
`is_excluded_from_scan` (:107-110) is exact-or-prefix over those two. Neither set carries SC-01's
three (`test-*` basenames, `harness_boundary.py`, all `*.md`), so reuse is wrong in both directions
at once.

## Frozen and confirmed unchanged

`depends_on` (T-20 present), `verify` (byte-identical, re-read after the edit), `files`, `traces`,
`title`, `status`, and `approval: {status: pending}`. Task count 20; lane split 15
main-session-direct / 5 team — matches the expected split. The file `safe_load`s.

## Open questions

None.
