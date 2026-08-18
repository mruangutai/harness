# Mode A design-contract review — FEAT-23 ship-flow fixes

**Pin check:** `git rev-parse HEAD` = `b7ae135f965985df6c4d1b542063150d22d19bbd`. Short form `b7ae135`
matches the pinned `review_sha`. Confirmed directly, not taken from the dispatch.

**Verdict: PASS.** No rendered UI surface exists in this plan. Two operator-facing *text* surfaces
exist and were audited per the dispatch's explicit hand-down (`board-station.py`'s messages/exit
codes, and `/harness-plan`'s no-ticket kickoff branch). One non-blocking completeness note on the
first; the second is adequately specified. Nothing here should block the operator's signature.

## Census — every surface the plan touches (`plan.yaml` `lanes.rows` + task `files:`)

| Surface | Task | Why it is / is not an end-user interaction surface |
|---|---|---|
| `.claude/skills/harness/bin/gh-sync.py` | T-01 | Existing CLI. This feature only adds an internal `feature.json` write plus one unspecified-wording print line on an unreadable-file path (item 6). No rendered surface; not one of the two named surfaces. Out of primary remit. |
| `.claude/skills/harness/bin/test-gh-sync.py` | T-01 | Test fixture, no output any operator reads. Out of scope. |
| `.harness/harness/docs/DECISIONS.md` | T-04 | Engineering record read by agents/operators as documentation prose, not an interactive surface with states/spacing/colour. Out of scope. |
| `.harness/harness/docs/DECISIONS-INDEX.md` | T-04 | Generated index, same nature as above. Out of scope. |
| `.claude/skills/harness-simplify/SKILL.md` | T-02 | New skill, agent-consumed procedure text (read by `harness-eng-lead` at point of use), not operator-interactive. Out of scope. |
| `.claude/skills/harness/SKILL.md` | T-03 | Orchestrator playbook, agent-consumed. Out of scope. |
| `.claude/commands/harness-plan.md` | T-03, T-06 | Read by the main session at the start of every live `/harness-plan` operator session — directly shapes what the operator sees and is asked. **In scope** — one of the two named surfaces (T-06's kickoff bullet). |
| `.claude/skills/harness/bin/board-station.py` | T-05 | New CLI whose stdout/stderr text and exit codes are read live by the operator during a planning session (`execution_mode: main-session-direct` context on the calling side). **In scope** — the other named surface. |
| `.claude/skills/harness/bin/test-board-station.py` | T-05 | Test fixture. Out of scope directly, though relevant to whether the gap below is gated (it is not — see below). |
| `.claude/skills/harness/bin/run-unit-tests.sh` | T-05 | Test-runner registration array, no operator-facing text. Out of scope. |
| `.harness/harness.json`, `.harness/factory/fleet.yaml`, `gh_board.py` | resolved_but_not_written | No content change (D-05: `set_station` called, not edited; `harness.json`/`fleet.yaml` ruled out of scope). Out of scope. |

This is a measured census against `plan.yaml`'s actual rows and files, not a prediction of absence.
No `DESIGN.md` exists for this feature and none is warranted — there is no rendered surface (no
html/css/tsx/jsx/vue/svelte anywhere in the touched set) for a spacing/colour/theme contract to
govern. The two questions below are the correct scope, not a broader Mode A pass.

## Question 1 — `board-station.py`'s operator-facing messages and exit codes: coherent?

Mostly yes, with one real but non-blocking completeness gap.

**Coherent parts, measured:**
- Exactly one non-zero exit path (missing/extra arg, non-positive-integer issue number → usage line
  on stderr, exit 2), stated explicitly as "the ONLY non-zero exit" (T-05 intent item 1). Every other
  path, including a caught `BoardError`, exits 0 — deliberate and already ruled settled (constraint:
  T-05 intent item 6 mirrors `gh-sync.py`'s existing parent-write pattern).
- The success line (`board-station: #<n> -> <station>`) and the `BoardError` line
  (`board-station: ERROR - ...`) both carry the tool-name prefix and both explicitly cite
  `gh-sync.py`'s established shape (`gh-sync.py:197` `print(f"gh-sync: parent #{rec['parent']} ->
  {station}")`, `gh-sync.py:199` `print(f"gh-sync: ERROR - {e}", file=sys.stderr)`). That mirroring is
  exact and coherent.
- The three-way failure taxonomy (caller error / environmental precondition / station-write failure)
  matches `gh-sync.py`'s own documented split (`gh-sync.py:19-30`), so an operator who already reads
  `gh-sync` output learns nothing new by shape.

**Gap found:** T-05 intent items 3 and 4 — the "no harness root found" line and the "no board
configured / sync off / no repo" line — specify only *that* a plain line prints, not its wording or
prefix. `gh-sync.py`'s own precedent for the parallel case carries the same `<tool>: ` prefix as its
success and error lines (`gh-sync.py:141` — `print("gh-sync: no github.board configured — station
writes are not attempted")`). T-05's intent requires the prefix for the success and error lines
(items 5–6, both citing "gh-sync.py's shape" explicitly) but is silent on it for the two informational
lines (items 3–4). That silence is a real, checkable gap in the message-format contract: an
implementer following the letter of items 3–4 could ship two of `board-station.py`'s four possible
output lines without the `board-station: ` prefix the other two carry, while the sibling tool this is
explicitly modeled on has no such inconsistency across its own equivalent lines.

This does not gate: `test-board-station.py`'s prescribed case labels ("...with no board configured
writes nothing and exits 0") assert behavior (no board write, exit 0), not exact stdout text, so no
verify clause would catch either choice. Per this role's gating rule, an unaddressed detail the
contract is silent on and does not forbid either resolution of is advisory, not a `must_fix`. Noting
it now is cheaper than a later reader spending time reconciling why two of four lines in the same tool
read differently.

## Question 2 — `/harness-plan`'s "no ticket is named" branch: well defined?

Yes, adequately. T-06's intent requires the literal phrase "no ticket is named," and requires the
branch state explicitly: "nothing is written and nothing is asked" — the non-happy-path is named, not
left to be inferred as an unstated default, which is exactly the completeness bar this role checks
for. Ordering is enforced by T-06's own `verify` (`k -lt t`, i.e., the kickoff bullet must precede the
plan-sequence line), so the branch cannot silently be positioned after the point where it would be too
late. Feedback on the happy path is visible to the operator for free: `board-station.py`'s own
success/error/skip line (Question 1's surface) prints during the run, so the operator is not left
guessing whether the move happened.

One thing genuinely goes unaddressed by this bullet, but it is a workflow-semantics question, not a
message/state-completeness one this lens governs: *how* "the operator names the ticket" is
recognized during a live session (a spoken ticket number in the initial ask, versus something the
grilling dialog must elicit) is not specified anywhere in the edited text, and grilling's own bullet
(`harness-plan.md:5-9`) does not mention tickets at all. I raise this as an open, non-blocking
question rather than a finding — it is a dialog-interpretation matter for whoever owns the grilling
flow, not a spacing/colour/state-completeness defect in the surface I audit.

## What went unjudged

Both named questions were judged. No dimension was skipped as "surface exists but not verifiable from
source" — everything here is markdown/CLI text, fully legible from source; there is no rendered-layout
or pixel-level claim this role cannot see.

## Digest fields — reasoning

- `severity_max: low` — the one finding (Question 1's prefix-convention gap) is advisory, does not
  gate any verify clause, and the contract permits either resolution — exactly the shape this role's
  gating rule says must not block.
- `must_fix: []` — nothing here should block the operator's signature.
- `cycles: 0` — clean first pass, no send-backs.

artifact: .harness/harness/features/FEAT-23-ship-flow-fixes/notes/review-harness-ui-reviewer-2026-08-17-2-uireview-validator.md
