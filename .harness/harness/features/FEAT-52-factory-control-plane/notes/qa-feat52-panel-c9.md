# QA panel evidence — FEAT-52 factory-control-plane, cycle 9

**Verdict: FAIL.** All 15 signed `verify:` clauses are mechanically green at the pin, and the
matrix floor (unit) is satisfied — but the per-criterion evidence this dispatch exists to
supply shows **five of the twelve automated SCs have no named carrying case for their
discriminating clause**, one of them (SC-13) with **zero** coverage of the new production logic
it claims to gate. A green suite here is not proof; several of the "passing" verify clauses pass
precisely because the new code path is never exercised, not because it is correct.

## 1. Pin check

- `git rev-parse HEAD` = `fa6efda60976671feb71a5e8bf33d79711ec0d2b`. Pin =
  `d8c42a9df691f3e4774047138ef9caeb0c8f5850`. **HEAD != pin.**
- `git status --porcelain`: clean, nothing uncommitted.
- `git diff <pin> HEAD --stat`: exactly one file, `feature.json`, one line
  (`review_sha: "none" -> "d8c42a9d..."`). No source, test, or plan content differs between HEAD
  and the pin — `git merge-base --is-ancestor <pin> HEAD` succeeds, and the sole delta is the
  review_sha metadata write itself. Every measurement below is therefore valid at the pin;
  I ran the ref-taking suite (`test-anchor-directions.py`) explicitly with
  `HARNESS_REVIEW_SHA=d8c42a9df691f3e4774047138ef9caeb0c8f5850` to confirm (exit 0, same 7 PASS
  lines as the HEAD-default run).
- merge-base with `main`: `8ff525e246ba3af9d69d08646e52be28d7546c47`.
- `git diff main...<pin> --stat`: 93 files changed, 6646 insertions(+), 191 deletions(-).

## 2. All fifteen verify clauses — byte-for-byte from `plan.yaml`, run at the pin

T-04 and T-13 verify text cross-checked byte-for-byte against the dispatch's verbatim quotes —
**identical, no mismatch.**

| Task | Exit | Note |
|---|---|---|
| T-01 | 0 | `test-inflight-registry.py` (124/124) + `test-check-domain.py` (multi-suite, all ok) |
| T-02 | 0 | `test-check-instruction-paths.py`, 10 PASS lines |
| T-03 | 0 | `test-inject-expertise.py`, 18/18 |
| T-04 | 0 | checker 36 files/0 violations; adapters --check clean; `missing []` |
| T-05 | 0 | `test-check-instruction-paths.py` (same 10); checker 18 files/0 violations |
| T-06 | 0 | checker 12 files/0 violations; `missing []` |
| T-07 | 0 | checker 7 files/0 violations; `missing []` |
| T-08 | 0 | checker 1 file/0 violations; `missing []` |
| T-09 | 0 | `test-dispatch-guard.py`, 42/42 |
| T-10 | 0 | checker 3 files/0 violations; `missing []` |
| T-11 | 0 | checker 32 files/0 violations; adapters --check clean; `missing []` |
| T-12 | 0 | `test-check-instruction-paths.py` (same 10); whole-scope checker: 62 files/0 violations |
| T-13 | 0 | `gen-decisions-index.py --stdout` diffs clean against `DECISIONS-INDEX.md`; `test-gen-decisions-index.py` 14/14 |
| T-14 | 0 | `test-inject-expertise.py`, `case14` present and PASS |
| T-15 | 0 | `test-anchor-directions.py`, 7/7 (6 rows + whole-scope-at-pin) |

All 15 exit 0. **No signed verify clause is red.**

## 3. Per-SC evidence — the twelve `verify: automated` criteria

`--list-scope` at the pin: 62 entries; all five canonical sites S1–S5 individually present
(verified by name, not count).

