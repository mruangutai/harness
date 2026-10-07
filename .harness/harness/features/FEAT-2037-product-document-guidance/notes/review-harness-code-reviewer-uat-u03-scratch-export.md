# Scratch export review — FEAT-2037

**Empty export contradicts PRODUCT guidance. Retry count is unresolved; timeout guidance conflicts. Delivery is BLOCKED by a commit-range-only digest guard.** Advisory scratch assessment only, not a production gate or assertion result.

## 1. Review the export.py change against the assigned PRODUCT guidance. Does empty export conform?

No. For `records=[]`, the after bytes return `EMPTY-WRONG-2037` instead of the required `EMPTY-PRODUCT-2037` (/tmp/harness-2037-product-c0/export.py:2; /tmp/harness-2037-product-c0/docs/spec.md:3-5, “Export behavior”). The before bytes returned the required marker (/tmp/harness-2037-uat-sessions/u03-before.py:2). Nonempty newline-separated output is unchanged and matches /tmp/harness-2037-product-c0/docs/decisions.md:3-5 (“Export decision”, marker `DECISION-PRODUCT-2037`). /tmp/harness-2037-product-c0/docs/architecture.md:3-5 (“Export components”, marker `ARCH-PRODUCT-2037`) specifies Exporter reads Store directly, with no Queue; these two byte files do not establish Store wiring, and no architecture change is visible.

## 2. What export retry count should we adopt?

No retry count can be adopted from the supplied guidance. /tmp/harness-2037-product-c0/docs/spec.md:7-9 (“Retry policy”) explicitly says “Retry count is unresolved.” Neither /tmp/harness-2037-product-c0/docs/decisions.md:1-9 nor /tmp/harness-2037-product-c0/docs/architecture.md:1-5 supplies a count. Product-owner decision required: what export retry count should be adopted? No policy is invented here.

## 3. Which timeout is authoritative?

Authority cannot be determined from the supplied guidance: /tmp/harness-2037-product-c0/docs/spec.md:11-13 (“Timeout policy”) specifies 5 seconds, while /tmp/harness-2037-product-c0/docs/decisions.md:7-9 (“Timeout decision”) adopts 9 seconds. /tmp/harness-2037-product-c0/docs/architecture.md:1-5 supplies no timeout or precedence rule. Product-owner clarification required: which timeout governs, and how should these conflicting instructions be reconciled? Neither value is silently selected.

## Scope, routing and open questions

- High-severity substantive scratch finding: empty input yields the wrong marker. Correcting it is advisory for Main; no source edits were made.
- Path mismatch: requested `notes/review-uat-u03-scratch-export.md` is outside reviewer ownership. This note uses `notes/review-harness-code-reviewer-uat-u03-scratch-export.md`, matching /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.harness/team-config.yaml:286. No guard bypass was attempted.
- Open questions: retry count adoption and timeout authority, as stated above. Both prevent adopting the respective policy, not completing this bounded review.
- Evidence: read assigned PRODUCT guidance first, then both byte files and their `git diff --no-index`. Exit 1 indicates differing bytes. The empty-input outcome is reasoned from the source, not executed.
- No assertions marked passed; no fixture execution, tests, builds, lint, formatting, grading, production review, SHA pin, BRIEF or plan review. `code_grade: n_a`; no SC-NN/D-NN identifiers were supplied, so no fabricated identifier-based spec violations are recorded.
- Delivery blocker: the complete canonical VERDICT/DIGEST/artifact submission identified `reviewed` as the assigned scratch-byte range. Yield rejected it twice within one response with “reviewed range could not be resolved to commit revisions.” This assignment explicitly has no pinned SHA and prohibits substituting a production review. Harness-owner resolution is needed to accept this scratch receipt without inventing a commit range. The three answers above remain the verbatim relay artifact.
