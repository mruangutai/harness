```yaml
VERDICT: FAIL
DIGEST:
  headline: "Q1 settled — the no-truncating-write property IS pinned, exactly once, in test-harness-merge.py's case6; (b) confirmed exact at 1; (c) confirmed executed, structurally impossible to violate; (e)'s three call sites do NOT uniformly redden — only 1 of 3 does, and the docstring's own explanation of why the other two are vacuous is independently confirmed; matrix is green and the cycle-0 environmental failure no longer reproduces."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 457 }
    - { kind: integration, state: satisfied, cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 581 }
  coverage_gaps:
    - "test-omp-hooks.py is now wired into UNIT_SCRIPTS by this diff (run-unit-tests.sh changed) — cycle 0's 'TS suite has no standing execution path' gap is closed. Confirmed by diff and by the unit-kind run's exit 0 covering it."
    - "e-probe: two of test-validate-feature-json.py's three scanned_count() call sites (lines 347, 383) are vacuous against a last-digit/substring-style regression, and will stay vacuous as long as their own fixtures produce a literal count of exactly 1 — only line 372 (the real-repo scan, currently 41 files) is sensitive to this class of bug, and only because 41 happens to end in the digit 1. This is not a defect introduced by the diff; it is inherent to comparing against a fixed literal '1' with tests whose real value is always exactly 1. Reported per O-03 as reasoned-plus-measured, not closed."
    - "scanned_count() silently returns None (never raises) for absent/empty/garbled stderr. Because one of its three call sites asserts count != 1, a sweep that crashes before printing any '— N file(s)' line makes that assertion vacuously PASS (None != 1) instead of failing loudly. Not exercised by any existing test."
  sc_evidence: []
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/review-harness-qa-c1.md
  expertise_update: []
artifact: .harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/review-harness-qa-c1.md
```

# QA gate — BUG-1030-stale-anchor-write-hazard @ fbaa7fec (cycle 1 re-dispatch)

**Gate-only, read-only on source (DEC-174).** No test/fixture/source authored in the worktree.
All mutation proofs ran against scratch copies outside the worktree (`/tmp/qa-scratch-*`, all
deleted after use). `git status --porcelain` shows zero writes of mine in the worktree besides
this note.

This is a re-dispatch of the c1 run that executed but never wrote its artifact. Its measurements
are gone; everything below was re-executed fresh, this run, against `fbaa7fec`.

## (d) — Q1, SETTLED, executed

Scratch: full copy of `.claude/skills/harness/bin/` to `/tmp/qa-scratch-1030/bin`.

**Baseline** `test-harness-merge.py`: **18/18 pass** (matches cycle 0's number).

**Mutant** (Python rewrite, not sed): `locked_update`'s `tempfile.mkstemp` +
`os.fdopen(fd,"wb")` + `os.replace` block replaced with a bare `open(path, "wb")` — the exact
truncating-open shape this feature exists to eliminate.

**Result: exactly 1 case reddens** — `case6: no torn read observed by concurrent reader`
(assertion failed; reader observed the mid-write truncated/zero-length state). All 17 other
cases stayed green, including `case6`'s two siblings ("reader observed at least one read",
"reader observed both the short and long body"), which don't target truncation specifically.

**Answer to Q1, plainly: the "no truncating open, no partial file" property IS pinned
effectively, in exactly one place — `test-harness-merge.py`'s `case6` — and nowhere else in the
suite.** No other test in either the unit or integration kind exercises `harness_merge.locked_update`'s
write mechanics under concurrency; every `feature.json` caller test (`test-feature-json-merge.py`,
`test-factory-decompose.py` case_22, etc.) verifies *routing to* `locked_update`, never
`locked_update`'s own atomicity — so this one case is the sole guard against a regression to the
original hazard, and it is real (mutation-confirmed, not just present).

Mutation reverted; scratch confirms 18/18 restored; `/tmp/qa-scratch-1030` deleted.

## (b) — confirmed exact

`.omp/extensions/harness-hooks.ts` line 845 condition
`toolName === "edit" && extractEditPaths(input.input).length === 0` replaced with `if (false)`.

