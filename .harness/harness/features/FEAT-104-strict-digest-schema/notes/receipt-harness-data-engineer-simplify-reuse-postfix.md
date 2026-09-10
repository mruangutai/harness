## FEAT-104 · SIMPLIFY POSTFIX (99035a9c) · REUSE angle · harness-data-engineer

**BLUF:** the fix delta adds a THIRD hand-written spelling of the "strict schema_version" predicate
(the third and fourth candidates I was asked to check — `run-state-schema.json` and the `.agents/`
mirrors — are not independent copies), and the three shell/py spellings have already silently
diverged in what "strict" means at the boundary. One real finding.

### Findings

1. **`check-domain.sh:1594-1597` (creation floor) vs `check-domain.sh:1760-1764` (new downgrade
   guard) vs `check-state.sh:1590-1595` (new persona selector)** — three independently hand-written
   copies of "is this an int, not a bool, and >= 2" in one file pair, two of them new in this fix:
   - `check-domain.sh:1594-1597`: `isinstance(_version, int) and not isinstance(_version, bool) and _version >= 2`
   - `check-domain.sh:1760-1764` (`_prior_is_strict`): `isinstance(_prior_version, int) and not isinstance(_prior_version, bool) and _prior_version >= 2`
   - `check-state.sh:1590-1595` (`_persona` ternary): `isinstance(_version, int) and not isinstance(_version, bool) and _version >= 2`
   I read all three: **semantically identical today**, not divergent, but each is composed fresh
   against a different local variable name (`_version`/`_prior_version`/`_version`) rather than
   calling one predicate. **Cost:** the predicate already needed a companion in this same diff —
   `_version_decreased` at `check-domain.sh:1766-1770` inverts the SAME three-part test a fourth
   time (`not isinstance(...) or isinstance(..., bool) or _version < _prior_version`) using
   De Morgan's form instead of the positive form used everywhere else. A future change to what
   counts as "strict" (e.g. also rejecting `_version == 2` itself, or moving the floor to 3) has to
   be edited in four places across two files; the De Morgan'd fourth copy is the one most likely to
   go stale silently, since a reviewer skimming for `>= 2` literals will find the other three and
   plausibly miss the inverted comparison buried in a boolean-or chain — the symptom would be a
   downgrade guard that trips (or fails to trip) at the wrong version boundary while the other three
   sites are already updated and passing their own tests. **Alternative:** factor
   `is_strict_schema_version(v)` once — either as a tiny shared Python function on the `sys.path`
   both heredocs already share (both files already import sibling `bin/` modules at runtime, per my
   prior-pass finding 1 in the non-postfix receipt), or, cheaper, encode the floor directly in
   `run-state-schema.json` as `"schema_version": {"type": "integer", "minimum": 2}` and have both
   scripts ask the schema object for its own floor instead of restating the literal `2`. **worth-
   doing: yes**, small and exactly the class of drift this same file pair already showed once in
   the non-postfix diff (finding 1 of my prior receipt, on the rejection-message text).

### Schema question (per dispatch)

`run-state-schema.json:9` types `schema_version` as `{"type": "integer", ...}` but declares **no**
`minimum` — the floor-of-2 constraint the three predicates above restate is NOT present in the
schema at all; the schema enforces the type but not the strictness boundary. So today it's three
(really four, counting the inverted `_version_decreased`) copies of the *same* undeclared business
rule, none derived from the schema, and the schema itself is not a fourth candidate — it simply
doesn't cover this rule.

### `.agents/` mirrors — not a fourth spelling, verified

`check-domain.sh`, `check-state.sh`, `validate-digest.py`, and `run-state-schema.json` under
`.agents/skills/harness/bin/` share the **same inode** as their `.claude/skills/harness/bin/`
counterparts (confirmed via `stat -f %i` on this worktree, all four pairs identical). They are
hardlinks, not independent files — editing one edits both by construction, so there is no sync
mechanism to check and no fourth spelling to count. (Matches this repo's own Expertise G-11/`.agents`
hardlink-twin convention.)

### Unchanged from the prior pass

The prior pass's findings 1 (rejection-message text drift) and 2 (top-level key-set triplication,
out-of-scope for this diff) stand unchanged — neither is touched by the fix delta. My judgement of
the rest of the diff (T-04 test helpers, `SCHEMAS`/`PASSTHROUGH` tables, `test-check-domain.py`'s
`DECLARED` pin, fixture plumbing, the two `.omp/agents/*.md` paragraphs) does not move: none of those
files are touched between `6126ac07` and `99035a9c`.

### Out-of-band

None — I did not find a live correctness divergence between the three predicate copies; they agree
on every input I traced (int/non-int, bool, `>= 2` vs `< 2`). This is a reuse-cost finding, not a
correctness bug.

### Verdict

Ran the REUSE angle only, flag-only per DEC-174 (no source/test edits made). One finding worth
carrying (predicate quadruplication); schema and mirror questions answered clean; prior-pass findings
re-affirmed unchanged.
