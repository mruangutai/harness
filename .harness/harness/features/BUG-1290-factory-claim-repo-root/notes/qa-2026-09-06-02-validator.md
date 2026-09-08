# QA test-matrix gate — BUG-1290 B-3 fix cycle — 2026-09-06-02-validator

**VERDICT: FAIL.** `matrix_ok: false`. The `bugfix` row's `integration` leg fires
(`fix_confined_to_tests_and_contract_docs = true`) and its DEC-35 presence check finds nothing:
the diff's only test-file change, `tests/unit/test-factory-claim.py`, does not match
`test_kinds.integration.detect` (`tests/integration/**`). Everything else measured — mutation
adequacy, T-01, unit — is clean and, on its own, would have been a PASS.

## 1. Change type & matrix resolution

Diff (`git status --porcelain` / `git diff --stat` against `HEAD=53a5d658`): one test file
(`tests/unit/test-factory-claim.py`, +14/-9) plus `.harness/`-only bookkeeping (`feature.json`
cycle bump, `plan.yaml` two `status:` scalars, two receipts, an answers file, an observations
append). **No production file changed.** Change type: `bugfix` (matches plan `change_type`).

`bugfix` row (`harness.json:203-219`), each `when` resolved against THIS diff, using DEC-217's own
literal definitions:

| predicate | resolution | reason |
|---|---|---|
| `touches_runtime_code` | **false** | every changed file is either under `tests/**` or under `.harness/`; none is production code |
| `fix_confined_to_tests_and_contract_docs` | **true** | the diff's one non-`.harness` change (`test-factory-claim.py`) lives under `tests/**` |
| `match_bug_class` | unresolvable, contributes nothing | no bug-class taxonomy entry fires for any diff yet (repo Expertise G-08), unchanged from cycle 1 |

Floor from `bugfix`: **`integration` only** — `unit` is NOT pulled this cycle (prior cycle's floor
was `unit`+added `integration`; this cycle flips because no production file changed). I additionally
**ran `unit`** as supplementary evidence (the changed fixture physically lives in `tests/unit/**`
and is the file the mutation proof under item 3 depends on) — reported below as extra, not as a
floor addition, per DEC-217's own rationale against ceremonial unit coverage.

## 2. Required kinds — resolved states

| kind | state | cmd | exit | tally (verbatim) |
|---|---|---|---|---|
| `integration` | **missing** (→ FAIL) | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | see below — kind's own `detect` (`tests/integration/**`) matches nothing in the diff |
| `unit` (extra, not required) | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | see below |

**Integration presence, resolved honestly (per dispatch item 2).** DEC-35's presence rule as
stated in the dispatch is "the diff itself contains the test exercising the change." Two readings
diverge here:
- **Mechanical reading (test_kinds.integration.detect):** the diff contains zero files matching
  `tests/integration/**`. By this reading — which is also what DEC-217's own worked example
  (BUG-1303) enforces: it deliberately placed its new guard *inside* `tests/integration/test-
  validate-digest.py`, and DEC-217 explicitly rejects "copying an already mutation-proven
  integration contract guard into `tests/unit/**` solely to satisfy a directory label," implying
  the converse (a test living only in `tests/unit/**`) does not satisfy the label either — presence
  is **missing**.
- **Loose reading:** "the test exercising the change" is unambiguously `test-factory-claim.py`
  (proven by the mutation probe below), and it IS in the diff, so presence is satisfied regardless
  of which `test_kinds` bucket it sits in.

