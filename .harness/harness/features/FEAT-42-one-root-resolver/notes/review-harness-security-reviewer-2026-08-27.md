# Security review — FEAT-42 one-root-resolver — cwd shadowing fix — 2026-08-27

Diff: ea71a1c..9d12e3a. Read-only review under DEC-174; no source edits made. All claims below
are measured (empirical scratch-dir tests, `git show`/`git log` against 9d12e3a, `wc -c`/`grep -c`
against the live main checkout), not inferred from the notes.

## BLUF

The claimed fix (`python3 -P` on 19 launches) is correct and complete for the ORIGINAL,
measured vulnerability — I re-derived all 19, found none missing, and confirmed empirically
(not just by reading the note) that `-P` strips the cwd from `sys.path` under every invocation
shape used here (heredoc, `-c`), that `PYTHONPATH` still resolves correctly alongside `-P`, and
that the two by-path launches left un-flagged (`gh-close-gate.sh:79`, `run-unit-tests.sh:149`)
are genuinely safe — a script launched by path gets its own directory at `sys.path[0]`, even
through a symlink. Python's own `harness_boundary.py` resolver (`resolve_root`/`root_above`/
`root_from_script`) is not marker-plantable by an ordinary agent: `resolve_root`'s only
attacker-reachable input, `HARNESS_PROJECT_DIR`, is never set anywhere in `.claude/settings.json`
or by any production caller — it exists solely for test fixtures — so under the standard
per-Bash-call-fresh-process threat model here, an agent cannot make the override branch fire at
all. `root_above` is walked only by `wayfind.py`, a non-enforcement CLI convenience tool.

**But the diff left an unaddressed, more severe instance of the identical trust bug it exists
to fix, in code this exact diff edited: `.omp/extensions/harness-hooks.ts:142`.** That is the
must-fix.

## Finding 1 (must_fix, high) — `.omp/extensions/harness-hooks.ts` resolves the ENFORCEMENT
SCRIPT ITSELF from a caller-supplied `cwd`, not from a fixed location

`runPolicy(cwd, script, args, payload)` (`harness-hooks.ts:134-165`) does:

```
spawnSync(join(cwd, BIN, script), args, { cwd, env: { ...process.env }, ... })
```

`BIN = ".agents/skills/harness/bin"`. This diff (commit `0a5bd49`, task T-20) touched exactly
this function to remove `HARNESS_PROJECT_DIR: cwd` from the child's env — correctly, per its own
comment, because "a wrong-but-plausible cwd... is honoured in preference to the script's own
derivation. That is the fail-open this feature closes." That reasoning is applied to the ENV
value one line below, and not applied to `join(cwd, BIN, script)` one line above it, in the same
statement — the path used to locate and `spawnSync` the gate binary itself is still built
directly from the same untrusted `cwd`.

Every caller (`before_agent_start`, `tool_call` for `bash`/`task`/`yield`) passes `ctx.cwd`,
tracked per-event by the host, not a single session-start constant the way
`${CLAUDE_PROJECT_DIR}` is for the Claude Code integration. If an agent under this host can
influence its own tracked cwd between tool calls (plausible — that is why the field is threaded
per-event rather than captured once), and can write a file anywhere permitted to it (the same
precondition the original bug required), it can place its own `check-domain.sh` /
`bash-write-guard.sh` / `validate-digest.py` at `<its-cwd>/.agents/skills/harness/bin/<name>` and
`runPolicy` will execute THAT file wholesale as the gate — not shadow one imported module, as the
Python bug did, but substitute the entire enforcement script. DEC-202 makes `.agents/skills` a
link to the one authored `.claude/skills` tree, but only at the real project root; a decoy
directory has no such link and none is required for this to work.

