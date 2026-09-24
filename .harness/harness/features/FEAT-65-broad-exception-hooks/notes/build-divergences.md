# FEAT-65 — operator-visible byte divergences vs baseline `4e8c73c0`

Every replaced or deleted operator-visible line, with the exact old bytes, the exact new bytes,
the ruling that retired it, and the owning case that re-pins the new bytes. Anything not listed
here is byte-identical to the baseline (SC-01 receipts: `notes/clean-pin-byte-receipts.md`).

Rulings are the grilling's (`.harness/notes/grilling-broad-exception-hooks-feat65-2026-09-23.md`):

- **R1 one template.** A hook's own failure prints `harness_boundary.hook_guard`'s one line, only
  the name slot varying; every per-hook pass-through sentence is deleted.
- **R2 absorbers deleted.** A rule-level "a bug in this rule must not flip the verdict" catch is
  removed; the defect reaches the outer guard, which never blocks and always says so.

## T-01 `check-domain.py`

### D-01 · claim rule's own pass-through sentence (site 11) — R1

- old (stderr, exit 0):
  `check-domain: claim-worktree boundary was not enforced; passing through because the guard failed internally: <exc>`
- new (stderr, exit 0):
  `check-domain: the hook failed internally (<Type>: <msg>) — passing through; this is not a pass, nothing was checked.`
- re-pinned by: `tests/integration/test-check-domain.py` — "a defect in the claim rule is no longer
  classified locally: it is named on stderr" (also asserts the old sentence is absent).
- `inflight_registry.UnreadableRegistry` keeps its BLOCKED refusal byte-for-byte
  (`test-check-domain-claims.py`, "unreadable registry" / "outside partial claim set refuses").

### D-02 · feature-checkout rule's silent absorb (site 10) — R2

- old: exit 0, nothing printed (the `except Exception: return` absorbed the defect).
- new: exit 0 and the template line on stderr.
- re-pinned by: `tests/integration/test-check-domain-worktree.py` — "[feat61] an unexpected core
  failure passes through hook_guard, named, and the allowance stands" (was "… is absorbed …").
- `harness_boundary.AmbiguousWorktree` keeps its BLOCKED refusal byte-for-byte.

### D-03 · `--resolve` manifest load, unexpected class (site 4) — R1

- old: any exception from `manifest_domains` → `check-domain: BLOCKED — the manifest does not parse, so no domain can be resolved: <e>`, exit 2.
- new: `harness_yaml.YamlParseError` (the producer's class, which also wraps its OSError/decode
  failures) keeps that line and exit 2; any other class is the hook's defect → template line, exit 0,
  no route on stdout.
- re-pinned by: `test-check-domain.py` — "a --resolve defect passes through the same guard and answers no route".

### D-04 · unexpected defect anywhere else in the body — R1

- old: an uncaught exception printed a Python traceback and exited 1 (non-blocking by DEC-100).
- new: the template line, exit 0. Same verdict (non-blocking); the diagnostic is one line the
  operator can act on instead of a traceback.
- re-pinned by: `test-check-domain.py` — "a defect reading the payload passes through with exactly
  the hook_guard line" (asserts stderr is exactly the template line and stdout is empty), plus the
  process-control pair ("KeyboardInterrupt escapes the guard", "a deliberate SystemExit keeps its own exit code").

### D-05 · Done-when validator failure text (site 22) — no operator wording change, detail widened

- old: `the Done when validator handoff_done_when.py failed — REFUSING the write (RuntimeError: injected failure)`
- new: `… REFUSING the write (RepoModuleError: cannot load 'handoff_done_when' from <path>: RuntimeError: injected failure)`
  — the validator is now called through `harness_boundary.call_repo_module` (FEAT-63's idiom for
  siblings whose contract is "never raises"); the cause type and text are still present.
- still exit 2; re-pinned by `test-check-domain-post.py` — "handoff validator exception fails closed"
  (fixture now carries `harness_boundary.py` and `run_identity.py` so the boundary can name the cause).

### Narrowings with no byte change (for the reader's trace; SC-06)

- Sites 3 and 5 (`import harness_boundary` under `--resolve` / `_run_domain`): `(ImportError,
  SyntaxError)` — the two classes `import` itself raises for a module that is missing or does not
  compile. Same BLOCKED lines, same exit 2. The entry guard uses the same pair to decide that the
  tree has no guard module and runs the body unguarded (the DEC-101 isolated-copy fixture).
- Site 9 (approval fragment YAML): classified "YAML/type/value"; `harness_yaml.load_str` already
  wraps its type and value failures in `YamlParseError`, so the caught set is
  `(YamlParseError, AttributeError)` — the latter is `.get` on a non-mapping document, the one class
  left at this boundary.
