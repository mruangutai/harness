# FEAT-43 goal-check — cycle 21, at pin `17106762`

**BLUF: nineteen of twenty success criteria are `met` on evidence I re-derived myself at the pin;
SC-11 is `unproven` and is the operator's UAT to decide.** No SC is `not_met`. No SC rests on
inherited evidence, and no SC depends on the synthetic-fixture distinction the panel flagged. One
residual belongs in the ship briefing: T-01's literal "grade 4 or better" self-standard for
`code_grade.py` is unmet for 2 of 47 functions, and REQ-06 does **not** govern that clause.

**Provenance of my runs.** `HEAD` is `a0ff125` (the pin plus feature bookkeeping);
`git diff --name-only 17106762..a0ff125 -- .claude .omp` is **empty**, so every command below
measured the pinned code. Re-derived live: `code-grade.py --base 7ccfae8d --head 17106762` → **exit
0**, 178 `FUNCTION` records, **0** grade-1, **14** `REASON REQUIRED`. Five focused test files run by
me, each exit 0: `test-code-grade.py`, `test-code-grade-cli.py`, `test-gate-policy.py`,
`test-validate-digest.py`, `test-check-plan-routes.py`. No suite, no formatter, no linter.

## Per-SC verdicts

| SC | method | verdict | deciding evidence (named case / citation) |
|---|---|---|---|
| SC-01 | automated·unit | met | `test-code-grade.py::check_fixtures` — `FIXTURES` counted by AST = **12**, `check(len(FIXTURES) >= 12)` at `:505`, `check(grades, {1,2,3,4,5})` at `:506`; per-record tuple asserts `abc_a/abc_b/abc_c` individually (`:502`) |
| SC-02 | inspection | met | Three fixtures re-derived by hand at the pin in `review-…-code-reviewer-…-c21.md:219-240` (lines 28, 30, 51 cited); three *different* ones by qa (`qa-…-c21.md:40`). `git show <pin>:…/test-code-grade.py` grep for "produced by the tool" → **0 hits** (I ran it) |
| SC-03 | automated·unit | met | `test-code-grade.py::check_direction_pairs` — AST enumeration of `DIRECTION_PAIRS` gives exactly **4 worse + 2 better**, one metric each (cognitive×2, cyclomatic, abc / cognitive, cyclomatic); both the metric (`:526`) and the grade (`:530`) movement asserted |
| SC-04 | automated·integration | met | `test-code-grade-cli.py::test_diff_and_determinism` — copied checkouts at two absolute paths, foreign cwd, monkeypatched reversed `_diff_paths` order, byte-identical stdout |
| SC-05 | automated·integration | met | `test-code-grade-cli.py::test_paths` — per-field loop over the FAIL record in text (`:77-82`) and one assertion per JSON key (`:87-92`): path, line, qualname, cyclomatic, cognitive, abc, grade, driver. No whole-string match |
| SC-06 | automated·integration | met | `test-code-grade-cli.py::test_parse_and_usage` — exit **3**, `PARSE ERROR: "src/bad.py"` on stderr, `UNGRADED:` block, `PASSING: 0` (`:108-116`) |
| SC-07 | automated·integration | met | `test-code-grade.py::check_changed_function_resolution` — seven-way single-commit fixture, gated set by set equality |
| SC-08 | automated·integration | met | same case — five individual absence assertions plus untouched-grade-1 absent-from-gated / present-in-informational |
| SC-09 | automated·unit | met | `test-code-grade.py::check_worked_examples` — parses `## Worked examples` out of the live `SKILL.md`, ≥5 examples, one assertion per example |
| SC-10 | automated·unit | met | `test-code-grade.py::check_delivery` — loops `(".omp/agents", ".claude/agents")` × five specialists = ten individual assertions, no repo-wide count |
| SC-11 | uat | **unproven** | No automated evidence is possible (`eval` has `cmd: null`, BRIEF §Verification gaps). The panel did not judge it, correctly. Script being prepared at `notes/uat-sc11-c21.md`; **the operator's run decides it** |
| SC-12 | automated·unit | met | `test-gate-policy.py::check_review_evaluation` — the exact pair printed in my run: `ok review blocks must_fix even without a severity escalation` / `ok review passes a clean medium-severity report` |
| SC-13 | automated·unit | met | `test-gate-policy.py::check_policy_loading` — my run printed four per-key `ok loader resolves {qa_gate,review,uat,merge} by name`, plus `unrecognised`, `absent gates block`, `unparseable`, `unreadable` each raising and naming the offender |
| SC-14 | automated·integration | met | `test-code-grade-cli.py::test_paths` — positive `REASON REQUIRED: grade_two` (`:80`), negative `expect("REASON REQUIRED" in clean.stdout, False)` (`:95`); reinforced positively by `test_bars_follow_test_kinds:226`. Live: my pinned gated run emits exactly **14** demands |
| SC-15 | inspection | met | `review-…-code-reviewer-…-c21.md:158-217` answers all 14 demands by qualname with cyc/cog/abc and a written reason. I re-derived the count independently: **14**, non-vacuous |
| SC-16 | automated·integration | met | `test-check-plan-routes.py` — my run printed `PASS case_27a_owner_manifest_controls_routes`, `PASS case_27b_prior_revision_false_ok`, `PASS case_27c_unreadable_owner_manifest_refuses`; 27b is the prior-revision false-`OK` proof |
| SC-17 | automated·unit | met | `test-code-grade-cli.py::test_bars_follow_test_kinds` — four boundary points off a swapped `test_kinds.configured.detect: "checks/**"` fixture, so classification is derived, not a path list |
| SC-18 | inspection | met | `git show 17106762:.claude/skills/harness-code-risk-grading/SKILL.md` **:162-163** — Sonar approximation disclaimer, "Shell scripts and TypeScript are not graded at all", and **:163-165** "does not fix code already below the bar". Read at the pin by me |
| SC-19 | automated·integration | met | `test-validate-digest.py` — my run printed `ok code reviewer omission of code_grade is rejected` (`:1637`); `check_code_grade_state` (`:1840`) rejects fail-plus-PASS |
| SC-20 | automated·integration | met | `test-validate-digest.py::check_review_policy` (`:1800`) + `check_config_errors` (`:2377`, same digest bytes accepted under `advisory`) + missing-`gates` raise + `check_prior_validator` (`:1815`, prior revision accepts — proves the assertion can fail) |

