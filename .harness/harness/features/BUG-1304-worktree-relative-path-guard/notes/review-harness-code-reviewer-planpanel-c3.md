# Plan-panel review — code-reviewer — BUG-1304 — cycle 3

## BLUF

Cycle 8's repair applies the fourth binding ruling's nine `required_plan_repairs` **faithfully**,
against `plan.yaml`/`BRIEF.md` text directly (not pm's claim). The plan is internally consistent:
no dangling `depends_on: T-08`, no lingering unresolved operator choice, the TTL backstop is the
existing `86400`/`1200` pair with no second horizon, SC-10 and SC-12 are genuinely disjoint
fixtures, and the three follow-up issues are recorded `REQUIRED`. One real, repair-adjacent gap
survives: **T-07's `verify` gates none of obligation 1c** (D-10's unreadable-registry doctrine
text), so a doer can satisfy T-07's verify while silently omitting the very content the fourth
ruling required be recorded. `must_fix`? No — it is docs-only, doesn't affect enforced behaviour,
and every runtime path this ruling touches is independently pinned by T-01/T-02/T-03/T-05. Rated
`med`, not gating.

## Nine `required_plan_repairs` — item-by-item fidelity

| # | Repair | Verdict | Evidence |
|---|---|---|---|
| 1 | REQ-05 scoping sentence; REQ-03 unamended | **APPLIED FAITHFULLY** | `BRIEF.md:75-81` — "THAT REFUSAL IS SCOPED, NOT FACTORY-WIDE ... REQ-03 is therefore not amended: its promise ... is kept unconditionally." REQ-03's own body (unread condition list) is unchanged text. |
| 2 | New SC-12, both routes, both halves, SC-06 proof on refusal half | **APPLIED FAITHFULLY** | `BRIEF.md:221-236` — `verify: automated evidence: integration`, allow half + refusal half stated separately per route, refusal half cites `bug1304_assert_pre_change_allows` explicitly. |
| 3 | SC-10 unchanged, disjoint from SC-12 | **APPLIED FAITHFULLY** | `BRIEF.md:234-235` states disjointness in text; fixtures independently confirmed disjoint at `plan.yaml` T-03 cases 14/15 (agent's ONLY claim is corrupt) vs cases 16/17 (agent's OWN claim readable, a SEPARATE unrelated registry corrupt) — genuinely different fixture shapes, not merely asserted. |
| 4 | D-10: (a) selected, (b) one-line-rejected, cost rescoped to (a), F2 paragraph untouched | **APPLIED FAITHFULLY** | `plan.yaml:494-499` (a) selected; `:500-503` (b) reduced to a single rejection sentence + reason; cost paragraph at `:465-475` (not shown above, read in full) is stated at (a)'s scope; F2 asymmetry paragraph at `:509-524` matches cycle-2's own med finding wording verbatim in substance (same anchors `harness_boundary.py:170-173`/`:177-183`). |
| 5 | T-02 seam shape: 3rd param, `S_p`/`U`, shared containment primitive, no "unresolved operator choice" text | **APPLIED FAITHFULLY** | `plan.yaml:701+` intent — `claim_worktrees(owner_root, agent_type, destination)`, three-clause ordering matches D-10 verbatim, "THE MEMBERSHIP TEST IN CLAUSE 1 USES THE SAME CONTAINMENT PRIMITIVE THE GUARDS USE." No "unresolved operator choice" string anywhere in T-02. |
| 6 | T-01 case 7 rewritten (refusal), case 8 added (allow); integration 9/10 unchanged; no id collision with cycle-2's F4 case-8 | **APPLIED FAITHFULLY** | `plan.yaml:562+` — `test-harness-boundary.py`'s `case_bug1304_claim_set` cases 7/8 match the ruling's refusal/allow halves exactly. F4's case 8 lives in a **different file and enumeration** (`test-inflight-registry.py`'s live_claims cases 1-10, with F4's OMP-backdate case at position 8 and the two unreadable-registry cases correctly shifted to 9/10). The two "case 8"s are in disjoint enumerations; neither collides with or silently overwrites the other. |
| 7 | T-03/T-05 SC-12 pair; floors 9→10, 11→12 as exact panel-style floors; F5 def-exclusion intact | **APPLIED FAITHFULLY** | T-03 cases 16/17 (`plan.yaml` ~956-978), floor text lists exactly 10 named cases and `verify` reads `test "$n" -ge 10`. T-05 cases 18/19 (~1170-1190), floor text lists exactly 12 named cases, `verify` reads `-ge 12`. Both verify blocks still pipe through `grep -vc '^ *def bug1304_assert_pre_change_allows'` before comparing. |
| 8 | T-04/T-06 pass resolved absolute destination as 3rd arg; catch-and-exit-2 clauses stand | **APPLIED FAITHFULLY** | T-04 (`plan.yaml:976+`): "passing the RESOLVED ABSOLUTE DESTINATION as the third argument"; catches `UnreadableRegistry` where `AmbiguousWorktree` is caught, exit 2. T-06 (`:1203+`): identical language, "exactly as T-04 does." |
| 9 | T-07 obligation 1c scoping sentence | **APPLIED FAITHFULLY (text) — see finding F-C3-1 for its verify)** | `plan.yaml:1267+`, obligation "1c." — "THE REFUSAL BINDS EXACTLY THE GOVERNED WRITES THE READABLE ROOTS CANNOT PLACE" is present verbatim in substance. |

## Step 2 — consistency and consequential edits

