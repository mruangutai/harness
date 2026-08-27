# STATE

## Current

- feature: FEAT-42-one-root-resolver. phase VALIDATE COMPLETE, mission ship. status Review.
- review_sha PINNED at `9d12e3a` = HEAD (INV-6). Zero SOURCE files dirty at the pin.
- GitHub mirror at Review: parent #870 and all 20 sub-issues #871-#890.
- cycles_used 6 of 10, runs 11 of 20. Both inside budget. ONE cycle spent in this whole phase —
  the goal-check lead's first pass graded the wrong scope on SC-09 and was sent back. The qa gate,
  the docs sweep and the review panel were clean first passes.
- BRIEFING WRITTEN, and it is the terminus of this run:
  `notes/ship-review-2026-08-27-validate.md` (+ rendered `.html`). No PR, no merge, nothing
  committed. The operator decides ship / fix first / re-scope / stop.

VERDICT OF THE PHASE: the feature MEETS ALL ELEVEN SUCCESS CRITERIA and the blocking qa gate is
GREEN, and the review panel FAILED it on ONE HIGH finding. `.omp/extensions/harness-hooks.ts:142`
does `spawnSync(join(cwd, BIN, script))` with `BIN` a RELATIVE ".agents/skills/harness/bin", so the
OMP host selects the gate SCRIPT ITSELF from caller-supplied `ctx.cwd` — six gates across eleven
call sites, in a file this diff edited (0a5bd49, T-20), with zero test coverage. #556 substituted an
imported MODULE; this substitutes the WHOLE GATE. `.omp/**` resolves to NOBODY, so no squad can fix
it: it is main-session-direct. Second repair recommended with it: `test-check-plan-routes.py:453-454`
asserts `"IGNORING it" not in stderr` and that string occurs EXACTLY ONCE in `.claude/skills` — in
the assertion itself. The case is green, counted in every zero-failure claim, and CANNOT FAIL.

HOST SPLIT, and I stated it wrong once before the panel corrected me. I measured that no line of
this branch's enforcement code had executed against a live agent, by dispatching a governed agent
with no `HARNESS-FEATURE:` line and watching it be ADMITTED where this branch's guard refuses at
exit 2. That is sound but CLAUDE-CODE-SPECIFIC: hooks resolve through `${CLAUDE_PROJECT_DIR}`, the
main checkout at 3952814. Under OMP the gate is selected from the cwd, so an agent in a worktree
runs THAT BRANCH's gates. Consequence bigger than exploitability: under the canonical host DEC-174's
carve-out is enforced by CONVENTION ALONE.

VERIFIED BY ME at 9d12e3a, independent of any squad:
- SC-01: 0 occurrences across 0 files over 1669 tracked files; discriminating (21/17 at 3952814).
  Presence half is METHOD-SENSITIVE: `.py`+`.sh` gives 23 importers, strict `.py` imports alone
  gives 14, below its own floor of 16. It passes on the wording; worth knowing.
- SC-04: each deleted symbol checked SEPARATELY, all 0. Survivors intact at `harness_boundary.py:515`
  and `post-merge-sweep.sh:64`.
- `harness-hooks.ts` finding re-derived line by line before it entered the briefing.
- `"IGNORING it"` occurs exactly once tree-wide — the tautology confirmed.
- No production file under `bin/` reads `CLAUDE_PROJECT_DIR`; `python3 -P` on 19 launches / 10 files.
- `check-state.sh` exit 0, 0 violations.

## Open Questions

- Q10 (OPEN, non-blocking): `resolve_root` probes with `os.path.isfile`; the deleted
  `check-plan-routes.py` probe used `os.access(..., os.R_OK)`. An unreadable-but-present
  `team-config.yaml` now flips from "not a root" to "is a root". No site is known to reach it.
- Q15 (OPEN, non-blocking, harness defect): `bash-write-guard.sh` refuses a command whose PROSE
  body contains an angle-bracket placeholder or an ASCII arrow, parsing it as a redirect. Three
  occurrences on this feature. Needs its own ticket.
- Q16 (OPEN, non-blocking, harness defect): `gh-sync.py` has `start-task` and no per-task finish
  command, so only `cmd_ship` moves a card to Done and every intermediate move is a direct
  `board-station.py` call. Needs its own ticket.
- Q20 (OPEN, non-blocking, harness defect): `validate-digest.py` releases a returning agent's
  claim (step one) and THEN refuses the return on children-in-flight, so a blocked lead runs on
  unclaimed and is invisible to `dispatch-guard`. T-17 does NOT close it: the session filter
  ignores FOREIGN-session children, and this lead's are same-session and live. Needs its own
  ticket.
- Q24 (NEW, non-blocking, record fidelity): T-21 has no GitHub sub-issue. Every other task has
  one, and `gh-sync.py open` is the command that would create it. Creating an issue is
  outward-facing, so it waits on the operator.
- Q25 (NEW, non-blocking, decision hygiene): DEC-174 amendment 4 enumerates the enforcement layer
  by filename. This feature changed every file on that list and added none, but the list has gone
  stale before and nothing checks it. Ruled worth a ticket earlier and never filed.
