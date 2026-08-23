# Code review — FEAT-31, d065b3b..fcb8984

## BLUF

**FAIL on one finding: Q-WARNVERB is HIGH.** Everything else in this diff — spec compliance
(REQ-01..10, SC-01..15 mapped to code), the two previously-shipped defects (discovery depth,
D-11's `_build_row` contradiction), and the SIMPLIFY commit itself — is in order and independently
re-derived from the committed sha, not taken on report. One real, evidenced gap remains: the
context-crossing warning text does not honour the "hard obligation" the feature's own settled
research (`notes/settled-Q-HOOKCTX.md`) placed on it, and the mechanism that would let it fire is
live in production right now.

## File census (`git diff d065b3b..fcb8984 --name-only`, 72 paths)

All Python (`.py`, 16 files: `context-watch.py`, `context-watch-hook.py`, `feature_schema.py`,
`upgrade-config.py`... and their `test-*.py`/`verify-*.py` siblings), 2 shell (`check-state.sh`,
`run-unit-tests.sh`), JSON config (`.claude/settings.json`, `feature-schema.json`,
`harness.json` x2), Markdown/YAML feature-process artifacts (`BRIEF.md`, `plan.yaml`, `STATE.md`,
`feature.json`, everything under `notes/`, `observations/`), and two docs
(`DECISIONS.md`, `DECISIONS-INDEX.md`). One `.html` — `notes/ship-review-fix1.html` — is a
rendered status report for the operator (inline CSS, no app logic), not an application UI surface.
**Confirmed: zero UI surfaces.** The dispatcher's call not to route ui-reviewer stands.

## Stage 1 — spec compliance

Read `BRIEF.md` (REQ-01..10, SC-01..15) and `plan.yaml` (D-01..26, T-01..19) in full, and the
committed `context-watch.py`, `context-watch-hook.py`, `feature_schema.py`, `check-state.sh`,
`feature-schema.json`, `DECISIONS.md`'s DEC-159 entry, all read via `git show fcb8984:<path>` —
not the working tree, which carries unrelated local dirt (`STATE.md`, `feature.json` run
bookkeeping, confirmed harmless by `git status`).

**SC-09 (verify: inspection) — re-derived independently, MET.** Ran all eight of T-19's own
grep assertions by hand against the committed `DECISIONS.md` slice
(`awk '/^## DEC-159 /,/^## DEC-160 /'`): header count 1, `templates/HANDOFF.md` present (body
intact), the false clause "the watchdog remains the post-hoc audit" count 0, `mid-flight` count 2,
`context-size` count 1, `context-watch-hook.py` count 1, `turn-count` count 2, `STRUCK|am\.[0-9]`
count 0. Read the prose too, not just the grep: it correctly states the turn-count nudge remains
deferred and what shipped is a different metric serving the same function — it does not claim the
deferred item was delivered, which is the exact trap the task's own intent named.

**SC-07 / T-15 / D-23, re-derived against real data, MET — and the dispatcher's premise about
it resolves cleanly.** `feature-schema.json`'s `runs.items.required` is `['id','squad','verdict']`
— `agent` is declared in `properties` but is genuinely schema-OPTIONAL, exactly as D-23 designed.
The write-time requiredness is a separate positional rule in `feature_schema.py`
(`_runs_agent_problems` + `RUNS_AGENT_EXEMPT`), keyed on a frozen per-feature index map, not on
the schema. Checked FEAT-31's own `feature.json` (`runs`, 15 entries) against the frozen exempt
count of 9 for this feature: `runs[0..8]` all lack `agent` (correctly exempt — they predate the
rule), `runs[9..14]` all carry it (correctly required and present). **There is no contradiction
and the T-15 rule is enforced, not unenforced, for every future entry** — the dispatcher's
hypothesis that "if optional in practice, the rule is unenforced" does not hold here because
enforcement lives beside the schema, not in it. `check-domain.sh` itself is untouched in this
diff, confirming D-23's claim that no cutover edit was needed there.

**D-11 (`_build_row`'s prior contradiction) — re-derived, now consistent.** `_measured_sizes`
is the single seam defining the measured set (lines that parse AND carry a dict at
`message.usage`); `_build_row` takes `current = sizes[-1]` and `peak = max(sizes)` over that same
set, and returns an unmeasured row when the set is empty rather than reporting 0/0. All three
figures — current, peak, entries — are computed off one set, matching D-11 as corrected.

**Discovery depth (prior Defect 2) — re-derived, correct, but the "both directions" claim needs
a correction.** `discover_orchestrator_rows` and `_orchestrator_jsonl_paths` both walk
`<root>/<project-dir>/<session-dir>/subagents/agent-*.meta.json` — two levels, matching D-11's
measured layout. `test-context-watch.py::L1/L2` and `verify-context-watch-live.py`'s
`_run_depth_self_test` both assert: (a) the correct two-level fixture is found, (b) a
one-level-too-shallow fixture finds zero, and (c) a mutant that flattens the walk back to one
level loses the correct fixture (count differential, not exit-status-only — D-08 honoured).
**I could not find a three-level-too-deep fixture anywhere in the diff** (`test-context-watch.py`,
`test-context-watch-cli.py`, `verify-context-watch-live.py` — grepped for "three level",
"too deep", "deeper", "depth" across all three). qa's own note
(`notes/qa-20260822-065648.md:76-81`) says the same thing I found: "both directions" there means
correct-vs-shallow, not shallow-vs-deep. **Correction to the dispatch brief: the fix is pinned
against under-nesting (the actual historical defect shape), not over-nesting.** This is a real,
minor gap — nothing catches a future edit that adds an *extra* level to the walk — but low
priority: the walk is two literal nested nested `for` loops, not a variable-depth glob, so an
accidental third level is a much less likely regression than the one actually shipped and now
covered. **Severity: low, not must_fix.**

**SC-13/SC-14/SC-08/SC-01/SC-02/SC-03/SC-04/SC-05/SC-06/SC-11 — spot-verified against the
committed source, all consistent with their BRIEF text and D-NN specifics.** `warn_for_agent`
computes `current` from the transcript's tail via `_last_measured_usage` using the same
measured-set rule as T-01, deliberately never computing `peak` (commented, and justified by the
2858-Bash-events cost argument in D-24/T-16). `context-watch-hook.py` is genuinely thin (D-24): no
arithmetic, no threshold comparison, no message text — confirmed by reading the full 91-line file.
`check-domain.sh` was not touched (confirmed via `git diff --stat`), matching every lane
decision that assumed it (D-23, D-24). `.claude/settings.json`'s hook is appended to the existing
`PostToolUse`/`Write|Edit|Bash` matcher, not a new one (T-17's verify block asserts this and I
re-read the committed JSON to confirm the same shape).

## Stage 2 — code quality

### 1. [HIGH] Q-WARNVERB — the delivered warning does not honour the feature's own settled
obligation, and the harm it warns against has already been observed once.

`.claude/skills/harness/bin/context-watch.py:538-544` (`warn_for_agent`'s returned text, read
from the committed blob at `fcb8984`):

```
"context-watch: WARNING agent=%s current=%s at or above threshold=%s "
"-- this advises only; the orchestrator decides. DEC-159's seam rule "
"applies: end this phase at the boundary and write ..."
```

`notes/settled-Q-HOOKCTX.md` — written by this same feature, before T-17 was built — measured
directly (not inferred) that Claude Code wraps a `PostToolUse` exit-2 as
`"PostToolUse:<tool> hook blocking error from command: ..."`, and that an agent receiving exactly
that framing from `check-domain.sh --post` **reacted by undoing a landed write**, because
in-post the write had already succeeded and "blocking error" reads as a refusal. The note states
in its own words: *"T-17's warning text carries a hard obligation, not a stylistic one: it must
state in its first line that nothing was blocked, the tool call succeeded, and no retry or revert
is needed — before it says anything about context size."*

The shipped text does not do this. It opens with the word "WARNING", never states the write
succeeded, and never forecloses retry or revert — it only says the tool "advises" and "the
orchestrator decides", which is a *different* claim from "nothing was blocked; do not retry or
revert". `check-domain.sh:698-703` already carries the correct pattern for the identical problem
(`VERB = "OVER BUDGET (already written)" if _post else "BLOCKED"`) — this feature had the fix
in front of it and did not apply it to its own new warning.

**Concrete cost.** A `harness-orchestrator`, mid-`Write` on e.g. a `feature.json` runs entry,
crosses the threshold and receives, in its own turn:
`PostToolUse:Bash hook blocking error from command: "...context-watch-hook.py": context-watch:
WARNING agent=... current=... at or above threshold=... -- this advises only...`
An orchestrator that treats "blocking error" as a real failure — exactly the behaviour already
measured once on the structurally identical `check-domain.sh` wrapper — may retry the write
(producing a duplicate `runs` entry or duplicate content) or revert it (data loss on the write
that just landed). The dispatch reports this already fired seven times over `feature.json`
writes during this feature's own build and happened to land clean every time; "happened to land
clean" is not a property of the wording, it is luck, and the next occurrence is not guaranteed to.

**This is a realistic case, not a hypothetical one**: the hook fires on ~94% of an
orchestrator's tool calls at the measured matcher coverage (D-25/T-17), so every orchestrator
that ever crosses the threshold will see this exact framing, not an edge case.

**Minimal remedy.** One string edit, in the file the feature already owns (team-dispatchable,
`harness-backend-dev`, no main-session-direct cutover required): prepend a first clause to
`warn_for_agent`'s return value stating plainly that nothing was blocked, the write already
landed, and no retry or revert is needed — mirroring `check-domain.sh`'s `VERB` pattern — before
the context-size figures. The same clause should be applied to `format_rows`' table warning
(`context-watch.py:413`) for consistency, though that one is read directly by an operator and
carries lower risk since it is never wrapped as a hook error.

**Ruling: HIGH.** Wrong behaviour in a realistic case, evidenced by the feature's own prior
incident on the identical mechanism, against an obligation the feature's own research explicitly
imposed on itself and then did not implement.

### 2. [MED] Unguarded top-level scan failure is reported as a definitive "no orchestrators
found" with exit 0, and no test exercises this path.

`.claude/skills/harness/bin/context-watch.py:745-763` (committed at `fcb8984`):

```python
try:
    rows = discover_orchestrator_rows(projects_root)
except Exception as exc:  # never crash — this tool only reads
    print("context-watch: error scanning %s: %s" % (projects_root, exc), file=sys.stderr)
    rows = []
...
if not rows:
    print("no orchestrators found under %s" % projects_root)
    _print_blind_spot_footer(rows, projects_root, config_path)
    return 0
```

If `discover_orchestrator_rows` ever raises for a reason its own internal guards (`_safe_listdir`,
`_build_row`'s try/excepts) don't already catch — a future refactor, an unanticipated OSError
subtype, an encoding surprise — the tool prints an "error scanning" line to stderr **and then**
falls straight into the same branch a genuinely-empty scan takes: stdout says "no orchestrators
found", and the process exits **0**. An operator or a script that checks only the exit code (the
documented contract: "0 when every discovered orchestrator row was measured and no row warned")
gets a clean bill of health indistinguishable from the true no-orchestrators-running case, exactly
while N real orchestrators may be running unmeasured — the REQ-07/SC-10 guarantee this whole
feature exists to uphold. Grepped both `test-context-watch.py` and `test-context-watch-cli.py` for
"error scanning": zero hits — this branch has no committed test.

I judge this MED rather than HIGH: the internal guards already cover every OSError-shaped failure
I could construct, so this is a defensive net around an unlikely bug rather than a currently
reachable path, and unlike Q-WARNVERB there is no measured incident. But it is real maintainability
risk sitting exactly on the fail-open pattern this review was told to hunt, and it is untested.

### 3. Confirmed, not re-filed: `_orchestrator_jsonl_paths` docstring is false (already on record).

`.claude/skills/harness/bin/context-watch.py:571-578` (corrected anchor — the dispatch cited
570-576; the `def` line is 571 and the docstring runs through 578). The docstring claims the
function "Mirrors `discover_orchestrator_rows`' walk ... and its agentType filter" and that a
malformed meta file is "simply skipped, same as `_build_row`'s own unmeasured-row path." Both
halves are false: `discover_orchestrator_rows` routes an unparseable or `agentType`-less sidecar
through `_unmeasured_row`, which **is emitted as a row** and feeds `unmeasured_count` (a REQ-07
surface, drives the process exit code); `_orchestrator_jsonl_paths` on the identical failure just
`continue`s — no row, no count, no exit-code effect. This is the SIMPLIFY commit's own finding
(lead overruled the ALTITUDE reader's fold-in recommendation on exactly this divergence) — I
re-derived it independently from the committed blob rather than trusting the commit message, and
it holds. Per the dispatch, not re-filing the mechanism; recording the confirmed/corrected anchor
only.

### Nothing else rose to a reportable finding

Spot-checked `resolve_threshold`/`resolve_retention_days` (both never raise, both state their
fallback reason where REQ-03/T-06 require it), the blind-spot footer's three lines (each
interpolates a computed or read value — SC-08 holds on inspection), `check-state.sh`'s INV-17
empty-body check (body = lines between a present heading and the next `##` line or EOF; empty =
every such line blank after strip — matches SC-15's stated scope exactly; headings compared
case-insensitively against `templates/HANDOFF.md`'s four sections, which match verbatim), and
`test-context-watch-hook.py`'s four hook cases plus never-raises assertions. All D-08 mutant
"red proofs" I sampled (Case L, Case J, T-15's Case E, T-10/T-14's marker-anchored mutants) assert
a mutation-applied check before comparing counts, never rely on exit status alone.

## Q-HOOKCTX / T-15 in-session inversion / T-17 non-observability

All three noted as **not defects** per the dispatch (hooks resolve through the main checkout's
stale enforcement layer on this branch) and treated as such — not re-litigated here.

## Verdict rationale

`must_fix: [Q-WARNVERB]`, `severity_max: high` → gate fails per `gates.review:
advisory_unless_high`. Everything else in this diff — including two previously-shipped real
defects and their fixes — held up under independent re-derivation from the committed sha.
