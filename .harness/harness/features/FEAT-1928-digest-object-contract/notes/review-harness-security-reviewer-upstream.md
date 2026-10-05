# Integrated upstream security review — FEAT-1928

**PASS — prior F-SEC-01 high/substance/task remains CLOSED, not downgraded; no new actionable security finding.** Independently inspected `91e88653..3c1923cf2475c1e976b5b941a5b5c7fc445f9e19` and `83746a425d692f2096f53d343594f1ee9ed8890c..3c1923cf2475c1e976b5b941a5b5c7fc445f9e19`, against approved BRIEF/plan and prior security/validator reports. No tests, builds, validators, probes, linters or formatters executed; no source changes.

## Evidence and scope

- Current-main census: 457 changed paths (`artifact://751`); prior-pin delta: 94 (`artifact://766`). Runtime/schema/append/historical consumers are in scope for Tampering/Elevation; instructions and durable assessments for routing integrity; credentialled probes/transcripts for Information disclosure. Tests/parity fixtures are evidence, not deployed entrypoints. Org presentation has no new input/executable security boundary. Upstream expertise/BUG records are instructions/evidence, not a new permission grant.
- Read source/tests/current native receipt match the pin (empty pinned working-copy diff). `c81a57b6..3c1923cf` changes exactly six metadata/evidence files; no source, tests or probe implementation changes. This establishes executed-source equivalence, not reviewer execution. Full current-main diff credential-pattern sweep (`artifact://783`) found no matches for examined token/private-key/literal-secret patterns; not a guarantee against arbitrary secret formats.

## Integrated trust boundaries

- **SC-07 / F-SEC-01 closure:** a governed engineering lead cannot replace another lead/run/feature's authoritative final mapping by naming its artifact. `digest_destination.py:24–109` binds exact host child/parent/persona/feature/checkout to the unique open registered run and manifest-authorized destination, then requires candidate equality without traversal. `:112–151` walks every component with held directory descriptors and `O_NOFOLLOW`, rejects symlink leaves and nonregular/unwritable files. `validate-digest.py:1829–1874` refuses authorization/read/write failures and only safe-dumps/appends. Existing attack assertions at `tests/integration/test-validate-digest.py:1652–1701` demand exit 2, victim byte identity and unchanged selected mapping. Destination/validator/attack tests are byte-unchanged from the prior reviewed pin.
- **Cache is not permission:** `harness-hooks.ts:940–978,1115–1156` checks run readiness and per-mutation runtime authorization before rooting/domain gates; successful absolute resolver answers alone are cached, partitioned by runtime ID/feature/cwd. Refusals, ambiguity and malformed answers are not cached. The CLI resolver (`inflight_registry.py:1004–1015`) rejects ambiguity rather than inheriting its separate Python helper's fallback. Rooting is lexical and never grants authority. `ast_edit` is a mutation and every semicolon-separated target is domain-gated pre/post, including mixed explicit URIs (`harness-hooks.ts:210–237`).
- **Lifecycle merge is correct:** `harness-hooks.ts:994–1009` clears BOTH binding and root cache before run-start/bind. `:1456–1461` clears cache/readiness ONLY at agent-end, deliberately retaining binding for yield ordering. Yield does not reuse cached root authorization: it supplies hook-owned binding separately from the untrusted object (`:1278–1285`); append recomputes destination and rechecks registered open-run identity. Retention therefore does not grant a different child/run authority.
- **Bash interaction:** host feature identity reaches pre/post guards; `check-domain.py:2627–2680` maintains feature-specific high-water marks, sweeps owner plus assigned worktree, and retains full sweep on ambiguity. This is post-write shape reporting, not append authorization. Its narrowing cannot mint digestBinding or bypass the descriptor-bound append destination.
- **SC-01/03/04:** dispatcher controls are rejected flat/batched, Main included, before claims (`harness-hooks.ts:377–407,1188–1205`); canonical local bundles reject escape/remote/cyclic references and unsupported projection, caching only successful frozen bundles (`digest-schema.ts:118–185,193–316`). Terminal null delegates to native strict host rejection (`harness-hooks.ts:1268–1270`), not Python acceptance. Current receipt/transcript explicitly bind clean executed c81 and show same-child null rejection then conforming completion. **The actual current receipt says OMP 18.6.1**, not the dispatch's 18.6.0 shorthand (`notes/live-digest-object-probe-current.md:6–18`, transcript records 19–27). Native live proof is OpenAI-only; Anthropic string-null failures remain failures.
- **Inherited limits:** loud validator hook-guard/missing-persona/reentrant/environment-error pass-through policies remain, not newly closed or newly exploitable controls (`validate-digest.py:2150–2248`). Historical safe YAML selection intentionally does not live-schema-validate records (`digest_record.py:33–87`, D-03). The original code reader's medium unfinished-prose-fence SC-07 mismatch remains real and unchanged; it is not authorization closure and no additional attacker privilege was established. Probe sanitation removes credential-shaped strings, signatures/encrypted fields and credential-pin hashes (`probe-digest-object-contract.py:78–87,276–287`); observed credential IDs are selectors, not secrets.

Open questions: none. This is bounded security validation, not blanket SC-07 compliance, multi-provider live proof or ship/merge authorization. Main owns any further verification; existing final pool and native receipt verification are the relevant checks, not reruns by this reviewer.

```yaml
VERDICT: PASS
DIGEST:
  headline: Integrated pin preserves unauthorized-append closure and introduces no actionable security finding.
  in_scope: true
  scope_reason: Pinned input/schema routing, cached rooting and mutation authorization, privileged append, historical consumers and credentialled transcript output cross trust boundaries.
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - {boundary: Dispatcher input to hook-owned strict persona schema including Main, stride: T, mitigated: true}
    - {boundary: Relative tool targets and cached roots to per-operation runtime authorization, stride: E, mitigated: true}
    - {boundary: ast_edit targets to domain authorization, stride: E, mitigated: true}
    - {boundary: Lead artifact string to registered-run descriptor-bound append, stride: E, mitigated: true}
    - {boundary: Traversal and symlinks to privileged artifact descriptor, stride: T, mitigated: true}
    - {boundary: Terminal null to native strict host acceptance, stride: T, mitigated: true}
    - {boundary: Schema references to local provider bundle authority, stride: T, mitigated: true}
    - {boundary: Credentialled runtime to sanitized committed transcript, stride: I, mitigated: true}
    - {boundary: Unexpected validator implementation failures under inherited loud fail-open policy, stride: T, mitigated: false}
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-security-reviewer-upstream.md
```
