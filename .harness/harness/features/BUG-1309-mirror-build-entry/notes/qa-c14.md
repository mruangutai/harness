# QA — test-matrix gate over ac2bc0bb (pin c8b23e03)

## BLUF
**FAIL.** The suite is green but does not discriminate a real, confirmed fail-open regression:
`git_merge`'s new token walk grabs the token immediately after `merge`, so any flag placed *after*
the subcommand (`git merge --no-ff <branch>`) is parsed as the branch name. End-to-end through the
real hook, this silently **allows** a merge on a `recovery-required` feature that `git merge <branch>`
correctly denies (reproduced live, mechanism below). No new or pre-existing test uses a post-`merge`
flag. This is `must_fix`, `severity: critical`. Two more contract clauses are also unassessed, and
one new assertion is confirmed non-discriminating by mutation.

## Behaviour → assertion table

| # | Behaviour (contract ref) | Asserted? | file:line | Plausible-bug-would-fail? |
|---|---|---|---|---|
| a | `git_merge` flag-aware walk — flags **before** `merge` (`-C`,`-c`,`--work-tree`) | ✅ new | `test-merge-gate.py:171-178` | yes — reddens pre-change (see §Discrimination) |
| a′ | `git_merge` walk — flags **after** `merge` (e.g. `--no-ff`) | ❌ **UNASSERTED** | — | n/a — confirmed live regression, see §Critical finding |
| b | `feature_for` returns a list | ✅ indirect, via c | `merge-gate.py:111-121` used by all owner tests | yes |
| c1 | `len(owners)>1` → deny | ✅ new | `test-merge-gate.py:149-162` | yes — reddens pre-change |
| c2 | deny names every owner, **sorted** | ⚠️ partial — presence only, not order | `test-merge-gate.py:158-160` | **no** — mutation proof below shows reversed/unsorted order still passes |
| c3 | deny offers no receipt command | ✅ | `test-merge-gate.py:160` (`"gh-sync.py" not in reason"`) | yes |
| c4 | ambiguity deny fires **before** the era-exempt gate | ❌ **UNASSERTED** | — | code verified correct by live probe (`BUG-1030-…` era-exempt + duplicate claimant → still denies), but no test in the suite exercises this; a regression reordering the two checks would ship undetected |
| d1 | single owner + **non-object** noise still allows | ✅ | `test-merge-gate.py:163-170`, and pre-existing `128-135` | yes, but see §Discrimination (does not distinguish new from old code) |
| d2 | single owner + **unreadable** (OSError/JSONDecodeError) noise still allows | ❌ **UNASSERTED** | — | no fixture anywhere in the file writes invalid JSON syntax or an unreadable (permission-denied) `feature.json` |
| d3 | single owner + **differently-branched** valid-object noise still allows | ❌ **UNASSERTED** | — | existing "no-record branch ignores unrelated malformed record" test changes the *owning* record's branch to `other`, producing zero owners, not one-owner-plus-differently-branched-noise |
| e | branch no valid record claims stays allowed | ✅ (pre-existing) | `test-merge-gate.py:77-79` | yes |
| f1 | `_build_entry_recovery_notice` "open" horn retained verbatim | ⚠️ only indirectly, via unchanged literal text; no fixture drives `command == "open"` while `entry == "recovery-required"` for a non-era feature | — | code path untouched by the diff (still the original `if command == "open": …` branch), so risk is low, but zero direct assertion exists |
| f2 | `_build_entry_recovery_notice` derives the non-era command via `feature_schema.recovery_command_for` | ✅ new | `test-gh-sync.py:3615-3629` | yes — asserts `expected_command == "recover-terminal"`, command text in stderr, `--yes`, and `open` absent |

## Critical finding — F-02 confirmed fail-open (must_fix, severity: critical)

Reproduced end-to-end through the real `PreToolUse` hook (`merge-gate.sh` → `merge-gate.py`), not
just `merge_ref`, in a fresh fixture with `github.build_entry = "recovery-required"`:

```
cmd='git merge feature/test'          -> decision='deny'  (correct)
cmd='git merge --no-ff feature/test'  -> decision=None     (SILENTLY ALLOWED)
```

