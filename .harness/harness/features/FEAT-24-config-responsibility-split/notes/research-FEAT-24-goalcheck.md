# Goal-check — FEAT-24 — all 13 SC at their declared verify method

**Measured at `fd8728c`, which is HEAD.** The dispatch's pin `91884f9` is its parent;
`git diff --name-status 91884f9 fd8728c` = `feature.json` alone, no source. Every source verdict
below therefore holds at both. Suite at HEAD: `run-unit-tests.sh --kind all` rc=0, **0 FAIL**,
1582 ok/PASS. `check-state.sh` rc=1, 4 VIOLATION lines, **0 naming FEAT-24** (the four are the
paused FEAT-25/26/27 dirs).

## BLUF

**7 met, 5 partial, 1 split.** Nothing is `cannot-be-met-as-written`. The two records that
conflicted (SC-02) are settled by my own mutants: **the panel is right, qa's 4/5 is stale.**

**SC-05 is not self-contradictory.** The two-clause/two-site reading holds — clause 1 is
`load_board`, clause 2 is `board_for` — and the panel reached "no reading holds" only by forcing
both onto one function. What is left is a scope question on one sub-clause, and under the reading
the BRIEF's own SC-04, REQ-03 and REQ-09 already use, **SC-05 is met 4/4**. Scored partial only
because ruling on the scope is the operator's, not mine.

The recurring shape across all five partials is the same one this feature exists to remove: **an
assertion that exists, is named, passes — and cannot fail.** I mutation-proved four such assertions
dead (SC-01 clause A, SC-07 ×2, SC-10 factory_land) and found four more SC-06 ok-lines pinned by no
`verify:` block, twice what eng-10's Q2 reported.

All mutations ran in a disposable worktree (`.claude/worktrees/pm-feat24-gc`), each diffed before
the run and `git status --porcelain` clean after. One probe harness of mine ran `python3 x` instead
of the test file and reported a false "0 FAILs"; caught and re-run. Every number below is from the
corrected runs.

## Verdicts I am superseding or overturning

| SC | Whose | At pin | Their verdict | Mine | Why |
|---|---|---|---|---|---|
| SC-02 | qa | `0fa6315` | unmet 4/5 | **met 5/5** | **Overturned.** Stale: commit `3396b5e` moved the decompose fixture from `"Ready"` to `"Promoted"`. I re-ran their exact mutant at HEAD and it reddens 3 cases |
| SC-02 | panel code-reviewer | `14994b3` | met 5/5 | **met 5/5** | **Adopted**, independently re-measured — and extended from their 1 mutant to all 5 keys |
| SC-05 | panel lead (Q3) | `14994b3` | unmet, "no reading holds" | **partial — 4/4 narrow, 3/4 broad** | **Overturned.** They forced both clauses onto one function. The remaining sub-clause turns on scope, which SC-04/REQ-03/REQ-09 already settle in favour of "true". See below |
| SC-06 | panel + eng-10 Q1 | `14994b3`/`efaddcf` | unmet | **partial 6/7** | **Refined.** Behaviour is met on all three modes; the residue is evidence durability, not behaviour |
| SC-09 | panel code-reviewer | `14994b3` | met | **met** | **Adopted and re-measured** — I re-ran the live `gh api` today |
| SC-12 | qa | `0fa6315` | met | **met** | **Adopted**, re-measured (T-05 GREEN at HEAD, my run) |
| SC-13 | panel lead | `14994b3` | unmet (whole) | **cl.1 met / cl.2 not_met** | **Split**, as instructed. Their 28/28 for clause 1 adopted and re-counted |
| SC-01, SC-07, SC-08, SC-10 | — | — | never re-enumerated | measured here | Treated as unmeasured, per dispatch |

## SC-02 — met, 5/5, mutation-proven by me at HEAD

One mutant per key, each reverted to the literal it would have been:

