# Security review — FEAT-48-parallel-safe-suite — cycle 7 — pin 8e7f56dc

**Verdict: PASS, no findings.** Diff `d135364e..8e7f56dc` is in-scope (dev-tooling
temp-dir/subprocess/env surface) but every mechanism checked is either sound or a strict
narrowing of the pre-existing exposure. Full file set from the dispatch was read; census below.

## Per-file census

| File | In/out | Why |
|---|---|---|
| `isolated_bin.py` | IN | new temp/copy primitive |
| `run_pool.py` | IN | new subprocess/env/temp-scan surface |
| `run-unit-tests.sh` | IN | argv/env wiring to the pool |
| `test-suite-independence.py` | IN | new AST scanner, `--scan-dir` argv, `os.walk` |
| `test-run-pool.py` | IN | drives `run_pool.py` argv/env, incl. a `sh -c` fixture |
| `test-check-domain.py`, `test-check-state.py`, `test-feature-worktree.py`, `test-check-fixture-secrets.py`, `test-validate-digest.py`, `test-bash-write-guard.py` | IN | all six adopt `isolated_bin()`/`tempfile.mkdtemp()` |
| `.harness/harness.json` | OUT | one string value grows (new file names appended to `detect`); no logic |
| `.harness/harness/docs/DECISIONS.md` (DEC-211) | OUT | prose; checked for false safety claims, none found |

## Findings, per dispatch bullet

**Temp-directory creation.** Every instance across the changed files is `tempfile.mkdtemp()` /
`tempfile.TemporaryDirectory()` — no manually-joined `/tmp/<literal>` or PID-only path anywhere
(grepped all nine changed Python files). `mkdtemp` creates with mode `0700` and an
unpredictable name (`_RandomNameSequence`), so no world-writable mode, no guessable name, no
pre-creation/symlink race. Where `os.getpid()` appears in a path
(`test-check-fixture-secrets.py:155,202`, `test-validate-digest.py:1707,3817,3869`) it names a
*file inside* an already-unique `mkdtemp()` directory, not the directory itself — PID collision
there is a uniqueness concern, not a security one. `run_pool.py`'s `snapshot()`
(`run_pool.py:29-40`) walks with `os.walk` default `followlinks=False`, so it can't be walked out
of the watched tree via a symlink. No `shutil.rmtree` targets a path built from unsanitized
external input — all rmtree calls target a `mkdtemp()`-owned root the same test created
(e.g. `test-check-fixture-secrets.py:168,218`, `test-feature-worktree.py:604,1119`,
`test-validate-digest.py:1717,3827,3881`, `test-bash-write-guard.py:705,834`).

