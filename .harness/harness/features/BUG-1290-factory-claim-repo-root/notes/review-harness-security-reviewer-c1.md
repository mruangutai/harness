
# Security review — BUG-1290 factory-claim-repo-root — c1

**Verdict: PASS, severity_max=info.** Diff `4e52d2e3..419614e5` (code range within
`4e52d2e3..76e26386`) read in full over the named file set. No must-fix findings. One
pre-existing (not diff-introduced) low-value info item, one info-level hardening suggestion.

## Scope

In scope: `factory_config.py` (`segment_of`, `features_root`), `factory_claim.py`
(`_BlockerCache`, `_blocker_gate`, candidate filtering step 4), `feature-worktree.py:resolve_repo`.
Reason: the diff turns a hardcoded single features root into a per-repository-name filesystem
join, so repo-name-to-path resolution is the trust boundary. `layout_migration.py`/`layout_fixtures.py`
changes are internal reader-table bookkeeping for an unrelated static-analysis tool (no runtime
input, no security surface).

## Q1 — path traversal via `segment_of`/`features_root` on a hostile repo-name

`segment_of` (`factory_config.py:397-402`) is `repo_name.split("/", 1)[-1]` and `features_root`
(`:405-411`) does `os.path.join(root, ".harness", seg, "features")`. Verified mechanically
(python repro): `"owner/../../etc/passwd"` → seg `"../../etc/passwd"` → path escapes `root`;
`"owner/"` → seg `""` → path collapses to `root/.harness/features` (segment silently dropped, no
escape); embedded `\`/NUL are inert on POSIX joins or raise `ValueError` (no traversal, potential
crash). **So the join itself is not traversal-safe** — but the value it receives is constrained:

- Every call site (`_BlockerCache.plan_path`, `.root_exists`, `.issue_number` at
  `factory_claim.py:170,190-192,197`) is invoked only with a `repo_name` drawn from
  `candidates` (`factory_claim.py:~300-315`), which step 4 already filters to
  `repo_name in served_repo_names` (exact string membership) — `served_repo_names` is built
  from `fleet["repos"]` entries (`.harness/factory/fleet.yaml`), a git-tracked, PR-reviewed
  operator config file with no writer anywhere in the tree that derives an entry from issue/PR
  content (checked `factory_gh.py`, `harness_boundary.py`, `board_lifecycle.py` — all only
  *read* fleet.yaml). An attacker who controls GitHub issue/PR/project-item content
  (`_repo_name_of`, `factory_claim.py:70-79`) can only produce a `repo_name` that either matches
  a real fleet entry byte-for-byte (no traversal payload survives an exact match against a
  legitimate `owner/repo` string) or gets filtered out at step 4 before reaching `segment_of`.
  **Verdict: not attacker-reachable in practice** — the traversal-shaped join is real but the
  only path to it is a fleet.yaml misconfiguration (operator-trusted), not attacker input.
- The one value that *is* attacker-influenced without a matching-set filter is the `feature` id
  (from the issue's `feature:<X>` label, `_feature_of`, `factory_claim.py:44-56`), which flows
  unsanitised into `os.path.join(root, feature, "plan.yaml"/"feature.json")`
  (`factory_claim.py:170, 190`). Confirmed identical shape on `4e52d2e3` (pre-diff) — this join
  was already unsanitised before BUG-1290; the diff only changes which `root` it's joined under,
  not whether `feature` is validated. **Recorded as pre-existing, not diff-introduced** (P-09).
  Practical impact is low even if triggered: a traversal `feature` value either fails to parse as
  a plan (falls into the `no_plan` refusal, which echoes the resolved path back — REQ-03,
  signed) or must land on a file that already validates as harness-plan YAML to leak anything,
  which is not attacker-achievable from an issue label alone. Not gating this review.

## Q2 — cross-tenant data exposure via `_BlockerCache` keyed on `(repo, feature)`

No. `_BlockerCache.__init__` (`factory_claim.py:98-100`) keys `_plans`/`_issue_maps` on
`(repo, feature)` tuples, and every read/write path (`_plan`, `plan_loaded`, `task`,
`issue_number`, `factory_claim.py:150-198`) is invoked with the *current* candidate's own
`repo_name` from the same loop iteration — there is no code path that looks up one repo's cache
entry while evaluating a different repo's candidate. This is in fact the confidentiality boundary
this diff *establishes*: pre-diff (`4e52d2e3`), `_BlockerCache` was keyed on `feature` alone under
one hardcoded `FEATURES_ROOT` (a single-repo assumption); multi-repo serving is new to this
feature, and the `(repo, feature)` keying is the fix that prevents a same-named feature id in two
served repos from aliasing. `tests/unit/test-factory-claim.py` case "5b"/SC-02 and the mutation
proof `test-factory-claim-mutation.py` (discards the `repo` argument at the `features_root` seam,
requires cases 5a/5b/5c to redden under that mutant) is exactly this scenario, mutation-verified.
No confidentiality gap found.

## Q3 — `no_plan` refusal / new log lines exposing filesystem or environment detail

`_blocker_reason_text`'s `"no_plan"` branch (`factory_claim.py:213-223`) prints the resolved
absolute path via `cache.plan_path(repo, feature)` — REQ-03 requires this explicitly and it is
signed-approved (BRIEF `## Approval`); flagged per dispatch as a decision question, not a fix.
The only *behavioral* change from pre-diff is that the printed path now varies by the *current
candidate's own* repo segment instead of being a fixed string — it never prints another served
repository's path for a request about this one, so no incremental exposure beyond what REQ-03
signs off on. Checked every other new/changed print/refusal in the diff
(`_repo_name_of`'s stderr normalisation notice, `_emit`'s stdout payload, the multi-feature-label
warning) — none is new to this diff in shape, and none of them carry an absolute path, a token,
or a credential. `fleet_path` appears in an unrelated, unchanged refusal message
(`factory_claim.py:~309`, board-station mismatch) — pre-existing, out of this diff's line range.

