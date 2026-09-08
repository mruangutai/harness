# Goal-check — BUG-1480 — cycle 0 — review_sha 4de92e75

**ALL SEVEN CRITERIA MET (7 met / 0 unmet / 0 unverifiable). REQ-01..REQ-06 all covered; REQ-06 is
covered by mechanism inspection only, with no executable row.** No criterion's behaviour is wrong.
Two proof-thinness notes and one BRIEF prose inaccuracy are recorded as recommendations, none gating.

## Measurement substitution — stated explicitly

The BRIEF's `command:` for SC-01/02/03 literally reads `cd /Users/molchairuangutai/GitHub/harness`,
which is where the code lands **after merge**. Pre-merge the main checkout still holds the PRE-FIX
`check-domain.sh`, so measuring there would grade the wrong tree. **I ran the identical command
inside the worktree** `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1480-handoff-note-checkout-root`,
once: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` → exit 0, 38.3s,
zero `FAIL ` lines. `git diff 4de92e75 -- .claude/skills/harness/bin/check-domain.sh
tests/integration/test-check-domain.py` is **empty** at worktree HEAD `bff942bf`, so the run
measured `review_sha` content exactly (G-07/G-15 discharged). All inspection evidence was read via
`git show 4de92e75:<path>`, never a plain file read.

## The seven criteria

| id | verify | verdict | evidence I opened |
|---|---|---|---|
| SC-01 | automated (integration) | **met** | run row, quoted: `ok    handoff worktree-only feature dir resolves` |
| SC-02 | automated (integration) | **met** | 42/42 pre-existing rows enumerated from the seven builders, each found `ok` by name (below) |
| SC-03 | automated (integration) | **met** | rows, quoted: `ok    handoff worktree-only unresolvable pointer refused` and `ok    handoff worktree-only brief-sc pointer refused` |
| SC-04 | inspection | **met** | `check-domain.sh:1151-1162` @4de92e75 — `try:` 1155, `except Exception: pass` 1160-1161, `return root` 1162; `grep -cE 'sys\.exit\|raise'` over 1151-1162 = **0** |
| SC-05 | inspection | **met** | `_norm` returns `_ck[1]` (`:1146`) and `rel` (`:1149`), both path strings; `git diff 64fcaa34..4de92e75` has exactly **two hunks** (helper add after `:1149`, one-arg swap at `:1761-1762`), so no `_norm` call site is touched. Four named sites located @4de92e75: `_resolved_rel` `:1866`, `_plan_route` `:1924` (`_norm(path)` `:1926`), `__main__` target assembly `:2058,2087,2091`, sweep `targets.append` `:2232` |
| SC-06 | inspection | **met** | `git merge-base --is-ancestor 6b5ae254 d8a99991` → 0 (test **is an ancestor** of fix, not merely earlier); red-then-green measured in `notes/qa-BUG-1480-c0-sc06.md:32-59` (2 FAIL rows at the test commit, 0 after) |
| SC-07 | inspection — **mechanism-only** | **met (mechanism-only)** | `handoff_done_when.py:78-87` @4de92e75 — `root = Path(root).resolve()` then `resolved.relative_to(root)` raising `target escapes the project root`; paired with `check-domain.sh:1162` `return root`. **No executable row exercises a cross-checkout `finding:`/`approval:` refusal**, so this grade rests on reading the mechanism, not on an observed refusal — strictly lower confidence than SC-01/02/03 |

### SC-02, per row — 42 rows checked individually, not by a FAIL count

Row names enumerated by reading the builders in `tests/integration/test-check-domain.py:4171-4399`,
then each name matched against the run output. `_report_handoff_results` (`:4443-4448`) prints
`ok   `/`FAIL ` per row and counts `fails += not ok`, so per-row reading is sound.

`_handoff_grammar_cases` 11 (e.g. `ok    handoff duplicate heading cannot truncate`) ·
`_handoff_pointer_cases` 12 (e.g. `ok    handoff approval rejects invalid ATX bad-seven.md`) ·
`_handoff_unsafe_cases` 9 (e.g. `ok    handoff approval symlink escape`) ·
`_handoff_pre_edit_cases` 4 (e.g. `ok    handoff pre-Edit unreadable existing file fails closed`) ·
`_handoff_validator_exception_case` 1 (`ok    handoff validator exception fails closed`) ·
`_handoff_existing_edit_cases` 2 (e.g. `ok    handoff edit with Done when`) ·
`_handoff_line_cap_cases` 3 (e.g. `ok    handoff 61-line boundary`).
**Total 42 expected, 42 present, 42 `ok`, 0 absent, 0 not-`ok`.**

## REQ-01..REQ-06 coverage

| req | pinned by | read |
|---|---|---|
| REQ-01 worktree-only feature dir accepted | SC-01, SC-03 (brief-sc row) | covered, behaviourally |
| REQ-02 main-checkout validation unchanged | SC-02 (42 rows) | covered, with a known hole — see R-1 |
| REQ-03 no fail-closed dependency in shape | SC-04 | covered |
| REQ-04 unresolvable pointer still refused, named, both checkouts | SC-02 (`handoff plan/brief/finding/approval unresolved`, needle = the bad pointer) + SC-03 | covered both directions |
| REQ-05 regression test red pre-fix | SC-06 | covered |
| REQ-06 containment bound moves with resolved checkout | SC-07 only | **covered by mechanism inspection only — flagged**, no row observes the intended refusal. `plan.yaml` T-02 `traces:` does now carry REQ-06 (panel finding `PF-880e7f88…` resolved) |

## Recommendations for the operator — not criteria, BRIEF is approval-gated

- **R-1 (med, proof-thin, REQ-02 direction).** No row anywhere combines "a linked worktree exists in
  the tree" with "the note under validation stands in the MAIN checkout". `_checkout_root`'s
  `_hb.real(_ck[0]) != _hb.real(root)` guard and its `return root` fallback are therefore never
  exercised in the one combination REQ-02 actually claims. Independently reached in
  `notes/qa-BUG-1480-c0-sc06.md:98-131`. Behaviour is not wrong; the proof is thin. Under DEC-174
  the fixture lives in `tests/integration/**`, so no squad member can add it — a backlog row for
  the main session, and D-01 keeps it out of this PR.
- **R-2 (low, proof-thin, REQ-06).** SC-07's mechanism-only grade above. Same DEC-174 lane, same
  backlog treatment.
- **R-3 (low, BRIEF prose).** SC-05 and `## Constraints` both name `_resolved_rel` as a `_norm` call
  site. At `4de92e75` `_resolved_rel` (`:1866-1893`) does **not** call `_norm`; the `_norm(cand)`
  call in that neighbourhood is `_hardlink_plan` (`:1920`), which the BRIEF never names. The
  substantive SC-05 claim survives — the two-hunk diff proves no call site changed shape — and the
  code reviewer reached the same reading (`notes/review-harness-code-reviewer-c0.md:94-99`). This is
  a BRIEF text defect, not a code defect; SC-05 stays **met**. Fixing the wording is an amendment
  only the operator can sign, and it is not worth reopening approval for this PR.

## Open questions

- **Q1 (non-blocking).** R-1 and R-2 want one integration fixture each, both under DEC-174's
  `main-session-direct` lane. Backlog rows on `main` after merge, or a follow-up ticket now?
- **Q2 (non-blocking).** R-3's wording fix touches an approved BRIEF. Leave the inaccuracy recorded
  here, or amend and re-sign?
