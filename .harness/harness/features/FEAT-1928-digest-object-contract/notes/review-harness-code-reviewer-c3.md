# Independent code review — FEAT-1928, c3

VERDICT: FAIL. One blocking containment defect in the new durable-record writer. Mechanical Python result: grade_2 (eight gated functions, no mechanical high findings). A second durable-record correctness issue is medium severity.

## Target and evidence boundaries

Reviewed the complete immutable range `b8e9f9c8f451cfe4b4e211eb97093525b7872c1b..828b3605d6334b96a6d21bfc8f93140b6b26a9c2`, not working HEAD. The source in the attached worktree matches that pin; the later changes are feature records. Read approved BRIEF, signed plan, build handoff and approval amendments before assessing the implementation. The build lead's `runs/simplify-eng/digest.md:130` declares `amendments: []`.

Ground truth is the full git diff (tool artifact `artifact://252`) and complete 403-path name inventory (`artifact://264`, including every P0000.json through P0290.json parity fixture). This is not an incremental review of the last human commit. Scope includes the .claude schema/validator/state/panel/skill changes, all .omp changes, six documentation targets and decision index, integration/unit/manual tests, canonical-reader classification, feature records/receipts/fixtures, deleted historical validator fixture, FEAT-495 records and log changes. Historical probe receipts were treated only as historical files, never current runtime evidence.

Exactly three commits carry the repository's `[harness:human]` marker: 27ea22063047a4ea1776eef05a64e05d0a6417b1, 4379809b1ce7e37e89407b2ade7912abc898fed9, 828b3605d6334b96a6d21bfc8f93140b6b26a9c2. Commit 14f04a75410acf26d0f1a9179fe52bff0c361815 is also covered by the full range, but lacks that marker and is therefore not added to the marker-derived return field.

No tests, builds, linters, formatters, live probes or mutations were run. Findings below are REASONED from pinned code, not claimed MEASURED reproductions. The explicitly required independent pre-cutover code grader was run once:

`python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base b8e9f9c8f451cfe4b4e211eb97093525b7872c1b --head 828b3605d6334b96a6d21bfc8f93140b6b26a9c2`

Its observed result: 203 passing records and eight grade-2 records. This report does not borrow the builder's grading totals as its own evidence.

## Stage 1: specification compliance

- SC-01 / D-01: `.omp/extensions/harness-hooks.ts:275-320,1037-1050` refuses caller schema controls (including batched task items), injects persona-owned strict schemas and performs this before dispatch-guard side effects. Main's model exemption does not exempt schema injection.
- SC-02: `.omp/extensions/harness-hooks.ts:1115-1122` rejects absent/null/string/list data and sends the object itself to the Python hook. Agent and skill diffs replace live full-return fenced examples with object returns; partial historical/amendment YAML examples are not a second live transport.
- SC-03 / D-02: `digest_schema.py` owns canonical Python validation; the sixteen persona JSON files and common.json are the source contract. `digest-schema.ts` resolves relative references, rejects escaping/cyclic/unresolved references, projects the structural allowlist, freezes and caches the bundle by canonical root and persona. Tests bind actual canonical schemas and actual hook dispatch, not merely a separately hand-maintained expected schema.
- SC-04/05: current receipt `notes/live-digest-object-probe-current.md` records the installed runtime/launcher identity separately from release source metadata, harness source pin, provider/model invocation and fresh transcript hash. It records a real explicit-null yield refused retryably by the OMP tool-call hook before native YieldTool.execute, followed by a valid object completion in the same job. This is evidence supplied by the receipt, not a probe executed by this reader. The narrow host-stage interpretation question below remains explicit.
- SC-06: persistent parity fixtures carry baseline provenance and mapped object results. The all-fields-required contract and its planned deltas were approved; absence of fields in old text examples is not silently grandfathered. I did not rerun the parity harness.
- SC-07 / D-03: `digest_record.py:34-76`, check-state consumers and `plan_merge/panel.py` share last successfully loaded fenced mapping semantics without importing live schema validation. Live appending has the two defects below.
- SC-08 inspection: `.omp/extensions/harness-hooks.ts:1115-1122,1295` removes string rendering and last-assistant fallback; `.claude/skills/harness/bin/validate-digest.py:2205-2299` consumes `digest_object`, not assistant prose. The full diff removes live text extraction, echo shadow acceptance and hollow-return repair. `.harness/harness/docs/DECISIONS.md` replaces DEC-122/172/216/223 with DEC-237; DEC-208 is not modified by this diff. Historical fenced mapping reading remains deliberately separate rather than a live compatibility shim.

