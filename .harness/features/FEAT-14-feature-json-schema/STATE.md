# STATE

## Current

- feature: FEAT-14-feature-json-schema · phase **build** · status Building
- branch `feat/204-feature-json-schema` · HEAD `4d3f439` · `review_sha` pinned `4d3f439`
- cycles_used **4** of 10 · runs 12 of 20
- **Segment 2: three of five tasks DONE. T-09 and T-10 remain with the operator.**

| task | state |
|---|---|
| T-03 | **done** — landed in `3d37762`, plan record corrected (`11d9676`) |
| T-11 | **done** — `cc6643f`, verify exit 0, `0 violation(s) across 10 plan(s)` |
| T-05 | **done** — `4d3f439`, verify exit 0, `--kind integration` exit 0 |
| T-09 | **BLOCKED** — its rename would falsify two dated records |
| T-10 | **BLOCKED** behind T-09 |

### T-08 CANNOT PASS AS WRITTEN — measured, and it is the next thing anyone hits

T-08's verify greps `feature.yaml` across `.claude`, `.github`, `harness.json`, `team-config.yaml`
and `docs/harness`, skips `docs/harness/DECISIONS*`, and pins **only**
`test-harness-yaml-corpus.py` at 4. Every other file it finds is a failure. At `4d3f439`:

| file | count | who owns it |
|---|---|---|
| `check-domain.sh` | 6 | **DEC-174 carve-out** — main session only |
| `test-check-domain.py` | 1 | **DEC-174 carve-out** — main session only |
| `check-plan-routes.py` | 3 | see below |
| `BUILD.md` 8 · `SPEC.md` 14 · `org.html` 2 | 24 | **T-09**, which is blocked |

Two consequences. T-08 is gated on T-09, not merely sequenced after it. And
`check-plan-routes.py:405` is a **dated incident record** — *"the first draft put the `return`
OUTSIDE its own `try:`, so a feature.yaml holding a YAML sequence…"* — so driving that file to zero
repeats the exact rule-15 collision that stopped T-09. Its siblings `:238` and `:566` are
present-tense and rename cleanly; only `:405` is protected.

### T-09 is BLOCKED — full evidence in `runs/t09-product/digest.md`

The product lead halted **before spawning a documentor**: nothing written, no DEC number consumed.
`BUILD.md:335` and `:353` carry `feature.yaml` inside dated evidence markers the file declares to be
records (`:308-310`). Intent, verify and rule 15 cannot all hold, so **no reading was chosen**.
Narrow the verify clause, or re-word the two records so the claim survives without the literal
string. `BUILD.md:357` is a softer third call. SPEC.md's 14 and org.html's 2 rename cleanly.

**Two dead assertions in T-09's own verify, free to fix while it is open.** Confirmed twice — once
by reading, once by the clause's silence when I ran it (exit 1, 9 failures, neither of these among
them): the §11.3 `phase` check captures from a prose cross-reference at `SPEC.md:1604` while the
real heading is `:1762`, and `'Building' in DECISIONS.md` is already true via `DECISIONS.md:1159`.

### T-05: the contradiction was mine, not the plan's

Item 5's *"leave the status fixture loop alone"* forwards to item 7, which says changing the
**filename** it joins is this task's business and changing what it **compares** is not — a split by
what changes, not by which loop. My first dispatch read it as covering the whole file, which is why
the ninth file went undone. T-11's `:834-836` is byte-identical throughout.

**Four assertions had gone vacuous and are now proven live** by three mutants killing disjoint sets:
deleting `isinstance(doc, dict)` fails `a_sequence`+`a_bare_scalar`; deleting `bool(token) and`
fails `a_mapping_with_no_status`; deleting the `str()` wrap fails `status_is_a_list`. All restored,
proven by empty diff and sha256. **My own mutation instruction was wrong** — it paired the
isinstance mutant with `a_mapping_with_no_status`, which parses to a dict and survives it correctly.

The eleven-key end-to-end case is a **paired control**, not a single assertion: a `Done` feature is
excluded from the plan COUNT (`check-plan-routes.py:568-569` `continue`s before counting), so
`"across 1 plan(s)"` would be satisfied identically by a checker that never found the directory.
`Done` → 0 plans, `Building` → 1 plan and 1 violation, status the only variable.

