# QA re-gate — FEAT-43 code risk grading, validate-regate-c21

```yaml
VERDICT: PASS
DIGEST:
  headline: "SEC-01 closes as a CLASS under discriminating live probes — the exact c18 forged digest (review_sha..review_sha, code_grade: n_a) and its ~1 and honest-base variants ALL now reject with the identical range-independent error at exit 1, while a fail-graded digest over the same no-op range still validates at exit 0; all four fail-closed derived-range branches (unresolvable default branch, unresolvable merge base, degenerate ancestor range, legitimate no-.py accept) reproduced live myself against fresh /tmp repos, with pass/fail/grade_2 confirmed still ungated under both refusal conditions; unit 29/29 and integration 28/28 hold at baseline; CR-01/CR-02/UI-01 all reconfirmed unregressed; two independent live mutations against the derived-range mechanism each fail exactly one named case and restore byte-identically"
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 29 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 28 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-14, test: "test-code-grade-cli.py:test_bars_follow_test_kinds (unchanged since c18, re-confirmed by suite exit 0)" }
    - { id: SC-17, test: "test-code-grade-cli.py:test_bars_follow_test_kinds (unchanged since c18, re-confirmed by suite exit 0)" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-regate-c21.md
severity_max: none
adequacy_notes: "None of the six required items were undeterminable. One item was left explicitly out of my scope by design: the c19 receipt's Q1 (whether the 'no merge base' branch needed a fourth hermetic test) was raised AND resolved by the squad's own send-back 2 (check_no_merge_base) before this run started; I independently reproduced that branch's correct behavior live (item 3b) rather than re-litigating whether the test was needed."
```

## Pin used

