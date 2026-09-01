# UI Review — FEAT-41 cycle 3 (re-prompt)

review_sha `5dc77108`, merge-base `7c4f0bd`. Worktree HEAD is `a725472e` (one re-pin commit ahead
of `5dc77108`; the two files load_plan/check-domain.sh touch are byte-identical between the pin
and HEAD, confirmed by `git diff 5dc77108 HEAD -- <path>` returning empty for both — so live
execution against the checkout reflects the pinned text).

Dispatch named the artifact path as `notes/review-ui-c3.md`; the domain guard denies that
filename (permitted pattern is `notes/review-harness-ui-reviewer-*.md`) and instructs not to work
around it, so this file is `review-harness-ui-reviewer-c3.md` instead. Noted as an open question.

## 1. Census — the scope-out, measured

**No `DESIGN.md` for this feature.** Checked two ways: (a) `find
.harness/harness/features/FEAT-41-one-station-vocabulary -iname DESIGN.md` → 0 hits; (b) `git
ls-files | grep -i DESIGN.md` → 5 repo-wide hits, none under FEAT-41
(`.claude/skills/harness/templates/DESIGN.md`, FEAT-10, FEAT-11, FEAT-19, FEAT-40).

**Diff `7c4f0bd..5dc77108`:** 196 files changed, +14567/−1341 (`git diff --stat`).

**Extension census** (html/css/scss/tsx/jsx/vue/svelte/less) over `git diff --name-only
7c4f0bd..5dc77108`: **2 hits**, both `.html` — `notes/ship-review-2026-08-29-01.html` and
`notes/ship-review-2026-08-30-01.html`. Both open with a generated `<style>` block and each closes
with `<p class='derived'>Derived from ship-review-*.md — the markdown is the record; do not edit
this file. Regenerate with bin/render-brief.py.</p>` — a regeneration footer, not product UI (G-11).
Net in-scope UI-surface files: **0**. This is a measured scope-out (O-01), not a prediction.

## 2. Operator-facing diagnostic messages — per-message audit

| Message | What I ran | Verdict |
|---|---|---|
| **check-state.sh INV-34** station-only remediation (content at `5dc77108`; current-HEAD line numbers shifted by later commits, text identical) | Built the literal file the message instructs — `schema: plan/1` / `feature: TEST-INV34-PROBE` / `status: station-x` / `tasks: []` — and loaded it through `harness_yaml.load_plan()` in-process. **Loaded clean**: `{'schema': 'plan/1', 'feature': 'TEST-INV34-PROBE', 'status': 'station-x', 'tasks': []}`. `load_plan`'s FEAT-41 T-19 carve-out (`if not tasks and not str(doc.get("status")...).strip(): raise`) is exactly the station-only shape the message describes, so the remediation it names actually remediates. | **PASS** |
| **check-domain.sh** `plan.yaml` write denial | Reused `test-check-domain.py`'s own fixture helpers (`_approval_root`, `_fire_write`) to fire the real hook subprocess twice — once with `agent_type=harness-orchestrator`, once with no `agent_type` at all. Both: exit 2, stderr opens with the REASON clause (`plan.yaml has exactly ONE writer, plan-merge.py, because every station value must be validated against the vocabulary before it lands on disk. An editor write cannot do that...`) **before** the four `plan-merge.py <verb>` ROUTE lines. Matches the code's own ordering claim for both payload shapes, live-triggered not just read. | **PASS** |
| **plan-merge.py:182** `_refuse_illegal_station` | Read source + both call sites (station-not-in-legal checks). Message: `f"plan-merge: {station!r} is not a legal station — expected one of: " + ", ".join(legal)`. Names the offending value (`{station!r}`) and every legal one (`legal` is the full mandated-stations list, joined). | **PASS** |
| **harness_yaml.py:339-342** `PlanSchemaError` empty-plan text | Read at pin: `"\`tasks:\` is empty and there is no top-level \`status:\` — a plan with neither records nothing. A station-only record must declare the station it records."` Wrapped by `YamlParseError.__str__` as `"failed to parse YAML in {path}: {text}"`, so the file is always named. Names both unmet conditions (empty `tasks`, absent `status`) and states the fix in prose (declare the station). | **PASS** |
| **check-state.sh INV-33** stale-pin message | Carried forward from cycle 2's own live-fixture run (`notes/review-harness-ui-reviewer-c2.md` §6 — real two-commit git fixture, actual `check-state.sh` output captured), re-confirmed unchanged: this diff's `check-state.sh` INV-33 block lands whole in `7c4f0bd..5dc77108` and is not touched again after. Names feature, pinned sha, changed file, and last commit that touched it — sufficient for the reader to re-pin. One pre-existing style nit: `(INV-33)` is a parenthesized suffix; every other of the file's 20+ numbered invariants opens with an `INV-NN:` prefix, so a habitual `grep "INV-NN:"` misses this line (a bare `grep INV-33` still finds it). | **PASS**, one carried LOW note |

No `high` or `med` finding. The one open item is the pre-existing INV-33 prefix/suffix
inconsistency, unchanged since cycle 2, non-blocking.

## Verdict basis

Both halves complete: the census is a measurement (extension count + generated-footer check +
`git ls-files` DESIGN.md sweep), not an inference, and all five named messages were read at the
pinned commit and, where triggerable, actually triggered rather than merely read.

## Operational note (not a UI finding)

My first write of this artifact resolved a relative path against the MAIN checkout instead of
this worktree and landed a stray, untracked
`.harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-ui-reviewer-c3.md`
at `/Users/molchairuangutai/GitHub/harness/...` (outside the worktree I am scoped to). The
bash-write-guard correctly refused my `rm` of it ("Report the finding; never fix" — DEC-151), so
it is still there. Flagged in `open_questions` for the operator/main session, which can reach that
path, to remove it.
