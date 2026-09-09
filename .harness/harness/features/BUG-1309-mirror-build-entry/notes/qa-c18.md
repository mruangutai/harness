# QA c18 — SC-04 gap evidence measurement

## BLUF
All three SC-04 gaps are CLOSED by measurement. Full suite: 36 `ok`, 0 `FAIL`, `ALL PASSED`,
`rc=0` (captured via `out=$(...); rc=$?`, never a pipe). T-05's full `verify:` block, quoted
verbatim from `plan.yaml:1062-1073` and byte-diffed against the dispatch's quote (identical),
runs to `VERIFY-PASS`, `rc=0`. Gap A and Gap C cases discriminate cleanly. **Gap B discriminates
only under a forced glob ordering that the real filesystem never produces for these two
directory names** — reported below as a genuine, narrower finding, not a fabricated pass.

## 1. Full run at the pin
```
out=$(python3 tests/integration/test-merge-gate.py); rc=$?
```
`rc=0`. `OK_COUNT=36`, `FAIL_COUNT=0`. Final line: `ALL PASSED`.
`git diff --stat 9fe5cf3112aed6782dfe3f1833b5e7077b31d953^..9fe5cf3112aed6782dfe3f1833b5e7077b31d953`
confirms the complete file set under review is exactly
`tests/integration/test-merge-gate.py | 38 +++++++++++++++++++++++++++++++++++-` (+37/-1),
no production file touched this cycle.

## 2. Discrimination, per gap (mutation on scratch copies under `/tmp/qa-c18-scratch`, never in-tree)
Production code is unchanged this cycle, so "pre-change production copy" is byte-identical to
the pin — no discrimination there. Used PRED-1/3's own sanctioned alternative: a temporary
mutation of the production path under a temp root. Built a scratch bin
(`merge-gate.sh`+`.py`, `feature_schema.py`, `harness_boundary.py`, `run_identity.py`,
`harness_yaml.py`) and confirmed it faithfully reproduces the pin (baseline: all three named
cases `ok` against the unmutated scratch copy, via `HARNESS_PROJECT_DIR` override, whose
`MARKER` resolution is read by `harness_boundary.resolve_root`).

- **Gap A — CONFIRMED discriminating.** Mutating the deny message to drop `{feat}`/`{command_line}`
  (`deny("merge-gate: a Build entry receipt is owed, so this merge is denied.")`) reddens
  `T-05 non-era absent build_entry denies naming feature and re-run command` (`FAIL`, rc=1).
- **Gap C — CONFIRMED discriminating** (single combined case, all four fixtures present).
  Mutating away the `chmod 0` exception, breaking `os.chmod` protections, reddens the case: `FAIL`, rc=1.
- **Gap B — CONFIRMED discriminating, but narrower than the claim.** Hoisting the era-exempt
  allow above `len(owners) > 1` reddens the case **only when `owners[0]` is the era-exempt
  record**. See §3 for the measured glob-order dependency; PRED-3's "on either glob order"
  claim is REFUTED as literally stated on this host (below), CONFIRMED in effect (the case does
  catch the ordering defect the moment that branch is exercised).

## 3. Gap C reachability (PRED-1, PRED-2) — all four arms individually proven reached
Removed each arm from a scratch copy, one at a time, keeping the other three intact, and ran
against the shipped four-fixture case:
| Arm removed | Result | Failure text |
|---|---|---|
| `OSError` from the catch tuple | **FAIL** (case reddens) | outer `except Exception` deny: "could not evaluate this feature's Build-entry receipt" |
| `json.JSONDecodeError` from the catch tuple | **FAIL** | same outer-catch deny |
| `isinstance(document, dict)` test | **FAIL** | same outer-catch deny (`AttributeError` on `list.get`) |
| `document.get("branch") == branch` equality | **FAIL** | ambiguity deny: "claimed by more than one feature record (FEAT-9001-fixture-non-era, FEAT-9005-different-branch)" |

**All four proven reached.** (Not "four proven, one unproven" — genuinely four for four.)

PRED-2, measured: process is not root (`uid=501(molchairuangutai)`, `whoami` = non-root user).
`open()` on the `chmod 0` fixture genuinely raises `PermissionError: [Errno 13] Permission
denied` for this user (measured directly). **However**, the shipped `chmod 0` fixture's content
is `json.dump({})` — no `branch` key — so it is a **non-claiming** record: even if `open()`
succeeded, `document.get("branch") == branch` would be `False` and the record would be ignored
anyway. Built a stronger "flip" fixture whose unreadable record's content *would* claim
`feature/test` if read (`{"branch": "feature/test", ...}`, still `chmod 0`): production ALLOWS
it (decision `None` — the `OSError` arm alone protects it, sole real owner wins); the
no-`OSError`-catch mutant DENIES it (`could not evaluate...`). This confirms the OSError arm is
load-bearing on its own **only against the stronger fixture** — the shipped fixture binds it
solely as a side effect of the combined four-fixture case (which the arm-removal proof above
already establishes is reached), not standalone. Worth a coverage note, not a gap: the arm IS
proven reached; a future single-kind fixture would bind it more tightly.

