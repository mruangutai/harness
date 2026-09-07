# BUG-1290 — ship review, third pass

**You struck B-16 and asked for the committed test first. B-16 is closed. Every gate is green
again, all nine success criteria are met, and the product manager records SC-02's residue as
DISCHARGED. The change is ready for your ship decision.**

Nothing else moved. Production code is **byte-identical** to the tree you were shown yesterday and
to the one you were shown this morning: `git diff --stat 7104aa43 c488218e -- .agents/
.claude/skills/` is empty, my own measurement. The entire third cycle is **one test file,
+57 / −8 lines**.

The new `review_sha` is **`c488218e`**.

**Two things deserve your attention before you decide.** First, the delivered test satisfies your
directive's *purpose* but not its literal wording — a ruling only you can make, and it is cheap to
say "fine". Second, the defender you asked for is itself undefended in one specific direction —
row **B-27**, the *third* instance of the same shape (B-3 → B-16 → B-27). I measured both myself
rather than taking the panel's word.

---

## What you asked for, and what landed

Your directive, verbatim from `notes/answers-2026-09-06-b16.md`: the test "must fail case `5b` when
the issue-map cache is mutated to discard the repository key, so deleting the fixture dependency
cannot silently return the suite to the pre-B-3 blind state."

What landed, in `tests/unit/test-factory-claim.py`:

- Case `5b` was factored onto a **shared** scenario builder (`_run_5b_scenario`) and a **shared**
  predicate (`_5b_property_holds`). Its observable assertion is unchanged.
- A new case **`5g`** reuses both under a mutant `_BlockerCache` **subclass** — it routes every
  repository's issue-map lookup through the first repository seen for a feature id, which is exactly
  what a cache keyed on `feature` alone does — and asserts `5b`'s property is **FALSE** under it.
  The mutant subclasses production rather than copying its body, so it tracks the real seam.

**The sharing is the mechanism.** `5g` cannot be satisfied by a private copy of the scenario, so a
future engineer tidying the fixture moves both cases or neither.

### A ruling for you: purpose delivered, literal wording not

You wrote "must fail case `5b`". As committed, case `5b` **never runs under the mutant** — a new
case `5g` runs the same scenario under it and asserts the failure. The code reviewer and the
validation lead both graded this **faithful delivery of the operative clause** and flagged it as
the one item you might rule differently on (`runs/2026-09-06-11-validator/digest.md`, Q2).

I agree with them, for a reason worth one sentence: this test file is order-dependent and shares a
single fixture tree, so mutating the cache *in place* around `5b` would leak the mutant into cases
`5c`–`5f` that run after it. The observable you asked for — the deletion of the fixture dependency
reddens the suite — is delivered exactly. **If you want the literal form anyway, say so**; it is a
different and riskier change, and it would cost the last rework cycle.

### The measurement that settles it — mine, not any agent's

Four arms, run on an out-of-tree scaffold copy so nothing in the worktree was touched
(`/tmp/b16-orch-control.py`):

| Arm | `5b` | `5g` | Suite |
|---|---|---|---|
| intact | ok | ok | 125/125 |
| **the deletion B-16 named** — harness fixture's `depends_on=["T-99"]` removed | ok | **FAIL** | 1 of 125 FAILING |
| harness fixture's own issue map emptied | **FAIL** | ok | 1 of 125 FAILING |
| the mutant's delegating call replaced by a bare `raise` | ok | ok | 125/125 |

Row 2 is your directive, discharged: the deletion that used to leave 124/124 green now reddens the
suite. Row 3 shows the two cases cover **different** fixture fragments — the pair is load-bearing
together. Row 4 is B-27, below.

Independently reproduced by qa (both fixture arms, after its lead sent it back for having inherited
engineering's measurement) and by the product manager on its own five-arm scaffold.

---

## The gates

| Gate | Result | Evidence |
|---|---|---|
| Engineering | PASS, 0 send-backs; a second persona re-measured all four claims | `runs/2026-09-06-08-eng/digest.md` |
| qa test-matrix (**the one blocking gate**) | **PASS**, `matrix_ok: true`, `must_fix: []` | `runs/2026-09-06-09-validator/digest.md`, `notes/qa-2026-09-06-09-validator.md` |
| Simplify (four angles) | **Empty pass** — nothing cleared the apply bar; production untouched | `runs/2026-09-06-10-eng/digest.md` |
| Validation panel at `c488218e` | **PASS**, `must_fix: []`, **four reviewers ran, none skipped** | `runs/2026-09-06-11-validator/digest.md` |
| Goal-check | **9 of 9 SC MET**; SC-02 re-graded from scratch, residue **discharged** | `runs/2026-09-06-12-product/digest.md`, `notes/research-BUG-1290-goalcheck-b16.md` |

The panel's four reviewers each wrote their own note and all four are on disk (86/136/65/66 lines —
I counted). The ui reviewer's is an **earned decline**: it enumerated all 65 changed lines against
six surface classes for a census of zero, rather than skipping.

