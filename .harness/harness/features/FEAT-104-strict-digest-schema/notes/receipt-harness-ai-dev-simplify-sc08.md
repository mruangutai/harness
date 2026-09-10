# Receipt — harness-ai-dev — simplify/altitude — SC-08 assertion delta

**BLUF: LEAVE. The two new substrings sit at the right altitude — they pin the declaration ROUTE (schema
file + declared symbol) that SC-08 demands, not incidental prose, and they adopt this file's own
established substring-assertion convention rather than inventing a new one. One low-severity, non-blocking
observation on the backtick-quoted form; no fold-in, no briefing-row.**

## Reading chosen: (a) — stable contract, not incidental wording

SC-08 (`BRIEF.md:92-94`): "The rejection text names the declaration route by file and symbol —
`validate-digest.py` `SCHEMAS`/`PASSTHROUGH` for a digest key, the step-schema symbol for a step key —
asserted as a substring, not merely non-empty." That is an explicit instruction to assert file identity
and symbol name as literal substrings — reading (a) is what the criterion itself specifies, not an
inference from the diff.

## Evidence

1. **Emitter** (`check-domain.sh:1653-1658`): the message is `"offending key(s): {...}. A recovery field
   is declared in .claude/skills/harness/bin/run-state-schema.json; a per-dispatch fact goes under
   `evidence` with a lowercase identifier key..."`. The test asserts only the **basename**
   `"run-state-schema.json"`, not the full path — already the weakest sufficient form: a schema
   relocated to a different directory but kept under that filename still passes, and the human-facing
   fact ("look at this file") survives. The `` `evidence` `` substring names the declared container field,
   matching the emitter's own backtick-quoting convention for symbol-like tokens (same style at
   `check-domain.sh:1843-1845` for `on`/`off`/`yes`/`no`/`true`/`false`/`01`) — this is an established
   codebase convention for marking a literal identifier in a message, not decorative markdown a reword
   would casually drop.
2. **File's own precedent**: `_floor_creation_cases()` (`test-check-domain.py:144-146`) already asserts
   `"schema_version floor" in ...stderr and "string" in ...stderr`; `_evidence_cases()` asserts
   `"undeclared step key"`. Literal-substring assertion on stderr is this suite's established altitude for
   message contracts — the delta extends that pattern to the file+symbol facts SC-08 newly requires, it
   does not introduce a new instrument.
3. **Asymmetry test** (which of the four substrings survives a contract-preserving reword): `"undeclared
   step key"` and `"rogue_step_key"` are unaffected by any message rewording that keeps a rejection.
   `"run-state-schema.json"` survives a message rewording; only a schema *rename* would break it, which
   is itself the kind of route change SC-08 wants surfaced. `` "`evidence`" `` survives a reword that keeps
   backtick-quoting convention; only a reword that also drops markdown emphasis on symbol names would break
   it, and that would be a repo-wide convention change, not a one-message edit.

## Finding (info, non-blocking)

- **F-1** — `tests/integration/test-check-domain.py:89`, severity: **low**. The backtick-inclusive
  assertion `` "`evidence`" in strict.stderr `` is marginally more brittle than the bare `"evidence" in
  strict.stderr` would be: a message rewording that keeps naming the container but drops markdown emphasis
  (e.g. switches to single-quoting) would falsely redden this case, whereas asserting the bare word would
  survive it. Cost is low — the file already relies on this exact backtick convention elsewhere
  (`check-domain.sh:1843-1845`), so a convention-wide change is the only thing that breaks it, and that
  change would touch many messages at once, not just this one. Concrete edit it WOULD make (test file is
  read-only under DEC-174, so this is reported, not applied): drop the backticks in the assertion,
  `and "evidence" in strict.stderr`. Recommendation: **leave** — matches file precedent, low probability,
  low blast radius if it ever reddens.

## Standing residual carried forward, not re-raised

Q7 (`is_strict_schema_version()` predicate spelled 3 complete + 2 partial times across `check-domain.sh`
and `check-state.sh`) — open and accepted, out of scope for this delta.

## Recommendation

**LEAVE** — for the delta as a whole. Both new substrings are the weakest sufficient instrument for
SC-08's explicit demand, they extend the file's own established altitude rather than adding a new one, and
the one asymmetry found (F-1) is low severity and better left given the file's existing backtick
convention.

## Verification

Read-only run per the confinement in this dispatch: no edits made, no suite run, no commit. Verified via
`git status --porcelain` (worktree) showing zero tracked modifications from this session.
