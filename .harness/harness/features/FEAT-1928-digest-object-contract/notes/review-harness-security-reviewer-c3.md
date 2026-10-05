# Security review — FEAT-1928 · c3

**FAIL — the new validator-owned append is a confused-deputy write outside the yielding lead's domain.** Reviewed only `b8e9f9c8f451cfe4b4e211eb97093525b7872c1b..828b3605d6334b96a6d21bfc8f93140b6b26a9c2`; source reads use the supplied source-identical feature worktree. No source edits, suite runs, validators, formatters, or exploit executions.

## F-SEC-01 — high · substance · task · security-reviewer

- **Pinned site / owner:** `.claude/skills/harness/bin/validate-digest.py:1855-1900,1911-1929,2279-2299`; T-02, `change_type: cross_module`, `execution_mode: main-session-direct`; `execution_agent` is absent in the plan (main session owns execution). SC-07's safe registered artifact / DEC-208 boundary is the acceptance anchor.
- **Actor and gain:** a governed engineering lead, including a prompt-compromised lead, can author its own yield but cannot directly write a product/validation lead's run. The validator instead appends the attacker's valid mapping into that other run, changing the final authoritative historical mapping consumed by state/plan readers. Main control-plane `.harness/team-config.yaml:300-324` grants engineering only `runs/*-eng/**`, product only `runs/*-product/**`, and validation only `runs/*-validator/**`.
- **Concrete consumer-visible reproduction (static trace, not executed):** with an existing readable/writable product run digest in the checkout, and no live children in the engineering lead's active run, take an otherwise conforming engineering lead yield and change only `artifact` to `.harness/harness/features/FEAT-1928-digest-object-contract/runs/<existing>-product/digest.md`. Its schema accepts any nonempty artifact string (`digest-schemas/common.json:14-17`); lead semantics check roll-up, not artifact ownership (`validate-digest.py:1381-1404`). Resolution finds the regular file, the suffix check passes, and `_append_record` opens it in append mode. The next historical read selects the engineering mapping rather than the product lead's earlier mapping. No filesystem race, symlink, shell access, or ability to edit the victim file is required.
- **Containment variant:** relative artifacts skip realpath-family containment entirely (`validate-digest.py:1883`); a pre-existing symlink in a parent directory can therefore redirect an otherwise regular `digest.md` outside the checkout. Absolute paths are only bounded to the entire checkout family, never to the authenticated run/feature/domain. These are the same missing destination-authorization boundary, not separate speculative findings.
- **Attribution:** the pinned diff adds `open(found, "a")` and safe-dump append. At the base, artifact handling only read and validated the existing file; it did not mutate it. Thus reuse of broad artifact lookup becomes a new write capability in this diff, not an inherited unauthorized-write finding. Base behavior established by diff inspection, not a base execution.
- **Required acceptance:** before any append, bind the destination to trusted active-run identity and its authorized artifact/domain, not the caller's string; resolve parent components and refuse realpath escape for both relative and absolute forms. A valid engineering yield naming a product/validation digest, another unauthorized feature/run, or an escaping parent symlink must reject and leave every target byte unchanged; legitimate registered appends, identical no-op and append-only corrections must remain supported. Add these destination-boundary cases to T-02's owning integration coverage. Current coverage tests a leaf symlink, not this cross-domain destination (`tests/integration/test-validate-digest.py:1556-1577`).

## Other assessed surfaces

Full pinned changed-path census independently read (403 paths); full diff credential-pattern sweep found no credential-shaped matches. Runtime schemas, loaders, dispatch/yield hooks and historical state/plan readers are in scope for T/E; manual probe and current receipt/transcript are in scope for I. Agent/skill/doctrine updates are routing instructions, reviewed for boundary changes; static tests/fixtures/parity records and other feature bookkeeping add no independent executable surface. FEAT-495's two changes are PR/status metadata only. Historical probe files were not used as current behavior evidence.

- Dispatch controls are refused at top level and each batch item before claim acquisition, including Main (`.omp/extensions/harness-hooks.ts:289-319,1031-1052`). Bundled schemas resolve relative references with lexical and realpath containment, cycle checks and frozen cached output (`.omp/extensions/digest-schema.ts:118-185,294-316`); caller-controlled remote schema retrieval is not introduced.
- SC-05 exposure inspection: current live receipt `notes/live-digest-object-probe-current.md:8-20` contains runtime/provenance/job identifiers and sanitized transcript identity, not authentication material. Current transcript contains numeric `credentialId` selectors, not credential values; credential-store access selects only counts (`tests/manual/probe-digest-object-contract.py:131-145`). Sanitization removes known token forms and signature/encrypted fields (`:79-86,276-287`). No additional secret-exposure finding is supported by observed committed bytes.
- YAML rendering uses safe dumping, and historical reads use the shared safe loader (`validate-digest.py:1926`; `digest_record.py:58-66`); no new executable YAML deserialization or spreadsheet export surface.

Open questions: none. Verification to run after remediation belongs to main; no command is represented here as exercised.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Validator append lets a lead overwrite another domain's authoritative digest mapping.
  in_scope: true
  scope_reason: Strict dispatch/yield routing, new caller-selected artifact writes, historical routing guards, and credentialled probe output cross trust boundaries.
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: security-reviewer
      summary: "F-SEC-01: T-02 validator-owned append authorizes the caller's artifact only by filename/file shape, allowing an engineering lead to append into a product or validation run."
      why: "Pinned validate-digest.py:1855-1929; main-session-direct, no execution_agent specified. Concrete static reproduction and byte-preserving rejection acceptance are recorded above."
  must_fix:
    - Bind the append target to trusted active-run identity and authorized artifact/domain; reject cross-domain and realpath-escaping targets before writing.
  threat_model:
    - boundary: Dispatcher input to hook-owned persona schema
      stride: T
      mitigated: true
    - boundary: Lead-controlled artifact to privileged validator append
      stride: E
      mitigated: false
    - boundary: Appended mapping to historical state and plan routing
      stride: T
      mitigated: false
    - boundary: Credentialled live runtime to committed sanitized transcript
      stride: I
      mitigated: true
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-security-reviewer-c3.md
```
