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