Two honesty notes the validation lead volunteered, which I am passing on rather than smoothing:

- qa's `matrix_ok: true` in the panel run is **carried forward**, not re-derived — the matrix passed
  in the separate qa run and that is the one to cite.
- The validation lead **overrode its own pre-stated gating trigger**. My dispatch said that a single
  edit leaving both cases green "would gate"; one exists (B-28), and the lead declined to gate,
  reasoning that the edit is to the assertion itself — which defeats any test ever written — while
  the threat you named is fixture deletion, and both fixture arms are caught. I agree with the
  override. You are seeing it because it was a deliberate deviation from an instruction I gave.

---

## The one honest caveat — row B-27

`5g` asserts a **negation**: "the property does not hold under the mutant". Arm 4 above is what that
costs. If someone later breaks the mutant so it merely *raises*, the run exits non-zero, the
predicate returns False for the wrong reason, and `5g` reports **ok** while proving nothing —
125/125, silent.

**It is not live today** and it is not a gap in what you asked for: the mutant as committed does
delegate, and the failure mode requires a future edit *to the mutant itself*. The panel ranked it
first of four backlog candidates; the product manager raised the same thing independently as a
recommendation it explicitly declined to turn into a gate. I reproduced it before writing this
paragraph.

The remedy is small: assert the mutant's **specific** observable — exit 1 with the harness candidate
blocked on an unresolvable `T-99` — instead of "the property is false".

**My read, and it differs from my read on B-16.** On B-16 I recommended ship-and-backlog and you
overruled me, correctly: the gap was in the thing you had just paid for. B-27 is the same shape one
level up, but the cost/benefit has inverted — the fix is two lines, and the budget is nearly gone
(below). I recommend **ship and take B-27 as backlog**, and I would say the same about a fourth
level: this defence ladder terminates when a human reads the test, not when the ladder is tall
enough.

---

## Budgets — both crossed or crossing, stated plainly

- **Rework cycles: 9 of a hard 10.** This cycle spent one — qa's lead sent qa back for inheriting
  engineering's self-defence measurement instead of making its own. That send-back was correct and
  it caught nothing wrong; it cost a cycle anyway. Engineering, simplify, the panel and the
  goal-check each cost **zero**.
- **Runs: 23 of an informational 20.** Crossed this morning; four more today. My read: today's four
  runs each earned their place — one delivered the fix, one gated it, one looked for simplification
  and honestly found none, one graded the goal. That is the shape a healthy cycle has.

**What this means for a further fix.** A clean directed cycle with no send-backs costs **zero**
cycles, so B-27 is not automatically unaffordable. But one send-back anywhere in it exhausts the
hard budget and the feature goes `BLOCKED` at its ship gate, with everything preserved and nothing
shipped. Raising `max_total_cycles` is your decision and mine to record — it is not something I may
do on my own initiative.

---

## How this briefing was assembled

**No report round was spawned.** I read the run digests off disk and verified the artifacts they
cite. The paths: `runs/2026-09-06-08-eng/digest.md`, `runs/2026-09-06-09-validator/digest.md`,
`runs/2026-09-06-10-eng/digest.md`, `runs/2026-09-06-11-validator/digest.md`,
`runs/2026-09-06-12-product/digest.md`, plus the four reviewer notes,
`notes/qa-2026-09-06-09-validator.md`, `notes/qa-2026-09-06-11-validator.md` and
`notes/research-BUG-1290-goalcheck-b16.md`. The earlier phases are as reported in the second-pass
briefing, `notes/ship-review-2026-09-06-07-ship.md`, which this one supersedes rather than replaces.

The four-arm table, the empty production diff, the removed scratch worktree and every
`check-state.sh` finding below are **my own measurements**. Everything else is attributed.

---

## Proposed backlog

Strike any row by its ID. Unstruck rows become backlog issues on acceptance. **B-3 and B-16 are
gone — you had both fixed.** Rows B-27 onward are new since this morning. Every earlier unstruck row
is carried forward verbatim; anything not listed here dies silently.

### Product residue — this change

