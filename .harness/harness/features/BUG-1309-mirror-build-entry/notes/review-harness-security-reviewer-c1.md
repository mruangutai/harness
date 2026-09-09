# Security review c1 — BUG-1309-mirror-build-entry — review_sha d80a7b12 (code pinned at 1ad433b4)

## BLUF
**F1 is CLOSED.** No new high stands. `severity_max: low`. Recommend PASS.

## F1 closure — reconstructed scenario, executed
Cycle-0's F1 demonstrated `GH_BIN=/nonexistent/gh` + a non-era-exempt feature with `github.build_entry`
absent + `gh pr merge 42` crashing `main()` with an uncaught `FileNotFoundError` (exit 1, no deny
JSON — silent allow). `bash-write-guard.sh` denies this reviewer any disk write, including in `/tmp`
(REVIEWERS read-only, no path carve-out — verified live: my own `cat >`/`rm` attempts were blocked).
So I reconstructed the scenario as a real, unmodified, in-process execution of `merge-gate.py` loaded
from disk (`importlib.util.spec_from_file_location`), with `open`/`glob.glob` monkeypatched to hand
back in-memory fixture content in place of disk files — the `gh` subprocess call itself was **not**
mocked; it really invoked `subprocess.run(["/nonexistent/gh", ...])` and really raised
`FileNotFoundError`, exercising `gh_head`'s new `except OSError` for real.

- `gh_head("42","owner/repo")` alone, real unresolvable binary: returns
  `('', "[Errno 2] No such file or directory: '/nonexistent/gh'")` — no exception. (merge-gate.py:75-85)
- Full `main()`, feature not era-exempt, `build_entry` absent, `gh pr merge 42`: prints
  `{"hookSpecificOutput":{...,"permissionDecision":"deny","permissionDecisionReason":"merge-gate: BUG-9999 records github.build_entry=absent..."}}`
  to stdout, no traceback, process falls off the end (exit 0).

**Exit-code correction to the dispatch's framing:** "only exit 2 blocks" is bash-write-guard.sh's
convention, not merge-gate.py's. `deny()` (merge-gate.py:~103) never calls `sys.exit`; the hook's own
test suite asserts the CORRECT deny outcome as `r.returncode == 0 and d == "deny"` (JSON on stdout) —
see `tests/integration/test-merge-gate.py:65,73,95,100`. This doesn't change the finding: a crash
produces neither valid deny-JSON on stdout nor exit 2, so it is a silent allow under either
convention. Recorded so the next reader doesn't misjudge a future finding by exit code alone.

Corroborated by the already-green fixture at `tests/integration/test-merge-gate.py:97-101`
("T-05 unresolvable gh falls back and denies a locally owed receipt", identical shape to my repro).

## No-overshoot — answered separately, both required cases executed
Same in-process harness, same real `/nonexistent/gh` OSError, two more fixtures:
- Entry `opened` (owes nothing), not era-exempt → `permissionDecision` absent (allow), stderr:
  `"merge-gate: could not verify this merge - the head branch could not be resolved through gh (...) ... allowing it, because GitHub is a mirror and never a gate (DEC-138)."`
- Local branch matches no `feature.json` at all → same allow, same DEC-138 stderr line.

Neither overshoots into deny. SC-04's last clause and DEC-138 hold under the fixed code.

## F2 disposition (basename-only detection, cycle-0 low)
Unchanged, still open, still non-gating. `git show 1ad433b4` touches only `gh_head` and `main`;
`is_bin`/`direct_merge`/`gh_merge`/`git_merge`/`nested_merge`/`merge_ref` are byte-identical to
cycle-0. Same reasoning as before (P-02): an actor precise enough to evade basename detection
already has the local `feature.json`-edit privilege the design accepts as the trust boundary
(DEC-138/D-07).

## New-in-remediation findings — none gating; two assessed-and-dismissed
- **`UnicodeDecodeError` in `gh_head`'s `subprocess.run(..., text=True)`** (merge-gate.py:75-80):
  `except OSError` does not catch a `UnicodeDecodeError` from adversarial/corrupt bytes on the `gh`
  process's stdout/stderr; `TimeoutExpired` is unreachable (no `timeout=` kwarg) and `ValueError`
  is unreachable (argv is well-formed strings, no incompatible `stdout=`/`capture_output` mix).
  If it fired, it would propagate uncaught → same silent-allow shape as the original F1. **Not new**:
  before this diff, the whole call had *no* try/except, so every exception including this one was
  already uncaught — the fix narrowed exposure to OSError-only rather than widening it. Reachability
  requires the same actor who already controls what `gh`/`GH_BIN` resolves to on this machine — P-02,
  same non-escalating class as F2. **low, non-gating.**
- **`local_branch()` (merge-gate.py:71-73) has no try/except around its own `subprocess.run(["git",...])`.**
  An unresolvable `git` binary would crash the same way the old `gh_head` did. Untouched by this
  diff — pre-existing, not introduced. Far lower likelihood than `gh`'s absence: `git` is
  load-bearing for the harness to run at all (worktrees, `harness_boundary.resolve_root`), whereas
  `gh` absence is an anticipated, named condition (DEC-138: "`gh` absent... the flow succeeds").
  **info, non-gating, pre-existing.**
- **`import feature_schema` moved from module scope into `main()`** (merge-gate.py:8,126): fires
  after the `github.get("sync") / merge_ref(command)` early-return, so it now runs on *fewer*
  invocations than before (previously at module scope it ran on every Bash call this hook sees,
  matched or not). An `ImportError` there is not newly reachable — it never was: the module ships
  in the same directory, is imported successfully by 322 passing `test-gh-sync.py` cases and by
  every other integration suite the lead ran. A narrowing of exposure, not a new fail-open route.
- **Universal-hook-becomes-universal-traceback**: not reachable. `merge_ref(command)` gates every
  path that changed (`import feature_schema`, `head_branch`, `gh_head`, `feature_for`) behind
  "this command looks like a merge" — confirmed by reading `main()` top-to-bottom (merge-gate.py:126-135).
  Non-merge Bash calls (`git status`, `ls`, …) return before any of the touched code runs.
- **Token/PR-body/issue-payload leakage**: none. The only new data flowing to output is
  `str(exc)` (e.g. `[Errno 2] No such file or directory: '/nonexistent/gh'`) interpolated into the
  existing DEC-138 stderr audit line — echoes the operator-set `GH_BIN` path, not a secret.

## Threat model
| boundary | STRIDE | mitigated |
|---|---|---|
| `gh_head`'s subprocess crash defeating the merge decision (F1) | Tampering | **true** — closed, reconstructed and re-run |
| no-overshoot: unresolvable `gh` denying a merge that owes nothing | Denial of service (self-inflicted false deny) | **true** |
| `gh_head`'s narrower `UnicodeDecodeError`/adversarial-output gap | Tampering | false, but non-escalating (P-02) — assessed |
| `local_branch`'s unresolvable-`git` crash | Tampering | false, pre-existing, far lower likelihood — assessed |
| command-string basename detection (F2) | Tampering (evasion) | false, but non-escalating — unchanged from c0 |

## open_questions
None blocking.
