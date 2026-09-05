# QA gate — BUG-1303-plan-code-review-digest — build diff 63404ef0..b724a0f4

**BLUF: FAIL on the matrix floor (`unit` required, missing).** Nothing else is wrong: the new
guard's discrimination is clean, mutation-proven red-capable, and the suite is green (0 FAIL,
156 lines, `ALL PASSED.`, 19.0s). The `unit` gap is a **recurring structural matrix issue**
(same shape flagged and left open in BUG-1128), not a defect this build introduced.

## 1. Change type and matrix resolution

`plan.yaml`: T-01/T-02/T-03 = `change_type: bugfix` (lines 186, 373, 479); T-04 = `docs` (line
536). `test_matrix.bugfix` (`.harness.json:203-213`): `always: [unit]`, `when:
{kind: __bug_class__, if: match_bug_class}`. `docs.always: []`.

**`match_bug_class` does not fire** — consistent with every prior gate in this repo (repo
Expertise G-08; independently re-confirmed here: no `bug_class` taxonomy entry exists anywhere
in `test_kinds`, and DECISIONS.md:5074 itself calls `__bug_class__` "a predicate placeholder that
exists in no `test_kinds` and can therefore never resolve"). So the `when` leg contributes
nothing; the floor is `unit`, always.

**Diff-warranted addition: `integration`.** `tests/integration/test-validate-digest.py` is itself
part of the diff (`git diff --stat`: +255/-0 there) and matches `test_kinds.integration.detect`
(`tests/integration/**`); `run-unit-tests.sh` (current version, line 28) runs it via a directory
glob `tests/integration/test-*.py` under `--kind integration`. Per P-05 (a test added/changed
alongside the code demonstrates it exercises this change), `integration` is required in addition
to the matrix floor.

| kind | required by | state | evidence |
|---|---|---|---|
| `unit` | `bugfix.always` | **missing** | No file under `tests/unit/` is in the diff (`git diff --name-only` confirmed zero `tests/unit/*` entries). `run-unit-tests.sh --kind unit` only globs `tests/unit/test-*.py` (script line 27) — `test-validate-digest.py` lives in `tests/integration/` and is never a member of that bucket. There is no unit-kind test, old or new, that exercises persona-doc/schema agreement; the entire mechanism is integration-shaped by construction (it reads multiple `.md` files across two trees). This is the **same shape BUG-1128's qa gate flagged** (`notes/qa-c1.md:22-46,200-202`): a bugfix confined to a surface this project's own convention tests only via one non-`unit` kind cannot satisfy `bugfix.always: [unit]`, and that open question (a `_matrix_provenance` carve-out) was never resolved — `_matrix_provenance` (`.harness.json:236-265`) still has no `bugfix` entry. Reporting `missing`, not waving it past, for consistency with that precedent. |
| `integration` | diff-warranted (P-05) | **satisfied** | `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-validate-digest.py`: **exit 0**, **`^FAIL ` count: 0**, final line **`ALL PASSED.`** — matches BRIEF SC-01's `c369fb1f` baseline (exit 0, zero FAIL, `ALL PASSED.`, 18.9s) with no regression, now at 19.0s. |
| `docs` (T-04) | `docs.always: []` | n/a by matrix | T-04 covered by its own inspection `verify:` per plan.yaml; nothing further required |

**`matrix_ok: false`.** The gap is real and floor-level, not a soft-skip candidate (no `excluded`
status, no signed decision covers `bugfix` in `_matrix_provenance`) and not `locally_run`. It is
squarely `missing` per the five-state rubric.

## 2. Suite run (mine, once, as directed)

```
$ cd <worktree> && env -u HARNESS_AGENT_TYPE python3 tests/integration/test-validate-digest.py
exit status: 0
lines matching ^FAIL : 0
final line: ALL PASSED.
```
(wall time ~19.6s in this run vs. plan's recorded 18.9s at baseline — noise, not a regression signal.)

## 3. Guard discrimination audit (REQ-04 / SC-05)

**(a) Sixteen distinct per-persona `ok [documented contract]` lines**, one aggregate line each,
confirmed present and individually named in the raw output:
harness-ai-dev, harness-backend-dev, harness-code-reviewer, harness-data-engineer,
harness-dev-ops, harness-documentor, harness-eng-lead, harness-frontend-dev,
harness-orchestrator, harness-pm, harness-product-lead, harness-qa,
harness-security-reviewer, harness-ui-reviewer, harness-validator-lead,
harness-visual-designer. Exactly 16, no aggregate substitute.

**(b) Both synthetic group lines present, byte-verbatim** against plan.yaml's own text
(grepped, not retyped): `plan.yaml:335` and the suite output agree exactly:
`ok    [documented contract discrimination] omitted field reported, present field accepted`;
`plan.yaml:357` and the suite output agree exactly:
`ok    [documented contract completeness] unmapped persona, absent source, unlocatable block and out-of-block field each reported by name`.

**(c) Roster is derived, never hand-typed.** `tests/integration/test-validate-digest.py:480`:
`roster = sorted(validator.ALIAS)` — the persona set graded is read straight from the validator's
own registry (`validator.ALIAS`), inside `run_documented_contract_cases`. No parallel hand-typed
persona list sits beside `CONTRACT_SOURCES` (`test-validate-digest.py:297-314`, a path map only,
never a roster).

**Red-capability, demonstrated live (not merely inferred from the suite's own green run).**
Wrote a throwaway `/tmp/qa1303_redcheck.py` (deleted after, never touched the worktree), imported
`test-validate-digest.py` via `importlib` and called its pure helpers directly on synthetic bad
input:

```
$ python3 /tmp/qa1303_redcheck.py
CASE_A gaps: ['headline']
CASE_B results: [(False, 'harness-ghost-persona: present in validator registry but has no documented-contract source mapped'), (True, 'harness-qa: fakeqa.md')]
CASE_B ghost FAIL line: harness-ghost-persona: present in validator registry but has no documented-contract source mapped
RED-CHECK PASSED: both synthetic bad inputs correctly reported as failing/gapped
```
Case A: `documented_contract_gaps(("headline","files_touched"), <block missing headline>)` returned
`['headline']` — a genuine gap detected, not vacuously empty. Case B: an unmapped roster persona
(`harness-ghost-persona`, present in roster, absent from the sources map) produced a named `False`
result via `documented_contract_results` — exactly the REQ-04 failure mode, reproduced against
today's real code, not merely read off the suite's pre-built self-test. Confirms the section is
capable of reporting red, on demand, not only observed green.

`git status --porcelain` after cleanup (temp file already deleted, no worktree file touched by this
check):
```
 M .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json
 M .harness/harness/features/BUG-1303-plan-code-review-digest/plan.yaml
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/receipt-harness-dev-ops-simplify-efficiency.md
```
Both modifications and the untracked receipt predate and are unrelated to this segment — I made
no edit to `feature.json` or `plan.yaml`, and no tracked file in the diff under test shows any
modification. These three paths are concurrent sibling-agent activity (per the roster, other
BUG-1303/PlanBug segments are running in parallel against this same tree) outside this note's
scope.

## 4. Test-first audit (from commit record, not narration)

`git log --oneline 63404ef0..b724a0f4`:
```
b724a0f4 Record documented output block as enforced digest contract     (T-04)
8596745f Simplify documented contract checks                            (main-session complexity split)
cdfce3cb Document plan-phase code review digests                       (T-01 + T-02 + T-03, bundled)
```
`git show --stat cdfce3cb`: touches exactly `.claude/agents/harness-code-reviewer.md`,
`.claude/skills/harness-code-review/SKILL.md`, `.omp/agents/harness-code-reviewer.md`,
`tests/integration/test-validate-digest.py` — the full T-01 (guard) **and** T-02 (agent-copy fix)
**and** T-03 (SKILL.md fix) file set, in **one commit**.

plan.yaml's own T-01 intent (lines 204-206, 321-324, 364-368) declares the suite was **expected to
be red** at the end of T-01 alone — harness-code-reviewer missing `code_grade` in both agent trees,
plus the three plan-mode assertions of (6) — closed only once T-02/T-03 land, and instructs the
build agent to "quote the red output in your receipt."

**The commit record does NOT support verifying that ordering.** Because cdfce3cb bundles guard and
both fixes together, there is no commit in this range showing the guard alone, red. The claimed
9-failure red state and its resolution order rest entirely on the build agent's own receipt
narrative — I looked for it, but a receipt is a report, not a git artifact, and nothing on disk
(no intermediate commit, no stashed diff) independently reproduces that red state now. **This part
of test-first compliance is unverifiable from disk, and that is the honest answer** — not a
finding that ordering was violated, just that git alone cannot confirm or refute it. (`8596745f`'s
"Simplify documented contract checks" is a post-hoc refactor of the helpers already added in
cdfce3cb, not a fix closing a red assertion — consistent with the dispatch's own framing.)

## 5. Verdict

```yaml
VERDICT: FAIL
matrix_ok: false
```
The FAIL is the matrix floor (`unit`: missing), a structural/recurring gap this repo has flagged
before and never resolved (BUG-1128), not a code-quality defect in this build. Everything else
audited — guard discrimination, roster derivation, red-capability, suite green, no regression,
tracked tree clean — checks out.

## Open question for the panel/lead

Same as BUG-1128's unresolved item 2: `bugfix.always: [unit]` is structurally unsatisfiable for a
change whose entire test surface is a documentation/contract guard living in
`tests/integration/`. Recommend a `_matrix_provenance` entry (signed decision) either carving
`bugfix` changes confined to `tests/integration/**` + doc/persona files toward `integration`
instead of `unit`, or resolving `__bug_class__`/`match_bug_class` into a real taxonomy that can
route such changes correctly. This is routing/harness-config territory, not something a re-run of
this segment can fix.
