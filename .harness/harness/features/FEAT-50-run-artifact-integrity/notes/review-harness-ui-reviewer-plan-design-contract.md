# Design-contract review — FEAT-50-run-artifact-integrity plan (Mode A, unsigned)

BLUF: **FAIL.** One `high` gap (F2) — REQ-03 promises refusal for a write "aimed at another
checkout of this repository", SC-03 only tests {main-checkout, in-worktree, no-worktree}, and
T-03's own extraction mechanism (regex on the gate's raw `rel`, which is worktree-prefixed for
any worktree-resident target) structurally cannot reach the "another feature's worktree" case it
explicitly claims to deny. Everything else reviewed — the #1056 and #1058 refusal-text specs, and
the BRIEF document's operator-facing prose — is well specified against this repo's own bar, with
two `med`/`low` document-clarity gaps (F3, F4) and one `low` wording refinement (F1).

## #1056 — validate-digest.py (T-01/T-02/D-01/D-02)

Calibrated against the file's own conventions at `validate-digest.py:1477-1613`: every fail-open
line ends `"... — passing through."`, and the exit-2 contract-violation line reads `"Your return
does not satisfy the digest contract, so it cannot be accepted. Fix these and return again ..."`.

1. **Specified?** Yes. Exit-0 line requires literal `"not validated"` + persona name; exit-2 line
   requires persona name + "a structured return is required", "the same voice the other contract
   violations in this file use." Concrete enough for a dev to write without guessing.
2. **Names the cure?** Yes for exit-2 ("a structured return is required" — restate and return
   again, same shape as the existing contract-violation line). No per-case variance is needed here
   — one failure shape, one cure.
3. **Attributable (path)?** N/A — this defect carries no path, only a persona name. No PR#152-class
   risk.
4. **Advisory vs gate distinguishable?** Yes, cleanly: exit 0 vs exit 2, and the spec explicitly
   forbids reusing "passed through as acceptable" wording for the new exit-0 line, precisely so it
   cannot read as "accepted." Confirmed against calibration: no existing exit-0 line in the file
   is confusable with an exit-2 line.
