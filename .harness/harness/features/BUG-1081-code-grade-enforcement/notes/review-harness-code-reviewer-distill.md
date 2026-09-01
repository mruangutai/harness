# Distillation — harness-code-reviewer — BUG-1081-code-grade-enforcement

**Two candidates accepted (craft, both via displacement), one rejected.** Repository-tier file
untouched — nothing from this feature turned on a path/file/decision unique to this repo beyond
what G-01..G-05 already hold.

## Tool-mechanics note (read before trusting the ops list below)

`expertise-merge.py apply` is a strictly additive union merge: same-id-different-text is a hard
CONFLICT (exit 7, nothing applied) and it has no drop/replace primitive at all — confirmed by
reading `compute_union`/`cmd_apply` directly (`.agents/skills/harness/bin/expertise-merge.py:113-193`)
and by `test-expertise-merge.py`'s case 5 (`case_cap_overflow`: file byte-identical to before on
cap overflow). Both craft sections I needed were already at their exact cap (Patterns 15/15,
Gotchas 15/15, Outcomes 10/10). A "replace" op as the SKILL's ops schema describes it (same
`target` id, new text) is therefore not executable through the tool alone. I resolved it as the
distill SKILL's exit-7/exit-8 guidance directs ("resolve yourself" / "curate rather than
append"): I removed exactly the two superseded lines (P-08, P-12 — nothing else touched, verified
byte-identical elsewhere) via a direct, immediately-re-read-first write to bring Patterns to
13/15, then used the merge tool to ADD the two sharpened replacements under lock. This keeps the
tool as the mechanism for every genuinely new addition and confines the manual step to the one
operation (deletion) the tool cannot perform under any invocation. `check-expertise.sh` run
single-file afterward reports both files `OK`.

## Section counts

| File | Section | Before | After |
|---|---|---|---|
| `.harness/expertise/harness-code-reviewer.md` | Patterns | 15/15 | 15/15 |
| `.harness/expertise/harness-code-reviewer.md` | Gotchas | 15/15 | 15/15 (unchanged) |
| `.harness/expertise/harness-code-reviewer.md` | Outcomes | 10/10 | 10/10 (unchanged) |
| `.harness/expertise/harness-code-reviewer.md` | Open | 0/5 | 0/5 (unchanged) |
| `.harness/harness/expertise/harness-code-reviewer.md` | all | unchanged | unchanged |

Net Patterns composition: 13 entries carried untouched, P-08 and P-12 both replaced in place
(new text, same id, re-appended at the tail of the section by the tool — id numbering is now
non-sequential in file order; this is cosmetic, `check-expertise.sh` does not require sequential
order).

## Accepted

**Candidate 1 → craft, replaces P-12.** My cycle-2 full-suite `sys.settrace` line trace
(`review-harness-code-reviewer-c2.md` §4) proved `_contained_feature_dir`'s realpath-containment
branch executed zero times across the entire committed suite — every hostile fixture was caught
by the earlier segment check first — and this became the panel's actionable coverage gap (c2
validator digest Q2), closed by `check_symlinked_feature_component`. Old P-12 only prescribed
checking discrimination *after* reachability is established; it had no instruction to establish
ground-truth reachability itself, and reading fixtures by eye is exactly how this gap could have
been missed (each of the four fixtures looks individually plausible as a defeat of the branch).
New P-12 folds in the measured technique — run a full-suite dynamic trace rather than reason
fixture-by-fixture — ahead of the existing discrimination check, as one entry, not two. Evidence:
`review-harness-code-reviewer-c2.md` §4 ("Coverage gap, measured"); `2026-09-01-c2-validator/digest.md`
Q2 and its disposition ("Q2 resolved: `check_symlinked_feature_component` added, with mutation
evidence").

**Candidate 2 → craft, replaces P-08.** c1's validator digest recorded, for F1, that "neither
reviewer could call this from inside its own lens" — I (code review) correctly answered every
adversarial category I had enumerated (depth, symlink, non-git) and marked the boundary
requirement MET; the defeat was a hostile string producing a *valid but different* root, a
category outside my enumeration entirely, not a failure of any answered question. This is the
same underlying failure shape old P-08 already named for a *different* mechanism (a peer's
clearance answering their question but not yours) — both are "the bound of what got evaluated
is not the bound of what could go wrong." Rather than add a second, narrower entry beside P-08
(a distillation smell — same rule, two cases), I generalized P-08's wording to cover both the
inherited-peer-clearance case and the self-enumeration case as one rule, dropping the specific
glob-character-class example per the "keep the rule, drop the cases" instruction. Evidence:
`2026-09-01-02-validator/digest.md` F1 ("Overturns one stage-1 grade... Neither reviewer could
call this from inside its own lens").

## Rejected

**Candidate 3 — reject, no new entry.** The finding (a simplify receipt overstated duplication;
the discarded call was the sole assertion the digest's declared base resolves) is real and I
stand by it, but it does not clear the distillation bar: the *methodology* it exemplifies —
verify a record's claim against the code rather than trust it, including across a moved pin — is
already P-03 verbatim ("both assert intent, not ground truth"), and "trace a false downstream
claim to its authoring source" is already O-02. The only thing candidate 3 adds beyond those two
is the observation that a correction to a committed record can ride as a non-blocking backlog
item indefinitely because nothing in the must_fix/severity framework ever forces it closed — but
that is a harness/process gap (how backlog items get resolved), not a review technique, and
raising it as Expertise would misfile a structural question as personal craft. No entry added.

```yaml
VERDICT: PASS
DIGEST:
  headline: Two craft Patterns sharpened by replacement (P-08, P-12) via drop-then-merge-tool-add since the union-merge tool has no in-place replace primitive; one candidate rejected as already covered by P-03/O-02; repository tier untouched
  expertise_update:
    - op: replace
      target: P-12
      section: Patterns
      file: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/expertise/harness-code-reviewer.md
      entry: "WHEN judging whether a security-relevant branch is exercised DO run a full-suite dynamic trace (e.g. sys.settrace) rather than reason fixture-by-fixture — each hostile fixture can be caught earlier, leaving the branch at zero real executions though it looks reachable; then check for a discriminating mutant."
      why: "cycle-2 sys.settrace trace proved a security branch had zero executions despite four fixtures looking like they should reach it; old P-12 only covered the discrimination half, not establishing ground-truth reachability"
    - op: replace
      target: P-08
      section: Patterns
      file: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/expertise/harness-code-reviewer.md
      entry: "WHEN evaluating a boundary or identity check against an enumerated set of adversarial questions — your own or an inherited peer's clearance — DO ask what category the set omits; a defeat that returns a valid-but-different result sits outside any bounded enumeration by construction."
      why: "generalizes old P-08 (peer-clearance mismatch) to also cover self-enumeration gaps, evidenced by cycle-1's boundary defeat that no enumerated adversarial question (mine or the peer's) had named"
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/expertise/harness-code-reviewer.md
    - .harness/harness/features/BUG-1081-code-grade-enforcement/notes/review-harness-code-reviewer-distill.md
  open_questions: []
artifact: .harness/harness/features/BUG-1081-code-grade-enforcement/notes/review-harness-code-reviewer-distill.md
```
