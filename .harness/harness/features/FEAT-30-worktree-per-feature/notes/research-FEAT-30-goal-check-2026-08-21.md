# Goal-check — FEAT-30-worktree-per-feature — 2026-08-21 (pin a76d69a)

Filed under `research-FEAT-30-*` because `check-domain.sh` denies harness-pm the
`goal-check-*` filename the dispatch named; my grants are `notes/research-*.md` and
`notes/uat-*.md`. Raised as an open question rather than worked around.

**GOAL MET, with one caveat that is the operator's to rule on.** 11 of 12 criteria `met`; SC-01 is
`met-with-caveat` — its "two for harness" half is exercised only against a stand-in checkout whose
repo key is `harness`, never against this repository, and the two-level
`<segment>/<repo>/<id>` layout has **zero live instances** (`git worktree list`: this checkout plus
the legacy one-level `.claude/worktrees/FEAT-31`). All 8 REQs are traced by at least one task in
`plan.yaml`.

## Suites — measured here, exit captured in the same command, `^FAIL ` counted

| kind | exit | PASS lines | FAIL lines | scripts |
|---|---|---|---|---|
| unit | 0 | 179 | 0 | 18/18 |
| integration | 0 | 213 | 0 | 14/14 |

Corroborates the operator's 179/0 and 213/0 exactly (`notes/qa-2026-08-21-01.md:58,61`).

## Per-SC

| SC | verdict | method I ran | evidence |
|---|---|---|---|
| SC-01 | met-with-caveat | ran integration | `test-feature-worktree.py` `case_isolation:194`, `case_branch_isolation:216`, `case_layout:161`; 16+10+4 assertions green. Fixture `build_fixture:77` — repoA stands in for harness, repoB declared in a real `fleet.yaml` (`default_branch: master`) |
| SC-01b | met | ran integration + own 3-trial predicate probe | 14 assertions green (case A `:685`, case B `:766`); my probe: 4/4 committers succeed and `assert_commit_isolation` raises `IsolationViolation` on 3/3 shared-checkout trials, so the `committer_failed` short-circuit (`:788`) did not fire |
| SC-02 | met | ran integration | `case_cut_point:239` — merge-base vs pre-create tip, per worktree, per repo (main and master); 4/4 green |
| SC-02b | met | ran integration | `test-check-domain.py:1998` accept, `:2010` refuse naming where worktrees belong; both green |
| SC-02c | met | ran integration **and re-ran the pin test against 4792cd1^** | 16 named per-agent cases green at pin; roster walk `:1764` asserts exactly 16 with membership (`agent in at_root`). Pre-T-04: **16 of 16 SC-02c cases FAIL** — fail-first shown per agent, not in aggregate |
| SC-03 | met | ran integration **and re-ran the pin guard test against 4792cd1's pre-T-05 guard** | `test-bash-write-guard.py:698-718` refuse/allow pairs green at pin; pre-T-05 exits 1 with 10 failing cases, all SC-03/SC-07 refuse cases. The guard is shown able to fire |
| SC-04 | met | ran integration | `test-feature-worktree.py:397-461` — exit 5 with `MISSING <path>`, exit 0 with `VERIFIED <path>`, exit 5 with `DIFFERS <path>`. Paths named, not counted; 10 assertions green |
| SC-05 | met | ran integration | `test-check-domain.py:1661` — 16 per-agent in-worktree/root parity cases against the REAL `team-config.yaml`, through a REAL linked worktree, each asserting equality AND self-membership; roster length asserted 16 |
| SC-06 | met | inspection at pin | `harness-orchestrator.md` **lines 23-33** ("## Where you work" through the HEAD-move rule) is a followable rule: absolute worktree path, `git -C <that path>`, never move HEAD. `.claude/commands/harness.md:15-31` gives the create command and the layout. `grep -c worktree` = 2 and 6 at the pin |
| SC-07 | met | ran integration | `test-feature-worktree.py:351-384` — exit 4 with `WOULD DISCARD` for untracked and tracked dirt, tree still on disk; Bash route `test-bash-write-guard.py:739-743`; 10 assertions green |
| SC-08 | met | ran integration **and ran T-06's UNION_APPLY mutant myself** | `test-expertise-merge.py` loss demo `:72`, green union `:82`, concurrent trials `:110`. Mutant applied by name → exit 1; unmutated control → exit 0 |
| SC-09 | met | ran both suites at pin **and both at base 49c528a** (`git archive` into scratchpad) | Zero test identities lost: unit `comm -23` empty (+23 new), integration `comm -23` empty (+123 new). Both halves hold |

## Caveats the operator reads

1. **SC-01's "two for harness" is a stand-in.** `--repo harness` resolves against the fixture's own
   root, so the code path is asserted; this repository never held two worktrees at once. SC-02b
   licenses a throwaway repo, SC-01 does not say either way. Plan-level, not a build defect.
2. **Base-count label is wrong, the claim is not.** The dispatch says unit was 179/0 at 49c528a and
   "did not move". Measured: base unit is **156** PASS lines (+23 at the pin). One base script,
   `test-no-distribution.py`, cannot run in an extracted tree (`git ls-files` on a non-repo) — an
   extraction artifact, not a base failure; it passes at the pin. SC-09's real clause (nothing that
   passed before fails now) holds regardless.
3. **qa's two med findings stand; I corroborated one as latent.** SC-01b's `committer_failed`
   short-circuit can report the negative as detected without calling the predicate; it did not fire
   in 3 of my trials or the operator's 5. SC-01's static isolation assertions have no independent
   red-proof — SC-01's text does not demand one, so it does not change the verdict.
4. **SC-06 is named by no task.** Its text is met on its own terms; ownership is an artifact of the
   plan, not of the deliverable.
