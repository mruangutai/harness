# FEAT-10 — the software factory, increment 1 — ship review

**2026-08-09 · branch `feat/FEAT-10-software-factory` · HEAD `b86565b` · not pushed, no PR**

---

## The decision in front of you

**Everything the plan asked for is built, every criterion is met, every gate is green, and the work
is committed. One thing is not proved: the fix for the defect you found by hand has never been run
against a real board.**

That is the whole ship call. Nothing else is outstanding that a signature cannot close.

| | |
|---|---|
| Tasks | **12 of 12 done** — 10 by team, T-01 and T-08 by your own hand under the DEC-174 carve-out |
| Success criteria | **20 met, 0 partial, 0 not met**, on the strict clause-level bar you ruled |
| Test matrix (the only blocking gate) | **PASS** — 22 test files, 0 failures, re-measured by me before the commit |
| Review panel | **PASS** — panel2's single `must_fix` is closed; 11 advisory findings survive, none dispatched |
| Docs / state checkers | **PASS** — both exit 0, zero violations |
| Cycle budget | **12 of 12. Zero headroom.** See the warning below |
| Runs | **31 against a budget of 20** — informational, never a stop |

### What you get if you ship

An approved plan in this repo becomes GitHub issues on one cross-repo Projects v2 board, with the
task DAG drawn as real `blocked_by` edges under one parent container. An agent claims the next
unblocked one atomically — ownership is the return value of a `create_ref`, so exactly one
concurrent creator wins. It gets a prepared checkout of a repo the harness does not live in, on its
own branch. The work comes back as a pull request you merge. The board, not a session, holds state
the whole way.

### What you do not get, and should know before signing

- **Nothing has been proved against the live GitHub API by an automated criterion.** Every green
  assertion in this feature runs against scripted `gh` and `git` stubs. That is disclosed in the
  brief's own `## Verification gaps`, it is a design boundary rather than an oversight, and it is
  why your two hand-run journeys were worth more than the suite.
- **There is no scripted UAT.** You deleted SC-07 under #194's one-in-flight cap. Its job was
  largely done by measurement instead: your first live run went green end to end after the
  project-id fix, and your second reproduced A1.
- **One of the twenty criteria was graded met *conditionally*, and the condition is a row in the
  backlog below.** SC-05 — "opens a pull request and never merges" — was recorded as met on the
  explicit rider that it "flips to not_met if `factory_land.py:77` is judged a defect". The review
  panel declined to judge it one: it graded that line `med` with an empty `must_fix`, because
  merging is your forced next action, so a missing pull request is detected immediately. **B-1 is
  that line.** If you now judge it a defect, SC-05 is the criterion that moves — **and it is the
  only one.** SC-10, SC-11 and SC-14 each carry a recorded reason for being unaffected, and SC-19
  is driven by something else entirely (`runs/goalcheck-product/digest.md`). The blast radius is
  one criterion, not the tally.
- **The concurrency guarantee is inferred, not measured.** That two racing `create_ref` calls
  serialise follows from the endpoint being create-only, measured to refuse an existing ref at 422
  with zero mutation. It has never been raced for real. If the inference is wrong the failure is
  loud — two agents collide at push — not silent, which is why it was accepted.

---

## A1 — the defect you found, and what closing it cost

You reproduced this live with a one-character typo in a station name: the publish exited 0, emitted
a clean payload, wrote nothing to stderr, and left zero claimable tasks.

**The cause.** Step 7 of `factory_decompose` recorded the board item id *before* calling
`project_field_set`, and kept no receipt for the station-set. Any failure between the two left a
task carrying an issue **and** an item — a state the dispositions could not tell apart from a clean
completion. Step 7's own guard then skipped that task on every future run, and the claim poll
(`status:"Ready" is:open`) could never see it.

**Why your typo made it total rather than occasional.** `project_field_set` raises
*deterministically* when the board does not offer the fleet's station option, and `preflight()` runs
`gh auth status` and nothing else — so nothing validated the station names first. Run 1 orphaned
task 1, run 2 orphaned task 2, and by run N+1 every task had an issue and an item, the loop skipped
all of them, nothing raised, and publish reported complete success over a board on which no task was
claimable.

**The fix, committed as `b86565b`.** The item id is recorded only after `project_field_set` returns.

**Two things about the fix are worth your attention, because both are places it could have gone
wrong quietly.**

1. Moving the record promotes a rare crash window to the ordinary recovery path, so step 7 now
   re-calls `project_item_add` on an issue already on the board. Whether that is idempotent is
   unverified and the stub cannot settle it — the exact shape of the project-id bug that shipped
   green. It was closed by *removing* the dependency rather than assuming it: a board lookup on the
   partial path only.
