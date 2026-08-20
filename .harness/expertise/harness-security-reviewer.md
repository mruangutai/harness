# Expertise — harness-security-reviewer

## Patterns (max 15)
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
- P-08: WHEN a diff might change data exposure — new leak, added instance, or dropped field —
  DO diff against the pre-change state, not zero: only proven-unchanged mechanism,
  reachability, and affected set earns 'pre-existing' dismissal; discarding a raw-error field
  for a fixed string is a reduction worth stating.
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
- P-14: WHEN a dispatch names specific files to check DO also grep the full diff for
  secrets/credentials, not only the named files — docs, config, and workflow changes carry
  credential-shaped strings too, and a narrowed sweep misses them.
- P-15: WHEN severity-rating an unmitigated boundary whose sole compensating control is human
  diff review DO check whether that control already produced, then caught, a real defect
  within this same review scope — a demonstrated near-miss justifies rating above a purely
  hypothetical gap.
- P-16: WHEN two reviewers' findings about the same mechanism seem contradictory DO check
  whether they answer different questions before reconciling — the defect can live in the
  union of both scopes, not in either alone.
- P-17: WHEN grading severity by reachability DO separately flag irreversibility of outcome — a
  low-severity, low-reachability finding (e.g. a possible secret write) can still warrant top
  priority if the failure can't be undone once it fires. An opt-in/time-window control and a
  containment control (permissions, gitignore) are not substitutes for each other.

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
- G-08: WHEN a diff introduces a comment asserting a safety property DO verify it now, not defer
  to 'next touch' — a pre-existing false claim can wait; one the diff itself introduces is this
  review's finding, at info severity, since a later reviewer may cite it to close a question
  unfixed.
- G-09: WHEN a migration adopts a derived or wildcard pattern across many enforcement sites but
  one site keeps a hardcoded literal DO check whether it is correct only by coincidence for
  today's single value — tests scoped to that value cannot catch the future divergence.
- G-10: WHEN proposing a remedy for an authorization or matching gap DO state it as a
  constraint — the exact derivation or invariant — not a direction like 'use a wildcard': a
  neighboring form can satisfy the direction while creating a false grant if identifiers
  aren't actually globally unique.
- G-11: WHEN a threat-model boundary is marked mitigated:false because its firing precondition
  does not exist yet (e.g. only one tenant onboarded) DO label it precondition-absent next to
  the entry — otherwise it reads identical to an active, currently-exploitable gap to a later
  reader.
- G-12: WHEN classifying a finding's remedy routing DO classify by which file or layer the
  stated remedy would change, not by where the defect was found — a data-file defect can still
  need an enforcement-layer fix under a carve-out, while a narrower same-layer remedy would not.
- G-13: WHEN a threat_model entry is unmitigated in prose (assessed-and-dismissed,
  precondition-absent, or scope-closed) DO set its structured `mitigated` field to false, not
  true — a downstream reader routes on the YAML field, never the prose; a mismatched field
  misroutes even when the prose reasoning is correct.
- G-14: WHEN a check computes a result but appends it to a list the exit code never reads DO
  flag it as non-gating regardless of what it prints — a check that prints OK while silently
  unenforced is worse than no check, since it reads as validated.
- G-15: WHEN listing remediation recommendations DO check each against your own findings
  section first — an alternative phrased as 'or the broader form' (e.g. gitignore a whole log
  directory) can silently contradict evidence you already gathered (e.g. sibling files in that
  directory already tracked).

## Outcomes (max 10)
- O-01: WHEN a review closes clean DO require identity-level evidence — assertions proving
  equality, consumers traced to their actual write, or an applied-and-killed mutant — not a
  read-and-conclude. Re-executing an already-green suite is confirmatory, not identity-level: it
  re-confirms what was never in doubt and discriminates nothing.
- O-02: WHEN closing a theoretical vulnerability class (ReDoS backtracking, path-precedence,
  race ordering) DO produce a runnable measurement — timed adversarial input, printed resolved
  value — rather than a structural argument alone; complexity-class and language-semantics
  arguments are cheap to get wrong and expensive to trust.
- O-03: WHEN a diff bulk-touches injected or preloaded instruction content for one intended
  edit-class (e.g. a path rename) DO diff-filter every touched file for the known substitution
  and inspect the residual — an empty residual across the full set bounds a suspicion into a
  dated finding.
- O-04: WHEN a guard denies a probe, or an anomaly can't be reproduced, DO record it rather
  than smoothing it over — an unreproducible symptom one agent records can match an independent
  one another records, revealing a shared infrastructure defect neither could see alone.
- O-05: WHEN a diff's risk was already assessed and accepted in a signed plan or decision DO
  cite that signature and its revisit trigger, and never add the risk to must_fix — gating a
  ship on a cost the operator already signed is not this role's call.
- O-06: WHEN self-scoping a diff that reads as security-irrelevant DO also ask whether its
  surface has ever had a security review, and say so in scope_reason — 'this delta needs none'
  and 'this surface has never been reviewed' are different questions; only the first licenses a
  decline.

## Open (max 5)
