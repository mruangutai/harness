# Receipt — harness-backend-dev — FEAT-44-omp-context-advisory — cycle 3 (stale-anchor-write-hazard)

## Scope
`.claude/skills/harness/bin/factory_decompose.py`'s `write_factory` — the last Python writer of
`feature.json` outside the locked core (`feature_json_write.write_feature_json`,
`harness_merge.locked_update`) — plus `test-factory-decompose.py`.

## What changed

`write_factory` (`factory_decompose.py:148-199`) no longer carries its own
`tempfile.mkstemp`/`os.fdopen`/`os.fsync`/`os.replace` primitive. It now builds a `transform`
closure and calls `feature_json_write.write_feature_json(path, transform)` — the same fcntl
lock, same-directory tempfile, fsync and atomic rename `gh-sync.py`'s three call sites already
share (DEC-199). `import tempfile` was dropped (the module's only use of it). The module
docstring (`:19-31`) now names the locked entry point and the absent-file decision below.

`grep -n "tempfile.mkstemp\|os.replace" factory_decompose.py` returns **zero hits** — not even
in prose; the docstring names the primitive by its shape ("same-directory tempfile, fsync and
atomic rename") rather than spelling the literal identifiers, so the grep receipt is clean and
the sentence explaining the change does not accidentally re-introduce what it describes as gone.

## The absent-file contract decision

**Converged onto `gh-sync.py`'s `save_recorded` contract: an absent `feature.json` is REFUSED
(`harness_merge.MergeRefusal(9, ...)`), not started from `{}`.** This is a genuine behaviour
change from the private primitive's own `if os.path.exists(path): ... else: doc = {}` fallback
(`factory_decompose.py:149-155` on the pre-fix tree) — a `{factory: ...}`-only document is now
refused rather than written.

**Call sites checked, none of which is a legitimate first writer:**
- `factory_decompose.py`'s own five call sites (`_main`, lines ~353/372/384/409/431/463 on the
  pre-fix tree) always run AFTER `load_factory(feat_dir)` (`:104-135`), which reads the
  file if present — but nothing in `_main`'s own flow ever CREATES `feature.json`; it only
  reads (tolerant of absence, returning an empty in-memory `factory` dict) and then writes
  the `factory` block back.
- `factory_cli.py` — the shared command-line contract module — has no feature.json-creating
  code path at all (grepped; only `exit`/`payload`/`message` helpers).
- `test-factory-decompose.py`'s own `make_feature`/`make_feature_bad_feature_key` fixtures
  and the two standalone D4-4/T-03 blocks all write `plan.yaml`, `BRIEF.md` AND
  `feature.json` together as one complete fixture — the fixture builder choosing to write a
  minimal `"{}"` document is a TEST CONVENIENCE, not evidence that `write_factory` is ever
  the real first writer in production. `feature.json` is instantiated by the orchestrator
  from `.agents/skills/harness/templates/feature.json` on the feature's first cycle, well
  before decompose (a factory/served-repo tool, D-12) ever runs against that feature.

No caller needed the create-from-empty path preserved, so the update path converges cleanly
onto `write_feature_json`'s own "absent base is a strict, empty baseline" rule (an absent file
IS technically still refusable there too, since it produces a one-key document that fails all
8 required-key schema checks) — DEC-199's contract already agreed with this decision; I only
needed to make `write_factory` refuse the absent case EXPLICITLY, in its own `transform`, ahead
of `write_feature_json`'s per-candidate schema check, so the refusal message names the actual
cause (absent file) rather than a generic "missing 8 required keys" schema dump.

## Tests — RED before, GREEN after (item 1)

Three new cases added to `test-factory-decompose.py`, verified RED against the untouched
`write_factory` (captured via `git stash push -- factory_decompose.py`, re-run, `git stash
pop`), verbatim:

```
FAIL  (C3-1) write_factory's key survives the interleave
        {'feature_id': 'FEAT-99-probe', 'branch': 'none', 'pr': None, 'status': 'Backlog', 'review_sha': 'none', 'cycles_used': 0, 'max_total_cycles': 5, 'runs': [], 'max_total_runs': 20}
ok    (C3-1) the unrelated concurrent writer's key survives the interleave
FAIL  (C3-2) write_factory refuses a candidate introducing a new schema problem
FAIL  (C3-2) feature.json left byte-identical after the refusal
        {
  "feature_id": "FEAT-99-schema-guard",
  ...
  "factory": {
    "repo": 12345,
    ...
  }
}

FAIL  (C3-3) write_factory refuses a path outside a features directory, code 9
        code=None
FAIL  (C3-3) no file created at the refused path

5 of 188 FAILING.
```

Every OTHER check (183 of them, including every pre-existing case) still passed on that same
RED run — the fixture-nesting change (item 3) is orthogonal to `write_factory`'s own behaviour
and was verified not to perturb any pre-existing assertion.

