# Handoff — FEAT-2557, build → validate — written at 94d1755e, seq-3

## Next

Pin `review_sha` to the seam commit that carries this note, run `gh-sync.py status review`, then
send ONE `validate` dispatch to `harness-validator-lead` over that sha (run-start `--squad
validator`). `change_type: docs` requires no test kind, so qa gates the matrix as not-applicable,
and every SC is `verify: inspection`, graded on `git show <review_sha>:<path>`.

## Trust

- T-01 is built and its signed verify exits 0, printing `LAYOUT-SKILL-AGENTS-DEC-OK` — `notes/receipt-main-session-T-01.md` — verified-at 94d1755e
- The feature diff from main is exactly the five T-01 files plus this feature's directory — the T-01 verify's terminal scope check — verified-at 94d1755e
- DEC-259 was free in all 8 worktrees and on every remote branch at signature — `notes/answers-2026-11-27-signoff.md` — verified-at ce74dbff
- T-01's station is done in plan.yaml — `plan.yaml` T-01 status — verified-at 94d1755e
- Every agent's preload stays under 5500 words; eng-lead is at 5178 — `check-skill-weight.py` — verified-at 94d1755e
- The SIMPLIFY pass returned no findings on all four angles — `notes/simplify-pass.md` — verified-at 94d1755e
- Dropped cards #2559 and #2561 are closed not planned and gone from the github block; the missing verb is #2562 — `feature.json` github — verified-at ef69b397

## Dead ends

- The skill's review bullet first wrapped "prefixed siblings" across a line break, and the line-wise verify grep missed it; it is rewrapped onto one line — `.claude/skills/harness-codebase-design/SKILL.md` Applying it — verified-at 94d1755e
- The first DEC-259 index ruling ran to 32 words, over the 30-word cap that `test-gen-decisions-index.py` enforces; it is shortened — `.harness/harness/docs/DECISIONS-INDEX.md` DEC-259 row — verified-at 94d1755e

## Working set

- `.harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md`
- `.harness/harness/features/FEAT-2557-code-layout-pattern/plan.yaml`
- `.claude/skills/harness-codebase-design/SKILL.md`
- `.claude/skills/harness/bin/LAYOUT.md`
- `AGENTS.md`
- `.harness/harness/docs/DECISIONS.md` (DEC-259)
- `.harness/harness/docs/DECISIONS-INDEX.md`

## Done when

Scope: validate over the pinned review_sha
Authority: brief-perspective:.harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md#code maintainer
Authority: brief-perspective:.harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md#reader (eng-lead architecture review / code-reviewer)
Authority: brief-perspective:.harness/harness/features/FEAT-2557-code-layout-pattern/BRIEF.md#operator
Authority: plan-task:T-01.verify
