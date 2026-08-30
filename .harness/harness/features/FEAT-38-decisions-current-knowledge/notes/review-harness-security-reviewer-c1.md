# Security re-review c1 — FEAT-38-decisions-current-knowledge — `review_sha` `2557950`

## Verdict on F-1 (cycle-0 HIGH): CLOSED for the documented threat model. One new MEDIUM finding, not the same class, does not gate.

## F-1 — the `-c core.fsmonitor=<cmd>` document-to-shell RCE

**Closed.** Drove the checker's own real code path — imported `check-decision-claims.py` at the pin
(bytes verified identical to `git show 2557950:...`, confirmed no working-tree drift via
`git diff 2557950 -- <4 files>` = empty) and called `refusal_reason()` and, for the ones it allows,
`run_claim()` end-to-end with an observable side effect (a file under `/tmp/sec_probe`), never a
hand-rolled `subprocess.run`.

All three cycle-0 vectors refused, payload unexecuted:
- `git -c "alias.zz=!<cmd>" log -1` → refused at rule 2 (option before subcommand).
- `git -c "core.fsmonitor=<cmd>" status` (and `... log -1`) → refused at rule 2; `status` also not in
  `ALLOWED_GIT_SUBCOMMANDS` regardless.
- `git -c "diff.external=<cmd>" diff --ext-diff` → refused at rule 2.

**Position bound holds against real git, not just the checker's own logic** — I moved the boundary
myself and it did not move for the attacker. Empirically, against a scratch repo
(`git 2.50.1 (Apple Git-155)`), with `-c`/`--config-env`/`--exec-path`/`--git-dir`/`--work-tree` placed
**after** the subcommand instead of before it:
- `git log -c "alias.zz=!touch ..."`, `git diff -c "core.fsmonitor=touch ..."`, `git grep -c "..." x` —
  the checker's `refusal_reason()` ALLOWS these (rule 2 only inspects `rest[0]`), but real git does
  **not** honor `-c` there — `log`/`diff`/`grep` each have their *own*, unrelated `-c` meaning
  (combined-diff / count), confirmed by running them directly and by `run_claim()` (payload files
  never appeared).
- `--config-env=`, `--exec-path=`, `--git-dir=`, `--work-tree=` placed after the subcommand: real git
  rejects every one with `fatal: unrecognized argument: ...` (tested `=`-joined and separated forms).
  So rule 2's claim ("no option before the subcommand" kills these) is true precisely because git
  itself refuses them once genuinely repositioned — the boundary did not just move to an
  equally-live spot.
- `-O`/`--open-files-in-pager` (`git grep -O<cmd>`, clustered `-rO`, `-O=cmd`, and misapplied to
  `log -O`) → refused uniformly by `_git_open_pager_option`, independent of which subcommand it
  trails.
- `--ext-diff` / `--textconv` (`git diff --ext-diff`, `git show --textconv`) → allowed by the checker,
  but produce ordinary git output (verified via `run_claim`), because rule 5's env neutralization
  removes the `diff.external`/`textconv` config that would have to be set for either to do anything —
  see below for the one channel where that neutralization is incomplete.
- Marker-parsing edge cases (`git --`, `git -`, an empty-string token in the subcommand position) →
  all refused; no smuggling.

**F-1 verdict: CLOSED**, not merely moved, for the reachable threat model (a PR that only adds a
claim-marker string to `DECISIONS.md`).

## New finding — MEDIUM, does not reopen F-1, does not gate

Rule 5's own docstring claims ambient git config is "unreachable even though it was never named in a
command string at all." That claim is **incomplete**: it only neutralizes `GIT_CONFIG_GLOBAL`,
`GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM`. Git has a fourth, independent env-based config channel —
`GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>` — that `_subprocess_env()`
(`check-decision-claims.py:248-260`) passes through unmodified from `os.environ`.

**Proven, not theorized**, via `run_claim()` itself: with `GIT_CONFIG_COUNT=1`,
`GIT_CONFIG_KEY_0=diff.external`, `GIT_CONFIG_VALUE_0='touch /tmp/... ; echo hostile-diff'` set in the
*process* environment (not the marker, not argv), `run_claim('git diff --ext-diff')` — an
already-allowlisted, zero-refused-token command — executed the payload: the touch target was created
and stdout contained `hostile-diff`.

**Reachability, honestly bounded — this is why it's MED, not HIGH.** The precondition is that the
*process invoking the checker* already carries attacker-set `GIT_CONFIG_COUNT`-family env vars. I
checked whether the documented F-1 threat actor (a PR touching only `DECISIONS.md`) can reach that
precondition: no. `.github/workflows/tests.yml` sets no `GIT_CONFIG_*` env anywhere, and for
`pull_request`-triggered runs GitHub reads the workflow file from the **base** branch, not the PR
head, so a fork PR cannot inject job-level env by editing the workflow either. There is no path from
"PR adds a claim marker" to "job environment carries `GIT_CONFIG_COUNT`." Whoever *could* set that
precondition (a compromised earlier CI step, a self-hosted runner with leaked env, a developer's own
shell) already has a capability well beyond what this checker is trying to bound. **Severity: MED —
requires unusual access or preconditions; a real gap in rule 5's stated invariant, not an active hole
in the reachable (PR) threat model.** Not `must_fix` given the budget and non-reachability; recorded
so a future hardening pass closes it (e.g. also neutralizing `GIT_CONFIG_COUNT` and clearing any
existing `GIT_CONFIG_KEY_*`/`GIT_CONFIG_VALUE_*` from the inherited env, not just the three named
vars).

