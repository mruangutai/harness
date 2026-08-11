# Goal-check — FEAT-12 End copy-based distribution — d543809

> **Cycle 2 amendment (2026-08-10).** SC-04 was re-graded from `partial` to **met** after the
> inspection bound was relaxed for read-only filesystem inspection of kaya's working tree. The
> missing after-capture now exists at `notes/research-FEAT-12-kaya-agents-after.md`. **Only SC-04
> changed.** SC-05 stays `partial`, SC-06 stays `not_met`, the other eight stand. Counts in the
> original BLUF below are superseded by this line: **nine met, one `partial`, one `not_met` and
> blocking.**

**BLUF (cycle 1, counts superseded above). Eight of eleven success criteria are met on named
evidence. Two are `partial` and one is `not_met` and blocking.** The distribution mechanism is
genuinely gone from this repository and the
record: SC-01, SC-02, SC-02b, SC-03, SC-07, SC-08, SC-09, SC-10 all hold, each on a named test case
or a direct inspection, not on suite-green. What falls short is the *cross-repo evidence*:

- **SC-05 is `partial` and cannot be closed by re-running anything.** The before/after manifests are
  **path lists, not sha256 manifests**. They witness that kaya's `.harness/` still holds the same 377
  file paths; they cannot detect a content-only modification, which is the exact failure SC-05 exists
  to detect. The before-state no longer exists, so byte-identity can never now be evidenced. This is
  a plan-level problem for the operator, not a fix cycle.
- ~~**SC-04 is `partial`.**~~ **Closed in cycle 2 — SC-04 is `met`.** Skills and commands clauses are
  met on a captured `REMOTE_CLEAN` verify. The agents clause's missing after-count was captured on
  2026-08-10 by read-only inspection of kaya's working tree: `0`, with all three parent directories
  present. Evidence: `notes/research-FEAT-12-kaya-agents-after.md`. See the amended SC-04 row.
- **SC-06 is `not_met (awaiting operator UAT)` and blocking.** No runner in this repository can
  observe another repository. Script written: `notes/uat-FEAT-12-sc06.md`.

## Sha gate

`git rev-parse HEAD` → `d54380922964552dc4e0e026b3fd4419c12cbe3c`. Branch
`chore/203-end-copy-distribution`. `git status --porcelain`: ` M .harness/.../FEAT-12.../feature.yaml`,
`?? .harness/.../FEAT-12.../notes/qa-FEAT-12-qagate.md`, `?? .harness/features/FEAT-14-feature-json-schema/`,
`?? .harness/features/FEAT-15-domain-product-base/`. No source file dirty. Gate passes.

## The eleven criteria

