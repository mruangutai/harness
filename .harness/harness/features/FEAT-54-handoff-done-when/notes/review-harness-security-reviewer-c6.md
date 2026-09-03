# Security review c6 — FEAT-54-handoff-done-when

**PASS, info.** Zero new gating findings. The only code-shaped delta since c5's already-PASSED
security review (`4690f724`) is prose inside the three in-feature handoff notes (F-11 fix);
`handoff_done_when.py`, `check-domain.sh`, `check-state.sh`, and `probe-handoff-comprehension.py`
are byte-identical to what c5 already reviewed clean, confirmed by `git diff 4690f724..dd55b357`
returning empty for all four.

## What I checked, at `dd55b3570c6a20f5ca1da016d6959752bd0ffc74`

**1. `handoff_done_when.py` path resolution (the dispatch's primary ask — `finding:`/`approval:`
pointers carry a path).** Read the full 288 lines via `git show`. Two-layer defense:
- `_unsafe_rel_path` (string level, applied in `_parse_authorities` before any filesystem touch):
  rejects control chars, absolute paths, `..` in `PurePosixPath.parts`, and empty/`.`.
- `_read_target` (real-filesystem level): `path.resolve(strict=True)` — which follows symlinks —
  then `resolved.relative_to(root)`; a symlink that resolves outside `root` fails this check
  regardless of what the string-level check saw. `.agents/ → .claude/` is therefore benign: any
  path through it still resolves to a real path under the repo root and passes containment.
  `stat.S_ISREG` blocks FIFOs/devices/sockets; size is checked before read and the read itself is
  capped at `MAX_TARGET_BYTES + 1` (1 MiB) — no unbounded or blocking read.
- **Ran the actual unit suite** (`env -u HARNESS_AGENT_TYPE python3 tests/unit/test-handoff-done-when.py`)
  rather than trusting the read: 29/29 PASS, including the four security-shaped fixtures
  `finding symlink escape`, `finding special file`, `approval symlink escape`,
  `approval special file` — these build a real symlink pointing outside the fixture tree and a
  real `os.mkfifo`, so the containment and regular-file checks are exercised live, not just
  present in source.
- Resolver exceptions fail closed: `_resolution_problems` catches any exception per pointer and
  turns it into a blocking problem string ("resolver failed closed").

**2. `check-domain.sh` / `check-state.sh` — shell invocation and argument handling (the dispatch's
second ask).** Both import `handoff_done_when` and call `.problems(rel, content, root, resolve=…)`
as an **in-process Python function call** — note content never reaches a shell, so word-splitting
and quoting concerns don't apply to this integration point. Grepped both files for `shell=True`,
`os.system`, `Popen(` — none found; every `subprocess.run` in the diff uses list-form argv.
`check-domain.sh`'s new `except Exception` around the resolver call appends a blocking problem
(fail closed, matches the resolver's own posture) rather than swallowing silently. The widened
Edit-reconstruction route (now also covers `RE_HANDOFF` targets) is a hardening, not a regression:
invalid on-disk UTF-8 used to be silently mangled via `errors="replace"`; now it raises
`UnicodeError` and the edit is refused (`exit 2`) rather than reconstructed from corrupted bytes.

**3. `tests/manual/probe-handoff-comprehension.py` — subprocess argv and secret exposure (the
dispatch's third ask).** `ask()` builds `[omp, "-p", prompt(note), "--no-extensions",
"--no-skills", "--no-rules", "--no-tools", "--model", model]` — list-form, one `--no-tools`, no
`--auto-approve`, matching **SEC-F-10 (already closed in c5, not re-derived here — confirmed only
that the file is byte-identical to the c5 pin)**. Path handling for the `notes` CLI argument is
independently defense-in-depth versus the resolver: `validate_note` explicitly rejects
`path.is_symlink()` before resolving (stronger than a resolve+contain check alone), `read_regular_file`
opens with `O_NOFOLLOW` (closes the TOCTOU window between the symlink check and the open),
enforces `S_ISREG`, and caps at 1 MiB; `is_handoff_note` then requires the resolved path be exactly
`.harness/harness/features/<one>/notes/handoff-*.md`. No secrets are placed in argv/env by this
script; error output truncates stderr/stdout to 400 chars but carries no credential-shaped field —
this is a manual, CI-never-runs diagnostic whose only sensitive dependency is `omp`'s own stored
credentials, unchanged by this diff.

**4. The three in-feature handoff notes' new `Authority:` pointer lines** (F-11's actual fix,
graded for correctness by code-review, checked here only for pointer-content safety):
`plan-task:T-01.verify`, `brief-sc:SC-04` (×2), and
`finding:.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-c5.md#F-04`.
All relative, in-feature, no absolute paths, no `..`, no unsafe characters — legal by
`_unsafe_rel_path` and resolvable within the repo root.

**5. Config/doc-only files** (`harness.json`'s new frozen `handoff_done_when_baseline` list,
`DECISIONS.md`, `DECISIONS-INDEX.md`, `SKILL.md`, `templates/HANDOFF.md`, the grilling note):
read each diff — prose and a static path list, no secrets, no executable surface.

## SEC-F-08 disposition — unchanged, confirmed at this pin

Med, advisory, non-gating under `gates.review: advisory_unless_high`. Raw repository/model/provider
terminal controls (model id, note path, sha256, per-arm coverage counts) still print to stdout in
`probe-handoff-comprehension.py`'s diagnostic output. File is byte-identical to the c5 pin
(`4690f724`) that already carried this forward — not re-argued.

## Not re-derived per dispatch

SEC-F-10 (closed c5): confirmed via byte-identical diff only, per explicit instruction not to
re-derive.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Zero new gating findings; the only code delta since c5's PASS is in-feature handoff-note prose (F-11), already path-safe."
  in_scope: true
  scope_reason: "handoff_done_when.py parses markdown and resolves typed pointers (finding:/approval:) against real files with a path component; check-domain.sh/check-state.sh invoke it at write time; probe-handoff-comprehension.py shells out to omp with live credentials. All three are genuine security surface."
  severity_max: info
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "handoff-note Authority pointer (finding:/approval:) -> filesystem path", stride: "T", mitigated: true }
    - { boundary: "symlink under repo root (e.g. .agents/ -> .claude/) used as pointer target", stride: "T", mitigated: true }
    - { boundary: "probe-handoff-comprehension.py note-path CLI argument -> filesystem read", stride: "T", mitigated: true }
    - { boundary: "probe-handoff-comprehension.py note text -> omp subprocess argv", stride: "I", mitigated: true }
    - { boundary: "handoff_done_when.py resolver raising an unexpected exception", stride: "D", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-security-reviewer-c6.md
```