| ID | Nature | Finding |
|---|---|---|
| B-1 | chore | **REQ-08 has no committed defender.** Deleting the `factory_config.py` features reader row entirely still yields `CLEAN`; only T-04's probe discriminates, and it lives in `plan.yaml`'s verify block, which CI never re-runs. Promote it into a committed case. |
| B-2 | chore | **Mutation depth is one seam.** `features_root` has a dedicated mutation proof; `segment_of` does not. A `segment_of` mutant *does* redden case `5d`, so the property is caught — only the committed proof is missing. |
| B-4 | chore | **`factory_claim.py:38` `_BIN_DIR` is dead within its module.** Its only reader is unit case `5d`, via `claim._BIN_DIR`. A later cleanup deletes it and reddens `5d` for a reason unrelated to what `5d` tests. Repoint `5d` at `fc._BIN_DIR`. |
| B-5 | chore | **`features_root`'s join is not traversal-safe in isolation.** `"owner/../../etc/passwd"` escapes the harness root; `"owner/"` collapses the segment. **Not attacker-reachable today** — candidate filtering matches exact `fleet.yaml` membership first. Defence in depth only. |
| B-6 | bug | **The `feature`-label-derived join is unvalidated, and `feature` *is* attacker-influenced** (`factory_claim.py:170,190`). **Pre-existing**; belongs to the factory owner, not this diff. |
| B-7 | chore | **`segment_of`'s docstring claims to be "the one home of that rule" and the tree disagrees.** Four identical derivations survive (`post-merge-sweep.sh:163`, `quarantine.py:109`, `worktree_terminal.py:107-129`, `feature_schema.py:231`). Correctly out of scope; nothing indexes them. |
| B-8 | chore | `_BlockerCache._plan` and `.issue_number` build the `(repo, feature)` key inline in two places rather than through one accessor. Declined at the pin boundary. |
| B-9 | chore | `features_root(repo)` is resolved at three call sites in `_BlockerCache`. Measured inert (13.32 µs per call, at most twice per unique pair per poll). Shape note only. |
| B-10 | chore | **REQ-05's wording correction.** The requirement says the segment rule is called by `factory_claim.py`; measured, it reaches it transitively through `features_root`. SC-06 is met on its own words. You declined to rule on it twice; queued here so it survives. |
| B-17 | chore | **`build_features_root()`'s docstring overstates the fixture.** It presents both segments' issue maps as load-bearing; measured, only the harness side discriminates. Unchanged by this cycle — the B-16 diff did not touch it. |
| **B-27** | **bug** | **`5g`'s negation is fail-open in one direction.** A mutant that merely *raises* satisfies `not _5b_property_holds(...)` via the `code != 0` branch, leaving `5b` and `5g` green at 125/125 while nothing is proven (arm 4 above; orchestrator-measured, panel-ranked first, pm-raised independently). **Not live today.** Remedy: assert the mutant's specific observable — exit 1 with the harness candidate blocked on `T-99` — rather than the bare negation. |
| B-28 | enhancement | **`_5b_property_holds` is a single point of failure for both cases.** Weakening it to `payload.get("issue") == 952` alone leaves BOTH `5b` and `5g` green at 125/125 with kaya-ai's half of the proof gone (qa-measured). Requires editing the assertion itself — the validation lead declined to gate on it and I agree. |
| B-29 | enhancement | **A failing `5g` renders a detail tuple shaped exactly like a passing `5b`'s**, because `5g` fails when the mutant did *not* break the property. Every other case in the file trains the reader the opposite way. Legibility only. |
| B-30 | chore | **`_5b_property_holds`'s "never raises" docstring is imprecise** — non-dict JSON reaches `.get()` past the `(JSONDecodeError, TypeError)` guard. Unreachable in practice: the only success-path stdout write is a dict literal (`factory_claim.py:217-221`). |

### The feature's record — pre-existing, not caused by this cycle

| ID | Nature | Finding |
|---|---|---|
| B-23 | bug | **The plan-panel record is incomplete and `check-state.sh` INV-32 is red on it** — readers `scope`, `should-not-exist` and `goalcheck` are all unrecorded. Re-measured today: still red, unchanged. `plan.yaml` is byte-identical to the approval commit, so this predates every cycle since. Only the product manager may write `panel:`. |
| B-24 | chore | **No `notes/handoff-build.md` exists** — the build seam was crossed without one, by a predecessor. Still flagged. Deliberately **not** fabricated after the fact; writing a "working memory" note for a phase nobody ran would falsify the record. |
| B-25 | chore | **Run bookkeeping fails its own contracts, and it recurred today.** All five of this cycle's `state.yaml` files carry the forbidden `run_uid` key; five older run digests still fail the lead digest contract (today's five do **not** — that part improved). Systemic lead behaviour across three cycles. |

### Harness defects observed during these runs

Defects in the factory itself, not in the change. Listed because this repository *is* the harness.

