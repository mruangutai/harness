# Amendment — the cycle-0 goal-check applied to plan.yaml and BRIEF.md — FEAT-58

**All nine findings LANDED; nothing declined.** The critical defect is fixed at its source and at
every restatement: `D-08`'s derivation is now a three-part SET that keeps every tracked `.harness`
subtree except the features corpus, and the fixture plus `REQUIRED_PATHS` can now see it regress.
Criteria went **12 → 13** (SC-12 split). `--verify`'s gate is **`check-state.sh`'s preflight**,
recorded as **D-12**, carried by **N-06**. `status: plan`, `approval.status: pending`, BRIEF
`## Approval` `status: pending` — all untouched. `lanes:` untouched; D-06 still unresolved.

## Per-finding disposition

| id | disposition | where it landed |
|---|---|---|
| GC-01 | **LANDED** | `plan.yaml:239-262` D-08 `choice` — three-part set, `(b)` = maximal tracked `.harness` dirs disjoint from `.harness/<repo>/features`, recursion named with `git ls-tree -d -r -t`; `:263-306` `because` keeps the derived-not-literal proof and now carries the exit-0 measurement that killed minus-`.harness`; `:582-596` N-02 check 1 restates the same three parts; `:642-648` N-02's unit test asserts the nested case and requires the canned input to carry it; `BRIEF.md:132-142` SC-01 names the three subtrees per path |
| GC-02 | **LANDED** | `plan.yaml:417-431` fixture tracks `.harness/factory/fleet.yaml`, `.harness/expertise/<agent>.md`, `.harness/harness/docs/DECISIONS.md` (+`.harness/harness.json` as the distinct directly-in-`.harness` case); `:442-448` `REQUIRED_PATHS` names each; `:936-950` N-05 asserts them **per path** with `os.path.isfile`, exit status explicitly excluded |
| GC-02b | **LANDED — decided yes** | `plan.yaml:959-976` N-05 group 3 now adds a new tracked `.harness` subtree **and** a nested `.harness/harness/<new>` one, asserted as three separate clauses. Reason: the derivation failed at the `.harness` level, so a top-level-only derived-not-literal proof greens for a part-(b) that is hardcoded or absent. `:951-957` extends the discrimination proof to a second, part-(b) break |
| GC-03 | **LANDED** | `plan.yaml:476-491` — the exclusion list must EQUAL the plan's own test-file set, `--strict` fails on any missing path, non-strict prints named PENDING lines plus how many files were read; `:1443-1450` N-09 runs `--self-check --strict`, and it is in N-09's `verify:` |
| GC-04 / Q2 | **LANDED — closed, not deferred** | new decision **D-12** `plan.yaml:330-357`; wiring spec `plan.yaml:1045-1082` (N-06 PART 3, with `test-check-state-verify-gate.py` added to N-06 `files:`/`verify:`, and REQ-06/SC-09 added to N-06 `traces:`); `BRIEF.md:173-181` SC-09 now asserts the gate INVOKES `--verify` (by recorded argv, not exit 0) and REFUSES on failure without repairing |
| GC-05 | **LANDED** | `plan.yaml:464-473` — the `<100` bound KEPT, plus two named clauses: the fixture's `git rev-parse --show-toplevel` resolves under the temp dir and not this repo, and every `git ls-files` path resolves inside that toplevel |
| GC-06 | **LANDED** | `plan.yaml:1312` N-09 `change_type: cross_module`. That kind requires `unit` as well as `integration` (`harness.json:172-177`), so `:1426-1441` adds `tests/unit/test-nonregression-notes.py` — the note reader is a pure function and it is what decides clauses 1 and 2 |
| GC-07 | **LANDED** | N-01 `traces:` narrowed to `[REQ-05, SC-12]` (`plan.yaml:377-379`); the SC-in-`traces` convention is now stated as deliberate at `BRIEF.md:113-115` — the goal-check reads it to find which task grades which criterion and no other field carries that edge |
| Q1 | **LANDED — split** | `BRIEF.md:194-209` SC-12 (D-5 non-regression) and SC-13 (REQ-10 nothing-altered, carrying the D-06 Arm A pathspec sentence); `:108-111` the one-line reason for thirteen; N-09 `traces:` gains SC-13; `plan.yaml` D-06 `choice` and N-09 PART 3 re-point the nothing-altered clause at SC-13 |

**One thing a grep will still find, deliberately:** the phrase `minus-.harness` survives at
`plan.yaml:273`, `:447`, `:583`, `:939` — every occurrence labels it as the REJECTED form and states
the measurement that rejected it. Removing the record would invite a later scan to re-propose it.

## Coverage — as written in BRIEF.md

| Item | What | REQ | SC |
|---|---|---|---|
| **D-1 (DoD)** | Exactly one feature directory materialised | REQ-01 | SC-01 |
| **D-2 (DoD)** | Every other feature readable on disk | REQ-02 | SC-02 |
| **D-3 (DoD)** | Audit: active feature only, no corpus, refuses | REQ-03 | SC-04, SC-05, SC-06 |
| **D-4 (DoD)** | No two features claim one branch | REQ-04 | SC-07 |
| **D-5 (DoD)** | Fresh clone and CI unchanged | REQ-05 | SC-12 |
| **M-1 (DoD)** | One idempotent `--verify`/`--repair`, verify never repairs, and a named gate calls `--verify` | REQ-06 | SC-09, SC-10 |
| **M-2 (DoD)** | It runs from `post-checkout`, `post-merge`, `post-rewrite` | REQ-07 | SC-11 |
| — | Corpus path gitignored; writes through it refused | REQ-08 | SC-02, SC-03 |
| — | The live FEAT-02 / FEAT-03 collision, on real data | REQ-09 | SC-08 |
| — | Nothing altered outside the active feature | REQ-10 | SC-13 |

All seven binding items keep their own REQ and at least one SC. Thirteen criteria, contiguous
SC-01…SC-13, every one `verify: automated` with `evidence: integration` — no null runner, no byte
figure, no `du` value (re-read and asserted mechanically after the last write).

## Open

- **D-06 stays unresolved** — the operator picks Arm A or Arm B at signature; Arm A also signs the
  one named pathspec exclusion, now recorded against SC-13.
- **`lanes:` at `plan.yaml:8-25` still describes the halted plan and is unwritable by any verb.**
  D-07 (`:206-237`) carries the live lane table. Known, out of scope here.
- A fresh plan panel has still never run against this draft (`panel.last_run: none`).
