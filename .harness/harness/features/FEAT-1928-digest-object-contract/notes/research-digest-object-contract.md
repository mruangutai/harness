# Research — digest object contract

Research baseline: Harness `442611def0f8ad2434dcabefb31b6841eff01b64`; OMP `d0d1f81054a82d0e76d3f0bce42d8a706fe8cb10`.

## Conclusion

The grilling destination is feasible as a hard cut. The live wire format can be a per-persona object, while existing and future `digest.md` files remain append-only prose plus fenced YAML. The implementation must keep two boundaries distinct:

1. live returns accept objects only and are validated first by OMP's injected output schema and then by `validate-digest.py` against the canonical schema file; and
2. durable `digest.md` readers load the last fenced YAML mapping so the historical corpus remains readable without preserving a live text-return compatibility path.

All enforcement-layer source and owning tests must be edited directly by the main session under DEC-174. A validation team can judge a pinned worktree only when it is launched from the main checkout's pre-cutover hook; it must not be graded by the hook version under review.

## Historical digest readers

At the Harness baseline, `check-state.py` imports `validate-digest.py`, reads every completed lead `digest.md`, passes the whole text to the validator, and separately regexes the tail `VERDICT:` for INV-46. `plan-merge.py` uses `_fenced_blocks` and `_lead_digest` for `record-panel` and `record-amendments`, selecting the last fenced block that safely loads to a mapping containing `DIGEST`.

The clean cutover gives historical artifacts a narrow loader separate from live schema authority and provider projection. The durable loader:

- scans fenced blocks from the end;
- selects the last YAML mapping;
- returns that mapping and its structured keys to `check-state.py` and `plan-merge.py`;
- does not import or apply the new closed live schema; and
- never rewrites the file.

Historical mappings contain durable keys outside the new live contract, so validating them against the live schema would break existing readers. Live hook input remains object-only and schema-validated, and a lead object is validated before the validator appends its new fenced block. Historical files therefore need no rewrite or date grandfathering, and the durable loader is not a text-return shim.

The unrelated member-note reader used by INV-47 may retain its note-specific text behavior; those notes are not governed live digest objects.

## OMP schema behavior and provider compatibility

OMP resolves a task schema in caller, agent, session order and defaults `schemaMode` to `permissive` (`structured-subagent.ts`, `resolveSchema`). The Harness hook therefore has to refuse dispatcher-owned `outputSchema` and `schemaMode` at the top-level and in each batch item, then inject both the persona schema and `schemaMode: strict` into every Harness dispatch, including dispatches from the main session.

OMP's yield tool validates the submitted `data` before accepting the yield. A schema failure throws a retryable error; a later schema-valid submission resets the consecutive failure count (`yield.ts`, lines 515–565 at the OMP baseline). This supports the required `data: null` then valid-object test.

OMP's in-tree dereferencer resolves only local `#/$defs/...` and `#/definitions/...` pointers. External references remain unresolved, and `yield.ts` deliberately falls back to a loose object schema when any `$ref` survives. Canonical per-persona files may still share definitions through external `$ref` for Python `jsonschema`; one in-process TypeScript adapter must read those files, resolve and bundle the selected schema, and cache the resolved bundle for the extension lifetime before injection. Load, resolution, or projection failure refuses dispatch. The adapter never falls back loosely, spawns Python per dispatch, or introduces a second hand-authored contract.

The injected bundle should use the common structural subset exercised by the configured OpenAI and Anthropic role families: object, array, string, integer, number, boolean, null, properties, required, additionalProperties false, items, enum, and nested anyOf where a nullable shape requires it. One schema-projection assertion checks that whitelist; a per-model-tier copy would test the same output repeatedly. The terminal injection gate instead runs OMP's canonical schema normalization and compatibility suites once for OpenAI and Anthropic, while the credentialled live probe supplies actual host/provider evidence.

