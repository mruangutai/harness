# FEAT-43 code-risk grading — ship review (final)

**Supersedes every earlier ship review.** Every question these briefings have put to you is now
answered, and every answer has been executed.

**Recommendation: SHIP.**

Twenty of twenty success criteria are met. Zero `not_met`. Zero open. `must_fix` is empty across the
full panel and all three delta reviews. Nothing is waiting on anyone but you.

## The claim the feature exists to make is now measured, not argued

SC-11 was the one thing no gate could settle: does the shipped guidance actually change what an
engineer writes? You ran it, blinded, and it **passed** — decisively, not marginally.

| | skill arm | control arm |
|---|---|---|
| worst cognitive complexity | **6**, **5** | **16**, **14** |
| arm worst | **6** | **16** |
| within-arm spread | 1 | 2 |

`worst_A < worst_B` — 6 < 16. `gap > max(spread)` — 10 > 2. Both conditions of the frozen MAXIMA
rule hold, and **the gap is five times the larger within-arm spread**, so this is not a noise result
dressed as a signal. All four variants parsed; no ungraded output, so nothing is inconclusive.

The rule was fixed *before* any number was drawn (`answers/Q9-…` §1), which is what makes the result
worth anything. pm did not adopt the arithmetic: it re-derived it, then re-ran the grader over the
four surviving arm outputs and **reproduced all four values exactly**.

**Two things about this result you should hold onto.**

**Your discarded first run is why the second one counts.** The initial dispatch was voided before any
number was recorded, because shared context revealed the experimental arms to the control agents —
precisely the contamination the script's control-arm rules exist to prevent. Its outputs were
deleted. That was a void on *procedure*, not on numbers, so this is a disclosed discard rather than a
selection between two draws. Recording it is what makes the surviving result credible.

**And one link in the chain is testimonial, not measured.** The four outputs survive in `/tmp` and
regrade exactly — but nothing in the artifacts can prove *by inspection* that they are the
neutral-context run's rather than the discarded one's. That rests on your disclosure. SC-11 is
strongly evidenced; it is not end-to-end machine-verified, and this briefing will not pretend
otherwise.

**What the pass licenses, and what it does not.** It supports the feature's central claim: the skill
measurably lowers the worst complexity an engineer writes on a non-trivial task. It is one A/B with
two variants per arm — enough to justify shipping the guidance, not enough to quantify the effect
size or to claim it generalises to every task shape.

## Seven defects, all closed

| | Was | Now |
|---|---|---|
| **CR-01** | the tool rejected its own change — exit 1, six grade-3 production functions | **exit 0**: 198 graded, zero blocking |
| **CR-02 + UI-01** | a grade-3 record failed the build while printing no severity at all | severity derived from blocking-ness, in text and JSON; the guidance names the case |
| **SEC-01** | a reviewer naming a no-op range bought "not applicable" and skipped the gate | the decision diffs a repository-derived range; **the range a digest names no longer changes the answer** |
| **ENUM-01** | the severity ladder was narrowed and only 1 of 4 consuming templates followed | fixed in both trees and mechanically guarded |
| **REQ-11 prose** | glossary and skill still taught the old vocabulary; one heading named the failing side of the bar as the target | four sentences corrected against the tool |
| **T-01** | two engine functions grade 2, excused by allowlist | grade 4, allowlist entries **deleted** rather than re-pointed |
| **B21** | two spec-traced branches held by nothing | bound by named tests that fail under the exact mutations that used to pass |

Three of those seven were found *after* a gate had already gone green — ENUM-01 by the goal-check
after the panel passed, the REQ-11 prose drift by the documentor, B21 by a delta review. That is the
argument for running the later stages even when the earlier ones are clean.

## Evidence at the ship pin `cd8dae47`

