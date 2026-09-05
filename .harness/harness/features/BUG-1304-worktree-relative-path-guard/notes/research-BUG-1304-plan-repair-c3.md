# Plan repair after panel cycle 2 — BUG-1304 — pm

## BLUF

Panel cycle 2 is recorded in `plan.yaml`'s `panel` (cycle 2, ten findings, cycle 1 carried in
`history` plus per-finding `verified_closed_at_cycle: 2`). The three determinate defects (F3, F4,
F5) are repaired in the tasks that own them. The two that are not pm's to close (F1 high, F2 med)
are recorded only, in D-10's `because`. **I selected NEITHER F1 remedy.** The plan is ready to go up
for signature with `approval.status: pending`, unchanged and untouched.

## Repaired

- **F3 — `T-02.intent`.** The `live_claims` paragraph opened with "return [] when the file is absent
  or unparseable", contradicting the same task's `UnreadableRegistry` paragraph, SC-10 and D-10. The
  paragraph is now written once, coherently: absent → `[]` (legitimately empty), exists-but-unreadable
  → RAISE. The old phrasing is gone from the file.
- **F4 — `T-01.intent`.** New **case 8**: an OMP claim with a PROVEN supervisor identity (built as
  case 5 builds it — the test process's own pid plus `inflight_registry._process_start_time`),
  back-dated past `OMP_UNVERIFIED_TTL_SECONDS`, IS still returned. It is the case that reddens a
  backstop-only enumerator, which passes cases 1–7. Cases 1–7 are unrenumbered (case 2 cites case 5).
  The same file's two trailing unreadable-registry cases moved 8→9 and 9→10 so one file's
  enumeration stays unique — no other artifact cites them. `T-01.verify` unchanged.
- **F5 — `T-03.verify`, `T-05.verify`.** The call-site count now pipes through
  `grep -vc '^ *def bug1304_assert_pre_change_allows'`, so the helper's own `def` line is excluded.
  Floors stay `-ge 9` / `-ge 11`. Proved on a fixture with one `def` + nine call sites: tightened
  count 9 where the old `grep -c` gave 10; at eight call sites the floor fails. Both remain literal
  `|` blocks, runnable from the repo root.

## Recorded only — not repaired, not decided

- **F1 (HIGH) — D-10's blast radius.** D-10's cost paragraph is **corrected to the truth**: the
  refusal is not scoped to the write's own destination or registry — `claim_worktrees` scans the
  owner-root registry plus every linked worktree's registry while it BUILDS S, and the destination
  is not an argument to it — so while ANY scanned registry is unreadable, EVERY governed write by
  EVERY governed persona on EVERY feature is refused, including writes inside the writer's own
  healthy assigned worktree. The `bash-write-guard.sh:684-694` comparison is kept **only for the
  direction** of the trade and explicitly disclaimed as a precedent for its scope. Both remedies are
  recorded with neither selected: **(a)** allow a destination inside a member of the PARTIAL S
  (panel's assessment carried: sound under any superset of S) → reorders T-02's predicate, needs a
  NEW criterion for the allow half; **(b)** keep the global rule and carve the exception into REQ-03
  → proposed carve-out text recorded **in D-10 as proposed only**, needs one added inspection
  criterion on the refusal message's repair instruction. Q1
  (`research-BUG-1304-plan-repair-panelc1.md:85-86`) is marked superseded by that paragraph.
  `T-02.intent` states the ordering as an unresolved operator choice and forbids a doer deciding it.
  **BRIEF.md untouched** — writing the carve-out into REQ-03 would presume remedy (b).
- **F2 (med) — the fail-open/fail-closed asymmetry.** Stated in **D-10's `because`**, not D-09,
  because D-10 is the entry that makes the registry input fail-closed, and the asymmetry only exists
  as a property of that rule; D-09 is about liveness horizons. Anchors re-verified myself in the
  worktree: `harness_boundary.py:170-173` (`OSError` → `[]`) and `:177-183` (unreadable pointer
  skipped). No task added, no scope widened.

## Integrity

`approval.status pending`, `panel.cycle 2`, 10 findings, 10 tasks, 10 decisions; `status: plan`;
no id renumbered; every task keeps literal `files:`, a literal-`|` `verify:`, `execution_mode`,
`change_type`, `traces:`; no placeholders; `check-plan-routes.py` → 0 violations (10 expected
DEC-174 DEVIATION lines).

## Open for the operator

- **Q1 (superseded, blocking at signature):** pick F1 remedy (a) or (b), or strike D-10. Read D-10's
  `because`, not Q1's cycle-1 wording.
- **Q2 (non-blocking):** F2 is a live fail-open one layer above this feature; it needs its own issue.
