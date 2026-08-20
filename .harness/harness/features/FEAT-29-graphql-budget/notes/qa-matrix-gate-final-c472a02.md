# QA matrix gate — final, pinned at c472a02

`git rev-parse HEAD` = `c472a02262a64f465dad077e14df61f770538b58` — matches the dispatched
`review_sha` (`c472a02`). Not BLOCKED on the pin.

T-03 `verify:` cross-checked against `plan.yaml` line 286-287: signed text is exactly
`.claude/skills/harness/bin/run-unit-tests.sh --kind unit`. Matches the dispatch verbatim. Not
BLOCKED on the verify string.

## 1. Per-kind results, first-party, at the pin

`HARNESS_GH_COST_LOG` confirmed unset in this shell before each run (`env | grep` empty); never
exported outside a temp root.

| kind | cmd | exit | scripts run | pass | fail |
|---|---|---|---|---|---|
| unit | `run-unit-tests.sh --kind unit` | 0 | 18 | 18 | 0 |
| integration | `run-unit-tests.sh --kind integration` | 0 | 12 | 12 | 0 |

`.harness/logs/gh-cost-2026-08-19.jsonl` byte size: **39504 before both runs → 39504 after
`--kind unit` → 39504 after `--kind integration`. Unchanged across both.** Consistent with the
OFF-by-default recorder (`gh_cost_log.py:53`, default `"0"`) and with the suites using fakes, not a
live `gh` — no live `gh` call was made.

Note: `--kind integration` runs `test-check-state.py` as one of its 12 registered scripts (it is
already inside `INTEGRATION_SCRIPTS`, not something dispatched directly). It passed and the cost
log's byte count did not move, evidence it drove no live `gh` call. This was not a direct invocation
of `check-state.sh` or `test-check-state.py`; it ran only as a member of the mandated `--kind
integration` command in item 1 of the dispatch. Flagging for the record rather than silently
absorbing it, since a separate constraint names that file — no independent invocation of either was
made.

## 2. OFF-side coverage — by inspection, no source writes

**(a) Does any OFF-side case drive a non-zero `rc`? No.**
Both wrap-site OFF blocks call `_counting_fake()` with its default `rc=0`
(`test-gh-cost-log.py:289` `def _counting_fake(rc=0, stdout="ok")`, called bare at :338 and :370).
The only non-zero-`rc` case in the whole file (`_counting_fake(rc=1)`, :390) drives the **ON**
FAILING block (:381-410), not an OFF one. The two OFF+non-zero-rc-labelled checks that do exist
(:251-259, "unset, a FAILING invocation …") call `gh_cost_log.record(...)` **directly** (:254),
bypassing `measured()` and both wrap sites entirely — they exercise `record()`'s own guard at
`gh_cost_log.py` ~:112, not the guard inside `measured()` at :157 that the hypothetical mutant
touches. No OFF-side case anywhere reaches `measured()`'s disabled branch with a non-zero
`m.returncode`.

**(b) Would the current unit suite go red under the hypothetical mutant? No — SURVIVES.**
The mutant only changes behaviour inside `measured()`'s `if not _enabled() or
is_counter_call(argv):` branch (`gh_cost_log.py:157-159`), and only when `m.returncode not in
(None, 0)`. For any test to distinguish it from the current code, it must go through `measured()`
(not call `record()` directly) with the recorder OFF and a non-zero returncode. Enumerating every
`measured()`/wrap-site invocation in the file:
  - :202, :230 — both explicitly `HARNESS_GH_COST_LOG=1` (ON); mutant's branch never entered.
  - :320-333, :349-365 — wrap-site ON blocks; not applicable.
  - :338-346, :370-379 — wrap-site **OFF** blocks, but `_counting_fake()` default `rc=0`; mutant's
    `if m.returncode not in (None, 0)` is `False`, so the mutant's extra `record()` call never
    fires — behaviour is identical to the original, and the two `check()`s ("no line written",
    "exactly one subprocess call") both still pass.
  - :388-410 — the one non-zero-rc case, but **ON**, not OFF; mutant's disabled branch is skipped
    entirely (`_enabled()` is True).
No test combines OFF + `measured()`/wrap-site + non-zero rc. **Survives — killed by nothing.** This
is a genuine coverage gap in the OFF-side matrix, not a hypothetical one: SC-05's "including for a
failing invocation" (BRIEF.md lines 83-90) is asserted only against `record()` called directly
(:251-259), never against the actual `measured()` code path a real failing wrapped call takes.

**(c) At that moment, is `m.returncode` actually populated? Yes.**
Traced through `factory_gh.run_gh` (`factory_gh.py:151-162`): `with gh_cost_log.measured(args) as
_cost:` opens the context manager, `subprocess.run` executes, and **`_cost.returncode =
r.returncode` (line 162) runs unconditionally, inside the `with` block, before it exits** — for
every returncode, 0 or non-zero, ON or OFF. Only a `FileNotFoundError` (`gh` binary missing) skips
line 162, and that is a different failure shape than "invocation ran and returned non-zero." So for
the ordinary case the mutant probes — gh runs, returns non-zero — `m.returncode` is set to the real
non-zero value before `measured()`'s `finally` executes on either the OFF or the ON path. The
mutant's `if m.returncode not in (None, 0):` would evaluate `True` and record a line the OFF state
promised never to write. Confirmed live by (b): nothing catches it.

## 3. Matrix grading — T-03, `change_type: feature`

`test_matrix.feature.always` = `[unit, integration]` (`.harness.json`).

| kind | state | cmd | named tests |
|---|---|---|---|
| unit | **satisfied** | `run-unit-tests.sh --kind unit` | `test-gh-cost-log.py` (35/35, all new for T-03), `test-factory-gh.py` (part of the same run, exercises the `run_gh` wrap site) |
| integration | **satisfied, per the operator's signed ruling** | n/a — ruled inapplicable/pre-satisfied by amendment | BRIEF.md SC-05 `evidence: unit`; ruling recorded plan.yaml lines 84-97 |

Grading against the ruling as instructed, not re-litigating: the operator ruled the integration read
SATISFIED for T-03 because none of `test_kinds.integration.detect`'s four files reference
`gh_cost_log` and none appear in the plan, so the kind is structurally unreachable as signed, and
SC-05 already carries `evidence: unit`. **`matrix_ok: true`** under that ruling.

## Prior recorded findings — confirmed, not rediscovered

Confirming rather than re-deriving: B-1, B-2, B-3, B-5, B-6, B-11, B-12
(`integration.detect`/`INTEGRATION_SCRIPTS` mismatch), B-13, B-15 all stand as previously recorded.
harness-qa is not granted `factory_gh.py` — not re-raised.

## New finding this gate — item 2(b)/(c) above

The OFF-side of SC-05 ("no file and no line … including for a failing invocation") is tested only
against `gh_cost_log.record()` called directly. No test drives a failing invocation through
`measured()`/a real wrap site with the recorder OFF, so a mutant that leaks a record on that exact
path survives the current unit suite. This is a coverage gap, not a suite failure — the suite is
green and exit 0 both kinds, but it does not discriminate the disabled-branch record leak. Reporting
as a finding per dispatch instruction; not filed as a new open_question since the dispatch asked for
inspection only, no source writes.
