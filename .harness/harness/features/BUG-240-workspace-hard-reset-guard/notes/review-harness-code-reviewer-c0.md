# Code review — BUG-240 workspace hard-reset guard — cycle 0

Pinned: `ed047fde93d367d52d09d665bac8c6957667ac0c`, diff base `3e3147eb` (BUG-240 plan commit).
Files reviewed, both: `.claude/skills/harness/bin/factory_workspace.py` (+46), `tests/unit/test-factory-workspace.py` (+199, +4 docstring). Read at the pin via `git show ed047fde:<path>`; the worktree is clean at these two paths (`git status --porcelain` empty for both), so line citations below match both the pinned blob and the working tree.

**VERDICT: PASS.** No must_fix. Two med, non-blocking, non-scope findings below.

## Stage 1 — spec compliance

| REQ/SC | Status | Citation |
|---|---|---|
| REQ-01 self-checkout stop, no mutation | met | `factory_workspace.py:142-151` (`os.path.realpath(path) == os.path.realpath(_control_plane_root())` → `factory_cli.refuse`), runs before both `isdir(.git)` branches at :153/:166 |
| REQ-02 dirty-checkout stop | met | `factory_workspace.py:153-164` (`run_git(["status","--porcelain"], path)`; `if dirt.strip(): factory_cli.refuse(...)`) |
| REQ-03 stop names path+condition, refuse grammar, EXIT_REFUSED | met | both blocks call `factory_cli.refuse(tool="workspace", what=…, value=os.path.abspath(path), next_step=…)`; `refuse()` → `sys.exit(EXIT_REFUSED)` (`factory_cli.py:50-52`, confirmed read-only, not under review) |
| REQ-04 ignored-only dirt not stopped | met | `status --porcelain` at :154 carries no `--ignored` flag, so ignored content never appears in `dirt`; test `BUG-240 ignored-only dirt: not refused` (`tests/unit/test-factory-workspace.py:378-403`) |
| REQ-05 clean/missing checkout unchanged order | met | clone branch (:166-170) and refresh branch (:172-176, `fetch`→`checkout <default>`→`reset --hard`) untouched by the diff; both guards are read-only (`os.path.realpath`, `os.path.isdir`, `git status --porcelain`) so they add no destructive call and no reordering; pinned by `BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard` (`tests/unit/test-factory-workspace.py:212-218`) plus pre-existing cases (A)/(B)/(C) |
| REQ-06 no bypass | met | see SC-06 below |
| SC-01 dirty tracked: refused, names path+condition, file survives | met | `tests/unit/test-factory-workspace.py:334-345` (case 1, Recorder, exits 2 before fetch/reset/clone), `:347-376` (cases 2/3, **real git** via `real_repo()`, asserts stderr line + byte-identical survival) |
| SC-02 ignored-only dirt not refused | met | `tests/unit/test-factory-workspace.py:378-403` (case 4, real git, asserts exit 0/None, `junk/scratch.txt` survives, issue branch checked out) |
| SC-03 self-checkout refused when clean, names self-checkout condition | met | `tests/unit/test-factory-workspace.py:405-423` (case 5: `Recorder(porcelain="")` — clean — with `_control_plane_root` stubbed to the target; asserts `"control-plane" in err_lines[0]` and `"uncommitted" not in err_lines[0]`) |
| SC-04 clean/missing checkout unchanged, ordered | met | see REQ-05 row; also case 6 (`tests/unit/test-factory-workspace.py:431-452`) proves D-01's negative half — an onboarded-but-different harness checkout is NOT refused, `fetch` still fires |
| SC-05 `run-unit-tests.sh --kind unit` exits 0 | met (not independently re-run here) | I ran `tests/unit/test-factory-workspace.py` directly under `env -u HARNESS_AGENT_TYPE`: 38/38 checks, exit 0, 0 lines matching `^FAIL `. The aggregate `run-unit-tests.sh --kind unit` invocation across the whole `tests/unit/` tree is QA's verification remit (peer `BUG240Qa` is running this panel concurrently); running it here would be project-wide validation outside this review's scope. T-02's own verify chain already requires and (per `status: done`) satisfied it. |
| SC-06 no bypass, verify: inspection | **met — see full citation below** | |

