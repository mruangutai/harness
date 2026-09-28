# FEAT-68 security review — validate c2

**FAIL.** I reviewed full SHA `ab17ca1705f85846c446c0921d53ad3544d5b300`, independently measuring the deduplicated union of `e655f14a56a14bf1777cae55a19195c9af10505d..9ab1813e86067ca4a21a84f49364cf4f453055b4` and `9ab1813e86067ca4a21a84f49364cf4f453055b4..ab17ca1705f85846c446c0921d53ad3544d5b300` as **156 paths**. I inspected that complete union and all 16 required named inputs: BRIEF, plan, six run digests, five evidence notes, and three preserved receipt scripts. Scope included the five authorization/input-sensitive Python decompositions, deleted renderer and 102 browser-interpreted HTML derivatives, owning tests/reference changes, and post-pin provenance/evidence changes.

## Security assessment

The production delta introduces no exploitable auth, injection, secret, SSRF, dependency, deserialization, logging, export, or cross-user disclosure regression. The authorization-sensitive `harness_boundary.classify` and `check-domain.domain_check` decompositions retain ordered denial behavior, including the unknown-verdict default to `_deny_verdict`; plan, board, and layout inputs retain their validation/finding paths. Removing `render-brief.py` and the 102 HTML derivatives reduces interpreted-output exposure. Credential-shaped review found only explanatory `src/secrets.py` prose, not a credential.

VF-03 is repaired: `notes/clean-pin-byte-receipts.md:31-34` now states checkout-root-only normalization, consistent with its 53/57 table, exact D-01..D-05 bytes, `notes/build-divergences.md:1-52`, and A-1..A-3. Full implementation-pin provenance is also present in `notes/red-first-receipts.md:1-4` and `notes/build-divergences.md:1-3`; chronology and recorded measurements are unchanged.

## Finding

**SEC-C2-01 — form, medium, T-01 / main-session-direct.** `notes/clean-pin-byte-receipts.md:22-27` calls its commands “Exact invocations, from the repository root” but commands 2 and 3 invoke `notes/receipt-scripts/...`; that directory does not exist at repository root. The preserved scripts actually live under `.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts/`. Further, `notes/receipt-scripts/feat68-cleanpin.py:38` reads `/tmp/feat68-grade-assert.py` rather than the preserved third script, so the documented three-command reproduction is not self-contained and fails on a clean auditor environment. A committer can therefore leave persuasive full-SHA and “verbatim preserved” provenance that a later auditor cannot execute to distinguish the recorded experiment from a substituted one; the gain is defeating independent audit of the security-relevant fail-closed/authorization equivalence evidence, not new runtime privilege. Remedy: record repository-root-valid paths (or an explicit feature-root prefix) and make the clean-pin script consume the preserved grade assertion, then state the exact full-SHA invocation that actually produced the unchanged measurements. This is the still-unmet VF-04 reproduction binding, not a production-code vulnerability.

SC-05 source, residue, matrix record, and implementation-pin preconditions are present. The final orchestrator-owned ship-review Markdown/no-HTML-sibling observation is correctly not treated as a pre-panel defect.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The 156-path production union is security-clean, but VF-04 remains non-reproducible because its repository-root commands point to absent paths and the preserved driver depends on an unpreserved /tmp script."
  in_scope: true
  scope_reason: "The diff crosses authorization and untrusted-input boundaries in enforcement scripts, removes browser-interpreted output, and changes security-relevant audit provenance; all 156 union paths and all 16 named inputs were inspected."
  severity_max: med
  findings:
    - kind: form
      scope: task
      severity: med
      reader: security-reviewer
      summary: "SEC-C2-01: T-01/main-session-direct VF-04 reproduction commands are not executable from the claimed repository root and the preserved clean-pin driver reads an unpreserved /tmp grade script."
      why: "A committer can present full-SHA provenance that an auditor cannot independently reproduce, weakening detection of substituted authorization/fail-closed equivalence evidence; use valid feature-root paths and consume the preserved grade script. Anchors: clean-pin-byte-receipts.md:22-27; receipt-scripts/feat68-cleanpin.py:38."
  must_fix:
    - "SEC-C2-01 (T-01, owner main-session-direct): correct the exact repository-root invocations and bind feat68-cleanpin.py to the preserved feat68-grade-assert.py without changing measurements or chronology."
  threat_model:
    - boundary: "Untrusted plan/artifact/path inputs through the five refactored enforcement modules"
      stride: "T|E"
      mitigated: true
    - boundary: "Markdown-to-browser interpreted output and 102 generated HTML derivatives"
      stride: "T|I"
      mitigated: true
    - boundary: "Post-pin evidence authored by a committer and relied on by a later auditor"
      stride: "T|R"
      mitigated: false
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-security-reviewer-c2.md
```
