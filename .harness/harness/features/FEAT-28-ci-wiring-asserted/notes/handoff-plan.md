# Handoff — FEAT-28-ci-wiring-asserted, plan → build — written at 6bbd706, seq-2

## Next

STOP. Do not dispatch a build. The plan phase ended at the user gate and the gate is unanswered:
`plan.yaml` `approval.status: pending`, `BRIEF.md ## Approval` pending. The blocking question is
whether to reverse DEC-183's settled "nothing protects the gate — not pending, settled", which
deleted 39 assertions to make it true. **If the owner declines, the feature is void, not reduced** —
that reversal is the whole of FEAT-28. On approval the first dispatch is T-01 to eng-lead
(`test-check-plan-routes.py`, the `case_26` predicate family); T-02 then T-03, strictly serial.

## Trust

- Every Trust claim below re-measured at 6bbd706 after HEAD moved twice under this run (FEAT-27 committing on its own branch) — `git rev-parse HEAD` — verified-at 6bbd706
- Both gates pass by EXIT CODE, not by silence — `check-plan-routes.py` exit 0, `validate-feature-json.py` exit 0 — verified-at 6bbd706
- `case_25b9` is a genuine phantom — `grep -rn "case_25b9" .claude/skills/harness/bin/` returns 0 hits — verified-at 6bbd706
- The truncation trap is real: `def case_25():` exists at `test-check-plan-routes.py:1030`, so any rule truncating a cited id to its leading `case_NN` RESOLVES `case_25b9` — verified-at 6bbd706. The plan now forbids truncation (`plan.yaml:162`) and its mutation case uses `case_25zz9`, which truncates to `case_25`, finds that def, and so distinguishes the broken rule from the fixed one.
- `case_19a3b` is the one REAL citation in `tests.yml` — `test-check-plan-routes.py:366` — verified-at 6bbd706
- The plan touches no FEAT-27 file: host `test-check-plan-routes.py` is already in `INTEGRATION_SCRIPTS`, and `.github/workflows/tests.yml` is clean and was never touched by any commit on this branch (`git log main..HEAD -- .github/workflows/tests.yml` empty) — verified-at 6bbd706. The FEAT-27 wait is a LANDING constraint (one checkout, HEAD on their branch), NOT a file conflict.
- The predicate design is red-provable but the plan-time prototype is GONE (session scratchpad). I ran it once: 32 `ci_wiring_*` assertions green on the real workflow, exit 0, no tree mutation — **treat as UNVERIFIED and re-derive**; reproducing green-on-real / red-on-mutant IS T-01's acceptance.
- `.github/workflows/tests.yml` resolves to `harness-dev-ops` and is NOT in DEC-174's carve-out list (`check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-state.sh`) — DEC-174 @4627, read directly — verified-at 6bbd706. **But see the open question**: DECISIONS-INDEX.md states the carve-out as a CATEGORY ("hooks, validators or gate scripts") which would include `check-plan-routes.py`. `--resolve` answers who may WRITE; the EXECUTION carve-out is mechanized nowhere.

## Dead ends

- Do not dispatch a build in this checkout while FEAT-27 is live — one working tree, HEAD on `feat/FEAT-27-expertise-repository-tier`, two commits landed mid-run — verified-at 6bbd706
- Do not use `case_99zz` or `case_25b9` itself in the phantom mutation proof — `case_99` has zero defs so it reddens under broken and fixed rules alike; `case_25b9` is deleted from the real text by T-02, so a fixture keyed to it depends on the thing under test — source: plan.yaml:237-239 — verified-at 6bbd706
- Do not pin the plan count M — M-gating was deliberately removed 2026-08-13 after it failed a healthy all-shipped tree — source: plan.yaml D-05, `tests.yml:156-164` — verified-at 6bbd706
- Do not try to close the `Integration suite` self-protection hole here — deleting `tests.yml:81` leaves a green `integration` context with the guard never run; needs a second required context or a base-ref check — source: plan.yaml D-03 — verified-at 6bbd706
- Do not expect `SendMessage` at orchestrator or lead tier — absent this session, so a correction becomes a second spawn against the same unlocked file. It happened at both tiers; four run dirs exist for three intended runs — verified-at 6bbd706

## Working set

- `.harness/harness/features/FEAT-28-ci-wiring-asserted/BRIEF.md` — `## Approval` line 178 holds the blocking question
- `.harness/harness/features/FEAT-28-ci-wiring-asserted/plan.yaml` — 3 tasks, D-01..D-05
- `.harness/harness/features/FEAT-28-ci-wiring-asserted/notes/orchestrator-citation-audit.md` — my measurement of all three `tests.yml` citations
- `.harness/harness/features/FEAT-28-ci-wiring-asserted/runs/2026-08-19-01-product/digest.md` — the audit that found the resolver defect
- `.harness/harness/docs/DECISIONS.md` @5317 — DEC-183, the clause being reversed