## 4. Matrix, PRED-4, and the full verify block
`change_type: feature` (`plan.yaml:1046`) obligates `unit` + `integration` always (no `ui`
predicate fires — no interaction flow). This cycle's own diff is one integration test file
(`tests/integration/test-merge-gate.py`), satisfying `integration` on its own; `unit` is
satisfied cumulatively by the feature's standing `tests/unit/test-omp-hooks.py`, which T-05's
own `verify:` still runs (56 pass / 0 fail, bun test). **`matrix_ok: true`.**

Ran the full T-05 `verify:` block exactly as quoted in the dispatch — cross-checked byte-for-byte
against `plan.yaml:1062-1073` via a Python substring diff (`MATCH: True`, no drift). Result:
`LOOP-PASS` → `HOOKS-PASS` (56/56) → `SETTINGS-PASS` (`all 9 prerequisites present (8 hooks`) →
`grade=4` → `VERIFY-PASS`, `rc=0`.

**PRED-4 CONFIRMED.** The Gap A case was renamed to a longer string
(`"...denies naming feature and re-run command"`), while the `verify:` block's `for n in (...)`
still carries the short name (`"T-05 non-era absent build_entry denies"`). `grep -qF "ok    $n"`
is a substring match on `$out`'s lines; the actual output line
`ok    T-05 non-era absent build_entry denies naming feature and re-run command` *starts with*
the short substring, so it matches. Measured directly: the full loop reported `LOOP-PASS` with
no `MISSING:` line for any of the 26 enumerated names.

## 5. Three UAT-relevant denial forms (measured against the production gate at the pin)
All three deny, `rc=0`, `decision='deny'`, naming `FEAT-9001-fixture-non-era` and the
`gh-sync.py open <dir>` re-run command — exercised by `tests/integration/test-merge-gate.py:219`,
`:220`, `:221` respectively (loop at `:218-226`):
- `git merge -F /tmp/message feature/test` → deny.
- `git merge --cleanup strip feature/test` → deny.
- `git --attr-source HEAD merge --no-ff feature/test` → deny.

## PRED-5 — fixture isolation, CONFIRMED
`fixture()` (`test-merge-gate.py:22`) calls `tempfile.mkdtemp()` fresh on every invocation, so
every case — including the Gap C noise root — gets a distinct OS-level directory; the full
36/36-clean run is itself the empirical evidence: any leaked noise from the Gap C root would
have flipped a later "allows" case (e.g. `T-05 single owner plus unrelated malformed record
still allows`) to a false deny, and none did.

## Worktree state
Ran `git -C <worktree> status --porcelain` at the end of this run. It is **NOT empty**:
```
 M .harness/harness/features/BUG-1309-mirror-build-entry/feature.json
?? .harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-code-reviewer-c18.md
?? .harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-ui-reviewer-c18.md
```
None of these three paths were touched by this QA run — I made zero edits inside the worktree;
every mutation/probe lived under `/tmp/qa-c18-scratch`, which has been deleted
(`rm -rf /tmp/qa-c18-scratch`, confirmed). These three entries are concurrent sibling validator
artifacts (`C18CodeReview`, `C18UI`) writing in the same shared worktree during this dispatch —
flagging rather than silently absorbing per the acceptance contract.

## Coverage gaps / findings
- Gap B's ordering fix is real and the case DOES catch it when exercised, but the shipped
  fixture's assurance is glob-order-dependent (see §2/§3) — on this host `glob.glob` returns
  `FEAT-9001-fixture-non-era` before `BUG-1030-stale-anchor-write-hazard` regardless of
  directory-creation order (tested both orders directly), so the natural CI run only ever
  exercises the "accidentally correct" mutant branch. This is a coverage-robustness note, not a
  code defect — production's real ordering guard (`len(owners) > 1` fires purely on count, never
  on `owners[0]`'s identity) is provably order-independent by inspection of `main()`
  (`merge-gate.py:167-181`); only a *mutant that inverts that guarantee* is order-sensitive to
  catch, and this fixture set doesn't force the adversarial order.
- Gap C's `chmod 0` fixture is weaker than its own clause implies (non-claiming content); the
  arm is still proven reached via the combined-fixture removal proof, so no code or plan defect
  follows — noted for calibration only.