- **T-08 dependents**: grepped every task's `depends_on` — none names `T-08` (T-01 `[]`, T-02 `[T-01]`,
  T-03 `[T-02]`, T-04 `[T-02,T-03]`, T-05 `[T-02]`, T-06 `[T-02,T-05]`, T-07 `[T-04,T-06]`, T-09 `[T-02]`,
  T-10 `[T-02,T-04,T-06,T-07]`). Confirmed clean.
- **T-09/T-10 prose**: T-09 (`plan.yaml:1411+`) opens "IN SCOPE, AND SETTLED... not strikeable and no
  part of it is an open question" — no reference to T-08 as live/strikeable. T-10 (`:1521+`) states
  "T-08 is struck and lands nothing" (past tense, correct) and "No task in this plan is strikeable
  any longer."
- **T-07 obligation 1b's strike sentence**: absent everywhere — T-07's 1b instead reads "Write no
  conditional sentence about a strike: T-09 is in scope, settled by the fourth binding ruling."
  BRIEF SC-11 (`BRIEF.md:207`) reads "carried by T-09, which is IN SCOPE ... not conditional on
  anything" — non-conditional, matches Q2's ruling.
- **Backstop constant**: grepped every `TTL_SECONDS`/`86400`/`1200` occurrence in both files (61
  hits) — every value is either the existing `OMP_UNVERIFIED_TTL_SECONDS` (always cited as `86400s`)
  or the existing `CLAIM_TTL_SECONDS` (always `1200s`). No new constant name, no third number.
- **Three required follow-up issues**: D-11 (`plan.yaml:525+`) lists all three (dispatch-guard
  `_root_for`, `linked_worktrees` fail-open/F2, `validate-digest` `live_children`/OC-3) and states
  "filing them is REQUIRED, not optional."
- **No unresolved operator choice**: grepped `OC-[0-9]|open.?choice|operator choos|unresolved` across
  both files. Every `OC-1`/`OC-3` hit is either (a) inside the frozen cycle-1 panel-history block
  (`plan.yaml:207`, `verified_closed_at_cycle: 2`, historical record of what was true at cycle 1 —
  not live text) or (b) D-11's own required-filing language for OC-3, which is the correct closed
  disposition, not an open one. Every `operator` hit resolves to "ratified"/"authorised"/"no operator
  choice remains" — none reads as a live pick-one-of-N. `panel.findings[F1].disposition` is
  `resolved` and F2's is `separate_issue_required`, as the acceptance brief states; confirmed against
  the actual YAML, not taken on trust.

## Step 3 — bounded adversarial sweep

**Q1 — does SC-12 or the three-clause ordering assert something no task produces?** No. Both halves
trace to a producing task at every level: seam (T-02's clause 1/3), unit (T-01 cases 7/8, `test-harness-boundary.py`),
guard-level (T-03 cases 16/17; T-05 cases 18/19), and wiring (T-04/T-06 pass the destination through
and catch the exception at the documented seam). No orphaned assertion found.

**Q2 — does the partial-S allow open a new discover-nothing/refuse-nothing path?** No. D-10's clause
1 ("d inside a member of S_p → allow, whatever U holds") is sound by the ruling's own superset
argument: S_p only grows as more registries become readable, so a destination already proven inside
a member stays proven regardless of U. Clause 3 (U non-empty, d not in S_p → raise, naming every
U member) covers every other case, including the all-registries-unreadable extreme (S_p empty, U
full → refuse). I could not construct a fixture where the ordering both discovers nothing and
refuses nothing; the only genuinely fail-open surface in this feature's read path remains F2
(`linked_worktrees`), already named, already required to be filed separately (D-11), not reintroduced
by this repair. This is the third look at the class and it comes back clean for the repair itself.

**Q3 — is any touched `verify:` still satisfiable without the thing it claims?** One genuine gap,
reported below as F-C3-1 (T-07). T-01/T-02/T-04/T-06/T-08 verifies are exit-code or exact-count
based and unaffected by the repair's edits in a way that weakens them. T-03/T-05's `-ge` floors are
minimums (not `-eq`), same as at cycle 2 when this shape was reviewed and found matching exactly —
unchanged by cycle 8, not a new gap.

## Findings

- **id**: F-C3-1
  **severity**: med
  **summary**: T-07's `verify` (`plan.yaml:1276-1282`) greps for `CLAIM-SET MEMBERSHIP`, `the
  assigned worktree`, `OMP_UNVERIFIED_TTL_SECONDS`, `inflight_registry.py:30-35`, and a negative
  check on the old DEC-153 bullet — none of which touches obligation 1c's content (D-10's
  unreadable-registry doctrine text, `plan.yaml:1267+` "THE SAME ENTRY CARRIES D-10 ... THE REFUSAL
  BINDS EXACTLY THE GOVERNED WRITES THE READABLE ROOTS CANNOT PLACE").
  **consequence**: a doer can satisfy every clause of T-07's `verify` and thereby have the task
  marked complete while writing a `DECISIONS.md` entry that never mentions D-10's
  unreadable-registry refusal or its scope at all — silently dropping the doctrine record of a
  panel-cycle-2 HIGH finding's resolution (F1, `PF-055b89703a96f6c82edc6d37e6fb973c`) that REQ-07
  exists specifically to capture. Not gating: it is docs-only, the enforced runtime behaviour is
  independently pinned by T-01/T-02/T-03/T-04/T-05/T-06's own tests regardless of what
  `DECISIONS.md` says, and cycle 10 is signature-packaging only so this is advisory for the
  operator to weigh, not a blocker on the repair's own merits.

## Verdict rationale

No `must_fix`; `severity_max = med` (F-C3-1). Per the gating rule, `must_fix` empty and
`severity_max < high` → `PASS with notes`.
