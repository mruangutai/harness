## BLUF

**FAIL.** Spec compliance (Stage 1) is clean across REQ-01..07 and D-01..D-19 — no scope creep, no
omission, SC-08/SC-09 verified by direct citation, SC-07's OMP closure independently reproduced
(live-pid fixture + discriminating mutation both confirmed). Stage 2 finds one **high**, real
fail-open regression in `hook_mode()`'s new suspension branch (F-1), plus one **high** blocking
`code_grade` record (F-4). Both gate. Three lower-severity items are advisory only.

## Stage 1 — spec compliance

| REQ | Status | Evidence |
|---|---|---|
| REQ-01 (zero polling) | met | `.claude/skills/harness/SKILL.md:46-47`, `.claude/skills/harness-team/SKILL.md:128-129` state "zero" explicitly |
| REQ-02 (nonterminal suspension) | met, but see F-1 | `validate-digest.py:1662-1710` — SUSPENDED branch validates persona+awaiting set-equality before `return 0` |
| REQ-03 (same-parent resume) | met (doc) | `SKILL.md:47-48`, `harness-team/SKILL.md:130-131`; enforced indirectly by the registry, not directly testable in this diff |
| REQ-04 (two governed routes quarantined, Bash-in-domain excluded per D-19) | met | `check-domain.sh:1683-1703`, `plan-sign-gate.py:339-390`; D-19's narrowing stated verbatim in DECISIONS.md and BRIEF `## Verification gaps` |
| REQ-05 (explicit adopt/discard) | met | `quarantine.py` `cmd_adopt`/`cmd_discard`, no timer/scheduler; grep across `bin/` confirms the only callers are the CLI itself and the two gates' refusal text (T-04 intent) |
| REQ-06 (terminal digest only after completion/adoption) | met | SUSPENDED branch returns before `validate()` is ever called (`validate-digest.py:1680`) |
| REQ-07 (OMP unchanged) | met | D-04 in `orphan_write` (`inflight_registry.py:291-317`): `has_compatibility_claim` is false when every live claim for the feature is `runtime == "omp"`, so `orphan_write` always returns `False` for an OMP-only feature regardless of writer identity — independently reproduced, see SC-07 below |

D-01..D-19 checked individually against the diff: no violation found. D-11's ordering (FEAT-41 route
denial before the quarantine branch) is source-confirmed at `check-domain.sh:1647-1678` (denial,
`sys.exit(2)`) preceding `:1680-1703` (quarantine branch) — see Lead 6. D-13/D-14 (fail-open on an
unresolvable `--file`, one shared root) confirmed at `plan-sign-gate.py:346-348` and `:35`. No task
touches a file outside its declared `files:` list; no file in the touched set lacks a task/decision
tracing to it.