I could not execute the actual OpenCode/OMP host from this sandbox to confirm whether `ctx.cwd`
is agent-steerable in practice (Claude Code's own docs note here that its own shell state does
NOT persist between Bash calls, but that is a Claude-Code-specific fact, not evidence about a
different host). Flagging the precise open assumption per policy: **this is reachable if and
only if the OMP host lets a tool call change the `cwd` it reports on the next `ctx` for the same
agent session.** Independent of that assumption, the function's own contract is unsound: it
treats one instance of caller-supplied `cwd` as untrustworthy (the removed env var) and the
structurally identical other instance (the executable path) as trustworthy, in the same commit,
with no comment addressing the discrepancy. `.omp/extensions/harness-hooks.ts` has zero test
coverage (no `*harness-hooks*test*` file in the tree) and is not mentioned in
`notes/cwd-import-bypass-2026-08-27.md` or `notes/qa-gate-2026-08-27.md` — this class of bug was
checked for the Python side and not for the TypeScript side of the same fix.

Recommended remedy (not applied — DEC-174): derive the bin directory from this extension file's
own on-disk location (e.g. `import.meta.dirname`-relative arithmetic, the TS analogue of
`root_from_script`), never from `ctx.cwd`; keep `cwd` only as the argument passed *to* the
already-located script, exactly as `resolve_root` treats `HARNESS_PROJECT_DIR` as data, not as
the module's own address.

## Finding 2 (residual, med, not blocking) — `check-domain.sh`'s relative-path assumption is a
convention, not an enforced boundary, and now spans two hosts

`_show`/`_norm` (`check-domain.sh:970,1000`) resolve `file_path` with `os.path.abspath`, i.e.
against the hook subprocess's OS cwd, deliberately left unfixed per the note ("not reachable
from Claude Code, which sends absolute paths"). Re-derived rather than accepted: nothing in
`check-domain.sh` asserts or rejects a relative `file_path` — the code silently accepts one and
resolves it against whatever cwd the hook process happens to have. That is an unenforced
precondition on a module now consulted by (at least) two different host integrations
(`.claude/settings.json` and `.omp/extensions/harness-hooks.ts`, DEC-202 explicitly making OMP
canonical for provider-neutral discovery) with no shared guarantee about path shape. "Claude Code
always sends absolute" is true as an observation about one client today; it is not a boundary
this module enforces, and the module is no longer single-client. If a relative `file_path` ever
reaches it while the hook's cwd differs from the write's actual target tree — exactly the
mismatch this whole feature was created to close for `sys.path` — the domain/shape verdict is
computed against the wrong tree: at best a wrong classification, at worst (a target that resolves
outside any declared repo) the `not_a_domain_question` pass-through, which is a full skip of
governance, not a refusal. No live exploit demonstrated; recommend a hard `assert
os.path.isabs(file_path)` (refuse rather than silently cwd-resolve) as a follow-up, tracked as a
backlog item rather than gating this diff.

## Finding 3 (residual, low, out of this diff's scope) — `feature_schema.schema_path_for` walks
unbounded above the verified root for a second, unrelated marker file

