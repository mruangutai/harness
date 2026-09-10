## BLUF

The operator's expectation is CONFIRMED, and stronger than stated: once T-08's sparse cone lands, `check-state.sh`, `board_lifecycle.py`, `check-plan-routes.py` and `validate-feature-json.py` need **zero corpus reads at all** for their per-feature invariants — their existing local globs against their own root already do "current feature and nothing more," because a converged worktree materialises exactly one feature. D-11's five-script relocation is **wrong as scoped**: only **one** of the five (`layout_migration.py`) genuinely needs the corpus root, and for a reason the plan never named — its MIXED-layout detection is a whole-corpus *structural* property, not a per-feature verdict. D-12's cwd union is **moot**, not merely unnecessary: with no ref-resolved corpus set to union into, there is nothing to union. The plan shrinks from 16 tasks to **9** (T-01 narrowed, T-02/T-08/T-09/T-10/T-11/T-15/T-16/T-17 kept, T-03/T-04/T-05/T-06/T-07/T-13/T-14 all shrink or partially delete), 4 decisions overturned (D-11, D-12) or narrowed (D-04, D-09), and the two carve-out conditions resolve cleanly: FEAT-02's `branch` corrects to `"none"` (one field, evidence below), and the placeholder test is specified.

---

## (1) Re-derived ledger, site by site

**check-state.sh, every glob site** (`glob.glob(os.path.join(H, "*", "features", "*", ...))`, all at `.claude/skills/harness/bin/check-state.sh`). `H` is resolved from this checkout's own root (`:38-47`), never a second `os.getcwd()`. Under T-08, a converged worktree's `H/*/features/*` contains exactly one entry — its own. So **every** invariant below that loops that glob is, unmodified, "current feature and nothing more" today; nothing needs to change in them.

