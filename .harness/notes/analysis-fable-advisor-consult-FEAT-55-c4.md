# Advisor consult — FEAT-55 — cycle-4, five questions before signature

**Path note.** The dispatch named `/Users/molchairuangutai/GitHub/harness/.harness/notes/…`. That is
the MAIN checkout; this feature lives in a worktree and both c3 consult notes are in the worktree's
`.harness/notes/`. Written here for that reason — same durable lead-owned path shape
(`.harness/notes/analysis-*.md`), worktree prefix.

**Persona: `fable-advisor` — the same external reader that served as the c3 and c4 plan panels'
`should-not-exist` step and answered both c3 consults. It RESOLVED; it was not skipped, preflight
did not refuse it, no substitute answered.** Read-only, no write grant; this note is the validator
lead's transcription of its return (`agent://ApplyThirdIssueTypesRulings.SaltyVulture.AdvisorC4`,
transcript `history://ApplyThirdIssueTypesRulings.SaltyVulture.AdvisorC4`).

**Nothing here resolves, accepts or waives anything, and no severity is reassigned.** Every item is a
recommendation to the operator, who alone rules; accepting a finding's risk is recorded only by
`sign-approval --overrule` (DEC-176). No plan edit was made by this consult. `plan.yaml`'s `panel:`
key was excluded from the advisor's reads per the concurrency partition.

**Advisor headline.** *Q1: fix before signature, on all three routes — the remedy is provably red,
and the reddening power must live in the exit-status and `github.issue_types` assertions, not in
CASE markers or required-string literals. Q2: two findings, one operator question — defer jointly.
Q4: batch-contingent phrasing is why `PF-45294813` fell through two executed batches; it reads FIX,
and the advisor retires that phrasing.*

**Anchor policy.** pm is rewriting `panel:` concurrently, so absolute line numbers past `plan.yaml:146`
are unstable (the advisor measured the file at 1532 then 1513 lines). Anchors are task-id + section
or case. `decisions:` anchors precede the insertion point and are stable.

---

## Q1 — the backfill contribution is never the sole refusal trigger (`scope`, med)

**Recommendation: FIX before signature — one case per route (T-03, T-05, T-07).** Premise re-derived
at source and HOLDS: T-04 §4, T-06 §3 and T-08 §6 each state the required-set-covers-backfill rule
separately, and no case isolates it — in T-03 F / T-05 G / T-07 I the *to-be-created* work already
needs undeclared `Task`, so refusal fires whether or not the backfill contributes.

**The weighing the dispatch demanded.** The advisor first corrects the framing: the c6 fix was **not**
found inert — R1 HOLDS on both legs across all three routes, and the advisor confirms the scope
reader's reading. What is true is that this is the second consecutive cycle in which, after operator
attention on REQ-07's refusal machinery, the panel produced a *new* wrong implementation passing
every planned case. That argues for fixing: an accept here is not "risk not yet examined" but "risk
examined twice and knowingly left open", which a later panel or goal-check will likely bounce anyway.

**Testable-to-red — named, not asserted.**
- *Wrong implementation:* builds `required` from `type_for_parent` + `type_for_change_type` /
  `type_for_nature` over **unrecorded items only**, omitting the §4/§3/§6 backfill clause, while
  still ordering backfill after the (now vacuously green) refusal check.
- *Case (T-03 shape; T-05/T-07 analogues in their own vocabulary):* `FAKE_TYPES=partial`;
  feature.json pre-records the parent and ALL four tasks — three `typed: True`, exactly ONE remnant
  whose type resolves to **Task** (e.g. the config task, 502) at `typed: "created"`. Zero creates
  needed; the sole source of a missing type is the backfill remnant.
- *Correct:* `required = {"Task"}`, refusal to stderr naming `Task` and `github.issue_types.Task`,
  **exit 2**, zero `updateIssue`, remnant unchanged. *Wrong:* `required = {}`, vacuous pass, backfill
  hits `declared["Task"]` → uncaught `KeyError`, **exit 1**, traceback.
