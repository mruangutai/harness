# FEAT-43 code-risk grading — ship review

**Recommendation: ship, once you have decided two things and run one hand-test.**

The four blockers that stopped this feature at cycle 13 are closed. I verified each one by running
the measurement myself rather than accepting a squad's report, and a fresh independent panel — three
reviewers and QA who had not seen the earlier cycles — adjudicated all four CLOSED and returned
`must_fix: []`.

**The one thing still genuinely unknown is the feature's central claim.** SC-11 asks whether the
guidance actually changes what an engineer writes. No automated gate can answer it; it needs you to
run a short A/B test. Everything else — nineteen of twenty success criteria — is met on evidence.

## What was wrong, and what closed it

**1. The feature did not pass the gate it ships (was high).** At the old pin the tool exited 1 over
this feature's own change, with six grade-3 production functions below a bar of 4 — two of them
inside the grading engine itself.

*Closed.* Over the ship pin the same command exits **0**: 186 graded functions, **zero blocking
failures**. I ran it. The fix was real decomposition, not relabelling, and the panel checked exactly
that: the cheapest fake remediation available was to push those six functions into the *non-blocking*
grade-2 carve-out, which is numerically worse but does not fail the build. The panel refuted it —
the grade-2 set went 15 → 14 while the graded set went 119 → 186, and none of the six appears in it.

There was a second round here worth telling you about, because it is the system working. The first
fix closed all six named functions, and my post-commit check then failed anyway: the remediation had
pushed the test suite's own `main` to grade 1, and the guard meant to prove "the tool passes its own
bar" was blind to it — it enumerated three hardcoded production files and never looked at the test
files. The second fix closed the *class*: the guard now covers every changed file at its own bar.

**2. "Gated grade-3, below bar" had no name (was med), and 4. the report gave an author nothing to
act on (was high).** One root cause: severity was a lookup on the grade literal, so a grade-3
production function failed the build while printing no severity at all.

*Closed.* Severity is now derived from **blocking-ness** rather than the grade, so anything that
fails the build says so, in text and in JSON, and the shipped guidance names the case. The UI
reviewer proved it on a live render rather than a source reading.

**3. A reviewer's grade claim could bypass the gate (was high).** The validator decided whether
Python had changed by diffing the range the reviewer typed into its own digest. Naming a no-op range
bought a "not applicable" and skipped the gate entirely.

*This one took two attempts and is the most important thing in this briefing.* The first fix bound
the reviewed *head* to `review_sha`, which sounds right and was not: a range from the pin to the pin
is a self-consistent no-op whose head resolves correctly. QA reproduced the bypass live and failed
the gate. QA then proposed the obvious remedy — reject `base == head` — and I rejected it, because
QA's own note already contained the walk-around: `<review_sha>~1..<review_sha>` is a different shape
with the same effect. Blacklisting shapes is how you build a gate that reports success.

The premise behind the alternative turned out to be wrong, and a measurement settled it rather than
an argument. QA held that binding the base needed a new `feature.json` field, i.e. a schema change.
But `git merge-base main <pin>` returns `7ccfae8d` — *exactly* the base the panel reviewed. The
predecessor was already in the record; nothing was reading it.

*Closed as a class.* The decision now diffs a range the repository derives, so the digest has no
channel into it at all. The tell is that **the range the reviewer names no longer changes the
answer** — all three shapes now refuse, identically. The panel's security reviewer forged nine
digests, five of them shapes nobody had enumerated, and every one was refused.

## What the panel found that nobody was looking for

After the panel passed, the product segment found a **fifth blocker**, and it is a good argument for
running the goal-check even when the gates are green. This feature's own change narrowed the reviewer
severity ladder — it removed `info` — and updated one of the four reviewer templates that consume it.
A security or UI reviewer whose worst finding was informational would have written the value its own
template told it to write and been hard-rejected as a contract violation. `info` is the most common
value in the historical record. The panel missed it only because its own findings happened to rank
higher.

Fixed in all four templates in both trees, and **guarded**: a check now fails loudly when a template
and the validator disagree. The delta review mutated that guard three ways to prove it binds,
including starving its discovery to confirm it fails rather than passing vacuously on an empty set.

The same sweep found this feature's own glossary and shipped skill still teaching the pre-remediation
vocabulary — including a section heading that told the reader to keep functions *under* the bar, which
names the failing side. Four sentences corrected, verified against the tool, suites green.

## How this briefing was assembled

**No report round was spawned.** I read the run digests from disk, as the playbook requires. The
paths, all under `.harness/harness/features/FEAT-43-code-risk-grading/`:

- Plan and build: `runs/plan-product/digest.md`, `runs/t01-t07-eng/`, `runs/t02-eng/`,
  `runs/t03-eng/`, `runs/t06-eng/`, `runs/t10-product/`, `runs/build-qa-validator/`,
  `runs/build-qa-validator-rerun/`, `runs/build-simplify-eng/` — each `digest.md`.
