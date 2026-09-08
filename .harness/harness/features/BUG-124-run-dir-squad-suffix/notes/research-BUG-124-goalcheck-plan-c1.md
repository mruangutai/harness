# Goal-check c1 — BUG-124 revised plan vs the operator's stated intent

## Does this plan deliver the operator's stated intent?

**YES.** Both cycle-0 items are closed on evidence, the two intent clauses the c0 note flagged are
now either mechanised (the escape) or disclosed and accepted (the narrowing), and every SC-01..SC-09
has a producing task case. Three new items below are advisory, none blocking.

Intent source: **issue #124** (title, first sentence — "a dispatcher can name a run-dir path its
callee provably cannot write … the squad suffix must come last for the domain glob to match, and my
dispatch inverted it"; body cites FEAT-08 B-19,
`.harness/harness/features/FEAT-08-remove-cost-tracking/notes/ship-review-validate-close.md:197`),
plus the operator's plan-door clauses the c0 note enumerated (`research-BUG-124-goalcheck-plan-c0.md:40-48`).
The c0 coverage walk (5 REQ → 3 tasks, both directions, no orphan) still holds; the revision added
REQ-06 → T-02 + T-03 and SC-08/SC-09, and struck no clause.

## GOALCHECK-F1 — **CLOSED**, on my own measurement, not the revision's say-so

Detector re-run here (anchor = literal `.harness/`, repo/feature/slug class `[A-Za-z0-9._-]+`,
compliance = trailing `-product|-eng|-validator`) over `plan.yaml`, `BRIEF.md`, `STATE.md` and every
file under `runs/` and `notes/`:

- **`plan.yaml`: zero anchored run-dir references of any kind** — so no `verify:` or `intent:` string
  carried verbatim into a dispatch can be seen by the gate it installs. Both former sites are
  re-spelled: T-01 `verify:` (`plan.yaml:174`) and T-02 `verify:` (`plan.yaml:255`) hold
  `[.]harness/…/runs/eng-t01/digest.md` with a runtime `.replace("[.]", ".")`, and T-02's `intent:`
  states the convention it implements (`plan.yaml:264-272`).
- `BRIEF.md`: zero. `STATE.md`: one, compliant (`STATE.md:6`, `runs/panel-record-product`).
- **Positive control fired** — the same search reports three BAD sites in cycle-0 artifacts
  (`runs/goalcheck-plan-product/digest.md:11`, `runs/planpanel-validator/digest.md:19`,
  `notes/research-BUG-124-goalcheck-plan-c0.md:67`), so the clean plan result is not an empty search.
- The escape is **pinned by a unit assertion, not by convention**: `plan.yaml:174` asserts
  `run_dir_refs(q) == []` for the `[.]` form and `== [("harness","F","eng-t01")]` for the real anchor.
- Non-run-dir anchored paths in `intent:` (the receipt path, `plan.yaml:410-411`) carry no `/runs/`
  segment and are invisible to `run_dir_refs`. The three raw grant GLOBS in T-01's `intent:` WHY
  paragraph are anchored, but their slug begins `*`, outside the specified slug class — and even
  under a wider class each one matches its own grant, so neither reading refuses them.

## GOALCHECK-Q1 — operator's acceptance is fully recorded; all three confirmed

- **(a) YES** — `plan.yaml:29-34` (D-01 `choice`): callee-INDEPENDENT shape validation against the
  `/runs/` grant family, "and no ownership by the dispatched persona is checked". Non-vacuity reason
  retained (`:38-41`).
- **(b) YES** — `BRIEF.md:39-42`, inside `## Requirements`, headed "**Disclosed as detected by
  nothing:**".
- **(c) YES, and it names the case in full** — "a well-formed slug carrying a trailing squad suffix
  that is **not the callee's own** — an orchestrator dispatching `harness-eng-lead` and naming
  `runs/t01-product/digest.md`" (`BRIEF.md:40-42`). Not weaker than the accepted decision; it names
  the same instance the c0 note used and attributes it to D-01.