### F1 — high, blocking: relative artifact paths escape through a parent symlink

Kind: substance. Original severity: high. Raising reader: code-reviewer. Scope: task. Pin: 828b3605d6334b96a6d21bfc8f93140b6b26a9c2.

Exact owning path: `.claude/skills/harness/bin/validate-digest.py:1827-1887` (`_durable_artifact_candidates`, `_resolve_durable_digest`, `_unsafe_digest_reason`), with the write at 1911-1935. Binding: T-02, change_type `cross_module`, execution_mode `main-session-direct`, execution_agent absent in signed plan. Acceptance violated: SC-07 safe durable append / D-01 governed object contract.

Consumer-visible reproduction (REASONED): create an existing external regular `digest.md`; make a run-directory parent beneath the feature root a symlink to that external directory; submit an otherwise-valid lead return with relative artifact `runs/escape/digest.md`. Candidate resolution joins that relative path to the feature root. The final component is a regular file, so `os.path.islink(found)` is false and `os.path.isfile(found)` true. The containment check is disabled specifically for relative input (`owner_root = ... if os.path.isabs(path) else None`). Consequently the hook accepts and appends the validated object to the external file. Rejecting literal `..` and final-component symlinks does not contain a resolved parent symlink. This is a newly privileged writer crossing the intended checkout/worktree boundary, not an advisory formatting preference.

Required acceptance: the relative parent-symlink escape must return refusal (exit 2) without altering external bytes; equivalent absolute escape and sibling-prefix paths must also remain refused; ordinary in-family files and approved linked-worktree targets must retain intended behavior. Apply resolved containment consistently before opening an append target. Main should add/exercise an actual hook-mode fixture, not only invoke the helper, to prove the accepted object cannot bypass the check. This finding owns only T-02; it does not re-gate documentation or T-04 historical readers.

### F2 — medium: successful append need not become the durable last mapping

Kind: substance. Original severity: med. Raising reader: code-reviewer. Scope: task. Pin: 828b3605d6334b96a6d21bfc8f93140b6b26a9c2.

Exact owning path: `.claude/skills/harness/bin/validate-digest.py:1911-1935`; consumer semantics at `.claude/skills/harness/bin/digest_record.py:34-66`. Binding: T-02, change_type `cross_module`, execution_mode `main-session-direct`, execution_agent absent. Acceptance violated: SC-07, newly appended validated object must be the mapping successors read, preserving old prose bytes.

