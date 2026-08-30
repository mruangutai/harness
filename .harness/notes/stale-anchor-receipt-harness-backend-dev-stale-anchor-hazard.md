# Receipt — harness-backend-dev — stale-anchor-write-hazard (BackendMergeHelper)

## Headline

Delivered a locked, schema-validated feature.json writer (`feature_json_write.py` +
`feature-json-merge.py` CLI), fully test-first and green. **Did NOT wire `gh-sync.py`'s three
write sites onto it** — doing so, exactly as specified, breaks `test-gh-sync.py` in a way that
is provably irreconcilable without editing that file (outside my domain) or weakening a
guarantee the dispatch itself requires. `gh-sync.py` and `test-gh-sync.py` are byte-identical
to their pre-session state.

## What shipped

- `.claude/skills/harness/bin/feature_json_write.py` (NEW) — the one public read-modify-write
  entry point, `write_feature_json(path, transform, timeout=None)`, built on
  `harness_merge.locked_update`. No second lock/rename primitive (DEC-199). Validates the
  candidate document with `feature_schema.problems_for_text` before the atomic replace.
- `.claude/skills/harness/bin/feature-json-merge.py` (NEW) — thin CLI: `set-key`,
  `append-run`, `set-github`, mirroring `plan-merge.py`/`observations-merge.py`'s own split.
