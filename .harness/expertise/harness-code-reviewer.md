# Expertise — harness-code-reviewer

## Patterns (max 15)
- P-01: WHEN a test's label or comment describes what it covers DO verify that claim against the actual invocation and assertion at that line — a label is prose, not a measurement, and can advertise coverage that doesn't exist.
- P-02: WHEN hunting fail-open DO trace whether the exit happens before or after the state-write it guards — an exit inside the failing call blocks the write, turning the miss into a clean re-runnable skip rather than corruption.
- P-03: WHEN a durable record (commit message, decisions-doc entry) asserts a fact about the code — what a change did, or which consumers depend on what — DO verify it against the code it names, not the record itself — records assert intent, not ground truth.
- P-04: WHEN a PLAN task's `verify:` clause checks only for presence of new content on its named surface DO check whether sibling duplication-risk tasks pair that with an absence check elsewhere — a missing absence check is a structural tell for duplication.
- P-05: WHEN sweeping a deletion feature for removed terminology DO scan the whole repo, not just diff-touched files — a diff-scoped sweep can pass while live surfaces outside it (commands, docs, injected Expertise) still carry the term.
- P-06: WHEN a diff's deliverable is removal DO treat repo-wide sweep/grep evidence as the removal proof, not the test suite — a green suite only shows nothing broke, not that the target is gone.
- P-07: WHEN landed code deviates from signed amendment or plan text DO report the deviation regardless of whether it happens to be beneficial — ruling on the merits is a separate judgment from the duty to flag drift from what was signed.
- P-08: WHEN a reproduced count or figure disagrees with a plan's stated number DO check the feature's own disclosed caveats before reporting it as a novel finding — a discrepancy already disclosed is confirmation, not news.
- P-09: WHEN a success criterion states a precondition in argv/flag terms DO verify the code's mode-selection actually branches on that condition, not just that behavior matches under one representative environment — a criterion can pass every test yet be false as written if the mechanism reads a different signal.
- P-10: WHEN reviewing a guard that gates on tool_name, argv or an env var DO enumerate every OTHER route (different tool, inherited variable, alternate invocation) that reaches the same protected action, and check each is separately gated — correct logic on the tested route does not prove reachability-completeness.
- P-11: WHEN inheriting a peer's unreachability argument for a new call site DO check the argument's own preconditions before applying it — a mechanism that holds because of one site's structure does not transfer to a structurally different sibling without its own justification.
- P-12: WHEN judging whether a guarded test assertion is reachable on a green run DO distinguish "unconditionally evaluated" from "conditional but taken by current fixtures" — the latter can silently stop firing on a future fixture change without the guard itself ever being touched; note which grade applies.
- P-13: WHEN you establish a test assertion is reachable DO check separately whether a discriminating proof exists (a mutant or wrong-value test) that it can actually fail — reachability proves the check runs; only discrimination proves it can catch a wrong result. Flag whichever half is missing.
- P-14: WHEN a BRIEF or plan cites tests as evidence for a requirement DO check whether those tests exercise the real implementation or a mocked stand-in — a green suite that replaces the function under test proves only caller shape, not the requirement's behavior.

## Gotchas (max 15)
- G-01: WHEN a file you need to cite shows dirty in git status DO read it at the pinned SHA via `git show <sha>:<path>` and state which you read — a diff reviewed against pinned bytes can differ from the same path's working-tree state.
- G-02: WHEN a test asserts only a return/exit code DO check whether other code paths in the same function can produce that same code — a regression or reimplementation that satisfies the code via an unintended site still passes; assert a distinguishing message or output too.

## Outcomes (max 10)

## Open (max 5)