## Secondary finding — LOW, no execution, no gate

Rule 6 ("for grep, no argument reads from a file or a device") is implemented in
`_refusal_reason_grep`, which only runs when the command's **first token is bare `grep`**.
`_refusal_reason_git` (used whenever the first token is `git`) never calls it. Confirmed via
`refusal_reason()` and `run_claim()`: `git grep -f <file>`, `--file=<file>`, and clustered `-rf`
**bypass rule 6 entirely** and run for real, while the equivalent bare `grep -f <file>` is correctly
refused (existing test `test_grep_dash_f_argument_file_is_refused_and_never_blocks_on_fifo` only
exercises the bare-`grep` path, so this gap has zero test coverage). Real impact is bounded: `-f`
reads regex *patterns*, not code — no execution primitive, no content exfiltration (only match/no-match
against tracked content), worst case a ≤10s blocking read (bounded by the existing subprocess timeout,
already tolerated for every other allowlisted command). `--devices` doesn't exist as a `git grep`
option at all, so that arm of rule 6 is dead code on the `git` path regardless. **LOW** — a real
completeness gap against the remedy's own stated invariant (worth a code-quality/spec-compliance note
to the other reviewer), not an execution-boundary defect.

## Residual accepted as-is, per the dispatch's framing

Repo-local `.git/config` is unaffected by `GIT_CONFIG_GLOBAL`/`SYSTEM`/`NOSYSTEM` by design (those
redirect/disable the *global* and *system* files only; git always reads the local repo's own config).
**I accept this boundary**: `.git/config` is CI/git metadata, never tracked repository content, so no
PR — the actual reachable attacker here — can write to it. Unlike the `GIT_CONFIG_COUNT` finding
above, I found no channel by which PR-controlled content becomes `.git/config` content in this
pipeline (no build step copies tracked files there). Not a finding.

## Verification performed (every probe named, including the ones that failed to get through)

`refusal_reason()` and, for allowed commands, `run_claim()` with an observable filesystem side
effect, run against: pre- and post-subcommand `-c`/`--config-env`/`--exec-path`/`--git-dir`/
`--work-tree` (`=`-joined and separated); `-O` bare/clustered/`=`-joined and misapplied to a
non-grep subcommand; `--output=`; `--ext-diff`/`--textconv` (allowed, but non-executing once rule 5's
covered channels are neutralized); `git grep -f`/`--file=`/clustered `-rf`/`--devices=` vs. bare
`grep` equivalents; non-allowlisted subcommands (`commit`, `apply`, `submodule`); first tokens other
than `git`/`grep`; empty command; lone `-`/`--`; empty-string subcommand token; and the
`GIT_CONFIG_COUNT`/`KEY`/`VALUE` ambient-env channel. Also ran the pinned
`test-check-decision-claims.py` in full (21/21 pass, including `test_live_authority_claims_all_hold`
against the live document).

```yaml
VERDICT: PASS
DIGEST:
  headline: "F-1 (git -c RCE) is CLOSED, not moved — every reposition of -c/--config-env/--exec-path/--git-dir/--work-tree after the subcommand is refused by real git itself, not just the checker; one new MEDIUM gap found (GIT_CONFIG_COUNT ambient-env bypasses rule 5's neutralization, proven via run_claim) but it is unreachable from the documented PR threat model, so it does not gate."
  in_scope: true
  scope_reason: "Re-grading a HIGH RCE finding in a document-to-shell execution path is squarely a security surface; also swept the remedy's own new rules for execution-boundary gaps it might have introduced."
  severity_max: medium
  findings: 2
  must_fix: []
  threat_model:
    - { boundary: "PR content (DECISIONS.md claim marker) -> CI Integration suite -> check-decision-claims.py -> subprocess.run(argv)", stride: T, mitigated: true }
    - { boundary: "checker argv -> git binary -> -c/--config-env/--exec-path/--git-dir/--work-tree in any position -> config-driven hook/alias/external-diff", stride: E, mitigated: true }
    - { boundary: "checker process environment (GIT_CONFIG_COUNT/KEY/VALUE) -> git config -> diff.external -> shell, via any allowlisted subcommand", stride: E, mitigated: false }
    - { boundary: "git grep -f/--file/-rf argument-file read via the git-subcommand path (vs. bare grep, which is checked)", stride: I, mitigated: false }
    - { boundary: "repo-local .git/config honored by design", stride: T, mitigated: true }
  open_questions:
    - { id: Q1, question: "Schedule a follow-up hardening pass on check-decision-claims.py: (a) also neutralize/clear GIT_CONFIG_COUNT and any inherited GIT_CONFIG_KEY_*/GIT_CONFIG_VALUE_* in _subprocess_env(); (b) route _refusal_reason_git's grep subcommand through _grep_file_or_device_option too, so `git grep -f/--file/-rf` is refused the same as bare `grep -f`. Neither is reachable by the documented PR threat model today, so neither blocks this ship.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/review-harness-security-reviewer-c1.md
```
