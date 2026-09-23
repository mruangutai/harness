# Security review — FEAT-64 c0

**PASS.** Reviewed immutable range `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983..dc71e09e0647882c63f66ab0b6d6048bc6dd2688` over the supplied canonical changed-file set. The diff is security-scoped **in** because it changes config/YAML/JSON input, GitHub responses, subprocess failures, repository paths, and exception rendering. No exploitable security regression was found.

## Measured OWASP/STRIDE inspection

- **Injection/subprocesses:** `factory_gh.py:146-180` and `post-merge-sweep.py:189-204` retain list-form argv with `shell=False`; no shell, SQL, template, export/formula, redirect, or user-controlled URL sink was added.
- **Input, paths, and fail posture:** typed failures around manifest, fleet, plan, feature JSON, frontmatter, and YAML preserve existing refusal/unresolved outcomes (`check-plan-routes.py:118-138`, `handoff_done_when.py:420-433`, `harness_boundary.py:970-982`). The plan memo is cleared at the public entry and keyed by feature directory. Containment/realpath decisions are unchanged.
- **GitHub/error material:** `factory_gh.py:167-176` converts malformed success bodies without echoing the response body. `GhError` keeps captured streams as attributes as before; rendered errors use the existing canonical message path. A full pinned-diff credential-pattern inspection found no added token, Authorization header, URL credential, private key, or fixture secret.
- **Exceptions/fail-open:** `_as_repo_module_failure` (`harness_boundary.py:431-439`) preserves the prior load/call conversion and chain. New `hook_guard` (`harness_boundary.py:442-461`) can print exception text and return 0, but it is deliberately unwired at this pin (BRIEF SC-04), so no actor can newly reach that renderer or bypass a hook in this diff. FEAT-65 must re-audit each wired call site.
- **Auth/data/dependencies:** no authorization decision, cross-tenant response, credential handling, dependency declaration, or new network destination changed.

## Explicitly dismissed/advisory

- Future `hook_guard` exception text could contain input-derived detail, and any `fail` value other than `closed` selects open. With zero callers at this pin there is no actor, capability delta, or shipped exposure, so this is not a finding; validate fixed posture and bytes during FEAT-65 wiring.
- Narrowed catches intentionally expose programming defects rather than converting them to success/silence. Expected environment/parser/process failures remain caught at their owning boundaries, so this reduces fail-open masking rather than creating it.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned FEAT-64 boundary narrowing introduces no exploitable security regression; active parsers and subprocesses stay typed and fail as designed, while the only new fail-open renderer is unwired."
  in_scope: true
  scope_reason: "The canonical diff handles untrusted config/manifest/YAML/JSON and GitHub responses, subprocess argv/status/streams, repository paths, and exception rendering, so OWASP injection/exposure/input checks and STRIDE trust-boundary review apply."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "config/manifest/YAML/JSON into validators", stride: "T|D|E", mitigated: true }
    - { boundary: "operator argv and GitHub response into subprocess/parser", stride: "T|I|D", mitigated: true }
    - { boundary: "repository-module failures into gate diagnostics", stride: "I|D|E", mitigated: true }
    - { boundary: "future hook failures into stderr and verdict", stride: "I|E", mitigated: false }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-security-reviewer-c0.md
```
