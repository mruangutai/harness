# BRIEF — FEAT-03-subissue-mirror — one sub-issue per task, so closure is exact at both terminal states

> The H1 above is a contract, not decoration: `# BRIEF — <FEAT-NN-slug> — <human phrase>`. `gh-sync.py`
> reads the phrase from it to title the feature's parent issue (`FEAT-NN-<slug> — <human phrase>`,
> the grilling's settled convention). pm authors the phrase from `## Goal`.

## Problem

The mirror DEC-138 specified — one GitHub issue per `T-NN` — has never once been used as designed,
and the workaround every feature reached for disabled task closure for a whole build. In **kaya**,
`feature.yaml github.issues` shows FEAT-01 collapsing T-03 and T-04 onto #31, FEAT-02 mapping every
task to #120, and **kaya's FEAT-03** mapping all eleven tasks to #48 with milestone #10 empty
(open=0/closed=0). Kaya's FEAT-03 documents the consequence in its own `feature.yaml`, in caps — a
**"CLOSE-TASK HAZARD, ELEVENFOLD"**: because all eleven tasks point at #48, `gh-sync.py close-task`
on *any* task closes #48, so the note instructs that `close-task` must not be run at all during the
build. The mirror's closure half is switched off by hand, with a comment as the only guard. This is
not sloppiness — DEC-138 am.1 predicted it ("intake absorbs, never imports 1:1"): tasks are usually
*parts of* an existing backlog issue, not new peers of it. The second half of the problem is
symmetric and simpler: `gh-sync.py` has `open`, `close-task`, `backlog` and `ship` and **no
abandonment path at all**, so a feature the user drops leaves its mirror open forever, or gets
closed as though it shipped.

## Goal

Make the mirror close correctly for both terminal states. Each `T-NN` gets its **own sub-issue**
under one parent container per feature, so `close-task` closes exactly one task and the eleven-fold
hazard is structurally impossible rather than hand-guarded. Ship closes the container and the
milestone; abandonment closes the feature's own sub-issues as `not_planned` and posts the reason
verbatim from the ship review the user signed. The three GitHub primitives this needs already exist
in `wayfind.py` and get **extracted**, not re-implemented.

## Requirements

- REQ-01: Each task of a mirrored feature has its own tracker item, and a feature's task items are
  grouped under exactly one container item.
- REQ-02: Closing one task closes exactly that task's item — no other tracker item changes state.
- REQ-03: Backlog issues a task absorbs are cited on that task's item and survive its closure
  unchanged; they change state only through a human signature.
- REQ-04: Both terminal states have a path. Shipping closes the container and the definition of
  done; abandonment is visibly distinct from shipping and carries the user-signed reason verbatim.
- REQ-05: The container is recorded in local state when the mirror creates or adopts it, and is
  never read back out of the tracker — the mirror stays write-only.
- REQ-06: The internal-id attach trap, the parent read and the blocking-edge write each exist in
  exactly one place in the codebase, shared by every caller.
- REQ-07: A feature whose mirror is on and whose tasks are mirrored, but whose container is
  unrecorded, is surfaced to a human at every `/harness` entry.
- REQ-08: Every behaviour of the mirror is provable offline — no test and no build step requires a
  live tracker call.
- REQ-09: The changed mirror contract is recorded where a later reader will find it, and no prose
  the org still reads states the superseded one — both the decision record and the standing
  dispatch-time prose. (Which agent or tier makes each edit is a PLAN concern; the outcome is that
  no live prose contradicts the new contract at ship. See `PLAN ## Preconditions and hand-offs`.)

## Success Criteria

- SC-01: `open` creates one sub-issue per `T-NN` and attaches each to the feature's single parent
  **by the child's internal `id`, never its `number`**; the fake-gh call log shows the id form. A
  re-run after a crash between recording an issue and attaching it completes the missing attach and
  duplicates nothing.
  verify: automated      evidence: unit
- SC-02: `close-task T-NN` produces exactly one `issue close` call, and no absorbed issue number
  appears anywhere in the call log.
  verify: automated      evidence: unit
- SC-03: `abandon --reason-file <path>` closes every recorded sub-issue with
  `state_reason=not_planned`, closes the milestone, leaves the parent **open**, and posts the reason
  through a file path (no string the mirror assembled).
  verify: automated      evidence: unit
- SC-04: `ship` closes the parent issue and the milestone; with `--body-file <path>` it posts that
  file verbatim and nothing else.
  verify: automated      evidence: unit
- SC-05: `parent`, `milestone`, the `T-NN` issue map and the attach receipts survive a
  `feature.yaml` write/read round trip in both directions — recording the parent does not lose the
  issue map, and recording an issue does not lose a `parent:` line that was already there.
  verify: automated      evidence: unit
