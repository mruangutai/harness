# Goal-check — drafted plan vs the operator's stated intent — BUG-1309, cycle c0

**Does this plan deliver the operator's stated intent? Qualified yes.** Six of the eight settled
bullets are delivered outright, two are partial, none is missing. Two things must be settled before
signature: T-05 denies a merge on a **GitHub read failure**, which crosses `## Out of scope`
("Changing the user-gated merge policy") and DEC-138; and T-04's refusal message routes a legacy
in-flight feature to `gh-sync.py open`, which performs the other forbidden act (task-level
historical mirror records). Authority graded against:
`.harness/notes/grilling-mirror-build-entry-2026-09-06.md`, not BRIEF.md.

## Settled bullets — one row each

| # | Settled bullet | Carried by | Verdict |
|---|---|---|---|
| 1 | Ship = post-merge terminal phase | T-08 intent (github-mirror.md block, "Ship is post-merge terminal finalization only"), T-07, T-09 | delivered |
| 2 | Build entry = signed-plan transition running `open`; never Ship | T-08 (SKILL.md new step 1; trigger cell replaces "mission ship, right after the approval gate passes"), T-02, T-09 | delivered |
| 3 | Build refuses when the local outcome is absent; proceeds on a recorded temporary failure | T-04 intent branches (`None` → `refuse()` exit 2; `recovery-required` → stderr + continue) | delivered |
| 4 | Enabled sync → `opened` or `recovery-required`; config errors and partial remote writes block Build | T-02 steps 4–5, `decisions D-04` | **partially delivered** |
| 5 | Disabled/unconfigured sync → `not-applicable`, gates nothing | T-02 step 5; T-04 intent (config resolver skips before `cmd_start_task`); T-05 step 1; T-06 first skip; T-07 sync guard | delivered |
| 6 | `recovery-required` → rerun idempotent `open`; the user's merge action refused until a normal receipt | T-05 steps 5–6, `decisions D-02`, `D-07` | **partially delivered** |
| 7 | Legacy recovery = terminal receipt only, never historical sub-issues | T-03 intent ("creates ZERO task sub-issues", `github.issues` left as found), `D-05` | delivered |
| 8 | Legacy recovery during a GitHub outage stays non-terminal, keeps its worktree | T-03 (skip funnel records nothing) + T-07 (absent value ⇒ retain) | delivered |

**Row 4, what closes it.** Bullets 4 and 5 collide on one case the plan resolves silently: `github.sync: true`
with `github.repo` unpinned. T-02 step 5 sends *both* config-resolver skips to `not-applicable`, so an
enabled-sync project that never pinned its repo becomes a no-mirror project and Build proceeds —
bullet 4 says a local configuration error blocks it. Close it by making the "github.repo is not
pinned" skip pass no `build_entry` when `github.sync` is true (leaving the field absent, which
already blocks), reserving `not-applicable` for sync false/absent, and recording it as a D-NN.

**Row 6, what closes it.** See exposure 1 — the deny fires for a reason other than "a receipt is owed".

## The four exposures — consequences

