# QA red-proof audit — FEAT-34 BRIEF (SC-01..SC-10)

**BLUF.** 0/10 SCs are structurally vacuous (no absence-only grep, no substring-only
match, no deletable invariant found among them). 1 of 10 — **SC-04** — rests on a
fixture type that does not exist anywhere in `test-check-state.py` today and the BRIEF
never names that cost, unlike the parallel cost it DOES name for SC-06/07/08. That is
the one finding that should hold up signature. Everything else is advisory.

## Per-SC verdict

- **SC-01** — falsifiable (pos/neg pair: `Done`→fires, `Review`→silent). "Demonstrated
  failing before the invariant exists" is a TDD-order claim, gradable from git history
  exactly the way `harness-verification-rules`' own audit-test-first clause already
  requires. Not gradable by `cmd`, but not a fixture problem either. **OK.**

- **SC-02, load-bearing.** Re-derived the HAZARD: `check-state.sh:22` is
  `root="${CLAUDE_PROJECT_DIR:-$(pwd)}"` at HEAD (`3ed95a4`), confirmed verbatim — the
  script reads `feature.json` from whatever `root` is, never from a resolved default
  branch. `feature-worktree.py:287` does `git rev-parse f"{default_branch}:{rel}"` —
  the mechanism SC-02 names as reusable exists and is exercised today (unlanded-artifact
  check in `remove`). **Fixture buildability:** `test-check-state.py`'s `case_u` (INV-25)
  already builds real git repos with real commits and real `git worktree add` — not
  directory trees, actual git history. It does not yet build two *branches with
  divergent committed content for the same path*, but that is a small extension of an
  idiom already proven in this file, not a new fixture class. **Both halves of SC-02 as
  written are genuinely falsifiable** by a working-tree read: a plain read of `root`'s
  copy would fire on the working-tree state in BOTH constructed cases, satisfying
  neither half correctly, exactly as the BRIEF claims. **OK, advisory only** — note the
  extension needed in the plan round so nobody discovers it mid-build.

- **SC-03** — two named clauses (dirty + decline-until-dealt-with) map directly onto
  `feature-worktree.py`'s real `WOULD DISCARD` (exit 4) behavior, confirmed present.
  "Graded per clause" is precise enough for two graders to agree IF the test asserts two
  separate substrings/regexes rather than one combined one — that discipline has to be
  enforced at build time, but the SC text already names the two clauses distinctly.
  **OK.**

- **SC-04 — MUST-FIX finding.** Needs a *second repository* under `WORKTREES_SEGMENT`
  with its own default branch, its own `Done` feature, and its own real worktree.
  Checked `test-check-state.py` end to end: the only multi-repo fixture in the file is
  `_factory_tree`/`case_s` (`FLEET_YAML`, INV-24) and it is purely declarative —
  `fleet.yaml` plus plain files, never a real second git repo or a real
  `git worktree add`. `harness_boundary.py`'s `resolve_fleet` is a path-boundary
  resolver, not a test fixture. **No fleet-repo-with-real-git fixture exists anywhere in
  this file today.** Contrast: the BRIEF's Constraints and "Verification gaps" sections
  explicitly flag the SC-06/07/08 registration cost ("registration is part of the work,
  not an afterthought") — SC-04 gets no equivalent callout, only "a harness-only
  implementation fails this case," which reads as a property of the invariant, not as an
  acknowledged build cost for a fixture class that has to be invented from nothing.

- **SC-05** — same idiom as SC-02 (real git, `case_u`-style), one repo, two features
  (one absent-on-default-branch, one `Done`). Buildable with the existing pattern.
  **OK.**

- **SC-06** — two shapes (`$1=0` ff, `$1=1` squash+commit) asserted separately, matches
  the grilling note's own measurement verbatim. Needs a new `test-*.py`; **must be
  registered in both `test_kinds.integration.detect`** (re-derived at HEAD: 22 explicit
  file entries + 1 glob) **and `run-unit-tests.sh:18`'s `INTEGRATION_SCRIPTS`** (re-derived:
  22 entries, and the 22 sets are identical today — no `KIND-DRIFT` currently). The BRIEF
  names this cost explicitly. **OK, contingent on the plan round doing the registration**
  — flagged as a live risk, not a defect in the BRIEF.

