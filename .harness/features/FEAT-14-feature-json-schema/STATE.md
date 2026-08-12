# STATE

## Current

- feature: FEAT-14-feature-json-schema · phase **build** · status Building
- branch `feat/204-feature-json-schema` · HEAD `364833c` · `review_sha` pinned `364833c`
- cycles_used **5** of 10 · runs 10 of 20
- segment 2: T-03 recorded done · T-11 running · **T-09 and T-10 BLOCKED on the operator** ·
  T-05 queued behind T-11

**Segment 1 is COMPLETE and committed.** T-01 and T-03 both landed in `3d37762`; T-02, T-04, T-06,
T-07 and T-12 are `done` and are not segment 2's to revisit. T-03's status field was the only thing
outstanding — its verify exits 0 AND the intent's mandated comment amendment is present at
`.github/workflows/tests.yml:66-74`, so it is intent-complete, not merely verify-green (`11d9676`).

### T-09 is BLOCKED and T-10 with it — full evidence in `runs/t09-product/digest.md`

The product lead halted **before spawning a documentor**: nothing written outside its run dir, no
DEC number consumed. T-09's intent renames `feature.yaml` everywhere in `BUILD.md`; its verify
allows zero occurrences; `BUILD.md:335` and `:353` carry the string inside dated evidence markers
the file itself declares to be records (`BUILD.md:308-310`). Intent, verify and PRINCIPLES rule 15
cannot all hold, so **no reading was chosen**. The operator picks: narrow the verify clause, or
re-word the two records so the claim survives without the literal string. Both are pm's.

I re-measured every premise before relaying: BUILD.md has **11** occurrences over 8 lines; SPEC.md's
**14** and org.html's **2** are all present-tense and rename cleanly. Two assertions in T-09's own
verify are dead and free to fix while the clause is open — the §11.3 `phase` check captures from a
prose cross-reference at `SPEC.md:1604` instead of the heading at `:1762` (the real body still
declares `phase`), and `'Building' in DECISIONS.md` is already true via `DECISIONS.md:1159`.

**T-10 is blocked, not merely unstarted:** its verify already exits 0 against an empty diff at HEAD,
so running it now would land a task by changing nothing. A vacuous pass is not a landing.

### The third contradiction: T-11's stated dependency makes its own verify unsatisfiable

T-11 records `depends_on: [T-04, T-05]` and its intent opens "T-05 runs before you". Measured
impossible, so I **reordered T-11 ahead of T-05**. Monkeypatched `_is_shipped`, live corpus:

| configuration | `check-plan-routes.py` prints |
|---|---|
| A — today: `feature.yaml` + `("shipped","abandoned")` | 35 violation(s) / 16 plan(s) |
| B — T-11 first: `feature.yaml` + `("Done",)` | **0 violation(s) / 10 plan(s)** |
| C — T-05 first: `feature.json` + `("Done",)` | 35 violation(s) / 16 plan(s) |

B reproduces intent item 5's prediction byte-for-byte. C fails T-11's verify: T-05 repoints the
reader at `feature.json`, no feature dir holds one until T-08, a missing file means "not finished",
so every plan is checked again — and T-08 depends on T-11, so the plan as written deadlocks. The
reorder is safe because the two tasks' edits to those two files are disjoint by construction (T-05
item 7 forbids the constant and the `want_checked` loop; T-11 items 1–4 own exactly those).

**Predicted, so nobody chases it:** T-11 is green at its own commit and goes RED again (35/16) the
moment T-05 lands, until T-08 converts the corpus. "T-11 closes the 35" is falsified by C.
**T-08 closes them**, and T-08's own verify asserts exactly that.

**T-11's verify never runs the file T-11 edits:** it calls `--kind unit`, but
`test-check-plan-routes.py` is in `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:17-18`), and items 3–4
add every new assertion there. The eng run was told to run both kinds. The clause was not edited.

### Baselines measured this session, for attribution

- full `run-unit-tests.sh` (both kinds) **exit 0** · `check-plan-routes.py` 35/16 (expected red)
- `DECISIONS.md` keeps all **50** `feature.yaml` occurrences (rule 15); T-08's verify already
  exempts `docs/harness/DECISIONS*` from its sweep, so the two are consistent
- **DEC-189 is taken**, so T-09 would take 190/191/192 — making the plan's D-04 (cites DEC-189) and
  D-08 (cites DEC-190) stale. pm's to correct; not back-filled here
- 17 `feature.yaml` and 17 T-04 drop receipts — T-04 is complete
- `notes/baseline-check-state.txt` is **0 bytes**, consistent with segment 1's "zero violations" but
  it makes T-08's verify stricter than "no NEW violations": it demands **zero** after conversion

### Carried, and NOT in segment 2's five tasks

**G1** (SC-02 wants failing fixtures at the `factory` and `factory.edges` levels) and **G4** (the
`.json`-holding-valid-YAML rejection needs a mutation) both live in
`test-validate-feature-json.py` — T-01's `files:`, and none of segment 2's five. Flagged, not done.

## Open Questions

- Q1 non-blocking, measured false three ways: `tests.yml` claims `test-check-plan-routes.py case 25`
  asserts the Plan-route step is present and unneutered. No such test exists, and T-03 added a
  second CI step with the same hole. No task's `files:` authorizes the fix. Briefing row.
- Q2 non-blocking, pre-existing: the guarded-import needle misses `except (ImportError, ...)` and
  `except ModuleNotFoundError`.
- Q3 non-blocking, **now with direct evidence**: a `python3 - <<'PY'` heredoc that rewrote
  `plan.yaml` was NOT intercepted by the write guard, while `rm` against a scratchpad path in the
  same session WAS blocked. The write landed in-domain so nothing was damaged; I moved to Write for
  the rest of the segment. FEAT-17-guard-boundaries' territory.
- Q4 non-blocking: `test_exactly_one_guarded_import_in_the_tree` misstates its own contract, kept
  deliberately — nine test names are pinned to FEAT-05's PLAN.
- Q5 non-blocking: shared run artifacts have no concurrency guard.
- Q6 non-blocking, carried: `validate-digest.py:182`'s orchestrator digest enum stays out of scope
  (D-13) — it carries `blocked` while the six board columns have no `Blocked`.
- Q7 non-blocking, carried: BRIEF SC-08 carries one clause twice; SC-07's prose says "exits
  non-zero" where its test asserts exactly 3.
- Q8 **BLOCKING**: T-09's intent, verify and rule 15 cannot all hold over `BUILD.md:335` and `:353`.
- Q9 non-blocking: T-09/T-10 record `depends_on: [T-08]`/`[T-09]` and T-08 has not run; the operator
  assigned both anyway. Recorded, not absorbed — it is not why either is blocked.
