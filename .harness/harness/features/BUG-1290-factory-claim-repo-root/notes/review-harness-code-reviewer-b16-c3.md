BLUF: **PASS.** `5g` is a defensible functional equivalent of the operator's literal wording, not
a literal delivery of it — case `5b` itself never runs under the mutant, a new case does — but the
underlying purpose (a deleted fixture dependency cannot silently return the suite to the pre-B-3
blind state) is provably covered by the measured 5b/5g pair. One real fail-open in the new
predicate's negation is worth a non-gating backlog row; nothing here rises to `must_fix`.
Reviewed at `c488218e`; production byte-identical to the passed `7104aa43` pin, out of scope here.
`code_grade: grade_2` — two pre-existing, previously-reasoned test-harness functions, unmoved by
this cycle's own delta (see addendum).

## 1. Spec compliance — substitution, but a faithful one

The directive (`notes/answers-2026-09-06-b16.md`) says the test "must fail case `5b`" under the
mutation. As committed, `name_5b`'s own check (`test-factory-claim.py:1231`) never runs against the
mutated cache — it only ever calls `_run_5b_scenario()` against the real `_BlockerCache`. The
mutation is exercised exclusively inside a **new**, separate case `5g` (`:1301-1323`), which reruns
the shared scenario under `_FeatureOnlyIssueMapCache` and asserts the negation of 5b's property.

I judge this a **substitution, not literal compliance** — but a defensible one, not a dodge:
mutating global `claim._BlockerCache` state inside the same check that also asserts 5b's positive,
un-mutated baseline would either require nested patch/restore inside `name_5b` itself (duplicating
5g's try/finally) or risk leaking the mutant into 5c-5f, which run after 5b in this monolithic,
order-dependent file. Isolating the mutation to its own case is the safer design.

More importantly, the operator's *underlying* concern — a deleted fixture dependency going
undetected — is verifiably met: the three independently-measured arms show intact→125/125,
`depends_on` removed→**5g** reddens, issue-map emptied→**5b** reddens. Every one of the two named
regression shapes trips at least one case. I do not gate on the literal-wording gap; I record it as
the honest answer to "which of the three did you deliver," per the dispatch's own framing.

## 2. Honest limits of the negation — no concrete single-edit break found

I tried to construct a single edit that leaves **both** 5b and 5g green while the repo-key defense
is actually gone: collapsing the fixture to one repo, aliasing both repos' dependency ids, and
defanging `_FeatureOnlyIssueMapCache.issue_number` into a no-op override. In every case tried, at
least one of 5b/5g reddens (a no-op mutant override makes 5g fail precisely because it stops
discriminating, which is correct behavior). **No concrete break named → not gating**, per the
dispatch's own bar ("only a concrete one gates").

## 3. Quality of new code — one real fail-open in the negation, not currently live

`_5b_property_holds` (`:1208-1223`) returns `False` on `code != 0` or a JSON-decode/type failure,
documented as intentional ("Total... so it never raises"). Traced against `factory_cli.run`
(`factory_cli.py:72-93`): **any** uncaught exception inside `claim._main` — including one totally
unrelated to the cache-key collapse (e.g. a future typo in `_FeatureOnlyIssueMapCache` that raises
`TypeError`/`KeyError`) — is trapped and converted to a non-zero exit. That non-zero code alone
satisfies `not _5b_property_holds(...)`, so **5g would pass even if the mutant subclass is broken
for a reason that has nothing to do with the documented cache-collapse behavior.** This is a real
gap between what 5g's assertion *binds* (did the run produce anything other than 5b's exact happy
path) and what its docstring narrates (the specific repo→feature collapse). It is not live today —
the delivered mutant is correctly implemented and the three measured arms confirm it discriminates
for the right reason — but it is a structural ceiling on 5g's future discriminating power. **Non-gating, `bug`, backlog**: tighten 5g to require `code == 0` plus a specific wrong-payload shape
(e.g. `payload.get("issue") != 952` or `"951" not in err`) rather than accepting any non-happy-path
exit as proof.

The shared builder, `setdefault` canonicalization, and `try/finally` restore of `claim._BlockerCache`
are each sound: the restore is inside the same `try/finally` that wraps `_run_5b_scenario()`, so an
exception during the mutated run still restores the real class before `5g`'s outer `except`
records a failure — no state leak to any later case (5g is last before the summary print). Both
NEW functions individually grade PASS at 4 against the test-code bar of 3
(`_run_5b_scenario` cyclomatic 1/cognitive 0/abc 11.4; `_5b_property_holds` cyclomatic 6/cognitive
3/abc 10.2) — see code-grade addendum below for why the digest's binding `code_grade` field is
`grade_2`, not `pass`.

## 4. Record honesty — agree, non-gating

