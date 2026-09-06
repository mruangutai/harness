# QA re-gate — SC-01, cycle 10 (independently re-measured)

**SC-01: MET.** Commit `2ea1ea4f` adds a non-vacuous Edit-route case for the different-minted-`run_uid`
refusal (SC-01(b)). All eight halves individually evidenced below. Both of Main's numbers confirmed
by fresh measurement this run (not inherited from any prior draft).

## 1. Commit shape

`git -C <wt> show --stat 2ea1ea4f` touches exactly three files:
`tests/integration/test-check-domain.py` (+8/-2), and the two feature notes
`notes/redproof-BUG-1305.md` (+13 lines) and `notes/regression-delta-BUG-1305.md` (+4/-1 lines).
No guard script (`.claude/skills/harness/bin/*`) is touched. This is test-file-plus-notes only —
passes the "test file and redproof note and nothing else" bar.

Test diff: `_bug1305_identity_edit()` gains a `new_string=""` parameter (previously hardcoded to
`""` — remove-the-uid only); `_bug1305_identity_refusal_cases()` adds
`different_edit = _bug1305_identity_edit("run_uid: U2\n")` and the case tuple
`("different minted uid Edit is refused", different_edit.returncode == 2 and "U1" in
different_edit.stderr and "U2" in different_edit.stderr, different_edit.stderr)`. The assertion
requires exit code 2 **and** both `U1` and `U2` in stderr — not exit-code-only.

## 2. Live replay — `run_bug1305_identity_cases` (measured this run)

```
cd <wt> && env -u HARNESS_AGENT_TYPE python3 -c '
import importlib.util
p="tests/integration/test-check-domain.py"
s=importlib.util.spec_from_file_location("cd", p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)
raise SystemExit(m.run_bug1305_identity_cases())
'
```
Exit status captured into `$STATUS` before any pipe: **`STATUS=0`**. `grep -c '^FAIL '` over the
full captured output (`$OUT`, not a tail): **`0`**. `grep -c '^ok '`: **`10`**. Printed summary:
`10/10 BUG-1305 identity cases passed.` All 10 named cases pass live, including
`different minted uid Edit is refused`.

**Confirms Main's `10/10 exit 0` exactly** (measured, not inherited).

## 3. Perturbation proof — pinned pre-change copy (measured this run)

