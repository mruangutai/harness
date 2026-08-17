# Code review — FEAT-23-ship-flow-fixes — panel validator — pin `490c37c`

## Verdict: PASS

Stage 1 (spec compliance) clean: every changed file traces to a REQ/D, no scope creep found, all
inspected SCs hold at `file:line`. Stage 2 (quality): one low-severity observation, no must_fix, no
new findings above the corroborated one already routed to pm. `severity_max: low`.

## 1 — the `83e769b..490c37c` delta, measured

`git diff 83e769b..490c37c --stat`: `board-station.py` (+2/-2), `test-board-station.py` (+3/-2), and
one new receipt file (all-prose). Read in full: both code-file hunks touch only a comment sentence
(`board-station.py:32-33`) and two comment lines (`test-board-station.py:75-77`) — replacing "item
1's exit contract" / "item 6's widened except" with "the EXIT CONTRACT paragraph above" / "the
module docstring's EXIT CONTRACT paragraph", after T-02/T-03 restructured the module docstring's
prose into named sections. **No executable line, assertion, fixture, or import changed.** The
receipt at `notes/receipt-harness-backend-dev-2026-08-17-10-simplify-eng.md` claims the same and its
claim is independently confirmed here, not taken on trust. The qa gate's green result at `83e769b`
(`notes/qa-2026-08-17-9-qa-validator.md`) transfers cleanly to the pin — nothing it certified moved.

## 2 — T-01's fail-open shape

`cmd_ship` (`gh-sync.py:744`) and `cmd_abandon` (`:682`, symbol-cited per DEC-196's own convention
since T-01 shifts line numbers): `_record_status` is confirmed the literal last statement of each
function, after all `gh()` calls and prints. `cmd_ship`'s early exit is `rec["milestone"] is None`
(single condition); `cmd_abandon`'s is `rec["milestone"] is None and not rec["issues"]` (conjunction)
— confirmed by reading both guards at `:637-648` and `:707-716`. The reasoning holds: `skip()` calls
`sys.exit(0)`, so reaching `_record_status` structurally proves neither exit fired, and re-gating the
write on a milestone-only guard would wrongly skip `Abandoned` in the milestone-less-but-issues-held
case — exactly what `test-gh-sync.py`'s `tmpE` case (`"abandon with no milestone but WITH issues
still records status Abandoned"`) is built to catch.

**Nothing else in `gh-sync.py` asserts something the change falsified.** Both docstrings' "feature.json
is untouched" sentence was corrected in both `cmd_ship` and `cmd_abandon`; the stale test comment in
`test-gh-sync.py:625-626` ("cmd_abandon must write no receipt") is also corrected. A full-file grep
for `untouched`/`writes no receipt`/`no receipt` at the pin turns up only `save_recorded`'s own
(still-true) atomic-write description — no orphaned claim remains.

**One low-severity observation, not gating.** `_record_status`'s read-failure path (`OSError`,
`ValueError`, non-dict `doc`) is explicitly non-raising per task intent item 6. Its *write*-failure
path is not: `_atomic_write` re-raises on any `BaseException` from the tempfile/fsync/replace
sequence, and no caller in either `cmd_ship` or `cmd_abandon` catches it. If that raises (e.g. a
disk-full or permission error in the feature directory, immediately after the milestone/parent close
already succeeded on GitHub), the operator sees a traceback rather than a clean exit, and
`feature.json` is left non-terminal while GitHub reads terminal — the same INV-26 mismatch this
feature exists to close, reached by a different, much rarer trigger. This is not a regression:
`save_recorded`'s six call sites (`:546` onward) already have this exact shape and none of them catch
it either, so T-01 reused an established convention rather than introducing a new gap. Not a
must_fix — flagged for awareness only, at `low`.

## 3 — `board-station.py` fail-open audit

Every non-usage-error path returns 0, matching the documented contract. Traced each: harness-root
probe (`:73-79`, walks up, environmental miss -> print+return 0), `harness.json` read (`:85-97`,
unreadable/non-dict -> print+return 0), `github` block / `sync` / `repo` checks (`:99-109`,
environmental miss -> print+return 0), `gh_board.load_board` (`:111-114`, `None` -> print+return 0),
and the board write itself (`:116-120`, broad `except Exception` -> stderr `ERROR -` line + return
0). The one non-zero exit is the usage-error branch (`:61-67`), which correctly precedes every
environmental check.