| key | site | reverted to | reddens |
|---|---|---|---|
| ready | `factory_decompose.py:399` | `"Ready"` | 3 cases, incl. `(2) both stations set to the fleet's ready option` |
| building | `gh_board.py:112` | `"Building"` | `derive_station returns the declared building station` |
| review | `gh_board.py:114` | `"Review"` | `derive_station returns the declared review station` |
| done | `check-state.sh:1184` | `"Done"` | `INV-26 expects the declared station for status: done` |
| backlog | `check-state.sh:1185` | `"Backlog"` | `INV-26 expects the declared station for status: backlog` |

Discriminating because the fixtures differ from the literals: `Promoted`, `Col-B`, `Col-R`,
`Shipped`, `Icebox`.

**Out of SC-02's scope but worth the operator's eye:** SC-02 asks one assertion per *key*, and gets
it. Per *site* the denominator is **8 revertable production lookups**, of which **6 discriminate**:
the five above plus `factory_claim.py:266` (ready). The two that survive their mutants are
`factory_land.py:95` (review) and `factory_claim.py:383` (building). (`factory_claim.py:232`
is excluded — `board["stations"][key]` is key-agnostic and has no per-key branch to revert, the same
reason qa correctly rejected `factory_config.board_station` as SC-02 evidence.) See SC-07 and SC-10.

## SC-05 — the discriminating question, answered: the two-site reading holds

**SC-05 is not a self-contradictory criterion.** Clause 2 says "a fleet member's config" → that is
`board_for`. Clause 1 names no scope and REQ-09 is about a project's own board → `load_board`.
"Both asserted separately" argues for two sites. The panel's Q3 reached "no reading holds" by
forcing both clauses onto one function; that is the error, and it changes the operator's options.

| sub-clause | site | verdict | evidence |
|---|---|---|---|
| explicit `null` is accepted | `load_board` | **met** | `load_board: an explicit null board is accepted and returns None` (T-04 GREEN, my run); live probe returns `None` |
| writes no station | `board-station.py` | **met** | `an explicitly null board still exits 0 having written nothing` (T-04 GREEN) |
| **and is the only non-error path** | `load_board` | **depends on scope — see below** | live probe, below |
| board key absent from a fleet member's config is an error | `board_for` | **met** | `factory_config.py:315-319`; `board_for raises when the product config declares no board` passes |

**Live probe of `load_board`, seven shapes** (`gh_board.load_board` against a built fixture):

| shape | result |
|---|---|
| A file absent (OSError) | **returns None** |
| B unparseable JSON | **returns None** |
| C cfg not a dict | **returns None** |
| D `github` absent | **returns None** |
| E `github` present, not a dict | **returns None** |
| F `github` dict, no `board` key | **RAISES FleetError** |
| G `board` explicitly null | **returns None** |

This settles the dispatch's correction 1 in the dispatch's favour: **F raises** — the panel's
adequacy note is right and the operator's contrary measurement is wrong. It also refines the
dispatch's count: the silent set is four *branches* but **six shapes**, because D and E share
`gh_board.py:72-73`.

### 1c turns on a scope question nobody has asked, and the answer is not mine to pick

**Broad reading** — "non-error path" means any input to `load_board`. Then six shapes are non-error,
1c is **false in the tree**, and closing it is Options A/B below.

**Narrow reading** — "non-error path" ranges over *board declarations*, the sentence's own subject.
Then only F and G are in the domain: F raises, G returns None, and **1c is true**. A/B/C/D/E are not
board declarations at all — they are absent or malformed *config files*.

**Three pieces of the BRIEF's own structure favour the narrow reading, and I found no evidence for
the broad one beyond the bare wording:**

1. **SC-04 fixes `load_board`'s domain to board shapes.** Its eight shapes are not-a-mapping,
   missing `owner`, missing/non-integer `number`, missing `station_field`, missing `stations`, wrong
   `stations` key set, empty station value, no `board` key. **None of A–E appears.** A sibling
   criterion aimed at the same function already treats its domain as declarations.