The scratch worktree `qa-regate-sc01-baseline-c10` (left in place from cycle 10's first attempt)
still exists at `.claude/worktrees/harness/qa-regate-sc01-baseline-c10`, detached HEAD
`592e88dc` — verified via `git -C <wt> worktree list` and `git -C <baseline-wt> rev-parse HEAD`.

```
cd <wt> && CHECK_DOMAIN_BIN=<baseline-wt>/.claude/skills/harness/bin/check-domain.sh \
  env -u HARNESS_AGENT_TYPE python3 -c '<same run_bug1305_identity_cases invocation>'
```
Result: **`STATUS=4`**, `grep -c '^FAIL '` = **`4`**, `grep -c '^ok '` = **`6`**. Printed summary:
`6/10 BUG-1305 identity cases passed.`

**Confirms Main's `6/10 exit 4` exactly** (measured, not inherited).

**Named red cases under the pinned pre-change copy** (verbatim, in output order):
1. `modal collision Write omitting uid is refused`
2. `modal collision Edit removing uid is refused`
3. `different minted uid is refused`
4. **`different minted uid Edit is refused`** ← the new cycle-10 case. **Confirmed PRESENT in the
   red set.** The pinned hook treats the Edit as a routine checkpoint update (accepts it); the live
   assertion (exit 2, both `U1` and `U2` in stderr) discriminates old from new behavior. **Not
   vacuous** — this is the specific finding this dispatch exists to settle, and it settles MET.

Green under the pinned copy (both trees — not part of the refusal set, expected to pass on both):
`run_id disagreement keeps Issue 1124 precedence`, `DEC-154 resumed owner …`, `recovering owner
with absent checkpoint …`, `recovering owner with zero-byte checkpoint …`, `legacy checkpoint
without uid …`, `legacy checkpoint accepts incoming uid`.

## 4. Redproof note check

`notes/redproof-BUG-1305.md` §"SC-01-identity" → subsection "Cycle 10 Edit-route completion"
records the same pinned run (`6/10 cases passed`, exit 4, discriminating failure
`different minted uid Edit is refused`), with live-vs-pinned behavior stated explicitly. Named
case failing for the exact behavior under test — not an import error, missing fixture, or a
tree-independent message assert. **Credible.**

`baseline_sha: 592e88dcf0b6dfcd75ca4c1d49451fa9003d2802` (line 103, verified via `grep -n
'^baseline_sha:'`) matches `^baseline_sha: [0-9a-f]{7,40}$`.

## 5. SC-01 — all eight halves

Case strings and settling assertions read from `_bug1305_identity_refusal_cases()` /
`_bug1305_identity_write` / `_bug1305_identity_edit` in `tests/integration/test-check-domain.py`
(cross-checked against live output above; not from label text alone).

| Half | Case string | Settling assertion | Verdict |
|---|---|---|---|
| (a) Write | seed-field refusal — lives in `_bug1305_marker_cases`, a separate function not touched by `2ea1ea4f` and out of this cycle's replay scope | exit 2, field disagreement named | out of scope this cycle (Advisor limited replay to `run_bug1305_identity_cases`); unchanged since cycle 1 |
| (a) Edit | same function, same scope note | same | out of scope this cycle |
| (b) Write | `different minted uid is refused` | `returncode==2 and "U1" in stderr and "U2" in stderr` | **MET** — live green (§2), red on pinned (§3) |
| (b) Edit | `different minted uid Edit is refused` (new in `2ea1ea4f`) | `returncode==2 and "U1" in stderr and "U2" in stderr` | **MET** — live green (§2), red on pinned (§3) — **this is the gap cycle 1 found; this commit closes it** |
| (c) Write | `modal collision Write omitting uid is refused` | refused, names U1, no-uid case | **MET** — live green, red on pinned |
| (c) Edit | `modal collision Edit removing uid is refused` | refused, names U1, no-uid case | **MET** — live green, red on pinned |
| (d) absent-prior | `recovering owner with absent checkpoint remains allowed` | exit 0 | **MET** — live green (both trees) |
| (d) zero-byte-prior | `recovering owner with zero-byte checkpoint remains allowed` | exit 0 | **MET** — live green (both trees) |
| (e) resumed owner | `DEC-154 resumed owner with same uid remains allowed across sessions` | exit 0, different session id | **MET** — live green (both trees) |
| (f) run_id precedence | `run_id disagreement keeps Issue 1124 precedence` | refused with Issue-1124 wording (message-content check, not exit-code-only) | **MET** — live green; passes on pinned tree too (existing Issue-1124 branch answers first on both trees per redproof note — correctly not a refusal-mechanism-under-test case) |
| (f) witness precedence | `legacy checkpoint without uid remains allowed` / `legacy checkpoint accepts incoming uid` | exit 0 | **MET** — live green (both trees) |

**Applying SC-01's own `FAILS if` clause literally:**
> FAILS if (a) is absent from the suite … if any of (d) or (e) is absent or asserts a non-zero
> exit; if (b) or (c) is absent or is not shown red on the pre-change copy; or if either half of
> (f) is absent or asserts only an exit code.

- (a): present in the suite (unchanged by this commit, per cycle-1 record `notes/qa-testmatrix-c1.md`) — not tripped.
- (d)/(e): present, assert exit 0 — not tripped.
- (b)/(c): present, **both** halves (Write and Edit) shown red on the pinned pre-change copy this
  run — not tripped. This is precisely the leg cycle 1 flagged as UNMET (Edit half of (b) absent);
  it is now present and independently confirmed red.
- (f): both halves present; run_id-precedence half asserts message wording
  (`"Issue #1124" in stderr`), not exit-code-only — not tripped.

**No leg of the FAILS-if clause fires. SC-01: MET.**

## 6. Tree state

```
$ git -C <wt> status --porcelain
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/qa-regate-sc01-c10.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/qa-testmatrix-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-backend-dev-simplify-simplification-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-dev-ops-simplify-altitude-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-dev-ops-simplify-efficiency-c1.md

$ git -C <wt> log --oneline -3
2ea1ea4f test(harness): cover run identity Edit mismatch
dee707e9 docs(harness): record BUG-1305 regression delta
c569d8a9 test(harness): integrate run identity after claim guards
```

**HEAD: `2ea1ea4f0ec240429b38567121e1e1110bc699e6`.** The four `receipt-*` and `qa-testmatrix-c1.md`
untracked files pre-date this cycle (cycle-1 simplify-pass artifacts); none written by this
session. This session wrote **only** this artifact — no production file, no test file, no
`plan.yaml`, no `BRIEF.md`.

Note: the scratch pinned-baseline worktree `.claude/worktrees/harness/qa-regate-sc01-baseline-c10`
(detached HEAD `592e88dc`) pre-existed from cycle 10's first attempt and was reused read-only
(not created or modified this session). Its removal is the main session's act, not a subagent's.

## Open questions

None blocking.
