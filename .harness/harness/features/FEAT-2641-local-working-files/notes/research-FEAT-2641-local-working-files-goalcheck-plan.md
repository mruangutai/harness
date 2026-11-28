# Goal-check — FEAT-2641 plan against the operator's stated intent (pm, plan-product goalcheck)

Graded against `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-notes-local-only-2026-11-27.md`
(the grilling artifact), with plan.yaml as applied (approval pending, panel c1 recorded).
Refreshed 2026-11-27 (plan c2 apply) for two items only, departures A and B, after the operator's
rulings GC-01 and OQ-01 in `notes/answers-plan-product.md` and the cycle-2 remedies. The cycle-2
remedies are applied to the text but no reader has read them. Every other line is the cycle-1 grade.

**BLUF: does this plan deliver the operator's stated intent? Yes: all 3 perspectives pass.** Every
ignore, untrack, gate-removal, runtime-keep and committed-record clause is carried. Both `## Settled`
departures are now on the record. D-07 is kept by operator ruling OQ-01, and that is recorded in
D-07's `because` and in a BRIEF Constraints bullet. Reject-none and declined-distill cleanup is
automatic under GC-01: T-10 adds it to set-feature-station, and D-11/T-05 add skip-distill.

## Perspectives (one line each)

- **operator** — PASS. Carried by SC-01, SC-02 and SC-03 (T-01); SC-06 (T-03, T-05 and T-10); SC-07 (T-06); SC-08 (T-03); SC-09 (T-03 and T-05); SC-17 (T-05, T-06 and T-10); and SC-18 (T-04 and T-05). Grilling line 21 is met: the command that writes the terminal station runs the cleanup. That command is `gh-sync.py abandon`; `plan-merge.py set-feature-station` when it writes `rejected`, which covers both reject paths; or `gh-sync.py skip-distill` for the skip-distill path. Each cleans only after its own write has landed. One residual is not a departure: a distill that applied no Expertise op is not merged through merge-distill, so its cleanup is the `feature-worktree.py clean` routine run as a step (PM-C2-02, open to the operator). The grilling's line 20 ties automatic cleanup to merge-distill succeeding.
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
2. **CI readers removed with tests, runtime hooks kept** — met. D-07 keeps ship's precondition in
   `feature.json` by operator ruling OQ-01 (see departure A, now on record).
   T-02 retires every row the grilling named, plus INV-18, INV-46 and INV-51. That fits the
   grilling's "any other run-directory reader". The tests go too, and so do `prune-run-evidence.py`
   and its test (T-05). The kept runtime checks are check-domain's handoff shape, validate-digest's
   receipt and citation checks, expertise receipt verification and run-start succession. They are
   pinned byte-identical to `e2bffca0` and green (SC-12, SC-13, and T-09's `git diff --quiet`).
3. **Cleanup routine and terminal paths** — met (see departure B, now closed). merge-distill cleans
   after a successful merge, under the lock (T-06, SC-07). `abandon --yes` cleans after recording
   the station (T-05, SC-06). `set-feature-station` cleans once it has written `rejected`, on both
   reject paths (T-10, SC-06). `skip-distill --yes` records the decline, commits `feature.json`
   alone and only then cleans (D-11, T-05, SC-18). Ownerless project notes are never deleted: D-06
   `project_notes`, plus SC-06's "a project note not listed survives" and T-03's unit cases.
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
  feature.json validator-PASS precondition takes its place to keep BUG-1129 closed. **Now on the
  record:** the operator ruled to keep it (OQ-01, `notes/answers-plan-product.md`). D-07's
  `because` names the departure and the ruling, and BRIEF `## Constraints` carries a "Departure
  from the grilling" bullet, so it reaches the signature. It is not graded down.
- **B. reject-none and declined-distill cleanup** (grilling line 21 says "the command that sets the
  terminal station cleans up"). **Closed by GC-01.** `plan-merge.py set-feature-station` writes the
  station on both reject paths and now cleans once that write has succeeded (T-10, D-05). A refused
  write keeps the evidence (exit 4/5/9 before cleanup). `gh-sync.py skip-distill` (D-11, T-05)
  records the decline and then cleans. Cycle-2 remedies, applied but unread by any reader, close
  three gaps in that verb. It now runs before the GitHub preflight, so it cannot SKIP silently. It
  cleans only after a successful commit of `feature.json` alone. Its cleanup reaches a short-id
  retained worktree. No caller-run step remains for these paths.
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
- harness-principles, "Never falsify the record": the operator grade moved from partial to pass only
  because the operator's rulings changed the plan's text (GC-01, OQ-01), not because the BRIEF
  restated it. The grilling is still the yardstick; the zero-op distill residual is named.