| Gate | Result |
|---|---|
| Goal-check | **20 of 20 met, 0 `not_met`, 0 open** |
| The feature's own grading gate | **exit 0** — 198 graded, zero blocking, 12 grade-2 all reasoned and answered at this pin |
| The engine against its own bar | **53 functions, zero below grade 4**, no carve-out |
| Full independent panel (`17106762`) | **PASS**, `must_fix: []` |
| Three delta reviews (`6752597`, `e12d53b1`, `cd8dae47`) | **PASS**, `must_fix: []`, severity ending at **low** |
| Test matrix — the project's only blocking gate | **PASS** |
| `check-state.sh` | **exit 0** |
| Canonical repository suite | 957 results, **one** failing suite — not ours |
| SC-11 UAT | **passed**, operator-executed, recorded at this pin |

The single red suite is `test-hooks-install.py (e-green) SC-14`: its fixture resolves `--repo
harness` to the real checkout instead of its temporary clone, this feature's diff touches none of the
files involved, and it reproduces on main. Backlog B8.

## What is still true and uncovered

- The SC-11 provenance link described above.
- **Three branches neighbouring the ones B21 closed remain unbound** — `AsyncFunctionDef` through
  both helpers, `_qualname`'s class branch with a non-empty incoming prefix, and
  `_resolve_pre_image`'s multi-candidate tie-break. Pre-existing, outside the scope you authorized.
  B23.
- The collision test binds a *derived symptom*, not a direct cross-attachment — `grade_source` keys
  its name map with `_child_qualname`, never `_qualname`, so direct discrimination is impossible
  given the engine's shape.
- The last three reviews were **two-member delta reviews**, not full panels. The c21 panel's security
  and UI verdicts stand and were not refreshed; no delta touched auth, secrets, untrusted input,
  network, deserialization or a rendered surface.
- No coverage instrumentation exists in this repository. Suite counts count scripts, not behaviour.

## How this briefing was assembled

**No report round was spawned.** I read the digests from disk; paths are enumerated in the c24, c25
and c26 briefings, plus this cycle's `runs/…-sc11-record…/digest.md` and
`notes/research-goalcheck-final.md`.

**One correction to a subordinate's finding, disclosed.** pm reported backlog row B22 as stale,
having checked by glob and found nothing. I checked with `git status` and `find`: the stray
`.harness/harness/features/FEAT-43-code-risk-grading/` directory **does** exist in the main checkout,
untracked, two files. **B22 stays.** A row struck on a bad check is a row that dies silently, which is
exactly what this table exists to prevent.

## Budget

`cycles_used` is **26 of 26** — exhausted, under the ceiling you set. `runs` is **40 against an
informational 20-run budget** (INV-22), surfaced rather than buried. My read, unchanged: the runs that
closed defects earned their place and were each independently confirmed; the five bookkeeping
corrections I performed by hand were overhead created by leads not meeting their own digest contract,
which is B20 and which recurred in every single cycle of this feature.

## Backlog disposition

Unstruck rows become backlog issues on acceptance. **Anything not listed here dies silently.** B21 is
closed and removed.

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
| B20 | bug | **harness**: lead digests written without the required contract block, one outside the feature directory, one declaring PASS over its own member's FAIL. Recurred every cycle; I fixed five by hand |
| B22 | chore | a stray untracked `.harness/harness/features/FEAT-43-code-risk-grading/` directory in the main checkout, two files, from an earlier relative-path write. **Verified present** |
| B23 | chore | three branches neighbouring the ones B21 closed remain unbound; pre-existing, outside the authorized scope |
| B24 | chore | the collision fixture's third top-level `run` function looks redundant but is load-bearing — deleting it reintroduces a crash and silently loses the binding. Wants a comment saying so |

## The decision

**Ship.** Say the word and the main session takes it from here: merge, `gh-sync.py ship`, the backlog
rows you leave unstruck, feature-close distillation, and worktree removal — none of which is mine to
do, and none of which has been done.

If you would rather strike rows first, strike them by ID and the rest become issues on acceptance.

## State of the branch

Nothing shipped. No PR, no merge, no deploy, no issue closed; the worktree stands. `review_sha` is
`cd8dae476607704fd3d2b874150aae9f814292d2`, parent issue #924 and all ten sub-issues are at Review,
the working tree is clean, `check-state.sh` exits 0, and no source has moved past the pin.
