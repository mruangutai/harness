# Security c5 — FEAT-2229

**BLOCKED: SEC-C4-01 / T-01 / SC-02 is statically addressed, but execution closure is not established.** The assigned actual-CLI probe was refused before execution by the host's read-only guard. This is an execution-permission blocker, not an observed product failure or a new must-fix.

Reviewed immutable `c163d5ea0fb17da27b3455559f317d67852981c7`, base `dfa52536`; inspected c163d5ea's matcher/test delta, without opening prior pins. Read BRIEF, T-01/decisions, operator c4 ruling, AGENTS, relevant SPEC/DEC-188/DEC-254/index, c4 security note and consolidated assessment. Other SCs and DEC-188 retain c4 assessments.

## SC-02 identifier closure

`check.py:209-212,281-287` replaces the digit-only rejection with an explicit delimiter lookahead: line end, whitespace, colon, opening parenthesis, em/en dash, or hyphen followed by whitespace. By inspection this excludes `DEC-10x`, `DEC-10_a`, `DEC-10-1`, `DEC-10.5` and preserves the requested colon/parenthesis/bare/space/tab controls. The scanner reads text with universal newline conversion, then retains line endings while scanning. These are source observations, **not executed CRLF or CLI results**. Existing section extraction still ends at the next real heading of equal or shallower level; the delimiter does not consume neighboring content. No additional matcher bypass was demonstrated.

Prepared one execution command using the pinned integration module's fixture builders and `run_check`, which invokes actual `plan-merge.py check`. It covered 107 planned negative/positive CLI observations: identifier continuations (including digit, uppercase, Unicode letter, underscore, joined hyphen, dot, slash), missing genuine heading, malformed heading formats, title-content delimiters, bounded neighboring clauses, LF/CRLF, spaces/tabs, and three fence controls. **Zero observations executed.** Host response: `bash-write-guard: BLOCKED — harness-security-reviewer is READ-ONLY and this command writes files (python open).` No alternate write route or guard evasion attempted. An authorized executor must run these discriminating CLI controls before claiming security execution closure. No builds, suites, graders, formatters or mutants executed.

## Security scope and retained record

Measured all 57 paths in `dfa52536..c163d5ea`: 4 production gate paths, 7 governance/template paths (including template configuration), 1 live configuration, 3 authority documents, 4 regression/classification paths, 38 feature records. Gate/authority interpretation is in scope for tampering; records are in scope for secrets/authority claims. Prior reviewed mechanisms retain c4 conclusions; this short review reopens only the changed identifier matcher and its fence-test context. Full-range added-line credential-pattern sweep found zero matches. No new dependency, network, shell, export or cross-user-data surface in this delta.

The operator-backlogged low Unicode whitespace/line-break and list-container advisories remain unchanged, not new must-fix items. C4-QA-CONTRACT, SIMPLIFY B-1/B-2 and create:true remain expressly backlog; none was re-audited.

Threat boundary: decision-document author plus draft submitter → clause-integrity gate (Tampering). The actor already controls document contents; the relevant gain is bypassing clause attribution, not a new document-write privilege. Mitigation remains execution-unconfirmed.

Managed persona pin was created successfully and removed successfully (helper exit 0); temporary probe fixture command never ran. No product edits or run-directory writes.

**Open question SEC-C5-EXEC (blocking):** permit the assigned temporary-fixture CLI execution for this read-only reviewer, or route the exact requested controls to an authorized executor. No product-code must-fix is established by this review.
