# Panel record — BUG-440 plan panel, cycle 1 — transcribed and applied

**The panel is now durable in `plan.yaml`'s `panel` key, and all five findings are closed by text.**
The panel team's two readers ran and five findings survive at the readers' own severities, none
reassigned; the out-of-team `goalcheck` reader is recorded too — see the appended section. No task
was added; every remedy is a correction to plan or brief text, so no finding carries `resolved_by`.
The plan still needs exactly one operator ruling, and the panel widened it from two options to three.

Source of record: `runs/plan-panel-validator/digest.md` (read whole, prose included). `scope`'s own
note never landed — `check-domain.sh`'s `claim_worktrees()` refused its write over a stale live
`harness-code-reviewer` claim in FEAT-05's registry. That is a harness defect the lead raised as its
Q1, **not a skip**: both readers are recorded `status: ran`, and `scope`'s full prose survives at
`history://Bug440Plan.MilitaryAmphibian.ScopeReview`.

## The five findings

| id | Sev | Reader | Finding | Disposition |
|---|---|---|---|---|
| `PF-b884d6eeb8f166e13839f46191cb8866` | med | scope | T-01 anchored the `run_verdicts` recording beside `code_reviewing_runs.append(...)`, which is inside `if _squad == "validator"` | **resolved** — T-01 `intent` step 1 rewritten |
| `PF-3f3c8cbd75c6538ac820075bfc6efe9b` | low | should-not-exist | The signature ruling is a false dilemma; reconcile-first is nowhere offered | **resolved** — `BRIEF.md` disclosure now A/B/C |
| `PF-ea2e1ae8c184fa68182114bb1966225f` | low | should-not-exist | D-04's dict collapses duplicate `runs[]` ids last-wins while the contract quantifies over entries | **resolved** — D-07 ruling, D-04 and T-01 amended |
| `PF-3d82c450255917a1e1a403dd329ce431` | low | scope | T-01's `verify:` pins only the red-proof heading, not that a real failure was recorded | **resolved** — `verify:` strengthened |
| `PF-dcb6d405dd9dfba7c620224365930746` | info | should-not-exist | The red proof witnesses non-vacuity, not test-first ordering; goal-check Ruling 1's ground overstates it | **resolved** — ground corrected, conclusion kept |

Every id was computed with `panel_findings.py id` on the reader and the digest's own summary,
recorded unaltered, and re-verified after transcription: all five reproduce.

The lead's `panel_dismissed` block is transcribed as `panel.dismissed`, **not** as findings: six
`scope` INFO entries asserting the plan is correct on blast radius, quantifier direction, exact
equality, D-05, D-01 and the absence of orphan REQ/SC — each names a verification and no
consequence, and both readers cleared the same five angles independently. That agreement is the
panel's substantive result and is not a defect list.

## The two rulings I owed

**F-03 — the side structure becomes a per-id LIST (D-07).** The approved contract quantifies over
`feature.json` `runs[]` **entries**; a dict keyed on id compares one entry per id. The shape is real,
not hypothetical: measured across the live control plane 2026-09-06 — 65 `feature.json`, 1002
`runs[]` entries, duplicate ids in exactly one feature (`FEAT-45-adversarial-plan-panel`, id
`2026-08-31-1-validator` twice, both `PASS`, therefore benign today). A list costs the same three
lines T-01 already touches and leaves single-entry behaviour byte-identical, so no fixture changes;
one finding per **distinct** contradicting value (`dict.fromkeys`) keeps SC-01's "exactly one line"
true. I did **not** add a run-id uniqueness invariant — that would be new scope.

**F-04 — strengthen the `verify:`.** T-01 is main-session-direct with no builder/reviewer split, so
the task's own gate is the only automated check before SC-05's inspection; a heading-only stub
passing it is a gate that proves nothing. The `verify:` now also requires the note to carry the
pinned sha `772790be…`, the `CHECK_STATE_BIN` invocation, and a line beginning `RESULT: RED`, and
T-01 `intent` step 4 mandates writing that line. Still four greps plus the one imported case,
runnable verbatim from the worktree root, well under 60s, still a literal `|` block. It does not make
fabrication impossible — nothing automated can — it raises the floor from a heading to a specific
false claim.

## Files changed, and why

- `plan.yaml` — `panel` (set-panel), T-01 `intent` and `verify`, D-04 `choice` (amend), D-07 (apply).
  All through `plan-merge.py` verbs. `approval:` untouched, still `pending`.
- `BRIEF.md` — DISCLOSURE ruling now offers **(A)** merge and accept red, **(B)** reconcile the four
  records first and merge green, **(C)** send the plan back. B adds no scope: the four records are
  per-checkout data edits independent of this code change.
- `notes/research-…-goalcheck-plan-c1.md` — Ruling 1's ground corrected (non-vacuity, not ordering),
  §5 and Q1 rewritten to the three options, and §7's "no `panel` key" reload observation pinned to
  the moment it was taken.
- `notes/research-…-panel-value-c1.md` — the `set-panel` value, kept as the transcription's source.

## Open — for the operator, and one for the harness

**The ruling left for signature:** *(A)* accept `/harness` entry staying red with the 4 blocking
INV-37 findings until you or a delegate reconciles FEAT-07, the two FEAT-22 `INCOMPLETE` rows and
FEAT-25 under a separate ticket you own filing; *(B)* reconcile those four records first, then merge
into a green gate; or *(C)* neither, and the plan goes back for repair or grandfathering scope.