2. That lookup's first version compared `content.repository` bare, while the consumer it claimed to
   copy documents that field can be **absent** and carries a URL fallback. Every lookup would have
   been a false miss on a real board, the protection dead, and the suite green because the stub
   supplies the field. The engineering lead rejected it and it was fixed. That rejection is one of
   the two cycles this segment charged.

**Evidence.** Red was proved by injecting the pre-fix module and re-running the segment's final
tests: 17 of 172 checks fail, including the three that reproduce your live journey. Green was
re-measured at the settled tree immediately before the commit: 22 test files, 0 failures.

**The gap:** all of that is against the stub. Your typo journey — the only thing that ever
reproduced A1 outside a test — has not been re-run.

### The one open question

**Should the factory be run once more against a real throwaway repo and board before this ships?**

You held this open at the last round rather than acting on it, because it needs a throwaway repo and
a fresh board that only you can authorize, and the last one required a `delete_repo` scope refresh
to clean up. It is required by no signed criterion. My read: it is the single highest-value hour
available on this feature, because it is the only thing that would close the one loop the automated
set cannot reach — and because A1 is proof that the stub-only bar has already let a total failure
through once.

---

## The cycle budget, and why it matters for what you decide next

**12 of 12, with zero headroom.** You raised the ceiling from 10 to 12 at the last round and that
raise is now recorded in `feature.yaml` as DEC-157 requires.

The practical consequence: **if you order any rework from here — a fix, a re-review, a re-plan — the
next orchestrator hits a hard bound and returns BLOCKED rather than doing the work.** It is not a
soft signal. Ordering rework means raising the ceiling again in the same breath.

The 31 runs against a 20 budget is a different thing and is informational by design. A long feature
is fine when each run earns its place; the last four each found or closed a defect that would
otherwise have shipped, A1 among them. It is not an apology.

---

## What each squad delivered

Summaries below are drawn from the run digests, cited by path.

**Product — planning was the expensive part, and it was worth it.** Eleven product runs took the
plan from 11 tasks and 11 criteria to 12 tasks and 20, and the biggest single change was replacing
the claim mechanism outright rather than patching it: `gh issue edit --add-assignee` is additive, so
two racing agents both wrote, both read `[A, B]`, both concluded they lost, and left an issue owned
by nobody with no release path. Ownership became a `create_ref`
(`runs/revise-product/digest.md`). Later passes converted a criteria set that was 13 negatives out
of 14 into one that proves the factory *works* (`runs/revise2-product/digest.md`,
`runs/sc-delta-validator/digest.md`), and rewrote all 8 requirements and 20 criteria into plain
English with exactly one meaning change, disclosed to you at signature
(`runs/prose-delta-validator/digest.md`).

**Engineering — three build waves, eleven tasks, zero send-backs.** `runs/w1-eng/digest.md`,
`runs/w2-eng/digest.md` and `runs/w3-eng/digest.md` landed the CLI contract, the single `gh` seam,
the fleet loader, publish, claim, workspace, land and the fork-level integration suite, each
test-first, each with its own verify green. Two members found real defects in their own work before
returning and neither cost a cycle. The architecture reviews before the build
(`runs/arch-eng/digest.md`, `runs/edges-delta-eng/digest.md`, `runs/bound-delta-eng/digest.md`)
caught the cwd-relative fleet path, the missing process-exit coverage, two unprotected ledger
windows, and a signal collapse that would have voided your conditional acceptance of a residual.

**Validation — the panels earned their keep twice, and the second time is why this is safe.** The
first panel reviewed 15 never-reviewed modules and topped out at `med`, with security at `info`
across twelve audited mechanisms (`runs/panel-validator/digest.md`). The second panel was convened
specifically on the two files nobody had read, and found A1 — the only high-severity defect in the
feature (`runs/panel2-validator/digest.md`). The test-matrix gate returned BLOCKED once on a config
defect rather than a code defect, and PASS after you fixed the config
(`runs/qa-validator/digest.md`, `runs/qa2-validator/digest.md`).

**Goal-check — the tally moved because you set a harder bar, not because the work changed.** The
first pass graded 16 met / 3 partial / 1 not met against a clause-level bar the brief never stated
(`runs/goalcheck-product/digest.md`). You ruled that bar. The three partials were then closed with
assertions that were each proved to fail against a deliberately broken production file, not merely
read (`runs/assert-eng/digest.md`, `runs/assert2-eng/digest.md`,
`runs/goalcheck2-product/digest.md`), and SC-06 flipped once T-08 landed
(`runs/sc06-product/digest.md`). **20 met, 0 partial, 0 not met.**