- Site 18 (feature schema): `(OSError, ValueError) + feature_schema.SCHEMA_ERRORS` keeps DENIED for
  the classes the comment there names (unreadable schema, not JSON, rejected by jsonschema); the
  injected-`ValueError` case in `test-check-domain-grant.py` is unchanged. An unrelated defect now
  reaches the guard (exit 0, template) instead of DENIED exit 2 — the signed classification's
  "unexpected defects reach the outer guard and cannot become exit 1".
- Site 19 (run-state schema): `_run_state_boundary_errors()` mirrors check-state's INV-16 set plus
  `re.error`; the two KeyError contract cases in `test-check-domain.py` are unchanged.
- Site 24 (dirty check): the internal `raise RuntimeError(_r.stderr)` became `check=True`
  (`CalledProcessError`), caught with `(OSError, SubprocessError, ValueError)`; `_found = None` as before.

## T-02 `validate-digest.py` (hook name `check-digest`)

### D-06 · unreadable hook payload (site 12) — R1

- old (stderr, exit 0): `check-digest: unreadable hook payload (<e>) — passing through.`
- new (stderr, exit 0): `check-digest: the hook failed internally (ArtifactAccessError: SubagentStop hook payload: invalid JSON: <detail>) — passing through; this is not a pass, nothing was checked.`
- re-pinned by: `tests/integration/test-validate-digest.py` — "[feat65] an unreadable payload is the
  hook's own failure and takes the same template"; the canonical-reader duplicate-key audit
  (`_duplicate_hook_payload_failures`) re-pinned to the template's `ArtifactAccessError:` prefix.

### D-07 · returned-digest own failure (site 17) — R1

- old (stderr, exit 0): `check-digest: internal error validating <agent>'s return (<e!r>) — passing through; this is our bug, not theirs.`
- new: the template line, exit 0. `GatePolicyError` keeps `check-digest: <error>`, exit 2.
- re-pinned by: "[feat65] a defect reading the payload passes through with exactly the hook_guard
  line" (exact stderr) and "[feat65] a defect in the registry errand is no longer reported in its
  own sentence" (an unrelated defect anywhere in hook mode).

### D-08 · durable-copy own failure (site 9) — R1

- old (stderr, exit 0): `check-digest: internal error validating <found> (<e!r>) — passing through; this is our bug, not theirs.`
- new: the template line, exit 0 (the same guard; `check_artifact_file` is reached from hook mode only).
- no pre-existing case pinned the old sentence; covered by the guard cases above.

### D-09 · registry errand sentences (sites 13–16) — kept for their real classes, R1 otherwise

- `inflight_registry unavailable (...)` — kept for `ImportError` only.
- `could not read children of <agent> (...)` / `could not release <agent>'s claim (...)` — kept for
  `UnreadableRegistry`, `harness_merge.MergeRefusal`, `OSError` (what `_update_registry` raises).
- `could not compose the release command (...)` — kept for `(AttributeError, TypeError, ValueError)`.
- any other class in those errands: template line, exit 0 (was the local sentence + the verdict
  continuing). Re-pinned by "[feat65] a defect in the registry errand …" (asserts the old
  "Not blocking on our own errand" sentence is absent).

### Narrowings with no byte change (SC-06)

- Site 1: `(OSError, subprocess.SubprocessError, ValueError)` — `TestKindsError` is a `ValueError`;
  `SyntaxError` keeps its own earlier clause. Sites 2/3/5: `artifact_accessors.FeatureJsonError`.
  Site 4: `harness_yaml.YamlParseError` (`PlanSchemaError` is one). Sites 6/7/8/10:
  `(ImportError, OSError, ValueError)`; `run_bug919_resolve_fallback_case` re-pinned to inject
  `OSError` (was `LookupError`, not a class the lookup raises). Site 11:
  `(OSError, subprocess.SubprocessError, ValueError)`. Site 18: `(AttributeError, OSError, ValueError)`.
- The direct CLI (`validate-digest.py <persona> [file]`) is not wrapped: "[feat65] the direct CLI is
  not wrapped: a validator defect is loud and nonzero".

## T-03 the nine hooks

### D-10 · bash-write-guard claim rule's own pass-through sentence (site 5/6) — R1

- old (stderr, exit 0): `bash-write-guard: claim-worktree boundary was not enforced; passing through because the guard failed internally: <exc>`
- new (stderr, exit 0): `bash-write-guard: the hook failed internally (<Type>: <msg>) — passing through; this is not a pass, nothing was checked.`
- re-pinned by: `tests/integration/test-bash-write-guard.py` — "[feat65] a defect in the claim rule is no longer classified locally: it is named on stderr". `UnreadableRegistry` keeps its `deny_bare` refusal.

### D-11 · bash-write-guard feature-checkout rule's silent absorb (site 4) — R2

- old: exit 0, nothing printed. new: exit 0 and the template line.
- re-pinned by: "[feat61] an unexpected core failure passes through hook_guard, named, and the allowance stands".

### D-12 · dispatch-guard's four own-failure sentences — R1

