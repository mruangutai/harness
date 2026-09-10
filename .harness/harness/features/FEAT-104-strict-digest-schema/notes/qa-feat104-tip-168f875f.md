# QA gate — FEAT-104, re-grade at branch tip `168f875f`

**This note SUPERSEDES `notes/qa-feat104-postfix-99035a9c.md`**, which graded `99035a9c`, a sibling
of the tip that the main session has since amended away. `168f875f` is the real, current branch
tip and is graded here in place, in the dispatched worktree.

## 1. Pin identity

```
$ git -C .../FEAT-104-strict-digest-schema rev-parse HEAD
168f875fba8d70c68694f7def4b9c10c3296ebd7
$ git -C .../FEAT-104-strict-digest-schema status --porcelain
(only untracked new notes/receipts from this cycle — zero tracked-file changes; tree clean)
$ git diff 78e34f06 168f875f --stat
62 files changed, 8760 insertions(+), 31 deletions(-)
```
HEAD is the commit under grade; the tracked tree is clean. Graded in place, no scratch worktree
created (none needed this cycle).

Per-file md5 across `6126ac07` (old review pin) / `99035a9c` (amended away) / `168f875f` (tip)
reproduces the dispatch's contract table exactly: `check-domain.sh`, `test-check-domain.py`,
`test-validate-digest.py` byte-identical `99035a9c`→`168f875f` (F1/F3 fixes present, unchanged);
`validate-digest.py` differs by exactly the F3 message-wording line (the `lead`-comment reword from
`99035a9c` is reverted, restoring the original wording); `check-state.sh` and `test-check-state.py`
are byte-identical to the **old pin** `6126ac07` — F2 is **not present** at the tip, confirmed
deliberate (§6), not an accidental revert.

## 2. Change type and required kinds

