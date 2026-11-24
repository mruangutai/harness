# Goal-check (validate c5, final round) — FEAT-2488-plan-merge-atomicity

- **Pin:** `45f16cfa9f5ceb063d3d12987e3a6824b5929f35`
- **Base:** `2491336e`
- **Round-4 delta:** `d4fab731..45f16cfa`
- **Run:** r-20261124-6-validate-validator
- **Reader:** harness-pm (goalcheck)

## BLUF: PASS

All three perspectives pass, and SC-01 through SC-07 are met at the pin.

- **MF-11 (stdio class) is closed as a class.** It was repaired in the implementation, under the same contract (P-06).
- **MF-12 (journal class) is closed as a class.** It was closed by the ruled remedy (b) and the ledgered T-01 amendment.
- **No regression in the delta.** I found no new gating instance of either class in a changed surface.
- **Scope held.** Round 4 stayed inside the c3 fix brief, and the C4 forbidden surfaces are untouched.
- **Decision dispositions.** All six `decisions_affected` rows are `keep`, so none is graded.
- **Findings.** Two form advisories, F-5 and F-6. Neither is substance and neither gates.

## How I measured

**Binding.** HEAD is `66655995`. The only change after the pin is to `feature.json` (the re-pin). `review_sha` at HEAD equals the pin.

**Runs.** All runs used a `git archive 45f16cfa` copy in `/tmp/goalc5`. I stripped `HARNESS_AGENT_TYPE`, `CLAUDE_PROJECT_DIR`, `HARNESS_PROJECT_DIR` and `PYTHONUNBUFFERED` from the environment.

**Mutants.** Each mutant is one single-point edit to its own copy. Apart from this note, nothing in the repo was written.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | **pass** | SC-01, SC-04, SC-07 | See the operator detail below. |
| code maintainer | **pass** | SC-02, SC-03, SC-06 | See the code-maintainer detail below. |
| reader (qa / reviewer) | **pass** | SC-05, SC-01 | See the reader detail below. |

**Operator detail.**
- The pin's `test-plan-merge.py` ran rc 0 with 943 PASS rows and 0 FAIL. That includes the torn-state rows 2488/a–j (122 rows), 2488/g (exact receipt lines) and 2488/n, the child-CLI stdio matrix (94 rows).
- The unit journal suite ran rc 0, 202/202.
- The six SC-07 suites are byte-unedited from base to pin (`git diff --quiet` rc 0), and each ran rc 0 with 0 FAIL.

**Code-maintainer detail.**
- `harness_merge.py` stays the one cross-file mechanism.
- Its docstring now states the one-name discovery. It also states that a feature.json-named journal "is never discovered", which matches `_journals_naming`, a single `os.lstat` of `_JOURNAL_NAME`.
- I grepped the pin's harness_merge, plan-merge.py, plan_merge and check-domain for `listdir`, `endswith(JOURNAL_SUFFIX)` and "named for another file". There were no matches.

**Reader detail.**
- Every new 2488/n, 2488/o and foreign-journal row goes red against the pre-fix file, and against single-point mutants (below).
- The test-plan-merge.py delta only adds lines (+204, 0 deletions).
- The one unit-test deletion, `case_reversed_primary_refuses_before_any_lock`, was ruled correct, and its lock-order guarantee is asserted by the foreign matrix's "takes only … in the one order" rows.

## SC status

- **SC-01 — met (automated, integration).** The full run is described above. The advisory-after-commit clause is now evidenced across every stdio state (see (5)).
- **SC-02 — met (inspection).**
  - `guards.py#_emit` and `#_silence` add only stdio syscalls: `os.open(devnull)`, `dup2` and `close`. There is no mkstemp, no `os.replace` and no journal access.
  - The pair write is still one `locked_pair_update` call.
  - T-02's verify-tail assertion "no rename primitive or journal handling in plan_merge" passed at the pin.