- *Assertions that redden:* (i) exit status **exactly 2** — the traceback exits 1; (ii) combined
  stdout+stderr contains **`github.issue_types`** — a `KeyError: 'Task'` traceback does not.
- *The trap the advisor names:* "a non-zero process exit status" is satisfied by the crash too, and
  "names Task" is satisfied by `KeyError: 'Task'`.
- *Why not the same shape a third time:* c5 added zero-`updateIssue` clauses over an **empty**
  backfill set (nothing to catch); c6 seeded a **declared**-type remnant beside undeclared
  to-be-created work (catches **ordering**); this seeds an **undeclared**-type remnant with nothing
  left to create (catches **set membership**). Three wrong implementations, three discriminators;
  neither earlier case subsumes this one.

**Three routes, not one:** required-set construction is per-caller glue stated separately in T-04 §4,
T-06 §3, T-08 §6 (D-11 shares only `missing_types`), and the operator's own 2026-09-04 ruling —
quoted verbatim inside T-05 G and T-07 I — already rejects open-route-only red-green for REQ-07. A
T-03-only case would need the operator to narrow their own ruling. Cost: one case and one CASE letter
per file; **no new required-string literals** (`partial` and `github.issue_types` are already pinned
in all three loops).

**Consequence of accepting instead:** the omission bug ships and, on an all-recorded rerun against a
partially-declared repository, crashes with a traceback instead of REQ-07's actionable refusal — and
on the open route may first type other declared-type remnants, i.e. typing side effects from a run
that should have refused cleanly. Bounded to Harness-created issues, no data loss. If the operator
rules accept, the ruling should say in as many words that REQ-07's backfill leg is knowingly untested.

> **Lead correction to the advisor, verified at source.** The existing refusal cases already assert
> *"a non-zero process exit status, and that the combined stdout+stderr names both `Task` and
> `github.issue_types`"* (T-03 F, T-05 G, T-07 I). Clause (ii) is therefore **already in the wording
> a new case would copy**, and it reddens against the `KeyError` implementation on its own. The
> advisor's sentence that a case built from the existing clauses "alone would be inert" overstates
> its own point (ii). Effect on the recommendation: none — but the remedy is **cheaper and safer**
> than stated. Copying the existing assertion block is sufficient for the discriminating leg;
> tightening "non-zero" → "exactly 2" is worthwhile hardening (both implementation tasks pin
> `exit 2`), not the prerequisite the advisor's trap paragraph implies.

## Q2 — D-08's eighth-purpose row (low, advisor's own) vs carried `PF-9a71cb9a0c590b06b890ff1517b80385`

**Recommendation: TWO findings, ONE operator question — defer both jointly to backlog as a single
item; do NOT fold either into the batch Q1 would order.** They are distinct (`PF-9a71cb9a`: the
byte-identity drift guard stops guarding after the gate; c4 finding: the row exceeds what REQ-09
authorises) but share one decision variable — the size and duplication policy of one **511-character**
row (length re-measured this consult; the c3 `[unverified]` on the count is discharged). Any remedy
reopens the same four coupled sites: D-08 (`plan.yaml:75-77`, stable), T-11 §3's character-for-character
mandate, T-12 §1's identical row, and T-12's byte-identity verify regex. Ruling them separately risks
an inconsistent pair.

