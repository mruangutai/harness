# QA final coverage — FEAT-14 feature.json schema

Status: DRAFT (Phase 1 blind derivation, written before opening plan/hand-downs/source)

## Phase 1 — expected coverage, derived from BRIEF.md lines 385-529 only

- SC-01: unit — validate all 17 `feature.json` against schema; assert no key outside the 11; no `phase` key anywhere.
- SC-02: unit — 3 distinct failing fixtures (top-level undeclared key, `runs[]` item undeclared key, `github`/`factory` sub-key undeclared), each asserting rejection AND that the message names the offending key.
- SC-03: unit — 11 fixtures across 8 required + 3 optional keys, one fixture per key (not a count comparison); plus a `phase`-alongside-all-required-keys fixture rejected as undeclared.
- SC-04: integration — `check-domain.sh` run in PreToolUse mode on a bad Write payload, exit 2 read directly (not inferred from source).
- SC-05: integration — bad file written to disk, PostToolUse sweep run, exit 2 asserted (not exit 0), key named.
- SC-06: unit — per-file (17) migration-table assertion: status enum byte-identical incl. case, `pr` int/null, no old status values / `phase` / string `"none"`; lowercase-value-rejected case.
- SC-07: unit — import forced to fail, exit exactly 3, message names missing package + install command.
- SC-08: integration — violation count vs T-04 captured baseline (falls or equal, never rises, no new violation text); INV-18/21/22/23/factory invariants still fire on a deliberately broken fixture; INV-17 quiet on FEAT-01/FEAT-02 with an exemption note naming them; exempt set computed from plans, not hardcoded.
- SC-09: unit — `gh-sync.py`, `factory_claim.py`, `factory_decompose.py`, `check-plan-routes.py` existing suites pass + one new case per tool (4 total) reading a `feature.json` fixture.
- SC-10: inspection — not this gate's evidence class (`not-provable-by-this-gate`).
- SC-11: inspection — not this gate's evidence class (`not-provable-by-this-gate`).
- SC-12: unit — `templates/feature.json` exists and validates against schema; `check-state.sh` INV-18 message and `harness/SKILL.md:23` both name it by filename.
- SC-13: integration — sweep for `feature.yaml` references, exactly two carve-outs (DECISIONS* records, test-harness-yaml-corpus.py docstring pinned to an exact occurrence count).
- SC-14: integration — 3 new DECISIONS.md entries (jsonschema dependency, closed key set, phase/status collapse); DECISIONS-INDEX.md byte-for-byte match against `gen-decisions-index.py --stdout`.
- SC-15: uat — out of gate scope (`not-provable-by-this-gate`).
- SC-16: integration — checker-unavailable + otherwise-valid payload -> exit 2 (never exit 1), message names the real target path (never a temp file), sweep emits the unavailability message once, not per file.
- SC-17: unit — check-plan-routes.py skips only on `status: Done`, `shipped`/`abandoned` literals absent, migrated-corpus count == 10 (0 is a failure, asserted non-zero), six board values + lowercase `done` each individually asserted for skip-or-check.
- SC-18: integration — 7-case INV-17 matrix: (1) Review missing handoff-build fires named; (2) Done missing handoff-validate (non-exempt) fires; (3) FEAT-01/02 Done zero notes exempt -> no violation; (4) Plan status no notes -> no violation; (a) Done, all tasks main-session-direct, no notes -> no violation + exemption note naming suppressed stems; (b) squad-built Done missing handoff-validate.md still raises; (c) Done with no `execution_mode` key raises, and empty/absent `tasks:` raises (no vacuous pass over empty list). Plus: check-state.sh executable code (comments stripped) contains no `PHASE_ORDER`, no `phase`-key read, no case-sensitive `handoff-<Capitalized>.md` path construction.

## Named traps from BRIEF §Verification gaps (to re-check at HEAD, not just cite)