- **SC-03 — met (inspection, carried).** The delta does not touch the fsync ordering in `locked_pair_update`. The only harness_merge hunks are the docstring, `_JOURNAL_NAME`, `_journal_names`, `_journals_naming` and `_recover_journal`'s removed name check.
- **SC-04 — met (automated).** The 2488/g rows pass, including "neither carries APPROVAL-RESET".
- **SC-05 — met (inspection, carried).** test-plan-merge.py has no deletions in the delta, so the successors and their 8+ check() calls are unchanged.
- **SC-06 — met (inspection, carried).** The harness_merge docstring keeps its lock-order paragraph (plan.yaml.lock then feature.json.lock). The other SC-06 files are unchanged in the delta.
- **SC-07 — met (automated).** As stated under the operator detail.

## Judgement points

### (1) The T-01 intent amendment is truthful

**Clause: "journal discovery is JOURNAL_PAIR[0] + JOURNAL_SUFFIX only".** True. `_JOURNAL_NAME = JOURNAL_PAIR[0] + JOURNAL_SUFFIX`, looked up as a path. D1 is ruled approved, so the APFS case variant is the producer's own file, not a contradiction.

**Clause: "a foreign-named journal is never read, never wedges, never replayed".** True, by measurement:
- The pin passes 40 foreign rows. They cover three planted names across five routes, `recover_journals` returning False for three paths, and a FIFO under a foreign name that never hangs.
- The pin's unit suite run against `d4fab731:harness_merge.py` fails 31/185. Every foreign row reddens with JOURNAL UNREADABLE naming the foreign file, and both FIFO rows exit 5.

**Clause: "an unreadable real journal still refuses exit 5".** True. Four routes pass at the pin.

**Supersession of c1 amendment (5).** The c4 amendment supersedes c1 amendment (5)'s refuse-before-lock clause for non-primary names. That is true in code: the pre-lock name refusal is deleted from `_recover_journal`. In text it holds only by later-in-time precedence, which is F-5.

### (2) The amended verify runs the check-domain test, and the signature stands

**Verify.** The verify literally contains `tests/integration/test-check-domain-approval.py`. I ran it verbatim at the pin and got rc 0: seven pool files, "0 unresolved reader site(s)", and the docstring/API probe passed.

**Receipts.**
- Both receipts read `AMENDED tasks:T-01.{intent,verify} judgement=amendment` with two APPLIED lines each, and neither has an APPROVAL-RESET line.
- The INV-33 "STALE review_sha" VIOLATION inside them is the expected pre-re-pin state. It was cured by the re-pin at 66655995.

**Signature.**
- At the pin, `approval.status: approved` (delegated, 2026-11-23).
- `feature.json judgements` gains two `amendment` entries, one for `T-01.intent` and one for `T-01.verify`.
- `signed_task_hashes` is unchanged. The signature stands (DEC-23).

**T-02 verify.** I also ran it verbatim: rc 0.

### (3) Round 4 stayed inside the c3 brief

**Files.** Outside `.harness`, `git diff --name-only d4fab731 45f16cfa` lists exactly four files:
- `guards.py` (T-02)
- `harness_merge.py` (T-01)
- `tests/integration/test-plan-merge.py` (T-02)
- `tests/unit/test-harness-merge-journal.py` (T-01)

Every one is owned.

**`.harness` changes.** All of them are inside this feature's folder.

**Docs.** `.harness/harness/docs` is unchanged from base to pin (rc 0).

### (4) The C4 forbidden surfaces are untouched

I ran `git diff --quiet 2491336e 45f16cfa -- <path>` on each surface, and each returned rc 0:
- `check-plan-routes.py`
- `tests/integration/test-check-plan-routes.py`
- `check_state/`
- `plan_merge/union.py`
- `tests/integration/test-checker-structure-locks.py`

### (5) "The verb still exits 0 after commit" is now evidenced across stdio states

2488/n is all green for both verbs, under the full brief matrix: each stream in {working, broken, closed, None}, plus the four joint states. Its rows assert:
- rc 0
- both files landed once, with no journal
- stdout is exactly the receipts, so nothing is misrouted

