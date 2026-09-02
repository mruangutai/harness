```yaml
VERDICT: PASS
DIGEST:
  headline: "G-10 displacement landed — targeted single-line rewrite verified byte-for-byte; 40 ids intact; checker exit 0."
  applied_op:
    op: replace
    target: "G-10 (craft)"
    section: Gotchas
    entry: "WHEN charging a documentation or comment claim as an overclaim DO parse its literal logical form first — a 'caught only when X' sentence is a necessary condition, not falsified by an uncaught case outside X; check every affirmative claim (e.g. 'vector-agnostic') separately before charging."
    word_count: 45
    method: "targeted single-line in-place rewrite via bash/python line-index replace (no Edit tool exposed in this runtime; the file's own _write tool — a whole-file overwrite — was explicitly avoided per constraint); no hook/guard refusal encountered"
  quoted_line_28_after_write: "- G-10: WHEN charging a documentation or comment claim as an overclaim DO parse its literal logical form first — a 'caught only when X' sentence is a necessary condition, not falsified by an uncaught case outside X; check every affirmative claim (e.g. 'vector-agnostic') separately before charging."
  id_counts:
    total: 40
    patterns: 15
    gotchas: 15
    outcomes: 10
  intact_ops_first_ten_words:
    P-09: "WHEN a finding could be either introduced by this diff"
    G-03: "WHEN auditing an except-OSError swallow inside a before/after"
    G-06: "WHEN a git diff shows 0 insertions/0 deletions for"
    O-03: "WHEN a high-severity finding has no failing approved success"
  checker_output_verbatim: |
    OK   .harness/expertise/harness-security-reviewer.md
    ADVISORY .harness/expertise/harness-security-reviewer.md:19: G-01 names 'DEC-100' — repository-layer candidate; rule on it (issue 340)
  checker_exit_code: 0
  checker_advisory_note: "pre-existing, named non-violation per dispatch — not touched"
  in_scope: true
  scope_reason: "Direct assignment: land the one missed operator-ruled displacement (G-10) in this agent's own craft Expertise file."
  severity_max: n/a
  findings: 0
  must_fix: []
  threat_model: []
  open_questions: []
  files_touched:
    - .harness/expertise/harness-security-reviewer.md
  expertise_update:
    - op: replace
      target: G-10
      section: Gotchas
      entry: "WHEN charging a documentation or comment claim as an overclaim DO parse its literal logical form first — a 'caught only when X' sentence is a necessary condition, not falsified by an uncaught case outside X; check every affirmative claim (e.g. 'vector-agnostic') separately before charging."
      why: "Applied by hand (targeted single-line rewrite) per this dispatch, completing the seventeenth of seventeen operator-ruled displacements from the FEAT-48 distillation pass; expertise-merge.py was not used because it exits 7 on a same-id rewrite."
      applied: true
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-security-reviewer-g10land.md
```

## Notes

- Pre-edit read confirmed line 28 (`grep -n '^- G-10:'`) carried the exact pre-displacement text
  named in the dispatch, character for character.
- The replacement `entry:` string was read directly from the committed receipt at
  `.harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-security-reviewer-distill.md:149-155`
  (the `G-10 (craft)` replace op) and cross-checked against the dispatch prompt's quoted text —
  identical.
- Edit method: no `Edit` tool is exposed in this runtime's toolset (only `read`/`glob`/`grep`/`bash`/`write`/`yield`/`hub`).
  The file's `write` device performs a whole-file overwrite and was explicitly excluded by the
  dispatch's constraints. A `bash`-driven Python script performed the equivalent of a targeted
  line-index replace: read the file, assert the exact pre-image of line 28, replace only that
  line, write the file back unchanged elsewhere. No hook or guard refusal was encountered; nothing
  was worked around.
- `expertise-merge.py` was correctly NOT invoked (per dispatch: it exits 7 on a same-id rewrite).
- Post-edit verification was content-based throughout: quoted line 28 in full, quoted the
  first ten words of each of the four previously-landed ops (`P-09`, `G-03`, `G-06`, `O-03`) as
  they now stand, and ran the id census by section rather than relying on any excluding hash.
- `check-expertise.sh` returned `OK` with exit 0; the sole `ADVISORY` line is the pre-existing
  `G-01`/`DEC-100` note named as a non-violation in the dispatch — untouched, as instructed.
- No other entry, section, or file was modified. `P-09`, `G-03`, `G-06`, `O-03`, and all other
  ids/lines in this file are byte-for-byte as they stood before this change.
