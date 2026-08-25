# FEAT-40 — Q15 fix cycle applied (2026-08-25)

**BLUF.** All four mandatory corrections plus the two consistency consequences are applied to
`plan.yaml` as surgical in-place edits, and one consequential `BRIEF.md` constraint line is
corrected. `approval:` is untouched and still `pending`. Gates re-run clean. **T-04 does NOT gain
`depends_on: T-03`** — reasoning below.

## What changed

| # | Site (post-edit) | Change |
|---|---|---|
| 1+2 | `plan.yaml` T-03, DEC-203 item 5 (`:258-273`) | SIX → SEVEN purposes; seventh added verbatim; purpose 4 widened to `/harness-init` and `gh-sync.py ship`; "widened by exactly one" → "widened by exactly two purposes and by one surface"; added an explicit instruction to state the amendment-2 conflict and cite amendment 3 as the widening precedent |
| 3 | `plan.yaml` T-04 step 7c | "THE READ-BACK BOUND IS NOT WIDENED BY THIS…must not add a seventh" DELETED; replaced with the ruling: the bound is written over purposes and surfaces, not components; T-03 records the seventh purpose and the widened purpose 4; this task asserts nothing to the contrary |
| 4 | `plan.yaml` T-04 step 7c HOW + TESTS | `audit_findings`'s contract now says achieving it means MOVING `board_lifecycle.py:866` and `:887` up into `cmd_audit`, keeping `:898`'s print and `:901-904`'s `factory_cli.refuse` in `cmd_audit`, and never reusing the refuse branch. Added a second test asserting `cmd_audit`'s output is unchanged, so "prints nothing itself" is reachable rather than red |
| c1 | `plan.yaml` T-09 step 10 | "six purposes DEC-203 carries" → "seven". Nothing else in T-09 touched |
| c2 | `BRIEF.md` `## Constraints`, DEC-186 bullet | children read is a sixth **and the audit's detection reads are a seventh**; names the widened workflow surface and amendment 3's caller precedent |

Applied by a match-exactly-once Python script; every one of the six replacements matched 1/1 or the
script would have written nothing.

## The `depends_on` decision — NO edge, T-04 stays `[T-01]`

The discriminating question the dispatch set: does corrected step 7c make T-04 write a DEC-203
citation into a source file or comment at execution time?

**No.** Grep of T-04's whole `intent:` (`plan.yaml:325-549`) for `DEC-` returns three hits, all
instructions to the executor, none a string it writes: `DEC-138 amendment 7` (why not to import
`parent_args`), `DEC-146` (failure posture), and my new step-7c paragraph. My replacement wording is
purely negative — "this task writes nothing…asserting that ship's reads leave the bound unchanged".
T-04's `verify:` block (`:317-324`) greps no decision id either. So T-04 never opens `DECISIONS.md`,
never copies from it, and cannot go stale against an entry that does not exist yet. That is the
opposite of T-09, whose step 10 is explicitly *"copy the set from it… this is why T-09 depends on
T-03"* (`:954-957`).

The stronger-sounding argument for the edge — that landing T-04 first leaves code exceeding the
signed read-back bound — does not survive: DEC-203 does not exist before T-03 in **either** order, so
at T-04's commit the live bound is DEC-186's five purposes regardless. Ordering shortens that
interval, it cannot remove it. What authorises the widening is the operator's approval of this plan,
which precedes every task. Buying a shorter interval costs serialising the build spine (T-05, T-11,
T-10 all chain off T-04) behind the largest docs task.

Cycle check, done before deciding it was even available: T-03 is `depends_on: []`, so the edge would
have been acyclic and safe. It is declined on merit, not availability.

**Conditional reversal, and it is the operator's:** if the pending scope call folds `gh-sync.py:898`
into T-04 and that comment cites DEC-203, the edge becomes required — that is a citation write and
eng-lead's Q2 is right about it.

## Gates

- `check-plan-routes.py` → **0 violation(s) across 1 plan(s)**, exit 0. The DEVIATION lines are the
  pre-existing advisory main-session-direct rows, unchanged by this edit.
