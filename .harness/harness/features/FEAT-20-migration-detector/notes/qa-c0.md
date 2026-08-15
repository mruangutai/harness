# QA gate — FEAT-20-migration-detector — c0

**VERDICT: PASS.** Both required kinds (unit, integration) ran green at `11cb644`, both registration
greps fired, and every automated SC I could bind independently reproduced.

## Phase 1 (BRIEF/plan only, no source read yet)

Before opening `layout_migration.py` or `check-state.sh`, expected coverage derived from BRIEF's 15
SCs and D-01..D-04:
- A unit suite over the detector module covering: real-repo positive control, per-surface MIXED
  (evidence-split and reader-disagreement flavors, both surfaces), CLEAN (fully migrated, and both
  sanctioned intermediate states), CANNOT_VERIFY (neither-form, unreadable, no-evidence, empty-table),
  BOTH-forms MIXED, MIXED-vs-CANNOT_VERIFY precedence, NOT APPLICABLE (case 14) paired with a marker
  case that flips it to CLEAN (case 15) so 14 isn't proving "empty scan is quiet" by accident.
- An integration suite proving `check-state.sh` surfaces INV-27 on a reddening/cannot-judge fixture,
  is silent on an applicable-clean fixture AND on a no-marker fixture, and handles an import failure.
- Every reader-path line carries a distinguishing tag (finish vs. revert) — asserted, not just present.
- No test for the CI wiring itself (`verify: inspection` — SC-09), no test for SC-10/SC-11 (also
  `inspection`) — those are audited, not run.

This matches what T-01/T-02's plan.yaml intent actually specifies almost line for line, which is
itself worth flagging as a **finding**: this plan is unusually prescriptive (verbatim output strings,
numbered cases pinned by number in three other documents) — there is very little daylight in which
Phase-1-derived and Phase-2-actual coverage could have diverged. That is a property of this plan, not
evidence the gate is weaker for it.

## Matrix — computed, not assumed

`change_type` per task: T-01 `logic`, T-02 `cross_module`, T-03 `config`, T-04 `docs`.
From `harness.json` `test_matrix`: `logic.always=[unit]`, `cross_module.always=[unit,integration]`,
`config.always=[]`, `docs.always=[]`. **Union = {unit, integration}.** Matches BRIEF's own
"Verification gaps: None" statement.

| kind | state | cmd | named tests |
|---|---|---|---|
| unit | satisfied | `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` | `test-layout-migration.py` — 18 cases, exit 0 |
| integration | satisfied | `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` | `test-check-state.py` — cases (x.1)-(x.5), exit 0 |
| functional | excluded (`DEC-187`) | null | — |
| component | unresolved | null | not required by this matrix |
| ui | unresolved | null | not required by this matrix |
| eval | unresolved | null | not required by this matrix (no `ai_behavior` task) |
| typecheck | unresolved | null | not required by this matrix |

Registration greps, run myself against my own captured output (not receipts):
- `grep -q '^PASS test-layout-migration\.py$'` unit output → **fires**, line 818.
- `grep -q '^PASS test-check-state\.py$'` integration output → **fires**, line 272.

Both suites exited 0. `test-layout-migration.py` printed all 18 case labels (16 plan-specified +
case 17 non-enum-surface-is-loud-error + case 18 exit-code-contract, both named in T-02's intent as
additions). `test-check-state.py`'s new cases (x.1)–(x.5) all `ok`.

**Shell-note compliance:** the write-guard refused `>"$u"` (shell-variable redirect target) exactly as
warned. Redirected to literal scratchpad paths instead
(`/private/tmp/.../scratchpad/unit-out.txt`, `.../int-out.txt`); the `grep -q ... || { ... }`
assertion logic from `plan.yaml`'s `verify:` blocks was run verbatim against those files, unchanged.

## SC-10 — closed 8-file set, diffed myself

`git diff --name-only 88b1182..11cb644` (20 paths) against `plan.yaml`'s `lanes:` 8-row closed set
(`layout_migration.py`, `test-layout-migration.py`, `check-state.sh`, `test-check-state.py`,
`run-unit-tests.sh`, `.github/workflows/tests.yml`, `docs/harness/DECISIONS.md`,
`docs/harness/DECISIONS-INDEX.md`): **all 8 present, all 8 in the diff, no path outside that set is
a code/production/decision file.** `git diff --diff-filter=R --name-status 88b1182..11cb644` is
**empty** — no renames.

