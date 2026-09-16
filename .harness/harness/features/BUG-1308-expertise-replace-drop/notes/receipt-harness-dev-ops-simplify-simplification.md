# SIMPLIFICATION angle — BUG-1308 expertise-replace-drop

BLUF: one real backlog-worthy finding (the `resolved` 5-tuple has two consumers that
positionally unpack fields they never use); everything else examined was earned. No
apply-now finding.

## Findings

### F1 — `resolved` 5-tuple partially ignored by two of its three consumers (backlog)
- File/line: `.claude/skills/harness/bin/expertise-merge.py:243` (`_check_proposal_ambiguity`)
  and `:322` (`_build_outcomes`).
- Summary: both functions unpack the full `(verb, section, target, entry, preserved)` tuple
  by position but each uses only a subset — `_check_proposal_ambiguity` uses `section, target`
  only (`verb`, `entry`, `preserved` bound but dead); `_build_outcomes` uses `verb, target,
  preserved` only (`section`, `entry` bound but dead). Only the third consumer,
  `_apply_resolved` (line 291), uses all five.
- Concrete cost: every future change to the tuple's shape (add a field, reorder two adjacent
  ones) must be replayed correctly across three positional-unpack sites even though two of them
  don't read most of the positions — an unused-variable lint won't catch a silent reorder
  because the names are still bound, just unread. This is a real, if modest, maintenance tax
  the change introduces (the tuple and both partial consumers are new in this diff).
- Alternative: a `collections.namedtuple("ResolvedOp", "verb section target entry preserved")`
  built once in `_resolve_all` (line 264), with `_check_proposal_ambiguity` and
  `_build_outcomes` reading `.section`/`.target` or `.verb`/`.target`/`.preserved` by name.
  Unused fields become invisible instead of named-but-ignored, and a reorder can't silently
  mis-bind a consumer that only touches two of five names.
- Rating: **backlog**. Fixing it touches four sites (the tuple's one construction point plus
  three unpack sites), not a single local edit, and the diff already passed qa's suite — no
  assertion here needs weakening to apply it, but it's not a one-edit change either.

## Examined and judged earned (no finding)

- **The four `_validate_*`/`_parse_op` split** (`_validate_verb:157`,
  `_validate_target_section:170`, `_validate_entry_and_keys:181`, `_parse_op:192`): each does
  distinct, non-overlapping work (verb legality incl. the friendlier `op=merge` message,
  section presence/membership, entry-key legality per verb) and `_parse_op` composes them plus
  builds the return tuple — none is a bodyless pass-through whose deletion would just relocate
  the same lines one level up.
- **`_validate_verb`'s two checks** (`op == "merge"` then `verb not in _OP_KEYS`, lines
  159–166): technically only the second check is load-bearing for reachability since `"merge"`
  is never a key of `_OP_KEYS`, but the first produces a distinct, more useful refusal message
  (the replace-plus-drop rewrite instruction) that D-10 specifically wants surfaced. Not a
  redundant conjunct — different message, same as decision cited in-scope as settled (D-10).
- **`_rebuild_section`'s refusal to index into `base_entries`** and **`_resolve_all` resolving
  every op against the original `base_sections`** (lines 269–283, 254–266): read both in full;
  these are exactly the anchors the dispatch calls out as having taken design rounds. No
  simpler-looking pipeline replacement was found that preserves order-independence and the
  original-snapshot semantics, so I propose no change to either.
- **Comments in the new code**: grepped for narration phrasing (`used to`, `now also`,
  `previously`, `no longer`, `we now`, `this change`) across the whole file — the only hit is
  the `_OP_KEYS` block comment (lines 143–145), which states present fact with decision
  provenance ("`merge` is deliberately absent: D-10 keeps it...") rather than narrating a
  before/after. No narration-style comment exists in the new code.
- **Unit test cases** (`tests/unit/test-expertise-ops.py`, u1–u16) and **integration cases
  11–20** (`tests/integration/test-expertise-merge.py`): read every case name and docstring.
  Each targets a distinct scenario (cap-at-capacity, removal, missing target, ambiguous target
  two sub-cases, atomic failure, add-only compatibility, contract drift, concurrent writers,
  multi-op composition, malformed-ops CLI) — no pair is a near-duplicate body that could share
  a table/helper without dropping a distinct assertion. Left untouched, per the dispatch, the
  exit-11 wording assertions at `tests/integration/test-expertise-merge.py:542-545` and
  `:563-566`.

## Not examined (out of scope per dispatch)

- `apply`'s pre-existing union path (`cmd_apply`, `compute_union`) — REQ-07 settled,
  behaviourally unchanged, zero lines removed.
- `op: merge` refusal design (D-10) and (section, id) keying (D-01/D-02) — settled decisions,
  not re-litigated.
