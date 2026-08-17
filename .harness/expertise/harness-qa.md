# Expertise — harness-qa

## Patterns (max 15)
- P-01: WHEN citing a test as SC evidence DO read the invocation and the assertion at that line,
  not the test's own label string — a label can name a different verb than the one actually
  invoked, and an unchecked label propagates as a false measurement up the review chain.
- P-02: WHEN scoping a negative assertion (e.g. "X was not closed") DO confirm it filters a
  structured call log to the specific operation, not a stdout substring check — a substring check
  can pass vacuously if unrelated output happens to contain the same text.
- P-03: WHEN a fixture's premise is "this code path is never reached" DO grep the function body
  directly for the call in question rather than trusting the fixture's own comment or name.
- P-04: WHEN a gate reports a single boolean like `matrix_ok: true` DO also state what fraction of
  the diff's tasks the matrix actually required a kind for — a gate can be matrix-correct while
  binding one task and asserting nothing about the rest; the denominator is the finding.
- P-05: WHEN crediting a test as coverage for a change DO confirm the test file is itself part of
  the diff, not pre-existing — only a test added or changed alongside the code demonstrates it
  exercises this change rather than merely happening to exist nearby.
- P-06: WHEN a change's deliverable is a removal DO re-run the same payload through the pre-change
  and post-change binaries, not just diff the source — a green suite proves only that nothing
  broke; re-running it over the same tree is reproducibility, not independent derivation of the
  deletion.
- P-07: WHEN a fixture asserts a pass/fail verdict DO assert its CONTENT — which entity, which
  message — not just a token's presence or an exit code. A different code path, or an
  over-permissive implementation, can produce the identical token, so presence-only assertions
  pass under both correct and incorrect code.
- P-08: WHEN a test asserts a live enumeration contains an expected member (e.g. `x in
  out.split()`) DO also assert the set's exact membership or count, not just presence — a
  membership check passes even when an extra, unauthorized member is also present, hiding an
  over-grant the equality check would have caught.
- P-09: WHEN judging whether an assertion is vacuous DO run a substring/mutation probe rather than
  reading the message text — reading generalizes from one message to a sibling whose wording
  differs just enough to already discriminate, producing a false vacuity claim.
- P-10: WHEN a verify clause does `git diff --quiet HEAD -- <files>` DO check for
  commit-before-verify ordering — committing moves HEAD to include the edit, making the
  comparison self-referential and passing regardless. Diff against the pinned baseline SHA,
  never HEAD.
- P-11: WHEN a verify does `grep -q <literal>` against a whole file DO check where the match
  actually lands — the substring can be satisfied by an unrelated section, so the check gates
  nothing about the section it names, even though it exits 0.
- P-12: WHEN a fake stands in for a call taking a selector argument (e.g. `fields`) DO assert the
  argument value at each call site, not just that the call happened — an argument-blind fake
  returns fixed data regardless, so dropping a field stays green while the real callee refuses
  the request.
- P-13: WHEN citing a test count that mixes plan-required and self-added cases DO break down the
  provenance — how many the plan requires versus how many are additions — rather than reporting
  one merged total, which overstates plan compliance.
- P-14: WHEN a required kind's `detect` glob matches a changed file DO also confirm that kind's
  `cmd` actually runs the file, via an explicit script list — a glob match without list membership
  means the kind reports satisfied while the binding suite never executes.
- P-15: WHEN the floor kind for a change type would leave part of the diff structurally unbound DO
  add the kind that actually executes those files, not just report the shortfall — a boolean like
  `matrix_ok` cannot itself show whether it passed on the floor or on an addition.

## Gotchas (max 15)
- G-01: WHEN proving a test runner's MISCONFIGURED exit path live by creating a stray
  `test-*.py` probe DO delete it and confirm with `git status --porcelain` before finishing — an
  explicit-list-plus-glob drift detector makes any leftover probe file exit 2 for every run after.
