# FEAT-1559 research and plan draft

## BLUF

The pending plan is ready for reader review: six main-session-direct tasks, sixteen decisions (D-04 deliberately absent), fourteen falsifiable SCs across operator, reader and code maintainer. This is an enforcement-layer cutover, not a storage-only optimisation. No production code, test, CI, hook config, feature.json or STATE.md was changed. No build/test/lint/formatter was run. The required plan structural check exited 0; research probes below exited 0. The plan writer itself automatically emitted an unsigned-BRIEF and absent Build-entry diagnostic; these are not silently represented as green feature-state verification.

Feasibility: clear with high enforcement risk; surface L. Proceed to review and user approval, not execution. The former FEAT-57 execution prerequisite is superseded by operator ruling 3 (#1655 closed abandoned); no replay receipt or T-19 serialization remains required.

## One exact reader source set

All review readers must use these same feature artifacts and issue/source inputs; do not review only the proposal, or the superseded archive in isolation:

1. This worktree's .harness/harness/features/FEAT-1559-corpus-outside-worktree/BRIEF.md.
2. This worktree's .harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml, generated only by plan-merge.py apply.
3. This artifact, notes/research-FEAT-1559-corpus-outside-worktree-draft.md.
4. notes/research-plan-proposal.md: durable research-backed proposal, deliberately omitting archival carry entries; the actual plan additionally carries the eight specified archive entries unchanged. It is not an alternate plan or a direct writer.
5. notes/grilling-corpus-outside-worktree-2026-10-04.md and runs/plan-product/acceptance.md in this feature tree.
6. CONTROL/.harness/notes/seed-corpus-outside-worktree-2026-10-04.md.
7. CONTROL/.harness/notes/dod-worktree-corpus-2026-09-10.md, all seven DoD units and the real-repository/synthetic-fixture addendum.
8. Issue https://github.com/mruangutai/harness/issues/1559, including operator comments https://github.com/mruangutai/harness/issues/1559#issuecomment-5612266665 and https://github.com/mruangutai/harness/issues/1559#issuecomment-5612425746. Later supplied grilling controls the provider/exits decision.
9. Immutable archive origin/feat/FEAT-58-corpus-outside-worktree at f57e41dd, .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml. Read using git show for planning provenance only; NEVER merge this branch. The archive is a specification source, not an agent corpus content provider.
10. Current source anchors below at supplied HEAD 652e70d4, plus active .harness/harness.json test_matrix/test_kinds and .harness/team-config.yaml routing. All plan task files use current .claude/skills/... Python paths; historical .sh citations in carried choices remain provenance, not executable task paths.

CONTROL is /Users/molchairuangutai/GitHub/harness. WORKTREE is /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree. Feature artifacts are inside WORKTREE/.harness/harness/features/FEAT-1559-corpus-outside-worktree; nothing was written to CONTROL's feature corpus or a harness root.

## Research findings and current seams

- feature-worktree.py#targets distinguishes worktree_segment from artifact_segment. A fleet feature has a harness planning worktree and a separate code worktree; the latter carries no harness artifacts. Direct worktree creation, fleet planning creation and pinned-checkout.py#cmd_add all go through git worktree add. Creation helpers need no second sparse convention: post-checkout is the common seam.
- pinned-checkout.py#_pin_name spells feature--run-id--persona. Validator pins are record-bearing checkouts in scope, not ordinary non-record-bearing scratch probes.
- harness_boundary.py#worktree_owner provides the existing shared-owner legitimacy checks. #linked_worktrees enumerates .git/worktrees but does not normalise a linked caller to its owner first. The supplied fact is preserved: check-domain.py and validate-digest.py call it from linked roots, where .git is a file. Fixing the shared enumeration fixes both callers; no false marker is required on a site that enumerates .git/worktrees, not features.
- check_state/ctx.py#Ctx currently loads all BRIEF/PLAN, plan.yaml and STATE inputs even after narrowing ctx.features. Filtering only the feature list therefore cannot meet the local-open criterion. runner.py#main constructs Ctx before invariant selection. Layout verification and missing-subject refusal must precede that construction.
- check_state/table.py#INVARIANTS declares repo versus feature scope and read dependencies. board.py consumes ctx.features for factory/board predicates and worktrees.py#inv_29 needs landed-terminal data. The plan separates owner-record views from host/git/config context instead of rebinding the entire checker root and accidentally changing checkout-local invariant subjects. INV-52 is the new declared branch-claim row; selected feature preloads remain local.
- merge-gate.py#feature_for currently globs checkout-local feature.json and skips unreadable records. branch-create-gate.py's flow lookup is limited to .harness/harness/features. These are current Python entrypoints, and their denial is a printed permissionDecision payload rather than a failing process. The plan preserves allow controls and existing absent-owner policy rather than inventing blanket branch refusal.
- Repo population readers are board_lifecycle.py#_feature_dirs, check-plan-routes.py#discover_plans and validate-feature-json.py#discover_paths. Explicit file arguments retain their declared local subject. layout_migration.py is evidence about checkout layout, not a new corpus provider; its coupled-reader table and layout_fixtures must follow moved joins instead of retaining dead source signatures. digest_destination.py and dispatch-guard.py have selected-feature authorization reads, deliberately not widened to landed sibling data.
- check-domain.py's own-run post-write sweep is checkout-local and its hardlink enumeration remains comment-only under carried D-14. Existing main-corpus write refusal is inherited from harness_boundary on both Write/Edit and Bash routes. No governed write path gains git subprocesses or a new state-command invocation; corpus-dependent gates and audit entrypoints can verify their structural subject separately.
- hooks/post-merge currently execs post-merge-sweep.py. The cutover retains that sweep, uses an ordinary delegate call so missing/failing delegates can be named and the post shim exits 0, and adds post-checkout/post-rewrite. The delegate's installation root is not automatically the checkout affected by Git; command defaults/--checkout must address the latter. post-rewrite stdin is preserved.
- .omp/extensions/harness-hooks.ts#rootTarget/#rootCall implements lexical rooting, DEC-251. Ordinary absolute main-corpus read targets remain byte-identical and bypass feature-root lookup. No adapter production change is necessary. Existing tests/unit/omp-hooks.test.ts and BUG-1016's committed receipt establish the lifecycle seam; T-05 adds a corpus-specific regression control.

## Required probes — observed, not projected

### Feature-root resolution

Command: python3 CONTROL/.agents/skills/harness/bin/inflight_registry.py feature-root --feature FEAT-1559-corpus-outside-worktree.

Observed exit 0; stdout resolved to WORKTREE. This was a research probe, not structural verification of the planned sparse layout.

### Fleet active-segment resolution

Current fleet.yaml declares mruangutai/kaya and harness-factory-smoke. A read-only tracked-path census currently has harness records only: there is no live kaya planning record to use as a real-population example. I did not claim that one exists or create it in the owner corpus.

Probe imported the current feature-worktree.py from WORKTREE and called targets("mruangutai/kaya"). Observed exit 0 and this raw stdout:

```
[('planning', '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree', 'harness', 'kaya', 'main'), ('code', '/Users/molchairuangutai/GitHub/harness-factories/kaya', 'kaya', None, 'main')]
Segment resolution: use exact .harness/*/features/<active-id> directory paths, not worktree segment harness; current tracked population has only harness, so no live kaya record to probe.
```

The first tuple's root is the existing helper's script-resolved checkout in this probe, not evidence it is the ultimate owner. Existing active records select exact artifact segments, not worktree segments. Operator ruling 2 supersedes the original zero-candidate refusal: recordless ids use checkout identity and include that id across all segments. Multiple segment claims and underivable identities still refuse. T-01/T-04 cover first creation and ambiguity; T-06 records actual conversion subjects.

### BUG-1016 root-hook interaction

Probe extracted and transpiled the exact current rootTarget function using Bun, then evaluated absolute, relative and quoted-absolute record paths with a different synthetic checkout root. It did not run a test suite or change adapter code. Observed exit 0 and raw stdout:

```
{"input":"/Users/molchairuangutai/GitHub/harness/.harness/kaya/features/FEAT-1/BRIEF.md:1-20","output":"/Users/molchairuangutai/GitHub/harness/.harness/kaya/features/FEAT-1/BRIEF.md:1-20","unchanged":true}
{"input":".harness/kaya/features/FEAT-1/BRIEF.md","output":"/wt/FEAT-1559/.harness/kaya/features/FEAT-1/BRIEF.md","unchanged":false}
{"input":" \"/Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-02/BRIEF.md\" ","output":" \"/Users/molchairuangutai/GitHub/harness/.harness/harness/features/FEAT-02/BRIEF.md\" ","unchanged":true}
```

The probe establishes the lexical predicate only. It does not substitute for SC-02's registered adapter/guard lifecycle and real owner-file integration proof. T-05 explicitly tests no resolver call for the all-absolute case and a relative-path control.

### Backlog intake

Ran gh issue list --repo mruangutai/harness --state open --limit 100, exit 0, after reading the backlog-intake convention. Related items remain separate: #1638 hardlink aliases, #2060 non-T-NN loader and #1640 historical record-less directory. None is absorbed as unrelated scope; directory census deliberately observes record-less subjects without rewriting their metadata.

## Decisions retained versus replaced

| Archive decision | Current handling |
| --- | --- |
| D-01 | Re-anchor to never materialised, all record-bearing classes, plain-clone/probe no-op. |
| D-02 | Re-anchor cross-checkout refusal and absolute owner-root read B; no symlink provider. |
| D-03 | Re-anchor active-local versus repo-wide audit separation and verification boundary. |
| D-04 | Drop: only existed to ignore the rejected .harness/corpus symlink. |
| D-05 | Carry exact choice/because/dec: falsifiable behavior, not reproducing a disputed old exit. |
| D-06 | Carry exact choice/because/dec: era-exempt exact FEAT-02/FEAT-03 pair, nonempty reason, supersets collide, historical records untouched. |
| D-07 | Re-anchor DEC-174 to current hooks/validators/tests; FEAT-57 prerequisite superseded by ruling 3 (#1655 abandoned). |
| D-08 | Re-decide every .harness/*/features exclusion and exact active artifact-segment addition; no top-level allowlist. |
| D-09 | Re-decide B, no symlink and no git-content provider, no in-progress siblings. |
| D-10 | Re-anchor common Git hook seam and verify-only gates; creator implementations unchanged. |
| D-11 | Carry exact choice/because/dec: minimal real-Git synthetic fixture, never repo copy; keep tests/integration/f58_sparse_fixture.py as the carried helper name and REQUIRED_PATHS as a single fixture source. Add real-owner proof beside it. |
| D-12 | Re-anchor four retained error exits 3/4/7/8 and dirty non-gating versus structural refusal. |
| D-13 | Carry exact choice/because/dec: immutable endpoints, announced absence/shallow skips, no collected moving-ref baseline. |
| D-14 | Carry exact choice/because/dec: hardlink behavior struck/out of scope; checkout-local hardlink census marker only, branch-gate allow/deny surviving. |
| D-15 | Carry exact choice/because/dec: census quantifies detected sites, not marked sites; four-value vocabulary, no linked_worktrees feature marker, dynamically opaque patterns declared blind. |
| D-16 | Carry exact choice/because/dec: read-only real-owner name-set proof plus >70 non-vacuity floor, and dirty versus structural proof in one owned actual-repository disposable pin. No fixed census expectation or live-tree mutation. |
| D-17 | Carry exact choice/because/dec: registered branch/merge decisions assessed by payload, not exit. |

The apply pipeline parses the archive plan, selects the eight mandated decision objects without changing their values, joins them with the current proposal decisions, sorts by id and passes the resulting proposal to plan-merge.py apply on stdin. There is no direct plan writer. Historical N-NN references bind by obligation: fixture/state-command -> T-01; local audit/preflight -> T-02; branch population, gates and census -> T-03 (branch predicate itself -> T-01); hook integrity -> T-04; plain-clone/immutable-endpoint/real-data assertions -> T-05; file-count/conversion receipt -> T-06. No old N-NN task is scheduled and no stale .sh path is an anchor.

### Complete archived task mapping for carried D-13/D-14/D-15

| Archived id | Current task and obligation |
| --- | --- |
| N-01 | T-01: fixture/state command and immutable planning baseline. |
| N-03 | T-03: both registered Write/Edit and Bash denial routes; no symlink provider. |
| N-06 | T-02: audit verify preflight; T-03: linked_worktrees owner normalization and comment-only checkout-local hardlink census marker. PART 3(c) red proof is a one-time receipt, not collected; PART 2 receives no undetectable marker. |
| N-07 | T-03: merge-gate population and permissionDecision allow/deny proof. |
| N-08 | T-01: exact historical branch exemption; T-02/T-03: invariant/gate consumption. |
| N-09 | T-05: live clone/audit regression assertions and one-time immutable diff receipt; T-06: conversion measurement. PART 1(b) remains receipt-only; PART 3(3) is demoted to a one-time receipt under PF-8040e714, with execution-time merge-base frozen and recorded. |
| N-10 | T-01: owner seam; T-03: owner population consumers and surviving branch-gate widening/marker/payload controls. |
| N-11 | Retired; surviving N-10 PART 6/3/7 obligations map to T-03; hardlink behavior and denial tests stay struck. |
| N-12 | T-03: detected-site census, marker vocabulary, injected scratch discrimination and declared blind class. |
| N-13 | T-05: read-only actual-owner name-set assertions and disposable pin at current owner HEAD. |

Every N-NN cited in D-13/D-14/D-15 choice or because is covered above, including N-03 and references through historical receipt filenames. Historical .sh anchors and obsolete symlink wording are provenance, not current dispatch instructions.

## Verification, dependencies and acceptance coverage

Tasks are topologically ordered T-01 -> T-02 -> T-03 -> T-04 -> T-05 -> T-06. Provider and branch predicate land in T-01 before audit consumers, so there is no deadlock in which T-02 needs a T-03 provider to pass its own commands. File ownership is disjoint: 45 anchors, no shared production/test/document file. Unit and integration coverage are required for the five cross_module tasks; docs-only operational T-06 adds no production behavior and still has automated manifest validation implemented by T-05. All six execution modes are main-session-direct with DEC-174 reasons.

| DoD unit | SCs and task subjects |
| --- | --- |
| D-1 active materialisation | SC-01/07/10; T-01 state/fixture, T-04 creator hook proof, T-06 observed inventory. |
| D-2 on-disk readable landed records | SC-02; T-01 owner seam, T-03 both registered guards, T-05 adapter lifecycle and actual owner reads. |
| D-3 local audit and fail-closed discovery | SC-03/04/09/12/13; T-02 preloads/invariant dispatch, T-03 global consumers/census, T-05 real name equality and mutants. |
| D-4 branch claims | SC-05/13; T-01 pure predicate, T-02 declared global invariant, T-03 gate payload and sparse owner controls. |
| D-5 fresh clone and CI identity | SC-06/11; T-01 clone no-op, T-05 immutable endpoints and whole-tree matrix, unchanged CI. |
| M-1 deterministic verify/repair | SC-07/09/13; T-01 mode/JSON report/dirty/idempotence, T-02/03 verification-only gates. |
| M-2 every Git lifecycle route | SC-08/01; T-04 three hooks, delegates, hidden-feature merge, rewrite stdin/rebase. |

SC-14 is pinned-source inspection, not a vague prose pass: reviewer reads git show review_sha for AGENTS.md, .harness/README.md and the two specified skill documents. No SC is UAT. No UI surface changes, so DESIGN.md/prototype is unnecessary. component/ui/typecheck runners are null and do not carry these Python/hook/doc criteria; functional/eval remain excluded. The active unit/integration runners and detection globs are sufficient; no test matrix changes are planned.

Measurement is deliberately file-count mode. Seven standing worktrees' 48–61 MB logical du values and historical +1.1 MB/day growth are supplied motivation, not observed recovered disk bytes. Only T-06's per-checkout materialised feature names/counts and clean idempotence/dirty-skip receipts count as conversion evidence. No df claim is made, no dirty conversion is forced and no standing tree is removed.

Fail-first is part of every behavior task. Missing new command is only bootstrap failure, not proof of each predicate; negative cases include wrong cone, cleared bits, wrong directory set, dirty plus structural, absent/ambiguous segment, root unavailable, record-less missing entry, sentinel/third claimant/empty exemption, missing/failing delegates and an unmarked scratch census site. Existing BUG-1016 positive controls are not called red-first. Registered gates use payload assertions. Real host and immutable endpoint skips are announced, never a met verdict. Whole-tree suite verification is named once at T-05 after all production changes, with immutable baseline receipts, not scattered sibling runs.

## Principles applied

- .agents/skills/harness-craft/references/redesign-from-first-principles.md: replace the symlink/provider architecture rather than carrying it beside B; reuse owner resolution and the common Git seam.
- .agents/skills/harness-craft/references/outcome-oriented-execution.md: one clean cutover, no transitional alias or fallback corpus. Order the provider before its audit consumers; final whole-tree verification belongs after all changed files land. Test-first ordering remains mandatory.
- harness-spec-driven: exact symbol/path anchors, literal verify dispatch, SC traces, no overlapping file writers and only plan-merge verbs. harness-brief: perspectives are outcomes, decisions are choices. harness-simplify: reuse owner resolution and existing CLI seams rather than a provider hierarchy; avoid a shared one-line hook-body abstraction and leave lexical adapter production code unchanged.

The four independent simplification readers and adversarial panel are not manufactured by this author. The parent review workflow owns those gates before signature. This draft reports no panel status and writes no approval mapping.

## Tool receipts and raw structural stdout

All three apply invocations exited 0 and printed APPLIED. First creation output automatically included check-state --changed diagnostics: BRIEF not approved, INV-37 absent github.build_entry, approval pending and historical INV-23 notes. The second preserved decisions and replaced T-01/02/03/05 fields; full captured stdout is artifact://1188 (use :raw for untruncated lines). The final apply made verify blocks directly executable with set -e and shell-comment expected results, and named the fixture-only REQUIRED_PATHS constant; full captured stdout is artifact://1190. All three printed the same unsigned-state diagnostics. No output contained an APPROVAL-RESET: receipt; therefore no gh-sync status call was made. No panel or approval proposal was supplied; the tool bootstrapped pending approval. The final structural check below was run after that last apply, exited 0 in 0.22 seconds and printed the displayed 45-anchor result.

The initial check (before clarifying JSON report, real pin proof and moving the provider ahead of consumers) exited 0 with 6 tasks, 41 anchors and 0 failures. It is superseded by this final check, not represented as evidence for the final draft.

Final command:

```
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree/.harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree
```

Exit 0. Raw stdout, including absence of any OVERLAP/FAIL line:

```
OK T-01 7 anchor(s) resolved
OK T-02 8 anchor(s) resolved
OK T-03 14 anchor(s) resolved
OK T-04 5 anchor(s) resolved
OK T-05 9 anchor(s) resolved
OK T-06 2 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree/.harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree: 6 task(s), 45 anchor(s) resolved, 0 failure(s)
```

This proves anchor/route/trace structure, not implementation or goal completion. All SC outcomes remain not_met at draft time; their planned commands are not exercised verification.

## Operator execution prerequisite — superseded

Q-01 is closed by operator ruling 3 in notes/answers-operator-2026-10-04-signature-rulings.md: FEAT-57-review-latency was abandoned (#1655 closed, label abandoned). No replay receipt or T-19 serialization is required. Earlier receipts above describe historical draft state, not current prerequisites.