5. **Honest about who erred?** Partial gap (**F1**, `low`, non-gating). The spec requires the
   exit-0 line say "not validated" but never requires it say **whose** gap this is, unlike sibling
   fail-open branches in the same function which self-attribute explicitly (`"this is our bug, not
   theirs"` at the internal-error branch; `"Not blocking on our own errand"` at the #551 registry
   branch — both grepped and confirmed present in the file). Scenario: an agent reads
   `"check-digest: harness-qa's return — not validated"` and cannot tell, from the line alone,
   whether it is being told "you failed" or "we could not check you," where every neighboring
   fail-open line in the same file already answers that question explicitly.
   **Proposed addition to T-01's intent**, appended to the exit-0 line's requirement: *"...and, in
   the same self-attributing form the file's other own-bug branches use, state plainly that this
   is our gap and not {agent}'s — e.g. `check-digest: {agent}'s return carries no
   last_assistant_message (absent or null) — this is our gap, not {agent}'s; the return was NOT
   VALIDATED.`"*

## #1057 — check-domain.sh feature-checkout binding (T-03/D-03/D-04)

Calibrated against the file's own documented incident at `check-domain.sh:1083-1087` (PR #152: a
worktree-**stripped** path told an agent about the wrong checkout's file) and against
`harness_boundary.classify` (`:440-482`), which returns `rel = os.path.relpath(abs_target, base)`
— the **raw, unstripped** path — as `_verdict["rel"]`, always, regardless of which of the two
DEC-143 candidates matched.

1. **Specified?** Yes for the message itself: exit 2, literal `"belongs in the worktree"`, target
   path "as the gate displays it (unstripped...)", + the worktree name.
2. **Names the cure?** Yes, and per-case: "name the worktree the write belonged in" is computed
   from `linked_worktrees(root)` matched to the extracted feature id, not a generic sentence.
3. **Attributable?** The wording requirement is correct — it explicitly requires the unstripped
   form, closing exactly the PR#152 defect class in the *text*. But (**F2**, see below) the
   *mechanism* that decides whether to fire at all cannot reach one of the three cases the intent
   itself claims to cover, so the message is never reached there — a stronger defect than
   misattribution: silence.
4. **Advisory vs gate?** Clean binary — no message on allow (T-05's own "feature-checkout-inside"
   case asserts stderr says nothing), exit-2 refusal otherwise. No confusable advisory tier.
5. **Honest about who erred?** N/A — #1057 has no "our gap vs. their gap" split; it is always the
   writer's own placement.

**F2 — `high`, must_fix.** REQ-03 states: *"the same write aimed at **another checkout** of this
repository is refused"* — generic, not "the main checkout." T-03's intent enumerates exactly that
generic case: *"the target resolves anywhere else -- the main checkout, **or another feature's
worktree**: DENY at exit 2."* But:
 - SC-03 (T-03's sole traced criterion) tests only three shapes: main-checkout write,
   in-worktree write, no-worktree-registered write. It never tests a write aimed at a **different**
   feature's registered worktree.
 - T-05 (feature-checkout-main / -inside / -absent / -red) matches SC-03 exactly — no case for a
   sibling worktree either.
 - The mechanism T-03 specifies to find the feature id — match `^\.harness/[^/]+/features/([^/]+)/`
   against "the target's repo-relative path **as the gate already computes it**" — is, in
   `domain_check()`, `_verdict["rel"]`, i.e. `os.path.relpath(abs_target, base)`. For a target
   resolving inside **any** worktree (its own, or a sibling's), that path is worktree-prefixed
   (e.g. `.claude/worktrees/harness/FEAT-51-.../.harness/harness/features/FEAT-51-.../BRIEF.md`)
   and never matches the `^\.harness/...`-anchored regex. **The check silently never fires for any
   worktree-resident target — including a sibling feature's worktree — so the "or another feature's
   worktree" denial T-03's own intent claims is unreachable by the mechanism it specifies.**

   Concrete scenario: an agent dispatched under FEAT-50, holding a domain grant that matches
   `.harness/*/features/*/BRIEF.md`-shaped globs generically (not scoped to one feature id — the
   manifest grants by persona, not by feature), issues a Write whose absolute path resolves inside
   FEAT-51's registered worktree instead of FEAT-50's. Per REQ-03 and T-03's own prose this must
   deny, naming FEAT-51's worktree. As specified, the regex never matches, the new check says
   nothing, and the write into the wrong checkout lands — the identical failure class #1057 exists
   to close, for a sibling worktree instead of the main checkout, and with no test anywhere that
   would catch the regression.

   **Recommend to pm** (one of, not both): (a) narrow REQ-03/T-03's own prose to state the denial
   is main-checkout-only (drop "or another feature's worktree" from the intent, and correct REQ-03
   to name "the main checkout" rather than "another checkout"), matching what SC-03/T-05 actually
   commit to and test — or (b) extend feature-id extraction to also try the checkout-relative form
   (`harness_boundary.checkout_relative(abs_target)`'s stripped path, which begins with
   `.harness/...` even for a worktree-resident target) and add a fourth SC-03 clause plus a T-05
   case exercising a write into a **different registered feature's** worktree. Either closes the
   REQ-03/SC-03 gap; leaving it as-is ships a requirement its own criterion never checks.

## #1058 — check-domain.sh digest-clobber guard (T-04/D-05/D-06, T-06 playbook)

Calibrated against `shape_problems()`'s established `_head()` convention (`:1083-1087`) and its
`display` parameter, which — confirmed at both call sites (`:1503-1505` sweep, and the identical
3-tuple `targets` construction feeding the single call site at `:1546-1547`) — is **always** the
unstripped `_show()` path, uniformly for the pre (single-write) and sweep routes alike. This is the
class DEC-180/PR#152 already fixed generically; T-04 plugging into it inherits the fix for free.

1. **Specified?** Yes, fully: names the fact ("already holds a recorded digest"), the consequence
   ("this write would replace rather than extend it"), and the cure ("write this run's digest into
   a run directory of its own") — plus the display-path requirement, matching house convention.
2. **Names the cure?** Yes. One failure shape (content mismatch), one cure — no per-case variance
   needed, unlike T-03's two-directional case.
3. **Attributable?** Covered by construction — T-04's branch lives inside `shape_problems()`, whose
   `display` plumbing is already uniform across both call sites (confirmed above), so the message
   gets the unstripped path automatically. No gap found on this axis.
4. **Advisory vs gate?** Clean binary — no problem appended on allow/create/prefix-match, a problem
   appended (→ exit 2 at the pre route) otherwise. No advisory tier to confuse.
5. **Honest about who erred?** N/A — squarely the writer's own reuse of a stale run dir; no
   "our gap vs. theirs" split exists for this defect.

No finding beyond the two document items below (T-06's playbook edit is adequately scoped: names
`check-domain.sh`, states the enforcement in one place, matches the actual prefix-preserving
mechanism rather than overclaiming "run dirs can never be reused").

## BRIEF.md as a document

**Does "## Open ruling required from the operator" let a no-context reader choose among (a)/(b)/(c)?**
Mostly, with two gaps:

**F3 — `med`.** The section never tells the operator *where* to record their choice. SC-12 (written
**earlier** in the same file) says grading reads `"## Approval" and any "approval.rulings" entry`
— but `approval.rulings` is named nowhere in the Open Ruling section itself, and `plan.yaml`'s
current `approval:` block carries only `status`/`approved_by`/`date`, no `rulings` key at all.
Scenario: the operator reads the (blocking) Open Ruling section, picks (c) or records a deferral in
conversation, signs by flipping `approval.status: approved` — and SC-12 fails at grading because no
`approval.rulings` entry exists anywhere in the file, at the exact point the operator believed the
blocking question was answered. **Proposed addition**, appended to the end of the Open Ruling
section: *"Record your choice by adding `approval.rulings: [{ id: INV-32, choice: a|b|c, note: <one
line> }]` to this file's `approval:` block when you sign; SC-12 is graded by reading it there.
Recording `c` here defers the remedy — `check-state.sh` will still exit 1 with these 32 rows
outstanding — and leaves (a) as its own future ticket; it is not the same as ruling (a) or (b)
closed."*

**F4 — `low`, non-gating.** The section opens "Constraint 4 of the stated intent requires
`check-state.sh` to exit 0" — but BRIEF.md's own `## Constraints` section is unnumbered and
organized by DEC-id, not by the 1–6 numbered list "constraint 4" actually names (that list lives
only in `notes/answers-2026-08-31-plan.md`). A reader working from BRIEF.md alone — meant to stand
as the plan's own record — cannot locate what "Constraint 4" says without opening a second file.
**Proposed replacement**, first sentence of the section: *"The operator's stated intent requires
the three canonical commands — including `check-state.sh` — to exit 0
(`notes/answers-2026-08-31-plan.md` constraint 4), and that cannot be reached by fixing these three
issues."*