1. New unit test files must be registered in `run-unit-tests.sh`'s `UNIT_SCRIPTS`, not `INTEGRATION_SCRIPTS` — the integration kind's `detect` globs only match `test-check-state.py` / `test-factory-integration.py`, so misregistration makes the file invisible to the matrix.
2. The required CI job (`tests.yml`'s `integration` job) must itself run `--kind unit` (T-03) or SC-01/02/03/06/07/09/12/17 (all unit-evidence) have no mechanical runner on the branch-protected context.
3. `check-state.sh` is expected red between T-06 and T-08 by construction (glob names `feature.json` while corpus still `feature.yaml`) — accepted, not a live concern at HEAD.

## functional / component / ui / eval / typecheck

Per BRIEF: no SC rests on any of them, feature touches no UI/LLM/DB surface. To be re-confirmed against the actual diff in Phase 2 (per dispatch, do not just cite BRIEF's claim).

---

(Phase 2 continues below once plan/hand-downs/source are read.)

## Phase 2 — read plan.yaml, source, and measured live

Diff range: `1bdfe3f..be8a3a6` (110 files, +6891/-2545). `review_sha` 3abaedd; `1bdfe3f` is the
plan-signing commit, so this is the correct range (not `3abaedd..HEAD`, which would miss T-05..T-12).

### Baselines re-run (not trusted from the lead's table)

| check | result |
|---|---|
| `run-unit-tests.sh --kind unit` | rc 0, 12 scripts, 36/36 cases in `test-validate-feature-json.py` PASS |
| `run-unit-tests.sh --kind integration` | rc 0, 12 scripts (incl. `test-check-domain.py`, `test-check-state.py` 58 `ok`/0 `FAIL`) |
| `check-state.sh` | rc 0, **zero** VIOLATION lines, one INV-17 exemption note naming FEAT-15 |
| `check-plan-routes.py` | `0 violation(s) across 10 plan(s)`, rc 0 |
| `gen-decisions-index.py --stdout` vs `DECISIONS-INDEX.md` | byte-for-byte, `diff` exit 0 |
| `git status --porcelain` before any probe | **empty** |

All five match the lead's table. **git status baseline: empty (quoted above).**

### DEC-174 carve-out: direct invocation, not reasoning (constraint 1)

**SC-04 — LIVE, MEASURED.** Ran `check-domain.sh` with `hook_event_name: PreToolUse`, `tool_name:
Write` against a fixture `.harness/features/FEAT-X/feature.json` carrying `invented_key`. Exit **2**.
stderr: `undeclared key 'invented_key' at /` plus the redirection sentence. (First attempt exited 0 —
`CLAUDE_PROJECT_DIR` without a `.harness/team-config.yaml` falls back to `check-domain.sh`'s own repo
root, so the target path never matched `RE_FEATURE_JSON` relative to the wrong root. Fixed by writing
a minimal manifest into the fixture; this is a real trap for anyone probing this hook cold, not a
defect in the hook itself.)

**SC-05 — LIVE, MEASURED.** Wrote a bad file to disk (`sneaky_key`), fired `check-domain.sh --post`
with a `Bash` payload (no path in the payload — exercises the sweep). Exit 2, key named. Not exit 0.

**SC-16 — LIVE, MEASURED, both halves.** (a) Otherwise-valid payload, `jsonschema` shadowed with a
module that raises `ImportError` (placed via `PYTHONPATH`, ahead of site-packages — `check-domain.sh`'s
own wrapper always prepends its own bin dir, so shadowing `feature_schema` itself is not reachable
this way, but shadowing `jsonschema`, which is imported *inside* `feature_schema`, is). Exit 2, never
0/1, message names the install command and the **real relative target path**
(`.harness/features/FEAT-X/feature.json`), never a temp file. (b) Two-file POST sweep under the same
forced-unavailable env: `CANNOT be checked` appears **exactly once** across both files — confirmed by
count, not by reading.

**MAJOR GAP, found while proving SC-04/05/16 live: `test-check-domain.py` carries ZERO schema-rejection
assertions.** Grepped it for `additionalProperties`, `undeclared key`, `feature_schema`,
`problems_for_text` — no matches. Its only `feature.json`-related fixtures
(`_legal_feature_json`/`write()` in `run_post`) are **deliberately schema-clean** — the helper's own
docstring says so, to isolate the line-budget assertion from the schema branch. That means D-03's core
enforcement (an undeclared key on the Write route → exit 2; the checker-unavailable route → exit 2, not
0/1) has **no standing regression test anywhere in the suite** — SC-04, SC-05 and SC-16 are proven true
today only by the three live probes above, run once, by me, outside any suite that will run again on
the next PR. This falsifies the dispatch's own premise that these SCs' "assertions live in
`test-check-domain.py`" — they do not. A future edit that broke or removed the schema-check branch in
`check-domain.sh` (lines 866-922) would pass `--kind integration` clean. `coverage_gaps`, ranked above
G1 in `must_fix` below — G1 is two missing fixtures for schema behavior that already has some coverage
elsewhere; this is the primary write-time enforcement path with none.

**SC-14 mutation (constraint 2, named target) — RESTORED, and it surfaced a real finding.** Ran the
splice/confirm/restore in a disposable worktree (`git worktree add`, DEC-153), never the main
checkout — the guard correctly denied a direct `Edit` on `docs/harness/DECISIONS-INDEX.md` first
(`harness-qa may not write` there), which is the expected DEC-179 domain result, not a defect.
  - Splicing `MUTANT-PROBE` into DEC-192's **ruling prose** and re-running
    `gen-decisions-index.py --stdout` **reproduced the mutant in the generated output** — `diff` exit
    **0**, no detection. Reading `build_index()` confirms why: ruling prose is round-tripped verbatim
    from `parse_existing_index()`'s existing rows, never regenerated from `DECISIONS.md`'s body (by
    design — rulings are meant to be hand-authored once). Only the **structural** fields (`@line`,
    `[tags]`, `refs:`, amendment span, supersession clause) are recomputed and therefore checkable.
  - Confirmed the asymmetry: mutating a **structural** field instead (`DEC-191` → `DEC-999` in the
    `refs:` list, same row) **was** caught — `diff` exit 1.
  - Worktree removed (`git worktree remove --force`), never touched the main checkout. This is not a
    hypothetical: it is the exact incident the dispatch names — DEC-192's row was corrupted in its
    ruling prose by the interrupted spawn, and I have now shown that had the SC-14 gate actually run
    against that corruption, **it would have passed it**. **Finding, not smoothed: SC-14's
    byte-for-byte check discriminates structural drift in the index but is structurally blind to a
    corrupted ruling clause** — which is exactly the shape of the incident this run exists to guard
    against.

**SC-13 mutation (constraint 2, named target) — RESTORED.** T-08's verify clause (not a separate
SC-13-only script) is the actual mechanized sweep: `git grep -c feature\.yaml` over `.claude`,
`.github`, `.harness/harness.json`, `.harness/team-config.yaml`, `docs/harness`, exempting
`docs/harness/DECISIONS*` by prefix and five files by **pinned exact count**
(`test-harness-yaml-corpus.py`:4, `check-domain.sh`:6, `test-check-domain.py`:1,
`check-plan-routes.py`:1, `BUILD.md`:3) plus a dated-anchor-string check per pinned file. Replicated
this logic read-only at HEAD: **OK**. In the same disposable worktree, injected one new
`feature.yaml` reference into `.claude/skills/harness/SKILL.md` (a non-carve-out instructing file) —
sweep **went red**, naming the file and count. Restored via worktree removal.
  - **Note on BRIEF vs plan**: BRIEF SC-13 (line 448-454) describes "exactly two carve-outs" —
    `DECISIONS*` and one exact-count file. The actual T-08 verify clause carve-outs **five** exact-
    count files plus the `DECISIONS*` prefix, per plan ruling R-01 (dated 2026-08-12, in
    `approval.rulings`, operator-approved). This is a sanctioned amendment via the plan's own
    ruling mechanism, not a drift — but it means BRIEF's prose describing SC-13 is now stale
    relative to what actually gates it. Not a defect; worth a documentor note.

### SC-08 — the discrepancy, resolved

BRIEF line 421: "It is NOT 'exits 0' — it exits 1 today." At HEAD: `check-state.sh` exits **0**,
**zero** VIOLATION lines. `notes/baseline-check-state.txt` is genuinely **0 bytes** (confirmed:
`wc -c` = 0), matching the dispatch's flag, not an error.

**Which is right:** the zero-byte baseline is correct, and BRIEF's "exits 1 today" is **stale prose**
written earlier in planning, before other concurrent work (or this feature's own T-04 precondition
wait) cleared whatever pre-existing violations BRIEF's author had in view. The file is not evidence
of a broken capture step — T-04's step 0 genuinely captured zero VIOLATION lines at the moment it
ran, and `check-state.sh` still reports zero at HEAD. **SC-08's real bar — "the count may only fall,
never rise" — is satisfied: 0 → 0.** Recommend BRIEF's line 421 be corrected in a future documentor
pass; it is not a live defect, but it is a specific claim that is checkably wrong today.

INV-18/21/22/23/INV-24(factory) fixtures in `test-check-state.py` (58 `ok`, 0 `FAIL`) — read
directly, not inferred: real tempfile fixtures per invariant, not vacuous ones (e.g. INV-24 has 14
distinct cases including null-repo, null-issue, self-collision, no-fleet-file). INV-17's plan-keyed
exemption on FEAT-15 fires live: `check-state.sh`'s own stdout at HEAD carries the exemption note
naming FEAT-15 and the three suppressed stems.

### SC-18 — seven-case matrix, verified against actual assertions (not labels, per P-01)

Read `test-check-state.py:203-312` directly. All seven cases present and passing: (1) Review +
absent `handoff-build.md` → raises, names it; (2) FEAT-01 Done, no notes → quiet (literal exemption);
(3) Done + absent `handoff-validate.md` → raises; (4) Plan, no notes → quiet; (5) all-MSD Done → no
violation **and** exemption note asserted by name (both halves, not just silence); (6) `NO_MODE`
plan Done → still raises, no exemption; (7) both `tasks: []` and absent `tasks:` key → both raise
(vacuity guard, both shapes, one assertion each). `check()` here **deliberately never asserts on exit
code** — correct per the dispatch's own warning that a dead invariant exits identically to a live one.

Executable-code sweep (comments stripped, my own grep, not the suite's): `PHASE_ORDER` appears only
in a comment at line 439; no `.get("phase"` anywhere in code; no `handoff-[A-Z]` path construction
anywhere in code. All three SC-18 tail clauses hold.

### G1 — RE-OPENED, and it is real (not closed by reasoning alone)

`test-validate-feature-json.py` has exactly **three** undeclared-key fixtures (top-level, `runs[]`
item, `github` sub-key) per T-01's own intent block — **no fixture for an undeclared `factory`
sub-key, and none for `factory.edges`**, despite the schema declaring `additionalProperties: false`
at both those levels. Probed directly against `feature_schema.problems_for_text` (not the schema
source, the running code): both **do** reject correctly today (`undeclared key 'bogus' at /factory`
and `at /factory/edges`, respectively). **So this is a coverage gap, not a live defect** — but it is
exactly the "this could regress silently" shape: nothing in the suite would catch a future edit that
loosened `factory` or `factory.edges`'s `additionalProperties`. `coverage_gaps`.

### tests.yml "Unit suite" deletability — RE-OPENED, confirmed FALSE claim in-tree

`tests.yml:112-114` comment: "`test-check-plan-routes.py` case 25 reads this file and asserts the
step is here and unneutered." Grepped `test-check-plan-routes.py` for `tests.yml`, `case_25`, `case
25`, `Unit suite`, `unneutered` — **zero matches**. Grepped every `test-*.py` in the bin dir for
`tests.yml` — the only hit is `test-check-domain.py:711`, which uses `tests.yml` purely as a fixture
*path string* for a domain-resolution case, asserting nothing about its content. **The comment's
claim is measured false.**

**Provenance, checked rather than assumed: this claim is INHERITED, not introduced by this feature.**
`git log -S "case 25" -- .github/workflows/tests.yml` finds the phrase first written in `eafc8ad`
(#133/DEC-183), well before this feature's range. `git diff 1bdfe3f..HEAD -- .github/workflows/tests.yml`
shows T-03 added the new "Unit suite" and "Validate feature execution state" steps and rewrote the
install-step comment, but **never touched** the "Plan-route gate" step or the comment block containing
the false case-25 claim — that block is byte-identical before and after this feature. So: (a) this
feature does not ship a NEW false claim, it ships beside a pre-existing one; (b) the false claim is
about the **Plan-route gate** step specifically, which predates this feature entirely; (c) the **new**
"Unit suite" step T-03 added has no protection claim made about it at all (true or false) — it is
simply unguarded, which is a real but separate gap from the false comment. Both are real, neither is
new to this diff. Not this feature's `must_fix` — an `open_question` for the lead/repo owner instead,
since fixing it means editing `tests.yml` outside this feature's scope.

### Coverage table — every kind in `harness.json` test_kinds

| kind | declared | actually ran | exit | honest for this diff? |
|---|---|---|---|---|
| unit | active, cmd set | `run-unit-tests.sh --kind unit`, 12 scripts | 0 | yes — `logic`/`cross_module` tasks (T-01, T-05) require it and it ran |
| integration | active, cmd set | `run-unit-tests.sh --kind integration`, 12 scripts | 0 | yes — `cross_module`(T-05), `config`(T-03,T-04,T-08) via SC-04/05/08/13/14/16/18 all named `integration` and their assertions live in `test-check-state.py`/`test-check-domain.py`, both registered `INTEGRATION_SCRIPTS` (confirmed by reading `run-unit-tests.sh`, not the `harness.json` `detect` glob, which names only 2 of the 12 — the `detect` glob is NOT what the `cmd` actually runs, so it is not misleading in practice but is itself a latent trap if anyone starts trusting `detect` for kind membership) |
| functional | excluded (DEC-187) | n/a | n/a | yes — no service API in this diff, matches the exclusion's stated reason |
| component | unresolved, cmd null | not run | n/a | **not applicable** — diff touches no `.tsx`; soft skip, honest |
| ui | unresolved, cmd null | not run | n/a | **not applicable** — no UI surface in this diff (confirmed: zero `.tsx`/`.jsx`/frontend paths in the 110-file diff); soft skip, honest |
| eval | unresolved, cmd null | not run | n/a | **not applicable** — no `ai_behavior` task in this plan (all `change_type` values are `logic`, `docs`, `config`, `cross_module`); soft skip, honest |
| typecheck | unresolved, cmd null | not run | n/a | **not applicable** — no TypeScript in the diff; soft skip, honest |

`change_type` census across the 12 tasks: `logic`(T-01) → unit required, present. `docs`(T-02, T-09)
→ matrix requires nothing (`docs: always: []`), and T-02/T-09 got unit coverage anyway via
`test-check-domain.py`'s existing shape assertions plus the verify clauses I re-ran directly.
`config`(T-03, T-04, T-08) → matrix requires nothing, but SC-04/05/08/13/14/16 (all `integration`)
land here and I proved them live. `cross_module`(T-05) → unit+integration required, both ran green.
No task is `ai_behavior`, `frontend`, `api`, `bugfix`, `feature`, or `scaffolding`.

### SC-by-SC evidence

| SC | evidence class | verdict | pointer |
|---|---|---|---|
| SC-01 | unit | **proves** | `test-validate-feature-json.py` fixture suite, 36 cases, all green; corpus spot-check (my own script) over all 17 `feature.json` — zero `phase`, zero non-schema keys |
| SC-02 | unit | **partially proves** | top-level + `runs[]` + `github` sub-key fixtures present and green; `factory`/`factory.edges` sub-key rejection is correct but UNTESTED — G1, `coverage_gaps` |
| SC-03 | unit | **proves** | 11 fixtures present (`accepted_all_eleven`, `accepted_only_required`, 3×`accepted_omitting_*`, 8× `rejected_omitting_required_*`, `rejected_phase_undeclared`), all green |
| SC-04 | integration | **proves TODAY, but not as standing coverage** | live `check-domain.sh` invocation above, exit 2, key named. **No test in any suite exercises this** — see the schema-rejection gap above. `sc_evidence` cites my live probe in this artifact, not a test path |
| SC-05 | integration | **proves TODAY, but not as standing coverage** | live POST-sweep invocation above, exit 2, key named. Same gap as SC-04 — no regression test |
| SC-06 | unit | **proves** | fixture-level (shipped/lowercase-done/pr-string-none all rejected) + my own per-file corpus sweep, all 17 files clean against the migration table |
| SC-07 | unit | **proves** | `cli_jsonschema_unavailable_exit_exactly_3`/`_not_0_or_1`/`_stderr_names_required` all green in the unit suite |
| SC-08 | integration | **proves**, with the BRIEF-line-421 correction above | `check-state.sh` re-run, 0 violations, baseline 0 bytes, count did not rise; INV-18/21/22/23/24 fixtures real and green; INV-17 exemption note confirmed live for FEAT-15 |
| SC-09 | unit | **proves** | grepped all four tools' test files directly: `test-gh-sync.py` (`write_feature_json`/`read_feature_json` helpers, used across its suite), `test-factory-claim.py:244-268` (an explicit eleven-key `feature.json` fixture read end to end by `issue_number`), `test-factory-decompose.py:219-288` (`make_feature` builds and reads `feature.json`), `test-check-plan-routes.py:839-916` (multiple `feature.json` fixture cases incl. the eight-required-key template case) — all four carry real new-format fixture coverage, all green in `--kind unit`/`--kind integration` |
| SC-10 | inspection | not-provable-by-this-gate | operator spot-check, out of QA's evidence class |
| SC-11 | inspection | not-provable-by-this-gate | schema-source inspection, out of QA's evidence class |
| SC-12 | unit | **proves** | `templates/feature.json` exists, validates clean via `feature_schema.problems_for_file`; both instruction points (`harness/SKILL.md:24`, and `check-state.sh`'s INV-18 remediation message — confirmed by grep) name it by filename |
| SC-13 | integration | **proves** | replicated T-08's sweep read-only at HEAD (OK), then live mutation in a disposable worktree turned it red, restored. BRIEF's "exactly two carve-outs" is stale vs the plan's actual (sanctioned) five-file/prefix scheme — noted, not a defect |
| SC-14 | integration | **proves the structural half; disproves the prose half** | byte-for-byte match confirmed at HEAD; live mutation shows the check is blind to ruling-prose corruption — the exact incident this run investigates. See finding above |
| SC-15 | uat | not-provable-by-this-gate | operator read, out of QA's evidence class |
| SC-16 | integration | **proves** | live invocation, both the exit-2/real-path half and the once-not-per-file dedup half, both measured directly |
| SC-17 | unit | **proves** | `check-plan-routes.py` re-run at HEAD: `0 violation(s) across 10 plan(s)`; corpus grep confirms zero `shipped`/`abandoned` literals; 7 files at `status: Done` matches BRIEF's named seven |
| SC-18 | integration | **proves** | all seven cases read directly at the assertion (not the label) and confirmed passing; executable-code sweep for `PHASE_ORDER`/phase-key-read/capitalized-path confirmed clean by my own grep |

### must_fix, ranked

1. **`test-check-domain.py` has zero schema-rejection assertions for the feature.json write-time gate
   (D-03's core enforcement).** SC-04, SC-05 and SC-16 are true today only by my one-off live probes;
   nothing mechanical protects them against a future regression in `check-domain.sh`'s schema branch
   (lines 866-922). This is the highest-priority gap because it is the PRIMARY enforcement path this
   whole feature exists to add, not a secondary nesting level or a documentation string. Add fixtures
   analogous to `run_post`'s but WITHOUT the deliberate schema-clean padding: an undeclared-key payload
   on the Write route (PreToolUse, exit 2) and a jsonschema-unavailable payload (exit 2, not 0/1),
   covering both the PRE and POST routes.
2. **G1 — no fixture proves `factory`/`factory.edges` reject an undeclared key**, though the running
   code is correct today (verified by direct probe). Lower priority than (1): the schema-source
   enforcement for these two levels already has partial sibling coverage (`github` sub-key is tested,
   the same `additionalProperties: false` mechanism applies uniformly), so the blast radius of a
   silent regression here is smaller than (1)'s.
3. **SC-14's byte-for-byte check does not discriminate a corrupted ruling clause**, only structural
   drift — demonstrated live, and it is the exact shape of the incident (`MUTANT-PROBE` in DEC-192's
   row) that motivated this gate run. Not blocking this feature's ship (the generator's design — hand
   -authored ruling prose, mechanically-verified scaffolding — is a real trade-off, not an oversight),
   but it should be recorded as a known limit of SC-14's automated evidence, not left implicit.
4. **BRIEF SC-08 line 421 ("exits 1 today") and SC-13 lines 448-454 ("exactly two carve-outs") are
   both stale relative to what actually shipped** (0-violation baseline; five-file exact-count scheme
   under R-01). Neither is a functional defect — both are prose corrections for a documentor pass.

**Not in must_fix (moved to `open_questions`):** `tests.yml`'s false case-25 claim about the
Plan-route gate step, and the Unit-suite step's own lack of any protection claim. Both are real, but
both are INHERITED (the false comment predates this feature by multiple releases; `git log -S`
confirms it and `git diff 1bdfe3f..HEAD` confirms this feature never touched that block) — fixing them
means editing `tests.yml` outside this feature's scope, so I am not gating FEAT-14 on a pre-existing
repo defect this feature did not introduce and did not worsen.

### Mutation hygiene

- Baseline `git status --porcelain` before any probe: **empty**.
- Every mutant applied in a disposable `git worktree` (SC-14, SC-13), never the main checkout — the
  bash-write-guard denied a direct `Edit` attempt on `DECISIONS-INDEX.md` first, correctly, per
  DEC-179 domain rules.
- Each worktree removed via `git worktree remove --force` immediately after reading its signal, never
  batched.
- No `.harness/features/` fixtures written outside `notes/qa-final-coverage.md`; scratch fixtures for
  SC-04/05/16 lived entirely under the session scratchpad.
- No `gh-sync.py`/`factory_claim.py`/`factory_decompose.py` invoked against the live corpus.
- **Final `git status --porcelain` is NOT empty** — it shows exactly one entry, this artifact file
  itself, which is my authorized deliverable (constraint 4: "Create nothing under `.harness/features/`
  except `notes/qa-final-coverage.md`"). "Clean" means identical to the baseline plus that one
  sanctioned write, not literally empty; I am stating that distinction explicitly rather than quoting
  a false "(empty)" for the after-state.

```
$ git status --porcelain   # before any probe
(empty)
$ git status --porcelain   # after, at return time
 M .harness/features/FEAT-14-feature-json-schema/notes/qa-final-coverage.md
```

Every worktree (`wt-sc14`, `wt-sc13`) was independently confirmed removed and never left a trace in
this output at any point it was checked (see the SC-13/SC-14 sections above, each with its own
in-context `git status --porcelain` / `git worktree list` confirmation at the moment of restoration).
