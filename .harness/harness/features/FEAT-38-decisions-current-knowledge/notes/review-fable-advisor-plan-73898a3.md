# Advisor review — FEAT-38 plan at 73898a3 — should this be built at all?

Reviewer: second-opinion advisor (read-only), 2026-08-29. Angle: work that should not be done,
build-then-delete honesty, unstated assumptions, sequencing against the measured fail-open
approval guard. Conformance to the brief was NOT re-graded; two prior runs own that.

## BLUF — TRIM: one clause in T-24's verify, then build. Nothing else warrants reopening.

The five removal tasks are the right work and the plan is unusually honest about the
build-then-delete arc. But T-24's verify is unsatisfiable at its own completion by the plan's
own evaluation model — the exact defect class the plan already fixed once with the T-27 edge,
missed for the fifth reference site. Measured, not inferred (finding 1). Left as signed, it
burns a build cycle on a mandatory upward escalation the plan itself authored. The fix is one
pathspec exclusion; everything else below is med/low and none of it justifies a resequence.

---

## Finding 1 — HIGH — T-24's blast-radius sweep fails by construction at T-24's completion

Lands on: T-24 (plan.yaml:1798, verify sweep clause at plan.yaml:1820-1821) and its intent's
claim that the unscoped sweep is "the only thing in the plan that proves no sixth reference
site exists".

Measured in this worktree: running T-24's sweep clause verbatim —
`git grep -l check-decision-claims -- . ':!.harness/harness/features' ':!.harness/notes'
':!.harness/logs'` — returns five files, including `.harness/harness.json`, which matches via
the substring inside `test-check-decision-claims.py` at integration-detect entry 30
(.harness/harness.json:119). That entry is T-25's work, and T-25 `depends_on: [T-24]`
(plan.yaml:1907) — it CANNOT have run when T-24's verify runs.

The plan's own evaluation model is completion-time: T-24's intent justifies the T-27 edge with
"with T-27 unrun that clause exits 1 naming a file this task must not touch" (plan.yaml, T-24
intent), and the approval note signs "T-24 waiting on T-27 so the code lane trails the
documentor lane". By that same model, after T-27 + T-24's three edits land, the sweep still
matches `.harness/harness.json` → prints 'references survive' → exit 1. The dependency cannot
be reversed (T-25 needs T-24 first for the runner-order argument, correctly). Concrete failure
scenario: harness-backend-dev lands exactly what the intent instructs, its gate goes red naming
a file it is forbidden to touch, and the intent's own instruction — "report it upward, do not
patch it quietly" — forces an escalation. One wasted cycle, minimum, on a defect the plan wrote.

The intent's rationale for keeping the sweep unscoped is also false: SC-14's third assertion
(BRIEF.md, SC-14) is the identical sweep with the identical three exclusions, graded at
review_sha where T-25 has landed. The tree-wide proof is owned — by SC-14, not by nobody.

Fix (one clause, needs the operator since the plan is signed): add `':!.harness/harness.json'`
to T-24's sweep. That file's cleanliness is asserted twice already — T-25's verify (both
halves, positively) and SC-14 at review_sha. Alternatively move the unscoped sweep into T-25's
verify, the true last link of the removal chain.

## Finding 2 — MED — the grilling Destination promises more than the signed brief delivers

Lands on: REQ-10's conditioning (BRIEF.md, REQ-10) vs the Destination of
`.harness/notes/grilling-remove-executable-claims-2026-08-29.md`, which reads "no remaining
script that builds a command line from document or config text" and "no document-driven command
execution anywhere in the harness".

