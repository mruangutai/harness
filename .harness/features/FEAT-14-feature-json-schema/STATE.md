# STATE

## Current

- feature: FEAT-14-feature-json-schema · phase **build** · status Building
- branch `feat/204-feature-json-schema` · HEAD `df132c6` · `review_sha` pinned `df132c6`
- cycles_used **5** of 10 (no rework was performed this segment) · runs 11 of 20
- **Segment 2 is HALTED. Two of five tasks landed; three are blocked on the operator.**

| task | state |
|---|---|
| T-03 | **done** — landed in `3d37762`, plan record corrected (`11d9676`) |
| T-11 | **done** — `cc6643f`, verify exit 0, `0 violation(s) across 10 plan(s)` |
| T-05 | **PARTIAL, committed RED** (`df132c6`) — 8 of 9 files correct, verify exits 1 |
| T-09 | **BLOCKED** — its rename would falsify two dated records |
| T-10 | **BLOCKED** behind T-09 |

**T-08 MUST NOT RUN YET.** It depends on T-05, and T-05 is incomplete. Its verify does not run the
unit suite, so T-08 can pass while the red below is still there.

### Three decisions only the operator can make

**1. T-05 vs `test-check-plan-routes.py`.** Item 1 makes repointing the classifier at `feature.json`
mandatory. That breaks the file's fixture at `:839`, which still writes `feature.yaml`, so
`case_24_Done_is_skipped` fails and `run-unit-tests.sh` exits 1. Item 5 says in terms *"Leave
test-check-plan-routes.py's status fixture loop alone"* and item 7 repeats it. **The intent forbids
the fix its own first item requires, and the verify clause runs the suite that then fails.**
Repointing that one filename fixes it and destroys nothing of T-11's.

**This is NOT a consequence of my reordering T-11 ahead of T-05 — I proved that rather than argue
it.** The classifier returns False for every fixture in that loop because no fixture writes a
`feature.json` at all. Running both loop versions against the repointed reader: the **pre-T-11 loop
fails on TWO rows** (`shipped`, `abandoned`), today's on one (`Done`). The reorder changed which
assertion fails, never whether one does. Reverting it would not help.

**Worse than the red, because it is silent.** Four assertions at `:883-913` (`a_sequence`,
`a_bare_scalar`, `status_is_a_list`, `a_mapping_with_no_status`) now pass **vacuously**: the
classifier returns at the missing-`feature.json` check and never reaches the `isinstance` guard they
exist to protect — a guard written for a live crash that made the checker examine nothing, print no
summary and still exit 1. A green suite is exactly what this failure produces. Item 7 does not
protect this loop. Item 5's eleven-key end-to-end case for this tool is also absent.

A precondition decides what those fixture bodies become: `_is_shipped` still parses the `.json` path
with `harness_yaml.load_file`, not `json.load`. If that becomes `json.load`, the fixture shapes and
the trailing-comment rationale change again.

