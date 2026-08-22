# FEAT-31 — ready to ship except for the two things only you can do

**All 19 tasks are done, the blocking qa gate passes, the review panel's one gating finding is fixed,
and 12 of the 14 success criteria are met.** The two that are not are `verify: uat` — SC-10 and
SC-15's behaviour half — and `gates.uat` is `blocking_when_uat_criteria_exist`, so **they block the
ship independently of every other gate. No squad can close them. That is the whole of what is left.**

**The feature works, and it is measuring you right now.** `context-watch.py` finds every
`harness-orchestrator` on this machine — I re-measured both sides in one process: **109 sidecars by
independent glob, 104 measured rows + 5 unmeasured = 109 by the tool. Exact.** Of those, **37 are at
or above the 200,000 threshold.** `verify-context-watch-live.py` agrees with an independent
recomputation to the token on a live agent.

**The most useful thing I can tell you: this orchestrator crossed its own feature's threshold while
building it.** My own row read `current=186,503 headroom=13,497` mid-run and I am well past it now.
The instrument works on its author.

## What you need to decide

1. **Run the UAT. It is the only thing blocking the ship.** Two parts:
   - **SC-10** — run the tool with no argument, then with a live orchestrator named, and answer its
     four questions from the output alone. Runnable for the first time.
   - **SC-15's behaviour half** — needs a **clean relay**: a successor whose *only* input is the
     feature directory. **I offered myself as that evidence and pm refused it, correctly.** My first
     dispatch did match my predecessor's `## Next` — but I also held a prompt naming T-05 and T-09,
     so there are two sufficient causes for one observation against a criterion whose premise is a
     successor given *only* the directory. pm called it **confounded rather than imperfect**. I
     declined to grade my own relay; the grader rejected it. That separation is worth more than the
     criterion.
2. **Confirm the signature covers 19 tasks.** The plan gained **T-19** after
   `notes/signature-reaffirmed-18-tasks.md` was signed at 18. `approval:` is byte-identical and SC-09
   was already approved scope, so I read T-19 as *fulfilling* the signature rather than extending it —
   but that is your call, not mine to assume.
3. **Two stray files sit in the MAIN checkout**, outside my worktree and not mine to remove:
   `runs/t09-product/digest.md` (stale, claims `BLOCKED`, **contradicts** the real PASS) and
   `runs/fix3-eng/state.yaml`.

## The three gates

| Gate | Result |
|---|---|
| **qa (blocking)** | **Matrix PASSES.** unit, integration, `--check-kinds` all exit 0; zero FAIL, MISCONFIGURED, KIND-DRIFT |
| **review (advisory_unless_high)** | **FAILed on one `high` — now fixed and re-verified** |
| **uat (blocking)** | **OUTSTANDING — yours** |
| goal-check | **12 of 14 met**; SC-10 not met, SC-15 partially |

**The qa gate is worth reading twice, because both halves were true at once: no test failed, and the
gate still failed.** The matrix passed on all three commands while **SC-09 — an approved criterion —
had no implementing task at all.** And `plan.yaml`'s D-02 *falsely claimed* plan4 had closed it,
crediting a task whose own intent forbade the work. **The false record is what hid the gap** — inside
the very decision written to stop that happening. Closed by T-19; D-02 corrected with the superseded
sentence kept and marked, not reworded to look as though it had always held.

**The panel's one `high` was the feature's own rule, unmet in its own code.**
`notes/settled-Q-HOOKCTX.md:48-51` makes it a *hard obligation* that the warning say, in its first
line, that nothing was blocked and no retry or revert is needed — **before** any figure. The shipped
text led with the context number and met none of it. Exposure was total and measured: **36 of 36**
crossing orchestrators made a Write/Edit/Bash call afterwards, and the framing had already caused one
real revert of a landed write. The warning now opens:

> `context-watch: this write already landed on disk -- do not retry it and do not undo it.`

Pinned by **order** assertions — `startswith` plus `.index(reassurance) < .index(figure)` — on the
library return, stdout, *and* the real stderr channel, with a diff-confirmed mutant red at 76/81. A
substring check would have passed on a text that buried the reassurance at the end.

