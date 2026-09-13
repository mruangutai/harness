# You are a PHASE, not the feature — the seam, the handoff, the successor

Read this at a phase boundary, when the context advisory arrives, and as your first read on
waking as a successor. History: DEC-148, DEC-159, DEC-193, DEC-201.

## The phase

Your mission IS one phase — plan (or patch), build, validate, or ship. **Ending at the phase
boundary is normal termination**, not abandonment; continuing into the next needs a reason.
Session cost grows with the square of length, so one long orchestrator outspends every other
saving in the org.

Phase exits, all disk-checkable: **plan** and **ship** end at user gates; **build** exits when every
planned T-NN has a PASS run in `feature.json`; **validate** exits at a `validate` PASS with
`must_fix` resolved. The **fix loop is the exception** — `fix` rounds are worked inside your
validate session and inside the rework ruling, never relayed per cycle.

Record your station in `plan.yaml`'s top-level `status:` — `backlog`, `plan`, `ready`, `building`,
`review`, `done`, or the terminal `abandoned`, lowercase — and each transition as a STATE.md log
entry. **Write it with `plan-merge.py set-feature-station`, never by hand.** `feature.json` holds
NO `status:` key (FEAT-41) and no `phase:` key (DEC-191); the schema refuses both. One file
records the station, and it is the plan.

## The handoff

**At the seam, write the handoff** — `notes/handoff-<phase>.md` from `templates/HANDOFF.md`: your
working memory, not a summary. Five sections, ~60 lines, shape-gated at write: `## Next` (the
decided next action, cited to PLAN), `## Trust` (`claim — evidence pointer — verified-at <sha> |
UNVERIFIED`), `## Dead ends` (exclusions active for the next phase, same grammar — no pointer, no
entry), `## Working set` (3–5 paths) and `## Done when` (exactly one `Scope:` plus one to four
`Authority:` pointers, all of which resolve when the note is written; no standing re-resolution).
Under a by-perspective BRIEF at least one authority is
`brief-perspective:<BRIEF path>#<perspective>`, pointing at a `**<name>**` line of `## Done when —
by perspective` — the one statement of done, cited rather than re-derived (SC-11). The title line
carries `seq-<N>`, the ordinal of the run that wrote it; INV-40 counts successors from it.
**Superseded, never appended.**

**A context-triggered handoff uses that same note** (DEC-159) — no new seam, no new artifact. Write
it at the next STEP boundary, never mid-dispatch and never with a child in flight.

**Never carry payloads forward.** A member's return lives in its digest; your context needs the
verdict and the path. Rationale goes in `notes/` — never in feature.json, and never as history
anywhere spawn-read.

## As a successor

Your first act after reading the handoff is a `succession` judgement (SC-20) —
`feature-record.py judgement --file <feature.json> --by harness-orchestrator --kind succession --decision <continue|downgrade|stop> --reason <one line>`
— decided from the feature's cumulative spend (`feature-record.py spend`) and the note's `## Next`,
and reported in your first return. You do not ask; the operator overrules from the return. Then
validate `## Next` against PLAN and STATE. The note prices trust, it never grants it — anything
UNVERIFIED gets re-checked first. No note on disk (crash)? The disk-only path is fully supported:
STATE.md `## Current`, feature.json and the cited run digests, read by the loop's step-1 scoping
— and the succession judgement is still your first write.

## The worktree (DEC-95, DEC-193)

Your dispatch names a worktree by absolute path. Work inside it for the whole run, by absolute path
and by `git -C`. Creating it and removing it are the main session's acts.

**Never run `feature-worktree.py remove`.** `git worktree remove` succeeds at exit 0 from inside the
tree it removes, so an orchestrator obeying that instruction deletes its own working directory.
Your part of a terminal state is to finish landing your artifacts and report; the `post-merge`
hook removes the checkout when the merge lands, and `check-state.sh` INV-29 refuses while a
worktree still stands for a feature at a terminal state.

**Run-dir slugs:** `<task-or-purpose>-<squad>` (`t04-fe-eng`, `plan-product`, `fix-c2-validator`)
— the squad suffix is what the lead's domain glob keys on; never embed the feature id. A run-dir
path that is QUOTED rather than written — in a plan block, a pasted refusal, a bug report — is
spelled `[.]harness/` so `dispatch-guard.sh` does not read it as a write.
