# Plan-panel review (scope reader) — FEAT-54-handoff-done-when — cycle 2

## Conclusion

The revision correctly implements D-10 in every task and code-facing instruction I traced (T-04
resolve=True, T-07 resolve=False, T-02's grammar/resolve split, T-01(g)'s 9-assertion pairing). One
real defect sits in the plan's own record, not its tasks: **D-01's decision text still asserts the
thing D-10 exists to forbid.** One must-fix repair, one advisory duplication, one plain disagreement
with the goal-check note's F-03, and the three unruled cycle-0 findings all STAND unchanged. Verdict
below reflects the must-fix.

## FIND-1 — must_fix — med — D-01 (plan.yaml:104) contradicts D-10 on what INV-17 checks

D-01's `choice` clause: *"block shape and pointer resolution are checked whenever the section is
present, whoever wrote it"* (plan.yaml:104). D-10, added later in the same file, rules the opposite
for the identical pass: INV-17 (`check-state.sh`, `resolve=False`) does "block shape and pointer
GRAMMAR only... and never opens a target" (plan.yaml D-10 choice). T-07 explicitly cites D-01 as its
governing decision ("so it also enforces the Done when contract, per D-01", plan.yaml:524) while its
own instructions correctly implement D-10's resolve=False semantics — the *task* is right, the
*decision it cites* is not. A signer reading D-01 alone, or a future engineer citing D-01 to justify
re-adding target resolution to the persisted pass, would be reinstating exactly the rot vector
PF-4205e7e2 named and the operator ruled against. This is the literal "smuggles resolution back in"
failure mode the dispatch asked me to hunt for — it exists in the decision record, not in T-07's
code instructions. Repair: amend D-01's choice/because to say "pointer grammar" (or defer entirely
to D-10) before signature; one-line, in pm's own writable surface.

## Seam (a) — D-10 write-time-only split: otherwise clean

Every code-facing site I checked is consistent with D-10 and does not re-resolve: T-04 (plan.yaml
:335-337, :364-367) passes `resolve=True`; T-07 (plan.yaml :527-534) passes `resolve=False` and
explicitly forbids opening a target; T-02 §3 (plan.yaml :265-271) specifies grammar-only checks per
pointer type that require no file I/O (prefix + shape only — `plan-task:` suffix literal `.verify`,
`brief-sc:` digit shape, no target opened for `finding:`/`approval:`); T-01 case (g) (plan.yaml
:201-211) pins the D-10 boundary as 4 resolve/no-resolve pairs plus a ninth assertion against an
absent-target fixture, plus counter-assertions that presence/shape/grammar still fire under both
settings. Keeping pointer GRAMMAR in the persisted pass is coherent with the ruling — a typed prefix
consults no target and cannot rot — modulo FIND-1 above, which is the record contradicting its own
mechanism.

## Seam (b) — T-13/D-09 strike: no orphan, SC-07 gradable

Independently grepped `T-13\|D-09` across plan.yaml and BRIEF.md: zero hits (confirms the goal-check
note's grep). No REQ or SC rests on the deleted mutation note. SC-07 (`verify: inspection`, "two
import sites plus the absence of a second parser") is falsifiable as written: the codebase already
has an established sibling-module import convention (`check-domain.sh:104-125`, the
`harness_boundary.py` pattern T-02/T-04 are told to follow), so "one cited file:line" per gate is a
concrete, greppable presence check, paired with a concrete absence check (no second `Scope:`/
`Authority:` parse, no second target-open) per DEC-169's presence-beside-absence rule. Judgment is
required only at the margin of what counts as "another reading of a pointer target" — no worse than
SC-08's already-accepted inspection shape.

## Seam (c) — SC-08's dated-measurement exemption: mechanical enough, narrow residual risk

The exemption test (name a past sha/feature id AND report what was observed) is not perfectly
mechanical in the abstract, but SC-08 pre-names its two current exempt sites by content
(`check-state.sh` FEAT-31 migration comment, INV-17 empty-body narrative — both verified present,
both explicitly naming a commit sha or "FEAT-31 T-10"). That bounds today's ambiguity to sites T-04
and T-07 might newly write, and both of those tasks write normative present-tense prose ("must state
FIVE fixed sections"), not measurement narrative, so the two classes stay visually distinct in
practice. Low residual risk, not a finding on its own.

## Seam (d) — standing of the three unruled cycle-0 findings

- **PF-570b9c87 STANDS**, unchanged. T-06 case (g) (plan.yaml, unmoved) still bakes the real-corpus
  scan plus the mtime/byte no-mutation audit into `test-check-state.py`, a permanent
  `INTEGRATION_SCRIPTS` member. The revision did not touch this case.
- **PF-918326 STANDS**, unchanged. T-09's intent still specifies the `handoff_comprehension`
  `test_kinds` entry with `detect`/`cmd`/`status`/`runner_note` only — no `exclude` key is
  instructed. Independently confirmed at HEAD: all 8 existing kinds carry `exclude`
  (`harness.json:108,114,122,129,135,142,149,156`), including `omp_session_accessor`, the entry T-09
  names as its model. `code_grade.py:469`'s `kind.get("exclude", "")` therefore defaults to no
  exclusion for the new kind alone. Still a one-key, cheap fix; still open.
- **PF-d0ea19ff STANDS**, unchanged. SC-14, T-03(h) and T-06(h) are all still present, planting two
  permanent forever-green regression guards for an explicitly out-of-scope exclusion (per-section
  caps).

## Disagreement with the goal-check note

**F-03 (BLOCKING in the goal-check note) is factually wrong against this plan text.** It claims
"T-04 :360-361 updates only the message... the normative comment [is] instructed by no task." Read
in full, T-04 (plan.yaml:369-381) contains a clause the citation range does not reach: "ALSO bring
this gate's OWN PROSE into the five-section contract," with (i) explicitly targeting the DEC-159
"four fixed sections" comment and (ii) the cap message's "intent, trust, dead ends and a working
set" enumeration — the exact two sites F-03 says are uninstructed. This matches the shared-context
note that "T-04 and SC-08 now also cover the gates' OWN four-section prose" as a stated change of
this revision. F-03 appears to have been read against a truncated slice of T-04's intent. Do not
treat it as blocking; REQ-09's `check-domain.sh` clause is carried.

I agree with F-01 (PF-4205e7e2 still `disposition: open` despite D-10 implementing it — pm's write,
one-line repair) and, weakly, with F-04 (T-04 both adds `"## Done when"` to `check-domain.sh`'s own
`required` heading list and appends the module's own absent-section message, so an author omitting
the section sees the problem twice; not SC-blocking, advisory only — note T-07 explicitly avoids the
identical overlap via `HANDOFF_NARRATIVE_HEADINGS`, which is the asymmetry worth naming).

```yaml
VERDICT: FAIL
DIGEST:
  headline: "D-01's decision text still claims INV-17 resolves pointers, contradicting D-10 in the same plan; one-line repair needed before signature. Everything else traced (D-10 code-facing split, T-13/D-09 strike, SC-08 exemption, three standing findings) is sound; goal-check F-03 is incorrect and should not gate."
  severity_max: med
  findings: 6
  must_fix:
    - "D-01 (plan.yaml:104) says the persisted INV-17 pass checks pointer resolution; D-10 (same file) says it never does. Amend D-01's choice/because to 'pointer grammar' or defer to D-10 before signature."
  spec_violations: []
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml"
  code_grade: n_a
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-planpanel-c2.md
```
