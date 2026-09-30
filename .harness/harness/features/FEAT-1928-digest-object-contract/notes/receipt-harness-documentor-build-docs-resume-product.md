# T-03 documentation receipt

**BLUF:** The six signed documentation surfaces now describe one hard-cut live digest contract: a closed persona object returned through OMP YieldTool, strict schema injection owned by the task hook, direct object validation at yield, and validator-only append of durable fenced YAML. DEC-237 records the amended number allocation and doctrine.

## Updated

- `.harness/harness/docs/DECISIONS.md` — added DEC-237; deleted DEC-122, DEC-172, DEC-216 and DEC-223; repointed current doctrine; left historical narratives historical. DEC-208 is byte-identical to dispatch HEAD.
- `.harness/harness/docs/DECISIONS-INDEX.md` — regenerated from the authority, removed deleted rows and added the DEC-237 ruling.
- `.harness/harness/docs/SPEC.md` — replaced text/fence returns with complete YieldTool object examples and documented dispatch, retry, artifact, history and host-boundary behavior.
- `.harness/harness/docs/BUILD.md` — added the current OMP procedure and failure table; explicitly marked retained Claude-era material as historical.
- `.harness/harness/docs/org.html` — updated the human-facing digest explanation and complete object example.
- `.harness/README.md` — updated the operator overview, canonical schema pointer and lead durable-record behavior.

## Recorded doctrine

- The fetched-main allocation is DEC-237: origin/main ended at DEC-235, FEAT-1896 owns DEC-236, and the divergent stale `feat/FEAT-46-decision-standard` branch has no PR and does not reserve numbers under the operator's 2026-09-29 ruling.
- All sixteen canonical persona schemas are closed. Every declared property is required; conditional properties remain present; `none` and `[]` express absence; null and undeclared keys are refused; minimal list-entry variants are closed.
- Dispatchers cannot supply `outputSchema` or `schemaMode`. The task hook refuses those keys before claim side effects and injects the canonical schema in strict mode without a loose fallback.
- YieldTool `data` is the object. Missing, null, string, list, wrapped or invalid values return an actionable retryable tool error to the same job; no prose parser, template echo, last-message fallback or host-synthesized digest remains.
- Leads write human prose first. The validator alone appends deterministic fenced YAML after validation and refuses unsafe or unwritable artifacts. Historical readers consume the last safe fenced mapping without retrovalidation or rewriting.
- The object-only digest path is OMP-native. Claude Code has no supported typed YieldTool digest route; broader provider-neutral hook policy and `AGENTS.md` remain outside T-03.

## Verification

- Exact signed command passed: `python3 tests/integration/test-gen-decisions-index.py && python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` — all 12 integration cases printed `ok`; the generated-index diff was empty.
- Direct schema smoke passed: the documented `harness-documentor` and `harness-eng-lead` objects returned no canonical JSON Schema errors.
- Direct structure smoke passed: org HTML parsed and its `section`, `pre` and `div` tags balance; DEC-237 is unique; deleted decision headings and rows are absent.
- DEC-208's complete block is byte-identical to dispatch HEAD.
- Direct read-through covered SPEC §§8/10.4, BUILD §0a and its historical boundary, README's handoff section, the org digest section, DEC-237 and the regenerated index.

No project-wide build, suite, linter or formatter was run, as required. The pre-existing `feature.json` modification was not touched. T-04 anchors and `AGENTS.md` were not changed.