- `run-dir shape check failed (<Type>: <msg>) -- passing through.` (site 4), `could not resolve the checkout for <feat> (<exc>) — no claim recorded.` (site 6), `feature tree resolver failed (<exc>) -- passing through.` (site 8): deleted — the helpers behind them raise nothing of their own (`linked_worktrees` and `worktree_for_feature` absorb their filesystem failures; the run-dir vocabulary helpers are pure), so each was for defects only. A defect now prints the template line, exit 0.
- `claim step failed (<Type>: <msg>) — passing through, the dispatch is NOT blocked.` (site 9): kept for `UnreadableRegistry`, `harness_merge.MergeRefusal`, `OSError`; any other class → template line, exit 0.
- `unreadable hook payload (<detail>) — passing through.` (site 2): kept for `ArtifactAccessError`; a missing `artifact_accessors` is now a defect (template line) rather than "unreadable payload".
- re-pinned by: `tests/integration/test-dispatch-guard.py` — "feat65: a claim-step defect passes through hook_guard, named" / "feat65: the registry's own unreadable class keeps the typed claim-step sentence".

### D-13 · merge-gate's two "could not evaluate … receipt" denials (sites 4/5) — R1, CLOSED form

- old (stdout, exit 0): `{"hookSpecificOutput": {…"permissionDecision": "deny", "permissionDecisionReason": "merge-gate: could not evaluate <feat>'s Build-entry receipt, so this merge is denied. …"}}` (and the feature-less twin).
- new: site 4 deleted; site 5 kept for `(ImportError, OSError)` (feature_schema missing, git failing to run). Any other class → `hook_guard(main, "merge-gate", fail="closed")`: stderr `merge-gate: BLOCKED — the hook failed internally (<Type>: <msg>); enforcement is CLOSED rather than partial.`, exit 2, no decision JSON. The host treats exit 2 as blocked, so the verdict is unchanged; the channel moved from the decision JSON to stderr.
- re-pinned by: `tests/integration/test-merge-gate.py` — "FEAT-65: a receipt-evaluation defect is BLOCKED by the closed guard and named".

### D-14 · four DEC-234 prologues — no byte change; byte-identical to run-unit-tests.py's

- `branch-create-gate.py`, `gh-close-gate.py`, `merge-gate.py`, `plan-sign-gate.py`: `except Exception:` → the reference `except (ModuleNotFoundError, ValueError):` with the FEAT-64 comment moved verbatim; branch-create-gate additionally spells its imports `_bootstrap_contextlib`/`_bootstrap_io` and its docstring as the reference does (the copy had drifted). A resolver defect now escapes (traceback, exit 1); re-pinned by one "FEAT-65: an unexpected resolver defect is loud and nonzero" case per gate.

### Narrowings with no byte change (SC-06)

- `branch-create-gate.py` config load/shape/command: `ArtifactAccessError` / `AttributeError` / `AttributeError`.
- `gh-close-gate.py`, `plan-sign-gate.py`: `ArtifactAccessError` at their config/payload reads.
- `inject-expertise.py`: root `(ImportError, ValueError)`; payload `ImportError` / `ArtifactAccessError`.
- `feature-record.py propose-rework`: `harness_yaml.YamlParseError` keeps `REFUSED: <plan> does not load`; anything else is a traceback, exit 1 (SC-09: `test_an_unexpected_defect_stays_loud_and_nonzero`).
- `inflight_registry.py`: `/proc` probes `(OSError, ValueError, IndexError, StopIteration)`; `ps` `(OSError, subprocess.SubprocessError, ValueError)` → `None`; `feature_root` `(AmbiguousWorktree, OSError)` → owner root. No entrypoint guard (SC-10: "feat65: the direct feature-root command stays loud and nonzero on a defect").
- `dispatch-guard.py` bootstrap probe: `ImportError` / `(ArtifactAccessError, YamlParseError, OSError, ValueError)` → status "1"; tool-grant read `(OSError, ValueError, IndexError)`; registry import `ImportError`.

## validate c1 fixes

### D-15 · `branch-create-gate.py` `_CONFIG_READER` (CR-01) — no byte change

- The embedded compatibility program's `except Exception:` → `except (OSError, ValueError, AttributeError):`
  (no file, not JSON, a top-level document with no `.get`). Same `false -` on those; a `github:` block that
  is not a mapping keeps its traceback — the exceptional path the gate runs this program FOR.
- `check-plan-routes._broad_catch_count` now counts handlers inside string constants that parse as
  Python and carry a `try` (programs handed to another interpreter). Baseline `branch-create-gate.py`
  counts 5 under it (4 own + 1 embedded); the pin counts 0.
- re-pinned by: `test-branch-create-gate.py` `run_feat65_config_reader` (four recoveries + the traceback
  path); `test-broad-catch-census.py` `case_feat65_census_reads_executable_embedded_python`.
