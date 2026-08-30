# QA re-verification — FEAT-38 — pin 48bbe7e (repin over T-14/T-22/T-23)

**VERDICT: PASS.** Delta re-derived independently (dispatch's claimed file set was materially
incomplete — see §0). Both new files' checkers still discover a known-positive; delta is `docs`
per the matrix (no required kind), matches plan.yaml's own labels; full/unit/integration suites are
0 FAIL, exit 0; index is fresh; no surviving `am.N` citations; every id T-14 repointed to resolves to
a live heading.

## 0. Delta re-derivation — dispatch's claim was wrong

`git diff --stat 2557950 48bbe7e`: **26 files, +1041/-77**, six commits
(46206de, 6d67b52, e88182c, c1d657b, 7cb69a9, 48bbe7e) — not four. The dispatch described only
e88182c/c1d657b/7cb69a9/48bbe7e's two new files and **omitted 46206de (review-pin) and 6d67b52
(ship-review) entirely**, which add `notes/research-FEAT-38-goalcheck-2557950.md`,
`notes/review-harness-code-reviewer-c1.md`, `notes/review-harness-security-reviewer-c1.md`,
`notes/ship-review-2026-08-29-16.{md,html}`, `notes/handoff-ship.md`, plus `STATE.md`/`feature.json`
churn. **No file outside `.harness/harness/features/FEAT-38-*` and the 13 T-14 doc/config surfaces is
touched** — confirmed by grepping the diff's name-list for `\.py$|/bin/`: zero hits. No source,
checker, or test file is in the delta. Proceeding on this re-derived set, not the dispatch's.

## 1. Change-type classification vs `harness.json` and plan.yaml

T-14 touches `.claude/**` markdown + `.gitignore` + `.harness/factory/fleet.yaml` (docs/config);
T-22/T-23 touch only feature-local `notes/`/`plan.yaml` (docs). plan.yaml declares
`change_type: docs` for **all three** (T-14 line 1051, T-22 line 1487, T-23 line 1547) — matches my
own reading exactly, no mismatch.

| kind | required? | state | cmd |
|---|---|---|---|
| unit | no (`docs.always: []`, `config.always: []`) | n/a — not required | — |
| integration | no | n/a — not required | — |
| functional | no | not_applicable, `status: excluded`, DEC-187 | null |
| component/ui/eval | no | not_applicable (unresolved, not required) | null |

**No REQUIRED kind is unmet** — the matrix floor for this delta is empty. `matrix_ok: true`.

## 2. Unit suite (isolated, no concurrent jobs)

Full run: `EXIT=0 FAIL=0 PASS=1002 KIND-DRIFT=0`. `--kind unit`: `EXIT=0 FAIL=0 PASS=417` (identical
to the 2557950 baseline). `--kind integration`: `EXIT=0 FAIL=0 PASS=585`. **417+585=1002, matches the
full run exactly — no bucket drift.**

Baseline was 1117 total (417+700); integration's raw PASS-line count fell 700→585. Investigated
per-script: all **29** `INTEGRATION_SCRIPTS` entries (and all 27 `UNIT_SCRIPTS`) produced exactly one
runner-emitted `PASS <script>.py` marker apiece, **0 `FAIL` anywhere, 0 scripts missing**. The
raw total mixes the runner's one-line-per-script marker with each script's own free-form
`PASS`/`ok -` sub-case convention (repo Expertise G-04: this total is not a reliable cross-run
test-case count). Since script-level pass/fail is identical to baseline and the delta touches no
test or source file, the drop is internal sub-case volume, not lost coverage — reported as a finding,
not a gate blocker.

## 3. The two feature-installed checkers, at the pin

- `check-decision-anchors.py`: `EXIT=0`, `examined 20 anchor(s), 0 failed`.
- `check-decision-claims.py`: `EXIT=0`, `examined 11 claim(s), 0 failed`.
- **Known-positive probe** (`git show 7ebfc9e:.harness/harness/docs/DECISIONS.md` → anchor checker
  `--file`): `EXIT=1`, `examined 32 anchor(s), 3 failed` (the same three `feature.yaml` anchors the
  prior gate recorded). **Exact match to the prior gate's baseline — the checker still discovers,
  not blind.**

## 4. Index freshness

`gen-decisions-index.py --stdout` diffed against committed `DECISIONS-INDEX.md`: **0 differing
lines, diff exit 0**. `git status --porcelain` confirmed clean before and after (no file left
dirty by the probe).

## 5. T-14 correctness — surviving stale citations, and target-id existence

`git grep -nE 'DEC-[0-9]+am\.[0-9]+|DEC-[0-9]+\.am'` over tracked files (excluding worktrees and
feature notes): **0 hits.** T-14's own diff repoints citations to five distinct new ids:
DEC-120, DEC-138, DEC-171, DEC-145, DEC-191 (one occurrence, `DEC-19`, was a plain deletion of a
dangling amendment reference, not a repoint). All five confirmed as live `## DEC-N —` headings in
`.harness/harness/docs/DECISIONS.md` at the pin (lines 2226, 2925, 4101, 3201, 5257 respectively).
No repoint targets a nonexistent decision.

## 6. Test-first compliance

**Does not apply, and that is stated plainly, not swept as a vacuous pass.** T-14/T-22/T-23 are
docs/record tasks with zero production logic in their diff (§0/§1) — 18 one-line citation edits, a
new read-back note, and a plan status flip. There is no behavioral change for a test to precede.

## Nothing committed

Only the checker/index probes above touched the working tree, and `git status --porcelain` was
confirmed clean before and after each. This artifact is the only tracked-tree addition.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Delta re-derived independently (dispatch's claimed file set was incomplete); docs-only, no required kind unmet, both checkers discover, index fresh, no stale citations, all 5 repointed ids live."
  suite: pass
  suite_full: { exit: 0, fail: 0, pass: 1002, kind_drift: 0 }
  suite_unit: { exit: 0, fail: 0, pass: 417 }
  suite_integration: { exit: 0, fail: 0, pass: 585 }
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, required: false, state: not_applicable, cmd: none }
    - { kind: integration, required: false, state: not_applicable, cmd: none }
    - { kind: functional, required: false, state: not_applicable, signed: DEC-187 }
    - { kind: component, required: false, state: not_applicable, cmd: null }
    - { kind: ui, required: false, state: not_applicable, cmd: null }
    - { kind: eval, required: false, state: not_applicable, cmd: null }
  coverage_gaps: []
  sc_evidence: []
  cycles_used: 0
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/qa-2026-08-29-11-validator.md
```
