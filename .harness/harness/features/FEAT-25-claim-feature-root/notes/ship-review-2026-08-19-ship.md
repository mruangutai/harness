# Ship review — FEAT-25 claim feature root

**Recommendation: ship.** Branch `feat/FEAT-25-claim-feature-root`, two commits, `8d7b273`.
All eight success criteria met, the blocking gate green at the commit it grades, the review panel
returning nothing at `high`. Four cycles of ten, fourteen runs of twenty.

## What changes for you

**The factory can take work again.** `factory_claim.py:43` was still building its feature root at
`.harness/features`, the path unit 3 vacated. Every plan read failed, so every candidate came back
refused and nothing was ever claimed. It failed closed — no wrong work was handed out — but the
live kaya proof (#496) takes its work through this tool and could not start. That edge is now
unblocked.

**And when a refusal is genuine, it says why.** Before, a candidate whose plan could not be read was
told its title yielded no matching plan task, sending whoever debugged it to issue titles and plan
contents when the cause was a directory that was not there. It now names the absolute path it tried
and says whether the root or the plan file is missing. The old message survives, narrowed to the case
it actually describes.

**Third, the layout detector can now judge `factory_claim.py`** instead of excluding it — the file
whose stale root just cost you a dead factory is no longer invisible to the check that would have
caught it.

## How this was assembled — read this before trusting the rest

**No report round was spawned.** Three lead spawns to re-narrate digests I can open is spend with
nothing to surface it. Assembled by reading every run digest off disk, including the plan phase I did
not run:

`runs/2026-08-18-1-product/`, `2026-08-18-1-planreview-validator/`, `2026-08-18-01-eng/`,
`2026-08-18-2-product/`, `2026-08-18-3-product/` (plan) · `2026-08-19-1-eng/` (build) ·
`2026-08-19-2-qa-validator/` (gate) · `2026-08-19-3-simplify-eng/` (simplify) ·
`2026-08-19-4-panel-validator/` (panel) · `2026-08-19-5-goalcheck-product/` (goal-check) ·
`2026-08-19-6-distill-{eng,validator,product}/` and `2026-08-19-7-distill2-validator/` (close-out) —
all under `.harness/harness/features/FEAT-25-claim-feature-root/runs/`, each with a `digest.md`.

**UAT: none required.** The BRIEF declares no UAT criteria and no criterion carries a `uat` method —
verified by pm and re-verified by its lead reading the document end to end. Nothing waits on you to
execute.

## The two judgement calls the ship rests on

Both are mine or my leads', both are disclosed rather than absorbed, and either can be overturned —
overturning the first costs a re-run, the second costs a fix cycle.

### 1. The blocking gate is green at the commit, red in the working tree

`run-unit-tests.sh --kind integration` **exits 1 in this working tree.** One script is red:
`test-gen-decisions-index.py`, because the uncommitted `.harness/harness/docs/DECISIONS.md` in your
tree disagrees with a fresh regeneration of the decisions index. That file belongs to another
workstream, is absent from FEAT-25's diff, and no file this feature touched participates.

qa called the kind satisfied by attribution. **The validator lead refused that, and was right to** —
harness.json's own rule is that the only soft skip is a signed `status: excluded`, never one inferred
at gate time, and a lead who may excuse a red command by attribution has removed the gate. But its
verdict was unresolvable from where it stood, because a lead holds no shell.

**So I measured it.** In a throwaway worktree checked out at `8d7b273` with no working-tree drift,
the same configured command, unmodified, **exits 0 with all 12 scripts passing.** Nothing excluded,
nothing waived, nothing inferred. The gate grades a commit; the working tree is not what ships.
Method written down and repeatable at `notes/gate-measurement-2026-08-19.md`.

**If you reject that reading, the gate is red and this does not ship until the index is regenerated.**
I did not regenerate it: it is another workstream's uncommitted edit and not mine to resolve.

### 2. "verify: automated" means graded by running code, not by a standing assertion

Two criteria — SC-04 (the refusal names the path) and SC-06 (the detector reads `factory_claim.py`)
— are **factually true at this commit** but each has one clause carried by no permanent assertion.
Under a stricter reading of `automated` both flip to unmet and you are owed a fix cycle.

pm took the looser reading and its lead accepted it on the BRIEF's own vocabulary: the document uses
exactly two methods, and SC-08's `inspection` already means "graded by reading", so `automated` must
mean "graded by running" or there is no word left for it. SC-02 corroborates — it writes its own
pinning demand into its wording, so the author knew how to require pinning and did not require it of
SC-04 or SC-06. **I accept it and flag it as the interpretive call it is.**

## What each squad found

**Engineering** (`2026-08-19-1-eng/digest.md`) — three tasks, all to backend-dev, **zero send-backs**.
Every new assertion was observed failing before the fix landed, and no probe edits were needed
anywhere because the work was ordered tests-first. Suite counts 120 / 106 / 41 against the `d1ffd7f`
baselines 114 / 106 / 40 — no threshold widened, no assertion deleted, exactly the one authorised
rename. Its lead disclosed that it ran no command itself (leads hold no shell) and routed each verify
to an in-squad non-doer that re-extracted the command from the approved plan first.

**Simplify** (`2026-08-19-3-simplify-eng/digest.md`) — four independent readers, **nothing applied**,
one backlog row. It declined its single permitted fix on the grounds that the edit's only proof would
have been written by the same agent making it, over text nothing else pins. That is the right refusal
and I record it as a result, not a gap.

**Validation** (`2026-08-19-2-qa-validator/`, `2026-08-19-4-panel-validator/`) — the panel gates
nothing; nothing reached `high`. It produced two real mutation proofs, and its lead **removed** a
member's finding that a diagnostic branch had "zero test coverage": it is covered, and shipping that
claim would have put a false coverage gap in your backlog. Security scoped in and cleared; the UI
reviewer scoped out on a measured census rather than an assumption.

**Product** (`2026-08-19-5-goalcheck-product/digest.md`) — 8/8 criteria met, six on pm's own
measurements with the two inherited ones named. pm caught what the whole prior record had missed:
SC-07 says each suite "passes", and every earlier artifact evidenced that with an exit code — which
is precisely what the fail-open below defeats. pm re-established it with an empty `FAIL` grep.

## A correction to our own record, which you should see

The panel's signed digest claimed the fail-open defect existed at "four sites, two files" and
reassigned its owner to the shared test harness. **That is false.** The validator lead falsified its
own signed claim during distillation, and I verified independently: at all three cited
`test-check-state.py` sites the accumulator sits outside the guard, and the file contains no
`fails += 1` at all. It is **one site in one file**. The panel digest keeps its original text with a
correction appended — struck, not edited out. The verdict is unaffected; the backlog row's scope and
owner are.

## Proposed backlog

Unstruck rows become issues on your ship acceptance. **Anything not listed here dies silently**, so
this is everything that survived.

| ID | Nature | What |
|---|---|---|
| **B-1** | **decision** | **#500 alone may not unblock unit 8 (#496).** `factory_decompose.py:276-283` and `:360` label every issue `feature:<id>` unconditionally, so a kaya feature directory outside the `harness` segment stays unreadable and is still refused — now with a correct message, but still refused. **Three options: place kaya's first feature directory under the harness segment; use an unlabelled first proof issue; or pull unit 7 (#495) forward.** Yours to settle before unit 8 is dispatched — not this feature's to fix. |
| B-2 | bug | Fail-open in `test-layout-migration.py:416-418`: `fails += 1` sits inside `if not ok and detail:`, so a failing case with no detail prints `FAIL` and the script exits 0. Reachable at `:304`, `:308`, `:312`. Pre-existing (measured: this feature's whole diff to that file is one hunk adding case 22). One site, one file. Remedy is a one-line dedent. |
| B-3 | chore | Case 22 pins the features surface as CLEAN but not that `factory_claim.py` is among the readers. Deleting the table row *and* its fixture stub together evades the import guard, so the detector could silently stop judging the file again. Remedy is one assertion — but it is a plan change, since T-03 says "add nothing else". |
| B-4 | chore | The two new refusal texts are pinned by no byte-exact assertion anywhere in the repository. A wrapping slip that drops a space degrades the diagnostic with every gate green. |
| B-5 | chore | `.harness/harness/docs/DECISIONS.md` in your working tree disagrees with a fresh decisions-index regeneration, reddening `--kind integration` for every run in this checkout. **It also masks `test-check-plan-routes.py`, the only enforcer of the load-bearing `# balance: (` comments.** Unowned; one regeneration closes both. |
| B-6 | chore | `test-factory-claim.py:997` and `:1003` still label themselves "seven" over assertions correct at eight. Assertions are right, labels lie. Deliberately not fixed — SC-07 authorises exactly one rename and it is spent. Should ride B-2/B-3's pass on that file. |
| B-7 | chore | Diagnostic text at `factory_claim.py:194`/`:198` uses a plain hyphen where every sibling uses an em-dash, so the emitted line mixes both. The text is plan-mandated, so changing it is a plan change, not a defect fix. |
| B-8 | bug | `validate-digest.py --hook` fires on `SubagentStop` whenever a lead yields with members in flight. **Five independent reports from four hosts on this feature alone.** It twice produced a digest materially wrong about its own run. Leads now burn context holding turns open as a workaround. |
| B-9 | bug | Leads hold no `SendMessage` tool, though `harness-team` and the Agent tool description both reference it for continuing a member. A lead cannot course-correct a running member; one lead spent a spawn discovering this. Grant it or remove the references. |
| B-10 | chore | The mirror created parent issue **#539** rather than adopting the effort's execution record **#498** — nothing on disk named an adoptable parent. Milestone #16, sub-issues #540/#541/#542, all closed. You may want them linked by hand. |
| B-11 | chore | Two feature directories share the id FEAT-25 (`claim-feature-root`, `expertise-repository-tier`). Mechanically safe — lookups use the full slug — but every human "FEAT-25" reference is ambiguous. Nothing allocates ids (#323). |
| B-12 | chore | `.harness/expertise/` has a craft/repository split, but the repository tier does not exist in this tree. A member correctly evicted a repo-specific fact this feature and it had nowhere to land. The split will keep evicting repo knowledge until the second tier is built. |
| B-13 | chore | `test-bash-write-guard.py` and `test-check-domain.py` are cwd-sensitive — exit 1 from inside `bin/`, 0 from the repository root — and `run-unit-tests.sh` inherits the caller's cwd. A gate measured from the wrong directory reads three reds and misattributes them. |
| B-14 | chore | `check-domain.sh --post` flags historical `STATE.md` files inside a temporary worktree as live violations, so any worktree probe emits spurious blocking output. |
| B-15 | chore | No member wrote an observation log this feature, so **every** distilled entry traces to a lead's recall rather than a member's own record. Memory quality is currently a function of one relay. Nothing requires members to log. |
| B-16 | chore | pm removed from its own memory the rule "a source reading is not admissible evidence for a `verify: automated` criterion — name the passing test or return it not met", while the reading that rule embodies is the open question in section 2 above. If you rule strict, re-add it. |
| B-17 | chore | An untracked note, `.harness/notes/dec-11-frontmatter-enumeration-2026-08-19.md`, was present in my capture at branch-cut and gone minutes later. Untracked, so git holds no copy and it is unrecoverable. No agent's git captures ever saw it and no member touched that path. Stated as a fact, without a theory. |
| B-18 | chore | **The distillation writes to `.harness/expertise/` are NOT committed, deliberately.** Ten Expertise files carry this feature's distilled entries in the working tree. They sit outside the feature directory and in no task's `files:` list, so committing them on this branch would fail SC-08 clause (a) on any re-grade of a criterion the goal-check already passed. They are durable on disk and format-checked (`check-expertise.sh` exit 0, all 15 files, counts held). **Where they land is your call** — a separate commit outside the feature branch is the clean option, and my own memory already carries this as an open question: shared Expertise has no lineage protection and nothing reconciles it against a plan's declared files. |
| B-19 | bug | **Nothing serialises Expertise writes against an open distillation run.** Section caps are computed from the copy injected at spawn, so a concurrent writer can fill the slot a member counted and turn a valid `add` into a cap violation. It happened here: I applied the completed run's ops while a redundant second pass was still in flight, and that pass returned two ops that would have made `harness-code-reviewer.md` 16 Gotchas against a cap of 15. Caught only because the lead flagged it blocking and told me to re-grep. |

## Numbers

- **Cycles: 4 of 10.** Three tasks landed first-pass with zero send-backs. The four are: two inherited
  from planning, one send-back inside the eng distillation, and one re-dispatch of a distillation run
  I judged incomplete — it had in fact completed, so that cycle bought nothing and I am counting it
  against myself rather than quietly dropping it.
- **Runs: 14 of 20 — under budget**, and each one resolved something: five planned, one built, four
  validated and graded, four distilled.
- **Diff: six files**, all under `.claude/skills/harness/bin/`, exactly the union the plan declared.
  All five forbidden files individually absent; `load_board` absent from every added line.

## What I need from you

1. **Ship, or overturn one of the two judgement calls in section 2.** You pre-authorised the chain
   through the main session — I have opened no PR and merged nothing.
2. **Strike any backlog row you do not want**, by ID.
3. **B-1 needs a decision from you before unit 8 is dispatched**, and it is the only row that blocks
   other work.
4. **Tell me where the Expertise writes should land (B-18).** They are uncommitted on purpose and
   they are the one piece of this feature's output with no home yet.

## One note on the criterion that nearly caught me

SC-08 grades the three-dot diff **minus this feature's own directory**, and says in as many words
that prose in the feature's own notes naming a forbidden file or the `load_board` symbol cannot fail
either clause. Re-grading at the final commit I ran clause (b) over the full diff and got a failure —
`load_board` appears in 21 added lines, every one of them inside the feature directory, in the
digests and receipts that discuss the constraint. Restricted to the graded set it is clean, as are
all five forbidden files, checked individually. The criterion anticipated the exact mistake its
grader would make, which is worth knowing the next time someone is tempted to simplify its wording.


## Post-briefing addendum — the redundant distillation pass returned

Recorded here rather than silently folded in, because it corrects something I told you above.

**The fourth cycle was not wasted after all — it was harmful and then useful.** I re-dispatched a
distillation run I judged incomplete; it had in fact completed. That made a second writer active on
the same files while I was applying the first run's ops, which is backlog row **B-19** and a real
concurrency hazard rather than a wasted spawn.

**What I did with its ops.** Its `harness-code-reviewer` ops are **dropped, not applied**: both
lessons are already on disk under different wording (`G-15`, `O-05`), that file's Gotchas is at
15/15, and applying them as adds would have made 16 and failed the format check. Its
`harness-validator-lead` ops **are applied** — both are distinct from anything on disk, and that
file had room. `check-expertise.sh` exits 0 across all 15 files with counts held. The lead returned
this as a **blocking** question telling me to re-measure before applying anything, and it was right
to; I re-grepped every count rather than trusting either report.

**One retraction from that lead, which favours nobody.** It closed `harness-ui-reviewer` without a
spawn on the judgement that the candidate was already covered. That call was wrong in substance —
the entry now on disk (`G-08`) covers exactly the case it thought was covered elsewhere. Harm is
zero, because the original run had already spawned that reviewer and captured the op. Stated
because the record should show the call was wrong, not merely harmless.

**None of this changes the ship recommendation, any success criterion, or the gate.** No source file
moved; the six graded files are byte-identical to `review_sha`.
