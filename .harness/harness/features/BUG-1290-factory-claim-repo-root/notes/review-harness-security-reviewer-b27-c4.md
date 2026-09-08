# Security review — BUG-1290 B-27 cycle — pin 72a97b9942832169af84479ae36487398d27ca39

**BLUF: PASS, `severity_max: none`, scoped IN and measured (not a pre-emptive decline).** This
commit's own diff (`c488218e..72a97b99`) touches only `.harness/` notes/receipts (519 insertions,
0 code) — confirmed empty for `.agents/`, `.claude/skills/`, `bin/` by re-running the orchestrator's
stat. But the *feature's* file set (test-factory-claim.py, test-factory-claim-mutation.py) is
unchanged since `fb9a4ac4` (`git diff --stat fb9a4ac4 72a97b99 -- tests/unit/test-factory-claim*.py`
is empty) and was not previously audited by this role under a security lens for its runtime-patching
shape, so I read both in full at the pin rather than citing "test-only" as a decline.

## What I measured

**2a — in-process monkey-patching of `factory_claim._BlockerCache` / `factory_config`, restore paths.**
Every patch site in both files is a `try:`/`finally:` pair restoring the saved attribute
unconditionally (`test-factory-claim.py:1335-1340` for `_BlockerCache` under 5g;
`test-factory-claim-mutation.py:120-125` and `:177-182` for `factory_config` and `_BlockerCache`
under the two mutation arms; `run_main()`'s own `finally` at `test-factory-claim.py:438-443` restores
`fc.features_root`/`fc.product_config`/`sys.argv`/`factory_gh`). The 5g capture shim (`_capture`,
`test-factory-claim.py:1332-1334`) records into a dict and never prints — confirmed by reading its
body, not inferred — so a failing captured verdict cannot itself leak text past the restore.
The one scenario worth naming explicitly: `test-factory-claim-mutation.py`'s `_run_suite()` executes
`test-factory-claim.py` **in-process via `runpy.run_path`, inside the mutation window** (`factory_claim.
factory_config`/`_BlockerCache` is swapped before the call). I checked whether that "later caller in
the same process" is reachable from the real unit runner: `run-unit-tests.sh` delegates to
`run_pool.py`, whose `run_one()` (`run_pool.py:59-63`) calls `subprocess.run([sys.executable, path], …)`
— **each `tests/unit/test-*.py` file is its own fresh interpreter process.** There is no shared
process for a mutation to leak into; the only files that ever run in the SAME process as the
mutated `factory_claim` module are the mutation file's own `_run_suite()` calls, each already
wrapped in the `try/finally` above. Only a hard process abort (SIGKILL, segfault, `os._exit`) would
skip the `finally` — and that kills the process the mutated state lived in, so there is no live
caller left to receive it. Not a finding.

**2b — `tempfile.mkdtemp` fixtures.** `run_main()` and the 5a/5c/db/absent-root/p1-p6 cases all use
`tempfile.mkdtemp(prefix="claim-…")` with no `dir=` override (always the default system temp root,
never a fixed/predictable path under the repo) and no `chmod`/`umask` call anywhere in either file
(grepped `chmod|umask|0o[0-7]{3}` — zero matches) — `mkdtemp` keeps its stdlib-default `0700`
owner-only mode. Fixture files inside are written by `write_yaml`/`write_json` (plain `open()`+dump,
no widened mode). Nothing is written outside the returned temp root — every `os.path.join` target
in the write helpers descends from the `mkdtemp()` return value or from `FIXTURE_HARNESS_ROOT` (a
second, similarly-scoped `mkdtemp` tree built once at import via `build_features_root()`). These
directories are never explicitly removed (no `shutil.rmtree`/`tempfile.TemporaryDirectory`), so they
accumulate under the CI runner's `/tmp` across runs — real, but a disk-hygiene chore, not a security
gap: mode stays 0700, content is synthetic fixture data.

**2c — secrets/tokens/credentials.** Grepped both files for
`token|password|secret|api_key|Authorization|Bearer|ghp_|gho_|ssh-rsa|BEGIN…PRIVATE` (case-insensitive)
— zero matches. `AS_LOGIN = "agent-1"` is a hardcoded fixture literal, not a real identity or token.

**2d — injection/path traversal through repo/segment names.** `fixture_features_root()`
(`test-factory-claim.py:398-400`) does `segment = repo_name.split("/", 1)[-1]` then
`os.path.join(FIXTURE_HARNESS_ROOT, ".harness", segment, "features")` — this is the exact join
shape a traversal would target. But every `repo_name` reaching it is a hardcoded module constant
(`REPO`, `REPO_B`, `REPO_KAYA`, `REPO_HARNESS_SEG`, `"acme/other"`, `"acme/zzz-missing-segment"`) or
a literal passed inline at a call site (`repo_dict(REPO_KAYA)`, `repo_dict(repo_missing)`) — never
CLI argv, env, or any value read from outside the test file itself. There is no untrusted-input path
into this join; traversal is not reachable from this diff.

**2e — data exposure via print/capture.** `check()`'s `detail` argument (which can carry the
`mkdtemp()` absolute path, e.g. B5-ter's `absent_root in err` assertion, or fixture issue numbers)
prints to real stdout **only on FAIL** (`test-factory-claim.py:41-48`, confirmed by reading the
function body, not assumed) — standard, expected assertion-diagnostic behavior. The path is an
ephemeral CI-local `/tmp` scratch directory, the issue numbers are synthetic fixture literals
(700-900s range), and `AS_LOGIN` is the same fake "agent-1" from 2c — none of this is a real
credential, a real issue/operator identity, or a host path with any sensitivity beyond "this ran on
this machine." `test-factory-claim-mutation.py`'s `print("MUTANT ACTIVE", file=sys.__stdout__)`
deliberately bypasses the `redirect_stdout` capture to prove reachability — the string itself
carries no sensitive content. No new data-exposure vector.

## Recurrence noted, not investigated
Per dispatch: the null-yield reviewer return recurred again this cycle on the eng lead's simplify
return. Noted as instructed; out of this role's scope to chase further.

## Residual, non-gating
- `tempfile.mkdtemp` fixture directories under both test files are never cleaned up
  (`chore` — disk accumulation in CI `/tmp` over repeated runs; mode stays 0700, no risk, just waste).

## Threat model
| boundary | STRIDE | mitigated |
|---|---|---|
| in-process monkeypatch window (`factory_claim._BlockerCache`/`factory_config`) vs. a later same-process caller | Tampering | true — `try/finally` restore on every path, and `run_pool.py` subprocess-isolates each test file so no later same-process caller exists |
| fixture repo/segment name → filesystem join (`fixture_features_root`) | Tampering (path traversal) | true — precondition absent: no untrusted input reaches this join, all values are hardcoded literals |
| `tempfile.mkdtemp` fixture dirs | Information disclosure | true — 0700 default mode, synthetic content only |
| assertion-failure diagnostic prints (stdout/stderr → CI log) | Information disclosure | true — only ephemeral tmp paths and synthetic fixture literals ever appear |

No must-fix findings. `severity_max: none`.