The current role maps contain OpenAI Codex for deep, strong, standard, and review in `openai.yml`, and Anthropic Opus/Sonnet for those roles in `anthropic.yml`. At OMP `d0d1f81054a82d0e76d3f0bce42d8a706fe8cb10`, `schema-normalization.test.ts`, `schema-compatibility.test.ts`, `anthropic-tool-schema.test.ts`, and `provider-schema-compatibility.test.ts` passed together.

## Live host gate

Static and integration tests are insufficient to retire the #1676 hollow-envelope repair. Before deleting it, a fresh disposable OMP subprocess in the feature worktree must receive the injected strict schema, submit explicit `data: null`, observe the native retryable schema rejection, then submit a conforming object and complete successfully. The probe must preserve a feature-local receipt containing the Harness and OMP SHAs, provider/model, exact invocation, null rejection event, retry, valid completion event, exit status, and sanitized transcript hash. A dry run is prerequisites-only and is not evidence.

If the job settles on the null yield instead of permitting the retry, the deletion gate fails and the design returns for a new decision; no fallback or compatibility branch is added silently.

## Durable write rules

For a lead return, the lead writes the human portion of `digest.md` before yielding. After canonical validation, `validate-digest.py` resolves the artifact in the lead's registered checkout, requires a resolvable existing regular file, and appends a fenced YAML block emitted by PyYAML `safe_dump`. A write or resolution failure rejects the return.

The validator compares the submitted mapping with the last fenced mapping. Equality skips the append; a changed valid mapping appends a correction and never replaces prior bytes. This preserves DEC-208. The hook must no longer render YAML; its `yamlLines`, text extraction, assistant-message fallback, echo-shadow slicing, and hollow-envelope repair are all obsolete at the hard cut.

## Contract census and documentation

The object contract affects all 16 validator personas even though only eight agent definitions and three skills currently carry full fenced templates. Canonical schema files are required for:

- harness-ai-dev, harness-backend-dev, harness-code-reviewer, harness-data-engineer;
- harness-dev-ops, harness-documentor, harness-eng-lead, harness-frontend-dev;
- harness-orchestrator, harness-pm, harness-product-lead, harness-qa;
- harness-security-reviewer, harness-ui-reviewer, harness-validator-lead, harness-visual-designer.

A shared schema file may hold reusable object fragments. The per-persona files are the authoritative contracts; there is no frontmatter copy, generated copy, or drift invariant. PASSTHROUGH and DOCUMENTED_OPTIONAL declarations move out of Python and into those schemas.

Eight `.omp/agents` files and `harness-handoff`, `harness-digest-dev`, and `harness-team` must replace fenced return templates with a canonical schema pointer and one filled object example for the relevant persona. The census must reject remaining live fenced digest templates without treating historical feature notes or decision evidence as current instructions.

The design requires one new decision that absorbs the current truths from DEC-122, DEC-172, DEC-216, and DEC-223; those four entries are deleted in the same change under DEC-205. DEC-208's append-only ruling remains semantically unchanged. Current docs must describe the OMP task/yield object contract and remove the old SubagentStop/last-assistant-message contract. The ownership table must explicitly sanction `validate-digest.py` appending the validated block to a run digest.

## Execution boundary

The hook, validator, durable readers, schema bundle loader, gate configuration, and every owning test are enforcement-layer work. DEC-174 therefore routes all of them to `main-session-direct`, as well as the unowned `.omp/agents` edits. There is no governed-team implementation task for those files.

Non-enforcement decision and documentation files can be assigned to `harness-documentor`. That team run must be launched from the main checkout's pre-cutover hook and review the pinned worktree; the worktree's new hook is exercised only by direct tests and the disposable OMP probe. A post-cutover smoke may be a ship gate, but it cannot be the validator team's own grading mechanism.

## Principles applied

- Outcome-Oriented Execution: the plan converges directly on the object-only end state. It permits an explicit schema-artifact phase before activation, but introduces no dual live-input adapter and requires the active cutover task to return with its touched tests green.
- Redesign From First Principles: schemas become the contract at dispatch, validation, examples, and durable rendering rather than being bolted beside the text parser. Every live caller and current document is migrated, and text-only machinery is deleted.
