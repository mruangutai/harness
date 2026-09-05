PASS

# QA test_matrix gate re-run — BUG-1286-test-tree-enforcement (c1, pinned 9adbce6b)

**BLUF: PASS.** Required kinds (`unit`, `integration`) both satisfied at the pinned sha; every
orchestrator measurement corroborated exactly with my own independently-run numbers; case 11's
four red mutants and two green controls re-proved myself against the built artifact (identical
results to the backend-dev receipt, now independently confirmed); live-config wiring confirmed.
One genuine, previously-unreported coverage gap found in the adequacy audit: the **toplevel-mismatch**
fail-open route in `tracked_paths()` — the exact scenario D-03's own rationale calls load-bearing
("a fixture root nested inside another checkout... must not be moved after the self-ownership
test") — has no test anywhere in the diff. Advisory, not gating (see severity below). HEAD
unchanged at `3379169a` (one commit past the pin, the `feature.json` pin write per the shared
context); nothing staged; nothing authored.

## 1. Required kinds (unchanged from c1's original gate)

Diff is `cross_module` (T-01) + `scaffolding`/`docs` (T-02–T-05); `cross_module.always = [unit,
integration]` in `harness.json` floors both; `scaffolding`/`docs` add nothing; `bugfix.when`'s
`match_bug_class` predicate has no implementation anywhere in the tree (repo Expertise G-08) so it
never fires. **Required set: `unit`, `integration`. No more, no less. `matrix_ok: true`.**

## 2. Commands run — my own exit status and counts

| Command | Exit | PASS | FAIL | Notes |
|---|---|---|---|---|
| `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 341 | 0 | 27 files, `pool: 8 workers, 27 files, 2.16s wall` |
| `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-run-unit-tests-layout.py` | 0 | 14 | 0 | direct run of the diff-added file |
| `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh --check-layout` | 0 | — | — | silent/clean |
| `env -u HARNESS_AGENT_TYPE python3 tests/manual/suite-census.py tree-audit` | 0 | — | — | `TOTAL 85 OUTSIDE 9 VIOLATIONS 0` |
| `grep ... DECISIONS.md && grep ... DECISIONS-INDEX.md && gen-decisions-index.py --stdout \| diff - ... && check-decision-anchors.py` (T-05 verify, verbatim from `plan.yaml:1047`) | 0 | — | — | `examined 30 anchor(s), 0 failed` |

All run with `env -u HARNESS_AGENT_TYPE` (repo Expertise G-07). `$?` read directly, no pipe.

## 3. Orchestrator measurements — all CORROBORATED with my own numbers

| Measurement | Orchestrator | Mine | Verdict |
|---|---|---|---|
| unit | exit 0, 341/0, 27 files | exit 0, 341/0, 27 files | **CORROBORATED** |
| integration | exit 0, 14/0 | exit 0, 14/0 | **CORROBORATED** |
| `--check-layout` | exit 0 | exit 0 | **CORROBORATED** |
| `tree-audit` | `TOTAL 85 OUTSIDE 9 VIOLATIONS 0` | identical | **CORROBORATED** |
| decision anchors | 30 examined / 0 failed | `examined 30 anchor(s), 0 failed`, exit 0 | **CORROBORATED** |

Baseline note (from repo Expertise/prior receipt, not re-measured by me): 316 PASS pre-feature at
`5eebad66` → 341 now is +25, matching the 25 new `check()` calls added across T-01's 11 cases.

## 4. Adequacy — per-route and per-rule bound/unbound table

**Four fail-open routes in `violations()` (`suite_layout.py:101-150`):**

| Route | Bound? | Test |
|---|---|---|
| no `.git` present (`os.path.exists(root/".git")` false, `suite_layout.py:130`) | **BOUND** | unit case 5, `test-suite-layout.py:260` (`legal_tree()` never creates `.git`) |
| `git rev-parse --show-toplevel` mismatches root (`suite_layout.py:74-75`, raises `LookupError`) | **UNBOUND** | grepped both `test-suite-layout.py` and `test-run-unit-tests-layout.py` for "toplevel"/nested-repo scenarios — no match in either file |
| `suite_layout.py` itself absent from the tracked index (`suite_layout.py:136`) | **BOUND** | unit case 9, `test-suite-layout.py:359-360` ("repository not shipping suite_layout.py gets no outside-tests finding") |
| `tracked_paths()` raising on missing-git / non-zero exit / timeout (`suite_layout.py:52-73`) | **PARTIALLY BOUND** | unit+integration case 4 (`test-suite-layout.py:241-247`, `test-run-unit-tests-layout.py:114-123`) covers only the `git ls-files` non-zero-exit sub-route (empty `.git` dir). `FileNotFoundError` (git binary absent) and `subprocess.TimeoutExpired` are never exercised — grepped both test files for `timeout`/`FileNotFoundError`/`monkeypatch`/`mock`: no matches anywhere |

**Four `DOCUMENTED_EXCEPTIONS` self-policing rules (`_registry_findings`, `suite_layout.py:79-98`):**

| Rule | Bound? | Test |
|---|---|---|
| entry is not an exact path (glob char) | **BOUND** | case 6, `test-suite-layout.py:288-289` |
| entry listed twice | **BOUND** | case 6, `test-suite-layout.py:296-297` |
| entry unnecessary (vocabulary would never flag it) | **BOUND** | case 6, `test-suite-layout.py:304-305` |
| entry no longer tracked | **BOUND** | case 6, `test-suite-layout.py:312-313` |

**Finding QA-1 (new, severity med, advisory):** the toplevel-mismatch route is precisely the
scenario D-01's/D-03's own governing text names as load-bearing (`plan.yaml` D-03: "the toplevel
comparison is a precondition of enumeration and must not be moved after the self-ownership test,
because a fixture root nested inside another checkout enumerates empty, which would fail
[silently inert]"). By inspection the shipped code is correct (comparison precedes the
`suite_layout.py`-tracked check, `suite_layout.py:74-75` before `:136`) and I did not find it
wrong — but nothing in either test file would catch a future regression that reorders or drops
this check. This is the same class as the two already-backlogged findings (F-1, F-2): a
non-gating coverage gap in a fail-closed path, not a live defect. I did not construct the nested-
checkout fixture myself (author-nothing constraint on this dispatch) — recording it as a finding
for the validator lead/backlog rather than closing it.

## 5. Case 11 — four red mutants and two green controls, re-proved independently

Wrote my own throwaway probe (`/tmp/bug1286_qa_probe/probe.py`, deleted after use, never touched
any tracked file) that `importlib`-loads `tests/unit/test-suite-layout.py` as a module (letting its
own top-level suite run once, harmlessly, against the real repo) and calls its already-bound
`hygiene_uncertified(test_kinds_cfg)` / `select_control_candidate(test_kinds_cfg)` against six
deep-copied, independently-mutated `test_kinds` dicts derived from the real `harness.json`:

| Scenario | My result |
|---|---|
| GREEN 1 — unmutated `detect` | `uncertified == []` |
| GREEN 2 — legitimate narrowing, drop `**/test_*.py` | `uncertified == []`, control candidate falls through to `.harness/tools/a.test.d/gen.py` |
| RED i — `tests/../evil/**` substituted for `tests/unit/**` | `uncertified == ['unit: tests/../evil/** (core contains a directory separator)']` |
| RED ii — `**/test_*/**` appended (non-final-segment wildcard) | `uncertified == ['unit: **/test_*/** (core contains a directory separator)']` |
| RED iii — `**/*.spec.*` appended | `uncertified == ['unit: **/*.spec.* (no fixed literal key ...)']` |
| RED iv — `**/test_*.p?` appended (extension-position escape) | `uncertified == ['unit: **/test_*.p? (no fixed literal key ...)']` |

All six match the backend-dev receipt's own probe (`notes/receipt-harness-backend-dev-T-01-c1.md`
§5) exactly — **now independently reproduced**, not merely trusted. All four red cases genuinely
redden with the correct named pattern; both green controls stay clean. Case 11's positive control
in the *live* run also fired for real: `PASS case 11 behavioural: positive control offender is
detected` against `.harness/tools/test_dir/gen.py` (confirmed live via `select_control_candidate`
returning that exact candidate, matching `CANDIDATE_CORPUS`, `test-suite-layout.py:474-480`).

**Live-config wiring confirmed** (`test-suite-layout.py:494` `test_kinds_cfg = repo_cfg["test_kinds"]`
— `repo_cfg` loaded from the real `.harness/harness.json` at line 102, not a copy — and passed
through to `hygiene_uncertified`/`select_control_candidate`/`offenders` at lines 507-530): this is
genuinely config-derived, not hardcoded, matching the plan's D-01 claim.

**Case-11 `INAPPLICABLE` disposition (c2's finding, `test-suite-layout.py:520-527`): I confirm the
prior judgment is correct.** The corpus currently DOES yield a qualifying candidate
(`.harness/tools/test_dir/gen.py`, reconfirmed above), so the behavioral positive control is live
today, not vacuous; the advisory risk is only that a future `test_kinds` change disqualifying the
whole `CANDIDATE_CORPUS` would silently reduce case 11's behavioral half without reddening
anything. Latent, non-gating — I do not judge this disposition wrong.

## 6. Test-first audit

Not re-run in full (already settled at c1: `notes/receipt-harness-backend-dev-T-01-c1.md` §1
records a genuine captured RED — `AttributeError: module 'suite_layout' has no attribute
'DOCUMENTED_EXCEPTIONS'`, exit 1 — before implementation, then GREEN after; this is evidence of
order, not just correctness). I did not find reason to doubt it.

## Worktree state

`HEAD` = `3379169a73ad11e20df931f0b7bccff1aa568672` (unchanged, one commit past the pinned
`9adbce6b`, the `feature.json` pin write per the shared context — not touched by me).
`git status --porcelain` at the repo root: empty (clean). `/tmp/bug1286_qa_probe` created and
deleted within this session; nothing tracked was read-then-written.

## DIGEST

```yaml
VERDICT: PASS
severity_max: med
must_fix: []
```

## Open questions

None blocking. QA-1 (toplevel-mismatch route untested) is worth a backlog entry alongside the
already-known F-1/F-2, but does not gate under `gates.review: advisory_unless_high` and does not
change `matrix_ok`.
