# Ship review — BUG-1309-mirror-build-entry — 2026-09-09

## The decision in one paragraph

**This is ready to ship, and the only thing missing is your instruction to do it.** All eleven
success criteria are met — including SC-10, which you closed yourself today by judging the revised
merge-gate refusal message clear and actionable. The blocking test-matrix gate is green, the c19
review panel returned PASS with an empty `must_fix`, and no finding at any severity gates. Nothing
is left for a squad to build, nothing is left for a squad to check, and no cycle is being requested
— the budget is spent at 17 of 17 and this briefing needs none of it. What remains is one word from
you, plus two optional side decisions you can settle in the same sitting: which backlog rows to
keep, and whether you want to confirm the UAT step coverage below.

## What you need to decide — three items, one sitting

| # | Item | What I need |
|---|---|---|
| **1** | **Ship, or not.** The feature is at station `review`, `review_sha` pinned to `4857818b`, branch `feat/BUG-1309-mirror-build-entry` unmerged | **"ship"** — or "fix X", "re-scope", "stop". Nothing happens without it |
| **2** | **The backlog table below (B-1 … B-29).** Strike any row by ID. Unstruck rows become GitHub backlog issues when you accept the ship; **anything not listed there dies silently, so I listed everything I could source** | Struck IDs, or "keep all" |
| **3** | **Optional — UAT step coverage.** Your result reached me as an overall "pass" plus your judgement of the refusal wording, without a per-step readout. SC-10 is recorded MET on that, and I did not re-grade you | Either nothing, or "Steps 3b/5/6/7 also passed" for the record. **This does not gate the ship** |

## SC-10 — what was recorded, and at what fidelity

Your result is transcribed at `notes/uat-BUG-1309-mirror-build-entry.md:360-403` — appended only,
45 added lines and 0 deletions, so the script you ran is byte-unchanged. It records that the relay
reached the harness inline through the main session on 2026-09-09, that you judged the message
**clear and actionable**, and that you reported **"pass"** — attributed to that channel, never
restated as something an agent measured. The message you were judging:

```
merge-gate: FEAT-9001-uat-scratch needs its GitHub mirror recovery completed before this merge can continue. Run: python3 .claude/skills/harness/bin/gh-sync.py open /private/tmp/bug1309-uat/.harness/harness/features/FEAT-9001-uat-scratch
```

**The one limit, stated rather than smoothed over.** The script's own verdict rule asks for Steps 3,
3b, 5, 6 and 7 to each pass; the relay carried an overall pass and your explicit judgement of the
Step 3 wording. That licenses recording SC-10 as met — your judgement *is* the criterion's declared
method, and no agent may substitute for it. It does not license citing that section as per-step
evidence, and nobody resolved the difference by guessing in either direction. Item 3 above is how
you close it if you want it closed.

## Where the feature stands

- **Goal-check: 11 of 11 criteria met** — `notes/research-BUG-1309-c19-uat-sc10.md`, one row per
  criterion with a cited evidence path. Two rows deserve their exact wording:
  - **SC-04 is met BY YOUR RULING** accepting both evidence gaps on inspected-correct source
    (`notes/research-BUG-1309-c18-sc04-ruling.md`) — **not** by new automated evidence. The
    behaviour is correct at `merge-gate.py:172` and `:174`; what is missing is automated coverage of
    the ambiguity deny's wording and a fixture ordering that would let one case redden. Rows B-13
    and B-14 are those two remedies, still unscheduled.
  - **SC-09 is `verify: inspection`** by the brief's own declaration, checked at the pin.
