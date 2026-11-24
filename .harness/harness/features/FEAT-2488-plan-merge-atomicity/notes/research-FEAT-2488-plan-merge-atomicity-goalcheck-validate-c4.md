# Goal-check (validate c4) — FEAT-2488-plan-merge-atomicity

- Pin: `6528b4db2f0725c6051bae22099aa064b23336bb` · Base: `2491336e` · Round-3 delta: `0ab2c053..6528b4db`
- Run: r-20261124-5-validate-validator · Reader: harness-pm (goalcheck)

**BLUF: PASS.** All three perspectives **pass**, and SC-01 through SC-07 are **met** at the pin.

- **MF-9 is closed by implementation repair under the same contract** (P-06). I measured it: under buffered stdio, T-02 amendment (7)'s "the verb still exits 0" is now true.
- **MF-10 is closed by the ruled remedy (a).** That remedy needed a ledgered T-01 files+intent amendment. The amendment describes the shipped check-domain change truthfully, and the signature stands: approval stays `approved`, and neither receipt contains `APPROVAL-RESET`.
- **Round 3 stayed inside the ruling's scope.** The C4 surfaces are untouched, and the test splits preserve every assertion.
- All six `decisions_affected` rows are `keep`, so none is graded.
- There are two form advisories (F-3 recurs, F-4 is new). Neither is HIGH, and there are no substance findings.

**Binding.** The worktree's `.claude` and `tests` equal the pin (`git diff --quiet 6528b4db -- .claude tests` returned rc 0). HEAD is `af7836c5`. The commits after the pin touch only `feature.json`.

**How I ran things.** Every run below used a `git archive 6528b4db` copy in `/tmp`, with HARNESS_AGENT_TYPE, CLAUDE_PROJECT_DIR and HARNESS_PROJECT_DIR unset. Each mutant is a single-point edit to one temp copy. Nothing in the repo was written apart from this note.

## Perspectives

| Perspective | Grade | Carried by | Evidence |
|---|---|---|---|
| operator | **pass** | SC-01, SC-04, SC-07 | The torn-state convergence and exit-5 refusals still pass (2488/a–j, unit journal 0 FAIL). A landed amendment now exits **0** when the stream is broken under buffered stdio. Before this round it exited 120 (MF-9, measured below). Both amend receipt lines are unchanged (2488/g). The six SC-07 suites are unedited since base, and all ran rc 0 with 0 FAIL rows. |
| code maintainer | **pass** | SC-02, SC-03, SC-06 | This delta adds no rename or journal I/O to plan_merge: `_silence` is a stdio dup2, not journal code. `harness_merge.py`, `feature_json_write.py`, `plan-merge.py` and `amend.py` are untouched in `0ab2c053..6528b4db`. The `_relay_after_commit` and `_print_receipts` docstrings now match measured behaviour. |
| reader (qa / reviewer) | **pass** | SC-05, SC-01 | Every torn state is still built on disk. The new 2488/l and 2488/m and T-09 13 rows each go red against the defect and against single-point mutants (below). Commit 6b22caef keeps the multiset of check/t09 labels identical: test-plan-merge 539/539, unit journal 73/73, check-domain-approval 29/29. |

## SC status

- **SC-01 (automated, integration) — met.**
  - I ran the pin's `tests/integration/test-plan-merge.py` with the parent exporting PYTHONUNBUFFERED=1 and each child stripping it (`_buffered_env`). Result: rc 0, 0 FAIL rows.
  - That run includes 2488/k (closed stderr, ValueError), 2488/l (broken stdout, both verbs) and 2488/m (broken stderr with a planted relay row, both verbs).
  - `tests/unit/test-harness-merge-journal.py` gave rc 0, 0 FAIL.
- **SC-02 (inspection) — met.** At `guards.py#_silence` and `#_note_on_stderr`, the only new syscalls are `os.open(os.devnull)`, `os.dup2` and `os.close`. There is no mkstemp or os.replace, and no journal access. The pair write is still one `locked_pair_update` call.
- **SC-03 (inspection) — met, carried.** `harness_merge.py` is unchanged in the delta (`git diff --name-only 0ab2c053 6528b4db` does not list it).
- **SC-04 (automated, integration) — met.** The 2488/g exact-line rows pass at the pin. `_print_receipts` keeps the same print-then-flush on a healthy stdout and diverges only inside its except branch.
- **SC-05 (inspection) — met, carried.** The delta does not touch the successors, and the split commit preserves the labels.
- **SC-06 (inspection) — met, carried.** None of the docstring or exit-code files changed in the delta.
- **SC-07 (automated, integration) — met.** Edits are absent: `git diff --quiet 2491336e 6528b4db -- <six suites>` returned rc 0. Each of the six suites ran rc 0 with 0 FAIL rows at the pin.
  - Because check-domain.py changed, I also ran all 9 `test-check-domain*.py` files at the pin: each rc 0, 0 FAIL.

## (1) T-02 amendment (7), "the verb still exits 0", is now TRUE (measured)

Each run below is the pin's test-plan-merge.py against one variant of `guards.py`:

| guards.py | 2488/l (stdout broken) | 2488/m (stderr broken) |
|---|---|---|
| pin | pass, rc 0 | pass, rc 0 |
| `0ab2c053` (pre-fix) | FAIL **rc=120**, "Exception ignored while flushing sys.stdout" (both verbs) | FAIL **rc=120** (both verbs) |
| mutant A: drop `_silence(sys.stdout)` in `_print_receipts` | FAIL (both verbs) | pass |
| mutant B: `_note_on_stderr`'s except does nothing instead of `_silence(sys.stderr)` | pass | FAIL (both verbs) |

