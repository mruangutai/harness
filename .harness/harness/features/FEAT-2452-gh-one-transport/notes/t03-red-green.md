# T-03 red/green evidence: lifecycle label create on the shared seam, board fixtures on FACTORY_GH only

Built main-session-direct (DEC-174) by `BuildD_T03` in this worktree, from HEAD `80bc0f7a`. `HARNESS_AGENT_TYPE` and `CLAUDE_PROJECT_DIR` were unset for every run. Raw outputs are in `t03-red-green/`. No git writes were made.

| Step | File | Result |
|---|---|---|
| C2 confinement landed first, production untouched | `01-prod-untouched.txt` | `git status`/`git diff --stat .claude/skills` are empty. |
| C2 confinement red (old board_lifecycle) | `02-red-confinement-*.txt` | test-board-lifecycle exit 1: the sentinel logs `label create abandoned --repo acme/widget --color b60205 …`, because the old `GH_SYNC_GH`-or-`gh` shell-out reached the default binary. Its LABEL apply case also FAILs because no create reached the fake. test-gh-board, test-gh-board-item-add and test-board-station exit 0, since gh_board already used only FACTORY_GH. |
| Behaviour red (old board_lifecycle, with the new label-create regression) | `03-red-behaviour-lifecycle.txt` | exit 1, 13 FAIL. For nonzero and launch-failure creates: the label is still attached, there is no failure report, and the exit is 0 rather than 1. The existing-label case FAILs on colour/argv because the create never reached FACTORY_GH. Every create also trips the sentinel. |
| Production cutover | (none) | `_ensure_abandoned_label` now calls `factory_gh.try_gh` and raises `result.error` unless `result.ok` or the pinned matcher holds. Colour b60205, the description and the absence of `--force` are unchanged. The `subprocess` import is removed. The dual-binary prose in board_lifecycle and gh_board is replaced by the single FACTORY_GH contract. |
| Green (lifecycle) | `04-green-lifecycle.txt` | exit 0, all checks passed. |
| Owned `GH_SYNC_GH`/`D-11` occurrences | `05-grep-gh-sync-gh.txt` | grep exit 1: none left in T-03's five files. |
| Literal T-03 verify | `06-verify.txt` | exit 0. 4/4 scripts PASS in 18.6 s wall, under the 60 s bound. |
| Code grades | `07-code-grade-full.json`, `07-code-grade-changed.txt` | Every changed or new function PASSes: `_ensure_abandoned_label` is 4 (bar 4), and test helpers are 3–5 (bar 3). The 8 FAILs are untouched legacy functions (`_status_findings`, `cmd_retitle`, `derive_station`, …). This was a paths-mode run filtered to the changed names; the base..head gate is Main's to run after commit. |

## Pinned label-exists matcher (cited verbatim from T-02, `gh-sync.py` `ensure_labels`)

```python
text = f"{result.stdout}{result.stderr}".lower()
exists = (isinstance(result.status, int) and result.status != 0
          and "label with name" in text and "already exists" in text)
if not (result.ok or exists):
    raise result.error
```

Only the failure action differs. The mirror calls `skip(...)`; lifecycle raises the `GhError` into `_apply_reconcile_findings`' existing per-card catch.

## Confinement shape

- `tests/unit/test-gh-board.py`: `fake_gh`/`fake_gh_failing` return a context manager (`_offline`). It applies `offline_gh_env` through `mock.patch.dict(os.environ, env, clear=True)` and calls `assert_sentinel_unused` on exit. A sentinel hit is reported as a FAIL check. Each case enters it in its `with` header.
- `tests/integration/test-board-lifecycle.py`: `_stub_env` builds its env with `offline_gh_env` and returns the sentinel log. `run` and `run_module` call `assert_sentinel_unused` after every fork.
- `tests/integration/test-board-station.py`: `run` and the FEAT-64 shim case build env with `offline_gh_env` and assert the sentinel.

## Regression (reconcile case 4b)

There are two NOT_PLANNED recorded tickets (#30, #31), giving two LABEL findings.
- **Nonzero create:** the fake prints `HTTP 403…` and exits 1.
- **Launch failure:** `run_module` patches `factory_gh.launch_gh` to raise a status-None `GhError` for `label create`, then runs the script through `runpy`.
- Both cases assert: no `issue edit --add-label`, two `fix failed` reports (so the later card was attempted), both LABEL findings in the residual, and exit 1.
- **Existing label:** the fake exits 1 with T-02's stderr shape, `label with name "abandoned" already exists; use `--force` …`. Both cards get the label and the exit is 0. The create argv carries `--color b60205` and the description, never `--force`.