| SC | Verdict | Carrier | Note |
|---|---|---|---|
| SC-01 | **PARTIAL** | `test-inject-expertise.py:case4` (`.../bin/test-inject-expertise.py:161-174`) | Case4 confirms the block is emitted unconditionally with an absolute first-content-line path. It does **not** set the subprocess `cwd` to a directory different from the resolved root, and does **not** assert the injected value differs from that cwd — the exact discriminating half SC-01 names ("A case in which the two coincide cannot fail for the reason this feature exists"). `grep -rn cwd= test-inject-expertise.py` confirms `run_hook()` never overrides `cwd`. |
| SC-02 | **PARTIAL** | `case14` (line ~320-325) for the exit-code half only | Case14's grep-for-`exit [1-9]` + positive-control assertion is present and passes — the *second* clause of SC-02. The **first** clause — "when the root cannot be resolved, the block says UNRESOLVED and instructs `VERDICT: BLOCKED`" — has **no test case** anywhere in `test-inject-expertise.py`. `grep -n "UNRESOLVED\|BLOCKED"` on the file returns nothing. |
| SC-03 | **PARTIAL** | `test-check-instruction-paths.py:47-48` | Only 3 of 5 canonical sites are individually asserted in the committed test (`harness-qa-gate/SKILL.md`, `harness-expertise/SKILL.md`, `harness-handoff/SKILL.md`). S4 (`.omp/agents/harness-backend-dev.md`) and S5 (`.claude/skills/harness/templates/PLAN.md`) are **not** asserted by name in the committed suite (confirmed present manually at §4, but that is my probe, not a committed regression test). |
| SC-04 | **satisfied** | `test-anchor-directions.py`, all 6 rows + whole-scope run | Read via `git -C <root> show <ref>:<path>`, ref pinned via `HARNESS_REVIEW_SHA`; each of S1-S5 individually asserted with direction; whole-scope run at the pin: 0 violations. |
| SC-05 | **satisfied** | `test-check-instruction-paths.py:29` ("inline and fenced relative paths are both violations") | Asserts exit 1, both line numbers (`:1:`, `:3:`), and `2 violation(s)`. Independently reproduced at §4 with a fresh negative fixture. |
| SC-06 | **NO CARRIER** | none | T-05 item 3 explicitly mandates a case proving the debugging-skill path resolves from a product-shaped cwd with no `.agents`/`.claude`, AND that the pre-change bare spelling does not exist relative to that cwd. `grep -n "systematic-debugging\|product clone\|product-shaped" test-check-instruction-paths.py` returns nothing. Neither half of SC-06 has a committed test. |
| SC-07 | not-my-kind | — | `verify: inspection` |
| SC-08 | **PARTIAL** | none for the mutation-proof half; CI wiring confirmed present by direct read | `.github/workflows/tests.yml:204-216` does run the checker in the `integration` job and fails on non-zero exit and on a missing summary line — confirmed by direct read, so the *production* wiring exists. But T-12's own mandated committed test (one function taking a workflow path, fed the real file plus two mutants — step-deleted, failure-branch-removed) is **absent** from `test-check-instruction-paths.py` (`grep -n "tests.yml\|workflow\|mutant"` returns nothing). SC-08's own text: "An assertion never shown red is not evidence that the job can fail" — here there is no assertion of this shape at all. |
| SC-09 | not-my-kind | — | `verify: inspection` |
| SC-10 | **satisfied** | `test-inflight-registry.py:case35` | 5 sub-assertions, all PASS: linked-worktree basename resolves to the worktree path (differs from owner root), no-worktree case resolves to owner root, short-form basename accepted, `--feature` required. |
| SC-11 | **satisfied** | `test-anchor-directions.py` row 6 + `test-check-instruction-paths.py:35` | Row 6 min_occurrences=2 both-span proof at the pin; RED proof ("control-plane feature path is refused") independently reproduced at §4. |
| SC-12 | **NO CARRIER for its own discriminating clauses** | `test-inject-expertise.py:case4` only exercises the `unknown` branch | SC-12 requires two committed cases: a clean fixture agent file yielding `HARNESS_PATH_DRIFT: none`, and the SAME file with one relative span added yielding `HARNESS_PATH_DRIFT: 1 unanchored path(s)` naming the file and line — "observed rather than assumed." `grep -n "PATH_DRIFT"` in the test file finds only case4's assertion of the `unknown` state (which fires because the fixture root has no `.omp/agents/<agent>.md` at all, an unrelated reason). Neither the `none` state nor the RED `N unanchored path(s)` state is tested anywhere. |
| SC-13 | **NO CARRIER — most serious gap** | none | T-09 mandates exactly four new cases in `test-dispatch-guard.py` (REFUSED / ALLOWED / DISCRIMINATION-IN-OTHER-DIRECTION / MISMATCH-REFUSED) against fixture roots carrying `.omp/agents/` entries for a shell-less and a bash-holding persona. `grep -n "HARNESS-FEATURE-TREE-ROOT\|feature_root\|tree-root"` across the entire `test-dispatch-guard.py` file returns **nothing**. Worse: every one of the file's existing 42 cases builds its fixture via `_checkout()`, which creates **no `.omp/agents/` directory at all** — and the new block's own step 1 says "If the file is missing... PASS THROUGH." So the production code at `dispatch-guard.sh:147-175` (confirmed present and correctly shaped by direct read) is silently bypassed by every existing case. T-09's verify clause is green **because the new logic never fires in the suite**, not because it is proven correct. |
| SC-14 | not-my-kind | — | `verify: inspection` |
| SC-15 | **satisfied** | `test-check-domain.py:3426-3429` ("SC-15 PAIR") | Foreign product cwd allows the feature-worktree receipt write (exit 0) and refuses the same path's in-product twin (exit 2), same fixture and cwd. |

## 4. Falsifiability probes (fresh fixtures under `/tmp`, removed after)

- **Fixture A** (SC-05 shape: `.omp/agents/harness-backend-dev.md` with one inline
  `` `.harness/harness.json` `` and one fenced `.claude/agents/harness-pm.md`): checker exit **1**,
  both violations named with file **and** line number (`:1:`, `:4:`), `2 violation(s)`.
- **Fixture B** (SC-11 shape: `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/features/FEAT-99-x/notes/receipt-agent.md`):
  checker exit **1**, names file/line, message
  "feature-directory path anchored to the control plane".
