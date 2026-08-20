# Expertise — harness-backend-dev

## Patterns (max 15)
- P-01: WHEN asserting an exception's VALUE slot or a numeric/sentinel field DO assert the exact
  expected value, never a weaker existence/type check — a weaker check (e.g. `is not None`) can
  pass under the same mutant that breaks the real contract; pick a value absent from every
  compared case's fixed prose.
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
  predicting by name which checks redden before the run — an unpredicted redness is a FAIL unless
  it is a pre-existing check already coupled to the same path, which you verify, never assume.
- P-08: WHEN N things must be enumerated as pairwise-distinct (messages, states, branches) DO
  verify all C(N,2) pairwise comparisons exist, not just N-1 chained ones — a missing pair can be
  uncovered even though every other pair is asserted, and inequality is not transitive.
- P-09: WHEN mutating source to prove a test can fail DO record its sha256 before mutating,
  restore it, re-verify the hash matches, and confirm the file is absent from
  `git status --porcelain` — this is what makes a "no net change this cycle" claim checkable, not
  just asserted.
- P-10: WHEN scoping a mutation to prove one discriminator without detonating unrelated fixtures DO
  mutate the DATA the check depends on (a marker, a fixture value), not a GUARD shared by every
  caller — a shared-guard mutation routes every caller through the changed path, for a much larger
  blast radius.
- P-11: WHEN fixing a coverage hole in already-correct production code (no defect, nothing to add)
  DO prove it by mutation-testing the existing code, not by a RED/GREEN cycle on new production
  code — the Iron Law governs production-code order, and there is none to add for a test-only fix.
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
- P-15: WHEN a module-scope constant is computed once at import time DO add at least one
  unpatched-default test case that exercises it without monkeypatching first — if every other
  case patches the constant before use, a suite can stay fully green forever over a stale default
  nothing exercises.

## Gotchas (max 15)
- G-01: WHEN a coverage sweep or mutation produces zero hits/zero red checks DO treat that as
  inconclusive, not proof of absence — a fixture may spell the condition differently than your
  anchor terms, or an upstream contract may already foreclose the input shape; read the fixture or
  trace the access pattern.
- G-02: WHEN a test suite's docstring or label claims a specific contract DO treat it as an
  unverified claim and check the adjacent assertion actually matches it — a stale label can
  propagate across review tiers as if it were a measurement.
- G-04: WHEN a task's stated intent and its verify command assert opposite rules DO treat the
  verify command as what binds downstream behavior, not the intent prose — the executor acts on
  verify, so a contradiction there is a live defect even if the intent reads correctly.
- G-05: WHEN verifying a "clean on arrival"/no-pre-existing-drift claim DO diff against a fresh
  checkout of the cited commit, not the current working tree — a working tree already touched by
  later runs can launder a false baseline claim as true.
- G-06: WHEN a script's own source is grep-scanned for forbidden identifiers as a verify receipt DO
  avoid spelling those identifiers anywhere in the file, including comments or docstrings that
  explain the prohibition — the explanation text itself counts as a hit.
- G-07: WHEN a mutation runs across multiple test scripts DO treat only a clean, named-check FAIL
  as valid proof — a script that ABORTS instead (uncaught traceback, no per-check tally) proves
  nothing about the target check, even in the same run; report the abort separately, never as
  evidence.
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
- G-12: WHEN a dispatch or brief states an artifact is absent, or frames "the gap" to close DO
  verify directly against the live tree before acting — the claim is a snapshot, not a lock, and is
  likely stale on a re-dispatch or once a sibling run has landed the fix.
- G-13: WHEN restoring a mutation probe mid-cycle, nothing committed yet, DO NOT use
  `git checkout -- <path>` as the restore step — it resets to HEAD, the pre-fix defect state, not
  the prior cycle's fix, and can silently revert still-live work. Restore by hand and re-verify
  the hash instead.
- G-14: WHEN a contract states a negative invariant over two conditions (no fallback on remote
  failure AND a local copy present) DO enumerate the 2x2 and name the untested cell — two fixtures
  covering disjoint cells leave it untested, and the code fails open under a matching mutation.
- G-15: WHEN a test double returns a payload, or a spare/second queued result, DO shape it like the
  real wire response AND outcome class (success vs failure) — a synthetic payload leaves decode
  untested, and a spare failure can route a misrouted call down the wrong except, masking the check.
- G-16: WHEN a writeup states a count, or "zero FAIL lines" is offered as proof of a real green, DO
  re-run the count and check it rose by the expected delta — a silent zero-FAIL false green (e.g. a
  SyntaxError) looks identical to a genuine pass unless the count is checked.

## Outcomes (max 10)
- O-01: WHEN a true, low-risk finding needs a source edit after the gate that would review it has
  already passed DO backlog it, not apply — a correct finding's disposition turns on its place in
  the gate sequence, not on correctness alone.
- O-02: WHEN a task's dispatch or intent reads like a complete, detailed spec DO treat that
  completeness itself as a red flag — the more finished the spec looks, the stronger the pull to
  transcribe it straight into production code before a test exists. Write the failing test first
  regardless.
- O-03: WHEN a prior open_question sits unresolved across a scope-changing amendment DO re-check
  it against the NEW scope before re-raising it — a scope change can retroactively resolve a
  question raised under the old scope without anyone touching the file the question named.

## Open (max 5)
