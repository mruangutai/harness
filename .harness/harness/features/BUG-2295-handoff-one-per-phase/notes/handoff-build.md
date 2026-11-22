# Handoff — BUG-2295-handoff-one-per-phase, build → validate — written at a11ab09f, seq-2

## Next

Record T-01 at station `done` (`plan-merge.py set-task-station`), commit that as the seam commit, pin `review_sha` to it, run `gh-sync.py status <feature-dir> review`, then send ONE `validate` dispatch (`HARNESS-MISSION: validate`) to `harness-validator-lead` over that sha with inputs `feat=BUG-2295-handoff-one-per-phase` and `review_sha`. The readers grade T-01 (SC-01..SC-04); `qa` is gate-only and needs the red-first evidence at `notes/red-first-T-01.md`; SC-03/SC-04 are pinned inspections of `gh-sync.py` `cmd_ship`. T-01 is `execution_mode: main-session-direct`, so any `must_fix` returns to the main session, never to an engineering lead.

## Trust

- T-01 built main-session-direct — `git diff --stat dd04e52a a11ab09f` outside the feature dir touches exactly the three `files:` of T-01 — verified-at a11ab09f
- Red-first: 6 refusal assertions failed against base dd04e52a with check-domain.py untouched (build-c1, validate-c12, plan-c305 via Write and Edit), then 96 ok — `notes/red-first-T-01.md` — UNVERIFIED (main-session claim; qa re-runs the gate at the pin)
- SIMPLIFY pass ran, four angles, one simplification applied (regex captures the canonical stem) and suites re-ran green — `notes/simplify-pass.md`, `git show --stat a11ab09f` touches check-domain.py only — verified-at a11ab09f (note), UNVERIFIED (re-run claim)
- cmd_ship predicate and exemption call byte-identical, only the comment changed — `git diff dd04e52a a11ab09f -- .claude/skills/harness/bin/gh-sync.py` — UNVERIFIED (main-session claim; code reviewer grades SC-03/SC-04 at the pin)
- Operator signature: rework ruling 1 round / 45 min, T-01 main-session-direct — `notes/answers-2026-11-22-signoff.md`, `feature.json` `rework`, `BRIEF.md` `## Approval`, `plan.yaml` `approval.status` — verified-at a11ab09f

## Dead ends

- Do not route a T-01 fix to `harness-eng-lead`: every T-01 surface is main-session-direct under DEC-174 — `plan.yaml` `lanes.rows`, `BRIEF.md` `## Constraints` — verified-at a11ab09f
- Do not pass `outputSchema`/`schemaMode` on any dispatch this session: the live hook predates the BUG-2305 fix — dispatch assignment text — source: main session
- Do not treat null typecheck/component/ui runners as a qa gap: integration is the one required kind for these Python files — `BRIEF.md` `## Verification gaps` — verified-at a11ab09f
- Do not key ship on recorded validate runs or touch shipped cycle-suffixed notes: DEC-252 and T-01 `intent` exclude both — `plan.yaml` T-01 `intent` — verified-at a11ab09f

## Working set

- .harness/harness/features/BUG-2295-handoff-one-per-phase/plan.yaml
- .harness/harness/features/BUG-2295-handoff-one-per-phase/BRIEF.md
- .harness/harness/features/BUG-2295-handoff-one-per-phase/notes/red-first-T-01.md
- .claude/skills/harness/bin/check-domain.py
- tests/integration/test-check-domain-post.py

## Done when

Scope: validate run over the pinned seam commit returns a clean panel
Authority: brief-perspective:.harness/harness/features/BUG-2295-handoff-one-per-phase/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2295-handoff-one-per-phase/BRIEF.md#code maintainer
Authority: plan-task:T-01.verify
