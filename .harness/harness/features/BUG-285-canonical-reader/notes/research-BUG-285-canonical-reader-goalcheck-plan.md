# Goal-check — BUG-285-canonical-reader current unsigned plan

## Conclusion

**Question:** does the resulting plan deliver the operator's stated intent?

**Answer:** Yes. The eight-task plan remains a `plan` mission and now applies the post-rebase rulings without treating closed issue #285 as live scope. Issue #1594 governs the canonical-reader migration, issue #1682 is an explicit nested-validation requirement in SC-03 and SC-07, and the already-landed #285 fixture is preserved rather than planned again. This is a plan-coverage judgment only: no build, shipment, signature, panel reader, or reviewer was run in this reconciliation pass.

## Source authority and current-main baseline

- `source_issues: [285, 1594]` is retained as provenance. The feature was instantiated from #285 and then governed by #1594; D-05 records that distinction. Issue #1682 is a requirement this plan must close, not an origin issue, so it is carried through the brief and task traces rather than added to `source_issues`.
- Issue #285 is closed by the narrower canonical-reader fix already on current main. Its comment-bearing JSON fixture and central reader coverage are present at `tests/unit/test-feature-json-reader.py`; SC-07 requires that landed coverage to stay green and reserves red-first language for the genuinely new #1682 cases.
- The current checkout is `391b8c80cd7bd5c1bf708f3a064debec72b57e0a`. A fresh local AST inventory of `.claude/skills/harness/bin/*.py` showed the existing `FeatureJsonError`, `load_feature_json`, and `opt_int` in `feature_json_write.py`, with `gh-sync.py#load_recorded` and `factory_decompose.py#load_factory` already calling that reader. T-02 therefore relocates the landed implementation into `artifact_accessors.py`, repoints both real consumers in the same coherent task, preserves compatibility behavior, and adds the new strictness; T-03 explicitly excludes both symbols from semantic-bypass work.
- T-03's file-and-symbol projection was rebuilt from that live AST result. It names current semantic bypass symbols rather than whole-file guesses, including the current GitHub response envelopes, both `handoff_done_when.py` plan reads, `feature-record.py#_budgets_for`, both `inflight_registry.py` parse paths, and the current `gh-sync.py` raw readers. Syntactically proven parser primitives, validated in-memory parses, and locked writer transforms remain classified exemptions rather than hidden omissions.
- T-04's current correct-reader projection now includes the live `feature-record.py#cmd_propose_rework`, `gh-sync.py#_projected_for`, and `worktree_terminal.py#_repo_arg_for_segment` call sites, plus every other current dispatchable `load_plan` or `load_fleet` caller. The stale pre-rebase `feature-record.py#cmd_set_rework` projection is gone. Physical relocation of `manifest_domains` is deferred because its live callers are excluded `.sh` hooks.

## Operator-ruling coverage

- **One accessor layer with an explicit live-code exception:** D-01 and T-02 keep Option B for active in-scope Python readers while leaving `manifest_domains` in `harness_yaml.py` until #1674. The brief records the dependency-light reason: moving a reader whose only live callers are shell-embedded hooks adds forwarding and startup risk without benefiting a Python caller.
- **Useful documentation, not a tested route-table API:** SC-02 and T-02 retain concise module-docstring guidance naming reader and sanctioned writer/source routes. They prohibit a runtime route-table mapping, a provided prose-data interface, duplicated test tables, and assertions over docstring wording; behavior plus the AST classification prove the executable contract.
- **No durable one-shot CLI:** T-01 proves a non-empty pre-migration condition through integration fixtures and the live classification capture. T-07 leaves only the permanent `--canonical-reader-audit` contract. No `--expect-findings` mode is built or retained.
- **Nested validation from #1682:** SC-03 and T-02 require `parse_constant` rejection of `NaN`, `Infinity`, and `-Infinity`, and require a present wrong-typed `github` or `factory` parent/issues field to refuse rather than degrade to the same empty answer as absence. The T-02 verification command runs the central accessor suite and both real-consumer suites, including zero-mutation duplicate-parent and duplicate-task-issue scenarios.
- **Semantic and mechanical separation:** D-04 keeps T-03 as dispatchable semantic bypass work, T-04 as correct-reader relocation, T-05/T-06 as direct-lane semantic gate work, and T-07 as direct-lane mechanical gate relocation plus final enforcement. T-02 owns the landed feature reader's relocation because moving the implementation and updating its only two consumers must remain one buildable change.
- **Python-only boundary and DEC-174:** D-03, SC-08, and T-01/T-07 leave `.sh` parsing blocked on #1674 without a token scanner or heredoc parser. T-08 is restricted to adding `branch-create-gate.sh` to DEC-174's enforcement-layer enumeration and regenerating the index; it adds no feature-scoped #1674 narrative.

## Complete SC/task traceability

Every SC has at least one task, every task traces at least one SC, and all three perspectives remain served:

- SC-01 ← T-01, T-03, T-05, T-06, T-07
- SC-02 ← T-02, T-04, T-07
- SC-03 ← T-02, T-03
- SC-04 ← T-03, T-04
- SC-05 ← T-01, T-05, T-06, T-07, T-08
- SC-06 ← T-04, T-05, T-06, T-07
- SC-07 ← T-02
- SC-08 ← T-07, T-08

The operator perspective is covered by SC-04, SC-05, and SC-08; the code-maintainer perspective by SC-01, SC-02, and SC-03; and the reader perspective by SC-06 and SC-07.

## Panel proportionality and approval

The existing panel roster is unchanged: scope, should-not-exist, design, and goalcheck retain their original reader/persona identities. All eight stored findings remain `disposition: open`. The four proportionality findings retain their exact ids, readers, severities, kinds, and summaries and now each carries `scope: task`:

1. `PF-13232df5d4cb16267b57b26be007de43` — addressed by removing the tested/provided route-table API while retaining maintainer documentation.
2. `PF-2f51f186cf2ca206673d12a3a1771cae` — addressed by removing durable `--expect-findings` work.
3. `PF-f0b326189c54873879085f2f3f226700` — addressed by deferring physical `manifest_domains` relocation until #1674.
4. `PF-2d417a03aa738f4cdd407e416cc77687` — addressed by restricting T-08 to the DEC-174 enumeration and index regeneration.

The plan remains unsigned with `approval.status: pending`; this pass neither adds approval data nor claims shipment.
