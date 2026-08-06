# Code review — FEAT-09, delta cycle (VF-1 fix only)

base `4918d06` (already-reviewed panel pin) · review_sha `7a1bff8`. Scope pinned by user ruling to
`git diff 4918d06..7a1bff8 -- .claude/ docs/`: exactly 2 files, 34 lines. Confirmed
`git diff 7a1bff8..HEAD --stat -- .claude/ docs/` is empty, so working tree == pinned bytes for both
files reviewed. `git log 4918d06..7a1bff8` has no `[harness:human]` marker; the fix commit `7218d63`
is main-session-direct under the DEC-174 carve-out, which is a hand edit but explicitly the org's
sanctioned lane for this file, not an unreviewed bypass.

## Verdict: PASS, severity_max low, nothing gates

## Stage 1 — spec compliance

Traces cleanly to VF-1 / SC-04 (`BRIEF.md:48-49`). The diff is exactly: one functional line
(`unset HARNESS_RESOLVE_PATH` in `check-domain.sh`'s `else` branch) + an explanatory comment block,
plus two new test cases. No scope creep: VF-2 (the `Edit`-bypasses-the-shape-gate defect, `:376`) is
explicitly left untouched — confirmed the diff never touches that region — and `STATE.md:48-56`
correctly records VF-2 as a separate, still-open design question, not silently folded into this fix.

**Q1 — does the fix make SC-04 true as written?** Yes, and it makes it *stronger* than the literal
wording requires. SC-04 only constrains the clean-argv case (no `--resolve`, clean stdin payload).
The bug was that mode selection actually ran on `os.environ.get("HARNESS_RESOLVE_PATH") is not None`
(`check-domain.sh:146-147`), not on argv, so an inherited environment variable — present or empty —
silently satisfied SC-04's premise while violating its intent. The `unset` closes that regardless of
what the calling environment carries, which is a superset of what SC-04 literally asks for, not a
narrower fit to the letter. Verified empirically, not just by reading: reconstructed the pre-fix
script via `bash <(git show 4918d06:...)` (no file writes — Bash write access is denied to reviewers
by design) and reproduced the exploit myself against a payload file: clean env exits 2, env var set to
a real path exits 0 (prints `harness-dev-ops`, silently answering a *resolve* query instead of
enforcing), env var set to `""` also exits 0 (prints `NOBODY`) — matching the STATE.md write-up
exactly. Same three probes against the post-fix script (working tree, confirmed identical to
`7a1bff8`) all exit 2.

## Stage 2 — code quality, and the specific reachability questions asked

**Q2 — any remaining path into the resolve branch without `--resolve` in argv?** None found. The
`unset` runs in the bash wrapper *before* `python3` is exec'd (`:48-54`), and every hook fire is a
fresh process (`.claude/settings.json:23` registers the hook as a `command` type with no arguments) —
so there is no window for the variable to survive from one invocation into the next, and no shared
shell state to leak through. This is a structural guarantee from the ordering, not merely an
empirical absence — my nested-invocation probe (export in one `check-domain.sh` exec, then a second
exec in the same parent shell) corroborates it but the ordering argument is what actually establishes
it. Also independently confirmed no other file in the repo reads `HARNESS_RESOLVE_PATH`
(`grep -rn HARNESS_RESOLVE_PATH`) — the sibling `bash-write-guard.sh` does not consume it.

**Q3 — do (i)/(j) guard the thing that broke, or only its current spelling? (the mode-3 question)**
The two cases use different *values* (a real path, and the empty string) — for the predicate
`is not None`, {absent, empty, non-empty} is the complete equivalence-class partition, and (g)/(h)
already cover "absent." So the value axis is not the blind spot.

The real shared technique is the **assertion**, not the setup: both (i) and (j) check only
`r.returncode == 2` (`test-check-domain.py:485-489`). In this script, exit 2 is produced by at least
five distinct sites, four of them *inside* the resolve branch itself before `domain_check()` is ever
reached: no-manifest (`:156-158`), duplicate-key (`:163-166`), parse-error (`:167-170`), plus
`require_or_bootstrap` failure and the real `BLOCKED` at `domain_check()` (`:360`). A reimplementation
that keeps the env var readable (i.e., does not actually close VF-1) but happens to exit 2 from one of
the *other* resolve-branch sites — under a slightly different manifest/agent/root condition than the
one (i)/(j) exercise — would read as green while the underlying leak is still open. The missing
assertion is that stderr carries the specific `BLOCKED — harness-documentor may not write` message,
which is exactly the convention this same suite already established at (c)/(d): *"an exit-0-with-
empty-stdout resolver passes any check that only reads the exit code, and that is precisely the
fail-open shape."* (i)/(j) don't apply their own suite's stated principle to themselves. **Severity:
low — does not gate.** Today's implementation is correct (verified above); this is a test-completeness
gap for the next regression, not a live defect.

**Q4 — did the fix break `--resolve`, particularly the stdin rule?** No. The `--resolve` branch
(`if [ "${1:-}" = "--resolve" ]; ... export HARNESS_RESOLVE_PATH="${2:-}"`) is byte-identical across
`4918d06..7a1bff8` — the diff only adds a comment block above it and the `unset` in the sibling
`else`. Confirmed behaviourally too: ran `--resolve` against a process-substitution open pipe nobody
writes to (no file created — reviewer is read-only) and it answered immediately without blocking,
matching SC-03.

**Q5 — is the comment accurate, and does it explain why?** Mostly, with one overstatement. The
mechanism description (`:37-44`) is accurate and cites real line numbers/behaviour, verified above.
The rejected-alternative note (`:46-47`, "do NOT branch on argv instead: `sys.argv[2]` is already
consumed... as the agent identity") states a true fact (`:118`, `:135`) but draws a stronger
conclusion than the code supports: `.claude/settings.json:23` registers the hook with **zero
arguments**, so in every real invocation `${1:-}` → `sys.argv[2]` → `argv_agent` is always `""`, and
an argv-based mode check (`sys.argv[2] == "--resolve"`) would not actually collide with anything
today. Informational only — the env-based fix is the right one regardless, and the comment doesn't
misdescribe the mechanism itself, only slightly oversells the reason for avoiding the alternative.

## Findings summary

| # | Severity | Gates? | Summary |
|---|---|---|---|
| Q3 | low | no | (i)/(j) assert exit code only; a reimplementation exiting 2 from a *different* resolve-branch failure site while still leaking the env var would pass green. Add a stderr-contains-`BLOCKED` assertion, matching this suite's own (c)/(d) convention. |
| Q5 | info | no | Comment's stated reason for rejecting an argv-based mode check is stronger than the code supports (`settings.json` registers zero args, so no real collision exists today). Mechanism description itself is accurate. |

Gates checked and independently re-run in the worktree (not read from the claim): `run-unit-tests.sh`
→ 32/32 PASS lines across all 13 scripts including `test-check-domain.py`'s 10/10 `--resolve` cases;
`check-docs.sh` → exit 0; `check-state.sh` → exit 0; `gen-decisions-index.py --check` → exit 0. All
four match the evidence handed to me.
