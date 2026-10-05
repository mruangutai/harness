# Grilling — #1928 digest wire format: object is the contract — 2026-09-28

## Destination
Full cutover: every harness agent yields its digest as an object validated against one
per-persona JSON Schema; the hook forwards the object to validate-digest; `digest.md`'s YAML
block is rendered from the validated object; the text path and its workarounds are deleted.

## Mission
mission: plan
reason: new enforcement surfaces (schema files + drift invariant, dispatch refusal, hook write into run dirs); diff spans 8 agent files, 3 skills, ~26 test files; DEC-174 main-session-direct.
confirmed-by: operator

## Settled
- Destination → full cutover (not transport-only, not schema-first-cut-later).
- Text hosts → dropped **for the digest path only**. The SubagentStop/`last_assistant_message` text contract is removed and its docs updated; Claude Code is marked unsupported for the digest contract.
- Schema home → `bin/digest-schemas/<persona>.json` is the single copy (shared parts via `$ref`). No frontmatter `output:`, no generator, no drift invariant. validate-digest validates with `jsonschema` against the same files. The closed contract (DEC-223 PASSTHROUGH/DOCUMENTED_OPTIONAL) moves into the schemas.
- Dispatch → the `tool_call` handler in `harness-hooks.ts` (in-process, sibling of `taskModelOverride`) **refuses** any dispatcher-supplied `outputSchema` or `schemaMode` (top-level or in any `tasks[]` item) and **injects** the persona's schema plus `schemaMode: "strict"` into every harness dispatch via `revisedInput`. No main-session exemption (the FEAT-65 collision came from the main session). Rationale: frontmatter cannot set schemaMode and the default is permissive (omp://tools/task.md:44), so injection is the only way to make the host's native check a hard gate.
- Emitter → agents yield the object (`data: {VERDICT, DIGEST: {…}, artifact}`). Fenced `DIGEST:` templates in the 8 agent files and 3 skills become a schema pointer plus one filled example object per persona. validate-digest's text parsing (strip_comment/split_items/parse_digest/_block_list) is deleted.
- Migration → hard cut. A text report is rejected with a "return the object" message; a census check fails if any agent file or skill still shows the fenced template; the echo-shadowing slice, the last-assistant-message fallback and the hollow-envelope repair (#1676) are deleted in the same merge — the last one gated by the empty-yield requirement below.
- Equivalence requirement → before the old parser is deleted, every existing validate-digest test case is run through the old validator (text) and the new one (converted object); accept/reject must match case for case.
- Empty-yield requirement → a test yields `data: null` under the injected strict schema and shows the host rejects it with a retry and the next valid yield passes. Deleting the #1676 repair depends on it; if the host's job-settling step still ends the job first, it is a decision again.
- digest.md → the lead writes only the human part; after a lead's object passes, **validate-digest.py** (PyYAML `safe_dump`) appends the fenced YAML block rendered from that object. Rules, each with a test: a failed write rejects the report; an unresolvable file rejects the report; an append identical to the last block is skipped; a different object is appended as a correction (DEC-208/#1058). The TS `yamlLines` renderer is deleted. The hook's write is added to the ownership table in `.harness/README.md`.
- Decisions → one new DEC for the design, superseding DEC-172, DEC-216, DEC-223 and DEC-122. DEC-208 stands unchanged.

## Not yet specified
- How on-disk `digest.md` files written before the cutover are read by `check-state` INV-15/46 and `plan-merge.py` (YAML loader for the historical corpus vs. grandfathering by date). pm to sharpen.
- Injected schema shape: whether OMP resolves `$ref` across files and which JSON Schema keywords survive into the model-facing yield schema for every model tier (DEC-152). If not all, the hook injects a bundled, dereferenced schema restricted to the supported subset. pm to verify before task design.
- Self-validation under DEC-174: which hook version governs the validate team's own returns while it judges this change (the main checkout's pre-cutover hook vs. the worktree's new one). pm to specify so the validators are not graded by the contract under review.

## Out of scope
- Dropping the Claude Code host entirely, and the "provider-neutral" claim in AGENTS.md: a separate decision.
- Rewriting digest.md as JSON on disk (rejected in #1928).
- Semantic/cross-file checks in validate-digest (git range, code_grade, receipts, matrix floor, lead roll-up, registry, #919 suite re-run): they survive unchanged and only their input changes.

## Facts I verified (so pm does not re-derive them)
- The OMP output-schema precedence is task item `outputSchema` → agent frontmatter `output` → parent session; the default `schemaMode` is permissive — omp://task-agent-discovery.md:243-249.
- No `.omp/agents/*.md` declares `output:` today; harness-hooks.ts never reads or sets `outputSchema` — scout DigestFacts, at 442611de.
- validate-digest.py is 3120 lines; per-persona fields are Python dicts `SCHEMAS` (:183-263, 9 personas), `PASSTHROUGH` (:267-286), `DOCUMENTED_OPTIONAL` (:368-413); text parsers at ~:562-891 — at a726bad8.
- `jsonschema` is already a required dependency (DEC-190; `feature_schema.py:36`); precedent schemas are `bin/feature-schema.json` and `run-state-schema.json`; there is no `schemas/` dir.
- The `model:` refusal is in-process TS (`taskModelOverride`, harness-hooks.ts:357) and skipped for the main session (:1094); dispatch-guard.py passes through when it breaks (DEC-100); `name:` refusal at dispatch-guard.py:155.
- #1960's string-`data` branch shipped as #1969 (`db18398b`); the hard cut deletes the text path it serves.
- Digest text consumers on disk: `check-state.py` INV-15/INV-46 and `plan-merge.py` record-panel/record-amendments.
