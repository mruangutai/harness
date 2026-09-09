# QA Gate — BUG-440 digest verdict reconciliation (c1)

review_sha: `2964cddbbfe465d1268cb12a248861d8a28e31a6`. Diff scope re-derived as
`772790be5..2964cddb` (the sha itself is a 4-line dedup commit; the feature's real diff spans four
commits back to the `main` merge-base).

## BLUF

**Matrix: PASS.** **T-01 verify: PASS.** **SC-06: PASS.** Test infrastructure is sound and the
implementation matches REQ-01..04 and SC-07 byte-for-byte. But **two of the three required mutants
escape the case undetected** (m2, m3) — the fixture proves the *comparison logic* fires correctly but
does **not** prove the finding is *blocking* (REQ-01) nor that it stays *silent on invalid digests*
(REQ-03d), because of two independent vacuities in the fixture, both confirmed by live mutation, not
inferred. Recommend **FAIL** on assertion completeness for SC-01 and SC-03(d); everything else holds.

## Matrix

- `change_type: bugfix` (plan.yaml T-01). `test_matrix.bugfix`: `unit if touches_runtime_code` (true —
  check-state.sh is runtime code) → **unit required**. `integration if
  fix_confined_to_tests_and_contract_docs` (false — the fix touches check-state.sh itself, not tests
  alone) → not obligated by this leg. `__bug_class__ if match_bug_class` — per this repo's own
  Expertise (G-08, repository tier), `match_bug_class` has no resolvable taxonomy entry in this project
  yet, so this leg is inert.
- The `integration` kind is *also* satisfied here independently: the diff's own test file lives at
  `tests/integration/**`, matching `test_kinds.integration.detect`, whose bound command is
  `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` (`harness.json:315`) — the standing
  per-kind command, not merely T-01's own scoped verify. I did not execute that full command (it would
  run the entire `tests/integration/**` bucket, outside this dispatch's scope); the scoped proof required
  by this dispatch — `python3 tests/integration/test-check-state.py` directly — is SC-06 below and is
  the changed surface's own file.
- **matrix_ok: true.** unit + integration both satisfied per the file changes and T-01's own verify;
  no kind is `cmd: null`/misconfigured for this diff.

## T-01 verify (carried verbatim from plan.yaml, cross-checked identical to dispatch)

All five conjuncts pass: `RESULT=0`.
```
grep1 ok / grep2 ok / grep3 ok / grep4 ok
ok - BUG-440 INV-37 reconciles digest verdicts without mutation
EXIT=0
```

## SC-06 (full file, scoped proof — the changed surface's own suite)

`python3 tests/integration/test-check-state.py`: exit **0**, 217 real output lines (218 captured
minus my own appended `EXIT=` sentinel), **0** lines beginning `FAIL`. Baseline at
772790be was 216 lines/51.9s; +1 line is exactly the new case's own `ok -` print, consistent with no
regression. Wall time **71.67s** (up from 51.9s baseline — not gated by SC-06's wording, informational
only; not itself a finding).

## SC-05 (red proof, read at the pinned sha, not the working tree)

`git show 2964cddb…:…/redproof-BUG-440.md` at the pinned sha carries the exact heading, the full pinned
`772790be…` sha, a `CHECK_STATE_BIN=` invocation, verbatim `FAIL -` output, and `RESULT: RED` at column 0.
**Judged genuine, not a stub**: I reran the identical invocation against a disposable copy of the
pre-change script mutated back toward m1 (below) and independently reproduced byte-for-byte the same
three lines (`runs/G` digest-missing VIOLATION, `runs/X/digest.md` contract VIOLATION, `run dir O`
orphan note) — this is exactly what the fixture emits when the INV-37 check does not exist at all, which
is what the pre-change script lacks. Not fabricated.

## SC-07 (tail-anchor semantics)

`check-state.sh:1546-1548` is byte-identical to `validate-digest.py:1155-1160` (`re.finditer(r"^\s*VERDICT:"...)`
→ slice from last match → `re.search(r"^\s*VERDICT:\s*(\S+)"...)`), cites those exact line numbers in a
comment, reuses `_dtext` already read for `validate()` (no second `open(dg)`), and the new region
(`check-state.sh:1519-1558`) contains **zero** literal occurrences of `PASS`/`FAIL`/`BLOCKED`/`ESCALATE`
— confirmed by direct grep. Satisfied.

## Non-vacuity — mutation results (isolated copy via `isolated_bin.py`, mutated, run via
`CHECK_STATE_BIN=`, never touching the live tree; `git status --porcelain` confirmed unchanged from
pre-probe baseline — the only diff was an unrelated peer's new note file)

| Mutant | Change | Expected | Actual | Verdict |
|---|---|---|---|---|
| m1 | `_dm.group(1) != _rv` → `False` (never report) | case returns False | **False** | case reddens correctly — the exact-equality comparison is load-bearing |
| m2 | move the finding from `bad.append` to `warn.append` (non-blocking) | case returns False | **True** (`code==1` still, from unrelated fixture violations on runs G/X) | **case does NOT redden — REQ-01's "blocking, not warning" clause is unbound by this test** |
| m3 | move the reconciliation block to run unconditionally after `if _errs:` (also fires for invalid digests) | case returns False | **True** | **case does NOT redden — REQ-03(d)'s "no second finding on an invalid digest" clause is unbound**, because fixture run X's invalid digest text (`"# digest\n"`) carries no `VERDICT:` line at all, so `_dm` is `None` and the moved block never emits regardless of where it's hung |