Simplify's finding (`runs/2026-09-06-10-eng/digest.md`): `_5b_property_holds`'s docstring claims
totality ("never raises"), but a `json.loads(out)` returning a non-dict JSON value would reach
`.get()` and raise `AttributeError`, uncaught by the `(JSONDecodeError, TypeError)` tuple. **I
agree this is non-gating.** Confirmed independently: `factory_claim.py`'s only stdout write on
success is `factory_cli.payload({...})` (`:217-221`) with a hard-coded dict literal; every other
stdout-adjacent branch is empty stdout via a non-zero exit. There is no code path in this file that
can produce non-dict JSON on stdout, so the docstring's imprecision names an unreachable shape, not
a live hazard. Backlog `chore`.

## 5. Coupling cost — intended for the named threat, an accepted SPOF for a different one

Sharing `_run_5b_scenario`/`_5b_property_holds` between 5b and 5g is the **stated, intended**
defense against fixture drift (comment at `:1183-1186`): editing the fixture moves both cases, so
neither can be "fixed" by narrowing without the other noticing. It is simultaneously an
**undetected single point of failure against a different threat**: nothing here tests the
predicate itself, so an edit that loosens `_5b_property_holds` (e.g. dropping the `"951" in err`
conjunct) is accepted identically by both 5b and 5g — both would go green on a materially weaker
property, and nothing in this file would notice. This is the ordinary "who tests the test helper"
gap common to any shared assertion, not something new to this design; I record it as a known,
accepted risk rather than a defect, since detecting it would need a distinct, independent check on
the predicate itself which is out of scope for this cycle.

## Code-grade addendum — canonical range, not the single-commit diff

`validate-digest.py` binds `code_grade` to `merge-base(origin/main, review_sha)..review_sha`
(`6e95435a..c488218e`), not this cycle's single-commit delta. Re-ran `code-grade.py` over that
canonical range: 15 records, 13 PASS, 2 grade-2 FAILs → `code_grade: grade_2`.

- `tests/unit/test-factory-claim.py:324 build_features_root` — ABC 33.5 (bar 3), cyclomatic 1,
  cognitive 0. **Reason:** pure sequential fixture assembly (four segments' `write_yaml`/`write_json`
  calls, no branches, no loops); ABC is high because each fixture write is its own call/assignment,
  not because the function is hard to follow. **Pre-existing, unaffected by this cycle**: confirmed
  via `code-grade.py --base 7104aa43 --head c488218e` — zero records (this cycle's own delta touches
  only lines 1181-1325, nowhere near 324-386). Already reasoned and accepted at
  `review-harness-code-reviewer-b3-c2.md` (CG-1). Accepted again here.
- `tests/unit/test-factory-claim.py:403 run_main` — ABC 26.7 (bar 3), cyclomatic 6, cognitive 9.
  **Reason:** the single shared test-harness driver every case in the file calls through (patches
  `gh`, builds argv, captures stdout/stderr, restores four monkeypatched globals in `finally`) —
  legitimately touches many collaborators once, in one place. **Pre-existing, unaffected by this
  cycle** (same zero-delta confirmation as above). Already reasoned and accepted at
  `review-harness-code-reviewer-b3-c2.md` (CG-2). Accepted again here.

Both are carried-forward, reasoned grade-2 debt, not new or worsened by `5g`. Does not change
`severity_max` (`med`) or `must_fix` (`[]`).

## Backlog (non-gating)

- `bug` — 5g's negation accepts any non-happy-path exit as "mutant detected," not only the
  documented cache-collapse shape (§3).
- `chore` — `_5b_property_holds` docstring's "never raises" claim is imprecise for an unreachable
  non-dict-JSON shape (§4, already raised by simplify, agreed here).

```yaml
VERDICT: PASS
DIGEST:
  headline: 5g is a faithful functional substitute for the literal "fail case 5b" wording; the pair covers both named regression shapes and no must_fix found
  severity_max: med
  findings: 4
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - "tests/unit/test-factory-claim.py:324 build_features_root — ABC 33.5/bar 3, cyclomatic 1, cognitive 0: pure sequential fixture assembly (four segments' write_yaml/write_json calls, no branches, no loops); ABC is high only because each fixture write is its own call/assignment. Pre-existing, unmoved by this cycle's delta (code-grade.py --base 7104aa43 --head c488218e: zero records); already reasoned and accepted at review-harness-code-reviewer-b3-c2.md (CG-1)."
    - "tests/unit/test-factory-claim.py:403 run_main — ABC 26.7/bar 3, cyclomatic 6, cognitive 9: the single shared test-harness driver every case in the file calls through (patches gh, builds argv, captures stdout/stderr, restores four monkeypatched globals in finally), legitimately touching many collaborators once in one place. Pre-existing, unmoved by this cycle's delta (same zero-record confirmation); already reasoned and accepted at review-harness-code-reviewer-b3-c2.md (CG-2)."
  reviewed: "05127422..c488218eb448be1a6cffda103fcdd7275a366069"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root/.harness/harness/features/BUG-1290-factory-claim-repo-root/notes/review-harness-code-reviewer-b16-c3.md
```