Mechanism: `git_merge` (`merge-gate.py:46-61`) finds the `merge` token and unconditionally returns
`rest[index+1]` as the branch — it does not continue skipping dash-prefixed tokens *after* `merge`
the way it does *before* it. `--no-ff` becomes the "branch". `head_branch` then returns
`"--no-ff"` as the resolved head branch (`merge-gate.py:99-102`, since `kind=="git" and value` is
truthy). `feature_for("--no-ff")` finds no owner, `main()` hits `if not owners: … return` with no
`failure`, so it prints nothing and allows silently (`merge-gate.py:146-150`).

Probe: `/tmp/bug1309-probe2.py` (unit-level, `merge_ref`) and `/tmp/bug1309-probe-e2e.py`
(end-to-end through the real hook binary with a real stdin JSON payload). Both confirm the
orchestrator's claim exactly — **not** a hypothetical, this is live. No test in the diff or the
pre-existing suite constructs a command of the shape `git merge <flag> <branch>` or
`git merge <branch> <flag>` (the latter is fine — `git merge feat/x --no-ff` still resolves to
`feat/x` correctly, only a flag placed *immediately after* `merge` breaks it). The new `-C`/`-c`/
`--work-tree` tests all place the global flag *before* `merge`, which the fix does correctly handle
via the `takes_value`/dash-skip loop — but that loop's protection stops the instant it consumes the
`merge` token itself.

## Discrimination audit (new cases only, reddened against `de04d841` pre-change source)

Mechanism: pre-change scripts recovered via `git -C <worktree> show de04d841:<path>` into
`/tmp/bug1309-prechange-bin/{merge-gate.py,merge-gate.sh,feature_schema.py,harness_boundary.py}`.
Both scripts take `ROOT` as `sys.argv[1]` directly, so each case was invoked as
`python3 <script> <root>` with a real stdin JSON `tool_input.command` payload, bypassing
`merge-gate.sh`'s boundary-resolution shell wrapper entirely (harness-independent, reproducible).
Driver: `/tmp/bug1309-probe-discrim.py`.

| Case | PRE (de04d841) | POST (ac2bc0bb) | Reddens? |
|---|---|---|---|
| duplicate valid records deny naming both | `deny`, but generic exception-path message lacking `duplicate_id` (old `feature_for` picks one record arbitrarily via glob, then a later lookup against the wrong doc throws) | `deny`, ambiguity message naming both | ✅ yes — assertion `duplicate_id in reason` fails on PRE |
| single owner + non-object noise still allows | `None` (allow) | `None` (allow) | ❌ **NO** — pre-change `feature_for` already filtered non-dict records via `isinstance(document, dict)`; this case was already true before the fix and does not discriminate the delta |
| `-C` / `-c` / `--work-tree` global-flag merge detected | `None` (allow — merge silently undetected) | `deny` (correctly detected) | ✅ yes, all three |

**Non-discriminating case, named:** `T-05 single owner plus unrelated malformed record still allows`
(`test-merge-gate.py:163-170`) proves nothing about this delta — it passes identically pre- and
post-change. It is a legitimate regression guard for the future, not evidence this fix works.

**Sortedness mutation proof (P-06/O-06 style):** mutated a copy of `merge-gate.py`
(`/tmp/bug1309-mutant/merge-gate.py`) to build `names` from `reversed(owners)` with `sorted()`
removed. Ran the exact assertion from `T-05 duplicate valid records claiming the branch deny naming
both` against the mutant: **still passes** (`/tmp/bug1309-probe-sort.py` output: `mutant (unsorted,
reversed order) passes original assertion: True`). The test only checks substring membership of
both feature ids and reason-string equality across two identical calls in the same process — it
never checks relative order, and same-process glob order is itself stable, so "stable across
repeated calls" ≠ "sorted." The "stable sorted order in the deny message" clause of the contract is
therefore **unverified by any test.**

## Suite run
Not re-run (orchestrator already confirmed green at the pin; my own audit needed the pre/post
comparison runs above, not the standing suite itself). `env -u HARNESS_AGENT_TYPE` used throughout
per repo Expertise G-07.

## Adequacy verdict
Green ≠ adequate. Of the six behaviour groups in the dispatch: (a) partially covered — the *pre-merge*
flag case is well covered, but the *post-merge* flag case (the one that actually shipped a live
fail-open) has zero coverage; (c) partially covered — ambiguity-fires and no-receipt-offered are
solid, sort-stability and era-exempt-ordering are not; (d) partially covered — only the non-object
noise kind is exercised, unreadable and differently-branched noise are not; (f) the "open" horn is
retained by inspection only, no direct assertion.
