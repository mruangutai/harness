# Ship review — FEAT-38, decisions as current knowledge

**The feature is built, both closable gates are green, and it is one thing away from a ship
decision: you.** All 28 planned tasks are done. The blocking qa gate passes. The review panel
passes with nothing above `low`. The goal-check grades **15 of 16 live criteria met**.

**The sixteenth is SC-13, and it is UNRUN — not failed.** `gates.uat` is
`blocking_when_uat_criteria_exist`, so the ship decision waits on you. It takes about 15 minutes.

**I also have to correct something I told you.** My previous state note asserted "SC-13 stands and
does not return to the operator". That was wrong, and it was my error — I restated my dispatch's
premise instead of checking it. `harness-pm` checked the file. `notes/uat-FEAT-38.md` reads
`status: ready` with all four `result:` fields blank. **No SC-13 judgement has ever been recorded.**

Your ruling 6 says SC-13 "STANDS and is not re-run". That is a ruling about not *re-running* a
judgement — and the record holds none to stand on. If you did read those three entries and simply
never wrote it down, say so and I will record it. If you did not, the script is ready.

## How this briefing was assembled

**No report round was spawned.** Per DEC-69 I read the digests already on disk rather than paying
for agents to re-narrate them. The sources:

- `runs/t27-product/digest.md`, `runs/2026-08-29-01-eng/digest.md`,
  `runs/t28-t29-product/digest.md`, `runs/2026-08-29-t25-eng/digest.md` — the five build tasks
- `runs/2026-08-29-qa-ship-validator/digest.md` and `notes/qa-ship-gate.md` — the blocking gate
- `runs/2026-08-29-simplify-ship-eng/digest.md` — the four-angle pass
- `runs/2026-08-29-18-panel-ship-validator/digest.md` and the four `notes/review-*-ship-panel.md`
- `runs/goalcheck-ship-product/digest.md` and `notes/research-FEAT-38-goalcheck-635cd3b.md`
- `runs/2026-08-30-uat-repoint-product/digest.md`
- `notes/ship-review-2026-08-29-18.md` — the previous briefing, for the standing backlog

**One gap you should know about.** The plan-phase digests predate me and I did not re-read them
wholesale; I took the earlier phases through the previous briefing, which synthesised them. Rows
B-1 through B-23 below are carried forward from it and I did **not** re-verify each one this phase.

## What landed

Five tasks remained at the third signature. They landed in dependency order, and I ran each task's
own `verify:` myself — extracted from the signed `plan.yaml` rather than retyped, so the gate text
cannot drift from what you signed.

| task | commit | what |
|---|---|---|
| T-27 | `0a94d91` | All eleven claim markers deleted from `DECISIONS.md`, across six entries |
| T-24 | `8c879f5` | Claims test deregistered from the runner and both claims files deleted, atomically |
| T-28, T-29 | `70690ea` | DEC-205's rule 2 removed and its three check-counting sentences repaired; the `bin/` argv-class audit written |
| T-25 | `8a7c75c` | Claims test deregistered from `harness.json`'s integration detect |
| qa + simplify | `635cd3b` | The blocking gate's evidence, and one dead-code apply |

`review_sha` is **`635cd3ba`**, pinned at the tip that contains the build and taken *after* simplify
so no apply commit could move the tip under the panel. The stale `48bbe7e` pin is gone.

## The gates

**qa — PASS, and it is the only blocking gate of the three.** `matrix_ok: true`, `must_fix: []`.
Suite exit 0, **zero** lines beginning `FAIL`, and all **55** registered scripts actually ran — I
checked the discovered set against the registered set, because a gate that discovers nothing passes
every check it has. qa recorded its own limits rather than smoothing them: the matrix owes `[]` over
the prose bulk of this diff, and the test-first audit is vacuously clean because four of five tasks
are docs or config and the fifth is a deletion.

**Review panel — PASS, `severity_max: low`, no `must_fix`.** `gates.review` is
`advisory_unless_high`, so it does not gate. The panel earned its run rather than stapling four
passes together: SC-11's meaning half had never been verified at reviewer tier, ten of its entries
having been carried forward on a byte-identity chain that T-27 and T-28 both cross. Every automated
criterion in this feature asserts *shape*, so a moved entry would have left the suite green. One
send-back closed it — ten byte-identical, changed set exactly the six expected entries.

