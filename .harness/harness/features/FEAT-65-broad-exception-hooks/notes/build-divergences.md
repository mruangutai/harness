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