I resolve this as **missing**, because DEC-217's own worked example turns on the mechanical
reading (it took a deliberate placement decision to satisfy exactly this leg) and the general
skill rule ("presence is not satisfied by an unrelated existing test... find the test that
exercises the changed behavior, or the kind is missing") is written against `test_kinds`
detect-glob matching, not a looser "some test somewhere" standard. This is a genuine gap, not
absent effort: the underlying capability has integration coverage from cycle 1
(`tests/integration/test-factory-integration.py`), but that file is untouched by this diff and so
does not exercise *this* specific increment (the issue-map differentiation added to case 5b). I
raise the alternate reading as an open question below rather than silently picking it, because the
mutation evidence (item 3) is unusually strong and an operator may reasonably choose to waive the
directory-label mismatch for this specific increment — that is not mine to decide.

Command output (verbatim tallies):

```
$ env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration
... (46 files: test-factory-decompose.py, test-feature-worktree.py, test-factory-integration.py,
    test-layout-migration.py, test-check-state.py, test-gh-sync.py, test-check-domain.py, ...)
pool: 8 workers, 46 files, 62.75s wall
slowest: test-check-state.py 60.61s, test-gh-sync.py 43.30s, test-check-domain.py 39.67s
EXIT=0
```
`grep -c '^FAIL '` on that output = 0. None of the 46 files is a member of this diff.

```
$ env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit
----- test-factory-claim.py (exit 0, 0.13s) -----
PASS test-factory-claim.py
----- test-factory-claim-mutation.py (exit 0, 0.21s) -----
BASELINE 3/3 ok
MUTANT ACTIVE
FAIL  BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
FAIL  BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
MUTATION PROOF: 3/3 cases reddened
PASS test-factory-claim-mutation.py
pool: 8 workers, 28 files, 2.27s wall
EXIT=0
```
The three `FAIL` lines are `test-factory-claim-mutation.py`'s own expected reddening under its
active mutant (`MUTANT ACTIVE` precedes them, `MUTATION PROOF: 3/3 cases reddened` confirms them as
the proof's own output) — not real failures; `grep -c '^FAIL '` on the whole `--kind unit` run = 3,
all three inside this one block.

Also ran the specific changed file directly: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py`
→ exit 0, `124/124 checks passed.`, all six `BUG-1290 5a..5f` lines `ok`.

`component`/`ui`/`typecheck` — not in the `bugfix` floor and diff touches no such surface: not
applicable. `functional`/`eval` — `status: excluded`, signed DEC-187: not applicable.
`omp_session_accessor`/`handoff_comprehension` — `locally_run`, diff touches neither
`inflight_registry.py` session resolution nor the handoff contract: not applicable.

## 3. Mutation adequacy for REQ-02's issue-map clause — independently re-measured

Own probe (`/tmp/bug1290-qa-scratch/qa_probe.py`, never written into the repo), re-keying ONE of
`_BlockerCache`'s two caches on `feature` alone at a time, patching the real
`.agents/skills/harness/bin/factory_claim.py` (asserted `claim.__file__ ==
<bin_dir>/factory_claim.py`; method bodies copied verbatim from the real `_plan`/`issue_number`
signatures at lines 98–111 / 132–149, only the cache key line changed), run against both the
post-edit fixture (`tests/unit/test-factory-claim.py`, working tree) and the pre-edit fixture
(`git show HEAD:tests/unit/test-factory-claim.py`, materialized at
`/tmp/bug1290-qa-scratch/test-factory-claim-HEAD.py`):

```
MUTANT=none   fixture=test-factory-claim.py      cases={5a:ok,5b:ok,5c:ok,5d:ok,5e:ok,5f:ok}   total_FAIL=0
MUTANT=none   fixture=test-factory-claim-HEAD.py cases={5a:ok,5b:ok,5c:ok,5d:ok,5e:ok,5f:FAIL} total_FAIL=1
MUTANT=plans  fixture=test-factory-claim.py      cases={5a:ok,5b:FAIL,5c:ok,5d:ok,5e:ok,5f:ok}  total_FAIL=1
MUTANT=plans  fixture=test-factory-claim-HEAD.py cases={5a:ok,5b:FAIL,5c:ok,5d:ok,5e:ok,5f:FAIL} total_FAIL=2
MUTANT=issues fixture=test-factory-claim.py      cases={5a:ok,5b:FAIL,5c:ok,5d:ok,5e:ok,5f:ok}  total_FAIL=1
MUTANT=issues fixture=test-factory-claim-HEAD.py cases={5a:ok,5b:ok,5c:ok,5d:ok,5e:ok,5f:ok}    total_FAIL=1(5f only)
```

The `5f` FAIL against the HEAD fixture is a probe-fidelity artifact, not a mutation signal: `5f`
opens source files via a path anchored on `__file__`, and the HEAD copy runs from `/tmp`, so its
own anchor resolves to a nonexistent directory and the case's `try/except` reports `False`. This
happens identically under `MUTANT=none` (no patch applied at all), proving it is unrelated to
either mutant.

Reading only 5a/5b/5c (the discriminating cases, unaffected by the artifact): the **`issues`
mutant is caught by 5b under the post-edit fixture (`FAIL`) but NOT caught under the pre-edit
fixture (`ok`)** — direct, independently-measured confirmation that this diff closes a real
mutation-coverage gap in the issue-map cache (the pre-edit fixture's empty `factory.issues: {}`
maps made cross-repository key confusion invisible: `{}.get(x)` is `None` regardless of key). The
`plans` mutant is caught by both fixtures (`FAIL` on 5b in both rows) — no regression on that half.
This **matches** the eng digest's claim; I did not transcribe it, I reran it myself and it landed
on the same conclusion.

## 4. Test-first compliance — the applicable form

Naive form (production commit after test commit) does not apply: this cycle adds **no production
code**; the behaviour the fixture proves was landed by T-03 in an earlier cycle. Applicable form:
was the fixture demonstrated RED under its target mutant, and NOT-red before the edit that added
it? Answer, from item 3 directly: **yes** — the `issues` mutant reddens case 5b under the current
(post-edit) fixture and does not redden it under the pre-edit fixture, which is exactly "RED under
the target mutant, GREEN (non-discriminating) before the edit." This is a **reasoned** finding from
my own mutation measurement, not a git-history reconstruction (there is no new production commit to
order against). Holds; no violation to report.

## 5. T-01's `verify:` — unmoved this cycle

Ran the exact string from `plan.yaml:274-281` (cross-checked verbatim — matches), on this tree and
on a disposable detached worktree at `HEAD` (`git worktree add --detach
/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-bug1290-b3-head HEAD`, since `git stash`
is unavailable and the write-guard requires an absolute destination under the top-level
`.claude/worktrees/`, not the nested one):

```
# this tree (post-edit):
MISSING RED: 5a / 5b / 5c / 5d / 5e / 5f
exit=1

# HEAD copy (pre-edit), same command, cd substituted for the detached worktree:
MISSING RED: 5a / 5b / 5c / 5d / 5e / 5f
exit=1
```

Both exit 1 with all six cases `MISSING RED` — because T-03 (an earlier cycle) already landed the
seam, so every `5x` case reports `ok`, never `FAIL`, at both refs. **This cycle did not move T-01's
`verify:` state** (1→1, unchanged). Per dispatch instruction, not gated as a failure.

## 6. Verdict

`matrix_ok: false`. `unit`: satisfied (extra, not required). `integration`: **missing** — required
by the `bugfix` row's `fix_confined_to_tests_and_contract_docs` leg, and no file in the diff
matches `test_kinds.integration.detect`. **VERDICT: FAIL.**

**What's needed to clear the gate:** either (a) relocate or duplicate the discriminating assertion
(case 5b's issue-map differentiation) into a file under `tests/integration/**` so the diff itself
satisfies the leg's detect surface — DEC-217's own worked example (BUG-1303) took exactly this
route — or (b) an operator-signed waiver reading DEC-35's presence rule loosely enough that a
`tests/unit/**`-resident test with proven mutation adequacy satisfies an `integration`-labeled leg.
I did not pick (b) silently; see the open question.

## Matrix gaps

`integration` — missing, as above. Nothing else.
