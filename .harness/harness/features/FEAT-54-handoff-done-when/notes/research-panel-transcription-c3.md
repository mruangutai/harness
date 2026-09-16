# Panel transcription c3 — FEAT-54-handoff-done-when

**DONE.** `plan.yaml`'s `panel:` now records the c3 run (`cycle: 3`, `last_run:
2026-09-02-c3-validator`, three readers `ran`, **9 findings**), the four stale `no operator ruling
exists` dispositions are replaced with the operator's batched rulings of 2026-09-02, and PF-bd92960a
no longer contradicts D-10's amended `because`. SC-04's verification sentence now pins the reviewer's
own per-feature note as the home of its review-time evidence (closes F-2). Both approval blocks stay
`pending`; no `approval.rulings` was written. No task, decision, requirement or criterion added.

## Commands run, in order

```
python3 /tmp/feat54_step0.py                      # pre-write dump -> /tmp/feat54-panel-pre.json
python3 .claude/skills/harness/bin/panel_findings.py id --reader should-not-exist --summary "<F-2>"
  -> PF-356837534b18f5a4e622e5f461c41a71
python3 .claude/skills/harness/bin/panel_findings.py id --reader should-not-exist --summary "<F-3>"
  -> PF-86e99df98a2caca9ae1334ab55d9468c
python3 /tmp/feat54_build_panel.py                # -> /tmp/feat54-panel-c3.yaml; recomputed the two
                                                  #    ids in-process: identical to the CLI output
python3 .claude/skills/harness/bin/plan-merge.py set-panel \
  --file <abs plan.yaml> --value-file /tmp/feat54-panel-c3.yaml
  -> PANEL cycle 3 -> ...plan.yaml / APPLIED
Edit BRIEF.md SC-04 verification sentence (lines 93-94 -> 93-96)
python3 /tmp/feat54_verify.py                     # read-back from disk
python3 .claude/skills/harness/bin/check-plan-routes.py <plan.yaml>  -> 0 violation(s), exit 0
```

Both new ids were computed from the FINAL summary text written into the file, never typed. Backticks
in the digest's F-3 wording (`` `fully resolving` ``) were dropped before hashing because a plan value
carries no markdown; `panel_findings.py` only lowercases and collapses whitespace, so that stripping
IS part of the identity — which is why the id was computed after the wording was final, not before.

## Read-back evidence (from disk, post-write)

```
cycle: 3 | last_run: 2026-09-02-c3-validator
readers: [('scope','ran'), ('should-not-exist','ran'), ('goalcheck','ran')]
findings count: 9
PF-4205e7e2… [med]  ACCEPTED by the operator at the batched ruling of 2026-09-02 and implemented as D-10
PF-1e45eb3a… [info] REJECTED by the operator at the batched ruling of 2026-09-02
PF-570b9c87… [low]  ACCEPTED by the operator at the batched ruling of 2026-09-02   <- rewritten
PF-91832661… [low]  ACCEPTED by the operator at the batched ruling of 2026-09-02   <- rewritten
PF-d0ea19ff… [low]  REJECTED by the operator at the batched ruling of 2026-09-02   <- rewritten
PF-f2aee0d4… [med]  resolved by this planfix-c2c run
PF-bd92960a… [info] REJECTED by the operator at the batched ruling of 2026-09-02   <- rewritten
PF-35683753… [low]  resolved by this planfix-c3 run                                 <- NEW (F-2)
PF-86e99df9… [info] assessed and DISMISSED as a repair by the panel at 2026-09-02-c3-validator  <- NEW (F-3)

no-operator-ruling phrase present anywhere: False
approval: {'status': 'pending'} | rulings key present: False
status: plan
tasks: T-01..T-12 (12)   decisions: D-01..D-08, D-10 (9)
```

**Carry proof, mechanical** — post-write `(id, severity, reader, summary)` compared per id against the
Step-0 pre-write dump: `identical=True` for all seven carried findings; `dropped pre-existing
findings: none`. Byte-identity is structural, not retyped: the builder copies those four keys by
reference from the pre-write mapping and overrides `disposition` only.

**PF-bd92960a re-derived before rewriting.** D-10's `because` (plan.yaml:207) records the same ruling
— stable contract, grammar only, never target existence, a future rename is that feature's versioned
contract change, plus the operator's Q3 confirmation. The old disposition asserted the opposite; the
new one agrees with D-10 clause for clause.

## BRIEF.md — one hunk, inside SC-04 only

`git diff -U0 -- BRIEF.md` is a single hunk at line 92 (SC-04's verification region). SC-04's claim
sentence (lines 89-91) is untouched, `verify: inspection` is retained, SC-05 onward is untouched, and
`## Approval` still reads `status: pending` with empty `approved-by` and `date` (BRIEF.md:196-200).

## Attribution of the non-panel `plan.yaml` hunks — NOT this run

`git diff` vs HEAD shows hunks at `:207` (D-10) and in T-06/T-09. Those predate this run: the Step-0
dump printed D-10's amended `because` **before** any write here, and the c3 panel digest cleared
T-09's `exclude` literal and T-06(g) by reading the same file pre-write. My only write to `plan.yaml`
was `set-panel`, which splices the `panel:` range and refuses unless the file reloads equal to the
value supplied.

## Not committed, deliberately

The feature's own plan-phase record shows one commit for the c2 revision (`ca43c014`) and the whole
c3 pass left uncommitted (BRIEF.md, plan.yaml, three notes all dirty before I started). There is no
per-run commit convention to honour, and committing here could not isolate my two files from the
prior run's uncommitted edits inside the same files.

## Open

- **E1 stands, unchanged (main session only):** `approval:` is `{status: pending}` with no `rulings:`
  key, so the batched ruling of 2026-09-02 is recorded in `panel.findings[].disposition` and in D-10,
  but nowhere in the approval record. Only `sign-approval` writes it.
- F-3 remains open by design — the panel dismissed the repair; T-06(g)'s `fully resolving` qualifier
  is a future editor's one-sentence upkeep, not a cycle.
