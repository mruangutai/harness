BLUF: 2 SIMPLIFICATION findings. If only one apply is permitted: apply F1 first — the
5 vacuous `.setdefault("typed", {})` calls across `factory_decompose.py`/`gh-sync.py`, because
they are dead code (the invariant they guard is already established by `load_factory`/
`load_recorded`), the fix is zero-risk deletion at each site, and the brief names "vacuous
branches" as the first category to flag.

## Findings

**F1 — vacuous `setdefault("typed", …)` calls, 5 sites, two files**
- `factory_decompose.py:436` (`_backfill_issue_types`), `:536`, `:556`, `:569` (all inside `_main`)
- `gh-sync.py:1122` (`cmd_open`)
- Summary: each call defends against `factory`/`rec` lacking a `"typed"` key, but that key is
  unconditionally present before any of these call sites run. `factory_decompose.py`'s
  `_empty_factory()` (line 107) always sets `"typed": {}`, and `load_factory` (line 113) either
  returns that or a populated copy — every caller of these five sites reaches `factory` only via
  `load_factory` at `factory_decompose.py:498`. Symmetrically, `gh-sync.py`'s `load_recorded`
  (line ~567: `rec["typed"] = dict(typed) if isinstance(typed, dict) else {}`) makes the same
  guarantee for `rec`, and `cmd_open`'s only path to `rec` is `load_recorded` at line 1117 —
  `cmd_open` itself is called from exactly one site, `main()` line 2080.
- Concrete cost: five lines of dead defensive code that assert an invariant already established
  two call frames up, in a section of the diff (issue-type provenance) that a reviewer must
  already read carefully for the D-20 absent-means-unknown rule — each vacuous `setdefault` adds
  one more branch a reader must rule out ("could this actually fire?") for no behavioral payoff.
- Alternative: delete `.setdefault("typed", {})` at all 5 sites; index `factory["typed"]` /
  `rec["typed"]` directly, matching every other read of the same key in both files
  (e.g. `factory_decompose.py:398,437,444`; `gh-sync.py`'s `_parent_needs_type`/`_task_needs_type`
  already index `rec.get("typed", {})` directly without a mutating setdefault).
- Checked against plan.yaml decisions: read D-20 (plan.yaml:147-181) and D-10 (:106-109) in full —
  neither mandates re-normalizing `typed` at each write site; D-20 governs the *read* semantics
  (absence-of-entry means unknown), not defensive mutation at every call site. Not an anchor.
- severity: low
- apply: yes

**F2 — `type_for_nature` duplicates `_resolve` instead of calling it**
- `gh_issue_types.py:66-76` (`type_for_nature`) vs `gh_issue_types.py:49-59` (`_resolve`)
- Summary: `_resolve(name, table, overrides)` already implements exactly the membership-check +
  override-lookup pattern `type_for_change_type` reuses via `_resolve(change_type, ..., overrides)`
  (line 63). `type_for_nature` reimplements the same 8 lines inline instead of calling
  `_resolve(nature, DEFAULT_TYPE_BY_NATURE, overrides)`, including a literal copy of `_resolve`'s
  error string ("... is not a known change_type ...", line 69) which is wrong for the nature case
  (a `nature` value, never a `change_type`, triggers it) — a stale copy-paste artifact of the
  duplication.
- Concrete cost: ~8 duplicated lines in a net-new, 167-line module meant to be the single shared
  home for this mapping (its own docstring: "there are three resolvers, each answering for exactly
  one role") — the third resolver silently diverges from that shared implementation, and the
  divergence carries a wrong error message forward with it.
- Alternative: `def type_for_nature(nature, overrides): return _resolve(nature, DEFAULT_TYPE_BY_NATURE, overrides)`,
  matching `type_for_change_type`'s one-liner. (This does not fix the underlying message's mention
  of "change_type" — that wording is `_resolve`'s own and is shared by both callers already; folding
  the duplicate at least stops it from existing twice.)
- Checked against plan.yaml decisions: read D-18 (plan.yaml:490-492, :1304-1308) — it pins WHICH
  table each resolver reads (task vs. parent, never crossed), not HOW each resolver is internally
  implemented. Calling `_resolve` from `type_for_nature` preserves D-18's role separation exactly
  (three public functions, three distinct tables) and touches no anchor.
- severity: low
- apply: yes

## correctness
none — no key-presence check on `rec["typed"]` / `factory["typed"]` (`"typed" in rec` or
equivalent) anywhere in the five production files or the four named test files. Every read
site value-checks (`.get("typed", {}).get(key) == "created"`, `is True`, `in ("created",
"adopted")`), which is exactly the D-20 four-state discrimination the shared context warns must
not collapse to two states.

## decision_questions
none

## git status --porcelain (verbatim, end of run)
```
 M .claude/skills/harness/references/github-mirror.md
 M .harness/harness/features/FEAT-55-issue-types-created-work/feature.json
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/qa-2026-09-05-01-validator.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-data-engineer.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-qa.md
```
None of the above are mine: `github-mirror.md` is the main session's concurrent edit (named as a
hard non-goal in the shared context); `feature.json` and the qa/backend-dev/data-engineer files are
sibling peers' concurrent work. This artifact and my own observations log are the only writes I made.
