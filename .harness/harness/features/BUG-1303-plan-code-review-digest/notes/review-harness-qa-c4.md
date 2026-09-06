# QA gate — BUG-1303 review-c4 (pinned 59c5de97)

Files read: nine-path non-artifact set in full (both agent copies, both SKILL.md, both harness.json
copies, DECISIONS.md/-INDEX.md, both test files) plus BRIEF.md, plan.yaml (all 4 tasks + panel),
DEC-216/217 at DECISIONS.md:6792/6818, DEC-212 at :6620.

## VERDICT: FAIL — a real regression surfaced on independent full-suite re-run

The two named files (`tests/integration/test-validate-digest.py`, `tests/unit/test-config-shape-matrix.py`)
both pass standalone, and every assertion they add is red-capable (below). But `.harness/harness/docs/DECISIONS-INDEX.md`
is part of my reviewed nine-path surface, and `run-unit-tests.sh --kind integration` — the standing
command the `integration` kind actually runs — fails on a **different** integration script,
`tests/integration/test-gen-decisions-index.py`, over exactly that file. See "FAIL — SC-06 /
DECISIONS-INDEX.md regeneration idempotence" below.

## Q-D — change_type resolution and DEC-217 predicates

**Resolution method:** read `plan.yaml` tasks directly (never inferred). T-01/T-02/T-03 declare
`change_type: bugfix`; T-04 declares `change_type: docs` (`docs.always: []`, contributes nothing).
Floor = bugfix's `when` legs, evaluated per DEC-217's literal text over **the whole diff's
non-`.harness/` surface** (per this dispatch's instruction to use the nine-path set, not a per-task
subset) — `.harness/harness.json`, `.harness/harness/docs/DECISIONS.md`, `DECISIONS-INDEX.md` are
under `.harness/` and excluded from the predicate by its own text.

