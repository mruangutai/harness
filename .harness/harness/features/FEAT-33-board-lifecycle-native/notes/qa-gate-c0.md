# QA gate — FEAT-33 board-lifecycle-native — c0

**VERDICT: PASS**, with two findings that do not gate (a stale dispatch task-count matrix, and one
SC-19 number drift) and one live-board observation that is expected transient state, not a defect.

## Suite

`.claude/skills/harness/bin/run-unit-tests.sh --kind all`, run to completion (not truncated by the
120s foreground timeout — ran in background to full exit):

- **46 of 46 scripts PASS, 0 FAIL, 0 MISCONFIGURED, exit 0.** Confirmed, matches the dispatch's
  measurement. 801 individual `PASS` lines, 0 `FAIL` lines. The 17 hits for
  "MISCONFIGURED/ImportError/Traceback/MODULE_NOT_FOUND" are all test *names* asserting the
  *absence* of a traceback (e.g. `run(): without FACTORY_DEBUG set, no traceback is printed`) —
  none are a real collection/import error.
- `check-state.sh` exits 0. Live re-run right now shows exactly 1 VIOLATION, and it names
  FEAT-34's unsigned BRIEF.md — unrelated to this feature, matching migration-harness.md's and
  T-11's verify's exact claim (`grep -c '^  VIOLATION'` = 1, no line contains `FEAT-33`).
- `test-board-lifecycle.py` is correctly registered in `run-unit-tests.sh:17` `UNIT_SCRIPTS` (the
  mandatory one-line edit T-04 calls out — an unregistered `test-*.py` would exit 2 MISCONFIGURED
  and was checked, not assumed).

## Matrix enforcement against the diff (72 files, `faf409e8..HEAD`)

**The dispatch's own task-count matrix is wrong — a finding, corrected here.** It states
`api ×1, bugfix ×5, config ×6, docs ×4, feature ×8, logic ×3` (sums to 27). Re-counted directly
from `plan.yaml`'s 22 tasks: **api×1 (T-03), bugfix×3 (T-07, T-08, T-22), config×6 (T-01, T-10,
T-11, T-12, T-18, T-20), docs×4 (T-09, T-14, T-19, T-21), feature×5 (T-04, T-05, T-06, T-15,
T-17), logic×3 (T-02, T-13, T-16)** — sums to 22, matching the plan. `bugfix` and `feature` were
overstated by 2 and 3 respectively in the dispatch text; nothing was understated, so no kind was
hidden by the wrong count.

Against `harness.json`'s `test_matrix` on the corrected counts:

| change_type | required kinds | state |
|---|---|---|
| config (6) | none (`always: []`) | n/a — satisfied trivially |
| docs (4) | none | n/a — satisfied trivially |
| logic (3) | unit | **satisfied** — T-02/`test-factory-config.py` etc., T-13/`test-gh-sync.py` (Ready/Review exact-set assertions at `test-gh-sync.py:1596-1697`), T-16/`test-gh-sync.py` title assertions |
| api (1, T-03) | unit; +integration (touches external service — GraphQL mutations) | **satisfied** — unit in `test-factory-gh.py` (326 new lines, asserts argv/GraphQL vars); integration added to `test-factory-integration.py` per D-12 (confirmed present, not a new file) |
| feature (5) | unit + integration | **satisfied** for all five — each of T-04/05/06/15/17 has its own `test-board-lifecycle.py` unit cases AND its own forking case in `test-factory-integration.py` (cases J, K, L, M, N — verified by name, each anti-vacuum-checked: "at least one gh call was actually recorded", stdout content asserted, not just exit code) |
| bugfix (3) | unit; T-07/T-08 also `--kind all` per their own stated reasoning (T-02 touches integration-kind fixtures) | **satisfied** — T-07 replays #642's exact shape (`test-gh-sync.py:1266-1290`) and fails pre-change per its own intent; T-08 has per-issue (not per-count) label/reason assertions; T-22 has all four INV-26 boundary cases in `test-check-state.py:1608-1653` |

**`matrix_ok: true`.** No required kind is missing once the corrected counts are used.

## SC evidence (spot-checked against the diff, not against test labels)

