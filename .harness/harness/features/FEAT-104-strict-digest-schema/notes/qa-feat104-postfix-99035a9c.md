# QA gate — FEAT-104, post-fix re-validation of 99035a9c

## HEADLINE — BLOCKING DIVERGENCE FOUND FIRST

**The dispatched worktree's actual HEAD is NOT `99035a9c`.** `git -C
.claude/worktrees/harness/FEAT-104-strict-digest-schema rev-parse HEAD` returns
`168f875fba8d70c68694f7def4b9c10c3296ebd7` ("fix(feat-104): close downgrade and
declaration-route gaps"), a **sibling** of `99035a9c` — both are children of `16887ff0`,
neither is an ancestor of the other (`git merge-base --is-ancestor` both directions: NO).
`git diff 99035a9c 168f875f --stat` shows `168f875f` **reverts the F2 fix**: `check-state.sh`'s
persona-switch block (`_version`/`_persona` computed from `schema_version`) is deleted and
replaced with a hardcoded `_vd_mod.validate("lead", _dtext)`, and `test-check-state.py`'s two
`_digest_cases` (the F2 regression tests) are deleted outright, along with the `_step_cases`/
`_report` refactor structure. **`validate-digest.py`'s F3 fix (the file-token wording) is
unaffected** — that hunk is identical at both commits; only `check-state.sh` + its test changed.

I raised this to `Feat104Revalidate.Simplify104` and `Feat104Revalidate.Qa104Gate` before
proceeding. Simplify104 confirmed by return message: its squad authored **no commit** this run
(DEC-174 NOBODY carve-out, flag-only, no shell), so `168f875f` did not come from eng, and
instructed me to grade `99035a9c` specifically (the SHA both segments were dispatched against)
while reporting the divergence prominently — which this note does. **Origin of `168f875f` is
unknown to both segments that examined it.** Whatever the main session pins as `review_sha` MUST
reconcile this before shipping: if `168f875f` (or its parent tip) becomes the pin, F2 is OPEN
again and this whole gate must re-run against it.

To grade the actual assigned commit without moving the dispatched worktree's HEAD, I created a
disposable detached worktree pinned to `99035a9c`:
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/qa-feat104-99035a9c`
(`git worktree add --detach ... 99035a9c`; `git rev-parse HEAD` there = `99035a9c`, tree clean).
All commands below ran there unless marked "main checkout". The dispatched worktree's HEAD was
never touched.

## 1. Pin identity

- `git -C .../FEAT-104-strict-digest-schema status --porcelain` → empty (clean) — but HEAD is
  `168f875f`, not `99035a9c` (see above).
- `git -C .../qa-feat104-99035a9c rev-parse HEAD` → `99035a9c2bbda83c16191562b94e58e860e180a6`,
  `git status --porcelain` → empty. **This is the tree graded below.**
- `git diff 78e34f06 99035a9c --stat` (from the assigned worktree, read-only) confirms
  `78e34f06` is the merge-base and the diff is the full feature diff (62 files, +8826/-32).

## 2. Change type and required kinds

`plan.yaml` task `change_type`s: T-01/T-04/T-05/T-06/T-07/T-08 = `logic`; T-03/T-09 = `docs`;
T-10 = `scaffolding`. `harness.json` `test_matrix`: `logic.always = [unit]` only (no `when`
clause fires for this project's `logic` template); `docs.always = []`; `scaffolding.always = []`.
**The mechanical floor from the matrix is `unit` alone.**

The fix delta `6126ac07..99035a9c` is itself a `bugfix` to runtime gate code
(`check-domain.sh`, `validate-digest.py`) plus their own tests. `bugfix.when`: `unit` if
`touches_runtime_code` (true — fires, still just `unit`); `integration` if
`fix_confined_to_tests_and_contract_docs` (false — the fix touches runtime code, not only tests/
docs, so this leg does not fire); `__bug_class__` via `match_bug_class` is an unresolved
placeholder repo-wide (no bug-class taxonomy entry exists), per repository Expertise G-08 — it
never fires for any diff yet and does not add a requirement here. **`bugfix` classification adds
nothing beyond `unit`.**

I am **adding `integration` myself**, not reading it off the matrix: F1/F2/F3 and all three
gates' own regression tests (`test-check-domain.py`, `test-check-state.py`,
`test-validate-digest.py`) live under `tests/integration/`, and per DEC-174 they are the carve-
out's own test suite for the exact files this fix touches. Presence of coverage for this specific
fix is only checkable there.

