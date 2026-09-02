# FEAT-48 — ship review at `review_sha 27f8105b`

## The decision you have to make

**The feature is finished and its ten success criteria are met. One question stands between it and
the ship, and it is a scope question, not an engineering one.**

A test that the suite itself runs can plant a file under the watched `bin/` directory and hide it
from the mutation check — permanently, deterministically, in one pass — by creating a directory,
writing into it, and then removing that directory's execute bit. I reproduced this myself through
the real CLI. `run_pool.py --mutation-check` exits **0**, prints no `MUTATED` line, and the payload
is still on disk afterwards. The identical scenario **without** the `chmod` is caught cleanly
(`MUTATED .tmp_cache/backdoor.py`, exit 1), so the detector works; it is blinded, not broken.

**The three facts that decide it:**

1. **No approved success criterion fails.** SC-10 names three mutation vectors, two refusal cases
   and one `__pycache__` clause; all six pass. All ten SCs are MET at the pin, independently
   confirmed by pm (`notes/research-FEAT-48-goalcheck-validate-c9.md`).
2. **It is not a regression from this cycle's fix.** I ran the same reproduction against
   `run_pool.py` at `b86ce66a` (the original build commit), `e64e863e` (the c8 pin) and `27f8105b`.
   **All three: exit 0, no `MUTATED`.** The `except OSError` that swallows it has been on the file
   loop since the feature's first commit; `993ac997` only extended the same guard to the
   directory-symlink branch, which is what the c8 review asked for.
3. **Nobody in the org may fix it.** `.claude/skills/harness/bin/**` is `main-session-direct` by
   the DEC-174 policy carve-out (`plan.yaml:15-23`). There is no lead I can route it to. It is
   yours either way — as a fix before ship, or as an accepted, recorded limit.

**My recommendation: ship, and take it as a backlog row (B-1), with B-2 done in the same act.**
The actor is a test that deliberately hides its own writes. Anything that can do that already runs
arbitrary code as your user inside the suite and could equally edit `bin/` before the pool starts,
or edit the checker. This detector's job is to catch *accidental* shared-tree mutation — the
`.mutant-*.sh` class the feature actually removed — and it does that. What I would not ship
unchanged is the **claim**: `plan.yaml` D-11 says "Inside DIR it is vector-agnostic", and that
sentence is now measurably false. This feature's own doctrine is that an overclaim is worse than a
gap, and D-11's `because` block says so in as many words.

**If you would rather close it**, the remedy is small and local: `_record` should swallow only
`FileNotFoundError`, not every `OSError`, so a `PermissionError` on an entry `os.walk` just proved
exists becomes a hard failure rather than a silent drop. That is a one-line change plus a test leg,
inside a file only you may edit, and it would need a re-pin and a re-run of this validation.

## How this briefing was assembled

**No report round was spawned.** I read the run digests and member artifacts off disk, as DEC-69
requires, and I re-took every mechanical measurement myself rather than accepting it on report:

- `notes/validate-evidence-c9.md` — my own measurements at the pin
- `runs/2026-09-02-c9-validator/digest.md`, `runs/2026-09-02-c9-product/digest.md`
- `notes/review-harness-code-reviewer-c9.md`, `notes/review-harness-security-reviewer-c9.md`,
  `notes/review-harness-ui-reviewer-c9.md`, `notes/qa-c9.md`
- `notes/research-FEAT-48-goalcheck-validate-c9.md`
- carried from the prior cycle: `notes/handoff-validate.md`, `notes/qa-c8.md`,
  `notes/research-FEAT-48-goalcheck-validate-c8.md`

## What the squads returned

