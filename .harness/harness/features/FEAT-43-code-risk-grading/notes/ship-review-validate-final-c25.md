# FEAT-43 code-risk grading — ship review (final)

**Supersedes `ship-review-validate-final-c24.md`.** That briefing asked you three questions. You
answered two of them, and the third — the ship decision — is what remains.

**Recommendation: ship, after you run the SC-11 hand-test.**

Both of your rulings are executed and recorded. T-01's deviation is closed at the root rather than
accepted, and SC-11's arithmetic was pinned to arm **maxima** and marked settled *before* any number
was drawn, which is the only way that recording is worth anything.

## What you decided, and what happened

**You refused the T-01 deviation.** Two functions in the grading engine were grade 2 — excused by
allowlist entries citing written reasons. They are now **grade 4**: `_body_hashes.collect` went
cyc/cog/ABC 9/18/17.3 → 4/5/8.8, and `gated_set` went 8/25/24.9 → 2/1/10.0, behind six named helpers.
**Both allowlist entries were deleted rather than re-pointed**, and no replacement entry was added for
any new helper, so the carve-out is gone rather than moved. The engine now reports **53 functions,
zero below grade 4**. T-01's clause — "keep every function you write in `code_grade.py` at grade 4 or
better… the tool must pass its own bar" — is true as written, not true-except-twice.

This was the riskiest edit in the feature, because `gated_set` is the seam three signed decisions
specify, and the written reason for its former grade-2 status argued explicitly that the logic
belonged in one place "rather than distributing it across helpers that could disagree." You overruled
that argument, so the burden moved to evidence. It was met: **three independent mutations by two
agents**, each failing a *different* named case at *two* seams, each restored byte-identically and
re-run green. The resolution order — qualname, then body hash, then the rename-aware fallback — and
`before is None or record.grade < before.grade` as the sole gating comparison are both unchanged, and
all eight resolution cases pass individually.

**You ruled SC-11 on arm maxima.** Recorded at `answers/Q9-sc11-maxima-and-t01-no-exemption.md` and
stamped SETTLED inside `notes/uat-sc11-c21.md` itself, before the run. The script is unchanged,
unexecuted, and still matches the ruling — pm confirmed both.

## The full picture: six things were wrong, all six are closed

| | Was | Now |
|---|---|---|
| **CR-01** | the tool rejected its own change — exit 1, six grade-3 production functions | **exit 0** over the feature's own range: 195 graded, zero blocking |
| **CR-02 + UI-01** | a grade-3 record failed the build while printing no severity at all | severity derived from blocking-ness; every blocking record says so in text and JSON, and the guidance names the case |
| **SEC-01** | a reviewer naming a no-op range bought "not applicable" and skipped the gate | the decision diffs a repository-derived range; the range a digest names no longer changes the answer |
| **ENUM-01** | the feature narrowed the severity ladder and updated 1 of 4 consuming templates, so a clean security or UI review would be hard-rejected | fixed in both trees and mechanically guarded |
| **REQ-11 prose** | the shipped glossary and skill still taught the old vocabulary — one heading named the failing side of the bar as the thing to aim at | four sentences corrected against the tool |
| **T-01** | two engine functions grade 2, excused by allowlist | grade 4, allowlist entries deleted |

## Evidence at the ship pin `e12d53b1`

| Gate | Result |
|---|---|
| The feature's own grading gate | **exit 0** — 195 graded, **zero blocking**, 12 grade-2 (all reasoned and answered at this pin) |
| The engine against its own bar | **53 functions, zero below grade 4**, no carve-out |
| Full independent panel (at `17106762`) | **PASS**, `must_fix: []` — three reviewers plus QA, none from earlier cycles |
| Delta review of the enum fix (at `6752597`) | **PASS**, `must_fix: []` |
| Delta review of the T-01 closure (this pin) | **PASS**, `must_fix: []`, `severity_max: med` |
| Test matrix — the project's only blocking gate | **PASS** — unit 29/29, integration 32/32 |
| `check-state.sh` | **exit 0** |
| Canonical repository suite | 957 results, **one** failing suite — not ours |
| Goal-check | **19 of 20 met, none `not_met`**, SC-11 unproven |

