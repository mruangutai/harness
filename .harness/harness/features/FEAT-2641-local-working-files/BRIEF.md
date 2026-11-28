# BRIEF — FEAT-2641 feature working files stay local

## Problem

Every feature commits its working files: `notes/` (research, reviews, answers, receipts,
handoffs, prototypes and their screenshots), `runs/` and `observations/`. Since FEAT-71
(2026-10-08) `main` gained 5,376 git objects over 116 squash-merged PRs, about half of them
notes and runs; Kaya prototype PNGs alone are 12 MiB, a quarter of main's blob bytes. Deleting a
record later never shrinks history; only not committing it does. They are committed because CI
gates read them (INV-17, INV-40(c), INV-43, INV-47, the run-record invariants, ship's
`notes/handoff-validate.md` refusal), yet the operator's ruling is that notes exist only for
distill and expertise and need not be committed or shipped in any artifact. At `e2bffca0` the
tree tracks 2,750 such files (1,954 notes, 750 runs, 46 observations), and nothing cleans the
local copies when a feature finishes.

## Done when — by perspective

**operator** — No feature's notes (prototypes and screenshots included), runs or observations,
and no project note under `.harness/notes/`, is ever committed or carried in a pull request; the
ones already tracked leave the tree without history being rewritten. My local disk is cleaned for
me when a feature distills or ends by abandon or reject, or when I decline its distill, and
nothing deletes a project note no feature claimed. A worktree is never removed while its feature
still has working files on disk.

**code maintainer** — No CI gate reads a working file: the invariants and the ship refusal that
did are deleted with their tests, not stubbed or skipped. One routine owns working-file cleanup
and every terminal path calls it. The decision record states the new rule as current truth.

**orchestrator** — The flow still runs end to end on local disk: write-time and yield-time checks
that read notes, receipts and run records while work happens keep refusing exactly as before, a
distill whose receipts were never committed replays and merges, and ship no longer depends on a
note the main checkout cannot see.

## KPIs

| KPI | Baseline | Target |
|---|---|---|
| Tracked files under feature `notes/`, `runs/`, `observations/` and `.harness/notes/` | 2,750 (`git ls-tree -r e2bffca0`) | 0 at the pin and on `main` after merge |

## Success criteria

- SC-01 (operator): A committed guard test reads `git ls-files` and finds no tracked path under `.harness/*/features/*/notes/`, `.harness/*/features/*/runs/`, `.harness/*/features/*/observations/` or `.harness/notes/`, and `git check-ignore` reports a probe path in each of the four classes as ignored, including `notes/prototypes/<FEAT>/shot.png` and `notes/mockups/shot.png`; qa shows the test red at the base `e2bffca0` (2,750 tracked working files there) before green at the pin.
  verify: automated
  evidence: unit
- SC-02 (operator): History is not rewritten: the base `e2bffca0` is an ancestor of the pin (`git merge-base --is-ancestor e2bffca0 <review_sha>` exits 0), and `.harness/harness/features/FEAT-2581-feature-record-package/notes/answers-2026-11-27-signature.md`, tracked at the base and untracked at the pin, still reads through `git show e2bffca0:<that path>`; the reviewer cites both commands and their exit status.
  verify: inspection
- SC-03 (operator): `merge-gitignore.py` appends the four working-file directory rules to a project `.gitignore` that lacks them, `--check` reports each missing rule without writing, and normal mode removes the run rules Harness once shipped (`.harness/*/features/*/runs/*/ui/**`, `.harness/*/features/*/runs/**`, `.harness/features/*/runs/**`) while every unrelated byte stays unchanged.
  verify: automated
  evidence: integration
- SC-04 (code maintainer): `check-state.py --list` names INV-8, INV-12, INV-15, INV-16, INV-17, INV-18, INV-36, INV-43, INV-46, INV-47 and INV-51 only as retired, INV-40 no longer grades handoff succession, and INV-7 grades only the cycle arithmetic; `check-state.py --feature` on a fixture feature at station `review` whose `feature.json` records eng and validate runs but which has no `notes/`, `runs/` or `observations/` directory prints no VIOLATION, shown red at the base first.
  verify: automated
  evidence: integration
