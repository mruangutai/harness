# Observations — harness-validator-lead — FEAT-20-migration-detector

- 2026-08-14: Review panel run `2026-08-14-1-validator`, four reviewers dispatched in one wave at
  `ea476fd`. Seeding `state.yaml` was BLOCKED: `check-domain.sh` rejected top-level keys `cycle` and
  `diff_base` as non-checkpoint (DEC-154), even though both values are a bare integer and a bare
  SHA. The allowlist is closed by NAME, not by value shape — `review_sha` passed, `diff_base` did
  not. Moved both into per-step `note:` strings.

- 2026-08-14: Lead-tier seam check that no single reviewer is positioned to make (P-06). The
  caller asked for BOTH exit-2 call sites verified. I read each at source rather than wait:
  - CI: `.github/workflows/tests.yml:233` ends the Layout gate step with `exit "$rc"`, `rc` being
    the detector's own code, so exit 2 fails the step. Lines 204-229 fail CLOSED on a missing
    summary line, a missing `examined` line, and any of the three zero counts.
  - Session entry: `check-state.sh:1266-1318` imports `layout_migration` in-process, appends a
    CANNOT RUN violation on import failure (`:1270`) and on a raising scan (`:1280`), and composes
    findings from the structured result — it never re-parses CLI text and never reads an exit code.
  Both hold. The seam is closed at `ea476fd`.

- 2026-08-14: The latent fail-open I found at that seam, which is a REGRESSION-PINNING gap rather
  than a live defect (P-08 — "the code does X" and "something holds it to X" are different claims).
  `check-state.sh:1302-1318` dispatches on `_srep.cause` through a four-branch `if/elif` chain with
  NO trailing `else`. `layout_migration.scan` (`:197-207`) sets exactly one of `no-rows`,
  `unreadable`, `neither`, `no-evidence` at every CANNOT_VERIFY construction site, so the chain is
  exhaustive TODAY and nothing falls through. But a fifth cause added by units 3-7 — or one branch
  deleted — makes that surface append NOTHING to `bad`, while the module still returns exit 2 that
  the session-entry call site never reads. Result: `check-state.sh` reports a clean tree over a
  surface the detector could not verify. Issue #148's shape at the call site, not in the verdict
  logic the feature hardened. [FIXED — see the 2026-08-14 entry under the detector-hygiene pass.]

- 2026-08-14: CONFIRMED that gap with the discriminating measurement rather than leaving it as
  reasoning (Evidence rule). `test-check-state.py` carries exactly five INV-27 cases, x.1-x.5
  (`:1647-1714`). Only ONE renders a cause: x.2 (`:1670`) asserts `"CANNOT VERIFY"` and
  `"[neither]"`. NOTHING exercises `unreadable`, `no-evidence` or `no-rows` at this call site. The
  NAMEABLE SURVIVING MUTATION: delete `elif _srep.cause == "no-rows":` at `check-state.sh:1316-1318`
  (or `unreadable` at `:1303`, or `no-evidence` at `:1313`). Unit case 16 still passes — it tests
  the MODULE's exit 2, not the invariant's rendering. All five x.N cases still pass. NOT gated: the
  code is correct at `ea476fd`, the operator signed the no-mutation-proof class as non-blocking, and
  CI still fails via `exit "$rc"` even with a branch deleted.

- 2026-08-14: qa segment gated at `11cb644`; this panel was pinned at `ea476fd`. The caller called
  them "the equivalent tree". I asked the panel's qa step to run
  `git diff --name-only 11cb644..ea476fd` so the digest could STATE the delta instead of relaying an
  equivalence claim I had not measured (Evidence rule; G-07). Measured answer: only `STATE.md`,
  `feature.json`, `notes/handoff-build.md`, `notes/qa-c0.md` — ZERO of the eight source files.

- 2026-08-14: PANEL CALIBRATION. ui-reviewer scoped out in ~39s on a measured file-extension census
  over all 22 diff files plus a `git ls-tree` check that no `DESIGN.md` exists — it verified the
  dispatch's framing instead of accepting it. Its `severity_max: n/a` is the sanctioned spelling for
  a scoped-out reviewer (G-06), not drift. code-reviewer was by far the longest (~11.5 min vs ~5-6
  for qa and security) and produced the only executed perturbation; the runtime bought something.

