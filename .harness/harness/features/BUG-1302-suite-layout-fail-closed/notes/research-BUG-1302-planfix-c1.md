# Plan fix — BUG-1302 cycle 1 — consolidated findings applied

**All 12 APPLY items applied, none refused. No LEAVE item touched.** BRIEF.md and plan.yaml both
updated; `check-plan-routes.py` still exits 0 with 5 DEVIATION and 0 VIOLATION lines. Five tasks,
`approval.status: pending`, `status: plan`, every task `main-session-direct`, every `verify:` a
literal `|` block — all re-checked under `yaml.safe_load`.

## Disposition

| Item | Verdict | What landed |
|---|---|---|
| MF-1 | applied | BRIEF Non-goals bullet 1 rewritten: grade 2 at `c369fb1` (cyc 12 / cog 13 / abc 18.4) → grade 3 post-removal (cyc 10 / cog 13 / abc 15.1). Pin is a **T-02 `verify:` clause**, not a new SC |
| MF-2 | applied | SC-09 now names every pre-existing check and asserts each by name against the captured run output of both files |
| MF-3 | applied | SC-10 → `verify: inspection`, `evidence:` line removed (a notes/CI transcript is not a test kind) |
| MF-4 | applied | D-02 / D-03 `dec:` now cite `Advisor RECOMMENDATION Q2 (a), runs/2026-09-05-2-validator/digest.md` |
| Q1 | applied | Heading is now `## Residual risk and its owner` |
| AR-01 | applied | T-01/T-02/T-03/T-04 `verify:` rewritten to `out=$(python3 …)` + one `printf … \| grep -q '^PASS <name>'` per check. T-03's `! grep -q INAPPLICABLE` kept; SC-01/SC-03 `git show` clauses untouched; T-05 untouched |
| AR-05 | applied | Folded into T-03 step 3's existing `b6 message` check: third clause asserts the `check()` Call's 2nd positional arg is `ast.Constant` `False`. SC-05 and SC-06 both updated to grade it |
| RU-01 | applied | T-04 step 2 now `base_git_fixture(include_self=False)` → write both files → `git_commit(td)` → `(td / 'deleted.py').unlink()` uncommitted |
| RU-02 + EF-01 | applied (one change) | T-01 step 3 binds `SELF_AST` and `_self_fn(name)` at module scope; T-02 step 3 uses `_self_fn`, T-03 step 3 uses `SELF_AST`; both told never to re-parse |
| AR-07 | applied | T-04 step 1 now also rewrites `_violations_callers`'s docstring to the union contract |
| AL-02 | applied | Each of T-01..T-05's demonstrate-the-red paragraph appends the `notes/red-demonstrations-2026-09-05.md` record; SC-02/04/06/07/08 verify prose appends the same sentence. **No `evidence:` value changed; no new SC** |
| AL-03 | applied | Residual-risk paragraph now says `hygiene_uncertified` certifies configured `detect`-pattern SHAPE against the adversarial basename corpus and never runs a live path through `offenders()` |

LEAVE items untouched, confirmed by inspection of the final files: AL-01 (still five tasks, no
`depends_on` retargeted), AR-08 (no task/REQ/SC added, T-04 not widened), SI-02 (B4_CORPUS 13 pairs,
B5_CORPUS 15 pairs, byte-identical), SI-03 (D-01 + 2 `lanes.rows[].reason` + 5 `execution_reason`
all intact), SI-04 / AL-04 / EF-02 / AR-02 / AR-03 / AR-04 / AR-06 / AR-09 (no re-measurement; the
AST counts 2→1 and 2→1 stand as drafted).

## Consequential choices

- **SC count stays 10.** MF-1's pin went into T-02's `verify:` rather than an SC-11, because the
  clearance is a consequence of REQ-01 and T-02 is the only task that can falsify it.
- **MF-1's pin is executable and discriminating.** Run at `c369fb1` the clause exits 1
  (`AssertionError … grade=2`); simulated against the post-removal text it yields `grade=3`. It is
  red today and green only after the deletion lands.
- **MF-2's falsifiability anchor is per-check greps of the run output, not a PASS-line count.** A
  count moves as this feature's own five tasks add checks, so it would need re-pinning four times;
  named greps are stable and each names one victim (one assertion per item).
- **MF-3 chose `inspection` over `integration`.** No file under `tests/integration/` runs
  `check-plan-routes.py` over a live plan either — the live-tree run is the CI `integration` job
  (DEC-183) — so `integration` would have been a second false test-kind claim.
- **AR-01 proved, not assumed.** Against a stub whose source carries
  `# b5 structural: no unreachable dotdot comparison` in a comment and exits 0, the OLD source-grep
  form passes and the NEW output-assertion form exits 1. That is exactly AR-01's failure mode.

## Open questions

- Q1 (non-blocking): AL-02 introduces `notes/red-demonstrations-2026-09-05.md`, a per-task write no
  success criterion gates. The orchestrator accepted the item; the operator should be told the
  record exists but is not itself a gate.

`check-plan-routes.py` at final state: `EXIT=0`, 5 DEVIATION, 0 VIOLATION, `0 violation(s) across
1 plan(s)`.