- SC-01/02: `test-board-lifecycle.py:450` (provision, no-project case), DECLARATION finding at `:502-511`
- SC-03: per-issue assertions in `test-gh-sync.py:610-930` (`--reason completed`, `state_reason=not_planned`, `b60205` label) — none are count-based
- SC-04: `notes/migration-harness.md` + raw captures `migration-harness-audit-{before,after}.txt` — narrative matches captures byte for byte (13→2 findings)
- SC-05: `test-gh-sync.py:1266-1290`, #642 replay, fails pre-change per stated intent
- SC-06/08: `test-factory-config.py:365-436` (six accepted, five/seven rejected); SC-08's actual discriminator is `test-board-lifecycle.py:390-401` ("no argv contains 'Abandoned'"), correctly NOT the seven-key rejection case (plan explicitly separates these)
- SC-07: `test-board-lifecycle.py:362-363` ("nothing to do")
- SC-09: `test-board-lifecycle.py:556-568`
- SC-10: suite green (above) + `check-state.sh` exit 0 + four-file untouched list confirmed via `git diff --stat` against `gh_board.py`/`board-station.py` (both absent from diff, as required)
- SC-11: **deliberately `not_met`** — `notes/migration-kaya-ai.md` is explicit that this is uat, operator-run
- SC-12: `DECISIONS.md` DEC-196 am.3 declares `plan`; `DECISIONS-INDEX.md:214` reads `am.1-am.4`; `gen-decisions-index.py --stdout` diffed clean against the committed index (live-verified)
- SC-13/14: `gh-sync.py:878-961` matches spec exactly (Ready→sub-issues only, never parent; Review→parent+sub-issues; Done/Abandoned/Plan write nothing); tests at `test-gh-sync.py:1596-1697` assert exact sets, not counts
- SC-15: `DECISIONS.md:6500-6506` six-row map, one writer each; `SKILL.md:191,197,199` — `main-session-direct` appears twice (T-14's own verify requirement), `gh-sync.py status` named for both actors
- SC-16: `test-board-lifecycle.py:592-670` — FEAT-32 (fixture), FEAT-08 (#85), FEAT-09 (#98) each its own assertion, plus three exemptions each individually asserted
- SC-17/18: `test-gh-sync.py` title-generator assertions (T-16); backfill refusal/skip cases in `test-board-lifecycle.py` (T-17)
- SC-19: `notes/retitle-harness.md` — **number drift, not a failure**: report shows 218 renamed (not the brief's estimated 188), 0 already-correct, 0 refused, second run "0 to rename", 436 GraphQL points logged. The 188 was a 2026-08-22 measurement; 30 more task tickets existed by 2026-08-23 execution (other in-flight features). Substance of SC-19 (report exists, zero refused, idempotent re-run, points logged) is met; the specific count is stale in the BRIEF, not wrong in the evidence.
- SC-20: `check-state.sh:1354-1362` bounded exactly to `feature.json.status == "Review"`; both directions asserted in `test-check-state.py:1608-1653` (v.T22a-d)

## Coverage gaps found (Phase 1 vs Phase 2 delta)

None of my Phase-1-derived expectations (drawn from BRIEF/SC alone, before reading code) turned out
to be uncovered. The one real delta: I expected SC-19's "188" to be a fixed target and found the
live run produced 218 — a plan-vs-reality drift already disclosed by the report itself, not
something the report tried to hide. This is a finding for the record, not a gate failure.

## Live-run capture judgement (the three uat-shaped notes)

1. **`notes/migration-harness.md`** — supports its claim. "13→2 findings" is corroborated by raw
   `audit-before.txt`/`audit-after.txt` captures (verified by diffing them, not by reading prose).
   The "2 accepted findings" framing is honest: it explicitly says the verify was originally
   unsatisfiable and states why, rather than silently loosening it. **A live re-run just now shows
   a THIRD finding** — this feature's own `FEAT-33` STATUS mismatch (`feature.json` still reads
   `Building`, parent `#675` card now reads `Review`, because entering validate/QA moved the
   parent card per T-14's own instruction before `feature.json`'s status is updated to match).
   This is the expected transient shape of an in-flight feature going through its own gate, not a
   regression — it will resolve when this feature's status is next recorded. Flagging it so pm
   does not mistake a stale "2 findings" snapshot for the current live count.
2. **`notes/migration-kaya-ai.md`** — supports its claim, and is the strongest of the three: it
   documents finding and fixing #783 (the STATUS class walking this checkout's own features
   against a foreign board, 18/29 false findings) live, mid-task, rather than after the fact. Final
   captured audit (`migration-kaya-ai-audit-after.txt` not separately re-verified live to avoid
   touching a real board twice, but the committed report's own "Final audit" block matches its
   before/after table) shows `0 findings`, contradiction-free with the discriminating pair table
   (board 2 foreign vs board 3 own).
3. **`notes/retitle-harness.md`** — supports its claim with independent cross-checks (3 titles spot
   checked against `gh issue view` directly, byte-level em-dash check, and an explicit
   self-correction where the author caught their own false-positive grep on the words
   "refuse"/"refusal" appearing inside ticket titles). This self-correction is itself evidence the
   report was written honestly rather than polished after the fact.

## Verifies graded weak, per the dispatch's own warning

Confirmed live: T-09's `--check`-style clause was already corrected to the real
`gen-decisions-index.py --stdout | diff` form and passes live. T-11/T-12/T-18's corrected verifies
(replacing "grep this session's own report for a string" with live tool re-invocations) were
spot-checked and pass live where check-state.sh and audit/retitle re-runs were safe to perform
read-only. No new instance of the self-satisfying-grep defect was found beyond the six already
disclosed and corrected in `plan.yaml`.

## Test-first audit

Every task whose intent I read states an explicit "fails pre-change" requirement and the actual
test bodies carry `#642 replay`-style pre-change framing, "measured at 46ee87c" pre-state
citations, or explicit assertions that a case would fail against the described defect (SC-03,
SC-05, SC-13, SC-16, SC-17, SC-18, SC-20 all worded this way in their own test comments). No
violation found in the sampled tasks.

## sc_evidence summary for pm

| SC | test |
|---|---|
| SC-01 | `.claude/skills/harness/bin/test-board-lifecycle.py:450` |
| SC-02 | `.claude/skills/harness/bin/test-board-lifecycle.py:502-511` |
| SC-03 | `.claude/skills/harness/bin/test-gh-sync.py:610-930` |
| SC-04 | `notes/migration-harness.md` + `notes/migration-harness-audit-{before,after}.txt` (inspection) |
| SC-05 | `.claude/skills/harness/bin/test-gh-sync.py:1266-1290` |
| SC-06 | `.claude/skills/harness/bin/test-factory-config.py:374-436` |
| SC-07 | `.claude/skills/harness/bin/test-board-lifecycle.py:362-363` |
| SC-08 | `.claude/skills/harness/bin/test-board-lifecycle.py:390-401` |
| SC-09 | `.claude/skills/harness/bin/test-board-lifecycle.py:556-568` |
| SC-10 | suite run above + `check-state.sh` live exit 0 |
| SC-11 | not_met (uat, operator-run) — `notes/migration-kaya-ai.md` |
| SC-12 | `.harness/harness/docs/DECISIONS.md` DEC-196 am.3 + `DECISIONS-INDEX.md:214` (inspection) |
| SC-13 | `.claude/skills/harness/bin/test-gh-sync.py:1596-1697` |
| SC-14 | `.claude/skills/harness/bin/test-gh-sync.py` (SC-14 fixture, zero-sub-issue case) |
| SC-15 | `.harness/harness/docs/DECISIONS.md:6500-6506` + `.claude/skills/harness/SKILL.md:191,197,199` (inspection) |
| SC-16 | `.claude/skills/harness/bin/test-board-lifecycle.py:592-670` |
| SC-17 | `.claude/skills/harness/bin/test-gh-sync.py` (T-16 title assertions) |
| SC-18 | `.claude/skills/harness/bin/test-board-lifecycle.py` (T-17 refusal/skip cases) |
| SC-19 | `notes/retitle-harness.md` (inspection; number drift noted above) |
| SC-20 | `.claude/skills/harness/bin/test-check-state.py:1608-1653` |
