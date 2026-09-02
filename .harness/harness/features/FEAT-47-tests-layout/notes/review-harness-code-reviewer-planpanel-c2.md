# Plan review — FEAT-47-tests-layout — plan-panel / scope — cycle 2

**BLUF. Not signable.** Cycle 1's `critical` F-01 remedy (D-16's line-exemption census + T-07) correctly
closes the four sources c1 named — but c1's own audit of "which live files assert the deleted arrays as
current" was itself incomplete. A fresh, repo-wide sweep for `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`/
`check-kinds` (excluding the three record prefixes T-06's residue mode excludes) finds **three more
live, currently-tracked files** doing exactly what F-01 was about, that no task in this plan touches and
that T-07's exemption list does not cover. This is proven from the current tree alone, no execution
needed. Independently, `plan.yaml`'s own decision-log number, `DEC-207`, is **already taken** in
`DECISIONS.md` by an unrelated FEAT-45 entry, which makes T-06's most direct "did you write the new
entry" check vacuously true today. Both are new findings this cycle; everything c1 raised is otherwise
correctly discharged, and the census/depends_on/REQ-tracing mechanics are sound and re-verified below.

## New finding 1 — critical — REQ-07's Expertise census missed three more live files

T-07's `files:` list repairs exactly `harness-eng-lead.md` (G-02) and `harness-code-reviewer.md` (G-04).
No other task touches an Expertise file (confirmed: `plan.yaml` contains no reference to
`harness-dev-ops.md`, `harness-pm.md` or `harness-qa.md` by path or by entry id). Yet, at the current
tree, `git grep -n UNIT_SCRIPTS -e INTEGRATION_SCRIPTS -e check-kinds` (excluding the same three record
prefixes T-06's residue mode excludes, and excluding the sources c1 already found and this plan already
fixes) also matches:
- `.harness/harness/expertise/harness-dev-ops.md:13` — G-10, "WHEN `run-unit-tests.sh`'s
  `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays are touched by a merge from `main` DO run `--check-kinds`
  immediately after..."
- `.harness/harness/expertise/harness-pm.md:3` — P-01, "WHEN a criterion declares `evidence: unit` DO
  confirm the file holding its assertions is in run-unit-tests.sh's `UNIT_SCRIPTS` and not
  `INTEGRATION_SCRIPTS`..."
- `.harness/harness/expertise/harness-qa.md:8` — G-05, "WHEN a feature branch's later merge-from-main
  reintroduces run-unit-tests.sh's `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` entries... DO expect the
  KIND-DRIFT union check to exit 2..."

All three are git-tracked (confirmed via `git ls-files`), all three sit under
`.harness/harness/expertise/` (injected at every spawn of those three personas, same as the two T-07
fixes), and none is one of T-05's three declared `(path, fragment)` exemption pairs. `.harness/harness/
expertise/` is not one of the three record prefixes T-06's residue mode excludes, so all three matches
are live findings the sweep WILL report. **Consequence:** `T-06`'s own verify — which runs
`python3 tests/manual/suite-census.py residue` with no `--ref` (working tree) — fails on the very first
run, for the identical reason c1's F-01 failed, via three instances neither c1's audit nor this plan's
authors found. REQ-07 ("No live file presents the deleted arrays or their cross-check as current") is
not met by this plan as scoped, and it is not a hypothetical: it is checkable today with zero execution.
**The fix is a plan decision** (add these three files to T-07's scope and repair them the same way, or
widen the census — record it as D-19, not mine to make) but the finding itself is not in question.

## New finding 2 — high — `DEC-207` is already taken; T-06's presence-check is currently vacuous

`grep -oE '^## DEC-[0-9]+' .harness/harness/docs/DECISIONS.md | sort -n | tail -1` returns `207` **today**
(`.harness/harness/docs/DECISIONS.md:6339`, title "A gate may grade a specification before any code
exists..." — FEAT-45-adversarial-plan-panel's own governing entry, unrelated to tests layout). T-06's
intent anticipates a number collision ("RE-DERIVE IT... if it is not DEC-207, take the next free number
and update every `dec:` field in this plan, this task's verify and the team-config comment T-01 writes,
in the same commit") — but three problems survive that instruction:
1. `grep -q "^## DEC-207 " .harness/harness/docs/DECISIONS.md`, T-06's own verify line, is **already
   true today**, against the unmodified tree, because of the pre-existing unrelated heading. It is a
   presence check with no content discrimination — it cannot tell "T-06 wrote its new entry" from
   "T-06 wrote nothing and an unrelated entry from a merged sibling happens to share the number."
2. If the executor correctly re-derives (since 207 is taken, the free number is 208+) but forgets the
   specific sub-step "update... this task's verify," the *executed* check still reads `DEC-207` and
   still passes vacuously — silently certifying a step that never ran.
3. The remediation also asks to update "the team-config comment T-01 writes" — but `.harness/
   team-config.yaml` is not in T-06's `files:` list, so that repair is outside T-06's declared scope
   even when performed correctly.
Nine of this plan's own D-NN entries (D-01–D-04, D-08, D-14–D-16, D-18) currently cite `dec: DEC-207`,
all of which are already stale against the live tree. `gen-decisions-index.py` does catch a literal
*duplicate* heading (`COLLISION: duplicate decision key`, `gen-decisions-index.py:121`) if the executor
blindly appends a second `## DEC-207`, so the worst "silent" outcome is bounded to the specific
forgotten-self-edit path in (2) above — which is why this is `high` and not `critical`.

## New finding 3 — med — `suite-census.py`, backing 5 of 10 SCs, has no dedicated test of its own

`suite-census.py` is the sole instrument for SC-01, SC-02, SC-07, SC-09 and SC-10 — including the whole
REQ-07 remedy. No task creates a test file for it (`tests/unit/test-suite-layout.py` tests
`suite_layout.py`; `tests/integration/test-run-unit-tests-layout.py` tests the runner's `--check-layout`;
neither drives `suite-census.py`'s four subcommands against synthetic fixtures). It is exercised only by
T-05's verify (`migration`, `verdict-lines --strict`) and T-06's verify (`residue`), always against the
real repository in its intended-correct end state — never against a deliberately-bad fixture. In
particular, D-16's four residue self-refusal rules (reject an expertise-dir exemption; reject a
non-matching pair; require the positive control non-empty; print covered lines) are prose in the intent
only — nothing proves any of the four actually fires. This is exactly the "who watches the watcher"
question the dispatch asks: the refusal mechanism that is supposed to make F-02-class fail-open
structurally unreachable is itself never driven to the failing case.

## New finding 4 — med — T-07's verify can pass on a content-gutted stub

T-07's verify checks: no forbidden token; `"tests/integration" in` each file's full text; `"- G-02:"` /
`"- G-04:"` present. `check-expertise.sh` (read in full) enforces section names, per-entry word cap,
id format and file budget — it does **not** enforce the WHEN/DO shape T-07's intent mandates ("keep the
WHEN/DO shape"). A replacement entry gutted to e.g. `- G-02: see tests/integration` passes every
assertion in T-07's verify and passes `check-expertise.sh`, while losing the insight the task exists to
preserve. Given T-07 is `main-session-direct` (no independent reviewer gate before merge), this is a
real, if narrow, gap.

## Verify audit — T-01..T-07, both questions

| Task | (a) What makes it red | (b) Tree where it passes? |
|---|---|---|
| T-01 | Inline classifier assertions on `is_control_plane_target`/`is_control_plane_glob`; the two test files. | Yes. Re-verified against `harness_boundary.py:234-242,370-381` directly: appending `tests/**` to `HARNESS_CONTROL_PLANE` (a target-only list) and leaving `is_control_plane_glob`'s four-prefix check untouched produces exactly the claimed split. Sound. |
| T-02 | Floor `n -ge 39`; per-file rename record; `python3 "$f"` per moved file. | Yes. Re-derived the 38-name enumeration independently (script, no shell redirect): 38 unique names, zero overlap with T-03's 19, union plus `test-run-unit-tests-kinds.py` equals exactly the 58 tracked names today — nothing missing, nothing extra. `git rev-parse origin/main` = `75daa3b`; `git ls-tree` there also counts 58. Sound. |
| T-03 | Floor `n -ge 20`; per-file rename; exact bin residue; `.test.ts` absence; each file run. | Yes, same re-derivation. `test-suite-independence.py`'s anchor recipe (`root_above`, no climb, sys.path-only fix) matches FEAT-48's actual T-03 intent verbatim (root_above vs root_from_script vs resolve_root reasoning, `--scan-dir`) — checked against FEAT-48's live plan text, not restated from memory. Sound. |
| T-04 | `git ls-files --error-unmatch`; zero `probe-*` in bin; `compile()`. | Yes, trivially — move plus valid syntax. Provenance sentence "It was first registered in" confirmed present verbatim at `probe-omp-session-accessor.py:14`. Sound (weak by design, per REQ-08's disclosed gap, not a new issue). |
| T-05 | `--check-layout`/`--bogus`; pool-arg parse; per-kind tally-set equality; `suite_layout` unit tests; sole-implementation sweep; `migration --floor 58`; `verdict-lines --strict`. | Yes on every point hand-traced, including against FEAT-48's actual `run_pool.py` invocation line (`--mutation-check "$BIN_DIR"`, confirmed byte-identical in FEAT-48 `plan.yaml`) and D-11's watched-directory argument. 104 tracked `.py` files confirmed today (claim: 104, floor 90 — non-vacuous, not raised to match). Sound, no change from c1. |
| T-06 | Index-sync; `test-gen-decisions-index.py`; `test-check-decision-anchors.py`; `grep DEC-207`; `suite-census.py residue`. | **No.** New finding 1 makes `residue` fail on first run (three unaddressed Expertise files). New finding 2 makes the `grep DEC-207` line pass **vacuously today**, independent of finding 1, and risks silently certifying a skipped self-edit even after finding 1 is fixed. |
| T-07 | `check-expertise.sh`; token absence; `"tests/integration" in` text; id lines present. | Yes for a faithful edit. Also yes (wrongly) for a content-gutted stub — new finding 4. Not affected by finding 1 (T-07's own two files are correctly repaired; the gap is the other three files T-07 never touches). |

## Cycle-1 findings — disposition

- **F-01 (critical, T-06's residue sweep unsatisfiable against its own mandated content), and its four
  named compounding sources** — **discharged as literally stated.** Re-verified all four at source:
  DECISIONS.md's "Eight of twelve" fragment still present verbatim (`DECISIONS.md:5588`) and is now
  D-16's first declared exemption, with T-06 step 3 instructing the surrounding present-tense sentences
  fixed (confirmed those sentences — "The fix is... which leaves..." — are still present-tense today,
  exactly as c1 quoted, so the repair instruction targets real text). The two Expertise files are now
  T-07's scope. The probe's provenance sentence is D-16's second exemption, confirmed present verbatim.
  `test-factory-integration.py`'s two FEAT-33 sentences are confirmed present at exactly two sites
  (lines 1384, 1434 — no third occurrence in that file), matching T-02's explicit strike instruction.
  **However**, the underlying defect class recurs: cycle 1's own audit of "which live files assert the
  deleted arrays" was itself incomplete (see new finding 1). F-01 as *named* is closed; the *hazard* it
  represents is not, via three instances outside its scope.
- No other findings were filed in c1 (only "Checked and clean" notes and one explicitly-unfiled minor
  point about T-02's mechanism wording, which remains correct-conclusion / imprecise-mechanism and has
  no consequence, per c1's own framing — not re-litigated here).

## Checked and re-confirmed sound (no new issue)

- REQ-01..REQ-08 all traced by ≥1 task; every `traces:` cites a real REQ; no orphan in either direction
  (re-verified against the current 8-REQ BRIEF).
- `depends_on` is acyclic and correctly orders the "known red window": T-02 opens it, T-03 closes it in
  the same task whose verify re-runs `test-no-distribution.py` from its new home; no task between reads
  the runner in the broken state. T-06 correctly `depends_on: [T-05, T-07]`, so T-07's Expertise repair
  lands before T-06's residue sweep runs (order is right; finding 1 is a scope gap, not an ordering bug).
- Census arithmetic: 38 + 19 + 1(deleted) = 58 = today's tracked count, independently re-derived by
  script, zero mismatch either direction. Post-FEAT-48 (39+20+1=60) matches FEAT-48's own D-09 contract,
  cross-checked against FEAT-48's live plan text, not restated from a coupling note.
- SC-05's regex/fragment sweep: `test-panel-findings.py` and `test-plan-panel.py` (FEAT-45's two files)
  genuinely do not match the `tests/unit`/`tests/integration` regex — confirmed by running the claimed
  regex against both files directly (zero matches), so the "104 tracked, exemption list stays at 4"
  claim holds.

## What I could not evaluate

- `goalcheck_path` does not exist — expected pre-signature, recorded rather than treated as satisfied.
- Neither this plan nor FEAT-48 has executed. All soundness claims above are against plan **text** (this
  plan's and FEAT-48's) plus the **current tree** state (git-verified directly, not hand-traced), never
  against a running suite, `suite_layout.py`, `suite-census.py`, or the rewritten `run-unit-tests.sh`,
  none of which exist yet.
- I did not independently re-derive every `dec:` field's eventual correctness beyond DEC-207 itself
  (e.g. D-05/D-06/D-07/D-17's citations to DEC-187/DEC-197/DEC-174/DEC-145, which are pre-existing
  numbers and unaffected by the collision) — only the nine `dec: DEC-207` placeholders, which are the
  ones this feature's own unwritten entry would occupy.
- I did not verify `test-gen-decisions-index.py`'s or `test-check-decision-anchors.py`'s internals
  beyond confirming `gen-decisions-index.py` itself detects duplicate headings; I relied on that to
  bound finding 2's worst case rather than tracing both test files line by line.

## Stopping rule

Two fresh findings clear the `high`/`must_fix` bar this cycle (one `critical`, one `high`), both
concrete, provable from the current tree without execution, and not raised in cycle 1. **The plan is
not signable as written, and I would not sign it.** The remedy is narrow and does not require
re-opening cycle 1's structural design (D-16's census mechanism is sound and re-verified): widen T-07's
scope (or add a task) to repair `harness-dev-ops.md`, `harness-pm.md` and `harness-qa.md` the same way,
and either free `plan.yaml`'s decision number from the taken `DEC-207` before signature or make T-06's
verify assert on the new entry's distinguishing content rather than on the bare number.

---

**Compact findings for transcription:**

critical | T-07 repairs only 2 of (at least) 5 live Expertise files that assert `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`/`check-kinds` as current craft (`harness-dev-ops.md:13`, `harness-pm.md:3`, `harness-qa.md:8` are untouched by any task and uncovered by any of T-05's three declared exemptions) | T-06's residue sweep (its own verify, `suite-census.py residue`) fails on the first run, for the same class of defect cycle 1's F-01 named, via instances neither cycle 1 nor this plan's authors found; REQ-07 is not met by this plan as scoped.
high | `DEC-207`, the number every `dec:` field in this plan's decisions cites for its own new entry, is already taken in `DECISIONS.md` by an unrelated FEAT-45 entry; T-06's verify line `grep -q "^## DEC-207 "` is vacuously true against the unmodified tree today | T-06's explicit self-healing instruction (re-derive, then edit the plan's own verify text) is the only thing standing between this and a silently-skipped "did you write the new decision entry" check; forgetting that one sub-step leaves the check passing on nothing.
med | `suite-census.py`, the sole instrument behind SC-01/02/07/09/10, has no dedicated test driving its own subcommands (especially `residue`'s four self-refusal rules) against a synthetic bad-input fixture | The mechanism built specifically to make REQ-07's remedy fail-closed is never itself proven able to fail; a bug in the refusal logic would ship silently and only be caught, if at all, by a human at inspection time.
med | T-07's verify (token-absence + substring-presence + id-line-presence) does not enforce the WHEN/DO shape its own intent mandates, and `check-expertise.sh` doesn't either | A content-gutted stub entry (e.g. "see tests/integration") passes every automated check while losing the insight the task exists to preserve.
