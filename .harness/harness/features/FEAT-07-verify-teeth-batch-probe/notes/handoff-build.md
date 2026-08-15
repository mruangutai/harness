# Handoff — FEAT-07-verify-teeth-batch-probe, build → validate — written at 29b612e, seq-1

## Next

Dispatch validator-lead against `review_sha: 29b612e` for the ONE blocking gate: `qa`
(`harness.json` `gates.qa_gate: blocking`). `security` and `ui` self-scope out of this diff — a
YAML digest validator plus nine markdown files, zero end-user surface, no DESIGN.md — so they are
recorded skips, not runs. `code` is advisory (`advisory_unless_high`) and is the open call: DEC-174
keeps the review panel self-hosted, so it is permitted, and T-01 is the one file no member has read.
Whatever it returns, it does NOT discharge DEC-174's human-reads-the-diff control; say so wherever
its verdict appears. qa needs PLAN's ten `change_type:` values — one `logic` (T-01, 19 new fixtures)
and nine `docs` — because `test_matrix` maps `logic` to `[unit]` and `docs` to `[]`, so
`matrix_ok: true` is the correct outcome and qa has no source access to derive it. Then pm's
goal-check on all 18 SCs, then the briefing. Ship-refresh is a SKIP: `.harness/codebase/` does not
exist.

## Trust

- All ten tasks are committed, `0a34989`..`29b612e`, and I re-ran EVERY task's `verify:` clause at
  my own tier rather than routing on the reports — all green — verified-at 29b612e
- `run-unit-tests.sh` exit 0 and `check-docs.sh` exit 0 over 180 files — I ran both — verified-at 29b612e
- SC-11 holds by inspection: `git log main..HEAD` over the validator and its fixtures returns
  exactly ONE commit, `d6fa0a8`, containing both files — verified-at 29b612e
- DEC-175's nine `validate-digest.py` line anchors all resolve correctly, and the file was NOT
  edited after they were written — verified-at 29b612e
- The main session probe-edited `validate-digest.py` to prove the joint-hint fixture discriminates,
  then restored it; the eight anchors I sampled are byte-correct — verified-at 29b612e
- SC-12's receipt half CANNOT be met as written: `harness-documentor` holds no `notes/receipt-*`
  grant (`team-config.yaml:144,158,171,184,199` — the five dev specialists only). Substance is
  recorded instead: precondition exit 0, index clean, nothing absorbed — verified-at 29b612e
- Cost 426.66 of 550 and the remaining steps will likely cross it. Informational under DEC-134 —
  UNVERIFIED as a forecast, measured only as the running total

## Dead ends

- Do not re-open D-07 or re-suggest `no-task`. Rejected by the user with the reason recorded —
  `notes/answers-amf-fix-product.md` — verified-at 4091b36
- Do not edit `validate-digest.py` again. DEC-175's committed anchors point into it — `git log`
  over that path returns one commit — verified-at 29b612e
- Do not treat an agent code-review PASS as satisfying DEC-174. Its control is a human reading the
  diff — `docs/harness/DECISIONS.md` DEC-174 ruling paragraph — verified-at 29b612e
- Do not re-run `security` or `ui` reviewers on this diff. No auth, secrets, input or UI surface;
  O-01's rationale — `git diff --stat main..HEAD`, 13 files — verified-at 29b612e
- Do not fix the documentor receipt grant or pm's (#46). Out of scope by the user's ruling —
  `notes/answers-amf-fix-product.md` Q4 — verified-at 4091b36

## Working set

- .harness/features/FEAT-07-verify-teeth-batch-probe/feature.yaml
- .harness/features/FEAT-07-verify-teeth-batch-probe/BRIEF.md
- .harness/features/FEAT-07-verify-teeth-batch-probe/PLAN.md
- .claude/skills/harness/teams/review.yaml
- .harness/harness.json