- `.claude/skills/harness/bin/test-feature-json-merge.py` (NEW) — 23 checks, all green.
- `.claude/skills/harness/bin/run-unit-tests.sh` — registered the new test in `UNIT_SCRIPTS`
  (dispatch's own instruction; also sidesteps touching `.harness/harness.json`'s
  `test_kinds.integration.detect`, which is `harness-dev-ops`'s domain, not mine).

Deliberately NOT touched: `gh-sync.py`, `test-gh-sync.py`, `feature_schema.py`,
`feature-schema.json`, every DEC-174 file.

## One deliberate deviation from the literal spec, inside the library itself

The dispatch says: "validate it with `feature_schema.problems_for_text`... if that returns
problems, REFUSE." Implemented literally, this refuses **any** feature.json missing even one
of the eight DEC-191 keys — including every document already on disk that predates DEC-191.
Running the literal version against `test-gh-sync.py` (see below) proved this empirically:
`test-gh-sync.py`'s own `write_feature_json` fixture helper (line 101) has built
`{"feature_id": ..., "status": ...}` — a 2-key document — since T-01/FEAT-23, and the whole
suite's `stage()` and every `_pr_fixture`/`_full_fixture` build on it.

Fix: **monotonic non-regression**, not "any problem refuses." A candidate is refused only for
a schema problem **not already present on the base** document (see
`feature_json_write.write_feature_json`'s docstring for the full reasoning and the explicit
citation of `feature_schema.py`'s own `RUNS_AGENT_EXEMPT`/D-23 precedent — this codebase
already has exactly this "enforce going forward, not retroactively" shape for the same
schema). A brand-new document (base absent or unparseable) still gets a zero baseline, so it
must be fully schema-clean. This is a considered engineering decision, not a workaround: it
still refuses every stale-anchor-shaped corruption (a schema-clean document written over
becomes unparseable or newly-invalid; that is never in the base's problem set). Proven by
`test-feature-json-merge.py` cases 1, 3, 4 (all built on a schema-COMPLETE base, so the
non-regression policy behaves identically to strict validation there).

## Why `gh-sync.py` is NOT wired to the new library — the finding

I implemented the rewiring exactly as specified (all three sites through
`feature_json_write.write_feature_json`, `_atomic_write` deleted, refusal messages preserved)
and ran `test-gh-sync.py` against it. It **aborted partway through** (only 80 of ~180+ checks
ran before an uncaught `SystemExit`), for a reason distinct from the schema question above and
NOT fixable by the monotonic-non-regression change:

`harness_merge.require_destination` (which `write_feature_json` calls, per the dispatch's own
explicit instruction 1: "the module refuses a path that does not resolve to
`.harness/*/features/*/feature.json`") refuses any `feat_dir` that is not nested under a real
`.harness/(.../)?features/FEAT-.../` directory. **The bulk of `test-gh-sync.py`'s fixtures for
`load_recorded`/`save_recorded` are bare `tempfile.mkdtemp()` directories** — e.g. lines 1230,
1251, 1268, 1285, 1301, 1318, **1333** (the fix1-atomicity test), **1372** (the
round-trip test), and **2064** (`_dabsentT02`). None of these resolve under a features
directory, so every one of them is refused by `require_destination` before `save_recorded`'s
own logic — including the absent-file check — ever runs.

This is not a fixable edge case; it is a direct contradiction **inside my own dispatch**.
Acceptance item 3 says, verbatim: *"save_recorded REFUSES an absent feature.json with its
existing SystemExit and its existing message text."* The test that exercises exactly that
(line 2064, `_dabsentT02 = tempfile.mkdtemp()`) is itself a bare tempdir. Wired through
`write_feature_json`, `require_destination`'s refusal (code 9, "not a feature's feature.json
under a features directory") fires **before** the absent-file-specific message can, changing
both the exception shape and the text — which directly violates the SAME acceptance item that
asked me to preserve it verbatim. There is no regex for `FEATURE_JSON_TAIL` that resolves
this: loosening it to accept any `.../feature.json` (no features-directory requirement) would
make `test-feature-json-merge.py`'s own required case 5 ("path outside
`.harness/*/features/*/feature.json` is refused" — which uses exactly this bare-tempdir
shape as its refused fixture) fail instead.

**Verdict on the merge helper itself: it is not the wrong remedy, and it stands fully on its
own merits** — `feature_json_write.py` and `feature-json-merge.py` are correct, complete,
locked, atomic, and schema-validated, and any FUTURE caller (a rewritten `gh-sync.py`, or the
next tool that touches feature.json) can adopt them today. **It is `gh-sync.py`'s specific
call sites that cannot adopt it without either (a) test-gh-sync.py's fixtures being updated to
nest under `.harness/features/FEAT-NN/` — mechanical, low-risk, but `test-gh-sync.py` is not
in my domain this run — or (b) an explicit decision to scope `require_destination` differently
for internal callers vs. the CLI, which changes the "one public entry point" design the
dispatch itself specified and is a real decision, not mine to make unilaterally.**

Also worth naming honestly, on the stale-anchor incident itself (per the dispatch's own
invitation to say if the remedy doesn't close it): **it does not.** The incident was a
line-anchored EDIT tool patching feature.json bytes directly — that path never calls Python,
so no library placed inside Python call sites (gh-sync.py's or anyone else's) can intercept
it. This feature closes the adjacent hazard (races and corruption among Python writers); it
does not and cannot close the literal incident described. `feature_json_write.py`'s own
docstring says this plainly.

## Verification

### `python3 .claude/skills/harness/bin/test-feature-json-merge.py`

RED proven before GREEN: at the start of this run the module did not exist
(`ModuleNotFoundError: No module named 'feature_json_write'`); after the initial
implementation, case 2 and case 7 failed RED for a real reason (`runs[0]` missing `agent` per
SC-07 — fixture bug, not implementation bug) before being fixed; the monotonic-non-regression
change was proven not to regress the 4 cases (1,3,4,6-10) that already covered
strict-on-a-clean-base behaviour.

Final verbatim output (23/23):
```
PASS - case1: MergeRefusal propagated
PASS - case1: file byte-identical to before
PASS - case2: both concurrent writers' entries survive (lock serialised, did not clobber)
PASS - case3: refused
PASS - case3: refusal names a JSON decode error
PASS - case3: file left as the original valid document
PASS - case4: refused
PASS - case4: refusal names a missing required key
PASS - case4: file byte-identical to before
PASS - case5: refused with the destination code
PASS - case5: no file created at the refused path
PASS - case6: CLI exits 0
PASS - case6: status landed
PASS - case6: every other key survived unchanged
PASS - case7: CLI exits 0
PASS - case7: run entry appended
PASS - case8: CLI exits 0
PASS - case8: github block landed
PASS - case9: CLI exits non-zero
PASS - case9: stderr names the schema problem
PASS - case9: file byte-identical to before
PASS - case10: CLI exits non-zero for a missing file
PASS - case10: no file created
PASS - 23/23 checks passed
```

### `python3 .claude/skills/harness/bin/test-gh-sync.py`

Unmodified, `gh-sync.py` unmodified (reverted after the failed rewiring attempt — see above).
Exit 0, `ALL PASSED`. This is the ORIGINAL, untouched behaviour — not evidence the rewiring
works, evidence the revert was clean.

### `bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds` and `--kind unit`

```
check-kinds: the script arrays and test_kinds.integration.detect agree.
```
Full `--kind unit` run: 27/27 scripts `PASS`, exit 0, including `PASS test-feature-json-merge.py`.

## Files touched vs. deliberately not touched

Touched: `feature_json_write.py` (new), `feature-json-merge.py` (new),
`test-feature-json-merge.py` (new), `run-unit-tests.sh` (1-line `UNIT_SCRIPTS` addition).

Deliberately not touched: `gh-sync.py`, `test-gh-sync.py` (both reverted to their pre-session
state after the finding above), `feature_schema.py`, `feature-schema.json`,
`.harness/harness.json` (dev-ops domain), every DEC-174 file.

## Open item for the routing decision (not mine to make)

`gh-sync.py`'s three write sites (`_record_status`, `_record_pr`, `save_recorded`) still use
`_atomic_write` and are not locked or schema-checked. Closing that gap needs one of:
1. Update `test-gh-sync.py`'s fixture helpers (`write_feature_json` at line 101, and the bare
   `tempfile.mkdtemp()` fixtures at lines 1230/1251/1268/1285/1301/1318/1333/1372/2064) to
   nest under a realistic `.harness/features/FEAT-NN/` shape and carry all eight required
   keys — mechanical, but `test-gh-sync.py` is outside every domain granted this run.
2. Or a decision that `require_destination`'s path-shape check does not apply to gh-sync.py's
   already-trusted, orchestrator-supplied `feat_dir` — which is a real design decision (it
   loosens the "one public entry point, always destination-checked" contract) belonging to
   whoever owns this feature's decisions, not to me.