**SC-08** (inspection): all four clauses present and citable —
`.claude/skills/harness/SKILL.md:44-49` (orchestrator loop step 4) and
`.claude/skills/harness-team/SKILL.md:126-135` (lead's "never wait — suspend the turn" paragraph).
A reader holding only these four would not poll: clause 2 states "zero" explicitly, clause 3 assigns
resumption and replacement-blocking to the registry (not the reader's judgment), clause 1 supplies
the only legal turn-end shape, clause 4 gates all further action on `quarantine.py list`. **met.**

**SC-09**: `test-gen-decisions-index.py` executed — 14/14 ok including the three new T-08 guards
(`test_dec_210_entry_names_both_enforcement_points`,
`test_dec_210_entry_states_the_bash_write_route_for_plan_yaml`,
`test_dec_210_index_row_names_the_compatibility_host_in_the_ruling`). DECISIONS.md's DEC-210 entry
names both `check-domain.sh` and `plan-sign-gate.sh` and states the `plan-merge.py` Bash route
sentence (`docs/DECISIONS.md:6497-6504`). **met.**

## SC-07 (OMP closure) — independently reproduced, met

1. **Live-at-assertion-time check**: both hook-level fixtures (`test-check-domain.py:3489-3496`,
   `test-plan-sign-gate.py:479-487`) launch a real `subprocess.Popen(sleep 30/60)`, record its pid
   into the claim via `supervisor_pid=`, and fire the hook (`_feat51_fire`/`qgate`) **before**
   `.terminate()` — confirmed by reading the call order, not inferred from the label. Executed both
   files directly: all OMP-labelled cases `ok`.
2. **Discrimination**: built an in-memory mutant of the shipped `orphan_write` (exec'd the real
   source text with `has_compatibility_claim`'s `runtime != "omp"` filter replaced by an
   unconditional `True`, no file written to disk) and ran it against a live-OMP-claim registry
   produced by the real `claim_with_receipt`. Real module: write allowed (`True`). Mutant: write
   allowed became `False` (refused) — the OMP case turns red exactly as SC-07 requires. Both modules
   exercised the same on-disk registry state; only the `orphan_write` predicate differed.

No gating finding here.

## Stage 2 — six leads

**Lead 1 — `hook_mode()` release ordering: FAIL, see F-1.** Enumerated every return path.
Every path releases except the one validated-SUSPENDED branch (`:1680`, before `_reg.release` at
`:1721`), matching D-02/D-09's "release first, then contract" for all *classifiable* returns. But
the refusal-on-live-children branch (`:1711`, `if _kids and _return_verdict in VERDICTS`) now
requires the parsed verdict to be a *recognized* token — SUSPENDED-valid or one of `VERDICTS` — where
the pre-change code refused unconditionally on any nonempty `_kids`, independent of the returned
text. See **F-1**: an absent/null `last_assistant_message` falls through this narrowed condition
into the pre-existing "PRESENCE, NOT TRUTHINESS" block (`:1735-1736`) and now exits 0 instead of 2.

**Lead 2 — SUSPENDED unreachable outside `hook_mode`: confirmed, no finding.** Repo-wide grep:
`SUSPENDED` occurs only inside `hook_mode` (`:1662`, `:1704`), in tests/docs/playbooks, and never in
`VERDICTS` (`:35`) or any persona schema.

**Lead 3 — query-scoped expiry: confirmed, no finding.** `orphan_write`'s mutator
(`inflight_registry.py:299-303`) passes `lambda claim: _matches(claim, feature=feature)` into
`_expire_where`, scoping expiry to the target feature only — matches `live_children`'s existing
discipline.

**Lead 4 — duplicated refusal text: confirmed, does not rise above a backlog row.** The middle
sentence ("is canonical, but {agent} holds no live claim for {feature}. Its parent is gone and a
replacement may already be writing.") is character-identical between `check-domain.sh:1695-1696`
and `plan-sign-gate.py:408-409`. `plan-sign-gate.py`'s own header states "ONE refusal text, used
verbatim for EVERY denial" (`:50-51`) for its `sign-approval` `REASON`, and the file's own new
quarantine refusal is a second, independently-worded text — a real inconsistency with the stated
principle. Already caught and filed report-only by SIMPLIFY
(`notes/receipt-harness-backend-dev-simplify-reuse-c1.md`, Lead 2) because both files are
DEC-174 main-session-direct/no-squad-edit. I concur with that disposition: **low**, backlog, not
`must_fix` — the fix (hoist to one `inflight_registry.orphan_refusal_reason()`) is correct but
cannot be applied by either persona holding these files without a separate main-session task.

**Lead 5 — `--file` fail-open negative control: confirmed, no finding.** The
`NEGATIVE CONTROL: an orphan apply whose --file value is a shell variable is allowed` case
(`test-plan-sign-gate.py:524-526`) runs under `claims=_other` — a live claim held by a *different*
persona (`harness-qa`) in a *different* session than the calling `harness-orchestrator`/`_session`
— which is exactly the live-orphan fixture, not a no-claim fixture. Ran the file directly: passes.

**Lead 6 — D-11 ordering: confirmed, no finding.** Source-read: the FEAT-41 route-denial's
`sys.exit(2)` (`check-domain.sh:1647-1678`) textually and executionally precedes the FEAT-51
quarantine branch (`:1680-1703`); an orphan `Write` of `plan.yaml` reaches the first branch, exits
2 with "plan.yaml has exactly ONE writer" (`:1660`), and never reaches the quarantine code. Backed
by a dedicated regression test, `an orphan Write of plan.yaml keeps the FEAT-41 route denial` +
`the plan.yaml route denial does not mention quarantine` (`test-check-domain.py:3522-3525`), both
`ok` when executed.

## Findings

### F-1 — `hook_mode()`'s narrowed live-children refusal fails open on an absent/null return — **high, must_fix**

`validate-digest.py:1656-1660` computes `_return_verdict` from `last_assistant_message`; the
live-children refusal at `:1711` now fires only `if _kids and _return_verdict in VERDICTS`. Before
this diff, the equivalent check fired on `_kids` alone, independent of any parsed text
(`0bc57c88:validate-digest.py:1652-1657`).

**Failure scenario**: a `harness-eng-lead` with a genuinely live `harness-backend-dev` claim
returns a payload whose `last_assistant_message` is absent or `null` (the exact platform gap the
file's own "PRESENCE, NOT TRUTHINESS" comment says was observed live — "Five empty returns in
FEAT-45" — `:1731-1734`). `_return_verdict` is `None`, matching neither `"SUSPENDED"` nor
`VERDICTS`, so the `:1711` refusal is skipped entirely; the parent's own claim is still released
(`:1721`, unconditional); execution falls to `:1735-1736`, which returns **0** ("NOT VALIDATED").
Before this diff the same payload was refused at exit 2, forcing the lead to return again. After
this diff the lead is allowed to end its turn with **no verdict, no suspension, and its own claim
released**, while its child is still running — reopening exactly the "children racing a replacement
writer" shape this feature exists to close, on the turn-end side rather than the write side.

**Reproduced live** against the shipped binary (not a hand-built mutant): a real
`inflight_registry.claim` for `harness-backend-dev` under `harness-eng-lead`, then
`validate-digest.py --hook` fired with `{"agent_type": "harness-eng-lead", "cwd": root}` (no
`last_assistant_message` key) → **exit 0**, stderr: `"...the return was NOT VALIDATED."` No test in
`test-validate-digest.py`'s new suspension group (`run_t51_suspension_cases`, labels at `:1463-1504`)
or the pre-existing T-09 group covers this combination — all lead/orchestrator+live-children cases
use `LEAD_BLOCK`, a well-formed terminal `VERDICT: PASS` text.

**Not a plan-authorized narrowing**: T-01's intent lists exactly three branches (SUSPENDED-valid,
terminal-VERDICT-with-kids, no-kids) and states "leave every other path byte-identical in
behaviour" for everything not itself changed by the suspension carve-out — the live-children
refusal for a non-SUSPENDED, non-terminal return was not called out as a path meant to narrow.

**Remedy** (report-only, not applied): the refusal condition at `:1711` should fire whenever
`_kids` is nonempty and the return is *not* the validated-SUSPENDED case, rather than requiring an
affirmatively-recognized terminal token — i.e. restore "any live children → refuse unless legally
suspended" rather than "recognized live children AND recognized verdict → refuse."

### F-4 — `quarantine.py:100 cmd_adopt` is grade 3 in production code, below the grade-4 bar — **high, code_grade: fail**

`code-grade.py --base 0bc57c88 --head fa5ce88e`: `cmd_adopt`, cyclomatic 7, cognitive 10, ABC 22.5,
GRADE 3, driver `cognitive+abc`, bar 4, `RESULT: FAIL`, `SEVERITY: high`. The function mixes root
resolution, basename legality checking, and a full `plan.yaml`-vs-other-artifact branch (the
`plan.yaml` arm alone runs `subprocess.run`, forwards both streams, and checks the exit code) in one
body. This is exactly the shape the risk-grading skill's "one reason to change per function"
pattern flags: extracting the `plan.yaml` delegation into its own helper (e.g.
`_adopt_plan_yaml(canonical, quarantined) -> int`) would drop `cmd_adopt`'s own branching back
toward the dispatch-only shape `cmd_list`/`cmd_discard` already have.

### F-2 / F-3 — two grade-2 `plan-sign-gate.py` functions: reasoned, non-blocking

`_invocation` (`:309`, grade 2, cognitive driver, med) and `quarantines` (`:339`, grade 2,
cyclomatic+cognitive+abc, med). Both are a sequence of independent, spec-mandated early-return
guards (D-13's six-step fail-open matrix), not accidental nesting — `quarantines` mirrors the
pre-existing `denies()` sibling's shape by design (T-07's own instruction: "mirroring denies()'s
shape so the two rules read as siblings"), and `denies()` itself is ungraded here only because it
is unchanged in this diff. Splitting further would separate steps that only make sense read as one
sequential decision. Accepted at grade 2 per policy (never blocks); reasons recorded per function as
required.

### F-5 — `test-quarantine.py:109 case_1_2_...`: reasoned, non-blocking

Grade 2 (bar 3 for test code), ABC 29.6 driven by six sequential `check(...)` assertions against one
fixture (adopting a one-task quarantined `plan.yaml` onto a 14-task canonical). This matches this
test file's and its siblings' (`test-check-domain.py`, `test-plan-sign-gate.py`) established
convention of asserting several facts about one scenario in one case function rather than
fragmenting one logical test across several. Accepted at grade 2.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Stage 1 spec compliance clean; Stage 2 finds a real fail-open in validate-digest.py's new suspension branch (F-1, high) plus one blocking code_grade record in quarantine.py (F-4, high)
  severity_max: high
  findings: 5
  must_fix:
    - "F-1: hook_mode()'s live-children refusal at validate-digest.py:1711 skips an absent/null last_assistant_message, allowing a lead/orchestrator with live children to exit 0 instead of being refused (validate-digest.py:1656-1736)"
    - "F-4: quarantine.py:100 cmd_adopt is grade 3 in production code (cyclomatic 7, cognitive 10, ABC 22.5, driver cognitive+abc), below the grade-4 bar"
  spec_violations: []
  code_grade: fail
  reviewed: "0bc57c887b06a5f651363153b5895437c6748e6d..fa5ce88e07d0a094570da25bf1110370ef84fcab"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "F-1's remedy narrows the fix to hook_mode() alone (restore 'any live kids -> refuse unless legally suspended'); confirm this doesn't reopen a case T-01's six new labels were written to close before applying it.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-51-claude-code-lifecycle-safety/.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/review-harness-code-reviewer-panel-c1.md
```
