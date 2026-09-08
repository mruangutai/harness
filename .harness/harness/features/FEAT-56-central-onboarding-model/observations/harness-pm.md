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
