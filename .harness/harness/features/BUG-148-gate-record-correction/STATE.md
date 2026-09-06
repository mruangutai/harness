# STATE

## Current

- feature: BUG-148-gate-record-correction
- run: .harness/harness/features/BUG-148-gate-record-correction/runs/2026-09-06-03-product/state.yaml
- squad: none (plan phase complete; awaiting the operator's signature)
- status: awaiting-user
- station: plan (`plan.yaml` `status: plan`, `approval.status: pending`)

**Plan phase COMPLETE, unsigned.** BRIEF.md (5 REQ, 6 SC, every SC declares its verify) and
plan.yaml (2 tasks, 4 decisions, panel record) are drafted and signature-ready. Nothing was
corrected: DECISIONS.md, DECISIONS-INDEX.md and FEAT-05's STATE.md are byte-unchanged, and no
historical artifact was touched.

Segments run, in order: plan draft (pm) → goal-check of the drafted plan against the operator's
grilling (pm, FAIL, 2 must_fix) → fix cycle (pm, both closed) → plan-panel (validator lead, both
readers RAN, PASS, `severity_max: med`, `must_fix: []`, 5 findings) → panel transcription into
plan.yaml `panel:` (pm). `check-plan-routes.py` exits 0; `check-state.sh` reports nothing against
this feature except the expected "BRIEF.md is NOT approved" halt and the pending-approval note.

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

- Q1 (BLOCKING, panel `PF-6b4a7af5de3e77e59af34e9a00b68548`, med): the operator settled on "add a
  dated note"; D-01 rewrites each false sentence in place. Forced for DECISIONS.md (DEC-205 plus
  `test_no_amendment_construct_survives_in_the_authority`); for FEAT-05's STATE.md it is a choice
  supported by `check-domain.sh:1798-1800` ("`## Current` is replaced, never appended"), not a
  requirement. Accept the rewrite, or have D-01 restate it as a choice?
- Q2 (`PF-54450f537e28244ae73d9c0e48ae4efe`, low): REQ-03 embeds the `--stdout | diff` pipeline
  verbatim in both records — plant the string twice, or name the script's docstring its single home?
- Q3 (`PF-ed3ec57922f582bd208169c1120d0946`, low): require T-02's mechanism clause to match T-01's,
  so the two corrected records cannot diverge while both verifies pass?
- Q4 (non-panel): the grilling artifact `.harness/harness/notes/grilling-gate-record-correction-2026-09-06.md`
  is untracked and outside the feature directory, which SC-05's allowlist does not admit. Commit it
  under this feature's own `notes/`, or leave it uncommitted?