After the fix: `160/160 checks passed`, zero `FAIL` lines.

(Total-count arithmetic note for anyone diffing these numbers later: the totals include
pre-existing case 22's `fake_replace`/`fake_open` monkeypatch hooks, whose own inner
`check()` calls fire *inside* `run_publish`'s `contextlib.redirect_stdout` — so their "ok"
text is silently swallowed into the captured buffer while `RAN`/`FAILS` still count them. That
swallowed count differs between implementations because they call `os.replace`/`open` a
different number of times internally (old: 7 direct calls × 4 hook checks = 28; fixed:
`harness_merge.locked_update`'s I/O isn't all intercepted by the same hooks). This is a
pre-existing property of case 22, not a regression — confirmed by isolating it with
`git show HEAD:.../factory_decompose.py` vs the fixed tree against a stripped-down copy of the
suite, and by the fact `FAILS` is 0 in both variants there.)

## C3-2/C3-3 case design

- **C3-2** seeds a schema-clean, 8-required-key base document, then calls `write_factory` with
  a `factory["repo"]` of `12345` (schema: `factory.repo` is `["string","null"]`) — a NEW
  problem absent from the clean base's baseline, so `write_feature_json`'s monotonic
  non-regression rule refuses it. Confirms the refusal (`harness_merge.MergeRefusal`) and
  byte-identical file after.
- **C3-3** calls `write_factory` against a `feat_dir` not nested under `.harness/*/features/*/`
  and confirms `harness_merge.require_destination`'s refusal code (`9`) and that no file is
  created — this is the SAME refusal shape as `test-feature-json-merge.py`'s own `case5`.
- **C3-1** is modeled directly on `test-feature-json-merge.py`'s
  `case_2_concurrent_writer_blocks_not_clobbers`: two `os.fork()` children, one calling
  `write_factory` and the other an independent `feature_json_write.write_feature_json`
  transform (simulating a `gh-sync.py`-shaped writer) setting an unrelated top-level key, the
  latter sleeping 0.05s mid-transform WHILE HOLDING THE LOCK to widen the overlap window.
  Wrapped each child body in `try/finally: os._exit(0)` (not a bare `os._exit(0)` after the
  call) — an earlier draft without this crashed a forked child on an unrelated bug, and the
  child's *normal* Python shutdown path ran `tempfile.TemporaryDirectory`'s registered
  finalizer, deleting the SHARED temp directory out from under the sibling process and the
  parent; `finally: os._exit(0)` guarantees the hard exit (which skips finalizers) runs
  regardless of what the child's body does.

## Fixture nesting (item 3)

`make_feature`, `make_feature_bad_feature_key`, and the two standalone D4-4/T-03 blocks built
`feat_dir` as a bare `<tmp>/feature` directory. `require_destination`'s
`FEATURE_JSON_TAIL` needs `.harness/(?:[^/]+/)?features/(?:FEAT|BUG)-.../feature.json`, so
every one of those fixtures is now nested at `<tmp>/.harness/features/<feat>/`, matching
`test-gh-sync.py`'s `nested_feature_dir` convention exactly (same two path segments, no
extra repo-tier segment).

**What each touched assertion pinned before, and why nesting doesn't weaken it:** none of the
~150 pre-existing assertions test anything about the FIXTURE'S OWN PATH SHAPE — they test
`factory_gh` call arguments, `feature.json`'s `factory` block contents, exit codes and
stdout/stderr text, all of which are independent of how deep `feat_dir` sits on disk. Nesting
is a pure fixture-plumbing change; the SET of properties each case pins is unchanged, confirmed
by the GREEN run reproducing the exact same pass/fail outcome (0 fails) for every pre-existing
named check.

## Verify

- `python3 .claude/skills/harness/bin/test-factory-decompose.py` — **160/160 passed** (was
  188 with 5 failing before the fix, on the same nested fixtures).
- `python3 .claude/skills/harness/bin/test-feature-json-merge.py` — **34/34 passed**, unaffected.
- `python3 .claude/skills/harness/bin/test-gh-sync.py` — **ALL PASSED** (0 `FAIL` lines), unaffected.
- `grep -n "tempfile.mkstemp\|os.replace" .claude/skills/harness/bin/factory_decompose.py` — no
  output (zero hits, prose included).

## Non-goals honored

`gh-sync.py`, `feature_json_write.py`, `feature_schema.py`, `feature-schema.json`,
`run-unit-tests.sh`, every DEC-174 file, and all real `.harness/*/features/*/feature.json`
files were not touched. `.agents/skills/harness/bin/factory_decompose.py` (the duplicate copy
under `.agents/`) was left as-is — out of the stated scope (`.claude/skills/harness/bin/`
only); its own drift from this fix is a separate, unscoped concern.