| squad | verdict | in one line |
|---|---|---|
| validator (panel) | **ESCALATE** | c8's two `must_fix` are genuinely closed and no criterion fails; the panel split on how to rate the chmod blinding, and its lead ruled `med` while its security reviewer ruled `high` |
| — code reviewer | PASS | both c8 items closed case-by-case with no assertion dropped; `code_grade` clean; one `med` plan-text mismatch |
| — security reviewer | FAIL | the chmod blinding, reproduced end to end; `severity_max: high` |
| — qa | PASS | matrix satisfied on `unit` + `integration`, both green at the pin; every dispatched case discriminates under a fault it built itself |
| — ui reviewer | PASS | all five terminal-output surfaces legible and attributable; two carried-forward `low` gaps |
| product (goal-check) | **PASS** | all ten SCs MET at `27f8105b`, every row re-taken at the pin |

## What is now proven, that was not before

- **`code_grade` is clean.** `code-grade.py --base origin/main --head 27f8105b` → exit 0,
  `PASSING: 70`, **zero** blocking records. c8's nine records, three of them `high`, are gone at
  source: `run_self_tests` went from CYC 14 / COG 29 / ABC 49.7 to **3 / 0 / 6.5**. That was the
  first of c8's two `must_fix`.
- **The lstat crash is fixed, and the fix is live code.** Both the directory-symlink branch and the
  file branch now route through the guarded `_record`. With the guard bypassed, the same injected
  failure escapes in **both** branches — so the guard is doing work, not decorating. That was the
  second `must_fix`.
- **All six in-file self-tests discriminate.** The file was rewritten wholesale in `993ac997`, so
  the c8 proof did not carry and I re-took it: three monkeypatch probes redden all six between
  them, and **no case is ever-green**. CI gates them unconditionally.
- **SC-03's amended shape holds on both halves.** In CI: root printed and correct, `discovered 63`
  against a floor of 50, zero live findings. At review time: the three pinned `ea6f51f` blobs are
  scanned and **all ten named sites are found individually, with zero extras.**
- **The `__pycache__` boundary is now exactly what SC-10 licenses.** A rewritten *and* a newly
  created `__pycache__` entry are ignored; a loose `.pyc` outside `__pycache__` is reported.
- **The suite is green at the pin:** exit 0, 63 files, 8 workers, 48.29s wall, zero `FAIL`, zero
  `MUTATED`, working tree clean before and after.

## Proposed backlog

Unstruck rows become backlog issues on ship acceptance. **Anything you strike dies silently, so
strike deliberately.**