**Goal-check — 15 of 16.** Every criterion graded by its own declared method, per-item where the
criterion quantifies over several. SC-09 and REQ-08 are retired tombstones and were graded by
nobody, as you ruled.

## Two things I verified myself rather than take on report

**The retained anchor checker is untouched, and it can still go red.** Ruling 2 asked for
byte-identity, so I asserted it directly instead of inferring it from a green suite:
`check-decision-anchors.py` and `test-check-decision-anchors.py` are byte-identical to
`git show 99bb52c:` and are named by both registration sides. qa honestly flagged that nobody had
shown the remaining guards still discriminate, so I probed it: against an unmodified copy the
checker exits 0 over 20 anchors; with one fabricated anchor planted it exits 1 and names the line.
The probe ran on a `/tmp` copy, so the tree was never perturbed.

**T-27 did not touch prose, so ruling 6's void condition did not fire.** The prose line sequences
either side of T-27 are identical — 5067 lines each, 20 lines removed being 11 markers and 9 blank
lines, zero insertions. I had to redo this measurement grep-free: this machine's `/usr/bin/grep` is
`pi-uu-grep 0.2.0`, in which the pattern for a line-leading `+` matches **every** line, and it first
reported 83 insertions against a true `--numstat` of zero.

## What SC-13 actually asks of you, and how little has moved

SC-13 asks you to read the folded **DEC-138, DEC-174 and DEC-181** and judge whether each reads as a
decision stating current truth rather than merged history, and whether any claim you consider
settled has silently disappeared.

I measured what changed in those three entries between the old pin and the live one:

| entry | at `48bbe7e` | at `635cd3ba` | change |
|---|---|---|---|
| DEC-138 | 128 lines | 128 lines | **byte-identical** |
| DEC-174 | 122 lines | 122 lines | **byte-identical** |
| DEC-181 | 51 lines | 46 lines | 3 claim markers and 2 blank lines removed; **zero prose, zero additions** |

So the subject matter is materially unchanged. The script was pinned at the stale `48bbe7e` and
stated DEC-181 as 51 lines; presenting it that way would have had you grade a revision that no
longer exists, so I had it repointed at `635cd3ba` as a fix cycle. `status:` is still `ready` and
all four `result:` fields are still blank — only you set those, and no agent may mark a criterion
met.

## The one substantive review finding

The panel found `board_lifecycle.py` citing `DEC-203` for a rule the decision record never made:
`Abandoned` occurs once in the whole authority and `GhError` occurs **zero** times, yet three of the
five citation sites rest on it. It is `low` and does not gate.

It is worth naming for what it is: **an instance of exactly the class this feature accepted losing
detection for.** A citation that resolves and no longer says what the citing code claims. It was
caught by a human reading a diff, which is precisely the compensating control the brief names. The
trade is working as you signed it.

## Budget

**Cycles: 16 of 30.** Two rework cycles — the panel's SC-11 seam send-back, and the UAT repoint.
Every other run this phase returned PASS on its first pass, and DEC-157 counts rework only.

**Runs: 34 against an informational `max_total_runs` of 20**, crossed long before this phase. The
count notices a long feature and stops nothing. My read: these runs earn their place. Nine runs
closed the entire remaining build, both gates, the goal-check and the UAT repoint, with two cycles
of rework between them, and the panel's one send-back closed a real verification gap that every
automated gate in the feature would have passed over.

## The self-hosting carve-out

T-24 and T-25 change the test runner's own registration, which sits close to DEC-174's line. The
signed plan routes both as `team`, so I did not override your signature — I removed the circularity
from the **verification** instead. Every mechanical gate over those two tasks was run by me
directly rather than accepted from the squad, I read both diffs myself, and the byte-identity of the
retained pair was asserted with `shasum` against `git show 99bb52c:` rather than inferred from the
suite the change edits. That is "ordinary edits, tests run explicitly, a human reading the diff" as
far as it goes inside a signed team execution.

## Proposed backlog

One row per residual finding that does not gate. **Strike any row you do not want; anything not
listed here dies silently, so everything is listed.** B-1 to B-23 keep the previous briefing's
numbering; I did not re-verify them this phase. Your earlier ruling already settled four: **B-8 and
B-11 moot, B-10 superseded, B-9 absorbed into the plan as T-29.**

