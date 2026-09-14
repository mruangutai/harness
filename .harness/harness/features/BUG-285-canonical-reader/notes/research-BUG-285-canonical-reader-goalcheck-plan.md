# Goal-check — BUG-285-canonical-reader applied plan

## Conclusion

**Question:** does this plan deliver the operator's stated intent?

**Answer:** Yes. The applied plan delivers the live intent in issue #1594 and both operator-ruling comments, with issue #285 correctly treated as superseded source context rather than governing scope. Complete SC/task coverage makes it ready to enter the signature gate, where the operator must rule on the four proportionality trade-offs. All eight panel findings remain open; none is recorded resolved. This is a plan-coverage judgment, not a claim that any unbuilt success criterion has shipped.

## Perspective grades

- **operator — pass** — SC-04, SC-05, and SC-08 are carried by T-01, T-03, T-04, T-05, T-06, T-07, and T-08.
- **code maintainer — pass** — SC-01, SC-02, and SC-03 are carried by T-01, T-02, T-03, T-04, T-05, T-06, and T-07.
- **reader (reviewer / qa) — pass** — SC-06 and SC-07 are carried by T-02, T-03, T-04, T-05, T-06, and T-07.

## Operator-intent coverage

- **Live authority and supersession:** issue #285's supersession comment says #1594 subsumes the caller-specific remedy. `BRIEF.md` constraint 1 adopts #1594 plus both rulings as live intent, while SC-07 and T-02 centralize #285's comment-bearing inverse fixture in `load_feature_json` coverage instead of leaving it on `gh-sync.py`.
- **Current-checkout-derived scope:** at checkout `84ecff4a7bdef5008057036b3579cf4c62bd2714`, the raw sites are still distributed across explicit file reads (`gh-sync.py#_record_pr`), GitHub subprocess output and error envelopes (`factory_gh.py#run_gh`, `_project_field_resolve`, `project_resolve`, and `issue_board_item_id`), frontmatter and OMP configuration (`check-omp-port.py#frontmatter` and `check`), validated in-memory text, hook/stdin payloads, and bytes inside locked writer callbacks. T-01 derives the complete file-and-symbol set from live AST output and checks it against one hand-classification artifact; T-03 through T-07 call their file lists current projections, require every classified row and targeted test, and stop for a plan amendment on drift. This answers the panel's former fixed-list omissions without replacing the live inventory with another count.
- **Python-only boundary pending #1674:** D-03, SC-08, T-01, T-07, and T-08 cover only `.py` sources and explicitly exclude `.sh`. Current shell evidence remains visible in `branch-create-gate.sh` and `check-state.sh`; the plan neither migrates it nor claims a token scan, heredoc parser, or exemption count can verify it.
- **AST checker first:** D-02 and the dependency chain place T-01 before T-02, then T-03 through T-08 linearly. T-01 uses genuine `ast.Call` nodes, proves a non-empty pre-migration result, distinguishes prose and aliases, hand-classifies every result, and makes the classification the migration input. T-07 alone switches that same guard to permanent zero drift.
- **One accessor module, Option B:** D-01, SC-02, T-02, T-04, and T-07 move the existing `load_plan`, `load_fleet`, and `manifest_domains` ownership beside all new readers in dependency-light `artifact_accessors.py`, above `harness_yaml.py`. T-04 preserves only the minimum forwarding needed by excluded shell-embedded callers until #1674 and has the AST guard reject new Python use of that forwarding surface.
- **Every parse category:** T-01 requires a row for raw JSON, raw PyYAML, low-level `harness_yaml` calls, explicit artifacts, in-memory validation payloads, hook/stdin payloads, GitHub stdout, canonical locked writer transforms, low-level primitives, and the sole `state.yaml` reader. T-02 supplies `load_feature_json`, `load_harness_json`, `load_plan`, `load_fleet`, `manifest_domains`, `load_frontmatter`, `load_omp_config`, `read_hook_payload`, and `parse_gh_json`; syntactically proven non-reader cases remain explicit exemptions rather than disappearing from coverage.
- **Typed and strict readers:** SC-03 plus T-02/T-03 require extension-selected parsing, UTF-8 reads inside the error boundary, duplicate-key rejection, one documented accessor error type, mapping-shape checks, retained plan-schema and fleet validation, and reuse of `harness_yaml.py`'s strict YAML primitive. T-03, T-05, and T-06 replace broad parse catches with the typed contract where the existing caller handles parse failures and remove silent parse-to-empty defaults instead of relocating them.
- **Separate semantic and mechanical diffs:** D-04 and SC-06 are operationalized as semantic T-03, mechanical T-04, semantic direct-lane T-05/T-06, and mechanical direct-lane T-07. Each task forbids mixing the other class into its review unit.
- **DEC-174 direct-lane proof:** DEC-174 requires enforcement-layer changes and each gate's test to be main-session-direct, with imported library work dispatchable and gate cutovers proven by an identical violation set. T-01, T-05, T-06, and T-07 use `execution_mode: main-session-direct`; T-05/T-06 capture complete pre/post output sets, and T-07 records every legacy `check-plan-routes.py` case's return code and raw stdout/stderr and requires byte equality while keeping new audit cases disjoint. T-08 is documentation-only and records the ruled `branch-create-gate.sh` enumeration.
- **No signature yet:** `plan.yaml` has `approval.status: pending` and no signature. That is the correct pre-gate state; this goal-check does not alter approval.

## Complete SC/task traceability

Every SC has at least one task, every task traces at least one SC, and no perspective is unserved:

- SC-01 ← T-01, T-03, T-05, T-06, T-07
- SC-02 ← T-02, T-04, T-07
- SC-03 ← T-02, T-03
- SC-04 ← T-03, T-04
- SC-05 ← T-01, T-05, T-06, T-07, T-08
- SC-06 ← T-04, T-05, T-06, T-07
- SC-07 ← T-02, T-03
- SC-08 ← T-07, T-08

The BRIEF uses the current perspective/SC goal-record format rather than separate `REQ-NN` entries. The operator requirements above are therefore traced through their governing SCs and tasks, not through nonexistent requirement IDs.

## Panel findings and signature ruling

The current stored panel carries all eight findings as `disposition: open`; none is recorded resolved. For plan coverage, the applied task text addresses the four substantive failure scenarios: live-derived migration ownership and amendment-on-drift (T-01, T-03 through T-07), byte-identical legacy `check-plan-routes.py` behavior (T-07), exhaustive accessor/read/write-route ownership without a runtime prose-table API (T-02), and the formerly omitted dispatchable parse envelopes and plan reads (T-03). Those four findings nevertheless remain open in the panel record.

The other four are proportionality findings. All four remain operator rulings, not resolved findings:

1. `PF-13232df5d4cb16267b57b26be007de43` — SC-02's unit-verified module-exposed "complete read/write-route table" is documentation promoted to tested API with no consumer
2. `PF-2f51f186cf2ca206673d12a3a1771cae` — --expect-findings is one-shot scaffolding shipped as a durable CLI mode on an enforcement gate, and no task removes it
3. `PF-f0b326189c54873879085f2f3f226700` — manifest_domains physical relocation is all cost until #1674 — every live caller is a frozen .sh hook, and no task captures those hooks' pre/post behavior
4. `PF-2d417a03aa738f4cdd407e416cc77687` — T-08 writes feature-scoped #1674 narrative into DEC-174 beyond the ruled enumeration update

**Signature-gate readiness:** ready. The operator must accept, amend, or reject those four proportionality trade-offs when signing; apart from those rulings, the applied plan completely covers the live intent. No build or shipment is claimed.