- SC-05 (orchestrator): `gh-sync.py ship` reads no `notes/` file: a feature with no `notes/` directory whose `feature.json` records a validator-squad validate or fix run at PASS passes the validation precondition, and one with no such run, not built entirely main-session-direct, is refused before any GitHub write; qa shows the first case refused at the base.
  verify: automated
  evidence: integration
- SC-06 (operator): `gh-sync.py abandon --yes`, and `gh-sync.py reject --yes` with a numeric successor, delete the feature's `notes/`, `runs/` and `observations/` and each `.harness/notes/` path its `feature.json` `project_notes` lists, only after they record the station; without `--yes` they list those paths and delete nothing; a project note not listed survives; a refused station write deletes nothing. `gh-sync.py reject --superseded-by none`, whose caller records the station, deletes nothing with or without `--yes`, never previews a removal, and names the `feature-worktree.py clean` command.
  verify: automated
  evidence: integration
- SC-07 (operator): `merge-gate.py merge-distill` deletes the same set after the merge succeeds and reports each deleted path; any refusal before the merge deletes nothing.
  verify: automated
  evidence: integration
- SC-08 (operator): `feature-worktree.py clean --repo <repo> --id <FEAT> --yes` deletes the same set when either the landed record (the owner checkout's `plan.yaml`) or the worktree's `plan.yaml` reads `done`, `abandoned` or `rejected` — including owner `done` with worktree `review` — and refuses, deleting nothing, when neither does; it refuses, deleting nothing, when a listed project note is a directory; without `--yes` it lists the paths and deletes nothing.
  verify: automated
  evidence: integration
- SC-09 (operator): `feature-worktree.py remove` refuses with exit 4, removing nothing, while the feature directory holds untracked files under `notes/`, `runs/` or `observations/`, naming each of those directories with its file count (no per-file line) and the `clean` command, and removes the worktree once they are gone; `post-merge-sweep.py` leaves such a worktree in place.
  verify: automated
  evidence: integration
- SC-10 (orchestrator): A distill whose expertise receipts and run records exist only on local disk replays and merges: `expertise-merge.py replay --check` reads every receipt in the feature's local `notes/` with no base-tree exclusion; `git add -A -- .harness` stages the Expertise file and `feature.json` (the distill runs' committed ledger) and no `notes/`, `runs/` or `observations/` path; `merge-distill` refuses while that `feature.json` change is uncommitted and merges once it is committed and the committed Expertise equals the replay.
  verify: automated
  evidence: integration
- SC-11 (orchestrator): `feature-record.py project-note` adds a `.harness/notes/<name>` path to `feature.json` `project_notes` idempotently and refuses, writing nothing, an absolute path, a traversal, a nested path or any path outside `.harness/notes/`; `validate-feature-json.py` accepts a record carrying the key.
  verify: automated
  evidence: unit
- SC-12 (orchestrator): The runtime checks that read local disk while work happens are unchanged: `tests/integration/test-check-domain-post.py`, `tests/integration/test-check-domain-approval.py` and `tests/integration/test-validate-digest-shadows.py` are byte-identical to the base and pass at the pin (handoff shape at write, dev receipt and inspection citations at yield).
  verify: automated
  evidence: integration