| ID | nature | finding |
|---|---|---|
| B-1 | bug | Amend the three unsatisfiable `verify:` blocks (T-10, T-15, T-19). Replacement text ready in `notes/research-verify-block-defects.md`. Needs your signature. Carried forward, not re-checked this phase |
| B-2 | bug | Host defect: the edit/write tool family resolves worktree-relative paths against the MAIN checkout. **Recurred three more times this phase** — see B-35 |
| B-3 | bug | Host defect: a member returned an empty structured result and the `SubagentStop` validator did not block it |
| B-4 | chore | A T-06 member ran `git checkout --` on the main checkout for two generator files. Both confirmed back at committed content |
| B-5 | chore | Resolved previously; retained for numbering |
| B-6 | bug | `DEC-162` presents the removed codebase-map tier as current. Pre-existing, outside this feature's scope |
| B-7 | bug | `SPEC.md` contradicts itself on org depth: team-shape prose uses pre-DEC-120 layer numbers, §10.2 uses the cap of 3 |
| B-8 | — | **Struck by your ruling: moot** |
| B-9 | — | **Struck by your ruling: absorbed into the plan as T-29** |
| B-10 | — | **Struck by your ruling: superseded** |
| B-11 | — | **Struck by your ruling: moot** |
| B-12 | chore | SC-04 has no automated gate over `.harness/harness/docs/` |
| B-13 | chore | `test_kinds.unit.detect`'s catch-all and `integration.detect`'s explicit paths both match the three logic test files |
| B-14 | chore | One unexplained transient in `test-gen-decisions-index.py`; not reproduced in 7 subsequent runs |
| B-15 | chore | `run-unit-tests.sh`'s `PASS` total is ambiguous across the conventions different scripts use. **Bit me again**: a script-level count read 1001 where the true figure is 55. Worth one normalized aggregate line |
| B-16 | bug | `plan-merge.py` is add-only (exit 7 on a changed value), so a task `status:` transition has **no route through it**, and it exits 8 creating a plan that carries an approval mapping. **Confirmed live this phase** — I had to write every status flip with a line-addressed `sed` |
| B-17 | chore | The plan's T-05 intent maps `DEC-137 → DEC-162` as a successor that carries its glossary half. It does not |
| B-18 | chore | `docs` and `config` floor at zero required test kinds, so most tasks carried no required test |
| B-19 | bug | `render-brief.py:131` strips HTML comments across the whole document before fenced-block handling, so a code block containing one renders empty. **I wrote this briefing around the defect rather than into it** |
| B-20 | bug | `render-brief.py:36,:53` — `--quiet` on `--paper` is ~3.39:1 against WCAG AA's 4.5:1 in light mode |
| B-21 | chore | The joint citation `(DEC-100, DEC-120)` in three agent/skill files is imprecise |
| B-22 | enhancement | Nothing pins `DEC-N` citations in `.claude/**` against future rot |
| B-23 | bug | A member reported `SC-13` as `not_met` where its own evidence said "unrun by design". A `not_met` on a `verify: uat` criterion misroutes a ship gate as a build failure |
| B-24 | bug | **New, and it destroyed a record.** A lead wrote its run into `runs/2026-08-29-01-product`, already the panel-revision run's directory, overwriting that run's `digest.md` and `state.yaml`. `runs/` is gitignored, so it was never in git and is unrecoverable. I relocated the new artifacts to `runs/t27-product/` and left a tombstone. Nothing in the run-directory contract stops a lead choosing a slug that already exists |
| B-25 | bug | **New.** `bash-write-guard.sh` cannot expand shell variables and does not track `cd`: it resolves write targets against the session root. `cd <dir> && sed -i '' … plan.yaml` and `sed -i '' … "$P"` were both denied "outside your domain" while the identical command with a literal absolute path was allowed — and `check-domain.sh --resolve` grants `plan.yaml` to `harness-orchestrator`. The two surfaces disagree, which the guard's own comments call a bypass by construction |
| B-26 | bug | **New, and it is the most dangerous thing I hit.** `/usr/bin/grep` here is `pi-uu-grep 0.2.0`, not GNU grep. The pattern for a line-leading `+` matches **every** line. It produced four false readings this phase, including an apparent 83 insertions against a true `--numstat` of 0, and a script count of 1001 against a true 55. Any gate or agent counting diff or suite lines with shell grep on this machine is unreliable |
| B-27 | chore | **New.** `check-decision-anchors.py`'s docstring still calls the snippet problem "the executable-claims checker's job (a different tool)" — false now that the tool is deleted. Pre-existing, not introduced, and **SC-18 structurally forbids fixing it in this feature** because it pins that file byte-identical to `99bb52c` |
| B-28 | enhancement | **New.** DEC-205 names two refused rot detectors but never names what compensates today. The real answer — human review, non-standing, scoped to this change — lives only in `BRIEF.md`, a per-feature artifact rather than the living authority. The remedy would add positive content to DEC-205, which your ruling forbids, so it is yours to authorise or decline |
| B-29 | enhancement | **New, and it is REQ-10's residual.** The `bin/` argv class is **not empty**: 11 of 70 scripts build an argv value from a parsed input, recorded as remaining work in two risk groups in `notes/research-FEAT-38-bin-argv-class-audit.md`. The panel re-derived 18 rows and confirmed all 11 labels correct. Backlog under REQ-10's reconciliation with the grilling note's destination — this feature is a step toward that end state, not the state reached |
| B-30 | chore | **New.** `gen-decisions-index.py:156-167` — `strip_trailing_clauses` returns a boolean both consumers discard. Present identically before this feature, so not its residue; the stripping itself is load-bearing and only the boolean is dead |
| B-31 | bug | **New.** `board_lifecycle.py` cites `DEC-203` for a rule the authority never made; `GhError` occurs zero times in it. Three of five citation sites rest on it |
| B-32 | enhancement | **New.** `check-state.sh:1633` builds a `gh` argv from `harness.json`'s `github.repo`. Out of REQ-10's conditioned scope by the brief's own wording, so dispatching it would widen a signed requirement |
| B-33 | chore | **New.** SC-04's pinned baseline of `37` for the amendment pattern does not reproduce (34 occurrences / 31 lines) while its `30` and `24` reproduce exactly. Every pattern is 0 at the pin, so intent is met; the recorded figure is what is off |
| B-34 | chore | **New.** Test-runner-registration edits classified `change_type: logic` trigger a `unit` floor this repo's forking bash runner makes structurally unreachable. Whether such edits should be `config`, or a change type added, is yours — it signs `test_matrix` |
| B-35 | chore | **New, and it is live dirt in your main checkout.** Two panel artifacts, `review-harness-code-reviewer-ship-panel.md` and `review-harness-ui-reviewer-ship-panel.md`, were written into the MAIN checkout under `.harness/harness/features/FEAT-38-decisions-current-knowledge/notes/` and are untracked there now. I copied byte-identical versions into the worktree so the feature record is complete, and **left the originals alone** — the main checkout is not mine to alter, especially with FEAT-45 being planned in it |
| B-36 | chore | **New.** `gh-sync.py` puts `BRIEF.md` prose into `gh issue create` argv. One test case — a title with a leading dash — would pin it. A ticket for that script's owner, not a task here |
| B-37 | chore | **New.** The audit's provenance filter excludes "git output" but is silent on the captured stdout of a sibling harness script, which is why `test-check-state.py` scored `TEXT-DERIVED-ARGV` on the strict reading. Worth one clarifying sentence before the next sweep |
| B-38 | enhancement | **New.** `test_kinds.<kind>.cmd` holds a whole command line in configuration with **no executor anywhere under `bin/`** — its executor is an agent or a CI step. Whether that is acceptable is yours |

## What I need from you

1. **Run the UAT** — `notes/uat-FEAT-38.md`, repointed at `635cd3ba` and operator-ready, about 15
   minutes. Set `status:` to `passed` or `failed` and leave your `result:` text. **Or**, if you
   already made that judgement and never recorded it, tell me and I will record it. This is the last
   thing between the feature and a ship decision, and no agent may close it.
2. **Strike any backlog row you do not want.** Unstruck rows become issues on ship acceptance.
3. **Non-blocking, still open from the plan phase:** Q6 to Q10, which gate nothing. Q7 is B-28.

I have not created a pull request, merged anything, or moved a card to Done. The board is at Review.