### How this briefing was assembled — the disclosure

**No report round was spawned.** No lead was asked to re-narrate work it already wrote down. Instead
**all 31 run digests were read off disk**, including the plan and build phases this segment did not
run: every path under `.harness/features/FEAT-10-software-factory/runs/*/digest.md`, one per entry
in `feature.yaml`'s `runs:` list. Three lead spawns to summarise files that are already on disk is
spend with nothing to surface it. The cost of the disclosure is that you can tell a complete
briefing from one missing a phase; without it you could not.

---

## Escalations, resolved

| Raised | Resolution |
|---|---|
| `blocked_by` edges encoded but not enforced — the board would show a block marker the factory ignored | You ruled enforce. `D-01`'s read-back bound was widened in place naming DEC-138 as the baseline, and SC-22 falsifies a tool that ignores blockers. The rendered edge is still never read; the DAG authority is the signed plan (`runs/amend-product/digest.md`) |
| The test matrix could not return a verdict — `functional` had a null command against a diff that bound it | You settled it as DEC-187: `functional` is excluded by signed decision rather than satisfied. The gate then returned PASS (`runs/qa2-validator/digest.md`) |
| A criteria set that proved only refusals | You ordered the outcome-first rework. 20 criteria, 18 automated, all traced to a requirement |
| A reviewer edited an enforcement-layer file in a throwaway worktree to mutation-test it, disclosed it unprompted, restored it and verified clean | Accepted, nothing filed. Nothing reached the tree |
| Whether `_validate_stations` — behaviour beyond the signed plan, declared not slipped in — needed a formal amendment | The run digest stands as the record. `plan.yaml` not amended |

---

## Proposed backlog

Everything below survived collation and gates nothing. Strike any row by its id; **anything not
listed here dies silently when you accept**, so the list is deliberately complete rather than short.

| ID | Nature | What it is |
|---|---|---|
| B-1 | bug | `factory_land.py:77` fails open on `gh pr create`. Any error whose text contains "already exists" plus any URL anywhere is adopted as the pull request — no 422 co-condition, no check the URL is PR-shaped. Exit 0, the board advances to Review, and the payload carries a wrong url. **Verified still present by me today.** Fix is a `create_pull_request` helper behind the `gh` seam, which also closes B-2. **This is the line SC-05's conditional grade hangs on** — see the caveat above |
| B-2 | chore | Three different "already exists" predicates in three places with three strictnesses — inside the seam for `create_ref`, in the caller for `blocked_by`, and loosest of all in `factory_land`. Two of six tools now know that `gh` prints an HTTP error body, which is knowledge the seam exists to hold |
| B-3 | bug | An absent or malformed `fleet.yaml` or `plan.yaml` surfaces as `unexpected failure: YamlParseError: …` — an exception class name in an operator-facing line the CLI contract forbids. **Verified still present by me today**: no tool's `expected` tuple carries it. Systemic across all five tools; fix is two raw call sites, not five tuples |
| B-4 | bug | The `--issue` re-run does not "complete idempotently" as the signed T-05 text says: the self-ownership branch re-emits the payload and exits 0 without retrying the station set. The code and its own test agree with each other and both disagree with the plan. Decide which is wrong, then fix that one. Self-heals downstream, which is why it is not higher |
| B-5 | bug | Repeat publish under a different `--repo` can confuse issue numbers across repositories |
| B-6 | enhancement | `factory_claim` has no `harness`-label provenance check. Safe **only** because Projects v2 auto-add is not configured on the board — a board setting, not a code property. If auto-add is ever enabled the factory claims and opens PRs against arbitrary externally-authored issues. Worth recording where the trigger will be found |
| B-7 | chore | Publish accepts a feature directory at any path while claim hardcodes `.harness/features/` — a plan can be published that claim cannot resolve. A contract question between the two tools, not a one-line fix |
| B-8 | chore | The DEC-187 model was fixed in this project's config and **not in the templates**, so every new `/harness-init` seeds the pre-DEC-187 behaviour and ships no `status` field. Six files disagree in total, two of them templates. This is the edit still owed after your deliberate sequencing |
| B-9 | bug | Issue #199, **seventh recurrence**: the receipt path the handoff skill prescribes is denied by the domain guard to most personas. Every dispatch that follows the skill hits it. Either grant the path to every member or stop the skill prescribing it |
| B-10 | chore | The dead assertion at `test-factory-integration.py:691-692` — the fixture pre-creates the directory it checks. It costs nothing today because a sibling assertion binds the same clause and does redden; it costs later, because it reads as coverage |
| B-11 | chore | `test-factory-decompose.py`'s `_strip_factory_block` round-trip test passes vacuously and does not exercise the risky ordering |
| B-12 | chore | Two SC-18 escapes, neither demoting the criterion: a module-scope alias whose name does not contain "fleet" is invisible to the scan, and the scan covers `factory_*.py` rather than all of `bin/` |
| B-13 | chore | T-08's change type requires `unit` while INV-24's only real coverage is `integration`; the matrix passes only because sibling tasks pull both kinds in. Separately, 4 of 12 tasks carry no matrix floor at all, including the one contributing the only real-process test |
| B-14 | chore | `factory_claim` computes its features root at module import, against the no-side-effects-on-import intent. The value is correct and stdout is untouched; the deviation is timing |
| B-15 | chore | `factory_config --show` with no flag prints empty stdout and exits 0, which fails `json.loads('')`. Either a stated exemption or a defect; currently neither |
| B-16 | chore | The label "edge (i)" names two different scenarios in one document, and the task text instructs a builder to emit the first one's stderr reason for the second one's cause. Their repairs differ — amend the plan versus fix one issue title. One-word fix |
| B-17 | chore | SC-10 declares `evidence: unit` while the plan's own reasoning argues the case that proves it lives in the integration file. The case is built regardless; the field is editorial |
| B-18 | enhancement | **D-12, the two-ledger problem**: `gh-sync.py` and `factory_decompose` are two independent writers of issues for the same tasks into the same repo, keeping two maps in the same file. Named and deliberately not fixed; a later increment owns it |
| B-19 | enhancement | Nothing validates `depends_on` referential integrity, so a dangling entry in a signed plan reaches publish unvalidated and stderr is the only place the DAG gap is named |
| B-20 | enhancement | The board grows monotonically — nothing archives or removes items — and reaping stays yours. Bounded today by a server-side ready-column query, measured at 1 of 150 |
| B-21 | chore | A published issue's identity comes from the T-NN in its **title**, a hand-editable remote string. An issue whose feature label resolves but whose title matches no plan task is now blocked, but no criterion asserts it |
| B-22 | enhancement | Should any segment run against a working checkout another process can move under it? Demonstrated twice on this feature — a moving HEAD during the second panel, and an enforcement file changing mid-run during the A1 fix. A worktree at the pin is free both times |