- 2026-08-14: I MIS-NARRATED A MEMBER'S CONDUCT IN A SIGNED ARTIFACT, and the advisor caught it, not
  me. I wrote that security "filed it `info` as a pre-existing nit" about the false x.5 comment.
  Security's artifact says the opposite in as many words: "Info-level, IN THE DIFF, worth a one-line
  correction whenever this area is next touched" (`:74-75`). It scoped the item correctly; only its
  REMEDY framing (defer-until-touched) underweighted a false safety claim newly introduced. My
  re-rating to low survives on that narrower ground, but the sentence as first written was false
  about a member — rule 15, and precisely the G-09 failure where a relayed digest makes a member
  spend its distillation slot rebutting my error. ROOT CAUSE: I read security's artifact BEFORE its
  digest arrived, formed the "pre-existing" reading from its Q2 one-liner, and never re-read the
  artifact body when I wrote the finding up. Having the artifact open earlier is not the same as
  having it open AT THE SENTENCE (G-07's actual claim).

- 2026-08-14: qa's panel note narrates "cases 1-18 (18 required by plan, plus cases 17-18 added)",
  self-contradictory and overstating the plan: T-01 specifies cases 1-16 and T-02 adds the
  exit-code-contract case, so 17 are plan-required and 1 is extra. Its ANCHORS are correct; only the
  parenthetical count is loose. Info, NOT a send-back — cosmetic, visible from the same sentence,
  and looping a minor nit to max_cycles is a process defect, not diligence.

- 2026-08-14: code-reviewer's line anchors drift 3-8 lines from source throughout (it cites
  `reader_files` at `:199`, actual `:195`; `_evidence` returns at `~146/~156`, actual `:143/:152`),
  though it marked some approximate with a tilde and every MECHANISM I spot-checked was exactly
  right. P-01 earned its keep: I published the anchors I measured, not the ones it reported.

## Pre-merge pass, run `2026-08-14-4-validator` @ `045dcd9`

- 2026-08-14: DISPATCH-GUARD BLOCKED MY OWN WAVE. I passed `model: sonnet` on all four Agent calls
  and `dispatch-guard.sh` rejected every one, citing DEC-152/155 — a model pin is org design, not a
  dispatch option. The guard was right and cost one wave of latency, nothing else. I had no reason
  to set it; I added it reflexively while composing four prompts at once. Re-dispatched verbatim
  minus the parameter and all four launched.

- 2026-08-14: THE SHA GAP NOBODY IN THE SHIP LOOP COULD HAVE CLOSED. The panel and every review
  artifact are pinned at `ea476fd`; the operator's merge candidate is `045dcd9`. The blocking qa
  gate is pinned earlier still, at `11cb644` (`runs/qa-gate-validator/digest.md:1`). Three
  different SHAs carry the three pieces of assurance. The transitive chain that makes them apply to
  the merge candidate is assembled from two INDEPENDENT member measurements, one per link, and no
  member holds both:
  - `11cb644..ea476fd` — zero of the 8 source files (panel qa, `review-harness-qa-c0.md:45`)
  - `ea476fd..045dcd9` — zero of the 8 source files (premerge security,
    `review-harness-security-reviewer-premerge.md:7-14`; 22 files, all `.harness/expertise/*` and
    FEAT-20 bookkeeping)
  Therefore the 8-file source tree at `045dcd9` is byte-identical to `11cb644`, and the blocking
  gate's green plus every panel finding transfer to the merge candidate. This is the synthesis the
  lead tier exists for: each member measured one link and neither could state the conclusion.

