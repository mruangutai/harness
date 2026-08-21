# Ship review — FEAT-30-worktree-per-feature — build phase

**One decision is blocking everything, and it is one line.** Everything else in this document is
context for it.

**No report round was spawned.** This is assembled from disk plus my own measurements. Cited:
`runs/2026-08-20-01-build-eng/digest.md` and `state.yaml`; the six receipts
`notes/receipt-harness-dev-ops-build-eng-{T-01,T-02,T-02-c2,T-08,T-10}.md` and
`notes/receipt-harness-backend-dev-build-eng-T-06.md`; my own
`notes/orchestrator-M17-build-baseline-exact.md`, `M18-runner-exits-2-until-T-08.md`,
`M19-DEC-193-falsified-by-this-feature.md`, `M20-signed-intent-vs-existing-invariant.md`;
`notes/layer0-segments-FEAT-30.md`; `notes/handoff-plan.md`. Spawning three leads to re-narrate files
I can open buys nothing.

---

## The decision I need from you (Q1)

`test-harness-yaml.py` asserts that exactly one guarded import exists in `bin/`, against a hardcoded
allowed set of three files. `feature-worktree.py` is a fourth — **because T-01's signed intent
required it**: *"import harness_boundary lazily and, if the import fails, exit 2 with a message
naming the module."* The member did exactly that.

So the approved plan and an existing invariant test contradict each other, and **nothing in the plan
owns the reconciliation**:

