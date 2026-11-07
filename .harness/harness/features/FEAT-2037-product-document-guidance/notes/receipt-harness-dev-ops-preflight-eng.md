# Receipt — harness-dev-ops — preflight-eng — FEAT-2037 (task: none, read-only; revised after eng-lead corrections)

Scope: read/grep/glob only. No shell, no checker or test run, no edit to either checkout. Only write: this receipt. No SC or gate grading; completion of this analysis is not readiness.

## A. Chronological read list (everything I read; conclusions follow in section B onward)
1. glob `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness/bin` and owner `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin` (listings).
2. grep `resolution_manifest|_owner_root` in control `.../FEAT-2037-product-document-guidance/.agents/skills/harness/bin/check-plan-routes.py` and owner `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-plan-routes.py`.
3. read control `check-plan-routes.py:60-180`.
4. grep `def worktree_owner` in control `harness_boundary.py`; read `harness_boundary.py:1040-1180`.
5. read owner manifest `/Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml` lines 1-300, 301-343.
6. read branch manifest `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.harness/team-config.yaml` lines 1-300, 301-343.
7. grep case map of `tests/integration/test-check-plan-routes.py`; read `:1-60`, `:1515-1570`.
8. read worktree `.git` pointer file; glob the feature directory.
9. grep `^def (_owner_root|resolution_manifest)` in `.claude/skills/harness/bin/check-plan-routes.py` of owner and control.
10. read owner `/Users/molchairuangutai/GitHub/harness/.git/HEAD` and `/Users/molchairuangutai/GitHub/harness/.git/worktrees/FEAT-2037-product-document-guidance/HEAD`.
11. read `notes/blocker-plan-product-2026-10-05.md` and `.agents/skills/harness/references/artifact-paths.md`.
12. grep `WORKTREES_SEGMENT|MARKER|PROJECT_DIR_ENV` in `harness_boundary.py`; grep `def manifest_domains` in `artifact_accessors.py`.
13. (revision) grep `REPO_ROOT|run(plan|...` and read `test-check-plan-routes.py:56-138`.
14. (revision) grep `test-check-plan-routes|check-plan-routes` across the feature dir; read `notes/verification-main-c0.md` in full.
15. (revision) attempt `read artifact://102` (the raw failing run recorded by main): **not found** (`Available: 3`). Failing case names therefore remain unobserved by me.
16. (revision) grep `deviation|DEVIATION` in control `check-plan-routes.py`.

## B. BLUF
- The resolver mechanism is as reported (section C), and `main()` counts a deviation as one violation (`check-plan-routes.py:2479-2482`).
- **Ground truth, not remeasured by me:** the user-reported failure (six cases failing for manifest route deviation between the feature-worktree manifest and the stale owner manifest, with `#2071` apps/packages/workspace grants absent from the owner baseline, owner main carrying dirty user logs and untracked Kaya artifacts) is recorded by main in `notes/verification-main-c0.md:8-11`. I did not rerun anything to confirm or refute it.
- **Observed now:** the owner manifest and the branch manifest read identical across all 343 lines. Both views also carry the same displayed snapshot tag `#5A2F`, which I record as an observation only and draw no semantics from. No grant is present in one and missing from the other. This is a present-state comparison only; it says nothing about the earlier state.
- main's note (`verification-main-c0.md:13,18-19`) records that the operator chose "Sync owner baseline", a fast-forward only that preserved user files and stopped on conflict. `git merge --ff-only origin/main` in the owner checkout is recorded as succeeding 652e70d4 to f35d3a72 with no stash, and the integration kind afterward as exit 0 (raw artifact://107). I did not observe that command or run. [INFERENCE: this recorded recovery is consistent with the manifests reading identical now; I did not verify the sequence.]

## C. Locating check-plan-routes.py; _owner_root and resolution_manifest
- Control copy `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness/bin/check-plan-routes.py` and owner copy `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-plan-routes.py`: the definitions appear at the same lines and the grep output shows identical text. `.claude/skills/harness/bin/check-plan-routes.py` in both checkouts also shows the same definitions at lines 108 and 168. I did not diff whole files, so "differs elsewhere" is unobserved; the test suite loads from `.claude/skills/harness/bin` (`tests/integration/test-check-plan-routes.py:12,28-31`).
```
108: def _owner_root(root):
110:     worktree = harness_boundary.worktree_owner(root)
111:     if worktree is None:
112:         return root
113:     _, owner_root, legitimate = worktree
114:     if owner_root is None or not legitimate:
115:         raise ValueError(f"cannot establish the owner checkout for {root}")
116:     return owner_root
168: def resolution_manifest(root):
170:     owner_root = _owner_root(root)
171:     deviation = _manifest_deviation(root, owner_root)
172:     return owner_root, deviation
```
- `worktree_owner` (`harness_boundary.py:1086-1164`, no git subprocess) walks up to the first `.git`. A directory means the main checkout. A file means a linked worktree: it parses `gitdir: <abs>/.git/worktrees/<id>`, takes the parent of that `.git` as the owner (`:1140-1154`), and judges legitimacy by commonpath under `<owner>/.claude/worktrees` (`WORKTREES_SEGMENT`, `:37`, `:1155-1160`).
- This worktree's `.git` line 1 reads `gitdir: /Users/molchairuangutai/GitHub/harness/.git/worktrees/FEAT-2037-product-document-guidance`, so the owner is `/Users/molchairuangutai/GitHub/harness`, whose `.git/HEAD` is `ref: refs/heads/main`.
- `_manifest_deviation` (`:119-165`) compares branch vs owner `.harness/team-config.yaml`: byte-identical fast path (`:145-147`), then parsed `artifact_accessors.manifest_domains` equality (`:150-153`, defined `artifact_accessors.py:391`); a difference or unparseable branch manifest returns `DEVIATION ...` (`:162-165`). A missing or unreadable owner manifest raises ValueError (`:140-141`). `main()` appends the deviation and adds one violation (`:2471-2482`).