**Advisory carried forward from `notes/qa-feat104-c7.md`** (prior QA note at the old pin): T-05
(`run-state-schema.json`, a JSON schema file a gate script reads) is declared `change_type: logic`
but plausibly meets DEC-212's `touches_config_shape` predicate (a value's container-type/required-
ness/structural nesting change in a config a gate reads), which would obligate `integration` as a
floor line rather than a qa-added one. Not re-derived at length here; unchanged since the last
note and not affected by this fix cycle (T-05 files are untouched between `6126ac07` and
`99035a9c`).

## 3. Per-kind results

| kind | required? | runner state | command | exit | result |
|---|---|---|---|---|---|
| unit | yes (`logic.always`) | active | `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | **satisfied** — 36 files, 4 `^FAIL ` lines, all `test-factory-claim-mutation.py`'s own mutation-proof output (§4) |
| integration | qa-added (not floor) | active | `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | **satisfied** — 70 files, 0 `^FAIL ` lines; F1/F2/F3 cases all pass (§5) |
| functional | no | excluded (DEC-187) | — | — | **not_applicable** — repo has no service-API third bucket; unit/integration already split the suite, and this diff adds nothing under `tests/functional/` |
| component | no | unresolved | — | — | **not_applicable** — not named by `logic`/`docs`/`scaffolding`; diff adds/changes no `*.spec.tsx`/`*.stories.tsx` |
| ui | no | unresolved | — | — | **not_applicable** — not named by matrix; diff touches no `tests/e2e/**`/`*.e2e.spec.ts`, no interaction flow |
| eval | no | excluded (DEC-187) | — | — | **not_applicable** — only `ai_behavior.always` names it; this feature's change_types are `logic`/`docs`/`scaffolding` |
| typecheck | no | unresolved, not in matrix | — | — | **not_applicable** — diff touches no `*.ts`/`*.tsx` |
| omp_session_accessor | no | locally_run | `tests/manual/probe-omp-session-accessor.py` | not run | **not_applicable** — diff's detect surface for this kind (`inflight_registry.py` session-file resolution) is untouched by `78e34f06..99035a9c` |
| handoff_comprehension | no | locally_run | `tests/manual/probe-handoff-comprehension.py` | not run | **not_applicable** — diff does not change the handoff contract this probe exercises |
| issue_types_live | no | locally_run | `tests/manual/probe-issue-types.py` | not run | **not_applicable** — diff does not touch the issue-type path |

`matrix_ok: true` — the one required kind (`unit`) is satisfied, the qa-added kind
(`integration`) is satisfied, and every other kind's `not_applicable` is reasoned against its own
`detect` surface, not merely asserted.

## 4. Complete canonical suite (worktree pinned to `99035a9c`)

`env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh` (no `--kind`
filter), from the worktree root:
- Exit status captured to a variable: `FULL_EXIT=0`.
- `106 files`, `pool: 8 workers`, wall time `75.54s` (runner's own report).
- `grep -c '^FAIL '` on the full log: **4** lines. All 4 attributed by reading the surrounding
  block: `----- test-factory-claim-mutation.py (exit 0, 0.38s) -----` → `BASELINE 3/3 ok` →
  `MUTANT ACTIVE` → 3 `FAIL  BUG-1290 5a/5b/5c` lines (its own perturbation proof, deliberately
  printed) → `MUTATION PROOF: 3/3 cases reddened` → `MUTANT KEY-COLLAPSE ACTIVE` → 1 more
  `FAIL  BUG-1290 5b` line → `KEY-COLLAPSE PROOF: ... printed` → `PASS test-factory-claim-
  mutation.py`. **All 4 are that file's own mutation-proof output, not a red signal** (repo
  Expertise G-08, project Expertise P-09).
- `--kind unit`: `UNIT_EXIT=0`, 36 files, same 4 FAIL lines (same file, same attribution).
- `--kind integration`: `INT_EXIT=0`, 70 files, 0 FAIL lines, wall `78.23s`, `pool: 8 workers`.

## 5. Fix-closure evidence — F1, F2, F3