- Earlier validate cycles: `runs/validate-review-validator/`, `runs/validate-fix-eng/`,
  `runs/validate-fix-qa-validator/`, `runs/validate-fix-simplify-eng/`,
  `runs/validate-review-final-validator/`, `runs/validate-fix-c11-eng/`,
  `runs/validate-fix-c13-qa-validator/`, `runs/validate-fix-c13-simplify-eng/`,
  `runs/validate-fix-c13-r01-eng/`, `runs/validate-regate-c13-r01-validator/`,
  `runs/validate-final-simplify-eng/`, and the cycle-13 panel's three reviewer notes.
- This effort: `runs/validate-remediate-c14-eng/`, `runs/validate-remediate-c18-eng/`,
  `runs/validate-regate-c18-validator/`, `runs/validate-sec01-c19-eng/`,
  `runs/validate-final-simplify-c21-eng/`, `runs/validate-regate-c21-validator/`,
  `runs/validate-final-panel-c21-validator/`, `runs/validate-goalcheck-c21-product/`,
  `runs/2026-08-29-01-validate-enumfix-c22-eng/`, `runs/validate-delta-c23-validator/`,
  `runs/2026-08-29-01-product/`, `runs/2026-08-29-01-engineering/`.
- Notes: the four c21 panel artifacts, `notes/research-goalcheck-c21.md`,
  `notes/uat-sc11-c21.md`, `notes/receipt-harness-documentor-validate-goalcheck-c21-product.md`,
  `notes/review-harness-code-reviewer-validate-delta-c23.md`, `notes/qa-validate-delta-c23.md`.

**Two disclosures.** First, I did not take the central claims on report: I re-ran the grading tool at
every pin, reproduced the security bypass myself before and after the fix, and confirmed the enum
drift by direct measurement. Second, **two lead digests arrived not meeting the digest contract** —
the panel's was written outside the feature directory and without its contract block, and the
enum-fix lead's was missing the block. I moved the first into place and transcribed both leads' own
returned blocks into the files verbatim, changing no content. The cycle-14 digest additionally
declared PASS while one of its own members had returned FAIL; I corrected it to FAIL, which is also
what my post-commit gate and the cycle-18 QA gate independently found. All three corrections are
annotated in the files.

## The evidence, in one place

