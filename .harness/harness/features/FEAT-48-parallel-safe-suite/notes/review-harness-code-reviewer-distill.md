# Distillation — harness-code-reviewer — FEAT-48-parallel-safe-suite

## BLUF

Repository tier got two new, real entries (`G-06`, `G-07`) — genuine room existed there. Craft
tier's three sections were already at cap (15/15/10) with **zero deletion capability in
`expertise-merge.py apply`** — verified by reading the tool's source and then by two real dry
runs against the live file, both cleanly refused with nothing written. Four craft-worthy
candidates (one from the lead's relay, three self-derived from the plan-panel notes) that I
judge stronger than four existing entries could not be applied for that reason; the denial is
quoted below and raised as a harness-defect `open_question`, not routed around.

## Material read

Per dispatch: `harness-distill/SKILL.md` first; then `notes/review-harness-code-reviewer-{c7,c8,c9}.md`,
the seven `notes/review-harness-code-reviewer-planpanel-{c0..c6}.md`, and
`notes/ship-review-2026-09-02-c9.md` (CEO briefing). No observations log exists for this role on
this feature (expected — only pm and the orchestrator kept one).

## Relayed candidates — judged

**(a) c8's "7 pre-existing / 2 introduced" `code_grade` partition, retracted by the lead.**
ACCEPTED, in judgment. Confirmed at source (`code-grade.py`'s own selection logic, re-read):
the tool only ever reports a function with no pre-image or a worsened grade — there is no
representable "inherited, unrelated, unchanged" category, so any partition claiming that shape
is wrong by construction, independent of whether the specific c8 count was also stale. Distilled
two ways: a general craft form (blocked, see below) and a repo-specific form naming
`code-grade.py` directly, which DID apply → `G-06` (repository tier).

**(b) the panel's decomposition prediction (3-of-5 records) vs. the applied fix (7→9, worse).**
REJECTED. Six-spawns test fails: this is an instance of already-present craft `P-03` ("a record
or a prior gate's result asserts a fact about the code... verify against the code... asserts
intent, not ground truth"). A prediction about a future gate outcome is exactly this class of
unverified claim; `P-03` already tells me to re-verify it rather than trust it. No new rule
needed.

**(c) B-5 — shipped code safer than the signed plan text; remedy was amending the text, not
reverting the code.** ACCEPTED, in judgment. This is a distinct lesson from anything currently
in Outcomes: existing `O-06` says judge severity by consequence, not by blame for deviating from
the plan — it doesn't say which of the two artifacts (code or text) is the one to fix. Distilled
as a craft Outcomes candidate (blocked, see below).

## Self-derived candidates, from the seven plan-panel notes

The plan-panel notes are a distinct body (reviewing a *plan's* verify blocks and prose, not
code) and count fully as my own material.

**ACCEPTED** — verify-regex-vs-house-style (cycle 2/3): T-05's DEC-heading regex required a bare
space where all 188/188 (later 193/193) existing `DECISIONS.md` headings carry an em-dash; an
author following the file's own universal convention would have reddened a substantively correct
entry. Generalizes past this one file: test a verify block's text-matching regex against real
samples of the target document's own convention, not the spec author's assumed shape. Craft
Patterns candidate (blocked, see below).

**ACCEPTED** — intent-narrower-than-downstream-verify (cycle 4, the HIGH finding, "no tree exists
in which T-02 and T-03 pass as currently scoped"): a task's own intent named specific hazard
sites; a *later* task's verify asserted a whole-tree property (zero live findings); three sites
existed that no task's intent covered, so a faithful, fully-correct execution of the narrowly
scoped intent still reddened the downstream check on every run. Distinct from existing craft
(`P-09`, which is about a guard's *own* untested routes, not a cross-task scope mismatch). Craft
Patterns candidate (blocked, see below).

**REJECTED** — "a fix for one disclosed blind spot (T-03's content-read exclusion) opens a new,
unnamed one in the same family" (cycle 3, F2). Six-spawns test: close, but this is a narrower
restatement of the same "narrowing fix vs. disclosed claim" shape existing `P-07`
("who watches the watcher") and the D-11-overclaim pattern already cover in spirit; not
distinct enough to earn a slot over stronger candidates, and craft has no room regardless.

**REJECTED** — "ambiguity that fails loud (self-correcting) rates lower severity than ambiguity
that fails silent" (cycle 2, the `.claude` dot-directory-pruning finding). Real technique, but
softer and less rigorously evidenced than the four accepted candidates; with craft full and a
hard ranking required, this one did not make the cut.

**REJECTED** — "ownership/completeness is proven by a derived mechanism (a computed `run_set`),
not by a static `files:` list" (cycle 5, §6). Valuable but narrower — specific to this plan's own
derived-ownership design, not obviously portable to a repository that doesn't use that idiom.
Below the bar given the competition for a full section.

**REJECTED** — cross-plan staleness (cycle 1, G-01: a sibling plan's prose describes a pre-fix
draft of a shared file). Genuinely a distinct class from existing `G-03` (recurring claim, check
each occurrence's scope) but weaker in general applicability — most repos don't run twin
concurrent plans against the same file the way this one does. Left out under the cap.

## Applied

### Repository tier — real writes, room existed

```
op: add, target: (new), section: Gotchas, entry: G-06
  "WHEN reading a code-grade.py report DO remember it only lists functions with no pre-image
  (new) or a worsened grade versus base — it never emits an 'inherited, unrelated, unchanged'
  record, so a partition claiming that shape for any listed record is definitionally wrong."
  why: c8's retracted 7-pre-existing/2-introduced partition (relay candidate a) was wrong
  because this category is unrepresentable in the tool's own output — the general form is
  craft (blocked below); this is the repo-specific instantiation naming the actual tool.

op: add, target: (new), section: Gotchas, entry: G-07
  "WHEN reviewing run_pool.py's --mutation-check snapshot DO note `_record`'s `except OSError`
  swallows every OSError, not only FileNotFoundError — removing a watched directory's execute
  bit mid-run hides any file created inside it from both snapshots (open backlog row, unresolved
  as of this build)."
  why: c8/c9/ship-briefing's B-1 backlog row (`_record` swallows every OSError) is a durable,
  currently-true, disclosed-but-unresolved fact about this repo's own mutation-check mechanism —
  the same convention as the file's existing G-01..G-05 (specific bin-script behavioral facts).
```

Applied via `expertise-merge.py apply --file .harness/harness/expertise/harness-code-reviewer.md`:
`ADDED G-06`, `ADDED G-07`, `PRESERVED G-01..G-05`, `APPLIED`, exit 0.
`check-expertise.sh` on both files: `OK`, exit 0.

### Craft tier — attempted, ACTUALLY DENIED, ops returned verbatim

Craft's three sections were already at cap (Patterns 15/15, Gotchas 15/15, Outcomes 10/10)
*before* this run. `expertise-merge.py apply`'s only two failure modes are `CONFLICT` (exit 7,
same id + different text) and `CAP EXCEEDED` (exit 8, new id past the cap) — confirmed by
reading `compute_union` directly: `merged_list` is seeded from `base_entries` and nothing in the
tool ever removes an entry from it. There is no code path that implements the `op: replace` /
`op: drop` semantics `harness-distill/SKILL.md` documents. I confirmed this is real, not a
misreading, with two throwaway dry-run probes against the live file (`P-10` collision, `P-99`
cap overflow) before submitting the real candidates — both refused, file verified byte-unchanged
after.

The real attempt, submitted together, exit 7, **nothing applied** (quoted verbatim):

```
CONFLICT section=Patterns id=P-10
  existing text: WHEN inheriting a peer's unreachability argument for a new call site DO check
    the argument's own preconditions before applying it — a mechanism that holds because of one
    site's structure does not transfer to a structurally different sibling without its own
    justification.
  proposed text: WHEN a verify block's regex matches text by an assumed shape (heading
    separator, keyword form) DO test it against real samples from the target document's own
    established convention, not the spec author's assumption — a document fully compliant with
    its own house style can still fail the gate.
CONFLICT section=Patterns id=P-11
  existing text: WHEN judging whether a guarded test assertion is reachable on a green run DO
    distinguish "unconditionally evaluated" from "conditional but taken by current fixtures" —
    the latter can silently stop firing on a future fixture change without the guard itself ever
    being touched; note which grade applies.
  proposed text: WHEN a task's intent names specific sites but a sibling/downstream task's
    verify asserts a wider property (e.g. zero findings tree-wide) DO check the intent covers
    every site that wider assertion needs — an under-scoped intent can fail every faithful
    execution against a wider check.
CONFLICT section=Gotchas id=G-11
  existing text: WHEN a diff replaces one exact-substring test assertion with several
    independent membership checks DO verify the split still requires adjacency — a wrong or
    fallback value containing every fragment separately still passes, so the assertion silently
    stops pinning the real output.
  proposed text: WHEN partitioning a mechanical gate's failing records into pre-existing versus
    introduced DO read its own selection rule first — a gate that only reports new-or-worsened
    items cannot emit an inherited-untouched-debt record, so that category is unrepresentable
    and a partition claiming it is wrong by construction.
CONFLICT section=Outcomes id=O-08
  existing text: WHEN a lead's send-back says the current grade is already acceptable DO write
    any revision as a new artifact, leaving the original unmodified — it is the record of the
    grade before new evidence moved it, and only survives untouched.
  proposed text: WHEN code diverges from a signed plan or spec DO determine the divergence's
    direction before recommending a remedy — code stricter or safer than the text is correctly
    closed by amending the text, while code weaker than the text is correctly closed by fixing
    the code.
```

I judge all four proposed texts stronger than the entries they would have displaced (`P-10`,
`P-11`, `G-11` narrower and more situational; `O-08` a workflow-hygiene note largely restated by
`harness-handoff`'s own "write a new artifact" rule). The judgment stands; the write does not.
Craft file left byte-unchanged — verified directly after the refusal.

## Harness defect — raised, not worked around

`harness-distill/SKILL.md`'s ops table documents `op: replace` and `op: drop` as legal
distillation operations against a full section. `expertise-merge.py apply`'s actual
implementation (`compute_union`, confirmed by source read and two live dry runs) is pure
union-add with conflict-on-collision only — it has no code path that removes or overwrites an
existing entry under any input. Every full-craft-section distillation for every agent, every
feature, hits this same wall: once a section reaches its cap, genuinely stronger material can
never displace weaker material through the sanctioned write route, contradicting the "distill IS
the curation step" design intent. Recording a workaround for this in Expertise would be exactly
the anti-pattern the rules warn against (a workaround outliving the fix), so it is not written
there — it is raised here as a blocking-for-future-distillations defect instead.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Repository tier gained two real entries (G-06, G-07); craft tier's three sections were already at cap and expertise-merge.py has no replace/drop capability at all, so four judged-stronger candidates were denied and are reported verbatim rather than worked around."
  entry_counts:
    craft:
      Patterns: { before: 15, after: 15, status: unchanged }
      Gotchas: { before: 15, after: 15, status: unchanged }
      Outcomes: { before: 10, after: 10, status: unchanged }
      Open: { before: 0, after: 0, status: "not used — see rationale in artifact" }
    repository:
      Patterns: { before: 0, after: 0, status: unchanged }
      Gotchas: { before: 5, after: 7, status: "G-06, G-07 added" }
      Outcomes: { before: 0, after: 0, status: unchanged }
      Open: { before: 0, after: 0, status: unchanged }
  accepted:
    - candidate: "relay (a): code_grade selection-rule fact"
      resulting_entry: "G-06 (repository tier, applied)"
    - candidate: "relay (c): B-5 mismatch direction determines remedy"
      resulting_entry: "would-be O-08 replacement (craft) — DENIED, exit 7, see artifact"
    - candidate: "self: run_pool.py OSError-swallowing gap (B-1 backlog)"
      resulting_entry: "G-07 (repository tier, applied)"
    - candidate: "self: verify-regex-vs-document-house-style (plan-panel cycle 2/3)"
      resulting_entry: "would-be P-10 replacement (craft) — DENIED, exit 7, see artifact"
    - candidate: "self: intent-narrower-than-downstream-verify (plan-panel cycle 4)"
      resulting_entry: "would-be P-11 replacement (craft) — DENIED, exit 7, see artifact"
    - candidate: "self (general form of relay a): mechanical gate selection-rule craft version"
      resulting_entry: "would-be G-11 replacement (craft) — DENIED, exit 7, see artifact"
  rejected:
    - candidate: "relay (b): panel's decomposition prediction vs. applied outcome"
      reason: "redundant with existing craft P-03 (verify a gate result against ground truth; a prediction is the same unverified-claim class)"
    - candidate: "self: fix for one blind spot opens an unnamed one in the same family (plan-panel c3, F2)"
      reason: "narrower restatement of existing P-07 / D-11-overclaim pattern; craft full, did not rank above the four accepted"
    - candidate: "self: ambiguity fails loud vs. fails silent, severity calibration (plan-panel c2)"
      reason: "softer/less rigorously evidenced than the four accepted candidates; craft full, ranked below the cut"
    - candidate: "self: completeness proven by derived run_set, not static files: list (plan-panel c5)"
      reason: "narrower — specific to this plan's derived-ownership idiom, not clearly portable"
    - candidate: "self: cross-plan staleness, a sibling plan's prose describes a pre-fix draft (plan-panel c1, G-01)"
      reason: "distinct from existing G-03 but weaker in general applicability; most repos don't run twin concurrent plans against one file"
  severity_max: n/a
  findings: 0
  must_fix: []
  spec_violations: []
  reviewed: none
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "expertise-merge.py apply implements pure union-add with conflict-on-collision only; harness-distill/SKILL.md documents op: replace and op: drop as legal ops. Once any section hits its DEC-145 cap, no proposal can ever displace a weaker entry through the sanctioned write route — verified by source read and two real, refused dry runs (exit 7 CONFLICT quoted in the artifact). This blocks curation for every agent's Expertise file, not just mine, and needs a fix to expertise-merge.py (or a documented curation-only mode) rather than a per-agent workaround.", blocking: true }
  files_touched:
    - ".harness/harness/expertise/harness-code-reviewer.md"
  expertise_update:
    - { op: add, target: "(new)", section: Gotchas, entry: "G-06: WHEN reading a code-grade.py report DO remember it only lists functions with no pre-image (new) or a worsened grade versus base — it never emits an 'inherited, unrelated, unchanged' record, so a partition claiming that shape for any listed record is definitionally wrong.", why: "closes relay candidate (a), repository-specific instantiation; applied, exit 0" }
    - { op: add, target: "(new)", section: Gotchas, entry: "G-07: WHEN reviewing run_pool.py's --mutation-check snapshot DO note _record's except OSError swallows every OSError, not only FileNotFoundError — removing a watched directory's execute bit mid-run hides any file created inside it from both snapshots (open backlog row, unresolved as of this build).", why: "durable fact about this repo's own tooling (B-1 backlog row); applied, exit 0" }
    - { op: replace, target: P-10, section: Patterns, entry: "WHEN a verify block's regex matches text by an assumed shape (heading separator, keyword form) DO test it against real samples from the target document's own established convention, not the spec author's assumption — a document fully compliant with its own house style can still fail the gate.", why: "DENIED exit 7 CONFLICT, craft Patterns at cap with no replace capability; see artifact for quoted denial" }
    - { op: replace, target: P-11, section: Patterns, entry: "WHEN a task's intent names specific sites but a sibling/downstream task's verify asserts a wider property (e.g. zero findings tree-wide) DO check the intent covers every site that wider assertion needs — an under-scoped intent can fail every faithful execution against a wider check.", why: "DENIED exit 7 CONFLICT, craft Patterns at cap with no replace capability; see artifact for quoted denial" }
    - { op: replace, target: G-11, section: Gotchas, entry: "WHEN partitioning a mechanical gate's failing records into pre-existing versus introduced DO read its own selection rule first — a gate that only reports new-or-worsened items cannot emit an inherited-untouched-debt record, so that category is unrepresentable and a partition claiming it is wrong by construction.", why: "DENIED exit 7 CONFLICT, craft Gotchas at cap with no replace capability; see artifact for quoted denial" }
    - { op: replace, target: O-08, section: Outcomes, entry: "WHEN code diverges from a signed plan or spec DO determine the divergence's direction before recommending a remedy — code stricter or safer than the text is correctly closed by amending the text, while code weaker than the text is correctly closed by fixing the code.", why: "DENIED exit 7 CONFLICT, craft Outcomes at cap with no replace capability; see artifact for quoted denial" }
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-code-reviewer-distill.md
```
