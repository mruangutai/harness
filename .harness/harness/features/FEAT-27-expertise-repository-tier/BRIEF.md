# BRIEF — FEAT-27 Expertise repository tier

Unit 6 of effort #336, the multi-repo control plane. Ticket #494. Sequence record #498.
Decision authority #340. All measurements in this brief were taken at `ada8e99`.

## Problem

The two-layer Expertise model is written down and half-built. `harness-distill/SKILL.md:43-46` tells
every agent that repository-specific knowledge lives at `.harness/<repo>/expertise/<agent>.md` with a
40-line budget, and that both layers ride every spawn. Neither half is true.
`inject-expertise.sh:27-29` has exactly two read paths and neither is that one (#484), and
`check-domain.sh --resolve` answers **NOBODY** for every agent's repository-tier path, so no agent can
write the file the skill tells it to write (#372). During FEAT-21 one distillation entry was returned
unwritten for exactly this reason. The result is a rule that sixteen agents are taught, obey, and
cannot execute — and the effort's destination criterion **DC-3**, "agents carry kaya's expertise", has
nothing to stand on.

## Goal

Make the repository tier real: an agent spawned here receives a labelled repository-tier block
alongside its craft block, can write its own repository-tier file, and the eleven entries in today's
craft files that are true of this repository only live in that tier instead. The format checker learns
the tier's own budget and gains the advisory craft/repository scan `harness-distill` already promises
(#412). Nothing about how craft Expertise works changes.

## Two premise corrections, stated where they can be vetoed

**Craft does not move, and this feature moves no files.** The dispatch that commissioned this plan
described unit 6 as a physical re-home of `.harness/expertise/`. It is not. The operator shipped the
layer table on 2026-08-14 (#340, second comment) putting **craft at `.harness/expertise/` permanently**
— craft carries across repositories, so scoping it under one repository's segment would be wrong. #336
line 30 already marks A-05/A-10 "SUPERSEDED-as-instruction, VALID-as-record", and both #484 and #372
describe the fix as *add a read path* and *add a grant*. **DC-7's expertise clause is therefore closed
by the repository tier existing, not by `.harness/expertise/` disappearing.** If the operator meant a
literal re-home of the craft tier, this plan is wrong and should be rejected at signature.

**The corpus is 96% craft, so this is sixteen rulings, not a rewrite.** Re-derived at `ada8e99` with
#340's own token set (`DEC-NN`, `INV-NN`, `FEAT-NN`, `.harness/`, `.claude/`, `check-*.sh`,
`factory_*.py`, `gh-sync`, `harness.json`, `team-config`), scanning per entry — a column-0 `- ` bullet
plus its indented continuation lines — across all 15 files:

**16 of 374 entries carry a repository token: 4.3%. Eight of the fifteen files carry none.**

That **confirms** #340's measured correction (10 of 267, 3.7%, seven of thirteen clean) at a larger
tree; it does not contradict it. Adjudicating those 16 under #340's rule — a craft entry may cite a
path as an *example* — gives **11 movers and 5 that stay craft**. The per-entry table is in
`notes/research-FEAT-27-expertise-tier.md` and is reproduced in the plan's T-04 intent. The plan is
built on that measurement: the migration is a bounded, enumerable, per-entry act, not a distillation
of 1164 lines.

## One unit, not two

The row on #498 reads "Expertise re-home **+** craft/repo split", and the effort's boundary rule is
that a unit boundary must leave the tree working and verifiable. Splitting here would produce a first
unit that creates an empty tier, grants it and reads it while every repository-specific entry stays in
the craft layer — a tree that is working but **unverifiable in the way that matters**: no criterion
could distinguish "the tier exists and is correctly empty" from "the tier exists and the migration was
forgotten", because the same emptiness satisfies both. The measurement is what settles it: sixteen
flagged entries, eleven movers, in six files, and each one is a named anchor in T-04's verify. That is
one afternoon of adjudication, not a second unit's worth of work — and #412's advisory scan, which
lands in the same unit, is the standing detector that keeps the split honest afterwards. Splitting
would buy a smaller diff at the cost of the only check that proves the split happened.

## The three halves are coupled by ordering, not by atomicity

The tier has three moving parts — the **grant** (T-01, `team-config.yaml`), the **hook's read path**
(T-02, `inject-expertise.sh`) and the **physical entries** (T-04). Asked whether they must land
together, the answer is no: one strict order and one genuine independence, and neither leaves a
user-visible dead end at any point in between.

**The grant must precede the move, strictly.** `check-domain.sh --resolve` answers `NOBODY` for
`.harness/harness/expertise/<agent>.md` at `ada8e99` — that is #372 — and the write guard refuses a
write to a path resolving to nobody. So T-04 cannot create a single repository-tier file until T-01
has landed. This is forced by the enforcement layer, not chosen: it is why `T-04` carries
`depends_on: [T-01]`, and why the ordering could not be relaxed even if it were convenient.

**The hook's read path is independent of both, in either direction.** `inject-expertise.sh` finds
the tier by globbing `.harness/*/expertise/<agent>.md`, and a glob over a directory that does not
exist matches nothing, so the pre-move hook is a no-op rather than an error — T-02's own case 3
asserts exactly that: no repository tier on disk, exit 0, no repository header emitted. The converse
holds too: a granted and populated tier that the old hook cannot yet read is simply not injected,
which is the state every agent is in today. So T-02 may land before or after T-01 and T-04, and it
carries `depends_on: []` for that reason.

**What the in-between states cost, stated plainly.** Grant without hook: agents can write the tier
and nothing reads it — no worse than today, where they can do neither. Hook without grant: the hook
reads a directory that cannot exist — a no-op. Grant and files without hook: the entries are on disk
and uninjected, recoverable by landing T-02 with no rework. None of these is a state a user or an
agent hits an error in; the only unreachable combination is the one the dependency already forbids.

**This is therefore an ordering asymmetry, and the plan already encodes it** — no task needs to be
merged with another, and no atomic landing is required.

## Requirements

- REQ-01: An agent spawned in this repository receives its repository-tier Expertise in its starting
  context, labelled so it cannot be confused with craft.
- REQ-02: Every one of the sixteen agents can write its own repository-tier Expertise file without the
  write guard refusing it, and cannot write another agent's.
- REQ-03: The repository-specific knowledge currently held in craft files lives in the repository tier
  instead, with no entry lost in the move.
- REQ-04: The format checker holds repository-tier files to their own budget and reports a craft entry
  that names a repository-specific token, naming the token that triggered the report, without failing.
- REQ-05: A spawn is never blocked or degraded by the injection hook, including when no repository
  tier exists.
- REQ-06: The harness's own documentation names the same two Expertise paths that the hook reads and
  the guard grants.

## Success Criteria

- SC-01: A spawn payload for an agent that has both tiers on disk produces injected context containing
  a repository-tier header naming the segment, and the repository file's body — and the same test fails
  against the pre-change hook, which emits no such header.
  verify: automated      evidence: unit
- SC-02: For each of the sixteen agents individually, `check-domain.sh --resolve` on
  `.harness/harness/expertise/<agent>.md` prints exactly that agent's name and nothing else. Baseline:
  it printed `NOBODY` for every one of them at `ada8e99`.
  verify: automated      evidence: integration
- SC-03: Each of the eleven entries ruled repository-specific is present in its owning agent's
  repository-tier file and absent from that agent's craft file, and each of the five ruled craft is
  present in its craft file and absent from the repository tier — sixteen entries, checked one at a
  time, thirty-two assertions, never a global grep and never a count.
  verify: inspection
- SC-04: Given a craft file containing a repository-specific token, `check-expertise.sh` prints an
  advisory line naming the file, the entry id and **the token that triggered it**, and still exits 0.
  Given a file with no such token it prints no advisory line. Both directions asserted.
  verify: automated      evidence: integration
- SC-05: `check-expertise.sh` reports a 41-line repository-tier file as over budget and does not report
  a 41-line craft file, so the 40/150 split is enforced by the path and not by a single constant.
  verify: automated      evidence: integration
- SC-06: With no repository tier present, and with a payload whose `agent_type` is missing or
  unparseable, the hook exits 0, emits no repository header, and emits no error — the spawn path is
  unchanged for every agent that has not distilled yet.
  verify: automated      evidence: unit
- SC-07: All fifteen craft files still pass `check-expertise.sh` after the migration, and every
  repository-tier file created passes it too — each file named individually in the output, not a
  directory-level exit code alone.
  verify: automated      evidence: integration
- SC-08: `.harness/README.md`, `.harness/harness/docs/SPEC.md`,
  `.claude/skills/harness-distill/SKILL.md` and `.claude/skills/harness-curate/SKILL.md` name the same
  two Expertise paths that `inject-expertise.sh` reads and `team-config.yaml` grants — all four named,
  checked one file at a time. Two renderings of the repository path are admissible and both are
  correct where they appear: the placeholder `.harness/<repo>/expertise/` in prose, and the literal
  glob `.harness/*/expertise/` where the text is a command the reader runs or a grant the guard
  matches. What must appear nowhere in the four is a **third** form — specifically
  `expertise/<repo>` or `**/expertise`, either of which names a directory neither the hook nor the
  guard resolves.
  verify: inspection
- SC-09: The truncation notice for an over-budget repository-tier file names 40, not 150, so an agent
  reading a truncated block is told the correct budget.
  verify: automated      evidence: unit
- SC-10: The injected context states precedence once, in words — repository over project over global,
  by specificity — together with the warning that a repository block for a segment other than the one
  the agent was dispatched against is not authoritative for its work. No block claims primacy in its
  own header — the phrase "authoritative on conflict" appears nowhere in the injected context, and
  headers label scope only. Asserted on the hook's real output, not on the script's source.
  verify: automated      evidence: unit

## Backlog disposition

| Issue | Disposition |
|---|---|
| **#484** | **Closed by this feature.** T-02 adds the third read path; SC-01 proves it. |
| **#372** | **Closed by this feature.** T-01 adds the grant; SC-02 proves it per agent. |
| **#412** | **Closed by this feature.** T-03 builds the advisory scan under #340's two constraints — proven able to redden, and it reports the triggering token. SC-04 is exactly those two constraints. |
| **#413** | **Declined, with a measurement.** The four validator-squad files sitting at 15/15 Patterns are `harness-qa`, `harness-code-reviewer`, `harness-ui-reviewer` and `harness-validator-lead`. All four scan **zero** repository-specific entries at `ada8e99`, so this migration frees them exactly zero slots. The cap question is untouched by unit 6 and stays a standalone chore. |
| **#375** | **Declined, orthogonal.** Concurrency and lineage protection for the shared craft tier is a property of how features write it, not of which tiers exist; adding a second tier neither helps nor worsens it. One of the eleven migrating entries (`harness-orchestrator` OQ-02) *is* this bug written as an Open item, and it moves as-is — the ticket stays open. |
| **#374** | **Declined, orthogonal.** A member's runs sitting outside its lead's view at distillation is a dispatch-visibility problem; it has the same shape whether there are one or two tiers. |

## Constraints

- **No touch, two orchestrators are live:** `fleet.yaml`, `.harness/harness.json`, `gh_board.py`,
  `load_board`, `factory_claim.py`, and everything under `.harness/harness/features/FEAT-24-*/`.
  Reading them is fine; this plan changes none of them.
- **The hook must never block a spawn.** `inject-expertise.sh` fires on every `SubagentStart`, nested
  ones included (DEC-100). It must keep exiting 0 on every path, and it must not acquire a YAML parse
  dependency — an unquoted `#` in `team-config.yaml` has already taken a resolver down once.
- **The craft tier's location and semantics are out of scope.** `.harness/expertise/` stays where it
  is, with its 150-line budget, its per-agent grants and its global sibling.
- **`check-state.sh`, `check-domain.sh`, `bash-write-guard.sh` and `validate-digest.py` are not
  edited.** No task touches them, and `check-state.sh` has no expertise invariant to update. The
  measurement, stated so it is true as written: `grep -i expertise` over
  `.claude/skills/harness/bin/check-state.sh` at `ada8e99` returns **exactly two lines**, `:343` and
  `:353`, both spelling it **`Expertise`** with a capital E, and both are INV-9 prose about the
  `SubagentStart` registration — the message text of "no `.claude/settings.json`" and "no
  `SubagentStart` hook". Neither asserts an Expertise **path**. A case-sensitive `grep expertise`
  returns zero, which is why an earlier draft of this line read "zero matches"; the conclusion is
  unchanged either way, because nothing in this plan changes the hook's registration or its path.
- **Entry ids are not renumbered.** Removing an entry from a craft file leaves a gap in its section's
  numbering. `check-expertise.sh` requires the `XX-NN` prefix, not contiguity, and DEC-66 makes the ids
  stable references.
- The advisory scan is **advisory**: it must never contribute to a non-zero exit. #340 rejected a
  blocking gate explicitly, because a legitimate craft entry may cite a path.

## Verification gaps

None bear on this feature. The null-`cmd` kinds in `harness.json` are `component`, `ui`, `eval` and
`typecheck`; this feature touches shell, Python tests and markdown only, and every `automated` SC above
rests on `unit` or `integration`, both of which have live runners. `functional` is `excluded` under
DEC-187 and is not used here.

One narrower gap, recorded because it shapes where evidence comes from: `integration.detect` in
`harness.json` does not list `test-check-domain.py` or `test-check-expertise.py`, even though
`run-unit-tests.sh --kind integration` runs both. The runner is the authority for what executes, so the
`evidence: integration` criteria above are genuinely exercised; the detection glob is stale.
`harness.json` belongs to unit 5 this cycle, so it is raised as an open question rather than fixed here.

## Approval

status: approved
approved_by: operator (Mike Ruangutai), via main session
date: 2026-08-19
