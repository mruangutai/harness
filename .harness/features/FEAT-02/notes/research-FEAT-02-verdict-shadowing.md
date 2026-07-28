# Research — FEAT-02 VERDICT shadowing in validate-digest.py

## The defect, precisely

`validate()` finds the verdict with `re.search(r"^\s*VERDICT:\s*(\S+)", text, re.M)`
(`validate-digest.py:380`) — first match wins. The handoff rule's own template contains the line
`VERDICT: PASS | FAIL | BLOCKED | ESCALATE`; an agent that echoes the template before its real
return has `PASS` captured from the echo (`(\S+)` stops at the space before `|`), and the real
verdict below is never read. Recorded, not fixed, at BUILD task 22 (`docs/harness/BUILD.md:207`).

## Same-class exposure found during research

`parse_digest()` (`validate-digest.py:283-284`) anchors on the FIRST `DIGEST:` line the same way.
An echoed template therefore shadows the digest block too, not just the verdict. Template
placeholders mostly fail enum checks (fail-closed), but `headline: <one line...>` is a non-empty
string and passes — so the shadow is not reliably self-defeating. The fix should anchor digest
parsing to the accepted verdict line, with fallback to current behaviour when no verdict is found.

## Fix shape chosen (see PLAN.md D-01..D-03)

1. A `VERDICT:` line whose remainder is a `|`-separated enum is a template echo, not a verdict —
   exclude it from matching.
2. Among remaining `VERDICT:` lines: one (or several agreeing) → that token; several *differing* →
   a new contract violation ("ambiguous verdict"), never a guess. This honours the file's own rule
   at line 23: "Never guess a verdict."
3. `DIGEST:` is searched from the accepted verdict line forward; fall back to whole-text search if
   none follows (keeps all 36 existing cases green).

## Constraints verified

- Suite: `test-validate-digest.py`, 36 cases green today; CLI cases + hook cases (exact exit codes
  and stderr) + template-extraction cases. Repro cases must be proven red pre-fix (task-22 norm).
- Hook semantics (DEC-122/DEC-124): three pass-throughs and fail-open-on-our-own-bug are load-
  bearing. The new rejection is *their* violation → normal exit-2 path; pass-throughs untouched.
- stdlib-only Python; PyYAML not installed. The fix is line-scanning, no new deps.

## Open

- Whether same-treatment is wanted for an echoed `artifact:` line (low stakes — regex requires
  `\S+`, and the template's `<path ...>` still matches; but routing barely uses it). Left out.