I re-derived the two grading measurements myself rather than accept them, and the delta review
re-derived them again independently. The one red suite is `test-hooks-install.py (e-green) SC-14`:
its fixture resolves `--repo harness` to the real checkout instead of its temporary clone, this
feature's diff touches none of the files involved, and it reproduces on main. Backlog B8.

## What is honestly not covered

- **SC-11 is unproven**, and it is the feature's central claim: whether the guidance changes what an
  engineer writes. Four agent dispatches and four one-line commands, run by you.
- **Two spec-traced branches have no test, and the delta review proved it by mutation.**
  `_strip_docstring` implements D-03's literal "excluding the docstring" and underwrites D-02's
  promise that a docstring edit cannot fire the gate; `_qualname`'s prefix join is what stops
  same-named methods of different classes colliding during pre-image resolution. Gut either one and
  **the full suite and the self-grade both stay green**. They are correct by inspection and they
  **pre-date this change** — they were inline inside `_body_hashes.collect` and equally untested for
  24 cycles and two full panels; decomposition is what made them nameable. This is a decision for
  you: see B21.
- The last two reviews were **delta reviews, two members each**, not full panels. No security or UI
  adjudication at the final pin — neither delta touched auth, secrets, untrusted input or a rendered
  surface.
- SC-15's verdict rests on the 12 reason-demands re-derived and answered at *this* pin by the delta
  reviewer. pm, running concurrently, could not see that file and recorded its verdict on superset
  reasoning instead; the artifact pm said was missing does exist —
  `notes/review-harness-code-reviewer-validate-delta-c25.md`.
- There is no coverage instrumentation in this repository. "29/29" counts scripts, not behaviour.

## How this briefing was assembled

**No report round was spawned.** I read the digests from disk. Beyond the paths listed in the c24
briefing, this cycle added `runs/2026-08-29-01-validate-t01-c25-eng/digest.md`,
`runs/validate-delta-c25-validator/digest.md`,
`runs/2026-08-29-01-validate-goalcheck-c25-product/digest.md`, and the notes
`review-harness-code-reviewer-validate-delta-c25.md`, `qa-validate-delta-c25.md`,
`research-goalcheck-c25.md`, `receipt-harness-backend-dev-validate-t01-c25-eng.md`.

**Two disclosures.** First, I verified the central claims myself — the engine's self-grade, the
whole-range gate, and that no allowlist entry keys on `code_grade.py`. Second, **a budget
interpretation you should see rather than infer.** You authorized "the final rework cycle", and I
read that as one final *attempt*, not one final agent turn: two internal send-backs occurred inside
it (one in engineering, one in the goal-check) and I did not increment past 25 for them. Both are
recorded in their run digests. The engineering one is worth telling you about because it is the
system biting itself in a useful way: the first new test was *itself* below the test file's grade-3
bar, so the self-grading guard rejected the test that fixed the self-grading violation.

## Budget

`cycles_used` is **25 of 25** — exhausted. There is no further repair capacity. Anything found from
here is a backlog row or a new feature, not a fix.

`runs` is **36 against an informational 20-run budget** (INV-22). Surfaced, not buried. My read is
unchanged: the runs that closed blockers earned their place and were each independently confirmed;
the four bookkeeping-correction rounds I had to perform by hand were overhead created by leads not
meeting their own digest contract, which is B20.

## Proposed backlog

Unstruck rows become backlog issues on acceptance. **Anything not listed here dies silently.**
B1–B20 carry forward from the c24 briefing unchanged; two rows are new.