Premise re-verified: BRIEF REQ-09 (`BRIEF.md:55-57`) asks that DEC-203's purposes admit *that read* —
the capability read, singular. The probe read-back clause is load-bearing (T-10 §6 cites the eighth
purpose as its authorisation; SC-10's live pass needs it); the retro-enumeration of
`gh_issues.internal_id_args` practice is record hygiene REQ-09 does not ask for, and it is what
inflates the row.

Backlog item, one line: *"revisit the eighth-purpose row — split or shrink the identifier clause out
of the pinned wording, and decide whether T-12's byte-identity guard should outlive the gate."*
Rationale for not riding the batch: highest-collateral edit on the table (a pinned 511-char string
across two docs tasks plus a verify regex, where one typo re-reds T-11/T-12) attached to the lowest
severities, and fully reversible post-ship by a docs-only change under DEC-205. **Consequence of
deferring:** every reword is a two-file lockstep edit until the backlog item lands, and SC-11's
reviewer grades sub-issue identifier-read claims inside an issue-types feature — friction, not defect.
**Consequence of fixing now:** reopening settled docs tasks mid-signature for prose, with a real
chance of a c9 spent on wording.

## Q3 — D-14's `because` contradicted by T-02 (info, advisor's own)

**Recommendation: FIX, in whatever batch Q1 orders — one amend to D-14's `because`. Stated
unconditionally, and it stands on its own merits even if Q1 is refused** (the advisor explicitly
declines batch-contingent phrasing here; see Q4).

Premise re-verified — lead re-read it at `plan.yaml:101` (the advisor cited `:104-105`; drift from the
concurrent `panel:` rewrite, content byte-identical): *"gh 2.92.0 has no --type flag on issue create
or issue edit, measured, so the CLI cannot set a native type at all."* T-02 states one task later that
`issueTypeId` is a measured input field of **both** `CreateIssueInput` and `UpdateIssueInput`, and the
plan itself sets types through the CLI via `gh api graphql`. The design is a correct **choice**
presented as a physical impossibility.

**What a builder does wrong if it is left:** (a) **defect** — the T-04/T-08 builder reads D-14 as
ground truth, hits T-02's sentence, and creates via GraphQL `createIssue` with `issueTypeId`, typing
atomically at creation; that unwinds the create → record `"created"` → apply → promote `True`
ordering D-10/D-20 mandate and T-03 G / T-05 E / T-07 E pin. The remnant tests go red and stop the
defection, so it is a **stalled build cycle arguing with the plan**, not a shipped defect; or
(b) **dispute** — an SC-04 inspection reviewer flags a signed decision resting on a false premise and
burns a cycle re-litigating a settled choice. The bound is the tests; the cost is time plus an untrue
sentence in a signed record.

Remedy sentence (advisor's wording): *"gh 2.92.0's `issue create` and `issue edit` have no `--type`
flag, measured; setting the type at creation is possible only through the GraphQL `createIssue`
mutation's `issueTypeId` input, which we do not use because it would replace the established
`gh issue create` path — so the type is applied after the create, with the receipt ordering making the
window recoverable."* **Consequence of accepting:** no runtime effect ever.

## Q4 — the batch contingency, re-read

**Recommendation: `PF-452948136bf467869d223e027191ae49` now reads FIX, unconditionally — by its own
terms it read FIX the moment c6 was ordered. No other carried item is moved by batch reasoning. The
advisor retires batch-contingent phrasing from its recommendations.**

Mechanism of the fall-through, named by the advisor: *a conditional recommendation delegates the
condition-check to nobody.* The contingents that were also independently ruled (N3→R5, N5(b)→R4)
landed; the one whose only trigger was "a batch exists" was never re-evaluated when c6 and c7 existed.
Remedy unchanged and tiny: T-06's `verify:` runs `test-gh-backlog-issue-types.py` and
`test-gh-sync.py` while T-06's own intent says *"run test-gh-issue-types.py too and report"* — add the
one line. (Lead-verified at source: T-06 intent carries that clause; T-06 `verify:` does not run the
file.) **Consequence of accepting:** a `cmd_open` regression introduced while T-06 rewires `main()`'s
three-value unpack rides green through T-06's gate and surfaces at the feature-level suite — a later,
costlier debugging loop, not a shipped defect.

Per-item, for the rest of the carried set (none previously withdrawn):
`PF-56a2ce7a` not moved (never contingent; still rule jointly with `PF-0c12a033`) ·
`PF-45294813` **FIX** · `PF-e27f1c30` not moved, accept stands · `PF-0c12a033` not moved, accept /
keep-marker stands · `PF-9a71cb9a` not moved by batch reasoning, merged into Q2's joint deferral ·
`PF-62b2b8ae` **never was contingent** — the c3 recommendation was already an unconditional FIX
(delete T-10 §6's third SKIP bullet, fold into the second); it remains FIX · `PF-e74a2da8` not moved,
nothing to rule · `PF-1280cd8f` residue (a) not moved, accept stands.

## Q5 — invalidation sweep, eight carried findings

**c6/c7 weaken nothing. Two recommendations strengthened, one upgraded by Q4, one merged by Q2, the
rest unchanged.**

1. `PF-56a2ce7a` — **unchanged.** BRIEF SC-12 untouched by c6 (SC-10 only) and c7 (BRIEF not opened);
   re-read at `BRIEF.md:168-175`.
2. `PF-45294813` — text unchanged (T-06 `verify:` not written in either revision); **context changed
   decisively → upgraded to FIX** per Q4.
3. `PF-e27f1c30` — **unchanged, mildly strengthened:** c6's D-13 amendment ("receipt … ONLY on the
   available path") makes T-05 case F explicitly the behavioural proof of the compat guarantee, which
   is the accept rationale.
4. `PF-0c12a033` — **strengthened toward accept / keep-marker.** c6's D-20-aligned rewrite of T-04
   §6/§7 and T-08 §8 gives `"adopted"` a doctrinal home in the four-value vocabulary (absence =
   UNKNOWN, adopted = KNOWN-foreign). Behaviourally still inert; unwinding now costs more than at c3.
5. `PF-9a71cb9a` — unchanged by c6/c7 (T-11/T-12 untouched); **merged with the c4 finding into Q2's
   joint deferral.** The c3 `[unverified]` 511 count is discharged: measured exactly 511.
6. `PF-62b2b8ae` — **unchanged.** Both T-10 §6 SKIP wordings re-read verbatim; T-01 assertion 7 still
   pins a NOT_FOUND errors array to `query_failed`, so the latent contradiction stands; c6's R4
   rewrote §1, not §6. Fold-bullet-three recommendation unchanged.
7. `PF-e74a2da8` — **premise unchanged; surface grew by one literal** (c7 inserted `IT_maintenance`
   into the still-file-global loop, disclosed in the c7 note). Still nothing to rule — **but it is the
   finding to keep in view when specifying Q1's cases:** markers and file-global literals buy gate
   parity, never coverage.
8. `PF-1280cd8f` residue (a) — **unchanged.** T-10 §6's `type_for_parent(overrides)` read from the
   same harness.json re-read verbatim; R4's §1 gate split does not touch it and the fail-safe
   (missing type → SKIP + `refusal_text`, nothing created) is intact. Accept stands.

---

## Lead's assessment — what the operator should notice

- **The consult MOVED three items**, which is why it was worth running: `PF-45294813` accept→FIX,
  `PF-9a71cb9a` merged into a joint deferral with the new c4 low, and `PF-62b2b8ae` re-stated as
  never-contingent FIX (its c3 recommendation was unconditional and has simply not been ruled).
- **Suggested ruling order** (from the advisor's non-conflict analysis at c3-tail, still valid — no
  two remedies touch the same lines): rule **Q1** first because it sizes the batch; then
  **Q3** and **`PF-45294813`** and **`PF-62b2b8ae`**, all one- or two-line edits that ride it; then
  **Q2's joint deferral** and **`PF-56a2ce7a` + `PF-0c12a033` together**; `PF-e27f1c30`,
  `PF-e74a2da8` and `PF-1280cd8f` residue (a) need only accept-or-not.
- **Where the advisor is weaker than it reads:** its Q1 "trap" paragraph overstates (see the boxed
  correction). Its Q2 deferral rests on DEC-205's rewrite-in-place rule, which the lead did not
  re-read — `[unverified]`.
- **What this consult cannot tell you:** whether the operator accepts any of it. Every item above is
  a recommendation, and the eight carried findings plus three new ones remain unruled.

**Still open, for the operator alone:** Q1's disposition (fix-3-routes / fix-1-route / accept with the
risk named), Q2's joint deferral, Q3, `PF-45294813`'s now-unconditional fix, `PF-62b2b8ae`'s fold, and
the accept/keep dispositions on the remainder. Nothing above moves any of them.