- **Test-matrix gate (the project's only blocking gate): PASS.** Integration suite at the pin
  rc=0, 36 ok, 0 FAIL, matching the c18 baseline — `notes/qa-c19-copy.md`. T-05's own `verify`
  printed `VERIFY-PASS` with `code_grade` 4 against a floor of ≥4.
- **Review panel (c19): PASS**, `must_fix: []`, `severity_max: med`, four readers ran and none was
  skipped or declined — `runs/c19copy-validator/digest.md`. Its one med against this feature's own
  code is row B-16.
- **Approval: both signatures are in place.** `BRIEF.md ## Approval` approved, re-signed 2026-09-08
  over SC-11. `plan.yaml approval` approved, re-signed 2026-09-08 (commit `de04d841`, after the
  D-13…D-15 amendments). D-19 was appended additively afterwards under ruling R-7 §4, which owes no
  re-signature, and pm re-checked the criterion texts rather than assuming it.
- **Cycles: 17 of 17 — exhausted.** Today's two runs sent nothing back, so neither cost a cycle. Any
  further fix work needs you to raise the cap, which is why every residual below is a backlog row
  rather than a fix cycle.
- **Runs: 55 against a 20-run budget (informational, INV-22).** My read: the count is honest but it
  is no longer cheap. This feature absorbed eleven adversarial plan/review cycles, a silent-allow
  class that took three cycles to close completely, one withdrawn acceptance that had to be redone
  on a correctly-stated question, and a copy rewrite you asked for at the end. Each closed something
  real. But the last four cycles closed evidence and wording rather than behaviour, which is what
  convergence looks like from the inside — I would not spend a 56th run here.

## What changed since the 2026-09-08 briefing

That briefing put four items in front of you. All four are closed:

1. **F-01 and F-02** (nondeterministic branch attribution; the parser walking past `git -C <dir>
   merge`) — you ruled FIX as **R-1/R-2**, and both landed main-session-direct. The parser rewrite
   was then measured by three independent method families finding **zero silent allows** across
   39 + 27 + man-page enumeration (`runs/c17-validator/digest.md`), after c14 and c15 caught two
   further escape forms the first attempt missed (`runs/2026-09-08-c14-validator/digest.md`,
   `runs/2026-09-08-c15-validator/digest.md`).
2. **F-03** (the notice naming `open` where the classifier says `recover-terminal`) — ruled FIX as
   **R-3**; the notice now derives its command from `feature_schema.recovery_command_for`, recorded
   as D-15.
3. **The re-signature** — done, twice: the amended BRIEF on 2026-09-08, then the plan.
4. **SC-10** — done today, by you.

Two things you added along the way: **SC-11** (merge `--abort`/`--continue`/`--quit` must stay
allowed on a branch that owes a receipt — ruling R-6, D-18), and the **c19 refusal copy** you chose
verbatim, which is the sentence you judged today (ruling R-7).

One item on the old backlog is **resolved incidentally and I struck it myself**: `merge-gate.py`'s
module-scope `feature_schema` import — the ~50-60 ms on every Bash call — is now a deferred import
inside the deny path (measured at the pin, `merge-gate.py:164`).

## Residual risks you are accepting if you ship

None of these gates. All are recorded, none is waived.

1. **SC-04's evidence is a ruling, not automation** — see above. Rows B-13, B-14.
2. **"Names the feature" is proven but undefended.** The message contains the feature name twice at
   the pin, but no test can *fail* if `{feat}` is deleted, because the rendered path also carries the
   id. Behaviour correct, evidence incidental. Row B-15.
3. **Test-first order for the c19 copy commit cannot be established from the git record.** Source
   and both test hunks are in one commit with no intermediate red. qa reported this as unknowable
   rather than assuming either way, and I am not restating your pre-edit red observation as
   verified. Rows B-29 (policy) — the honest record is in STATE.md Q12.
4. **`code_grade` is exactly 4 against a floor of ≥4** — zero margin, so any complexity added to
   `git_merge` reddens T-05's verify.
5. **The `unit` matrix cell for the copy delta is satisfied procedurally**, by a test file the copy
   cannot affect; `integration` carries it substantively and was mutation-proven. Row B-24.
6. **Two standing gaps you already signed** (`BRIEF.md ## Verification gaps`): a live `gh pr merge`
   against real GitHub is never exercised, and **17 sync-enabled legacy feature directories remain
   knowingly unrecovered** — row B-3 is the only place that work is tracked.

## Proposed backlog — strike any row by ID; anything not listed dies silently

Rows carried from the 2026-09-08 briefing keep their content but are renumbered here, because that
table was never disposed of.

| ID | Item | Nature |
|---|---|---|
| B-1 | Gate-dispatcher consolidation plus the `HOOK_SPECS` gaps (you already accepted the fifth standalone gate) | enhancement |
| B-2 | `gh-sync.py`'s no-op remedy string (anchor `:247` from 2026-09-08 has since shifted; needs re-locating) | bug |
| B-3 | The 17 unrecovered sync-enabled legacy feature directories | chore |
| B-4 | The nonexistent `gen-decisions-index --check` clause in four features' plans | chore |
| B-5 | `gh-sync.py`'s unguarded `int()` (anchor `:1234` from 2026-09-08; may have shifted) | bug |
| B-6 | `merge-gate.py:163` interpolates the literal `this feature` when the git binary is unresolvable — fails closed, still present at the pin (I re-checked) | bug |
| B-7 | The DEC-138 stderr line says "owes no build-entry receipt" where the record is HELD — diagnostics only | bug |
| B-8 | Three different spellings of "Build entry receipt" across the messages | chore |
| B-9 | `test-check-state.py`'s "INV-37 message discriminator" case is vacuously green — asserts a token absent from an empty line | chore |
| B-10 | `test-merge-gate.py`'s "gh outage with no matching feature allows" does not discriminate a cycle-5 sentinel reintroduction | chore |
| B-11 | Handoff `Authority:` pointers (`plan-task:`, `brief-sc:`) cannot resolve for a feature living only in a worktree | bug |
| B-12 | The reviewer dispatch template does not state the canonical novelty range — how six cycles read "pre-existing" as "pre-existing since two commits ago" | enhancement |
| B-13 | SC-04 clause (f): add a `"branch" in reason` conjunct at `test-merge-gate.py:159-163` | chore |
| B-14 | SC-04 Gap B: reorder the fixture so the era-exempt claimant sorts into `owners[0]`, making the ordering case discriminating | chore |
| B-15 | Defend `{feat}`: assert on the reason region *before* `Run:` at `test-merge-gate.py:68-69` and `:102` | chore |
| B-16 | `merge-gate.py:188` (the repo-unpinned deny) still opens with `{feat} records github.build_entry={value}` — the exact jargon you rejected for `:192` — and splices a bare `(D-09)` into operator prose. **The panel's one med** | bug |
| B-17 | `merge-gate.py:180` leaks the raw constant name `feature_schema.BUILD_ENTRY_ERA_EXEMPT` into operator-facing stderr | bug |
| B-18 | `merge_target` matches `--abort`/`--continue`/`--quit` by exact token equality, so `git merge --abo` is DENIED where git would accept it. Over-deny, never a bypass | bug |
| B-19 | T-05's grade assertion takes `min()` over four helpers and never names `option_end`, `first_subcommand` or `merge_target` (satisfied in fact, 5/5/4) | chore |
| B-20 | T-05's enumerated case-name contract lists 21 names while its `verify` gates 26 | chore |
| B-21 | The UAT script has no step exercising the duplicate-claimant ambiguity refusal at all | chore |
| B-22 | Fixture calibration: SC-04 clause (k) asserts the stderr content but not that the note is one line; the `chmod 0` fixture in clause (i) is non-claiming | chore |
| B-23 | Shell-variable indirection (`B=feature/x; git merge $B`) and a fourth-level `bash -c` nest past the depth cap — explicitly NOT ruled in under R-2 | enhancement |
| B-24 | The `unit` matrix cell for copy-only deltas is satisfied by a file that cannot observe the copy | chore |
| B-25 | `notes/rulings-2026-09-08-c19-copy.md` §5.3 cites the `recover-terminal` expectation as "Step 6 (`:300`)"; it is Step 7 at `:303` | chore |
| B-26 | Harness defect, 6th sighting: an agent returned a complete fenced digest while the host recorded `failed (exit 1) — subagent called yield with null data` | bug |
| B-27 | Harness defect: `bash-write-guard.sh` blocks `cp` and shell redirection for a read-only role but not `python3 -c "open(path,'w')"` | bug |
| B-28 | Harness defect: `validate-digest.py` appears to have accepted a raw JSON object with no ```yaml fence — possible fail-open in fence detection | bug |
| B-29 | Policy: should a copy edit plus its dependent test re-anchor be split into a failing-test commit then a fix commit, for test-first auditability? | chore |

## What happens when you say ship

For your visibility, not as a request: the main session runs `gh-sync.py ship` from the main
checkout with this briefing as the issue body, the unstruck rows above become backlog issues, the PR
merges under your hand, the `post-merge` hook removes the worktree, and only then does
feature-close distillation run. I did not run any of it, and I hold no authority to.

## How this briefing was assembled — disclosure

**No report round was spawned.** I read the digests and notes on disk, as the playbook requires.
The load-bearing sources: `runs/c19copy-validator/digest.md` and `runs/2026-09-09-01-product/digest.md`
(the c19 validate round), `runs/c19uat-product/digest.md` with
`notes/research-BUG-1309-c19-uat-sc10.md` and `notes/uat-BUG-1309-mirror-build-entry.md` (today's
SC-10 recording), `notes/research-BUG-1309-c18-sc04-ruling.md` and
`notes/research-BUG-1309-goalcheck-c18.md` (SC-04 and SC-11),
`notes/rulings-2026-09-08-panel-c7.md` and `notes/rulings-2026-09-08-c19-copy.md` (your rulings),
`runs/2026-09-08-panelc7-validator/digest.md`, `runs/2026-09-08-c14-validator/digest.md`,
`runs/2026-09-08-c15-validator/digest.md` and `runs/c17-validator/digest.md` (the silent-allow class,
closed), `notes/qa-c19-copy.md` (the gate), `notes/ship-review-2026-09-08-resume.md` (the prior
briefing, whose backlog this table subsumes), and the `headline:` line of **all 55 run digests** on
disk for plan- and build-phase coverage. I did not read the plan- and build-phase digests in full;
their headlines plus `STATE.md`, `feature.json` and `notes/handoff-validate.md` carried what this
decision needs.

**What I re-verified myself rather than relaying:** the append-only shape of the UAT edit
(`git diff --numstat` — 45/0) and the appended section's fidelity to the relay; that both approval
signatures read `approved` and that the plan's was re-signed *after* the D-13…D-15 amendments
(commit `de04d841`); that D-13…D-19 are all present in `plan.yaml`; that `merge-gate.py`'s
`this feature` fallback survives at the pin (row B-6) while the module-scope import that was row
B-6 on 2026-09-08 does not — that one I struck on my own measurement.
