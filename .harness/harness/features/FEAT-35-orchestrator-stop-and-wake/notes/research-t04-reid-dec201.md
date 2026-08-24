# T-04 re-id: DEC-200 -> DEC-201 — done, two occurrences, nothing else

T-04's decision id in `plan.yaml` now reads DEC-201 in both places it appeared: the `verify:` index
assertion (`grep -q "^- DEC-201 "`) and the first line of `intent:` ("Append one new entry,
DEC-201, ... after DEC-199"). I confirmed the count before editing — `grep -n DEC-200 plan.yaml`
returned exactly the two lines the dispatch named (235 and 237), no third; the file-wide count of
`DEC-200` is now 0. The seven lineage citations in T-04's intent (DEC-199, DEC-198, DEC-158,
DEC-148, DEC-159, DEC-118, DEC-120) and the phrase "after DEC-199" are byte-unchanged. Two surgical
`Edit` calls, not `plan-merge.py` — the merge tool is add-only and exits 7 when an `id`'s value
differs from the base, so a changed `intent:`/`verify:` cannot pass through it. The `approval:`
mapping was NOT touched: it still reads `status: approved / approved_by: operator /
date: 2026-08-23`, and the operator's re-signature for this id correction is the main session's act,
not mine. Verified after the edit by loading the plan through `harness_yaml.load_plan` — the YAML
still parses, T-04's `verify` carries DEC-201, `DEC-200` is absent from its `intent` and DEC-201
present. `git diff` on `plan.yaml` shows exactly four changed lines: my two DEC lines, plus two
pre-existing `status: pending -> building` flips on T-04 and T-05 written by the orchestrator before
I was spawned. I did not run T-04's own `verify:` — DEC-201 does not exist in `DECISIONS.md` yet, so
that gate is the documentor's next turn and would fail by construction now. Out of scope and
untouched as instructed: the missing DEC-NN collision guard, `feature.json`, `STATE.md`, `BRIEF.md`,
`DECISIONS.md`, `DECISIONS-INDEX.md`, `.claude/skills/harness/SKILL.md` (already `(DEC-201)` at the
main session's hand under T-01), T-05's test, and every GitHub card.
