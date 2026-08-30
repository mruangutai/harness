# Receipt — harness-backend-dev — stale-anchor-write-hazard cycle 2

## Headline

`gh-sync.py`'s three feature.json write sites (`_record_status`, `_record_pr`,
`save_recorded`) now go through the locked, schema-validated
`feature_json_write.write_feature_json`; `_atomic_write` is deleted with no shim. The
monotonic non-regression policy's discriminating case (a dirty base) is now under test —
one real test-design gap was found and fixed (not a production defect). This closes the
DEC-199 implementation gap between the signed "every shared artifact goes through one
locked core" rule and the code; **it does not close the literal stale-anchor incident**
(a line-anchored EDIT splicing raw text never calls Python at all — see
`feature_json_write.py`'s own docstring, unchanged from cycle 1).

One real mid-run mistake, caught and reverted before it left the sandbox: two `edit` calls
using a bare relative path resolved against the MAIN checkout instead of this worktree
(`gh-sync.py` then `test-gh-sync.py`). Both were caught immediately via
`git status --porcelain` in the main tree and reverted with `git checkout -- <path>`
before any further work; the main checkout is confirmed clean (`git status --porcelain`
empty for both files). Every edit after that used the absolute worktree path in the
section header.

## Item 1 — the ratchet's discriminating case (test-feature-json-merge.py)

Added three cases, all on a DIRTY base (missing one required key, `status`) — the shape
the existing 23 cases never built:

- **case11 (ratchet holds):** transform introduces a SECOND missing key (`review_sha`).
  Refused; the refusal names `review_sha`, never `status`; file byte-identical.
- **case12 (does not over-refuse):** transform sets only an unrelated, already-legal key
  (`cycles_used`). Accepted; the key lands; `status` stays absent and is never reported.
- **case13 (unparseable base is strict):** base is not valid JSON. A schema-clean
  candidate lands (empty baseline). A candidate that is ALSO unparseable, but shaped
  differently (`Expecting value` vs. the base's `Expecting property name...`), is refused —
  pinned direction: leniency requires an EXACT prior message match, never "base already
  had some JSON-decode problem." File left as the original broken base.

**RED evidence, two kinds:**

1. **Genuine RED on first write, for a real reason.** case13's first draft used
   `broken_transform` returning `"{ a completely different broken payload *** not json"`
   against a base of `"{ not json at all, missing brace"`. Both strings fail at the exact
   same decoder position (right after `{ `), so `json.loads` produces the IDENTICAL error
   message for both — `Expecting property name enclosed in double quotes: line 1 column 3
   (char 2)` — which the monotonic-non-regression comparison (exact string match) reads
   as "already on the base," so it silently ACCEPTED the overwrite. Verbatim failure
   before the fix:
   ```
   FAIL - case13: differently-broken candidate over an unparseable base is refused ([])
   FAIL - case13: refusal names a JSON decode error ([])
   FAIL - case13: file left as the original unparseable base, not overwritten (b'{ a completely different broken payload *** not json')
   FAIL - 3/34 checks failed
   ```
   Fixed by SHARPENING the test's own malformed text (`{"feature_id": "x", "status":
   Building}` — a genuinely different failure shape/position, verified with a standalone
   `json.loads` probe first) — not by touching `feature_json_write.py`. This is not a
   production defect: identical-position decode errors reading as "the same problem" is
   the documented, deliberate behaviour of an exact-string-match ratchet (the direction
   the module's own docstring calls out). 34/34 green after the fix.

2. **Mutation-testing RED for case11/case12**, which passed on first write against
   already-correct code (P-11: a coverage gap in correct code needs mutation proof, not a
   RED/GREEN cycle on new production code, since there was no defect to fix). Mutated
   `feature_json_write.py`'s `_transform` from the monotonic policy back to
   "any candidate problem refuses" (predicted to break case11's "does not name status"
   assertion and case12's "accepted" assertion). Observed:
   ```
   FAIL - case11: refusal does NOT name the pre-existing problem (status) ([".../feature.json: missing required key 'review_sha' at / ...", ".../feature.json: missing required key 'status' at / ...", ...])
   FAIL - case12: accepted, not refused (["... missing required key 'status' at / ..."])
   FAIL - case12: unrelated key landed ({...no 'cycles_used': 3...})
   FAIL - 3/34 checks failed
   ```
   Exactly as predicted. Restored by hand (not `git checkout` — the file is untracked
   this cycle), verified `sha256sum` matched the pre-mutation hash
   (`0e3a4bfefc08089fb58b2d3cfcf1d35fb8c3a3cc0378a6c1904554370cbd05c9`) and
   `git status --porcelain` showed the file only as `??` (untracked, no diff possible
   against a committed baseline — the hash match is the provenance proof).

Final verbatim `python3 .claude/skills/harness/bin/test-feature-json-merge.py` (34/34):
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
PASS - case11: refused
PASS - case11: refusal names the NEW problem (review_sha)
PASS - case11: refusal does NOT name the pre-existing problem (status)
PASS - case11: file byte-identical to before
PASS - case12: accepted, not refused
PASS - case12: unrelated key landed
PASS - case12: pre-existing problem (missing status) still present, unreported as a refusal
PASS - case13: schema-clean candidate lands over an unparseable base
PASS - case13: differently-broken candidate over an unparseable base is refused
PASS - case13: refusal names a JSON decode error
PASS - case13: file left as the original unparseable base, not overwritten
PASS - 34/34 checks passed
```

## Item 2 — wiring gh-sync.py's three write sites onto the locked writer

### Design

Each of the three functions does its own absent/unreadable/non-mapping decision on a
PLAIN read FIRST, before `write_feature_json`/`require_destination` is ever called — this
is load-bearing, not stylistic: `require_destination` is the very first line inside
`write_feature_json`, so any call made before that pre-check would let a bad path shape
substitute its own, differently-worded refusal for these functions' own tolerant message.
A second, identical check re-runs INSIDE the locked transform (`base is None`) as
defence against the narrow TOCTOU window between the pre-check and the lock acquire —
this is new (locking closes a real race the old single-read `_atomic_write` could not),
not a behaviour change for the common case.

- **`_record_status`**: pre-check open+`json.load`, print+return on `(OSError, ValueError)`
  or non-dict, exactly as before. Transform re-reads under the lock and sets `status`.
  Any `MergeRefusal` from the locked write (including the `base is None` race guard) is
  caught at the call site and printed as "could not be read" — never raised, never
  creates a document, matching the preserved contract.
- **`_record_pr`**: same pre-check pattern, same early "already recorded — not
  overwritten" print if the PRE-lock read shows an int `pr` (avoids an unnecessary `gh pr
  list` call, matching the original's ordering). The idempotency check ALSO re-runs
  inside the locked transform against a FRESH read: if a concurrent writer landed `pr`
  between the pre-check and the lock, the transform returns `base` unchanged (a harmless
  no-op replace) instead of clobbering it — this is a case the original single-read
  `_atomic_write` version could not close, and it is exactly DEC-199's point.
- **`save_recorded`**: the absent-file `SystemExit`, with its EXACT original message text,
  is raised twice, verbatim — once on a plain `os.path.exists` check before
  `write_feature_json` is called (so the ordering requirement holds), and again inside the
  transform if `base is None` (the same narrow race). The non-mapping-document tolerance
  (`doc = {}`) is preserved exactly as before; a genuinely UNPARSEABLE existing document
  still raises an uncaught `json.JSONDecodeError` from inside the transform, matching the
  ORIGINAL code's behaviour exactly (no try/except was ever added around that
  `json.loads` — new tolerance was not invented here).

`_atomic_write` is deleted; `import tempfile` (its only user) is deleted from
`gh-sync.py`'s imports. Confirmed by grep: no live symbol, no calls —
```
$ grep -n "_atomic_write" .claude/skills/harness/bin/gh-sync.py
537:    T-c2): the same lock, same-directory tempfile, fsync and os.replace `_atomic_write` gave
593:    `_atomic_write` version could not).
678:    tempfile, fsync and os.replace `_atomic_write` gave it, matching factory_decompose.py's
```
(all three hits are prose in docstrings explaining what the primitive replaced, not a
reference to a live function or call). `ast`-based confirmation: `_atomic_write` is not
in the module's function definitions; zero `ast.Name` references to it anywhere in the
file.

### test-gh-sync.py fixture changes — what each pinned, and why the replacement pins no less

Added `nested_feature_dir(feat_name)` (a fresh tempdir's `.harness/features/<feat_name>/`,
matching `stage()`'s own convention and `FEATURE_JSON_TAIL`). Applied to all nine bare
`tempfile.mkdtemp()` fixtures the prior cycle's receipt enumerated (now-shifted lines:
~1244, ~1265, ~1282, ~1299, ~1315, ~1332, ~1347, ~1386, ~2078).

Of these nine, only **two** (~1347 `_datomic`, the fix1 atomicity fixture; ~1386 `_d` in
the round-trip loop) actually NEEDED the path fix — both call `save_recorded` against a
FILE THAT EXISTS, so `require_destination` fires for a bare tempdir. The other seven call
either `load_recorded` (a pure reader with no lock, no destination check, unaffected by
this feature at all: ~1244/1265/1282/1299/1315/1332) or `save_recorded` on a path where
the file is ABSENT (~2078: the T-02 absent-file refusal test), where `save_recorded`'s own
pre-check fires and returns before `write_feature_json` is ever reached. I nested all nine
anyway, per the dispatch's explicit instruction and because it is genuinely neutral —
it does not touch what any of the seven's assertions test (their oracle is
`load_recorded`'s return value or `save_recorded`'s SystemExit text, neither of which
depends on path shape once the destination check isn't hit) — but the technical
NECESSITY was only the two.

No fixture document needed widening to schema-complete: setting `status`/`pr`/`github`
introduces no NEW schema problem over a 2-key base (both are already-legal top-level
keys per feature-schema.json), so the monotonic non-regression policy tolerates every
2-key fixture used here without any assertion needing to weaken.

**One assertion changed, and here is the no-weaker argument, by name (per the acceptance's
explicit demand):**

- **fix1 atomicity test (`_datomic`, was line ~1333, now ~1347+~1368-1373):**
  `_leftover = [f for f in os.listdir(_datomic) if f != "feature.json"]` failed because
  `harness_merge.acquire` now creates a sibling `feature.json.lock` file — deliberately
  NEVER removed (harness_merge.py's own docstring: "flock has no stale state, so leaving
  the file behind costs nothing"). What this assertion PINS is "a failed write leaves no
  stray TEMP artifact from a partial/aborted write" — the `_atomic_write`-era shape was a
  `mkstemp` tempfile cleaned up on exception. The lock file is not that artifact: it is
  created once, on EVERY call (success or failure alike), and its presence is
  independent of whether the write itself failed. I widened the exclusion list to
  `("feature.json", "feature.json.lock")` — this is NO WEAKER on the property actually
  under test: a REAL leak (a stray `.tmp`/mkstemp basename from `locked_update`'s own
  `except BaseException: os.remove(tmp_path)` path failing to fire) would still show up
  in `_leftover` and still fail the check, because that filename is neither
  `feature.json` nor `feature.json.lock`. I did not touch the byte-identical assertion
  immediately above it (`fix1 A: a failed save_recorded leaves feature.json
  byte-identical, never truncated`), which is the property that actually matters for the
  stale-anchor-adjacent hazard and needed no change.
- **Every other touched assertion is untouched in substance** — the nine fixtures changed
  only WHERE the file lives on disk (a tempdir vs. a nested tempdir), never WHAT is
  asserted about its content, so no other no-weaker argument applies.

Verbatim `python3 .claude/skills/harness/bin/test-gh-sync.py` tail (full run, no abort):
```
ok    a failing --add-label does not abort the run — no SKIP, exit 0
ok    a failing --add-label on the FIRST issue still leaves every later issue closed
ok    a failing --add-label still leaves the card in the BACKLOG, never at done — the cosmetic write cannot cost the state correction
ok    the label failure is REPORTED on stderr, naming the issue
ok    _record_status still runs — feature.json reaches Abandoned