2. **REQ-03, which SC-05 serves, says "A board declaration that is **present but unusable**".** A/B/C/D/E
   are none of them present-but-unusable declarations.
3. **REQ-09 positively requires A and D to stay tolerant** — "a project that genuinely has no board
   can still be onboarded and operated." A project mid-onboarding has no `harness.json` (A) or no
   `github` block (D).

The broad reading therefore makes SC-05 demand a change that **breaks REQ-09**, the requirement its
own clause 1 exists to protect. A reading under which the only sanctioned remedy violates a signed
requirement is the wrong reading.

**I am not adopting the narrow reading on my own authority.** Reporting SC-05 as **partial**: met
4/4 under the narrow reading, 3/4 under the broad one, with the narrow reading better supported.
The operator's cheapest correct move is **Option E** — confirm the scope. That is a clarification,
not a rewrite.

**Two docstring claims are falsified**, reported separately from SC-11 because they are code, not
`DECISIONS.md`: `gh_board.py:48` ("That is the ONLY non-error path") and `:51-53`, which lists "the
`github` block absent" among the raising shapes — probe D shows it returns None. The panel reports
the same inaccuracy propagated to `gh-sync.py:129`.

### Options for closing sub-clause 1c, each with its own cost

| | What | Blast radius | Runs |
|---|---|---|---|
| **A** | Make all six shapes raise — 1c becomes true | **Largest and it collides with REQ-09.** A project with no `.harness/harness.json`, or an unreadable one, becomes a hard error at every `load_board` caller. That is precisely the onboarding path clause 1 exists to protect. Touches DEC-174 am.3 and DEC-196's null shape | 1 code task + 5 new cases + re-review ≈ **2 runs** |
| **B** | The operator's one-liner — make `:72-73` raise | Closes **D and E only**. A project shipping a `harness.json` with no `github` block now errors. **1c stays FALSE** (A, B, C still silent). Do not price this as the fix | 1 branch + 2 cases ≈ **1 run** |
| **C** | Re-plan: **strike** sub-clause 1c outright, recording that its content is already carried by SC-04's eight `load_board` shapes. Not a substitute sentence — a deletion with a named reason | BRIEF edit → **resets `## Approval`**, needs the user's signature. Zero code. The operator signs a *removal*, not new coverage | **0 runs** |
| **D** | Accept partial, ship, correct the docstring only | Records a signed criterion as partial. Honest, but the falsification risk is a later summary rounding it to met | 0 (direct edit) |
| **E** | **Confirm the narrow scope** — rule that "non-error path" ranges over board declarations, as SC-04, REQ-03 and REQ-09 all already do. 1c is then **true** and SC-05 is met 4/4 | A ruling on what the signed sentence already meant, not a change to it. Arguably no re-signature; the operator decides that | **0 runs** |

**Recommendation: E, with the docstring correction (Q4) bundled in regardless of which is chosen** —
`gh_board.py:48` and `:51-53` are false under *every* option.

E is right on the merits, not just on budget. Three independent parts of the signed BRIEF already
scope `load_board`'s domain to board declarations, and the broad reading makes SC-05 demand a change
that breaks REQ-09. The panel additionally verified that all three file-level silent shapes are
guarded ahead at every caller (`board-station.py:114-133`, `gh-sync.py:135-151`,
`check-state.sh:1138-1147`), so nothing is reachable-broken either way.

**A is the option that makes the sentence true and the product worse.** B does not close 1c at all —
A, B and C shapes stay silent — so it should not be priced as the fix. C is the honest fallback if
the operator reads the sentence broadly and wants the record clean.

With the feature at 20/20 runs and E1 pending, E and C are the only options needing no run; E would
still be my recommendation with the budget wide open.

## SC-06 — partial, per failure mode plus the no-fallback clause

