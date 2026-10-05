# Final-merge security review — FEAT-1928

**PASS — merged cold-revival identity restores governance without turning cached placement into append authority. Original F-SEC-01 authorization high remains CLOSED; SC-07 refusal/retry closure remains intact. No new actionable security finding.** Bounded integration concurrence, not ship authorization or a new full-feature audit.

Reviewed approved BRIEF/plan, original security append report and accepted validate-append-validator digest, newest-main-integration and simplify-finalmerge-eng receipts. Current metadata names exact pin `232685fb902a32795e169895fcf3c9fd154a7991`; independently measured prior `f9c9f1e21d05ae1d64f3f1fed38465be89059dc1`→pin: 60 paths (`artifact://912`). Scope IN: hook identity/input/output, prune refusal/retention, CI canonical-reader enforcement and fresh credentialled evidence. Spend aggregation, sequential-PM guidance, decision/index/classification ownership, metadata and historical quality-artifact removals introduce no additional credential, network, dependency or privilege surface. Canonical base is `ee6898b82f36e2ca5f7a27315d56c4785a65cef4`; no 457-path re-audit.

## Concrete boundary conclusions

- **Independent lifetimes, not cached permission (T-02, SC-01/02/07):** `harness-hooks.ts:944–965` caches only successful placement, keyed by runtime id/feature/cwd. `:995–1009` clears both caches before every run-start; only successful exact-id claim startup attempts lead binding. `:1139–1178` checks readiness and per-mutation authorization before placement-cache use. `:1483–1488` drops placement and readiness at turn end; a retained digestBinding cannot authorize a successful unready yield, and the next openRun clears/rebinds it. Binding is never populated from featureRootCache, dispatcher prose or yield fields.
- **Cold revival (T-02, SC-01/02):** `:1079–1108` reads the host session manager's persisted `session_init.systemPrompt/task`, obtains runtime child/parent from runtimeLineage, captures assignment once, and re-enters the same openRun. Later messages/tool output do not establish the revived identity. A known governed persona that cannot reclaim is held, not silently ungoverned; absent lineage cannot pass startRun. Editing trusted persisted session identity requires host/session-file control, not mere later-message access; no new lower-trust escalation was demonstrated. Incoming cold-governed/held/ungoverned tests remain alongside schema-refusal/no-claim tests (`omp-hooks.test.ts:2640–2715`); inspected, not executed here.
- **Strict output and original high closure (T-01/02, SC-01/02/04/07):** `harness-hooks.ts:1204–1231,1295–1315` refuses caller schema controls and loads strict bundles before dispatch claims, then forwards the object plus hook-owned binding. `digest_destination.py:24–109` preserves exact runtime/parent/feature and checkout binding, unique open registered lead run, manifest grant and exact artifact reauthorization; `:112–151` retains descriptor-relative O_NOFOLLOW, regular writable leaf and held O_APPEND handle. Claim settlement before validation is intentional: append trusts the startup binding plus currently registered open run, not a fabricated new live claim or cached root. Integration does not modify this authorization module or validator.
- **Reader visibility/prune provenance (T-01/02, SC-07):** `validate-digest.py:1851–1878` still checks the canonical reader against old text plus the exact safe-dumped suffix before writing that same suffix; failed selection refuses without prose repair, identical object remains no-write. Historical selector remains schema-free (`digest_record.py:33–71`). `prune-run-evidence.py:73–91,106–145` preserves recorded validator PASS runs, shipped-bundle-pin runs and explicit keeps, refuses invalid canonical feature records before deletion, and refuses unmatched keeps. The stronger incoming duplicate-key regression replaces the same-bug test, not its boundary. Main's explicit keeps preserve the three independent quality PASS records; no assertion of universal historical-artifact retention.

## Evidence and assurance limits

Independent `7e2e671304cd3e174989624fc11e8472b5e3b84b`→exact-pin census contains exactly six feature metadata/evidence paths, no source/test/schema/config/probe delta. Inspected source/tests/current native and lifecycle receipts have an empty working-copy diff against pin. Full bounded diff credential-pattern sweep (`artifact://932`) found no examined credential/private-key patterns; credentialId is a selector, and local paths/session ids are not demonstrated authentication material.

Fresh receipt `notes/live-digest-object-probe-current.md:5–21` records Main's native18/18, installed OMP18.6.1 launcher hash separately from release-tag source metadata, raw-null rejection through actual YieldTool.execute, same-job accepted object retry/exit0, transcript hash `ba1fcf4179323573037b1c2e1373f1f090a22dcd1a5387fb70f8defdc6d2fe29`. Latest `notes/live-omp-probe.md` records Main's lifecycle28/28 at executed7e2e. Main's verifier33/33 and pool120/120 are retained reported executions, not mine. Native proof is OpenAI-only; historical Anthropic STRINGnull17/18 FAIL remains. Prior SC-07 RED/refusal/human-fence retry evidence and all eight-SC/four-perspective accepted disposition remain retained, not re-executed or reopened.

**Unchanged limitation, separately retained:** validator loud fail-open policy (`validate-digest.py:2160–2248`) remains unmitigated, not newly fixed by strict native structural validation. Eleven accepted medium costs and three low advisory groups remain unchanged; no new defect or source rework inferred. Only read-only metadata/source inspection and this required report write; no tests, builds, linters, formatters, graders or live probes. No broader host-policy, full accessibility or UAT claim. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: Merged cold revival preserves independent placement and trusted append authority; prior authorization-high and SC-07 closures remain intact.
  in_scope: true
  scope_reason: Bounded integration crosses persisted identity, privileged durable append, canonical routing and credentialled evidence boundaries already reviewed in the prior feature cycle.
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - {boundary: Host-persisted session_init assignment to exact runtime claim on cold revival, stride: S, mitigated: true}
    - {boundary: Successful placement cache to per-operation mutation authorization, stride: E, mitigated: true}
    - {boundary: Strict injected object schema to dispatch refusal before claims, stride: T, mitigated: true}
    - {boundary: Hook-owned digest binding to registered run grant and held append descriptor, stride: E, mitigated: true}
    - {boundary: Human prose plus exact append suffix to canonical selected mapping, stride: T, mitigated: true}
    - {boundary: Invalid feature record to evidence deletion and retained PASS provenance, stride: T, mitigated: true}
    - {boundary: Credentialled runtime to sanitized durable evidence, stride: I, mitigated: true}
    - {boundary: Unexpected validator failures under unchanged inherited loud fail-open policy, stride: T, mitigated: false}
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-security-reviewer-finalmerge.md
```
