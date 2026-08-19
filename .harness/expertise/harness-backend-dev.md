# Expertise — harness-backend-dev

## Patterns (max 15)
- P-01: WHEN asserting an exception's VALUE slot, or comparing exception messages for inequality,
  DO pick a value absent from every compared message's fixed prose and reuse that SAME value
  across all cases — reused prose or a mismatched value lets the check pass without proving
  anything is wired.
- P-02: WHEN a task's listed verify steps are grep receipts plus a test suite that imports code
  standalone DO add a smoke check that actually imports/executes the changed module through its
  real call path — a broken import can leave every listed receipt green.
- P-03: WHEN asserting a call was removed via a log grep DO scope the grep to the payload, not the
  path — a path-only absence grep can vacuously "prove" removal while unrelated calls sharing that
  path remain.
- P-04: WHEN a test case's call could raise under a mutation DO wrap it in try/except and compare
  against a sentinel, never call it bare — an unguarded raise crashes the whole suite, silently
  skipping every later case, and the surviving output still looks like a clean partial pass.
- P-05: WHEN a function mutates its argument in place and also returns it DO never assert
  `fixture == result` as the proof of correctness — compare against an independent,
  distinctively-valued oracle instead. Comparing the fixture to itself cannot redden for any
  implementation, including one that silently drops a required field.
- P-06: WHEN the mandated pre-edit RED run passes on an untouched tree DO stop — a green RED means
  the premise is stale or the test is vacuous, not permission to proceed — and establish provenance
  from on-disk artifacts before writing or overwriting anything.
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
- P-13: WHEN production code was edited before RED was watched DO reconstruct RED: hash the file,
  restore its pre-edit state (`git show HEAD:<path>` if tracked, moved out of the tree if
  untracked), confirm the expected failures, restore, and re-verify the hash — never treat the
  lapse as harmless.
- P-14: WHEN a side-effecting write must not fire on an early-exit path DO place it as the
  unconditional last statement reached after every exit primitive (e.g. `sys.exit`), not behind a
  conditional guard enumerating exit cases — reaching that statement is itself the proof no early
  exit fired.
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
  team-config.yaml for broad top-level globs (e.g. the documentor's `docs/**`) before assuming a path
  resolves to NOBODY — pick a path outside every domain prefix instead.
- G-09: WHEN validating a live or side-effecting measurement against changed code DO confirm the
  loaded module's `__file__` resolves under the worktree being tested, not a stale main-checkout
  copy — a silently wrong root produces a plausible but false measurement.
- G-10: WHEN a fake HTTP double models a call by argv TEXT DO also assert its METHOD — list
  membership like `any(x in a for a in argv)` is blind to structure, so a correct call form and a
  broken one forcing the wrong verb can both satisfy it.
- G-11: WHEN an assertion searches a tool's stdout for a failure message DO first confirm which
  stream the tool actually writes it to — a check written against stdout is permanently blind to a
  message the tool writes to stderr, and its pass/fail is unrelated to what the tool actually does.
- G-12: WHEN an assertion slices a string between two marker substrings DO confirm both markers
  exist in the target first — if neither is present, the slice is silently empty and any search or
  comparison run over it can vacuously pass without inspecting real content.
- G-13: WHEN restoring a mutation probe mid-cycle, nothing committed yet, DO NOT use
  `git checkout -- <path>` as the restore step — it resets to HEAD, the pre-fix defect state, not
  the prior cycle's fix, and can silently revert still-live work. Restore by hand and re-verify
  the hash instead.
- G-14: WHEN a contract states a negative invariant over two conditions (no fallback on remote
  failure AND a local copy present) DO enumerate the 2x2 and name the untested cell — two fixtures
  covering disjoint cells leave it untested, and the code fails open under a matching mutation.
- G-15: WHEN a test double returns a payload DO shape it like the real wire response — encoding,
  line wrapping, envelope — not a synthetic clean value; a synthetic fixture leaves the decode
  path untested, so a real response differing in form ships as a live, unguarded defect.

## Outcomes (max 10)

## Open (max 5)
