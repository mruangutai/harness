# Code review — BUG-1309-mirror-build-entry — cycle 4 — review_sha af13278002da829af3eebc63bcd9e0e1c7161db6

## BLUF

**PASS.** The cycle-3 MED (an unrelated feature's malformed `feature.json` denying a merge that
matches no feature at all) is fixed and verified by execution against the shipped `merge-gate.sh`.
One NEW MED, not gating: the fix narrowed the outer `except Exception` against exactly the failure
mode cycle 3 found (a bad record read inside `feature_for`'s own loop) but did not narrow the
try's SCOPE — it still wraps `head_branch()`'s environmental resolution, which runs *before* any
feature match. When that resolution itself raises (proved via a genuinely broken `git` binary, not
a bad record), the identical un-interpolated "this feature" bystander deny reappears for a merge
that owes nothing — defeating DEC-138 in exactly the moment (GitHub unreachable) it exists to cover.
Reachability is bounded: it requires `gh` resolution to already have failed *and* the local `git`
subprocess call to raise `OSError` (binary missing/unspawnable), not merely `gh` alone.

Single commit since the last pin (`0f8ec4bd`): `af132780`, author Mike Ruangutai, no
`[harness:human]` tag, in scope for this cycle.

## Stage 1 — spec compliance: PASS

Diff is exactly the two files `git show --stat` reports (5/1 in `merge-gate.py`, 12/6 lines split
in the test file). No REQ/D touched by this remediation is left unimplemented; no scope creep. This
pin's job is closing cycle 3's F1 (an innocent-bystander deny that misattributes "this feature");
judged against that job below.

### 1. The three-posture reconstruction — ONE fixture, all three states, driven through the shipped `merge-gate.sh`

Fixture (`/tmp/bug1309-triple-*`), one `.harness/harness.json` (`sync: true`, `repo: acme/widgets`),
git HEAD on `feature/healthy`, three feature directories:
- `FEAT-HEALTHY-owes-nothing` — `branch: feature/healthy`, `github.build_entry: opened`, healthy plan.
- `FEAT-OWING-cannot-eval` — `branch: feature/owing`, `github: {}` (no build_entry), **0-byte `plan.yaml`**.
- `FEAT-9002-unrelated-malformed` — `feature.json` is `[]` (a JSON list, not an object), no branch field at all.

| # | Command | Env | exit | decision emitted? | reason / stderr |
|---|---|---|---|---|---|
| 1 (matched, can't eval) | `git merge feature/owing` | — | 0 | **yes, deny** | `merge-gate: could not evaluate FEAT-OWING-cannot-eval's Build-entry receipt, so this merge is denied. Repair the feature record and re-run the merge.` |
| 2 (gh outage, owes nothing) | `gh pr merge 7` | `GH_BIN=/nonexistent/gh` | 0 | **no** (stdout empty) | stderr: `merge-gate: could not verify this merge - the head branch could not be resolved through gh ([Errno 2] No such file or directory: '/nonexistent/gh') and the local branch feature/healthy owes no build-entry receipt; allowing it, because GitHub is a mirror and never a gate (DEC-138).` |
| 3 (malformed record, different feature) | `git merge feature/no-match-here` | — | 0 | **no** (stdout AND stderr both empty) | *nothing* — the `[]` record is invisible; the merge is decided on `FEAT-HEALTHY`/`FEAT-OWING`'s own records alone, neither of which matches |

Mechanism traced, not assumed, for #1: `recovery_command_for` (`feature_schema.py:324`) calls
`harness_yaml.load_file` on the 0-byte `plan.yaml`, gets `None`, then `plan.get("status")` raises
`AttributeError` **outside** that function's own narrow try (which wraps only the `load_file` call)
— caught by `main()`'s outer `except Exception` (`merge-gate.py:156-157`) *after* `feat` was already
set to the matched feature's basename at line 140. For #3: `feature_for` (`merge-gate.py:105-106`)
skips the non-dict record via the new `isinstance` guard before ever reaching `document.get("branch")`,
so the malformed file never participates in matching at all, regardless of `glob.glob`'s enumeration
order.

### 2. Hunting a pair conflict — the closed window confirmed closed, a narrower one found open

**Re-probed cycle 3's exact closed window** (a bystander deny from a malformed record belonging to
a *different* feature): confirmed closed, both directly (posture #3 above) and by running the
shipped 18th test's identical fixture against the immediate parent commit — see §4.

**Probed the pre-match window the fix left untouched.** `feat = "this feature"` (`merge-gate.py:131`)
sits *before* the `try` that wraps `import feature_schema`, `head_branch(...)`, and
`feature_for(...)`; `feat` is only reassigned at line 140, strictly after a feature has matched
(`document is not None`). Any exception raised *before* that reassignment — regardless of cause —
still deny-with-the-literal-placeholder. `feature_for`'s per-record read is now guarded, but
`head_branch` → `local_branch(cwd)` (`merge-gate.py:69-72`) is not: it calls
`subprocess.run(["git", "-C", cwd, "rev-parse", ...])` with **no** `except OSError`, unlike
`gh_head` two functions above it which explicitly catches `OSError` for exactly this reason.

**Executed, not asserted.** Same triple fixture, HEAD still `feature/healthy` (an "owes nothing"
feature, posture #2's exact scenario), same broken `gh` (`GH_BIN=/nonexistent/gh`), but `PATH`
restricted to a directory holding only `python3` and `dirname` — no `git`:
```
$ echo '{"tool_input":{"command":"gh pr merge 7"}}' | HARNESS_PROJECT_DIR=$ROOT GH_BIN=/nonexistent/gh \
    PATH=/tmp/no-git-bin bash merge-gate.sh
exit=0
stdout: {"hookSpecificOutput":{...,"permissionDecision":"deny","permissionDecisionReason":
  "merge-gate: could not evaluate this feature's Build-entry receipt, so this merge is denied.
   Repair the feature record and re-run the merge."}}
stderr: (empty)
```
`local_branch` raised `FileNotFoundError` (an `OSError` subclass) resolving `git`; it propagated
through `head_branch` into `main()`'s outer `except`, before any feature ever matched — the exact
un-interpolated "this feature" wording cycle 3 first found, on a feature (`FEAT-HEALTHY`) that
records `build_entry: opened` and owes nothing. **Posture #1's contract ("internal error on a
matched feature denies, naming it") and posture #2's contract ("failed GitHub read on a feature
owing nothing allows, with the DEC-138 line") conflict here**: the error is not on the matched
feature's own record at all, it is in environmental resolution that runs *before* matching, and the
deny both misattributes the cause and defeats the DEC-138 escape hatch in precisely the scenario
(GitHub unreachable) that hatch exists for.

**Reachability, honestly bounded.** This needs `gh` resolution to already have failed (common:
network blip, `gh` unauthenticated, GH outage — DEC-138's whole premise) **and** the `git` subprocess
call itself to raise `OSError` rather than a clean non-zero exit — realistically `git` unspawnable
(missing from `PATH`, permission-stripped, or a resource-exhaustion condition like `EMFILE`/`ENOMEM`
during fork/exec). Not reachable from feature-record content alone; requires a degraded execution
environment. Rated **MED**, same tier as cycle 3's F1 and for the same reason (bounded, environment-
level trigger, not attacker/misconfiguration-controllable) — not **must_fix**, but it is the same
defect *class* recurring under a different trigger, because the remedy fixed the specific failure
cycle 3 demonstrated rather than narrowing the try's scope to "this feature's own record" as its own
framing claims.

### 3. What else notices a corrupt (non-object) `feature.json`

`merge-gate.py`'s skip is intentionally silent **for that one merge only**. Checked what else in the
system would notice the same corrupt record, by name:

| Consumer | Detects `[]`-shaped `feature.json`? | How |
|---|---|---|
| `check-state.sh` INV-6/7/8/12 loop (`:604-627`) | **Yes** | `harness_yaml.load_file` succeeds (valid YAML), then an explicit `isinstance(doc, dict)` check at `:625` reports `"...is not a YAML mapping."` |
| `check-state.sh` INV-17 handoff-shape loop (`:1153-1158`) | No (but irrelevant) | Reads `harness_yaml.load_file(fy) or {}` with no isinstance check, but the loaded value (`_doc`) is never referenced again in that loop — station comes from `plan.yaml`, not this document — so this is not a real detection gap, just an unused read |
| `validate-feature-json.py` (schema `"type": "object"`) | **Yes** | jsonschema rejects a list against an object-typed schema; sweeps *every* `feature.json` on disk with no arguments, wired as its own dedicated step in `.github/workflows/tests.yml:101` — but that is a scheduled/CI check, not synchronous with the merge |
| `gh-sync.py`'s `load_recorded` (`:518-548`) | **Yes, loudly** | Explicitly documented 4th state: a non-mapping document is treated as the ERROR case, `raise SystemExit`, never as "nothing recorded" |
| `post-merge-sweep.sh`'s per-record handler (`:213-218`) | **Partially** | `except (OSError, json.JSONDecodeError)` does NOT catch a valid-JSON-wrong-type read; `feature_doc.get(...)` then raises `AttributeError` — but the caller's per-record loop (`:279-283`) wraps `_handle_record` in a blanket `except Exception`, prints `"post-merge-sweep: ERROR handling {path}: {e}"`, and moves on. The record is reported (generically, not by a targeted message) and — critically — the worktree is NOT removed on this path, which is the safe direction |
| `factory_claim.py`'s `_BlockerCache.issue_number` (`:142-158`) | **Yes, gracefully** | Already `isinstance(doc, dict)`-guarded; a non-dict document degrades to "no issues", not a crash |

**Not "nobody notices" — but nobody notices *synchronously, at merge time*.** By design (DEC-174:
validators are main-session-direct, never auto-run by the harness), a corrupt record sitting on disk
is invisible until an operator next runs `check-state.sh`, `gh-sync.py`, or the CI schema sweep
against it. Between the corrupting write and that next run, only `merge-gate.py`'s own posture
(now: silently skip if unrelated, deny naming the feature if matched) governs what a merge attempt
sees. Not re-raising BUG-1080's already-dispositioned, separately-tracked backlog item (Q3 in that
feature's QA notes) about `check-state.sh`'s YAML-tolerant parser accepting some strictly-invalid
JSON shapes that `validate-feature-json.py` would reject — different failure shape (comments/
unquoted scalars vs. wrong JSON type), already recorded elsewhere.

### 4. Widened beyond the delta; discrimination proven against the parent, not asserted

**Sibling PreToolUse gates re-checked** (`gh-close-gate.py`, `branch-create-gate.sh`,
`plan-sign-gate.py`): none replicate `feature_for`'s per-glob-match pattern (grepped for
`glob.glob.*feature.json` and `isinstance(document` across the three files — no matches); the
defect class stays specific to `merge-gate.py`'s own directory scan, as cycle 3 already established
and this cycle re-confirmed rather than assumed.

**18/18 `ok`, `ALL PASSED`**, `test-merge-gate.py` run directly at this pin.

**Pre/post divergence, executed against `af132780^` (= `0f8ec4bd`, the cycle-3 pin), not merely
asserted.** Built a scratch copy of `bin/` with only `merge-gate.py` swapped for the parent's byte
content (everything else, including `feature_schema.py`, untouched), and ran the *current* 18th
test's exact fixture (healthy feature `entry=opened` + a sibling directory with `feature.json: []`,
merging the healthy feature's own branch) against both:
```
parent (af132780^): exit 0, deny, reason = "...could not evaluate this feature's Build-entry
                     receipt..." (un-interpolated placeholder — the innocent-bystander lockout)
pinned (af132780):  exit 0, no decision emitted, no stderr (silent allow, correct)
```
Genuinely discriminating: the revised case is not vacuous, it fails on the immediate parent and
passes at the pin.

## Stage 2 — code quality: PASS

`code-grade.py --base $(git merge-base origin/main af132780) --head af132780`: **50 PASSING**, 4
gated grade-2 records — `merge-gate.py:122 main` (cyclomatic 17, cognitive 21, ABC 38.7, driver
cyclomatic+cognitive+abc), plus the same three pre-dispositioned test-file grade-2 records cycle 3
already accepted (`test-check-state.py:4621`, `test-hooks-install.py:396`, `test-post-merge-sweep.py:885`).
`main`'s own `GRADE-2 REASON` comment (`merge-gate.py:120-121`, "this is the gate's orchestration
boundary...") is present and unchanged at this pin. No grade-1, no production grade-3-below-bar.
`code_grade: grade_2`.

The delta itself (one `isinstance` guard, one placeholder initialization, one f-string
interpolation) is mechanical, matches the codebase's existing guard style (`feature_for`'s own
`except (OSError, json.JSONDecodeError): continue` right above it), and introduces no dead code, no
duplication, no comment/code drift.

## Findings summary

| # | Severity | Where | Scenario |
|---|---|---|---|
| F1 (cycle 3) | — | `merge-gate.py:104-106` | **Closed.** Verified fixed by execution (posture #3, §1) and by parent-vs-pinned divergence (§4). |
| F2 (new) | MED | `merge-gate.py:131` (`feat` placeholder) + `merge-gate.py:69-72` (`local_branch`, unguarded `subprocess.run`) | A `git`-subprocess `OSError` (binary missing/unspawnable) raised while resolving the head branch, combined with an already-failed `gh` lookup, denies a merge for a feature that owes nothing, with the same un-interpolated "this feature" reason cycle 3 found — reproduced by execution with `PATH` stripped of `git`. Bounded reachability: needs a degraded execution environment, not attacker/record-controllable. |
| F3 (info) | none | `post-merge-sweep.sh:213-218` | A valid-JSON-non-dict `feature.json` is not caught by the narrow `except (OSError, json.JSONDecodeError)`, but the caller's per-record `except Exception` (`:279-283`) reports it generically and keeps the worktree (safe direction) — noted for completeness, not a defect. |

`must_fix: []`. `severity_max: med` does not gate (protocol: `must_fix` empty and `severity_max <
high`).

## Open questions

None blocking. F2 is worth a follow-up — either narrow the `try` in `main()` to wrap only the
per-feature evaluation (starting after `feat_dir, document = feature_for(branch)` succeeds) rather
than the whole environmental-resolution block, or add `except OSError` to `local_branch` mirroring
`gh_head`'s own guard two functions above it — an operator call on priority, not a ship blocker.