## D. Manifest comparison (present state, read-only)
- Both files read in full (lines 1-300 and 301-343). The grants a pre-`#2071` baseline would lack are present in **both**: `apps/web/src/**` (:171), `apps/*/src/**` (:185), `packages/*/src/**` (:186), `apps/*/src/**/prompts/**` and `packages/*/src/**/prompts/**` (:201-202), `apps/*/src/**/schema*` and `packages/*/src/**/schema*` (:217-218), `pnpm-workspace.yaml` (:237), `pnpm-lock.yaml` (:238), `tsconfig.base.json` (:239), `apps/*/src/**/*.test.*` and `packages/*/src/**/*.test.*` (:263-264).
- Therefore I cannot name a delta between the two at this moment. The earlier delta is as stated by main (`verification-main-c0.md:11`) and is not remeasured by me. I could not observe owner git status or dirt without a shell.

## E. What the six cases assert: source-derived candidates versus the reported six
- **Unobserved:** the six failing case names (artifact://102 not available to me; `verification-main-c0.md:8` says only "six failures" and "every failure named route deviation"). I do not claim a match to any named case.
- **Source-derived candidate set.** The cases that are exposed to the owner-manifest comparison are the ones that run the checker with `cwd=REPO_ROOT` (the worktree, `test-check-plan-routes.py:76`) and no `project_dir` override, so the root comes from `__file__` and `_owner_root` resolves the owner (`:56-81`). The callers are `run(plan)` at :112, :122, :130, :139/:143, :184 and :199, plus the argv-less `run(cwd=REPO_ROOT)` at :343. They belong to these cases:
  - case_01_02_03 (:108) expects non-zero, the task id and the path in stdout. A deviation does not break it, because it already expects non-zero.
  - case_04 (:118) asserts exit 0 for an all-granted plan. A deviation (exit non-zero via `total_violations += 1`) breaks it.
  - case_05 (:126) asserts exit 0 for an ungranted plan declared main-session-direct. A deviation breaks it.
  - case_06_07 (:134) compares the wildcard run's exit status to the same plan with the wildcard removed. Both runs carry the deviation, so the comparison would still hold.
  - case_14_15 (:179) asserts a `DEVIATION` line (:185), which the plan-time deviation could satisfy, and exit 0 (:186), which it would break.
  - case_17 (:189) asserts no `VIOLATION` line naming T-01; the manifest deviation is a `DEVIATION` line.
  - case_19a (:324 onward, :343-346) compares argv-less output across cwd.
  The exit-0 assertions (case_04, case_05, case_15, and any case_19 argv-less zero-exit checks) are the ones a counted deviation reddens by construction. That reasoning is from source only.
- Not exposed: fixture-root cases using `project_dir=td` (e.g. :389-390, :565, :745-746, :1013-1014) run in a non-worktree temp root, where `_owner_root` returns the root itself. case_27 (:1515-1568) builds its own owner and branch manifests. case_41_t09 (:1666-1696) calls `_manifest_deviation` directly: comment-only difference is not a deviation, and a route difference is.
- The docstring at `:125-127` already records the same failure shape from an earlier feature ("six cases ... each runs a fixture plan against the live checkout and the deviation is counted as a violation"). That is an independent historical count; I do not equate it with this feature's six.

## F. Supported NON-BYPASS resolution and exact authorization
- The checker resolves routes through the owner manifest because that is what the write hook consults (`:1560-1564` docstring and the DEVIATION message at `:163-165`). Route grants that exist only on the branch therefore take effect for this check only once they are on the owner checkout. The supported route is landing the manifest-carrying commit on owner `main` and fast-forwarding the owner checkout. It is never a root override, an assertion change, or a manifest edit from inside the feature.
- Authorization actually recorded as given (`verification-main-c0.md:13`): the operator selected **Sync owner baseline**, meaning a fast-forward only (`git merge --ff-only origin/main` in the owner checkout), preserving the dirty user logs and untracked Kaya artifacts, and stopping on conflict. For any repeat, the same authorization is required. Anything beyond a clean fast-forward (stash, reset, checkout, clean, or a non-ff merge) needs a fresh operator decision.
- I performed none of this. This lead/dev-ops pass changed neither checkout.

## G. Injected skills in my context (actual absolute sources) and phrase delivery
- `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-handoff/SKILL.md`
- `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-expertise/SKILL.md`
- `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-principles/SKILL.md`
- `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-tdd-enforcement/SKILL.md`
- `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-code-risk-grading/SKILL.md`
- `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-craft/SKILL.md`
- `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-codebase-design/SKILL.md`
- `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance/.agents/skills/harness-digest-dev/SKILL.md`
- **No role-named `harness-dev-ops` SKILL.md was injected.** The role text came in as the agent persona (`HARNESS_AGENT_ID: harness-dev-ops`); its return contract is harness-digest-dev.
- Phrase `Consult the assigned product, not Harness`: **PRESENT**, delivered inside the injected harness-principles skill text (first bolded rule: "**Consult the assigned product, not Harness.** Resolve `<product-checkout>` ..."). I did not open any craft leaf.

## H. Open questions
- Failing case names for the six reported failures: artifact://102 is not readable by me. If main wants the match, the case list from that raw output must be read by someone who has it.
