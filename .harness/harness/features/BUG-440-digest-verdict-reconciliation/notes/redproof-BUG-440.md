## INV-37 red proof

Pinned pre-change source: `772790be52774eafe2971f9c44400e18b2d54275`.

Invocation:

```sh
CHECK_STATE_BIN=<isolated-bin>/check-state.sh python3 -c "import importlib.util as u, sys; s=u.spec_from_file_location('t','tests/integration/test-check-state.py'); m=u.module_from_spec(s); s.loader.exec_module(m); sys.exit(0 if m.case_bug440_digest_verdict_reconciliation() else 1)"
```

Verbatim failing output against the pre-change `check-state.sh`:

```text
FAIL - BUG-440 INV-37 reconciles digest verdicts without mutation
        mixed=False; clean=True; output=  VIOLATION  harness/features/FEAT-TEST/runs/G: run is complete but digest.md is missing — the lead's report artifact never landed (DEC-156).
  VIOLATION  harness/features/FEAT-TEST/runs/X/digest.md: does not satisfy the lead digest contract — a successor reads this file, not the transcript (DEC-156). Run bin/validate-digest.py lead on it for reasons.
  note       FEAT-TEST: run dir O exists on disk but feature.json does not record it — orphaned work (interrupted flow?). A resume must reconcile
```

RESULT: RED - case_bug440_digest_verdict_reconciliation() returned False against the pre-change check-state.sh
