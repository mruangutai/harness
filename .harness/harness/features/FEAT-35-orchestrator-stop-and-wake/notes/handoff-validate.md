# Handoff — FEAT-35, validate → ship — written at a2a373b, seq-5

## Next

**Validate is COMPLETE at its exit predicate: panel PASS, `must_fix` empty.** Two acts remain and
both are the main session's, not a run anyone can dispatch: (1) record SC-03's grade — Clause A is
met and in-repo, Clause B rests on your own live-orchestrator measurements that no agent can vouch
for; (2) re-sign for the second SC-03 amendment. Then commit the `.harness/` state, open the PR
(`gh-sync.py closes` supplies `Closes #751`), merge, take acceptance, run `ship`. **Do not dispatch
another validator run** — nothing is left that a reviewer can add.

## Trust

- SC-01/02/04 re-confirmed at the new pin AND shown to discriminate: 9/9 pass at `a2a373b`, 9/9 fail at `569d417` — `runs/2026-08-24-04-validator/digest.md` — verified-at a2a373b
- SC-06 RE-GRADED PASS; its c0 verdict covered `SKILL.md:99-138`, the region both fix commits edit, so the re-grade was necessary rather than ceremony — same digest — verified-at a2a373b
- The fix at `a2a373b` introduced NO regression; unit suite exit 0, 44 files, `test-orchestrator-playbook.py` ALL PASS — same digest — verified-at a2a373b
- SC-03 splits by verifier at `BRIEF.md:98-117`; Clause A met (c2 run), Clause B rests on `agent-ad292e24ec60c589b.meta.json` and `current=330,527 peak=330,527 entries=149` — verified-at a2a373b
- **MED, in the calibration text this pin added**: `SKILL.md:105-107` says handing off "stops being optional" at ~2x, three lines after `:102` "the threshold ADVISES … the decision is yours (DEC-198)". **I read both lines myself.** Not a gate — nothing enforces it — so `BRIEF.md:57` is not breached in letter — verified-at a2a373b
- **LOW**: `SKILL.md:104-105` embeds a dated operator quote and a token figure; REQ-07 exists to keep measurements in `DECISIONS.md`. Both findings sit in five lines, so ONE editing pass fixes both — verified-at a2a373b
- `## Approval` reads `2026-08-24`, written BEFORE the second SC-03 amendment — same date, so the record cannot show the gap — verified-at a2a373b
- `gh-sync.py closes` prints `Closes #751`; `parent_origin` stays `None` by operator ruling — verified-at e0ae671, unchanged since

## Dead ends

- Do not dispatch another validator run — panel PASS, `must_fix` empty, and Clause B is unreachable by any agent — verified-at a2a373b
- Do not grade SC-03 Clause B below the main session — `context-watch.py:53/:303-304` filters every non-orchestrator agentType — verified-at a2a373b
- Do not attempt SC-05 pre-merge — unsatisfiable by construction; obligation owner is the main session on the next build/validate phase — verified-at a2a373b
- Do not set `parent_origin: created`; do not write `base` into feature.json; do not re-file #803/#804/#805/#806/#808/#810 — verified-at a2a373b
- Do not git-restore under `runs/` — gitignored (`.gitignore:7`); the `-01-validator` digest is a content-faithful context reconstruction, not byte-identical — verified-at a2a373b

## Working set

- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/notes/ship-review-2026-08-24-validate.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/runs/2026-08-24-04-validator/digest.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/BRIEF.md`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/feature.json`
- `.harness/harness/features/FEAT-35-orchestrator-stop-and-wake/notes/answers-validate-2026-08-24.md`
