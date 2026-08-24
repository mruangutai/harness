# Review (qa seat, gate-only) — FEAT-33 board-lifecycle-native — c0

**VERDICT: FAIL.** Independent re-derivation confirms the qa segment's task counts and its 46/46
suite numbers exactly. But SC-10's own verify — `check-state.sh` exits 0 — does not hold when I run
it right now: exit 1, 2 VIOLATIONs, one of which names **this feature itself**. That contradicts
both SC-10 and the segment's own report, which claims "exits 0" in the same sentence as "exactly 1
VIOLATION" (self-contradictory on the script's own logic: `sys.exit(1 if bad else 0)`).

## Task counts, re-derived independently (not by grep)

Parsed `plan.yaml` with `yaml.safe_load`, counted `change_type` per task (22 tasks, `T-01`..`T-22`):
**api×1 (T-03), bugfix×3 (T-07/T-08/T-22), config×6 (T-01/T-10/T-11/T-12/T-18/T-20), docs×4
(T-09/T-14/T-19/T-21), feature×5 (T-04/T-05/T-06/T-15/T-17), logic×3 (T-02/T-13/T-16) = 22.** Matches
the dispatch's corrected figure and the qa segment's own re-count. The main session's `bugfix×5,
feature×8` (=27) is confirmed wrong: it double-matched `change_type:` inside task `intent:` prose.

## Matrix (`.harness/harness.json` test_matrix)

| change_type | required | state |
|---|---|---|
| config (6), docs (4) | none (`always: []`) | satisfied — n/a |
| logic (3) | unit | **satisfied** |
| api (1) | unit + integration (touches external service) | **satisfied** — unit in `test-factory-gh.py`, integration case (I) in `test-factory-integration.py` (forks a real process, asserts argv content, not just exit 0) |
| feature (5) | unit + integration | **satisfied** — each of T-04/05/06/15/17 has unit cases in `test-board-lifecycle.py` AND its own forking case (J,K,L,M,N) in `test-factory-integration.py`, verified by name and content, not by exit code alone |
| bugfix (3) | unit | **satisfied** — T-07 replays #642's exact shape (`test-gh-sync.py:1266-1290`), T-08 has per-issue LABEL/REASON assertions, T-22 has the four INV-26 boundary cases (`test-check-state.py`, v.T22a-d) |

`matrix_ok: true`. No required kind is missing.

## Suite — measured myself, not trusted

- `run-unit-tests.sh --kind all`, run to completion in the background (not truncated): **46 scripts
  reported PASS, 801 individual `PASS` lines, 0 `FAIL` lines, exit 0.** Grepped for
  MISCONFIGURED/ImportError/Traceback/MODULE_NOT_FOUND: zero real hits (only test *names* asserting
  absence of a traceback). This exactly matches the qa segment's own numbers — independently
  reproduced, not copied.
- `test-board-lifecycle.py` alone: 99 `PASS` lines, exit 0, and it is registered in
  `run-unit-tests.sh`'s `UNIT_SCRIPTS` (confirmed by the fact it ran at all under `--kind unit`).

## `check-state.sh` — the live discrepancy

Ran it myself, twice, just now:

```
VIOLATION  .harness/harness/features/FEAT-34-worktree-act3-enforced/BRIEF.md is NOT approved — ...
VIOLATION  FEAT-33-board-lifecycle-native: status is 'Review' but notes/handoff-build.md is
           missing — the build seam was crossed without a handoff; the successor is on the
           disk-only path (DEC-159).
