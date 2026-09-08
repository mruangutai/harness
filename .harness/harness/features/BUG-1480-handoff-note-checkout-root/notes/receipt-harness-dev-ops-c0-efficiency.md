# EFFICIENCY angle — BUG-1480 (c0)

**Conclusion: no findings. The added work is inside the interpreter-start/measured noise floor on both files. `apply` count 0.**

## The specific question: does `_checkout_root` re-running `checkout_relative` cost anything real?

**Blast radius — narrow, not per-write.** `_checkout_root(absolute_path)` is called from exactly one
site, `.claude/skills/harness/bin/check-domain.sh:1761-1762`, inside `if RE_HANDOFF.match(rel):`
(`check-domain.sh:1744`). It fires only when the write under evaluation is a
`notes/handoff-<phase>.md` (DEC-159) — a capped-60-line file written once per phase seam per
feature, not on every governed write. Every other write (STATE.md, feature.json, plan.yaml, digests,
CLAUDE.md, arbitrary files) never reaches this line. This is the "one-shot, not hot-path" case the
angle distinguishes from a per-write cost.

**The re-import is a `sys.modules` dict lookup, not a reload.** `_norm` (line 1143) and
`_checkout_root` (line 1156) each do `import harness_boundary as _hb` inside their own function
body; nothing calls `importlib.reload` or clears `sys.modules` between them. Measured directly:

```
$ cd .claude/skills/harness/bin && python3 -c "
import sys, time, os
sys.path.insert(0, os.getcwd())
import harness_boundary as hb
N = 5000
t0 = time.perf_counter()
for _ in range(N):
    import harness_boundary as hb2
t1 = time.perf_counter()
print('import x%d: %.4f ms total, %.6f ms/call' % (N, (t1-t0)*1000, (t1-t0)*1000/N))
"
import x5000: 0.3888 ms total, 0.000078 ms/call
```
0.078 µs/call — a dict lookup, confirmed, not a second module load.

**`checkout_relative` itself, measured the same way (5000 iterations, same script):**
```
checkout_relative x5000: 490.0593 ms total, 0.098012 ms/call
```
≈0.098 ms/call here, consistent in order of magnitude with the cost the function's own docstring
already records and settles (`harness_boundary.py:138-140`: "over 2000 iterations the deleted regex
took 0.3 ms in TOTAL against 46.8 ms in total here — 0.023 ms per write"). `checkout_relative` does
one `worktree_owner` lookup (reads a `.git` pointer file) plus an `os.path.relpath`/`realpath` — no
git subprocess, no tree walk beyond that.

**Against the baseline.** The hook's own comments record ~38 ms of interpreter start against a ~42 ms
total call (`check-domain.sh` surrounding prose, cited in the dispatch). `_checkout_root`'s one extra
call adds ≈0.1 ms — about 0.25% of the ~42 ms baseline, and gated behind a write class that happens
once per phase, not per write. This is inside the noise, not outside it.

## Rest of the angle — both files

- **Startup cost:** `_checkout_root` is a plain top-level `def`, defined but not called at import
  time — same shape as `_norm` immediately above it (check-domain.sh:1151). Defining a function adds
  no measurable startup cost; it is not invoked until the handoff branch runs. No finding.
- **Repeated I/O:** the one extra `checkout_relative` call repeats one `worktree_owner` file read
  that `_norm` already performed moments earlier for the same `absolute_path` — covered above as the
  cost in question. No other repeated I/O in the diff.
- **Closures / long-lived objects:** `_checkout_root` and `_norm` capture only `root` from module
  scope (already captured by `_norm`, `_show`, and dozens of other helpers in this file) — no new
  closure-held scope, nothing added to what already lives for the process lifetime.
- **Test file (`tests/integration/test-check-domain.py`):** `_handoff_worktree_cases` calls
  `make_linked_worktree` once (two `os.makedirs` + two small file writes, no git subprocess — see
  its own docstring, line 139) and `_invoke_handoff`/`fire` three times (three subprocess spawns of
  the real hook, each ≈40 ms per the baseline above). `make_linked_worktree` is already called 20+
  times elsewhere in this same suite file for the identical shape; one more call is not new work in
  kind, only in count. Three more subprocess spawns (~120 ms) against a suite that already spawns
  the hook subprocess hundreds of times (402 `ok` lines) is not a measurable fraction of total suite
  wall-clock. Did not re-run the full suite for this alone — the number needed (per-call subprocess
  cost) is already established in the dispatch's own baseline and confirmed above; re-running only to
  time three more calls among hundreds would be the redundant suite run this angle itself warns
  against.

## Findings

None. Zero `apply`, zero `defer`.
