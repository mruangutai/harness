# Observations — harness-pm — FEAT-21-features-layout-migration

- 2026-08-14 (cycle 1): The three blocking findings the reviewers added all shared one shape and
  none of them carried the literal my own sweeps were built around. `test-factory-cli.py:151-155`
  is a comma-joined tuple, `gh-sync.py:729` is a fixed three-level `..` climb, and
  `validate-feature-json.py:41` is a join over a root variable. My plan's per-row audits were
  correct and still missed all three, because every audit was a *literal* sweep and the detector's
  reader table is literal too. The sweep that would have found them is for path-depth arithmetic —
  chains of `..` inside a join, joins whose second element is `".harness"`, comma-joined tuples
  containing `"features"`. I folded a one-time run of it into T-09 so unit 4 inherits it.

- 2026-08-14 (cycle 1): Before shipping the three new discriminating verifies I ran each one against
  the tree at HEAD and confirmed it FAILS pre-fix. Two of the four assertions would otherwise have
  been non-discriminating: `test-factory-cli.py` carries no slash-form literal at all, so T-06's
  existing legacy-literal sweep passed before and after the fix and proved nothing. The cheap check
  is: run the verify's own predicate against the unfixed file and require a failure.

- 2026-08-14 (cycle 1): The tempting fix for the multi-repo key collision — segment-qualify
  `check-state.sh`'s dict keys — is a trap I only saw by reading every derivation site. Ten sites
  use `os.path.basename(os.path.dirname(p))`; one uses `os.path.basename(_fp)` and its next line is
  `plan_docs.get(_feat)`. Qualify one shape and not the other and the station-mirror loop `continue`s
  past every feature at exit 0. I deferred the keying and fixed only the label. Counting call sites
  was not enough; the shapes had to be compared.

- 2026-08-14 (cycle 1): `check-domain.sh --resolve` on a lane row's representative path is a
  10-second measurement and it changed nothing in my rows — but it converted `resolved_at: 62fef85`
  from an inference into a measurement, and it surfaced that a measured grant and the declared lane
  legitimately disagree wherever DEC-174's carve-out overrides. The row now records both, so a later
  reader does not read the disagreement as an error.

- 2026-08-14 (revision pass): A discriminating verify has a second, invisible cost: DEC-182's
  50-line budget counts `verify:` but NOT `intent:`. My first draft of the two region-anchored
  clauses took T-06 to 61 and T-10 to 60 machine-field lines and turned `check-plan-routes.py` from
  0 violations to 2. The fix was to strip every explanatory comment out of the clause and restate
  the anchoring rationale in `intent:`, which is where DEC-182 wants justification anyway. Both
  tasks now sit at 50/50 and 49/50 — no headroom left for either.

- 2026-08-14 (revision pass): I could not diff my own edits against git, because the whole FEAT-21
  directory is still untracked (`??`), so there was no baseline to subtract. I reconstructed the
  pre-edit budget by arithmetic instead. Next time, capture the checker's output BEFORE editing an
  untracked plan — the "it was green before" claim in a dispatch is not a baseline I can re-derive.

- 2026-08-14 (revision pass): The way to prove a shipped verify clause reds is to `safe_load` the
  plan, slice the clause out of the loaded `verify:` string by a content anchor, and run THAT — plus
  a synthetic "evasion" copy of the target file where only the sibling edits landed. Running a
  hand-typed prototype proves a clause like the shipped one, not the shipped one. It caught nothing
  this time, but it is the only version of the check that answers the question asked.

- 2026-08-14 (revision pass): A dated measurement comment drifts without lying. `tests.yml`'s
  "`git ls-files ...` returns 8" was true at eafc8ad and returns 19 at 62fef85 — nobody falsified
  anything, features simply accumulated. I nearly stamped "measured at 62fef85" onto the 8, which
  would have converted honest drift into a false dated claim. Re-run the quoted command before
  attaching a sha to its result.

- 2026-08-14 (goal-check): SC-10 asked a parity test to redden when EITHER of two renderings changes
  alone, and it only reddens on one side. Case 20 in `test-layout-migration.py` compares
  `layout_migration.render()` against a helper that MIRRORS `check-state.sh`'s INV-27 composition
  rather than executing it — a copy cannot detect drift in the thing it copies. Two mutations settled
  it in five minutes: dropping the last blamed reader on the module side reddened 4 assertions; the
  same drop inside `check-state.sh` left case 20 at 0 FAIL. A parity criterion needs one side to be
  the REAL artifact, or the composition needs a single owner both call sites import.

- 2026-08-14 (goal-check): My first mutation was ill-chosen and read as "the test is fine" — I
  filtered readers containing `check-domain`, but case 20 constructs synthetic reader paths, so the
  mutant never touched its fixtures while reddening two unrelated cases. A mutation that reddens
  OTHER cases but not the one under test is evidence the mutant missed, not evidence of coverage.
  Aim the mutant at the fixture the case actually builds.

- 2026-08-15 (goal-check cycle 2, SC-10 alone): "Reddens if EITHER rendering changes alone" is only
  answerable once you know which side consumes which function. `check-state.sh:1313-1323` calls
  `blame_text`/`cause_text` and assembles its own line; it never calls `render()`. That asymmetry is
  what makes both directions mutable at all — a module-level mutation moves BOTH sides together and
  stays green, which would have read as a blind spot if I had only mutated the shared owner. Read the
  consumer relationship before designing the mutation, or you measure the design instead of the test.

- 2026-08-15 (cycle 2): Five mutations, one per branch, was worth far more than one per side. M1 and M2
  hit the same gate file and reddened DIFFERENT assertion sets (1 vs 2) because MIXED and CANNOT_VERIFY
  are separate branches there. One mutation per *side* would have left a whole branch unprobed while
  reporting the side covered.

- 2026-08-15 (cycle 2): The test's own comment claimed an uncovered case was "covered by check-state's
  `case_x` and by `cause_text`'s unit coverage". Half true: `cause_text`'s wording is asserted
  (`test-layout-migration.py:266-274`), `case_x` never mentions it (`grep -n no-rows
  test-check-state.py` -> no hits). A comment naming its own compensating coverage is a claim to grep,
  not a mitigation to accept — even when the comment is honest about the gap existing.

- 2026-08-15 (cycle 2): `bash-write-guard.sh` blocked a plan's own approved `verify:` on `>"$u"`,
  reporting target "xx". My first diagnosis — "the variable was not resolved" — was wrong, and I only
  caught it because I greped the guard before filing it. `mask_quoted` (:155-179) blanks the contents
  of EVERY quoted span to `x`s on purpose, so any QUOTED redirect target blocks, literal or variable.
  Designed fail-closed behaviour, not a parsing bug. Two lessons: a `verify:` I author with a quoted
  redirect is unrunnable by the role that authored it (use an unquoted target), and a defect report
  filed on a plausible-sounding mechanism ages worse than no report.
