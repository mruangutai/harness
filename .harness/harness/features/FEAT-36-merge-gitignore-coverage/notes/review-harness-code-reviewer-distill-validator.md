# Code-reviewer Expertise distillation — FEAT-36

**BLUF: BLOCKED.** All three digest-skim candidates are durable craft lessons, but the mandated merge tool cannot apply the required same-ID replacements: it refused all three atomically with exit 7. No Expertise file changed.

## Source-separated judgment

- **Observations:** 0 accepted from 0 candidates. `.harness/harness/features/FEAT-36-merge-gitignore-coverage/observations/harness-code-reviewer.md` is absent, as verified by targeted path lookup; no observation log was created or altered.
- **Digest skim:** 3 accepted from 3 distinct candidates. `runs/review-validator/digest.md` supplied candidates 1 and 3; `runs/review-c2-validator/digest.md` supplied candidate 2 and independently repeated candidate 1, which was counted once.
- **Rejected candidates:** none.

## Candidate dispositions

1. **Accepted — exact diagnostic sets.** F-02 demonstrates a durable fail-open assertion class: substring or per-member membership can accept decorated near-matches and fabricated supersets. This sharpens and subsumes craft G-13; the c2 recurrence supports durability.
2. **Accepted — two-sided preservation.** SC-05/adequacy demonstrates that a signed non-interference criterion needs independent proof of both the requested transition and byte-identical preservation of pre-existing caller state. This displaces narrower craft P-04, which only covers presence/absence checks for duplication.
3. **Accepted — the whole pinned matrix governs.** F-01 demonstrates that one changed behavioral test passing does not turn a separate required matrix failure green. This replaces craft P-06 and corrects its stale `HEAD` wording to the immutable review pin.

## Curation and section caps

| Tier | Section | Before | After | Disposition |
|---|---:|---:|---:|---|
| craft | Patterns | 15 | 15 | P-04 selected for displacement; P-06 selected for stale correction; neither applied |
| craft | Gotchas | 15 | 15 | G-13 selected for a subsuming replacement; not applied |
| craft | Outcomes | 10 | 10 | retained |
| craft | Open | 0 | 0 | retained |
| repository | Patterns | 0 | 0 | untouched; candidates are repository-independent craft |
| repository | Gotchas | 4 | 4 | retained |
| repository | Outcomes | 0 | 0 | retained |
| repository | Open | 0 | 0 | retained |

Stale-entry audit: P-06 is stale because it directs review against `HEAD`, contrary to pinned-SHA review. P-04 and G-13 are not false, but are weaker than the accepted replacements. No other entry had evidence of staleness, so all others were retained.

## Exact intended ops and application evidence

```yaml
- op: replace
  target: P-04
  section: Patterns
  entry: "WHEN a signed criterion changes one target while promising preservation elsewhere DO verify both postconditions independently: the requested transition occurs and pre-existing caller state remains byte-identical — a passing target-transition assertion does not prove non-interference."
  why: "Accepted digest-skim candidate 2; displaces a narrower presence/duplication heuristic."
- op: replace
  target: P-06
  section: Patterns
  entry: "WHEN the required matrix fails at the pinned review SHA DO report the red gate as a finding even if the changed behavioral test passes — success of one registration does not turn a separate required failure green."
  why: "Accepted digest-skim candidate 3; corrects stale HEAD wording and records pinned-matrix precedence."
- op: replace
  target: G-13
  section: Gotchas
  entry: "WHEN output is a closed diagnostic set DO compare parsed exact records for equality, not substring or per-member presence — both allow fabricated supersets or decorated near-matches to pass."
  why: "Accepted digest-skim candidate 1, repeated at c2; subsumes the narrower enumeration-membership rule."
```

`expertise-merge.py apply --file .harness/expertise/harness-code-reviewer.md --entries -` returned exit 7 with `CONFLICT` for P-04, P-06, and G-13, showing each existing and proposed text. The tool implements additive union only; it has no replace/drop operation with which to resolve a full-section displacement. A scoped `git diff` over both owned Expertise paths was empty after the refusal.

**Successfully applied ops:** `[]`.

## Scoped checks and touched files

- Expertise checks: none run, because no Expertise file changed; the assignment permits `check-expertise.sh` only for changed Expertise files.
- Touched: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-distill-validator.md` only.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "Three craft replacements are accepted, but expertise-merge.py atomically refused them and no permitted replacement path exists."
  severity_max: high
  findings: 1
  must_fix:
    - "Provide a merge-tool replacement/drop path or an explicitly approved non-whole-file owner-safe application mechanism, then apply the three exact replacements recorded here."
  spec_violations: []
  reviewed: "FEAT-36 digest-skim distillation sources"
  human_commits_in_scope: []
  source_counts:
    observation: {accepted: 0, candidates: 0}
    digest_skim: {accepted: 3, candidates: 3}
  open_questions:
    - {id: Q1, question: "What permitted mechanism should apply same-ID replacements when expertise-merge.py refuses them with exit 7?", blocking: true}
  files_touched:
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-distill-validator.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-distill-validator.md
```
