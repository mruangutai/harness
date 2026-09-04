# Goal-check — FEAT-54 plan c0 vs stated intent

**Does this plan deliver the operator's stated intent? — Not yet: the mechanism covers all ten settled
answers, but four of them are bound by no success criterion, and the central promise (historical notes
untouched) is graded against the wrong git pair. Nothing the operator excluded leaks in.**

Authority: `.harness/notes/grilling-handoff-done-when-2026-09-02.md`. The grilling's `## Settled` block
(grilling:9-18) carries exactly the ten items the dispatch lists, in that order — no divergence.

## Per-settled-item coverage

| # | Settled item (grilling line) | REQ | SC | Task | Carried |
|---|---|---|---|---|---|
| a | standalone fifth section (:9) | REQ-01 | SC-01 | T-03, T-04, T-07, T-08 | yes |
| b | scope = the immediate `## Next` action, not phase/feature (:10) | REQ-01 | **none** | T-08 (template prose), T-10 | REQ+task only |
| c | one `Scope:` + 1–4 `Authority:`, no other prose (:11) | REQ-02 | SC-02 | T-01(c), T-02(2), T-03(c) | yes |
| d | AND semantics (:12) | REQ-03 | **none** | T-01(f), T-02, T-08 | REQ+task only |
| e | four bounded authority types; code location is not one (:13) | REQ-04 | SC-03 (types only) | T-01(d)(e), T-02(3), T-03(d) | partial — no SC for the unknown-type/code-location refusal |
| f | typed pointer syntax (:14) | REQ-05 | SC-03 | T-02(3), T-03(d) | yes |
| g | resolution enforced, not syntax-only (:15) | REQ-06 | SC-03 | T-02(3), T-03(d), T-06(e) | yes |
| h | historical valid; new/edited must comply (:16) | REQ-07 | SC-04, SC-06 | T-05, T-06, T-07 | yes, but SC-04 is mis-anchored (F-01) |
| i | 60-line cap kept, no per-section caps (:17) | REQ-08 | SC-05 (cap fires) | T-04, T-07, T-10 | partial — no SC over the "no per-section cap" negative |
| j | benchmark gated deterministically, rerun by hand (:18) | REQ-10 | SC-09 | T-09, D-04 | yes, but SC-09's evidence kind is wrong (F-03) |

Baseline re-derived, not trusted: `git ls-tree -r --name-only b7956fc4 -- .harness/harness/features`
yields exactly 141 `notes/handoff-*.md`; the worktree index also 141. REQ-07/D-01's number is sound.

## Out-of-scope leakage — five exclusions, zero leaks

1. Rewriting the historical corpus (grilling:26) — no task lists a note path; T-05 forbids globbing the
   tree (plan.yaml T-05 intent, :314-315); SC-04 asserts unchanged. Clean.
2. Raising the 60-line cap (:27) — T-04 keeps cap and message unchanged; SC-05. Clean.
3. Per-section caps (:28) — T-04 and T-10 both say add none. Clean.
4. Token/latency savings claims (:29) — BRIEF disclaims explicitly (BRIEF.md:12-13); T-09's probe prints
   fact coverage only. Clean.
5. Benchmark as a permanent automated gate (:30) — D-04/T-09: `locally_run`, absent from `test_matrix`
   and from both script arrays; SC-09 asserts the absence. Clean.

## Traceability — both directions, no orphans

REQ-01..REQ-10 each traced by ≥1 task; every `traces:` value exists. Nit: REQ-04 is traced only by
T-01/T-02 (module), though T-08 writes its prose into the template.

## Findings, by severity

- **F-01 (high) SC-04 does not prove UNTOUCHED, only "unchanged since the grade".** BRIEF.md:86 grades
  `git diff --name-only <review_sha> -- <glob>`, which compares `review_sha` to the tree. A commit inside
  this feature that rewrote all 141 notes satisfies it, as long as nothing changed afterwards. The
  operator's promise needs the base→`review_sha` range. The "for notes that existed before this feature"
  qualifier is a hand-filter with no command. T-06(g) only proves one check-state run mutates nothing.
