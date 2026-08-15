# Goal-check — FEAT-03-subissue-mirror — c0

## Verdict: PASS. Twelve of twelve `met` (SC-01..SC-12). SC-13 carved out, not adjudicated.

The feature delivered. Every REQ traces to shipped code, all seven `automated` SCs are named to a
specific passing test (not to a green suite), and all five `inspection` SCs were re-inspected by
direct command in this run rather than inherited from qa's digest. No SC returns `not_met` or
`partial`, so no fix cycle is routed.

## The one contested call: SC-12 is `met`, and validator-lead's finding rests on a wrong premise

validator-lead (`runs/2026-07-31-12-validator/digest.md:32`) held that SC-12's evidence does not span
its text because "NO line names `ship`'s environmental skip". **The premise is wrong about which verb
is new.** BRIEF `## Problem` (`:19-20`): `gh-sync.py` already had `open`, `close-task`, `backlog` and
`ship`, and **no abandonment path at all**. So `ship` is an **old** subcommand and `abandon` is the
only new one. SC-12 demands "the new subcommands as well as the old"; it never demands `ship`
specifically, and it never demands per-verb coverage of each reason.

SC-12 has two dimensions, and each is spanned by a named test:

| Dimension | Spanned by |
|---|---|
| sync off | `test-gh-sync.py:172` (`open`), `:529` (`abandon`) |
| repo unpinned | `:176` |
| gh missing | `:168` |
| a failing API call | `:353` (mid-flight `gh()` rejection, exit 0 + SKIP) |
| the **new** verb | `:529` — `abandon with sync disabled -> SKIP, exit 0` |

I ran the discriminator both halves the dispatch asked for. **Half 1:** `:167-176`'s three generic
guards all invoke `open`, an old verb — so they alone do not span the new one; `:529` does, and it is a
test name, not a source read. **Half 2:** "a failing API call" is covered at `:353` via
`FAKE_GH_ATTACH_FAILS` (`:113-138`), which is `open`'s attach path — the reason is spanned, the verb
there is old.

**The admissibility rule does not bite.** I did not use `gh-sync.py:443` / `:96-110` as evidence and
did not need to: under SC-12's plain reading there is no gap to close, because both dimensions carry a
named passing test. The cross-product reading (4 reasons × each verb) would demand eight-plus tests
and is a strictness SC-12's text does not state — PLAN:149's own evidence line names five labels, not
a matrix.

**One precision correction, and it is what seeded the confusion:** `:353`'s label reads "failed attach
is a SKIP, exit 0, **for the new subcommand too** (SC-12)". That clause is factually false — the
attach is inside `cmd_open`. I cite `:353` for the failing-API-call *reason* only, never for the
new-verb half. See Q1.

## SC adjudication — all twelve

