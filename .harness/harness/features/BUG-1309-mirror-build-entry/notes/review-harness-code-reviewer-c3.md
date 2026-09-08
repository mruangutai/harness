# Code review — BUG-1309-mirror-build-entry — cycle 3 — review_sha 0f8ec4bda7c96050d2d9bcddb30f96132cde5b54

## BLUF

**PASS.** The one question this cycle exists to answer is answered cleanly, by execution: the gate
now DENIES on an internal evaluation error and still ALLOWS on a failed GitHub read. Both postures
were reconstructed against throwaway `/tmp` fixtures, never the tracked tree. One new MED finding,
non-blocking: the try/except's scope is wider than "this feature's own record" — it also wraps
`feature_for`'s full directory scan, so an unrelated feature's malformed `feature.json` can deny a
merge that owes nothing at all, and the deny message misattributes the cause to "this feature."

`0f8ec4bd` is the only commit since the last pin (`532a20f5`), authored directly by the operator
(Mike Ruangutai), not tagged `[harness:human]` in the message but with no agent name in the
authorship line — treated as in-scope, unreviewed prior to this cycle, per contract.

## Stage 1 — spec compliance: PASS

**(a) Internal error → deny, executed.** Fixture: `FEAT-9001-fixture-non-era`, `build_entry`
absent (owes a receipt), `plan.yaml` overwritten to 0 bytes. `git merge feature/test` via the real
`merge-gate.sh`:
```
exit code: 0
decision: deny
reason: "merge-gate: could not evaluate this feature's Build-entry receipt, so this merge is
         denied. Repair the feature record and re-run the merge."
```
Mechanism traced, not assumed: `harness_yaml.load_file` on an empty file returns `None` (no
exception raised inside `recovery_command_for`'s own try, which only wraps the `load_file` call);
`plan.get("status")` then raises `AttributeError` on the `None`, escapes `recovery_command_for`,
and is caught by 0f8ec4bd's new `except Exception` in `main()`.

**(b) Failed GitHub read on a feature owing nothing → allow, executed.** Fixture: entry=`opened`,
repo pinned, `GH_BIN=/nonexistent/gh`. `gh pr merge 7`:
```
exit code: 0
stdout: (empty — no permissionDecision emitted)
stderr: "merge-gate: could not verify this merge - the head branch could not be resolved through
         gh ([Errno 2] No such file or directory: '/nonexistent/gh') and the local branch
         feature/test owes no build-entry receipt; allowing it, because GitHub is a mirror and
         never a gate (DEC-138)."
```
Control run, same broken `gh`, feature owing a receipt (entry absent): still **denies** with the
receipt-owed reason (`could not verify` does NOT leak into that reason) — matches the existing
`"T-05 gh outage with a feature owing a receipt denies"` case, confirming DEC-138 and the
receipt-owed refusal both survive side by side.

**No collapse of the two postures.** They remain opposite answers to different questions, both
demonstrated by direct execution against the shipped `merge-gate.sh`, not inferred from the tests.

**Regression-test validity, executed against the parent.** Ran the exact parent (`0f8ec4bd^`)
`merge-gate.py` against both new fixtures (0-byte `plan.yaml`; `feature.json` as `[]`). Both crash
uncaught before 0f8ec4bd:
```
case 1: exit 1, AttributeError at feature_schema.py:333 (plan.get on None)
case 2: exit 1, AttributeError at merge-gate.py:103 (document.get on a list)
```
Exit 1 with no JSON output is the project's established "non-exit-2 fails open" PreToolUse
semantics (unchanged, confirmed by the security reviewer at c2's own G-01 disposition) — so both
new cases genuinely discriminate pre/post fix: pre-fix they silently ALLOW via a crash, post-fix
they DENY cleanly. Not vacuous.

**Broad-except hunt — placement and swallowing (per this cycle's charge):**
- (1)/(2) reason quality: the new deny message is honest but generic — it never claims a specific
  wrong cause, so it does not manufacture a confident-but-false diagnosis for the two *matching*
  fixtures (empty plan; non-object feature.json for the merged feature itself). See the one new
  finding below for the case where the message becomes actively misleading.
- (3) wrapper placement: the *outer* `try/except Exception: return` (harness.json + stdin read, at
  the top of `main()`, unchanged by this commit) still silently allows on failure, before a merge
  command is even identified. This is pre-existing and was examined and explicitly dispositioned
  by the security reviewer at c2 as consistent with the project-wide "only exit 2 blocks" PreToolUse
  posture (G-01) — not re-raised here. `merge_ref(command)` itself (called between the two
  try/excepts, outside both) was read in full: every helper it calls (`words`, `is_bin`,
  `direct_merge`, `gh_merge`, `git_merge`, `nested_merge`) operates on token lists and strings with
  no unguarded indexing or file I/O; no failure scenario found there.
- (4) `except Exception` cannot catch `SystemExit`/`KeyboardInterrupt` (both are `BaseException`
  siblings, not `Exception` subclasses) — confirmed against Python's exception hierarchy, and no
  `sys.exit()` call exists anywhere inside the new try block to test regardless. The wrapper sits
  strictly after `if not github.get("sync") or not merge_ref(command): return`, so a non-merge Bash
  command never reaches it — confirmed live, `"T-05 non-merge command allows"` still passes.

**Widened to sibling PreToolUse gates (per this cycle's charge).** Grepped the whole `bin/` tree for
`permissionDecision`/`hookSpecificOutput` emitters: `gh-close-gate.py` and `branch-create-gate.sh`,
both DEC-138-adjacent gates. `gh-close-gate.py`'s `denies()` operates purely on the shell-command
string (tokens, regexes, bounded list indexing) and touches no per-feature file — the specific
defect class here (untrusted *file content* causing an unguarded attribute error) has no analogue
there. `branch-create-gate.sh` is a documented, intentionally different posture — it fails CLOSED on
`gh` unavailability by design ("this one is a gate, not a mirror"), unchanged by this diff, and
found no unguarded exception path in its python one-liners. `plan-sign-gate.py` (a third
PreToolUse gate found in the same directory) governs an unrelated concern — plan-signature and
quarantine enforcement, never touched by any commit in this feature's history — and is out of this
remediation's scope; noted, not investigated further.

**One new finding (MED, not gating):**

`merge-gate.py:104-105` (`feature_for`) — `document.get("branch") == branch` runs **unguarded**
outside the function's own `try/except (OSError, json.JSONDecodeError)`, for **every** glob match,
not only the merge's own target. 0f8ec4bd's new outer `except Exception: deny(...)` in `main()` now
converts that crash into a deny for the *current* merge, regardless of whether the malformed record
belongs to it.

Executed, deterministic reproduction: two feature directories, `FEAT-OTHER-untouched` (healthy,
`build_entry: opened`, branch `feature/unrelated`) and `FEAT-BROKEN-corrupt`
(`feature.json` = `[]`). Merging `feature/no-match-here` — a branch matching **neither** feature,
which `"T-05 branch matching no feature allows"` asserts must always ALLOW — instead:
```
exit code: 0
decision: deny
reason: "merge-gate: could not evaluate this feature's Build-entry receipt, so this merge is
         denied. Repair the feature record and re-run the merge."
```
Run against the parent (`0f8ec4bd^`) on the identical fixture: crashes uncaught (`AttributeError`
at `feature_for`, matching the parent's known fail-open), i.e. it was a **silent allow** before this
fix and is now a **deny of an unrelated merge** after it.

Two compounding problems: (a) **blast radius** — a single malformed `feature.json` anywhere under
`.harness/*/features/*/` (harness_own tree currently has ~76 feature directories per the BRIEF) now
blocks *every* merge project-wide, including ones with no build-entry obligation at all, until that
one unrelated file is repaired; whether an *unrelated but matched* merge is also caught depends on
`glob.glob`'s unspecified enumeration order, so the exposure is not confined to the "no match" case
I used to make it deterministic. (b) **wrong stated cause** — the reason text asserts "this
feature's Build-entry receipt" could not be evaluated, but in the no-match case there is no
"this feature" in the picture at all; the true cause is a different feature's corrupted record,
encountered incidentally while scanning for a match. D-07 explicitly names "a PR matching no
harness feature at all" as a case that must never be caught by an unrelated failure (there, a
GitHub outage) — the same innocent-bystander principle is what this gap now violates, in a
different code path. Rated MED, not high: it requires a `feature.json` that is syntactically valid
JSON but the wrong *type*, which the harness's own governed writers do not produce (a genuinely
malformed write mid-`json.dump` typically yields invalid JSON, which `feature_for`'s existing
`except (OSError, json.JSONDecodeError)` already catches) — reaching it needs an external hand-edit
or a different tool writing to that path.

No REQ/D found unimplemented; no undeclared scope creep (diff is exactly the two files, 49/12 lines,
matching `git show --stat`); no SC-verify-inspection claim touched by this commit.

## Stage 2 — code quality: PASS

`code-grade.py --base $(git merge-base origin/main 0f8ec4bd) --head 0f8ec4bd`: 50 PASSING, 4
gated grade-2 records (`merge-gate.py:120 main`, `test-check-state.py:4621`,
`test-hooks-install.py:392`, `test-post-merge-sweep.py`), all pre-dispositioned with written
`GRADE-2 REASON` comments across earlier cycles — `main` itself carries one at `merge-gate.py:118`
("this is the gate's orchestration boundary..."), confirmed present in the current source. No
grade-1, no production grade-3-below-bar. `code_grade: grade_2`.

`test-merge-gate.py` run directly at this pin: 18/18 `ok`, exit 0 — matches the lead's own claim,
independently reproduced.

Delta-only quality: the diff is a mechanical `try:`/`except Exception: deny(...)` wrap plus two new
test cases exercising the shipped CLI end-to-end (subprocess through `merge-gate.sh`, not a mocked
internals call) — the interface under test is the real one, not reached past. No dead branches, no
duplication, no comment/code drift introduced. Both new assertions are discriminating (proven above
against the parent, not merely plausible).

## Findings summary

| # | Severity | Where | Scenario |
|---|---|---|---|
| F1 | MED | `merge-gate.py:104-105` (`feature_for`), reached via the new `except Exception` in `main()` | An unrelated feature's malformed `feature.json` (valid JSON, wrong type) denies a merge for a branch matching no feature at all — an "innocent bystander" deny with a misattributed reason ("this feature's Build-entry receipt"), demonstrated by execution and by parent-comparison |

No must_fix. `severity_max: med` does not gate per the review protocol (`must_fix` empty and
`severity_max < high`).

## Open questions

None blocking. F1 is worth a follow-up scoping the try/except (or `feature_for`) more narrowly to
the target feature's own record, or catching `AttributeError` specifically inside `feature_for`'s
existing except tuple the way `feature_json` shape errors are handled elsewhere — an operator call
on priority, not a ship blocker for this remediation.