The remaining 12 diffed paths are this feature's own harness bookkeeping —
`BRIEF.md`, `plan.yaml`, `STATE.md`, `feature.json`, `notes/*` (5 receipts/handoffs/review),
`observations/harness-pm.md`, `.harness/notes/research-FEAT-20-migration-detector.md`. These are
the standard per-feature artifact set every feature produces; none is a "file this feature changes"
in the BRIEF's Scope sense (which is about the shipped surface), and none moves or renames anything.
Flagging this explicitly rather than silently treating SC-10 as satisfied on the closed set alone,
because BRIEF's literal wording ("No file outside [the 8] is modified") is stricter than what the
`lanes:` block — the operative artifact — actually enumerates. Read this as **satisfied on the
lanes-block scope**, with the bookkeeping delta named rather than absorbed.

Separately: `git status --porcelain -- <all 8 lanes paths>` returns **empty** — none of the 8 is
currently dirty relative to HEAD. That closes the gap between "HEAD is pinned at `11cb644`" and "the
bytes I ran the suites against are the pinned bytes": the working tree has unrelated dirt elsewhere
(see SC-11 below), but not on any file this gate's verdict depends on.

## SC-11 — fixture isolation

`grep -c tempfile.TemporaryDirectory`: `test-layout-migration.py` → 20 occurrences,
`test-check-state.py` → 48. Properly bracketed this time: captured `git status --porcelain` to a
file, re-ran the full unit suite (which includes `test-layout-migration.py`'s 68 combined
`TemporaryDirectory` fixture builds), captured status again, `diff`'d the two captures — **exit 0,
byte-identical.** The suite run wrote nothing to the repository tree. (The dirty entries present in
both captures — `STATE.md`/`feature.json` diffs, two deleted unrelated `backend-dev` member files,
two untracked unrelated log/notes files — are pre-existing and unaffected either way.) SC-11 is
supported by measurement, not inference.

## SC-12 — case 14/15 pairing

