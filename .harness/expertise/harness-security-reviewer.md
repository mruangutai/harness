# Expertise — harness-security-reviewer

## Patterns (max 15)
- P-01: This codebase has no network, database, or browser surface — the only
  untrusted-input boundary is the hook payload. `.claude/skills/harness/bin/*.{py,sh}`
  read JSON on stdin and parse agent-authored text or tool params. Start every
  audit there; the rest of the repo is Markdown.
- P-02: WHEN grading a possible finding DO name the threat model before severity:
  an actor who already controls a value already holds the privilege it grants (no
  escalation, not a finding); a control reachable only from a higher-trust step
  than the threat actor is defense-in-depth, not a gap.
- P-03: WHEN a diff removes or loosens a validation invariant or a required schema
  field DO scope the review IN as Tampering, even absent new input, auth, or
  network surface — the loosened guard is itself the trust boundary that other
  agents' returns route on.
- P-04: WHEN checking whether a code deletion left a fail-open regression (e.g. a
  now-dead import or removed branch) DO run the relevant fixture test suite rather
  than trusting a static grep or read alone — execution catches a NameError or
  non-2 exit reading cannot.
- P-05: WHEN grading severity by reachability DO also check the mechanism against
  any approved success criterion's literal wording it touches — an SC stated in
  one frame (e.g. argv) but violated via another (e.g. an inherited env var) is
  FALSE as written, which reclassifies the defect to must-fix regardless of
  exploitability.
- P-06: WHEN auditing a PreToolUse/PostToolUse guard DO check which tool_name
  values its dispatch actually covers, not only the logic once triggered — a
  locally-correct early-exit for one tool (e.g. Write) can leave other routes
  (Edit, Bash) silently unchecked, invisible from reading the triggered logic
  alone.

## Gotchas (max 15)
- G-01: Only `exit 2` blocks a hook (DEC-100); any other exit — including an
  uncaught exception — is non-blocking and silently disables the gate for that
  invocation. Rate hook crashes as fail-open (control bypass), not DoS. Check
  whether the script wraps its own logic in try/except, not just the payload parse.
- G-02: WHEN auditing a shelled CLI call DO check for flag re-parsing, not only
  shell injection: list-form argv with no shell stops injection, but a positional
  argument before any flag can still be read as a flag if it starts with '-'; a
  `--` boundary or digit check fixes it.
- G-03: WHEN a diff widens an accepted-value set to keep an old field or key for
  backward-compat DO check whether it only re-admits a spelling already legal
  pre-change — if so, grade not-a-finding; only a genuinely new accepted shape is
  a gap.
- G-04: WHEN a guard bypass fails open silently (exit 0, no stderr, no log line)
  DO treat the unauditability itself as an aggravating severity factor,
  independent of blast radius — an audit afterward cannot distinguish "the guard
  allowed this" from "the guard was off".
- G-05: WHEN a reachability argument requires proving no trigger exists (e.g.
  across arbitrary shell) DO weigh it against fix cost — an unprovable negative
  paired with a one-line fix means the reachability investigation is the wrong
  expenditure; grade on blast radius and auditability instead.

## Outcomes (max 10)

## Open (max 5)
