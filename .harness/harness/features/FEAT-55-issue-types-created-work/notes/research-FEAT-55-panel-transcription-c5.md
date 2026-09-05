# FEAT-55 — cycle-5 panel transcription into plan.yaml

**BLUF.** `plan.yaml`'s `panel:` block now records the cycle-5 adversarial panel: `cycle: 5`,
`last_run: 2026-09-05-02-validator`, `severity_max: med`, `must_fix: []`, three `reader:`-keyed
readers all `ran`, and **exactly nine findings** — four new `low`, one carried `med`, four
`operator_accepted` `low`. Written through `plan-merge.py set-panel` only. Nothing else in the plan
was touched; `approval:` remains `status: pending`, feature `status: plan`, `BRIEF.md` unopened.

## The nine ids, and how each was derived

Every id is the stdout of
`python3 .claude/skills/harness/bin/panel_findings.py id --reader <r> --summary <s>`, invoked from
`/tmp/feat55_build_panel.py` on the exact strings stored in the block. None was typed.

| ref | id | reader | sev | derivation |
|---|---|---|---|---|
| N1 | `PF-f8e806d111d71a0bb6c4298cd47963c9` | scope | low | new; summary from the 2026-09-05-02-validator digest `findings` N1, `why` expanded from `notes/review-harness-code-reviewer-planpanel-c5.md` §C |
| N2 | `PF-bc6cbd0c92ecd36a44eee2da8762f05a` | scope | low | new; digest N2 + §C long-form `why` |
| N3 | `PF-17e86df90d8237d8fdf5eb5cb96a274a` | should-not-exist | low | new; digest N3 + the digest's own §Findings gloss |
| N4 | `PF-bad4d5185e8a8cedba6acd7d5ed1bb79` | should-not-exist | low | new; digest N4 + §Findings gloss |
| C1 | `PF-e74a2da89380cfa94f6b1693191d759d` | should-not-exist (info) + scope (med) | med | **carried**; `reader`/`severity`/`summary` verbatim from the cycle-4 block, so the id reproduces; `why` gained one closing clause recording the cycle-5 re-derivation (the `why` is not in the identity) |
| — | `PF-56a2ce7a053111a3aff62a4b97c5902e` | should-not-exist | low | carried verbatim, `operator_accepted` |
| — | `PF-0c12a033f69bb6bc60b8f96134f94fd0` | should-not-exist | low | carried verbatim, `operator_accepted` |
| — | `PF-e27f1c3018b6b8477547a1b028607f96` | should-not-exist | low | carried verbatim, `operator_accepted` |
| — | `PF-d8a7b516b793e1227b17d61c754240c7` | should-not-exist | low | carried verbatim, `operator_accepted`, `supersedes:` preserved |

**All five carried ids reproduced** from their stored `reader` + `summary` — verified by recomputing
each with the same CLI and comparing to the cycle-4 value: `True` for all five. No string was
adjusted to make an id come out; the check ran the other way round.

`fix_order` carries the four NEW ids only, in the validator lead's own ranking `N4, N3, N1, N2` —
not their listing order. `fix_order_reason` records that all four are `low`, that nothing gates,
that the five carried entries are operator matters and not a fix queue, and that the panel returned
`must_fix: []`.

## The six discharged ids

Dropped from `findings:` and recorded once in `discharged_at_cycle_5:`, each with the content string
the panel read out of `plan.yaml` to call it HOLDING (from the digest `roll_call`): the three-route
backfill-only refusal case (`PF-1f968f2c…`), the D-14 overclaim sweep (`PF-e02dcbdf…`), T-06's gated
integration test (`PF-45294813…`), T-10 §6's single SKIP wording (`PF-62b2b8ae…`), and the coupled
pin split — scope half `PF-383a1a92…` (row narrowed to 394 chars, `internal_id_args` unpinned) and
durability half `PF-9a71cb9a…` (guard moved into the standing
`tests/unit/test-issue-types-pin.py`). Five operator rulings, six ids. Each of the six now occurs
exactly once in the whole file, inside `discharged_at_cycle_5:`.

## The sequencing note

`sequencing_note:` records the panel's 5(d) answer as its finding of record: **no plan gate and no
task verify between T-01 and T-12 invokes the standing unit suite**, but the guarantee is not
plan-encoded — `tests/unit/test-issue-types-pin.py` is deliberately red until T-11/T-12 land,
`run-unit-tests.sh` globs `tests/unit/test-*.py`, `gates.qa_gate` is blocking, and T-12 is
`main-session-direct` with no ordering rule relative to the qa segment; a premature qa run fails the
only blocking gate with a `loop_back` no squad may own under DEC-174. Deliberately **not** expressed
as a task, decision or `depends_on`: build-phase segment ordering is the orchestrator's
execution-time authority, and the orchestrator carries the constraint in its handoff.

## Verification

- `plan-merge.py set-panel` → `PANEL cycle 5 … APPLIED`; the verb refuses unless the block reloads
  identical to the value supplied, so the stored block is byte-faithful to what was staged.
- Reload: 9 findings, 3 readers all `ran`, `must_fix: []`, `status: plan`,
  `approval: {status: pending}`, 12 tasks and 20 decisions unchanged in count.
- `check-state.sh` (the worktree's own copy, so its root resolves to this checkout) reports **no
  INV-32 line for FEAT-55 at all**. That is expected and not evidence by itself: INV-32 skips any
  plan whose approval is not `approved` (`check-state.sh:424-427`). So the INV-32 predicates were
  applied directly to the stored block (`/tmp/feat55_inv32_probe.py`): **BAD none, WARN none**, with
  a positive control proving the predicates discriminate — a `step:`-keyed `readers` block produces
  **3 BADs**, the exact failure this feature hit once before.

## Could not transcribe faithfully — nothing

Every finding, severity, disposition and reader string is the panel's own. The only text that is not
a straight copy is C1's one added `why` clause (permitted: the cycle-5 panel extended it, digest ref
C1) and the expanded `why` text for N1–N4, which is the readers' own long-form reasoning lifted from
their note rather than new argument. No severity was reassigned; no finding was reworded to read
better.

## Open

- Digest Q1 (the 5(d) ordering) is unresolved by design and belongs to the orchestrator, not to the
  plan. Digest Q2 and Q3 are harness defects (validator exit path; run-digest guard blocking an
  in-place digest rewrite) — they travel in the orchestrator's DIGEST, not in `panel:`.