- **SC-07** — red proof is explicit ("an unguarded hook deletes it and the assertion
  fails"), needs the same new-file registration as SC-06. **OK, same contingency.**

- **SC-08** — both halves (absent-before / installed-after) named. References
  `core.hooksPath` generically, correctly staying neutral on Q1 (where the tracked
  hooks directory lives) — self-consistent with Q1 being non-blocking on signature.
  **OK.**

- **SC-09.** Counted `.claude/agents/*.md`: **16 files, confirmed.** Read every file's
  `skills:` frontmatter: only `harness-orchestrator.md` preloads `harness` (the skill
  whose `SKILL.md:325` carries "Act 3 is never yours... `git worktree remove` succeeds
  at exit 0 from inside the tree it removes"). None of the other 15 agent files list
  `harness` among their preloaded skills, and the three universal skills
  (`harness-handoff`, `harness-expertise`, `harness-principles`) do not mention worktree
  removal anywhere I found. **"Fifteen of sixteen fail today" is exactly measured, not
  approximated — 1/16 pass.** `harness-team:90` mentions worktrees but never removal,
  confirmed. Weak point: `verify: inspection` with no `evidence:` line, unlike every
  other automated SC — yet the check itself is entirely mechanical (grep each agent's
  frontmatter, grep the named skill's body for the rule), so leaving it as manual
  inspection is a criterion two different graders could plausibly score differently
  (which skill "counts" as stating the rule is a judgment call absent a fixed string to
  match). **Advisory:** recommend the plan round convert this to an automated check
  (a small script asserting, per agent, that its skill closure contains the rule text)
  rather than leaving it inspection-only forever.

- **SC-10** — "read with `git show <review_sha>:<path>`" describes the *review method*
  the grader uses, not a behavior change to `check-state.sh` itself; self-consistent
  with the standard `review_sha`-pinning idiom used elsewhere in this repo. One
  interaction worth naming: SC-10's "full `integration` kind passes" is an aggregate
  signal. If SC-06/07/08's new test files are added but NOT registered in both
  enumerations (see SC-06), the kind still reports pass — 0 files matched is not a
  failure — while SC-06/07/08 individually would correctly show as `missing` under the
  qa gate's presence rule, *provided* the grader checks named tests per SC and does not
  accept the aggregate `integration: pass` as proxy evidence for them. Not a BRIEF
  defect; a grading-discipline note for whoever runs the qa gate on this feature.

## Line-citation re-derivation (all resolved at HEAD `3ed95a4`)

`check-state.sh:22` (`root=...`), `:1076` (`git worktree list --porcelain`), `:1086-1094`
(record walk), `:1132`/`:1148` (no-removal-guidance comment / removal-guidance line) —
all resolve to the cited content. `feature-worktree.py:287` (`rev-parse
{default_branch}:{rel}`) resolves. `run-unit-tests.sh:18` (`INTEGRATION_SCRIPTS`) and
`:110-115` (`KIND-DRIFT`) resolve. `SKILL.md:321` ("Removed at a terminal state...") and
`:325` ("Act 3 is never yours...") resolve. `harness-team` SKILL.md `:90` (worktree
branch-from-local note, no removal) resolves. No wrong ranges found this pass.

## Registration-trap count

`harness.json` `test_kinds.integration.detect`: 22 explicit `test-*.py` entries + 1 glob.
`run-unit-tests.sh` `INTEGRATION_SCRIPTS`: 22 entries. **The two sets are identical
today** — confirmed by diff, no `KIND-DRIFT`. Any new file this feature adds needs both
edits or it silently matches zero files.
