# Signature inputs — FEAT-54-handoff-done-when — cycle 3, 2026-09-02

**The plan is ready for the operator's signature and nothing else is outstanding in it.** The four
batched rulings of 2026-09-02 are applied and recorded; the cycle-3 goal-check says the plan delivers
the operator's stated intent; the cycle-3 adversarial panel ran both readers and left nothing high,
critical or unrated. Both approval blocks read `pending`, because only the main session signs.

This note exists for one reason: **`approval.rulings` has no write route.** The rulings below are the
exact inputs the main session needs, in the shape the record wants them.

## The contract finding: rulings cannot be written by anyone today

- `plan-merge.py sign-approval --file <plan.yaml> --by <name> --date <YYYY-MM-DD>` writes exactly
  three fields: `status`, `approved_by`, `date` (`plan-merge.py:1052-1055`). It has no `--ruling`
  argument and no `rulings` field.
- Every other verb leaves the approval bytes byte-identical; `apply` exits 8 on a proposal whose
  approval mapping differs; `amend` refuses `approval` as unamendable (`plan-merge.py:1449-1451`).
- So there is **no tool route that writes `approval.rulings` at all**, for the main session or
  anyone else — while `check-state.sh` INV-17/INV-32 reads the key (`check-state.sh:488-506`) and
  `templates/plan.yaml:53-56` documents its shape and says the main session may add it.

That is a harness gap, not a FEAT-54 defect: an invariant grades a key no verb can produce. It is
raised as an open question for the harness owner, and it is why the rulings are recorded where they
could legitimately be recorded — `plan.yaml`'s `panel.findings[].disposition`, plus D-10's `because`
for the substance of ruling 4 — and mirrored here.

## The four rulings, as ruling inputs

Each row is what an `approval.rulings` entry would carry: the finding id, the operator's verb, the
attribution INV-32 requires (`who`, `date`), and the one-clause reason.

| finding | severity | ruling | who | date | reason |
|---|---|---|---|---|---|
| `PF-570b9c87adac19d62513b5e90cce0f81` | low | **accept** | operator | 2026-09-02 | The concurrency-sensitive real-corpus mtime/byte no-mutation audit leaves the permanent integration suite; historical-baseline confidence rides non-flaky fixture coverage and explicit review-time evidence. |
| `PF-918326616878584f5958be94fba0ede7` | low | **accept** | operator | 2026-09-02 | The `handoff_comprehension` locally-run kind specifies the repository's conventional `exclude`. |
| `PF-d0ea19ffc351a13d6b569f0169222109` | low | **reject** (overrule) | operator | 2026-09-02 | Deterministic regression coverage that narrative sections have no per-section caps is kept; a future deliberate contract change must update that coverage. |
| `PF-bd92960a1606d9794331d84a14e0b978` | info | **reject** (overrule) | operator | 2026-09-02 | The typed pointer grammar is a stable contract: the persisted INV-17 pass validates grammar only, never target existence, and a rename or narrowing is an explicit versioned contract change by the feature that makes it. |

Ruling 5, Q3, confirmed: **grammar validation is part of the persisted shape validation.** Recorded
in D-10's `because` and carried by REQ-06, SC-15 and T-06 cases (e1)/(e2).

**INV-32 note.** An `approval.rulings` entry is only *required* for a finding that is `unrated` or
above `med` and stays open. All nine findings here are `med` or below and every one carries a
disposition, so the plan passes INV-32 with `rulings` absent. Recording them would improve the
record, not unblock the signature.

## What each ruling did to the artifacts

- **Accept PF-570b9c87** → `plan.yaml` T-06 case (g) rebuilt on a fixture corpus under
  `tempfile.TemporaryDirectory` (clean-corpus and byte/mtime no-mutation assertions on fixture notes
  only), and its trailing paragraph now states that no case in the file touches the real tree.
  `BRIEF.md` SC-04 keeps its claim word-for-word and moves to `verify: inspection` — a recorded
  review-time `check-state.sh` run at `review_sha`, whose evidence home is pinned to the reviewer's
  own `notes/review-<reviewer>-*.md`.
- **Accept PF-91832661** → `plan.yaml` T-09's intent and its inline `verify:` assertion both specify
  `"exclude": ".claude/worktrees/**"`, the value `omp_session_accessor` carries and all 8 existing
  kinds declare.
- **Reject PF-d0ea19ff** → nothing changed. SC-14, T-03 case (h) and T-06 case (h) are
  byte-unchanged, verified after both runs.
- **Reject PF-bd92960a** → no mechanism added. D-10's `because` records the grammar-stability ruling
  and the Q3 confirmation; D-10's `choice`, D-01 and D-03 are byte-unchanged.

## To sign

```
python3 .claude/skills/harness/bin/plan-merge.py sign-approval \
  --file .harness/harness/features/FEAT-54-handoff-done-when/plan.yaml \
  --by "<operator>" --date 2026-09-02
```

`BRIEF.md`'s `## Approval` block is edited by the main session in the same act — both must read
`approved` before the build phase may start at T-01.

## Still open at the gate, none blocking the signature

- **Q-A (harness owner).** `approval.rulings` is graded by INV-32 and documented by the plan
  template, and no verb writes it. Either `sign-approval` gains a rulings input, or the invariant and
  template stop promising a key nobody can produce.
- **Q-B (operator, non-blocking).** The two new cycle-3 findings are recorded and disposed:
  `PF-356837534b1…` (low, SC-04's evidence path — resolved this cycle by pinning the reviewer note)
  and `PF-86e99df98a2…` (info, T-06(g)'s `fully resolving` fixture qualifier — assessed and dismissed
  by the panel as one sentence of upkeep). Nothing needs a ruling.
- **Q-C (harness owner).** The panel's non-harness reader returned a return shape outside the team
  spec's single-key `findings` envelope for the second cycle running; the hosting lead judged it
  parseable and recorded the deviation rather than correcting it.
- **Q-D (harness owner).** Two product-lead contexts have chosen the same run-dir slug on this
  feature and one overwrote the other's `state.yaml`; nothing makes a run id unique per host.

## Budget

`cycles_used: 9` of `max_total_cycles: 10`; `runs: 16` of `max_total_runs: 20` (informational). The
correction pass that applied the accepted rulings is the ninth cycle. **One cycle remains**: if the
signature triggers another repair round, raising the budget is the operator's decision, recorded in
`feature.json`.
