# Grilling — a standard for what constitutes a decision (FEAT-46)

Origin: the operator read `DECISIONS.md` and judged that FEAT-38, which folded amendments into their
entries, left a file that is still overwhelmingly prose commentary rather than decisions. That is a
different defect from the one FEAT-38 was scoped to fix, and both readings are correct: the fold can
be sound while the thing folded was never a decision.

Every figure below was measured on the FEAT-38 worktree at `635cd3ba`, 188 entries, 6,240 lines of
entry body. Measurements were re-run once after a zero-padding bug (`DEC-04` vs `DEC-4`) and an
index-row contamination were found in the first pass; the corrected numbers are the ones here.

## The destination

`DECISIONS.md` states decisions. An entry is a choice that still binds future work, written in a
fixed clause form, with commentary capped at a tenth of its length. Everything failing that either
gets rewritten into the form or leaves the file, and the machinery enforces the shape so the drift
cannot recur.

## Settled

| # | Ruling | Consequence |
|---|---|---|
| 1 | **Two axes, not one.** Failing the *form* means rewrite; failing the *substance* means strike | 94 form-failing entries are cited durably, 29 heavily. A form-based prune would delete `DEC-120`, `DEC-203`, `DEC-138`, `DEC-182` — the constitution |
| 2 | **Substance test: `DEC-23` verbatim, plus forward force.** A choice stays; an observation about behaviour goes; a choice that no longer binds anything is also struck | `DEC-105` (token baseline) is an observation → strike. `DEC-94` (pilot host) was a real choice with no forward force → strike |
| 3 | **Form: `Chose` and `Because` mandatory. `Over` and `Tradeoff` only when real** | Refused all-four-unconditionally: `DEC-190` has no rejected alternative, and forcing one invites a fabricated `Over:`, which is worse than prose |
| 4 | **Prose cap 10%** of an entry's non-blank lines, prose being any block not opening with a clause marker | The threshold is inert: 10% and 20% fail the identical 111 entries. The distribution is bimodal — entries score ~0% or 100% |
| 5 | **Displaced prose is deleted; `git log --follow` holds the history** | `DEC-205`'s own accepted cost, reused rather than re-argued. No relocation project, no ~100 sidecar rationale files |
| 6 | **Triage is agent-run; every strike needs a second independent reader** | Only strikes both readers agree on reach the operator; disagreements arrive as a pair with both arguments. A wrong strike deletes a rule something still obeys, and does it silently |
| 7 | **One feature, phased** | Standard → checker in warn mode → triage and strikes → rewrites → checker blocking |

## Derived, not asked

- **The standard already exists.** `DEC-23` — "a *choice* goes to `PLAN.md ## Decisions`; an
  *observation about how the codebase behaves* goes to the mental model" — was scoped to `PLAN.md`
  and mental models and never pointed at the authority file. FEAT-46 extends an approved boundary
  rather than authoring a new one. `DEC-105` is `DEC-23`'s own counter-example wearing a DEC number.
- **Zero citation refactoring.** `DEC-205`: a deleted number is never reused and numbers are never
  renumbered. Rewriting the 990 durable citations would destroy the audit trail — every historical
  note saying "under DEC-105" was true when written. The 6,986 citations in runs, notes, logs and
  feature dirs are never touched.
- **A strike owes a named successor.** `DEC-205`, as amended by FEAT-38: struck only once a named
  successor exists that its citations can be repointed to. Of the 98 zero-clause entries, 85 are
  durably cited, so a strike there is not free.
- **Struck records are exempt from the form check.** `DEC-90` is a tombstone; it has no clauses to
  carry and must not be forced into one.
- **Tables count as prose.** This is why `DEC-105`'s measurement table scores 100%.
- **The checker requires rewriting `DEC-205`.** It states "one mechanical check guards this file, and
  only one", and records two refused checks so nobody re-suggests them. A form-and-prose checker
  survives that clause's own logic — mechanical, zero judgement, inspects the file's shape rather
  than the world — but the rewrite must be explicit. Amendments are ended, so `DEC-23` and `DEC-205`
  are *rewritten*, not annotated.
- **FEAT-38 lands first.** It owns the current text of `DEC-205` and `DEC-181`. Two features editing
  the same entries concurrently is the merge conflict this whole convention exists to avoid.
- **DEC-174 carve-out applies.** The checker is enforcement-layer code, so tasks touching it run
  `main-session-direct` and cannot be validated through the path being changed.

## The measurement that reframed the ask

The operator's summary was that *much of the decisions and their prose can be removed*. The file
disagrees:

| Bucket | Count | Remedy |
|---|---|---|
| Clause form, ~0% prose | 77 | keep |
| Clauses **plus** a prose tail — `DEC-95` 67%, `DEC-99` 78% | 13 | cut the tail, no judgement needed |
| Zero clauses, durably cited | 85 | mostly rewrite; strike only on the substance test |
| Zero clauses, uncited | 13 | cheapest strikes, but the list still holds `DEC-205` and `DEC-190` |

**The removal set is small; the rewrite set is large.** The file is mostly decisions in the wrong
clothes with a commentary minority, not the reverse. Planning must size for rewriting, not deleting.

## Fog — named, not resolved

- **How many entries actually fail the substance test is unmeasured.** It needs the rubric applied
  per entry, which is the triage itself. The 13 uncited zero-clause entries are a floor, not an
  estimate.
- **Whether a 10% prose cap is survivable by genuinely complex decisions is untested.** `DEC-138`
  (GitHub integration) and `DEC-174` (the self-hosting boundary) are 108 and 101 prose lines. If
  either cannot be stated in clause form without losing something load-bearing, the cap is wrong and
  that will surface during the rewrite, not before it.
- **Nobody has measured whether a shorter `DECISIONS.md` is better read.** The per-spawn cost
  argument is real and recorded (`DEC-105`, `DEC-135`), but "an entry a reader trusts" is the stated
  goal and it has no metric.

## Out of scope, explicitly

- **Rewriting historical citations.** Prohibited by `DEC-205`, and it would erase the record.
- **A propagation checker.** Struck whole under `DEC-188`; not revived here.
- **The referenced-file watch (M3) and the periodic LLM audit (M4).** Refused in `DEC-205` with
  reasoning. FEAT-46 does not re-litigate them; its checker is a third thing.
- **`DECISIONS-INDEX.md`'s full generation contract.** Issue 686 remains open in part; FEAT-46 needs
  only that a struck entry's row behaves.
- **FEAT-38's UAT.** Independent. Its three folded entries are judged on their own terms, and this
  critique neither passes nor fails it.