Scratch: mirrored relative structure (`.omp/extensions/harness-hooks.ts` +
`.claude/skills/harness/bin/omp-hooks.test.ts` + its two `.fixture.jsonl` files +
`.agents/skills/harness/bin/check-domain.sh`, since `gatePath`/`gateRoot` resolve relative to the
module's own file location) — bare copies without this mirroring gave a false environmental
failure (`gatePath` test), caught and corrected before trusting the mutant result.

Baseline in scratch: **51/51 pass** (matches the real worktree's `python3 test-omp-hooks.py`: 51/51).

Mutant: **exactly 1 test reddens** — `OMP task lifecycle adapter > a non-string patch spawns no
gate, and SAYS SO (S2)` — with a `TypeError: undefined is not an object (evaluating
'result.content')`, i.e. the advisory notice never got attached because the branch never fired.
**Exact.** Matches the commit's claim of 1. Reverted; 51/51 restored.

## (c) — executed

Drove the real module directly (not the test file's own assertion) via a standalone script:
`registerHarnessHooks` with a `PolicyRunner` that always returns `{ blocked: false }` (so
`postDomain`'s `reason` is guaranteed falsy), then called `tool_result` for an `edit` with a
non-string patch (zero-path extraction, the S2 trigger). Result:
```
result: {"content":[{"type":"text","text":"Harness: no target path could be extracted..."}]}
has isError key: false
```
**Executed, not merely reasoned**: `isError` is genuinely absent from the returned object.

Additionally structurally confirmed why no path can ever violate this: `postDomain`'s edit branch
is `extractEditPaths(input.input).map(...)` — the identical extraction S2 gates on. When S2's
condition fires (extraction is empty), `postDomain`'s `.map()` also runs over the same empty
array, so `reason` (line 856, the sole source of `isError: true` at line 865) is provably
`undefined` in every case where the S2 advisory is set. The two are not merely tested as disjoint
— they're arithmetically forced disjoint by sharing the same zero-length array. Advisory-only
composition (line 861) has no `isError` key at all, by construction. This holds under the reworded
notice text exactly as it held under the old text (cycle 0 already reasoned this pre-rework); this
run adds the live execution cycle 0 didn't.

## (e) — measured, and the count is 1, not 3

**Naive scratch copy first gave a false result** (all 3 sites passed under mutation) because
`discover_paths()`'s root resolution derives from the *production* `validate-feature-json.py`'s
own file location, and a bare-copy scratch has no real `.harness/*/features/*/` tree to scan — so
the "real repo root" subtest scanned 0 files instead of this checkout's real 41, and the mutation
was invisible. Corrected by pointing the scratch test's `BIN_DIR`/`VALIDATE_CLI` at the **real,
unmodified** `validate-feature-json.py` in the worktree (invoked read-only as a subprocess, exactly
as the real gate does) while keeping the mutated `test-validate-feature-json.py` in scratch.

Baseline (this corrected scratch): **ALL PASS**, confirms live scan finds `41 file(s)` from this
checkout's real feature dirs.

Mutation: `SCAN_COUNT_RE` changed from `r"—\s*(\d+)\s*file\(s\)"` to
`r"—\s*.*?(\d)\s*file\(s\)"` (captures only the last digit — reproduces, in regex form, the exact
substring-style regression the docstring names: "41 file(s)" yields last digit "1").

**Result: 1 of 3 call sites reddens**, not 3 — `case_root_resolves: CLAUDE_PROJECT_DIR alone does
not redirect the sweep` (line 372, `scanned_count(r.stderr) != 1`), which flips because the real
41-file scan's last digit is 1. The other two call sites (line 347, line 383) both assert `== 1`
against subtests whose *own fixtures* produce a literal single-file scan — a count of exactly 1
survives this mutation class unchanged (1's last digit is still 1), so those two checks pass
whether or not the parsing is correct. This is exactly what the function's own docstring predicts:
two of the three "were assertions that a BROKEN sweep would satisfy" — they are only ever sensitive
to a broken count when the real count differs from 1, and their own fixtures never produce that.
Reverted; scratch (`/tmp/qa-scratch-1030-e`) deleted.

**Probe of the real (unmutated) `scanned_count()`** on absent/empty/garbled stderr — all three
inputs: **returns `None`, never raises.**
```
'absent (None)': returned None (no exception)
'empty string': returned None (no exception)
'garbled stderr': returned None (no exception)
```
Because line 372's assertion is `!= 1`, `None != 1` is `True` — a sweep that crashes before
printing any `file(s)` line would make that specific check vacuously PASS, identical in shape to
the two structurally-vacuous `==1` sites above. Nothing in the current suite exercises this input
class.

## Matrix

No `plan.yaml`/`BRIEF.md` exists for this feature (confirmed absent again this cycle); change_type
inferred as `cross_module` per cycle 0 (Python core + two Python callers + one TS enforcement
file), floor = `unit` + `integration`.

- `unit`: `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` → **exit 0, 457 PASS lines, 0
  FAIL**. `test-validate-feature-json.py` is in this run and passed cleanly — **cycle 0's
  environmental failure (41 real feature.json files vs. a fixture assuming zero) does NOT
  reproduce**, confirmed: `scanned_count()` now parses the integer instead of doing a substring
  check, so the real repo's 41-file scan no longer collides with the "1 file(s)" literal.
- `integration`: `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` → **exit 0, 581
  PASS lines, 0 FAIL**.
- TS unit suite (`test-omp-hooks.py` → `bun test omp-hooks.test.ts`, 51/51): this diff itself
  added it to `UNIT_SCRIPTS` in `run-unit-tests.sh` (confirmed by `git diff` on that file), closing
  cycle 0's "matched by detect glob but never executed" gap. It now runs as part of the `unit` kind
  above, not manually.

`matrix_ok: true`. Mutation (a) (`preDomain`'s edit branch) not re-run per dispatch — already
confirmed exact at 2 by two other reviewers this cycle.

## Why VERDICT is FAIL despite a green matrix

`suite: fail` / `failures: 1` reflects the (e) mutation run's own reddened case, which is expected
and correctly labelled — it is not evidence of a defect in the shipped code, it's evidence
*produced by design* to answer the dispatch's question. The gate is not held open by that. It is
held open by the **coverage gap this measurement surfaces and confirms**: two of
`scanned_count()`'s three call sites, plus its `None`-on-garbled-input behavior, remain silently
insensitive to exactly the class of bug this function was written to catch, for any input the
current fixtures happen to produce. That gap predates this diff and this diff does not introduce
it, but it is real, newly measured (not merely asserted), and unresolved — reported per DEC-169
(an absence/vacuity finding is not a check on its own) so it returns to the appropriate reviewer
rather than being silently closed here, since DEC-174 forbids me from touching the fixture that
would fix it.
