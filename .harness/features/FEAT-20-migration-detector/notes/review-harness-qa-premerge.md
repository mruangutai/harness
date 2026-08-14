# Pre-merge measurement pass — FEAT-20-migration-detector — `045dcd9`

**PASS.** `045dcd9` is confirmed the branch tip. The `ea476fd..045dcd9` delta touches zero of the 8
reviewable source files — bookkeeping only (Expertise close-out writes, feature notes, one log, one
map hand-off). `main` has not moved past the pinned base `88b1182`, so there is no merge to measure.
Both required kinds (unit, integration) were re-executed independently at `045dcd9` in a throwaway
worktree, exit 0, and the new test files are confirmed registered and run — not a silent pass.

## M1 — tip confirmation

```
git rev-parse feat/FEAT-20-migration-detector  → 045dcd988aedb1b58e84b85df38bcc7c392638cf
git rev-parse 045dcd9                          → 045dcd988aedb1b58e84b85df38bcc7c392638cf
```
**Confirmed, locally.** Also confirmed against the remote, since a local clone's refs are not
necessarily current: `git ls-remote origin main feat/FEAT-20-migration-detector` returns branch tip
`045dcd988aedb1b58e84b85df38bcc7c392638cf` — matches exactly. `045dcd9` is the exact branch tip on
GitHub, not an ancestor and not stale locally.

## M2 — the unreviewed delta

`git diff --name-status ea476fd..045dcd9` (26 files) and `git log --oneline ea476fd..045dcd9` (10
commits — session log, map hand-off, handoff supersede, state closes, ship review, close-out
distillation, operator ruling x2, panel commit, orchestrator observations).

None of the 8 reviewable source files (`layout_migration.py`, `test-layout-migration.py`,
`check-state.sh`, `test-check-state.py`, `run-unit-tests.sh`, `tests.yml`, `DECISIONS.md`,
`DECISIONS-INDEX.md`) appear in the delta. Every changed path is one of:
- 12 `.harness/expertise/*.md` — the close-out distillation writes (matches
  `072be78 close-out: twelve Expertise files sharpened`)
- `.harness/features/FEAT-20-migration-detector/{STATE.md,feature.json,notes/*,observations/*}` —
  feature bookkeeping (answers, handoff supersede, distillation receipts, review-panel notes, ship
  review in both `.md` and `.html`, UAT goalcheck)
- `.harness/logs/2026-08-14.md`, `.harness/notes/map-336-phase1-handoff-2026-08-14.md` — session log
  and an unrelated map hand-off artifact, both outside this feature's directory but neither touching
  source

**No hunks to show** — zero source files changed, so there is no unreviewed code delta. The panel's
review at `ea476fd` remains current on the code itself.

## M3 — surface still 8 files (against base `88b1182`)

`git diff --name-only 88b1182..045dcd9`, filtered outside
`.harness/features/FEAT-20-migration-detector/`, returns exactly:
- the 8 named source files (unchanged set, confirmed present)
- 12 `.harness/expertise/*.md` (close-out distillation — expected, not a ninth *source* file)
- `.harness/logs/2026-08-14.md`, `.harness/notes/map-336-phase1-handoff-2026-08-14.md`,
  `.harness/notes/research-FEAT-20-migration-detector.md` (session/research bookkeeping)

**No ninth source file.** Everything beyond the 8 is Expertise/notes/logs — the same category the
prior panel already classified as bookkeeping, not code under review.

## M4 — base drift

```
git rev-parse main       → 88b1182644616d37c19e2708f3585277eccb5c94
git log --oneline -5 main → 88b1182 (HEAD), cf3af8f, 514aacd, 63b83c7, 3e23907
```

`main` is **identical to the pinned base** `88b1182` — it has not moved, locally. Also confirmed
against the remote (not just the local clone, which is not guaranteed current): `git ls-remote
origin main feat/FEAT-20-migration-detector` returns `88b1182644616d37c19e2708f3585277eccb5c94` for
`refs/heads/main` — identical. This is the measurement itself, not an inference: (a)-(d) are all
**not applicable by construction** — there is no `main` delta to intersect against the 8 files, no
merge to attempt with `merge-tree`, no DEC-194 collision to check, and no merged-result test run to
distinguish from the branch-tip run already done in M5. This is a point-in-time measurement, not a
standing guarantee — if `main` advances between now and the actual merge, M4 must be re-run before
that merge is trusted.