## SC-01..SC-09 — every id, with its producing case

| SC | verdict at plan time | producing case / evidence route |
|---|---|---|
| SC-01 | gradeable, met by plan (see GC1-N2) | T-02 (a) `plan.yaml:378-379` — real hook stdin seam, literal `eng-t01` |
| SC-02 | gradeable, met by plan | T-02 (b) `:380`; forms from `run_dir_forms` |
| SC-03 | gradeable, met by plan | T-02 (c)(d) `:381-383`; 48-of-48 baseline pinned at 6d969ed3, append-only |
| SC-04 | gradeable, met by plan | T-02 (f) `:386-388`, invented squad `oddsquad` |
| SC-05 | gradeable, met by plan | T-02 (i) `:399-402` (unloadable) and (e) `:384-385` (empty) |
| SC-06 | gradeable, met by plan | RED PROOF `:406-419`, receipt read at `review_sha` |
| SC-07 | gradeable, met by plan | T-02 (g) `:389-390`; D-04 places the check before the claim |
| SC-08 | gradeable, met by plan | T-02 (h) `:391-398` + the prescribed anchor-rewrite mutation `:415-416` |
| SC-09 | gradeable, met by plan | T-02 (e)+(i), mirror-image assertions (`:402-404`) |

None is unmet by the plan as drafted; none was weakened by the c1 revision. **SC-09 has a producing
task case** and **the SC-05/SC-09 pair is jointly satisfiable by T-02 as written**: (e) and (i) are
two separate appended cases against two different throwaway manifests (grant-less vs garbage bytes),
each asserting its own SKIPPED text present and the other's absent, and both are not-exit-2 cases, so
neither competes with the other's outcome. Two distinct texts are mandated at `plan.yaml:330-337`.

## New this cycle

- **GC1-N1 (low, no task needed).** Three pre-D-05 artifacts on disk carry raw anchored `eng-t01`
  paths (sites above). Once T-02 lands, a dispatch pasting that text verbatim is refused — recoverable
  in one step by re-spelling, and rewriting a run digest to fix it would falsify the record. No SC or
  task covers artifacts written before D-05, and none should; flagged so a builder is not surprised.
- **GC1-N2 (low, one-clause remedy, operator's call).** SC-01 now quotes the trigger path in the
  escape spelling (`BRIEF.md:65`). Read literally the criterion is self-refuting — a prompt naming
  `[.]harness/…/runs/eng-t01/digest.md` must NOT exit 2, that being the whole point of D-05. The
  `<feat>` placeholder already marks the line as illustrative and T-02 (a) is unambiguous, so it is
  gradeable; a parenthetical ("spelling illustrative; the case builds the real anchor") would remove
  the ambiguity at signature. I did not edit BRIEF.md.
- **GC1-N3 (advisory, unchanged from c0).** T-02's `verify:` (`plan.yaml:255`) still asserts the
  distinguishing string only, not `exit 2`; the exit assertion lives in case (a). Also SC-09's
  evidence is assertion-SHAPE, not a demonstrated red — the collapse-the-two-lines mutation is
  mandated in `intent:` (`:417-418`) and required by no criterion. Both accepted as written.

## Open questions

- Q1 (non-blocking, for the lead/panel): the five remedied panel findings still read
  `disposition: open` (`plan.yaml:107-140`), so the plan presents as carrying live med/low findings
  at signature. Transcription is not pm's in this batch.
- Q2 (non-blocking, operator, GC1-N2): add the one clarifying clause to SC-01, or accept as is?

Read-only pass. `BRIEF.md`, `plan.yaml`, `STATE.md` sha256 unchanged across it
(`d2625c89…`, `399154c5…`, `4e901e7d…` at HEAD ff2b749e); nothing committed, `approval: pending`,
`status: plan`.
