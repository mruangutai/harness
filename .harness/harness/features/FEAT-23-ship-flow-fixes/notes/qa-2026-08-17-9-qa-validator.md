# QA gate — FEAT-23-ship-flow-fixes — pin 83e769b

## Verdict: PASS

Matrix floor (bugfix→unit, feature→unit+integration; docs→[]) is satisfied. Both required kinds
ran green at the pinned SHA. All three discriminating-coverage concerns raised in the dispatch were
checked against evidence (not code reading) and hold.

## HEAD / pin check

`git rev-parse --short HEAD` = `83e769b`, matches `review_sha`. Main checkout at
`/Users/molchairuangutai/GitHub/harness` (not a worktree — confirmed via `git worktree list`
showing only the main entry after cleanup).

## Phase 1 — expected coverage, derived from BRIEF.md + plan.yaml only, before reading source

- SC-01/SC-02: an integration-level test that stages a pre-terminal `feature.json`, runs `ship`/
  `abandon`, and asserts the recorded status reads `Done`/`Abandoned`.
- SC-03: existing gh-sync behaviours (milestone close, adopted-parent-stays-open, created-parent-
  closes, `--body-file` posts once) must still be exercised and green — regression coverage, not
  new cases.
- T-01's intent additionally demands: (a) the write is not milestone-gated on `cmd_abandon`'s
  conjunction — a fixture with no milestone but a recorded issue is the discriminating case; (b)
  the "every other key survives" assertion runs over a fully schema-populated fixture, or it is
  vacuous.
- SC-10: seven unit cases for `board-station.py` — success write, no-board, outside-harness-root,
  sync-off, BoardError-on-stderr, usage exit-2, and a non-`BoardError` exception path — plus proof
  that "writes nothing" means no `gh` call was logged, not just exit 0.
- SC-05 through SC-09, SC-11, SC-12: text/inspection checks on the skill and the two playbooks and
  the two new DECISIONS entries plus index regeneration.
- SC-04, SC-13: `uat`, not achievable at gate time — correctly deferred.

## Phase 2 — what's actually in the diff, and the gap against Phase 1

No gap. Every Phase-1 item has a named, present test, and the three discriminating-coverage
concerns the dispatch flagged were independently confirmed:

1. **T-01 bug-class fixture** — `test-gh-sync.py`, case
   `"abandon with no milestone but WITH issues still records status Abandoned"` (tmpE): stages
   `milestone: None`, `issues: {"T-01": 41}`, runs `abandon`, asserts `status == "Abandoned"`. This
   is exactly the conjunction-breaking shape the dispatch named — the fixture that would catch a
   regression re-gating the status write on the milestone. Present and passing.
2. **Key-survival fixture strength** — `_full_fixture()` in `test-gh-sync.py` stages all eight
   `feature-schema.json` top-level keys (`feature_id`, `branch`, `pr`, `status`, `review_sha`,
   `cycles_used`, `max_total_cycles`, `runs`) plus a `github` block (`milestone: 7`, `parent: 41`,
   `parent_origin: created`, `attached: ["T-01"]` as a list of strings, one recorded issue). The
   survival assertion (`ship leaves every other top-level key unchanged` /
   `abandon leaves every other top-level key unchanged`) quantifies over that real key set, not a
   two-key vacuous fixture. Confirmed by reading the fixture, not asserted from the label.
3. **T-05 silent-failure mutant** — proved live, not read. In a disposable worktree
   (`.claude/worktrees/qa-mutate-t05`, added and removed per DEC-153; restore verified with
   `git status --porcelain` after `git checkout --`), mutated `board-station.py`'s broad
   `except Exception as exc: err(...); return 0` to `except Exception: return 0` (silently
   swallowing a real board-write failure). Reran `test-board-station.py`: 2 of 8 cases failed —
   `"board-station reports a BoardError on stderr naming issue and station and exits 0"` and
   `"board-station exits 0 when set_station raises a non-BoardError exception"` — both went from
   `PASS` to `FAIL` (`rc=0 stderr=''`, expected an `ERROR -` line). The mutant is killed: a
   real-failure-into-silent-success regression on either exception path is caught. Tree restored;
   `git status --porcelain` on the main checkout confirms no source residue (see below).

## Matrix — kinds, commands, exact result lines

change_type distribution: 4 docs (T-02, T-03, T-04, T-06), 1 bugfix (T-01), 1 feature (T-05).
`docs.always: []`; `bugfix.always: ["unit"]`; `feature.always: ["unit", "integration"]`. **unit and
integration are both required; nothing else is.**

- **unit** — `satisfied`. `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`, exit 0.
  16 scripts, every one `PASS`, including `test-board-station.py` (8/8 `PASS`, T-05's own suite,
  routed here per `UNIT_SCRIPTS` registration in `run-unit-tests.sh`, matching the unit `detect`
  glob).
- **integration** — `satisfied`. `.claude/skills/harness/bin/run-unit-tests.sh --kind integration`,
  exit 0. 12 scripts, every one `PASS`, including `test-gh-sync.py` (T-01's own suite: run directly,
  103 `ok` lines, `ALL PASSED`, rc=0 — the two new labelled cases `ship records feature.json status
  Done` and `abandon records feature.json status Abandoned` both `ok`, plus the three pre-existing
  preserved cases `ship closes the milestone regardless of parent origin`,
  `ship leaves an adopted parent open`, and the `--body-file`-posts-once case all still `ok`).
