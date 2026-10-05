# Append-boundary security review — FEAT-1928

**PASS — the prospective canonical-selection guard closes the unfinished-prose-fence seam without granting append authority or modifying human prose. Prior F-SEC-01 high remains CLOSED, not downgraded; no new actionable security finding.** This is bounded security concurrence on SC-07's remedy, not blanket eight-SC acceptance or ship authorization.

Reviewed canonical `91e8865346a7bf4e2b8a5bf2033b17f01f8d6b14..f9c9f1e21d05ae1d64f3f1fed38465be89059dc1`, focusing on the delta from accepted `3c1923cf2475c1e976b5b941a5b5c7fc445f9e19` after approved BRIEF/plan and upstream assessments. Independent git diff binds executed `ee39d8876cde56e06561266ba02dfc174176559f` to the pin: exactly eight metadata/evidence paths, no source/test/schema/config/probe delta. The inspected source and named evidence have an empty working-copy diff against the pin. No tests, probes, builds, linters, formatters or grader executed by this reader.

## Boundary evidence and prior dispositions

- **SC-07 medium/substance/task fence mismatch RESOLVED by refusal and safe retry, not regraded.** `validate-digest.py:1851–1878` reads existing text, preserves identical-mapping no-write behavior, creates one exact `safe_dump(..., sort_keys=False)` suffix, and requires `_last_record(text + suffix, found) == obj` before `target.write(suffix)`. The checked suffix is the written suffix. Failed prospective selection returns actionable close-fence guidance before any write/flush; no automatic prose repair. `_last_record` uses unchanged `digest_record.last_fenced_mapping` (`digest_record.py:33–71`), not a parallel parser, live fallback or schema grandfathering. A changed valid object cannot newly report success while the historical reader selects absent/stale content. An already identical selected record needs no new append.
- **Discriminating evidence remains Main-owned.** `test-validate-digest.py:1497–1512,1586–1592` binds exit code and exact before/after bytes for first-record refusal, stale-correction refusal and closed-prose success. `notes/append-visibility-rework.md` records actual RED22/24 → GREEN24/24, pool120/120 (`artifact://803`), and separate actual CLI refusal2/unchanged bytes → append only the missing human fence → retry0/exact canonical mapping. This closes the seam by rejecting unreadable appends, not by silently weakening SC-07. `runs/simplify-append-eng/digest.md` records four quality PASS/zero applies; `notes/code-risk-current.md` records Main's OLD-grader writer grade4 and cases grade3, not my executions.
- **Original authorization high CLOSED on the existing remedy.** Live closed-schema/semantic validation precedes the lead append (`validate-digest.py:1110–1127,2222–2242`). `digest_destination.py:24–109` rechecks hook-owned exact identity/checkout binding, unique open registered run, manifest grants and exact destination; `:112–151` retains directory/leaf `O_NOFOLLOW`, held descriptors, regular-file checks and append-only handle. The new guard operates inside that authorized handle and cannot mint permission from prose, artifact text or a cached root. No legacy parser/fallback or new credential/network/dependency surface appears in the three production/test/guidance delta paths.
- **Confidentiality:** full canonical diff credential-pattern sweep (`artifact://868`) and direct receipt/transcript/lifecycle sweeps found no examined secret/token/private-key patterns. The unchanged sanitizer removes credential-shaped strings, signatures/encrypted fields and credential-pin hashes (`probe-digest-object-contract.py:78–87,276–287`). Native transcript seq19–27 records null rejection then same-job object acceptance; credentialId is a selector, not a credential. Lifecycle evidence contains operator-local paths/session identifiers, not demonstrated authentication material. Both inspected browser images contain only the operator-reference paragraph; `notes/browser-guidance-proof.md` binds Main's actual rendering, not an independent browser execution by this reader. No data belonging to another user or usable secret was established. Pattern inspection is not a guarantee against arbitrary secret formats.
- **Unchanged limits remain open, not newly closed:** inherited loud fail-open validator policy (`validate-digest.py:2150–2248`); eleven justified medium code costs; low native-null CI guard gap, enum-legend drift guard gap and stale SubagentStop attribution. Prior native/authorization/contrast highs remain closed on their evidence, not downgraded. Current native evidence is OpenAI-only; the two preserved Anthropic STRINGnull17/18 failures and distinct canonical-provider evidence remain unchanged. No extra repair scope or independent accessibility/UAT claim is inferred.

```yaml
VERDICT: PASS
DIGEST:
  headline: Prospective canonical selection closes the append-visibility seam while preserving the original authorization-high closure.
  in_scope: true
  scope_reason: Validated agent input crosses privileged durable append and historical-routing boundaries; new credentialled receipts, transcript and browser artifacts require confidentiality review.
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - {boundary: Live object to closed-schema and semantic validation before append, stride: T, mitigated: true}
    - {boundary: Human prose plus exact suffix to canonical successor-visible mapping, stride: T, mitigated: true}
    - {boundary: Failed prospective selection to unchanged bytes and operator-controlled retry, stride: T, mitigated: true}
    - {boundary: Lead artifact to trusted binding and reauthorized open registered run, stride: E, mitigated: true}
    - {boundary: Traversal or symlink to held append descriptor, stride: T, mitigated: true}
    - {boundary: Credentialled runtime to sanitized transcript and browser evidence, stride: I, mitigated: true}
    - {boundary: Unexpected validator failures under inherited loud fail-open policy unchanged, stride: T, mitigated: false}
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-security-reviewer-append.md
```