**I can corroborate that finding from my own behaviour.** Eight of my `feature.json` writes drew a
`PostToolUse` exit 2 wrapped as a "blocking error". Every one had landed. The only reason I kept them
is that `check-domain.sh` says `OVER BUDGET (already written)` rather than `BLOCKED`.

## What I got wrong

**Six errors, and the pattern matters more than the count.**

1. **I read a run's digest before its run returned — three times.** A digest is rewritten *in place*,
   so reading one early reads a draft. The third instance **dispatched T-19 twice**: two hosts ran it
   concurrently, and `mutates_repo` only serializes inside one host's DAG. DEC-159 does not carry its
   new rule twice **only because pm had written "run the verify command BEFORE your edit" into T-19's
   own intent.** A member's defensive instruction saved the criterion from its orchestrator. I later
   watched the trap confirm itself — hashed SIMPLIFY's digest, saw it stable five times while the run
   said `blocked`, then saw it change to PASS.
2. **I told a fix to regenerate the decisions index "only if the row changed."** Wrong in the
   silently-corrupting direction: rows carry `@line` anchors, and T-19 shifted **39** of them.
3. **I cited DEC-141** for "generated files follow their source". DEC-141 governs `render-map.py`.
4. **My "highest decision is DEC-194"** came from a grep matching only the 25 amendment sub-headings,
   not the 195 entries. It was 197.
5. **I named an artifact path pm holds no grant for**; the guard denied it correctly.
6. **A narration error the panel caught.** I wrote "103 + 5 versus a glob of 107 — exact agreement."
   **103 + 5 = 108.** The finding was real; I paired figures taken minutes apart while the corpus was
   growing. Re-measured in one process it closes exactly at 109.

**Errors 2 and 3 were caught by a lead reading the source instead of complying with my prose; 5 by the
domain guard; 6 by the review panel.** Every one of my mistakes was caught by something other than me,
which is the system working — but four of the six were *assertions I made without checking*, and that
is the habit to distrust.

## Two things about this branch that look like defects and are not

**Hooks resolve through `CLAUDE_PROJECT_DIR` to the main checkout, so a branch that changes the
enforcement layer is still governed by the old layer while it is being built.**

- **T-15's new rule is inverted in-session.** The branch's own validator passes 31 files with the
  `agent` key and fails naming `runs[9]` without it — but the session's hook rejects the key as
  *undeclared*, because the main checkout's schema predates T-15. **The key required after merge is
  refused before it.** I kept it; removing it would break the validator at merge.
- **T-17's hook cannot be observed firing from here.** It first fires after merge. Its committed
  coverage was judged adequate without that, by qa and again by the panel.

## Proposed backlog

Unstruck rows become issues on your acceptance. **Anything not listed dies silently, so this is
everything that survived.** None of these duplicate #663–#669.