- `--list-scope` at the pin: **62** entries (non-empty), each of S1-S5 confirmed present
  individually by exact string match (§3 table header).
- SC-02 positive control: committed, in `case14` — `grep`-equivalent Python scan of the shipped
  `inject-expertise.sh` finds **zero** `^[ \t]*exit [1-9]` matches, and the same pattern against a
  one-line `exit 2` fixture matches **exactly one** — confirmed passing (`PASS case14`).

(Note: `mktemp -d` on this host resolves under `/var/folders/...`, which `bash-write-guard`
blocked for a bare shell redirect in this session; fixtures were built under plain `/tmp/...`
instead, which the guard permitted. Recorded per Q-01 in my own Expertise — the guard's
posture toward this path shape is inconsistent session to session.)

## 5. Test-matrix gate

`test_matrix` in `.harness/harness.json`: `logic -> always:[unit]`, `docs -> always:[]`,
`config -> always:[]`, no other change_types present among the 15 tasks (T-01/02/03/09/14/15 =
logic; T-04..08/10/11/13 = docs; T-12 = config). **Required floor: `unit` only.** T-12 touches
`.github/workflows/tests.yml`, adding a CI step — I read DEC-212's `touches_config_shape`
trigger as scoped to configuration a *gate script reads* (e.g. `team-config.yaml`), not CI
workflow orchestration, so I do not read it as tripping the `integration` floor; flagging this
reading as an open question rather than asserting it silently.

- `run-unit-tests.sh --kind unit` (scoped): **exit 0.** Includes `test-check-instruction-paths.py`,
  `test-inject-expertise.py`-class scripts, `test-anchor-directions.py`, all UNIT_SCRIPTS.
- `run-unit-tests.sh` (unscoped, full): **exit 1**, but the **only** failures are the six
  pre-briefed `test-check-plan-routes.py` sub-cases, each printing the identical
  `DEVIATION <worktree>/.harness/team-config.yaml differs from <main checkout>/...` line — the
  known, out-of-scope environmental drift. No other `FAIL` line appears anywhere in the log.

`matrix_ok: false` — not because the declared floor kind failed to run (it ran green), but
because the criterion-level "presence" test (verification-rules: "presence is not satisfied by
an unrelated existing test") fails for SC-06, SC-08, SC-12 and SC-13: the unit/integration kind
that is supposed to carry each of those criteria's discriminating clause contains no case that
exercises it. SC-13 in particular means the `integration` evidence claimed for a **load-bearing
security control** (the shell-less-lead write-anchor guard) has never been exercised by any
committed test.

## 6. Test-first audit

History from merge-base to the pin is one squashed commit per task (`f031794e [T-02]`,
`c92043a3 [T-09]`, etc.) — impl and test land together in each task's single commit. This
granularity does not expose intra-task ordering (test written before or after the production
code within the same commit), so I cannot audit test-first compliance below the task level from
git history alone; reporting this honestly rather than guessing.

## Findings, severity, blocking

1. **[high, blocking]** SC-13: zero test coverage for `dispatch-guard.sh`'s new
   `HARNESS-FEATURE-TREE-ROOT` enforcement block. Production code is correctly shaped
   (`.agents/skills/harness/bin/dispatch-guard.sh:147-175`) but every existing
   `test-dispatch-guard.py` fixture bypasses it via a fixture root with no `.omp/agents/`
   directory. A regression here (e.g. the mismatch check silently removed) would ship undetected.
2. **[high, blocking]** SC-12: the `HARNESS_PATH_DRIFT: none` clean case and the
   `N unanchored path(s)` RED case (SC-12's own "observed rather than assumed" RED path) are
   both untested; only the unrelated `unknown` branch is exercised.
3. **[med, blocking]** SC-06: no committed test proves the family-5 product-clone
   debugging-skill read-through in either direction.
4. **[med, blocking]** SC-08: the CI-enforcement mutation proof T-12 mandates (two mutant
   workflow files) does not exist; only the production wiring itself was confirmed, by direct
   read, not by a committed assertion able to go red.
5. **[low]** SC-02: the UNRESOLVED/`VERDICT: BLOCKED` behavioral branch untested (exit-code
   clause is fine).
6. **[low]** SC-01: the cwd-differs discriminating assertion is not made; case4 would pass
   identically if the injected root happened to equal the invoking cwd.
7. **[low]** SC-03: 2 of 5 canonical sites (S4, S5) not individually asserted in the committed
   scope-completeness test.

## Open questions

- Is DEC-212's `touches_config_shape` intended to reach a CI workflow-file structural addition
  (T-12), or only configuration a gate script parses at runtime? I read it as the latter and did
  not raise the matrix floor to `integration` on that basis — routing for confirmation since
  the answer changes `matrix_ok`'s stated reason.
- Findings 1-4 read as executable specification gaps against the plan's own explicit task text
  (T-09 item "FOUR NEW CASES", T-05 item 3 "PROVE THE READ", T-03 item 6, T-12 "the committed
  assertion... AND the proof"), not ambiguity in what was asked. Routing to eng-lead/backend-dev
  to close before ship rather than resolving myself, since closing them is production-test
  authorship, not evidence-gathering.