- SC-06: The three primitives of REQ-06 exist in exactly one place. Each is identified by its
  **payload or lookup form, never by its endpoint path** — after extraction `wayfind.py` contains
  none of the four: the argv `"-F", f"sub_issue_id=` (the internal-id attach, today `:272`),
  `"-F", f"issue_id=` (the blocking-edge write, today `:281`), `"--jq", ".id"` (the internal-id
  lookup, today `:271` and `:279`) and `/parent"` (the parent read, today `:147`). Second half:
  `gh-sync.py` contains no call to `parent_args` or `blocked_by_args`.
  **Carve-out, and it is load-bearing:** the sub-issue list GET (`wayfind.py:113`) and the blocker
  list GET (`:117`) **stay in `wayfind.py` with their endpoint strings inline** and are out of scope
  — they are wayfinding reads, not among REQ-06's three primitives. A path-level check could never
  prove this SC and would *void* it: the retained list GETs and the extracted writes build the
  **identical** endpoint string (`repos/{repo}/issues/{num}/sub_issues`,
  `repos/{repo}/issues/{num}/dependencies/blocked_by`), differing only by the `-F` payload, so a
  grep on the path asserts the absence of code that must remain. The `ticket` dry-run print at
  `:262-263` also stays verbatim (it names the trap in prose), which is why the two `-F` checks are
  scoped to the argv form rather than the bare `sub_issue_id=` substring.
  verify: inspection
- SC-07: The `unit` gate actually exercises `gh-sync.py`: `test_kinds.unit.cmd` runs both bin test
  scripts, and `test_kinds.unit.detect` matches them (today it matches zero files in this repo).
  verify: inspection
- SC-08: `check-state.sh` reports the missing-container invariant at warn level on a fixture with
  `github.sync: true` plus recorded issues and no parent, and is silent when the parent is recorded;
  the overall exit code is unchanged in both cases.
  verify: automated      evidence: unit
- SC-09: No test and no script asserts on `sub_issues_summary` immediately after a write, and no
  test invokes a real `gh` binary.
  verify: inspection
- SC-10: The migration is new-features-only: no task adds a backfill or retrofit code path, and no
  task edits the `github:` block of any existing `feature.yaml`. **kaya's** FEAT-01, FEAT-02 and
  FEAT-03 — the three features with live `github.issues` maps — are not retrofitted, and nothing
  here could reach them (they live in another repo).
  verify: inspection
- SC-11: `check-docs.sh` exits 0 and `check-state.sh` INV-10 is clean after the DECISIONS amendment
  lands, with the reversal of DEC-138 am.1's "they close with it" recorded.
  verify: inspection
- SC-12: A mirror step that fails for an environmental reason (sync off, repo unpinned, gh missing,
  a failing API call) still exits 0 with one SKIP line, for the new subcommands as well as the old.
  verify: automated      evidence: unit

- SC-13: No prose the org reads at dispatch still states the superseded closure contract. At ship,
  `grep -c 'closes its issue and everything it absorbs' .claude/skills/harness/SKILL.md` is 0 (one
  match today, `:137`), and `:144`'s ship row names the parent as well as the milestone. This is a
  **main-session** edit, not an agent's — see `PLAN ## Preconditions and hand-offs` for the owner
  and for why `check-docs.sh` cannot detect this gap.
  verify: inspection

## Verification gaps

- `functional`, `integration`, `component`, `ui`, `eval` and `typecheck` all have `cmd: null` in
  `.harness/harness.json`. Every task here is therefore scoped `logic`/`bugfix`/`config`/`docs`, whose
  `test_matrix` rows resolve to `unit` (or `[]`) only — deliberately, so no SC rests on a null kind
  (DEC-163).
- **`unit` did not cover this surface at all until this feature fixes it.** `unit.cmd` is the single
  path `test-validate-digest.py`, and `unit.detect`'s globs match **zero** files in this repo (both
  test scripts are hyphenated and live under the hidden `.claude/` tree). T-01 turns `unit` into a
  runner and widens `detect`; SC-07 is `inspection` rather than `automated` because an SC about the
  gate cannot be proven by the gate it changes.
- **The live GitHub API path is not proven by anything in this repo.** `github.sync` is `false` and
  `github.repo` is `null` here, so every mirror invariant is exercised against `test-gh-sync.py`'s
  fake `gh` only. What carries the real API's behaviour instead: DEC-168's measured live probe
  (closure does not cascade in either direction; `sub_issues_summary` is eventually consistent) and
  the first live `open` on a project that has sync on — which stays a user-gated moment, not a gate
  this feature can pass.
