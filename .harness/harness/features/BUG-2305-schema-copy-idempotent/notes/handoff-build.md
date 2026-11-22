# Handoff — BUG-2305-schema-copy-idempotent, build → validate — written at 9c39f18a, seq-2

## Next

Pin `review_sha` to the seam commit that records T-01 at station `done`, run `gh-sync.py status <feature-dir> review`, then send ONE `validate` dispatch (`HARNESS-MISSION: validate`) to `harness-validator-lead` over that sha with inputs `feat=BUG-2305-schema-copy-idempotent` and `review_sha`. The readers grade T-01 (SC-01..SC-04); `qa` is gate-only and needs the red-first evidence at `notes/red-first-T-01.md`. T-01 is `execution_mode: main-session-direct`, so any `must_fix` returns to the main session, never to an engineering lead.

## Trust

- T-01 built main-session-direct, hook + test + DEC-237 amend + regenerated index — `git diff --stat 7f9cc9d8 9c39f18a` touches exactly the four `files:` of T-01 — verified-at 9c39f18a
- Red-first: 5 assertion failures against base 7f9cc9d8 with the hook untouched, then 164/164 green — `notes/red-first-T-01.md` — UNVERIFIED (main-session claim; qa re-runs the gate at the pin)
- SIMPLIFY pass ran, four angles, no findings, no code change (9c39f18a differs from d178ef3a only under the feature dir) — `notes/simplify-pass.md` — verified-at 9c39f18a
- Operator signature: rework ruling 1 round / 45 min; Q-01 index regeneration authorized — `notes/answers-2026-11-22-signoff.md`, `feature.json` `rework` — verified-at 9c39f18a
- Typecheck did not run: `harness.json` `typecheck.cmd` is null (#2257) — `BRIEF.md` `## Verification gaps` — verified-at 9c39f18a

## Dead ends

- Do not route a T-01 fix to `harness-eng-lead`: the hook surface is NOBODY-owned and DEC-174 keeps it main-session-direct — `plan.yaml` `lanes.rows` — verified-at 9c39f18a
- Do not pass `outputSchema`/`schemaMode` on any dispatch this session: the live hook is the pre-fix version and refuses them — dispatch assignment text — source: main session
- Do not treat a `qa` typecheck gap as a finding: the runner is null and #2257 owns it — `BRIEF.md` `## Verification gaps` — verified-at 9c39f18a

## Working set

- .harness/harness/features/BUG-2305-schema-copy-idempotent/plan.yaml
- .harness/harness/features/BUG-2305-schema-copy-idempotent/BRIEF.md
- .harness/harness/features/BUG-2305-schema-copy-idempotent/notes/red-first-T-01.md
- .omp/extensions/harness-hooks.ts
- tests/unit/omp-hooks.test.ts

## Done when

Scope: validate run over the pinned seam commit returns a clean panel
Authority: brief-perspective:.harness/harness/features/BUG-2305-schema-copy-idempotent/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/BUG-2305-schema-copy-idempotent/BRIEF.md#code maintainer
Authority: plan-task:T-01.verify