**1. Over-delivery: T-05's new merge gate.** The gate itself is *inside* bullet 6, which asks in the
operator's own words for the merge action to be refused; a PreToolUse hook changes neither who
merges nor when they may, so it does not cross `## Out of scope` line 23. **One branch does cross it:**
T-05 step 5's third bullet DENIES when step 3 could not resolve the head branch. Step 3's `gh pr merge <n>`
route resolves through `gh pr view`. Concrete consequence: with `github.sync: true` and `gh`
unauthenticated or GitHub down, *every* `gh pr merge <n>` in the repo is denied — including for a
feature recorded `opened`, and including a PR that matches no harness feature at all, because step 4's
"no match: exit 0" is unreachable once step 3 has failed. That is a merge policy the operator did
not ask for. Closing change: on resolution failure exit 0 with a warning, unless the *locally*
resolved current branch (step 3's third route) maps to a feature that owes a receipt.

**2. Under-delivery / scope.** No violation of "requiring sync for `github.sync: false`" — T-05 step 1,
T-06's first skip, T-07's sync guard and T-04's pre-`cmd_start_task` resolver skip each hold, and
T-03 creates no task sub-issues. **But the second out-of-scope line is reachable through T-04.** No
existing feature carries `build_entry`, and T-04 carries no era guard (only T-06 does), so resuming
any task on a pre-existing sync-enabled feature refuses at exit 2 and instructs the operator to run
`gh-sync.py open <feature-dir>`. On a feature whose tasks are already done that call creates exactly
the historical task sub-issues the brief records as the rejected workaround (BRIEF.md:11-13). Closing
change: give T-04's absent branch the same frozen era-exempt set as T-06, or make its message route a
feature whose plan station is past `building` to `recover-terminal` only.

**3. The four delegated decisions.** D-01 (`github.build_entry`, absence as the refusing fifth state):
simplest durable behaviour — absence must carry meaning because the ~50 legacy `feature.json` files
have no field, and the era guard depends on that. D-02 (no age escalation): explicitly delegated, and
state-based-only changes nothing. D-03 (`recover-terminal`, report-and-ask, `--yes`): matches the
`cmd_abandon` precedent; no policy change. **D-04 is correct, for a reason the plan does not state.**
Traced: T-02 step 4 records nothing when `_BUILD_ENTRY["remote_written"]` is True → field absent →
T-04's `None` branch → `refuse()` exit 2. That is bullet 4's outcome, not an unrelated one. The state is
indistinguishable from "open never ran" *in that field*, but not in the document: `gh-sync.py:1039`,
`:1051`/`:1061` and `:1084` persist the milestone, parent and each issue id immediately after every
create, so a partial write is legible and the re-run adopts them rather than duplicating. One residual
misdirection: T-05 step 6 names `recover-terminal` for a feature whose station reads `done`; run on a
partially-written feature that recorded a milestone but no parent, T-03's refusal condition (milestone
**AND** parent) does not fire and it would stamp `recovered-terminal` on a feature that had a genuine
full open in flight. Worth one clause in T-03's refusal condition.

**4. DEC-138 (`DECISIONS.md:2948-2952`).** Per refusal: T-04 start-task — LOCAL (`rec["build_entry"]`).
T-06 INV-37 — LOCAL (`feature.json` + `harness.json`). T-07 retention — LOCAL. T-05's *decision* is
LOCAL (step 5 reads `feature.json`), but its *input* is not: step 3's `gh pr view` is a GitHub read
and step 5 denies on its failure. That single branch is the mirror gating, and it contradicts
DEC-138's stated posture that `gh` absent or unauthenticated means the flow succeeds and reports the
sync skipped. D-07's "a gate that cannot verify says so" is a real principle, but `branch-create-gate.sh`
applies it to a *local* fact; here it is applied to a remote one.

## Open questions

- **Q1 — merge-gate fail-closed during a GitHub outage.** Not actually unresolved: `D-07` resolves it to
  DENY. Against the destination it is not under-delivery; it over-serves it and buys the excess with a
  policy the operator fenced off. Blocking, and it is the operator's call, not pm's.
- **Q2 — the era-exempt set (D-08).** Measured at the working tree: 76 feature directories, 65 with a
  `feature.json`, and **17 of those record no milestone at all under `github.sync: true`** (FEAT-01,
  FEAT-02, FEAT-03, FEAT-04, FEAT-05, FEAT-10, FEAT-15, FEAT-17, FEAT-19, FEAT-28, FEAT-36, BUG-1030,
  BUG-1055, BUG-1071, BUG-1080, BUG-1128, BUG-1157). D-08 exempts all 76 by directory name, so those
  17 already-lost mirrors are never reported and no task recovers them: the destination
  "a sync-enabled feature never silently loses its mirror lifecycle" is delivered forward-only.
  **FEAT-55 specifically:** it is in the era set, so it will carry no receipt and INV-37 will never
  name it — but it is no longer unmirrored. Its `feature.json` github block now records milestone 52,
  parent 1289 and twelve task sub-issues 1391–1402, i.e. the operator's late-`open` workaround already
  ran and already created the historical sub-issues the brief was written to avoid. So FEAT-55 stays
  *unreported*, not unmirrored. Closing change, cheap: narrow D-08's generator to exempt only feature
  directories whose `feature.json` records a milestone, and either add one operator-approved
  `recover-terminal` task over the remaining 17 or name them in BRIEF as knowingly unrecovered.
  Non-blocking for the plan's forward guarantee; blocking for the destination sentence as written.

## Not graded here

`check-plan-routes.py` was already measured on this plan (0 violations, exit 0, three DEVIATION
carve-out rows T-04/T-06/T-07) and was not re-run. `plan.yaml` and `BRIEF.md` were not written by this
run.
