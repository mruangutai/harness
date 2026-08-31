# Handoff — FEAT-45-adversarial-plan-panel, build → validate — written at 9d26350, seq-4

Supersedes the seq-3 note, whose `## Next` handed seven main-session-direct tasks up. Those landed
at 7ee3f65 and the build is now COMPLETE: all twelve tasks `done`, QA PASS, SIMPLIFY clean.

## Next

Enter validate. Two preconditions sit together and BOTH come before the panel is dispatched:
re-pin `review_sha` to the build tip, then `gh-sync.py status <feature-dir> Review` (moves the
parent AND every sub-issue). Then dispatch the review panel through `harness-validator-lead`.
`review_sha` is still `1d3e5db` — the PLAN-phase sha, deliberately left per the operator's Q1
ruling — and it does NOT contain any build work. Pinning it is validate's first act, not build's.

## Trust

- All twelve tasks are `done` in plan.yaml and committed; `approval.status` still `approved` and
  never written by any agent — `feature.json`, `plan.yaml` — verified-at 9d26350
- The orchestrator re-ran the `verify:` block of every task it dispatched (T-01, T-09, T-10, T-11,
  T-12) verbatim from plan.yaml itself, each exit 0 — not relayed from a digest — verified-at 9d26350
- Full suite at tip: runner exit 0, `grep -c '^FAIL '` = 0, 1012 result lines. Discovery is NOT
  shrunk — QA independently counted 56 scripts full / 29 unit — verified-at 9d26350
- QA gate PASS, `matrix_ok: true`. It re-verified 7 of the eng lead's 16 claimed mutants itself and
  RECORDED that the other 9 stay author-reported — `notes/qa-feat45-c0.md` — verified-at 9d26350
- SIMPLIFY ran all four angles and applied NOTHING; the tree was byte-unchanged afterwards, so no
  post-apply suite re-run was owed — `runs/2026-08-31-01-eng/digest.md` — verified-at 9d26350
- `panel_findings.py` is genuinely the single source of finding identity — the reuse angle found no
  second normalization or hashing anywhere in the tree — verified-at 9d26350
- T-12 was added MID-BUILD by harness-pm under FEAT-45's existing signature, not a re-signature: the
  third team file is T-02's signed product, recorded as decision D-15 — `notes/research-team-count-tripwire.md` — verified-at fc42462

## Dead ends

- Do NOT dispatch a validator against `review_sha: 1d3e5db`. It predates every build commit, so the
  panel would return PASS on a tree the work is absent from — `feature.json` — verified-at 9d26350
- Do NOT re-run SIMPLIFY or re-open a build task to satisfy a panel finding about the doctrine files.
  `plan-panel.yaml`, both `harness-validator-lead.md` copies, `SKILL.md`, `harness-plan.md`,
  `templates/plan.yaml` and `harness-spec-driven/SKILL.md` all resolve to NOBODY under
  `check-domain.sh`; no squad can apply there and a fix cycle would be futile — verified-at 9d26350
- Do NOT route a `check-state.sh` or `test-check-state.py` fix to a lead. DEC-174 enumerates both and
  bars EXECUTING enforcement-layer changes through a team run — `DECISIONS.md:4326` — verified-at 9d26350
- Do NOT read `check-state.sh` green as a precondition for anything. INV-26 is structurally red for
  this feature all through Building and the cause is the mirror's own writers, not the plan; see the
  orchestrator's returned open questions — verified-at 9d26350
- Do NOT use `plan-merge.py` to CHANGE a task `status:` — it is ADD-ONLY and exits 7 on a differing
  id. It IS the correct route for ADDING, as T-12/D-15 were added

## Working set

- `.harness/harness/features/FEAT-45-adversarial-plan-panel/feature.json` — pin `review_sha` here first
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/plan.yaml` — 12 tasks, D-15
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/BRIEF.md` — REQ-01..REQ-14, SC-01..SC-17
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/qa-feat45-c0.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-31-01-eng/digest.md`