### SC-06 — explicit citations (this is the one criterion this review discharges)

- **Refusal site 1** (self-checkout/identity): `factory_workspace.py:142-151`.
- **Refusal site 2** (uncommitted work): `factory_workspace.py:153-164`.
- **Argument parser**: `factory_workspace.py:129-133` — `parser.add_argument("--repo", …)`, `("--issue", …)`, `("--fleet", …)`, `args = parser.parse_args()`. Exactly three flags; none named force/yes/skip and none reach either refusal block as a condition.
- **No flag, argument or environment variable skips either refusal.** I grepped the full pinned file (case-insensitive) for `force`, `--yes`, `environ`: the only environment read is `os.environ.get("FACTORY_GIT", "git")` inside `run_git` (line ~70) — a pre-existing test-injection seam that predates `3e3147eb` (out of this diff's scope per the batch context) and selects which `git` binary is invoked; it does not gate or skip either `factory_cli.refuse` call. `_control_plane_root()` (`:51-57`) calls `harness_boundary.root_from_script`, confirmed pure arithmetic with zero environment reads and zero filesystem access (`harness_boundary.py:57-64`, read-only, not under review) — so no `HARNESS_PROJECT_DIR` or similar override can redirect what the identity check compares against. Test case 7, `BUG-240 no bypass: the parser rejects --force` (`tests/unit/test-factory-workspace.py:460-474`), asserts `argparse` rejects `--force` (exit 2) and that the shipped source text of `fw.__file__` contains none of `--force`, `--yes`, `FACTORY_FORCE`.

**SC-06 verdict: MET**, with the above as the reviewer's own citations (not a restatement of the test's claim).

### Correction of record, confirmed at source

BUG-240 cases 2, 3 and 4 drive **real git**, not a monkeypatch: each calls `run_main(fw.run_git, …)` (`tests/unit/test-factory-workspace.py:358`, `:396`), which inside `run_main` does `fw.run_git = rec` — i.e. `fw.run_git` is reassigned to itself, a no-op substitution, so the actual `subprocess.run([...])` path executes. `real_repo(wr)` (`:166-184`) builds a real bare origin and a real pushed checkout via `subprocess.run(["git", …])`, no network. Case 3 shares case 2's single `run_main` invocation and asserts `tracked.txt`'s bytes afterward — a genuine regression reproduction of the original defect (pre-guard, `reset --hard` would have overwritten `second_content` back to the first commit; post-guard the refusal fires before `fetch` and the file is never touched). Cases 5 and 6 do use `Recorder` (mocked `run_git`) but exercise a real, unconditional monkeypatch of `_control_plane_root` under a documented try/finally restore.

## Stage 2 — code quality (fail-open hunt + general)

Checked per the assignment's four specific questions:
1. **Ordering** — both refusals run before `isdir(.git)`/the clone-or-refresh dispatch (:166); confirmed by reading `_main` top to bottom, no reachable path skips them.
2. **Error-path fail-open** — `run_git(["status","--porcelain"], path)` failing (non-zero exit) raises `RuntimeError`, which is **not** in `factory_cli.run`'s `expected=(FleetError,)` tuple, so it falls into the `BaseException` trap (`factory_cli.py:88-96`) and still exits 2 — fails closed, never proceeds to the destructive branch, just with the "unexpected failure" wording instead of `refuse()`'s. `os.path.realpath` does not raise on a non-existent path in CPython. An empty/whitespace `status --porcelain` is legitimately "clean" (`dirt.strip()` false), not a fail-open — that is exactly what a clean checkout's porcelain output is.
3. **Refusal mechanism** — confirmed both blocks go through `factory_cli.refuse(...)` → `EXIT_REFUSED`, never a bare `RuntimeError`.
4. **`_control_plane_root()`** — confirmed `root_from_script`, not `resolve_root` (`:57`); the module docstring (:21-24) and function docstring (:52-56) both explain why, matching D-01/T-02's intent.