| Option | Cost |
|---|---|
| **A — add `feature-worktree.py` to the allowed set** | Edits a file in no task's `files:`. One line. |
| **B — drop the guard from `feature-worktree.py`** | In scope (T-01's own file), breaks no test, but departs from a signed instruction: an unguarded import exits 1 with a traceback, not `exit 2`. |

**My recommendation: A.** Three reasons, each checked. `check-domain.sh` is *already* in the allowed
set for guarding `import feature_schema` — a first-party sibling, exactly like `harness_boundary` — so
"it is not an external dependency" does not distinguish this case from one already accepted. The test's
own comment says assertion 2 *"MUST be a subset, never =="* precisely so new legitimate cases can land.
And the signed D-12 yaml rule (assertion 1) is untouched either way, since this file imports no yaml.

I also measured what makes B cheap, in fairness to it: **nothing tests the guarded branch.** The only
`returncode == 2` assertion in T-01's suite is for an undeclared `--repo`. So the `exit 2` requirement
is asserted nowhere and the branch is unreachable in practice. If you judge the clean exit incidental,
B costs less. **I would not treat `exit 2` as load-bearing without evidence, and there is none.**

**One failing assertion, 18 `ok` lines. Either option restores green in one line.**

---

## Status: what is built, and why nothing is committed

All five team-lane tasks are built. `cycles_used` **7 of 13**, six remaining. Runs 7 of 20.

| Task | Verdict | Substance (I reviewed the code, not just the verdict) |
|---|---|---|
| T-01 | PASS | CLI create/list/path + isolation suite. SC-02 asserted via `merge-base` against the pre-create tip, not a branch name. |
| T-02 | PASS, 1 cycle | `remove` with three ordered gates. Prints `WOULD DISCARD <path>` and `MISSING/DIFFERS/VERIFIED <path>` **per path with content hashes** — never a bare count, exactly as SC-04 and SC-07 demand. |
| T-06 | PASS, 1 cycle | `expertise-merge.py`: union apply under an exclusive lock. Two genuinely concurrent `Popen` writers, asserted **by named entry**, admitting only union-or-locked, any third outcome reported by name. |
| T-08 | **FAIL** | Registrations correct and minimal (`INTEGRATION_SCRIPTS` 12→14; one line in `harness.json`). Red **only** on the out-of-scope collision above. |
| T-10 | PASS | SC-01b case A and the shared-checkout negative. |

**Why no commit.** `gates.qa_gate` is blocking, the integration suite is red, and **SC-09 is violated
right now** — a test that passed at `49c528a` fails at HEAD. Committing that would ship a red suite
and a false record. The work sits in the tree; six files, nothing staged. I also did **not** mark any
task `done` in `plan.yaml` and ran no `close-task`, because nothing has landed and recording
otherwise would falsify the board.

**Growth is real, not silent.** Baseline at `49c528a`: unit exit 0 / 179 PASS / 0 FAIL; integration
exit 0 / 90 PASS / 0 FAIL. Now: unit exit 0 / 179 / 0 (unchanged, correct); integration exit 1 / 212
PASS / 2 FAIL. The +122 decomposes as 74 (T-01/T-02) + 32 (T-06) + 14 (T-10) + 2 runner lines. Both
suites are genuinely discovered and executed. The 2 FAIL lines are one defect reported twice — the
assertion plus its script summary — and no third ever appeared.

---

## Where the delivered feature is weakest — plainly

**1. Two instances of one shape: correct code, untested rationale.** T-01's red proof reddens at the
*fixture guard*, so SC-01's static isolation assertions are green **without ever having been shown able
to go red**. And `list` filters by `commonpath` exactly as its intent demands — but no
`worktrees-old` sibling case asserts it, so a refactor to `startswith` would pass the whole suite.
Neither breaks any task's `verify:`, so neither became a cycle at six remaining. A mutation pass, not
a reading pass, is what closes them.

**2. The near-miss that matters most, and the squad caught it, not me.** T-10's shared-checkout
negative satisfied itself via the committer-failure path **~13 consecutive times without ever calling
the isolation predicate** — that is failure mode 3 from R-02's own list, *not* the documented flake I
warned it about. It fixed the gap and then got 8/8 clean red proofs. Had it retried past that as
"the known flake", SC-01b would have shipped green and incapable of red. **Three tiers under-counted
this feature's blast radius by reading; again, only mutation found the truth.**

**3. Both plan-text defects trace to one design choice.** T-01 imports a sibling module. That was
required and it is good design. Consequence one: the guarded form trips the anti-fallback cap (Q1).
Consequence two: T-10's `verify:` copies a single file, which cannot import that sibling and dies with
`ModuleNotFoundError` **before any assertion, on the pristine file** — verified by inspection, no
`sys.path` manipulation exists. The member re-expressed it as `cp -R` matching T-06's proven pattern
and disclosed it. **`plan.yaml`'s recorded verify is still broken and needs pm's one-line fix**, or
every future re-verification of T-10 fails spuriously (Q3).

**4. I cannot verify any red proof myself.** Every one begins by copying `bin/` to a temp directory,
and the write guard blocks the orchestrator's `cp` there as out-of-domain. Red-proof claims are
unverifiable at layer 1 **by construction** — which is why I demanded actual command output rather
than assertions of success.

**What I did verify independently:** the CLI against the real repository —
`feature-worktree.py list --repo harness` returns `FEAT-31 feat/FEAT-31-orchestrator-context-watch
<abs path>`, exit 0, correctly including the legacy one-segment worktree and correctly excluding the
main checkout. Fixtures cannot give that.

---

## Q2 is settled — the lead could not run the check, I could

The lead flagged an unsettled contradiction: `cp -R … "$T/bin"`, the first line of five verify blocks
including **T-03's, T-04's and T-05's**, was green for one spawn and denied for another. Both halves
are true. The guard genuinely does not expand `$T` — it printed the literal `$T/bin` when it denied me.
But `bash-write-guard.sh:49-57` exits early for **no `agent_type`** and for **`harness-dev-ops`**, so
some callers never reach that check. Four consistent data points: T-02's spawn was dev-ops (green),
T-06's was backend-dev (denied), I am orchestrator (denied), and the operator carries no `agent_type`.

**The discriminator is who ran it, not what was run — and your lane exits first.** T-03, T-04 and T-05
will run literally as written. No re-expression needed.

---

## Your five tasks, unchanged and unblocked by Q1

`notes/layer0-segments-FEAT-30.md` is the work order: **T-03 → T-04 → T-05**, plus T-07 (any time) and
T-09 (last). It carries the measured warnings, chiefly: a **fail-open window until T-04 lands** —
`harness_boundary.py:37` and `check-domain.sh:644` both hard-code one path segment while the CLI writes
two, so **do not create a real feature worktree with the new CLI until T-04 lands**; T-04's line anchors
re-verified live; a **positional** assertion in `harness/SKILL.md` T-09 can break by insertion alone;
and start from my commit, not `49c528a`, since T-07's verify runs a T-06 file.

## Proposed backlog

| ID | Finding | Nature |
|---|---|---|
| B-1 | `test_kinds.integration.detect` names 4 scripts while the runner runs 12. The qa gate confirms coverage from those globs, so **T-04 is set up for a false "integration missing" FAIL** on a correctly-tested change. Wording to hand the grader is in M-17. | bug |
| B-2 | This feature **falsifies DEC-193**: it states code lives at `.claude/worktrees/<id>/`, the delivered layout is `<repo>/<id>`. No task touches docs and nothing detects a falsified decision. Recommend an **am.3 after T-04 lands**, routed to `harness-documentor` — a team lane, not your hands. | chore |
| B-3 | `feature.json` rejects a `phase:` key as undeclared, while the orchestrator playbook (DEC-148/159) instructs writing one. One of the two is wrong. | bug |
| B-4 | `test-check-domain.py` and `test-bash-write-guard.py` give a **false red from the wrong cwd** (13/14 and 25/27 from `bin/`, 14/14 and 27/27 from the root). T-03/T-04/T-05 all modify them. | enhancement |
| B-5 | D-01 names three CLI subcommands; T-01's intent specifies a fourth (`path`) and four were built. Intent is the executable spec, so delivery is right and the decision text is stale. | chore |
| B-6 | SC-06 is named by no task, though T-09's `verify:` implements its assertion verbatim. | chore |
| B-7 | `expertise-merge.py`'s exit-6 lock-held branch never fired in a real race (20/20 landed the union); covered only by a direct lock-file test. Coverage asymmetry, not a defect. | chore |
| B-8 | `factory_config.workspace_path()`'s docstring enumerates its callers and claims sole ownership; T-01 adds one and `harness_boundary.py` was already uncited, but that file is in no task's `files:`, so the enumeration goes stale. | chore |
| B-9 | A task-notification fired for a member that then continued and notified again with different figures. The lead treated the first as terminal and sent a send-back, briefly putting two writers on one file. No damage, but **a lead cannot distinguish "stopped" from "paused"** and the serialization rule assumes it can. | bug |
| B-10 | The orchestrator cannot re-run any red proof in this plan (every one copies `bin/` to temp; the guard denies it). Red-proof verification is structurally impossible at layer 1. | enhancement |

## What I did not do

No PR, no merge, no review panel, no goal-check, no simplify, no commit. The panel and goal-check
belong after your five tasks: T-04 and T-05 carry the highest-risk surfaces, five of the twelve
criteria (SC-02b, SC-02c, SC-03, SC-05, SC-06) cannot be graded until they land, and a panel on a
half-diff would be invalidated the moment they did.
