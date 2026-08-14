# Handoff — FEAT-20-migration-detector, ship → operator gate — written at 1b7702b, seq-3

## Next

**Nothing to dispatch. The feature is complete and the only remaining act is the operator's.**
15 of 15 criteria met, both gates passed, close-out done, briefing written and rendered at
`notes/ship-review-2026-08-14.md`. Merge and ship acceptance are user-gated and no agent performs
either. On acceptance the **main session** — not an orchestrator — runs `gh-sync.py ship` (closes
milestone 11 and parent #360, posts the briefing) and `gh-sync.py backlog` for the unstruck rows.

If a fix cycle respawns an orchestrator here: read STATE.md `## Current` first, re-pin `review_sha`
at a commit containing the fix before any validator run, and do **not** re-run distillation — it is
once per feature and it is done.

## Trust

- 15/15 criteria met, each verified first-hand at the pin, not read from a receipt —
  `notes/uat-goalcheck-c0.md` — verified-at 434307a
- SC-10 ruled by the operator as the shipped surface; signed text stands. Recorded twice and
  consistently — `notes/answers-sc10-ruling.md`, `notes/answers-2026-08-14-2-product.md` —
  verified-at 1b7702b
- Blocking qa gate PASS and review panel PASS with `must_fix: []`, `severity_max: med` under
  `advisory_unless_high` — `runs/qa-gate-validator/digest.md`, `runs/2026-08-14-1-validator/digest.md`
  — verified-at ea476fd
- Close-out distillation: 38 ops over 12 files, net 269 → 293 entries, **no entry id lost**, measured
  against `8cd251a` which predates every distillation write; `check-expertise.sh` exits 0 over all 13
  files — commit `072be78` — verified-at 1b7702b
- The `2026-08-14-3-validator` run is recorded `BLOCKED` and that is honest, not a stuck feature: its
  work landed in full, and `validate-digest.py` binds `qa` to gate fields a distillation never runs,
  so a retry returns BLOCKED forever — briefing row **B-7** — verified-at 1b7702b
- `cycles_used` 4/10, `len(runs)` 10/20 and a floor — T-01/T-02 were main-session-direct —
  `feature.json` — verified-at 1b7702b
- The detector is live and non-vacuous: `features: CLEAN`, `docs: CLEAN`,
  `examined 20 feature dir(s), 1 doc root(s), 7 reader file(s)`, exit 0; zero renames across the
  feature — run directly — verified-at 1b7702b

## Dead ends

- Do not re-run ship-refresh. There is no `.harness/map/` and no `INDEX.md` anywhere, so no map can
  be stale — checked, not assumed — verified-at 1b7702b
- Do not re-open SC-10. The operator ruled it; a re-plan was offered and declined —
  `notes/answers-sc10-ruling.md` — verified-at 1b7702b
- Do not fix any backlog row inside FEAT-20. B-1 through B-11 are out of scope by the coordinator's
  explicit instruction — `notes/ship-review-2026-08-14.md` — verified-at 1b7702b
- Do not edit `.github/workflows/tests.yml:110-114`; pre-existing, byte-unchanged, owned by issue
  #279 — `git diff 88b1182..HEAD` shows zero deletions in that file — verified-at 1b7702b
- Never `git add -A`: two deleted `.harness/members/backend-dev/FEAT-02-*.md` and two untracked files
  under `.harness/logs/` and `.harness/notes/` predate this feature — `git status` — verified-at 1b7702b
- `verify:` clauses are not runnable verbatim — the write guard refuses redirects to a shell
  variable, so `>"$(mktemp)"` is blocked; use a literal path — verified-at 1b7702b

## Working set

- `.harness/features/FEAT-20-migration-detector/notes/ship-review-2026-08-14.md`
- `.harness/features/FEAT-20-migration-detector/STATE.md`
- `.harness/features/FEAT-20-migration-detector/feature.json`
- `.harness/features/FEAT-20-migration-detector/notes/uat-goalcheck-c0.md`
- `.harness/features/FEAT-20-migration-detector/notes/answers-sc10-ruling.md`
