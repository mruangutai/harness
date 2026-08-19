# Ship review — FEAT-27, the Expertise repository tier

**Recommendation: ship.** All seven tasks are built, every gate has passed, and all eleven success
criteria are met. The review panel returned `severity_max: med` with an empty `must_fix`, which is
advisory under `gates.review: advisory_unless_high` and does not block. Two things need your
decision before this closes, and neither is a defect in the code: a signature question, and the
disposition of the backlog below.

## What was wrong, and what is true now

Since 2026-08-14 the harness has told sixteen agents that repository-specific knowledge belongs at
`.harness/<repo>/expertise/<agent>.md`. Neither half of that was true. The spawn hook had no such
read path (#484), and `check-domain.sh --resolve` answered **NOBODY** for every agent's
repository-tier path (#372), so no agent could write the file the rule told it to write. During
FEAT-21 a distillation entry was returned unwritten for exactly that reason.

All three are now closed — #484, #372 and #412 — and the proof is not a test fixture. **At this
feature's own close-out the repository tier went from six files to 13**, seven of them created by
agents that had nowhere to put repository knowledge the day before. The mechanism was exercised by the org before
you were asked to accept it.

## The gates

| Gate | Result |
|---|---|
| `test_matrix` (the only blocking gate) | **PASS** — `matrix_ok: true` for all seven tasks |
| Review panel — four reviewers | **PASS**, `severity_max: med`, `must_fix: []` → advisory |
| Goal-check — SC-01 … SC-11 | **PASS**, all eleven met |
| Suites at the pin `9b929de` | unit exit 0, integration exit 0, zero `FAIL` lines |

**16 runs against an informational budget of 20, and three cycles of ten.** The three cycles were: one real fix (a hardcoded test fixture
went stale when sixteen grants were added), and two lead-reported send-backs inside the qa and panel
segments — both of which improved the result rather than repairing a mistake.

I re-measured the load-bearing claims myself rather than relaying them: both suites at the pin;
sixteen `--resolve` calls each returning the agent's own name with a `NOBODY` negative control;
all 15 craft and all 13 repository Expertise files each named `OK`; and the hook probed end to end
in a temp root, where two segments inject under scope-only headers, the precedence line appears
exactly once, and the 40- and 150-line truncation notices each name their own budget.

## What the process actually caught — the part worth reading

This feature's subject is test honesty, and the machinery turned that lens on itself.

**Six assertions in this repository could not fail.** Not six that were wrong — six that were green
and incapable of going red. Three were found by mutation, one by reading a neighbour of the code
under test, and none by any suite passing. A seventh was *refuted*: an assertion two squads had
condemned turned out to redden correctly against the mutant it actually exists to catch. Green under
an unrelated mutant is not vacuity, and that distinction is now written down.

**One falsehood survived a green gate four times.** `SPEC.md` claimed the global Expertise cap is
tighter than the project one; the code gives both 150, and SPEC's own table said so twelve lines
away. The task's `verify:` was a set of literal greps and passed over every instance, because all
four were paraphrases. Every one was found by a person reading the section.

**Two seam defects lived in the union of two reviewers' scopes** — each reviewer individually
correct. The authoring checker accepts a segment class the hook silently drops, so it can print `OK`
on a repository file the hook will never inject. And the audit loop this feature added crashes on a
dangling symlink, aborting its sweep under the same exit code it uses for "violations found" — while
this same feature taught another tool that dangling symlinks there are ordinary.

**A correction to my own record.** A claim that a weaker test assertion "would have passed the
mutant" propagated through three artifacts, including a commit message I wrote. Measurement showed
two assertions flip, not one. Three artifacts agreeing is not corroboration when all three inherited
it from one source. The commit stands; the correction is recorded rather than hidden.

## Two decisions that are yours

**1. The signature.** You adopted the `[ -r ]` guard criterion mid-flight and directed it as one
follow-up task this cycle, naming its lane, `change_type` and mechanism. I built it as T-07. But
`plan.yaml` was signed for six tasks and now holds seven, and its approval block carries one flat
`approved` with a single same-day date and no amendment field — so the artifact cannot evidence its
own amendment either way. `harness-spec-driven` requires approval to reset when the task set changes,
and product-lead flagged this as blocking *before* T-07 dispatched.

**I proceeded, and that was a judgement call, not a formality that was satisfied.** My reasoning: your
instruction was explicit and specific, `plan.yaml` read `approved` so the step-0 gate passed, and
blocking on a signature only you can write would have cost a round trip against an instruction
already given. If you disagree, the cost is one test case.

**2. The backlog below.** Anything you do not strike becomes an issue; anything not listed dies
silently, so it is all listed.

## Not committed, deliberately — needs you

**25 Expertise files carry uncommitted distillation output** (13 craft, 12 repository) and I
did not commit them to this branch. They fall outside every task's `files:` list except T-04's
migration, and committing them here would repeat FEAT-25's B-18. They are in the working tree for you
to land separately.

**One correction to my own record.** I told the validator squad that the three reviewers hold no
`Write`, repeating a phrase from the playbook without checking it. It is false: all three declare
`Write` and are granted **both** Expertise paths with `upsert: true`. Their fifteen ops were therefore
never stranded — they went back to their owners, who applied them themselves. That is also the safer
path, because the writer re-reads the file at write time and an operator applying later cannot.

**Final state of the corpus, measured after everything landed:** both tiers exit 0, fifteen craft and
thirteen repository files, and exactly the six `ADVISORY` lines the validator lead predicted in
advance — a seventh would have meant an entry drifted into the wrong tier. No file was wiped. One
reviewer re-ranked its own displacement after the lead challenged the reasoning, sparing an entry this
very feature had vindicated twice.

`harness-product-lead`'s six proposed ops remain **unapplied** — that tier holds no `Edit` on its own
Expertise file. They are in `runs/distill-product/digest.md` and are the one set that still needs a
hand.

## Proposed backlog

| ID | Finding | Nature |
|---|---|---|
| B-1 | `DEC-27` is falsified on two clauses by this feature's own code and carries no strike record, which DEC-188 requires. Not fixed here because `DECISIONS.md` is uncommitted under another flow | bug |
| B-2 | `check-state.sh:149`'s comment names an approval-reset rule neither `:133-139` nor `:150-154` implements — an amended-but-unsigned plan reports green. DEC-174 carve-out, human-only fix | bug |
| B-3 | `check-expertise.sh` accepts segment names (`[^/]+`) that `inject-expertise.sh` silently drops (`[a-z0-9-]+`) — the checker signs `OK` on a file the hook will never inject | bug |
| B-4 | `check-expertise.sh` crashes on a dangling `*.md` symlink and aborts the sweep, leaving later files unaudited under the same exit code as "violations found" | bug |
| B-5 | `cap_body`'s truncation notice is skipped exactly when truncation is silent — `wc -l` counts newlines, so a file with no trailing newline is undercounted | bug |
| B-6 | The precedence line is emitted only when a repository block exists, so a global+project spawn now gets two un-arbitrated blocks and no precedence statement — narrows the architecture review's unconditional resolution | bug |
| B-7 | SC-02 is pinned by nothing standing: T-01's `verify:` is one-shot and unregistered, and `test-check-domain.py` has zero repository-tier cases. Cheapest high-value fix | chore |
| B-8 | The global-tier branch at `inject-expertise.sh:98-101` is unreachable by any fixture. One new fixture also de-vacuates B-9 and makes B-6 testable | chore |
| B-9 | `case9a`'s ordering clause is vacuous — `all()` over an empty filtered list is True | chore |
| B-10 | `case2`'s ordering assertion cannot fail: bash glob expansion already returns collation order | chore |
| B-11 | `case12`'s four hostile `agent_type` values are vacuous — you declined this as Q5, recorded as agreed | chore |
| B-12 | `test-check-expertise.py` case2's `FEAT-\d+` sub-case cannot discriminate the new advisory from the pre-existing violation | chore |
| B-13 | `case11` asserts `"Traceback" not in stderr`, which misses shell-emitted noise; `stderr == ""` is the right remedy | chore |
| B-14 | `harness.json` detect globs are wrong both ways — `integration` names 4 of 12 scripts, `unit` matches all 29. Fixing them would flip T-03's unit kind to "missing" and FAIL the blocking gate; fix globs and registration together | chore |
| B-15 | `test-harness-yaml.py:186-187` and `harness_yaml.py:362` claim a "D-03 equivalence proof" against a `collect()` DEC-171 deleted, and claim coverage of every agent while pinning 6 of 16 | chore |
| B-16 | `harness-curate/SKILL.md:34`'s checklist says 150 lines where the same file audits the repository tier at 40 — it misinforms the distiller in the step that does the editing | chore |
| B-17 | `check-expertise.sh:62` cites a "CHANGE 1 note" that exists only in `plan.yaml` — a comment narrating the plan, not the code | chore |
| B-18 | `test-inject-expertise.py` labels four project-tier fixtures `GLOBAL BODY`, making an untested path read as covered | chore |
| B-19 | `test-check-expertise.py`'s `valid()` and `body_with_entry()` emit byte-identical skeletons | chore |
| B-20 | The manual sort at `inject-expertise.sh:82-92` duplicates bash glob ordering and no assertion pins it | chore |
| B-21 | `inject-expertise.sh:33`'s bare `$HOME` under `set -u` is the one hole in the hook's always-exit-0 contract (inherited, not this diff) | bug |
| B-22 | SPEC uses two tier vocabularies for the same objects — a two-way craft/repository split and a three-way global/project/repository one. Both true, jointly confusing | chore |
| B-23 | `.harness/README.md:27` names `feature.yaml`; all 29 features carry `feature.json` and none has ever carried the other | chore |
| B-24 | Entry ids are renumbered in the destination on migration, which no criterion checks and which dents DEC-66's stable-reference rationale. A constraint reading, so yours | enhancement |
| B-25 | D-01's residual: repository tiers multiply per-spawn context, worst case ~580 lines today, and neither the name regex nor the segment filter bounds the count. Signed, revisit at unit 7 | enhancement |
| B-26 | Concurrent distillation runs race on the shared corpus — one squad's gate read another squad's mid-write file and reported a FAIL on an agent it never touched (#560 materialising) | bug |
| B-27 | `SendMessage` is unavailable at the lead tier, so a lead cannot course-correct an in-flight member. Raised independently by three leads | bug |
| B-28 | `dispatch-guard.sh` blocked a `model:` parameter **six times** across three different leads in this one feature. A rule its own readers break repeatedly is a rule-text problem | chore |
| B-29 | Nothing asserts `review_sha` equals the branch tip (#487). It drifted here and was caught by a human, as on FEAT-25 | bug |
| B-31 | The orchestrator playbook says the write-less reviewers' ops are returned for the orchestrator to apply. All three reviewers hold `Write` and both Expertise grants, and the orchestrator can write no file but its own — the instruction is false in both halves | bug |
| B-32 | `harness-product-lead` holds no `Edit` on its own Expertise file, so a lead cannot self-distill; its six ops need another hand | bug |
| B-33 | Members size a distillation against the section caps (15/15/10/5), but the binding constraint on a loaded file is the 150-line FILE budget — `harness-orchestrator.md` sits at 144 with sections nowhere near full. The next distillation hits a checker FAIL at write time instead of a considered displacement | chore |
| B-34 | A lead recorded a calibration lesson against itself, and the same lead repeated the same two defects in the next round of the same job. Digest calibration notes are injected nowhere, so a lesson never reaches the agent that wrote it | enhancement |
| B-30 | FEAT-26, FEAT-28 and FEAT-29 carry unapproved BRIEFs in this shared checkout — not this feature's, surfaced because they appeared while it ran | chore |

## How this briefing was assembled

**No report round was spawned.** I read every run's digest from disk, including the plan phase I did
not run. Assembled from, all under
`.harness/harness/features/FEAT-27-expertise-repository-tier/runs/`:
`2026-08-18-1-product/digest.md` · `t02t03-eng/digest.md` · `qa-validator/digest.md` ·
`e1-judgment-product/digest.md` · `fixture-eng/digest.md` · `t05-q4-product/digest.md` ·
`t07-eng/digest.md` · `simplify-eng/digest.md` · `qa-final-validator/digest.md` ·
`specfix-product/digest.md` · `panel-validator/digest.md` · `goalcheck-product/digest.md` ·
`distill-eng/digest.md` · `distill-product/digest.md` · `distill-validator/digest.md`.

Ship-refresh was **skipped with reason**: `.harness/codebase/` does not exist, so there is no map to
intersect.

The branch is `feat/FEAT-27-expertise-repository-tier`; the panel and goal-check both graded
`9b929de`. PR, CI and merge are yours.