### Predicted red — measured, honest, NOT to be chased

`check-plan-routes.py` reports **35 violation(s) across 16 plan(s)** and exits 1. Correct: no feature
dir carries a `feature.json` until T-08, so nothing is skipped. **T-08 closes it** and its own verify
asserts exactly that. "T-11 closes the 35" is false — measured three ways. Also still expected:
every feature file is `feature.yaml`, `validate-feature-json.py` exits 1, INV-18 fires per feature.

### The cycle count was corrected, and the arithmetic is on the record

3 at signing (`answers-2026-08-11-revision.md:114`) → 5 at `b3055ec`, whose message records no
rework for either increment. One is traceable: E1 was a real defect, `t01t03-eng` ESCALATEd and
`e1fix-eng` was spent fixing it — a send-back DEC-157 counts. The second is untraceable and was
removed rather than given a reason invented afterwards. **4.** Neither the `t05-eng` ESCALATE nor the
run finishing it counts: an answered question about approved plan text is not a FAIL routed back, an
unmet-SC re-dispatch, or a lead-reported send-back.

## Open Questions

- Q1 **BLOCKING**: T-09's intent, verify and rule 15 cannot all hold over `BUILD.md:335` and `:353`.
  T-10 is blocked behind it, and its own verify already exits 0 against an empty diff — running it
  now would land a task by changing nothing.
- Q2 **BLOCKING**: T-08 is unsatisfiable as written (table above). Two of the files it must drive to
  zero are DEC-174 carve-outs, and `check-plan-routes.py:405` is rule-15 protected.
- Q3 non-blocking: the status-loop fixture at `test-check-plan-routes.py:840` writes YAML text into
  a file named `feature.json`. It parses, nothing is red, and no task owns converting it now that
  T-11 is done — the worked example of the old serialisation item 5 exists to delete.
- Q4 non-blocking, measured false three ways: `tests.yml` claims `test-check-plan-routes.py case 25`
  asserts the Plan-route step is present and unneutered. No such test exists, and T-03 added a
  second CI step with the same hole. No task's `files:` authorizes the fix.
- Q5 non-blocking, **closed by measurement**: `gh-sync.py`'s deleted `_strip_github_block` carried a
  corruption incident narrative. The deletion was directed and signed. DEC-131 does **not** preserve
  it — that entry is about orphaned spawns. It survives only in git history at `9cda973`.
- Q6 non-blocking: **DEC-189 is taken**, so T-09 would take 190/191/192, making the plan's D-04
  (cites DEC-189) and D-08 (cites DEC-190) stale. pm's to correct; not back-filled.
- Q7 non-blocking: `check-plan-routes.py:558` still says FEAT-08 "is `awaiting_user` and stays
  checked" in the present tense; FEAT-08 reads `status: Review`.
- Q8 non-blocking: T-11's verify runs `--kind unit`, but `test-check-plan-routes.py` — the file it
  edits — is in `INTEGRATION_SCRIPTS`, so the clause never executes the file the task changes.
- Q9 non-blocking: `notes/baseline-check-state.txt` is **0 bytes**, making T-08's verify stricter
  than "no NEW violations" — it demands **zero** check-state violations after conversion.
- Q10 non-blocking, pre-existing: the guarded-import needle misses `except (ImportError, ...)` and
  `except ModuleNotFoundError`.
- Q11 non-blocking, **two fresh data points**: a `python3` heredoc that rewrote `plan.yaml` was not
  intercepted by the write guard, while `rm` to a scratchpad path was blocked; and a `>` redirect to
  a designated scratchpad path was denied while `tee` to `/tmp` succeeded. FEAT-17's territory.
- Q12 non-blocking, carried: `validate-digest.py:182`'s orchestrator status enum still carries the
  pre-collapse vocabulary (D-13), so this return says `awaiting_user`, not a board column.
- Q13 non-blocking, carried: BRIEF SC-08 carries one clause twice; SC-07's prose says "exits
  non-zero" where its test asserts exactly 3.