## Ruling on the synthetic-fixture distinction (panel point 2)

**No SC depends on it.** UI-01 was closed against a `/tmp` fixture because the CR-01 fix left no
blocking below-bar record in the honest range. I read SC-05's own field list: path, line, qualname,
cyclomatic, cognitive, ABC, grade, driver metric — **`severity` is not among them**, so the
`SEVERITY: high` rendering the panel could only show synthetically is not a thing SC-05 asks for at
all (it is asserted anyway, at `test-code-grade-cli.py:80`). SC-14 quantifies over "the gated set",
and its positive direction has **live** instances on this very diff — 14 `REASON REQUIRED` lines
from my own pinned gated run; its negative direction is unshowable on a corpus that contains a
grade-2 function, so a fixture is the only possible witness and is the right one. Both criteria grade
the *tool's behaviour*, which is general by construction; neither says "on this diff".

## Ruling on the carried-forward tasks (panel point 3)

**Live, not inherited.** I confirmed the byte-identity myself:
`git diff --name-only 94383e67..17106762 -- .claude/skills/harness-code-risk-grading/ .harness/glossary.md .omp/agents/ .claude/agents/` → **0 files**. But the stronger point is that the
SCs T-04/T-05/T-06/T-10 carry do not rest on that argument at all: SC-09 and SC-10 are executed by
`check_worked_examples` / `check_delivery`, which **read those files at run time** in a tree I proved
identical to the pin, and I ran them; SC-18 I read directly out of the pin via `git show`. Nothing is
marked `unproven` on inheritance grounds.

## Ruling on the T-01 / REQ-06 grade-2 residual — **a named residual for the ship briefing**

Re-derived myself: `code-grade.py .claude/skills/harness/bin/code_grade.py` → 47 functions, exit 0,
two at grade 2 — `_body_hashes.collect` (`:346`, cyc 9 / cog 18 / abc 17.3) and `gated_set` (`:374`,
cyc 8 / cog 25 / abc 24.9).

**REQ-06 does not govern T-01's clause.** REQ-06 is a *merge* requirement — worst grade cannot merge,
second-worst proceeds with a written reason — and it is fully satisfied: zero grade-1 records, both
functions reasoned (SC-15 items 3–4). T-01, however, traces to **REQ-03**, and its final paragraph
sets a *stricter, file-specific* standard the requirements never asked for: "Keep every function you
write in `code_grade.py` at grade 4 or better… The tool must pass its own bar"
(`plan.yaml:186-187`). A requirement about mergeability cannot discharge a task instruction about
craftsmanship; REQ-06 makes the change shippable, not T-01 complete. No SC asserts T-01's clause, so
nothing gates — but the suite stays green only because `SELF_GRADING_ALLOWLIST` in
`test-code-grade.py:207` excuses both entries (qa's deletion probe, `qa-…-c21.md:96-107`, shows the
entries are load-bearing for the test and structurally inert to the gate). An allowlist is a record,
not a fix. **The operator should see this named at the ship decision** — accept the deviation or route
a follow-up — rather than have it live only inside a `low` panel note. I do not treat it as blocking;
I decline to treat it as governed.

## Are the success criteria met?

**Yes for the tooling, and undecided for the teaching.** Nineteen of twenty criteria are met on
evidence I re-derived at the pin rather than adopted: every `automated` criterion resolves to a named
passing case in one of five test files I ran to exit 0, and the three `inspection` criteria resolve to
citations read at the pin (`SKILL.md:162-165`, the reviewer's fourteen answered reason demands, and
two independent hand re-derivations of the fixtures). Nothing is `not_met`; nothing rests on inherited
or synthetic evidence in a way its own criterion forbids. **SC-11 is the one open criterion, and it
carries the feature's central claim — that the guidance changes what an engineer writes.** It is
`verify: uat` by the operator's own post-signature amendment, `eval` has no runner, and the pre-build
A/B probe graded a draft skill and is explicitly not evidence for it. So the feature is done up to one
human judgement: **the operator's SC-11 UAT decides whether FEAT-43 delivered its goal, and one
residual — T-01's unmet grade-4 self-standard on two of `code_grade.py`'s 47 functions — should be
read out to them at the ship decision.**

## Working tree

```
$ git -C <worktree> status --porcelain
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/research-goalcheck-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/uat-sc11-c21.md
```
Only my own artifact plus the sibling pm's concurrent SC-11 UAT script; every tracked file is
unmodified. Every probe ran in `/tmp`; HEAD was never moved.