ALL PASSED
```

**Before/after check count**, per the acceptance's explicit ask: `grep -c "^ok"` on the
full run = **273 before** (the untouched pre-cycle-2 file, via `git stash`, against
untouched pre-cycle-2 `gh-sync.py`) and **273 after** (this cycle's rewired
`gh-sync.py` + fixed fixtures). Same total, zero removed, zero newly vacuous, the same
9 fixtures now exercising the real locked-writer path instead of a destination check
that did not exist before this feature.

### bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds

```
check-kinds: the script arrays and test_kinds.integration.detect agree.
```
Exit 0. `test-gh-sync.py` is (and was already, pre-cycle-2) registered in
`INTEGRATION_SCRIPTS`, not `UNIT_SCRIPTS` — `--kind unit` does not run it; `--kind
integration` or a direct invocation does. Ran it directly (above) per the dispatch's
named acceptance file list. Also ran `--kind unit` for completeness: 454/454 checks
passed across every unit script including `PASS test-feature-json-merge.py` — the two
`check-domain: OVER BUDGET` lines printed during that run reference a DIFFERENT feature's
worktree (`FEAT-43-code-risk-grading`), are marked `(already written)`, and are unrelated
to any file this dispatch touches.

## Files touched

Touched: `gh-sync.py` (rewired three write sites, deleted `_atomic_write` and its
`tempfile` import), `test-gh-sync.py` (added `nested_feature_dir`, applied it to nine
fixtures, widened the fix1-atomicity leftover-file exclusion by one filename),
`test-feature-json-merge.py` (added cases 11-13, registered in `main()`).

Untouched this cycle: `feature_json_write.py`, `feature-json-merge.py` (no defect found;
mutation-tested, not edited — restored byte-identical after the mutation probe),
`run-unit-tests.sh` (cycle-1's registration only, no further change), every DEC-174 file,
`feature_schema.py`, `feature-schema.json`.

## The DEC-199 gap vs. the incident — restated plainly, per the dispatch's own framing

This closes a gap between a signed rule (DEC-199: "every shared artifact two contexts can
write at once goes through one locked, union-merging core") and its implementation
(FEAT-32 scoped exactly four consumers; `gh-sync.py` was a fifth writer of `feature.json`
left outside the core). It is justified by that gap, not by the stale-anchor incident:
the incident was a line-anchored EDIT tool splicing feature.json's raw bytes directly,
which never calls into Python and therefore was never, and could never be, reachable from
any of `gh-sync.py`'s three call sites or from `feature_json_write.py` itself. Closing
this gap makes every Python writer of `feature.json` race-safe and schema-checked against
every OTHER Python writer; it does nothing to and says nothing about a non-Python,
byte-offset write path.