**2. T-09 vs `BUILD.md`.** `BUILD.md:335` and `:353` carry `feature.yaml` inside dated evidence
markers the file itself declares to be records (`:308-310`). The intent renames; the verify allows
zero; rule 15 forbids falsifying. Narrow the clause, or re-word the two records so the claim
survives without the literal string. The product lead halted **before spawning a documentor** — no
file touched, no DEC number consumed. `BUILD.md:357` (probe D7's standing definition) is a softer
third call; SPEC.md's 14 and org.html's 2 are all present-tense and rename cleanly.

**3. Two dead assertions in T-09's verify, free to fix while the clause is open.** The §11.3 `phase`
check regexes from the first `11.3` in the file — a prose cross-reference at `SPEC.md:1604` — and
captures lines 1604–1761 while the real heading is `:1762`; it passes vacuously and the real body
still declares `phase`. And `'Building' in DECISIONS.md` is already true via unrelated prose at
`DECISIONS.md:1159`. `jsonschema` and `additionalProperties` are 0 at HEAD and are live.

### Predicted red — measured, honest, and NOT to be chased

`check-plan-routes.py` went `0/10` → **`35 violation(s) across 16 plan(s)`** when T-05 repointed the
reader. Correct and expected: no feature dir carries a `feature.json` until T-08. **T-08 closes it**
and its own verify asserts exactly that. "T-11 closes the 35" is false — I measured it three ways.

The four other expected reds are unchanged: every feature file is still `feature.yaml`,
`validate-feature-json.py` exits 1 across the corpus, `check-state.sh` INV-18 fires per feature.

### Verified for the record, not taken on a run's word

I re-ran every verify myself. T-11: clause exit 0, `--kind integration` exit 0, full runner exit 0,
diff confined to two files, both new assertions seen red under mutation and restored. T-05: full
runner exit 1 on exactly one assertion; `test-harness-yaml-corpus.py` holds at **4** occurrences
with the marker inserted verbatim; **no `feature.json` was created** under `.harness/features/`; no
DEC-174 carve-out file was touched; the three prohibited tools were never invoked against the live
corpus.

### No handoff note was written, deliberately

INV-17 requires `notes/handoff-<prev>.md` for a seam the status sits past. FEAT-14 is `Building`,
`notes/handoff-plan.md` exists, and the build seam has **not** been crossed — build is unfinished.
Writing `handoff-build.md` now would assert a crossing that did not happen. STATE.md is the record.

## Open Questions

- Q1 non-blocking, measured false three ways: `tests.yml` claims `test-check-plan-routes.py case 25`
  asserts the Plan-route step is present and unneutered. No such test exists, and T-03 added a
  second CI step with the same hole. No task's `files:` authorizes the fix.
- Q2 non-blocking, pre-existing: the guarded-import needle misses `except (ImportError, ...)` and
  `except ModuleNotFoundError`.
- Q3 non-blocking, **two fresh data points**: a `python3 - <<'PY'` heredoc that rewrote `plan.yaml`
  was NOT intercepted by the write guard, while `rm` against a scratchpad path WAS blocked; and a
  `>` redirect to a designated scratchpad path was denied while a `tee` to `/tmp` succeeded on the
  same shape. Both writes were harmless. FEAT-17-guard-boundaries' territory.
- Q4 non-blocking: `test_exactly_one_guarded_import_in_the_tree` misstates its own contract, kept
  deliberately — nine test names are pinned to FEAT-05's PLAN.
- Q5 non-blocking: shared run artifacts have no concurrency guard.
- Q6 non-blocking, carried: `validate-digest.py:182`'s orchestrator digest enum stays out of scope
  (D-13) — it carries `blocked` while the six board columns have no `Blocked`.
- Q7 non-blocking, carried: BRIEF SC-08 carries one clause twice; SC-07's prose says "exits
  non-zero" where its test asserts exactly 3.
- Q8 non-blocking, **closed by measurement**: `gh-sync.py`'s deleted `_strip_github_block` carried a
  corruption incident narrative. The deletion was directed and signed. DEC-131 does **not** preserve
  it — that entry is about orphaned spawns. It survives only in git history at `9cda973`. Rehome it
  or accept the loss; it is not blocking.
- Q9 non-blocking: **DEC-189 is taken**, so T-09 would take 190/191/192, making the plan's D-04
  (cites DEC-189) and D-08 (cites DEC-190) stale. pm's to correct; not back-filled.
- Q10 non-blocking: `check-plan-routes.py:558` still says FEAT-08 "is `awaiting_user` and stays
  checked" in the present tense; FEAT-08 reads `status: Review`. It is a comment no gate reads, so
  widening an approved task to reach it was not an orchestrator's call.
- Q11 non-blocking: T-11's verify runs `--kind unit`, but `test-check-plan-routes.py` — the file it
  edits — is in `INTEGRATION_SCRIPTS`. The clause never executes the file the task changes. Run
  separately this segment (exit 0); the plan text was not edited.
- Q12 non-blocking: `notes/baseline-check-state.txt` is **0 bytes**, consistent with segment 1's
  "zero violations" but it makes T-08's verify stricter than "no NEW violations" — it demands
  **zero** check-state violations after conversion.
