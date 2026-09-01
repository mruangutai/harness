## Next

Re-review cycle 3. All THREE of cycle 2's highs are closed, each with its own commit:

- C2-01 -> T-19 / D-17 (`80a919e`), the OPERATOR's ruling, not a build decision. Every feature now
  carries a plan.yaml; a station-only record (`tasks: []` + top-level `status:`) is legal; twelve
  directories backfilled with their ORIGINALLY RECORDED station; INV-34 enforces it. SC-08 is now
  LITERALLY TRUE - zero feature.json carry a status key. Issue #1079 is CLOSED.
- C2-02 (`e071509`) - hardlink, linked parent DIRECTORY and an over-cap chain all reached plan.yaml,
  the chain FAILING OPEN. Resolution now realpaths BOTH sides, identity covers hardlinks,
  unresolvable links fail CLOSED.
- C2-03 (`e071509`) - `${IFS}` forged a signature end to end. Fixed in `as_bash_reads_it`, once,
  before either scanner.

CHECK THE T-19 EXEMPTION HARDEST. Backfilling made two checks visible that had skipped those
directories all along (31 lines, no real findings), so a station-only plan is now scoped out of the
approval and STATE.md-task checks. Case (inv34.d) is the control and was green BEFORE the exemption
landed. If that exemption can be widened to a plan with tasks, this feature has broken the approval
check for the whole tree.

Cycle 0/1 verdict items stay closed: T-15 ratified in D-15, T-10 recorded not rewritten, T-18
STRUCK in D-16.

## Trust

- unit exit 0, 505 PASS; integration exit 0, 819 PASS; check-state.sh exit 0, ZERO violations, zero tracebacks — verified-at 80a919e
- SC-08 measured VERBATIM against its own text: 0 feature.json carry `status`; schema 10 properties / 7 required / additionalProperties false — verified-at 80a919e
- The T-19 hole was proven from BOTH sides before fixing: feature.json refuses the key (exit 11), plan.yaml refused to exist without tasks (PlanSchemaError) — verified-at 80a919e
- BUG-1030 was backfilled `review`, the value it RECORDED — not `abandoned`, which is only my inference from the closed issue; a migration moves values, it does not re-adjudicate them — verified-at 80a919e
- The station-only exemption is SCOPING: the only way to pass the approval check otherwise was to fabricate twelve signatures; control (inv34.d) was green before the exemption — verified-at 80a919e
- The new assertions print `ok`, not `PASS`, so the suite COUNTS ARE FLAT by design; confirmed they RAN under the runner by grepping its own log (4 T-09 11, 6 C2-03, 9 T-09 10) — verified-at e071509
- C2-02's chain case FAILED OPEN, not closed: over the hop cap the plan never entered the candidate list and the write was permitted — verified-at e071509
- All five signing-gate evasion forms exit 2 END TO END through the real gate script, and all three controls still exit 0 — verified-at e071509
- Only `${IFS}` braced splits; bare `$IFSsign-approval` becomes `plan-merge.py-approval` and CANNOT sign, so denying it would be a guess — verified-at e071509
- BUG-1030's audit: 45 statuses stripped, 44 terminal and correct, 1 non-terminal — measured against origin/main, not inferred — verified-at e071509
- Gated HIGH code-grade records: 0, measured with the NEW code_grade.py (it moved upstream) against merge-base 7c4f0bd — verified-at 542e888
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
