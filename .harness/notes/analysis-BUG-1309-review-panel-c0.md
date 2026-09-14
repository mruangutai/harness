# Review panel — BUG-1309-mirror-build-entry — cycle 0 — review_sha 6f64a21c

Collated by harness-validator-lead. Written here because the run dir
`<worktree>/.harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-07-01-validator/`
was refused by check-domain (my lead claim is bound to the BUG-240 checkout), so `state.yaml`
and `digest.md` do not exist for this run. This file is the record.

## BLUF

**FAIL — two independent HIGH findings, both in `merge-gate.py`, both invisible to a green suite.**
The gate this feature ships to stop a merge that owes a Build-entry receipt (a) denies a merge
SC-04 says must be allowed, and (b) allows a merge it must deny when its own `gh` subprocess
throws. The qa matrix is genuinely green (unit 33 files, integration 50 files, exit 0) and that is
not in dispute — it is green *over* both defects, which is the panel's real result.

## The panel

| step | persona | verdict | what it produced |
|---|---|---|---|
| code | harness-code-reviewer | FAIL | F1 high (spec mismatch), F2 med, F3 low. Ran all three directed probes; probes 2 and 3 clean, enumerated not inherited |
| qa | harness-qa | PASS | `matrix_ok: true`; unit 33 / integration 50, both exit 0 with non-zero discovery; one low coverage gap |
| security | harness-security-reviewer | FAIL | S1 high (fail-open, demonstrated by execution), S2 low. Scoped itself IN, with reason |
| ui | harness-ui-reviewer | PASS | scoped out on a measured census (77 files, 0 UI extensions, no DESIGN.md); one low finding on the adjacent refusal-message check it was asked for |

Notes: `notes/review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-c0.md` in the feature
dir. All four exist and were read.

## must_fix — one remediation, one owner, ordered

Both highs edit `merge-gate.py:main`. They must be fixed in one pass by one dev, in this order,
because the second changes the block the first must sit inside.

**M1 (from security, S1, high) — the gate fails OPEN on its own exception.**
`main()`'s `try/except Exception: return` covers only the harness.json read and the stdin parse
(`merge-gate.py:115-121`). `gh_head` (`:76`) invokes `os.environ.get("GH_BIN", "gh")` through
`subprocess.run` with no guard, so an unresolvable or non-executable `GH_BIN`/`gh` raises
`FileNotFoundError`/`PermissionError` out of `main()`. `merge-gate.py` `exec`s the script, so the
hook exits 1 with a traceback — and exit 1 is non-blocking for PreToolUse, where only exit 2
denies. Failure scenario, demonstrated by the reviewer running it: `GH_BIN=/nonexistent/gh`,
`gh pr merge 42`, non-era feature with `build_entry` absent → exit 1, no denial JSON, merge
proceeds with the receipt still owed. This is the same shape as the bug the feature exists to fix.
**The fix must not overcorrect into denying.** DEC-138 and SC-04's last clause require that a
failed GitHub read never condemns a merge: catch `OSError` in `gh_head`, return the empty-branch
failure tuple, and let `head_branch` fall through to `local_branch` so the decision is still made
on the local record.

**M2 (from code, F1, high) — the era bypass is narrower than the signed criterion.**
`merge-gate.py:132` reads `if feat in feature_schema.BUILD_ENTRY_ERA_EXEMPT and entry is None`.
SC-04 (`BRIEF.md:105-113`) says, unqualified by value, "for a feature that IS in that set the merge
is ALLOWED at exit 0 with no permission decision emitted"; D-08 and DEC-220 say the same. An
era-exempt feature carrying `recovery-required` therefore falls past the pass-set to `deny(...)`.
Failure scenario: any of the 78 frozen era-exempt directories — including BUG-1309's own — runs its
first real `open`, hits a transient `gh` failure, records `recovery-required`; `gh-sync.py`
`_build_entry_recovery_notice` (`:1379-1386`) prints to the operator "its merge is not refused";
the operator merges and is denied. Two of the other four readers of the set
(`check-state.sh:2002`, `post-merge-sweep.py:223`) implement the unconditional rule, which is why
this reads as `merge-gate.py` deviating rather than the decision record being stale.

**M3 (lead, adequacy) — the test that would have caught M2 does not exist, in either direction.**
`test-merge-gate.py:92` covers `era-exempt absent build_entry allows` and nothing else on the era
axis. qa cited `test-merge-gate.py:64-92` as SC-04's evidence and returned PASS; that binds the
non-era cases and the era-absent case only, so SC-04's era clause is asserted under a narrowed
reading. The remediation owes two cases: era-exempt + `recovery-required` → allow, and
`GH_BIN` unresolvable + local record owing a receipt → deny with the decision JSON, asserted on
the emitted decision and exit code, not on absence of a traceback. SC-06's own graded case
(`era-exempt recovery-required keeps the worktree`) proves the state M2 mishandles is reachable
and spec-contemplated.

## Kept, not gating

- **F2 (code, med)** — `tests/integration/test-hooks-install.py:392` `_run_merge_and_check` is a
  new-or-worsened grade-2 record (ABC 27.0) with no written reason on file. Grade 2 never gates and
  quality opinion never gates here; the actionable part is that the operator's "already ruled"
  grade-2 list handed to this panel has three entries and needs a fourth.
- **S2 (security, low)** — `is_bin`'s basename-only detection is evadable (five payloads proven).
  Security dismissed it as non-escalating because the same actor can edit `feature.json` directly,
  and I accept that for the adversarial case. I re-rate the *reason*, not the severity: the live
  risk is accidental, not hostile — a merge issued through a wrapper (`just merge`, a git alias)
  silently bypasses the gate, which is this bug's own failure class. Low, non-gating, but it is a
  documented limitation of the gate rather than a closed question.
- **F3 (code, low)** — `gh-sync.py:278,282` can record `recovery-required` for a root-level
  onboarding misconfiguration rather than a mirror failure. Satisfies D-04 literally; Build retries
  either way.
- **UI-1 (ui, low)** — `_build_entry_recovery_notice`'s non-exempt branch names the subcommand but
  does not append the feature dir to the command, unlike its five siblings. Same function as M2's
  operator promise: one fix site, two findings, worth handing to the same dev.
- **QA-1 (qa, low)** — INV-37's `open` remedy message is asserted only through the pure
  `recovery_command_for()` unit, never against captured `check-state.sh` stdout; the sibling
  `recover-terminal` branch is asserted against output.

## Assessed and dismissed, with reason

- **SIMPLIFY's `jsonschema` module-scope import cost** — operator-accepted before this panel and
  not re-raised. Not a defect the panel may re-open.
- **Security's jq-filter f-string in `_open_ensure_milestone`** — argv element, not a shell string;
  unchanged by this diff; gains a caller but no new reachability. Info, dismissed as
  pre-existing and non-escalating.
- **Code's Q1 ("is the `and entry is None` narrowing intentional?")** — I resolved it rather than
  passing it up: three authorities (SC-04, D-08, DEC-220) and the tool's own printed message agree
  the exemption is unconditional, and conforming code to a signed criterion is not a scope change.
  The consequence — 78 era-exempt features merge freely even when recording `recovery-required` —
  is what SC-06's retention design already assumes, and is flagged non-blockingly for the operator.
- **The `FEAT-55` plan.yaml riding the diff** — baseline provenance from the cut commit, per the
  dispatch. Not re-derived.

## Adequacy — what this panel could not tell you

1. A green matrix here bounds the happy paths of both new gates and **neither of the two failure
   modes found**. Both highs were found by reading and by executing the gate directly, not by any
   test, and both would survive the suite unchanged.
2. Neither high was reachable through the qa gate's own evidence, so `matrix_ok: true` and
   `severity_max: high` are consistent, not contradictory. Do not read the passing gate as clearance.
3. No reviewer exercised `merge-gate.py` end to end inside a real PreToolUse hook invocation; M1's
   exit-1-is-non-blocking step rests on the documented hook convention plus the reviewer's direct
   execution of the Python, not on an observed hook allowing a merge.
4. `ui` and `security` self-scoping was measured, not predicted — ui gave a file census, security
   named all four examined items — so their PASS/decline is evidence rather than silence.

## Harness defects observed (not findings against the code)

- The `security` step's task returned `failed (exit 1)` with "Subagent called yield with null data"
  while emitting a complete, well-formed digest in its message body and writing its note. Content
  was recovered from the message and the artifact; a lead that routed on the tool status alone
  would have discarded a HIGH finding.
- Lead run-dir writes in this checkout are refused while a same-typed lead claim is bound to
  another worktree, so this run has no `state.yaml` and no `runs/**/digest.md`.