Non-`.harness` files: `.claude/agents/harness-code-reviewer.md` (*.md), `.omp/agents/harness-code-reviewer.md`
(*.md), `.claude/skills/harness-code-review/SKILL.md` (*.md), `tests/integration/test-validate-digest.py`
(tests/**), `tests/unit/test-config-shape-matrix.py` (tests/**), **`.claude/skills/harness/templates/harness.json`**
— not *.md, not tests/**, not `.harness/`.

- **`touches_runtime_code`** ("modifies at least one file that is not under `tests/**`, is not a `*.md`
  documentation or contract file, and is not under `.harness/`"): **TRUE**, solely because of
  `.claude/skills/harness/templates/harness.json` (diff at `git diff 63404ef..59c5de97 -- .claude/skills/harness/templates/harness.json`:
  `bugfix.always: ["unit"]` → `[]` plus a new `when` list). → requires **unit**.
- **`fix_confined_to_tests_and_contract_docs`** ("every non-`.harness` change is either a `*.md`
  documentation or contract file or lives under `tests/**`"): **FALSE** — same file breaks it.
- **`match_bug_class`**: no bug-class taxonomy entry fires for any diff today (confirmed via
  `__bug_class__`'s standing placeholder status; repo Expertise G-08 already records this) — not
  applicable, unchanged by this feature.

**Required kind: `unit`.** State: **satisfied** — `tests/unit/test-config-shape-matrix.py` is new in
the diff and directly asserts the changed lines (`case_project_config_routes_bugfix_kinds_by_surface`,
`case_template_config_routes_bugfix_kinds_by_surface`). Ran it myself, `env -u HARNESS_AGENT_TYPE
python3 tests/unit/test-config-shape-matrix.py`: exit 0, `19/19 cases passed`, 0.25s — matches the
orchestrator's reported number, and also confirmed via the standing `run-unit-tests.sh --kind unit`
(exit 0, 27 files, no `^FAIL` line).

Also ran `tests/integration/test-validate-digest.py` myself: `env -u HARNESS_AGENT_TYPE python3
tests/integration/test-validate-digest.py`: exit 0, 0 lines matching `^FAIL `, `ALL PASSED.`, 19.60s —
consistent with SC-01's cited baseline shape and the orchestrator's number. **But** the standing
`integration`-kind command is `run-unit-tests.sh --kind integration`, which runs the whole
`tests/integration/**` bucket, not just this one file — and that command is red (below).

### Open question — untraced config-shape edit (not itself the FAIL, but related)

`.harness/harness.json`, `.claude/skills/harness/templates/harness.json`, `DECISIONS.md`'s DEC-217
entry, and `tests/unit/test-config-shape-matrix.py` all land in one commit (`e014ede3 "Route bugfix
test kinds by changed surface"`) that **is not in any T-01..T-04 `files:` list** — it is the mechanism
that installs DEC-217 itself, bundled into this diff by the merge-base/review_sha window rather than
by any task. Two consequences: (1) my evaluation above had to apply `touches_runtime_code` at the
*feature* level rather than per-task, because there is no task to scope it to — under a strict
per-task reading, T-01/T-02/T-03 are each purely `tests/**`-or-`*.md`, which would flip the floor to
`integration` instead of `unit` (already satisfied either way, so no practical gap on this axis, but
the two readings disagree on *which* kind is the named requirement); (2) the edit itself changes
`test_matrix.bugfix`'s container shape (`always: ["unit"]` → `always: [], when: [...]`) — squarely
DEC-212's own example of a "structural nesting" change — yet no task declares `change_type: config`,
so DEC-212's `touches_config_shape → integration` leg never fires via plan.yaml's mechanical routing
for this specific edit; only a `unit`-kind test (`test-config-shape-matrix.py`) covers it. This same
untraced commit is also the origin of the FAIL below: nobody re-ran `gen-decisions-index.py` after
its final edit to `DECISIONS.md`'s DEC-217 body, so the checked-in index row went stale. That is
concrete evidence an untraced commit skipping the mechanical routing carries real risk, not just a
traceability nicety.

## FAIL — SC-06 / DECISIONS-INDEX.md regeneration idempotence

SC-06 requires: "re-running `.agents/skills/harness/bin/gen-decisions-index.py --stdout` leaves the
index byte-identical." Ran it myself:

```
env -u HARNESS_AGENT_TYPE python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout \
  | diff -u .harness/harness/docs/DECISIONS-INDEX.md -
```

Result — **not** byte-identical, exactly one row differs:

```
- DEC-217 @6818 [tests,qa,state] refs: DEC-35 DEC-212 DEC-213 :: Bugfix test kinds follow the changed surface: ...
+ DEC-217 @6818 [tests,docs,digest,plan] refs: DEC-35 DEC-212 DEC-213 :: Bugfix test kinds follow the changed surface: ...
```

Confirmed by the standing gate too: `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh
--kind integration` exits 1, with `FAIL - test_committed_index_matches_a_fresh_regeneration:
.harness/harness/docs/DECISIONS-INDEX.md is not what the generator produces` in
`tests/integration/test-gen-decisions-index.py`. This is a named test, a real assertion diff (full-row
text mismatch), not a load/import/collection error — a genuine `FAIL`, not `BLOCKED`.

`compute_tags()` in `gen-decisions-index.py` derives a decision's index tags purely, deterministically
from its body text via keyword vocabulary. The committed row's tags (`tests,qa,state`) do not match
what the generator computes from DEC-217's *current* body (`tests,docs,digest,plan`) — meaning
whoever wrote the DECISIONS-INDEX.md row for DEC-217 either hand-typed it or ran the generator against
an earlier revision of the DEC-217 body and never re-ran it after the body's final edit. This traces
to the untraced `e014ede3` commit above, not to T-04 (T-04 authors DEC-216, not DEC-217).

**Concrete failure scenario:** any reader trusting `DECISIONS-INDEX.md`'s tag column for DEC-217 (e.g.
searching the index by tag for "which decisions touch `qa`/`state`") gets a stale, non-reproducible
answer, and the standing idempotence gate — the exact mechanism SC-06 and T-04's own `verify:` line
rely on to catch this class of drift — is currently red because of it. Severity: **high** — it is a
signed, `verify: automated`-adjacent (inspection-graded but mechanically checkable) success criterion
that is measurably unmet, and it fails the standing `integration`-kind command for the whole repo, not
just this feature's own narrow scope.

**Fix:** regenerate the index (`gen-decisions-index.py --apply` or equivalent) and land the corrected
row; re-run `run-unit-tests.sh --kind integration` to confirm green.

## Q-C — red-capability, `tests/unit/test-config-shape-matrix.py` (all 19 assertions, all new)

Method: disposable worktree `git worktree add .claude/worktrees/qa-c4-perturb-1303 59c5de97` (DEC-153;
avoided perturbing the shared review worktree, which three sibling reviewers are using concurrently).
Every perturbation below was applied, run, confirmed red, then `git checkout --` restored and
`git status --porcelain` confirmed clean before the next. Worktree removed cleanly at the end
(`git worktree remove`, no `--force`, empty diff beforehand).

| # | Assertion | Method | Result |
|---|---|---|---|
|1| project `config.when` requires integration on `touches_config_shape` | (a) flip `kind` to `unit` | FAIL confirmed |
|2| project `_matrix_provenance.config` exists | (a) delete key | FAIL confirmed |
|3| project provenance `.config.added == ["integration"]` | (a) mutate value | FAIL confirmed |
|4| project provenance `.config.signed == "DEC-212"` | (a) mutate value | FAIL confirmed |
|5| project `bugfix.always == []` | (a) set to `["unit"]` | FAIL confirmed |
|6| project `bugfix.when == expected` | (a) reorder two legs | FAIL confirmed |
|7| project `_matrix_provenance.bugfix` exists | (a) delete key | FAIL confirmed |
|8| project provenance `.bugfix.removed/.added` | (a) blank `removed` | FAIL confirmed |
|9| project provenance `.bugfix.signed == "DEC-217"` | (a) mutate value | FAIL confirmed |
|10| template `bugfix.always == []` | (a) set to `["unit"]` | FAIL confirmed |
|11| template `config.when` requires integration | (a) flip `kind` | FAIL confirmed |
|12| template `bugfix.when == expected` | (a) reorder two legs | FAIL confirmed |
|13| `DECISIONS.md` declares `## DEC-212` | (a) rename heading | FAIL confirmed |
|14| DEC-212 heading names config-shape purpose | (a) replace heading tail | FAIL confirmed |
|15| `DECISIONS.md` declares `## DEC-217` | (a) rename heading | FAIL confirmed |
|16| DEC-217 defines both bugfix predicates | (a) garble both predicate names in body | FAIL confirmed |
|17| `harness-qa-gate/SKILL.md` mentions `touches_config_shape` | (a) replace token | FAIL confirmed |
|18| `harness-qa-gate/SKILL.md` cites DEC-212 | (a) replace token | FAIL confirmed |
|19| `harness-verification-rules/SKILL.md` mentions `touches_config_shape` | (a) replace token | FAIL confirmed |

All 19/19 are directly red-capable by perturbation; none required (b). **Adequacy:** this file is
entirely orthogonal to BUG-1303's REQ-01..REQ-05 — it guards DEC-212/DEC-217 config-shape routing,
not the code-reviewer digest contract. It binds real behaviour (JSON structural equality, heading
presence, prose-token presence) rather than spelling only, but it answers none of BUG-1303's own
success criteria; it is in-diff because of the untraced `e014ede3` commit noted above, not because
any BUG-1303 task added it. Notably, none of these 19 assertions caught the DECISIONS-INDEX.md tag
staleness above — the file tests DEC-212/217's *DECISIONS.md* body and *harness.json* shape, never
`DECISIONS-INDEX.md`'s row-fidelity; that is `test-gen-decisions-index.py`'s job, correctly.

## Q-C — red-capability, `tests/integration/test-validate-digest.py` new section (independent of the code-reviewer's Q-C; not read before writing this)

26 real-file assertion lines + 2 synthetic group assertions, all new (`run_documented_contract_cases`
and its helpers, lines ~242-608 of the diff). Same disposable-worktree method.

**Per-persona documented-contract lines (16, `documented_contract_results` over the real registry):**
perturbed 3 representative branches, argue (b) for the rest by code identity (one function,
`documented_contract_gaps`, applied uniformly; only the file path and required-field set vary):
- (a) `.omp/agents/harness-qa.md`: renamed `suite:` → `XXX_suite:` in the fenced block → `FAIL ... missing fields: suite`, 1 FAILING. Restored.
- (a) `.omp/agents/harness-code-reviewer.md`: renamed `code_grade:` line → `FAIL ... missing fields: code_grade`, 2 FAILING (collateral hit on a plan-mode check below, expected). Restored.
- (a) `.claude/skills/harness-digest-dev/SKILL.md` (shared by 4 personas): renamed `tests_added:` →
  all 4 of `harness-ai-dev/-backend-dev/-data-engineer/-frontend-dev` reddened by name, 4 FAILING.
  Confirms both per-persona scoping AND the multi-owner-file case SC-05/D-04 exist to guard. Restored.
- (b) the other 12 lines (`harness-dev-ops`, `-documentor`, `-visual-designer`, `-security-reviewer`,
  `-ui-reviewer`, `-orchestrator`, `-pm`, and the 3 `harness-team/SKILL.md` leads) call the identical
  `documented_contract_gaps`/`documented_block` pair against a real on-disk file exactly as the three
  proven cases do; reachability is the same code path, only the path string and field set differ.

**Reviewer plan-mode token lines (8, `_reviewer_plan_mode_results`):** perturbed 2, (b) for the rest:
- (a) `.claude/skills/harness-code-review/SKILL.md`: `reviewed: plan:` → `reviewedX: plan:` → that one
  line reddened, the sibling `code_grade: ... n_a` line on the same file stayed green (proves the two
  checks are independent, not one covering the other). Restored.
- (a) `.claude/agents/harness-code-reviewer.md`: mangled the `features/<FEAT>/notes/...` fragment →
  only that line reddened, the file's other two lines stayed green. Restored.
- (b) the remaining 6 (the `.omp` copy's three checks, the `.claude` copy's `code_grade`/`reviewed`
  checks, `SKILL.md`'s `code_grade` check) are the identical substring/regex test against the same
  three files; reachability follows from the two proven cases.

**Group-level synthetic assertions (2, `_discrimination_ok` / `_completeness_ok`):** these run the
real `documented_contract_gaps`/`documented_block`/`documented_contract_results` against hardcoded
fixture strings, so I mutation-probed the guarded function itself rather than a fixture: replaced
`documented_contract_gaps`'s body with `return []` (a detector that reports no gaps ever) in the test
file, reran. Result: every real-file per-persona and plan-mode line stayed green (because the real
repo's documented blocks are in fact conformant, so a broken all-pass detector is indistinguishable
from a working one *on real data*) but **both** synthetic checks reddened by name — `[documented
contract discrimination]` and `[documented contract completeness]`, 2 FAILING — because their fixtures
are deliberately non-conformant. This is exactly SC-02/SC-05's own claim ("both are named cases in
the suite output, so neither can be ever-green") and it holds. Restored (`git checkout --`, verified
clean).

**Adequacy — SC-03 finding (medium, concrete):** SC-03 requires the plan-mode values be "derived from
the validator's own constants (`_PLAN_REVIEW_PREFIX`, `CODE_GRADE_VALUES`), not from a string retyped
into the test." The `reviewed:` half complies —
`reviewed_token = "reviewed: " + validator._PLAN_REVIEW_PREFIX` (test-validate-digest.py, in
`_reviewer_plan_mode_results`). The `code_grade` half does not:
`code_grade_line = re.compile(r"^\s*code_grade\s*:.*\bn_a\b", re.MULTILINE)` hardcodes the literal
string `"n_a"` rather than referencing `validator.CODE_GRADE_VALUES` (`{"pass", "fail", "grade_2",
"n_a"}` at `validate-digest.py:616`) at all. **Concrete failure scenario:** if `CODE_GRADE_VALUES`'s
`n_a` member is ever renamed (a real, foreseeable edit — the set already carries a v2-flavored
`grade_2`), this regex keeps matching the old spelling in the persona files even after the real
validator has stopped accepting it: the test stays green on stale, invalid persona text while
`validate-digest.py` would reject a real plan-phase digest carrying it. This is exactly the drift
class SC-03 exists to close for the `reviewed:` half but was not closed here for `code_grade`. It does
not fail today (both sides currently agree on `n_a`), so it is not a blocking `FAIL` on its own, but
it is a named SC-03 non-compliance a fix-cycle should close cheaply (reference
`validator.CODE_GRADE_VALUES` in the regex or assert membership instead of the literal).

## DIGEST

```yaml
VERDICT: FAIL
DIGEST:
  headline: The two named files each pass standalone and every assertion they add is red-capable, but the standing `run-unit-tests.sh --kind integration` command is red — `tests/integration/test-gen-decisions-index.py` fails because `.harness/harness/docs/DECISIONS-INDEX.md`'s DEC-217 row tags are stale relative to a fresh regeneration, breaking SC-06. Additionally: one SC-03 compliance gap (code_grade half of the reviewer plan-mode check hardcodes "n_a" instead of referencing validator.CODE_GRADE_VALUES) and one routing open question about the untraced config-shape commit that is also the origin of the FAIL.
  suite: fail
  failures: 1
  matrix_ok: true
  coverage_gaps: []
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 19 }
    - { kind: integration, state: missing, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 26 }
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-validate-digest.py::main (ALL PASSED, exit 0, 19.60s) — passes standalone, but the file lives inside a kind bucket that fails overall" }
    - { id: SC-02, test: "tests/integration/test-validate-digest.py::run_documented_contract_cases::_discrimination_ok" }
    - { id: SC-03, test: "tests/integration/test-validate-digest.py::_reviewer_plan_mode_results — reviewed: half compliant, code_grade half hardcodes n_a rather than validator.CODE_GRADE_VALUES (medium finding, not blocking on its own)" }
    - { id: SC-05, test: "tests/integration/test-validate-digest.py::run_documented_contract_cases::_completeness_ok" }
    - { id: SC-06, test: "tests/integration/test-gen-decisions-index.py::test_committed_index_matches_a_fresh_regeneration — FAILS: DEC-217 row tags [tests,qa,state] committed vs [tests,docs,digest,plan] regenerated" }
  must_fix:
    - "Regenerate .harness/harness/docs/DECISIONS-INDEX.md (gen-decisions-index.py --apply) so DEC-217's row matches a fresh run; re-confirm `run-unit-tests.sh --kind integration` exits 0 (severity: high)."
  open_questions:
    - { id: Q1, question: "e014ede3 (harness.json/templates/harness.json bugfix+config predicate edit, DEC-217's own DECISIONS.md entry, test-config-shape-matrix.py, and the now-stale DECISIONS-INDEX.md row) is untraced to any BUG-1303 task. Should it be attributed to a task, or is bundling infrastructure commits into a feature's reviewed diff via the merge-base/review_sha window intentional and out of scope for this feature's own gate?", blocking: false }
    - { id: Q2, question: "Should the SC-03 code_grade hardcode (n_a literal instead of validator.CODE_GRADE_VALUES reference) be fixed as part of this cycle, given SC-03 is a signed, verify:automated criterion whose letter is unmet for that half?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-qa-c4.md
```
