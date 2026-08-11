# Distillation — harness-code-reviewer — FEAT-11-graphql-field-resolve

**Source.** No observations log exists for this agent this feature (confirmed absent). Sole source:
`notes/review-harness-code-reviewer-c0.md`, my single panel run (VERDICT: PASS, 8dedeae..2ea9af3).

**Section counts.** Patterns 10→13. Gotchas 2→2. Outcomes 0→0. Open 0→0. No displacement — Patterns
had headroom (10/15) for three adds without exceeding cap.

## Candidates relayed by the orchestrator — rulings

**C1 — REJECTED.** "Pre-brief is a floor, not a ceiling on what to probe" is the *exact* shape of a
rule already preloaded into every spawn: `harness-handoff` (in context this run) states verbatim
"cited is a floor, never a ceiling" for decisions, and CLAUDE.md carries the same line for the index.
C1 applies that identical rule to a different object (already-ruled panel findings instead of cited
decisions). The marginal content over what is already preloaded every spawn is zero — writing it to
Expertise would spend budget re-stating a rule I already carry. The other half of C1 (measuring that
zero of four reviewers re-raised a ruled item) is telemetry about whether the panel design worked —
lead-tier signal, not a rule that changes my next run. Dropped both halves.

**C2 — ACCEPTED, generalized.** My note showed qa's fragment-boundary unreachability argument
(`id`/`name`/`options` inside a type-conditional inline fragment) does not transfer to `projectV2.id`,
a direct top-level selection one level up with no fragment mechanism to invoke. Kept the rule, dropped
the GraphQL-specific case detail per the skill's own instruction ("keep the rule, drop the cases") →
**P-11**. Checked against P-03 (durable-record-vs-diff verification) for overlap: no overlap — P-03's
target is a written record against ground truth, P-11's is a peer's *reasoning*'s scope against a new
site. Kept both, no `replace`.