**F1 — CLOSED.** `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` →
exit 0, `12/12 T-06 check-domain cases passed`, `ALL PASSED`. The specific case
`schema_version floor refuses a version-2 checkpoint downgrade` is present and passing; the
sibling `schema_version floor allows an existing version-1 update` also passes (SC-11/SC-15
compatibility preserved). Read `check-domain.sh:1760-1779`: on an existing checkpoint with
`schema_version >= 2` (int, non-bool), a proposed write with a lower/non-int/bool version is
refused, `exit 2`, message head `"schema_version downgrade for a run checkpoint."`. This closes
the pre-fix witness from `f08aad49` (11/12, downgrade accepted where refusal was expected).

**F2 — CLOSED**, graded at `99035a9c` (see HEADLINE for why this is graded there and not at the
worktree's actual tip). `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-state.py`
→ exit 0, `5/5 T-07 undeclared step key cases passed`, `ALL PASSED`. Both new `_digest_cases`
pass: `completed lead digest is closed against its raw persona` and `historical version-1 lead
digest remains readable`; both `_step_cases` remnants (3 of them) also pass. Read
`check-state.sh:1587-1598`: `_persona = _host if (int, non-bool, >=2) else "lead"`, then
`_vd_mod.validate(_persona, _dtext)`.

**F3 — CLOSED.** `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-validate-digest.py` →
exit 0, `34/34 T-04 undeclared digest key cases passed`, overall `ALL PASSED.` The T-04 three-key
case (`_t04_three_key_failures`, line 3130) asserts the single undeclared-key message contains
**all** of: `rogue_alpha`, `rogue_beta`, `rogue_gamma`, `digest contract is closed`,
`validate-digest.py`, `PASSTHROUGH`, `DOCUMENTED_OPTIONAL`, `SCHEMAS` — the `validate-digest.py`
file token is asserted alongside the three symbols, matching F3's fix
(`validate-digest.py:1401-1421`, the message now reads "Declare the field in
`.claude/skills/harness/bin/validate-digest.py`: ...").

## 6. Assertion strength — read, and measured where reading alone was insufficient

(a) **F1 downgrade case asserts BOTH exit code and message substring** — read directly at
`test-check-domain.py:157-159`: `downgrade.returncode == 2 and "schema_version downgrade" in
downgrade.stderr`. Not a bare presence check; a plausible regression (refusing but with a
different message, or accepting with exit 0) reddens it either way.

(b) **F2's strict-case PASS is caused by the persona switch, not an unrelated rejection path** —
established by **direct measurement**, not reasoning alone, since the source-edit ban prevents an
in-place mutation proof and this claim is exactly the kind Expertise O-08/P-07 warn must not be
taken on faith. I loaded the worktree's own (unmodified) `validate-digest.py` as a module in a
scratch script under `/tmp` (no repo file touched) and called `validate()` directly against the
test's own `rogue_digest` fixture with each candidate persona:
  - `validate("harness-product-lead", rogue_digest)` → `["undeclared digest key(s): 'rogue_key'. The digest contract is closed. Declare the field in .claude/skills/harness/bin/validate-digest.py: ..."]`
  - `validate("lead", rogue_digest)` → `[]`
  This confirms the strict case's failure is *specifically* the undeclared-key rejection firing
  on `rogue_key` once the raw persona is `harness-product-lead` rather than the generic `lead`
  compatibility persona (`validate-digest.py:1407`, `if raw_persona != "lead":` gates the
  undeclared-key sweep entirely) — not some unrelated cause (e.g. a missing-field or type error
  that happens to redden regardless of persona). A regression that silently kept passing `"lead"`
  to `validate()` at the strict branch would make this scratch call at `"harness-product-lead"`
  come back `[]` too — this reddens under that mutation.

No gap found in either T-06's or T-07's or T-04's new/changed cases.

## 7. SC re-audit (narrowed to fix-touched criteria)

- **SC-01** (`lead` return with `foo_bar: 1` rejected, exit 2, names `foo_bar`) — unaffected by
  this fix cycle; still asserted by T-04's undeclared-key cases. Satisfied.
- **SC-02** (per-persona SCHEMAS rejection, one case per persona) — unaffected; 55/55 T-01 schema
  cases + 34/34 T-04 cases still pass. Satisfied.
- **SC-03** (`check-domain.sh` refuses an undeclared `steps[]` key at `schema_version: 2`, names
  the key) — unaffected by F1's downgrade addition (different code path); still covered, 12/12.
  Satisfied.
- **SC-07** (three unknown keys → one rejection naming all three) — unaffected; T-04's three-key
  case still 1 message, all three keys named. Satisfied.
- **SC-08** (rejection names the declaration route **by file and by symbol**, asserted as a
  substring) — **this is F3's whole complaint, now both EMITTED and ASSERTED.** Emitted:
  `validate-digest.py:1401-1421`'s message names the file (`.claude/skills/harness/bin/validate-
  digest.py`) alongside the three symbols (`PASSTHROUGH`, `DOCUMENTED_OPTIONAL`, `SCHEMAS`).
  Asserted: `test-validate-digest.py:3140` requires the literal token `"validate-digest.py"` in
  the three-key message, next to the three symbol tokens. Satisfied.
- **SC-11** (undeclared step key accepted on an update to an existing `schema_version: 1` file,
  refused at `schema_version: 2`) — covered by `test-check-domain.py`'s `_step_cases` (unchanged
  by this fix) plus the sibling downgrade case confirming F1 did not narrow the version-1 update
  path. Satisfied.
- **SC-15** (four `schema_version` floor fixtures: omit/`1`/string-`"2"` refused at creation;
  `2` accepted at creation; update to existing v1 accepted) — all four still pass; F1 adds a
  **fifth** fixture (v2→v1 downgrade on update) that SC-15's text does not name but the panel
  finding demanded. Satisfied, plus the F1 addition.
- **SC-12** (`verify: inspection`) and **SC-13** (`verify: uat`) — **out of scope for this gate**,
  not evaluated.

## 8. Regression sweep on check-state.sh's own consumers (main checkout corpus)

Running the *worktree's* fixed `check-state.sh` directly resolves its root from its own on-disk
location (`harness_boundary.resolve_root`, FEAT-42 T-12) — measured: it resolves to the worktree
itself, not the main checkout, so it cannot sweep the main checkout's real run corpus without
being copied there (which DEC-174 forbids). Running the **main checkout's own** (pre-fix, un-
merged) `check-state.sh` doesn't test the fix at all. So I built a read-only scratch comparison
(`/tmp/qa104-sweep/sweep_compare.py`, outside the repo, no file written to any checkout) that
replicates the sweep's exact persona-selection logic against the main checkout's real corpus,
using the worktree's fixed `validate-digest.py` as the validator:

- **Discovery count: 309** completed lead digests found under
  `/Users/molchairuangutai/GitHub/harness/.harness/*/features/*/runs/*/{state.yaml,digest.md}`
  (non-empty; this is a real sweep, not an empty-set false-clean).
  Of these, **`strict_count = 0`** — no run in the current main-checkout corpus declares
  `schema_version >= 2` yet (D-06: schema_version 2 is FEAT-104's own convention, not yet merged
  to `main`), so the persona-switch's `_host` branch is never taken for a single one of the 309
  real records; every one still resolves to the legacy `"lead"` persona under the new logic,
  identically to the old always-`"lead"` behavior.
- `old_persona_always_lead_fail_count = 9`, `new_persona_switch_fail_count = 9`,
  **`NEW_REGRESSIONS = 0`** (no digest that passed under old-persona now fails under new-persona,
  and vice versa — verified pairwise per record, not just by matching totals).
- The 9 pre-existing failures (identical error text under both old and new persona) are legacy
  drift unrelated to this fix: 8 are `severity_max='info' is not in [...]` (a documented-but-
  illegal enum value from historical validator runs, predating DEC-208's `info`→`none`
  correction) and 1 is a `matrix_ok` type mismatch in an old FEAT-30 run. None involve
  `rogue_key`-class undeclared-field rejection, and none are newly caused by this fix.
- **No new digest-contract violation.** Not a BLOCKING finding — the fix is a no-op on the real
  historical corpus by construction (D-06), confirmed by measurement rather than assumed from the
  decision text.
- Five INV-29 standing-worktree violations observed separately (`check-state.sh` run from the
  main checkout, unrelated invariant) — `BUG-1480-handoff-note-checkout-root`,
  `BUG-201-depends-on-integrity`, `BUG-440-digest-verdict-reconciliation`,
  `FEAT-55-issue-types-created-work`, and one unresolvable-path worktree
  (`qa-bug440-c3-probe`) — are **pre-existing, from other features, and NOT this feature's
  defect**; named here only to exclude them from this gate's finding set per dispatch.

## Coverage gaps / findings

None found beyond the HEADLINE divergence (which is a coordination/process finding, not a code
defect in `99035a9c` itself) and the carried-forward T-05 `change_type` advisory (§2). No code
change is recommended from this run — F1/F2/F3 are all closed as measured above.
