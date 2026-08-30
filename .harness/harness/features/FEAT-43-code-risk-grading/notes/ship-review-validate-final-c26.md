# FEAT-43 code-risk grading — ship review (final)

**Supersedes `ship-review-validate-final-c25.md`.** That briefing asked you three things. You have now
answered two of them, and each answer was executed. What remains is the SC-11 hand-test and the ship
decision itself.

**Recommendation: ship, after you run the SC-11 hand-test.**

## What you decided this round, and what happened

**You chose HOLD AND FIX on B21**, and authorized one narrowly scoped cycle for it. That was the
right call, and the evidence now says so rather than the argument.

The two branches had no test — `_strip_docstring`, which implements D-03's literal "excluding the
docstring" and underwrites D-02's promise that a docstring edit cannot fire the gate, and
`_qualname`'s class-prefix join, which stops same-named methods of different classes colliding during
pre-image resolution. Both were correct by inspection. Neither was *held* by anything: gut either one
and the full suite **and** the engine's self-grade both stayed at exit 0.

**Both are now bound by named behavioural tests**, asserting through the real gating decision rather
than poking a private helper. I re-ran one of the two mutations myself rather than read it off a
transcript: with `_strip_docstring` reduced to `return body`,
`check_docstring_only_rename_not_gated` fails with `expected set(), got {'renamed'}`, and the restore
left only the test file modified. The delta review re-ran **both**, independently, and QA proved the
harder point — that the tests bind for the *right* reason.

That last part is the part worth your attention. A docstring-only edit **without** a rename would
have proved nothing: `gated_set` resolves by qualname first, finds the predecessor by name, and files
the function informational whether or not docstrings are stripped. A fixture built that way passes
while testing nothing — the exact "asserts less" trap. QA built an out-of-tree control and showed it
returns bit-for-bit identical results with the mutation live and dead. The shipped fixture renames,
and therefore actually reaches the body-hash path.

Production code was not touched. `code_grade.py` is byte-identical by blob hash at both pins, and the
commit is one file, +68/−0.

## The full picture: seven things were wrong, all seven are closed

| | Was | Now |
|---|---|---|
| **CR-01** | the tool rejected its own change — exit 1, six grade-3 production functions | **exit 0**: 198 graded, zero blocking |
| **CR-02 + UI-01** | a grade-3 record failed the build while printing no severity at all | severity derived from blocking-ness, in text and JSON, and the guidance names the case |
| **SEC-01** | a reviewer naming a no-op range bought "not applicable" and skipped the gate | the decision diffs a repository-derived range; the range a digest names no longer changes the answer |
| **ENUM-01** | the feature narrowed the severity ladder and updated 1 of 4 consuming templates | fixed in both trees and mechanically guarded |
| **REQ-11 prose** | glossary and skill still taught the old vocabulary; one heading named the failing side of the bar as the target | four sentences corrected against the tool |
| **T-01** | two engine functions grade 2, excused by allowlist | grade 4, allowlist entries **deleted** rather than re-pointed |
| **B21** | two spec-traced branches held by nothing | both bound by named tests that fail under the exact mutations that used to pass |

## Evidence at the ship pin `cd8dae47`

| Gate | Result |
|---|---|
| The feature's own grading gate | **exit 0** — 198 graded, **zero blocking**, 12 grade-2 (all reasoned and answered at this pin) |
| The engine against its own bar | **53 functions, zero below grade 4**, no carve-out |
| Full independent panel (at `17106762`) | **PASS**, `must_fix: []` |
| Delta review — enum fix (`6752597`) | **PASS**, `must_fix: []` |
| Delta review — T-01 closure (`e12d53b1`) | **PASS**, `must_fix: []`, `severity_max: med` |
| Delta review — B21 closure (this pin) | **PASS**, `must_fix: []`, **`severity_max: low`** |
| Test matrix — the project's only blocking gate | **PASS** |
| `check-state.sh` | **exit 0** |
| Canonical repository suite | 957 results, **one** failing suite — not ours |
| Goal-check | **19 of 20 met, none `not_met`**, SC-11 unproven |

The severity drop from `med` to `low` is substantive, not a softening: c25's `med` was driven
entirely by the two untested branches, and that driver is now closed. The one red suite remains
`test-hooks-install.py (e-green) SC-14` — fixture resolves `--repo harness` to the real checkout,
this diff touches none of the files involved, reproduces on main. Backlog B8.

## What is honestly not covered

- **SC-11 is unproven.** It is the feature's central claim and the only thing left that can move it
  is your hand-test.
- **The collision test binds a derived symptom, not a direct cross-attachment, and it cannot do
  otherwise.** `grade_source` keys its name map with `_child_qualname`, never `_qualname`, so
  `Alpha.run` and `Beta.run` can never be shown swapping places directly. What the test binds is the
  real consequence: the mutation's same-key overwrite destroys a hash entry, so a rename that should
  resolve cleanly is wrongly gated — asserted through the public API, failing on an assertion rather
  than a crash. The validator lead ruled your bar met on its literal terms, and flagged that
  demanding more would demand a test the engine's shape makes impossible. You should know the shape
  of the proof you are accepting.