REQ-10 as signed is met by the class being "swept and its members named with a recommendation"
— remediation beyond check-decision-claims.py is explicitly OUT of scope, and the brief names
`test_kinds.<kind>.cmd` as a live candidate. So if T-29's TEXT-DERIVED-ARGV set comes back
non-empty (plausible: something executes that cmd string; under bin/ I found only readers —
check-state.sh validates it, upgrade-config.py preserves it — but the executor may sit outside
bin/, which T-29's enumeration never reaches), the feature meets the signed brief while missing
the operator's recorded destination sentence. Concrete failure scenario: ship review quotes the
grilling Destination against a non-empty audit finding and bounces a feature that did exactly
what was signed. Nobody reconciled the grilling note after the conditioning was drafted. Fix is
zero-code: one reconciling sentence at ship ("destination narrowed to sweep-and-name by REQ-10's
signed conditioning"), or pre-agree that the brief governs. The signature already endorses the
conditioning explicitly, so this is a record gap, not a scope defect.

Scope adequacy checked rather than assumed: outside bin/, the only tracked executing script is
`.harness/notes/audit-digest-schema.py`, a one-off in a frozen notes dir. The bin/ scoping of
T-29 is essentially adequate for scripts; the residual class member is whatever agent or
workflow executes `test_kinds.cmd`, which is config-by-design, not document-driven drift.

## Finding 3 — MED — T-29's verdicts are graded for format, never for truth

Lands on: T-29 (execution_agent: harness-pm, plan.yaml:2119-2126) and SC-17 (verify: inspection).

T-29 is a provenance judgement over Python subprocess call chains, routed to the product
manager because the notes/ path is pm's lane (plan.yaml lanes block) — lane-driven, not
competence-driven. The mechanical verify checks that every candidate has a row with a non-empty
rationale; it cannot check that a verdict is right. Concrete failure scenario: a genuinely
text-derived site is labelled FIXED-LITERAL-ARGV with a plausible-sounding rationale, every gate
passes, and REQ-10 records a false clean bill — the exact "asserted and unproven absence" this
requirement exists to end, now with a signature over it. No plan change needed: SC-17 names no
inspector, so route the inspection to harness-code-reviewer or harness-backend-dev rather than
letting the note's author's lead self-certify it.

## Finding 4 — answer to "was T-29 a decision or a reflex": a decision, and it earns its cost

T-29 did not arrive from a grilling reflex. It is former backlog row B-9, filed in
`notes/ship-review-2026-08-29-18.md` BEFORE the grilling, and the grilling records the ruling
with its rationale ("the ruling is about a class of risk") — grilling note, Settled, item 3.
Cost check: the enumeration returns 72 files today, 48 of them test-*.py (measured in this
worktree). Per-file cited-call-site rows for 48 test files is the bulk of the cost and most
will read FIXED-LITERAL-ARGV; a two-tier note would be cheaper. But the mechanical per-row
verify is precisely what makes the absence claim falsifiable, the whole thing is one task and
one note, and trimming it now costs an operator decision worth more than the savings. Keep it
as signed.

## Finding 5 — build-then-delete: the plan is honest, and deletion beats both alternatives

The reversal is carried in D-10, D-14, D-15, the two-sided reversal verifies on T-20/T-21
(existed at 48bbe7e AND absent at final state), preserved original intents, empty traces with
stated reasons, and a brief section a signer cannot miss. That is the honest-record discipline
working as designed; I found no place where the plan launders the reversal.

Arguing the rejected side once, as asked: all 11 markers were measured read-only greps
(replan-remove-command-execution.md, BLUF), the RCE was closed and confirmed, and the
declarative redesign had zero execution surface — so "keep something" was cheap and defensible.
I still side with the operator, on their own stated goal: the claims mechanism was invented
mid-feature, layered above the fold, and reversed within days — it is itself an instance of the
disease this feature exists to cure (decisions that go back and forth). Deleting it, with the
reversal on the record, serves "fewer self-reversing decisions" better than preserving it in
any form would. Doing nothing (keeping the hardened checker) is worse than both: it leaves
DEC-205 counting two checks and an allowlist to maintain forever.

One consequence nobody costed, for the record rather than as a re-proposal: DEC-181's three
markers guarded exactly the facts with a DEMONSTRATED rot rate — the brief's own Problem
section records that DEC-181 had already rotted once (a code location that at 7ebfc9e was an
unrelated comment, a budget the code did not have). D-14's cost is not hypothetical for that
entry; expect its budget claims to drift again with nothing reddening. The brief leaves
"whether anything should replace it later" unsharp — when that question sharpens, DEC-181 is
the test case to price it against.

## Finding 6 — sequencing vs the fail-open approval guard: finish FEAT-38 first, guard next

The measured defect is real and given: check-domain.sh's approval guard is fail-open inside
every worktree, so "an agent may not write the approval signature" has been convention, not
enforcement [given by the review contract; not independently re-derived here]. Two reasons
finishing FEAT-38 first is still right:

1. The remaining work is 5 tasks, mostly deletions, across 3 agents — plausibly 3-5 of the 16
   remaining cycles, not 16. Abandoning now strands a half-transformed DECISIONS.md on a branch
   against the single highest-churn document in the repo; every week of delay compounds merge
   decay on a 15-entry rewrite that took 14 cycles to land. The waste of stopping is near-total;
   the cost of finishing is small.
2. The two are orthogonal: none of T-24/25/27/28/29 touches approval machinery, so finishing
   does not deepen the exposure, and fixing the guard does not change one line of this plan.

But the guard deserves the NEXT slot, and by the operator's own revealed posture: this very
feature deletes a working, hardened mechanism because convention-plus-allowlist was deemed an
unacceptable substitute for structural safety. A fail-open approval gate is the same shape —
convention where enforcement was assumed — and it sits under every signature in the org,
including the two on this plan, whose provenance is mechanically unverifiable inside a worktree
for exactly that reason. File it as a feature the day FEAT-38 ships.

## Low / notes

- LOW: T-27 and T-28 are one agent (harness-documentor), one surface, strict sequence; the
  split buys parallelism only if T-24 genuinely runs concurrently with T-28. Two dispatches
  where one would do — not worth reopening a signed plan.
- LOW: T-29's verify interpolates the unescaped basename into an ERE (`grep -qE "^\| $B \|`),
  so `.` wildcards; a false row-match is theoretically possible, practically negligible.
- LOW [unverified]: T-20/T-21/T-27 reversal verifies and SC-14 pin positive controls to
  `48bbe7e`. Fine at validate on this branch; if ship squash-merges and deletes the branch,
  those `git show 48bbe7e:` clauses die in the main checkout and the archived plan's verifies
  become unrunnable archaeology. Grading happens before that, so no action — noted only so
  nobody re-runs them post-merge and misreads the failure.
- Verified sound, stated plainly: the retained anchor checker is genuinely outside the risk
  class — fixed literal `["git", "ls-files"]` argv at check-decision-anchors.py:111-112, no
  document text near a subprocess (confirmed by reading the file, not the brief). T-24's
  MISCONFIGURED-detector measurement and the resulting T-24/T-26 merge fix a real ordering
  defect correctly. SC-16's positive count assertions and SC-18's byte-identity guard against
  exactly the two likeliest silent failures (deleting count sentences; over-deleting the
  neighbour checker). 11 live markers confirmed in the worktree DECISIONS.md, matching the
  plan's count. The removal task set is the minimal one that leaves no lying surface behind.

