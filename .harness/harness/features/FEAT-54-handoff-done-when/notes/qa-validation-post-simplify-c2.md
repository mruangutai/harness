# Post-simplify QA c2 — FEAT-54 handoff Done when

## BLUF

**PASS.** Both configured blocking kinds exited 0 with non-zero discovery (unit: 25 files; integration: 44 files). The prior exact 62-pair delta census retained exact identity and cleared every applicable grade bar: 20 production functions at grade 4+ and 42 test functions at grade 3+. The SIMPLIFY-touched `measure_note` is grade 4. The unit runner executed all six focused probe tests, and all six passed; rejected paths made zero model calls while the valid note remained the positive two-call control.

## Phase 1 expectations and matrix

Before source access, `BRIEF.md` and `plan.yaml` required unit coverage for shared Done-when shape, grammar/resolution, resolve-mode separation, AND semantics, and invalid authority types, plus integration coverage through the actual write and persisted-state gates. For the post-SIMPLIFY delta, the explicit acceptance boundary additionally required preserving probe input rejection with zero model calls and preserving the valid note's two-arm/two-call behavior. Phase 2 found those focused contracts in the existing six-test unit file; no coverage gap was closed or test changed.

| Kind | State | Exact command | Exit | Discovery |
|---|---|---|---:|---:|
| unit | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | `pool: 8 workers, 25 files` |
| integration | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | `pool: 8 workers, 44 files` |
| handoff_comprehension | locally-run, deliberately not executed | `tests/manual/probe-handoff-comprehension.py` | n/a | n/a |

Neither configured run had an assertion, import, load, collection, or syntax failure. The non-zero file counts establish that neither successful exit was a zero-discovery pass.

## Exact delta-scoped Python risk grade

The exact whole-file JSON input command from `notes/qa-validation-c2.md` was repeated:

```sh
python3 .claude/skills/harness/bin/code-grade.py --json .claude/skills/harness/bin/handoff_done_when.py tests/integration/test-check-domain.py tests/integration/test-check-state.py tests/manual/probe-handoff-comprehension.py tests/unit/test-handoff-done-when.py tests/unit/test-probe-handoff-comprehension.py
```

It exited **1** with `passing=314`; as before, unchanged legacy records outside the mandatory delta census cause that whole-file result, so it is not substituted for the scoped gate.

For the mandatory gate, `EXPECTED` was populated with the exact 62-pair JSON recorded verbatim at `notes/qa-validation-c2.md:31-33`, and that same JSON-producing command was piped to the exact prior assertion:

```sh
jq -e --argjson expected "$EXPECTED" '[.records[] | select([.path,.qualname] as $key | any($expected[]; . == $key))] as $scoped | [$scoped[] | [.path,.qualname]] as $actual | if (($actual|sort)==($expected|sort) and ($actual|length)==62 and all($scoped[]; .grade >= (if .path==".claude/skills/harness/bin/handoff_done_when.py" then 4 else 3 end))) then {census:($actual|length), production:([$scoped[]|select(.path==".claude/skills/harness/bin/handoff_done_when.py")]|length), test:([$scoped[]|select(.path!=".claude/skills/harness/bin/handoff_done_when.py")]|length), minimum_grade:([$scoped[].grade]|min), records:$scoped} else error("changed-function census incomplete or applicable grade bar failed") end'
```

The pipeline exited **0** and returned `census=62`, `production=20`, `test=42`, `minimum_grade=3`. Sorted pair identity and the explicit length check mean missing, extra, renamed, empty, or narrowed membership cannot pass. The production-only threshold remained grade 4; all non-production census members retained the registered test threshold of grade 3.

Current SIMPLIFY-touched record: `tests/manual/probe-handoff-comprehension.py:199` `measure_note` — grade **4**, cyclomatic **3**, cognitive **0**, ABC **12.7**, bar **3**, PASS. The simplification therefore preserves every applicable production/test bar rather than relying on the whole-file exit.

## Six focused probe contracts

The unit suite output named `test-probe-handoff-comprehension.py`, showed its process exit **0**, then reported `Ran 6 tests in 0.022s`, `OK`, and `PASS test-probe-handoff-comprehension.py`. The six collected methods and their asserted behaviors are:

1. explicit repository-outside, absolute-outside, and traversal paths: refused with `self.calls == []` (`tests/unit/test-probe-handoff-comprehension.py:53-67`);
2. repository-contained symlink under both explicit and default selection: refused with zero calls (`:69-77`);
3. special/non-regular directory input: refused with zero calls (`:79-82`);
4. wrong basename and oversized input: refused with zero calls (`:84-91`);
5. valid handoff: exactly two calls, one for each measurement arm (`:93-95`);
6. dry run: zero calls (`:97-101`).

The actual suite transcript also showed refusal messages for outside/traversal paths, the directory, symlink in both selection modes, wrong basename, and the 1,048,577-byte oversized note; its valid control emitted both `as-written` and `done-when-stripped` results and `all complete answers: 2/2`. This binds rejected-input security to the zero-call recorder and retains the positive behavior control.

## SC evidence and adequacy limits

This rerun preserves the prior automated evidence map: SC-01/02 `tests/integration/test-check-domain.py:4033-4058`; SC-03 `:4061-4079`; SC-05 `:4211-4223`; SC-06 `:4114-4166,4192-4208` and `tests/integration/test-check-state.py:2178-2223`; SC-09 `tests/integration/test-run-unit-tests-kinds.py:21-40,69-98`; SC-12 `tests/unit/test-handoff-done-when.py:110-115`; SC-13 `tests/integration/test-check-domain.py:4080-4085`; SC-14 `tests/integration/test-check-domain.py:4211-4223` and `tests/integration/test-check-state.py:2244-2258`; SC-15 `tests/integration/test-check-state.py:2178-2223`.

Per dispatch, this evidence does **not** include a credentialled comprehension run, formatters, linters, review, goal-check, UAT, SC-04 repository-root inspection, project-wide validation, or unrelated suites. It makes no claim about nondeterministic comprehension quality; it gates the behavior-preserving SIMPLIFY delta, the configured unit/integration matrix, focused probe security/behavior, and the exact delta risk census only.