- SC-13 (orchestrator): `tests/unit/test-handoff-done-when.py` is byte-identical to the base and passes at the pin, and `test_run_start_after_a_handoff_owes_a_succession_and_refuses_without_one` and `test_run_start_with_succession_reason_lands_run_and_judgement_in_one_write` in `tests/unit/test-feature-record.py` are unchanged and pass (run-start's succession refusal reads the local handoff).
  verify: automated
  evidence: unit
- SC-14 (code maintainer): Read at the pin with `git show <review_sha>:<path>`, `prune-run-evidence.py`, `tests/unit/test-prune-run-evidence.py`, `check_state/seams.py`, `check_state/run_state.py`, `tests/integration/test-check-state-handoff.py` and `tests/integration/test-check-state-inv51.py` are absent, and `git grep <review_sha>` finds no live reference to `prune-run-evidence` or to an instruction that commits or force-adds a note, run record, receipt or observation log under `.claude/`, `.omp/`, `.github/` or `.harness/README.md`.
  verify: inspection
- SC-15 (code maintainer): Read at the pin with `git show <review_sha>:.harness/harness/docs/DECISIONS.md`, a new entry states the local-working-files rule, DEC-257 carries a strike record naming it, every amend row in `plan.yaml` `decisions_affected` reads as current truth, and `gen-decisions-index.py --stdout` equals the committed `DECISIONS-INDEX.md`; the reviewer cites the lines.
  verify: inspection
- SC-16 (orchestrator): Read at the pin, the distillation reference ends with the cleanup step, commits the reconstructed Expertise with `feature.json` and no receipt or run record, and routes a distill that changed no Expertise to `feature-worktree.py clean`; the reject procedure tells the caller of `--superseded-by none` to run `feature-worktree.py clean` only after recording `rejected`; the orchestrator playbook records owned project notes with `feature-record.py project-note`, `.omp/commands/harness.md` names `feature-worktree.py clean` for a declined distill, and `harness-ship.md` no longer prunes run evidence; the reviewer cites file and line.
  verify: inspection
- SC-17 (operator): When the station or merge landed but working-file cleanup then fails, `gh-sync.py abandon`, `gh-sync.py reject` and `merge-gate.py merge-distill` exit 4, naming what landed, each path already removed, and the `feature-worktree.py clean` command to retry cleanup alone, and tell the operator not to re-run the terminal command; proven by in-process faults at the cleanup seam, with no GitHub write repeated.
  verify: automated
  evidence: unit

## Verification gaps

- none for runners: `unit` and `integration` are active with commands, and no SC rests on a null
  or excluded kind. `typecheck` is not touched (no TypeScript changes).
- Not proven by any test: the deletion of tracked working files from other checkouts' disks when
  they pull the merged `main` (git removes a file whose tracking a pulled commit deletes). That is
  git's documented behaviour, disclosed under Constraints, not a criterion.
- `handoff_comprehension` (locally run) is not run: the handoff contract (shape, sections, cap) is
  unchanged; only the CI re-check of persisted notes goes.

## Constraints

- BLOCKS — DEC-174: every task changes a gate, hook, validator, their tests, or the record and
  instructions describing that change, so every task is `main-session-direct`; none runs through
  a team, and none executes through the enforcement it changes.
- BLOCKS — DEC-188 and DEC-205: DEC-257 is flatly contradicted and is struck with a strike record;
  softer changes (DEC-44, DEC-46, DEC-130, DEC-131, DEC-150, DEC-154, DEC-156, DEC-157, DEC-159,
  DEC-160, DEC-191, DEC-203, DEC-208, DEC-215, DEC-230, DEC-237, DEC-238, DEC-252, DEC-253, DEC-255)
  are amended in place;
  `DECISIONS-INDEX.md` is regenerated.
- BLOCKS — DEC-232: plan anchors are `path`, `path#symbol` or `{path, quote}`.
- SUPPLIES — DEC-112: `merge-gitignore.py` is the one route that ships ignore rules to a checkout.
- SUPPLIES — DEC-191: `feature.json` keys are schema-declared; `project_notes` is added there.
- SUPPLIES — DEC-253: receipt replay and serialized `merge-distill` stay; only where receipts live
  changes.
- KEPT, not removed (operator): runtime checks reading local disk while work happens —
  check-domain's handoff shape gate, validate-digest's receipt and citation checks, expertise
  receipt verification, `feature-record.py run-start`'s succession refusal.
- Disclosure: when this lands and a checkout pulls `main`, git deletes from that checkout's disk
  every working file this feature untracks; each stays readable through `git show <sha>:<path>`.
  A feature shipped but not yet distilled at that moment loses its observation logs from disk
  (open question OQ-02).
- Disclosure: an in-flight branch still tracking its own working files turns the guard test red
  when it merges `main`; its repair is `git rm -r --cached --sparse` on those paths (OQ-03).

## Out of scope

- Rewriting `main`'s history to drop what is already committed — it changes every SHA and breaks
  cited SHAs and every clone (operator agreed).
- `core.abbrev` or any git-config workaround for hash length (operator agreed).

## Approval

status: pending
approved-by:
date:
