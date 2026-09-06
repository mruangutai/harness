# REUSE angle — BUG-1305 simplify pass (c569d8a9)

## BLUF

One ranked finding. If only one could be applied: **F1** — `run_identity.py`'s two hand-rolled
write primitives (`inject_uid`, `record_seed`) duplicate the tree's one canonical locked
read-modify-write core, `harness_merge.locked_update` (`harness_merge.py:121-153`), and lose its
fcntl lock in the process. Everything else checked out clean (RE_RUN_IDENTITY single authority,
test-loader convention, digest.py artifact-root resolution) — reported below as "checked, no
finding" so the ranking isn't padded.

## F1 — `run_identity.py:45-104` reimplements `harness_merge.locked_update` unlocked

- **File/line**: `.claude/skills/harness/bin/run_identity.py:47-71` (`inject_uid`) and `:77-104`
  (`record_seed`).
- **Existing thing**: `harness_merge.py:121-153`, `locked_update(path, transform, timeout=None)`
  — its own docstring calls it "the one locked read-modify-write core... imported by every write
  route in this feature" (`harness_merge.py:2-4`). It already does same-directory `mkstemp` +
  `os.fdopen` write + `os.replace`, wrapped in an `fcntl.flock` (`acquire()`,
  `harness_merge.py:105-118`) that is timeout-bounded specifically so a hook caller (like the
  PostToolUse route these two functions run in, `check-domain.sh:1575-1592`) does not stall.
  `feature_json_write.py:20-22` already wraps it this way for a comparable write-once/read-modify
  case ("This module builds no lock or rename primitive of its own... a thin, schema-checking
  wrapper over `harness_merge.locked_update`").
- **What run_identity.py does instead**: both functions repeat the `mkstemp`/`fdopen`/`os.replace`
  mechanics by hand (`run_identity.py:58-63`, `:90-96`) with **no lock at all**. `record_seed`'s
  write-once guard is a bare `os.path.exists(path)` check before the write
  (`run_identity.py:78-79`) — exactly the TOCTOU pattern `locked_update`'s fcntl lock exists to
  close: two POST hooks racing on the same fresh run directory could both pass the existence
  check and both `os.replace` a marker, with whichever loses simply overwriting the other's
  witness. `inject_uid`'s read-then-append-then-replace (`run_identity.py:49-61`) has the same
  unlocked shape against `state.yaml`, the exact file this feature exists to stop from being
  clobbered.
- **Concrete cost**: two independent spellings of "atomic same-dir replace" now live in this
  tree's write path for run-identity data, one locked (every other write route) and one not. The
  next person adding a third write-once file here has two conventions to choose from, and the
  unlocked one is the one that will get copied because it's shorter and it's the one already
  living beside the run-identity code.
- **Alternative**: express both as `harness_merge.locked_update(path, transform)` where
  `transform(base)` returns the existing bytes unchanged (signals "no-op") when the write-once/
  already-injected condition already holds, and returns the new bytes otherwise. No import cycle:
  `harness_merge.py` is stdlib-only and has no dependents inside this diff that would cycle back
  through `run_identity.py`.
- **One concrete way applying it could break something**: `locked_update`'s default
  `LOCK_TIMEOUT_SECONDS` is 10s (`harness_merge.py:36`), and both call sites run inside a
  PostToolUse hook body that is explicitly documented as "best effort" and wrapped in a blanket
  `except Exception: pass` specifically so recording never turns into a new refusal
  (`check-domain.sh:1589-1592`, `run_identity.py:74` docstring "Best-effort, write-once
  creation"). Adopting `locked_update` with its default timeout would let a lock contention stall
  a tool-call hook for up to 10s — the exact failure mode `acquire()`'s own docstring warns
  against for hook callers (`harness_merge.py:108-114`). A correct adoption has to pass an
  explicit short `timeout=` (as `dispatch-guard.sh`'s route already does, per that same
  docstring), not the bare default — an apply that used the default would trade a rare lost-write
  race for a much more frequent hook stall, which is a worse defect in a best-effort path.

## Checked, no finding

- **RE_RUN_IDENTITY / marker path**: single authority. `harness_boundary.py:43-46` defines the
  regex once from `run_identity.MARKER_NAME`; `check-domain.sh:1186-1191`, `:1318`, `:2045` and
  `bash-write-guard.sh:793` all import `harness_boundary.RE_RUN_IDENTITY` rather than
  re-deriving it, and `check-state.sh:53,1482` calls `run_identity.marker_path`/`read_marker`
  directly rather than re-spelling the filename. No second spelling found.
- **`mint_uid` (`uuid.uuid4().hex`)**: `inflight_registry.py:91,461` mints `claim_id` the same
  stdlib call inline. Not a duplicate worth extracting — it's a one-line stdlib call with nothing
  to drift, not a reimplemented helper.
- **`test-run-identity.py`'s `module()` loader** (`importlib.util.spec_from_file_location`
  under-test loading): the same pattern is already repeated verbatim in at least five existing
  unit tests (`test-code-grade.py`, `test-gate-policy.py`, `test-gh-cost-log.py`,
  `test-harness-boundary.py`, `test-render-brief.py`). This diff follows the established (if
  repetitive) suite convention rather than introducing a new one — not flagged.
- **`validate-digest.py`'s refactored `check_artifact_file`**: correctly reuses
  `inflight_registry.feature_root` for root resolution rather than re-deriving it; no finding.
- **`harness_yaml._resolve_identity`** (`harness_yaml.py:511-546`): resolves session identity for
  the `identity` forensic field passed into `record_seed` — already called via
  `harness_yaml._resolve_identity(d)` at the `check-domain.sh:1588` call site, not
  reimplemented in `run_identity.py`. No finding.

## Verification

`git -C <worktree> status --porcelain` — no output (clean; no file in scope touched).
