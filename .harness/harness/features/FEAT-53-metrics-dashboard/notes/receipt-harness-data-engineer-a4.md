# A4 — trend.jsonl write path and the touchpoint counter (read-only review)

**BLUF: the append-only merge argument holds AS SPECIFIED for the write mechanism itself (A4a), but
the argument is moot in practice — no task ever calls the writer at ship time (A4b), and the
touchpoint counter it depends on is never fed either (A4c). As drafted, T-10/T-11 ship a correct,
unused library.**

## A4a — VERDICT: HOLDS (mechanism), with two unguarded hazards

The write itself (T-10 intent, plan.yaml:441-445) is pure-append: opens with mode `"a"`, writes one
line, "never rewrites, sorts, dedupes or truncates." The self-check ("reads the existing bytes only
to assert its own append did not disturb them") is a read, not a read-modify-write — it never touches
the file handle used to write. "Keys sorted, no trailing spaces, exactly one newline" (plan.yaml:435)
is *per-record* canonicalisation applied once at construction time, not a re-sort of the file, so it
does not threaten line order.

Two things the spec does not cover:
1. **Duplicate-after-merge is unhandled.** The refuse-if-feature_id-exists check (plan.yaml:444-445)
   is a TOCTOU read-then-decide against the *local* worktree's copy, not a file-wide invariant. Two
   worktrees that each ship a different feature race fine (D-10's actual case). But nothing in T-10
   specifies what `read()` does if a merge legitimately lands two lines with the same `feature_id`
   (e.g., a ship retried after an aborted first attempt in a second worktree) — no de-dup, no loud
   error, and `kpi.py`'s "Wire that into kpi.py's trend key" (plan.yaml:450) never says first-wins,
   last-wins, or reject. This is silent, not a merge conflict.
   — severity: advisory, remedy_cost: amend (T-10 intent: state `read()`'s duplicate-feature_id rule).
2. **T-10's own test proves the common case, not the stronger one.** "two records appended in two
   separate git worktrees both survive a git merge" (plan.yaml:453-455) is exactly this repo's real
   ship topology (per-feature branch cut from a shared main, one PR merge) — a 2-way divergent-branch
   merge where both diffs are zero-length insertions at the same anchor (end of file) is git's
   easy/common case, not a corner case, so the test is real, not decorative. It does NOT exercise:
   (a) three-or-more ships landing in the same merge window (octopus / sequential merges close
   together), or (b) the duplicate-feature_id-after-merge case in finding 1. The stronger assertion:
   extend the test to a 3-worktree/2-sequential-merge chain and add the duplicate-feature_id case as
   its own assertion.
   — severity: advisory, remedy_cost: amend (extend T-10's verify description, no new file).
3. **Trailing-newline invariant holds only inductively.** "exactly one newline" (plan.yaml:435) read
   together with append-only-ever-writer (D-10: this is the only writer) means every line stays
   newline-terminated by construction, so a missing trailing newline before a concurrent append is
   not reachable *from this code path*. Not a finding — noted because the acceptance brief asked for
   a ruling on it explicitly.

## A4b — VERDICT: GAP CONFIRMED, remedy_cost: task-set-change

No task in this plan wires `trend.py append()` into any ship-time call site. `git -C <root> grep` and
a full read of plan.yaml (lines 1-714) confirm: T-10 only *defines* `append()`; nothing calls it. The
lane row (plan.yaml:33-35) and D-10's `because:` both assert "the ship-time append happens in the
user-gated ship step," but no task touches the actual ship mechanism — `gh-sync.py ship` (named in
`.agents/skills/harness/SKILL.md:235` as the trigger the main session runs at merge) is not in any
task's `files:` list, and no task adds a call to `trend.py append(...)` anywhere reachable from that
step. T-12's server explicitly disclaims this too ("READ-ONLY... The append in trend.py is not
reachable from any route," plan.yaml:528-529) — correctly ruling out the server as the caller, but
leaving no caller anywhere else.
- **Finding: write path has no caller.** Without a task that edits the ship mechanism (main-session
  lane, per the plan's own row) to invoke `append()` with a constructed record, `trend.jsonl` stays
  permanently empty and DESIGN's S-1 ("no axes at all") is not a transient gap state — it is the
  dashboard's permanent state for every feature, including ones shipped after this feature lands.
  severity: blocking, remedy_cost: task-set-change (a new main-session-direct task is required: wire
  `trend.py append()`, with a record assembled from `kpi.py`'s per-feature fields plus
  `touchpoints.count()`, into the ship step, i.e. `gh-sync.py ship` or wherever the main session marks
  a feature shipped).

## A4c — VERDICT: GAP CONFIRMED for all three events, remedy_cost: task-set-change

T-11 builds `touchpoints.py`'s `record()`/`count()` (plan.yaml:474-486) and wires `count()` into
`kpi.py` (the read side, plan.yaml:487-488) — but for none of the three D-16 events
(`approval_request`, `escalation`, `uat_request`) does any task add a `record(...)` call at the
place that event actually happens. A full grep of plan.yaml for `record(` / the three event names
turns up only T-11's own definition and description; no orchestrator/pm/validator skill file is in
any task's `files:`.

Lane-grant check: `.harness/*/features/*/touchpoints.jsonl` → `harness-orchestrator` resolves — I ran
`bash .claude/skills/harness/bin/check-domain.sh --resolve .harness/harness/features/FEAT-53-metrics-dashboard/touchpoints.jsonl`
(method used: Bash, since Bash is available to me) and it printed `harness-orchestrator`, so the
grant itself is real. The gap is not authorization, it's that nothing in this plan adds the call
site to the orchestrator's (or pm's, or validator's) approval/escalation/UAT code paths.

**This compounds a specific correctness hazard, not just an unused feature:** D-19/D-16 define
`count()` returning 0 for an absent file as "a measured zero... not unavailable" (plan.yaml:479-480).
If nobody ever calls `record()`, every feature's touchpoint count is a *silent, indistinguishable*
zero forever — the payload will never show `unavailable`, so the dashboard has no way to signal
"never measured" versus "genuinely had zero touchpoints." REQ-06 ships as a permanent, silently-wrong
zero rather than an honest gap state.
severity: blocking, remedy_cost: task-set-change (three new call sites needed, each in the agent/skill
file that owns that moment — plan-sign gate for `approval_request`, the escalation path for
`escalation`, the UAT-request step for `uat_request` — none of which is in this plan's `files:` at
all, so this is at minimum one new task, more likely three).

## A4d — VERDICT: schema-version contract unspecified; unavailable-map granularity unspecified

**`schema: "trend/1"`:** no task states what a reader is contractually required to do with it. T-10's
`read()` intent (plan.yaml:446-449) enumerates missing-file / zero-line / parse-failure as the three
reader-side unavailable reasons, but never mentions checking or branching on the `schema` value
itself. As specified, the field is written but never consulted — a future `trend/2` record would be
read by the same code with no version gate, silently mis-parsed as a `trend/1` record rather than
rejected or routed to a compat path.
severity: advisory, remedy_cost: amend (T-10 intent: state `read()`'s behaviour on an unrecognised
`schema` value — reject-with-reason is the obvious rule, given D-19's own precedent).

**`unavailable` as a sibling map:** D-18/D-19 place `unavailable` once, as a sibling of `grade` and
`attribution` at the trend-record's top level (plan.yaml:440), keyed by field name → reason. `grade`
itself is a nested object with seven sub-fields (plan.yaml:439-440). Nothing in T-10 or T-07 specifies
the key format for a *partial* failure inside `grade` (e.g., `bins` computed but `tracked_files`
not) — is it `unavailable: {"grade.bins": "..."}` (dotted path), `unavailable: {"grade": "..."}`
(whole-object, discarding whatever *did* compute), or is partial failure inside `grade` simply not a
representable state? T-07's `grading.py` (plan.yaml:317-345) has no unavailable/partial-failure return
at all — `distribution()` either returns the full object or (implicitly) raises. So today the
ambiguity doesn't surface because nothing produces a partial `grade`, but the schema as fixed by D-18
has no answer ready if that changes.
severity: advisory, remedy_cost: amend (D-19 or T-10 intent: state the dotted-path convention, or
declare nested-object fields atomic — succeed or reason-out as a whole, never partial).

## Findings summary

| id | section | severity | remedy_cost |
|---|---|---|---|
| F-1 | A4a | advisory | amend |
| F-2 | A4a | advisory | amend |
| F-3 | A4b | blocking | task-set-change |
| F-4 | A4c | blocking | task-set-change |
| F-5 | A4d | advisory | amend |
| F-6 | A4d | advisory | amend |

Not re-reported (already known per dispatch): T-15 `files:` misroute, T-05 UnicodeDecodeError verify.