- **Nothing mechanical detects the SKILL.md prose gap (SC-13).** `check-docs.sh` scans
  `.claude/skills/**/*.md`, but the only mechanism it has is a `<!-- stale: … -->` marker declared in
  `DECISIONS.md`, and declaring one for a phrase that is still live turns the checker **red** and
  gates every `/harness` entry on an edit no agent may make. So T-08 declares no marker, verified
  `check-docs.sh` stays exit 0 throughout (observed exit 0 at `f929d44`, "no stale statements
  found"), and **the checker is silent about SC-13 by design.** What carries it instead: the named
  pre-ship step in `PLAN ## Preconditions and hand-offs` and SC-13's own grep, run at the ship gate.
- **`check-state.sh` exits 1 in this repo for reasons unrelated to this feature** (observed at
  `f929d44`: `BRIEF.md is NOT approved`, plus an orphaned run dir). No SC and no task verify may
  assert `check-state.sh` exits 0; they assert on the specific invariant's line and on the exit code
  being **unchanged from the pre-change baseline**.
- No `functional` runner means the orchestrator's end-to-end sequence (open → close-task per commit →
  ship/abandon) is proven step-by-step, never as one flow.

## Constraints

- **Files-only, python3 stdlib.** No new dependency, no `jq`, no YAML parser — `feature.yaml` stays
  text-edited by regex as `gh-sync.py` already does it.
- **The mirror is write-only** (DEC-138). Issue state is never read back into harness state. The
  parent is *recorded*, never discovered: `gh-sync.py` must not call the parent read.
- **The mirror never composes text** (DEC-138 am.6). Anything posted comes from a file path — the
  signed ship review, the approved artifact.
- **Never a gate** (DEC-138). Environmental failure = one SKIP line, exit 0. Exit 1 is reserved for
  caller errors. The new subcommands inherit both halves exactly.
- **Extract, never re-implement.** The internal-id attach, the parent read and the `blocked_by`
  write come out of `wayfind.py` into one shared module; two copies of the id-not-number trap is the
  duplication class DEC-158 keeps finding.
- **Migration scope is new features only.** No retrofit of FEAT-01, FEAT-02 or kaya's FEAT-03:
  the first two are shipped (retrofitting risks closing settled work) and kaya's FEAT-03 is
  mid-build with its hazard documented and worked around.
- **No task and no test may require a live `gh` call**, since `github.sync: false` here.
- Closure semantics are settled and measured (DEC-168) — nothing re-probes them, and nothing asserts
  on `sub_issues_summary` right after a write.

## Out of scope

- **Feature B, in full** — PLAN gaining `depends_on:` per task, `gh-sync.py` emitting native
  `blocked_by` edges, ordering validation in `check-state.sh`, and the lead's DAG read from PLAN
  instead of re-derived per run. It is sequenced as its own BRIEF, not abandoned. The razor, both
  halves, because they look alike and are not:
  - **Extracting** the `blocked_by` write helper from `wayfind.py` is **in** scope (the settled list
    names all three primitives, and wayfind keeps using it). **Calling** it from `gh-sync.py` to
    emit edges is Feature B — **out**.
  - **Extracting** the parent read is **in** scope so wayfind keeps using it. **`gh-sync.py` calling
    it is out** — it is a READ, and DEC-138 makes the mirror write-only. `parent:` is *recorded* to
    `feature.yaml github.parent` at creation.
  `.harness/notes/explore-pm-tickets-subissues.md` argues for emitting edges ("worth it, and
  cheap"); the grilling superseded that by splitting Feature B out. It is not pulled back in here.
- **Surfacing absorbed issues in the ship briefing's proposed-backlog section.** The half this
  feature ships is that absorption stops closing anything. Where absorbed items reach the user is a
  `.claude/skills/harness/SKILL.md` edit, which **no agent domain covers** (`team-config.yaml` grants
  only `.claude/skills/harness/bin/**`), and the grilling lists the section's machine-readable form
  under `## Not yet specified`. See open question Q1.
- **Retrofitting FEAT-01/FEAT-02/kaya's FEAT-03.**
- **Freezing an adopted wayfinding map issue's body** at hand-off (pruning `## Not yet specified` /
  `## Out of scope`, adding `Superseded by BRIEF.md at <sha>`). Wayfinding issues are main-session
  authored (DEC-166/167); the mirror only *adopts a parent number*. See Q2.
- **Teaching the next pm the H1 title contract.** This BRIEF's H1 carries the human phrase that
  `gh-sync.py` reads to title the parent (`FEAT-NN-<slug> — <human phrase>`, the settled convention).
  The place that would make it a standing convention is `.claude/skills/harness-brief/SKILL.md`,
  which no agent domain covers — without that edit, a future BRIEF omits the phrase and its parent
  silently titles itself the bare feature id, which DEC-133 says tells the user nothing. Q2.
- **Inducting kaya's pre-harness decisions** — its own wayfinding effort.

## Approval

status: pending
