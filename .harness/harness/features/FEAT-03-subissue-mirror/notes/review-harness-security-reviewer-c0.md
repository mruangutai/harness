# Security review — FEAT-03-subissue-mirror

Range audited: `4d00dbc..e68ba00` (three commits: `2897b09` T-01, `ae728e8` T-02..T-07, `e68ba00` T-08).
`git diff --stat e68ba00..HEAD -- .claude/skills/harness/bin docs/harness/DECISIONS.md .harness/harness.json`
is empty — HEAD has not moved past the pin for the audited surface, so working-tree bytes were read
directly for those files. The one dirty path reported by `git status --porcelain`
(`.harness/features/FEAT-03-subissue-mirror/feature.yaml`) is outside the audited surface; I read it
at the pin anyway (`git show e68ba00:.../feature.yaml`) to check SC-10's discriminating fact — see
below. `STATE.md` and `.harness/logs/2026-07-31.md` are also dirty and out of scope (orchestrator
bookkeeping, no code).

## Verdict

**PASS.** `severity_max: low`. No `must_fix`. The diff is in-scope (it shells out to `gh` with
values parsed from `feature.yaml`/`PLAN.md`/`BRIEF.md` and posts content into a public tracker), but
every real control (no shell, list-form argv, path/size/readability validation on file args, no
control read back from GitHub into approval-gated state) is intact, and nothing found rises above
low/defence-in-depth.

## What was checked

- Full three-commit diff (not `HEAD~1`) via `git diff 4d00dbc..e68ba00`, file-by-file, plus the
  standing regression greps (all pass): `sub_issues", "--paginate"` = 1, `dependencies/blocked_by",$`
  = 1, `parent_args|blocked_by_args` in `gh-sync.py` = 0.
- `gh_issues.py`, `gh-sync.py`, `wayfind.py` (diff, not just final state — wayfind's changes are a
  mechanical extraction to the shared module, confirmed byte-for-byte against the pre-refactor
  inline calls).
- `check-state.sh`'s new INV-21 block (pure regex read of `feature.yaml`, no subprocess, no new
  surface).
- `run-unit-tests.sh`, `test-gh-sync.py` (fake-`gh` harness), `test-check-state.py`.
- `.harness/harness.json`, `docs/harness/DECISIONS.md` diffs (config/doc only, no executable
  surface).
- PLAN.md `## Decisions` (D-01..D-06), BRIEF.md SC-01..SC-13/Constraints/Out-of-scope, to separate
  approved-and-dismissed items from anything genuinely new.

## Argument construction — no injection found

Every `gh` invocation is `subprocess.run([GH] + args, ...)` with `args` a Python list — no shell,
so no shell metacharacter injection is possible regardless of content (`gh-sync.py:84`,
`wayfind.py:72,89,176`).

Values that could begin with `-` (BRIEF H1 phrase, task titles/bodies, milestone name) are passed as
**separate argv elements immediately following their flag** (`--title`, `--body`, `--milestone`,
etc.), e.g. `gh-sync.py:266-267,281-283`. `gh` is built on Cobra/pflag; pflag's `parseLongArg`
consumes the *next array element* unconditionally as a flag's value in the `--flag value` two-token
form, with no re-parsing for a leading `-` (this is Go pflag's documented/implemented behaviour, not
a guess about generic getopt semantics). **Not empirically verified in this sandbox** — `gh` execution
was denied by the environment's classifier — so this is reasoning from the pflag source shape, not an
observed test; flagged per the epistemic-honesty rule rather than asserted as checked.

One place this reasoning does **not** apply: `wayfind.py`'s **positional** arguments. `resolve`,
`claim`, and the internal `issue()`/`gh issue close` calls take a ticket number straight from CLI argv
position 1 (`t = a[1]`, `wayfind.py:280,291`) and place it as the first positional token before any
flag (`wayfind.py:297,302,315`; `claim` at `:287`). If that token began with `-`, Cobra's flag/
positional scan (which runs over the whole argv, not just after a value-flag) could reinterpret it as
a flag rather than an issue number — e.g., a second `-R`/`--repo` occurrence could in principle
redirect the call to a different repo. **Assessed as low, not a finding requiring a fix**: every
caller of `t`/`a[1]` in this diff sources it from a GitHub issue `number` field already read back as
JSON (always a positive integer) or from an agent-typed CLI arg in the same trust tier as the rest of
the harness — never from external, attacker-supplied text. Worth a defensive `if not t.isdigit(): die(...)` as hardening, not a blocker.

## Path handling on `--body-file`/`--reason-file` — assessed, not inflated

