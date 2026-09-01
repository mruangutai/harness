# UI Review c1 — BUG-1080 inv6-plan-phase-runs (operator-message remit)

Reviewed the remedy delta `a2fb6c0b`..`e9b11035` (confirmed via `git diff a2fb6c0b e9b11035 --
.claude/skills/harness/bin/check-state.sh`). Judging text only, per dispatch: the rewritten INV-6
message, the new SKILL.md step 6 instruction, and the two new test cases' failure diagnostics.

## 1. INV-6 violation message (`check-state.sh:462-464`) — cycle 0's MED is genuinely closed

Old (`a2fb6c0b`): `"{feat}: a validator run reviewed code but review_sha is not pinned —
reviewers would diff HEAD (the GAP-7 failure)."` New adds one sentence: `"A run that graded a
plan and no code carries \`code_grade: n_a\` and needs no pin (DEC-207)."`

This names the concrete key, the exact legal value, and the citation — an operator who hits this
can now act (`code_grade: n_a`) without opening `check-state.sh` or `feature-schema.json`, closing
cycle 0's finding exactly as its own "one-line, reversible fix" suggestion described.

**Convention comparison against INV-32 (`check-state.sh:286-297`).** INV-32's pattern is
condition → imperative remedy ("set `panel_era_start` to the date..."). INV-6's new sentence is
declarative ("carries `code_grade: n_a` and needs no pin") rather than imperative ("add
`code_grade: n_a` to it"), but the actionable content is equivalent — a reader has to make the
same one-word inferential leap ("carries" → "so add it") in both. Not over-long: comparable
sentence count and length to the INV-32 precedent. **No finding.**

**Ambiguity about WHICH run, in a multi-run feature.** The message's *first* clause — "a validator
run reviewed code but review_sha is not pinned" — is verbatim unchanged from `a2fb6c0b` and, per
`git show 9f2a0702`, was already unqualified before BUG-1080 existed at all (`any(sq ==
"validator"...)`). A feature with several validator entries gets one message naming the feature,
never the offending run's `id`. This is real but **out of the remedy's scope to fix** (dispatch:
"except where the remedy changed it" — this clause is untouched), and INV-32 sets no counter-
example since a feature carries exactly one `approval`/`panel`, never a list. Noting for whoever
next touches this block, not gating.

## 2. SKILL.md step 6 instruction (~lines 65-68) — the rule itself is unambiguous; a downstream interaction is not confirmed closed

> "A validator run that graded a PLAN and no code carries `code_grade: n_a` ... Every other run
> omits the key."

**As a rule for the orchestrator, this is a clean bright line**: stamp the key only when the run
graded a plan and reviewed no code. A validator run that *did* review code fails that test
regardless of when it ran, and correctly gets no key — so a reader cannot be talked into exempting
a genuine code-review run by this wording. On the specific worry named in dispatch ("a validator
run in the BUILD phase that did review code") — no, the criterion discriminates on WHAT was
graded, not WHEN, so that case is not a plausible misreading.

**The unconfirmed interaction, raised as an open question, not a finding against this text**:
`check-state.sh` line 132 of this same SKILL.md calls the Build-phase QA step itself "a
validator-squad segment," and the historical corpus (`FEAT-10`, `FEAT-12`, `FEAT-20`, …) records
those as `squad: validator` runs — id patterns like `qa-validator`, `qagate-validator`. Per SKILL.md
step 4, `review_sha` is not pinned until *after* that QA segment and after SIMPLIFY. Per this
step's own rule, a QA-gate run graded neither a plan nor code, so it correctly "omits the key" —
but `check-state.sh`'s `code_reviewing_runs` filter (unchanged in scope by this remedy: it only
*narrowed* which validator runs count, never widened who's exempt) treats ANY validator-squad
entry lacking `code_grade: n_a` as code-reviewing. If that combination is ever live — a QA-gate run
recorded, `check-state.sh` invoked, before the step-4 pin — INV-6 fires on ordinary Build-phase
progress, and the text's own framing ("INV-6 then demands a review_sha that cannot exist before
the Building → Review seam, which is exactly the deadlock BUG-1080 closed") could read to an
operator as if that whole pre-seam class is now handled, when only the plan-phase panel category
is. **I could not confirm this manifests**: `check-state.sh` is a self-run pre-commit discipline,
not a git-enforced hook (confirmed: only `post-merge` is tracked under `core.hooksPath`), and the
corpus's own validator runs are all read at a state where `review_sha` was already pinned, so
whether QA-gate entries and the pin land in the same commit in real practice is not established
from source alone. This is an architecture/gate-design question (does INV-6's trigger need the
same run-level exemption axis QA-gate runs would use), not a wording defect in this text — routing
it to the code-reviewer lens as an open question rather than filing it against SKILL.md's prose.

## 3. New test failure diagnostics (`test-check-state.py:3420-3455`)

- `case_inv6_message_names_the_remedy` (fails → prints `"the message states the defect without the
  remedy"`): names exactly what's missing.
- `case_inv6_producer_is_documented` (fails → prints `"nothing instructs any writer to stamp the
  key, so every recorded plan panel omits it and INV-6 deadlocks again"`): names the consequence
  and, via its own docstring ("SKILL.md step 6 is the only documented runs-writing instruction"),
  points at the one place to fix. Both diagnostics are actionable without re-reading the test body.
  **No finding.**

## Verdict rationale

No `must_fix`. Cycle 0's MED is closed by direct comparison of message text. One non-blocking,
pre-existing (not remedy-introduced) ambiguity about which run is at fault in a multi-run feature.
One open question, correctly unresolved from a text-only lens, about whether the exemption axis
needs to widen beyond the plan-phase category to cover Build-phase QA-gate runs — routed to
code-review, not filed as a UI wording defect since the SKILL.md rule itself reads unambiguously.

`severity_max: low` → PASS.
