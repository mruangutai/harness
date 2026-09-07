# STATE

## Current

- feature: BUG-148-gate-record-correction
- run: .harness/harness/features/BUG-148-gate-record-correction/runs/2026-09-06-04-product/state.yaml
- squad: none (plan phase complete; the operator's rulings are applied, the signature is outstanding)
- status: awaiting-user
- station: plan (`plan.yaml` `status: plan`, `approval.status: pending`)

**Plan phase COMPLETE, unsigned, rulings applied.** BRIEF.md (5 REQ, 6 SC, every SC declares its
verify) and plan.yaml (2 tasks, 5 decisions, panel record) are signature-ready. Nothing was
corrected: DECISIONS.md, DECISIONS-INDEX.md and FEAT-05's STATE.md are byte-unchanged, and no
historical artifact was touched.

Segments run, in order: plan draft (pm) → goal-check of the drafted plan against the operator's
grilling (pm, FAIL, 2 must_fix) → fix cycle (pm, both closed) → plan-panel (validator lead, both
readers RAN, PASS, `severity_max: med`, `must_fix: []`, 5 findings) → panel transcription (pm) →
operator rulings applied (pm). `check-plan-routes.py` exits 0; `check-state.sh` reports nothing
against this feature except the expected "BRIEF.md is NOT approved" halt and the pending note.

**Operator rulings of 2026-09-06, recorded as D-05 and in the findings' dispositions:**
(1) FEAT-05's STATE.md rewrites its false claim in place, matching DEC-174 — no appended note, and
D-01's `because` now records this as a ruling rather than as a forced consequence
(`PF-6b4a7af5de3e77e59af34e9a00b68548`, resolved). (2) The `--stdout | diff` form stays named in
BOTH corrected records; REQ-03 stands (`PF-54450f537e28244ae73d9c0e48ae4efe`, resolved). (3) T-02's
intent now binds its mechanism clause to T-01's and `depends_on: [T-01]`
(`PF-ed3ec57922f582bd208169c1120d0946`, resolved). (4) The approved grilling artifact was relocated
verbatim into this feature's `notes/`, inside SC-05's allowlist.

Facts measured by this orchestrator, in this worktree, that the plan rests on:
- `gen-decisions-index.py --check` today → exit 2, "unrecognized argument(s): --check. Wrote
  nothing." (argv parser `.agents/skills/harness/bin/gen-decisions-index.py:240-259`).
- On 2026-08-03 argv validation did not exist — it landed at `ffbdbfa1` (2026-08-05, #140). At
  `99b380e3` (2026-08-02) `main()` read `stdout_mode = "--stdout" in sys.argv[1:]`, so `--check`
  fell through to the WRITE path: the script regenerated `DECISIONS-INDEX.md` and exited 0. Both
  panel readers independently confirmed this premise at source.
- Lanes: `DECISIONS.md`/`DECISIONS-INDEX.md` → `harness-documentor`; FEAT-05 `STATE.md` →
  `harness-orchestrator` (no member persona holds it).
- Branch base `41c16c736e3cc4b2b331757081c90a24f2ba977d`. `git merge-base origin/main HEAD` is
  `8bdc2477` and already carries three foreign paths, which is why SC-03/SC-05 grade against the
  branch base instead.

Harness defect observed, not worked around: the goal-check run's directory
(`runs/2026-09-06-02-product/`) was reused by the following fix run, so only `plan-fix-c1` survives
in its `state.yaml`. The goal-check's own evidence survives at
`notes/research-BUG-148-goalcheck-plan-c0.md`.

## Open Questions

- Q1 (BLOCKING, the one decision left): sign BRIEF.md `## Approval` and plan.yaml `approval:` —
  `plan-merge.py sign-approval`, main session only. Both read `pending`.
- Q2 (non-blocking, main session's act): the untracked source copy of the grilling artifact at
  `.harness/harness/notes/grilling-gate-record-correction-2026-09-06.md` still exists. It resolves
  to NOBODY, so no agent lane may delete it; the relocated copy under this feature's `notes/` is
  the one the BRIEF cites.
- Panel findings `PF-a2df57f48de3e81d49745cfd1adaa20b` (med, accepted-by-design, disclosed in
  BRIEF's Verification gaps) and `PF-b7b07ec7b7f6cacb3b894cae4bda2a04` (low, informational) remain
  open by design; neither was ruled on and neither gates.
