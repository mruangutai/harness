# Receipt — simplify · reuse · FEAT-2274 plan surface (r-20261121-2-simplify-eng-reuse)

BLUF: 4 reuse findings (all flag-only, plan unchanged). No tasks run; no verify executed (read-only angle).
Angle: reuse. Adjacency: Python gate business logic + extension orchestration.

## R-1 — Unavailable wire line has ~8 deliberate emit sites and no named single emitter
- File/line: plan.yaml T-01 intent (l.121) + D-01 (l.82); existing sites: dispatch-guard.py:143,276,458,913 (+ run-dir SKIPPED 296-301); validate-digest.py:2678,2709,2691; hook_guard harness_boundary.py:603-610.
- Summary: T-01 names only `harness_boundary.py#hook_guard` yet requires every "deliberate unavailable-library/schema/identity branch" to emit the D-01 JSON; each branch today hand-prints its own stderr passthrough sentence.
- Cost: the JSON shape (decision/gate/reason) gets spelled N times; one site that drifts (key typo, missing gate) reads as a pass to the extension, and the per-branch tests (also N) catch only the sites someone remembered.
- Alternative: name ONE emitter beside hook_guard (e.g. `harness_boundary.unavailable(gate, reason)` that prints the JSON line, with hook_guard calling it) and have every deliberate branch call it. Where the library itself is the thing that failed to import (dispatch-guard.py:273-278), say that site is the one inline exception.
- Disposition: fold-in (T-01 intent / files).

## R-2 — Gate identifier: D-01 says script stem; hook_guard's existing `name` for validate-digest is "check-digest"
- File/line: validate-digest.py:2795 `hook_guard(hook_mode, "check-digest")`; pinned by tests/integration/test-validate-digest.py:5169,5295,5353 and test-inflight-registry.py:255.
- Summary: reusing hook_guard's existing `name` argument as D-01's `gate` yields "check-digest", contradicting "gate equal to the script filename without .py" and SC-01 "naming that gate"; recomputing it separately forks two names for one gate.
- Cost: either the notice names a gate that does not exist as a script, or a second name source appears and the two drift; changing `name` breaks the stderr-prefix assertions above silently outside T-01's listed anchors.
- Alternative: state in T-01 that the JSON `gate` is derived from the script path in the one emitter (R-1) while the stderr prefix `name` keeps its current spelling, so validate-digest tests stay untouched.
- Disposition: fold-in.

## R-3 — Extension-side narrow-gate applicability is a third spelling of command matching
- File/line: plan.yaml T-01 intent (l.123, "Build-design assignment"); gh-close-gate.py:206 `denies`, plan-sign-gate.py `_raw_pattern`/words, branch-create-gate.py:147 `_branch_name`; extension precedent harness-hooks.ts:1254-1255 (`/\bmerge\b/` prefilter before merge-gate.py).
- Summary: the extension must classify applicability when the gate cannot even spawn, so it needs its own matcher; the plan defers the arrangement to build time and does not name the existing mechanisms.
- Cost: TS matcher + Python `denies` must be edited in lockstep; the one nobody remembers goes stale, and a coarse TS over-match would fail closed on unrelated Bash (the plan forbids exactly this) while an under-match fails open on the protected action.
- Alternative: require the TS matcher to be a documented over-approximation modeled on the harness-hooks.ts:1254 prefilter precedent, and its cases (matching + unrelated) to be derived from the command corpora the three existing gate suites already protect rather than hand-picked new strings; record the pairing so a change to a gate's `denies` points at the prefilter.
- Disposition: fold-in (T-01 build-design assignment sentence).

## R-4 — New runtime suite re-invents the isolated-gate-bin fixture four gates already hand-copy
- File/line: tests/integration/test-gh-close-gate.py:253-265; test-branch-create-gate.py:247-261; test-plan-sign-gate.py:537 (`copytree(BIN, mbin)` + append an injected `resolve_root` raise to harness_boundary.py); plan.yaml T-01 files l.114 (create test-omp-native-gate-runtime.py).
- Summary: "copied isolated gate roots" with injected dependency faults is already the repo idiom, spelled privately in each narrow-gate test; the plan adds a fourth copy and does not name the three FEAT-65 "loud and nonzero, not 0/2" cases, whose asserted contract (`returncode not in (0,2)`) directly contradicts the new closed-after-match contract.
- Cost: obsolete FEAT-65 assertions either remain and go red, or get quietly rewritten without a named replacement; the pre-guard/dependency-failure matrix then exists twice (old cases + new suite) with differing fixtures.
- Alternative: name those three cases as converted (their injection becomes the matching-command dependency-failure case; add the unrelated-command-bypasses control beside it), and host a shared `isolated_gate_bin(mutate)` helper in an existing support module (tests/integration/check_domain_support.py precedent) instead of a fourth private copy.
- Disposition: fold-in (T-01 intent test paragraph); briefing-row not needed.

## Checked, no finding
- hook_guard(`fail="closed"`) already exists (harness_boundary.py:604) and merge-gate uses it (merge-gate.py:596): plan correctly reuses it for narrow gates; nothing to flag.
- Extension `jsonLines`/`parseDecision` (harness-hooks.ts:99-121) already parse standalone `decision` JSON lines; D-01's shape reuses that path.
- Existing additionalContext return (harness-hooks.ts:1571, SCHEMA_INJECTION_NOTE) is the composition seam; plan's "compose, do not overwrite" reuses it.
- DEC-234 prologue duplication is accepted by plan/BRIEF; not flagged.