| INV | Site | Class | Why |
|---|---|---|---|
| 1/2 approval | `:283-303` (loop `:294`) | (a) | own BRIEF.md + own plan.yaml station |
| 35 truncated `#NNN` | `:242` | (a) | own plan.yaml raw text |
| 3/4/5 PLAN.md legacy | `:561-586` | (a) | own PLAN.md / STATE.md |
| 32 panel record | `:426-559` (loop `:428`) | (a) | own plan.yaml `approval`/`panel`; `panel_era_start` is host config, not corpus |
| 6/7/8/12/22/33 | `:608-845` | (a) | own feature.json + `git log` scoped to that one file's own plan.yaml path (`:606-760`) — git history of ONE path, not a corpus walk |
| 9 platform prereqs | `:847-965` | n/a | reads `.claude/settings.json`, no feature loop at all |
| 17 handoff seams | `:1151-1286` | (a) | own notes/handoff-*.md + own plan.yaml exemption |
| 18 orphan runs | `:1290` | (a) | own runs/ dir vs own feature.json |
| 34 every feature has plan.yaml | `:1312` | (a) | presence of its own file |
| 23 line budgets | `:1341,1376` | (a) | own feature.json/STATE.md; CLAUDE.md is single repo-root file, not corpus |
| 15/16/36/37 run digests | `:1433` | (a) | own runs/*/state.yaml + own feature.json |
| 19 glossary | `:1616` | n/a | single repo doc, no feature loop |
| 21 mirrored no parent | `:1630` | (a) | own feature.json github block |
| **24 issue collision** | `:1669` (`_fac_pairs`) | **(c)** | genuinely cross-feature: `_fac_pairs[key] != feat` compares **every** feature's `factory.issues` against every other's. Concrete case named in the code itself is exactly the shape the operator's carve-out targets. **This is the natural second consumer of the uniqueness index** — the index already carries `issues`, so INV-24 becomes an in-process lookup against the SAME row set `merge-gate.feature_for` uses, not a second corpus walk. |
| 28 Done, no PR | `:1780` | (a) | own feature.json |
| 13 github block sanity | `:2499` | n/a | host config, no per-feature loop |
| 25 worktree location | `:1802-1907` | n/a (different axis) | enumerates *worktrees* via `git worktree list`, not features |
| 29 worktree terminal | `:1908-2061` | n/a (different axis) | same — each worktree reads its own local station; no corpus read |
| 26 board vs plan | `:2107-2391` | (a) | per card: own plan.yaml + own feature.json + one `gh` network call; iterates to *build* the candidate set but each verdict is single-feature |
| **27 layout MIXED** | `.claude/skills/harness/bin/layout_migration.py:180-192` (`_evidence`), invoked from check-state.sh `:2518-2529` | **(c)** | `_evidence` builds `legacy` vs `candidates` counts by globbing `.harness/features/*` (old shape) against `.harness/*/features/*` (new shape) **across the whole tree** — "is the corpus MIXED" is a property of the corpus, unanswerable from one feature's directory. Invoked from inside a worktree, this call needs the OWNER ROOT, not the local cone, or it silently under-counts and can never observe MIXED with only 1 feature visible. This is the one genuine D-11 relocation candidate. |
| 30 Done vs open milestone | `:2425` | (a) | own feature.json + one `gh` call |
| 31 hooksPath | `:2584` | n/a | host git config, no feature loop |

**check-plan-routes.py**, two sites named in the plan:
- `:678` (`seg_dirs = glob.glob(feats)` + `os.scandir`) — discovery walk for route-correctness checking. Each feature's route validity is self-contained (a task's `files:` against its own domain grant). **But** this discovery walk is invoked ONLY from CI (`.github/workflows/tests.yml:153`, a plain `actions/checkout@v4` with no sparse step per T-02's own text) and interactively with an explicit single plan path (`harness-spec-driven/SKILL.md:91`). It is never observed invoked from inside a sparse worktree. Class (a), and arguably not even armed today.
- `:835` (`check_invariant_number_collisions`) — **(c)**, genuinely cross-feature: compares every unbuilt feature's declared/inferred `INV-NN` tokens for collisions, the exact shape that shipped a real defect (`:800-810`, FEAT-26/FEAT-34, two features both using INV-28). Not solvable by the id/branch/issue index — it needs the full plan/BRIEF prose text of every unbuilt feature. If ever run from inside a worktree, this needs `corpus_features(path)` + per-feature local reads at the corpus root (content, not history — these are unbuilt, unmerged-branch features that may not even be on the default ref).

**board_lifecycle.py** `_feature_dirs` (`:476-477`) — **(c)**. Board reconciliation (`provision`/`audit`/`reconcile`) is a deliberate whole-board tool comparing every card to every feature's station; it is invoked manually by the operator (`harness-add-repo/SKILL.md:113,137`), never automatically from inside a feature worktree in today's operational surface. If ever run from a worktree, needs `corpus_features`.

**validate-feature-json.py** `:43-46` — (a) once narrowed: schema validation of one feature.json needs nothing beyond that file. Invoked only by CI (`tests.yml:101`, full checkout, no args) today.

**merge-gate.py** `feature_for` (`:132-142`) — **(b)**. The branch being merged names an arbitrary feature, not "current" — this is the canonical uniqueness-index consumer, exactly as T-05 already (correctly) designed via the Q4 ruling (candidate-by-name, local open, no `corpus_read`).

**check-domain.sh**:
- `_hardlink_plan` (`:2018-2036`) — **(c)/(b)-shaped**: an inode identity attack can target ANY feature's plan.yaml via a hardlink on the same filesystem, so this must scan the corpus's on-disk inode set — `corpus_features(root, provider="path")`, D-04's path provider, unaffected by the current-feature ruling. T-06's existing design here is correct and necessary.
- `SWEEP_GLOBS`/`_SWEEP_PATTERNS` (`:1052-1069`, consumed `:2147,2150-2151,2267-2271`) — **reclassifies to (a), and the planned conversion becomes unnecessary**. The "fail-open" T-06 named (a sparse worktree's glob sees only 1-of-88) is exactly the behaviour the operator just ruled correct. Both the root scan and each sibling-worktree scan (`linked_worktrees`) already only ever see that ONE checkout's own materialised feature post-T-08 convergence — `.harness/*/features/*` naturally collapses to the single entry with zero corpus reads. T-06's planned per-feature-suffix conversion solves a problem that no longer exists; drop it.

**branch-create-gate.sh** flow-prefix lookup (`:88-90`) — **(b)**. The flow being created by definition has no local materialisation yet (it doesn't exist as a worktree), so this must search beyond "current feature" — `corpus_features(root, provider="path")`. T-16's design is unaffected by the ruling.

**"How does each narrowed reader resolve 'current feature'?"** For every class-(a) reader above, there is **no resolution step at all** — "current feature" is simply whatever `glob(root/.harness/*/features/*)` returns locally, which is one name in a converged worktree and every name in a plain checkout (owner root, CI clone). No argument, no env var, no branch derivation. Run at the owner root or on the default branch with no worktree (the "none" case the BRIEF asks about): the glob returns the *entire* corpus, which is correct — there is no single "current" feature at the owner root, so every feature is graded, same as today. Class-(b)/(c) readers resolve an *explicit* target (a branch name, a flow id, a corpus-wide structural count) that is never "current feature" by definition — those are the ones that call the corpus API.

**Invocation sites of the five formerly-relocating scripts** (`.github/workflows/`, `.claude/commands/`, `.claude/skills/`, `.claude/agents/`, `bin/`, `tests/`):
- `check-state.sh` — `.claude/commands/harness.md:12` (agent-facing, run from inside whatever checkout is active — worktree or owner root); `tests.yml:305` (CI, full checkout). Current-feature narrowing changes nothing for either caller — both already get exactly what they should.
- `check-plan-routes.py` — `tests.yml:153` (full checkout, unaffected); `harness-spec-driven/SKILL.md:91` (explicit single-path arg, unaffected).
- `validate-feature-json.py` — `tests.yml:101` only (full checkout, unaffected).
- `layout_migration.py` — `tests.yml:231` (full checkout, unaffected — no worktree problem exists in CI) **and** `check-state.sh:2518-2529` (the one call site that DOES run from inside a worktree and DOES need the owner root).
- `board_lifecycle.py` — `harness-add-repo/SKILL.md:113,137` only, manual operator invocation, not observed from inside a feature worktree.
No CI workflow rewiring is needed: every CI invocation already runs on a full, non-sparse checkout (`tests.yml:50`, plain `actions/checkout@v4`), so none of this feature's worktree-scoping questions apply there at all.

---

## (2) The uniqueness index, designed

- **Placement**: `harness_boundary.py`, new function `corpus_uniqueness_index(root, ref=None)` beside `corpus_root`/`corpus_features`/`corpus_read` (D-01's module; same seam, same import graph 28 files already share).
- **The single git command, measured**: `git archive <ref> -- '.harness/*/features/*/feature.json'`, piped in-process to a tar reader that extracts `feature_id` (from path), `branch`, and `factory.issues` per member — **one git invocation**, not one `git show`/`git cat-file` per feature. Measured at HEAD (`805e772f`) on this host: **0.060s wall, 317440 bytes, 161 feature.json members** (`git archive HEAD -- '.harness/harness/features/*/feature.json' | wc -c`; member count via `tar -tf -`). A simpler single-field probe, `git grep -n '"branch"' HEAD -- '.harness/harness/features/*/feature.json'`, ran in 0.046s and found **79 matches** — this is likely the operator's 79; I could not reproduce their 5848-byte figure (my raw grep output is 12563 bytes, because it includes full matched lines) and report the discrepancy honestly rather than force agreement. Either single-invocation shape satisfies "one read, not a corpus walk"; I recommend `git archive` because it is the only one that also yields `factory.issues` without a second git call, which `feature_id`/`branch` alone (a grep) cannot.
- **Row shape**: `{id: str, branch: str|None, issues: list[int]}`. `branch` is `None` when absent, empty, or the literal string `"none"` (placeholder skip, condition two). `issues` is `[]` when `factory.issues` is absent or not a T-NN-to-number mapping/list. Nothing beyond these three fields is earned: no `pr`, no `review_sha` — no named consumer reads them from this index (merge-gate reads `pr`/`review_sha` from the single candidate's own feature.json after the index resolves it, never from the index row).
- **Named consumers**: `merge-gate.feature_for` (branch→feature lookup); `check-state.sh` INV-24 (issue-number collision, replacing its own `_fac_pairs` corpus walk); and the new branch-collision check condition one requires (below).
- **Refusal**: construction fails — `git archive` exits non-zero, or the parent process is not a git worktree at all — raises the same `CorpusIncomplete`-shaped refusal T-01 already defines, naming what failed and the corpus root tried. No N-of-M count applies here (there is no "how many rows should exist" precondition the way there is for a directory listing); refusal is binary: the read either produced rows or it did not.
- **What the fail-closed refusal in `corpus_features` still guards**, once no per-feature sweep uses it: exactly the readers that remain class (b)/(c) — `merge-gate`, INV-24, INV-number-collision, `layout_migration`'s MIXED detection, `_hardlink_plan`, `branch-create-gate.sh`. That is a real, narrower, but still load-bearing guard — an unresolvable corpus root must still deny a merge, still must not silently pass a hardlink-disguised route escape, and must still not report a false "layout clean" over a partial view.
- **Does `corpus_features` survive as a separate name, or is it a projection of the index?** Survives, separately — deletion test: removing `corpus_features(provider="path")` breaks `_hardlink_plan`, `branch-create-gate.sh`, and `layout_migration.py`'s candidate-shape count, none of which need `branch`/`issues` at all, only the feature-name set. `corpus_features(provider="history")` (the ref-resolved completeness gate) is the one that is now **unused by any named caller** once T-03/T-04's relocation is dropped — apply the deletion test to it specifically: removing it breaks nothing in this re-derived ledger. Recommend dropping the `provider="history"` mode's completeness-gate use case from T-01's scope (keep the function generically useful, but do not build the `CorpusIncomplete` N-of-M trigger (C) that only existed to serve the deleted sweep relocation).

---

## (3) Condition one — the evidence

Verified at source, HEAD (`805e772f`): `.harness/harness/features/FEAT-02/feature.json:3` and `.harness/harness/features/FEAT-03-subissue-mirror/feature.json:3` both carry `"branch": "feat/harness-native-foundation"`. Both record a `pr`: FEAT-02 `pr: 4`, FEAT-03 `pr: 15` (feature.json:4 in each), confirmed by reading the files.

- **PR #15** (FEAT-03's own record): `git log --all --oneline --grep="Merge pull request #15 " → 37a8a66e "Merge pull request #15 from mruangutai/feat/harness-native-foundation"`. The merge commit subject *itself* names the branch — this is independent, first-hand confirmation that FEAT-03's recorded branch is correct.
- **PR #4** (FEAT-02's own record): `git log --all --oneline --grep="#4)" → 04a57fcf "Replace GSD with the harness (foundation) (#4)"`. Unlike PR #15, this merge subject names **no branch at all** (`git show --no-patch 04a57fcf` confirms: two parents `86147944`/`71a2043a`, subject/body carry only the PR number, never a branch). `git name-rev 71a2043a → tags/archive/worktree-wt140~17^2` — an archived branch tag, not `feat/harness-native-foundation`. There is no independent evidence anywhere in history that PR #4's source branch was named `feat/harness-native-foundation`; that string appears in history exclusively in connection with PR #15's own, later, genuinely-named branch.
- **FEAT-01 also records `pr: 4`, and its `branch` field is already `"none"`** (`.harness/harness/features/FEAT-01/feature.json:3`). FEAT-01 and FEAT-02 share the same PR, and FEAT-01's record is the one already consistent with what PR #4's own merge commit shows (no branch name at all).

**Recommendation**: correct, not exempt — and it is a **one-field, one-record** edit, narrower than the two-field edit the operator anticipated. Set `FEAT-02/feature.json`'s `branch` from `"feat/harness-native-foundation"` to `"none"`, matching its own PR-4 sibling FEAT-01 and matching what PR #4's merge commit actually shows. Leave `FEAT-03-subissue-mirror`'s `branch` untouched — it is independently verified correct by PR #15's own merge-commit subject. This removes the collision at the record level with no invented branch name anywhere, and the corrected record agrees with the only first-hand evidence available (the merge commit itself), rather than with a value that appears to have been copied from FEAT-03's later, unrelated PR. Rejected alternative: era-exempt the pair — rejected on the operator's own stated ground ("an exemption list is a permanent carve-out purchased to avoid a two-field edit") and because the correction here is *even smaller* than two fields.

---

## (4) Condition two — the placeholder test, specified

- **File**: `tests/unit/test-corpus-uniqueness-index.py` (unit, DEC-213 — no subprocess, no fixture worktree; pure function test of `corpus_uniqueness_index`/the branch-collision check over a constructed row list, modelled on `tests/unit/test-harness-boundary.py`'s `check()`/failures-accounting preamble, direct `python3`, no pytest).
- **Fixture shape**: a module-level list of six `(id, branch)` rows standing in for the index's output (never a real git repo — the index-building git call is exercised separately in `tests/unit/test-corpus-boundary.py`'s existing conventions): `FEAT-01→"none"`, `FEAT-15-domain-product-base→"none"`, `FEAT-19-central-product-config→"none"`, `FEAT-28-ci-wiring-asserted→"none"`, `FEAT-02→"feat/harness-native-foundation"`, `FEAT-03-subissue-mirror→"feat/harness-native-foundation"`.
- **Assertions**, individually:
  1. Running the collision check over the four `"none"` rows alone produces **zero** findings.
  2. Running it over the FEAT-02/FEAT-03 pair alone produces **exactly one** finding naming both ids and the shared branch.
  3. Running it over the full six-row fixture together still produces **exactly one** finding (the placeholder rows do not inflate or hide the real one) — this is the assertion that actually pins "skip absent/empty/placeholder", not case 1 alone, since case 1 alone would pass if the checker were simply never invoked.
  4. A row whose `branch` is `""` or absent (not present in the dict at all) is also skipped — two more one-line fixture rows, asserted individually, not folded into the `"none"` cases.
- **Avoiding the live-corpus trap**: the exactly-one-finding assertion above runs over the **fixture list**, never `corpus_uniqueness_index()`'s live output — so it stays green whether or not condition one's correction has landed, and never reddens the moment the correction is applied. Separately, add ONE additional integration-tier test, `tests/integration/test-corpus-uniqueness-live.py`, that DOES call `corpus_uniqueness_index()` against this repository's real HEAD and asserts **zero** collisions — this is the live regression guard condition one's correction is *for*, and it is deliberately a separate, second assertion in a separate file/tier so a future real collision reddens the live test without touching the unit fixture's pinned four-none/one-collision shape.
- **`verify:`**: `python3 tests/unit/test-corpus-uniqueness-index.py && python3 tests/integration/test-corpus-uniqueness-live.py`
- **Filed, not folded in**: `.claude/skills/harness/bin/feature-schema.json:21-24` — the `branch` property's JSON Schema is `{"type": "string"}` with no enum/pattern, so the literal `"none"` is schema-legal where a real branch belongs and nothing mechanical distinguishes a placeholder from a typo'd branch name. This is a defect worth its own ticket, not this feature's task.

---

## (5) Task and decision impact

| Id | Verdict | Evidence |
|---|---|---|
| T-01 | SHRINKS | `corpus_root`/`corpus_read` and the path-provider `corpus_features` are still needed (§1/§2). The history-provider completeness gate (case (C), `CorpusIncomplete` N-of-M) has no remaining caller once T-03/T-04 drop the relocation — cut it. Add `corpus_uniqueness_index`. |
| T-02 | UNCHANGED | Pins `corpus_root` identity in a plain checkout; orthogonal to sweep scope. |
| T-03 | SHRINKS TO NEAR-NOTHING | check-state.sh's 21 glob sites are already correct post-T-08 (§1 table). Only INV-24 changes (routes through the uniqueness index instead of its own `_fac_pairs` walk) and INV-27's `layout_migration` call needs the corpus root passed explicitly. No relocation, no two-frame REQ-05 output, no D-12 union — none of it is needed. |
| T-04 | SHRINKS TO ONE MODULE | `board_lifecycle.py`, `check-plan-routes.py`, `validate-feature-json.py` need no corpus API at all (§1). `layout_migration.py` is the one module that genuinely relocates — it is the surviving core of this task. |
| T-05 | SHRINKS | Still needed (merge-gate is class (b)), but swaps `corpus_features` completeness-gate plumbing for a direct uniqueness-index lookup by branch — simpler, no N-of-M semantics. |
| T-06 | SHRINKS | `_hardlink_plan`'s fix is unchanged and still needed (§1). The `SWEEP_GLOBS` conversion is now unnecessary — drop it; the existing literal glob already collapses to "current feature" per checkout post-T-08 with zero code change. |
| T-07 | SHRINKS | The reader ledger is far shorter — most named readers now have NO corpus API interaction to assert parity over; the parity-row mechanism still applies to the handful of genuine (b)/(c) readers. |
| T-08 | UNCHANGED, MORE CENTRAL | This is now the entire mechanism that makes "current feature only" true. Nothing in the re-derivation touches it. |
| T-09 | UNCHANGED | In-place migration of standing worktrees; orthogonal to which readers call the corpus API. |
| T-10 | UNCHANGED | Running the migration once; orthogonal. |
| T-11 | UNCHANGED | `cmd_remove` dirty-check residual; orthogonal to corpus scope. |
| T-13 | SHRINKS, REDEFINED | The lint's *rule* changes: a local glob of one's own root is no longer a violation (it never should have been). Scope narrows to flagging enumerations that reach for a SECOND feature outside the uniqueness-index/path-provider pattern. |
| T-14 | SHRINKS, CONTENT CHANGES | Still needed, but the taught rule narrows from "every feature's record is read from outside your worktree" to "you only ever need your own feature directory; the uniqueness index is the one named exception." |
| T-15 | UNCHANGED | Tests `corpus_read` as a primitive for FEAT-57's manifest paths, independent of how many sweeps end up calling it. |
| T-16 | UNCHANGED | branch-create-gate.sh is class (b) — a flow with no local materialisation by definition. |
| T-17 | UNCHANGED | Verified: enumerates **worktrees** (`.claude/skills/harness/bin/check-domain.sh:752,780,2150` calling `harness_boundary.linked_worktrees`, which lists `<owner_root>/.git/worktrees`, `harness_boundary.py:161-175`), not features — a live latent defect on a wholly different axis from the corpus-scope question. Untouched by this re-derivation. |
| D-01 | UNCHANGED (narrower scope) | API placement holds; what's built inside it shrinks. |
| D-02 | UNCHANGED (narrower relevance) | Still the right principle for the readers that remain (b)/(c). |
| D-03 | UNCHANGED | T-08's sparse derivation mechanism, now load-bearing for the whole feature. |
| D-04 | UNCHANGED | Still needed: history-first content (T-15/corpus_read) vs path-only identity (`_hardlink_plan`, branch-create-gate.sh, layout_migration's count). |
| D-05 | UNCHANGED, NARROWER SURFACE | Recorded-frame declaration still correct for whichever readers still call the API; just far fewer of them now. |
| D-06 | UNCHANGED | `cmd_remove` residual; orthogonal. |
| D-07 | UNCHANGED | `.claude/` spelling; orthogonal. |
| D-08 | UNCHANGED | T-13's lint still belongs in `tests/integration` under DEC-213; only the lint's rule content changes. |
| D-09 | NARROWED | "Complete view" for merge-gate now means "the uniqueness index built successfully," not an N-of-M corpus count. |
| D-10 | UNCHANGED | Lane correction for the migration-record path; orthogonal. |
| D-11 | **OVERTURNED** | Only `layout_migration.py` relocates (§1/§5). check-state.sh, board_lifecycle.py, check-plan-routes.py, validate-feature-json.py do not — their local globs are already correct. |
| D-12 | **OVERTURNED / MOOT** | With no ref-resolved corpus set for these four readers, there is nothing to union the active feature into — it already IS the whole local scope. Who grades the in-flight feature's invariants, and where: the SAME local glob that always did, now correctly scoped by T-08's cone rather than by a caller-side union. |
| D-13 | UNCHANGED | The cut gate-enforced-declaration mechanism stands; applies to fewer readers. |
| D-14 | UNCHANGED | `.claude/commands/**` lane; orthogonal. |
| D-15 | UNCHANGED | T-17's three-site fix; orthogonal, verified above. |

**REQ-05's two frame lines**: confirmed to have **no content to state** for the now-dominant class-(a) case — a local read at one's own root has no provider and no ref to name (constraints block's suspicion confirmed). REQ-05 should be re-scoped to apply only where a reader actually calls the corpus API (the (b)/(c) consumers) — this is a BRIEF-level change, flagged as Q1 below rather than decided here.

**SC-04's short-corpus N-of-M fixture**: reachable, but only for `layout_migration.py`'s structural count (`_evidence`'s legacy-vs-candidate shapes) — the one surviving `provider="path"` completeness use. It is NOT reachable, as originally worded, for merge-gate/the uniqueness index, whose refusal is binary (index built or not), never a count. This is also a BRIEF-level scoping change (Q2 below).

---

## (6) The size statement

**Before**: 16 tasks (T-01..T-11, T-13..T-17). **After**: 9 tasks carry unchanged intent (T-02, T-08, T-09, T-10, T-11, T-15, T-16, T-17, plus a narrowed T-01), 6 tasks shrink substantially in scope but are not deleted (T-01, T-03, T-04, T-05, T-06, T-07, T-13, T-14 — that's 8, all retained in reduced form), **zero tasks are deleted outright** — every task's remaining work is real work that still needs doing, just far less of it:

- T-03's dropped work (21-site relocation, two-frame output, D-12 union) is **not needed** — it was solving the repo-wide-sweep problem the operator just ruled invalid. Nothing to reassign.
- T-04's dropped work for `board_lifecycle.py`/`check-plan-routes.py`/`validate-feature-json.py` (relocation + gate) is likewise **not needed**. `layout_migration.py`'s relocation is the one piece that **survives and absorbs the task's remaining substance**.
- T-05's dropped `corpus_features`-completeness plumbing is **absorbed into** the simpler uniqueness-index lookup, same task.
- T-06's dropped `SWEEP_GLOBS` conversion is **not needed** — the existing literal globs already do the right thing per checkout.
- T-07 and T-13's dropped ledger/lint breadth is **absorbed into** a shorter ledger/narrower lint over the smaller (b)/(c) reader set, same tasks.
- T-14's dropped "corpus lives outside your worktree" framing is **replaced by, not deleted in favour of**, the narrower "own directory only, except the uniqueness index" framing, same task, same files.

**Not deleted, not touched by this re-derivation**: T-02, T-08, T-09, T-10, T-11, T-15, T-16, T-17 and D-03/D-04/D-05/D-06/D-07/D-08/D-10/D-13/D-14/D-15 — 8 tasks and 10 decisions carry over verbatim.

---

## Open questions (for eng-lead / operator, not decided here)

- **Q1**: REQ-05's two frame lines have no content for a local-only read (confirmed above). Recommend re-scoping REQ-05 to fire only for corpus-API callers; this is a BRIEF edit, not mine to make.
- **Q2**: SC-04's N-of-M short-corpus fixture is reachable only for `layout_migration.py`; recommend re-scoping SC-04's subject from "the five sweeps" to that one module plus the index/hardlink refusal shapes (binary, not N-of-M). BRIEF edit.
- **Q3**: condition one's recommended correction (FEAT-02 `branch` → `"none"`) is a feature-record edit this dispatch is not authorised to make (DEC-174: measurement only). Needs main-session/operator execution.
