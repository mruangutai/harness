## Next

Cycle 4's three highs are FIXED, one commit each: HIGH-1 `5aa435d`, HIGH-2 `ba4ba22`,
HIGH-3 `18fa4fa`. Operator directed straight to PR and merge from here.

TWO OF THE THREE WERE IN MY OWN PREVIOUS CYCLE'S FIXES, which is the pattern worth carrying
forward more than any individual fix:

- **HIGH-1** - MF-3 replaced an absence-as-credential with a FORGEABLE one. `station_only` was
  validated in one direction only, so it could be minted onto a task-bearing signed plan. The
  converse now lives at `load_plan`, the one chokepoint every reader passes. I had also written a
  FALSE citation claiming case (inv34.d) covered this; it did not.
- **HIGH-2** - `xargs` was a fifth evasion. Measuring the class settled the approach: one variant
  reads the verb FROM A FILE, so no text scanner can ever see it. The rule is now FAIL-CLOSED ON
  INDIRECTION, not a fifth form-patch. Nine forms denied end to end, five controls still allowed.
- **HIGH-3** - MF-2's own fallback returned a bare abspath, which is a different namespace from a
  resolved root, so an in-base target misclassified and bash-write-guard exited 0 silently. The
  fallback now resolves as far as it safely can.

OPEN, AND NOT BUILD WORK: #1103 (identity check inside cmd_sign_approval - the gate is still a
denylist, not a boundary), #1104 (BRIEF-less directories are never approval-checked; predates this
feature). SC-01 passes on the operator-accepted reading in D-18.

## Trust

- unit exit 0, 511 PASS; integration exit 0, 822 PASS; gate one ENVIRONMENTAL violation (INV-29, BUG-1080's stale worktree, fires on clean origin/main too) — verified-at 18fa4fa
- Nine sign-gate evasion forms denied END TO END through the real gate, five controls still allowed — verified-at ba4ba22
- HIGH-2's third xargs variant reads the verb FROM A FILE, so its text is never in the command line; that is why the rule is indirection, not form — verified-at ba4ba22
- HIGH-1's do-no-harm semantics were MEASURED: refusing every schema-invalid merge reddened 21 existing cases whose bases predate REQUIRED_TASK_FIELDS — verified-at 5aa435d
- HIGH-3's permit is PRE-EXISTING (origin/main crashes fail-open on the same input); MF-2 made it silent, which for a guard is worse — verified-at 18fa4fa
- The station-only exemption is SCOPING: the only way to pass the approval check otherwise was to fabricate twelve signatures; control (inv34.d) was green before the exemption — verified-at 80a919e
- BUG-1030's audit: 45 statuses stripped, 44 terminal and correct, 1 non-terminal — measured against origin/main, not inferred — verified-at e071509
- Gated HIGH code-grade records: 0, measured with the NEW code_grade.py (it moved upstream) against merge-base 7c4f0bd — verified-at 542e888
- Cycles 0-3 are closed and each finding was re-verified at source by a later independent panel; SC-08 re-measured verbatim at 0 — verified-at 18fa4fa
- Cycles 0 and 1 are fully closed and each finding was re-verified at source by a later independent panel; detail is in `787c7fa..c4da870` — verified-at e071509
- T-14's invariant is INV-33 now, not 32: FEAT-45 shipped its own INV-32 first, so it owns the number; both suites' cases pass side by side — verified-at 8fa2d04
- F-04's realpath half does NOT reproduce as a PATH SHAPE: `./`, `..`, doubled slash and absolute are denied; the SYMLINKED-FILE case was the real hole and is H-01 — verified-at 42bc5fe

## Dead Ends

- Do NOT resolve paths on ONE side only in check-domain.sh. Shape-matching the as-typed path stays (it is stronger for `./`, `..`, doubled slashes and absolute paths, all denied), but resolution must realpath the path AND the root or it lands in a different spelling namespace and silently matches nothing. This entry twice recorded a conclusion that was too narrow: first "do not re-fix F-04's realpath half" (which talked past the symlinked-FILE hole, H-01), then "do not rewrite the readlink walk as realpath" (which forbade the actual fix, C2-02). Resolution answers what a path BECOMES; inode identity answers whether two names are the SAME FILE; a hardlink needs the second
- Do NOT close SC-08 by editing SC-08, and do NOT delete BUG-1071's `feature.json.status` — it has no plan.yaml, so that key is the only record it is in review. Issue #1079
- Do NOT reconcile `_record_station` and `_commit_terminal_station` to use the same words: written-nowhere and written-but-uncommitted have OPPOSITE correct answers, both asserted
- Do NOT exempt `--date` from sign-approval's escaping; a type-aware exemption is a hole in the check that closes F-02
- Do NOT add a `required` column to plan-merge.py's VERBS table; if a verb needs an optional argument it gets its own registration
- Do NOT re-run the one-time board pass; it is idempotent but it WRITES, and a run against a moved plan would move cards the panel has not seen
- Do NOT touch `review_sha` in any other feature.json — T-14's intent forbids it, and 19 directories carry honestly-stale-looking pins from layout history
- Do NOT edit `plan.yaml` with Write or Edit; T-09 closed that route for every author including the main session — use `plan-merge.py` verbs
- Do NOT treat `--kind unit` as the suite: it covers 29 of 56 scripts and that gap hid T-01's breakage for four tasks
- Do NOT quote a retired station spelling in a comment — SC-02 greps for it, and this feature tripped that four times

## Working Set

- .harness/harness/features/FEAT-41-one-station-vocabulary/plan.yaml
- .harness/harness/features/FEAT-41-one-station-vocabulary/BRIEF.md
- .harness/logs/2026-08-31.md
- .claude/skills/harness/bin/check-domain.sh
- .claude/skills/harness/bin/check-state.sh