- G-02: WHEN raw test output contains alarming lines like "X is not importable... failing closed"
  DO check whether they're the suite's own deliberate simulation-case output (confirm the real
  dependency imports in the environment) before treating it as a live gap.
- G-03: WHEN a mode selector reads an environment variable rather than argv DO add a test case
  that explicitly sets that variable in the subprocess env — existing clean-env cases pass because
  the env happens to be clean, and prove nothing about the actual bypass axis.
- G-04: WHEN a task's own `verify:` command exercises only one script of a required kind DO also
  run the standing per-kind test command directly — a task-local pass can coexist with the kind
  itself never having been shown green across its full bucket.
- G-05: WHEN every gate on a diff is token- or phrase-based (grep/sweep) DO recognize none of
  them can confirm replacement prose is actually true — only that a token is present or absent.
  A false statement that satisfies every sweep is caught only by reading the prose directly.
- G-06: WHEN writing a caveat that claims you did NOT do something DO check it against what your
  own artifact's prose actually describes before including it — an inaccurate caveat, even one
  that errs toward modesty, is still a falsified record.
- G-07: WHEN a suite's own fixtures never invoke the real binary against production data DO run
  that binary directly against the live tree too — a green fixture suite is evidence only for the
  synthetic cases it built, not for the real-tree behavior a criterion actually requires.
- G-08: WHEN a dispatch flags an apparent discrepancy against a prior artifact (e.g. a commit
  missing from a range) DO check the prior segment's own note before filing it as a new defect —
  the earlier record may already explain what looks like a gap.
- G-09: WHEN caveating a success criterion as narrower than it looks (e.g. "form-checked only")
  DO re-check the criterion's own stated scope first — a hedge on a criterion met exactly as
  written is false doubt a later reader must spend a cycle re-clearing.
- G-10: WHEN a perturbation proof reddens a test over a walked or scanned set DO independently
  establish that set's size (e.g. instrument the walk) rather than trusting the test's report —
  a redden over an empty or near-empty set is not the same evidence as one over a substantial
  set.
- G-11: WHEN a dispatch claims the test-matrix floor is empty because every task shares one
  change_type DO re-derive each task's change_type from plan.yaml directly — dispatch framing is
  inherited, not measured, and one stale count can silently empty a real floor.

## Outcomes (max 10)
- O-01: WHEN an amendment deletes a fixture that was the sole source of some coverage and the loss
  is already ruled closed elsewhere DO still name it explicitly as a coverage gap in your gate
  note — visibility costs nothing and keeps a future reviewer from assuming coverage exists.
- O-02: WHEN a gate's trigger covers multiple tool types DO verify each route independently
  reaches the enforcement logic — a check can be logically correct yet unreachable on some routes
  (an early exit keyed on tool name), and a green run looks the same whether it fired or not.
- O-03: WHEN a finding is settled by reasoning rather than by mutation (e.g. an audit/
  author-nothing dispatch) DO label it explicitly as reasoned, not measured, in your digest — the
  tier above needs to know that assurance is weaker than a mutation-proven verdict.
- O-04: WHEN a criterion's literal wording is stricter than the artifact scoping it DO report two
  distinct findings — intent-satisfied and text-unmet — and route the verdict up, rather than
  recording the criterion as satisfied under your own reading.
- O-05: WHEN Phase 1's expected coverage list matches the built suite almost exactly DO check
  whether the plan pinned test cases by number or verbatim string before crediting the match to
  independent derivation — a prescriptive plan collapses the gap structurally, not a stronger
  anti-bias signal.
- O-06: WHEN a fix's soundness rests on two call sites staying in parity DO mutate each site
  independently, not just one — a combined PASS can hide that only one side was ever probed, and
  drift on the other side would pass unnoticed.
- O-07: WHEN a fix for a raised finding lands after the review round that raised it DO state
  plainly that only your own evidence has examined it — the independence a second reviewer
  provides was not applied, however strong your own proof is.

## Open (max 5)