`plan.yaml` task `change_type`s (full feature diff, not this cycle's delta — Expertise P-13):
T-01/T-04/T-05/T-06/T-07/T-08 = `logic`; T-03/T-09 = `docs`; T-10 = `scaffolding`. `harness.json`
`test_matrix`: `logic.always = [unit]` **only** — no `when` clause exists for `logic` in this
project's matrix. `docs.always = []`, `scaffolding.always = []`. **The mechanical floor is `unit`
alone.**

`integration` is **qa-added**, not a floor line: F1/F2/F3 and all three gates' own regression tests
live under `tests/integration/`, the DEC-174 carve-out's own test suite for exactly the files this
feature touches, so presence-of-coverage is only checkable there.

**Advisory carried forward unchanged** (not re-derived — per dispatch): T-05 (`run-state-schema.json`,
a JSON schema file a gate script reads) is declared `change_type: logic` but plausibly meets
DEC-212's `touches_config_shape` predicate, which would obligate `integration` as a floor line
rather than a qa-added one; T-05's files are untouched between the last two grading cycles and this
one, so the advisory stands exactly as before.

**`matrix_ok: true`** — the one required kind (`unit`) is satisfied, the qa-added kind
(`integration`) is satisfied, every other kind resolves `not_applicable` against its own `detect`
surface (see §3).

## 3. Per-kind table

| kind | required? | runner state | command | exit | result / reason |
|---|---|---|---|---|---|
| unit | yes (`logic.always`) | active | `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | **satisfied** — 36 files, 2.25s wall |
| integration | qa-added | active | `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | **satisfied** — 70 files, 69.84s wall; F1/F3 cases pass (§5) |
| functional | no | excluded (DEC-187) | — | — | **not_applicable** — repo has no third bucket; diff adds nothing under `tests/functional/` |
| component | no | unresolved | — | — | **not_applicable** — diff touches no `*.spec.tsx`/`*.stories.tsx` |
| ui | no | unresolved | — | — | **not_applicable** — diff touches no `tests/e2e/**`, no interaction flow |
| eval | no | excluded (DEC-187) | — | — | **not_applicable** — only `ai_behavior.always` names it; this feature's types are `logic`/`docs`/`scaffolding` |
| typecheck | no | unresolved | — | — | **not_applicable** — diff touches no `*.ts`/`*.tsx` |
| omp_session_accessor | no | `locally_run` | `tests/manual/probe-omp-session-accessor.py` | not run | **not_applicable** — diff's detect surface (`inflight_registry.py` session-file resolution) untouched by `78e34f06..168f875f` |
| handoff_comprehension | no | `locally_run` | `tests/manual/probe-handoff-comprehension.py` | not run | **not_applicable** — diff does not change the handoff contract |
| issue_types_live | no | `locally_run` | `tests/manual/probe-issue-types.py` | not run | **not_applicable** — diff does not touch the issue-type path |

## 4. Complete canonical suite at `168f875f` (re-run required — check-state.sh/its test differ at the tip)

`env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh` (no `--kind`), from
the worktree root, exit captured into a variable (not through a pipe):

- `FULL_EXIT=0`. `pool: 8 workers, 106 files, 72.66s wall`.
- `grep -c '^FAIL '` on the full log: **4** lines, all attributed to
  `----- test-factory-claim-mutation.py (exit 0, 0.31s) -----`: `BASELINE 3/3 ok` → `MUTANT ACTIVE`
  → 3 `FAIL  BUG-1290 5a/5b/5c` lines (its own perturbation proof) → `MUTATION PROOF: 3/3 cases
  reddened` → `MUTANT KEY-COLLAPSE ACTIVE` → 1 more `FAIL  BUG-1290 5b` line → `KEY-COLLAPSE PROOF:
  ... printed` → `PASS test-factory-claim-mutation.py`. **All 4 are that file's own mutation-proof
  output, not a red signal** (repo Expertise G-08, project Expertise P-09).
- `--kind unit`: `UNIT_EXIT=0`, 36 files, 2.25s wall.
- `--kind integration`: `INTEG_EXIT=0`, 70 files, 69.84s wall, `ALL PASSED`.

This full re-run at `168f875f` was required and not duplicate work: `check-state.sh` and
`test-check-state.py` differ at the tip from `99035a9c` (the previously graded commit), so the
prior cycle's suite result does not transfer.

## 5. Fix-closure at the tip, by execution

**F1 — CLOSED.** `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` → exit
0, `12/12 T-06 check-domain cases passed`, `ALL PASSED`. Both required cases present and passing:
`schema_version floor refuses a version-2 checkpoint downgrade` (`ok`) and `schema_version floor
allows an existing version-1 update` (`ok`, SC-11/SC-15 compatibility preserved).

**F3 — CLOSED.** `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-validate-digest.py` →
exit 0, `34/34 T-04 undeclared digest key cases passed`, `ALL PASSED`. Read
`test-validate-digest.py:3130-3146` (`_t04_three_key_failures`): asserts the single undeclared-key
message contains all of `rogue_alpha`, `rogue_beta`, `rogue_gamma`, `digest contract is closed`,
`validate-digest.py`, `PASSTHROUGH`, `DOCUMENTED_OPTIONAL`, `SCHEMAS`.

**Re-read the emitted message directly at the tip** (its wording differs from what was graded at
`99035a9c` — the reworded `lead` comment was reverted, but the F3 message line itself is untouched).
Loaded the tip's own `validate-digest.py` as a module (no repo file touched) and called
`validate("harness-eng-lead", <rogue-key digest>)` directly. Verbatim emitted text:

> `undeclared digest key(s): 'rogue_alpha'. The digest contract is closed. Declare the field in
> .claude/skills/harness/bin/validate-digest.py: a lower-tier field carried by a lead belongs in
> PASSTHROUGH; a field in a persona's documented output block belongs in DOCUMENTED_OPTIONAL; a new
> required persona field belongs in SCHEMAS and must also be documented under DEC-216. A
> per-dispatch answer is not a digest key: put a PASS qualification in adequacy_notes or a per-step
> fact in the run state steps evidence container.`

Confirms the file token (`validate-digest.py`) and the three symbols (`PASSTHROUGH`,
`DOCUMENTED_OPTIONAL`, `SCHEMAS`) are all genuinely present in the live emitted string, not just in
the test's expectation.

**F2 — DECLINED WITH EVIDENCE, not an open defect.** See §6.

**`test-check-state.py` at the tip**: `env -u HARNESS_AGENT_TYPE python3
tests/integration/test-check-state.py` → exit 0, **3/3 T-07 undeclared step key cases passed**
(`version 1 produces no undeclared step key report`, `version 2 reports one undeclared step key
with run, step and key`, `version 2 declared keys plus evidence produce no report`). This is
byte-identical to the old pin `6126ac07` — the two `_digest_cases` present at `99035a9c` (which
pinned F2's persona-switch) are **absent**; nothing here exercises the digest/persona-selection
path at all (§8 spells out the resulting gap).

## 6. The F2 declination — reproduced evidence, not re-litigated

Declination is **settled** per dispatch: raw-persona validation in `check-state.sh`'s at-rest sweep
made an existing FEAT-104 run digest fail, stranding history under REQ-08/SC-12. Reproduced
directly rather than taken on relay.

`check-state.sh:1590` calls `_vd_mod.validate("lead", _dtext)` unconditionally in the at-rest sweep
— confirmed by reading the source at the tip (no persona-switch branch exists there; that logic
existed only in the amended-away `99035a9c`).

**Census of every completed run under `.harness/harness/features/FEAT-104-strict-digest-schema/runs/*/`
declaring `schema_version >= 2`** (excluding this cycle's own in-flight `2026-09-09-05` through
`2026-09-09-08`, listed separately below), calling the tip's `validate-digest.py` **twice** per
digest — once as `"lead"`, once as the run's own recorded `host` persona:

| run | host | `validate("lead", …)` errors | `validate(host, …)` errors | diverges? |
|---|---|---|---|---|
| `2026-09-09-01-t09-product` | `harness-product-lead` | 0 | 0 | no |
| `2026-09-09-02-qa-gate-validator` | `harness-validator-lead` | **0** | **1** | **YES** |
| `2026-09-09-03-simplify-eng` | `harness-eng-lead` | 0 | 0 | no |
| `2026-09-09-04-panel-validator` | `harness-validator-lead` | 0 | 0 | no |

**`2026-09-09-02-qa-gate-validator/digest.md` FAILS under the raw persona and passes only under
`"lead"`.** Its operative (last) `VERDICT:` block is a lead roll-up that carries `suite`,
`failures`, and `kinds` — QA-schema fields, not declared for a lead in `PASSTHROUGH`. Raw-persona
validation (`validate("harness-validator-lead", …)`) reports:

> `undeclared digest key(s): 'failures', 'kinds', 'suite'. The digest contract is closed. …`

Validating the same file as `"lead"` reports **zero** errors — the generic-`lead` exemption
(`validate-digest.py:1407`, `if raw_persona != "lead":`) is exactly what keeps this historical
record readable. This is the concrete case the declination's rationale describes: adopting F2 would
make `check-state.sh`'s at-rest sweep report this exact, already-completed FEAT-104 run as a
violation. The declination is evidenced, not merely asserted.

**In-flight run dirs, excluded from the verdict, reported separately (a sibling may be writing one
right now):**

| run | host | schema_version | status |
|---|---|---|---|
| `2026-09-09-05-qa-gate-validator` | `harness-validator-lead` | 2 | complete |
| `2026-09-09-06-simplify-eng` | `harness-eng-lead` | 2 | complete |
| `2026-09-09-07-qa-gate-validator` | `harness-validator-lead` | 2 | **running** (no `digest.md` yet at read time) |
| `2026-09-09-08-simplify-eng` | `harness-eng-lead` | 2 | complete |

Not read for content, not included in the divergence table above, and not allowed to decide this
gate.

## 7. Corrected census — the previous cycle's "measured no-op" conclusion is SCOPE-LIMITED, and its headline number is FALSIFIED for this feature

The prior note (`notes/qa-feat104-postfix-99035a9c.md` §8) censused **only the main checkout**
(`/Users/molchairuangutai/GitHub/harness/.harness/*/features/*/runs/*/`) and reported
`discovery: 309, strict_count: 0`, concluding F2's fix was "a measured no-op on today's data."
FEAT-104's own `runs/` tree is gitignored and **does not exist in the main checkout at all** —
confirmed: `ls .harness/harness/features/FEAT-104-strict-digest-schema/runs` from the main checkout
→ `No such file or directory`. A main-checkout-only sweep is structurally blind to every run this
feature has ever produced.

Re-taking the census from both roots (scratch script under `/tmp`, read-only, no repo file
touched):

- **Main checkout**: `discovery=310, strict_count=0`. (309→310 is a one-day corpus drift, not a
  discrepancy; the **conclusion for this root alone still holds** — no run outside this feature's
  own worktree declares `schema_version >= 2` yet, D-06 being FEAT-104's own convention, unmerged.)
- **Worktree** (FEAT-104's actual `runs/` tree): `discovery=17, strict_count=7` (4 completed
  non-in-flight strict runs + 3 completed in-flight strict runs, excluded from the verdict per §6).

**Corrected, worktree-scoped combined picture (excluding in-flight): `discovery=324,
strict_count=4`.** The previous cycle's `strict_count: 0` and its "measured no-op" conclusion are
**FALSIFIED for this feature** — not merely scope-limited prose, but a wrong number, because the
strict-schema runs the fix's own rationale is about live exclusively inside the worktree that census
never looked at. One of those four (`2026-09-09-02-qa-gate-validator`) is the exact case that
diverges under the raw persona (§6), which is the live demonstration the declination's rationale
requires and the prior cycle's conclusion asserted did not exist.

## 8. REQ-08 / SC-12 coverage judgement — COVERAGE GAP

With F2 declined, historical-digest readability (the generic-`lead` archive-reader compatibility
path) is **not bound by any test that can report RED at the tip**. `test-check-state.py` carries
zero `digest`/persona-selection cases (confirmed by direct grep — no match for `digest`,
`validate(`, or `lead` in that file at `168f875f`); its 3/3 T-07 cases are entirely about undeclared
*step* keys inside `state.yaml`, not about the digest-lint sweep's persona choice. SC-11/SC-12
(REQ-08's cited automated/inspection evidence) cover a different concern — writability of existing
`schema_version: 1` files and non-modification of run artifacts — neither exercises
`check-state.sh`'s call to `validate("lead", …)` on a digest.

**Concrete failure scenario:** a future change that removes or narrows the `raw_persona != "lead"`
guard in `validate-digest.py`, or that changes `check-state.sh` to pass a run's real host persona
instead of `"lead"`, would immediately break `2026-09-09-02-qa-gate-validator/digest.md` (§6) and
every future lead digest shaped like it — silently, since nothing in the standing suite exercises
this path.

**Named remedy for the main session** (report only, per DEC-174 — no test written here): add a case
to `tests/integration/test-check-state.py` that feeds the sweep a completed run's digest containing
lead-roll-up-shaped keys (e.g. `failures`/`kinds`/`suite`, as genuinely present in
`2026-09-09-02-qa-gate-validator`) and asserts `validate("lead", …)` reports no violation for it,
pinning the compatibility behavior explicitly instead of leaving it implicit in
`check-state.sh`'s hardcoded persona literal.

## 9. Assertion strength — F1 and F3

**F1** (`test-check-domain.py:152-159`): asserts **both** `downgrade.returncode == 2` **and**
`"schema_version downgrade" in downgrade.stderr`. A plausible regression — refusing with a different
message, or accepting the downgrade with exit 0 — reddens this either way. Not a bare presence
check; discriminates.

**F3** (`test-validate-digest.py:3130-3146`): asserts the message string contains all three rogue
key names, the phrase `digest contract is closed`, and all four route tokens (`validate-digest.py`,
`PASSTHROUGH`, `DOCUMENTED_OPTIONAL`, `SCHEMAS`), and separately (line 3135) asserts exactly **one**
message is produced for three rogue keys (`len(errors) != 1` fails the case). A regression that
narrowed the message to name only the three symbols and drop the file token — exactly SC-08's prior
gap — reddens this case, since `"validate-digest.py"` is checked as its own required token. Green
here discriminates the specific regression class it targets.

## 10. SC re-audit (narrowed to what the tip's diff touches)

- **SC-01** (a `lead` return carrying `foo_bar: 1` exits 2, names `foo_bar`) — still asserted by
  T-04's undeclared-key cases (34/34). Satisfied.
- **SC-02** (per-persona SCHEMAS rejection, one case per persona) — 55/55 T-01 schema cases + 34/34
  T-04 cases pass. Satisfied.
- **SC-03** (`check-domain.sh` refuses an undeclared `steps[]` key at `schema_version: 2`, names the
  key) — covered, part of the 12/12 T-06 cases. Satisfied.
- **SC-07** (three unknown keys → one rejection naming all three) — T-04's three-key case still
  1 message, all three keys named (§9). Satisfied.
- **SC-08** (rejection names the declaration route **by file and by symbol**, asserted as a
  substring) — **both halves true at the tip.** Emitted: verbatim message quoted in §5 names the
  file (`.claude/skills/harness/bin/validate-digest.py`) alongside the three symbols. Asserted:
  `test-validate-digest.py:3140` requires the literal token `"validate-digest.py"` in the three-key
  message next to the three symbol tokens. Satisfied.
- **SC-11** (undeclared step key accepted on update to existing `schema_version: 1`, refused at
  `schema_version: 2`) — 12/12 T-06 cases include both directions; F1's downgrade case confirms the
  version-1 update path is undisturbed. Satisfied.
- **SC-12** (no historical run artifact modified; T-10's manifest re-hash) — out of this gate's
  direct execution (`verify: inspection`), not re-run here; no tracked file under any `runs/` tree
  was touched by this grading session (read-only sweep). Not evaluated as a pass/fail by qa; noted
  as inspection-only per its own `verify:` tag.
- **SC-15** (four `schema_version` floor fixtures) — all four pass, part of the 12/12 T-06 cases.
  Satisfied.
- **SC-13** (`verify: uat`) — **out of scope for this gate**, not evaluated.

## Coverage gaps / findings summary

1. **Coverage gap (§8)**: REQ-08's generic-`lead` archive-reader exemption has zero automated
   coverage able to redden; remedy named for main session, not implemented here (DEC-174).
2. **Carried-forward advisory (§2)**: T-05's `change_type: logic` vs. DEC-212's
   `touches_config_shape` predicate — unresolved, unchanged, not re-derived at length.
3. No other gaps found. F1 and F3 are closed by executed evidence; F2's declination is evidenced,
   not an open defect.

```yaml
VERDICT: PASS
DIGEST:
  headline: "QA gate PASSES at tip 168f875f: matrix_ok=true (unit+integration both green, exit 0), F1 and F3 CLOSED by executed evidence, F2 DECLINED-WITH-EVIDENCE (reproduced the exact stranding case on 2026-09-09-02-qa-gate-validator); corrected worktree-scoped census FALSIFIES the prior cycle's strict_count:0/no-op conclusion (true count is 4, not 0) — one gap named (REQ-08 digest-lint exemption uncovered) and routed to main."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 36 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 70 }
    - { kind: functional, state: not_applicable, cmd: none }
    - { kind: component, state: not_applicable, cmd: none }
    - { kind: ui, state: not_applicable, cmd: none }
    - { kind: eval, state: not_applicable, cmd: none }
    - { kind: typecheck, state: not_applicable, cmd: none }
    - { kind: omp_session_accessor, state: not_applicable, cmd: none }
    - { kind: handoff_comprehension, state: not_applicable, cmd: none }
    - { kind: issue_types_live, state: not_applicable, cmd: none }
  coverage_gaps:
    - "REQ-08's generic-`lead` archive-reader exemption (validate-digest.py:1407, check-state.sh:1590) has zero test coverage able to report RED — test-check-state.py carries no digest/persona case at all. Concrete failure: a future narrowing of the exemption would silently break 2026-09-09-02-qa-gate-validator/digest.md and every future lead digest shaped like it. Remedy named for main session in §8; not implemented (DEC-174)."
    - "T-05 change_type: logic vs. DEC-212 touches_config_shape predicate — carried-forward advisory, unresolved, not re-derived (unchanged since last two cycles)."
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-validate-digest.py:_t04_documented_failures + rogue-key cases" }
    - { id: SC-02, test: "tests/integration/test-validate-digest.py run_t01_schema_cases (55/55) + T-04 (34/34)" }
    - { id: SC-03, test: "tests/integration/test-check-domain.py (12/12 T-06 cases)" }
    - { id: SC-07, test: "tests/integration/test-validate-digest.py:3130-3146 _t04_three_key_failures" }
    - { id: SC-08, test: "tests/integration/test-validate-digest.py:3140 (validate-digest.py file token assertion)" }
    - { id: SC-11, test: "tests/integration/test-check-domain.py (12/12 T-06 cases, both directions)" }
    - { id: SC-12, test: "T-10 manifest re-hash, verify: inspection — not executed by qa" }
    - { id: SC-15, test: "tests/integration/test-check-domain.py (12/12 T-06 cases, four floor fixtures)" }
  open_questions:
    - { id: Q1, question: "REQ-08's generic-lead digest exemption has no test that can redden it. Should test-check-state.py gain a case pinning that a completed lead digest carrying lower-tier roll-up keys (e.g. failures/kinds/suite, as seen live in 2026-09-09-02-qa-gate-validator) is accepted under validate('lead', ...)? See §8 for the concrete break scenario.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-104-strict-digest-schema/notes/qa-feat104-tip-168f875f.md
```
