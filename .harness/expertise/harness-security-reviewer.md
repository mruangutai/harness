# Expertise — harness-security-reviewer

## Patterns (max 15)
- P-01: This codebase's untrusted-input boundary is the hook payload (JSON on
  stdin, `.claude/skills/harness/bin/*.{py,sh}`) — but `bin/factory_*.py` is a
  second surface: it builds subprocess argv and GraphQL query documents from
  operator-config values (`fleet.yaml`) and shells to `gh`. Audit both.
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
- P-07: WHEN a CLI's own value-parsing (e.g. magic-value flags) can't be verified
  under review constraints DO close on provenance instead — but label the closure
  reachability-closed and name the exact provenance assumption (e.g. "value is
  always operator-authored") that would reopen it if violated.
- P-08: WHEN auditing whether a modified code path changed data exposure DO
  compare against the pre-change path's behavior, not against zero — a rewrap
  that discards a raw-error field and substitutes a fixed string is a reduction
  worth stating, distinct from "no new leak found".
- P-09: WHEN a review closes a construction-injection question by citing an
  assertion on the emitted value DO check whether it proves equality to the
  reviewed constant, not merely shape or pattern — a regex a second,
  differently-worded string also satisfies establishes nothing about identity.
- P-10: WHEN a feature removes a guard in one task and grants new
  reachability in another DO check the combination, not each task alone —
  neither task's scope may cover it, so no SC or gate records the ordering
  precondition, and the combined posture goes unaudited.
- P-11: WHEN a diff synthesizes a sparse object standing in for a fuller one DO
  trace every consumer field-by-field to its write or auth check — a permissive
  `.get()` reading an omitted key as absence-equals-permission is the fail-open
  shape to rule out.
- P-12: WHEN a security-relevant detail is observed but pre-existing/unchanged
  by the diff DO record it in the review as assessed-and-dismissed rather than
  omitting it — a recorded non-finding stops a later reviewer re-raising it; a
  silent drop does not.

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
- G-06: WHEN a diff's effect lands on a different repository than the one
  under review (e.g. a guard config pushed elsewhere) DO verify against
  that repo's live state — clone, diff, or fetch it — rather than resting
  on the local diff; this turns argued claims into measured ones.
- G-07: WHEN a diff is scoped IN and returns zero findings DO set severity_max
  to info, not n/a — n/a is reserved for scoped-out diffs; conflating them
  misreports whether the surface was actually assessed.

## Outcomes (max 10)
- O-01: WHEN a surface looks clean on first read DO close with identity-level
  evidence (assertions proving equality, consumers traced to their actual write)
  not a read-and-conclude — a zero-finding review is otherwise indistinguishable
  from a shallow pass to anyone downstream.

## Open (max 5)