Consumer-visible reproduction (REASONED): the human assessment ends with an unclosed ` ```text ` fence (without the surrounding spaces). Submit a valid lead object. `_append_record` appends an opening YAML fence and its closing fence and returns success. The durable reader is already inside the text fence: it treats the new YAML opener/body as text and the appended closer as the end of the text fence, which is ignored as a record. A new record has no usable mapping; a correction after an earlier valid mapping leaves consumers reading the stale earlier mapping. Thus success output does not establish the promised postcondition. No special return schema or malformed YAML object is needed; the input state is unfinished human Markdown.

Acceptance: cover both an initial assessment and a correction after an earlier mapping with an unclosed triple-backtick prose fence. Either refuse without changing bytes or produce an append preserving prior bytes for which the actual durable reader returns the submitted object. Refusal rather than undocumented Markdown repair is the narrower contract-preserving option. Medium reflects the unusual malformed prose state; this is recorded separately from the blocking containment defect.

### Scope questions, not invented task findings

Q1 (nonblocking): the full range also includes FEAT-495 feature/plan updates and an associated ship commit. These cannot be bound to T-01..T-04 or a digest-contract acceptance criterion. Recommend explicitly classifying them as unrelated record bookkeeping excluded from this feature's source acceptance, rather than retroactively inventing an owner/task.

Q2 (nonblocking): SC-04 names the actual YieldTool path and a schema rejection; the fresh receipt explicitly measures refusal in `harness-hooks.ts:1115` before YieldTool.execute. This establishes a real installed-host retry, but does not independently establish native executor schema-validation rejection of null. Recommend clarifying whether tool-call hook enforcement is the intended acceptance boundary; if native executor enforcement is required, require a receipt measuring that stage. No historical transcript is substituted for missing stage evidence.

## Stage 2: code quality

The structural adapter/canonical validator split is appropriate: Python keeps semantic checks while TypeScript does reference-free structural projection rather than copying persona definitions. Durable-record readers share one narrow module, preventing the old separate block-selection rules from diverging. Live text compatibility paths are removed rather than retained as aliases. Findings above are the new writer's correctness boundary, not a request for a larger abstraction.

### Independently graded grade-2 findings (all med, nonblocking)

Each row is a substance/task finding raised by code-reviewer, original severity med, at the same pin. These are measured maintainability costs accepted with reasons, not assertions of broken shipped behavior. Acceptance is to retain an explicit reason for the gated function and preserve the named behavior; no required source rewrite follows solely from a grade-2 result. All are owned by T-02 (`cross_module`, `main-session-direct`, no execution_agent), except `_object_shape_violations`, owned by T-01 (`api`, `main-session-direct`, no execution_agent).

| Exact path and function | Observed grade drivers | Independent reason / concrete behavior to preserve |
|---|---|---|
| `tests/manual/probe-digest-object-contract.py:400` `_task_dispatch` | cyclomatic 16, cognitive 7, ABC 25.4 | A receipt needs both single-task and batched dispatch frames, request/schema ownership and refusal evidence. Keep correlation of the actual host frames, rather than hiding it in one-use helpers. A wrong first dispatch or omitted task-item schema would change the derived evidence. |
| `tests/manual/probe-digest-object-contract.py:416` `_yields` | cyclomatic 13, cognitive 19, ABC 28.7 | The function joins yield calls to tool results by identity and keeps missing/malformed/result-error distinctions. Flattening it into unrelated scans risks falsely pairing a null attempt with the accepted object result. |
| `tests/manual/probe-digest-object-contract.py:536` `derive` | cyclomatic 9, cognitive 8, ABC 27.9 | One evidence assembly point names invocation, dispatch, null rejection, correction and terminal status. Its independent evidence fields are the probe's contract; splitting merely to reduce assignment count obscures their provenance. |
| `tests/manual/probe-digest-object-contract.py:663` `run_live` | cyclomatic 4, cognitive 4, ABC 26.4 | One session owner controls the real process, child exchange, transcript capture and finally cleanup. Preserve the single lifecycle; do not manufacture helper abstractions for an ABC-only gate. |
| `tests/manual/probe-digest-object-contract.py:879` `verify` | cyclomatic 11, cognitive 10, ABC 30.0 | Ordered preconditions and identity/provenance/evidence verification must refuse an incomplete receipt instead of accepting an attractive partial transcript. Its explicit phases make this boundary auditable. |
| `tests/manual/probe-digest-object-contract.py:902` `main` | cyclomatic 9, cognitive 13, ABC 35.9 | CLI routing owns mutually exclusive verify/dry/live modes and preflight/output handling. This is straight-line command lifecycle plus mode selection, not domain logic needing a new service layer. Preserve literal routing to the actual probe/receipt verifier. |
| `tests/unit/test-digest-dev-skill.py:115` `check_refusal` | cyclomatic 6, cognitive 4, ABC 30.7 | Assertions bind the skill's actual refusal example, canonical schema and receipt/ownership prose. Keep both positive object guidance and forbidden live transport/control assertions; a hand-written constant substitute would lose the real subject. |
| `tests/unit/test-digest-schemas.py:146` `_object_shape_violations` | cyclomatic 12, cognitive 21, ABC 24.2 | A shared recursive walker checks closed objects, all required keys and disallowed null forms throughout the actual canonical schemas. Its branches express one tree invariant, not independent business cases requiring distinct modules. |

The modified eight-case record-panel refusal fixture in `tests/integration/test-plan-merge.py` also remains coherent: one byte-identical plan fixture tests independent refusal reasons. It improves from its baseline grade and is not one of the eight gated grader records; it must not be reported as a ninth gated function.

### Tests, principles and handoff

Kept tests bind production subjects: the canonical loader/projection, hook task/yield path, durable reader/writer, panel consumers and state checks. Positive dispatch/object cases accompany transport/control absence checks. The manual receipt derives retry outcomes from actual tool frames, not the final assistant summary. Recorded suite results and fail-first claims in build receipts remain builder/QA evidence, not this reader's own execution.

Principles applied in review: `migrate-callers-then-delete` supports the clean removal of live text paths while deliberately retaining the distinct historical reader; `model-the-domain` supports a canonical schema registry and separate durable-record contract instead of mutable optional-field tables; `delete-first` supports deleting the obsolete validator fixture and shadow paths rather than maintaining compatibility shims. The remaining containment defect is an unsafe resolved boundary, not justification to expand the feature.

Main should reproduce F1 and F2 and run the affected signed T-02 verify block exactly as recorded in plan.yaml after changes land. I do not restate or shorten that multiline command here. No verification command was changed by this review. Only this report was written; source/tests/docs remain unchanged.
