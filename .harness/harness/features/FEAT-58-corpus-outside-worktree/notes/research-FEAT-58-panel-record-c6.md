# Panel record — cycle 6 transcription — FEAT-58-corpus-outside-worktree

**The cycle-6 panel is transcribed into `plan.yaml`'s top-level `panel` mapping. SIX new findings,
not five: four high (PP-01..PP-04) and two med (PP-05, PP-06). All four highs are recorded
UNRESOLVED and reach the operator's batched signature review under DEC-207.** No finding was fixed,
accepted, waived, resolved or risk-accepted by this chain, and no task, decision, REQ, SC, `status`
or `approval` field was touched. `PP-06` was absent from my dispatch's list but present in the
digest (`runs/planpanelc6-validator/digest.md:153-164`); dropping it would have falsified the
record, so it is transcribed with the rest.

## What was written, and by what route

Single write, single route: `plan-merge.py set-panel --file <plan.yaml> --value-file
notes/panel-value-c6.yaml`. The value file is retained beside this note as the transcription's own
witness. `cmd_set_panel` (`plan-merge.py:1067-1083`) line-splices the `panel` range only and refuses
unless the file reloads with `panel` equal to the value supplied, so every non-panel line is
byte-identical by construction.

- `last_run: planpanelc6-validator`, `cycle: 0`, `severity_max: high`.
- `readers:` — both `ran`, neither skipped. `should-not-exist` (fable-advisor, PASS, 3 findings;
  holds no write grant, so its findings are transcribed from the lead digest — recorded in its
  `note:`); `scope` (harness-code-reviewer, DIGEST verdict FAIL, 3 findings, `must_fix_returned: 1`).
- `findings:` — 19 rows: PP-01..PP-06 new, PL-01..PL-04 carried forward resolved with `resolved_by`
  plus an additive `cycle6_panel_verification` per row (PL-04 keeps the digest's caveat: resolved
  **as a specification**, with PP-01/PP-04 landing on that same remedy), and VL-01..VL-09 unchanged
  **inside** `findings:` so `sign-approval --overrule PF-ID` still reaches them.
- `fix_order:` verbatim, with PP-04 stated **last among the PART 1 group** and why.
- `orchestrator_verified_premises:` three, each attributed to the orchestrator at its own tier —
  including that `core.hooksPath` is local config and **contradicts the DoD note's own
  travels-with-a-clone claim**.
- `record_accuracy:` two facts — `scope`'s artifact prose (PASS / "No must_fix") against its DIGEST
  (FAIL, non-empty `must_fix`), routed on the DIGEST with nothing changed; and the reader
  contradiction on N-13's benign-transient handling resolved in `should-not-exist`'s favour,
  lead-verified at source.
- `prior_cycle:` byte-identical to the pre-existing 13-row mapping. `severity_reconciliations:` and
  `assessed_and_dismissed:` keep their four and two prior entries and gain the cycle-6 rows.
- `note:` and `transcription_rule:` state that this is a transcription: nothing re-ranked, re-worded
  into a different claim, merged, split, or given a disposition the digest does not state.

## PF- ids — computed, never typed

Each id comes from `panel_findings.py id --reader <reader> --summary <summary>` over that row's own
recorded values: `PP-01 PF-bad620b6…`, `PP-02 PF-73b804f7…`, `PP-03 PF-52754958…`,
`PP-04 PF-d4323cbe…`, `PP-05 PF-bfe22e77…`, `PP-06 PF-318dd276…`. The one normalization —
markdown emphasis and backticks removed, which `plan.yaml` values may not carry — is recorded in
`transcription_rule`, and ids are computed from the normalized value **as recorded**, so a later
`--overrule PF-ID` resolves against the stored text.

## Verification performed

`/tmp/f58_verify_c6b.py` — 62 assertions, all PASS: field values, both reader rows, every PP row's
severity/reader/`lands_on`, each id recomputed from its own row, the four highs' UNRESOLVED
dispositions, PL carry-forward against the frozen record, VL rows against the value file, 19-row
count, `prior_cycle` equality, fix order, premises, record-accuracy facts, and no backtick or bold
in any panel scalar.

**Diff scope.** `git -C <wt> diff --stat` shows four modified tracked files: `plan.yaml` (mine, panel
only) and `BRIEF.md`, `feature.json`, `observations/harness-pm.md` — all three already modified
before this dispatch and **not** written by it (mtimes 15:06 / 15:37 / 14:53 against my writes at
15:43). `status: plan` and `approval` are byte-identical to HEAD. The task/decision content that
differs from HEAD is the pre-existing cycle-6 amendment set (`N-06`, `N-09`, `N-10`, new `N-13`;
`D-07`, `D-11`, `D-12`, new `D-16`/`D-17`) — the very artifacts the panel read. HEAD was not moved
and nothing was committed.

**Baseline warning for the next reader:** HEAD is *not* the baseline for this feature's plan. The
cycle-6 record edits (PL `resolved_by`, VL-07's corrected pointer) are uncommitted, so a
HEAD-vs-worktree comparison reports them as this run's work. Compare against the retained value
file.

## Open questions

- **Q1 (from the panel, carried in `panel.open_questions`, non-blocking).** PP-05: `SC-16` and N-13
  PART 1 both claim the owner root is read "at the reviewed commit" while `check-state.sh` has no
  `HARNESS_REVIEW_SHA` mechanism. The honest remedy edits `SC-16`, an approval-gated artifact — the
  operator's, not a fix cycle's.
- **Q2 (mine).** The panel schema has no field for a reader's *internal* PASS/FAIL inconsistency, so
  fact 1 is recorded under a free-form `record_accuracy:` key rather than a schema field. Nothing was
  dropped or reshaped; if the operator wants that fact machine-readable, the schema needs the field.
