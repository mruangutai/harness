# Handoff — FEAT-38-decisions-current-knowledge, plan → build — written at 7ebfc9e, seq-1

## Next

**Do not dispatch anything.** The plan phase ends at a user gate and the gate is unsigned:
`BRIEF.md:224` and `plan.yaml:7` both read `status: pending`. The main session presents `BRIEF.md`,
takes the operator's answer on Q1 (the 2026-08-26 widening — 15 deletions and DEC-188's retention
clause struck), writes `approval:` in both artifacts, and moves the board to `Ready`. Only then does
the build phase open, at `plan.yaml` `T-01` — a `harness-documentor` task — dispatched to
`harness-eng-lead` as the eng segment, with `notes/reconciliation-plan.md` passed as an input path.

## Trust

- BRIEF.md and plan.yaml exist and are approval-pending — `BRIEF.md:222-226`, `plan.yaml:6-9` — verified-at 7ebfc9e
- plan.yaml parses; 23 tasks, 12 decisions, 20 `team` / 3 `main-session-direct` — `yaml.safe_load` over `plan.yaml` — verified-at 7ebfc9e
- Plan-route gate is green: 0 violations, exit 0; two advisory DEVIATIONs on T-22/T-23, which declare `main-session-direct` for a path granted to `harness-orchestrator` — `check-plan-routes.py plan.yaml` — verified-at 7ebfc9e
- The intake is stale and `notes/reconciliation-plan.md` governs: 7,414 lines / 202 entries, 38 amendments, DEC-19 repoints to DEC-85 (not DEC-84), 29 live citations (not 13) — `notes/reconciliation-plan.md` §1 — verified-at 7ebfc9e
- `.agents/skills` is a tracked symlink (mode 120000 → `../.claude/skills`); canonical paths are `.claude/skills/…` — `git ls-files -s .agents/skills` — verified-at 7ebfc9e
- Thirteen edit surfaces resolve to NOBODY and are carved into one `main-session-direct` task, T-14 — `check-domain.sh --resolve` per path; `check-plan-routes.py` T-14 line — verified-at 7ebfc9e
- pm's claim that four DEC-138 amendments sit inside DEC-168's span is true, and understated: six sub-sections are misfiled (DEC-137 in DEC-138 at :3286; DEC-138 ×4 in DEC-168 at :4383/:4410/:4438/:4517; DEC-189 in DEC-194 at :6401) — re-derived by heading-span scan — verified-at 7ebfc9e
- The run-1 blocker is cleared: `.harness/.inflight-claims.json` in the MAIN checkout holds zero claims — read at 1788013249 — verified-at 7ebfc9e
- SC-04's "37, 30 and 24 occurrences" uses a narrower frozen-set predicate than the reconciliation's 29 (pm also excludes `.harness/logs/**`). Both are internally consistent; neither was reconciled against the other — UNVERIFIED

## Dead ends

- Do not re-read `STATE.md`'s old open questions — the orphaned `harness-pm` claim and the 2-commits-behind base are both resolved; superseded by this file — verified-at 7ebfc9e
- Do not spawn `harness-visual-designer`: no end-user interaction surface, prototype gate not fired — product-lead digest Q4 — source: lead's tier decision, operator-overridable
- Do not pull #686 in beyond its one clause, and do not pull in #844/#748/#678/#687/#438/#680/#803/#486 — `BRIEF.md` "Two backlog tickets, ruled on rather than left open" — verified-at 7ebfc9e
- Do not anchor a build task on a line number from the grilling or the triage: DEC-188's clause moved :5942→:5949, DEC-181 :5409→:5416, DEC-186 :5673→:5678 — `notes/reconciliation-plan.md` §4 — verified-at 7ebfc9e

## Working set

- `.harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/BRIEF.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/reconciliation-plan.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/STATE.md`
- `.harness/notes/triage-decisions-authority-2026-08-26.md` (main checkout only)
