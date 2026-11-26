# T-02.intent amendment — main-session-direct build (DEC-174), ruled by AdvisorA3Wording

```yaml
VERDICT: PASS
DIGEST:
  amendments:
  - task: T-02
    field: intent
    was: 'HARNESS-FEATURE: FEAT-2542-dispatcher-placement. Product checkout: Harness itself, feature worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement. It ships no docs/spec.md, docs/decisions.md or docs/architecture.md; the authority read is .harness/harness/docs/DECISIONS.md (DEC-100, DEC-174, DEC-204, DEC-214, DEC-218, DEC-228, DEC-250, DEC-253, DEC-254 and DEC-257 as the format model), the BRIEF, plan.yaml decisions D-01 and D-02, the research note, and notes/characterization-pin.md. The main session writes this directly after T-01 lands. Edit only DECISIONS.md and DECISIONS-INDEX.md.


      Number. Use the dec_number T-01 recorded in notes/characterization-pin.md, which is DEC-258. If HEAD''s DECISIONS.md already carries a DEC-258 heading when this task starts, stop and report to the operator: renumbering would rewrite T-01''s gated source and the signed plan, so it is an operator-ruled amendment, never an edit inside this task.


      Append one entry after DEC-257, headed exactly:

      DEC-258 — A governed lead''s dispatch binds to its own runtime placement or is refused; the scope-reader route keys on that placement

      as a level-two heading.


      Follow DEC-255 and DEC-257''s shape: Chose, Over, Because, Tradeoff accepted, Record. Cite symbols, never file:line anchors (check-decision-anchors.py). It must state:


      Chose, rule 1 (#2542). A dispatcher in LEADS whose payload carries harness_agent_id is placed only by its own runtime claim through find_run_claim, persona-matched. dispatch-guard.py _dispatcher_placement runs once, before any other preflight and before any claim. There are five denial states, each an exit-2 lineage refusal naming its cause token, the runtime id, a remedy specific to that cause and the find-run inspect command:

      structured unreadable (unreadable): repair in place, never delete;

      escaped UnreadableRegistry or OSError (registry-error): repair the named registry, or, when the exception names no file, reproduce it with find-run before repairing anything;

      not-found: re-dispatch the lead so its run start reclaims;

      ambiguous: the operator identifies the surplus claim per registry root with list --root and releases only it in its own registry with --root, never by persona; the guard never chooses;

      ok with a persona mismatch (persona-mismatch): a live claim of uncertain ownership is left alone; work is re-dispatched from a correctly claimed lead run, or the operator releases a confirmed-stale claim in its own registry.

      None of the five is ever the declared feature, and none is ever the unavailable outcome. An unreadable registry is left as found.

      Unchanged: Main, non-lead dispatchers with or without harness_agent_id, and a lead payload without harness_agent_id keep the declared-feature path. The host already refuses an id-less governed nested Task (DEC-218), so the guard does not duplicate that refusal.

      Chose, rule 2 (#2532). The harness-product-lead to harness-code-reviewer scope-reader rule in _mission_scope holds unless that trusted placement resolves to the lead''s one open registered distill-* run, matched by registered_destination and DISTILL_RUN_RE. The route and the distill preflight consume one dispatch-local answer, _placed_distill_feature, read once, so the exemption and its enforcement cannot see different run state. A distill-placed start then flows into the unchanged distill preflight, which enforces marker, feature and tree root. A distill-placed lead declaring plan is still refused, so no relabeling works in either direction.

      Over: the unavailable outcome for these states; the silent declared-feature fallback, which is the defect; a declared-mission or child-field exemption; a run-id or phase-field plan detector, since run records carry no phase; panel existence; reordering _start_preflight and _distill_preflight; reading the registered run separately for the route and for the preflight; relaxing find_run_claim''s any-unreadable strictness, which backs release_run and markerless revival.

      Because:

      the measured base behaviour in the research note: all seven failed-placement fixtures claimed, and the FEAT-2489 product distill dispatch was refused without consulting placement;

      the hook lets a governed lead dispatch only from a ready, claimed run, so a failed placement is an anomaly with no backstop;

      DEC-100''s own text, A refusal outranks it;

      DEC-204, a run recovers its feature only from the one live claim bound to its exact runtime id, and release is exact;

      DEC-218, cannot-read is never no-claims;

      DEC-250, text supplies no authority.

      Tradeoff accepted:

      a corrupt registry or lost claim now stops that lead''s dispatches until the operator repairs it;

      the escaped state is reachable only by fault injection, proven through a copied bin tree;

      Main and non-lead dispatches keep the claim step''s DEC-218 treat-as-empty recovery.

      Record: FEAT-2542 (#2542, #2532); D-01 and D-02 with their signer and date from plan.yaml approval. State that it amends none of DEC-100, DEC-174, DEC-204, DEC-214, DEC-218, DEC-228, DEC-250 or DEC-253; that DEC-214''s HARNESS-FEATURE-TREE-ROOT prerequisite is enforced unchanged on a distill-placed child; that DEC-253''s registered-distill dispatch prerequisite is restored for a product distill while its caller-bound apply and raw Write grants are unchanged; and that it was executed main-session-direct under DEC-174. Refs: DEC-100, DEC-174, DEC-204, DEC-214, DEC-218, DEC-228, DEC-250, DEC-253.


      Then run python3 .claude/skills/harness/bin/gen-decisions-index.py in write mode. Hand-write the ruling text after the '' :: '' of the new DEC-258 row; the generator never writes it:

      A governed lead''s nested dispatch binds to its own runtime claim or is refused at exit 2 in five named states; the product-lead scope-reader rule yields only to a placed distill-* run.

      Never hand-edit line anchors; regenerate them. Leave every other entry and row unchanged. Commit, then run verify: its last steps are the build''s terminal gate, re-running the dispatch-guard suite and checking that dispatch-guard.py and test-dispatch-guard.py at HEAD equal the last tested_sha in notes/characterization-pin.md. If they differ, apply T-01 Step 4''s re-run rule before this task closes. Only plan.yaml station writes may follow this commit before the review pin.

      '
    now: 'HARNESS-FEATURE: FEAT-2542-dispatcher-placement. Product checkout: Harness itself, feature worktree /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement. It ships no docs/spec.md, docs/decisions.md or docs/architecture.md; the authority read is .harness/harness/docs/DECISIONS.md (DEC-100, DEC-174, DEC-204, DEC-214, DEC-218, DEC-228, DEC-250, DEC-253, DEC-254 and DEC-257 as the format model), the BRIEF, plan.yaml decisions D-01 and D-02, the research note, and notes/characterization-pin.md. The main session writes this directly after T-01 lands. Edit only DECISIONS.md and DECISIONS-INDEX.md.


      Number. Use the dec_number T-01 recorded in notes/characterization-pin.md, which is DEC-258. If HEAD''s DECISIONS.md already carries a DEC-258 heading when this task starts, stop and report to the operator: renumbering would rewrite T-01''s gated source and the signed plan, so it is an operator-ruled amendment, never an edit inside this task.


      Append one entry after DEC-257, headed exactly:

      DEC-258 — A governed lead''s dispatch binds to its own runtime placement or is refused; the scope-reader route keys on that placement

      as a level-two heading.


      Follow DEC-255 and DEC-257''s shape: Chose, Over, Because, Tradeoff accepted, Record. Cite symbols, never file:line anchors (check-decision-anchors.py). It must state:


      Chose, rule 1 (#2542). A dispatcher in LEADS whose payload carries harness_agent_id is placed only by its own runtime claim through find_run_claim, persona-matched. dispatch-guard.py _dispatcher_placement runs once, before any other preflight and before any claim. There are five denial states, each an exit-2 lineage refusal naming its cause token, the runtime id, a remedy specific to that cause and the find-run inspect command:

      structured unreadable (unreadable): repair in place, never delete;

      escaped UnreadableRegistry or OSError (registry-error): repair the named registry, or, when the exception names no file, reproduce it with find-run before repairing anything;

      not-found: re-dispatch the lead so its run start reclaims;

      ambiguous: the operator identifies the surplus claim per registry root with list --root and releases only it in its own registry with --root, never by persona; the guard never chooses;

      ok with a persona mismatch (persona-mismatch): a live claim of uncertain ownership is left alone; work is re-dispatched from a correctly claimed lead run, or the operator releases a confirmed-stale claim in its own registry.

      None of the five is ever the declared feature, and none is ever the unavailable outcome. An unreadable registry is left as found.

      Unchanged: Main, non-lead dispatchers with or without harness_agent_id, and a lead payload without harness_agent_id keep the declared-feature path. The host already refuses an id-less governed nested Task (DEC-218), so the guard does not duplicate that refusal.

      Chose, rule 2 (#2532). The harness-product-lead to harness-code-reviewer scope-reader rule in _mission_scope holds unless that trusted placement resolves to the lead''s one open registered distill-* run, matched by registered_destination and DISTILL_RUN_RE. The route and the distill preflight consume one dispatch-local answer, _placed_distill_feature, read once, so the exemption and its enforcement cannot see different run state. A distill-placed start then flows into the unchanged distill preflight, which enforces marker, feature and tree root. A distill-placed lead declaring plan is still refused, so no relabeling works in either direction.

      Over: the unavailable outcome for these states; the silent declared-feature fallback, which is the defect; a declared-mission or child-field exemption; a run-id or phase-field plan detector, since run records carry no phase; panel existence; reordering _start_preflight and _distill_preflight; reading the registered run separately for the route and for the preflight; relaxing find_run_claim''s any-unreadable strictness, which backs release_run and markerless revival.

      Because:

      the measured base behaviour in the research note: all seven failed-placement fixtures claimed, and the FEAT-2489 product distill dispatch was refused without consulting placement;

      the hook lets a governed lead dispatch only from a ready, claimed run, so a failed placement is an anomaly with no backstop;

      DEC-100''s own text, A refusal outranks it;

      DEC-204, a run recovers its feature only from the one live claim bound to its exact runtime id, and release is exact;

      DEC-218, cannot-read is never no-claims;

      DEC-250, text supplies no authority.

      Tradeoff accepted:

      a corrupt registry or lost claim now stops that lead''s dispatches until the operator repairs it;

      the escaped state is reachable only by fault injection, proven through a copied bin tree;

      Main and non-lead dispatches keep the claim step''s DEC-218 treat-as-empty recovery.

      Record: FEAT-2542 (#2542, #2532); D-01 and D-02 with their signer and date from plan.yaml approval. State that it amends none of DEC-100, DEC-174, DEC-204, DEC-214, DEC-218, DEC-228, DEC-250 or DEC-253; that DEC-214''s HARNESS-FEATURE-TREE-ROOT prerequisite is enforced unchanged on a distill-placed child; that DEC-253''s registered-distill dispatch prerequisite is restored for a product distill while its caller-bound apply and raw Write grants are unchanged; and that it was executed main-session-direct under DEC-174. Refs: DEC-100, DEC-174, DEC-204, DEC-214, DEC-218, DEC-228, DEC-250, DEC-253.


      Then run python3 .claude/skills/harness/bin/gen-decisions-index.py in write mode. Hand-write the ruling text after the '' :: '' of the new DEC-258 row; the generator never writes it:

      A governed lead''s nested dispatch binds to its own runtime claim or is refused at exit 2 in five states; the scope-reader rule yields only to a placed distill-* run.

      Never hand-edit line anchors; regenerate them. Leave every other entry and row unchanged. Commit, then run verify: its last steps are the build''s terminal gate, re-running the dispatch-guard suite and checking that dispatch-guard.py and test-dispatch-guard.py at HEAD equal the last tested_sha in notes/characterization-pin.md. If they differ, apply T-01 Step 4''s re-run rule before this task closes. Only plan.yaml station writes may follow this commit before the review pin.

      '
    reason: DEC-258 index ruling cut 32->30 words to pass T-02's own verify cap (test-gen-decisions-index.py); prose only, no contract change; ruled by AdvisorA3Wording (notes/answers-2026-11-26-t02-wording.md).
```