**C3 — ACCEPTED as two entries, not one.** My note actually did two separable things the dispatch's
framing bundled: (a) established the D-04 freeze assertions are *unconditionally* evaluated
(top-level `check(...)`, non-raise fails not skips) versus the over-scope guard being *conditionally*
evaluated-but-taken-on-this-green-run (inside `if set_exc is None:`); (b) noted the freeze assertions'
reachability was mine, and their power to actually catch a wrong string (qa's mutant 3) was qa's — two
different questions, two different lenses. My first draft of this distillation kept only (a) and
silently dropped (b); on reflection (b) is exactly the fail-open lens this role is supposed to hunt
(*"reachability proves the check runs, not that it can fail"*) and is actionable on my own future runs
without needing a second reviewer present — I can flag the missing half myself. Wrote both →
**P-12** (reachability grades) and **P-13** (reachability vs. discrimination, flag whichever is
missing).

## Staleness check on existing entries

**None stale.** Positive evidence for currency, not just absence of contradiction: **G-01** ("read at
the pinned SHA via `git show`") was actively exercised this feature — I read
`test-factory-integration.py`'s handler ordering, both D-04 freeze blocks, and the `option_id`
resolution loop at the pinned SHA rather than trusting diff-hunk indentation (`review-...-c0.md:71-73,
115-124, 144-146`). No entry contradicted by this feature's evidence.

## What I would flag upward, not into Expertise

The `projectV2.id` reachability gap noted in my run (`Q1` in that note's DIGEST) is feature-specific
content, not a durable rule — correctly left out of Expertise, still open in the feature's own record.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Distilled FEAT-11 cold: 2 of 3 relayed candidates accepted as 3 generalized Pattern entries (P-11, P-12, P-13), C1 rejected as a duplicate of an already-preloaded skill rule; no existing entry found stale, G-01 positively re-confirmed."
  severity_max: n/a
  findings: 3
  must_fix: []
  spec_violations: []
  reviewed: none
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/expertise/harness-code-reviewer.md
    - .harness/features/FEAT-11-graphql-field-resolve/notes/review-harness-code-reviewer-distill.md
  expertise_update:
    - op: add
      target: P-11
      section: Patterns
      entry: "WHEN inheriting a peer's unreachability argument for a new call site DO check the argument's own preconditions before applying it — a mechanism that holds because of one site's structure does not transfer to a structurally different sibling without its own justification."
      why: "C2 accepted, generalized past its GraphQL fragment-boundary case per the skill's case-dropping rule; checked against P-03 for overlap, none found."
    - op: add
      target: P-12
      section: Patterns
      entry: "WHEN judging whether a guarded test assertion is reachable on a green run DO distinguish \"unconditionally evaluated\" from \"conditional but taken by current fixtures\" — the latter can silently stop firing on a future fixture change without the guard itself ever being touched; note which grade applies."
      why: "C3 half (a) accepted: distinguishing the two reachability grades is what let me correctly separate the D-04 freeze assertions from the over-scope guard this run."
    - op: add
      target: P-13
      section: Patterns
      entry: "WHEN you establish a test assertion is reachable DO check separately whether a discriminating proof exists (a mutant or wrong-value test) that it can actually fail — reachability proves the check runs; only discrimination proves it can catch a wrong result. Flag whichever half is missing."
      why: "C3 half (b), initially dropped from my own draft then restored on reflection — this is the fail-open lens applied to test assertions themselves, actionable solo without a second reviewer present."
artifact: .harness/features/FEAT-11-graphql-field-resolve/notes/review-harness-code-reviewer-distill.md
```

---

## Round 2 — the missed source: `review-harness-code-reviewer-plan-contract.md`

Orchestrator's error, not mine (see dispatch): I ran twice this feature, and the plan-contract review
was never handed to me for round 1. Scope for this round: that one note only, judged against my file
as round 1 left it (13/2/0/0).

**Section counts before this round.** Patterns 13. Gotchas 2. Outcomes 0. Open 0.

### Candidates found in the plan-contract note — rulings

**Section A (anchor audit, D-04 byte-identity) — no new rule.** Direct-read-at-pinned-SHA is G-01
positively re-exercised again (`factory_gh.py:209` and `:255` compared by direct read, not diff-hunk
trust). Recorded as currency evidence, not a new entry — third feature this pattern has held.

**Section B (fail-open hypotheses B-1/B-2, forwarded as open questions not findings) — REJECTED,
already carried.** "If you cannot confirm reachability, forward as an open question rather than assert
a finding" is the same shape as `harness-code-review`'s own preloaded rule ("if you cannot say how it
breaks, drop it") plus `harness-handoff`'s `open_questions` channel definition — both already reach
every spawn without an Expertise entry. This is the identical reasoning I used to reject C1 last round;
consistent call, same precedent applied to myself.

**Section C, first half (SC-08's evidence base — BRIEF cites `patch_gh`-mocked suites as REQ-05's
proof, but those suites replace `project_field_set` at the module-attribute level before any call, so
their green result never exercises the rewritten implementation; the real proof is elsewhere, in a
subprocess-driven integration suite) — ACCEPTED, new entry → P-14.**
Checked against P-01 (test label vs. actual invocation/assertion at that line): does not fire here —
`patch_gh`'s Recorder-backed suites have honest labels and honest assertions on every line; the
assertions are real, they just run against a stand-in, not the SUT. P-01's lens (label vs. own body)
passes such a suite cleanly. This candidate's WHEN is different (an external document's evidence
citation) and DO is different (check for module-attribute replacement of the function under test) —
no overlap, both entries earn their slots. Also directly operational for Stage 1's `verify: inspection`
duty on `SC-NN` items citing test files as evidence. Added as **P-14** (Patterns 13→14, no
displacement needed).

**Section C, second half (Redy typo case — D-04's `because` clause claims `_validate_stations`
depends on `factory_gh.py:251-262`'s frozen string; direct read shows it never calls
`project_field_set` and asserts only its own `refuse(...)` message, so the dependency is false; same
false premise sits in both `plan.yaml` and the grilling artifact, which is why it escalated (E-1)) —
ACCEPTED as a `replace` on P-03, not a new entry.**
Discriminator checked first: does current P-03 fire on this instance? Read literally, P-03's WHEN is
"a commit message or a decisions-doc entry asserts **what a change did**." A `because` clause naming
*which consumers depend on what* is a claim about dependency structure, not about what the change
itself did — P-03 does not fire on it as written, so the widening carries real marginal value rather
than restating a rule I already hold.
First draft stapled two WHEN/DO branches ("what a change did, or why a constraint is needed... verify
against the diff... or the cited dependents' own source...") — rejected that shape on review: two
matched branches in one entry is a story, not a rule, per the skill's own red-flag table. Rewrote as a
single WHEN/DO generalizing the evidence source rather than enumerating claim-types: verify a durable
record's factual claim about the code against the code it names, not against the record. This covers
both the original commit-message/diff case and the new because-clause/call-graph case under one
mechanism, at the same length. Applied as **replace, target P-03** (Patterns stays at 14, a replace
consumes no slot).

**Net this round: Patterns 13 → 14/15** (one `add`, P-14; one `replace`, P-03 — no displacement, no
cap pressure).

**Positive currency evidence, no ops:** P-12 (reachability grades) re-exercised in Section D — the
over-scope regex guard "runs only inside `project_field_set`'s success-case test" is precisely the
conditional-but-taken-on-this-green-run grade the entry names.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Round 2, one missed source (plan-contract review) distilled cold: one new Pattern entry (P-14, mocked-evidence citations) and one replace sharpening P-03 to cover rationale/dependency claims alongside provenance claims; Section B's forward-as-open-question candidate rejected on my own C1 precedent; Patterns now 14/15, no displacement."
  severity_max: n/a
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: none
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/expertise/harness-code-reviewer.md
    - .harness/features/FEAT-11-graphql-field-resolve/notes/review-harness-code-reviewer-distill.md
  expertise_update:
    - op: add
      target: P-14
      section: Patterns
      entry: "WHEN a BRIEF or plan cites tests as evidence for a requirement DO check whether those tests exercise the real implementation or a mocked stand-in — a green suite that replaces the function under test proves only caller shape, not the requirement's behavior."
      why: "Section C first half: SC-08's cited suites (patch_gh, module-attribute replacement) never invoke the rewritten factory_gh.py; the real proof was a separate subprocess-driven integration suite the BRIEF didn't name. Checked against P-01, no overlap: P-01 grades a test's own label against its own body, this grades an external evidence citation against whether the cited test reaches the SUT at all."
    - op: replace
      target: P-03
      section: Patterns
      entry: "WHEN a durable record (commit message, decisions-doc entry) asserts a fact about the code — what a change did, or which consumers depend on what — DO verify it against the code it names, not the record itself — records assert intent, not ground truth."
      why: "Section C second half: D-04's because clause claimed two named consumers depend on two frozen strings; direct read of both consumers' call graphs showed neither dependency exists. Old P-03's WHEN (\"asserts what a change did\") literally does not fire on a because/rationale claim, so this is real widening, not restatement. Rejected a first-draft two-branch staple (what-did/diff vs why-needed/call-graph) as a story-shape red flag; replaced with one WHEN/DO generalizing the evidence source instead of enumerating claim-types, same length, still covers the original commit-message case."
artifact: .harness/features/FEAT-11-graphql-field-resolve/notes/review-harness-code-reviewer-distill.md
```