- **component, ui, eval, typecheck** — `skipped`, not applicable. All four carry `cmd: null` /
  `status: unresolved` in `harness.json` (confirmed by reading the config directly) and none of
  their `detect` globs (`*.spec.tsx`, e2e paths, `evals/**`, `*.ts`/`*.tsx`) matches anything in this
  diff — no TS/TSX, no e2e, no `ai_behavior` change_type.
- **functional** — `skipped`, `status: excluded` under signed DEC-187 (repo has no service API; the
  unit/integration split already covers everything a third bucket would).

matrix_ok: **true**.

## SC evidence (automated ones)

- SC-01: `test-gh-sync.py::"ship records feature.json status Done"` (tmpS case)
- SC-02: `test-gh-sync.py::"abandon records feature.json status Abandoned"` (tmpT case)
- SC-03: `test-gh-sync.py::"ship closes the milestone regardless of parent origin"`,
  `"ship leaves an adopted parent open"`, `"ship closes a created parent completed"`,
  `"ship --body-file posts once"` (all pre-existing, all still `ok`)
- SC-10: `test-board-station.py`, all 8 cases (7 required + the field-set-argument-content case)
- SC-04, SC-13: correctly `not_met` / deferred to real-world UAT, per BRIEF's own "Verification
  gaps" section — not a gate finding, an acknowledged deferral.
- SC-05 through SC-09, SC-11, SC-12 (`verify: inspection`): confirmed by direct grep against the
  shipped files — angle headings, `plan surface`/`code surface` phrases, source-note citation,
  absence of `harness-validator-lead` and `code-simplifier` in the skill; playbook ordering anchors
  in `harness/SKILL.md` and `harness-plan.md`; `DEC-195`/`DEC-196` headings present in
  `DECISIONS.md` and `gen-decisions-index.py --stdout` diffs clean against `DECISIONS-INDEX.md`.

## Coverage gaps

None found against the Phase 1 list. The BRIEF's own "Verification gaps" section already names
everything structurally ungated (playbook-ordering prose, kickoff message wording, the real-board
write) as deliberate and out of this feature's scope — not re-litigated here.

## Bounds compliance

- Read-only on product source: confirmed. The only mutation made (the T-05 silent-failure probe)
  was applied and reverted entirely inside a disposable worktree
  (`.claude/worktrees/qa-mutate-t05`), created via `git worktree add ... 83e769b` and removed via
  `git worktree remove --force` after `git checkout --` restored the file and
  `git status --porcelain` on that path confirmed clean, before the worktree was removed.
- No `gh` calls made.
- No commits, no `git add`.
- Did not edit `plan.yaml`, `BRIEF.md`, `feature.json`, `STATE.md`, or any DEC-174 file.

## Test-first compliance (reasoned, not measured — read the receipts, did not re-derive)

Per `notes/research-FEAT-23-verify-red-runs.md`: T-01's two new gh-sync cases and its
key-survival case were red-run before the fix (28 pre-existing cases stayed `ok`; the two new
assertions reddened, gh-sync exiting 0 with status still `Review`) and inverted after. Per
`notes/research-FEAT-23-453-station.md` and `notes/research-FEAT-23-foldin-red-runs.md`: T-05's
seven `board-station.py` labels were proved red on a FAIL and on a silently deleted case, and the
registration/drift-detector conjunct was proved by mutation (exit 0 unmutated, exit 2
MISCONFIGURED with an unregistered file). One caveat carried from `STATE.md`, not independently
re-derived here: T-01's pre-edit RED is unattested *by the member* — its first spawn died on an
API error before writing evidence, and the resumed spawn declined to reconstruct a red line it
had not itself observed; the lead's own pre-dispatch measurement and the verify-red-runs note
carry the claim instead. Non-gating — recorded for completeness, not as a finding against this
gate.

## git status --porcelain (raw, main checkout, post-gate)

```
 M .harness/harness/features/FEAT-23-ship-flow-fixes/STATE.md
 M .harness/harness/features/FEAT-23-ship-flow-fixes/feature.json
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-premerge.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-qa-premerge.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-security-reviewer-premerge.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-code-reviewer-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-qa-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-security-reviewer-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/observations/harness-qa.md
?? .harness/harness/features/FEAT-21-features-layout-migration/observations/harness-validator-lead.md
?? .harness/harness/features/FEAT-23-ship-flow-fixes/notes/qa-2026-08-17-9-qa-validator.md
```

Re-run after writing this artifact, so the delta is measured, not asserted. The two modified files
(`STATE.md`, `feature.json` for FEAT-23) and every other untracked file pre-date this run —
confirmed by diffing them: both FEAT-23 files are the orchestrator's own in-flight run bookkeeping
(re-pinned `review_sha`, new run entry, updated `## Current`/`## Open Questions`), and I made no
`Write`/`Edit` call against either path. The only line this gate added is the last one — my own
artifact.
