# Plan fix c1 — FEAT-54 — the criteria now bind

**All six findings are closed and the plan is repairable-no-further at this cycle: 14 success criteria
(was 10), 13 tasks (was 10), 9 decisions (was 7). `check-plan-routes.py` on this plan:
`0 violation(s) across 1 plan(s)`. Approval stays `pending` in both files.**

## Per-finding closure

| F | What changed, and where |
|---|---|
| F-01 | SC-04 (BRIEF:84-87) no longer diffs `review_sha..tree`: it now grades only the state-check clause. The untouched-corpus clause became **SC-11** (`verify: inspection`), which diffs `BASE=$(git merge-base main <review_sha>)` → `review_sha` over the note glob and `comm -12`s it against `git ls-tree` at that BASE, so only notes that existed at the base are graded; the `comm -13` arm is the mandated positive control (G-14). No sha is hard-coded. |
| F-02 | New **D-08** records the ruling: a note written during this build is a NEW note, complies, and is never baselined. **T-05 intent** now states b7956fc4 IS the base commit (`git merge-base main HEAD`) and says why globbing the tree would widen the baseline. New **T-11** (main-session-direct) sweeps every `notes/handoff-*.md` of this feature absent from the baseline into compliance, inside the 60-line cap; **T-07 `depends_on` = [T-06, T-11]** so the corpus scan runs after the sweep. **T-07 `verify`** dropped `test -n "$out"` (F-07) and gained a real positive control — `grep -qi 'done when' check-state.sh` plus `rc <= 1` — measured red on the unbuilt tree. REQ-07 (BRIEF:37-41) carries the same base-commit framing. |
| F-03 | Widened T-07, not narrowed SC-08. **T-07 intent** now orders `HANDOFF_HEADINGS` (check-state.sh:1059, read at :1199 and :1219) renamed to `HANDOFF_SECTIONS` with five entries, plus `HANDOFF_NARRATIVE_HEADINGS = HANDOFF_SECTIONS[:4]` for the empty-body loop (so a present-but-empty block is not double-reported), `miss` computed per note against the baseline, and the cap / literal exemption / `_handoff_exempt` explicitly untouched. |
| F-04 | **SC-09** re-declared `evidence: integration` — the probe-registration check lives in `run-unit-tests.sh:76-83` and its only driver is `test-run-unit-tests-kinds.py`, which is in `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:31`). New **T-12** (main-session-direct, DEC-174) adds the three missing assertions: positive registration on the real config, an unregistering mutation naming `probe-handoff-comprehension.py` (cases 6-8 only ever mutate `omp_session_accessor`), and absence from both script arrays. The "no model call" clause was **dropped from the criterion** and asserted where it can be: **T-09 `verify`** now re-runs `--dry-run` under `sys.addaudithook` failing on `socket.connect`/`getaddrinfo`/`subprocess.Popen`/`os.system`/`urllib.Request`, and asserts the kind is absent from `test_matrix`. |
| F-05 | **SC-07** restated as `verify: inspection` over two cited import sites at `review_sha` and a recorded mutation experiment; new **T-13** (main-session-direct, DEC-174) authors `notes/mutation-FEAT-54-shared-module.md` — mutate the exported `problems` symbol, run both suites, record the case names and exit codes per suite, restore byte-identical, print the reproduction command and sha. New **D-09** records why this is an experiment rather than a permanent mutation test (it would mutate a gate from inside the gating suite). |
| F-06 | (b) → **SC-10** extended: the operator also judges the `Scope:` label as the immediate `## Next` action, a phase/feature label reading as wrong against the template. (d) → **SC-12** (`unit`): three-of-four resolving is REFUSED with exactly one message, four-of-four returns no problem — T-01(f) intent rewritten to state the AND-vs-ANY contrast. (e) → **SC-13** (`integration`) plus **T-01(e)** and **T-03(g)**, each carrying two fixtures: an unknown prefix and a bare `check-domain.sh:1523`. (i) → **SC-14** (`integration`) plus new **T-03(h)**: a 25-line `Trust` section in a 60-line file is ALLOWED and no cap is mentioned — a positive-observable regression guard. |

## Per-SC evidence-kind check (against `.harness/harness.json` `test_kinds`)

Every SC declares exactly one `verify:`. `unit` (`cmd: run-unit-tests.sh --kind unit`) and `integration`
(`cmd: run-unit-tests.sh --kind integration`) are both non-null; no criterion rests on `eval`, `ui`,
`component`, `functional` or `typecheck`, all of which are `cmd: null` (DEC-163 respected).

- automated/integration: SC-01, SC-02, SC-03, SC-04, SC-05, SC-06, SC-09, SC-13, SC-14 — kind exists, `cmd` non-null.
- automated/unit: SC-12 — kind exists, `cmd` non-null; assertions land in `test-handoff-done-when.py`, which D-06 puts in `UNIT_SCRIPTS` only.
- inspection: SC-07, SC-08, SC-11. uat: SC-10.

## Carried forward, verified mechanically

REQ-01..REQ-10 each traced by ≥1 task (REQ-01 +T-11, REQ-06 +T-13, REQ-10 +T-12); every `traces:` value
exists in BRIEF; `change_type` on all 13 tasks; `depends_on` acyclic; `yaml.safe_load` loads the plan;
all 13 `verify:` blocks are literal (`|`) and pass `bash -n`, and every embedded `python3 -c` body
compiles. The five out-of-scope exclusions remain absent from the task set. DEC-174 routing untouched.
`approval.status: pending`; BRIEF `## Approval status: pending`.

Discrimination measured on the unbuilt tree: T-11 rc=1 ("no handoff note found"), T-12 rc=1, T-13 rc=1,
and T-07's new positive control `grep -qi 'done when' check-state.sh` rc=1.

## Open question

`lanes:` cannot be written. `plan-merge.py` unions only `tasks` and `decisions`; `amend` takes
`--key tasks|decisions`; any other top-level key is compare-and-swap (plan-merge.py:674-684), so a
changed `lanes` block exits 7. Three surfaces T-11/T-12/T-13 introduce are therefore not in the
`lanes:` rows: `features/FEAT-54-handoff-done-when/notes/handoff-plan.md`,
`notes/mutation-FEAT-54-shared-module.md` (both resolve to `harness-orchestrator`, which hosts rather
than executes) and `bin/test-run-unit-tests-kinds.py` (DEC-174). Each task's `execution_reason` carries
the routing, `check-plan-routes.py` reads tasks and not `lanes`, and it reports 0 violations — so this
is a record gap, not a routing gap. It needs either a `plan-merge.py` verb for `lanes` or a rule that
`lanes` is written once at plan creation.