| SC | Method | Verdict | Witness |
|---|---|---|---|
| SC-01 | automated | **met** | `test-no-distribution.py:62` `case1_absence_no_deploy_sh_tracked_anywhere`; `:65` `case1_absence_no_harness_deploy_command`; `:71` six doors survive. Absence checked directly too: `ls` returns "No such file or directory" for both paths; `git ls-files \| grep -E 'deploy\.sh\|harness-deploy'` is empty. Suite exit 0, 23/23 (qa digest) |
| SC-02 | automated (integration) | **met** | `test-check-plan-routes.py` `case_21` (def `:544`, writes the synthetic `registry.json` at `:573`) is the registry-independent fixture; the script is in `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:18`); `--kind integration` exit 0, 12 PASS at this sha with the real `~/.harness/registry.json` already deleted. **The BRIEF's "case 20" is a rotted pointer — see defect 1** |
| SC-02b | inspection | **met** | Inspected directly (inspection is the declared method): `~/.harness/registry.json` absent; `global-harness-skills-backup-2026-08-10.tgz` (322620 B) and `global-harness-agents-commands-backup-2026-08-10.tgz` (27515 B) both present. Matches T-09's verify, re-run by the orchestrator (`feature.yaml verified_on_resume`) |
| SC-03 | automated (unit) | **met** | `test-no-distribution.py:150` `case3_presence_fleet_yaml_safe_loads`, `:153` `..._exactly_two_repos`, `:157` `..._kaya_default_branch_is_master`. Two clauses have **no** standing assertion — the `mruangutai/harness` name, and `factory_config.py` accepting the file (case3 calls `yaml.safe_load` directly). I executed both at this sha: `load_fleet()` returns both repos (`main`/`master`) and `repo_entry(fleet,'mruangutai/kaya-ai')` returns the kaya entry without raising. Behavioural, one-shot — see Q4 |
| SC-04 | inspection | **met** (cycle 2; was `partial` in cycle 1) | skills+commands: **met** — T-05's verify re-run verbatim by the orchestrator returns `REMOTE_CLEAN` (`feature.yaml kaya_push`), which asserts zero `.claude/skills/harness*` and zero `.claude/commands/harness*` on `origin/master` **and** `review-team.md` present; that capture remains the grading evidence for these two clauses. agents: **witnessed** — `notes/kaya-agents-count-before.txt` = `16` (>0, no vacuous pass) paired with a captured after-count of `0` (`find .claude/agents -maxdepth 1 -name 'harness-*.md' \| wc -l`). Presence half **settled by `test -d`, which Glob cannot do**: all three of `.claude/agents`, `.claude/skills`, `.claude/commands` EXIST; `agents` and `skills` are empty directories, `commands` holds exactly `review-team.md`. Worktrees excluded by construction — `.claude/worktrees/` is a sibling, not a child, of the globbed dirs. Evidence: `notes/research-FEAT-12-kaya-agents-after.md`, kaya `master` `7d2f946`. **Sequence limitation, recorded not softened:** the after-count was captured at goal-check time (2026-08-10), **not** at T-02 time, so it witnesses the current working-tree state, not the state immediately after the deletion. SC-04 is worded against "`kaya-ai` at the state this feature leaves it in" (BRIEF:90), which is the object measured; nothing here attests the count was zero *continuously* since T-02. Corroboration only (not grading evidence): working-tree `harness*` counts under `skills`/`commands` are both 0, and `git ls-tree origin/master -- .claude \| grep -c harness` = 0. **Why the gap existed:** no commit ever touched `.claude/agents` and it is not gitignored — the 16 files were untracked local files, so filesystem inspection was the only method that could ever have evidenced this clause |
| SC-05 | inspection | **partial** | Both manifests opened. 377 lines each, `diff` empty. **Zero 64-hex fields, zero 40-hex fields — there are no sha256 hashes.** No `TOTAL_FILES` line, no `TOP_LEVEL` line, though plan T-01's intent mandated `shasum -a 256` plus both trailing lines. Top-level entries present in the paths: `codebase` (17), `expertise` (43), `features` (314), `harness.json`, `team-config.yaml`, plus `.DS_Store` — **`artifacts` and `notes` appear in zero lines**, plausibly because they hold no files, but the `TOP_LEVEL` line that would settle it is the missing one. See defect 4 |
| SC-06 | uat | **not_met (awaiting operator UAT)** | Blocking (`gates.uat: blocking_when_uat_criteria_exist`). Cannot be observed from this repository. Script at `notes/uat-FEAT-12-sc06.md` |
| SC-07 | automated (unit) | **met** | `test-no-distribution.py:95-102` — `ALLOW_LIST` is a **literal two-entry list**, commented "Declared here, never derived from what happens to be present," so it is **named in the test**, not derived: the vacuity risk the SC names does not apply. `TOKEN_RE` `:86` covers all four tokens; exclusions `:89-90` are exactly the four historical trees the SC exempts. Asserted by `case2_absence_no_unswept_distribution_tokens` `:128`, with `case2_presence_scan_reached_the_tree` `:130` guarding an empty scan set. qa mutation-proved the allow-list discriminates (removing the `test-check-plan-routes.py` entry reddens the case) |
| SC-08 | automated (unit) | **met** | Presence halves named, as required: `:211` `case4_presence_exactly_one_dec113_heading`, `:215` `case4_presence_dec113_precedence_rule_survives` (slice-scoped to DEC-113's section via `slice_section`, mutation-proved by qa's mutants A **and** B — B relocated the literal substring elsewhere in the file and the case still failed, so it is not a whole-file grep), `:240` `case4_presence_exactly_one_dec113_index_row`. Absence halves `:205`, `:232`, `:242`. **The "retains only" clause has no standing assertion**; I read the section myself — DEC-113 is now 8 lines, the crew-overrides ruling ending "resolves it first", with the ~50 lines of deploy narration gone (the `sc08_gap` closed at `8b53ebd`). Held at this sha by inspection; no test would catch its regrowth |
| SC-09 | inspection | **met** | Old heading at `d543809~11` was `### 3.3 Distribution — /harness-deploy vs /harness-init`. It is gone; no heading in `SPEC.md` contains "Distribution". §3.3 is now *The fleet — how a repository reaches the harness*, and names the checkout explicitly: `SPEC.md:409-411` "The harness is never copied into a product repository… it reaches a product repository by *checking that repository out*… There is no distribution step"; `:428` "The first factory run against it clones it under `workspace_root`; nothing is installed into it." Residual phrases noted below |
| SC-10 | automated (integration) | **met** | Positive assertions, quoted. `test-upgrade-config.py:175-176`: `check("missing-templates message points at an incomplete checkout, not the retired command", RETIRED_CMD not in out and "checkout is incomplete" in out, ...)`. `:185-186`: `check("unparsable shipped template message points at a complete checkout, not the retired command", ran_clean(r) and RETIRED_CMD not in out and "complete checkout of this repository" in out, ...)`. Both assert the replacement wording positively, not merely absence; qa mutated both replacement strings and both cases went FAIL. `grep -c -i deploy .claude/skills/harness/bin/upgrade-config.py` = **0** |

