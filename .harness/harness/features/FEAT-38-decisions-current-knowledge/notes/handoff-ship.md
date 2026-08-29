# Handoff — FEAT-38-decisions-current-knowledge, ship → REPLAN — written at 48bbe7e

## Next

**Do not dispatch a build, a gate, or the UAT. The ship trajectory is superseded.** The operator
ruled REMOVE COMMAND EXECUTION: `check-decision-claims.py` must stop running commands taken from
`DECISIONS.md`. That is **new scope against an approved plan** and must not be implemented under it.

The decided next action is a **planning cycle**, not a build one: take
`notes/replan-remove-command-execution.md` to the operator, settle its three questions, then run
`/harness-plan` to amend `BRIEF.md` (REQ-08, SC-09) and `plan.yaml` (D-10, T-03, T-20, T-21, and
T-18/T-19 only if the script is renamed). Approval is the operator's; nobody else signs.

**Do not present the UAT.** SC-13 asks the operator to accept entries whose governing convention
(`DEC-205` rule 6b) is about to be rewritten. Accepting it now buys a signature on text with a known
expiry.

## Trust

- All 23 tasks `done`; every automated gate green at `48bbe7e` — qa PASS, panel PASS (`severity_max: med`, empty `must_fix`), goal-check 12/13 — `notes/qa-2026-08-29-11-validator.md`, `notes/review-harness-*-c2.md`, `notes/research-FEAT-38-goalcheck-48bbe7e.md` — verified-at 48bbe7e
- **All 11 live claim markers are `grep` against one named file** — 10 `grep -F <literal> <path>`, one capped line count — so a non-executing `contains`/`max_lines` vocabulary covers 11 of 11 — `git show 48bbe7e:.harness/harness/docs/DECISIONS.md | grep -n '<!-- claim:'` — verified-at 48bbe7e by me
- Exactly five tracked files outside the feature dir reference the checker — `git grep -ln check-decision-claims 48bbe7e` — verified-at 48bbe7e by me
- `DECISIONS.md:6290`'s marker asserts `ALLOWED_FIRST_TOKENS = {"git", "grep"}` and is **self-referential** — it goes red on the first run after the redesign and must be removed, not translated — verified-at 48bbe7e by me
- `CLAUDE.md` is 12 lines and the numeric marker's `-m 81` cap is what makes its **substring** comparison safe by accident — verified-at 48bbe7e by me
- `plan.yaml` is UNTOUCHED by the amendment work — the dispatch was skipped before any edit; `git diff` on it is empty — verified-at 48bbe7e
- `cycles_used` 11 of `max_total_cycles` 10 — crossing accepted by the operator, bound deliberately not raised, neither number altered — `feature.json` — verified-at 48bbe7e
- SC-11's 15/15 meaning-preservation is INHERITED from the cycle-0 panel and pm at `2557950`; no entry was re-derived in this segment — **UNVERIFIED at my own tier**
- The proposed `contains`/`max_lines` design is **mine, unreviewed by any security lens.** It is a recommendation in a planning note, not a validated design — **UNVERIFIED**

## Dead ends

- Do not implement backlog **B-8** (clear `GIT_CONFIG_*`, route `git grep` through the file-option check, refuse option-like tokens everywhere) or **B-11** — both harden or annotate the execution path being deleted. Implementing then deleting is pure waste — verified-at 48bbe7e against the ruling
- Do not patch **B-10**'s prose — `D-10` and `DEC-205` rule 6b are rewritten wholesale by the replan
- **B-9 is NOT a dead end and is now more important** — no one has swept the rest of `bin/` for scripts building an argv from document or config text; the ruling is about a class, and the claims checker may not be the only instance
- Do not re-render `ship-review-2026-08-29-16.html` to fix its blank code block — `render-brief.py:131` strips `<!--.*?-->` across the whole document BEFORE fenced-block handling, so it reproduces every time. The `-18` briefing works around it; the bug is B-19 — verified-at 48bbe7e by reproducing
- Do not root a citation sweep at `.agents/**` (symlink onto `.claude`, traverses nothing) and do not use `git grep -E … \b` for a decision id (git's ERE has no `\b`). Both return a confident clean tree while sites stand — verified-at 48bbe7e
- Do not `sed -i` under the feature dir — the write guard refuses and directs you to the Write tool, correctly. Redirects are blocked too, so an "append" to an existing note means rewriting it whole — verified-at 48bbe7e
- Do not read a bare `PASS` total as comparable across receipts — one tree reads 1117, 1002, 1285 or 1150 by counting expression. Exit status and `^FAIL` count are the comparable numbers (B-15) — verified-at 48bbe7e
- Do not treat `runs/**` digests as durable — `.gitignore:7` ignores them; they die with the worktree. Durable evidence is in `notes/` — verified-at 48bbe7e

## Working set

- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/replan-remove-command-execution.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/research-verify-block-defects.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-29-18.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/BRIEF.md`
- `.harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml`