## M5 — matrix re-run at `045dcd9`

Isolated worktree: `git worktree add .../qa-feat20-premerge 045dcd9`, removed after with
`git worktree remove --force`, verified gone via `git worktree list` (not readback of file content —
the worktree entry itself is absent post-removal).

- **unit** — `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`. Exit 0.
  `PASS test-layout-migration.py` with all 18 named cases (1–18) present and asserting content
  (exit code + named surface/reader/tag), matching the case set already anchored to SC-01..SC-15 in
  the earlier gate note. State: **satisfied**.
- **integration** — `.claude/skills/harness/bin/run-unit-tests.sh --kind integration`. Exit 0.
  `PASS test-check-state.py`, with all five INV-27 cases present and passing: (x.1) mixed → names
  reader+tag+remedy, (x.2) unjudgeable → CANNOT VERIFY, (x.3) applicable clean → no INV-27 line,
  (x.4) no marker → no INV-27 line, (x.5) unimportable module → CANNOT RUN, exit 1. State:
  **satisfied**.

**Registration confirmed, not assumed:** both `PASS test-layout-migration.py` and
`PASS test-check-state.py` literal marker lines appear in the captured stdout of their respective
`--kind` invocations — the new test files ran as part of the standing suite, not merely present on
disk with the runner silently skipping them (this feature's own subject, per the dispatch).

**Shell note (same substitution as the prior gate, `review-harness-qa-c0.md`):** the write-guard
blocks redirects to scratchpad paths for this persona (`BLOCKED — redirect targets "..." outside
your domain`), so both commands were run directly with stdout captured from the tool result rather
than piped to a temp file. Semantically identical; only the capture mechanism differs. Filed again
here since it recurred verbatim on this pass, not because it is new.

## Non-findings

- `check-domain.sh --post` OVER BUDGET noise on worktree creation, about `FEAT-02` and
  `FEAT-05-pyyaml-file-parsers` STATE.md shape — pre-existing, unrelated to this diff, already ruled
  a non-finding in `review-harness-qa-c0.md`. Not re-filed.
- A second, unrelated worktree (`.../scratchpad/pr376`, detached at `045dcd9`) was present before and
  after this run — not created by me, not touched, not removed (out of scope: I only manage
  worktrees I create).
- Working tree at the main checkout shows unrelated pre-existing dirt (`.harness/members/backend-dev/
  FEAT-02-t01.md`, `-t02.md` deleted; a concurrent `review-harness-security-reviewer-premerge.md`
  appearing mid-session) — neither caused by nor cleaned by this QA pass; a parallel premerge review
  is evidently running concurrently.

## Coverage gaps

None beyond what the `ea476fd` panel already recorded (unpinned-against-regression, R-1/R-2; no
migrated-real-root fixture — both pre-briefed and not reopened here). This pass adds no new gap: it
measures that the already-reviewed code did not move and that the matrix stays green at the actual
merge candidate.

## Digest self-check

`sc_evidence: []` is deliberate — this pass adds no new SC evidence beyond `review-harness-qa-c0.md`'s
existing table, which stays the citable source. Ran `bin/validate-digest.py qa` directly against
this note's fenced block to confirm the empty list is accepted alongside `VERDICT: PASS`: result
`digest ok`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "045dcd9 is the confirmed branch tip; ea476fd..045dcd9 touches zero of the 8 reviewable source files (bookkeeping only); main has not moved past the pinned base 88b1182 so there is no merge to measure; unit+integration re-ran green and registered at 045dcd9 in a throwaway worktree."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 18 }
    - { kind: integration, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 5 }
  coverage_gaps: []
  sc_evidence: []
  open_questions:
    - { id: Q1, question: "This pass measured both local and remote (git ls-remote origin) main at 88b1182 (identical to base) — M4(a)-(d) are point-in-time not-applicable, confirmed against GitHub not just the local clone. If main advances before the actual merge lands, M4 needs re-measurement (name collision in DECISIONS.md, merge-tree conflict, and a merged-result test run) before that merge is trusted.", blocking: false }
  files_touched:
    - .harness/features/FEAT-20-migration-detector/notes/review-harness-qa-premerge.md
  expertise_update: []
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-qa-premerge.md
```
