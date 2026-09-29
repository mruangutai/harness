# BRIEF — FEAT-1928 digest object contract

## Problem

Harness agents return a machine-routed digest as YAML inside Markdown inside a string-valued yield envelope. When the host, dispatcher, template, and hand parser disagree, a byte-correct result can be rejected repeatedly or a malformed result can be normalized into a routing decision; FEAT-65 exhausted six retries on this collision and required recovery from disk and transcript.

## Done when — by perspective

**operator** — I can rely on every Harness dispatch using its persona's closed object contract, including main-session dispatches, and on malformed text, null data, or dispatcher-owned schema controls being rejected instead of repaired or silently accepted. I have live host evidence that the native retry path works before the old repair is removed.

**orchestrator** — I receive the same typed VERDICT, DIGEST, and artifact object from every Harness persona, with exact required and optional fields, so routing never depends on parsing prose or guessing an omitted field.

**code maintainer** — I can change one canonical per-persona schema and know that dispatch injection and canonical validation consume it, while provider-facing bundles contain no unresolved references. The old text parser, renderer, fallback paths, duplicate contract tables, and fenced live-return instructions are gone.

**reader** — I can open a run digest and see the lead's human assessment followed by deterministic validated YAML, including append-only corrections, and existing run digests remain readable and byte-unchanged by state and plan readers.

## Success criteria

- SC-01 (operator): For a single Harness task or every item in a batched task, dispatcher-supplied outputSchema or schemaMode is refused, while every one of the 16 Harness personas receives its own strict injected schema with no main-session exemption; the owning test demonstrates its pre-change failing state.
  verify: automated        evidence: unit
- SC-02 (orchestrator): Each Harness persona's accepted yield data is a closed object containing VERDICT, DIGEST, and artifact with its persona-specific contract; a text report is rejected with an instruction to return the object, and all eight affected agent definitions plus the three shared handoff skills contain an object example rather than a fenced live-return template; the owning tests demonstrate their pre-change failing states.
  verify: automated        evidence: integration
- SC-03 (code maintainer): Sixteen per-persona JSON Schema files under the canonical digest-schemas directory, with shared definitions where applicable, express every previously required, passthrough, and documented-optional field; Python jsonschema reads those files directly, the injected structural bundle has no unresolved reference and satisfies one structural-keyword whitelist assertion, and the terminal gate runs OMP's canonical OpenAI and Anthropic schema normalization and compatibility suites once; the owning tests demonstrate their pre-change failing states.
  verify: automated        evidence: unit
- SC-04 (operator): Through the actual OMP YieldTool path with the injected strict schema, explicit data null produces a retryable schema rejection and the next conforming object completes successfully; the test demonstrates the pre-change failing state.
  verify: automated        evidence: integration
- SC-05 (operator): At the pinned review_sha, the feature-local live-probe receipt names the Harness and OMP SHAs, provider and model, exact disposable OMP invocation, null-data rejection, retry, valid completion, exit status, and sanitized transcript hash; no dry run or simulated event satisfies this criterion.
  verify: inspection
- SC-06 (reader): Before the text parser is deleted, every baseline validate-digest acceptance and rejection case produces the same verdict from its text fixture and the equivalent object, with mismatches blocking the cutover; permanent object-contract tests demonstrate their pre-change failing states and retain the behavioral boundaries after deletion.
  verify: automated        evidence: integration
- SC-07 (reader): A valid lead object is safely dumped and appended after the lead's human prose; an unresolvable or failed artifact write rejects the return, an object identical to the last fenced mapping does not append, and a changed valid object appends a correction without replacing prior bytes. Existing digest files, including historical mappings with keys outside the new closed live schemas, remain byte-unchanged while check-state INV-15 and INV-46 and plan-merge record-panel and record-amendments select their last fenced mapping and consume structured keys without live-schema validation; the owning tests demonstrate their pre-change failing states.
  verify: automated        evidence: integration
- SC-08 (code maintainer): At the pinned review_sha, live code and current instructions contain no digest text parser, TypeScript YAML renderer, last-assistant-message fallback, echo-shadowing slice, hollow-envelope repair, Python PASSTHROUGH or DOCUMENTED_OPTIONAL contract table, or fenced live-return template; current docs describe the object contract and sanctioned validator append, one new decision replaces DEC-122, DEC-172, DEC-216, and DEC-223, and DEC-208's append-only ruling remains unchanged.
  verify: inspection

## Verification gaps

- none; unit and integration have active runners, and the credentialled live OMP observation is preserved as the pinned receipt inspected by SC-05.

## Constraints

- DEC-174 BLOCKS governed-team execution of every enforcement-layer edit and its owning tests. The hook, validator, schema loading and bundling, state and plan gate readers, configuration gate, and their tests are main-session-direct.
- DEC-208 SUPPLIES append-only digest history and worktree-relative artifact resolution. Its ruling remains semantically unchanged: identical validated content is not duplicated and changed validated content only extends the file.
- DEC-202 and DEC-233 SUPPLY OMP as the canonical Harness host and the authored skill tree. This feature removes the digest path's Claude SubagentStop and last-assistant-message contract without broadening its scope to a new host policy.
- DEC-205 SUPPLIES current-truth decision maintenance: the new object-contract decision and deletion of DEC-122, DEC-172, DEC-216, and DEC-223 ship together; deleted numbers are not reused.
- Existing semantic and cross-file checks in validate-digest remain behaviorally unchanged; only their live input changes from text to a validated object.
- Canonical persona schemas may share external references for Python jsonschema. One in-process TypeScript adapter reads those files, resolves and bundles the schema injected into OMP, restricts it to the structural subset supported by the configured OpenAI and Anthropic families, caches resolved bundles for the extension lifetime, and fails dispatch closed on load or projection errors; it never spawns Python per dispatch or hand-authors a second contract.
- Validation teams judge a pinned worktree while governed by the main checkout's pre-cutover hook. The contract under review never grades the validators judging it; direct tests and a fresh disposable OMP process exercise the new hook.
- The cutover is object-only. Historical fenced YAML is a durable artifact format, not a live compatibility input: the historical loader selects the last fenced mapping and hands structured keys to state and plan consumers without applying the new closed live schema. Historical files are neither rewritten nor grandfathered by date, while every live yield and every newly appended block remains schema-validated.

## Out of scope

- Dropping the Claude Code host as a broader platform choice or changing the provider-neutral claim in AGENTS.md; that is a separate decision from this digest-path cutover.
- Rewriting digest.md as JSON on disk; append-only fenced YAML remains the human-readable durable representation.
- Changing validate-digest's semantic or cross-file checks for git ranges, code grade, receipts, matrix floors, lead roll-up, registry state, or issue #919 suite reruns; they survive unchanged and consume the object.

## Approval

status: approved
approved-by: operator (via main session)
date: 2026-09-28