```
`exit 1`. Two VIOLATIONs, not the segment's claimed one. The FEAT-34 line matches the segment's
report exactly. **The second is new, and it names FEAT-33 itself.**

`feature.json` at this moment reads `"status": "Review"`, and `notes/` carries `handoff-plan.md`
but no `handoff-build.md`. The orchestrator playbook (`.claude/skills/harness/SKILL.md`) writes
`gh-sync.py status <dir> Review` immediately before dispatching the validate/review panel — which is
what put `feature.json` at `Review` — but nothing in that same step wrote the build→validate
handoff note DEC-159 requires. This is a real, reproducible INV-17 finding against **this feature's
own live state**, not a hypothetical.

**This directly falsifies SC-10 as measured right now**: SC-10's own verify text is "`check-state.sh`
exits 0 on the harness checkout after the migration," and it does not. It also means the qa segment's
report is internally inconsistent — it asserts "exits 0" and "exactly 1 VIOLATION" in the same
sentence, which the script's own `sys.exit(1 if bad else 0)` makes impossible; either the state
changed between their run and mine (plausible: the orchestrator's Review-entry write likely landed
after they wrote `qa-gate-c0.md`), or their exit-code claim was not itself independently checked.

I cannot resolve this myself — I hold no write access to source, and the fix here (a
`notes/handoff-build.md`, or the orchestrator/build-lead completing the DEC-159 handoff) is not qa's
to author. It is either an orchestration-sequencing gap in this feature's own run, or a genuinely
missing artifact — either way it is not "green," and reporting it as green would be exactly the
fail-open this panel exists to catch.

## Coverage — tested the `coverage_gaps: []` claim, not just repeated it

Spot-checked the three specific calibration failure shapes named in the dispatch, all against this
diff's actual new tests:

1. **Absence-only assertions.** `test-board-lifecycle.py:398-401` (SC-08, "no argv contains
   'Abandoned'") — paired with a positive assertion in the same block that a real mutation happened
   (`log` non-empty, options actually extended), so it is not vacuous. `test-board-lifecycle.py:705`
   ("records status" not in stdout, the #783 cross-repo STATUS-skip case) is paired with an explicit
   positive check two lines later that the skip line itself appears, naming both repos. Both pass
   DEC-169's pairing requirement.
2. **Dict-keyed-by-name blindness (the #783 shape).** `board_lifecycle.py`'s STATUS class now
   self-skips unless `repo_name == _own_repo(root)` (`board_lifecycle.py:559-568`), and
   `test-board-lifecycle.py`'s case 8/#783 block exercises exactly the cross-repo shape that caused
   the original 18/29 false findings. Confirmed the fix and the test both exist and agree.
3. **Count-based vs exact-set assertions** (the Review/Ready station writes, SC-13/14).
   `test-gh-sync.py:1608-1611` asserts `ids_written3 == {"ITEM_40", "ITEM_41", "ITEM_42"}` — an exact
   set, not a count — and the zero-sub-issue SC-14 fixture asserts no `item-edit` call at all, not a
   count of zero. Both resist the "conformers-only" defect class named in the dispatch.
4. **The bound in SC-20's widening.** `test-check-state.py` v.T22a-d asserts BOTH directions: the
   widened accept cases (Review/Building at feature-status Review) and the still-rejected cases
   (Building at feature-status Building; Backlog is never accepted regardless of feature-status).
   This is the shape the calibration note asks for — a boundary proven on both sides, not just the
   permissive side.

No new coverage gap found beyond the one the qa segment already disclosed (SC-19's 188→218 count
drift, itself a report-honesty finding, not a hidden one).

## SC-11 and the three captured reports

`notes/migration-harness.md`, `notes/migration-kaya-ai.md`, `notes/retitle-harness.md`: I did not
re-verify these captures byte-for-byte (the qa segment already diffed the raw before/after audit
captures against the narrative and reported a live re-run finding a THIRD, expected-transient
finding on migration-harness.md). I have no reason to doubt that spot-check. **SC-11 stays `not_met`
by design** — `uat`, operator-run — which is correct and not a gate issue here.

## Bottom line

- `matrix_ok: true`
- Suite (`--kind all`): pass, 46/46, 801 PASS / 0 FAIL, exit 0 — independently reproduced
- `coverage_gaps`: none newly found beyond SC-19's disclosed drift
- **SC-10 is NOT met as measured right now** — `check-state.sh` exits 1, naming this feature's own
  missing `notes/handoff-build.md`. That is a live blocking finding, not a coverage gap, and it
  returns to the orchestrator/build-lead, not to qa.