| ID | Nature | What |
|---|---|---|
| B1 | chore | `validate-digest.py` — `.encode()` preserves a `bytes` return neither consumer requires |
| B2 | enhancement | eager `from code_grade import commit_oid` costs ~8ms per hook for a one-branch symbol |
| B3 | enhancement | two `git rev-parse` spawns per validation (~22ms); collapsing changes the seam signature |
| B4 | chore | three blank lines where both files use PEP8's two everywhere else |
| B5 | chore | five spellings of "init a scratch git repo" across three test files; wants a shared test-support module |
| B6 | chore | two near-identical git wrappers with different error contracts |
| B7 | bug | the digest schema gives a read-only engineering assessment no legal way to report its suite |
| B8 | bug | `test-hooks-install.py (e-green) SC-14` fails on any developer machine — fixture resolves `--repo harness` to the real checkout. Makes the canonical suite red on main |
| B9 | bug | the review-binding error prints twice — one site, two call paths, no de-duplication |
| B10 | bug | branch corroboration silently no-ops when either branch is unknown (4 of 40 `feature.json` files carry no `branch`) — a fail-open inside a control added to close a fail-open |
| B11 | chore | `SELF_GRADING_ALLOWLIST` carries hand-maintained entries with no automated staleness check beyond the in-suite guard |
| B12 | enhancement | `validate-digest.py` grew 707 → ~1505 lines; the review-binding subsystem wants its own module |
| B13 | enhancement | the same `review_sha` is `git rev-parse`d five times in one validation |
| B14 | chore | the enum guard's discovery is bounded by `ALIAS`, not the filesystem: a template added without an `ALIAS` entry is silently unchecked |
| B15 | chore | `harness-validator-lead.md` in both trees still instructs `severity_max: info` — measured ungated, the last `info` in the repo |
| B16 | bug | **harness**: a documentor write with a relative path modified the MAIN checkout. Reverted; hazard is real |
| B17 | bug | **harness**: a member ran `git checkout -- <file>` despite an explicit prohibition, reverting a completed refactor. No mechanical guard behind the rule |
| B18 | bug | **harness**: the file-reading tool served stale cached contents to two reviewers, contradicting `bash` reads of the same paths |
| B19 | chore | vocabulary ruling: `none` means "nothing found" and is not a drop-in for `info` as a *finding* label |
| B20 | bug | **harness**: lead digests written without the required contract block, one outside the feature directory, one declaring PASS over its own member's FAIL. Caught only after the fact, and only for me to fix by hand |
| **B21** | **bug** | **two spec-traced branches in `code_grade.py` have no test**: `_strip_docstring` (D-03's "excluding the docstring", underwriting D-02) and `_qualname`'s prefix join. Proven untested by mutation — gutting either leaves the full suite green. Correct by inspection, pre-dating this change |
| **B22** | **chore** | a stray untracked `.harness/harness/features/FEAT-43-code-risk-grading/` directory sits in the MAIN checkout from an earlier agent's relative write. Untracked, so it cannot affect the pin — worth removing before the next feature so it is not mistaken for the live folder |

## What is left for you

**1. Run the SC-11 hand-test.** `notes/uat-sc11-c21.md`. Four dispatches, four commands, written for
someone who has not read this feature. Its arithmetic is your maxima ruling and is fixed. **A null
result is a finding against the skill, not a reason to re-run for a better draw**, and the pre-build
A/B probe does not discharge the criterion — the draft it graded shares no non-blank line with the
shipped skill.

**2. Decide B21** — ship with the two named untested branches recorded, or hold. My read: they are
correct by inspection, they pre-date this feature's change, and the budget to test them no longer
exists inside this feature, so recording them is the honest option; holding the feature over them
would buy nothing this cycle can deliver.

**3. The ship decision, and which backlog rows survive.**

## State of the branch

Nothing shipped. No PR, no merge, no deploy, no issue closed; the worktree stands. `review_sha` is
`e12d53b16e49e7c4d9332c5e290e6bdbc806251f`, the parent issue #924 and all ten sub-issues are at
Review, the working tree is clean, and no source has moved past the pin.