- 2026-08-14: SEAM IN THE PRIOR PANEL'S OWN COVERAGE (P-06, applied to a panel rather than to code).
  `review-harness-code-reviewer-c0.md`'s headline claims "spec compliance clean across all 8 files",
  but its Stage 1 enumerates SEVEN: `layout_migration.py`, `test-layout-migration.py`,
  `check-state.sh`, `test-check-state.py`, `tests.yml`, `DECISIONS.md`, `DECISIONS-INDEX.md`.
  `run-unit-tests.sh` — the registration file that decides whether the new test file runs at all,
  i.e. this feature's own subject — is absent, confirmed by grep over the whole notes directory.
  It is NOT uncovered in the panel's union: security described it (`review-harness-security-reviewer-c0.md:88`,
  "one-line array addition (test registration)") and qa executed through it with both registration
  greps firing. So the defect is a MIS-STATED SCOPE CLAIM in one member's headline, not a hole —
  which is exactly the distinction that stops it becoming a must_fix. Check the enumeration against
  the count whenever a member's headline asserts "all N files".

## Detector-hygiene pass, run `2026-08-14-5-validator` @ `a714bd0` (PR #385) — the FAIL

- 2026-08-14: A GREEN SUITE HID A 1134-LINE DUPLICATE PASTE, and the thing that made it visible was
  reading the code the orientation agent had already summarised. `test-check-state.py` at `a714bd0`
  defines 17 top-level names TWICE — `case_m`(528/1662) … `case_x`(1585/2719). Python binds the
  last, so the executing `case_x` is the one WITHOUT the `layout_fixtures` import: the #382
  consolidation the commit is named for never took effect in this file. 84 `ok`, exit 0. No gate in
  the repo detects a shadowed duplicate definition — `run-unit-tests.sh`'s drift detector checks
  file REGISTRATION, never in-file redefinition.

- 2026-08-14: THE ORIENTATION SUMMARY WAS RIGHT ABOUT THE DEFECT AND WRONG ABOUT THE REMEDY, and
  only opening the lines separated the two. It reported the first `case_x` (`:1585`) as "the
  refactored one" and offered "keep copy 1, keep #382; or keep copy 2, keep #383" as a symmetric
  choice. Reading `:1585-1659` shows copy 1's `case_x` is a CHIMERA — INV-27 docstring plus the
  `lf`/`FLEET_TEXT`/`STUBS` preamble (`:1595-1599`), then the body of `case_l` (assertions `(l1)`-`(l8)`,
  the INV-22 run-budget case that also lives intact at `:456-525`). `STUBS`, `FLEET_TEXT` and
  `MARKER_REL` are bound and never read; `results = []` is assigned twice (`:1594`, `:1614`). So
  there is no salvageable refactored INV-27 case to keep, and "delete copy 2" would delete INV-27
  coverage outright. G-07 generalises past artifacts: a SUMMARY of code is a hypothesis about the
  code, including one I commissioned myself.