| ID | Nature | Finding |
|---|---|---|
| B-11 | bug | **`check-domain` matches inflight claims by bare agent-type across every linked worktree, with no session scoping.** A concurrent same-role session on an unrelated flow becomes that role's only binding. The single most expensive defect in this feature. No recurrence today. |
| B-12 | bug | **Nothing stops a lead writing its digest into a run directory another run already owns**, and `runs/` is gitignored, so the overwrite is unrecoverable. The guard refuses this for the orchestrator; leads are not covered. |
| B-13 | bug | **Edit-tool/filesystem desync on hardlinked files.** `Edit` reported success and read back new content while `sed`/`md5sum`/`stat` showed unchanged bytes. |
| B-14 | bug | **Lead dispatches return a null yield while complete, correct work sits on disk. Recurred again today** — the panel's security reviewer exited 1 at the return validator *after* its note had landed and its `PASS` was unambiguous (panel digest, Q1). Third consecutive panel affected. Work survives only because artifacts are verified on disk rather than routing on job status. |
| B-15 | bug | **Agents leak edits into the main checkout via relative paths.** *No recurrence in the last two cycles — re-checked today; the working tree stayed confined to `tests/` and the feature directory.* |
| B-18 | chore | **The test matrix keys a required test kind on a directory label, not on the changed surface.** `test_kinds.integration.detect` is `tests/integration/**`. **Re-raised by qa today, unprompted**, as the thing that will mis-scope the next fix-only cycle touching unit-resident fixtures. |
| B-19 | bug | **The write-guard refuses an agent a shell append to its own in-domain path while permitting an editor write to the same path.** Inconsistent enforcement between the two write routes. |
| B-20 | bug | **Reviewer digests are parsed from the assistant-text fence rather than from `yield`'s structured data**, and agents burn turns rediscovering it. |
| B-21 | bug | **Panel reviewers return `files_touched: []` while their notes land at the cited paths.** A consumer trusting `files_touched` would conclude the reviewer produced nothing. |
| B-22 | chore | **State the test matrix's diff object in the protocol.** A fix cycle is not a change type; the matrix grades the feature's change. |
| B-26 | chore | **Agent scratch worktrees are not cleaned up and escape the invariant's naming. Recurred today**: a qa dispatch created `/private/tmp/qa-b16-proof-worktree`, outside the segment layout, which tripped INV-25 *and* an INV-29 the invariant could not compose a removal command for. **I removed it** (clean, no unlanded work). `qa-bug440-c3-probe` and the `qa-c2-*` trees from earlier panels still stand. |
| B-31 | chore | **`test_matrix.bugfix` carries a permanently inert leg.** `match_bug_class` has no bug-class taxonomy anywhere in this repository, so it can never fire. An inert predicate in an auditable matrix reads as coverage that does not exist. Retire the leg or supply the taxonomy. Raised by qa. |

**Unrelated to this feature, seen while measuring:** `check-state.sh` also reports a standing
worktree for `FEAT-55-issue-types-created-work`, whose feature reached a terminal state on the
default branch (INV-29). Not mine to remove — it belongs to that flow — but it is red now.

---

## What the factory still cannot tell you

Unchanged, and worth repeating because it is easy to misread as a failure:

- **After this fix, a live claim run from `main` still reports `no_plan` for FEAT-04.** That feature
  tree exists only in the FEAT-04 worktree. The brief disclosed this before you signed. This change
  fixes the resolver; it does not by itself light up the Kaya lane.
- **The panel verifies the resolver and its tests, not the multi-repository lane end to end.**
  `mruangutai/harness` is deliberately out of the live fleet, so no reviewer could exercise the real
  thing.
- **The coverage is one mutation operator per seam.** `5b` catches a collapsed production key; `5g`
  catches a fixture that stopped discriminating. Other cache-isolation failure shapes — wrong-repo
  population, eviction — remain untested, and `5b` alone still carries the property.

---

## Your decision

**Ship** — nothing is shipped, merged or PR'd yet. On acceptance the main session runs
`gh-sync.py ship` from the **main** checkout with this file as the body (it refuses from inside a
worktree, at exit 1, before any write), then `gh-sync.py backlog` for every unstruck row, then the
merge, then feature-close distillation.

**Fix B-27 first, or demand the literal `5b`-fails form** — say which and I route it. B-27 is a
two-line tightening of `5g`'s assertion; the literal form is a larger, order-dependent change I
recommend against. A clean cycle costs zero rework budget, but tell me whether to raise
`max_total_cycles` in the same breath, because one send-back inside it exhausts the hard 10 and
stops the feature.

**Re-scope or stop** — also available; everything is preserved on the branch.