`load_board`'s `None` return is overloaded — it means both "the station feature is genuinely not
configured" **and** "the config is malformed" (a typo'd `owner`/`station_field`/`number` key
collapses to the same `None`, per `gh_board.py:43-54`, unmodified by this diff). A caller cannot
distinguish "off on purpose" from "off by typo" from the return value alone. This is pre-existing
`gh_board.py` behaviour that `board-station.py` inherits by calling an unmodified function
(plan.yaml's `resolved_but_not_written` row confirms `gh_board.py` is read-only in this feature) —
not a defect T-05 introduced, and not something T-05's scope licenses touching. Noting it because it
is exactly the fail-open shape this review hunts for, but it does not gate this diff: the ambiguity
is inherited, undisturbed, and outside this feature's fix surface.

## 4 — docs vs. code: DEC-195 / DEC-196

DEC-195 states the apply's surface-ownership condition **wherever it states the apply**, confirmed
by reading the entry (`DECISIONS.md:5970+`): the "position, build flow" paragraph itself carries
"whose findings are applied only where the domain guard grants the touched file to a specialist,"
and the dedicated "apply is conditional on surface ownership" paragraph restates it in full with the
NOBODY-region scope. No paragraph in the entry states the apply without the condition — the check
this item asked for holds.

DEC-196 avoids the plan.yaml D-05 `because:` error already known and routed to pm (that clause calls
`feat_dir` "argv1"; the code's second positional). DEC-196's own text says "`gh-sync.py`'s `main`
takes the feature directory as a positional argument" without an index claim — confirmed accurate
against `gh-sync.py:777` (`cmd, feat_dir = argv[0], argv[1]`) as read. `board-station.py`'s own module
docstring likewise correctly cites `argv[1]`. Neither carries the plan's error forward into shipped
text.

Index regeneration confirmed clean at the pin: `gen-decisions-index.py --stdout | diff -` against
`DECISIONS-INDEX.md` produces no output. All four `DEC-195`/`DEC-196` lineage references (DEC-86,
DEC-107, DEC-118, DEC-174, DEC-186, DEC-192) resolve to real entries.

## 5 — T-03/T-06 playbook fidelity

`harness/SKILL.md`: the SIMPLIFY paragraph is inserted after the DEC-118 sentence closing the qa-gate
line (that sentence left intact, not split) and before the `review_sha` pin sentence — matches T-03's
"anchors are not adjacent" trap description exactly. `harness-plan.md`: the KICKOFF bullet sits after
the step-zero grilling bullet and before the Target-state bullet (line-order confirmed), and the
Target-state line carries T-03's simplify clause between "squad plans," and "eng-lead reviews
architecture" byte-identically preserved (both anchors occur exactly once, confirmed by grep count).

Branch coverage: the KICKOFF bullet states both branches — named-ticket (`board-station.py
<issue-number> Plan`, "before the BRIEF work begins") and the no-ticket case, using the literal phrase
"no ticket is named" the task's own verify greps for. The sequencing an agent would actually follow
is coherent: grilling produces (or fails to produce) a named source ticket, KICKOFF acts on it (or
not) before BRIEF work starts, then the plan sequence (now including the plan-surface simplify pass)
runs. No gap between what the prose describes and what a session following it would do.

**Corroboration, not new:** independently re-confirmed `harness-simplify/SKILL.md` carries zero hits
for `ceiling of one`, `delete or weaken`, and `one fix`, while `harness/SKILL.md` carries the paired
bound language inline in the SIMPLIFY paragraph. Matches the dispatch's pre-flagged, already-routed
item — recorded here as corroboration per the dispatch's own instruction, not filed as new.

## 6 — spec-compliance-first discipline

No SC verdict table built (pm's goal-check owns that against this pin). Every task's files were read
against BRIEF requirements and plan.yaml decisions before any quality judgement was formed; no
scope-creep or omission found. `run-unit-tests.sh --kind unit` re-run independently at the pin: all
16 scripts green including `test-board-station.py` (8/8), corroborating rather than re-litigating the
qa gate.

## Findings summary

| # | Severity | Location | Note |
|---|---|---|---|
| 1 | low | `gh-sync.py:445-466` (`_record_status`) / `:420-441` (`_atomic_write`) | Write-failure path (not read-failure) is unhandled and re-raises; on a rare disk error immediately after GitHub's close succeeds, reproduces the INV-26 mismatch this feature exists to close. Inherited from `save_recorded`'s existing convention, not introduced by T-01. Not a must_fix. |
| 2 | info | `gh_board.py:43-54` (unmodified) | `load_board` collapses "not configured" and "malformed config" to the same `None`, inherited by `board-station.py`. Pre-existing, out of this feature's fix surface — noted, not filed. |
| 3 | info | `.claude/skills/harness-simplify/SKILL.md` | Corroborates the already-routed pm finding: the skill carries neither the "delete or weaken" nor "ceiling of one" apply bounds that `harness/SKILL.md` states. Not new — in flight per dispatch. |

No `must_fix`. `severity_max: low`.