**Does it make the recommendation and its cost explicit, or bury them?** (b)'s cost is explicit and
strong ("falsifying 32 signed records... PRINCIPLES rule 15 forbids it... NOT recommended"). (a)'s
cost is stated ("smallest change... main-session-direct") plus the closing sentence clarifies both
(a) and (b) need a **new** task if chosen. (c)'s cost — that `check-state.sh` keeps exiting 1, i.e.
constraint 4 is **not actually met** under (c) — is not restated in this section but **is** stated
earlier in the same document at SC-11's own text, which a top-to-bottom reader reaches first; I
judge that adequate rather than buried, given document order, and file it as no finding.

## Findings summary

| id | severity | element | gates? |
|---|---|---|---|
| F1 | low | T-01 | no — non-gating, wording refinement |
| F2 | **high** | REQ-03 / T-03 / SC-03 | **yes — must_fix** |
| F3 | med | BRIEF `## Open ruling required from the operator` | no (below high), but should be closed before signature |
| F4 | low | BRIEF `## Open ruling required from the operator` | no — non-gating |

```yaml
VERDICT: FAIL
DIGEST:
  headline: >-
    REQ-03 promises refusal for a write aimed at "another checkout"; SC-03/T-05 test only the
    main-checkout case, and T-03's own regex-on-raw-path mechanism cannot reach a sibling
    feature's worktree even if a test were added — a real must_fix, not a style note. Everything
    else audited (the #1056 and #1058 refusal-text specs, BRIEF's operator-facing prose) is
    solidly specified against this repo's own established bar.
  mode: A
  in_scope: true
  severity_max: high
  findings: 4
  must_fix:
    - "F2: REQ-03/T-03/SC-03 — the 'another feature's worktree' denial T-03's intent claims is
      structurally unreachable by the regex-on-raw-rel mechanism it specifies (rel is
      worktree-prefixed for any worktree-resident target, never matching the anchored
      ^\\.harness/... pattern), and SC-03/T-05 never test that shape either. Narrow REQ-03/T-03's
      claim to the main-checkout case that is actually tested, or extend feature-id extraction to
      the checkout-relative form and add the missing SC-03 clause + T-05 case."
  states_unspecified: []
  contract_violations:
    - { path: "plan.yaml T-03 intent (feature-checkout binding)", actual: "claims DENY fires for
        'the main checkout, or another feature's worktree'", specified: "REQ-03 requires refusal
        for a write aimed at 'another checkout of this repository' (generic); SC-03/T-05 test
        only main-checkout/in-worktree/no-worktree — the sibling-worktree shape is neither tested
        nor, per the regex-on-raw-rel mechanism, reachable" }
  a11y: []
  open_questions:
    - { id: Q1, question: "Should REQ-03/T-03 be narrowed to 'refused when the write lands in the
        MAIN checkout' (matching what SC-03/T-05 actually verify), or should the sibling-worktree
        case be made reachable (checkout-relative feature-id extraction) and added to SC-03/T-05?
        This is pm's call to make before signature — either resolves F2, but not doing either
        ships a promise (REQ-03) the plan's own criterion never checks.", blocking: true }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-50-run-artifact-integrity/notes/review-harness-ui-reviewer-plan-design-contract.md
```
