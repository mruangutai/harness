# Handoff — build phase — FEAT-41-one-station-vocabulary

## Next

Re-review cycle 2 against the NEW `review_sha`. Cycle 1 returned FAIL with two high must-fix
(H-01, H-02) and two mutation-proven med; all four are fixed with their own commits and receipts
in `42bc5fe..c4da870`. Inputs: `plan.yaml` (16 tasks, D-01..D-16), `BRIEF.md`, and those commits.

CYCLE 1'S OWN BLOCKING QUESTION IS ANSWERED BY MEASUREMENT, not opinion: the production Write
tool DOES follow symlinks — link stayed a link, target's bytes changed — so H-01 was high, not
informational, and it is fixed at both checkpoints.

SC-08 IS LITERALLY FALSE BY EXACTLY ONE FILE and that is deliberate — issue #1079. BUG-1071 has
no `plan.yaml`, so its `feature.json.status` is the only record that it is in review: deleting it
destroys a fact, and creating a plan to hold it fabricates a document for a feature FEAT-41 does
not own. Amending the signed criterion to make it pass is not a build decision. The gate agrees
it is not blocking — `note` level, exit 0. Do NOT close this by editing SC-08.

Cycle 0's two verdict items stay CLOSED by the operator: T-15's lane deviation is ratified in
D-15, T-10's verify-line defect is recorded rather than rewritten because the plan format is
add-only. T-18 is STRUCK in D-16, not implemented — FEAT-45 fixed that upstream, better.

## Trust

- unit exit 0, 505 PASS; integration exit 0, 819 PASS — verified-at c4da870, both kinds run SERIALLY after every fix
- Gated HIGH code-grade records: 0, against merge-base 9f2a070, the same the reviewer will use — verified-at 8fa2d04
- H-01's fix uses readlink, NOT realpath (realpath leaves the path's spelling namespace, `/var` -> `/private/var`, and the case stays RED with the fix in); its POST case was written after the fix so the fix was MUTATED away to prove it discriminates — verified-at 42bc5fe
- H-02 is fixed ONCE, before either scanner: teaching two scanners about backslashes separately leaves F-03's asymmetry one escape away — verified-at 42bc5fe
- Both QA mutations were RE-RUN against the fixes: `_I` removal now reds exactly one row, `_verify_signature` disabled goes from 0 failures to 3 — verified-at c4da870
- F-02's layer two was UNREACHABLE until c4da870; QA proved it, and the forcing case uses a duplicate `approved_by` (YAML last-wins) rather than a monkeypatch — verified-at c4da870
- T-14's invariant is INV-33 now, not 32: FEAT-45 shipped its own INV-32 first, so it owns the number; both suites' cases pass side by side — verified-at 8fa2d04
- FEAT-45's records were migrated by THIS feature, not by FEAT-45: it shipped after T-04/T-07 ran, so its plan carried no station and its feature.json still carried `status` — verified-at 8fa2d04
- The 33 INV-32 lines seen mid-rebase were a STALE BASE, not a defect here; BUG-1071's era guard resolves them — verified-at 8fa2d04
- Q2 is fixed UPSTREAM: origin/main's `_hook_feature_dir` resolves the worktree via inflight_registry and SEC-01 bound to fb07ed6 when driven against the real layout — verified-at 8fa2d04
- Cycle 0's F-01..F-05 are all closed and cycle 1's panel re-verified each at source; detail is in `787c7fa..9bdbe91` — verified-at c4da870
- F-04's realpath half does NOT reproduce as a PATH SHAPE: `./`, `..`, doubled slash and absolute are denied; the SYMLINKED-FILE case was the real hole and is H-01 — verified-at 42bc5fe
- `_commit_terminal_station` was printing a Python LIST at the operator (`['fatal: ...']`); rendered to confirm before fixing — verified-at 9bdbe91
- INV-32 reports THIS feature's own review_sha until the pin moves; that is the invariant working, not a defect — verified-at a1dc932
- T-14's four verify greps need `-F` or escaped parens under `pi-uu-grep 0.2.0`, which reads the pattern as ERE — verified-at a1dc932

## Dead Ends

- Do NOT replace shape-matching WITH realpath in check-domain.sh, and do NOT rewrite H-01's readlink walk as realpath: shape is stronger for `./`, `..`, doubled slashes, absolute paths and a symlinked feature DIRECTORY, and realpath leaves the written path's spelling namespace so the gate looks green while denying nothing. This entry USED to stop at "do not re-fix F-04's realpath half", and cycle 1's panel found the hole that wording talked past — a symlinked FILE with an innocent name matched no pattern at all. Closed by ADDING resolved candidates (H-01), never by substituting resolution
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