### Finding 1 (med) — unaddressed TOCTOU window between the dirty-check snapshot and the destructive commands

`factory_workspace.py:153-181`: the dirty check is one `git status --porcelain` snapshot, taken once. Between that read and `git reset --hard origin/<default_branch>` (`:181`), the refresh branch runs a real network `fetch` (`:178`) and a `checkout` (`:179`) — real wall-clock time. If another process writes uncommitted content into the same checkout during that window — precisely the "three flows running against it" scenario the BRIEF's own 2026-08-10 incident describes — the earlier snapshot read it as clean, and `reset --hard` destroys the new write anyway. This is not a bypass reachable via any flag/argument/env var (REQ-06 unaffected) and no REQ/SC in this BRIEF asks for locking or re-checking, so it is not a spec violation and not `must_fix`. It is a narrower residual instance of the exact defect class (check-then-act around a destructive git operation) this feature exists to close, worth a follow-up ticket rather than blocking this one.

### Finding 2 (med) — `code_grade: grade_2`, driver `_main`, reasoned

`python3 .claude/skills/harness/bin/code-grade.py --base 6d969ed375f8458e32c47502ecdcc85bb9916635 --head ed047fde93d367d52d09d665bac8c6957667ac0c` (base = `git merge-base origin/main ed047fde`, matches `lanes.resolved_at` in `plan.yaml`):

```
FUNCTION .claude/skills/harness/bin/factory_workspace.py:128 _main
CYCLOMATIC: 5  COGNITIVE: 7  ABC: 33.0  GRADE: 2  DRIVER: abc  BAR: 4  RESULT: FAIL  SEVERITY: med
```
`_control_plane_root` (new, grade 5) and the two other changed/touched test functions all pass; `_main` is the sole grade-2 record and the sole driver of `code_grade`.

**Reasoned answer (REASON REQUIRED: _main):** the regression is entirely in ABC (33.0 vs bar 20), not cyclomatic (5, well under 8) or cognitive (7, under the grade-4 bar of 9). Both added guard blocks are flat, single-level `if` statements — no added nesting — but each calls `factory_cli.refuse(tool=…, what=…, value=…, next_step=…)`, and ABC counts each keyword argument's assignment/branch surface. The function is still one linear sequence — parse args, load fleet, identity guard, dirty guard, clone-or-refresh, checkout issue branch, emit payload — each step legible on its own; a reader does not have to hold nested state. Acceptable as an orchestration entrypoint at its current size; a third guard would be the point to extract `_refuse_if_unsafe(path)` to bound ABC growth. Not `must_fix` — grade 2 does not block the build per policy.

No other Stage 2 findings: comments (`POINT OF NO RETURN`, docstring's refusal paragraph) stay accurate against the code they describe; no dead code, no unhandled-error regression, no copy-paste divergence introduced by this diff.

## Not re-raised (per batch contract / plan.yaml panel disposition — settled)

F-01 (ordering only through `run_git` seam), F-02 (source-text grep for three literal spellings, PF-d795aab0…, `disposition: open`, operator kept), ALT-5 (dirty check over-reaches to untracked-non-destroyable content, deliberate per SC-04's own pinned assertions). Also not re-raised: PF-ff733189… (containment premise unfixtured) — `disposition: open` in `plan.yaml`'s `panel:` block, adjudicated at signature per this review's batch context.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both refusals sit before the first destructive git command, travel through factory_cli.refuse/EXIT_REFUSED, use root_from_script (not resolve_root), and no flag/arg/env var reaches either — all REQ/SC met with citations; two med non-blocking findings (TOCTOU window, code_grade grade_2 on _main)."
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  reviewed: "3e3147eb..ed047fde93d367d52d09d665bac8c6957667ac0c"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-240-workspace-hard-reset-guard/.harness/harness/features/BUG-240-workspace-hard-reset-guard/notes/review-harness-code-reviewer-c0.md
```
