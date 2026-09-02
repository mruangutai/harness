# SIMPLIFY — EFFICIENCY angle — FEAT-51 — c1

**BLUF:** `plan-sign-gate.py`'s T-07 deferral held — measured, the import cost is paid only on
a verb match, ~0 ms marginal for the common case. `check-domain.sh`'s own new quarantine block
did **not** copy that pattern: it imports `inflight_registry` (which drags in `harness_merge` →
`tempfile`/`shutil`/`zlib`/`bz2`/`lzma`) unconditionally for every `Write`/`Edit`/`NotebookEdit`
by a governed agent, not only when the target is actually a canonical artifact. Measured
+16–24 ms on an already-known-heavy per-write hook. One finding, report-only (DEC-174). No
findings in `quarantine.py` or `run-unit-tests.sh`.

**findings_count: 1**

---

## Lead question: did T-07's deferred import hold in `plan-sign-gate.py`?

**Yes, verified by direct measurement — the import is genuinely deferred and costs nothing on
the common path.**

- Module top-level (`.claude/skills/harness/bin/plan-sign-gate.py:26-30`): only `json, os, re,
  sys` — no `inflight_registry` at import time, and no top-level file I/O.
- `import inflight_registry as _reg` sits inside `quarantines()`
  (`plan-sign-gate.py:337, 349`), reached only *after* `_invocation(toks)` has already matched
  `plan-merge.py <mutating-verb>` or `quarantine.py adopt` **and** `_file_arg`/`_checkout_rel`
  resolved a `.harness/`-rooted path (`plan-sign-gate.py:308-333`). A non-matching command
  never reaches the import.

Measurements (`subprocess.run` around `python3 plan-sign-gate.py .` with stdin payload, 200
runs each, this machine):

| payload | avg per-call |
|---|---|
| main session (`agent_type` empty, exits at line 74 before any parsing) | 22.408 ms |
| subagent, non-matching command (`git status`) — `quarantines()` runs, no import | 22.477 ms |
| subagent, matching command (`quarantine.py adopt --file …`) — import fires | 33.065 ms |

Isolated import cost, to explain the ~10.6 ms delta above:

```
$ python3 -c "pass"                              →  19.721 ms  (bare interpreter)
$ python3 -c "import inflight_registry"          →  32.377 ms  (+12.656 ms for the import)
$ python3 -X importtime -c "import inflight_registry" | tail -1
import time:       640 |      15577 | inflight_registry   (cumulative 15.577 ms, incl. harness_merge → tempfile/shutil/zlib/bz2/lzma/random)
```

The non-matching-vs-main-session gap (22.477 ms vs 22.408 ms = 0.07 ms) is noise, not a real
cost — confirming the deferred import pays **nothing** for the overwhelming majority of Bash
calls in a session, which never touch `plan-merge.py`/`quarantine.py` at all. T-07's intent is
met in the shipped code.

## Finding 1 — `check-domain.sh` imports unconditionally on every governed write, not only canonical ones

- **file/line:** `.claude/skills/harness/bin/check-domain.sh:1680-1710` (the `# FEAT-51:` block);
  specifically the `import inflight_registry as _reg` at line 1686, which sits *before* the
  `canonical_artifact()` match check at line 1687.
- **summary:** unlike `plan-sign-gate.py`'s deferred-import pattern in the same diff, this
  block imports `inflight_registry` for every `Write`/`Edit`/`NotebookEdit` by a governed
  (`harness-*`) agent as soon as a `target` exists — before checking whether that target is
  even one of the four canonical basenames (`plan.yaml`, `BRIEF.md`, `feature.json`,
  `STATE.md`). Most governed writes are source/test/notes files, not those four.
- **concrete cost, measured:** end-to-end `check-domain.sh` pre-mode timing (subprocess,
  80 runs, governed agent, non-canonical Write target) —

  | tree | avg per-call |
  |---|---|
  | HEAD (this diff) | 66.567 ms |
  | base (`0bc57c88`) | 42.987 ms |

  A repeat run showed a similar gap (66.313 ms vs an isolated 50.398 ms base sample). The
  delta is noisy across runs (16–24 ms) but consistently attributable to the unconditional
  `import inflight_registry` — this file's own T-13 comment (line ~91-101) already records the
  full governed path as a known-heavy ~104.7 ms hook, so this adds a further ~15-25% to an
  already-expensive per-write cost, and it is paid on writes the new quarantine logic will
  immediately discard as irrelevant (non-canonical target → `_artifact is None` → no-op).
  This hook fires on every `Write`/`Edit` tool call from every governed agent for the rest of
  the session — not a one-shot cost.
- **alternative:** gate the import behind the same cheap, import-free basename check
  `plan-sign-gate.py` effectively performs via `_invocation()` before it ever imports the
  module — e.g. extend the existing `if` guard with
  `and os.path.basename(_norm(target)) in ("plan.yaml", "BRIEF.md", "feature.json", "STATE.md")`
  before the `try: import inflight_registry as _reg` line, so the import (and the transitive
  `harness_merge`/`tempfile`/`shutil`/`zlib`/`bz2`/`lzma` load) only fires for the rare write
  that could plausibly be a canonical artifact.
- **applicable:** report-only (`check-domain.sh` is DEC-174 report-only; no squad may edit it).

## Other surfaces checked — no findings

- **`quarantine.py`** (writable): `cmd_list` stats each glob hit once (`os.path.isfile`,
  `os.path.getmtime`), `cmd_adopt` reads the quarantined file once and either shells to
  `plan-merge.py` or calls `harness_merge.locked_update` once, `cmd_discard` does one
  `os.path.realpath` + one regex + one `shutil.rmtree`. No repeated stat/read of the same path
  within a single invocation.
- Minor, sub-threshold note (not a finding): `plan-sign-gate.py`'s `quarantines()` calls
  `_reg.canonical_artifact(rel)` directly and then, on the `TOOL` branch, calls
  `_reg.quarantine_rel(rel, agent, session)`, which recomputes `canonical_artifact(rel)`
  internally (`inflight_registry.py:274-282`) — one redundant `re.fullmatch` per matching
  invocation. A compiled-regex `fullmatch` on a short path is low-single-digit microseconds;
  this is far below "hot-path milliseconds" and not worth a finding.
- **`run-unit-tests.sh`** (writable): the diff only appends `"test-quarantine.py"` to the
  existing `INTEGRATION_SCRIPTS` array literal — no new work added to any run, and per the
  dispatch's own framing a deliberate full-suite run at this boundary step is evidence, not
  waste. No finding.
- **Closures/long-lived objects:** nothing in the diff builds a closure capturing a large scope
  that outlives its call — `quarantine.py`'s only closure is
  `lambda _base, payload=payload: payload` passed straight into `harness_merge.locked_update`
  and not retained afterward. No finding.

## Open questions

None.
