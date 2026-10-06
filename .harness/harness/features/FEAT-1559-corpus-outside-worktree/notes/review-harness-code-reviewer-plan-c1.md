# Code-reviewer — pending FEAT-1559 plan

## BLUF

**FAIL — one high substance contradiction:** the mandatory dirty-before-mutation repair refusal prevents the measured hidden-feature merge regression from being repaired by its post hook. One medium verification omission also remains. This is a pending-plan review, not implementation approval; code_grade is n_a. Mission proportionality is appropriate; no downgrade recommended.

Reviewed: plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree/.harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml. Research baseline supplied as 652e70d4, not a pinned implementation review SHA. Read BRIEF, on-disk plan, and the exact reader source set in notes/research-FEAT-1559-corpus-outside-worktree-draft.md, including both issue comments, immutable archive f57e41dd, current source anchors and active matrix/routing. Scoped git diff over the pending BRIEF/plan/draft returned no output; that does not supersede the on-disk artifact review. No tests, builds, linters, formatters or plan verification were run.

## Findings

### High — substance; scope none — dirty safety conflicts with the mandatory merge repair

Pointers: BRIEF SC-07 and SC-08; plan T-01 intent (lines 548–556) and T-04 intent (lines 693–695); CONTROL/.harness/notes/dod-worktree-corpus-2026-09-10.md:85–97,305–308.

T-01 says both modes diagnose dirty input first and repair never mutates dirty work. T-04 requires reproducing a hidden-feature merge that clears skip bits or produces unexpected deletions, then obtaining clean status and successful verification. The supplied reproduction reports **3337 ` D` status entries and zero remaining skip bits** before `sparse-checkout reapply` restores a clean tree. Those entries are dirty input to the prescribed repair boundary. Consequently the hook must skip the very repair SC-08 requires; its exit 0 cannot make the subsequent verifier green. This conclusion follows from the supplied measurement and plan text; no reproduction was rerun.

Must fix before signature: specify a compatible safety contract distinguishing demonstrably sparse-induced absence from genuine uncommitted work, or obtain an approved compatible change to the required lifecycle outcome. Do not simply ignore deletions or weaken dirty safety. Include discriminating assertions for the reported sparse-induced deletions, real user modifications/deletions, and the mixed case, with explicit non-mutation for genuine dirt. Propagate the resolved contract consistently through SC-07/08, D-10/12, T-01/T-04 and operator guidance.

Spec mismatch: plan.yaml → SC-08 (in combination with SC-07).

### Medium — substance; scope none — whole-suite plain-clone subject is not specified

Pointers: BRIEF SC-06; plan T-05 intent, lines 723–731; active .harness/harness.json test_kinds.unit/integration.

SC-06 requires existing required suites green **in a plain clone**. T-05 proves clone identity using a minimal synthetic fixture and separately directs the main session to run registered unit/integration suites after cutover, but does not place those suite runs in a non-linked full clone. The feature worktree is sparse by then; a synthetic fixture cannot exercise the repository's existing complete suites. A suite receipt without its required checkout class cannot discharge this clause.

Recommendation: identify one ordinary full-clone subject at the immutable implementation endpoint, run the existing registered suite commands there without changing CI/runner selection, and record exact root/class/endpoint and exits. Keep whole-tree verification centralized at T-05, not duplicated across tasks.

Spec omission: plan.yaml → SC-06.

## Plan and architecture assessment

- All fourteen SCs have task traces; no nonexistent or orphan SC reference found. Six tasks are topologically chained; the shared provider and branch predicate precede consumers. No dependency cycle found.
- Production and test ownership is disjoint. T-03 explicitly does not edit T-01's provider or T-02's files; the census vocabulary is available in the plan, not a hidden future dependency.
- T-05 aggregates whole-tree verification after all production changes, and T-06 is operational evidence only. The T-05-owned manifest validator exists before T-06 invokes it. No verify-versus-delete conflict found. Local checks do not substitute for the non-skipped real-owner/immutable-endpoint receipts.
- The proposed feature_corpus seam is suitably deep: owner legitimacy, directory population and branch claims are centralized; callers retain their established refusal carriers. No second content-provider hierarchy, cache, git-content fallback or sibling lookup is planned.
- Ctx is not rebound wholesale to owner-root: selected local preload and lazy global records are separated from checkout-local host/git/config subjects. Explicit-file audit arguments and authorization guards retain their local subjects. Linked peer enumeration remains a separate standard-library filesystem boundary.
- Hook implementation-root versus affected-checkout separation and lexical OMP adapter reuse are appropriate. Leaving TypeScript production unchanged follows the current rootCall/needsRoot and existing absolute-target controls; T-05 adds the corpus-specific lifecycle assertion rather than another rooting convention.
- Current-plan structural gates inspect every JSON finding, so dirty exit priority cannot mask structural refusal. The unresolved repair-policy contradiction above is separate from that sound gate design.
- **Mission proportionality:** retain plan lane. Operator-confirmed lifecycle enforcement, fail-closed population migration and real-host proof cross multiple existing module boundaries. Six sequential direct tasks are justified by safety and evidence; no proportionality finding. No unnecessary adapter production rewrite or creator-specific sparse implementation is scheduled.
- SC-14 is future pinned-source inspection, not discharged by this pending-plan review. Preserve git-show inspection of all four T-05 guidance documents at the implementation review endpoint.

## Open questions

- **Q-01 — blocking for execution, not drafting:** Where is the durable FEAT-57 frozen-and-spot-checked replay receipt, and who owns serialization of its audit edits against these check_state edits? Supplied sources retain this prerequisite; T-01 must not execute before it is discharged.
- **Q-02 — nonblocking clarification:** For creation of a brand-new feature absent from tracked paths and owner directories, what establishes its exact active segment before post-checkout? T-01 correctly refuses an absent segment, but T-04 claims helper/bare creation convergence. Recommendation: include an explicit first-creation ordering/subject case; classify any required broader creation-flow change before implementation rather than silently modifying the excluded creators.

No human implementation commits are graded; no source files were changed. No expertise update requested. The report is the only written artifact.
