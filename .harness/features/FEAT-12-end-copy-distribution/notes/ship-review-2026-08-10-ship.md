# FEAT-12 — end the copy-based distribution — ship review

**Recommendation: ship it, after you do two things only you can do.** Run the UAT, and rule on one
evidence gap that can never now be closed. Everything else is done, committed and gated.

The harness no longer distributes itself by copying. `deploy.sh`, `/harness-deploy` and the
machine-wide registry are gone. `kaya-ai` has been stripped of its copy and that deletion is pushed
to its `master`. A product repository now reaches harness tooling by being checked out by the
factory, declared in `.harness/factory/fleet.yaml`, which kaya is now in.

**Branch `chore/203-end-copy-distribution`. I pushed nothing and opened no PR — the merge is yours.**
Stated precisely, because "not pushed" would be false about the branch: it already has an origin
counterpart at `275de45`, pushed by the main session, and that remote copy carries four of this
feature's commits. I am 6 ahead of it and ran no `git push` at any point.
One commit went to another repository: `7d2f946` on `mruangutai/kaya-ai` `master`, which you
authorized.

---

## The two things that need you

**1. Run the UAT — SC-06, and it is a blocking gate.** Script at
`notes/uat-FEAT-12-sc06.md`. A fresh factory checkout of `kaya-ai` at `master` must execute a Bash
call, a Write and **a Task spawn** with no missing-hook error. The Task spawn is the one that
matters: kaya's `settings.json` wired eight harness registrations across four hook events, and four
of them are the ones a Task spawn fires. No runner in this repository can observe another
repository, so this was never automatable.

**2. Rule on SC-05.** The criterion says kaya's `.harness/` is byte-identical across the removal —
same file count, same per-file sha256. **The manifests that were meant to prove it contain no
hashes.** They are 377 identical paths and zero sha256 fields. The plan asked for
`xargs -0 shasum -a 256`; what ran produced a path list. The before-state no longer exists, so
re-running the capture yields two after-captures and proves nothing.

The review panel raised this as its only `high` and asked the one question that could still settle
it. I ran it rather than passing it up:

| Question | Answer, measured at `fb80543` |
|---|---|
| Is kaya's `.harness/` tracked in git? | **Yes — 117 files** |
| Did the deletion commit touch anything under it? | **No. The pathspec held** |
| Is kaya's `.harness/` clean now? | One modified file, `features/FEAT-03-live-review-loop/feature.yaml` |
| When was that file modified? | **2026-08-07 19:57** — three days before this feature ran |

So content integrity is **strongly evidenced by git for the 117 tracked paths** and **not evidenced
for the 260 untracked ones** (`.DS_Store`, artifacts, feature dirs). That is much better than the
panel had and still weaker than the criterion claims. Your options are to accept path-set equality
with the weakening recorded, or to restate the criterion. I have not marked SC-05 either way.

**One record correction rides with this.** Commit `f3452bf`'s body says the re-capture was
"IDENTICAL, byte for byte". The artifact does not support that phrase. It stands as written and is
corrected here rather than rewritten.

---

## Where the goal stands

**Nine of eleven success criteria met.** SC-01, SC-02, SC-02b, SC-03, SC-04, SC-07, SC-08, SC-09 and
SC-10 are verified by their own declared methods. SC-05 is partial, SC-06 awaits your run.

Gates: **qa gate PASS** — `matrix_ok: true`, the project's only blocking gate. Full suite exit 0, 23
test scripts, 0 failures. **Review panel FAIL on the one `high` above**, everything else advisory.
**UAT outstanding and blocking.**

`test-no-distribution.py` is new and is the standing gate on all of this: 18 assertions, each case
pairing an absence with a presence, and every case was proven able to go red by perturbation before
it landed. Two of its judgments were settled by qa with mutants rather than by reading.

---

## What I would want you to know that no gate reports

**Every gate on this feature searched for tokens. Nothing checked whether the replacement prose was
true.** Three false statements were written during this feature and all three passed every sweep;
each was caught by a human-style read. The sharpest: a member proved in its own research that
`factory_config.py` is not the fleet declaration's only reader, then wrote that exact falsehood into
`README.md` in a stronger form. Its lead caught it. The approved plan had told it to write that
sentence.

That defect class survives this feature. It is the single most consequential thing in this review.

**Two verifies in the approved plan were themselves broken.** T-06's calls a function with the wrong
number of arguments and raises regardless of outcome. T-14's presence clause matched a different
section of the same file, so it passed while gating nothing — which is how T-14 came back green with
its success criterion unmet. I caught the second by reading and spent one fix cycle on it.

---

