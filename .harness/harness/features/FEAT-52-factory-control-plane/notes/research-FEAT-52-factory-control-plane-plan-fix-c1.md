# Plan fix cycle 1 — every cycle-0 finding closed, and the H1 ruling

**All eight cycle-0 findings are closed. None declined.** After the cycle-1 send-back (G-1, below)
the plan is **20 tasks, 8 decisions, 6 REQ, 14 SC**.
`safe_load` parses, `check-plan-routes.py` exits 0 with 0 violations, traceability holds both ways,
no cycles, every `verify:` is a literal block. Contract B held throughout: **no existing id was
edited** — every amendment arrived as a new id whose `intent:` first line names the clause it
supersedes.

## H1 — the ruling, and what it cost to get right

**Ruled: two anchors, one injected (D-06).** `<HARNESS_CONTROL_PLANE_ROOT>` prefixes every READ and
is injected by the hook. `<HARNESS_FEATURE_TREE_ROOT>` prefixes every WRITE into a feature directory
and is **not** injected — the agent resolves it once, from the FEAT id DEC-204 puts on the first
line of its own dispatch, with a new verb `inflight_registry.py feature-root --feature <FEAT>`.

The resolution is not new. `inflight_registry.feature_root` (`inflight_registry.py:260-266`) already
returns `worktree_for_feature(owner_root, feature) or owner_root`, and `dispatch-guard.sh:115-126`
already resolves a dispatch's checkout by the identical rule. **That fallback is exactly the factory
case**: a product feature has no Harness worktree, so the resolver collapses to the control plane —
which is what #356 comment 1 ruled. For Harness self-development it returns the feature worktree.
One rule, correct in both directions. T-10 adds one CLI branch over a shipped function.

**The loser, recorded in D-06's `because:` and again in T-16's DEC entry: a second INJECTED value.**
It is unbuildable without inventing mechanism. `dispatch-guard.sh:76-80` records the measurement
that `tool_input.prompt` "exists only on the DISPATCH payload… and reaches no other hook", and
DEC-64 fixes the SubagentStart payload's contract at `agent_type`. The hook therefore cannot know
which feature a spawn belongs to. Resolving it hook-side would mean scanning the inflight registry
of the control plane and of every linked worktree for a claim keyed on **persona alone** — ambiguous
whenever two spawns of one non-single-flight persona run on different features at once — plus an
unmeasured dependency on `PreToolUse:Task` firing before `SubagentStart`. The agent already holds
its FEAT id with certainty, because `dispatch-guard.sh` fails **closed** without it.

Carried by: **REQ-06**, **D-06**, **SC-11** (instruction form) and **SC-10** (runtime resolution),
**T-10**, **T-11 clause 2**, **T-12** (supersedes T-02's receipt clause), **T-13** (supersedes
T-04's F3/F4 clauses), **T-14 clause 2**, **T-16**.

**Two SCs, because the ruling fails in two different places.** SC-10 goes red when the *resolver*
answers with the control plane for a feature held elsewhere — it asserts the printed value DIFFERS
from the owner root, which is the assertion the drafted plan never had. SC-11 goes red when an
*instruction* anchors a feature-directory path to the control plane, and T-11 clause 2 makes that a
first-class VIOLATION class with its own fixture. An SC asserting only "the write path is anchored"
would pass on the exact defect; neither of these does.

**L3 folded in here.** SC-01 now requires the asserted case to run with cwd set to a directory that
is NOT the resolved root and to assert the two differ; T-09 clause 1 carries it into T-01's first
test case, naming that case as what it corrects.

## H2 — the lint's blind spot

T-11 clause 1 supersedes T-03's THE RULE clause: a violation is now a matching path token inside an
inline backtick span **or on any line inside a fenced code block** (three-or-more backticks or
tildes, closed by at least as many of the same character; inside a fence the token is delimited by
whitespace or quotes, never by backticks). Clause 5 supersedes T-03's RED PROOF: the negative
fixture now holds **two** paths on two known lines, one inline and one fenced, and asserts both line
numbers and a summary of 2. Both halves, as required — SC-05 amended to match.

## The five others

| Finding | Closed by | Substance |
|---|---|---|
| M1 | D-07, SC-12, T-09 clause 2 | The spawn-time half now asserts the **path contract**. The hook invokes `check-instruction-paths.py` over the four files every agent receives — its own `.omp/agents/<agent_type>.md` plus the three always-preloaded skills — and emits `HARNESS_PATH_DRIFT: none` / `<n> unanchored path(s)` with up to five `file:line` pointers. Exit 0 on **every** branch, including checker exit 1, exit 2, and absent, so `DECISIONS.md:1503` and the seventeen exit-0 cases hold. RED is asserted: one fixture clean, the same fixture with one relative span, naming file AND line. |
| M2 | T-11 clause 3, T-14 clause 1, T-17, SC-03/SC-04 site S5 | `.claude/skills/harness/templates/*.md` joins the declared scope; T-14 anchors all seven template files; S5 (`templates/PLAN.md`) is a sixth per-site assertion. |
| M3 | SC-08, T-15 | T-07's three assertions are refactored into one path-taking function and fed **two mutants** — step deleted, and step present with its failure branch removed — because those two halves fail independently. The SC-05 treatment, as asked. |
| L1 | SC-02 | The clause now has an assertion: grep the shipped script for `^[[:space:]]*exit [1-9]`, assert zero matches, **and** assert the same pattern DOES match a one-line `exit 2` fixture. Without the positive control an erroring search reads as an absence. |
| L2 | BRIEF `S1-S5`, T-11 clause 4 | One canonical list, in BRIEF, used by name everywhere. F2 and F3 share a file, so the five families give four distinct sites; S5 is the fifth. T-11 clause 4 supersedes T-03's list, which had substituted `harness-tdd-enforcement`. |
| L3 | SC-01, T-09 clause 1 | Above. |

## Ordering, because three gates read the same surfaces mid-flight

`T-10` is a leaf. `T-12`/`T-13` correct the two write families **before** `T-11` introduces the rule
that forbids the control-plane spelling for them, and `T-14` anchors the templates **before** `T-11`
widens the scope to that directory — so `T-11`'s whole-scope verify is the first point it can be
green, and it is green. `T-09` depends on `T-11` because it invokes the finished checker. `T-15` and
`T-16` are last. No cycle; `T-07`'s CI job never sees a widened scope with an unswept directory.

## What I could NOT do, and why it is not a plan defect

- **`lanes:` is unamendable.** It is a non-union top-level key: any differing value is `MergeRefusal(7)`
  (`plan-merge.py:616-626`). The four new surfaces — `inflight_registry.py`,
  `test-inflight-registry.py`, `templates/*.md` — therefore have no `lanes:` row. Each carries its
  lane in its own `execution_mode` + `execution_reason`, which is what `check-plan-routes.py`
  actually reads, and it exits 0. Raised as a non-blocking open question.
- **The `approval:` block is still absent.** Untouched, per dispatch: a harness enforcement-layer
  defect already routed to the operator.

## One inaccuracy I introduced and then corrected in the same cycle

T-14 clause 1 says README rows 8-16 carry "nine control-plane paths". Measured at `e8e1b78b`:
**eight** spans match the checker's rule; the ninth backticked path on those rows is `.gitignore`,
which the rule does not match. Contract B forbids editing T-14, so **T-17** supersedes that one
sentence, and does more than correct a number — it pins the direction split of all eight spans
(three reads, five feature-directory writes) so the doer does not infer it, and warns off the
left-hand column of bare template filenames, which are names and not paths.

## Open questions

- **Q1 (non-blocking)** — `lanes:` cannot be amended by any `plan-merge.py` verb, so a plan that
  grows a surface after its first write can never record that surface's lane. Either `lanes` needs a
  splice verb like `set-task-station`, or the block needs to become a union key. Today the route
  check reads task fields, so nothing is unenforced; the `lanes:` block is simply incomplete by
  construction on any amended plan.
- **Q2 (non-blocking)** — `harness-pm` has no writable non-`.md` staging path inside a feature
  directory, so a `plan-merge.py` proposal must either go through a bash heredoc or be staged in a
  `notes/research-*.md` file. The heredoc route is unusable: `bash-write-guard.sh` reads a `>`
  followed by whitespace anywhere in the command text as a redirect, and the placeholder spellings
  this feature is about (`<HARNESS_CONTROL_PLANE_ROOT> is …`) trip it. A grant for
  `notes/proposal-*.yaml`, or a `--proposal-stdin-file` seam, would remove the workaround.
- **Q3 (non-blocking)** — D-06 assumes every persona that writes a feature-directory artifact can
  run one Bash command to resolve its anchor. That holds for the reviewers today (they run
  `git show`), but nothing asserts it. If a future persona loses Bash, its writes lose their anchor
  silently.
  **WITHDRAWN at cycle 1 — see `## G-1` above.** The premise was wrong in tense, not only
  understated: three personas hold no Bash today. Replaced by D-08, SC-13, SC-14, T-18, T-19, T-20.
- **Q4 (non-blocking)** — `dispatch-guard.sh:115-126` resolves a dispatch's checkout by basename
  **equality**, while `harness_boundary.worktree_for_feature:193-229` resolves by **prefix** and
  refuses on ambiguity. For a prefix-named worktree the recorded claim and the feature-tree write
  anchor land in different checkouts. T-18 enforces against the prefix resolver, so the
  disagreement becomes a loud refusal rather than a silent split; reconciling `_root_for` itself
  is a separate change and is not in this feature.

## G-1 — the no-Bash personas

**Confirmed as measured, closed, not declined. Q3 is withdrawn and replaced.** Its framing
("if a FUTURE persona loses Bash") was wrong in tense: three personas hold no shell today, by
design, and all three write into a feature directory as normal operation.

Measured at HEAD in this worktree: `harness-product-lead.md:4-9`, `harness-eng-lead.md:4-9`,
`harness-validator-lead.md:4-9` grant `read, glob, grep, task, write` — no `bash`. The other
thirteen personas all grant it (`^- bash$` matches 13 of 16 `.omp/agents/*.md`). The three
write `runs/<date>-<seq>-<squad>/state.yaml` (`harness-team/SKILL.md:44-47`) and
`<run_dir>/digest.md` (`:49-52`, `:209-210`, reported as `artifact:` at `:249`) — spans inside
T-06's file list and named by T-14 clause 2 (`runs/`).

**Ruled — D-08, extending D-06, superseding nothing in it.** The anchor is resolved by whoever
holds the shell. A persona with no `bash` never resolves its own: its **dispatcher** resolves it
(every such persona is spawned by a tier that does hold `bash`) and passes it as a line
`HARNESS-FEATURE-TREE-ROOT: /absolute/path`. `dispatch-guard.sh` — the one hook that can see a
dispatch prompt (`:76-80`) and already fails closed on a missing declaration (`:96-103`) —
refuses at exit 2 when the **dispatched** persona grants no `bash` and the line is absent, or is
present and disagrees with `inflight_registry.feature_root` for the declared feature. **The
predicate is the tool grant, never a name list**, so a future persona is covered on the day it
loses the shell.

**The losers, all in D-08's `because:`.** Grant leads `bash` — rejected, DEC-116 removes it
deliberately and re-granting it to fix a resolution defect is the error shape D-05 already
refuses. A second injected value — rejected, D-06's measurement is unreversed and nothing about a
shell-less target changes what `SubagentStart` can see (DEC-64). A hand-executed no-shell route
— a lead *can* glob `.git/worktrees/*/gitdir` and prefix-match, but that is
`harness_boundary.linked_worktrees:157-182` and `worktree_for_feature:193-229` (prefix-not-
equality at `:203-209`, `AmbiguousWorktree`, realpath) reimplemented as prose, so two
implementations of one resolver diverge silently. Instruction-only — kept as the agent-side half,
rejected as the whole remedy: it leaves only an SC that asserts a rule is written down. A guard
that *rewrites* the dispatch — rejected as unmeasured; nothing here records that a `PreToolUse`
hook can mutate `tool_input`.

**Lands as:** REQ-06 amended (BRIEF, direct edit), a DEC-116 `BLOCKS` constraint added, **D-08**,
**SC-13** (automated, `integration` — `test-dispatch-guard.py` is in `INTEGRATION_SCRIPTS`, so
the kind is the one that actually runs its assertions), **SC-14** (inspection, four per-file
findings), **T-18** (the guard block plus four cases, two of them discriminating in the *other*
direction), **T-19** (the four skills; supersedes T-12's second addition bullet), **T-20** (the
four agent definitions; adds to T-13). T-14 and T-12 could not be edited under Contract B —
T-19 carries the harness-team and harness-handoff wording, T-20 the agent definitions.

SC-13 discriminates in both directions on purpose: the `harness-backend-dev` case with the same
omission must exit **0**, without which a guard that refuses everything passes the first
assertion.

**One divergence found and NOT fixed here, deliberately out of scope.** `dispatch-guard.sh`'s
own `_root_for` (`:115-126`) matches a worktree by **basename equality**, while
`harness_boundary.worktree_for_feature:193-229` matches by **prefix** and refuses on ambiguity.
For a prefix-named worktree the claim root and the feature-tree anchor therefore disagree. T-18
enforces against `inflight_registry.feature_root`, the resolver of record after T-10, so the
divergence becomes loud rather than silent — but reconciling `_root_for` itself is a separate
change with its own blast radius. Raised as Q4.