**`shutil` copy semantics.** `isolated_bin.py:8-14` is the only new copy primitive:
`shutil.copytree(source, destination)` with default arguments — `symlinks=False` (follows and
materializes symlink targets rather than preserving a link an attacker could redirect later) and
`copy_function=copy2` (preserves source mode/mtime, nothing broader). `source` is
`os.path.dirname(os.path.realpath(__file__))`, i.e. exactly `.claude/skills/harness/bin` —
confirmed the live directory holds no symlinks (`find … -type l` → empty except the checker
script's own name), no `.env`/credential/key-shaped files, and no `.git`. So the private copy
can only ever contain the tracked bin scripts; it copies no secret, no `.git` object, and cannot
walk out of the source tree. `copytree` also refuses if `destination` already exists (no
`dirs_exist_ok`), and `destination` always sits inside a fresh `mkdtemp()` root, so no directory
it writes into is ever attacker-predictable or pre-existing.

**Env/argv without validation.** `HARNESS_TEST_WORKERS` (`run_pool.py:14-26`) is `int()`-parsed
and range-checked (`>0`); a bad value is a loud `exit 2`, never passed to a shell or used as a
path. `--mutation-check DIR` (`run_pool.py:66-73`) is `os.path.abspath()`'d and validated with
`os.path.isdir` before use — not shell-interpolated, only fed to `os.walk`/`os.stat`. The script
paths on argv in `run-unit-tests.sh` are a fixed, hardcoded bash array (`UNIT_SCRIPTS`/
`INTEGRATION_SCRIPTS`), never taken from environment or caller argv; `"${SCRIPTS[@]/#/$BIN_DIR/}"`
is bash parameter expansion feeding a Python argv array via `exec python3 … -- "${SCRIPTS[@]…}"`
(`run-unit-tests.sh:148`) — no shell is invoked a second time, so string-concatenation here is
not an injection vector. `$BIN_DIR` itself is the literal `.claude/skills/harness/bin`, never
env-derived. `test-suite-independence.py`'s `--scan-dir` (`test-suite-independence.py:153-160`)
is `os.path.abspath()`'d and only ever fed to `os.walk`/`ast.parse` for a local developer/CI
invocation — no remote/untrusted-input reachability.

**Data exposure via captured stdout/stderr.** Compared byte-for-byte against
`git show d135364e:.claude/skills/harness/bin/run-unit-tests.sh`: the pre-diff runner already
executed `python3 "$BIN_DIR/$s"` with **no output redirection**, so every test's stdout/stderr —
including anything a test prints from its own environment — already streamed straight to the
CI/terminal log. `run_pool.py:46-48` captures the same two streams (merged) and reprints them
verbatim in an attributed block after the subprocess exits. Same bytes, same destination
(CI log), only timing/ordering changes (post-hoc block vs. live interleave, and interleave was a
non-issue before since execution was serial). Not a new exposure — a diff-against-pre-change
check (not diff-against-zero), confirmed measured.

**Subprocess construction in `run_pool.py`.** `run_one` (`run_pool.py:46-48`) is
`subprocess.run([sys.executable, path], …)` — list-form argv, no `shell=True` anywhere in
`run_pool.py` or its callers. Environment is inherited (`env=None` default) — identical to the
pre-diff behavior where bash directly forked `python3 "$BIN_DIR/$s"`, also inheriting the caller's
env. `test-run-pool.py:81` contains a `subprocess.run(['sh','-c', f'echo y >> {keep}'])` — but
that is inside a *generated test fixture script*, using a path (`keep`) the test itself created
inside its own `tempfile.TemporaryDirectory()`; it is not attacker-reachable and not shipped
runtime code.

## Non-findings worth recording (assessed and dismissed)
- `test-check-domain.py`/`test-bash-write-guard.py` previously wrote a mutant executable file
  directly into the **live** shared bin directory (`HERE`) before this diff
  (e.g. old `.check-fixture-secrets-mutant-%d.sh` at `HERE`); the diff moves every such mutant
  into an `isolated_bin()` private copy instead. This is a strict *reduction* in shared-tree
  write exposure, not a regression — noted so a later reviewer doesn't re-flag it as new risk.
- DEC-211's prose (`DECISIONS.md`) makes no safety claim beyond what the code does; its stated
  coverage boundaries (static scan blind to non-`__file__`-derived targets and to
  content-derived paths) are accurately hedged, not oversold.

## STRIDE — the one boundary this diff touches
| Boundary | STRIDE | Mitigated | Note |
|---|---|---|---|
| Shared live bin tree vs. concurrent test workers | Tampering | true | `isolated_bin()` removes writes to the shared tree for the covered mutation probes; `run_pool.py --mutation-check` is a runtime detector as a second line, not the sole control |
| CI log stream vs. test stdout/stderr | Information disclosure | true (unchanged) | identical bytes to pre-diff, confirmed against `d135364e` |

## Open questions
None security-relevant. `test-suite-independence.py`'s fixture-coverage gap and
`test-run-pool.py`'s `__pycache__`-exclusion gap are already filed by the qa segment
(non-security, not re-litigated here).