- Each branch reddens its own rows and no case is ever-green (O-01, O-08).
- 2488/k stays green at the pin. The closed-stream ValueError is suppressed inside `_silence`.
- In every red run both files landed and no journal was left, so the old defect was only ever the exit code.

## (2) T-01 ledgered amendment — truthful; signature stands (DEC-23)

**What was recorded.** feature.json at the pin holds `judgements[8]` (`T-01.files`) and `judgements[9]` (`T-01.intent`), both kind `amendment` and both citing AdvisorE4Esc and MF-10.

- The receipts (`notes/fix-c3-build/amend-T-01-{files,intent}-receipt.txt`) read `AMENDED … judgement=amendment` with two APPLIED lines each. `grep -c APPROVAL-RESET` returns 0 for both.
- The `approval` mapping at the pin is byte-for-value equal to `0ab2c053`'s: `status: approved`.

**files.** At the pin, the loaded T-01 `files` are the four prior entries (values unchanged; only the indentation changed) plus `.claude/skills/harness/bin/check-domain.py` and `tests/integration/test-check-domain-approval.py`. Every code or test file changed base→pin is now owned by T-01 or T-02 (unowned set: `[]`). That closes the P-17 gap check-domain would otherwise open.

**intent, clause by clause:**

| Clause | Verdict | Evidence |
|---|---|---|
| "denies governed Write/Edit/NotebookEdit of `plan.yaml.harness-merge.journal` and `feature.json.harness-merge.journal` in a feature directory" | true | Write is measured on all 4 routes by T-09 13. Edit and NotebookEdit are measured by my own probe on the pin's hook: exit 2 with the journal denial, for both names. |
| "the same as-typed, symlink and hardlink routes as the plan.yaml denial" | true | It is the same `_plan_route`, parameterized. Mutant cd2, which drops `names` from the hardlink call, reddens only the two hardlink rows. Case folding is also covered (`re.IGNORECASE`): mutant cd3, without it, reddens only the two case-folded rows. |
| "naming plan-merge.py as the only writer" | true | The denial text, asserted by T-09 13. |
| "names spelled literally … a test pins them to `JOURNAL_PAIR` + `JOURNAL_SUFFIX`" | true | The test pins its own tuple to harness_merge. check-domain's `_PAIR_JOURNALS` is pinned transitively: mutant cd1, which renames one literal, reddens that name's 4 denial rows. Running the pin's test against `0ab2c053`'s check-domain.py reddens 8 of 8 denial rows while the notes/ controls and the plain-plan.yaml row stay green. |

## (3) Scope — inside the ruling

- **Changed in the delta:** `check-domain.py` (MF-10), `plan_merge/guards.py` (MF-9) and three test files: MF-9 tests, the MF-10 test, and the 6b22caef splits with their label multisets identical.
- **Plan:** `plan.yaml` gained only the T-01 files+intent amendment.
- **Feature folder:** notes and run records.
- **C4:** `git diff --stat 2491336e 6528b4db` over `check-plan-routes.py`, `tests/integration/test-check-plan-routes.py`, `check_state/` and `plan_merge/union.py` is empty, and so is `.harness/harness/docs`.
- **Nothing beyond the ruling:** no Bash-route work, no OQ-3 relay change in `feature_json_write.py`, and no sanitization growth.

## Decision dispositions (Mode 2)

At the pin, `decisions_affected` has six rows: DEC-229 ×2, DEC-199 ×2, DEC-174 and DEC-230. All six are `keep`, so none is graded. DECISIONS.md is unchanged base→pin.

## Findings (no HIGH; no substance)

- **F-3 (form, low; recurs and extends c3's F-3)**
  - **Surface:** a plan-text surface changed by this feature, `plan.yaml` T-01.intent, commit 54d02325, owned by T-01.
  - **What:** the new MF-10 paragraph again sits after the closing line "The signature stands (DEC-23); this is the ledgered judgement."
  - **Failure scenario:** a reader who takes that line as the end of T-01's deviations misses the check-domain duty.
  - **Assessment:** the text is truthful. This is not a gate.
- **F-4 (form, low, new)**
  - **Surface:** the plan field `T-01.verify`. This round did not change the field, but T-01 now owns check-domain.py.
  - **What:** T-01.verify does not run `tests/integration/test-check-domain-approval.py`.
  - **Failure scenario (measured by reasoning only, static):** with mutant cd1/cd2/cd3 applied, T-01's own verify stays green. Only the integration kind, run at validate and in CI, catches the regression.
  - **Assessment:** the integration gate covers it, so this is not a gate. Backlog, or add the file at the next amend.
- **Parity note (not a finding).** `MultiEdit` is not routed by check-domain for either the journal or plan.yaml. `git grep MultiEdit` in settings, check-domain and .omp at the pin returns nothing, so the tool is not wired here. This is pre-existing parity.

## Static-only claims

- SC-02, SC-03, SC-05 and SC-06 are inspection items.
- F-4's failure scenario was not run.
- Everything else above was executed at the pin.

## Principles applied

- **P-06:** I re-measured MF-9 and MF-10 against the defect (pre-fix files and single-point mutants), not against the build note.
- **P-16:** I graded amendment (7) and the new T-01 intent clause by clause against behaviour.
- **P-17:** I recomputed the unowned changed-file set after the files amendment.
- **O-07 / O-08:** old-file runs and one mutant per branch, with no ever-green row.

## Open questions

- None blocking.
