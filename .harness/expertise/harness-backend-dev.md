# Expertise — harness-backend-dev

## Patterns (max 15)
- P-01: CANARY-7f3a9b — this line exists only to prove Expertise injection fires.
- P-02: WHEN a task's listed verify steps are grep receipts plus a test suite that imports code
  standalone DO add a smoke check that actually imports/executes the changed module through its
  real call path — a broken import can leave every listed receipt green.
- P-03: WHEN asserting a call was removed via a log grep DO scope the grep to the payload, not the
  path — a path-only absence grep can vacuously "prove" removal while unrelated calls sharing that
  path remain.
- P-04: WHEN a new gate binds every persona sharing a return contract DO check whether your own
  review's return would satisfy it — a PASS accepted only because the change hasn't landed yet is
  itself proof of the gap it is reviewing.
- P-05: WHEN raising a review finding about a structural gap DO phrase it as the gap itself, not a
  proposed fix — a finding named this way survived a later redirect that changed the whole fix
  mechanism, while a fix-shaped finding would not have.
- P-06: WHEN a task extracts text via an awk/sed line-range or tail-anchored match DO verify the
  anchor pattern occurs exactly once in the target file — a second match silently shifts the
  extracted range with no error.
- P-07: WHEN adding or fixing an assertion to close a vacuous-pass gap DO prove it with a mutant,
  predicting by name which checks redden before the run — and treat "a different check reddened
  instead" as a FAIL of the fix, not a pass.
- P-08: WHEN N things must be enumerated as pairwise-distinct (messages, states, branches) DO
  verify all C(N,2) pairwise comparisons exist, not just N-1 chained ones — a missing pair can be
  uncovered even though every other pair is asserted, and inequality is not transitive.
- P-09: WHEN mutating source to prove a test can fail DO record its sha256 before mutating,
  restore it, re-verify the hash matches, and confirm the file is absent from
  `git status --porcelain` — this is what makes a "no net change this cycle" claim checkable, not
  just asserted.
- P-10: WHEN a task's verify pins a claim to a specific section via a presence grep DO scope the
  grep to the extracted section text, not the whole file — a substring present elsewhere in the
  file lets the check pass while asserting nothing about the section it names.
- P-11: WHEN a task's intent cites a specific line as an existing assertion of old wording to
  update DO read that line first — it may be a docstring or unexecuted comment, not a check. If no
  executable path exercises it, add new RED-then-GREEN tests instead of a rewrite.
- P-12: WHEN naming a test assertion for a property DO name it only for what the assertion can
  actually distinguish — a call-tuple equality check named "no state scoping" asserts nothing about
  state and passes vacuously even after the real state-scoping property breaks.
- P-13: WHEN production code was edited before RED was watched DO disclose the lapse, then
  reconstruct RED as evidence: hash the edited file, swap in `git show HEAD:<path>` over it,
  confirm the expected failures, restore, and re-verify the hash — never treat it as harmless.
- P-14: WHEN asserting on recorded subprocess argv against this repo's gh-call fakes DO scope
  comparisons to argv[1:3], not argv[0:2] — argv[0] is always the gh binary, so a [0:2]-anchored
  assertion against a subcommand pair can never match and passes vacuously.
- P-15: WHEN measuring a live call's cost or side effects DO bracket it with a null-control read
  taken before the window and derive any independent reference value only after the window closes —
  deriving the reference inside the window risks contaminating the number being measured.

## Gotchas (max 15)
- G-01: The harness repo has no application source; src/** is empty here.
- G-02: WHEN a test suite's docstring or label claims a specific contract DO treat it as an
  unverified claim and check the adjacent assertion actually matches it — a stale label can
  propagate across review tiers as if it were a measurement.
- G-03: WHEN writing fixtures against the fake-gh test harness DO read its logging and
  issue-numbering behavior in `.claude/skills/harness/bin/test-gh-sync.py` first — assumptions
  about counters, log format, or which calls get logged fail loudly but still cost a debug cycle.
- G-04: WHEN a task's stated intent and its verify command assert opposite rules DO treat the
  verify command as what binds downstream behavior, not the intent prose — the executor acts on
  verify, so a contradiction there is a live defect even if the intent reads correctly.
- G-05: WHEN verifying a "clean on arrival"/no-pre-existing-drift claim DO diff against a fresh
  checkout of the cited commit, not the current working tree — a working tree already touched by
  later runs can launder a false baseline claim as true.
- G-06: WHEN a script's own source is grep-scanned for forbidden identifiers as a verify receipt DO
  avoid spelling those identifiers anywhere in the file, including comments or docstrings that
  explain the prohibition — the explanation text itself counts as a hit.
- G-07: WHEN a receipt requires zero grep hits for a banned pattern (e.g. `startswith`) DO expect it
  to fire on legitimate unrelated uses too (e.g. parsing subprocess output, not path matching) — the
  check is textual not semantic; rewrite to satisfy it even when the change is cosmetic.
- G-08: WHEN building a negative-path ("ungranted") fixture against the domain manifest DO check
  team-config.yaml for broad top-level globs (e.g. `docs/harness/**`) before assuming a path
  resolves to NOBODY — pick a path outside every domain prefix instead.
- G-09: WHEN validating a live or side-effecting measurement against changed code DO confirm the
  loaded module's `__file__` resolves under the worktree being tested, not a stale main-checkout
  copy — a silently wrong root produces a plausible but false measurement.

## Outcomes (max 10)

## Open (max 5)
