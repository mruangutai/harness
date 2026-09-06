# QA Gate — BUG-1304 — build diff b64b2d53..6dd081a1

**Verdict: PASS.** Suite is green at baseline discovery count, test-first ordering holds by
file-touch inspection, SC-06's discrimination helper asserts both required halves at every call
site, and the FEAT-51 narrowing (DEC-218) left the sibling fail-open assertion intact.

## Matrix

Live tasks: T-01…T-06, T-09 = `logic`; T-07 = `docs`; T-10 = `scaffolding` (T-08 struck). Matrix
floor for `logic` is `unit` only (`.harness/harness.json:157-161`); `docs`/`scaffolding` require
nothing. No `cross_module`/`config`/`api` task in this plan, so no extra kind is obligated.

| kind | state | cmd | evidence |
|---|---|---|---|
| unit | **satisfied** | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind all` | rc=0; below |

`matrix_ok: true`.

## 1. Suite actually runs and can report red

```
env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind all > /tmp/bug1304-unit.log 2>&1; rc=$?
```
`rc=0`. `grep -c '^FAIL ' /tmp/bug1304-unit.log` → **0**. `grep -c 'checks passed' /tmp/bug1304-unit.log`
→ **20**, matching the baseline of 20 exactly (no discovery-count drop, no silent coverage
collapse). `HARNESS_AGENT_TYPE` was unset per repo Expertise G-07 to avoid the plan-merge phantom
regression.

## 2. Test-first ordering (git log + git show --stat, b64b2d53..6dd081a1)

Chronological order (oldest first): `da37f082`(test) → `81a66bb3`(fix) → `a4e8ecf7`(fix, T-09
prep) → `5a106acd`(test) → `5facdf5e`(test) → `83d17657`(fix) → `fb762215`(fix) → `ad67d22b`(test)
→ `62e5bf6d`(fix) → `7a9c3cb4`(docs) → `6dd081a1`(docs).

- `da37f082` touches only `tests/integration/test-inflight-registry.py` +
  `tests/unit/test-harness-boundary.py` (tests-only); precedes `81a66bb3`, which touches only
  `harness_boundary.py` + `inflight_registry.py` (impl-only). **T-01 before T-02: holds.**
- `5a106acd` touches only the fixture + `tests/integration/test-check-domain.py` (tests-only);
  `5facdf5e` touches only the fixture + `tests/integration/test-bash-write-guard.py`
  (tests-only). Both precede `fb762215` (impl-only, `bash-write-guard.sh`) and `62e5bf6d`
  (impl-only, `check-domain.sh`). **T-03/T-05 before T-04/T-06: holds.**

Ordering holds on all four pairs named in the dispatch, by file-touch inspection alone (no
implementation file appears in any test-labeled commit or vice versa).

## 3. New assertions discriminate (SC-06)

`bug1304_assert_pre_change_allows` call-site counts (grep count minus the `def` line itself):
`tests/integration/test-check-domain.py` → 11 matches − 1 def = **10**; `tests/integration/test-bash-write-guard.py`
→ 13 matches − 1 def = **12**. Matches the required 10/12 exactly.

Both definitions (`test-check-domain.py:4429-4443`, `test-bash-write-guard.py:986-1001`) combine
into one boolean `ok`/result tuple:
- half (a): `not any(marker in stderr for marker in ("enforcement OFF", "was not enforced",
  "passing through"))` — the frozen guard's stderr carries none of the fail-open phrases.
- half (b): a positive control fired at the *same* frozen guard in the *same* isolated bin
  (`control = _bug1304_fire(root, ".harness/forbidden/positive-control.md", agent, hook=prior)` /
  `_bug1304_bash_fire(root, f"echo controlled > {control_path}", agent, guard=prior)`) still
  returns exit 2.

Every one of the 10 + 12 call sites routes through this single helper, so no call site can satisfy
SC-06 on an exit code alone. **SC-06 holds as written.**

## 4. FEAT-51 narrowing (`ad67d22b`, DEC-218) is sound

`_feat51_fail_open_cases` (`test-check-domain.py:3953-3976`):
- The directory-at-registry-path (`raising`) case now asserts `fired, 2` (fail-**closed**,
  line 3960-3963), per the binding Advisor ruling recorded in DEC-218/STATE.md.
- The sibling `unimportable` case (`test-check-domain.py:3972-3975`) — quarantine machinery's own
  fail-open on an unimportable `inflight_registry.py` — still asserts **exit 0** ("boundary was
  not enforced"), and the comment at line 3961-3962 explicitly says the quarantine fail-open
  "stays pinned by the unimportable case below." Only one of the two FEAT-51 cases was narrowed;
  the live fail-open assertion was not removed.

## Notes

- `cycles_used: 0` — clean first-pass gate run, no repairs made or requested.
- No code, test, fixture, hook, or gate script was edited; read/run/grep only.