| ID | nature | row |
|---|---|---|
| B-1 | bug | `run_pool.py:29-34` — `_record` swallows every `OSError`, so an entry under a directory whose execute bit was removed is omitted from **both** snapshots and never compared. Remedy: swallow only `FileNotFoundError`. Present since `b86ce66a`; this is the row the decision above turns on |
| B-2 | chore | `plan.yaml` D-11's "Inside DIR it is vector-agnostic" and DEC-211's coverage paragraph name four uncovered classes and not this one. Add it. **Precise scope:** DEC-211's *"caught only when it changes an entry's mode, size or mtime"* is a necessary-condition sentence and is not falsified by B-1 — the security reviewer's charge against those two lines does not hold on a literal reading. What overclaims is D-11's affirmative "vector-agnostic inside DIR" |
| B-3 | bug | the `__pycache__` skip is keyed on the directory *basename* and is checked before the symlink branch, so it admits a payload of any name at any depth under any `__pycache__` directory, and a symlink literally named `__pycache__` is never recorded at all. Carried from c8 (M4) at `med`, unchanged by this diff |
| B-4 | bug | `snapshot()` records files and symlinks but never plain directories, so a **new empty directory** under `bin/` is invisible. My measurement; narrower than B-1 but the same family |
| B-5 | chore | D-11 (`plan.yaml:245`) and T-04's intent (`:930`) both mandate skipping `*.pyc` by suffix. `993ac997` removed that skip and pinned the narrower behaviour with a test. The **code is safer than the plan text**; amend the text rather than revert the code |
| B-6 | bug | T-06's own `verify:` block has never returned 0 since `b86ce66a`. Every substantive clause passes; `post == ["0"]` fails because the carrier note states `post-fix broken reads 0` twice — once in the fenced transcript T-06's own intent mandates, once as the parsed summary. All four panel members and pm agree the **clause** is wrong, not the note. Remedy: `post and set(post) == {"0"}`. Do **not** delete the duplicate line |
| B-7 | chore | `test-check-fixture-secrets.py:171-178` merged two distinct diagnostic messages into one generic "mutant could not be constructed", losing the distinction between "the anchor moved" and "the revert did not take". No coverage lost |
| B-8 | chore | `test-suite-independence.py` `_scan_statements` walks each statement fully and then recurses into its blocks, so a nested finding can be counted twice — an inflated `N site(s)` line, never a wrong verdict. Pre-existing |
| B-9 | bug | the suite is green **only** with `HARNESS_AGENT_TYPE` unset; with it set, `test-plan-merge.py` fails 11 checks and the suite exits 1. pm rules this a genuinely **new** criterion no REQ or SC covers, in a file outside this diff. Recommend a separate `BUG-NN`, not FEAT-48 scope |
| B-10 | chore | `BRIEF.md`'s `## Approval` block is byte-identical across `b86ce66a`, `e64e863e` and `993ac997`, so the approved SC-03 amendment carries no distinct re-signature act in the file. Only your hand can date it |
| B-11 | chore | issue #1053's `## Scope` still reads "Folded into FEAT-47". Outside `plan.yaml`'s write authority; only you can edit an issue body. Whether #1053 closes on ship is also yours |
| B-12 | enhancement | `BRIEF.md` BACKLOG-C — vendor the ten `ea6f51f` sites as committed fixtures so CI can re-check their literal source without a deep checkout. Recorded, not built, exactly as the amendment intended |
| B-13 | harness defect | `bash-write-guard.sh` blocks **all** bash-level file writes including `/tmp` for the read-only `harness-ui-reviewer` persona, which had to drive its fixtures through `python3 -c` instead. Its verdicts stand; its probe surface was narrower than dispatched |
| B-14 | harness defect | carried from c8: `harness-qa` returned `severity_max: medium` where the contract enum is `med`, and `validate-digest.py` accepted it |
| B-15 | chore | `test-run-pool.py` `case_cache_exclusion` pins only the `.pyc` leg, so a future narrowing of the `__pycache__` skip would pass it unchanged — a test-adequacy gap mirroring B-3 |

## Budgets, stated plainly

- **Cycles: 8 of 10.** Unchanged this round. Both leads reported **zero** send-backs and I routed no
  `FAIL` back, so no rework loop ran. Cycles count rework, and there was none.
- **Runs: 21 of an informational 20 — the budget is crossed.** It stops nothing (INV-22 is a note,
  not a gate), and you should see it before authorising more. My read: **they have earned their
  place.** The last four runs each closed something real — a criterion resting on a wrong premise,
  a symlink blindness, a first review of code that had never had one, and now a `code_grade` gate
  cleared plus a coverage claim measured false. What the count is telling you is that the *feature*
  was under-specified at plan time about what "the check catches" means, not that the runs were
  wasted.

## Resolved escalations

- **c8's `code_grade: fail`** — resolved by fix, not by argument. Clean at the pin.
- **c8's `run_pool.py:37-38` lstat asymmetry** — resolved by fix, with a reachability proof.
- **c8's SC-03 "unmeetable as written"** — resolved by your amendment. The amended text is met on
  both halves at the pin, with nothing left to build.
- **c8's M5 (DEC-211 overclaim)** — resolved by the documentation correction in `993ac997`, which
  now matches `_record`'s `(st_mode, st_size, st_mtime_ns)` tuple exactly.
- **c8's M4 (no `__pycache__` test leg)** — resolved; `case_cache_exclusion` pins both legs.

## Open questions for you

1. **B-1: ship with it recorded, or fix it first?** My recommendation is above: ship, record, and
   do B-2 in the same act. Fixing it needs a re-pin and a re-run of this validation.
2. **B-9: adopt the ambient-environment independence as a new criterion, or file it as its own
   bug?** It changes what "done" means, so it is yours. pm and I both recommend a separate bug.
3. **B-11: does issue #1053 close on ship?**