2488/o is green for its three in-process states.

Old-file and mutant runs (the pin's test-plan-merge.py against one variant of guards.py each):

| guards.py variant | FAIL rows | Which rows |
|---|---|---|
| `d4fab731` (pre-fix) | 18 | (a) |
| mutant: drop `AttributeError` from `_STDIO_FAULTS` | 3 | 2488/o no-fileno rows |
| mutant: delete `_emit`'s `stream is None` guard | 2 | stderr=None "stdout is exactly the receipts", both verbs: the `file=None` misroute |

(a) The rows are:
- every stdout=None, both-None and mixed-None "exits 0" row, both verbs: the MF-11 rc-1 after commit
- stderr=None "stdout is exactly the receipts", both verbs: the misroute
- 2488/o no-fileno ×3
- "caller-owned fd 16 … the caller's pipe afterwards": the clobber

**Coverage.** Each of the ruling's named members (None stdout, None stderr misroute, no-fileno `_silence`, caller-owned fd) has at least one row that reddens on the defect, and no row is ever-green (O-07, O-08).

**Other prints.** plan_merge's remaining `print(` sites at the pin belong to verbs other than amend and record-amendments: approval, delete, panel, stations, union, and check/`--show`. All are base-semantics and outside the ruled class contract, which is scoped to those two verbs.

## Decision dispositions (Mode 2)

`decisions_affected` at the pin has six rows: DEC-229 ×2, DEC-199 ×2, DEC-174 and DEC-230. All six are `keep`, so none is graded. DECISIONS.md is unchanged from base to pin.

## Findings (none HIGH, none substance, none gating)

### F-5 (form, low, new)

**Where.** `plan.yaml` T-01.intent. Changed by this feature at 8f948c52, owned by T-01.

**What.** c1 amendment (5) still reads "refuses UNREADABLE … any journal not named plan.yaml.harness-merge.journal. A feature.json-primary journal is therefore refused before any lock". The c4 paragraph says such a file is "never read, never wedges", and that it replaces "item 5's suffix-wide discovery". That is original item 5, not amendment (5).

**Failure scenario.** A reader grading T-01 against amendment (5) expects exit 5 for `feature.json.harness-merge.journal` and calls the inert behaviour a regression.

**Assessment.** The ruling (answers-2026-11-24-c4-departures, the deleted-test section) settles that c4 supersedes it, and the code and docstring agree. This is a recurrence of the F-3 pattern: an amendment trail with no explicit supersession pointer.

### F-6 (form, low; a record-accuracy note on a ruled item, NOT a re-raise)

**What.** The verbatim OQ-3 wording calls `feature_json_write.py:227` "outside T-01's and T-02's files". At the pin, T-02's `files:` includes `.claude/skills/harness/bin/feature_json_write.py#write_feature_json`. This feature changed that function's body: the hunks at lines 225–226, commit range `2491336e..45f16cfa`.

**What still holds.** The relay line itself is unchanged context from base (base line 210). So "pre-existing at base" holds, and the ruling's own test, a new instance introduced by a changed surface, still does not fire.

**Failure scenario.** The backlog ticket inherits a false ownership premise and is filed as unowned by this feature.

**Remedy.** Correct the cited wording when the ticket is filed. The grade does not change.

## Static-only claims

- SC-02, SC-03, SC-05 and SC-06 are inspection items.
- F-5 and F-6 come from reading.
- Everything else was executed at the pin as described.

## Principles applied

- **P-06:** I re-measured both MF classes against the pre-fix files and against single-point mutants, not against the build note.
- **P-16:** I graded the amended T-01 intent clause by clause, including the earlier amendment it silently supersedes (F-5).
- **P-17:** I recomputed delta file ownership. All four changed code and test files are owned.
- **O-07 / O-08:** I ran the old files and one mutant per branch, and no row is ever-green.

## Open questions

- **OQ-c5-1 (non-blocking):** should the F-6 wording ("outside T-01's and T-02's files") be corrected in the ruling record before the OQ-3 backlog ticket is filed?