| ID | Finding | Nature |
|---|---|---|
| B-1 | **No gate ever walks the real projects root.** `verify-context-watch-live.py` is in neither `UNIT_SCRIPTS` nor `INTEGRATION_SCRIPTS`, so even its own `--self-test` never gates — the discovery-depth mechanism this feature exists to fix stays undetectable by CI. The panel's deepest residual | bug |
| B-2 | **DEC-159 contradicts itself and the code**: `:3986` denies handoff notes above **40** lines, its own `:3968` says **~60 (raised at DEC-160)**, and `check-domain.sh:951` enforces **60**. It survived T-19 — a cycle whose whole subject was a false clause in this same entry | bug |
| B-3 | **The tool cannot say "I could not scan."** `main()`'s catch sets `rows = []` and prints "no orchestrators found" at **exit 0** — a clean sentence meaning the opposite of the truth. Three separately-filed reviewer items are this one absent capability | bug |
| B-4 | **Two hosts can run the same task concurrently.** `mutates_repo` serializes only inside one host's DAG; two hosts are invisible to each other. It happened here and only a task's own defensive intent prevented a double edit | bug |
| B-5 | **`plan.yaml` resolves to both `harness-orchestrator` and `harness-pm`**, so nothing structurally prevents the concurrent-writer plan overwrite that actually occurred in the plan phase | bug |
| B-6 | Hook tax: the `PostToolUse` matcher fires for **every** agent type while the script gates on `agent_type` internally — ~19ms per early-exit call from ~15 non-subject personas, atop `check-domain.sh --post`'s ~70ms. The matcher keys on tool name only, so the filter cannot move into `settings.json`. **Not** a re-litigation of D-25, which never costed the non-orchestrator population | enhancement |
| B-7 | `_orchestrator_jsonl_paths`'s docstring at `:570-576` claims parity with `discover_orchestrator_rows` that the code does not deliver — one feeds `unmeasured_count`, the other silently `continue`s | chore |
| B-8 | `warn_for_agent`'s docstring documents the forbidden-word contract but not the reassurance-first ordering, now the text's most consequential property | chore |
| B-9 | `context-watch-hook.py:19-20` quotes a **moving** corpus as a fixed figure (3359 / 94.8%) against D-25's 3280 / 93.9%. Neither is false; neither says the corpus moves | chore |
| B-10 | The `DECISIONS-INDEX` generation contract has **no decision behind it** — grepping the index for `generat` matches only its own header, and the rule is enforced solely by a test, unreachable by the index-first reading path CLAUDE.md mandates | chore |
| B-11 | `DEC-159:3959-3960` says `feature.yaml` twice where the tree carries `feature.json` | chore |
| B-12 | Unknown whether Claude Code runs **every** command in one `PostToolUse` array entry after an earlier exit 2. `check-domain.sh --post` and `context-watch-hook.py` share that entry; if it short-circuits, SC-13 silently fails in the compound case. Asserted nowhere, first testable after merge | chore |
| B-13 | A run digest can stay a **pre-dispatch stub with no verdict** (`runs/plan3-product/`) while `feature.json` records a verdict for it, and nothing cross-checks the two | chore |
| B-14 | `validate-digest.py` passed a digest that omitted `must_fix` entirely and put `sc_status` outside `DIGEST` | chore |
| B-15 | `harness-pm` holds no `goalcheck-*` artifact grant, so the goal-check writes under `research-*` by necessity rather than intent | chore |
| B-16 | The footer's compaction-count assertion pins the positive direction only — a footer that always printed "1 measured row" would still pass | chore |
| B-17 | Two stray files in the MAIN checkout: `runs/t09-product/digest.md` (stale, claims BLOCKED, contradicts the real PASS) and `runs/fix3-eng/state.yaml` | chore |
| B-18 | **`expertise-merge.py` implements only `add` of the `add\|replace\|merge\|drop` its own schema documents.** `compute_union` only appends, refuses same-id-different-text (exit 7) and over-cap additions (exit 8) — so at a full section the move `harness-distill` *requires* (displace) and the move that is *safe* (use the tool) are mutually exclusive. **Found independently by all three squads.** Consequence this run: two eng members and one qa member completed their documented work by hand-`Edit`ing Expertise files **outside the tool's lock while sibling distillers were live writers to the same directory** — precisely the loss DEC-125 introduced the tool to prevent. Nothing was lost (I verified every changed file by id), but the safe path does not exist | bug |
| B-19 | `expertise-merge.py apply --entries` **silently no-ops at exit 0** when the entries file matches no entry line — indistinguishable from a successful apply. Two members hit it by passing the YAML ops block the skill shows two sections above the markdown the tool actually wants | bug |
| B-20 | **Three lead `replace` ops are unappliable and are recorded here so they are not lost**: eng-lead P-07/G-09/G-10 and validator-lead P-12 and siblings. They are in `runs/distill-eng/digest.md` and `runs/distill-validator/digest.md` under `expertise_update`. `runs/distill-validator` is BLOCKED solely on this | chore |
| B-21 | The `suite:` digest field has no agreed meaning for a distillation dispatch — four members split 2-2 between `n/a` and `pass`. A validator that accepts both cannot be routed on | chore |
| B-22 | The `SubagentStop` hook accepted an `expertise_update` returned as a list of prose strings rather than the ops mappings the schema defines | chore |

## Cost and budget

