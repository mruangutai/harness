# FEAT-55 — native issue types on created work: build review

**FEAT-55 is not ready to ship, and it is closer than that sounds.** Nine of twelve tasks are
complete and verified. The other three are written, and I have measured that a **single missing
line-pair in one file** is the only thing stopping them. Two decisions are yours, and one thing this
feature cannot get for itself: a GitHub repository that actually has Issue Types turned on.

I also have to report that the **cycle budget is spent** — 11 against a limit of 10 — so I stopped
rather than push on. You declined a raise before the build opened, and I am not treating that as
stale.

## What you need to decide

### F-01 — one file nobody was told to edit (blocking)

`feature-schema.json` locks feature.json's `github` and `factory` objects shut
(`additionalProperties: false`) and declares no `typed` property in either. Approved decision D-20
requires a `typed` mapping in **both**. So the first save that carries one is rejected:

> `MergeRefusal(11): undeclared key 'typed' at /factory`

**No task in the signed plan edits that file.** I re-read all twelve `files:` lists. This is a plan
gap, not a coding mistake — the three affected tasks (T-04, T-06, T-08) are written correctly and
their authors proved them green under a temporary override.

I did not take that on trust. I added the two property declarations myself, re-ran everything
affected, then removed them and confirmed the file was byte-identical again. **All five suites went
green**, including two pre-existing factory suites that are red today:

| suite | now | with the two declarations |
|---|---|---|
| test-factory-decompose.py | FAIL | pass |
| test-factory-integration.py | FAIL | pass |
| test-gh-issue-types.py | FAIL | pass |
| test-factory-issue-types.py | FAIL | pass |
| test-gh-backlog-issue-types.py | FAIL | pass |

So this is genuinely the whole blocker; nothing is hiding behind it. Note the first two: **the
feature currently breaks two existing test suites**, same root cause.

**What I need:** permission to add `typed` to those two objects. Either pm adds the file to T-04's
and T-08's `files:` lists, or you have the main session do it directly. The file is already inside
the engineers' write domain — only plan authority is missing.

### F-02 — a query that would be dead on arrival (blocking, and nothing is red)

This is the one I would most regret shipping, because **every test passes on it.**

The plan asks for a capability query on every `gh-sync open`, and separately pins an existing test
that says *every* call must carry `--repo <repo>`. Those cannot both hold: **`gh api` has no
`--repo` flag.** I ran it on this machine, gh 2.92.0:

> `gh api graphql --repo … ` → `unknown flag: --repo`

The author, told the existing test must stay green and unedited, satisfied it by appending
`--repo` to the query anyway. It passes because the test double accepts any flag. Against real
GitHub it fails every time. The live probe from T-10 issues the same query *without* `--repo` and
gets a correct answer, which is what tells us which side is wrong.

**My recommendation:** drop `--repo` from the query, and widen that one assertion to accept an
`api graphql` line carrying `-f owner=` and `-f name=`. That keeps exactly what the assertion was
protecting — every call targets the intended repository rather than whichever one you happen to be
standing in — because `-f owner`/`-f name` is the only way gh lets you pin a graphql query. Nothing
is weakened.

This one is a re-plan, not a fix: the plan asks for something impossible, and only you can change
that.

### F-03 — the live probe has nowhere to run (external)

Success criterion SC-10 wants a verdict from a repository that actually declares Issue Types. The
probe works — it ran cleanly and reported **CAPABILITY ABSENT** for `mruangutai/harness`, which is
the correct answer for a repo without them. But a correct "absent" is not the live pass SC-10 asks
for. **We need either an Issue-Type-enabled repository to point it at, or your decision to accept
SC-10 on the absent-path evidence.** No amount of further work here can produce this.

## Where the work stands

| | |
|---|---|
| Complete and verified | T-01, T-02, T-03, T-05, T-07, T-09, T-10, T-11, T-12 |
| Written, cannot be verified | T-04, T-06, T-08 — all three behind F-01 |
| Committed at | `ef591a53` on `feat/issue-1289-issue-types` |
| Cycles | **11 of 10 — spent** |
| Runs | 32 of 20 — over the informational budget |

The two documentation halves landed in the required order (T-11 then T-12), and the drift guard
that protects them is green: the 394-character row is present in both files and identical. I
checked that at source rather than believing the report.

On the runs count: it is high for one reason, unchanged since the plan phase — this plan was signed
through five rounds of rulings instead of one. The runs themselves were efficient; this session's
two runs covered eleven tasks between them.

**Quality gates not yet run:** QA, the review panel, SIMPLIFY and the goal-check all sit after the
build completes. I did not run them, because a blocking gate that fails for a reason nobody is
allowed to fix teaches us nothing.

## How I assembled this

**I spawned no reporting round.** I read the run digests off disk:

- `runs/2026-09-05-01-eng/digest.md` — the engineering build, ten tasks
- `runs/2026-09-05-01-product/digest.md` — the documentation task
- the plan-phase record in `STATE.md` and `plan.yaml`'s `panel:` block

Every measurement in F-01, F-02 and F-03 above is one I took myself in this checkout, not a claim
relayed from a digest.

## Escalations resolved without you

Two send-backs, both inside engineering, both reported honestly by the lead and both its own cost:
T-03 and T-05 shared a test-double logging quirk that appended an invisible character to every
logged line, so their label assertions could never pass. Fixed at source. Those two send-backs are
what took the cycle count from 9 to 11.

## Proposed backlog

Anything you do not strike becomes an issue. Anything not on this list is forgotten.

| ID | Nature | What |
|---|---|---|
| B-1 | chore | Seven of the eight read-back rows are duplicated across two files with no drift protection; only the eighth (this feature's) is guarded |
| B-2 | chore | T-06's backlog receipt is flat on disk, while the plan's prose describes it nested under `items`. Behaviour is unaffected; ratify one or the other |
| B-3 | bug | The shell write guard blocked `cp` onto a protected file but allowed `python3 -c` to write the identical path in the same call — it reads command names, not what actually writes |
| B-4 | bug | `set-task-station` cannot record any task station on this plan (the tasks carry no status key and it only edits an existing one), and misreports the cause by naming the task it just called absent |
| B-5 | bug | A truncated capture of the unit suite showed zero failures while the suite had actually failed four files — captured output cannot be read for absence of failure |
| B-6 | bug | An agent's edit resolved a relative path against its process directory instead of its assigned worktree, briefly writing into the main checkout. It caught and reverted this itself |
| B-7 | bug | `validate-digest.py` rejects a plan-phase review's `code_grade: n_a`, the exact value the plan-phase panel is supposed to use |
| B-8 | bug | A run digest cannot be repaired in place, so every malformed first write permanently costs a second run directory |
| B-9 | chore | The plan-writing verb list omits `amend`, which every revision after the first needs |
| B-10 | chore | `amend --key` accepts only tasks and decisions, so a disposition edit inside the panel block has no route |

## What happens next

Rule F-01 and F-02 and the three blocked tasks verify immediately — I measured that. Then QA,
SIMPLIFY, the review panel and the goal-check run in order. SC-10 stays open until F-03 has an
answer. **None of that can start without a cycle-budget decision**, since the budget is spent and
the bound is a hard one.