- **Three neighbouring branches remain unbound** — the narrowed form of the c25 caveat, and it must
  not be read as "now fully covered". `AsyncFunctionDef` through both helpers, `_qualname`'s class
  branch with a *non-empty* incoming prefix (nested classes; both fixture classes are top-level), and
  `_resolve_pre_image`'s multi-candidate hash tie-break. All three pre-date this change and sit
  outside the scope you enumerated. B23.
- The last three reviews were **two-member delta reviews**, not full panels. The c21 panel's security
  and UI verdicts stand and were not refreshed; no delta touched auth, secrets, untrusted input,
  network, deserialization or any rendered surface.
- There is no coverage instrumentation in this repository. Suite counts count scripts, not behaviour.

## How this briefing was assembled

**No report round was spawned.** I read the digests from disk. This cycle added
`runs/2026-08-29-validate-b21-c26-eng/digest.md`,
`runs/2026-08-29-validate-delta-c26-validator/digest.md`, `runs/2026-08-29-c26-product/digest.md`,
and the notes `review-harness-code-reviewer-validate-delta-c26.md`, `qa-validate-delta-c26.md`,
`research-goalcheck-c26.md`. Earlier paths are listed in the c24 and c25 briefings.

**Disclosure.** I verified the central claims myself rather than accept them: the whole-range gate,
the engine self-grade, and one of the two mutations end-to-end including its byte-identical restore.
The budget interpretation disclosed in the c25 briefing still applies to that cycle; cycle 26 spent
zero send-backs in any of its three runs.

## Budget

`cycles_used` is **26 of 26** — exhausted, under the ceiling you set for this one cycle. No repair
capacity remains; anything found from here is a backlog row or a new feature.

`runs` is **39 against an informational 20-run budget** (INV-22). Surfaced, not buried. My read is
unchanged: runs that closed blockers earned their place and were each independently confirmed. The
five bookkeeping-correction rounds I performed by hand were overhead created by leads not meeting
their own digest contract — B20, and it recurred in every single cycle.

## Proposed backlog

Unstruck rows become backlog issues on acceptance. **Anything not listed here dies silently.**
B1–B20 and B22 carry forward from the c25 briefing unchanged; **B21 is now closed and removed**; two
rows are new.

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
| B10 | bug | branch corroboration silently no-ops when either branch is unknown — a fail-open inside a control added to close a fail-open |
| B11 | chore | `SELF_GRADING_ALLOWLIST` entries are hand-maintained with no staleness check beyond the in-suite guard |
| B12 | enhancement | `validate-digest.py` grew 707 → ~1505 lines; the review-binding subsystem wants its own module |
| B13 | enhancement | the same `review_sha` is `git rev-parse`d five times in one validation |
| B14 | chore | the enum guard's discovery is bounded by `ALIAS`, not the filesystem |
| B15 | chore | `harness-validator-lead.md` in both trees still instructs `severity_max: info` — ungated, the last `info` in the repo |
| B16 | bug | **harness**: a documentor write with a relative path modified the MAIN checkout |
| B17 | bug | **harness**: a member ran `git checkout -- <file>` despite an explicit prohibition. No mechanical guard behind the rule |
| B18 | bug | **harness**: the file-reading tool served stale cached contents to two reviewers |
| B19 | chore | vocabulary ruling: `none` means "nothing found" and is not a drop-in for `info` as a *finding* label |
| B20 | bug | **harness**: lead digests written without the required contract block, one outside the feature directory, one declaring PASS over its own member's FAIL. Recurred in every cycle; I fixed five by hand |
| B22 | chore | a stray untracked `.harness/harness/features/FEAT-43-code-risk-grading/` directory in the MAIN checkout from an earlier relative write. Untracked, harmless to the pin |
| **B23** | **chore** | three branches neighbouring the ones B21 closed remain unbound: `AsyncFunctionDef` through both helpers, `_qualname`'s class branch with a non-empty incoming prefix (nested classes), and `_resolve_pre_image`'s multi-candidate hash tie-break. All pre-existing, all outside the scope of the authorized cycle |
| **B24** | **chore** | the collision fixture's third, top-level `run` function is **load-bearing and looks redundant**: it keeps the mutated engine returning a wrong answer instead of a `KeyError`. A successor "simplifying" it to two classes reintroduces the crash and silently loses the binding. Wants a comment saying so |

## What is left for you

**1. Run the SC-11 hand-test.** `notes/uat-sc11-c21.md` — now committed carrying the current pin
`cd8dae47`, so the script and the code it grades agree. Four dispatches, four commands, written for
someone who has not read this feature. Its arithmetic is your MAXIMA ruling and is fixed. **A null
result is a finding against the skill, not a reason to re-run for a better draw**; the pre-build A/B
probe does not discharge the criterion.

**2. The ship decision, and which of B1–B20, B22, B23, B24 survive.**

## State of the branch

Nothing shipped. No PR, no merge, no deploy, no issue closed; the worktree stands. `review_sha` is
`cd8dae476607704fd3d2b874150aae9f814292d2`, parent issue #924 and all ten sub-issues are at Review,
the working tree is clean, and no source has moved past the pin.
