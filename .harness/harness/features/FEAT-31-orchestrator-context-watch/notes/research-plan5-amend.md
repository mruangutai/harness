# plan5 amend — SC-07 and SC-13 have tasks, D-02 is settled, the discovery clause agrees with itself

**BLUF.** All four jobs complete. `plan.yaml` is 18 tasks / 26 decisions, `safe_load` clean,
`approval:` byte-identical (hash matches), `check-plan-routes.py` exit 0 / 0 violations,
`check-domain.sh --post` exit 0. Every task with a recorded PASS still passes under the
strengthened assertions. **The operator must re-sign in my view** — the task set grew by four, three
of them main-session-direct.

**The worktree is at `2cf792f`, not the `294a1a7` the dispatch named.** `main` was merged in
(`2cf792f`), which carries `d065b3b` — **PR #658 is MERGED**, so the reason the dispatch gave for the
red unit suite no longer holds. Every number below was re-measured at `2cf792f`, none inherited.

## Job A — SC-07 and SC-13 got four tasks

| task | lane | cites |
|---|---|---|
| T-15 SC-07 | main-session-direct | DECISIONS.md 4859-4862 and 4864-4867 @2cf792f |
| T-16 SC-13 library | team, harness-backend-dev | 4864-4867 (the split it satisfies) |
| T-17 SC-13 cutover | main-session-direct | 4859-4862, 4864-4867 |
| T-18 test_kinds | team, harness-dev-ops | grant-forced, D-18 |

**SC-07 needs no `check-domain.sh` edit, which falsifies BRIEF.md:231-237.** `check-domain.sh:815`
already calls `feature_schema.problems_for_text`, so the gate's rule table is
`feature-schema.json` + `feature_schema.py`. That makes the module/cutover split **unavailable** here:
the library write *is* the cutover. Said explicitly in T-15's `execution_reason` (D-23).

**SC-07's two halves are in direct tension and only a positional rule satisfies both** (D-23).
Measured: 31 `feature.json`, **390 `runs` entries, keys exactly `id`/`squad`/`verdict`**. A schema
`required` denies all 31 — and the POST sweep reaches untouched files, so every Bash command exits 2.
Rejected with reasons: an on-disk **diff** (only the PRE `Write` route carries content —
`check-domain.sh:1027-1034` — green-and-incapable-of-red on the other three); a **date-prefix cutoff**
(175 of 390 ids are not date-prefixed, and FEAT-31's own six are all non-date, so the rule would
almost never fire); a **monotone suffix** (holed by exactly the one entry that matters). Chosen: a
frozen exempt-**count** per feature, default 0, measured at land time.

**SC-13's matcher was measured, not assumed** — the one thing `probe-hook-delivery-channel.md` told
the plan to check. Across the 25 most recent orchestrator transcripts, 3280 `tool_use` events:
**Bash 2858, Write 221, Agent 121, Read 78, SendMessage 2**. The existing `PostToolUse`
`Write|Edit|Bash` entry covers **3079/3280 = 93.9%**. No new matcher. `Edit` appears zero times; the
dispatch tool is `Agent`, not `Task` (D-25).

## Job C — the discovery clause, corrected, and two folded fixes

Re-measured today: one-level glob **0**, two-level **2004**, **104** `harness-orchestrator`, across
three project dirs. The clause now states the two-level layout and that a no-argument run scans
**every** project dir — SC-01/SC-10 are the authority, and REQ-05's worktree orchestrators have their
own project dir (9 in the `fix-harness-tooling-backlog` slug).

Both folded fixes are **clause corrections, not scope changes**: the clause's own words produce
numbers the signed criteria forbid. `current` — agent `a7783f0ec41e6a8c6`: **1046 lines parse, 669
carry `message.usage`, peak 696,472, last member 696,472, last LINE has no usage → `current` 0** for
an orchestrator holding 696,472. `entries` — the 1046/669 ambiguity leaves T-13's three-figure
agreement undefined, so it could fail on a correct tool. Both are now one measured set (D-11, T-01).

## Job D — 8 tasks, 10 lines, 0 left

6 rule-failing (T-06, T-10, T-14×2, T-13×2) + 4 shape-only (T-02, T-05, T-07, T-12). All 10 converted;
none left. **`test-check-state.py` prints no summary line at all** — 90 `^ok` lines, so T-10's and
T-14's comment named an output that does not exist. Floors: `test-context-watch.py` 15, `test-check-state.py`
90, `test-upgrade-config.py` 9 (`9/9 cases passed.` — a different shape from `15 of 15 cases passed`,
so patterns are per-file), `test-validate-feature-json.py` 43 `^PASS `, `test-check-domain.py` 167 `^ok`.
`check-state.sh` handoff lines are **3, all `note`, 0 `VIOLATION`** — the old `0 at 7299669` is now
false of the total, so the assertion is on the `  VIOLATION  ` prefix (`check-state.sh:1366`).

**One assertion form I wrote and then rejected:** piping a test into `grep -q` swallows its exit
status, so a suite reporting `13 of 15` and exiting 1 would pass. Every verdict line is left bare.

## Defects found in passing

- **`D-21`'s `choice` was silently truncated 299 chars** by ` ##` starting a YAML comment — the whole
  "BRIEF.md's SC-15 still reads verify automated … this plan does NOT edit it" clause was invisible to
  every loader. Repaired (quoted); 440 chars now load. Pre-existing at `4930f9b3`.
- **DECISIONS.md anchor rot, 8 lines.** T-10/T-12/T-14, D-19/D-20/D-22 cite `4851-4854` and
  `4856-4859`; correct at `7299669`, now `4859-4862` and `4864-4867`. Exactly the B-11 shape — the
  claim survives, the pointer dies. Not rewritten (out of scope); my new tasks quote the paragraph's
  opening phrase alongside the line range and name the sha.
- **DEC-90 is STRUCK** (index line 109, 2026-08-21) but BRIEF.md cites it as a live `BLOCKS`
  constraint. Approved artifact, not mine.
- `check-state.sh` exits non-zero on **one** unrelated violation: FEAT-26's unapproved BRIEF.md.

## Open for the operator

1. **T-12 must run after T-18** or its cross-check reports KIND-DRIFT on `test-context-watch-hook.py`
   and fails every required CI step. I was instructed not to alter existing `depends_on`, so the edge
   is unencoded — recorded in D-26 and T-18's intent.
2. `D-25` warns on **every** crossing tool call. The stateless edge rule warns ~once but misses when
   the hook does not fire on the crossing call. Repetition chosen; the trade is real both ways.
3. T-17 must confirm what the probe could not: that hook stderr reaches the model as **context**, not
   only as a tool-result error string. If false, SC-13 is not met.
