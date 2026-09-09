# EFFICIENCY angle — B-27 diff (fb9a4ac4)

**BLUF: no findings. The measured costs are all sub-second, run only inside the qa `--kind unit`
gate (not a per-session/per-write hot path), and are the deliberate evidence B-27's boundary
exists, not waste.**

## Measured wall-clock (env cleared, `env -u HARNESS_AGENT_TYPE`, worktree root, 3 runs each)

- `python3 tests/unit/test-factory-claim.py`: **0.137–0.153s** real (125/125 checks passed each
  run). This file is unchanged in run count by the diff — it still executes once per invocation.
- `python3 tests/unit/test-factory-claim-mutation.py`: **0.248–0.307s** real (both markers print:
  `MUTATION PROOF: 3/3 cases reddened`, `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed`).

## Marginal cost of the third in-process suite run

Before this diff, `main()` ran `_baseline()` + `_mutation_proof()` — two in-process runs of
`test-factory-claim.py` (confirmed by diff: `sys.exit(0 if _mutation_proof() else 1)` →
`features_root_ok = _mutation_proof(); key_collapse_ok = _key_collapse_proof()`). This diff adds a
third, `_mutate_and_run_key_collapse()`. Single-suite cost measured at ~0.14s; three in-process
runs cost ~0.27–0.31s ≈ 3 × ~0.09s each (some savings from shared process/import overhead not
present in the standalone timing). **Marginal cost of the third run ≈ 0.09s per invocation of
`test-factory-claim-mutation.py`.**

## Where this runs — boundary, not hot path

Grepped prior qa/receipt notes in this feature: this suite runs inside
`.agents/skills/harness/bin/run-unit-tests.sh --kind unit`, the qa test-matrix gate, alongside 27
other files (`pool: 8 workers, 28 files, ~3.1–4.5s wall` per multiple qa receipts in this
feature's notes). It is not invoked at session entry or on every write. **A ~0.09s marginal cost
inside a ~3–4.5s, 28-file gate pool is the evidence the boundary exists, not waste** — it is
exactly the "deliberate full-suite run at a boundary step" the skill says not to flag. The prior
qa receipt (`receipt-harness-backend-dev-2026-09-06-14-eng.md`) also shows a negative-control
mutation (neutering the key-collapse effect while keeping the reached-marker) that the third run
alone catches — the seam duplication is discriminating, not incidental.

## 5b run twice in `test-factory-claim.py` (`_emit_5b(check)` :1237, `_emit_5b(_capture)` :1338)

Both calls run inside the single 0.137–0.153s, 125-check suite execution — the second run of one
scenario (two-repo fleet build + one `run_main` invocation) is a small fraction of that budget, not
separately measurable against process noise at this scale. **Measured, negligible.** This is also
B-27's own point: 5g must exercise case 5b's real verdict path itself, under the mutant, or the
"merely raising" defect class it closes stays open — the second run is the fix's mechanism, not
overhead accidentally added on top of it.

## Temp-directory accumulation

`test-factory-claim.py` has 14 `tempfile.mkdtemp(...)` call sites (grep count) and **no
`shutil.rmtree`/cleanup anywhere in the file** — this is pre-existing, unchanged by the diff (the
mkdtemp call sites are identical before and after `fb9a4ac4`; no cleanup was added or removed).
Measured directly: a single run of `test-factory-claim.py` added **109** new `claim-*` dirs under
`$TMPDIR`; a single run of `test-factory-claim-mutation.py` (3 in-process runs) added **327** —
exactly 3×109, confirming the multiplier is proportional, not disproportionate. Sampled per-dir
sizes: `claim-fleet-*` ≈ 4KB (holds `fleet.yaml`), `claim-ws-*` ≈ 0KB (many scenarios never write
into the workspace root itself). Marginal bytes from this diff's added third run ≈ 109 dirs ×
~1–4KB ≈ **well under 1MB per gate invocation** — negligible in absolute terms, and not a new class
of leak (a two-run suite already leaked 218 dirs before this diff; three runs leak 327).
**Not a finding**: fixing it would require editing `test-factory-claim.py`'s fixture builders
(add `atexit`/cleanup), which sits outside this diff's two-file scope and outside my write scope on
this angle; flagging it as new waste introduced by `fb9a4ac4` would be inaccurate — the leak predates
this commit.

## Refused-in-advance: nothing proposes dropping a suite run

No finding here proposes removing `_baseline()`, `_mutation_proof()`, or
`_key_collapse_proof()`/`_mutate_and_run_key_collapse()` to save the ~0.09s. Doing so would drop
the only in-process run that proves the real suite **prints** `FAIL BUG-1290 5b` under the
issue-map-cache mutant (settled item #1 in this dispatch's constraints — the two seams are
deliberately distinct). Any such proposal is refused per the hard rule: an apply that weakens either
gate's ability to report RED is forbidden outright.

## Commands run

```
git -C <worktree> show fb9a4ac4 --stat
git -C <worktree> show fb9a4ac4 -- tests/unit/test-factory-claim.py tests/unit/test-factory-claim-mutation.py
env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py        (x3, timed)
env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim-mutation.py  (x3, timed)
grep -c tempfile.mkdtemp tests/unit/test-factory-claim.py
find $TMPDIR -maxdepth 1 -name 'claim-*' | wc -l   (before/after each suite run)
du -sk <sampled claim-* dirs>
```

No tracked file edited, staged, or committed.
