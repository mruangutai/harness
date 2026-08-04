# code review — FEAT-06 — cycle 0

**VERDICT: PASS.** Diffed `635ef14..9f87c48` (confirmed `git rev-parse HEAD == 9f87c48`, no
`[harness:human]` commits in range, 3 commits total: `f45fd0f` 8 tasks, `510b7ff` T-08, `9f87c48`
T-07). Stage 1 (spec compliance) and Stage 2 (code quality) both clean. No `must_fix`, no `high`+.

## Stage 1 — spec compliance

All 10 tasks trace to a `REQ`/`D` and match PLAN's specific values. Ran every task's `verify:`
myself (issue #19 means nobody else had):

- **T-01** (`check-state.sh:156-160`, `harness_yaml.py` `PLACEHOLDER_UNSET`, `validate-digest.py`):
  `run-unit-tests.sh` exit 0; `grep -rn '"none", "null", "n/a"' bin/` → 1; `PLACEHOLDER_UNSET` in
  both consumers; test-check-state.py cases (h)/(i)/(j) present, matching D-06's three-fixture spec
  exactly (value axis + precondition axis both covered).
- **T-02** (`review.yaml`): parsed step-id set `{code,qa,security,ui}`, `qa` step
  `mutates_repo: false`, `outputs` renamed to `review-harness-qa-c{{cycle}}.md` (not the segment's
  `qa-c{{cycle}}.md` — the collision T-02 exists to prevent). **Comment sweep (MF-1) re-verified**:
  `grep -ni 'three\|\b3\b\|four\|\b4\b' review.yaml` → every hit now says "four"/"4×", including the
  footer ("merge the four panels") and the header multiplier; line 4's stale ordinal ("a fourth
  dispatched step") was correctly reworded to "a separate dispatched step" rather than left wrong.
  **MF-1 is closed by this inspection** — but it remains asserted by nothing mechanically; a future
  edit could re-break it silently. Worth a note, not a re-open (`low`, not `must_fix`).
- **T-04** (`build.yaml`, born valid): parses, `steps_from` fields exact, `personas` superset of
  `{dev-ops, backend-dev}`. **Verified beyond the PLAN's own verify**: the rendered receipt path
  `receipt-harness-{{persona}}-{{task_id}}-c{{cycle}}.md` against all 5 declared personas —
  `team-config.yaml:144,158,171,184,199` grants `receipt-harness-<persona>-*.md` for all five
  (frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops). No persona's first dispatch would hit
  `check-domain.sh`'s exit-2 block — this was the one path that could have shipped a definition that
  looks complete and fails closed on first real use, and it doesn't.
- **T-05**: `test-harness-yaml-corpus.py` 12/12 including SC-06's broken-fixture-under-`teams/`
  case; `ls teams/ | wc -l` → 2.
- **T-06 + T-11 combined SKILL.md budget**: `git diff --numstat` → 14 added / 0 deleted, under the
  20-line cap (T-06 alone used 8 of 12, per `STATE.md`). `grep -c -i test_matrix` → 2. 8-line window
  containing `qa`+`validator`+`loop_back` → present (lines 45-52).
- **T-07**: `test-team-catalog.py` runs 10/10 ok, `run-unit-tests.sh` exit 0 with it registered.
- **T-08**: `check-docs.sh` exit 0 (45 patterns, 0 stale); SPEC §13 `build` row present, not ★;
  ship-feature panel widened to `{code ∥ qa ∥ security ∥ ui}` matching the review row; `gate-probe`
  DECISIONS.md entry amended, not deleted. Dispatched via `harness-documentor`
  (`runs/t08-product/state.yaml`: `squad: product`, gitignored, not part of the diff — correctly
  outside review scope).
- **T-09**: `harness-team/SKILL.md` +12 lines (cap 14), all four required tokens present.
- **T-10**: `gate-probe.yaml` deleted; `grep -rn gate-probe .claude/` → 0.

**Full unit suite**: `run-unit-tests.sh` exit 0, matches qa's 13(+1)/281 count.

### SC-03 (inspection, mine)

Re-ran `check-state.sh` on the real tree; diffed against `notes/before-check-state-635ef14.txt`.
**One delta**: `FEAT-06…: run dir panel-validator exists on disk but feature.yaml does not record
it — orphaned work`. This is my own review dispatch's run dir (this review's own `runs/`), created
after `9f87c48` — **not scored against the diff**, per the dispatch's explicit instruction. No INV-6
line anywhere; confirmed at the reviewed SHA itself
(`git show 9f87c48:…/feature.yaml`: `review_sha: none`, zero `squad: validator` entries — INV-6's
precondition is unmet at the pinned commit, matching BRIEF SC-03's stated precondition). The working
tree's `feature.yaml` (uncommitted, `review_sha: 9f87c48` + one `squad: validator` run) is this
review's own live state, pinned correctly *before* the validator entry per PLAN's own build-exit
protocol — also not part of the diff. `git diff 635ef14..9f87c48 -- check-state.sh` touches only the
INV-6 hunk. **SC-03: whole violation set unchanged except INV-6, and INV-6 fires on no existing
feature — CONFIRMED.**

### SC-12 (inspection, mine)

`.harness/team-config.yaml` is **not in this diff** (`git diff --stat` confirms), so the
domain-ungranted premise measured at `635ef14` still holds at `9f87c48` — not a stale citation.
Per-task reasons (`PLAN.md:216,285,361,440,478,517,603,644,686,714`) checked against which files
each task actually touched:

| Task | Files touched | Stated reason | Correct? |
|---|---|---|---|
| T-01 | `check-state.sh`, `validate-digest.py` (CLAUDE.md's 5), `test-check-state.py`, `harness_yaml.py` (D-05) | carve-out | yes |
| T-02 | `teams/review.yaml` (no grant) | domain-ungranted | yes |
| T-04 | `teams/build.yaml` (no grant) | domain-ungranted | yes |
| T-05 | `test-harness-yaml-corpus.py` (mission extension, not D-05, not CLAUDE.md's 5) | carve-out | yes |
| T-06 | `SKILL.md` (no grant) | domain-ungranted | yes |
| T-07 | `test-team-catalog.py`, `run-unit-tests.sh` (D-05) | carve-out | yes |
| T-08 | `docs/**` (granted `team-config.yaml:116`) | squad-dispatched | yes |
| T-09 | `harness-team/SKILL.md` (no grant) | domain-ungranted | yes |
| T-10 | `teams/gate-probe.yaml` (no grant) | domain-ungranted | yes |
| T-11 | `SKILL.md` (no grant) | domain-ungranted | yes |

No task dispatched through a team run (no `runs/t0N-*` dirs exist for any of T-01/02/04/05/06/09/10/
11; `handoff-build.md` states 9 of 10 ran depth-0 in the main session). **SC-12: every task's cause
matches its label — CONFIRMED.**

## Stage 2 — code quality

No fail-open found. Traced every miss/exception branch added in the diff:

- `test-team-catalog.py` checks 1,3,4,7,9: every lookup that can miss (`next(...)`, dict subscript
  on a possibly-`None` parse result) is wrapped so a miss raises into the surrounding `except
  Exception` and the check reports `FAIL`, never a silent pass. Check (9)'s `panel_set()` raises
  loudly on 0 or 2+ `∥`-bearing brace groups rather than guessing one — the exact pattern this
  feature's charter is about, done correctly.
- `check-state.sh`'s INV-6 rewrite: `_sha = (val("review_sha") or "").strip().lower()` correctly
  folds `None` (absent key) and `""` into the same empty-string branch as an explicit placeholder —
  no gap between "absent" and "placeholder" reopened.
- `test-harness-yaml-corpus.py`'s `scan()` rewrite (glob → `os.walk`) is a real defect it caught
  mid-execution (`STATE.md`: glob does not descend into dotted dirs, would have scanned 0 files) —
  not scope creep, it's what makes the widening actually widen.

**Two non-gating notes:**
- `info`: `validate-digest.py` adds `sys.path.insert(0, dirname(__file__))` before `import
  harness_yaml`, beyond D-01's stated mechanism (which relies on `sys.path[0]` already being `bin/`
  via `settings.json`'s absolute-path invocation). Harmless — `bin/` holds no colliding module name —
  belt-and-braces, not a defect.
- `low`: MF-1 (T-02's comment sweep) is verified correct today by this inspection but remains
  unguarded by any test — a future comment edit could silently regress it. Signed open by the user;
  not a new finding, just re-confirmed still true.

## Not re-raised (settled ground per dispatch)

SC-05's count conjunct (qa already flagged), `build.yaml` never executed, markdown-behaviour-has-no-
runner, issue #36, `DECISIONS.md:1634`'s stale three-wide panel row.
