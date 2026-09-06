SIMPLIFICATION angle — `claim_set_refusal` (harness_boundary.py)

## BLUF

**The three-exit branching is minimal.** No collapse is available that preserves the pinned
semantics. Each of the three exits is forced by a distinct REQ and pinned by a distinct assertion
that specifically checks the OTHER exits' text is absent from it — i.e. the tests actively prove
the three messages must differ, not just that they happen to.

## Mapping: exit -> forcing requirement -> pinning assertion

| Exit | Forces | Pinning anchor |
|---|---|---|
| (a) unreadable-registries | REQ-05 "bound-or-not is unanswerable is also refused" / SC-10, SC-12 | `tests/integration/test-check-domain.py:3963` (`"claim registries are unreadable"`) and `:3965` (stderr names `reg.REGISTRY_REL`, the file-to-repair requirement) |
| (b) control-plane expertise carve-out | REQ-06 (sanctioned `expertise-merge.py apply` advice, never "write it from a bound worktree") | `tests/unit/test-harness-boundary.py:457-459` (asserts `"expertise-merge.py apply" in expertise_refusal`) plus `tests/integration/test-bash-write-guard.py:1154-1156` (asserts `"write it from a bound worktree" not in response.stderr`) |
| (c) general case | REQ-05 "bound but unplaceable is refused" (names the worktrees held + the destination's proper home) | `tests/unit/test-harness-boundary.py:449-451` (asserts every claim member + destination + `/tmp/main` home all present) |

## Why no two of the three fold together

- (a) cannot fold into (c): SC-12 requires the unreadable-registry message to fire even when the
  agent's OWN claim is readable and proves a worktree — that is a fundamentally different input
  (an `unreadable_paths` set with no bearing on `claim_set` membership) from (c)'s "claim set is
  known but doesn't cover the destination." Collapsing loses the SC-10 "names the unreadable file"
  requirement, which (c)'s message has no field for.
- (b) cannot fold into (c) (the instinct flagged in the dispatch): REQ-06 is not a wording
  preference, it's a correctness requirement — (c)'s advice ("write it from a bound worktree") is
  actively WRONG for a `.harness/expertise/` destination, which is legitimately outside every
  worktree by design (control-plane route, not a relocation target). The test at
  `test-bash-write-guard.py:1154-1156` asserts the wrong phrase is ABSENT specifically from this
  case, proving the two messages must diverge, not just may.
- (a) cannot fold into (b): unrelated triggers (unreadable JSON vs. an expertise-path destination)
  with no shared condition to test against.

**Explicit note per dispatch instruction**: branch (b)'s `python3 expertise-merge.py apply` advice
and the absence of the phrase "write it from a bound worktree" from its message are pinned by
REQ-06, not a stylistic choice available to fold into the general-case message.

## Comment-narration scan

The single new comment left behind (`select_base`, replacing the old inline `inside()` closure)
reads as a present-fact statement ("All containment decisions use the module-level primitive
shared with `claim_worktrees`, so path membership cannot drift...") — not change-narration
("now we also...", "this was added because..."). No finding here.

## Recommendation

Nothing found. The three exits are each independently forced and independently pinned; collapsing
any pair loses an asserted, requirement-traced behavior. No recommendation.
