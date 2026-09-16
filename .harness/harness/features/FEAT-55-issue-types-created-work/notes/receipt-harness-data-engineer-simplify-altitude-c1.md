# SIMPLIFY · Angle ALTITUDE · harness-data-engineer

BLUF: 2 ALTITUDE findings, 2 recommended `fold-in`. No correctness (D-20 key-presence) hits. No
decision questions — D-21's schema duplication is settled and out of scope.

## Findings

### F-1 — `type_for_nature` re-derives `_resolve`'s rule instead of calling it, and the copy has already drifted
- file: `.claude/skills/harness/bin/gh_issue_types.py:66-76`
- summary: `_resolve(name, table, overrides)` (lines 49-59) is the one extracted, authoritative
  statement of "look up `name` in `table`, raise `UnknownWorkNature` if absent, apply a legal
  string override, else return the default." `type_for_change_type` calls it (line 63).
  `type_for_nature` (66-76) does not — it reimplements the same four steps inline.
- concrete cost: the reimplementation has already diverged from truth: its raised message reads
  `f"{nature!r} is not a known change_type, so no issue type is mapped for it - add it to
  DEFAULT_TYPE_BY_CHANGE_TYPE or fix the plan"` — copy-pasted from `_resolve`'s change_type
  wording, wrong on both nouns for a nature lookup (line 70). Whoever reads that exception message
  while debugging a backlog-item nature typo is pointed at the wrong table and the wrong plan
  field. Every future edit to the resolve rule (e.g. a stricter override-validity check) has two
  call sites to remember, and only one is discoverable by reading `_resolve`'s own callers.
- alternative: `type_for_nature` calls `_resolve(nature, DEFAULT_TYPE_BY_NATURE, overrides)`
  exactly as `type_for_change_type` does; delete the inline duplicate. One correct message, one
  rule, one place a future change has to land.
- severity: low
- apply: yes — fold-in (five-line body replaced by one call; behavior-preserving except the
  error message, which becomes *more* correct)
- **fold-in**

### F-2 — D-20's legal-`typed`-value set is validated on read in one caller, not the other
- file: `.claude/skills/harness/bin/factory_decompose.py:153-159` vs
  `.claude/skills/harness/bin/gh-sync.py:568-569`
- summary: `factory_decompose.py`'s `read_factory` filters every loaded `typed` entry through
  `v is True or (isinstance(v, str) and v in ("created", "adopted"))` before admitting it — an
  explicit, inline restatement of D-20's legal-value set. `gh-sync.py`'s `load_recorded` does the
  parallel job for `github.typed` and does not filter per-entry at all: `dict(typed) if
  isinstance(typed, dict) else {}` (line 569) admits any key/value pair verbatim.
- concrete cost: the same D-20 rule — "legal typed values are exactly `True`, `"created"`,
  `"adopted"`" — is spelled out once in `factory_decompose.py` and not spelled out at all in
  `gh-sync.py`; there is no third, shared place either reader can point to. Today this is inert
  (every downstream read is a positive `== "created"` / `is True` equality, so a stray or corrupt
  value degrades safely to "not needing type" either way — no live bug), but the two readers of
  one shared receipt shape disagree on whether malformed input is worth catching, and a future
  change to either file (e.g. a `!=` comparison, or surfacing an illegal value to the operator)
  inherits that asymmetry silently.
- alternative: move the predicate into `gh_issue_types.py` (e.g. `legal_typed_value(v)` or a
  `filter_typed(raw)` helper) next to the D-18 role resolvers it already owns, and have both
  `load_recorded` and `read_factory` call it — one authoritative spelling of "what counts as a
  legal provenance value" instead of one caller writing it and the other omitting it.
- severity: low (no live misbehavior; drift risk only)
- apply: yes — fold-in (small, mechanical, behavior-preserving: `gh-sync.py` gains the filtering
  `factory_decompose.py` already has, expressed through the same shared call)
- **fold-in**

## What I checked and did NOT flag
- The schema's two `typed` mappings (`feature-schema.json:86-95,116-125`) DO constrain the
  four-state value with `oneOf` (`enum: ["created","adopted"]` / `const: true`) — this is not "an
  optional mapping that validates nothing." The duplication of that schema block across the
  `github` and `factory` objects is D-21, signed — not re-raised.
- `detect_issue_types`/`apply_issue_type` exist separately in `gh-sync.py` (912-925, 980-986) and
  `factory_gh.py` (215-229): a real duplication candidate on its face, but `gh_issue_types.py`'s
  own module docstring names the reason and names it correctly — `gh-sync.py` SKIPs on an
  environmental failure, `factory_gh.py` raises `GhError`; a shared runner would have to pick one
  failure semantic for both callers. Accepted residual, compensating control (the docstring
  itself) already named. Right call — leave.
- `backlog-issues.json`'s two-state (`False`/`True`) `typed` field (`gh-sync.py:1663-1706`) is a
  structurally different, simpler shape than the three-string-plus-absence rule elsewhere
  (backlog items are never adopted, so there is no third state to represent). The docstring at
  `gh-sync.py:1572-1576` explicitly names the accepted residual — "this file has no legacy caller
  and no schema of its own" — as a deliberate, D-13-scoped tradeoff, not an oversight. Not a
  altitude violation of the D-20 rule; it is a different, narrower rule for a different receipt.
  Leave.
- `gh_issue_types.py` itself stays pure (no subprocess/network per its own docstring) and both
  callers respect that boundary — no caller-specific logic has leaked into it, and nothing
  caller-specific has been pushed into it either.

## D-20 four-state rule: one authoritative statement, or several?
**Several, with one gap (F-2).** The *semantics* (four states, absence-means-unknown,
only-"created"-is-backfilled) are stated in prose once, authoritatively, in D-20 itself and echoed
faithfully in code comments at `gh-sync.py:989-994`, `gh-sync.py:1043-1044`, and
`factory_decompose.py:390-398,431-434`. But the *legal-value check* — which is the mechanical
enforcement of that same rule — is spelled twice in code (`factory_decompose.py:158` inline
tuple, `feature-schema.json` oneOf enum x2 under D-21) and once by omission (`gh-sync.py`'s
`load_recorded` does none). No single function in `gh_issue_types.py`, the designated shared home,
owns the check. F-2 is that gap.

## correctness
none — no key-presence (`"typed" in rec` / `.get("typed") is not None`) reading of ABSENT as a
backfill candidate found anywhere in the five production files or the four new test files
(grepped both).

## decision_questions
none — D-21's schema duplication was reviewed and is settled reasoning, not a live question.

## Worktree cleanliness
`git -C <worktree> status --porcelain` at end of run (verbatim, before this artifact/observations
write; the two `??` files below are this run's own writes, the other three are concurrent
siblings' — nothing else in the tree changed by me):
```
 M .claude/skills/harness/references/github-mirror.md
 M .harness/harness/features/FEAT-55-issue-types-created-work/feature.json
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/qa-2026-09-05-01-validator.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-qa.md
```
No source file under `.claude/skills/harness/bin/` or `tests/` was touched by this run.
