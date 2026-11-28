# Goal-check — FEAT-2641 plan against the operator's stated intent (pm, plan-product goalcheck)

Graded against `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-notes-local-only-2026-11-27.md`
(the grilling artifact), with plan.yaml as applied (approval pending, panel c1 recorded).

**BLUF: does this plan deliver the operator's stated intent? Mostly yes: 2 perspectives pass and 1 is
partial.** Every ignore, untrack, gate-removal, runtime-keep and committed-record clause is carried.
Two `## Settled` departures are not yet in front of the operator in any durable record: the ship
precondition D-07, and cleanup for reject-none and declined-distill. Both should go to the operator
at signature. Neither needs a plan rewrite.

## Perspectives (one line each)

- **operator** — PARTIAL. Carried by SC-01, SC-02 and SC-03 (T-01); SC-06 (T-03 and T-05); SC-07 (T-06); SC-08 (T-03); SC-09 (T-03 and T-05); and SC-17 (T-05 and T-06). Partial because cleanup on `reject --superseded-by none` and on a declined distill is not run by the command that sets the station, as grilling line 21 requires. Instead a documented follow-up runs `feature-worktree.py clean` (T-05 step 4, and T-07's reject-path.md and harness.md edits). No open question puts this to the operator.
- **code maintainer** — PASS. SC-04 (T-02) retires INV-8/12/15/16/17/18/36/43/46/47/51 and INV-40(c), and keeps INV-7's arithmetic. SC-14 (T-05, T-07 and T-09) deletes prune-run-evidence, the seams and run_state modules, and their tests. SC-15 (T-08) adds DEC-260, strikes DEC-257 and lists 43 amend rows (counted from plan.yaml decisions_affected). One routine, `bin/working_files.py` (D-05), is the only remover behind all four callers.
- **orchestrator** — PASS. SC-05 (T-05): ship reads the ledger. SC-10 (T-06): local receipts replay. SC-11 (T-04): project-note. SC-12 and SC-13 (T-04 and T-09): runtime hooks byte-identical and green. SC-16 (T-07): instructions.

Every SC is traced by at least one task, and every task traces at least one SC (`traces:` in plan.yaml).

## The five operator constraints

1. **Ignore and untrack, no history rewrite** — met. T-01 adds four directory rules to `.gitignore`
   and to the snippet through merge-gitignore.py. They cover `notes/prototypes` and `notes/mockups`
   probes, `.harness/notes/`, and the kaya segment through `.harness/*/`. `git rm --cached --sparse`
   runs as its own commit, and a guard test refuses any tracked working file (SC-01). SC-02 checks
   ancestry plus a `git show` of the base. T-07's checkout-upgrade.md checklist carries the rules
   to other checkouts.
2. **CI readers removed with tests, runtime hooks kept** — met, apart from D-07 (see departure A).
   T-02 retires every row the grilling named, plus INV-18, INV-46 and INV-51. That fits the
   grilling's "any other run-directory reader". The tests go too, and so do `prune-run-evidence.py`
   and its test (T-05). The kept runtime checks are check-domain's handoff shape, validate-digest's
   receipt and citation checks, expertise receipt verification and run-start succession. They are
   pinned byte-identical to `e2bffca0` and green (SC-12, SC-13, and T-09's `git diff --quiet`).
3. **Cleanup routine and terminal paths** — partial (see departure B). merge-distill cleans after a
   successful merge, under the lock (T-06, SC-07). `abandon --yes` and numeric `reject --yes` clean
   after recording the station (T-05, SC-06). Ownerless project notes are never deleted: D-06
   `project_notes`, plus SC-06's "a project note not listed survives" and T-03's unit cases. No
   skip-distill command exists in `bin/` or `.omp/` (rg, this run), so a declined distill gets the
   new `clean` verb and an instruction in `.omp/commands/harness.md`.
4. **feature.json, plan.yaml, BRIEF.md and STATE.md stay committed** — met. The rules are
   directory-scoped. T-01's verify asserts that `plan.yaml` is not ignored, and the guard test's
   non-vacuity case asserts that `feature.json` is tracked. BRIEF.md and STATE.md are not probed
   directly. No rule can match them.
5. **DEC-174 lanes named** — met. The `lanes:` block is resolved at `0b5aa6e4`. All nine tasks are
   main-session-direct with their reasons. D-10 lands them as one PR graded only at the final head.
   The merge runs on the unchanged ordinary merge-gate route. The BRIEF also lists DEC-174 under
   Constraints.

## Departures from grilling `## Settled`

- **A. D-07 replaces, rather than deletes, ship's handoff-validate refusal** (grilling line 15 says
  "remove ... `notes/handoff-validate.md` presence refusal"). The note read is deleted. A new
  feature.json validator-PASS precondition takes its place to keep BUG-1129 closed. This is put to
  the operator only as OQ-01 in `notes/research-local-working-files.md` (Open section) and in the
  draft digest. plan.yaml and BRIEF.md do not carry it. It must reach the signature explicitly, or
  it becomes a silent departure.
- **B. reject-none and declined-distill cleanup run as a separate step** (grilling line 21 says "the
  command that sets the terminal station cleans up"). With `--superseded-by none`, the station is
  written by `plan-merge.py set-feature-station`, not by gh-sync. The plan leaves set-feature-station
  untouched and has the caller run `feature-worktree.py clean` afterwards (T-07 reject-path.md). The
  reason is that a refused station write must keep the evidence (panel PF-a6ec… and PF-731d…).
  Declined distill is similar: there is no skip-distill command, so harness.md tells the
  orchestrator to run `clean`. This is sound engineering, but it relies on an instruction being
  followed rather than on the station-setting command. No open question raises it. **This is what
  makes the operator perspective partial.**
- **C. DEC-257 is struck, not amended** (grilling line 18 says "amended"). DEC-188 requires a strike
  for a flat contradiction, so the plan has no discretion here. This is disclosed, not graded down.

## Adjacent intent risks already surfaced

- OQ-02 (BRIEF Constraints): when a checkout pulls the merged main, git deletes the untracked
  observation logs of features that shipped but have not distilled. That conflicts with "they exist
  for distill". The research note lists five such features.
- OQ-03: in-flight branches still tracking working files turn the guard red when they merge.
- FEAT-2641's own grilling and facts notes can be claimed through `project-note` only after T-04
  lands. Unclaimed, they stay with the operator, which is consistent with grilling line 22.

## Principles applied
- harness-principles, "Never falsify the record": operator is graded partial for departure B even
  though the BRIEF already encodes it. The grilling is the yardstick, not the BRIEF.