Every probe in this run targets `review_sha = 94383e671e51f95d142f3220f97c8e453721d516`
(`feature.json`'s recorded pin, read directly — NOT the HEAD under gate). `<pin>` below always
means this value. HEAD under gate is `17106762c588b3d1c0df45efbcb6128604efb185`; base of the
review range is `7ccfae8dd7644bc3aaea612dabf4317c0d804f99`.

## 1. Matrix re-run

Delta since c18 (`34a49c4b`): exactly one source commit, `17106762`
(`fix: derive the n_a decision range from the repository, not from the digest`), touching
`.claude/skills/harness/bin/validate-digest.py` and `.claude/skills/harness/bin/test-validate-digest.py`
only — confirmed via `git diff --name-only 34a49c4b 1710676`. SIMPLIFY's four read-only angles
applied nothing (HEAD unmoved from c19's `34a49c4b`... — no, HEAD is `1710676`, SIMPLIFY landed
nothing further; c19's fix commit itself is `1710676`, confirmed by `git log --oneline`).

`validate-digest.py` remains a `cross_module` seam — read by the SubagentStop hook, the CLI mode,
and exercised by `test-validate-digest.py` as one of the 28 integration scripts — so the change
type is **unchanged** from c18/c19. Matrix requires `unit` + `integration`, both configured active.

| kind | required | command | state | count | vs baseline (c13-r01: 29/29, 28/28) |
|---|---|---|---|---|---|
| unit | matrix: cross_module.always | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | satisfied | 29/29 scripts, 0 fail, exit 0 | matches |
| integration | matrix: cross_module.always | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | satisfied | 28/28 scripts, 0 fail, exit 0 | matches |
| functional | excluded (DEC-187) | n/a | soft skip | n/a | n/a |

Raw logs: `/tmp/qa_unit_c21.log` (1443 lines), `/tmp/qa_integration_c21.log` (1908 lines). Dedup
method (same as c18/c13-r01, script-name grep, `^PASS test-[A-Za-z0-9_.-]+\.py`, de-duplicated):
29 unique unit scripts, 28 unique integration scripts, zero `^FAIL test-` in either.

## 2. Cycle-18 must_fix — CLOSED, by discrimination

**The finding:** `code_grade_bound_to_review` bound only `head`, so a self-consistent no-op
`reviewed: "<pin>..<pin>"` legitimately resolved to the pin and bought `code_grade: n_a` at exit 0.

Reconstructed the literal c18 forged digest (`code_grade: n_a`, `reviewed: "<pin>..<pin>"`,
`artifact:` pointing at THIS run's own real path,
`.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-regate-c21.md`) plus the `~1`
variant and the honest `7ccfae8d..<pin>` base, all run against the current, committed
`validate-digest.py`:

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe_c21/forged_pin_pin.txt
VERDICT: BLOCKED (contract violation)
  - code_grade='n_a' is only valid when the reviewed diff has no Python file.
EXIT=1

$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe_c21/forged_tilde1_pin.txt
VERDICT: BLOCKED (contract violation)
  - code_grade='n_a' is only valid when the reviewed diff has no Python file.
EXIT=1

$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe_c21/honest_pin.txt
VERDICT: BLOCKED (contract violation)
  - code_grade='n_a' is only valid when the reviewed diff has no Python file.
EXIT=1
```

**Range-independence property, stated as such:** all three ranges (`<pin>..<pin>`,
`<pin>~1..<pin>`, and the honest `7ccfae8d..<pin>`) — despite naming three different shapes in
the digest's own `reviewed:` field — produce the identical error message at exit 1. The range the
digest names no longer changes the answer, because `code_grade: n_a` never reads it: the decision
comes from `merge-base(default branch, review_sha)..review_sha`, which for `<pin>` genuinely
contains Python changes, so all three are refused for the same reason regardless of what the
reviewer wrote. That is what closes the CLASS, not one SHAPE.

Contrast — `code_grade: fail` over the exact same forged no-op range (`<pin>..<pin>`) still
validates, because `pass`/`fail`/`grade_2` are deliberately never gated on base derivation:

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe_c21/forged_pin_pin_fail.txt
digest ok
EXIT=0
```

**Verdict: cycle-18 must_fix is CLOSED.** Confirms the orchestrator's own measurement rather than
contradicting it.

## 3. Fail-closed branch probes — four results, all from live runs

Built `/tmp/sec01probe_c21/live_item3.py` (independently authored, not copied from
`test-validate-digest.py`, though using the file's own established technique: real `/tmp` git
repos, `os.chdir`, in-process `importlib` load of `validate-digest.py`, `feature_dir` override).
Full run: `python3 /tmp/sec01probe_c21/live_item3.py` → all five checks `[PASS]`, script exit 0.

**a. `n_a` REFUSED, default branch unresolvable.** Fresh `/tmp` repo, one commit, deliberately no
`origin` remote and no `refs/remotes/origin/HEAD` ever set. `code_grade: n_a` over `<oid>..<oid>`:
```
["code_grade='n_a' cannot be confirmed: this checkout's default branch (origin/HEAD) could not be resolved, so the range the repository would review cannot be derived — this refuses the claim, it does not grant it."]
```

**b. `n_a` REFUSED, merge base unresolvable.** Fresh `/tmp` repo: `main` (mirrored to
`origin/main`/`origin/HEAD`, both resolvable) plus a real `git checkout --orphan` branch sharing
no commit history at all — `git merge-base` itself returns nothing against real plumbing.
`code_grade: n_a` over `<orphan_oid>..<orphan_oid>`:
```
["code_grade='n_a' cannot be confirmed: no merge base between the default branch and review_sha could be computed, so the range the repository would review cannot be derived."]
```

**c. `pass`/`fail`/`grade_2` STILL VALIDATE under both degraded conditions.** Same two repos as
(a)/(b), same pins:
- No `origin/HEAD` at all: `pass`, `grade_2` (with a reason), and `fail` (`VERDICT: FAIL`) all
  return `[]` errors — ungated.
- No merge base (orphan): `pass` over the same orphan pin returns `[]` errors — ungated.

**d. `n_a` legitimately ACCEPTED.** Fresh `/tmp` repo: a base commit (mirrored as
`origin/main`/`origin/HEAD`) followed by a docs-only commit (`NOTES.md`, zero `.py` files) as the
pin, so the derived range genuinely contains no Python change. `code_grade: n_a` over
`<head>..<head>` returns `[]` errors — accepted, proving the refusal in (a)/(b) is not a vacuous
"reject everything."

**Q1 coverage-gap check:** the c19 receipt's own open Q1 flagged the "no merge base" branch as
pinned nowhere before send-back 2. Read the receipt in full: send-back 2 (`check_no_merge_base`,
using a real orphan-branch `/tmp` repo) closed it before this run started. My own independent
probe (result **b** above, self-constructed, not reusing the fixture) reproduces the same
behavior live. **Not a coverage gap** — resolved by the squad and independently re-confirmed here.

## 4. Non-vacuous binding and test-first audit for the `1710676` delta

**What fails if `1710676` is reverted.** Reverted `validate-digest.py` alone to its pre-`1710676`
(`34a49c4b`) content, kept `test-validate-digest.py` at its current (post-`1710676`) content, and
ran the current suite:

```
$ git show 34a49c4b:.claude/skills/harness/bin/validate-digest.py > /tmp/qa_c21_revert/validate-digest-pre1710676.py
$ cp /tmp/qa_c21_revert/validate-digest-pre1710676.py .claude/skills/harness/bin/validate-digest.py
$ python3 .claude/skills/harness/bin/test-validate-digest.py
FAIL  code-grade and review-policy gates
        a forged no-op AT review_sha itself must reject — the n_a decision must never read the digest's own reviewed:: []
        a forged no-op AT review_sha whose TRUE derived range changed Python must still reject: []
        a review_sha already merged into the default branch must refuse with its own named error: []
        n_a with an unresolvable default branch must refuse: []
        n_a on an orphan review_sha with no merge base to the default branch must refuse: []
EXIT=1
```

Five named cases (`check_reviewed_range`'s AT-pin assertion, `check_derived_base_range`'s
changed-Python and degenerate-ancestor assertions, `check_unresolvable_default_branch`,
`check_no_merge_base`) all fail on this delta's own commit. Restored via `cp` from a pre-mutation
backup (`/tmp/qa_c21_revert/validate-digest-current-backup.py`), md5 confirmed
`42297a46503d1331c020b0e75b3385c9` before and after, `git status --porcelain` on the file empty
after restore.

**Auditing the receipt's admission — the `~1` variant did NOT independently fail on this same
revert.** Grepped the revert's FAIL output for `~1`/`must also reject`: zero matches. Confirms the
receipt's own statement verbatim (its RED-before-fix section: *"The `~1` unit-test variant didn't
independently fail pre-fix — that specific single real commit happens to touch `.py` on its own,
so the OLD digest-named diff caught it by coincidence"*) — reproduced independently here on the
whole-commit revert, not merely taken on the receipt's word.

**Does the mutation proof offered in place of that RED actually bind the `~1` case?** Restored the
current file, then applied the receipt's own named mutation
(`return reviewed_python_change(f"{base_oid}..{review_oid}")` → `return False, None`, i.e.
unconditionally claim "no Python changed" for the derived range) and ran the suite:

```
FAIL  code-grade and review-policy gates
        <review_sha>~1..<review_sha> is inside the class Q8 closes and must also reject: []
        <review_sha>~1..<review_sha> against a real repo must also reject: []
        (plus three other cases in the same family)
EXIT=1
```

**Yes — agree with the receipt's claim.** The `~1` case is genuinely bound, just not by a whole-
commit revert (coincidental, as the receipt says); the mutation that collapses the derived-range
decision to a constant does trip it, by name, live. Restored via `cp` from
`/tmp/qa_c21_revert/validate-digest-current-backup.py`, md5 confirmed
`42297a46503d1331c020b0e75b3385c9` before and after, re-ran green (`ALL PASSED`, exit 0).

## 5. Regression re-confirmation — CR-01, CR-02, UI-01

```
$ python3 .claude/skills/harness/bin/code-grade.py --base 7ccfae8d --head 17106762
EXIT=0
```
Measured, not assumed: **exit 0**, **178 records** (`grep -c '^FUNCTION$'`), **PASSING: 164**
(178-164 = 14 below-bar, zero blocking), **0** `SEVERITY: high`, **14** `SEVERITY: med` — every one
of the 14 confirmed at `GRADE: 2` (`grep -B5 'SEVERITY: med' | grep 'GRADE:' | sort -u` → single
value `GRADE: 2`).

| suite | exit |
|---|---|
| `test-validate-digest.py` | 0 (`ALL PASSED`) |
| `test-code-grade.py` | 0 (`PASS test-code-grade`) |
| `test-code-grade-cli.py` | 0 (`PASS test-code-grade-cli`) |
| `test-gate-policy.py` | 0 |
| `test-check-plan-routes.py` | 0 (`ALL PASS`) |

Named regression checks:
- **CR-01** — `check_self_grading`, one of the eight functions `test-code-grade.py:main()` calls
  (source read: `main()` tuple includes `check_self_grading`); the file's summary exit is 0
  (`PASS test-code-grade`), so this check ran and passed as part of that result.
- **CR-02** — `test_bars_follow_test_kinds` in `test-code-grade-cli.py`, wired into `main()`
  (`failures += test_bars_follow_test_kinds(repo)`, source read); covered by the file's exit-0
  `PASS test-code-grade-cli`.
- **UI-01** — `test_review_skill_states_severity_vocabulary` in `test-code-grade-cli.py`, also
  wired into `main()` (`failures += test_review_skill_states_severity_vocabulary()`, source read);
  same exit-0 result covers it.

## 6. Mutation, not assertion — targeting the derived-range decision specifically

Distinct from item 4's mutation (which the receipt itself performed): this one targets the
degenerate-ancestor branch of `_derived_reviewed_python_change` specifically, not the head
binding (already proven bound in cycle 18) and not the whole-range collapse already exercised in
item 4.

- md5 of `validate-digest.py` before: `42297a46503d1331c020b0e75b3385c9`.
- Mutation: `if base_oid == review_oid:` → `if False and base_oid == review_oid:` (disables the
  degenerate-range refusal specifically — a `review_sha` already merged into the default branch
  would silently fall through to the honest-looking diff call instead of being refused).
- Ran `python3 .claude/skills/harness/bin/test-validate-digest.py` against the mutant:
  ```
  FAIL  code-grade and review-policy gates
          a review_sha already merged into the default branch must refuse with its own named error: []
  EXIT=1
  ```
  Exactly one named case fails — `check_derived_base_range`'s degenerate-ancestor assertion.
- Restored via `cp` from `/tmp/qa_c21_revert/validate-digest-before-item6.py` (never
  `git checkout`/`git restore`). md5 after restore: `42297a46503d1331c020b0e75b3385c9` — matches.
  `git status --porcelain -- .claude/skills/harness/bin/validate-digest.py` after restore: empty.
- Re-ran green: `python3 .claude/skills/harness/bin/test-validate-digest.py` → `ALL PASSED`,
  exit 0.

## Cosmetic observation — REFUTED

Constructed a real `artifact: none` digest and ran it live:
```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe_c21/artifact_none.txt
VERDICT: BLOCKED (contract violation)
  - code_grade cannot be bound to review_sha: artifact 'none' does not name a .harness/<repo>/features/<FEAT>/ location — write your review under that feature's notes/.
EXIT=1
```
The binding-failure message prints **once**, not twice (`grep -c "does not name a"` → `1`).
**Refuted** — not a backlog candidate; the duplication described in the dispatch does not
reproduce on this HEAD.

## Tree state at the end

```
$ git -C <worktree> rev-parse HEAD
17106762c588b3d1c0df45efbcb6128604efb185
$ git -C <worktree> status --porcelain -- .claude/skills/harness/bin/validate-digest.py .claude/skills/harness/bin/test-validate-digest.py .claude/skills/harness/bin/code_grade.py .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/gate_policy.py .claude/skills/harness/bin/check-plan-routes.py .claude/skills/harness/bin/test-code-grade.py .claude/skills/harness/bin/test-code-grade-cli.py .claude/skills/harness/bin/test-check-plan-routes.py .claude/skills/harness/bin/test-gate-policy.py .claude/skills/harness-code-review/SKILL.md
(empty)
```
All source files byte-identical to `17106762`. Every probe/mutation was performed via `cp`
to/from `/tmp` backups, never `git checkout`/`git restore`, and each restore was verified by md5
match plus an empty `git status --porcelain` before proceeding to the next probe. No scratch files
left inside the repository — every fixture, backup, and repro script lives under `/tmp`.

## Why PASS

The matrix holds at baseline (29/29 unit, 28/28 integration). The cycle-18 must_fix — the
`review_sha..review_sha` bypass — is closed as a class, demonstrated by the range-independence
property (three differently-shaped forged ranges, one identical refusal) rather than by patching
one shape. All four fail-closed branches Q8 requires were constructed and run live, each producing
the required result, with the previously-flagged coverage gap (no-merge-base branch) independently
reconfirmed closed. CR-01/CR-02/UI-01 are unregressed by named check. Two independent live
mutations against the derived-range mechanism specifically (not the head binding) each fail by
name and restore cleanly. The one cosmetic claim in the dispatch does not reproduce.
</content>
