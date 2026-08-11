# QA gate-only re-run — FEAT-11 — pinned `review_sha 2ea9af3`

**PASS.** Matrix re-run over the full range `8dedeae..2ea9af3` (both T-01 `5c433f2` and the MF-1 fix
`2ea9af3`), gated at HEAD = `2ea9af3324ab1ef175fe8ef2307f5c850edfd315`. `5c433f2` is not itself gated
— only reconstructed to confirm what MF-1 changed. Both required kinds green, real counts. The MF-1
fix is real, targeted, and now demonstrably discriminating (mutant proof below).

## Pin and range integrity

- `git rev-parse HEAD` = `2ea9af3324ab1ef175fe8ef2307f5c850edfd315`, the requested pin.
- `git diff --stat 8dedeae..2ea9af3 -- .claude/skills/harness/bin/` = exactly the three handed-down
  surfaces: `factory_gh.py` (134 changed lines), `test-factory-gh.py` (245), `test-factory-integration.py`
  (26). No other `bin/` file moved across the **whole** range.
- `git diff --stat 8dedeae..2ea9af3 -- test-factory-decompose.py test-factory-claim.py
  test-factory-land.py` is **empty** — SC-08's "unedited" claim now verified at the pin, not just at
  `5c433f2`.
- Working tree has unrelated uncommitted edits (`feature.yaml`, `.harness/logs/2026-08-10.md`,
  untracked `FEAT-12-…`) — not mine, not part of this diff, ignored. `git status --porcelain --
  .claude/skills/harness/bin/` is **empty**: the surfaces I gate equal the pin exactly.

## Matrix — per-kind results

`change_type: bugfix`. Floor = `unit` (always) + `integration` (SC-09's evidence lives only in
`test-factory-integration.py`, an `INTEGRATION_SCRIPTS` file). Same floor as the prior gate; nothing
in the MF-1 diff changes the change type or warrants a kind beyond it.

| kind | cmd | state | result |
|---|---|---|---|
| unit | `run-unit-tests.sh --kind unit` | satisfied | 10/10 scripts PASS; `test-factory-gh.py` **118/118** |
| integration | `run-unit-tests.sh --kind integration` | satisfied | 12/12 scripts PASS; `test-factory-integration.py` **97/97** |

`matrix_ok: true`. Denominator (P-04): 1/1 diffed tasks (T-01, carrying the MF-1 amendment) had a
kind requirement; both required kinds ran and are green for it.

No stray `test-*.py` in `bin/` (22 files = 10+12 union). No `gh` live call in either bucket
(`test-factory-integration.py` routes through a fake `FACTORY_GH` binary; `test-gh-sync.py` the only
other `gh`-shaped reference, also fully stubbed) — same finding as the prior gate, re-checked at this
pin.

## The 118/118 question — measured, not corroboration by count alone

**Unit count did not move: 118/118 at both `5c433f2` and `2ea9af3`.** By itself that count is
ambiguous — it cannot distinguish "the fix is real" from "the fix didn't run." Two independent checks
resolve it:

1. **`check(` call count is identical** across the two commits (97 in both) — MF-1 changed the
   *argument* three existing checks assert against, added no new `check()` call and removed none. An
   unchanged total is the expected shape of a value-substitution fix, not evidence either way on its
   own.
2. **Mutant proof, run in the scratchpad against copies (never in-place):** hardcoded the literal
   `"owner"` into `factory_gh.py`'s owner-not-found raise (`:259`, replacing the interpolated `owner`
   variable) while leaving the post-MF-1 test file (asserting `"acmeuser" in str(exc)`) unchanged.
   Result: **1 of 118 FAILING** — `unknown owner: raises GhError naming the owner` reddens. The fixed
   check now discriminates a regression that strips interpolation.
   `git status --porcelain -- .claude/skills/harness/bin/` confirmed empty afterward — the mutation
   lived only in the scratchpad copy, nothing touched in place.

**Mechanism confirmed directly:** `factory_gh.py:259-260` — `"project owner not found", owner,
"check the owner login"` — the fixed prose around the value slot contains the bare word **"owner"**
twice. Before MF-1, the assertion `"owner" in str(exc)` passed whether or not `owner` was actually
interpolated, because the surrounding fixed text alone satisfies it. `"acmeuser"` occurs nowhere in
this file's fixed prose, so the post-MF-1 assertion can only pass if the caller's actual login value
reaches the message. **The unchanged count is corroboration, but only because the mutant shows the
check can now fail — the count alone would not have told me that.**