| Gate | Result at the ship pin `d2e3b5eb` |
|---|---|
| The feature's own grading gate | **exit 0** — 186 graded, 0 blocking, 14 grade-2 (all reasoned) |
| Full independent panel | **PASS**, `must_fix: []`, `severity_max: med` — 3 reviewers + QA, none from earlier cycles |
| Targeted delta review of the late fixes | **PASS**, `must_fix: []` |
| Test matrix (the project's only blocking gate) | **PASS** — unit 29/29, integration 32/32 |
| `check-state.sh` | **exit 0** |
| Canonical repository suite | 957 results, **one** failing suite — not ours, see below |
| SIMPLIFY, four angles | empty pass, nothing warranted applying |
| Goal-check | **19 of 20 criteria met**, none `not_met`, SC-11 unproven |

**The one red suite is not this feature's.** `test-hooks-install.py` case `(e-green) SC-14` fails; its
fixture resolves `--repo harness` to the real checkout instead of its temporary clone. This feature's
diff touches none of the files involved, and the cycle-13 record reproduced the same failure on main,
which contains no grading code at all. Carried as B8. I deliberately did **not** re-run it in the main
checkout to strengthen that evidence, because B8's own defect means doing so risks touching live
worktrees — say the word if you want that check run anyway.

## What is honestly not covered

Stated plainly, because a briefing that only lists green things is not useful.

- **SC-11 is unproven.** It is the feature's central claim and it is yours to decide.
- The UI fix was proven on a **synthetic** fixture, because the CR-01 fix left no blocking record in
  the real diff. Rendering is proven general, not proven on this diff. The goal-check checked whether
  any criterion depends on that distinction; none does.
- Four earlier tasks (T-04, T-05, T-06 delivery, T-10) were carried forward by the panel on a
  byte-identical-diff argument rather than re-derived. The goal-check re-grounded their criteria
  independently, so nothing rests on the inheritance.
- The delta review was two members, not four. No security or UI adjudication at the final pin — the
  delta touched no auth, secrets, untrusted input or rendered surface.
- There is no coverage instrumentation in this repository. "29/29" counts scripts, not behaviour.

## Budget

`cycles_used` is **24 of 25** after your two raises (13 → 20 → 25). **One cycle remains**, so there is
no room for another repair round: a further defect means stopping, not fixing.

`runs` stands at **33 against an informational 20-run budget** (INV-22), and I am surfacing it rather
than burying it. My read: these runs earned their place, but not all equally. The five that closed
blockers, the two panels and the goal-check each resolved something real and were independently
confirmed. The three bookkeeping-correction rounds I had to make by hand were pure overhead created
by leads not meeting their own digest contract — that is the harness costing you money, and B20 is
the row for it.

## Proposed backlog

Unstruck rows become backlog issues on acceptance. **Anything not listed here dies silently.**

| ID | Nature | What |
|---|---|---|
| B1 | chore | `validate-digest.py` — `.encode()` preserves a `bytes` return neither consumer requires |
| B2 | enhancement | eager `from code_grade import commit_oid` costs ~8ms per hook for a symbol used on one branch |
| B3 | enhancement | two `git rev-parse` spawns per validation (~22ms); collapsing changes the seam signature |
| B4 | chore | three blank lines where both files use PEP8's two everywhere else |
| B5 | chore | **now five** spellings of "init a scratch git repo" across three test files; wants the shared test-support module that does not exist yet |
| B6 | chore | two near-identical git wrappers with different error contracts; merge only if a third caller appears |
| B7 | bug | the digest schema gives a read-only engineering assessment no legal way to report its suite: `dev` + `suite: n/a` + PASS is rejected while `dev-ops` is allowed |
| B8 | bug | `test-hooks-install.py` `(e-green) SC-14` fails on any developer machine — its fixture resolves `--repo harness` to the real checkout. Pre-existing; makes the canonical suite red on main |
| B9 | bug | the review-binding error prints **twice** — one producing site reached by two call paths, no de-duplication. Confirmed live by the panel and the delta review |
| B10 | bug | branch corroboration silently no-ops when either branch is unknown (4 of 40 `feature.json` files carry no `branch`) — a fail-open shape inside a control added to close a fail-open. The panel accepted the narrowed guarantee and recommends making it refuse instead |
| B11 | chore | `SELF_GRADING_ALLOWLIST` carries 37 hand-maintained entries with no automated staleness check; measured structurally inert to the real gate |
| B12 | enhancement | `validate-digest.py` grew 707 → 1505 lines; the ~330-line review-binding subsystem wants its own sibling module. SIMPLIFY assessed it and correctly deferred rather than spend its one apply before a pin |
| B13 | enhancement | the same `review_sha` is `git rev-parse`d five times in one validation — ~33ms of that path's ~185ms |
| B14 | chore | the new enum guard's discovery is bounded by `ALIAS`, not the filesystem: a reviewer template added without an `ALIAS` entry is silently unchecked. Same change could cover lead templates |
| B15 | chore | `harness-validator-lead.md` in both trees still instructs `severity_max: info`. Measured **ungated** (the lead schema has no such key), so cosmetic — but it is the last `info` in the repo |
| B16 | bug | **harness**: a documentor write with a relative path resolved against its own cwd and briefly modified the MAIN checkout. Reverted byte-identically; the path-resolution hazard is real |
| B17 | bug | **harness**: a member ran `git checkout -- <file>` despite an explicit prohibition, silently reverting a completed refactor. It self-detected and redid the work. The prohibition is prose with no mechanical guard behind it |
| B18 | bug | **harness**: the file-reading tool served stale cached contents to both delta-review members, contradicting `bash` reads of the same paths. A tool that silently serves stale content can invalidate any review's evidence |
| B19 | chore | vocabulary ruling needed: `none` means "nothing found" and is not a drop-in for `info` as a *finding* label. Either drop the `info` rung or keep it as a finding label while stating `severity_max` bottoms at `none` |
| B20 | bug | **harness**: two lead digests were written without the required contract block, one outside the feature directory, and one declared PASS over its own member's FAIL. `check-state.sh` caught them, but only after the fact and only for me to fix by hand |

## The decisions — three, and they are all yours

**1. The ship decision itself.** Ship, fix, or stop. My recommendation is ship, after (2) and (3).

**2. SC-11's arithmetic, and it must be settled *before* the test runs, not after the numbers land.**
The criterion says "the worst cognitive complexity in the arm", which reads as the arm **maximum**.
The BRIEF's own probe citation reports arm **means** — and on the mean reading the probe's own numbers
*fail* the criterion's second half, while on maxima they pass. The UAT script pins maxima and says so.
Settling this after seeing the result would not be a measurement. The script is
`notes/uat-sc11-c21.md`: it is written to be run by someone who has not read this feature, it takes
four agent dispatches and four one-line commands, and it explicitly tells you what a null or reversed
result means. **A null result is a finding against the skill, not a reason to re-run for a better
draw.**

The pre-build A/B probe does **not** discharge SC-11: pm measured that the draft it graded shares no
non-blank line with the shipped skill. Do not accept it in lieu of the run.

**3. T-01's self-standard, unmet on two functions.** T-01 says, without qualification, "keep every
function you write in `code_grade.py` at grade 4 or better". Two of that file's 47 functions are
**grade 2** — `_body_hashes.collect` and `gated_set`. They do not block anything: REQ-06 makes grade 2
mergeable with a written reason, and both reasons are written and persisted. But pm ruled — correctly,
in my view — that REQ-06 governs *mergeability* and cannot discharge a *craftsmanship* clause, so the
panel's acceptance does not close it. Accept the deviation, or route a follow-up. It is a real
deviation from a written instruction and you should see it named rather than have it live inside a
`low` note.

## State of the branch

Nothing has been shipped. No PR, no merge, no deploy, no issue closed, and the worktree stands.
`review_sha` is pinned to `d2e3b5eb47c84fdfac5371b924b7ce1bb8fc37ba`; the parent issue #924 and all
ten sub-issues are at Review. Every commit and artifact is preserved.
