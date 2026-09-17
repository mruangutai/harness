# T-17 documentor receipt

**BLUF:** Metrics operations documentation is complete and committed as `db1b5ac51c6ad224737a52adf673eb3312ffeb61`; the commit contains exactly `.harness/harness/docs/METRICS.md` and `README.md`.

## Revision and verification

- Starting source pin: `93785232ac32ae4fecc0a456d286e772ad15eb82` (`git rev-parse HEAD^`).
- Final commit: `db1b5ac51c6ad224737a52adf673eb3312ffeb61`.
- Exact T-17 verification expression, passed to `python3 -c` without shell interpolation: **exit 0**, no stdout or stderr.
- `python3 .agents/skills/harness/bin/dashboard/serve.py --check`: **exit 0**, no output.
- Documented start command: server became ready at `http://127.0.0.1:8971`; `curl -fsS http://127.0.0.1:8971/` returned the Harness Metrics HTML with its root element.
- The exact PyYAML and Flask installation commands each succeeded in an isolated Python environment. The host interpreter is externally managed, so the isolated environment prevented any system-Python mutation.
- `git diff --check -- .harness/harness/docs/METRICS.md README.md`: **exit 0**, no output.

## Grounded implementation

- Entry point, five-item gate, flags, port and loopback bind: `.claude/skills/harness/bin/dashboard/serve.py:31-55,275-316`.
- Seven KPI names and windows: `.claude/skills/harness/bin/dashboard/client/src/tiles.tsx:9-23`; `.claude/skills/harness/bin/dashboard/serve.py:128-133`.
- Verbatim sourcing rules: `.claude/skills/harness/bin/dashboard/defects.py:10-13`, `.claude/skills/harness/bin/dashboard/grading.py:24`, `.claude/skills/harness/bin/dashboard/trend.py:97,222-228`.
- Sole ship-time append/commit and no backfill boundary: `.claude/skills/harness/bin/dashboard/trend.py:16-29,78-111`; `.claude/skills/harness/bin/gh-sync.py:2161-2164`; `.claude/skills/harness/bin/dashboard/client/src/gapstates.tsx:19-20`.
- Product routes and Refresh: `.claude/skills/harness/bin/dashboard/client/src/routes.tsx:84-88`; `.claude/skills/harness/bin/dashboard/client/src/work-view.tsx:16-24`.
- Status rank, definitions and boundaries: `.claude/skills/harness/bin/dashboard/attention.py:15,38-61,92-153`; `.harness/harness.json:367-371`.
- Local row sources, worktree precedence and retained source errors: `.claude/skills/harness/bin/dashboard/work.py:59-100,139-196,365-385`; `.claude/skills/harness/bin/dashboard/serve.py:190-235`.

## Changed-path evidence

`git show --format=%H --name-only HEAD` printed the final SHA followed only by:

- `.harness/harness/docs/METRICS.md`
- `README.md`

`git status --short -- .harness/harness/docs/METRICS.md README.md` emitted zero bytes after the commit. Other pre-existing feature-run artifacts remain outside this commit. This receipt was written afterward and is intentionally not committed.