| sub-clause | verdict | evidence |
|---|---|---|
| returns the board with **no checkout present** | met | `product_config reads the remote at default_branch with no checkout on disk` (`test-factory-config.py:500`) — asserts `_no_checkout` *and* the value |
| **missing file** raises naming repo/path/ref | met | `file_at_ref: a missing file raises GhError naming repo, path and ref` (`test-factory-gh.py:930`, fixture `Result(1, stderr="404 Not Found")`) + `product_config raises naming repo, path and ref when the remote read fails` (`:528`). **Mutant:** `factory_config.py:277-281` → `return {}` reddens exactly `:528` |
| **unparseable JSON** raises naming repo/path/ref | met | `:551`. **Mutant:** `factory_config.py:284-288` → `return {}` reddens exactly that case |
| **`gh` unauthenticated** raises naming repo/path/ref | **behaviour met by my probe; no committed test** | I stubbed `factory_gh.subprocess.run` → exit 1, stderr `gh: ... please run: gh auth login`. `product_config` raised `FleetError` naming repo, path and ref. But `run_gh` raises `GhError` on **any** non-zero exit, so this and missing-file are structurally one branch. No test names this mode, and none can distinguish it without changing `factory_gh.py` — eng-10's Q1 is correct |
| never falls back to a **checkout** | met, discriminating | `:625` plants a stale checkout board `777333`, a value used nowhere else in the file |
| never falls back to a **cached value** | met | `product_config memoisation: a failing read is not cached and the next call succeeds` (`:671`) |
| never falls back to a **default** | met | both mutants above replaced the raise with `return {}` — a default — and both reddened |

**Note the criterion's own enumeration:** SC-06 names three modes. The two cases eng-10 added cover
JSON-parse and **non-mapping**, and non-mapping is not one of the three. So the fix added one
in-scope case and one out-of-scope one.

**Durability gap — twice what eng-10's Q2 reported.** Grepping `plan.yaml` for each SC-06-bearing
ok-line:

| ok-line | hits in plan.yaml |
|---|---|
| `reads the remote at default_branch with no checkout` | 2 (pinned) |
| `remote content is not JSON` | **0** |
| `remote content is a JSON list` | **0** |
| `never falls back to a checkout on disk when the remote read fails` | **0** |
| `a failing read is not cached` | **0** |

Four of five are deletable with the suite green. On a `verify: automated` criterion in *this*
feature, evidence that can be silently deleted does not meet the bar. **Hence partial, not met.**

## SC-07 — partial, 1 of 3 consumers discriminating

Each consumer has its own named assertion and no two share one — that half holds. But two of the
three **cannot fail**, mutation-proven. `DEFAULT_BRANCH = "main"` in all three test files, so a
hardcoded `"main"` is invisible.

| consumer | assertion | mutant | result |
|---|---|---|---|
| `factory_claim` | `factory_claim reads default_branch from the fleet entry before any clone exists` (`:709`) | `factory_claim.py:355` → `"main"` | **reddens** exactly that case ✓ |
| `factory_land` | `(M1) pr create base is the fleet's default_branch` (`:288`) | `factory_land.py:67` `--base` → `"main"` | **0 FAILs — survives** ✗ |
| `factory_workspace` | end-to-end run succeeds | `factory_workspace.py:115` → `"main"` | **0 FAILs — survives** ✗ |

SC-07 justifies the `factory_workspace` clause as "its end-to-end run succeeds, **which it cannot do
if the key has left the fleet entry**". That is literally true, but the instrument carrying it is
`load_fleet`'s schema rejection (`factory_config.py:183`) — which is **shared with every other
consumer**, the one thing SC-07's "no two consumers sharing one" forbids.

`case3_presence_kaya_default_branch_is_master`: **PASS** (my run).

## SC-10 — partial, 11 of 12 items

