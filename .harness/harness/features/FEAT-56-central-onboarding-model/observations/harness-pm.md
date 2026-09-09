# Observations - harness-pm

- 2026-09-08: FEAT-56 audit — a dispatch premise stated .claude/skills and .agents/skills are HARDLINKED; measured islink('.agents/skills')=True -> ../.claude/skills and st_nlink=1, so it is a directory SYMLINK and a whole-file Write cannot desync the trees. The real desync surface is .omp/agents vs .claude/agents (distinct inodes, diff -q differs), policed by check-omp-port.py:126-166 + sync-agent-adapters.py. Verify a stated filesystem mechanism before designing a risk around it.
- 2026-09-08: FEAT-56 — issue #206 (2026-08-10) had its replacement item 2 struck by an operator ruling recorded only in wayfinding map #336's BODY (2026-08-18), not on #206. Reading the ticket alone would have planned a struck placement; the map/execution pair (#336 map, #498 build record) is where onboarding-era rulings actually live.
- 2026-09-08: FEAT-56 plan draft. templates/team-config.yaml is NOT yaml.safe_load-able at 4b5dbb23 (flow sequence with unquoted '## Approval' at line 28), so a loadability conjunct in a verify is unmeetable — caught only by running all eight verify blocks against the unbuilt tree; seven were red on a grep, one on a parse error.
- 2026-09-08: running every task verify pre-change is the cheapest discrimination proof I have found: exit 2 with a python 'can't open file' message distinguishes 'test file not written yet' from a real red, and it also caught a 15.9s three-suite chain that would have been a 48s one had I put test-check-state.py in it.
- 2026-09-08: FEAT-56 plan fix. A new conjunct added to an existing `&&` verify chain must go FIRST when it is the one the fix targets: placed later, an earlier conjunct exits first on the pre-change tree and the new check's red is assumed rather than observed. Placing it first let me paste EXIT 1 with the exact ParserError.
- 2026-09-08: FEAT-56. `plan-merge.py amend --show` prints the field body then a trailing `sha256:` line; take the sha from that same invocation, since another spawn's amend invalidates it. Two amends on one task (verify then intent) each need their own `--show`.
- 2026-09-08: FEAT-56 T-05. A false justification clause in an intent ("keep the file loadable by yaml.safe_load") survived a whole plan draft because no verify loaded the file. When an intent asserts a current-state premise, the task's verify must measure that premise, or the premise is unfalsifiable prose.
- 2026-09-08: FEAT-56 plan-fix c2. A panel finding's remedy string must be greped before it is
  written into a verify: the digest's own remedy for gh-sync.py named `default branch` PRESENT, and
  that string already sat at gh-sync.py:673 in an unrelated board comment, so the assertion would
  have been green before the task ran. Narrowed to `on its default branch` (0 matches). Same sweep
  killed `default branch` as the SPEC.md discriminator (5 matches) while keeping it for BUILD.md (0).
- 2026-09-08: FEAT-56. Proving an ORDER conjunct red is not possible on the pre-change tree — every
  presence conjunct ahead of it short-circuits first. Two /tmp fixtures that satisfy every presence
  conjunct and differ only in marker order (good -> exit 0, DB=1 FL=2 SG=3; bad -> exit 1, DB=2 FL=1
  SG=3) is what actually demonstrates the clause discriminates.
- 2026-09-08: FEAT-56. check-state.sh:534 expects THREE panel readers (should-not-exist, scope,
  goalcheck) and appends a bad line for any absent one, but only for plans whose approval.status is
  approved (:427). A plan-panel that ran two readers therefore transcribes clean and fails the state
  check the moment the operator signs. Recording a reader that did not run to avoid that would
  falsify the record; it goes up as an open question instead.
- 2026-09-08: FEAT-56. This BRIEF already used `evidence: <kind>` as a nearest-active-kind LABEL
  while the criterion named its own exact command (SC-08, SC-10 both do it). Reclassifying SC-01 the
  same way is convention-consistent, but the gap is real, so it went into `## Verification gaps` as
  its own bullet rather than being left implicit.
- 2026-09-08: plan-merge amend refuses a list field with exit 4 unless --yaml-value is passed, and --show needs the same flag; the refusal message names the reason, so read it rather than reaching for apply (which would exit 7 CONFLICT on a shrunk list anyway). Dropped T-02's phantom tests/unit path this way.
- 2026-09-08: set-panel REPLACES the whole panel mapping, so the safe route is to yaml.safe_load the plan's own panel, mutate in python, safe_dump to a temp value file — a hand-retyped mapping is a silent deletion of any finding you forget. Recorded goalcheck's two MISSING rows and repaired finding 7's id this way.
- 2026-09-08: a panel finding whose id hashes an edited summary is unreconcilable against its own run digest; the fix is to restore the digest's original summary and recompute, keeping closure narrative in disposition/resolved_by. FEAT-56 finding 7: PF-38d92d6f... -> PF-7d760241...
- 2026-09-08: plan-merge.py amend takes `--key tasks --id T-06`, not the `--task T-06` a dispatch
  may spell; `--show` prints the current value plus the sha256 the compare-and-swap needs, and the
  amend rewrites only that field's block, leaving `approval:` bytes untouched (verified: zero
  approval lines in git diff).
- 2026-09-08: to prove "everything else carried word for word" after amending one field, load the
  task from `git show HEAD:<plan>` and from the tree with safe_load and diff the field — a plain
  git diff of a folded/literal block cannot distinguish reflow from a content change.