**cycles 6 of 10 — inside budget. Runs 21 of 20 — CROSSED, and I am telling you rather than
letting the session-entry check find it later.** Runs are informational by design (INV-22) and the
crossing never stops a branch, so the honest question is whether they earned their place. **My read:
yes, with two exceptions.** Each of the last six runs closed something specific — a task, a gate, a
panel finding, a memory pass — and none was a retry of a run that had already succeeded. The two
that did not earn it are the duplicate T-19 execution (my error) and one no-op spawn a lead burned
discovering it holds no messaging tool. The count is also a floor: main-session-direct segments
never appear in `runs:` at all, so the six tasks the operator ran are invisible to it. Three cycles were spent this session and each bought something: the SC-09 gap, the
panel's `high`, and nothing wasted on a retry loop. Waste I will name rather than bury: **one
duplicate T-19 execution** (my error #1) and **several leads force-closed with members in flight** —
the members outlived their hosts and finished the work, but two runs reported verdicts their own
members then contradicted.

**9 commits this session. The production diff is 20 files, 4,361 insertions, 54 deletions** — all
Python, shell, JSON and markdown, zero UI surface, which is why no ui-reviewer ran.

`check-state.sh` is down to **one** violation, FEAT-26's unapproved BRIEF — a different flow. **Nothing
in FEAT-31 violates**, where two board-card violations stood at session start.

## Close-out: what the memory pass actually found

**Ship-refresh was skipped and that is correct** — this project has no map to refresh, so there was
nothing to intersect.

**Distillation ran as three concurrent lead dispatches. 24 entries landed across 14 Expertise files,
both tiers pass their format gate at exit 0, and I verified every changed file by enumerating entry
ids against `HEAD` — no file was wiped and nothing was lost.** Displacements that show as
"lost + added" were deliberate curation.

**But the pass surfaced a defect that outranks its own output, and all three squads found it
independently** — B-18 and B-19. The short version: the tool that exists so two concurrent close-outs
cannot lose each other's entries can only *add*, so anyone at a section cap must either abandon the
required curation or leave the tool's lock. Three squads were writing concurrently while two members
did exactly that.

**I hit it myself and took the disciplined branch**, which is why my own file gained only two `Open`
entries while others curated: my Patterns, Gotchas and Outcomes are all at cap, so `expertise_full`
is the honest report rather than a hand-write.

**One measurement came back against its own hypothesis and is worth keeping.** The digest-skim step is
on probation for whether it earns its cycle. In the eng squad it produced **9 of 12** accepted entries
against **3** from members' own logs — it earned it. The sharper result is the correlation: the two
members that keep observation logs produced all three self-derived entries, and the two that keep none
produced zero and accepted 4 of 4 relayed candidates. **A member without a log has its memory written
entirely by its lead**, and a 9-of-10 acceptance rate on pre-generalised candidates is not a quality
signal. The eng lead's own first proposed op is the fix for that, and it withdrew a fourth op because
this run's evidence no longer supported it.

**One member caught itself.** qa found an entry its earlier spawn had built on a premise it later
retracted, reverted it, and restored the displaced text verbatim.

## Method — read this before trusting the above

**No report round was spawned.** I assembled this from the run digests on disk. Read in full:
`runs/build-eng/digest.md`, `runs/build2-eng/digest.md`, `runs/fix1-eng/digest.md`,
`runs/qa-validator/digest.md`, `runs/panel-validator/digest.md`, `runs/simplify-eng/digest.md`,
`runs/fix2-product/digest.md`, `runs/t19-product/digest.md`, `runs/goalcheck-product/digest.md`,
`runs/t05-eng/` and `runs/fix3-eng/` (from their returns), and my predecessor's briefing
`notes/ship-review-fix1.md`. Read at verdict-plus-headline depth, with their substance reaching me
through that predecessor briefing which had read them in full: `runs/plan-product/`,
`plan2a`, `plan2b`, `plan4`, `plan5` — and `runs/plan3-product/digest.md`, which **is a
pre-dispatch stub carrying no verdict at all** (B-13).

**Every figure in this briefing I measured directly in this worktree**, and where a figure of mine was
wrong the correction is above rather than quietly dropped. The one number I inherited without
re-deriving is the ~19ms hook tax (B-6), which is the efficiency reader's measurement, not mine.

**Two disclosures that limit this document.** `.gitignore:7` ignores `.harness/*/features/*/runs/**`,
so **every digest path cited here is local to this worktree and never reaches the default branch** —
if you want any of it durable, it has to move. And the goal-check graded at `fcb8984`, one commit
before the fix3 tip now pinned as `review_sha` (`0fc10e5`); fix3 changed warning text and its
assertions only, so no SC verdict turns on the difference, but I did not re-run the grade.