Confirmed via `git log ea71a1c..9d12e3a -- .claude/skills/harness/bin/feature_schema.py`: **zero
commits touch this file in the reviewed range** — pre-existing (issue #749), not part of this
diff, does not affect this diff's verdict. Noted because the dispatch asked me to think hardest
about marker-planting: `schema_path_for` (`feature_schema.py:71-100`) walks from the write
target's directory toward `/`, unbounded past the checkout root, looking for
`<ancestor>/.claude/skills/harness/bin/feature-schema.json` to use INSTEAD of the module's own
schema (issue #749's fix for legitimate per-worktree schema keys). Unlike `harness_boundary`'s
`resolve_root`, this walk has no MARKER-style single-file gate and does not stop at the resolved
root — it is bounded only by the filesystem root. A schema-weakening file planted at any ancestor
between the checkout and `/` that the agent can write to (paths outside the declared workspace
are explicitly waved through by `check-domain.sh`'s own "not_a_domain_question" branch) would be
preferred over the real schema for every later `feature.json` write. This shares the exact shape
of the marker-planting attack the dispatch asked about, on a different file, pre-dating and
untouched by this feature. Flagging for the backlog, not this verdict.

## What I verified positively (not just re-read)

- All 19 `python3 -P` launches enumerated at `9d12e3a`; the two remaining by-path launches
  (`gh-close-gate.sh:79`, `run-unit-tests.sh:149`) confirmed safe by direct empirical test: by-path
  launch (relative, absolute, and through a symlink) puts the SCRIPT's own directory at
  `sys.path[0]`, never the invoking cwd; only `-c`/`-m`/`-` forms take the cwd, and every such
  form in `bin/*.sh` carries `-P`.
- `-P` does not disable `PYTHONPATH` — confirmed empirically alongside a decoy module: `-P` only
  removes the auto-prepended unsafe entry (cwd / script dir / `''`), `PYTHONPATH` entries still
  resolve at their normal position. This is why `check-state.sh:48`'s `PYTHONPATH=... python3 -P`
  co-occurrence is correct, not a reintroduction.
- No `sys.path.insert`, `os.environ[...] =`, or nested `subprocess`-launched `python3` in any
  production (non-test) file under `bin/` reintroduces a cwd-derived path; every `sys.path.insert`
  site anchors on `__file__`/`BASH_SOURCE`, never `os.getcwd()` or a bare relative default that
  can fire in practice (`dispatch-guard.sh`'s `os.environ.get(...) or "."` fallback is dead code —
  the same command line sets that env var unconditionally one token earlier).
- `resolve_root`'s `HARNESS_PROJECT_DIR` override: grepped `.claude/settings.json` and every
  production caller — never set outside test fixtures, so the override branch cannot fire for an
  ordinary agent turn under the current, fresh-process-per-hook threat model.
- Confirmed the stated DEC-174 blast-radius measurement myself: main checkout
  `dispatch-guard.sh` is 6366 bytes / 0 occurrences of `HARNESS-FEATURE`/`_root_for`; the worktree
  copy is 9447 bytes / 4 occurrences; main HEAD is `3952814`. Matches exactly.

## DEC-174 blast radius: is the test suite alone adequate evidence to land this?

No, and the gap is structural, not a quality complaint about the suite itself —
`verify-technique-2026-08-27.md` shows real diligence (subprocess-level, mutation-proven, paired
before/after). What no unit test under DEC-174 can exercise is the REGISTRATION-and-SPAWN path:
`${CLAUDE_PROJECT_DIR}` template resolution in `.claude/settings.json`, the host's actual hook
launcher, and (per Finding 1) the OMP extension's own dispatch. Every test invokes the scripts
directly, by path the test controls — which is exactly the invocation shape I independently
confirmed is safe, and exactly the shape the ORIGINAL bug did not live in. The suite proves the
SCRIPTS are correct in isolation; it cannot prove the DEPLOYED HOOK reaches the fixed copy, because
today it verifiably does not (0-occurrence main copy). Recommend, after merge and before broad
reliance: one live smoke probe repeating the ORIGINAL measurement (a decoy `harness_boundary.py`
in an agent's actual working directory, one real governed write) through the REAL registered
hook path on `main`, not a direct script invocation — the one check a unit test structurally
cannot stand in for. For the OMP host specifically, that probe needs to be repeated independently,
since it has no automated coverage today.

## Threat model summary

| Boundary | STRIDE | Mitigated |
|---|---|---|
| Agent-writable cwd -> Python `sys.path[0]` (the measured #556 bug) | Elevation of privilege | Yes — 19/19 launches, verified empirically |
| Agent-writable cwd -> OMP `runPolicy` script path | Elevation of privilege | **No** — Finding 1 |
| Relative `file_path` -> `check-domain.sh` cwd-relative `abspath` | Tampering / Information disclosure (misrouted domain verdict) | Partial — convention only, not enforced (Finding 2) |
| `HARNESS_PROJECT_DIR` env override in `resolve_root` | Spoofing (root confusion) | Yes — never set in production, reachability-closed |
| `root_above` marker walk (`wayfind.py`) | Spoofing | Yes — informational CLI, not an enforcement decision |
| `feature_schema.schema_path_for` unbounded ancestor walk | Tampering | No — pre-existing, out of this diff's scope (Finding 3) |