- 2026-09-08: FEAT-56 ship goal-check. A criterion of the form "each of N named files states X, one file:line citation per file" is met by every file whose cited line is right while a SECOND line in the same file still asserts the retired claim: templates/harness.json:5 and check-state.sh:374 both survived SC-03/SC-04 with correct citations at :2 and :111. The per-file citation rule fixes the width of the check but not its depth.
- 2026-09-08: FEAT-56 SC-06 grading. run-unit-tests.sh --kind unit exits 0 while printing four ^FAIL lines from test-factory-claim-mutation.py's by-design mutant output; the file's own banner (exit 0) and its PASS verdict line are the discriminator. Grepping the run log for ^FAIL and grepping for the OWNING file's PASS line are two different measurements.
- 2026-09-08: FEAT-56. Working tree was clean and identical to review_sha for every path SC-01's verify block reads (git diff <sha> --name-only over that exact path set, empty), so the block ran in-tree rather than against extracted blobs — cheaper, and the identity proof is what makes it equivalent. Worth establishing the path-scoped diff BEFORE choosing the route.
- 2026-09-08: FEAT-56 re-scope. "Provider-neutral" split cleanly once I checked WHICH surface carries the artifact: skills load under OMP from .agents/skills (my own skill:// resolutions prove it, with .omp/config.yml disabling the claude discovery provider), while .claude/commands/*.md load ONLY through that disabled provider. So a persona asked to make X provider-neutral must first establish whether X is a skill or a command; the answer flips the cost from 0 files to 14.
- 2026-09-08: line anchors taken from a sibling's goal-check note (check-state.sh :406/:2373/:2437) were all 1-2 lines stale at HEAD because a later fix cycle edited the same file. Re-grepped by string before citing; the note's numbers were right at ITS pin and wrong at mine.
- 2026-09-08: FEAT-56 replan. An and-chained verify hides every conjunct after the first failure; I found two dead clauses only by grepping each token separately against the file (a bare "step 2" ban that a correct renumbering would have failed, and "proceed to step 2" which wraps across a line break so a line-oriented grep never matched it). Per-token counts before writing the chain, always.
- 2026-09-08: FEAT-56 replan. Ordering a gate-registration task BEFORE the artifact it registers kept every intermediate commit green: check-instruction-paths.py builds its scan list from os.listdir, so a MAIN_SESSION_ONLY entry for a directory that does not exist is a no-op, while the reverse order reddens a gate check-state.sh runs before every commit.
- 2026-09-08: FEAT-56 replan. bash-write-guard blocked a plan-merge heredoc because the proposal text contained angle-bracket placeholders like <name>.md, which it read as a redirect target .md. Route: write the proposal with the Write tool into my own notes/research-FEAT-* path and pass --proposal <that path>; for single-field amends, pipe the value and use --value-file /dev/stdin.
- 2026-09-08: FEAT-56 replan-fix c1. A range-ban on step numbers (`! grep -qE 'steps? [4-9]'`) went stale the moment T-11 gained three KEEPs: the surviving numbering grew from 3 steps to 6, so 4 and 5 became legitimate and the ban made its own task unpassable. The ban's upper bound is a function of the KEEP set, and nothing recomputes it — narrowed to [7-9].
- 2026-09-08: FEAT-56. `test_kinds` is a non-discriminating positive grep for harness-init/SKILL.md: `--upgrade` at :221 carries `test_kinds.*.cmd`, so it stays green with the whole detection step deleted. Paired it with `harness-dev-ops`, measured on a mutant that deletes :239-418 whole.
- 2026-09-08: FEAT-56. The control-plane instantiation paragraph at harness-init/SKILL.md:279-282 splits MID-LINE at :280 (prohibition sentence ends, instantiation sentence begins on the same physical line), so "move :245-283" and "move :245-280" both describe a wrong cut; the intent had to name the sentence boundary, not a line.
- 2026-09-08: FEAT-56 T-11 — narrowing a sweep ban from `steps? [4-9]` to `steps? [7-9]`, to admit values that had become legitimate, silently unguarded two sites that spelled the banned value as the SECOND half of a compound reference ("steps 4 and 8"). The task intent enumerated seven dangling sites and asserted the verify saw each; after the narrowing only five were seen, and the assertion inside the intent stayed true-looking. Lesson: after narrowing any sweep pattern, re-run the OLD pattern and diff the hit sets — every line the old pattern caught and the new one does not is either intentionally legitimate or a hole, and there is no third case. The fix shape that preserved both properties was a second conjunct admitting only valid pairs (`steps? [1-9] and [7-9]`), not a widening of the first.
- 2026-09-08 (FEAT-56 panelfix-c1): a dispatch demanded every amended `verify` be RED today, but
  three of T-11's new conjuncts were KEEP positives over content already in the file — green by
  construction. Recording them as red would have been false; I graded them against a whole-range-cut
  mutant and a rows-removed mutant instead and said plainly in the artifact which four were red and
  which three could not be. A KEEP guard's discrimination is against the CUT, never against the
  pre-change tree.
- 2026-09-08 (FEAT-56 panelfix-c1): a step-number ban set (`! grep -qE 'steps? [4-9]'`) is satisfied
  by a document that numbers nothing, so it needs heading positives (`^### 1\.` .. `^### 3\.`) beside
  it. Proved by mutating the good scratch document to strip the numbers from its headings: every ban
  passed and only the positives fired.
- 2026-09-08 (FEAT-56 panelfix-c1): building a FULL scratch document shaped as the intent prescribes
  (not a paragraph fragment) let the whole 30-line T-10 verify run to exit 0, which is the only way
  the `DB < FL < SG` line-number conjuncts and `check-instruction-paths.py` get exercised at all. The
  panel's own adequacy note said the previous cycle never did this.
- 2026-09-08 (FEAT-56 panelfix-c1): `set-panel` replaces the whole mapping, so carried findings must
  be copied as the exact dicts loaded from disk. Verifying all 13 against
  `panel_findings.finding_id` before writing took one loop and would have caught any drift; all 13
  verified.
