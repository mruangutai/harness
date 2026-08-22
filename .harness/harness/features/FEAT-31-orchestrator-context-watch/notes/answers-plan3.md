# Operator answers — FEAT-31 plan, round 3 (2026-08-21)

Four rulings and one finding. Every one of them changes plan.yaml. `approval:` is still
`pending`, so no signature is being invalidated.

## A-1 — SC-01: `verify: automated` does NOT mean "runs in CI". Keep the criterion, keep the method.

The operator's ruling, verbatim: *"take it out of CI. that's wrong. when i say automated, i mean
that i want you, claude code, to run it for me when the time is right."*

The planner's Q1 premise was mine and it was wrong. No harness document couples `automated` to
`tests.yml`. `.claude/skills/harness-spec-driven/SKILL.md:155` says `automated` names its
`evidence:` test kind, and `.claude/skills/harness-brief/SKILL.md:83` only demands that the kind
have a runner. Neither mentions the CI job. So:

- SC-01 KEEPS `verify: automated`. It is not reclassified to `uat`.
- D-09's split still stands on its other leg — the check must not import the tool's own
  arithmetic, because that compares a function to itself.
- What changes is WHERE the live half runs: an agent runs it on demand, never `tests.yml`.

**AND THERE IS A HARD CONSTRAINT THE PLAN MUST RESOLVE, not restate.**
`.claude/skills/harness/bin/run-unit-tests.sh:40-51` is a drift detector: any `test-*.py` under
`bin/` that appears in neither `UNIT_SCRIPTS` nor `INTEGRATION_SCRIPTS` fails the ENTIRE suite with
`MISCONFIGURED`, whichever `--kind` is being run. That closes both easy doors:

- Register a live-orchestrator test → CI runs it → it reads `~/.claude/projects`, which does not
  exist on `ubuntu-latest` → red on every PR.
- Leave it unregistered → `MISCONFIGURED` → every other suite run dies.

