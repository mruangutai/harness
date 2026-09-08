# QA gate — review-c5 — BUG-1309-mirror-build-entry @ 473d82cb (gate-only re-run)

## Verdict: FAIL — matrix_ok: true, suite: pass, failures: 0, but two reproduced live defects in the sentinel's scoping

The standing matrix and every named suite are green (see below). The finding that fails this
cycle is **not** a suite failure — it is a reproduced behavioral defect in `feature_for`'s new
`unusable` sentinel that no case in the 19-case suite exercises, found by hand-building the
combinations the suite's pair-binding table shows are absent.

## Change type and required kinds

Diff at this pin (`473d82cb`, single commit): `.claude/skills/harness/bin/merge-gate.py`
(+13/-5) and `tests/integration/test-merge-gate.py` (+6). `change_type: bugfix`
(`.harness/harness.json:203-219`): `always: []`; `unit if touches_runtime_code` fires
(merge-gate.py is production code) → **unit required**. `integration if
fix_confined_to_tests_and_contract_docs` does NOT fire (production file changed). `__bug_class__`
is the known-unresolvable placeholder (repo Expertise G-08) — contributes nothing. Consistent with
cycle 4's finding, qa adds **integration** above the floor because the fix's only regression
evidence lives in `tests/integration/test-merge-gate.py`, the file the diff itself changed.
Required kinds: **unit, integration**. `matrix_ok: true`.

The full feature diff (`merge-base main HEAD` = `6ad7233f`) is far broader (new `merge-gate.py`,
`feature_schema.py`, `gh-sync.py` changes, `post-merge-sweep.sh`, `check-state.py` etc.) but this
cycle's own commit is the only content difference from the prior pin, per the assignment's
gate-only scope.

## Per-kind results — observed exit codes and case counts

