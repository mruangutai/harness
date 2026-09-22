# FEAT-62 pinned code review — cycle 1

## BLUF

**PASS. Stage 1 passes the amended signed contract; stage 2 finds no actionable code-quality defect.** Reviewed exactly `16ee44f0..3d92d38b8882bf6699c4b90a2dfd06489511d085`. The fix round closes CR-02/GC-02/GC-03, and the amended SC-01/SC-09 resolves CR-01/GC-01 and the specification aspect of GC-04. No source was edited.

## Exact scope

The 21 changed paths are: `.claude/skills/harness/bin/{check-plan-routes.py,check-state.py,feature_json_write.py,harness_boundary.py,plan-merge.py}`, `.harness/README.md`, the feature's `BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`, `notes/build-divergences.md`, all five c0 notes, `tests/integration/{test-check-plan-routes.py,test-check-state-table.py,test-feature-json-merge.py,test-plan-merge.py}`, and `tests/unit/test-harness-boundary.py`. There are no `[harness:human]` commits in the range. The worktree-only change is under the feature-record `.harness/**` surface and does not alter the pinned objects reviewed.

## Stage 1 — specification compliance: PASS

| SC | Grade | Pinned inspection |
|---|---|---|
| SC-01 | PASS | The eight baseline suites' exit/stdout/stderr triples remain identical (`notes/build-divergences.md:26-50`). D-1 sorted feature order and D-3 context-first diagnostics are explicitly admitted by the amended criterion and ruled at `:52-63`; no unlisted receipt difference is recorded. |
| SC-02 | PASS | The ordered table and retired map are at `check-state.py:4401-4547`; selector parsing/intersection and deterministic execution are at `:4552-4846`; the behavioral cases are at `test-check-state-table.py:90-228`. |
| SC-03 | PASS | The module-body/reparse audit is at `check-plan-routes.py:1797-1898`; isolated executable-body and reparse mutants are at `test-check-plan-routes.py:2585-2627`. |
| SC-04 | PASS | Resource matching is operation-level for `git:<op>` (`check-plan-routes.py:1977-1987`), endpoint/resource-level for `gh:<resource>` (`:1989-1998`), and recognizes `board_stations_for` as `gh:board` (`:1950-1953,2000-2011`). Three wrong-resource mutants independently replace `gh:board`, `gh:milestones`, and `git:show` declarations and require their exact missing-resource findings (`test-check-plan-routes.py:2620-2645`); file/git/gh undeclared-input mutants and changed-path selection remain present. |
| SC-05 | PASS | Every row carries authority in the table, and live/non-struck resolution plus missing/struck mutations remain at `check-plan-routes.py:2067-2101` and `test-check-plan-routes.py:2666-2698`. |
| SC-06 | PASS | The exact changed-path census contains no workflow, hook, command-entry, or pre-commit path. The posture scan and workflow/hook mutants remain at `check-plan-routes.py:2103-2136` and `test-check-plan-routes.py:2700-2718`. |
| SC-07 | PASS | Both writer fixture checkers open the writer's sibling `.lock`, request `LOCK_EX|LOCK_NB`, print `lock=free|held`, and specifically require `lock=free`: plan writer at `test-plan-merge.py:178-215`, feature writer at `test-feature-json-merge.py:456-486`. This observation distinguishes post-release execution from execution inside the lock. |
| SC-08 | PASS | `.harness/README.md:108-112` distinguishes automatic edit-loop feedback from the full pre-commit/CI gate. `AGENTS.md` is absent from the exact diff and retains the full-check instruction; no `SKILL.md`, preload, workflow, hook, or command-entry path changed. |
| SC-09 | PASS | The table has one row per active identity and one unique run function (`check-state.py:4401-4540`), while `Ctx` owns shared loading (`:451-814`) and the runner owns ordered group/feature execution (`:4721-4777`). The exact-range grade receipt reports **325 passing, zero below bar** (production 4/5; tests 3+). The handler census and complete body-difference review below satisfy the amended extraction rule. |

### Complete `except Exception` census and differing-body review

Both endpoints contain **47 sites**: 47 at `16ee44f0` and 47 at `3d92d38b`. No site was added or removed. Every clause and every emitted message remains textually unchanged. Of the 47, 35 handler bodies are unchanged apart from relocation/indentation. The complete set of 12 bodies that differ is:

| Base location | Pin location | Exact body change | Amended-rule classification |
|---|---|---|---|
| `check-state.py:671-672` | `:561-562` | `_git_top = None` becomes `self.git_top = None`. | accumulator/context plumbing; permitted |
| `:683-689` | `:697-703` | append-to-global plus loop `continue` becomes a returned `(None, error)` record for the context cache. | accumulator plumbing + fall-through/continue extraction; permitted |
| `:948-950` | `:587-589` | `cj = {}` becomes `cj = self.cj = {}`; same message append. | context accumulator plumbing; permitted |
| `:1053-1056` | `:1834-1837` | same message append; loop `continue` becomes `return bad, warn`. | continue-to-return extraction; permitted |
| `:1329-1332` | `:782-786` | direct message append plus `continue` becomes appending the same message as a cached error tuple, then `continue`. | accumulator plumbing; permitted |
| `:1523-1526` | `:2319-2322` | same message append; loop `continue` becomes `return None, bad`. | continue-to-return extraction; permitted |
| `:1662-1665` | `:2546-2549` | same message append; loop `continue` becomes `return fy, None, bad`. | continue-to-return extraction; permitted |
| `:2064-2065` | `:3082-3083` | loop `continue` becomes `return set()` from the extracted candidate helper. | continue-to-return extraction; permitted |
| `:2282-2285` | `:3417-3420` | loop `continue` becomes `return None` from the extracted document helper; comment unchanged. | continue-to-return extraction; permitted |
| `:2727-2731` | `:618-622` | `_signed_task_hash = None` becomes `self.signed_task_hash = None`; same message append. | context accumulator plumbing; permitted |
| `:2779-2781` | `:3917-3918` | comment-plus-loop `continue` becomes `return None, None` from the extracted record helper. | continue-to-return extraction; permitted |
| `:2963-2966` | `:4346-4349` | same message append; loop `continue` becomes `return bad, warn`. | continue-to-return extraction; permitted |

The prior 48th `_dirty_paths` broad catch is gone: pinned `check-state.py:4610-4614` catches `(OSError, subprocess.SubprocessError)`. Thus CR-02 and the census portion of GC-04 are closed; the remaining 12 differences are exactly the amended SC-09 extraction-compatible forms.

### Prior-finding disposition

- **CR-01 — resolved by signed amendment:** amended SC-01 admits D-1 and D-3; the implementation matches those ruled changes.
- **CR-02 — fixed:** `_dirty_paths` is narrowed and the census is 47→47.
- **GC-01 — resolved by signed amendment:** same SC-01 disposition as CR-01.
- **GC-02 — fixed:** exact git operation, GitHub resource, and `board_stations_for` board matching plus all three wrong-resource mutants are present.
- **GC-03 — fixed:** both writer fixtures actually probe the writer lock non-blocking and assert `FREE`/`lock=free`.
- **GC-04 — fixed/resolved:** the count is 47→47; every differing body is enumerated above and fits amended SC-09.

The `OMP-PORT` numbering and duplicate `INV-37` label remain **parked operator anomalies** (`notes/build-divergences.md:74-81`); this review neither resolves nor reclassifies them.

## Stage 2 — code quality: PASS

Stage 1 passed, so stage 2 was performed. The changed production functions meet the mechanical bar. The operation/resource parser preserves token position, handles `git -C`, distinguishes `git:worktree-list`, parses `gh api` endpoints, and explicitly covers the non-argv board seam. The writer feedback remains advisory and after durable lock release. The selective checker fails conservatively when Git status cannot be obtained, while authoritative hooks/workflows retain the full checker. Inspection found no new silent failure, fail-open authoritative path, unhandled boundary error, dead compatibility path, resource leak, or actionable reader-load regression.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Amended spec and quality stages pass: all c0 findings are explicitly closed, broad handlers remain 47-to-47, and every body difference is extraction-compatible."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: pass
  reviewed: "16ee44f0..3d92d38b8882bf6699c4b90a2dfd06489511d085"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-62-check-state-decomposition/.harness/harness/features/FEAT-62-check-state-decomposition/notes/review-harness-code-reviewer-c1.md
```
