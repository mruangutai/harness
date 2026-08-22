# plan3-amend — the six rulings landed, and the receipt

**All ten pre-written acceptance criteria PASS.** `plan.yaml` went from 10 tasks / 16 decisions at
7299669 to **14 tasks / 22 decisions**, `approval:` byte-identical and still `pending`.
`check-plan-routes.py` exits **0, 0 violations**. Every number below names its checkout and sha
(C-7).

Everything measured in the **FEAT-31 worktree at 7299669** unless stated otherwise.

## Ruling → id map (criterion 4 and 10)

| Ruling | Tasks | Decisions |
|---|---|---|
| A-1 (SC-01 keeps `automated`; C-1's door) | T-07 (fixture half), **T-13** (live half) | D-09 amended, **D-17** |
| A-2 (INV-17 globs every handoff note) | **T-14** (sibling), T-10 (reordered onto it) | **D-20** |
| A-3 (SC-15 = T-10 + hand grading) | T-10 | D-16 pointer, **D-21** |
| F-1 (T-07's file misclassified) | **T-11** | **D-18** |
| D-4(a) the eight | **T-11** | **D-18** |
| D-4(b) the check | **T-12** | **D-19**, **D-22** (Q-A default) |
| C-4 (BRIEF SC-14 mechanism) | BRIEF.md lines 188-189 → 188-191 | D-20 |

## The eight, enumerated and measured at 7299669 (D-4a)

`INTEGRATION_SCRIPTS` in `run-unit-tests.sh` holds **12**; `test_kinds.integration.detect` names
**4** of them (`test-check-state.py`, `test-factory-integration.py`, `test-gh-sync.py`,
`test-check-plan-routes.py`). The **8 absent**, each therefore classified `unit` by
`unit.detect`'s catch-all `.claude/skills/harness/bin/test-*.py`:

1. `test-validate-digest.py` 2. `test-check-expertise.py` 3. `test-gen-decisions-index.py`
4. `test-bash-write-guard.py` 5. `test-check-domain.py` 6. `test-harness-yaml.py`
7. `test-upgrade-config.py` 8. `test-merge-settings.py`

T-11 appends **ten**: those eight + `test-context-watch-cli.py` (F-1's instance) +
`test-run-unit-tests-kinds.py` (T-12's own test — the self-reference, resolved).

**The T-05 interaction is resolved, not invented around.** `test-upgrade-config.py` is one of the
eight and T-05 edits it, but T-05's agent is `harness-backend-dev` and
`check-domain.sh --resolve .harness/harness.json` returns **`harness-dev-ops` alone** at 7299669.
So T-05 gets a "DO NOT EDIT harness.json here, T-11 owns it" clause and T-07 gets the same plus
`depends_on: [T-11]`. **The split is forced by the grant, not chosen** — putting `harness.json` on
T-07 as F-1 literally instructed would make `check-plan-routes.py` report a DEVIATION.

**Class: CLOSED and costed.** 1 new task, 1 config file, 10 string appends, no code. The template
`.claude/skills/harness/templates/harness.json` is deliberately untouched: its `integration.detect`
is `tests/integration/**` with `cmd: null` at 7299669, so propagating ten paths naming *this*
repo's bin tests would ship a fresh project ten globs matching nothing. Sweep of all 10 pre-existing
tasks recorded in D-18: only T-02 (agrees via the catch-all), T-05 and T-07 (fixed by T-11) and
T-10 (already explicit) are in scope; no other task creates or moves a test file.

## D-4(b) — the check, and why it can go red on the *mismatch*

T-12 puts the cross-check **inside `run-unit-tests.sh`** with a `--check-kinds` mode.
The rule is a **set comparison, not a classifier**: every `INTEGRATION_SCRIPTS` name must be an
explicit literal path in `integration.detect`; no `UNIT_SCRIPTS` name may be. That deliberately
avoids depending on Q-B's unwritten precedence rule.

Red proof asserts the **named file in the message**, never an exit code: a mutant `harness.json` in
a tmpdir with `test-check-state.py` removed from `integration.detect`, mutation asserted applied
(both texts differ *and* the path present-in-original / absent-in-mutant), then
`HARNESS_JSON=<mutant> --check-kinds` must emit a `KIND-DRIFT` line **containing the literal
`test-check-state.py`**, with the KIND-DRIFT line count exactly 1 against case 1's 0. Non-zero exit
without that named line is reported **INCONCLUSIVE**. Case 3 proves the reverse direction; case 4
proves an unreadable config is loud, not skipped.

## A-1's door (C-1), chosen with its cost

SC-01 keeps `verify: automated, evidence: integration`. Fixture half = **T-07**. Live half =
**T-13**, `.claude/skills/harness/bin/verify-context-watch-live.py` — **deliberately not**
`test-*.py`, because the drift detector loops `for f in "$BIN_DIR"/test-*.py` and a
differently-named file never reaches it. The "skip loudly" variant is rejected in D-17 on
`tests.yml:78,84` (both kinds are required steps, so a printed skip inside one is a green suite that
verified nothing). **Cost, named:** the file matches no `test_kinds` detect glob at 7299669, so it
sits outside the test matrix and outside `tests.yml`, and nothing runs it unless an agent is told
to. T-13's `--self-test` gives it an automatable `verify:` so the plumbing is not wholly unexercised.

## A-2 — sibling, and C-3 resolved BY STRUCTURE

**Sibling task T-14, running BEFORE T-10** (`T-10.depends_on: [T-14]`). Reason recorded in D-20: a
fold makes a failed refactor indistinguishable from a failed empty-body check, and T-14-first means
T-10's check is written **once**, into the single extracted site, instead of inside the loop and then
moved.

C-3 resolved **by structure**: the `for prev in SEAM_NOTES[_status]` loop (`check-state.sh:592`)
keeps only the missing-note branch; the shape check moves out into one glob pass over
`notes/handoff-*.md` marked `# INV-17 handoff shape pass, all stems (FEAT-31 T-14)`. One call site +
a glob that finds seam-stem files too ⇒ **no file can be reported twice by construction**, not by a
rule someone must remember. `SEAM_NOTES` (`check-state.sh:495`) unchanged; stems never derived (the
comment at `:475-481`); `HANDOFF_HEADINGS` (`:509`) and the 60-line cap unchanged; failures stay
`bad.append` VIOLATIONs. `HANDOFF_EXEMPT_LITERAL` (`:523`) and `_handoff_exempt` (`:525`) gate only
the missing-note branch — case G asserts that.

**Migration receipt, attached to T-14.** In the FEAT-31 worktree at 7299669: **69** files match
`.harness/harness/features/*/notes/handoff-*.md` — 66 seam stems (25 `plan`, 21 `build`,
20 `validate`) and **3 non-seam**: `FEAT-09-plan-time-route-check/notes/handoff-ship.md` (56 lines),
`FEAT-22-docs-layout-migration/notes/handoff-t09-rotation.md` (50),
`FEAT-24-config-responsibility-split/notes/handoff-ship.md` (60 — exactly on the cap, no headroom).
All three carry all four headings, all within the cap ⇒ **zero new violations**. The main checkout
reads 71 at its own HEAD; it reconciles exactly (FEAT-30's three notes there and not here, minus
FEAT-31's own `handoff-plan.md` here and not there).

**C-5 confirmed, no finding.** Non-blank lines under `## Next`, measured here at 7299669:
**13 / 6 / 8** for those three files respectively. None fails T-10's not-yet-existing empty-body
rule. Recorded in T-10's intent as a re-assert-at-your-sha instruction, not a re-derivation.

## C-6 applied

`RE_HANDOFF` is at **`check-domain.sh:665`** in this worktree (`:706` is the main checkout, a
different branch). `SEAM_NOTES` at **`check-state.sh:495`**. T-10's stale `6f651f1` line citations
(509 / 614 / 474) were rewritten symbol-first, with an explicit warning that T-14 moves the code so
the numbers will not hold when T-10's doer arrives.

## A-3 / C-4 — what was NOT edited, and why

`BRIEF.md` is **approved** (`status: approved, operator, 2026-08-21`). Only C-4's SC-14 rewrite was
authorised, so **SC-15's text is untouched** and A-3 is recorded in **D-21** instead. D-21 names the
consequence out loud: a goal-check reading `BRIEF.md` alone would report SC-15 as fully automated,
which is **false** — the behaviour half is `not_met` until the hand grading is recorded alongside
SC-10.

## Verification receipt

- `harness_yaml.load_file` → OK, `schema: plan/1`; **tasks 14, decisions 22,
  `approval.status: pending`** (measured output).
- `approval:` block (plan.yaml lines 4-7): `cmp` against `git show 7299669:` → **identical bytes**;
  `git diff -U0` hunks start at line 10 — none touches 4-7.
- `BRIEF.md ## Approval`: md5 `1f9596505ded3edd18ba69fc9ef7f565` before and after.
- `check-plan-routes.py <this plan>` → **exit 0, "0 violation(s) across 1 plan(s)"**, 14 task lines.
  Repo-wide (no args) → **exit 0, "0 violation(s) across 4 plan(s)"**, and it examines this plan
  (its output carries `DEVIATION T-12 … test-run-unit-tests-kinds.py`, a string unique to this
  feature). Advisory DEVIATIONs went 1 → 4 (T-10 at baseline; + T-12, T-14 new; T-10 retained) —
  all three are declared `main-session-direct` on granted paths, which is the intended DEC-174 shape.
- `check-state.sh` → exit 1 with **9 violations, none for FEAT-31**; the only FEAT-31 line is the
  expected `plan.yaml approval is pending — awaiting the user` note.
- BRIEF diff: exactly `-2 / +4` lines, at lines 188-189 (old) → 188-191 (new). Listed below.

### Every changed BRIEF line (C-4)

Removed (lines 188-189 at 7299669):
```
  the stem is not one of `plan`, `build` or `validate`, INV-17 accepts that shape too — asserted by a
  test that fails before INV-17's seam table learns the mid-phase stem.
```
Added (lines 188-191 now):
```
  the stem is not one of `plan`, `build` or `validate`, INV-17 shape-checks that note too — asserted
  by a test that fails before INV-17's shape check reaches a handoff note whose stem `SEAM_NOTES`
  does not name. `SEAM_NOTES` itself stays unchanged: which notes are REQUIRED is a separate
  question from which notes are shape-checked.
```
SC-14's `verify: automated      evidence: integration` line, SC-15 and `## Approval` are untouched.

## Open questions — the operator's, carried not resolved

- **Q-A (blocking=false).** Is `harness.json`'s `test_kinds` enforcement layer under DEC-174?
  **Default adopted, in D-22:** the data entries → `team`/`harness-dev-ops` (T-11); the new check and
  its test → `main-session-direct` (T-12). Rests on `DECISIONS.md:4856-4859` (a module a gate imports
  is not itself a gate; the cutover that makes a gate use it is main-session-direct) and
  `:4851-4854` (the list names five *scripts* and their tests; the category decides, the list
  records). Three corroborations: the grant exists (`--resolve` → `harness-dev-ops`), T-03 already
  edits that file as `team`, and ruling otherwise retroactively invalidates T-03's lane. Overrulable
  in one read.
- **Q-B (blocking=false).** Is "explicit list beats catch-all glob" written down anywhere? Four
  files sit in both `unit.detect` and `integration.detect` at 7299669 and are treated as
  integration, so precedent is clear, but it is stated nowhere and there is no programmatic
  classifier. **T-12 was designed so its correctness does NOT rest on it** (a set comparison, no
  glob matching), but the *fix's* meaning still does. Recommend writing it down as a decision.

## Notes for whoever reads next

- A plain-scalar `: ` broke the first write (`2026-08-21: automated` in D-09) — caught by
  `harness_yaml.load_file`, not by eye. Nine decision/reason lines were repaired before the load
  passed. A plan.yaml that "looks right" is not a plan.yaml that parses.
- D-06 is **not** contradicted by D-19. Its stated basis is that an array append changes no gate
  rule; T-02 and T-07 stay `team` on exactly that basis. T-12 changes what the runner *rejects*,
  which D-06 never covered. The `lanes:` row for `run-unit-tests.sh` now records both lanes by edit
  kind.
- `lanes.resolved_at` moved `6f651f1` → `7299669`: all 14 pre-existing rows were re-resolved with
  `check-domain.sh --resolve` and every one was unchanged; 2 rows added.
