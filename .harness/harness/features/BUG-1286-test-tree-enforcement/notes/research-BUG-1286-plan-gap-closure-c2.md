# Plan gap closure — BUG-1286, plan phase, fix cycle 2

**All five gaps closed as ruled, in `plan.yaml` (three `amend` splices) and `BRIEF.md` (SC section
rewritten, 15 criteria to 17).** No implementation, test, `DECISIONS.md` or `harness.json` byte
moved; both approvals still `pending`; no `panel:` key written. All five mechanical checks pass.

## Gap -> change

| Gap | Artifact / id | What changed |
|---|---|---|
| 1 D-01 "everywhere" false as shipped | `plan.yaml` D-01 `choice` | extension restriction now scoped explicitly to the NEW repository-wide clause; states the bin clause deliberately keeps its own unrestricted `probe-*` glob because it reads the filesystem, not the index, and is the untracked-plant net; the under-`tests/` clause keeps its own three `.py` shapes. Closes with "three clauses, three deliberately different vocabularies, none of them widened by this feature" |
| 1 inherited claim | `plan.yaml` T-01 `intent` | after the `NAME_PATTERNS`/`SOURCE_EXTENSIONS` definition: the constants govern the new clause ONLY; do not feed them into the bin or under-`tests/` clause, both stay byte-identical |
| 1 inherited claim | `plan.yaml` T-05 `intent` | bullet 1 now says "authoritative vocabulary FOR THAT CLAUSE" and "out of scope OF THE REPOSITORY-WIDE CLAUSE", plus an explicit instruction not to write that the restriction holds everywhere; bullet 2 states the bin clause is retained unchanged with its own unrestricted `probe-*` glob |
| 2 SC-01 second clause ungradable | `BRIEF.md` | split: SC-01 keeps the behavioural assertion (`automated`/`unit`); new SC-02 is the test-first obligation, `verify: inspection`, grader named (qa's test-first audit) and evidence named (red result of the new assertions run against `suite_layout.py` at the base commit, before T-01's edit), with "a passing unit run at review time cannot discharge it" |
| 3 AC-05's `tests/manual/**` half unasserted | `plan.yaml` T-01 `intent` case 1 | fixture additionally creates `tests/manual/probe-fixture.py`; separate assertion that no finding names it, with the reason the shape is `probe-*.py` and not `test-*.py` written into the case |
| 3 criterion side | `BRIEF.md` SC-06 | now quantifies over the manual file the fixture actually contains, names the shape `probe-*.py`, and records why `tests/manual/test-*.py` is refused today (`suite_layout.py:20-28`) so no reader substitutes it |
| 4 SC-13 gave inspection no target | `BRIEF.md` | split into SC-14 (`harness.json` unchanged, no byte) and SC-15 (mutation scope: `run-unit-tests.sh` carries exactly one `run_pool.py` invocation, line 47 at HEAD `1977ebd6`, whose `--mutation-check` argument is `"$BIN_DIR"` and is not widened). Two independently failable claims, so two criteria |
| 5 lead call: SC-06/SC-08 traced nowhere | `BRIEF.md` SC-07, SC-09 | each now names its pre-existing discharging assertion: `manual tests are not actively detected` at `tests/unit/test-suite-layout.py:104-105`; `import layout_fixtures as lf` at `tests/integration/test-layout-migration.py:62`. Both anchors re-read at HEAD before writing. Nothing else about either criterion changed |

**D-04 checked after the change (asked for explicitly):** its `choice` is unchanged and agrees —
"the existing filesystem clause over the bin directory is retained beside the new index-driven
clause, and a path the bin clause already reported is not reported twice." It never claimed a shared
vocabulary, so narrowing D-01 removes the contradiction without touching it. Primary source for the
ruling re-confirmed: `suite_layout.py:20-33` — under-`tests/` shapes `test-*.py`, `test_*.py`,
`*_test.py`; bin shapes `test-*.py`, `*.test.*`, `probe-*` (no extension filter).

## Final SC numbering and AC mapping (17 criteria, all 11 ACs covered)

| SC | verify | AC |
|---|---|---|
| SC-01 | automated/unit | AC-01 |
| SC-02 | inspection | AC-01 (test-first, new) |
| SC-03 | automated/unit | AC-02 |
| SC-04 | automated/integration | AC-03 |
| SC-05 | automated/unit | AC-04 |
| SC-06 | automated/unit | AC-05 (manual shape `probe-*.py`) |
| SC-07 | automated/unit | AC-05 |
| SC-08 | automated/unit | AC-06 |
| SC-09 | automated/integration | AC-06 |
| SC-10 | automated/unit | AC-07 |
| SC-11 | automated/unit | AC-08 |
| SC-12 | inspection | AC-09 |
| SC-13 | inspection | AC-10 |
| SC-14 | inspection | AC-11 (`harness.json`) |
| SC-15 | inspection | AC-11 (mutation scope, new) |
| SC-16 | automated/unit | AC-11 |
| SC-17 | automated/unit | AC-04 |

Old -> new: 01 splits to 01+02; old 02-12 shift to 03-13; old 13 splits to 14+15; old 14->16,
old 15->17. No plan task referenced any SC id (`grep SC-` over `plan.yaml`: no matches), so the
renumber required no task re-proposal. `BRIEF.md`'s one prose cross-reference was updated
(`SC-13 freezes harness.json` -> `SC-14`).

## Mechanical re-verification (from the worktree root)

1. `yaml.safe_load(plan.yaml)` -> `LOADS OK`.
2. `check-plan-routes.py` with `CLAUDE_PROJECT_DIR` set to the worktree -> `OK T-01`..`OK T-05`,
   `0 violation(s) across 1 plan(s)`, exit 0.
3. All five tasks carry all eleven keys and exactly eleven (`T-01..T-05 ALL 11 KEYS`, len 11 each);
   6 decisions, 5 tasks intact.
4. `status: plan`, `approval: {status: pending}`, `panel` key absent (`panel_present= False`).
5. 17 SCs, no gap or duplicate, table ids identical to the SC list; every SC exactly one `verify:`;
   every `automated` one names `unit` or `integration`, both `status: active` in `harness.json`
   `test_kinds`; ACs covered = AC-01..AC-11 (11 distinct). SC-07 and SC-09 now name their
   pre-existing assertions in-criterion, so no SC is discharged by nothing.

Side check for SC-15's non-vacuity: `grep -c run_pool run-unit-tests.sh` = 1, so "exactly one
invocation" is true today and a widened second call would falsify the criterion.

## Open question

- Unchanged and not re-litigated: the `unit.detect` extension-agnostic residual stays a disclosed
  residual in `## Verification gaps`, with no SC added, per the orchestrator's ruling.
