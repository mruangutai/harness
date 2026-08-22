# EFFICIENCY angle — FEAT-31 simplify pass (harness-data-engineer)

**BLUF:** 1 finding, FLAG-ONLY. It is material (measured, structural, forever-cost) but the
touched file (`.claude/settings.json`) is main-session-direct under DEC-174, so no squad
member can apply it — it goes to the lead's docket as an open question, not a build-side fix.

## Checks performed (all measured, none asserted)

1. `context-watch-hook.py`'s per-call `importlib.util.spec_from_file_location` +
   `exec_module` re-load of the 779-line `context-watch.py` on every invocation: measured
   200 reps, 0.103ms/call (`python3 -c` timing loop, this session). Negligible against any
   hook-frequency budget — not a finding.
2. `resolve_threshold`'s per-call open+parse of `.harness/harness.json` (10014 bytes):
   measured 5000 reps, 34.15us/call. Negligible — not a finding.
3. `warn_for_agent`'s tail-read of the transcript jsonl (`_last_measured_usage`): reads from
   EOF in 64KB chunks and stops at the first qualifying line by design (docstring states the
   full-scan/peak tradeoff explicitly) — this is the deliberate efficient path, not waste.
4. `check-state.sh`'s new INV-17 handoff-shape glob (74 `notes/handoff-*.md` files read in
   full): this is a manual/pre-commit boundary check, not a hook in `.claude/settings.json`
   — confirmed by grep, `check-state.sh` is absent from the hooks block. A boundary-step full
   read is not waste per the skill's own carve-out. Not a finding.
5. `run-unit-tests.sh`'s new kind-drift cross-check subprocess (one `python3 -` heredoc per
   suite invocation, before any test runs): one process spawn per suite run, not per tool
   call. At the suite's own stated ~15s runtime this is immaterial. Not a finding.
6. The blind-spot footer's second full corpus read (~0.39s of ~0.80s) — already dispositioned
   in the dispatch, not re-flagged.

## The one finding (FLAG-ONLY)

**File:** `.claude/settings.json:57-61` (adds `context-watch-hook.py` to the `PostToolUse`
`Write|Edit|Bash` matcher, alongside pre-existing `check-domain.sh --post`).

**Summary:** the new hook is registered on a matcher that fires for every agent type — main
session, both leads, and all engineer/reviewer members — not just `harness-orchestrator`,
the only agent type the hook's own logic ever acts on (`context-watch-hook.py:121,133`
gates on `agent_type == "harness-orchestrator"` INSIDE the script, after the process has
already started). Every Write/Edit/Bash from the other ~15 personas pays a python
interpreter spawn that does nothing.

**Measured cost:** 20-rep loop, this session, this machine:
- `context-watch-hook.py` invoked with a non-orchestrator payload (the early-exit path):
  20 calls in 0.383s wall → ~19ms/call.
- bare `python3 -c "pass"` baseline: 20 calls in 0.338s wall → ~17ms/call — confirms the
  cost is almost entirely interpreter startup, not the script's own logic.
- for scale, the existing `check-domain.sh --post` on the same event: 20 calls in 1.406s
  wall → ~70ms/call (bash + subprocess-heavy). The new hook adds ~19ms on top of that
  ~70ms baseline per matched tool call — a ~27% increase in this event's total hook
  latency, paid by every Write/Edit/Bash from every agent that is never the intended
  subject.
- Per the hook's own docstring, one orchestrator alone produces ~127 matched tool calls per
  transcript on average (3359 tool_use events / 25 transcripts, Bash+Write+Edit share);
  the non-orchestrator population (main session, 2 leads, 5 engineers, review tier) across
  a feature is not smaller. At ~19ms/call this is tens of seconds of pure added latency per
  feature, system-wide, forever — not a one-shot cost.

**Why FLAG-ONLY, not applicable:** the fix is a matcher-granularity question — Claude Code's
hook `matcher` field matches on tool name only, not on `agent_type`, so the per-agent
filter cannot move out of the script and into the settings.json matcher itself. The two
candidate alternatives (merge the check into the already-running `check-domain.sh --post`
process rather than spawning a second interpreter; or accept the cost as the price of a
hook API that cannot filter by agent type) both require a call the lead should make, and
`.claude/settings.json` plus `check-domain.sh` are both DEC-174 main-session-direct files
no squad member may write. This is an `open_questions` item, not a build-side apply.

## Not re-raised

Nothing from the dispatch's already-settled list (D-11/D-18/D-23/D-24/DEC-159/174/178/198,
the `_measured_sizes` seam, the two-line comparison seams, backlog rows #663-#669, the
warning-text wording) was re-litigated.
