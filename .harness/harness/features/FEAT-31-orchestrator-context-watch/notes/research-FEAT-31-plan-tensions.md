# Research — FEAT-31 plan tensions, resolved with measurements

**BLUF: I did not write `plan.yaml`. A concurrent writer owns it and its findings beat mine on four
points.** I wrote a complete `plan.yaml` at ~06:05 on 2026-08-21; it was overwritten at 06:06:20 by
another author (surfaces I never wrote — `test-context-watch-cli.py`, `upgrade-config.py`,
`templates/harness.json`), and `notes/probe-hook-delivery-channel.md` appeared in the same window.
Two authors alternately overwriting one approval-gated artifact means whichever writes last reaches
signature unreviewed, so this escalates rather than resolves. Their findings 1, 2, 4 and 5 correct
things my draft got wrong (delivery channel, feature attribution, the missed `templates/harness.json`
surface, DEC-187 over DEC-163). What follows is only what their notes do **not** cover.

## T-A — SC-07's self-contradiction: diff-scope against **git HEAD**, not against disk

Disk-prior scoping (the candidate as phrased) fails. `check-domain.sh` has two routes and they see
different content:

- PRE blocks `Write` only (`check-domain.sh:981`), and there the file on disk is the prior version.
- POST reads what landed (`check-domain.sh:993`), so disk holds the **new** content. Disk-prior there
  grandfathers every entry and the POST route enforces nothing — and POST is the only route an
  `Edit`-append reaches.

So: `legacy_ids` = the ids of `runs` entries in `git show HEAD:<path>` that **themselves lack the
field**; require the field on every entry whose id is not in that set; empty set on any git failure
(fails closed). `problems_for_text(text, display)` gains an optional third parameter; `check-domain.sh`
must thread the absolute path through, and its `targets` list is a 3-tuple built at three sites
(`:983`, `:995`, the sweep) and consumed at `:1075` — widen all three, uniformly, because that file's
own comment records mixed arity as a measured defect.

**What it does not catch:** (a) presence, not truth — a placeholder id passes; (b) a new run reusing a
legacy id is grandfathered; (c) a `feature.json` whose legacy entries were never committed loses
grandfathering — safe today, verified: 372 `runs` entries across the tracked `feature.json` files carry
exactly `id`, `squad`, `verdict` and nothing else; (d) an `Edit` append is caught only post-hoc.

Keep `required: [id, squad, verdict]` in `feature-schema.json`. Adding the field to `required` is what
breaks the no-migration ruling; the diff rule is the single enforcement point.

## T-C — SC-14's second half is already true **twice over**, not once

- `check-state.sh:593` is the only place a handoff path is constructed, from `SEAM_NOTES[_status]`, so
  `notes/handoff-<anything-else>.md` is never opened, demanded or rejected.
- **Not previously named:** `check-domain.sh:665` `RE_HANDOFF` is
  `^\.harness/[^/]+/features/[^/]+/notes/handoff-[a-z0-9-]+\.md$` — the write-time shape gate already
  accepts **any** lowercase stem with no whitelist. So a mid-phase stem is accepted at both gates today
  and no test can redden on acceptance.

**Discriminating substitute:** INV-17 globs `notes/handoff-*.md` and shape-checks each note it finds
(four headings, 60-line cap) while `SEAM_NOTES` keeps deciding which are *required*; move the shape
check out of the `SEAM_NOTES` loop so a required note is reported once. Fixture: a well-formed
`handoff-plan.md` plus a malformed `handoff-mid-build.md` → 0 lines naming it before, exactly 1 after.

**Verified safe:** all 68 `handoff-*.md` currently on disk pass both rules, so the widening adds zero
findings to the current tree. The real gap it closes is a note that never passed a `Write`/`Edit` route
(git checkout, merge) — which `check-domain.sh` structurally cannot see.

**The mutation seam exists already:** `test-check-state.py:16` reads `CHECK_STATE_BIN`, and `:1815`
already copies the script plus `harness_yaml.py` into a temp bin dir and runs the copy. So "delete the
one line carrying the literal `handoff-*.md`, assert it is present in the original and absent in the
copy, run both against one fixture, compare line counts" is a two-command proof, no edit to the shipped
script. Assert on the **count** of lines naming the note, never on exit status — exit status cannot tell
this finding from any other violation in the same run.

## SC-15 cannot be met as written

`verify: automated / evidence: integration` over "a fresh orchestrator does the work the predecessor had
decided on" asserts **agent behaviour**. `unit` and `integration` are the only kinds with a real `cmd`;
neither runs an agent. The strongest automated surrogate is "the handoff's `## Next` is non-empty and
cites a T-NN", which does not prove a successor acts on it. It is a UAT step, or it is unmet.

## Two mechanical constraints any plan must carry

- A new `test-*.py` under `bin/` forces an edit to `run-unit-tests.sh` (drift detector, lines 17-51) —
  and if it is an integration test, a second edit to `test_kinds.integration.detect` in
  `.harness/harness.json`, which is an explicit pipe-separated file list, not a glob.
- CI is `ubuntu-latest` with no `~/.claude/projects`, and zero existing tests read it. Every fixture
  must be `tempfile.mkdtemp()` and every root passed explicitly, or the required `integration` context
  reds and blocks every PR.

## The cwd slug rule, verified exact

`"/".replace -> "-"` then `"."replace -> "-"`. Confirmed by running it:
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/fix-harness-tooling-backlog` produces
`-Users-molchairuangutai-GitHub-harness--claude-worktrees-fix-harness-tooling-backlog`, and that
directory exists under `~/.claude/projects/`. Assert it as a pure-function equality on those two
literals — no filesystem, CI-safe, and it reddens on any change to the transform.

## Open, for whoever owns the plan

- Two authors on `plan.yaml`. Mine is gone; theirs did not parse at 06:07 (`line 71, column 55`, a
  `": "` inside a plain scalar — the DEC-182 failure mode). One author must be stood down.
- SC-01's automated half cannot run in CI as written ("against a live orchestrator"). Their finding 3
  shows the live half is demonstrable by hand, which makes it a UAT step; the CI half must be a
  generated fixture whose naive and corrected peaks are provably distinct, with the recomputation
  written inline and importing nothing from the tool.