I ran `test-no-distribution.py` once directly at this sha: all 18 case-level assertions PASS, `ALL PASS`.

## REQ coverage

REQ-01 → T-07/T-08 (SC-01). REQ-02 → T-09 (SC-02, SC-02b). REQ-03 → T-02/T-05 (SC-04, partial on the
agents clause). REQ-04 → T-01/T-04 (SC-05, partial — the manifest does not measure content).
REQ-05 → T-06 (SC-03). REQ-06 → T-03 (SC-06, outstanding). REQ-07 → T-10/T-11/T-12/T-13 (SC-07, SC-09,
SC-10). REQ-08 → T-14 (SC-08). Nothing dropped. **Cycle 2:** REQ-03's agents half is no longer a weak
link — it is evidenced. The one remaining evidence gap is REQ-04's content half (SC-05), which is
unclosable rather than uncaptured.

## Record defects — measured, judged, NOT fixed

1. **BRIEF SC-02 and plan T-09 cite "case 20"; the fixture is `case_21`.** Discriminator: is the case
   number *part of the requirement* or a *pointer to it*? **Pointer.** The requirement is "the fixture
   builds its own synthetic `registry.json` in a temp dir and therefore did not depend on the real
   one" — swap `case_20`→`case_21` and the requirement is unchanged; delete the fixture and it fails.
   The behaviour is real and verified. **SC-02 is met.** Recommendation: at the operator's next
   signature, re-anchor both citations on the docstring text ("THE BEHAVIOURAL TEST") rather than the
   number — the file gets reordered, and a number anchor rots while the claim survives.
2. **Plan T-06's `verify:` can never pass.** It calls `factory_config.repo_entry('mruangutai/kaya-ai')`
   with one argument; the signature is `repo_entry(fleet, name)` — confirmed by
   `inspect.signature` at this sha — so it raises `TypeError` regardless of outcome. **A plan defect,
   not an SC defect.** I verified SC-03's own clauses directly and they hold. Recommendation: one-line
   plan correction to `repo_entry(f, 'mruangutai/kaya-ai')` at the operator's signature.
3. **Plan T-14's `depends_on` is `[T-10, T-11, T-12]` and omits T-08.** Recorded, not fixed. It blocked
   in fact: `segments-layer0-2026-08-10.md:90-94` records T-14's verify returning six hits at `ff75afb`,
   four of them in T-08's and T-11's files. A *covered* concern — no `sc_status` row.
4. **New, and the material one: the SC-05 manifest pair does not implement what T-01 specified.**
   T-01's intent mandated `find .harness -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256`
   plus `TOTAL_FILES` and `TOP_LEVEL` lines. What is on disk is a bare path list with none of the
   three. `f3452bf`'s body says T-04 re-captured "IDENTICAL, byte for byte" — that phrase is not
   supported by the artifact. Recommendation: the operator decides between (a) accepting SC-05 on
   path-set equality with the weakening recorded, or (b) restating SC-05. It **cannot** be closed by
   re-running: the pre-deletion state is gone.

## Residual observations — non-blocking, no SC row

- `SPEC.md:1925` still reads "rides the existing skill distribution" and `:1976` "commands do not
  distribute". `:1925` is falsified prose — there is no skill distribution any more. Neither is a
  *section presenting distribution as a live operation*, so SC-09 is unaffected, and no sweep in this
  feature covers the bare word "distribution". Worth a follow-up issue.
- qa's own low-severity finding stands: `ALLOW_LIST` is path-scoped, so a regression reintroducing
  `deploy.sh` prose into `test-check-plan-routes.py`'s comments would not be caught by any standing
  test (`notes/qa-FEAT-12-qagate.md:124-139`).
- No emergent success criterion was found. Everything above is either an existing SC's clause or a
  record defect.
- **Cycle 2, new and non-blocking.** Kaya's working tree at `7d2f946` shows
  ` M .harness/features/FEAT-03-live-review-loop/feature.yaml` — a content-level modification inside
  the very tree SC-05 is worded against. It makes path-set equality visibly weaker than it looks, and
  it is input to the operator's choice between accepting SC-05 as-weakened and restating it. It is
  **not** a re-grade: SC-05 stays `partial` on its recorded reasoning, and no attempt was made to
  re-derive byte-identity.
- **Cycle 2 record defect (new, defect 5).** T-02's capture design could not have worked for the
  agents clause as written: the 16 files were untracked, so only a filesystem after-count could
  evidence it, and no task step captured one. Recommendation at the operator's next signature — where
  a criterion is graded against a working tree rather than a commit, the plan task must name the
  capture command and its output artifact, as T-01/T-04 did for the manifests.