- `check-state.sh` → exit 1, and exactly **one** VIOLATION line in the whole run:
  `FEAT-40…/BRIEF.md is NOT approved`. No other violation, FEAT-40 or otherwise.
- `harness_yaml.load_plan` → parses; 11 tasks, 13 decisions; **0 untraced REQs** and 0 traces
  pointing at a REQ the brief does not carry.
- Suite not re-measured, per dispatch. HEAD is unmoved and nothing committed.

## Open, not mine to close

1. **T-09 step 10's per-purpose enumeration** (`plan.yaml:948-949`) still names only four
   subcommand pairings and says "`/harness-init` for the workflow detection" — now incomplete on two
   counts. The dispatch said fix the numeral and nothing else in T-09, so I did. The mitigation is
   already in the task: `:954-957` orders the executor to copy the set from DEC-203 and rules that
   the decision entry wins on disagreement. Flagged, non-blocking.
2. Three Item-closed comment sites, `T-11`/`D-12` renumbering, DEC-200 (#844) — untouched, per
   dispatch.

## Cycle 2 (2026-08-25) — send-back closed

Two edits, both applied by a match-exactly-once script; HEAD unmoved, nothing committed.

| # | Site | Change |
|---|---|---|
| 5 | `plan.yaml:72`, D-07 `choice:` | "widened to six purposes" → "widened to seven purposes and to a wider surface on the fourth". `because:` and `dec: none` untouched |
| 6 | `plan.yaml:982-987`, T-09 step 10 | the per-purpose enumeration now lists all SEVEN with their performing surface: start-task (claimed, station); `factory_claim` (blocker finished, which no `gh-sync.py` subcommand performs); `/harness-init` and `ship` (workflow detection); record-pr and `ship` (merged PR); `ship` (children); `/harness-init` and `ship` (audit detection reads). "subcommand that performs it" → "surface that performs it", because two performers are not subcommands. KEEP-VERBATIM clause and everything else in T-09 untouched |

Purpose 3's performer verified at source: `DECISIONS.md:5652-5657` assigns it to `factory_claim`, and
`factory_claim.py:155` `_blocker_gate` is the reader.

### Class sweep — every hit for six/sixth/seven/seventh/five/fifth/four/fourth/three/purpose/read-back/bound

Fixed: `plan.yaml:72`, `plan.yaml:982-987`.

Correct-as-is: `plan.yaml:52` (D-02, no count); `:98`, `:485`, `:896` and `BRIEF.md:197`, `:203`
(the audit's four network calls); `:145`, `:182`, `:231`, `:236`, `:241`, `:278`, `:353`, `:460`,
`:621`, `:775`, `:785`, `:813`, `:908`, `:921`, `:1023`, `:1027`, `:1035-1036`, `:1052` and
`BRIEF.md:5`, `:15`, `:94`, `:101`, `:126`, `:156` (unrelated threes/fours); `:258-272` (item 5, the
corrected authority); `:275` and `BRIEF.md:233` (DEC-192's six status values); `:494-503` (T-04's
ruling text; `:503`'s "enumerates six purposes" is the forbidden claim, correct as written);
`:931`, `:972-973`, `:988-990`, `:1039`, `:1042` (the github-mirror.md read-back paragraph and its
regression guard, no count claim); `:978` ("D-02 then adds a third" counts READS in the mirror, not
purposes in the bound); `:1161` (six test blocks); `BRIEF.md:124` (ship's purpose, the word);
`BRIEF.md:195` (audit finding class 2 of six); `BRIEF.md:227-231` (five today, sixth, seventh,
widened fourth — the correct pre-change statement).

### Gates, re-run after the edits
- `check-plan-routes.py` → 0 violation(s) across 1 plan(s), exit 0.
- `check-state.sh` → one VIOLATION in the whole run: FEAT-40 BRIEF.md is NOT approved.
- `harness_yaml.load_plan` → parses; 11 tasks, 13 decisions, `approval.status: pending`; 0 untraced
  REQs and 0 traces pointing at a REQ the brief does not carry.