## Cost and shape

Sixteen runs against an informational budget of 20, so no long-feature note fires, and 8 of 10
cycles. Two of those cycles were rework I would spend again: one where a documentor wrote a claim
its own research had disproved, one where a task passed its own verify with SC-08 still unmet.
Nine of the fourteen tasks were lane-locked to you and executed by the main session, and a
main-session segment is never recorded as a run — so sixteen is a floor, not the real step count.

**No report round was spawned for this briefing** — it is assembled from the digests on disk:
`runs/2026-08-10-01-product/digest.md`, `-02-product`, `-03-product`, `runs/t07-t10-eng/digest.md`,
`runs/t12-product/digest.md`, `runs/t14-product/digest.md`, `runs/t14fix-product/digest.md`,
`runs/t13-eng/digest.md`, `runs/qagate-validator/digest.md`, `runs/panel-validator/digest.md`,
`runs/goalcheck-product/digest.md`, `runs/distill-eng`, `distill-product`, `distill-validator`,
`distill-apply-validator`, `distill-apply-eng`. Ship-refresh was skipped because this repository has
no `.harness/codebase/` map to refresh.

Expertise changed in eight files, 139 entries to 160, applied by their owners.
`check-expertise.sh` reports OK on all thirteen files, and the three reviewer files plus qa took
insertions only — checked per file, not from the aggregate diffstat.

---

## Proposed backlog

Strike any row by name. Anything not listed here dies silently.

| ID | Nature | What |
|---|---|---|
| B-1 | bug | Nothing in the tree gates prose truth. Three false statements passed every sweep this feature |
| B-2 | chore | Plan T-06's `verify:` calls `repo_entry(name)` against a `repo_entry(fleet, name)` signature — raises regardless of outcome |
| B-3 | chore | BRIEF SC-02 and plan T-09 cite "case 20"; the fixture is `case_21`. Claim true, label wrong, in two signed documents |
| B-4 | chore | Plan T-14's `depends_on` omits T-08, which measurably blocked it |
| B-5 | bug | `docs/harness/BUILD.md:826` still reads `Enroll = deploy + /harness-init` — a backtick breaks the phrase pattern, so it evaded both T-12's and T-14's verify |
| B-6 | chore | `BUILD.md:829` and `DECISIONS.md:3945` cite DEC-113 for rulings it no longer carries |
| B-7 | bug | DEC-13's heading and body still describe deploy pushing templates. Falsified, one decision over from the two this feature struck |
| B-8 | bug | `SPEC.md:1925` still reads "rides the existing skill distribution" — no sweep here covered the bare word |
| B-9 | chore | `SPEC.md:419-421` illustrates the fleet-config claim with three scripts and omits `factory_claim.py` |
| B-10 | bug | The absence idiom `test "$(git grep … \| wc -l)" = 0` passes when the search itself errors. It shipped in four of this plan's verify strings |
| B-11 | bug | `git grep -E` does not honour `\b`, so a word-boundary sweep matches nothing and asserts nothing |
| B-12 | bug | `harness.json`'s `test_kinds.integration.detect` can never match the two files that actually run under `--kind integration` |
| B-13 | bug | `gh-sync.py open` created parent issue #223 instead of adopting #203. On ship acceptance #223 closes and **#203 — the issue you watch — stays open** |
| B-14 | bug | The orchestrator cannot apply another agent's Expertise ops (exit 2), which is the path its own playbook prescribes. Reviewers hold `Write` and self-apply |
| B-15 | bug | `check-expertise.sh` does not bind an entry's ID letter to its section, nor detect duplicate or skipped IDs |
| B-16 | bug | The instruction-shaped-pattern guard mangles any return that merely names `.claude/settings.json`, twice this feature |
| B-17 | bug | A `plan.yaml` plain scalar carrying a space-then-`#NN` truncates silently under `safe_load` while the route check exits 0 |
| B-18 | enhancement | kaya became fleet-reachable in the same range that stripped its guards. No task, criterion or gate records re-wiring as a precondition |
| B-19 | chore | SC-03's two clauses and SC-08's "retains only" clause have no standing assertion — both held at this sha by inspection alone |
| B-20 | chore | T-10's comment edits in `test-check-plan-routes.py` have no standing test; that file is `ALLOW_LIST`-exempt |
| B-21 | bug | `upgrade-config.py`'s no-templates message gives no remedy and is false for the repos the tool targets. Candidate to fold into #206 |

Already filed, listed so you can see the whole set: **#218** (qa cannot write test files here),
**#241** (`rm -f` bypassed the write guard), **#242** (`templates/team-config.yaml` does not parse).
