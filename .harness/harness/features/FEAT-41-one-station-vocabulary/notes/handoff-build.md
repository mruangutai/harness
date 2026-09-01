# Handoff — build phase — FEAT-41-one-station-vocabulary

## Next

C2-01 IS OPEN AND NEEDS THE OPERATOR, not another build pass — issue #1079. Cycle 2 found that
this feature's own T-07 deleted `status: Review` from BUG-1030, a plan-less NON-terminal record,
which is the exact shape #1079 exists to protect. Both repair paths are MECHANICALLY CLOSED and
proven: `feature.json` refuses the key (MergeRefusal exit 11, undeclared key) and `plan.yaml`
refuses to exist without tasks (PlanSchemaError). So a plan-less feature has NOWHERE to record a
non-terminal station, and every fix contradicts SC-08's signed text. #1079 carries three options
and a recommendation. Do NOT attempt this as a code fix.

C2-02 and C2-03 ARE FIXED (`e071509`). Both cycle-1 HIGHs had been closed only for the instance
shown: a hardlink, a linked parent DIRECTORY and an over-cap chain all still reached plan.yaml —
the chain FAILING OPEN — and `${IFS}` still forged a signature end to end. Resolution now
realpaths both sides, identity covers hardlinks, unresolvable links fail CLOSED, and
`as_bash_reads_it` neutralises braced expansions.

Cycle 0/1 verdict items stay closed: T-15's lane ratified in D-15, T-10's verify-line recorded not
rewritten, T-18 STRUCK in D-16 because FEAT-45 fixed Q2 upstream better.

## Trust

- unit exit 0, 505 PASS; integration exit 0, 819 PASS; check-state.sh exit 0 with ZERO violations — verified-at e071509
- The new assertions print `ok`, not `PASS`, so the suite COUNTS ARE FLAT by design; confirmed they RAN under the runner by grepping its own log (4 T-09 11, 6 C2-03, 9 T-09 10) — verified-at e071509
- C2-02's chain case FAILED OPEN, not closed: over the hop cap the plan never entered the candidate list and the write was permitted — verified-at e071509
- A hardlink is unanswerable by path resolution and trivial by inode identity; `st_nlink < 2` keeps the scan off the common path — verified-at e071509
- All five signing-gate evasion forms exit 2 END TO END through the real gate script, and all three controls still exit 0 — verified-at e071509
- Only `${IFS}` braced splits; bare `$IFSsign-approval` becomes `plan-merge.py-approval` and CANNOT sign, so denying it would be a guess — verified-at e071509
- BUG-1030's audit: 45 statuses stripped, 44 terminal and correct, 1 non-terminal — measured against origin/main, not inferred — verified-at e071509
- Gated HIGH code-grade records: 0, measured with the NEW code_grade.py (it moved upstream) against merge-base 7c4f0bd — verified-at 542e888
- H-01's fix NO LONGER uses the readlink walk — C2-02 replaced it with realpath on BOTH sides, which is what the one-sided version should have been; its POST case was mutation-proved — verified-at e071509
- H-02 is fixed ONCE, before either scanner: teaching two scanners about backslashes separately leaves F-03's asymmetry one escape away — verified-at 42bc5fe
- Both QA mutations were RE-RUN against the fixes: `_I` removal now reds exactly one row, `_verify_signature` disabled goes from 0 failures to 3 — verified-at c4da870
- F-02's layer two was UNREACHABLE until c4da870; QA proved it, and the forcing case uses a duplicate `approved_by` (YAML last-wins) rather than a monkeypatch — verified-at c4da870
- T-14's invariant is INV-33 now, not 32: FEAT-45 shipped its own INV-32 first, so it owns the number; both suites' cases pass side by side — verified-at 8fa2d04
- Cycle 0's F-01..F-05 are all closed and cycle 1's panel re-verified each at source; detail is in `787c7fa..9bdbe91` — verified-at c4da870
- F-04's realpath half does NOT reproduce as a PATH SHAPE: `./`, `..`, doubled slash and absolute are denied; the SYMLINKED-FILE case was the real hole and is H-01 — verified-at 42bc5fe
- Cycle 0's own findings (stale-base INV-32 lines, Q2 fixed upstream, the list-rendering print) are all closed; detail is in `787c7fa..9bdbe91` and D-16 — verified-at c4da870

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