- **Non-readers 4/4** — T-04's loop over `wayfind.py`, `layout_migration.py`,
  `check-plan-routes.py`, `branch-create-gate.sh`, each with its own positive control
  (`grep -qE '^(def |#!/)'`), all matching zero moved keys. T-04 GREEN, my run. (Regression guard
  only — the BRIEF's own gap note already says so.)
- **Readers 7/8:** `gh_board.py` ✓ and `check-state.sh` ✓ (literal-absence + positive controls,
  T-04/T-05 GREEN); `gh-sync.py` ✓ and `board-station.py` ✓ (named behavioural cases in T-04's
  verify); `factory_config.py` ✓ (the eight `board_for raises...` cases, which only pass after the
  migration); `factory_decompose.py` ✓ and `factory_claim.py` ✓ — both mutation-proven by me
  (`factory_claim.py:266` → `"Ready"` reddens `(P1) board B's query is built from board B's own
  field and ready option, not board A's`).
- **`factory_land.py` ✗** — SC-10 requires "a named case pinning the value they now resolve through
  the new source". `(M1) sets the station to Review` (`:308`) does not: `factory_land.py:95` →
  `"Review"` gives **0 FAILs**, because the fixture's review station is literally `"Review"`.

## The rest

**SC-01 — partial.** Clause B (rejection names the key and where the board moved) is **met and
strongly pinned**: `test-factory-config.py:331-338` asserts `repos[mruangutai/harness].board` *and*
`github.board` *and* `.harness/harness.json`; `:216-243` pins the top-level destination
present-**and**-absent. Clause A ("declares **only** schema, `repos[].name`,
`repos[].default_branch`, `workspace_root`") is **true in the tree by my reading of
`.harness/factory/fleet.yaml`** but pinned by nothing. Positive control: I appended
`stations:\n  ready: Bogus` to `fleet.yaml` in the worktree → `test-no-distribution.py` **0 FAILs**,
`test-factory-config.py` **0 FAILs**. The only committed assertion,
`case3_absence_no_board_in_fleet`, forbids `board` alone. So a closed-world clause on a
`verify: automated` criterion rests on inspection.

**SC-03 — met, with a named instrument blind spot.** T-04 and T-05 both GREEN at HEAD, my runs.
`derive_station`'s body contains none of the five names (my re-derivation). The INV-26 slice contains
no `"Building"`/`"Review"`/`"Backlog"`/`"Ready"`. It **does** contain `"Done"` once, at
`check-state.sh:1204` — a *feature-status* literal (`_fj.get("status")`), not a station name, and
T-05's grep deliberately omits `Done` from its alternation for exactly that token collision,
compensating with a narrower `_EXPECT[^=]*=` grep. Both positive controls present and passing.
**Blind spot:** a genuine station literal `"Done"` reintroduced anywhere in the INV-26 block outside
an `_EXPECT` assignment would not be caught.

**SC-04 — met, 16/16.** My own run: eight `load_board raises naming the file and the key: <shape>`
in `test-gh-board.py` and eight identically-named `board_for raises...` in `test-factory-config.py`,
all pass — the same eight shapes through both entry points, so neither caller can be loud while the
other is silent. Structurally discriminating: these are raise-assertions with message-content checks,
which cannot pass if the raise is removed (unlike an absence-grep).

**SC-08 — met.** `case3_absence_harness_is_not_a_fleet_member` PASS (my run), and named by that
exact string in T-07's verify at `plan.yaml:1128`.

**SC-09 — met, my own live read today.** `gh api
repos/mruangutai/kaya-ai/contents/.harness/harness.json?ref=master` returns `github.board =
{owner: mruangutai, number: 2, station_field: Status, stations: {backlog, ready, building, review,
done}}` — five stations — and none of `project_number`, `project_id`, `status_field`,
`in_progress_option` at top level or inside `github`. Independently confirms the code-reviewer's
verdict at `14994b3`.

**SC-11 — met, 3/3.** DEC-174 **amendment 3** (2026-08-18) exists, names FEAT-24, and explicitly
records that it falsifies one paragraph of amendment 2 which is left standing unedited. DEC-196
**amendments 1 and 2** exist, both naming FEAT-24; amendment 1 covers the stations-map clause.
`gen-decisions-index.py --stdout` vs `DECISIONS-INDEX.md` → `cmp` **identical**, rc=0, my own run.
Durability caveat: the per-entry assertions live only in T-10's `verify:` (`plan.yaml:1370-1376`),
which ran once at build time; the byte-match, by contrast, *is* committed
(`test-gen-decisions-index.py:366-383`). And eng-10's Q5 stands — T-10 checks an amendment *exists*,
never that it is *true*.

**SC-13 — clause 1 met, clause 2 not_met. Reported separately, never averaged.**
- **Clause 1 (met):** registered script count = **28** at HEAD — `UNIT_SCRIPTS` 16 +
  `INTEGRATION_SCRIPTS` 12, `run-unit-tests.sh:17-18`, my own count, matching the panel's 28/28
  before. No test file removed. **The instrument's blindness, confirmed:** this very diff deleted two
  named cases (`every_repo_declares_its_own_board`, `kaya_ai_is_paired_with_board_2`,
  `test-no-distribution.py:293-298`) and the count stayed 28, because counting FILES cannot see a
  deleted CASE. The criterion's own chosen instrument provably could not see the deletion that
  happened inside its own feature. Worse, nothing in the tree *implements* the before/after
  comparison — the 28/28 figure exists only because a reviewer, and now I, counted by hand.
- **Clause 2 (not_met):** structurally unclearable pre-merge. The suite is green at HEAD (rc=0,
  0 FAIL, 1582 ok/PASS, my run), the best available proxy — and it is not the merge commit.

## REQ-08 — reported separately from SC-11, as instructed

**DEC-174 amendment 3 is TRUE at HEAD.** It asserts both fleet rejections raise "a message that
names where the board moved to". Both do, verified at source: `factory_config.py:165-167`
(top-level `board`) and `:189-195` (`repos[].board`), each naming `github.board` in the
repository's own `.harness/harness.json`. The panel's stale-destination finding is closed **in the
code** by fix cycle C5 — REQ-08 satisfied by making the record true rather than by editing it, which
also avoided dragging `gen-decisions-index.py` behind it. This confirms the dispatch's correction 2.

## Open questions

- **Q1 (blocking):** SC-05's sub-clause 1c turns on whether "non-error path" ranges over board
  declarations (then it is TRUE, SC-05 is met 4/4) or over every input to `load_board` (then it is
  false). SC-04, REQ-03 and REQ-09 all already scope `load_board`'s domain to declarations, and the
  broad reading makes SC-05 demand a change that breaks REQ-09. Options A–E above.
  **Recommend E** — confirm the narrow scope. Zero code, zero runs. Not mine to rule.
- **Q2:** SC-01 clause A, SC-07 (`factory_land`, `factory_workspace`) and SC-10 (`factory_land`) each
  have a named, passing, **non-failable** assertion, mutation-proven. Closing all four is one code
  task (change four fixture values so they differ from the literal) + a re-review — **2 runs the
  budget does not have.** The cheapest honest alternative is to record them partial and carry the
  four fixture changes as a follow-on.
- **Q3:** Four of SC-06's five committed assertions are pinned by no `verify:` block, not two. Fix is
  four `has` lines in T-02's verify — a `plan.yaml` edit on a `status: done` task, therefore pm's.
- **Q4:** `gh_board.py:48` and `:51-53` are falsified by my probe, and the same inaccuracy is
  propagated to `gh-sync.py:129`. A docstring correction, needed under every SC-05 option.
- **Q5:** SC-13's clause-1 instrument is not implemented anywhere in the tree and cannot see a
  deleted case. Carried from the panel; the operator has this.