| kind | command | exit | discovered |
|---|---|---|---|
| integration (targeted) | `python3 tests/integration/test-merge-gate.py` | 0 | **19 ok**, `ALL PASSED` (matches assignment's expected 19) |
| integration (targeted) | `python3 tests/integration/test-gh-sync.py` | 0 | 322 `ok`, 0 `FAIL` |
| integration (targeted) | `python3 tests/integration/test-post-merge-sweep.py` | 0 | 61 `PASS` lines, 0 real `FAIL` (grep hits on `FAIL` are substrings inside passing assertion names — `FAILED IS NOT SUCCESS` etc.) |
| integration (targeted) | `python3 tests/integration/test-check-state.py` | 0 | 225 `ok`, 0 `FAIL` |
| unit (targeted) | `python3 tests/unit/test-omp-hooks.py` / `bun test tests/unit/omp-hooks.test.ts` | 0 | `56 pass / 0 fail / 100 expect()` |

No command run over an empty discovered set; every count is corroborated by named-case totals, not
bare exit codes.

## Pair-binding table — all 19 cases against the four states

`(a)` healthy + unrelated-malformed → ALLOW · `(b)` matched-but-unevaluable (empty plan) → DENY
naming it · `(c)` target branch's only record unusable → DENY + repair · `(d)` gh-read failure,
branch owes nothing → ALLOW + DEC-138 stderr.

| # | case (test-merge-gate.py) | binds |
|---|---|---|
| 1 | L64-65 recovery-required denies | none (generic owed-receipt deny) |
| 2 | L66-67 non-era absent build_entry denies | none |
| 3 | L68-69 unpinned repo denies naming config fix | none |
| 4-6 | L70-73 opened / not-applicable / recovered-terminal allow (×3) | none (no `failure`, so line 148's allowed-entry branch never touches the `d` message path) |
| 7 | L74-76 sync false allows | none |
| 8 | L77-79 branch matching no feature allows | none — *baseline* for `(d)` (`document=None, unusable=False, failure=None`); no malformed record present |
| 9 | L80-81 non-merge command allows | none |
| 10 | L82-87 path-prefixed gh detected | none |
| 11 | L88-89 bash -c wrapped detected | none |
| 12 | L90-92 era-exempt absent allows | none |
| 13 | L93-96 era-exempt recovery-required allows | none |
| 14 | L97-101 unresolvable gh falls back, denies locally owed | none (matched record wins via `local_branch` fallback; generic deny, `failure` unused) |
| 15 | L102-112 gh outage, no matching feature, allows | **(d)** singly |
| 16 | L113-117 gh outage, feature owing, denies | none (matched + entry-not-allowed path ignores `failure`) |
| 17 | L118-123 empty plan fails closed | **(b)** singly |
| 18 | L124-131 unrelated malformed does not block healthy | **(a)** singly |
| 19 | L132-137 unusable target record fails closed | **(c)** singly |

**Every one of the four states is bound by exactly one case, and no case binds a pair.** In
particular the two pairs cycle 4 flagged as reasoned-but-untested — `(a)+(c)` and `(b)+(c)` — are
still untested by name at this pin; cycle 4 hand-verified both held clean *at `af132780`*, where a
non-dict record was silently `continue`d with no sentinel at all. That code has since changed:
`473d82cb` gives non-dict records a persistent, scan-wide side effect (`unusable = True`), and
re-verifying those same two pairs at the new code was this cycle's job — not a restatement, because
the code they exercise is not the code that was checked (per G-06: a full rewrite invalidates a
prior cycle's proof even where the file name is unchanged).

## Reproduced: the pairing IS live, and it inverts case 15's outcome — `(d)` interacting with an unrelated malformed record

`feature_for`'s `unusable` flag is set by scanning **every** `feature.json` under `.harness/*/features/*/`,
not just records relevant to the branch being merged (`merge-gate.py:106-108`). `main()` checks
`if unusable: deny(...)` **before** it checks `elif failure:` (`merge-gate.py:138-141`), so `unusable`
takes priority regardless of whether the malformed record has anything to do with the branch under
test.

Reproduced by hand (root not in the repo, `/tmp`, not committed): took case 15's exact fixture
(branch mismatch → `document=None`, gh binary broken → `failure` set) and added one **entirely
unrelated** `FEAT-9003-unrelated-malformed/feature.json = []` alongside it.

- **Control** (case-15 shape, no unrelated record): `merge-gate.sh` on `gh pr merge 7` with a
  broken `GH_BIN` → stdout empty (no decision), stderr `merge-gate: could not verify this merge -
  ... allowing it, because GitHub is a mirror and never a gate (DEC-138).` — matches case 15.
- **With the unrelated malformed record added**: same command, same broken `GH_BIN`, **same target
  branch mismatch** → stdout now `{"...": "deny", "...": "merge-gate: could not evaluate a
  feature's Build-entry receipt, so this merge is denied. Repair the malformed feature record and
  re-run the merge."}`, stderr empty.

Adding a feature.json that is *unrelated to the branch under merge, and unrelated to the GitHub
outage* flips an intended ALLOW (DEC-138: "GitHub is a mirror, never a gate") into a DENY, and the
denial message names no feature at all (`deny()` at `merge-gate.py:139` is a static string — it
does not interpolate `feat`, unlike the exception-path denial at line 160). Any project that
accumulates even one stale/corrupt `feature.json` anywhere in its tree (crash mid-write, manual
edit, an abandoned feature's leftover state) now blocks **every** merge that either targets a
branch with no feature record or hits a GitHub read failure — project-wide, unrelated to the
merging branch. This is a materially larger blast radius than case 18's already-settled posture
(which only protects a HEALTHY match's own merge, via `feature_for`'s early return hard-coding
`unusable=False` on a match). This is a *different* failure mode from the settled "bystander
lockout" (that one protected the matched-and-healthy posture; this one is the no-match-at-all and
gh-outage postures, which have no such protection).

## Second, independent reproduction: the sentinel does not fire for a genuinely corrupt (unparseable) record — case 19's own posture escapes

`merge-gate.py:101-108`:
```
except (OSError, json.JSONDecodeError):
    continue
if not isinstance(document, dict):
    unusable = True
    continue
```
Only the *parses-fine-but-wrong-type* branch sets `unusable`. A record that fails to parse at all
(`OSError`/`JSONDecodeError`) is silently skipped with **no** sentinel set. Case 19's fixture
writes `json.dump([], f)` — valid JSON, wrong type — so it only ever exercises the second branch.

Reproduced by hand: same fixture as case 19 but the *target branch's own* `feature.json` is
literally malformed JSON (`"{ this is not valid json"`) rather than a validly-parsed list. Ran
`merge-gate.sh` on `git merge feature/test` for that branch: **stdout empty, stderr empty — the
merge is silently ALLOWED.** This is exactly the failure mode `473d82cb` was written to close (a
malformed record for the merging branch's own feature must fail closed with a repair action), and
it is open again for the sub-case the fix's own test never constructs. This is not a hypothetical
mutant — it is the natural real-world shape of corruption (a truncated write, a crash mid-`json.dump`)
that `except (OSError, json.JSONDecodeError)` exists to name, and it is the one code path the fix
left un-instrumented.

## Adequacy of the two new cases (item 4)

- **Case 17 (empty plan, state `b`)**: covers only a completely empty `plan.yaml`. A bug that
  changed `recovery_command_for` to swallow its own exception and return a plausible-looking
  default command string instead of raising would not be caught — the outer `except Exception` at
  `merge-gate.py:159` would never fire, and the merge would deny with the generic "no receipt
  exists" message rather than the "could not evaluate" message, silently losing the distinction
  the case exists to prove. The case also never varies *which* malformed shape breaks evaluation
  (valid-YAML-non-dict `plan.yaml`, e.g. a bare list or `null`, versus zero bytes) — a regression
  narrowing the exception's trigger to file-length-zero specifically would escape.
- **Case 19 (unusable target, state `c`)**: as demonstrated above, escapes completely for a
  genuinely unparseable `feature.json` on the branch's own record — the fix's `unusable` flag is
  reachable only through the `isinstance(document, dict)` check, never through the
  `except (OSError, json.JSONDecodeError)` path four lines above it.

## Findings — not restatements of any settled item

1. **[FAIL, reproduced]** `unusable` is scoped to the entire glob scan, not to the branch under
   evaluation; combined with the `if unusable: ... elif failure:` ordering in `main()`, an
   unrelated malformed `feature.json` anywhere in the tree converts an intended DEC-138 ALLOW
   (no-match or gh-outage postures) into an unnamed DENY. `merge-gate.py:106-111,138-141`.
2. **[FAIL, reproduced]** `except (OSError, json.JSONDecodeError): continue` at `merge-gate.py:104-105`
   never sets `unusable`, so a genuinely corrupt (not merely wrong-typed) `feature.json` for the
   *merging branch's own* feature silently ALLOWS the merge — the exact defect class `473d82cb` was
   written to close, reopened for unparseable JSON specifically. `merge-gate.py:101-108`.

Both are new: distinct in location and precondition from the four settled items (gh_head OSError
fail-open, era-bypass-on-absence, fail-open-on-internal-error, bystander lockout, silent-allow on
an unusable target) and from the routed-but-non-gating items (uninterpolated "this feature",
missing branch-uniqueness, backlog items). Finding 1 interacts with the non-deterministic-glob
backlog (B-7) only in that either malformed record anywhere could be "the one" scanned first, but
the bug does not depend on ordering — `unusable` is a monotonic OR over the whole scan, so ordering
is irrelevant to reproducing it, which is itself worth recording: this is not a race, it is
unconditional.

## SC evidence

No success criterion in this feature's BRIEF is being goal-checked this cycle (gate-only dispatch);
this note supplies qa's gate result for the panel, not an SC-by-SC audit.

## Files touched

Exactly this note. No source, fixture, or test file was created, edited, or committed; all
reproductions ran against disposable `/tmp` directories outside the tracked tree and are gone.