- **F-02 (high) the feature's own build handoff notes will redden T-07's verify.** The baseline is frozen
  at `b7956fc4` (D-01), and T-05 deliberately excludes notes written during this build (T-05 intent
  :315). Notes written at build seams before T-04 lands escape the write gate; after T-07 they are
  non-baselined and carry no section, so INV-17 reports them and T-07's own verify
  (`! grep -qi 'done when'`, plan.yaml:371) fails for a planning reason no code fix addresses.
- **F-03 (medium) SC-08 contradicts T-07.** SC-08 requires `check-state.sh`'s handoff heading constants to
  state five (BRIEF.md:100-103); T-07 orders `HANDOFF_HEADINGS` left untouched with a separate constant
  (plan.yaml:386-387). That constant is a four-item list at `check-state.sh:1059` and is still read at
  :1199 and :1219. As written the criterion is unmeetable-by-design; narrow it or change T-07.
- **F-04 (medium) SC-09 names a kind that cannot carry it.** `evidence: unit` (BRIEF.md:108), but the
  probe-registration check lives in `run-unit-tests.sh` itself (:76-83) and its test file
  `test-run-unit-tests-kinds.py` is in INTEGRATION_SCRIPTS; no UNIT_SCRIPTS file asserts SC-09. Also "makes
  no model call" is not observable from a `--dry-run` exit 0 — nothing asserts network silence.
- **F-05 (medium) SC-07 has no author.** It demands a mutation experiment (remove the resolution entry
  point, both suites redden); no task among T-01..T-10 produces that evidence, so it arrives at qa as an
  unassigned experiment despite `verify: automated`.
- **F-06 (medium) four settled items are bound by no criterion**: (b) immediate-action scope, (d) AND
  semantics, (e) unknown-type/code-location refusal, (i) no per-section cap. Each has a test case in
  T-01/T-03 intent, but a criterion is what survives a task rewrite. (b) is unmechanizable — route it into
  SC-10's uat text, which today asks only about message quality and line budget (BRIEF.md:109-111).
- **F-07 (low) T-07's verify requires non-empty output** (`test -n "$out"`, plan.yaml:371): a silent
  check-state run fails a correct implementation.
- **F-08 (low) T-08's verify greps `! grep -rqi 'four sections'` over all of SKILL.md**; the only live
  occurrences are `SKILL.md:304`, `templates/HANDOFF.md:4`, `check-domain.sh:1523` (T-04) and
  `DECISIONS.md:3701` (T-10), so REQ-09's scope does match the task file union — the grep is merely
  broader than the claim.

## D-01..D-07 — decision or operator question

- **D-01 (frozen 141-path baseline): the plan's to make.** The operator settled the outcome ("untouched
  four-section handoffs remain valid", grilling:16); a frozen list versus a git-log discriminator is
  mechanism, and its stated failure mode (renamed note loses exemption ⇒ must comply) *matches* the same
  settled line rather than extending it. Advisory only: it writes this repo's history into a per-project
  config file.
- **D-02, D-03, D-05, D-06:** mechanism (one module, resolution semantics, message register, script array).
  Plan's.
- **D-04 (persist the probe as a registered `locally_run` kind): the plan's, narrowly.** The operator
  settled "rerun the comprehension benchmark during review" (grilling:18) — persisting it is the only way
  to make that rerunnable, and `locally_run` + absent from `test_matrix` is the existing
  `omp_session_accessor` precedent (harness.json:120-125). It does add a permanent artifact and registry
  entry the operator never named; disclose at signature, do not block.
- **D-07 (amend DEC-159 in place + new id):** mechanism, and required by REQ-09. Plan's.

## What would ship if executed exactly as written

Delivered: the fifth section demanded and shaped at write (T-03/T-04) and in the corpus scan (T-06/T-07),
real four-type pointer resolution in one module (T-01/T-02), the historical exemption (T-05), the docs and
decision record (T-08/T-10), the rerunnable probe (T-09). Missing: proof the 141 notes were untouched
*by this feature* (F-01); a green state gate over this feature's own notes (F-02); criteria for AND, for
the code-location refusal, for scope-is-the-immediate-action, and for the absence of per-section caps
(F-06); SC-07 and SC-09 evidence nobody authors (F-04, F-05). Present but unasked: the frozen baseline key
and the registered probe kind — both disclosed above, neither out of scope.
