# T-01.intent amendment — validate c0 fix round c1, main-session-direct (DEC-174), ruled by AdvisorA4Validate

```yaml
VERDICT: PASS
DIGEST:
  amendments:
  - task: T-01
    field: intent
    was: 'HARNESS-FEATURE: FEAT-2542-dispatcher-placement. Product checkout: Harness itself, feature worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement (branch feat/FEAT-2542-dispatcher-placement, base 2e7a2c77d61e3ae93180dc6d71a355ff7b85d8f8). This repository ships no docs/spec.md, docs/decisions.md or docs/architecture.md; the authority read for this task is .harness/harness/docs/DECISIONS.md entries DEC-100, DEC-174, DEC-204, DEC-214, DEC-218, DEC-228, DEC-250 and DEC-253, plus the BRIEF and notes/research-FEAT-2542-dispatcher-placement-characterization.md (its Contract table is the expected outcome, its Appendix A the measured base outcome, of every row below). Run every command from the worktree root and keep every relative-path edit inside this worktree.


      Route: the main session does this task directly after the BRIEF and plan are signed (DEC-174). Never dispatch a team run or a lead for it. Edit only the three files in files:. inflight_registry.py, tests/integration/test-lead-start-return.py and every other file stay byte-identical to base.


      Step 0, decision number, before any edit. Run git fetch origin main, then grep -c ''^## DEC-258 '' on .harness/harness/docs/DECISIONS.md and on the output of git show origin/main:.harness/harness/docs/DECISIONS.md. If either count is not 0, stop and report to the operator: D-01, D-02, BRIEF SC-04 and the refusal text below all cite DEC-258, so a renumber is a plan amendment ruled before any source is written, never an edit inside T-01 or T-02. Otherwise the number is DEC-258 for this task and T-02.


      Step 1, tests first, in tests/integration/test-dispatch-guard.py, reusing its helpers (_checkout, _distill_checkout, _register_lead_run, _LEAD_RUNS, _bind_lead_runtime, _distill_task, _distill_fire, _claims_for, _read_registry, _load_registry_module, fire, _unavailable_gates) and isolated_bin from the bin directory.


      Naming rule. Every new assertion is its own check() call named <row id>:<field>, with the row ids listed below. Fields:

      exit: the stated exit code.

      claim: a refused row leaves no claim of the dispatched persona in the owner registry or any linked worktree registry and no harness_claim on stdout; a proceeding row leaves exactly one claim of the dispatched persona.

      receipt: proceeding rows only; stdout carries a harness_claim for the dispatched persona.

      cause: stderr contains every listed fragment and none of the listed excluded fragments.

      remedy: lineage rows only; stderr contains find-run --agent-id Orch.Lead and that cause''s remedy fragments from Step 3 (ii).

      unavailable: lineage rows only; _unavailable_gates(result) is empty.

      bytes: unreadable rows only; the corrupted registry file reads exactly {not json after the dispatch.

      run-reads: the witness row only, defined in (b).

      A lineage row asserts exit 2, claim, cause (fragments BLOCKED, lineage, Orch.Lead and cannot be placed (<cause token>)), remedy and unavailable, plus bytes when its state is unreadable-owner or unreadable-linked. Cause tokens: persona-mismatch, not-found, ambiguous, unreadable for both unreadable states, registry-error for both escaped states.


      (a) Fixtures. X is DISTILL_FEATURE (FEAT-90-one-root-fixture). Y is FEAT-91-other-fixture, a feature directory whose feature.json has runs [] (built as case_34 builds it).

      A product-lead checkout helper: X''s feature.json runs[] holds exactly one open PENDING harness-product-lead run with a given id (or none), a plan.yaml beside it with a given approval.status in the shape test-lead-start-return.py write_plan uses, the product grant .harness/*/features/*/runs/*-product/** in team-config.yaml, and the harness-code-reviewer agent file copied in.

      A placement writer that puts runtime id Orch.Lead (parent Orch) into one of eight registry states with the real registry API:

      ok: claim_run_start as the dispatching lead in X;

      persona-mismatch: claim_run_start in X as harness-validator-lead when the dispatcher is harness-eng-lead or harness-product-lead, and as harness-eng-lead when it is harness-validator-lead;

      not-found: no claim;

      ambiguous: claim_run_start as the dispatching lead in X and again in Y, two live rows for one id;

      unreadable-owner: a valid ok claim, then the owner .harness/.inflight-claims.json overwritten with the exact bytes {not json;

      unreadable-linked: the checkout made a git repository with one commit, a git worktree added at .claude/worktrees/harness/BUG-99-unrelated, the valid ok claim kept in the owner registry and {not json written to that worktree''s .harness/.inflight-claims.json;

      escaped-unreadable: a valid ok claim, dispatch fired through an isolated_bin copy of the bin tree whose inflight_registry.py has appended a find_run_claim override raising UnreadableRegistry(<owner registry path>);

      escaped-oserror: the same, with the override raising OSError(''injected placement fault''), which carries no filename.

      A run-read witness: an isolated_bin copy whose digest_destination.py has appended a wrapper around registered_destination that appends one JSON line with the call''s feature and lead to the file named by the environment variable FEAT2542_RUN_READ_LOG, then returns the original''s result.


      (b) case_38_product_reader_route_keys_on_trusted_placement. Dispatcher harness-product-lead with harness_agent_id Orch.Lead, child harness-code-reviewer declaring X with HARNESS-FEATURE-TREE-ROOT: <checkout>, unless a row says otherwise. Placements, each in registry state ok: distill = open distill-product run, approved plan; plan = open plan-product run, pending plan; norun = runs empty, pending plan. Missions: distill = HARNESS-MISSION: distill; plan = HARNESS-MISSION: plan; missing = no mission line; conflicting = two lines, distill then plan; other = HARNESS-MISSION: validate.

      Each row gives its outcome, then its base prediction: green means every field passes at base, otherwise the fields named red at base.

      c38/distill/distill: exit 0, claim, receipt; the check detail labels it the FEAT-2489 payload. Red at base: exit, claim, receipt.

      c38/distill/plan: exit 2, claim, cause plan-panel start for and refused before any work. Green.

      c38/distill/missing: exit 2, claim, cause child of a bound distill run but has no HARNESS-MISSION line. Red: cause.

      c38/distill/conflicting: exit 2, claim, cause conflicting or malformed HARNESS-MISSION. Green.

      c38/distill/other: exit 2, claim, cause child of a bound distill run but declares ''validate''. Red: cause.

      c38/plan/distill and c38/norun/distill: exit 2, claim, cause declares ''distill''; the plan team''s scope reader declares plan. Green.

      c38/plan/plan: exit 0, claim, receipt. Green.

      c38/norun/plan: exit 2, claim, cause authorization requires exactly one matching open registered lead run. Green.

      c38/plan/missing and c38/norun/missing: exit 2, claim, cause has no HARNESS-MISSION line, excluded child of a bound distill run. Green.

      c38/plan/conflicting and c38/norun/conflicting: exit 2, claim, cause conflicting or malformed HARNESS-MISSION. Green.

      c38/plan/other and c38/norun/other: exit 2, claim, cause declares ''validate''; the plan team''s scope reader declares plan. Green.

      c38/distill-pending/plan: open distill-product run, pending plan, mission plan; exit 2, claim, cause child of a bound distill run but declares ''plan''. Green.

      c38/distill/foreign-feature: distill placement, mission distill, child declaring Y with its tree-root line; exit 2, claim, cause bound distill run is for FEAT-90-one-root-fixture. Red: cause.

      c38/distill/no-tree-root: distill placement, mission distill, no tree-root line; exit 2, claim, cause is a child of a bound distill run and requires HARNESS-FEATURE-TREE-ROOT. Red: cause.

      c38/distill/foreign-tree-root: distill placement, mission distill, child declaring X with HARNESS-FEATURE-TREE-ROOT: FEATURE_TREE_ROOT, the suite''s own root and not <checkout>, as case 33''s a foreign feature-tree root shape builds it; exit 2, claim, cause declared feature-tree root. Red: cause, so Step 2''s inventory carries predicted_red: c38/distill/foreign-tree-root:cause; base refuses it at the plan-route mission rule before any tree-root check, the same refusal Appendix A measured for R/distill-placed/distill.

      c38/distill/run-reads: c38/distill/distill fired through the run-read witness; one assertion, run-reads: exit 0 and the log holds exactly one line, whose lead is harness-product-lead. Red: run-reads.

      Failure rows: product lead on the distill placement (open distill-product run, approved plan), one mission per failure state so every state and every mission meets a failure; case 40 adds distill for not-found and persona-mismatch. Each is a lineage row. Red at base: cause, remedy; exit, claim, unavailable and bytes are green, because base refuses these before the claim step.

      c38/fail-persona-mismatch/plan; c38/fail-not-found/missing; c38/fail-ambiguous/distill; c38/fail-unreadable-owner/conflicting; c38/fail-unreadable-linked/other; c38/fail-escaped-unreadable/distill; c38/fail-escaped-oserror/plan.

      These failure rows are also case 39''s coverage of the harness-product-lead to harness-code-reviewer pair, whose ok state is c38/distill/distill.


      (c) case_39_governed_lead_placement_is_bind_or_refuse. Each dispatch carries harness_agent_id Orch.Lead on the lead''s open distill-<suffix> run (_LEAD_RUNS suffix).

      harness-eng-lead to harness-backend-dev on distill-eng, in all eight states, two children each: bound (declares X, HARNESS-MISSION: distill and its tree-root line) and exploit (declares Y, no marker, no tree-root line), rows c39/eng/<state>/bound and c39/eng/<state>/exploit.

      State ok: bound is exit 0, claim, receipt; exploit is exit 2, claim, cause bound distill run is for FEAT-90-one-root-fixture. Green.

      Each other state: both children are lineage rows. Red at base: exit, claim, cause, remedy, and bytes for unreadable-owner only (the base claim step rewrites the owner registry); unavailable and the unreadable-linked bytes are green.

      harness-validator-lead to harness-qa on distill-validator, bound child only: c39/validator/ok/bound is exit 0, claim, receipt, green; c39/validator/not-found/bound is a lineage row, red: exit, claim, cause, remedy.


      (d) case_40_distill_exemption_never_fires_on_failed_placement. Product lead in the not-found and persona-mismatch states, child harness-code-reviewer declaring X with its tree-root line. All four rows are lineage rows.

      c40/<state>/distill-run: open distill-product run, approved plan, mission distill. Red: cause, remedy.

      c40/<state>/plan-run: open plan-product run, pending plan, mission plan. Red: exit, claim, cause, remedy (base exits 0 and claims).


      (e) case_41_main_and_non_lead_keep_prior_outcomes. Each control dispatches harness-backend-dev declaring Y with no marker, and asserts exit 0 and claim. Run each control in two states: unreadable-owner, the worst on-disk state, which also keeps the claim step''s DEC-218 treat-as-empty recovery; and escaped-oserror, where find_run_claim raises if anything calls it, so a passing row proves the control never reads placement and no other registry state can change its outcome. Rows c41/<control>/<state>, all green at base. Controls:

      main: agent_type Main, harness_agent_id Main, no parent id;

      orchestrator-id: harness-orchestrator with harness_agent_id Orch.Lead;

      orchestrator-no-id: harness-orchestrator with no runtime id;

      lead-no-id: harness-eng-lead with no harness_agent_id. Put a comment above the lead-no-id rows: they assert SC-02''s LEAVE clause for an id-less lead payload; the host refuses an id-less governed nested Task (DEC-218), and the signer''s OQ-1 ruling governs them, so a signed hardening changes exactly these rows.


      (f) case_30_repository_header_binds_exact_factory_claim and case_31_repository_binding_read_from_the_feature_worktree dispatch as harness-eng-lead with harness_agent_id LeadOne and no claim, which is the not-found class. Before their dispatches, bind LeadOne with _load_registry_module().claim_run_start(inflight_registry.feature_root(<checkout>, feature), harness-eng-lead, feature, LeadOne, OrchestratorOne, supervisor_pid=os.getpid(), cwd=<checkout>); in case 31 that is the feature worktree''s registry. Leave their assertions unchanged.

      Register cases 38 to 41 in CASES after case_37_orchestrator_keeps_registered_distill_authority.


      Step 2, fail-first at base source, one inventory for both runs. Before editing dispatch-guard.py, create notes/characterization-pin.md with these lines: dec_number: DEC-258; base_sha: 2e7a2c77d61e3ae93180dc6d71a355ff7b85d8f8; then, under a heading Row inventory, one line predicted_red: <check name> for every assertion that (b) to (e) mark red at base, and no other. Confirm git diff --quiet 2e7a2c77d61e3ae93180dc6d71a355ff7b85d8f8 -- .claude/skills/harness/bin/dispatch-guard.py exits 0, then run python3 tests/integration/test-dispatch-guard.py and append, under a heading Base run: head_at_base_run: <git rev-parse HEAD>; base_run_exit: <exit code>; and one line observed_red: <check name> per FAIL line. The two sets must be equal, and every case 1 to 37 assertion, including the rebound cases 30 and 31, must pass. Any difference means a fixture misses its intended branch: stop and report, and never edit a prediction to fit an observation.


      Step 3, production edit, in .claude/skills/harness/bin/dispatch-guard.py only.

      (i) Add _dispatcher_placement() in the FEAT-2225 T-04 block, beside DISTILL_RUN_RE and LEADS, memoized with a module-level sentinel so find_run_claim runs at most once per dispatch. It returns None when agent is not in LEADS, or when d.get(''harness_agent_id'') is not a non-empty string; that is the prior declared-feature path. Otherwise it calls reg.find_run_claim(owner_root, agent_id) inside try/except (reg.UnreadableRegistry, OSError) as exc; use exactly that typed tuple, never a broad except (the FEAT-65 census requires zero broad catches here). An exception is a refusal with cause registry-error and detail type(exc).__name__: exc. ok true with found[''claim''].get(''agent'') == agent returns found[''feature'']. ok true with another persona is a refusal with cause persona-mismatch. ok false is a refusal with cause found[''cause''] (unreadable, not-found or ambiguous) and detail found[''message''].

      (ii) Refuse through _refuse with, in order:

      first: dispatch-guard: BLOCKED — lineage: <agent> run <agent_id> cannot be placed (<cause>), so its dispatch of <dispatched> for <declared> is refused.

      second: two spaces and the detail; for persona-mismatch the detail is: the live claim bound to <agent_id> belongs to <claim persona> (feature <found feature>, registry <found root>), not <agent>.

      third, one remedy line chosen by cause (remedy fragments asserted in tests in brackets):

      unreadable: Repair each unreadable registry named above in place and never delete it: an unreadable registry is never read as no claims (DEC-218). Then re-dispatch. [never delete it]

      registry-error whose exception names files (exc.paths for UnreadableRegistry, [exc.filename] for an OSError whose filename is not None): The placement lookup raised on <comma-joined paths>; repair that registry in place and never delete it (DEC-218), then re-dispatch. [repair that registry in place, and the owner registry path]

      registry-error that names no file: The placement lookup raised without naming a file, so no registry is known to be corrupt: run the Inspect command below to reproduce the error and repair only what it names; never delete a registry. [without naming a file; excluded fragment: repair that registry in place]

      not-found: This lead''s run holds no live claim: re-dispatch the lead so its run start reclaims before it dispatches; never re-declare a feature to work around it. [re-dispatch the lead]

      ambiguous: Several live claims are bound to <agent_id> in the registries named above, and the guard never chooses. For each named root run inflight_registry.py list --root <root> to see each claim''s feature; the surplus claim is the one whose feature is not this lead''s open registered run in that feature''s feature.json runs[], and if that does not single one out the operator decides with the lead''s dispatcher. Release only that claim, in its own registry: inflight_registry.py release --agent-id <agent_id> --feature <its feature> --root <its root>. If release refuses because that registry holds more than one match, stop and repair the registry by hand; never release by persona. [list --root; release --agent-id Orch.Lead --feature]

      persona-mismatch: Leave a live claim of uncertain ownership alone. If that <claim persona> run is live, dispatch this work from a <agent> run that holds its own claim (a fresh lead run claims at its run start); only if the operator confirms that claim is stale, release it in its own registry with inflight_registry.py release --agent-id <agent_id> --feature <found feature> --root <found root>, then re-dispatch. Never relabel a dispatch to pass. [belongs to <claim persona>; Never relabel]

      last, always: Inspect: inflight_registry.py find-run --agent-id <agent_id> --root <owner_root>. A governed lead''s dispatch binds to the feature its own runtime claim names, never the declared one (DEC-258).

      (iii) In the module-level sequence, call _dispatcher_placement() exactly once, after _direct_orchestration_refusal() and before _start_preflight(). A failed placement then refuses before any other preflight and before the claim step. Do not reorder _start_preflight and _distill_preflight.

      (iv) One dispatch-local placement answer serves both the route and the distill preflight. Add _placed_distill_feature(), memoized with its own module-level sentinel: None when _dispatcher_placement() is None; otherwise, with destinations, errors from _destinations(), the result of _distill_run_feature(destinations, errors, <placement feature>, agent), computed once, so the dispatcher''s registered run is read once per dispatch. _mission_scope: plan_route = dispatched == PLAN_READER and agent == PLAN_TEAM_LEAD and _placed_distill_feature() is None. Keep declares and the return tuple unchanged. Rewrite its docstring to say the scope-reader route yields only to the dispatching product lead''s trusted distill placement.

      (v) _bound_distill_feature, agent branch: when agent is in LEADS, return _placed_distill_feature() if _dispatcher_placement() is not None, else _distill_run_feature(destinations, errors, declared, agent), which is the prior id-less path. The dispatched-in-LEADS branch is unchanged. Delete _dispatcher_feature; grep the bin directory and tests to confirm it has no other caller.

      (vi) Rewrite the BUG-2110 mission-applicability comment and the FEAT-2225 T-04 comment block to state the placement contract, the single dispatch-local placement answer and the placement-keyed route, citing DEC-258, #2542 and #2532.

      Leave these unchanged: _start_preflight, _distill_preflight, _refuse_unbound_distill_marker, _require_distill_feature, _require_distill_mission, the terminal claim try/except with its emit_unavailable, and every other refusal text.


      Step 4, pin run and receipt. Run the four suites and the git diff check of verify; all must exit 0 and the dispatch-guard suite must print no FAIL line. Commit the three files as the T-01 commit. Then append, under a heading Pin run: tested_sha: <git rev-parse HEAD of that commit>; pin_run_exit: <exit code of python3 tests/integration/test-dispatch-guard.py at that commit>; that suite''s final N of N cases passed line; the exit code of each other suite. Commit the receipt alone, then run verify, which reads the receipt at HEAD. If anything later changes dispatch-guard.py or test-dispatch-guard.py, re-run the four suites at the new commit and append a new Pin run block with its own tested_sha and pin_run_exit; the last block is the one graded, and T-02''s verify re-checks at the end of the build that both files at HEAD equal that tested_sha.

      Never run a shell wait loop. No new public interface, retry, telemetry, dependency or documentation change belongs to this task.

      '
    now: 'HARNESS-FEATURE: FEAT-2542-dispatcher-placement. Product checkout: Harness itself, feature worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement (branch feat/FEAT-2542-dispatcher-placement, base 2e7a2c77d61e3ae93180dc6d71a355ff7b85d8f8). This repository ships no docs/spec.md, docs/decisions.md or docs/architecture.md; the authority read for this task is .harness/harness/docs/DECISIONS.md entries DEC-100, DEC-174, DEC-204, DEC-214, DEC-218, DEC-228, DEC-250 and DEC-253, plus the BRIEF and notes/research-FEAT-2542-dispatcher-placement-characterization.md (its Contract table is the expected outcome, its Appendix A the measured base outcome, of every row below). Run every command from the worktree root and keep every relative-path edit inside this worktree.


      Route: the main session does this task directly after the BRIEF and plan are signed (DEC-174). Never dispatch a team run or a lead for it. Edit only the three files in files:. inflight_registry.py, tests/integration/test-lead-start-return.py and every other file stay byte-identical to base.


      Step 0, decision number, before any edit. Run git fetch origin main, then grep -c ''^## DEC-258 '' on .harness/harness/docs/DECISIONS.md and on the output of git show origin/main:.harness/harness/docs/DECISIONS.md. If either count is not 0, stop and report to the operator: D-01, D-02, BRIEF SC-04 and the refusal text below all cite DEC-258, so a renumber is a plan amendment ruled before any source is written, never an edit inside T-01 or T-02. Otherwise the number is DEC-258 for this task and T-02.


      Step 1, tests first, in tests/integration/test-dispatch-guard.py, reusing its helpers (_checkout, _distill_checkout, _register_lead_run, _LEAD_RUNS, _bind_lead_runtime, _distill_task, _distill_fire, _claims_for, _read_registry, _load_registry_module, fire, _unavailable_gates) and isolated_bin from the bin directory.


      Naming rule. Every new assertion is its own check() call named <row id>:<field>, with the row ids listed below. Fields:

      exit: the stated exit code.

      claim: a refused row leaves no claim of the dispatched persona in the owner registry or any linked worktree registry and no harness_claim on stdout; a proceeding row leaves exactly one claim of the dispatched persona.

      receipt: proceeding rows only; stdout carries a harness_claim for the dispatched persona.

      cause: stderr contains every listed fragment and none of the listed excluded fragments.

      remedy: lineage rows only; stderr contains find-run --agent-id Orch.Lead and that cause''s remedy fragments from Step 3 (ii).

      unavailable: lineage rows only; _unavailable_gates(result) is empty.

      bytes: unreadable rows only; the corrupted registry file reads exactly {not json after the dispatch.

      run-reads: the witness row only, defined in (b).

      A lineage row asserts exit 2, claim, cause (fragments BLOCKED, lineage, Orch.Lead and cannot be placed (<cause token>)), remedy and unavailable, plus bytes when its state is unreadable-owner or unreadable-linked. Cause tokens: persona-mismatch, not-found, ambiguous, unreadable for both unreadable states, registry-error for both escaped states.


      (a) Fixtures. X is DISTILL_FEATURE (FEAT-90-one-root-fixture). Y is FEAT-91-other-fixture, a feature directory whose feature.json has runs [] (built as case_34 builds it).

      A product-lead checkout helper: X''s feature.json runs[] holds exactly one open PENDING harness-product-lead run with a given id (or none), a plan.yaml beside it with a given approval.status in the shape test-lead-start-return.py write_plan uses, the product grant .harness/*/features/*/runs/*-product/** in team-config.yaml, and the harness-code-reviewer agent file copied in.

      A placement writer that puts runtime id Orch.Lead (parent Orch) into one of eight registry states with the real registry API:

      ok: claim_run_start as the dispatching lead in X;

      persona-mismatch: claim_run_start in X as harness-validator-lead when the dispatcher is harness-eng-lead or harness-product-lead, and as harness-eng-lead when it is harness-validator-lead;

      not-found: no claim;

      ambiguous: claim_run_start as the dispatching lead in X and again in Y, two live rows for one id;

      unreadable-owner: a valid ok claim, then the owner .harness/.inflight-claims.json overwritten with the exact bytes {not json;

      unreadable-linked: the checkout made a git repository with one commit, a git worktree added at .claude/worktrees/harness/BUG-99-unrelated, the valid ok claim kept in the owner registry and {not json written to that worktree''s .harness/.inflight-claims.json;

      escaped-unreadable: a valid ok claim, dispatch fired through an isolated_bin copy of the bin tree whose inflight_registry.py has appended a find_run_claim override raising UnreadableRegistry(<owner registry path>);

      escaped-oserror: the same, with the override raising OSError(''injected placement fault''), which carries no filename.

      A run-read witness: an isolated_bin copy whose digest_destination.py has appended a wrapper around registered_destination that appends one JSON line with the call''s feature and lead to the file named by the environment variable FEAT2542_RUN_READ_LOG, then returns the original''s result.


      (b) case_38_product_reader_route_keys_on_trusted_placement. Dispatcher harness-product-lead with harness_agent_id Orch.Lead, child harness-code-reviewer declaring X with HARNESS-FEATURE-TREE-ROOT: <checkout>, unless a row says otherwise. Placements, each in registry state ok: distill = open distill-product run, approved plan; plan = open plan-product run, pending plan; norun = runs empty, pending plan. Missions: distill = HARNESS-MISSION: distill; plan = HARNESS-MISSION: plan; missing = no mission line; conflicting = two lines, distill then plan; other = HARNESS-MISSION: validate.

      Each row gives its outcome, then its base prediction: green means every field passes at base, otherwise the fields named red at base.

      c38/distill/distill: exit 0, claim, receipt; the check detail labels it the FEAT-2489 payload. Red at base: exit, claim, receipt.

      c38/distill/plan: exit 2, claim, cause plan-panel start for and refused before any work. Green.

      c38/distill/missing: exit 2, claim, cause child of a bound distill run but has no HARNESS-MISSION line. Red: cause.

      c38/distill/conflicting: exit 2, claim, cause conflicting or malformed HARNESS-MISSION. Green.

      c38/distill/other: exit 2, claim, cause child of a bound distill run but declares ''validate''. Red: cause.

      c38/plan/distill and c38/norun/distill: exit 2, claim, cause declares ''distill''; the plan team''s scope reader declares plan. Green.

      c38/plan/plan: exit 0, claim, receipt. Green.

      c38/norun/plan: exit 2, claim, cause authorization requires exactly one matching open registered lead run. Green.

      c38/plan/missing and c38/norun/missing: exit 2, claim, cause has no HARNESS-MISSION line, excluded child of a bound distill run. Green.

      c38/plan/conflicting and c38/norun/conflicting: exit 2, claim, cause conflicting or malformed HARNESS-MISSION. Green.

      c38/plan/other and c38/norun/other: exit 2, claim, cause declares ''validate''; the plan team''s scope reader declares plan. Green.

      c38/distill-pending/plan: open distill-product run, pending plan, mission plan; exit 2, claim, cause child of a bound distill run but declares ''plan''. Green.

      c38/distill/foreign-feature: distill placement, mission distill, child declaring Y with its tree-root line; exit 2, claim, cause bound distill run is for FEAT-90-one-root-fixture. Red: cause.

      c38/distill/no-tree-root: distill placement, mission distill, no tree-root line; exit 2, claim, cause is a child of a bound distill run and requires HARNESS-FEATURE-TREE-ROOT. Red: cause.

      c38/distill/foreign-tree-root: distill placement, mission distill, child declaring X with HARNESS-FEATURE-TREE-ROOT: FEATURE_TREE_ROOT, the suite''s own root and not <checkout>, as case 33''s a foreign feature-tree root shape builds it; exit 2, claim, cause declared feature-tree root. Red: cause, so Step 2''s inventory carries predicted_red: c38/distill/foreign-tree-root:cause; base refuses it at the plan-route mission rule before any tree-root check, the same refusal Appendix A measured for R/distill-placed/distill.

      c38/distill/run-reads: c38/distill/distill fired through the run-read witness; one assertion, run-reads: exit 0 and the log holds exactly one line, whose lead is harness-product-lead. Red: run-reads.

      Failure rows: product lead on the distill placement (open distill-product run, approved plan), one mission per failure state so every state and every mission meets a failure; case 40 adds distill for not-found and persona-mismatch. Each is a lineage row. Red at base: cause, remedy; exit, claim, unavailable and bytes are green, because base refuses these before the claim step.

      c38/fail-persona-mismatch/plan; c38/fail-not-found/missing; c38/fail-ambiguous/distill; c38/fail-unreadable-owner/conflicting; c38/fail-unreadable-linked/other; c38/fail-escaped-unreadable/distill; c38/fail-escaped-oserror/plan.

      These failure rows are also case 39''s coverage of the harness-product-lead to harness-code-reviewer pair, whose ok state is c38/distill/distill.


      (c) case_39_governed_lead_placement_is_bind_or_refuse. Each dispatch carries harness_agent_id Orch.Lead on the lead''s open distill-<suffix> run (_LEAD_RUNS suffix).

      harness-eng-lead to harness-backend-dev on distill-eng, in all eight states, two children each: bound (declares X, HARNESS-MISSION: distill and its tree-root line) and exploit (declares Y, no marker, no tree-root line), rows c39/eng/<state>/bound and c39/eng/<state>/exploit.

      State ok: bound is exit 0, claim, receipt; exploit is exit 2, claim, cause bound distill run is for FEAT-90-one-root-fixture. Green.

      Each other state: both children are lineage rows. Red at base: exit, claim, cause, remedy, and bytes for unreadable-owner only (the base claim step rewrites the owner registry); unavailable and the unreadable-linked bytes are green.

      harness-validator-lead to harness-qa on distill-validator, bound child only: c39/validator/ok/bound is exit 0, claim, receipt, green; c39/validator/not-found/bound is a lineage row, red: exit, claim, cause, remedy.


      (d) case_40_distill_exemption_never_fires_on_failed_placement. Product lead in the not-found and persona-mismatch states, child harness-code-reviewer declaring X with its tree-root line. All four rows are lineage rows.

      c40/<state>/distill-run: open distill-product run, approved plan, mission distill. Red: cause, remedy.

      c40/<state>/plan-run: open plan-product run, pending plan, mission plan. Red: exit, claim, cause, remedy (base exits 0 and claims).


      (e) case_41_main_and_non_lead_keep_prior_outcomes. Each control dispatches harness-backend-dev declaring Y with no marker, and asserts exit 0 and claim. Run each control in two states: unreadable-owner, the worst on-disk state, which also keeps the claim step''s DEC-218 treat-as-empty recovery; and escaped-oserror, where find_run_claim raises if anything calls it, so a passing row proves the control never reads placement and no other registry state can change its outcome. Rows c41/<control>/<state>, all green at base. Controls:

      main: agent_type Main, harness_agent_id Main, no parent id;

      orchestrator-id: harness-orchestrator with harness_agent_id Orch.Lead;

      orchestrator-no-id: harness-orchestrator with no runtime id;

      lead-no-id: harness-eng-lead with no harness_agent_id. Put a comment above the lead-no-id rows: they assert SC-02''s LEAVE clause for an id-less lead payload; the host refuses an id-less governed nested Task (DEC-218), and the signer''s OQ-1 ruling governs them, so a signed hardening changes exactly these rows.


      (f) case_30_repository_header_binds_exact_factory_claim and case_31_repository_binding_read_from_the_feature_worktree dispatch as harness-eng-lead with harness_agent_id LeadOne and no claim, which is the not-found class. Before their dispatches, bind LeadOne with _load_registry_module().claim_run_start(inflight_registry.feature_root(<checkout>, feature), harness-eng-lead, feature, LeadOne, OrchestratorOne, supervisor_pid=os.getpid(), cwd=<checkout>); in case 31 that is the feature worktree''s registry. Leave their assertions unchanged.

      Register cases 38 to 41 in CASES after case_37_orchestrator_keeps_registered_distill_authority.


      Step 2, fail-first at base source, one inventory for both runs. Before editing dispatch-guard.py, create notes/characterization-pin.md with these lines: dec_number: DEC-258; base_sha: 2e7a2c77d61e3ae93180dc6d71a355ff7b85d8f8; then, under a heading Row inventory, one line predicted_red: <check name> for every assertion that (b) to (e) mark red at base, and no other. Confirm git diff --quiet 2e7a2c77d61e3ae93180dc6d71a355ff7b85d8f8 -- .claude/skills/harness/bin/dispatch-guard.py exits 0, then run python3 tests/integration/test-dispatch-guard.py and append, under a heading Base run: head_at_base_run: <git rev-parse HEAD>; base_run_exit: <exit code>; and one line observed_red: <check name> per FAIL line. The two sets must be equal, and every case 1 to 37 assertion, including the rebound cases 30 and 31, must pass. Any difference means a fixture misses its intended branch: stop and report, and never edit a prediction to fit an observation.


      Step 3, production edit, in .claude/skills/harness/bin/dispatch-guard.py only.

      (i) Add _dispatcher_placement() in the FEAT-2225 T-04 block, beside DISTILL_RUN_RE and LEADS, memoized with a module-level sentinel so find_run_claim runs at most once per dispatch. It returns None when agent is not in LEADS, or when d.get(''harness_agent_id'') is not a non-empty string; that is the prior declared-feature path. Otherwise it calls reg.find_run_claim(owner_root, agent_id) inside try/except (reg.UnreadableRegistry, OSError) as exc; use exactly that typed tuple, never a broad except (the FEAT-65 census requires zero broad catches here). An exception is a refusal with cause registry-error and detail type(exc).__name__: exc. ok true with found[''claim''].get(''agent'') == agent returns found[''feature'']. ok true with another persona is a refusal with cause persona-mismatch. ok false is a refusal with cause found[''cause''] (unreadable, not-found or ambiguous) and detail found[''message''].

      (i'') Feature validity. After the ok check and before the persona check, an ok result whose found[''feature''] is not a non-empty str (isinstance(feature, str) and feature) is a refusal with cause unreadable, detail: the live claim bound to <agent_id> in <found root> names no feature (a malformed claim row), and the unreadable remedy. Add no separate sentinel object: _lookup_placement returns a non-empty str or exits 2, so the persona-mismatch remedy never prints a missing feature. An omitted feature is find_run_claim''s LEGACY_FEATURE, a non-empty str, and passes.

      (ii) Refuse through _refuse with, in order, the lines below; a | separates printed lines. Every printed command follows four rules (validate c0 OQ-1): (1) it is python3 <script> <args>, where <script> is the real sibling path os.path.join(os.path.dirname(os.path.realpath(__file__)), ''inflight_registry.py''), computed once, never the bare script name; (2) every interpolated part, agent_id, feature and root included, is shell-quoted with shlex.quote; (3) no prose punctuation adjoins a command: the command is its own line, indented four spaces, and the prose introducing it ends with '':'' on the line before; (4) the contract sentence is the narrowed one under last. Below, command: <args> stands for that command line.

      first: dispatch-guard: BLOCKED — lineage: <agent> run <agent_id> cannot be placed (<cause>), so its dispatch of <dispatched> for <declared> is refused.

      second: two spaces and the detail; for persona-mismatch the detail is: the live claim bound to <agent_id> belongs to <claim persona> (feature <found feature>, registry <found root>), not <agent>.

      third, the remedy lines chosen by cause (remedy fragments asserted in tests in brackets):

      unreadable: Repair each unreadable registry named above in place and never delete it: an unreadable registry is never read as no claims (DEC-218). Then re-dispatch. [never delete it]

      registry-error whose exception names files (exc.paths for UnreadableRegistry, [exc.filename] for an OSError whose filename is not None): The placement lookup raised on <comma-joined paths>; repair that registry in place and never delete it (DEC-218), then re-dispatch. [repair that registry in place, and the owner registry path]

      registry-error that names no file: The placement lookup raised without naming a file, so no registry is known to be corrupt: run the Inspect command below to reproduce the error and repair only what it names; never delete a registry. [without naming a file; excluded fragment: repair that registry in place]

      not-found: This lead''s run holds no live claim: re-dispatch the lead so its run start reclaims before it dispatches; never re-declare a feature to work around it. [re-dispatch the lead]

      ambiguous: Several live claims are bound to <agent_id> in the registries named above, and the guard never chooses. For each named root, list its claims to see each claim''s feature: | command: list --root <root> | The surplus claim is the one whose feature is not this lead''s open registered run in that feature''s feature.json runs[]; if that does not single one out, the operator decides with the lead''s dispatcher. Release only that claim, in its own registry: | command: release --agent-id <agent_id> --feature <its feature> --root <its root> | If release refuses because that registry holds more than one match, stop and repair the registry by hand; never release by persona. The <root>, <its feature> and <its root> placeholders stay for the operator to fill in. [list --root; release --agent-id Orch.Lead --feature]

      persona-mismatch: Leave a live claim of uncertain ownership alone. If that <claim persona> run is live, dispatch this work from a <agent> run that holds its own claim (a fresh lead run claims at its run start); only if the operator confirms that claim is stale, release it in its own registry, then re-dispatch: | command: release --agent-id <agent_id> --feature <found feature> --root <found root> | Never relabel a dispatch to pass. [belongs to <claim persona>; Never relabel]

      last, always: Inspect: | command: find-run --agent-id <agent_id> --root <owner_root> | A governed lead''s dispatch is placed by its own runtime claim (DEC-258); a placement that cannot be established is refused, never silently rebound to the declared feature.

      (iii) In the module-level sequence, call _dispatcher_placement() exactly once, after _direct_orchestration_refusal() and before _start_preflight(). A failed placement then refuses before any other preflight and before the claim step. Do not reorder _start_preflight and _distill_preflight.

      (iv) One dispatch-local placement answer serves both the route and the distill preflight. Add _placed_distill_feature(), memoized with its own module-level sentinel: None when _dispatcher_placement() is None; otherwise, with destinations, errors from _destinations(), the result of _distill_run_feature(destinations, errors, <placement feature>, agent), computed once, so the dispatcher''s registered run is read once per dispatch. _mission_scope: plan_route = dispatched == PLAN_READER and agent == PLAN_TEAM_LEAD and _placed_distill_feature() is None. Keep declares and the return tuple unchanged. Rewrite its docstring to say the scope-reader route yields only to the dispatching product lead''s trusted distill placement.

      (v) _bound_distill_feature, agent branch: when agent is in LEADS, return _placed_distill_feature() if _dispatcher_placement() is not None, else _distill_run_feature(destinations, errors, declared, agent), which is the prior id-less path. The dispatched-in-LEADS branch is unchanged. Delete _dispatcher_feature; grep the bin directory and tests to confirm it has no other caller.

      (vi) Rewrite the BUG-2110 mission-applicability comment and the FEAT-2225 T-04 comment block to state the placement contract, the single dispatch-local placement answer and the placement-keyed route, citing DEC-258, #2542 and #2532.

      Leave these unchanged: _start_preflight, _distill_preflight, _refuse_unbound_distill_marker, _require_distill_feature, _require_distill_mission, the terminal claim try/except with its emit_unavailable, and every other refusal text.


      Step 4, pin run and receipt. Run the four suites and the git diff check of verify; all must exit 0 and the dispatch-guard suite must print no FAIL line. Commit the three files as the T-01 commit. Then append, under a heading Pin run: tested_sha: <git rev-parse HEAD of that commit>; pin_run_exit: <exit code of python3 tests/integration/test-dispatch-guard.py at that commit>; that suite''s final N of N cases passed line; the exit code of each other suite. Commit the receipt alone, then run verify, which reads the receipt at HEAD. If anything later changes dispatch-guard.py or test-dispatch-guard.py, re-run the four suites at the new commit and append a new Pin run block with its own tested_sha and pin_run_exit; the last block is the one graded, and T-02''s verify re-checks at the end of the build that both files at HEAD equal that tested_sha.

      Never run a shell wait loop. No new public interface, retry, telemetry, dependency or documentation change belongs to this task.

      '
    reason: 'Validate c0 must_fix 1 and OQ-1: an ok claim naming no feature is refused as unreadable; printed commands made copy-runnable (rules 1-4). Ruled by AdvisorA4Validate (notes/answers-2026-11-26-validate-c0.md).'
```