Same reasoning and same mutant-shape applies to the two sibling asserts MF-1 also moved
(`organization (...): raises GhError naming the owner` at `:432-433`, `board absent: raises GhError
naming owner + project number` at `:455-456`) — not independently mutant-proven this pass (one
targeted proof against the shared pattern is sufficient corroboration; all three moved together per
the MF-1 receipt and share the identical "value replaces a word already in fixed prose" defect shape).

## SC coverage — line citations re-grepped at 2ea9af3 (P-01: stale citations are a live risk)

MF-1 inserted comment blocks above the three moved asserts, shifting everything from line ~400
onward in `test-factory-gh.py`. Lines before that point are unchanged from the prior gate.

| SC | covered_by | evidence (re-grepped at 2ea9af3) |
|---|---|---|
| SC-01 | uat | operator-run, board 6, not mine |
| SC-02 | unit | `test-factory-gh.py:292` one `gh api graphql` call asserted; quoted `"field-list"`/`"project","view"` absent from `factory_gh.py` (unchanged, unmoved by MF-1) |
| SC-03 | unit | `factory_gh.py` `_FIELD_QUERY`; regex guard unmoved (before line 400) |
| SC-04 | unit | option-absent `:332`; field-not-single-select `:476` (was `:466`, shifted +10) |
| SC-05 | unit | org fixtures `:432-433` (was `:427-434`, shifted) — both label iterations, dead-branch mutant still applicable (not re-run this pass; logic untouched by MF-1) |
| SC-06 | unit | `:455-456` (was `:447-453`, shifted) board-absent, distinct message |
| SC-07 | unit | zero item-edit assertions, present at `:412`, `:434`, `:457`, transport-failure case (unmoved) |
| SC-08 | unit+integration | sha256-pinned unedited (task verify) **and** `git diff --stat 8dedeae..2ea9af3` over all three files is empty, confirmed at the pin, not just at 5c433f2 |
| SC-09 | integration | `test-factory-integration.py` 97/97 on the integration KIND command |
| SC-10 | unit | positive clause: `:411` (acmeuser), `:433` (acmeuser), `:456` (acmeuser project 3) — now genuinely discriminating per the mutant proof above; negative clause ("never api graphql"): `:335`, `:415`, `:440`, `:462` (all shifted from prior gate's `:335/:410/:434/:453`) |
| SC-11 | unit | `:410-415` (was `:406-410`) unknown-owner, distinct from org and board-absent |
| SC-12 | unit | `:476-481` (was `:466-472`) field-not-single-select, empty-dict fixture, same error as field-absent |

## Coverage gaps (disclosed in BRIEF, not new findings)

- No test kind measures GraphQL cost — SC-01 rests on operator UAT. (BRIEF `## Verification gaps`, ¶1)
- The organization exit-0 fixture (`GRAPHQL_ORG_OK_JSON`) remains **derived, not measured** — no
  organization-owned board is reachable from this account. (BRIEF ¶2, prior gate's own O-01 note —
  naming it again here costs nothing and keeps a future reviewer from assuming coverage exists.)
- The genuine transport/auth failure (SC-10's negative clause) is stub-only — cannot be provoked
  without breaking authentication. (BRIEF ¶3)

None of these are new; all three are the BRIEF's own disclosed limits, re-affirmed unchanged at this
pin.

## Test-first / MF-1 order

MF-1 landed as a single commit (`2ea9af3`) on top of the finished T-01 work — its own receipt
(`notes/receipt-harness-backend-dev-MF-1-c1.md`) frames it as a targeted correction to a
qa-flagged vacuous assertion, not new behavior requiring its own RED/GREEN cycle. Not re-litigating
that framing here; it is consistent with what the diff actually shows (three comment+argument edits,
no new `check()` calls, no production-code branches added).

## Enforcement-layer defect encountered — not mine to fix

`bash-write-guard.sh` mis-parsed `cp ... 2>/dev/null` — it treated the redirect target as if it were
a `cp` destination and blocked the command as out-of-domain, even though the actual `cp` target was
inside my own scratchpad. Worked around by dropping the `2>/dev/null` redirects; commands ran clean
after. Raised as `open_questions` below per the harness-expertise rule (a harness bug belongs there,
not in Expertise, where a workaround would outlive the fix).

## What I did not do

Did not touch `run-unit-tests.sh`, any DEC-174 carve-out file, or anything under `bin/` in place. The
one mutant proof ran against scratchpad copies only; `git status --porcelain -- .claude/skills/harness/bin/`
confirmed empty after. No commit. Did not re-run the full Q1/Q2/Q3(a) analysis from the prior gate —
none of it depends on code MF-1 touched (D-03 dead-branch logic, the fragment-boundary reachability
argument, and the D-04 frozen-literal check are all in `factory_gh.py` regions MF-1 did not edit), so
re-deriving them here would be re-running the same measurement over an unchanged surface, not new
verification.
