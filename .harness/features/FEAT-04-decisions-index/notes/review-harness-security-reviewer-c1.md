# Security review — FEAT-04-decisions-index — c1

**VERDICT: PASS.** Scope-out on a stdlib-Python-and-Markdown diff at `363b539` (feat/decisions-index).
No network, DB, auth, secrets, or user-facing surface is touched. This is a presence assertion, not a
shrug — three trust boundaries were examined and dismissed on evidence, listed below.

## Diff examined

`git diff 8614794..363b539` stat, then narrowed to the FEAT-04 window
(`46a1f91~1..363b539`, `.claude/skills/harness/bin/`) to separate this feature's own commits
(`ff9d866`, `25493ae`, `ce2cd17`, `bdfa3ab`, `80a9934`, `feebf60`, `363b539`) from concurrent,
non-FEAT-04 guard fixes (`3a989a0`, `71a2043`) that landed in the same window. FEAT-04's own tip
commit (`363b539`) touches only `CLAUDE.md` and `harness-handoff/SKILL.md` — prose, no code.

## Surfaces examined and dismissed (named, not assumed)

1. **`gen-decisions-index.py:329-330`** — `project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or
   os.getcwd(); os.chdir(project_dir)`. Same pattern as the already-shipped `check-docs.sh:26`
   (`cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"`). The env var is set by the harness's own invocation
   context, not by an external or lower-privilege actor — whoever controls the env already controls
   the invocation. Same-trust, not a finding. `DECISIONS_PATH`/`INDEX_PATH` are fixed relative
   strings (`docs/harness/...`); no attacker-influenced path component anywhere, so no traversal.

2. **`test-gen-decisions-index.py:29,65-72`** — `run_gen()` builds `subprocess.run([sys.executable,
   GEN], cwd=tree, env=env)`, list-form argv, no shell. `GEN` defaults to a fixed path beside the
   test file; the `GEN_DECISIONS_INDEX_BIN` env override exists only to let a fix be proven RED
   against a reverted copy (test file's own docstring, mirroring `test-check-state.py`'s
   `CHECK_STATE_BIN` escape). This is my G-02 shape (a leading-`-` value getting re-read as a flag),
   but whoever sets that env in this test harness already runs arbitrary Python locally — no
   privilege gain. `tempfile.TemporaryDirectory()` is used as a context manager in every test, so
   the fixture tree is cleaned up even on exception; `CHECK_DOCS` subprocess call (test 4, `:308`)
   is likewise fixed-path list-argv against a `TemporaryDirectory`.

3. **`gen-decisions-index.py:317-323,288`** — `parse_existing_index` reads hand-written ruling
   prose from the committed index and `build_index` passes it through verbatim into the
   regenerated file, which is later grepped into agent context. The boundary is real (output another
   system — an agent — interprets), but the content is authored in-repo under the same
   approval/commit gate as the code itself; no lower-privilege actor can reach it. Dismissed on
   trust, not overlooked.

No shelling-out with string interpolation, no `eval`/`exec`, no new third-party dependency (only
`os`, `re`, `sys`, `subprocess`, `tempfile`, `shutil` — all stdlib), no credentials or PII anywhere
in this diff.

## Already-on-record items (not re-derived)

- Items 1, 3, 4, 5 from the dispatch's known-findings list: acknowledged, not re-assessed here.
- Item 2 (bash-write-guard.sh heredoc/compound-`;` misparse): its two fixing commits (`3a989a0`,
  `71a2043`) are outside FEAT-04's own task set (T-01..T-10 land in `ff9d866`, `25493ae`,
  `ce2cd17`, `bdfa3ab`, `80a9934`, `feebf60`, `363b539`) — they're concurrent PR-review fixes, not a
  FEAT-04 deliverable, so I did not re-open the 222-line guard script to re-grade it. On direction
  only: the discriminator worth checking next is over-block (fail-closed, friction — the shape I hit
  first-hand this run when a redirect got denied) versus under-block (fail-open, control bypass per
  my own G-01) — I have first-hand evidence only of the former, none of the latter, so I can't say
  the severity is understated from this run's evidence alone.

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| `CLAUDE_PROJECT_DIR` env -> `os.chdir` | Tampering | yes — same-privilege-as-invocation |
| `GEN_DECISIONS_INDEX_BIN` env -> subprocess argv | Elevation of privilege | yes — same-trust, test-only escape hatch |
| Hand-written ruling prose -> regenerated index -> agent context | Information disclosure / Tampering | yes — authored in-repo under commit/approval gate |
