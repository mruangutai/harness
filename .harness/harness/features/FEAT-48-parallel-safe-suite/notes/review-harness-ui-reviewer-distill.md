# FEAT-48 — harness-ui-reviewer distillation

**BLUF:** Two new craft Outcomes applied (O-07, O-08). One high-value craft Pattern candidate
(terminal-output attribution) is accepted on merit but mechanically blocked: `expertise-merge.py`
is an add-only union merge with no delete/replace primitive, so a full 15/15 Patterns section
cannot be curated through the sanctioned tool despite the documented `replace`/`drop` ops in the
distill schema. Filed as an open_question, not forced in and not silently dropped. One relayed
candidate (bash-write-guard workaround) rejected as a banned harness-defect-workaround. Both files
`check-expertise.sh` clean.

## Material read

- `notes/review-harness-ui-reviewer-c7.md`, `-c8.md`, `-c9.md` (own three cycles)
- `notes/ship-review-2026-09-02-c9.md` (CEO ship briefing, B-13/B-14 rows)
- No observations log exists for this role on this feature (expected — only pm/orchestrator kept
  one); `runs/` digests do not exist (gitignored, removed with the worktree). Neither was hunted.

## Relayed candidates — judged

**(a) B-13 bash-write-guard blocks all bash-level writes for the read-only persona, including
`/tmp`.** REJECTED. Already filed as a harness defect (c9's own `Q1` open_question). The contract
is explicit: a guard that blocks a granted persona is never Expertise because a workaround outlives
the fix. Searched for a durable rule that survives independent of the bug ("probe via an in-process
interpreter when a bash-level write is blocked") and concluded it doesn't pass the six-spawns test
on its own — it is advice for coping with a specific bug, not a technique with standalone value once
the guard is fixed. Left as the harness owner's problem via the existing open_question, not
duplicated into Expertise.

**(b) Two LOW findings carried forward unchanged across cycles without re-litigation.** ACCEPTED
→ `O-07`. (Relay said "c7 to c9"; the material shows c7 had zero findings and the two LOWs first
appeared in c8, carried unchanged into c9 — corrected the premise, judged the underlying behavior
on its real shape.) This is a genuine efficiency pattern: re-verify against current bytes once,
state "unchanged," don't re-derive. It went unchallenged through the final ship-review table.

**(c) Grading five terminal-output surfaces for legibility AND attribution — attribution caught
what legibility alone missed.** ACCEPTED on merit. This is the standout craft lesson of the whole
feature: c9's "Pool attribution blocks" analysis (two files' output cannot interleave by
construction; `VIOLATION`/`FAIL self-test detail` never collide) is a distinct check from plain
readability and it's exactly the kind of thing a source-level review can miss if it only asks "is
this legible." Intended target: replace `P-10` (sibling-CLI exit-code consistency — the weakest
existing Pattern for this role: it turns on code paths and exit codes, arguably closer to
code-reviewer's remit than to UI/terminal-output review). **Could not apply**: see Tooling gap
below. Recorded as `Q2` open_question instead of forced in or silently dropped.

## Self-derived candidates

**Direct-execution over source-reading for terminal output.** ACCEPTED → `O-08`. All three cycles
(and especially c8/c9) ran the actual commands and captured real bytes — `env -u
HARNESS_AGENT_TYPE`, live monkeypatch injections, real mutation-check fixtures — rather than
inferring behavior from source alone. Those execution-based verdicts held unchallenged through the
final ship briefing. Distinct from existing Patterns (none of the 15 state "run it, don't just read
it" as its own rule) and from `G-14` (which is about grepping for idioms, not about executing).

**MUTATED-message diagnostic gap, T-06 verify-clause disposition, colour/ANSI grep sweep.**
Considered and NOT filed as new entries — each already matches an existing entry closely enough
(`G-13` covers "message states the fact but not the remedy/detail"; `G-14` covers "enumerate
idioms and grep" — reused verbatim in c9's ANSI sweep) that a new entry would be a near-duplicate,
not a sharper replacement. Existing Expertise correctly anticipated and was reused this cycle —
evidence the prior distillation is doing its job.

## Tooling gap — filed as open_question, not worked around

Read `expertise-merge.py` in full (`compute_union`/`cmd_apply`). Confirmed by direct test against
the real craft file: `merged_list` always starts from every base entry regardless of the proposal,
so a base entry can never be removed through `apply`. A same-id/different-text proposal always
raises `MergeRefusal(7)` (conflict); a new-id proposal at a full cap always raises `MergeRefusal(8)`
(cap exceeded) — verified live: `CAP EXCEEDED section=Patterns cap=15 union_size=16`, nothing
applied. The distill skill's own ops schema documents `op: replace` and `op: drop` as legal, but no
CLI path exists to execute either against a full section. This is a gap between the documented
contract and the shipped tool, not a judgment call — filed as `Q3`.

## Verified

- `check-expertise.sh` on both of my files: exit 0, `OK` on both.
- Real `apply` run: `ADDED O-07`, `ADDED O-08`, all 36 pre-existing ids `PRESERVED`, `APPLIED`.
- Post-apply file read back to confirm exact final content (Patterns 15/15 byte-identical to
  before, Gotchas 15/15 byte-identical, Outcomes now 8/10, Open 0/5).

```yaml
VERDICT: PASS
DIGEST:
  headline: 2 Outcomes added (craft); 1 strong Pattern candidate blocked by a real merge-tool gap, not applied; 1 relay rejected as a banned defect-workaround.
  counts_craft_before: { Patterns: 15, Gotchas: 15, Outcomes: 6, Open: 0 }
  counts_craft_after: { Patterns: 15, Gotchas: 15, Outcomes: 8, Open: 0 }
  counts_repository_before: { Patterns: 1, Gotchas: 0, Outcomes: 0, Open: 0 }
  counts_repository_after: not created, unchanged
  accepted:
    - { candidate: "carried-forward LOW findings re-verified once, stated unchanged (relay b)", entry_id: O-07 }
    - { candidate: "direct execution over source-reading for terminal output (self-derived)", entry_id: O-08 }
  accepted_but_unapplied:
    - { candidate: "attribution check alongside legibility for console output (relay c)", intended_target: "replace P-10", reason: "expertise-merge.py is add-only union merge with no delete/replace primitive; Patterns is 15/15 and both same-id (conflict, exit 7) and new-id (cap, exit 8) proposals were confirmed refused against the real file. Filed as Q3." }
  rejected:
    - { candidate: "bash-write-guard /tmp workaround as a durable probing rule (relay a)", reason: "harness-defect workaround; contract bans it outright since it outlives the fix; already filed as an open_question by c9's Q1" }
  mode: distill
  in_scope: true
  severity_max: n/a
  findings: 0
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions:
    - { id: Q1, question: "bash-write-guard blocks all bash-level writes for the read-only harness-ui-reviewer persona, including /tmp — already filed by c9, carried here unresolved.", blocking: false }
    - { id: Q2, question: "The attribution-check Pattern (relay c) is durable and warranted displacing P-10 (weakest existing Pattern, closer to code-review remit than UI review) but expertise-merge.py cannot mechanically displace anything in a full section. Does a future tool revision add a delete/replace primitive, or does curation route through a different, higher-privileged path?", blocking: false }
    - { id: Q3, question: "harness-distill's ops schema documents op: replace and op: drop as legal, but expertise-merge.py apply is a pure add-only union merge with no code path that removes an existing id. Confirmed live against the real craft file (exit 7 on same-id/different-text, exit 8 on new-id-at-cap). Is this a genuine tooling gap, or is curation of a full section expected to happen through a different mechanism this dispatch didn't name?", blocking: false }
  files_touched:
    - .claude/worktrees/harness/FEAT-48-distill/.harness/expertise/harness-ui-reviewer.md
  expertise_update:
    - { op: add, target: O-07, section: Outcomes, entry: "WHEN a LOW finding from a prior cycle is untouched by the new diff DO re-verify it against current bytes once and carry it forward as 'unchanged' rather than re-deriving the analysis — this passed ship review unchallenged each cycle.", why: "relay candidate (b), corrected premise (c8→c9 not c7→c9), judged on the underlying practice" }
    - { op: add, target: O-08, section: Outcomes, entry: "WHEN auditing terminal or console output for a UI review DO execute the real commands and capture actual bytes rather than reading source alone — direct-execution verdicts held unchallenged through final ship review across repeated cycles.", why: "self-derived from repeated direct-execution practice across three cycles; distinct from existing G-14 (grepping idioms) and all 15 Patterns" }
artifact: .harness/harness/features/FEAT-48-parallel-safe-suite/notes/review-harness-ui-reviewer-distill.md
```