Confirmed directly in unit output:
Read the assertion bodies myself, not just the `ok` labels (P-01 — a label can name a different verb
than what's actually invoked). Case 14 asserts
`code == 0 and "NOT APPLICABLE: no harness control-plane marker at " in out` for the literal, and
separately `set(map(int, m.groups() + s.groups())) == {0}` over both regex-extracted trailer lines —
a real check against all 6 numbers, not a string-presence check. Case 15 asserts
`code == 0 and int(m.group(1)) > 0 and int(m.group(3)) > 0` against the same fixture plus the marker
and legacy disk evidence. Both bodies match their labels; case 15 is the genuine discriminator, not
an inferred one.

## T-03's CI step — SATISFIED, not unsatisfiable

`change_type: config` maps to `test_matrix.config.always = []` — the matrix requires **zero** test
kinds for this task. It is trivially satisfied by having nothing to satisfy, not unsatisfiable.
Ran `grep -rl "tests\.yml" . --include="*.py"` (excluding worktrees) myself: two hits, neither an
assertion against the workflow's content —
`.claude/skills/harness/bin/layout_migration.py:236` is a comment (the one plan.yaml mandates,
pointing back at the CI grep coupling) and
`.claude/skills/harness/bin/test-check-domain.py:715` is an unrelated write-domain fixture path that
happens to be named `tests.yml`, not a parse of the workflow. So no `.py` in the tree actually reads
and asserts against `.github/workflows/tests.yml`'s content outside this task's own inline `verify:`
(which I re-ran above and it passed). This is exactly the posture BRIEF's Q1 signed off on, consistent
with DEC-183 ("that whole CI step class is unguarded by owner decision"). Reported as an adequacy
note, not a `must_fix` — the brief's own signature already accepted the gap.

## SC binding — automated vs. inspection, stated plainly

Automated, bound to a named test at `11cb644`:
- SC-01 → `test-layout-migration.py` case 1
- SC-02 → case 2
- SC-03 → case 3
- SC-04 → case 4
- SC-05 → case 6
- SC-06 → cases 7, 8
- SC-07 → case 9 (vs. case 10, distinct exit-2 causes)
- SC-08 → `test-check-state.py` cases (x.1), (x.3), (x.4)
- SC-12 → case 14 + case 15 (paired)
- SC-13 → case 16 (empty-table cause) plus case 1 (X+Y+Z==2, the "surface count accounts for every
  declared surface" clause — not case 11, which is the sibling no-disk-evidence cause, a different
  SC-13 antecedent)
- SC-14 → cases 3 and 5a/5b (both directions, tag asserted)
- SC-15 → `test-check-state.py` case (x.1) (tag + remedy asserted in INV-27 output)

Inspection only, per the BRIEF's own `verify:` line — not run by me as automated evidence:
- SC-09 (CI job behavior) — inspected the workflow YAML directly (see T-03 section above); not
  exercised by any test.
- SC-10 (closed file set) — diffed myself against `lanes:`, see above.
- SC-11 (fixture isolation) — grep + git-status inspection, see above, with the caveat noted.

No SC in this brief is silently uncovered: 12 of 15 are automated and I re-derived the binding myself
rather than trust the receipts; 3 are inspection by the brief's own signature and I performed that
inspection directly rather than defer to the receipts' claim of it.

## Coverage gaps (Phase 1 vs Phase 2 delta)

None material. Phase 1's expected list and the actual suite are near-identical — a property of how
prescriptive this plan is (see above), not a gap I'm eliding. The one honest gap: I did not perturb
(mutate) the detector to independently prove the suite discriminates — that would require a worktree
per DEC-153 and this dispatch's scope is enforce-the-matrix-against-this-diff, not a perturbation
proof. Naming it as an open question below rather than silently skipping it.

## files_touched

`.harness/features/FEAT-20-migration-detector/notes/qa-c0.md` — this note, the only file I wrote. My
writable domain does not cover `.claude/skills/harness/bin/**` (D-02/DEC-174 main-session-direct
carve-out), so I raise findings rather than author fixes — no findings this cycle require that route.

```yaml
VERDICT: PASS
DIGEST:
  headline: Both required kinds (unit, integration) green at 11cb644; both registration greps fired; SC-10/11/12 independently reproduced, not just re-read from receipts.
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 18 }
    - { kind: integration, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 5 }
    - { kind: functional, state: excluded, cmd: null, named_tests: 0 }
    - { kind: component, state: not_required, cmd: null, named_tests: 0 }
    - { kind: ui, state: not_required, cmd: null, named_tests: 0 }
    - { kind: eval, state: not_required, cmd: null, named_tests: 0 }
    - { kind: typecheck, state: not_required, cmd: null, named_tests: 0 }
  coverage_gaps: [no perturbation/mutation proof was run against the detector — enforcement-only dispatch, not authoring; see open_questions]
  sc_evidence:
    - { id: SC-01, test: ".claude/skills/harness/bin/test-layout-migration.py case 1" }
    - { id: SC-02, test: ".claude/skills/harness/bin/test-layout-migration.py case 2" }
    - { id: SC-03, test: ".claude/skills/harness/bin/test-layout-migration.py case 3" }
    - { id: SC-04, test: ".claude/skills/harness/bin/test-layout-migration.py case 4" }
    - { id: SC-05, test: ".claude/skills/harness/bin/test-layout-migration.py case 6" }
    - { id: SC-06, test: ".claude/skills/harness/bin/test-layout-migration.py cases 7, 8" }
    - { id: SC-07, test: ".claude/skills/harness/bin/test-layout-migration.py case 9 (vs case 10)" }
    - { id: SC-08, test: ".claude/skills/harness/bin/test-check-state.py cases (x.1),(x.3),(x.4)" }
    - { id: SC-09, test: "inspection only — .github/workflows/tests.yml, verified directly by qa; no automated test" }
    - { id: SC-10, test: "inspection only — git diff --name-only 88b1182..11cb644 vs plan.yaml lanes:, verified directly by qa" }
    - { id: SC-11, test: "inspection only — grep tempfile.TemporaryDirectory + git status --porcelain bracketed pre/post the full unit suite run, diff exit 0 byte-identical, verified directly by qa" }
    - { id: SC-12, test: ".claude/skills/harness/bin/test-layout-migration.py cases 14, 15 (paired)" }
    - { id: SC-13, test: ".claude/skills/harness/bin/test-layout-migration.py case 16 (empty-table cause) + case 1 (X+Y+Z==2 accounting clause)" }
    - { id: SC-14, test: ".claude/skills/harness/bin/test-layout-migration.py cases 3, 5a/5b" }
    - { id: SC-15, test: ".claude/skills/harness/bin/test-check-state.py case (x.1)" }
  open_questions:
    - { id: Q1, question: "No perturbation/mutation proof of the detector exists in this cycle (DEC-153 worktree proof was out of scope for an enforcement-only qa dispatch). Worth a follow-up dispatch before this detector becomes load-bearing for units 3-7, since a check that has never been shown to redden by deliberate mutation (as opposed to by hand-built fixtures) carries residual risk the brief itself names (issue #148 framing).", blocking: false }
  files_touched: [.harness/features/FEAT-20-migration-detector/notes/qa-c0.md]
  expertise_update: []
  cycles: 1
  must_fix: []
artifact: .harness/features/FEAT-20-migration-detector/notes/qa-c0.md
```
