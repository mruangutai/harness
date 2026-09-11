# Panel record — FINAL panel transcription into plan.yaml — FEAT-58

**BLUF: the final panel is transcribed and the plan is ready for the signature gate. Seven findings
are open — 1 high, 2 med, 4 low, 0 critical, 0 unrated — none accepted, waived or risk-accepted by
anyone; the structural answer is recorded as NOT STRUCTURAL with the per-REQ mechanism list; and the
always-green list (H-01 high, M-01 med — the two a build-phase test would NOT catch) is its own
field. Nothing was fixed here. Only `plan.yaml`'s `panel:` mapping changed.**

## What was written, and how

- Route: `plan-merge.py set-panel --file <fd>/plan.yaml --value-file <fd>/notes/panel-value-last.yaml`.
  Receipt: `PANEL cycle 0 -> …/plan.yaml` / `APPLIED`. No Edit, no Write to `plan.yaml`, no redirect.
- The replacement value was **built programmatically from the loaded prior panel**, never retyped, so
  carried rows cannot drift: PL-01..PL-04 and VL-01..VL-09 are copied byte-for-byte with their `PF-`
  ids; PP-01..PP-06 keep label, severity, reader, `lands_on`, summary, remedy, reporter, `fix_order`
  and `id` and had **only `disposition` moved** (plus an additive `disposition_source`); `prior_cycle`
  is copied unchanged. A post-write reload asserts every carried row equals its prior value.
- 26 finding rows total, every one carrying an `id:` so `sign-approval --overrule PF-ID` reaches it.

## The seven open rows and their computed ids

|label|sev|id|build catches?|
|---|---|---|---|
|H-01|high|`PF-71355e9c75df3b571e8e3d0d9de9a153`|NO — always-green|
|M-01|med|`PF-b73686f676e78f82fe0ab17cbebabad0`|NO — always-green|
|M-02|med|`PF-f1ae29441bee6ef1c64d301c99d5eb23`|YES|
|L-01|low|`PF-a8ce72db5b5b4054cb480c22676490db`|no runner exposure (citation defect)|
|L-02|low|`PF-9ffaa03b4f105bc652f81aad20c0469b`|no runner exposure (record defect)|
|L-03|low|`PF-454129f3295b6e2a2d9659d10c9c2065`|YES|
|NF-01|low|`PF-99f697b0e82bfd5e9b4e453dbeb8e485`|no — INV-31 catches the residue next run|

Each id was recomputed through the CLI — `panel_findings.py id --reader <r> --summary <s>` on that
row's own recorded reader and summary — and matched the written value for all seven.

The six goal-check findings are recorded as **CONFIRMED BY THE PANEL**, not re-raised, each with the
panel's severity, its structural-versus-clause call and its own evidence anchor. `severity_max: high`
carries `severity_max_reason` stating it is carried **solely** because H-01 stands unfixed by the
operator's own ruling, not because the panel rejected the plan.

## Honest cycle-8 dispositions on PP-01..PP-06 (the record now differs from what it said)

The prior block recorded all six as UNRESOLVED. Derived from `notes/research-FEAT-58-goalcheck-plan-c8.md:6-8`
and `:95-100`: **four landed whole** — PP-02 (INV-31 skip), PP-03 (clause 1 wording), PP-05 (review-sha
framing gone), PP-06 (zero-match case) — and **two did not**: PP-04's red proof cannot redden (now
tracked as **H-01**) and PP-01's env-strip witness is always-green (now tracked as **M-01**). Each row
names its residual. The record does not say "all six landed".

## Verification evidence

- `git diff --stat` (worktree): `plan.yaml` plus four files modified **before this run** — `BRIEF.md`
  (mtime 15:52:50), `feature.json` (16:48:08), `observations/harness-pm.md`, `.harness/notes/dod-…md`
  (15:53:39); `plan.yaml` mtime 16:55:45 is this write. **BRIEF.md was not touched by this pass.**
- Confinement, positively demonstrated: `panel:` still begins at **line 638** (nothing above moved),
  and every task-region anchor the goal-check cites is present, unmodified, at exactly
  *pre-edit line + 437* — the panel's growth — verified for `plan.yaml:3207-3211` → 3644-3648
  (clause 1), `:3239-3247` → 3676-3684 (PART 1 RED PROOF) and `:3340-3347` → 3777-3784 (the skip
  DISCRIMINATION clause NF-01 lands on). Task text is shifted, never changed.
- Re-read of the applied plan: `status: plan`, `approval: {status: pending}`, 12 tasks
  (N-01..N-10, N-12, N-13), 17 decisions — all as before. `prior_cycle` intact (`count` string
  unchanged); 4 PL and 9 VL rows present with their original `PF-` ids.
- No open finding's disposition records acceptance, waiver or risk acceptance; each says explicitly
  that no agent in this chain may, and that acceptance is `approval.rulings` (DEC-207).
- E1 is recorded verbatim from the digest's `escalations:` entry, `resolution: pending`,
  `decided_by: operator`, `recorded_as: approval.rulings at signature`.
- Nothing was run beyond reads, `set-panel`, and `git -C … diff/status`. HEAD not moved, nothing
  committed, no suite, linter or formatter run.

## Open question carried to the operator

**Q1 (blocking on the signature, not on the plan)** — H-01's disposition: accept at signature, or
convert to a build-phase task on N-13. If converted, the task must carry a **MISSING-producing
mutation**, not Q4's wording (Q4's wording reproduces the PP-03/PP-04 contradiction), and folding
M-01's remedy into it — assert the reached feature-directory NAME SET equals
`os.listdir(<owner_root>/.harness/harness/features)` — closes **both** with one assertion and needs no
SC-16 edit. The cycle-6 Q1 (PP-05) is carried as `Q1-cycle6` marked SETTLED rather than deleted.

## Fields retained rather than dropped

`orchestrator_verified_premises`, `record_accuracy`, `severity_reconciliations` (+2 rows recording
that this panel moved no severity), `assessed_and_dismissed` (+3 rows: the two readers' converged
lenses are weaker evidence than they look; the measurement set was inherited not re-derived; the
45-vs-48 ledger ruling upheld), `adequacy_notes` (this panel's six, then a marker, then the cycle-6
four unchanged), `prior_readers` (the cycle-6 readers), and `fix_order` — rewritten to say its
subject is **superseded as an instruction, preserved as record**, carrying the cycle-6 order verbatim
inside it, because no fix cycle follows this panel.