Decide and record which side the live check sits on. Options seen from here, and the plan may
find a better one: the live half is not a `test-*.py` file at all (a differently-named script,
or a documented command in the task's `verify:`); or it is one file that skips-with-a-loud-reason
when the projects dir is absent — but a silent skip is the defect class this repo files tickets
about, so a skip must be a named, printed outcome, not an early return.

## A-2 — SC-14 second half: APPROVED, option 1. INV-17 globs and shape-checks every handoff note.

The criterion as written cannot go red, and this was verified at HEAD, not inferred:
`check-state.sh:592-593` builds handoff paths ONLY by looping `SEAM_NOTES[status]`, so a note with
any other stem is never opened; and `check-domain.sh:706`'s `RE_HANDOFF` already accepts
`handoff-[a-z0-9-]+\.md`, so writing a mid-phase note is already legal. Nothing to teach a seam
table, nothing that could fail.

The approved behaviour, and it SPLITS one question into two that are welded together today:

- INV-17 globs `notes/handoff-*.md` in each feature directory and applies the shape checks to
  EVERY file it finds — the four `HANDOFF_HEADINGS`, the 60-line cap, and T-10's new empty-body
  check.
- `SEAM_NOTES` is UNCHANGED and still answers the separate question of which notes are REQUIRED.
  Do not derive stems from status values; the comment at `check-state.sh:474` records that
  deriving matches on a case-insensitive filesystem and goes dark on Linux CI.
- A shape failure is a VIOLATION through the existing `bad.append` path at `:618`, not a warning.
  The "warn instead" variant was offered and rejected.

MIGRATION COST IS ZERO, measured, and the plan should not re-derive it blindly — but it MUST
re-assert it as a task receipt, because the gate's reach is retroactive by construction:
`check-state.sh` sweeps every feature directory on every run, so these files are read the moment
the glob lands. Measured at ddeebb5: 71 handoff notes; 3 carry non-seam stems —
FEAT-09-plan-time-route-check/notes/handoff-ship.md (56 lines), FEAT-22-docs-layout-migration/
notes/handoff-t09-rotation.md (50), FEAT-24-config-responsibility-split/notes/handoff-ship.md
(60). All three carry all four headings and are within the cap. FEAT-24's sits EXACTLY on 60, so
it has no headroom. None was checked against T-10's empty-body rule, which does not exist yet —
do that, and if any existing note fails, that is a finding to raise, never a licence to weaken
the check to make the tree green.

Note for whoever writes it: the FEAT-01/FEAT-02 literal exemption and the all-main-session-direct
exemption skip only the MISSING-note branch at `:594`. Once a file exists the shape check at
`:614` runs regardless. The glob does not change that rule; it widens which files reach it.

This lands in the SAME `check-state.sh` INV-17 block that T-10 already edits, and it is
enforcement-layer work under DEC-174 — so it is `main-session-direct`, like T-10. Fold it into
T-10 or add a sibling task; say which and why. Its red proof follows T-10's rule: a mutant copy
located by a marker comment, the mutation ASSERTED APPLIED before anything runs, and a COUNT of
INV-17 lines compared, never an exit status.

## A-3 — SC-15: APPROVED as T-10 plus a UAT re-verify.

T-10 ships as planned: the automatable half is INV-17 rejecting a handoff whose four headings are
present but whose `## Next` body is empty. The live half — a fresh orchestrator's first dispatch
matching its predecessor's `## Next` — is graded once by hand against a real successor. Record it
so the criterion is not silently reported as fully automated.

## F-1 — A DEFECT THE PLANNER DID NOT RAISE. T-07's test file is misclassified, and it makes every
`evidence: integration` claim in this brief false for that file.

Verified at ddeebb5 by classifying both filenames against `.harness/harness.json`'s `test_kinds`
`detect` globs: `test-context-watch.py` → unit (correct), and
`test-context-watch-cli.py` → **unit**, NOT integration.

The cause: `test_kinds.unit.detect` includes the glob
`.claude/skills/harness/bin/test-*.py`, which matches everything; `test_kinds.integration.detect`
is an EXPLICIT filename list, and T-07 never adds itself to it. So `run-unit-tests.sh --kind
integration` would run the file while the qa matrix reads it as a unit test.

This is SILENT. `run-unit-tests.sh`'s drift detector reads its own two arrays and never reads
`harness.json`, so nothing catches the disagreement.

Fix: add `.harness/harness.json` to T-07's `files:` and its intent, appending the filename to
`test_kinds.integration.detect`. Then check EVERY other task in this plan for the same omission
rather than fixing only the one named here. This is the same root cause as FEAT-30's open Q5 —
the unit glob claims far more bin/ scripts than `--kind unit` actually runs — so if the plan can
close the class rather than the instance, say so and cost it; if it cannot, say that instead of
widening scope.

## Standing constraint for this round — read before you write plan.yaml

Issue #628: a `plan.yaml` write is a whole-file write with no merge path, and THIS feature's own
planning run is the recorded incident — two `harness-pm` spawns 63 seconds apart turned a 14-task
plan into a 1-task plan, and the overwritten draft does not parse. Exactly ONE pm writes
plan.yaml this round. Do not spawn a second, do not run two writers concurrently, and do not
re-read the file to "check" it while another context may be writing.

`approval:` is the MAIN SESSION's mapping and nobody else's. Carry it forward unchanged.

---

# Round 3, second attempt — corrections and two more rulings (2026-08-21)

The first attempt DIED to machine sleep before any write. `plan.yaml` is byte-identical to
7299669, checksummed, and `runs/plan3-product/state.yaml` has been corrected from `in_flight`
to `died` by the main session. **There is no result to collect.** Do not try.

Its pre-dispatch acceptance criteria in `runs/plan3-product/digest.md` SURVIVE and are re-used
verbatim — nine of them, written before the pm was dispatched precisely so they could not be
fitted to a return. Judge this round against those, not against new ones.

## Corrections to the rulings above. Every one was measured by the dead round at HEAD 7299669.

**C-1 — A-1's constraint has a clean escape, and it is the intended door.** The drift detector
loops `for f in "$BIN_DIR"/test-*.py`, so a `bin/` file whose name does not match that glob never
reaches it. The "skip loudly" alternative A-1 offered is the WEAKER door and should not be taken:
`tests.yml:78,84` runs both kinds as required steps, so a printed skip inside a required step is a
green suite that verified nothing — this repository's most-filed defect shape.

**C-2 — F-1 is EIGHT files, not one, and the operator has ruled on the class.** Eight of the
twelve entries in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` are absent from
`test_kinds.integration.detect`, so each classifies as `unit` via that kind's catch-all
`.claude/skills/harness/bin/test-*.py`. `test-upgrade-config.py` is among the eight and T-05
already edits it.

RULING D-4: **fix all eight, AND add a check so the two lists cannot disagree silently again.**
Not the instance, not the eight alone. The check is the point: today
`run-unit-tests.sh`'s drift detector reads its own two arrays and NEVER reads `harness.json`, so a
mismatch between the arrays and `test_kinds` is invisible to every gate. Whatever form the check
takes, it must be able to go RED — assert the mismatch is DETECTED, not that a command exited
non-zero.

**C-3 — A-2 carries a double-report risk the answers file did not name.** One loop at
`check-state.sh:592` currently BOTH builds the required-note path AND shape-checks it. Adding a
glob pass without first moving the shape check out of that loop would report every seam-stem
failure twice. Resolve it by ordering or by structure, and say which.

**C-4 — SC-14's APPROVED wording must change, and the operator must see the diff.** BRIEF.md
lines 186-190 assert the mid-phase acceptance is proven "by a test that fails before INV-17's seam
table learns the mid-phase stem". That mechanism is exactly what A-2 FORBIDS: `SEAM_NOTES` stays
unchanged and stems are never derived. Rewrite it MINIMALLY, leave `## Approval` byte-identical,
and list every changed line in the receipt.

**C-5 — A-2's open sub-question is CLOSED, with no finding.** None of the three non-seam-stem
notes fails T-10's not-yet-existing empty-body rule: their `## Next` bodies hold 13, 6 and 8
non-blank lines. Nothing to migrate, nothing to raise.

**C-6 — TWO CITATIONS IN THE RULINGS ABOVE ARE CHECKOUT-DEPENDENT, and one is wrong for your
checkout.** `RE_HANDOFF` is at `check-domain.sh:665` in this worktree, not `:706`; `:706` is its
line in the main checkout, which sits on a different branch. `SEAM_NOTES` is at
`check-state.sh:495`. Prefer the symbol name over the line number where you can.

**C-7 — EVERY COUNT IN A RECEIPT MUST NAME ITS CHECKOUT OR SHA.** The handoff-note corpus is 71
notes in the main checkout and 69 in this worktree. It reconciles exactly: FEAT-30's three notes,
present in main and absent here, minus FEAT-31's own `handoff-plan.md`, present here and absent
there. A receipt asserting a bare "71" reads as FAILED to anyone re-running it elsewhere. This
rule applies to every number in the plan, not just this one.

## Two questions the dead round raised that the operator has NOT answered

Carry them forward in your return; do not resolve them yourself.

- **Q-A: is `harness.json`'s `test_kinds` enforcement layer under DEC-174?** It is config CONSUMED
  BY gates rather than a hook or gate script, and DEC-174 am.4's list is non-exhaustive. This
  decides D-4's `execution_mode`. `check-domain.sh --resolve` grants `.harness/harness.json` to
  `harness-dev-ops` and T-03 already edits it as `team`. The sibling question was raised for
  `run-unit-tests.sh` in an earlier round and never answered.
- **Q-B: is "explicit list beats catch-all glob" written down anywhere?** Four files already sit in
  both `unit.detect` and `integration.detect` and are treated as integration, so precedent is
  clear — but the dead round could find it STATED nowhere, and there is no programmatic classifier.
  D-4's fix rests on that precedence, so say whether it should be written down.

## The collection problem is NOT yours to solve, and it is not blocking you

The dead round returned it as blocking: an orchestrator whose turn ends while a lead still runs
cannot collect it, because there is no wait primitive that terminates and no message tool to reach
a running agent. That is real and it is filed for the operator. It does NOT block this round: the
chain is dead, `ListAgents` shows no live subagent, and nothing is waiting to be collected.

What it means for you PROCEDURALLY: dispatch pm EARLY in your turn, not late. A pm dispatched near
the end of a turn cannot be collected and its work is lost — which is what happened twice.

## The single-writer constraint still stands, and it is the same one

Issue #628 is NOT fixed. Exactly ONE `harness-pm` writes plan.yaml this round. Do not spawn a
second for any reason — if the return falls short, report it as a finding, which is what the
pre-written criteria already instruct. `plan.yaml` IS committed at 7299669, so an overwrite is now
recoverable with `git checkout`; that is a mitigation, not a fix, and it is not licence for a
second writer.