## Q4 — fail-open on an unresolvable repository

No new fail-open path. `_repo_name_of` extracts a candidate's repo name, then step 4
(`factory_claim.py:~300`) filters with `if repo_name not in served_repo_names: continue` —
*before* the candidate is added to `candidates`, and therefore before any call into
`_BlockerCache`, `features_root`, or `factory_config.repo_entry`. An unresolvable/unserved
repository is silently dropped from the poll (not claimed, not gated, not logged as a hard
error) — this is unchanged pre-existing behavior (dedup-by-repo already existed for multi-repo
board serving) and is explicitly signed as a constraint in `BRIEF.md`: "No new refusal path for
an unknown repository: `factory_config.repo_entry` and candidate step 4 already fail closed.
BOUNDS the change." Confirmed by reading: no call in the diff reaches `segment_of`/
`features_root` with a value that hasn't passed the step-4 membership filter or the explicit
`--repo` `repo_entry()` raise.

## Q5 — injection into subprocess/shell from the resolved segment

None. `factory_gh.py` invokes `gh` exclusively via `subprocess.run([gh] + list(args), ...)`
(`factory_gh.py:153-155`) — argv-list form, no `shell=True`, no string concatenation into a
shell command anywhere in the diff or its call sites. `repo`/`repo_name` is always passed as the
*value* following an explicit `--repo` flag token (`issue_view`, `add_label`, `assign`,
`create_ref` call sites in `factory_gh.py:215,220,224,924` etc.) or interpolated into a `gh api`
REST path argument (`default_branch_sha`, `factory_gh.py:882-883`) — never itself passed as a
bare positional that `gh`'s flag parser could misread, and never containing `segment_of`'s
output (segment values feed only filesystem joins, never `gh` argv). `repo_name` reaching these
calls is fleet.yaml-exact-match-constrained per Q1's finding, so even a theoretical flag-prefix
concern is moot on operator-trusted input.

## Findings

None gating. No must_fix.

## Informational (non-gating)

- `INFO-1`: `features_root`'s join is not traversal-safe in isolation (Q1) — currently
  inert because every runtime call site constrains `repo_name` to an exact fleet.yaml match
  first. Worth a `segment_of`/`repo_entry` validation (reject `/`, `..`, empty, leading `.` in a
  fleet-declared name) as defense-in-depth against a future caller that skips the step-4 filter,
  not because any current path reaches it. No concrete attacker scenario exists today —
  `not-actionable` at this severity.
- `INFO-2`: the `feature`-label-derived path join (`os.path.join(root, feature, ...)`) has no
  input validation, pre-existing since before this diff and unchanged by it. No concrete
  attacker-achievable content-disclosure scenario found (requires a traversal target that also
  validates as harness plan/feature.json schema) — recording per P-09/P-12 so a later reviewer
  doesn't re-derive this from scratch, not raising severity.

## Threat model

| boundary | STRIDE | mitigated |
|---|---|---|
| GH issue/PR content → `repo_name`/`feature` used in filesystem path | Tampering | true (repo: exact-match filter; feature: pre-existing, low-impact, not this diff's to fix) |
| served-repo A candidate reading served-repo B's plan/feature.json cache | Information disclosure | true (this diff's own `(repo, feature)` keying fix, mutation-proven) |
| unresolvable/unknown repository proceeding past claim gating | Elevation of privilege / fail-open | true (filtered before any path resolution, signed BOUNDS constraint) |
| resolved segment reaching `gh` subprocess argv | Injection | true (argv-list form throughout, no shell) |