`post_body_path` (`gh-sync.py:65-80`) validates `os.path.isfile`, non-zero size, and readability,
then passes the **path itself** to `gh` unchanged — matching DEC-138 am.6 ("the mirror never composes
text"). There is no traversal/symlink/absolute-path restriction: `isfile` follows symlinks, and an
absolute or `../`-laden path is accepted. In isolation this would let an arbitrary local file (one
readable by the process) be posted verbatim into a public GitHub issue via `--body-file`/
`--reason-file`.

**Threat model check, per the brief's instruction to state this explicitly rather than inflate it:**
BRIEF.md's SC-03/SC-04 and PLAN.md's constraints both describe this path as coming from "the signed
ship review, the approved artifact" — i.e., composed and handed to `gh-sync.py` by the main session
after a human-reviewed step, not by an external or lower-trust agent. An actor who could already
control the CLI argv reaching `gh-sync.py ship/abandon` could run arbitrary local commands directly;
the path-validation gap adds nothing a local-code-execution attacker doesn't already have. **Assessed
as `med`-at-most defence-in-depth, not a finding**: worth a future path-confinement check (e.g.,
requiring the file live under the feature's own `notes/`) if the calling convention ever widens to a
less-trusted composer, but nothing in this diff does that.

## `GH_SYNC_GH` — assessed inert

`gh_issues.py:13-14`, `gh-sync.py:48`, `wayfind.py` (via `ghi.gh_bin()`) all resolve the binary name
from `os.environ.get("GH_SYNC_GH", "gh")`. Under this threat model (a local, single-operator CLI) an
actor able to set the process's environment variables can already execute arbitrary code in that
process's context — the env-var indirection adds no privilege the attacker didn't already have. It
exists purely so `test-gh-sync.py` never touches a real `gh` (SC-09), confirmed: the fake binary is a
temp-dir shell script the test harness writes and points `GH_SYNC_GH` at
(`test-gh-sync.py:23-48,100-105`); no test invokes a real `gh`. Not a finding.

## Data exposure

- `gh()`'s SKIP message (`gh-sync.py:87`) echoes `args[:3]` (e.g. `api`, the `repos/{repo}/issues/{num}`
  path) plus up to 200 chars of gh's stderr/stdout to the harness's own stdout. The repo slug is
  already recorded in the committed `harness.json`; the truncated stderr is gh's own error text, not
  harness-controlled secrets. `wayfind.py:76,91` echo full untruncated stderr the same way. **Info**:
  this is operator-facing stdout in a local CLI, not a log shipped anywhere external, and nothing
  observed here would leak a token (gh's own CLI does not print its stored auth token on failure).
- No credential, token, or PII is read from `feature.yaml`/`PLAN.md`/`BRIEF.md` and forwarded; the
  fields consumed are titles, bodies, labels, and issue/milestone numbers.
- SC-10's discriminating check (`FEAT-03-subissue-mirror/feature.yaml`'s own `github:` block staying
  unpopulated) was verified directly against the pin: `git show e68ba00:.../feature.yaml` shows
  `parent: none / milestone: none / issues: {}` — confirms this feature's own bookkeeping change
  carries no live parent/milestone/issue numbers into a tracked file.

## Minor, non-blocking

- `int(parent_arg)` (`gh-sync.py:259`) is uncaught on a non-numeric `--parent` value — raises a raw
  Python traceback rather than a clean `die()` message. A UX/diagnostics gap, not a security bypass
  (the process still exits non-zero; nothing proceeds silently). Info.
- `ensure_labels` (`gh-sync.py:210-220`) swallows the `gh label create` return code entirely
  (comment explains: "already exists" is the common failure). Deliberate, matches the "errors here
  are swallowed" comment; noted so a future scan doesn't re-flag it as an oversight.

## Assessed-and-dismissed (closed list — none changed the verdict)

- SC-06 identical-endpoint carve-out (list GETs retained in `wayfind.py`) — verified by the two
  grep counts above, both 1 as required.
- `gh-sync.py` importing `parent_args`/`blocked_by_args` — verified absent (count 0); this is D-01's
  write-only guarantee, not an untested branch.
- `wayfind.py:270`'s redundant `issue(repo, num, "id")` pre-attempt — present, deliberately retained
  per PLAN:224-227; not flagged.
- The `ticket` dry-run's literal `-F sub_issue_id=` prose (`wayfind.py:266`) — confirmed still prose,
  not an argv build; excluded correctly from the SC-06 grep scope.
- D-02's inverted `absorbs:` assertions, D-01's leave-open defaults for absent/unrecognised
  `parent_origin`, the unconditional `--body-file`/comment step on `ship` — all present as specified,
  matched against PLAN.md/BRIEF.md text cited above; none are findings.
- SC-10: FEAT-03's own `feature.yaml` `github:` block confirmed still `parent: none / milestone: none
  / issues: {}` at the pin (see Data exposure section) — no retrofit occurred.

## Housekeeping

No files were staged, committed, reverted, or stashed. No probe files were created. `git status
--porcelain` at close is unchanged from the pre-review snapshot:
```
 M .harness/features/FEAT-03-subissue-mirror/STATE.md
 M .harness/features/FEAT-03-subissue-mirror/feature.yaml
 M .harness/logs/2026-07-31.md
```