**Four** panel2 findings are deliberately **not** listed, because all four are already closed in the
tree — I re-read each one at HEAD rather than inferring it from the commit message. The INV-24
null-repo fail-open (`bf8f191`'s own comment cites "panel2 C1" by name), the within-feature
parent/issue collision, the four-of-eight test binding (every no-hit case now carries a positive
control, so absence is only believed when the checker demonstrably ran), and the missing
remediation instructions (all nine INV-24 messages now end with one).

---

## Housekeeping that needs a decision, not a fix

- **`.harness/logs/2026-08-09.md` is dirty and I left it that way deliberately.** Its twelve added
  lines are your own record — the `bf8f191` measurements, and issues #203 and #204 — and they carry
  claims I cannot verify. Signing unverifiable prose into my commit was the wrong trade. It is
  yours to commit.
- **Two handoff notes were missing and are now written — the gap was real.** Advancing the phase to
  `ship` made the state checker fire two violations: the build and validate seams were each crossed
  with no handoff note, so every successor orchestrator lost its predecessor's working memory and
  reconstructed from disk. I wrote both, each labelled RECONSTRUCTED AT FEATURE CLOSE in its own
  opening lines so the loss is preserved in the record rather than erased by the paperwork that
  clears the gate. Reverting the phase would have hidden it; leaving the gate red would have handed
  you a paperwork failure on ship day with nothing to show for it.
- **Do not delete `wip-omp-and-feat10-mixed` yet.** The old review pin `8bbb246` survives nowhere
  else, and every panel2 line citation points at it.
- **`plan.yaml:1435` still records T-08 as pending.** It landed by your hand. Stale, and the only
  plan-level correction this feature still owes — pm's to make, not mine.
- **Distillation was deliberately not run**, and you can overrule. Feature-close distillation
  belongs after ship; distilling a run you may reopen writes durable Expertise while the run is
  still hot, which is the failure that rule exists to prevent. It costs three dispatches whenever
  you want it. Ship-refresh was skipped on a measurement instead of a judgement: no codebase map
  exists, so there is nothing for it to refresh.
- **Nothing is pushed and no PR is open.** `main` is 10 commits ahead of `origin/main`. Both the
  push and the merge are yours.