**INV-32's third reader — CLOSED, see the appended section below.** This item is superseded: the
`goalcheck` reader is now recorded in `panel.readers` with `status: ran`, so all three readers
INV-32 expects are present and nothing here is left for the operator.

**Harness defect (the lead's Q1, unresolved):** `claim_worktrees()` unions live claims for a bare
agent-type string across every linked worktree, so a stale FEAT-05 claim can refuse an in-domain
write in an unrelated feature.

---

# Appended — the goalcheck reader is recorded (correction run, 2026-09-06)

**`panel.readers` now carries all three readers INV-32 expects; the five findings are untouched and
no goalcheck finding was added.** This closes the open question the first record run raised: the
`goalcheck` reader RAN — it is the plan-phase product segment the orchestrator sequenced before the
panel (pm's goal-check of the drafted plan against the operator's stated intent, persona
`harness-pm`, artifact `notes/research-BUG-440-digest-verdict-reconciliation-goalcheck-plan-c1.md`).
It is absent from the validator lead's digest because the `plan-panel` team declares two steps and an
orchestrator-sequenced segment is not a team step. **It is not a skip.**

Why it had to be fixed before signature, not after: `check-state.sh:534` sets
`expected_readers = {"should-not-exist", "scope", "goalcheck"}` and :544-547 appends a BLOCKING
violation for any of the three whose recorded status is neither `ran` nor `skipped`. INV-32 grades
approved plans only, so a two-reader record is green today and turns red the instant the operator
signs. Precedent for recording an out-of-team goalcheck reader: `BUG-1286` and `BUG-1305` plan.yaml.

## Ruling — no `reader: goalcheck` finding enters `panel.findings`

I agree with the orchestrator's read, on the evidence of my own goal-check note §6. F-01 through
F-04 (all MED) were corrected in the same pass that found them — `BRIEF.md` and T-01 `intent` carry
the corrections — so none survived to be recorded. F-05, F-06 and F-08 are `No change` items that
name no defect in the plan text: F-05's tension is already answerable inside the operator's own
disclosure ruling, F-06 would be a criterion true by construction (P-03), F-08 is informational.

The near-miss worth naming is **F-07** (LOW, advisory: SC-02's clean tree must not host a
`squad: validator` run or it reddens on INV-6 rather than INV-37). I checked whether its advice would
be lost if unrecorded: it is not — T-01 `intent` already fixes fixture E as `harness-product-lead`
(`plan.yaml:374`), so the advice is in the instruction the builder receives. **Nothing open, nothing
recorded.** A reader that ran and left nothing open is the healthy outcome; the `readers` entry is
the proof it ran, and padding the finding list to make it look productive would be falsifying the
record.

## What changed, and the acceptance output verbatim

One write: `plan-merge.py set-panel` over the whole `panel` mapping, from a value derived by loading
the mapping already on disk and appending one reader, so every other key is carried through
unaltered. `reader_coverage_note` was rewritten — it no longer predicts an INV-32 goalcheck
violation. `last_run`, `cycle`, `team`, `verdict`, `severity_max`, `source_digest`, `transcribed_by`,
`transcribed_at`, `transcription_rule`, `dismissed` (1) and `adequacy_notes` (5) are unchanged;
`approval:` was not touched. The value file is
`notes/research-BUG-440-digest-verdict-reconciliation-panel-value-c1r2.md`.

```
1 plan-panel-validator ['goalcheck', 'scope', 'should-not-exist'] 5 pending
```

```
MATCH PF-b884d6eeb8f166e13839f46191cb8866 PF-b884d6eeb8f166e13839f46191cb8866 scope med resolved
MATCH PF-3f3c8cbd75c6538ac820075bfc6efe9b PF-3f3c8cbd75c6538ac820075bfc6efe9b should-not-exist low resolved
MATCH PF-ea2e1ae8c184fa68182114bb1966225f PF-ea2e1ae8c184fa68182114bb1966225f should-not-exist low resolved
MATCH PF-3d82c450255917a1e1a403dd329ce431 PF-3d82c450255917a1e1a403dd329ce431 scope low resolved
MATCH PF-dcb6d405dd9dfba7c620224365930746 PF-dcb6d405dd9dfba7c620224365930746 should-not-exist info resolved
re-derived 5 of 5
```

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
DEVIATION T-01 .claude/skills/harness/bin/check-state.sh, tests/integration/test-check-state.py, .harness/harness/features/BUG-440-digest-verdict-reconciliation/notes/redproof-BUG-440.md granted to harness-backend-dev, harness-dev-ops, harness-orchestrator, harness-qa but declared main-session-direct
0 violation(s) across 1 plan(s)
EXIT=0
?? .harness/harness/features/BUG-440-digest-verdict-reconciliation/
```

The single `git status --porcelain` line is the whole (untracked) feature directory: nothing outside
`<FEATDIR>` was modified. The `DEVIATION` line is D-06's accepted DEC-174 carve-out output (G-12);
only `VIOLATION` lines gate, and there are none.

## Open

Nothing new. The operator's A/B/C ruling above is still the only thing owed before signature, and
the lead's `claim_worktrees()` harness defect is still unresolved.
