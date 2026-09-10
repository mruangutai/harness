# Handoff — FEAT-104-strict-digest-schema, validate → validate (re-panel) — written at f08aad49, seq-5

## Next

Wait for the main session's NEW `review_sha` — it is landing F1, F2 and SC-08/F3 itself under the
DEC-174 carve-out — then dispatch `harness-validator-lead` with the `review` team
(`/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/teams/review.yaml`) at that pin,
`cycle: 8`, run dir `runs/2026-09-09-05-panel-validator/`, handing it
`runs/2026-09-09-04-panel-validator/digest.md` as the prior set so it re-grades F1–F3 rather than
rediscovering them. Increment `cycles_used` to 8 when that run is dispatched: it is rework. Only
after it returns clean do the product goal-check (SC-01..SC-16, SC-14 struck), the SC-13 UAT
generation and the briefing — all three are still owed and none has been done.

## Trust

- F1 is real and DEMONSTRATED, not inferred: the 2→1 `schema_version` update write exits 0
  (accepted) where the case expects 2 — `python3 tests/integration/test-check-domain.py`, case
  `schema_version floor refuses a version-2 checkpoint downgrade`, 11/12 — verified-at f08aad49
- The witness is not a fixture artifact: the version-1 update case sharing the same `_existing_write`
  helper passes and all four creation cases refuse correctly — same run — verified-at f08aad49
- 6126ac07 contains every code change under review; tip f08aad49 changes only `feature.json`'s
  `review_sha` — `git diff --stat 6126ac07 f08aad49` — verified-at f08aad49
- `code_grade` PASS at the pin: `code-grade.py --base abff2a84 --head 6126ac07` exits 0, 42 changed
  functions, no gated row — measured here and independently by `code` — verified-at 6126ac07
- `matrix_ok: true` from qa's own re-run at the pin, unit and integration by exit status, eight
  null-`cmd` kinds `not_applicable` — `notes/review-harness-qa-c7.md` — verified-at 6126ac07
- `tests/integration/test-check-domain.py` is uncommitted-modified and is the MAIN SESSION's
  test-first red case for F1, confirmed by Main over IRC; not committed here —
  `git status --porcelain` — verified-at f08aad49
- SC-13 is `verify: uat` and gates — `BRIEF.md` SC-13, `.harness/harness.json:376` —
  verified-at f08aad49

## Dead ends

- Do not route F1, F2 or F3 to any lead as a fix cycle: all three remedies edit `check-domain.sh`,
  `check-state.sh` or `validate-digest.py`, DEC-174 surfaces no team may touch, so the cycle would
  be spent proving that — `runs/2026-09-09-04-panel-validator/digest.md` F1–F3 — verified-at f08aad49
- Do not re-derive F1 from source reads: two independent reads agree and the execution witness above
  settles it — same digest, `adequacy_notes` — verified-at f08aad49
- Do not treat F5 or F6 as gates: F5 is what the signed plan's T-03 required, so reversing it is a
  plan change; F6 is a `change_type` note with coverage present regardless — same digest,
  dismissals — verified-at f08aad49
- Do not read `check-state.sh`'s exit 1 here as a FEAT-104 defect: all five violations are other
  features' standing INV-29 worktrees — `check-state.sh` run here — verified-at f08aad49

## Working set

- `.harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-09-04-panel-validator/digest.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-security-reviewer-c7.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/BRIEF.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/feature.json`
- `.claude/skills/harness/bin/check-domain.sh`

## Done when

Scope: the reviewer panel has re-run at the main session's new pin and re-graded F1–F3
Authority: brief-sc:SC-03
Authority: brief-sc:SC-15
Authority: brief-sc:SC-13
