# Final security review — FEAT-1928

**PASS — F-SEC-01 is closed at the exact review pin; no remaining actionable security finding.** Range: `af2a958ab06c0d6fc026b363b59fc3147e3982f1..83746a425d692f2096f53d343594f1ee9ed8890c`. Read-only source/test review; no tests, validators, mutations, builds, lint or formatting executed.

## Scope and evidence binding

The independently measured census is **692 changed paths** (`artifact://592`): schema/input enforcement, hooks, artifact append and historical readers are in scope for T/E; probes/transcripts, documentation and historical records are in scope for I. Tests/retained fixtures are evidence rather than independently deployed entrypoints. Factory configuration removes a served repository (reduces destination authority); the boundary-module delta is commentary, not a permission change. Persona/skill/doctrine changes carry routing instructions. Full-diff credential-pattern sweeps, split into exhaustive feature/remaining partitions to avoid the search byte cap (`artifact://652`, `artifact://653`), found no credential-shaped matches; this is not a guarantee against arbitrary secret formats.

Read source/test paths match the pin (empty pinned source/test diff). Independently compared executed clean `98b6c38332bf270f4c88dbc89d7b9d044c7b858d` to the pin: exactly six metadata/evidence files differ, no production or test paths. Existing terminal Python evidence is `artifact://570`: 120 files/eight workers/130.15s, including 21/21 SC-07 append cases at lines 7184–7206. These are consumed results, not reviewer executions.

## Prior finding closure and current boundaries

- **F-SEC-01, original high / substance / task, owner T-02, SC-07: CLOSED, not downgraded.** The previous attack was a governed engineering lead naming a product/validator/other run's artifact so the validator replaced that run's authoritative final mapping by appending. `digest_destination.py:24–109` now binds hook-owned child/parent/feature/checkout identity to one PENDING registered run and its manifest-authorized destination; candidate paths must equal that destination and cannot contain traversal. `harness-hooks.ts:891–904,1165–1173` captures and supplies the binding independently of yield data. `digest_destination.py:112–161` opens every directory component and the leaf with `O_NOFOLLOW`, relative to held descriptors; the leaf must be regular and writable. The yield cannot substitute a binding. Owning predicates (`tests/integration/test-validate-digest.py:1652–1696`) assert exit 2, victim byte equality and unchanged selected mapping for cross-squad/run/feature and relative/absolute parent-symlink attacks; terminal evidence above records their success, including wrong-parent/ambiguous-run startup refusal.
- **T-01/T-02 input and reference boundaries:** `digest_schema.py:75–168` uses strict JSON readers, canonical persona resolution and an explicit local referencing registry. `digest-schema.ts:118–185,193–279,299–316` rejects escaping/remote/unresolved/cyclic references and unsupported projection keywords; only successful frozen bundles are cached, keyed by real schema directory and canonical persona. Dropped value constraints remain Python-enforced. `harness-hooks.ts:312–343,1071–1087` refuses dispatcher schema controls in flat/batched tasks, Main included, before claims; there is no permissive schema fallback.
- **T-02 append failures / T-01,T-04 historical parsing:** `validate-digest.py:1824–1894` converts destination/read/write failures to exit 2, uses safe dumping, compares the last mapping for idempotency, and only appends corrections. `digest_record.py:33–87` uses the shared safe YAML loader and intentionally selects the last parseable fenced mapping, without live-schema validation or rewriting. Historical authorization is still the artifact writer's domain; historical parsing is not a new live-input bypass. Missing records/keys remain reported by state readers; plan readers consume structured keys (SC-07/D-03).
- **Inherited limits, not newly closed controls:** `validate-digest.py:2150–2248` retains loud hook-guard exception pass-through and the existing missing-persona/reentrant/#919 environment-failure policies. The OMP hook authors persona and `stop_hook_active:false`; governed yields do not supply those fields. No new attacker-controlled trigger or privilege delta was established for these inherited fail-open policies. This PASS does not assert fail-closed handling of arbitrary validator implementation failures.
- **T-05 / SC-05 exposure inspection:** `notes/live-digest-object-probe-current.md:6–19` and transcript records 20–31 show actual OpenAI OMP18.6.0 native null refusal, same-job retry and completion; launcher identity is distinct from release-tag metadata. Failed Anthropic STRING-null runs remain failures, not native-null proof. Probe credential access selects counts only (`probe-digest-object-contract.py:131–145`); recursive sanitization removes token forms, signatures/encrypted fields and credential-pin hashes (`:78–87,276–287`). Observed transcript credential IDs are selectors, not credentials; no committed credential exposure was found.

Open questions: none. This is a security verdict, not an SC-06 parity acceptance, UAT verdict, or ship/merge authorization; historical generator failures are not successful comparisons.

```yaml
VERDICT: PASS
DIGEST:
  headline: Exact-pin security boundaries close the prior unauthorized digest-append finding.
  in_scope: true
  scope_reason: The 692-path pinned diff changes governed input/schema routing, privileged artifact append, historical consumers and credentialled transcript output.
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - {boundary: Dispatcher input to hook-owned strict persona schema, stride: T, mitigated: true}
    - {boundary: Lead artifact string to authorized registered-run append, stride: E, mitigated: true}
    - {boundary: Traversal or symlink components to privileged artifact descriptor, stride: T, mitigated: true}
    - {boundary: Schema references to local provider bundle authority, stride: T, mitigated: true}
    - {boundary: Credentialled runtime to committed sanitized transcript, stride: I, mitigated: true}
    - {boundary: "Unexpected validator implementation failures (inherited loud fail-open policy, not a new finding)", stride: T, mitigated: false}
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-security-reviewer-final.md
```