| SC | Verdict | Method | Evidence (re-verified this run) |
|---|---|---|---|
| SC-01 | met | automated | `test-gh-sync.py:193,217,218,237,318` — parent created/recorded, three attaches, internal id not number, crash-resume attaches the recorded-not-attached task, re-run duplicates nothing |
| SC-02 | met | automated | `test-gh-sync.py:244,245` — exactly one `issue close`; `:245-246`'s negative is scoped to the fake-gh `closes` list, not stdout, so the absorbed-numbers print does not make it vacuous |
| SC-03 | met | automated | `test-gh-sync.py:381,385,387,391,417,445` — all three parent-origin cases asserted separately; `:387-389` also asserts the reason text is absent from the log |
| SC-04 | met | automated | `test-gh-sync.py:553,578,583,605,635,658` — `:635-638` asserts the **flag form** (`--body-file` present, path present, exactly one comment on #40), not merely a call count; `:583` carries the unconditional milestone inside the *adopted* fixture, which is the discriminating placement |
| SC-05 | met | automated | `test-gh-sync.py:212,214,297,324,328` plus `:237` — `:237`'s re-run reads `attached:` back from disk in a fresh process, which is the attach-receipt round trip |
| SC-06 | met | inspection | `wayfind.py` — all four absence greps **0**; carve-out presence greps both **1** (`sub_issues", "--paginate"`, `dependencies/blocked_by",$`); `grep -cE 'parent_args\|blocked_by_args' gh-sync.py` = **0**; five builders at `gh_issues.py:13,17,21,25,29` |
| SC-07 | met | inspection | `harness.json test_kinds.unit.cmd` = `run-unit-tests.sh`; `run-unit-tests.sh:6` lists both named scripts (plus T-07's third); `detect` resolves to all three files (was `[]`) |
| SC-08 | met | automated | `test-check-state.py:64,74,84,95` — three fixtures plus "exit code unchanged by INV-21 (a: 1, b: 1)"; warn level confirmed at `check-state.sh:382` (`warn.append`, not `bad`) |
| SC-09 | met | inspection | zero `sub_issues_summary` assertions in `bin/` (sole match is a docstring at `test-check-state.py:6`); `test-gh-sync.py` fakes gh solely via `GH_SYNC_GH` (`:103`); no `gh` invocation in `test-check-state.py` or `test-validate-digest.py` |
| SC-10 | met | inspection | only FEAT-03's own `feature.yaml` is in `4d00dbc..HEAD`; its `github:` block (`:81-84`) still reads `parent: none` / `milestone: none` / `issues: {}` — the two diff hits are `cycles_used` and a `skipped_segments` reason string, not the block. Zero `backfill\|retrofit\|migrat` matches in `gh-sync.py`, `gh_issues.py`, `wayfind.py`, `check-state.sh` |
| SC-11 | met | inspection | `check-docs.sh` exit **0** ("no stale statements found", 45 patterns / 77 files); `amendment 7` count 1 in `DECISIONS.md`; `check-state.sh` output carries **no** `INV-10` line |
| SC-12 | met | automated | `test-gh-sync.py:168,172,176,353,529` — see the ruling above |

## REQ coverage — 9 of 9 traced

REQ-01/05 → T-03 (`cmd_open`). REQ-02/03 → T-04 (`cmd_close_task`). REQ-04 → T-05 `cmd_abandon` +
T-06 `cmd_ship`. REQ-06 → T-02 (`gh_issues.py`). REQ-07 → T-07 (`check-state.sh:366-382`). REQ-08 →
T-01 (`run-unit-tests.sh`) and SC-09's no-real-gh receipt. REQ-09 → T-08 (DEC-138 am.7) **for the
DECISIONS half only**; its second half ("no live prose states the superseded contract") is SC-13's,
carved out of this check and owned by the main session.

## UAT census: the gate does not apply

Confirmed from BRIEF myself, not inherited. 13 `verify:` lines against 13 `SC-NN` — **7 `automated`,
6 `inspection`, 0 `uat`, 0 `manual`**. `harness.json` sets `uat: blocking_when_uat_criteria_exist`;
no uat criterion exists, so the gate does not fire and **no UAT script is needed**. 13 methods against
12 `sc_status` entries is the SC-13 carve-out, not a discrepancy.

## What rests on the fake `gh` — say it precisely at the briefing

`github.sync: false`, `github.repo: null`, so all three mirror sync points SKIP in this repo and every
GitHub assertion runs against `test-gh-sync.py`'s fake `gh` (`GH_SYNC_GH` override).

- **Rests on the fake — SC-01, SC-02, SC-03, SC-04, SC-05, SC-12** (six of the seven automated SCs).
- **Does NOT rest on the fake — SC-08.** `test-check-state.py` drives `check-state.sh` over temp-dir
  fixtures and invokes no `gh` at all.
- **The five inspection SCs are static/structural** (greps, config reads, a diff) — no gh either way.

BRIEF `## Verification gaps` (`:161-166`) already records this. The briefing must not overstate it:
the **first live `open` on a sync-enabled project stays a user-gated moment**, and DEC-168's measured
probe — not this suite — is what carries the real API's closure semantics.

## The four reviewer findings move no verdict

F1 (`post_body_path` catches only `OSError`, so a non-UTF-8 file tracebacks instead of `die`ing) is
real, but **no SC claims non-UTF-8 error handling**; the empty, unreadable and nonexistent cases each
have a passing test (`:475`, `:494`, `:482`). F2 (`wayfind.py` untested), F3 (positional args before
flags) and F4 (a stale line anchor in am.7) likewise touch no SC's claim. All four are backlog
candidates, none a goal-check gap.

## Two baseline notes the briefing should not inherit stale

1. **`check-state.sh` now exits 0** in this repo (measured this run; only a `note` about an orphaned
   `2026-07-31-13-product` run dir). qa observed exit **1** with a `notes/handoff-build.md` missing
   VIOLATION; that file now exists (`notes/handoff-build.md`, 3896 bytes). The baseline moved in the
   safe direction. SC-11 asserts INV-10 clean, not an exit code, so no verdict changes.
2. **SC-07 says "both bin test scripts"** — written when two existed. `run-unit-tests.sh:6` now lists
   three (T-07 added `test-check-state.py`). Met *a fortiori*: both named scripts are in the explicit
   list and `detect` resolves to all three. Not a discrepancy.

## Open questions

- **Q1 (non-blocking, defect in a test label):** `test-gh-sync.py:353`'s label claims "for the new
  subcommand too (SC-12)" but the failed attach is inside `cmd_open` — an **old** subcommand. The
  label asserts something false and is what seeded validator-lead's SC-12 finding. A one-word label
  fix, routable to eng-lead as a chore. It does not change SC-12's verdict.
- **Q2 (non-blocking, EMERGENT — not an SC, not mine to adopt):** BRIEF never stated it, so I did not
  gate on it. A mid-flight `gh()` failure in `cmd_abandon` **step 1** (the reason comment) calls
  `skip()` → `sys.exit(0)`, so the abandonment exits 0 having closed **no** sub-issue and **no**
  milestone, with only a SKIP line. That satisfies SC-12 literally (exit 0, one SKIP) but leaves the
  terminal state half-done and no re-run receipt marks it. **Judgement: new, not covered by any
  existing SC.** Recommendation: a Feature-B-adjacent BRIEF item, not a FEAT-03 fix — adopting it now
  would be an unapproved SC. Reaches the user through the orchestrator.
- **Q3 (non-blocking):** `wayfind.py` has zero runtime coverage in the `unit` runner while T-02 made
  it import-dependent on `gh_issues.py` (three reporters: eng-lead Q3, qa gap 1, validator F2). SC-06
  is `inspection` and structural grep only. Recommendation: a `test-wayfind.py` as a backlog chore —
  and note that adding one requires editing `run-unit-tests.sh:6`'s explicit list, or the drift
  detector exits 2 MISCONFIGURED.
- **Q4 (non-blocking, records a settled count):** the "eight `evidence: unit` SCs" figure that
  circulated upstream is wrong. My own full BRIEF parse: `grep -c 'verify: automated'` = **7**,
  `grep -c 'verify: inspection'` = **6**, uat/manual = **0**. qa's correction stands.

## Nothing staged, committed, reverted or stashed

The orchestrator holds the pen (DEC-153). No probe file created, so the runner's exit-2 drift
detector is not poisoned. BRIEF.md and PLAN.md untouched — the two SC wording issues above are
recorded as open questions, not edits.
