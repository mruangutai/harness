# ALTITUDE receipt — BUG-1306 hermeticity diff (dev-ops, c0)

**Verdict: sound at this feature's scope; one real depth gap exists and is a briefing-row, not a fold-in.**

## Invoker identified (grounding for the depth judgement)

`tests/integration/test-plan-merge.py` is started by `.claude/skills/harness/bin/run_pool.py:59-63`
(`run_one`): `subprocess.run([sys.executable, path], stdout=..., stderr=..., text=True)` — **no
`env=` kwarg**, so it inherits the calling process's full ambient environment for every unit and
integration test file. `run_pool.py` is invoked by `.claude/skills/harness/bin/run-unit-tests.sh:47`
(`exec python3 "$BIN_DIR/run_pool.py" --mutation-check "$BIN_DIR" -- "${SCRIPTS[@]}"`), which is
itself the sole `KIND=all|unit|integration` entry point (lines 16-31). This is the one place all
test processes actually start; it is not scrubbing `HARNESS_AGENT_TYPE` or anything else.

Grep across `tests/` confirms `test-plan-merge.py` is the ONLY file that subprocess-invokes
`plan-merge.py sign-approval` (or any other `HARNESS_AGENT_TYPE`-sensitive verb). `test-plan-sign-gate.py`
exercises the *hook* through a fake `gate()`, not the real command; `test-check-domain.py` and others
only reference `plan-merge.py` by name in denial-routing prose. So D-01's one-file confinement is
factually correct today — nothing else needs this fix yet.

## Finding 1

- **File/line:** `tests/integration/test-plan-merge.py:41` (the module-level
  `os.environ.pop("HARNESS_AGENT_TYPE", None)`).
- **Summary:** The hermeticity rule is stated and enforced at the per-file level (one test
  module's import-time pop) rather than at the actual subprocess boundary that starts every test —
  `run_pool.py:61`'s bare `subprocess.run([sys.executable, path], ...)`, which inherits the ambient
  env unconditionally for all unit and integration files alike.
- **Concrete cost:** There is no single authoritative statement of "a test process must not
  inherit `HARNESS_AGENT_TYPE`" — it exists only as this one file's comment + pop. A future test
  file that shells out to another identity-gated verb (a second `sign-approval` caller, or any
  future command that reads `HARNESS_AGENT_TYPE`) will hit the identical agent-vs-human asymmetry
  BUG-1306 fixes here, and will have to independently rediscover and re-implement the same pop —
  nothing forces it, and D-04 declines a tree-wide lint that would catch the omission.
- **Alternative:** Scrub `HARNESS_AGENT_TYPE` once in `run_pool.py:run_one`, at the actual process
  boundary, so every test subprocess starts hermetic regardless of which file it is — one
  authoritative home instead of a rule copied file-by-file as each new need surfaces.
- **Recommendation: briefing-row.** The "put it in the runner" remedy is the deeper fix, but it
  directly contradicts this feature's settled D-01 (fix confined to this one file) and D-04 (no
  tree-wide environment lint) — correct decisions for BUG-1306's scope, given only one file needs
  it today. Route to whoever next touches `run_pool.py` or adds a second identity-sensitive
  integration test.

## Accepted residuals — judged, not re-raised

- The `plan-merge.py line 1188` citation in the new comment (lines 35-41) is a known, accepted
  aging reference (LEAVE, per shared context) — not re-raised as a finding.
- D-04 (no tree-wide fix): right to accept for this feature, since the grep above shows only one
  file is affected today. The compensating control **is** named in-file ("Popping once here covers
  run_apply, run_verb, and any raw subprocess.run or Popen a future case writes, with no
  per-call-site rule") — that covers every current and future call site *inside this one file*, but
  does not and cannot cover a second file. That gap is exactly Finding 1.
- Docstring update to `run_verb` (lines 149-151) is a straight, accurate reflection of the new
  import-time pop — no altitude issue.

## Nothing else found

No other altitude issues in the two-hunk diff.