- 2026-08-14: The cut is clean and worth recording as coordinates rather than prose: `case_l` ends
  at `:525`, the shadow region is exactly `[528, 1661]`, and the live region is `[1662, 2899]`
  (qa's per-pair SHA-256 measurement; 16 of 17 pairs byte-identical, only `case_x` differing).
  Deleting `[528, 1661]` restores the intended file; #382 then still has to be applied by hand to
  the surviving `case_x` at what is currently `:2719`. The swap is mechanical: I byte-compared all
  seven inline stubs at `:2732-2747` against `layout_fixtures.STUB[rel]["legacy"]` and they are
  identical.

- 2026-08-14: MY OWN OBSERVATIONS LOG CONTAMINATED A MEMBER'S INDEPENDENCE, which I did not
  anticipate and which is structural rather than a one-off. I appended the duplication finding to
  THIS FILE mid-run, while qa was still investigating. It is a repo path and qa holds `Read`, so qa
  found it and wrote in its artifact that my diagnosis "independently corroborated" its own — citing
  the log by path and noting the working tree had gained a third modification mid-run. The log is
  never INJECTED into a spawn, but it is READABLE by every member with source access, so a lead who
  observes mid-run is publishing to the panel it is about to assess. qa's per-pair SHA-256 hashes
  and its `3c75aa6` reproduction were genuinely new; its COORDINATES were not. Whenever a member
  claims independent corroboration of a finding I have already written down, check what my own log
  already held before relaying the claim.

- 2026-08-14: I ALMOST SIGNED VERDICTS FOR MEMBERS THAT NEVER SPOKE. My first `state.yaml` for this
  run recorded `status: complete, verdict: PASS, severity_max: info` for security and ui as "lead
  scope-out" entries, before either had been spawned. My reasoning was that a non-UI, non-auth diff
  makes both spawns waste — which may even be true — but the record would have attributed a verdict
  to an agent that never ran, in a file a successor reads as fact. Rule 15 is not only about
  softening failures; inventing a PASS is the same defect with a friendlier face. I dispatched both
  instead, and BOTH EARNED IT: security scoped IN and traced 17 subprocess sites, and ui produced
  the only finding nobody else framed. The cheap honest option and the informative one were the same
  option. A scope-out is the MEMBER's finding to return, never the lead's to record on its behalf.

- 2026-08-14: THE DECISIVE FINDING ARRIVED BY TWO ROUTES AT ONCE, and neither route alone would have
  gated. I derived from the branch order in `layout_migration.scan` (`:235` undeclared-segment and
  `:245` no-evidence both fire BEFORE the `both`-reader test at `:248`) that DEC-194's amended
  sentence overclaims — which I was going to file as a LOW advisory about doc wording, since the
  three cause-wordings were byte-unchanged by the diff. code-reviewer independently constructed a
  `SurfaceReport(cause="undeclared-segment")` and observed `blame()` return non-empty, filing it as a
  CODE divergence. Put together they are one high finding: `render()` (`layout_migration.py:318-320`)
  composes blame for EVERY `CANNOT_VERIFY` cause while `check-state.sh:_cv_wording` (`:1295-1312`)
  calls it in only two of five lambdas, so CI and session entry still name different readers — the
  exact claim #379 says it closed. THE LESSON: a doc-wording advisory of mine and a code finding of a
  member can be the same defect seen from two ends, and the merge upgrades both. I nearly filed mine
  as low because the DIFF did not touch those lines — "unchanged by this diff" is an argument about
  provenance, never about whether the claim being shipped is true.

- 2026-08-14: A FIX ORDER THAT NO MEMBER COULD HAVE SET. M-3 (restore DEC-194 and append amendment 2)
  must happen AFTER M-1 (resolve the blame divergence), because the amendment's text has to state the
  settled behaviour and the current narrowing is false whichever way M-1 resolves. code-reviewer
  filed both and ordered neither; ordering is only visible once you hold the doc finding and the code
  finding together.

- 2026-08-14: THE VACUITY QUESTION PAID OFF ON `case_20` (G-03). `layout_fixtures.py`'s docstring
  credits its own paren balance for not tripping `test-check-plan-routes.py` case_20. The parens ARE
  balanced — I checked all seven pairs — but that is not what protects it. case_20 scans every
  `.py`/`.sh` in `bin/` excluding only `test-*` (`:1167-1169`), so the file IS in scope; it survives
  because it carries none of the `PREDICATES` tokens at `:1120-1121`, leaving `probes` empty at
  `:1180`. The docstring therefore hands units 3-7 the WRONG invariant to preserve, and the stubs are
  literal fragments of the very reader files case_20 audits. "Does not trip the gate" and "the reason
  the author gives for not tripping it" are separate claims, and only the second is what a
  maintainer will act on.

- 2026-08-14: #367 IS FIXED and the dispatch's accepted-residual list is stale on it.
  `check-state.sh:1313-1316` is now a closed cause table with a loud `unrecognised cause` fallback,
  replacing the else-less `if/elif` chain I filed at `ea476fd`. Worth checking a handed-down residual
  list against source before briefing a panel to ignore its items — briefing a reviewer past a FIXED
  defect costs nothing, but briefing it past a defect that has MOVED costs the finding.

## Confirmation pass, run `2026-08-14-6-validator` @ `6296149` (PR #385) — the PASS

- 2026-08-14: THE FIX RE-CREATED THE EXACT TRAP THAT MADE THE FAIL HARD, and the only reason I did
  not fall into it twice is that I had recorded the trap's shape. At `6296149` the surviving
  `case_x` sits at `:1585` — the SAME line the chimera occupied at `a714bd0`, because deleting the
  1134-line shadow moved the real function up to where the fake one had been — and it opens with the
  identical INV-27 docstring and `lf` preamble. Every surface sign I checked first (one def per
  name, imports `layout_fixtures`, uses `lm.MARKER`) was ALSO true of the chimera. What separates
  them is only the BODY: `:1601-1644` is `build(tmp, marker, overrides, evidence)` and the x.N
  assertions, where the chimera had `build(tmp, n, declared, budget)` and `(l1)`-`(l8)`. GENERAL
  RULE: when a fix deletes a duplicate, the survivor inherits the deleted one's line numbers, so
  every anchor in the FAIL digest silently re-points. Verify the body, never the header, and never
  the anchor.

- 2026-08-14: THE ONE PROBE THAT CONVERTED "GREEN" BACK INTO EVIDENCE. In the FAIL round I ruled the
  green suite non-evidence because the shadow meant it passed identically with two copies — a
  correct ruling that left an obligation nobody would otherwise have discharged. I put the
  discharge in qa's dispatch as an explicit mutation requirement, and qa mutated
  `lf.STUB[".harness/team-config.yaml"]["legacy"]` in a scratch export, saw `test-check-state.py`
  go to exit 1 with subcase `(x.3)` failing, restored it, and returned to exit 0 — asserting both
  that the mutation applied and that the suite ran. Without that step this PASS would have rested
  on the same green I had already ruled worthless. A ruling that green is non-evidence creates a
  debt that must be named in the NEXT dispatch or it is silently forgiven.

- 2026-08-14: RAISING THE REPRODUCTION BAR BETWEEN ROUNDS PAID. c1 proved M-1 with a synthetic
  `SurfaceReport`; I asked for the same probe again and code-reviewer instead built a real tree and
  ran the real `check-state.sh`, showing both sites naming `check-state.sh [migrated]`. "The
  function returns the same list" and "the gate an operator runs prints the same readers" are
  different claims, and only the second is what the merge decision needs. Similarly, M-3's
  restoration went from my line-level comparison against the c1 diff's recorded `-` lines to
  code-reviewer's SHA-256 of the whole entry body, and the index from a read of row 212 to a
  `gen-decisions-index.py --stdout | diff` round-trip that also explained the tag reorder I had
  noticed and could not account for.

- 2026-08-14: I RE-RANKED MY OWN PRIOR ADVISORY UPWARD, WHICH IS A MOVE I HAD NOT MADE BEFORE. In c1
  I rated A-2 (nothing pins the blame policy) LOW, citing the operator's standing precedent for the
  correct-today-not-pinned class. At c2 the same finding is unchanged in content but the evidence
  around it moved: the seam has now produced TWO divergences in one day, and the M-1 fix CHANGED the
  policy without adding a test. I raised it to med. A precedent covers a class of finding, not a
  specific seam's track record — when a seam empirically breaks twice, its own history outranks the
  class precedent, and re-rating an advisory I previously filed is not inconsistency.

- 2026-08-14: PANEL CALIBRATION, c2. ui refused the comfortable answer: a fix landed adjacent to its
  c1 med, and it executed both paths, found the `neither`-cause string byte-identical, and returned
  PRESERVED with a concrete one-line alternative — then improved that alternative on its second look
  by finding the sibling MIXED branch at `check-state.sh:1328-1329` already uses `"; readers {_rd}"`,
  which turns "invented wording" into "the file's own convention". Its artifact and digest disagree
  on a file count (14 vs 16), so I cited no count. The `files_touched: []` defect MOVED rather than
  went away — security fixed it after three rounds, code-reviewer committed it this round.
  Security's and qa's duplicate counts differed (14 vs 17) and were NOT in conflict: `case_*` only
  versus all top-level defs, 14 + 3 helpers = 17. Resolving that at my tier is cheaper than sending
  either back.
