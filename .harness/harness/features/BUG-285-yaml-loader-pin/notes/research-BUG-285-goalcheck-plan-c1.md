# does this plan deliver the operator's stated intent?

**Not yet — the cycle-0 must_fix is closed on substance but the amend introduced a NEW defect of its
own:** step f now orders the *builder* to `COMMIT` the probe note, and DEC-153 reserves the commit pen
to the orchestrator alone (`DECISIONS.md:3471-3473`). One field, one rewording. Everything else in
the plan is unchanged and still correct. Graded against `notes/intake-BUG-285.md` section 1 (the
operator's words), not the BRIEF. Nothing was edited; no suite was run. HEAD still
`7e0c2ec148c05786d2cbbc1bf1f352c3e0403738`.

## must_fix (one, in plan.yaml, before the operator signs)

- **File** `.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml`, **field**
  `tasks[T-01].intent`, **step f** (`plan.yaml:116-120`). Replacement wording:
  *"f. Record both transcripts verbatim, plus the exact commands you ran, in your own notes file
  under this feature's notes/ directory — name it notes/qa-<runid>.md, the path your domain grants
  (team-config.yaml:259) — and LEAVE that file in place. Do not run git commit: the commit pen is the
  orchestrator's (DEC-153). Report the note's exact path as your DIGEST artifact so the orchestrator
  stages it by pathspec in the same commit as the test change — SC-03 is graded with
  `git show <review_sha>:<that path>`, so a note absent from that commit grades not_met however good
  the proof. Then delete the throwaway script and its tempdir. Nothing under tests/ or .claude/ may
  be left changed by the probe."*
  Fold into the same edit the general/specific clash the amend leaves standing: `plan.yaml:49-51`
  says "do not edit any file other than tests/integration/test-gh-sync.py", which read literally
  forbids the note step f mandates. Qualify it: *"…other than tests/integration/test-gh-sync.py and
  your own notes file under this feature's notes/ directory."*

## 1. The cycle-0 must_fix — closed on substance, wrong on mechanism

Step f now carries "and COMMIT that note with the test change - SC-03 is graded with `git show
<review_sha>:<that path>`, so an uncommitted note grades not_met" (`plan.yaml:116-119`). The
untracked-note failure the c0 note named is addressed and the reason is stated, so a builder cannot
mistake the requirement. But the *actor* is wrong: the member is told to commit, which is exactly the
class of act DEC-153's audit sanctioned (`DECISIONS.md:3462-3464, 3471-3473`). Unambiguous, and
unambiguously directing a decision violation.

## 2. The amend touched step f and nothing else

`safe_load` at the current file: top-level keys `approval decisions feature lanes schema
source_issues status tasks` — no `panel:`; `approval.status: pending` (`plan.yaml:3-4`); one task;
four decisions (D-01..D-04, `:16-31`); `files: ['tests/integration/test-gh-sync.py']`
(`:42-43`); `verify:` still a literal block loading to exactly
`env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gh-sync.py\n` (`:44-45`). Every c0-recorded
line anchor before `intent:` is unmoved; the file grew 125 → 127 lines, both inside step f. All
eleven task keys are the c0 set.

## 3. The four cycle-0 findings still hold on the amended text

Scope is still one fixture in one file (`:42-43`, `:47-51`; BRIEF `## Constraints` `:36-48`).
Mutant-red/real-green is still *required*, by SC-03 (`BRIEF.md:65-70`) and by intent steps a–f
(`:99-120`), not merely mentioned. `intent:` remains buildable with no further questions — every
anchor it cites was re-derived at c0 and none has drifted. Nothing authorises a production change:
`BRIEF.md:38-40` routes a red assertion to the operator, `plan.yaml:49-50` forbids the edit, and D-04
(`:28-31`) plus steps b–d confine the mutant to a `shutil.copy` in a tempdir, naming the
single-inode symlink reason.

## 4. New gaps from the amended sentence itself

The DEC-153 clash above is one. The other two candidates are clean: SC-05's diff is scoped
`-- tests/integration/test-gh-sync.py` (`BRIEF.md:77-81`), so a committed note is invisible to it;
and BRIEF's one-file constraint (`BRIEF.md:41-42`) names `gh-sync.py` and other *test* files, which a
note is not. The feature directory is committable — `git check-ignore` on `notes/` exits 1 — so the
obligation is satisfiable once the actor is corrected.

## Advisory (do not gate)

- SC-04 "at least 318 ok" (`BRIEF.md:71-76`) vs T-01 "more than 318" (`:124-125`): both hold. Carried
  from c0, still no edit needed.
- No open question for the operator. Zero artifacts edited by this goal-check.
