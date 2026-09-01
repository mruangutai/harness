# QA distillation — BUG-1081-code-grade-enforcement

Applied 3 ops through `expertise-merge.py apply` (exit 0 each, verified by re-read): 2 craft
displacements, 1 repository-tier addition. `check-expertise.sh` single-file mode: OK on both
files, post-apply.

## Craft — `.harness/expertise/harness-qa.md` (150-line budget; 46 lines after)

| Section | Before | After |
|---|---|---|
| Patterns | 15/15 | 15/15 (P-06 text replaced) |
| Gotchas | 15/15 | 15/15 (untouched) |
| Outcomes | 10/10 | 10/10 (O-01 text replaced) |
| Open | 1/5 | 1/5 (untouched) |

Both target sections were at cap, so each add required a displacement. The merge tool has no
"replace" verb in practice — same-ID/different-text is a hard CONFLICT (exit 7) — so I removed
the weaker line with a targeted `edit` (single-line CUT, not a whole-file write; this file has
no concurrent writer this session) and then `add`ed the replacement under the freed ID via the
merge tool, which reported `ADDED P-06` / `ADDED O-01`, `PRESERVED` for the other 37 entries.

- **P-06 (Patterns), replaced.** Old: "removal deliverable → re-run payload pre/post binaries."
  New: *"WHEN a success criterion's pre-fix state cannot be re-created after the fix lands (e.g.
  an accept-then-reject before/after property) DO name it explicitly as evidence resting on
  committed narrative, not a runnable assertion — folding it into a blanket 'zero
  under-fixtured criteria' claim overstates what the suite actually proves."*
  Evidence: `runs/2026-09-01-01-validator/digest.md` adequacy note 1 — two SC clauses (SC-01,
  SC-04) rest on committed RED narration post-fix, and the qa cycle-1 note's "no under-fixtured
  criterion found" summary was stronger than that evidence supported. Displaced P-06: narrower
  (removal-change-type only) than the new entry, which applies to any feature with a before/after
  SC — a more common and more durable shape.
- **O-01 (Outcomes), replaced.** Old: "amendment deletes sole-coverage fixture, already closed
  elsewhere → name explicitly." New: *"WHEN you attribute a RED to unrelated drift and escalate
  for a resync DO ensure the post-resync GREEN is re-run and captured by the gate itself, not
  merely asserted in the resolution note — otherwise the ship decision's evidence was produced
  outside the gate that owns it."*
  Evidence: `runs/2026-09-01-c2-validator/digest.md` — qa correctly attributed `matrix_ok: false`
  to `team-config.yaml` drift against `main`, escalated (E1), the orchestrator resynced at
  `676940ce`, and the resolution note records "both kinds green" — but no qa-gate reader
  independently re-ran the suite to confirm it. Displaced O-01: a narrower, already-mitigated
  scenario ("visibility costs nothing") versus a load-bearing evidence-chain gap that a ship
  decision actually depended on.

## Repository tier — `.harness/harness/expertise/harness-qa.md` (40-line budget; 11 lines after)

| Section | Before | After |
|---|---|---|
| Gotchas | 5/15 | 6/15 (G-06 added) |
| Patterns / Outcomes / Open | 0 | 0 (unchanged) |

- **G-06 (Gotchas), added.** *"WHEN bash-write-guard blocks a Bash-tool scratch-copy (cp/redirect)
  for a perturbation proof DO create a disposable git worktree under .claude/worktrees/ instead —
  the guard permits `git worktree add` there while denying ad hoc scratch copies elsewhere, and
  Bash-copy permissiveness is not reliable session to session."*
  Evidence: `notes/review-harness-qa-c2.md` §4 — a disposable worktree at
  `.claude/worktrees/qa_t01_probe_wt` let this cycle reproduce T-01's RED evidence where an
  earlier cycle (`notes/qa-test-matrix-c1.md`) had recorded itself blocked from scratch-copying.
  Repository-tier: names this repo's actual guard and its one sanctioned worktree path — not
  true of a repository that has neither.

## Candidate disposition (all 3 relayed candidates)

1. **Accepted → craft Pattern (displaced P-06).** See above.
2. **Accepted, but rerouted → repository-tier Gotcha (displaced nothing, room existed), not a
   craft Pattern.** The candidate's own framing ("you found the route yourself... a disposable
   worktree placed under the permitted worktrees directory") is a fact about *this repo's*
   `bash-write-guard` and its `.claude/worktrees/` convention, not a portable rule — a repo with a
   different guard or no worktrees convention gets nothing from it. I did **not** also add a
   craft entry for "run a regression at the parent commit in an isolated worktree" — that
   technique is already covered by the existing craft Pattern P-15 (attributing a merge
   regression: run it at each parent commit in an isolated clone or worktree), which this
   cycle's T-01 reproduction is simply an instance of. Adding a second entry for the same
   technique would be the "instance list" distillation smell the skill warns against.
3. **Accepted → craft Outcome (displaced O-01).** See above. Not rerouted to repository tier:
   the failure mode (evidence for a ship decision produced outside the gate that owns it,
   following a correctly-attributed drift-and-resync cycle) is general to any gate/escalation
   protocol, not specific to this repo's tooling.

No candidate was rejected outright — all three passed the six-spawns-from-now test and were
either strong enough to displace a weaker craft entry or belonged, as stated, in the repository
tier.

## expertise_update (ops actually applied, merge tool exit 0)

- `replace P-06` in `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/expertise/harness-qa.md`
- `replace O-01` in `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/expertise/harness-qa.md`
- `add G-06` in `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1081-code-grade-enforcement/.harness/harness/expertise/harness-qa.md`
