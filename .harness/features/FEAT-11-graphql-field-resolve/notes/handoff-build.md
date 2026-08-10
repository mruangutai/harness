# Handoff — FEAT-11-graphql-field-resolve, build → validate — written at 2ea9af3, seq-4

<!-- Written at the seam, retrospectively within the same session: I ran build, validate and
     ship without stopping, and the invariant checker is right that the note is owed anyway.
     Recorded as retrospective rather than presented as contemporaneous. -->

## Next

Dispatch the `review` team to `harness-validator-lead`, pinned at `2ea9af3` — the MF-1 commit, not
`5c433f2` and never the plan-phase `835b297`. Both earlier pins predate the work. Pre-brief the four
known items (BRIEF `## Verification gaps`, `feature.yaml residuals.d03_partial_success`,
`feature.yaml mf1_correction`, `notes/qa-c0.md`) so the panel does not spend itself rediscovering
them. T-01 is the only PLAN task and it is built.

## Trust

- T-01's `verify:` block passes, exit 0 — re-run by me from the repo root against the plan's own
  scalar, not relayed — verified-at 2ea9af3
- Both required test kinds are green as the STANDING `test_kinds` commands, not as the task verify:
  unit 10/10 scripts, integration 12/12 — `notes/qa-c0.md` — verified-at 2ea9af3
- The three sha256 sentinels in T-01's verify recompute byte-identical, so the plan's Q4 is moot and
  no amendment is owed — recomputed by me — verified-at 8dedeae and unchanged since
- `factory_gh.py` is byte-identical to its post-T-01 state despite being mutated twice for the MF-1
  proof — empty `git diff --stat` run by me — verified-at 2ea9af3
- qa's MF-1 was HALF WRONG: only `:407` asserted vacuously, not `:428` — the org message carries
  "owned", never "owner" — `feature.yaml mf1_correction` — verified-at 2ea9af3
- The working tree is clean over `run-unit-tests.sh` and all four DEC-174 carve-out files, so
  FEAT-12 has landed nothing here — `git status --porcelain` — verified-at 2ea9af3

## Dead ends

- Do NOT route the D-03 partial-success finding as an eng fix cycle — its remedy contradicts a
  signed decision — `feature.yaml residuals.d03_partial_success` — verified-at 2ea9af3
- Do NOT ask qa to author a missing test in `bin/` — no grant matches
  `.claude/skills/harness/bin/test-*.py` — `team-config.yaml:217-218` — verified-at 2ea9af3
- Do NOT make any live `gh` call — board 6 and `harness-factory-smoke-a1` are retained fixtures
  whose item states an operator measurement depends on — source: the operator's signature ruling
- Do NOT edit `run-unit-tests.sh` — peer feature FEAT-12 owns it and it is T-01's verify command —
  `feature.yaml peer_feature_collision` — verified-at 2ea9af3

## Working set

- `.harness/features/FEAT-11-graphql-field-resolve/feature.yaml` (pins, rulings, residuals)
- `.harness/features/FEAT-11-graphql-field-resolve/notes/qa-c0.md` (the blocking gate's result)
- `.harness/features/FEAT-11-graphql-field-resolve/runs/t01-eng/digest.md`
- `.harness/features/FEAT-11-graphql-field-resolve/runs/mf1-eng/digest.md`
- `.harness/features/FEAT-11-graphql-field-resolve/BRIEF.md` (`## Verification gaps`)
