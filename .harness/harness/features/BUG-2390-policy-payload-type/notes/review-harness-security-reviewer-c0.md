# Security review — BUG-2390 — c0

PASS — no introduced exploitable payload-validation or fail-open policy regression found.

- **Pin/scope:** reviewed authored code `9eb07b4f..369096a4` in `.omp/extensions/harness-hooks.ts` and `tests/unit/omp-hooks.test.ts`, and inspected those files at `79db636b50aa6547edb2b16591f7c26c721f0b47`. The later range changes neither file. Merged BUG-2399 changes are not attributed to this repair. Scope IN: caller-authored expertise ops cross the host-to-policy stdin boundary; classification controls whether policy failures permit operations.
- **Policy classification (T/E):** `harness-hooks.ts:410–447` still handles structured denial and exit 2 before shape-specific inspection. Broad-gate unavailable handling is unchanged. At `:431–433`, arrays yield no Bash command, while object payloads retain the same command extraction and narrow-gate applicability. The only production array call is `expertise-merge.py member-ops` (`:1673–1686`), outside both gate sets; narrow-gate callers construct object payloads. No attacker-controlled array can replace their host-created command envelope through this change.
- **Ops validation (T/E):** `:970–986` rejects non-arrays with the existing refusal message; `opsList` returns the checked array itself, without copying, coercion or array-as-object assertion. `applyExpertise` still performs argument, caller, destination and registered-distillation authorization before forwarding it (`:1658–1686`). Serialization remains `JSON.stringify(payload)` (`:522–530`), and member-ops errors still reach `memberOpsReceipt`, not an automatic allow.
- **Fixture integrity:** `omp-hooks.test.ts:38–44` throws on arrays before object reads; runner/call/callback types honestly carry `PolicyPayload`. Member-ops retains the explicit `[[ADD], [ADD]]` assertion (`:2162–2163`). The six existing payload `as any` reads are unchanged; no new cast relocates the removed lie. Existing malformed-ops rejection remains at `:2077`.
- **Other surfaces:** no dependency, credential consumer, network destination, subprocess argument construction or authorization grant is introduced in the authored two-file delta. Credential-term inspection of the broader pinned diff disclosed no credential value; merged records were not treated as newly authored executable ingress.

Guidance: product AGENTS.md map; control-plane SPEC §§4.2 and 5.3; DEC-174. Recorded receipts show baseline/green 214 passes and static red TS2614 (missing exported PolicyPayload), not a runtime red or demonstrated union-assignment error. These are inspected historical receipts, not checks executed by this reviewer.

Checks performed: pinned Git diff/show and source inspection only. No tests, builds, linters, formatters or fixes. QA owns current-pin gates.

Findings: none. Must fix: none. Open questions: none.
