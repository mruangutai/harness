# REUSE angle — FEAT-24 plan.yaml — receipt

Read-only pass over `plan.yaml` (10 tasks, 10 decisions) and `BRIEF.md` (13 SCs). One finding.

## Finding 1 — T-06 and T-09's verify scripts hand-roll a second board validator that T-02 explicitly builds to be the only one

**File · line:**
- `plan.yaml:772-798` (T-06 verify, `.harness/harness.json`)
- `plan.yaml:980-1011` (T-09 verify, kaya-ai's `.harness/harness.json`)

**What exists already:** T-02 (`plan.yaml:336-459`) adds `factory_config.validate_board(board,
where, path)` in `.claude/skills/harness/bin/factory_config.py`, and T-02's own intent item 2
(`plan.yaml:378-383`) states it in as many words: *"It is the ONLY board validator in the tree
after this feature."* Its checks are exactly the shape T-06 and T-09 need to verify: the five-key
`stations` set (D-06), `owner`/`number`/`station_field` presence, non-empty station values,
FleetError naming the offending key.

**What the plan specifies instead:** T-06's verify (`plan.yaml:773-797`) and T-09's verify
(`plan.yaml:981-1009`) each open the JSON by hand, pull out `github.board`, and re-check the same
facts with a hand-written `want = {"backlog": "Backlog", ...}` dict and manual key-set/value
comparisons — a second, independent spelling of the exact validation T-02 just centralized. Neither
script imports `factory_config` or calls `validate_board`.

**Concrete cost:** three places now assert "what a valid board looks like" — `validate_board`
itself, T-06's `want` dict, and T-09's `want` dict. If D-06's key set or `validate_board`'s rules
change later (a station added, a rule loosened), whichever of the three copies nobody remembers to
touch keeps passing — T-06 or T-09's verify would go on certifying a board shape the real loader
would now reject, silently. This is the exact drift class the plan's own D-05 (`plan.yaml:204-214`)
was written to prevent for the loaders themselves; it just reappears one level up, in the verify
scripts written to check them.

**Smallest fix:** in both heredocs, after loading `b = cfg["github"]["board"]` (T-06) /
`b = g.get("board")` (T-09), add `sys.path.insert(0, ".claude/skills/harness/bin")` and
`import factory_config`, then replace the manual key/value comparison loop with a call to
`factory_config.validate_board(b, "github.board", <path-label>)` wrapped in try/except to report a
`T-06:`/`T-09:` prefixed failure on `FleetError`. Keep the D-06-specific value assertions (that
each station's option name matches the probed live board options, e.g. `stations["backlog"] ==
"Backlog"`) as a second block *after* the `validate_board` call — those are content facts
`validate_board` does not and should not check, so they are not duplicated by this fix.

**The apply must also change task ordering, or it creates a new failure instead of fixing one.**
`validate_board` does not exist until T-02 lands — today it is `_validate_board`, private, with no
stations check; T-02 intent item 2 (`plan.yaml:378-383`) is what makes it public. T-06 and T-09
both currently carry `depends_on: []`, and T-06's own intent (`plan.yaml:804`) says "This task can
run first." If the import is added without also adding `depends_on: [T-02]` to both T-06 and T-09,
and rewriting T-06's "can run first" sentence to "any time after T-02, before T-04," a T-06 run
that still executes before T-02 dies on `AttributeError` on a correctly-executed task — the same
build-cycle cost this finding exists to prevent, introduced by the apply itself. This is a real
trade, not a free one: T-06 and T-09 lose their current ability to run in parallel with T-02.

**Rank:** would-cost-a-build-cycle — this is a live gate, not a cosmetic reformatting; a stale
verify script would pass with a board shape the shipped loader rejects, which is precisely the
fail-open pattern the feature exists to remove, now recreated in its own verify surface.

## Not flagged (checked and ruled out)

- T-01's `file_at_ref` — grepped `factory_gh.py` and the whole `bin/` tree for any existing
  `contents/` REST-endpoint reader or base64 decode of repository content; none exists. Genuinely
  new.
- T-02's per-`(repo_name, ref)` memoisation — no importable cache helper exists in `bin/`;
  `feature_schema.py:66` has a similar module-level cache but it is a single-value cache with a
  different shape, not a reusable utility. A design convention repeated, not code duplicated.
- T-07's verify (`plan.yaml:843-860`) hand-checks `fleet.yaml`'s exact top-level and per-repo key
  sets. This is a stricter/different check than `load_fleet` performs (which does not reject
  extra keys) and is asserting a fact about the fixture file's literal shape, not re-implementing
  loader rejection logic that T-02's own suite already covers. Not a duplicate.
- Repeated "grep the whole file for other statements of the same claim and correct them" language
  across T-02/T-04's intents (`plan.yaml:418`, `:602-607`, `:617-620`) — each instance names a
  different file, read by a different task. Two different readers, not one reader seeing it twice.