## SC-01 assertion quality (six-substring `all(...)` over the one `mismatch[0]` line)

Of the six tokens (`FEAT-TEST`, `M`, `FAIL`, `PASS`, `feature.json`, `digest.md`), **three cannot fail
structurally**, independent of the code under test:
- `"M"` — the line is already pre-filtered to `"runs/M" in line` before the token check runs, so `"M"`
  is guaranteed present by construction of the `mismatch` list itself.
- `"feature.json"` and `"digest.md"` — both are hardcoded literal filenames baked into the f-string
  template (`os.path.relpath(dg, H)` where `dg` is always named `digest.md`; the feature.json path is
  built with a literal `"feature.json"` join), not variable content the code could get wrong. They would
  appear in the message regardless of whether the code correctly identified *which* feature/run they
  belong to.
- `"FEAT-TEST"`, `"FAIL"`, `"PASS"` are real variable content (computed via `os.path.basename(_feat_dir)`
  and the two verdict values) and would fail under a plausible defect — **except** `"FAIL"`/`"PASS"`
  are order-blind: a code defect that swapped which verdict is reported as "digest" vs. "feature.json"
  (reversing the two `!r}` interpolations) would still pass both presence checks, since both literal
  words still appear in the string, merely transposed.

## SC-04 (before/after hash coverage)

`paths` = `[feature.json]` + every `digest.md` found via `os.walk` under `runs/` at fixture-build time
(6 entries: M, E, N, I, X, O — G correctly has none, since no file exists to hash). `before == after` is
a straightforward whole-dict comparison that would fail on any single-byte mutation to any covered file.
Confirmed check-state.sh's new region contains no `open(..., "w")`/write call anywhere (grepped). Sound.

## Per-SC resolution

| SC | State | Evidence |
|---|---|---|
| SC-01 | **satisfied, with a reported gap** | case passes; 3/6 substring assertions are structurally non-discriminating (see above); REQ-01's blocking-vs-warning distinction is NOT independently proven (mutant m2 escapes) |
| SC-02 | satisfied | `clean_ok` sub-check, exit 0, no `INV-37` in output — no complication found |
| SC-03 | **satisfied for (a)(b)(e); gap on (d)** | `no_new`/`existing` sub-checks genuinely bind (a) host-not-lead, (b) not-complete, (e) unclaimed-orphan, and (c) missing-digest; (d) invalid-digest's "no second finding" is unproven against a digest that fails validation but DOES carry a well-formed `VERDICT:` line (mutant m3 escapes — the only invalid-digest fixture entry has no `VERDICT:` line at all, so the discriminator can never fire either way) |
| SC-04 | satisfied | before/after sha256 dict compare, full coverage, no write path exists in the new code |
| SC-05 | satisfied | genuine captured red run at the pinned sha, reproduced independently |
| SC-06 | satisfied | exit 0, 217/218 lines, 0 FAIL lines, +1 line exactly accounted for |
| SC-07 | satisfied | byte-identical tail-anchor regex + comment citation, digest text reused, no restated verdict-token list |

## Coverage gaps (concrete inputs that would slip through)

1. **REQ-01 blocking-vs-warning is unproven.** A code change that filed the INV-37 finding into `warn`
   instead of `bad` would ship green through this suite, because the fixture's other two entries (G:
   missing digest, X: invalid digest) already force `code == 1` for unrelated reasons. A fixture with
   **only** the mismatching run M (no G, no X) would close this gap and force `code` to depend
   exclusively on INV-37's bucket.
2. **REQ-03(d)'s "no second finding on invalid digest" is unproven for a digest that has a VERDICT
   line but still fails `validate("lead", ...)`.** Concrete input: a digest text with `VERDICT: FAIL`
   present but missing a required schema field (e.g., no `DIGEST:` block) — that still fails
   `validate()` (existing INV-15 violation fires) while carrying a real, matchable verdict line. Under
   the current test, run X's invalid text (`"# digest\n"`) has no `VERDICT:` line at all, so a
   regression that (incorrectly) also reconciles on invalid digests is invisible to this suite.
3. SC-01's `"M"`/`"feature.json"`/`"digest.md"` tokens add no assertion strength beyond what the
   pre-filters already guarantee; not a functional gap, but padding that should not be counted as three
   of "six separate substring assertions" per SC-01's own wording.

## Recommendation

Both gaps are fixable by adding two run entries to the mismatch fixture in `case_bug440_digest_verdict_reconciliation()`
(one isolated mismatch-only tree to close gap 1, one "invalid digest that still names a VERDICT" entry to
close gap 2) — small, additive, no change to check-state.sh needed. This is dev/qa build work, not a
design question; opening as a blocking finding rather than an open_question since it is cheap and
reversible (test-only).
