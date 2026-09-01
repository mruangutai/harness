# FEAT-50 security recheck — pinned fix cycle `dca2d3d..7505b87`

**Verdict: PASS.** All three prior findings are CLOSED, empirically retested with mutation kills
against a fresh, independently-built fixture (not the fix's own test harness). The outcome-branch
sweep found no sibling gap of the same shape. No new fail-open introduced by the changed lines.

**SHA note:** worktree HEAD is `7505b8739fd19a68601a27898d880fc719962712`; the dispatch's pinned sha
`7505b87681c8d8007a2677381313581f61faf1b0` does not exist in this repo (`git cat-file -t` fails). Both
share only the 7-char prefix `7505b87` and HEAD's commit message (`fix: close FEAT-50 review
findings`) matches the expected fix commit, so I reviewed HEAD as the intended target. Flagged as a
non-blocking open question — the dispatch sha is corrupted/mistyped, not a resolvable ambiguity.

## Finding 1 (HIGH, security) — CLOSED

Fix: `bash-write-guard.sh:785` adds `feature_checkout_guard(rel, ap)` under the `shared` branch
(previously only the `allow`/`not_a_domain_question` branch called it, confirmed absent at
`dca2d3d:bash-write-guard.sh:783-789`).

Independent fixture (`/tmp/feat50sec/repro1.py`, not the shipped test): a fresh temp checkout with
`shared: [{path: .harness/*/features/*/BRIEF.md}]`, `harness-documentor` with `domain: []`, and a
real linked worktree (`.git/worktrees/<id>/gitdir` + worktree-side `.git` pointer) for
`FEAT-SECCHK-thing`, targeting the MAIN-checkout `BRIEF.md`.

```
bash-write-guard.sh (Bash route)  exit=2  "...is a feature artifact whose write belongs in worktree .../.claude/worktrees/FEAT-SECCHK-thing..."
check-domain.sh (Write route)     exit=2  "...is a feature artifact whose write belongs in worktree..."
```

Both routes now agree (2/2), closing the exact divergence in the finding.

**Mutation, scoped to only the shared-branch call** (not the shipped test's both-calls mutant): copied
`bash-write-guard.sh`, deleted only
```
        if verdict["outcome"] == "shared":
            feature_checkout_guard(rel, ap)
```
→
```
        if verdict["outcome"] == "shared":
```
Re-fired the identical shared-outcome payload against the mutant:
```
MUTANT bash-write-guard.sh exit=0   (real script: exit=2)
```
The mutant alone reproduces the pre-fix bypass (write allowed) while the real script refuses —
proving the added line, and only that line, is what closes it. Shipped regression test
(`test-bash-write-guard.py::run_feat50_checkout_binding`, cases `bash-feature-checkout-shared` and
`bash-feature-checkout-red`) passes: `6/6 FEAT-50 Bash binding cases passed`.

## Finding 3 (MED, security) — CLOSED, and confirmed NOT a blanket deny

Fix: `check-domain.sh:1142-1155` — `prior = None` by default; `FileNotFoundError` only sets
`prior = ""` when `os.path.lexists` is also false (i.e. genuinely absent, not a broken symlink); any
other `OSError` (`PermissionError`, `IsADirectoryError`) leaves `prior = None`; `prior is None` denies.

Independent fixture (`/tmp/feat50sec/repro3.py`) against a real `runs/<id>/digest.md`, one case per
plausible "prior exists but unreadable" shape, plus the two must-stay-open controls:

| case | exit | expectation |
|---|---|---|
| `chmod 000` on a real prior digest | **2** | refuse — matches |
| broken symlink in place of the digest | **2** | refuse — matches |
| directory in place of the digest | **2** | refuse — matches |
| genuinely absent file (never created) | **0** | allow — matches, not swept into the deny |
| prefix-preserving write over real prior content | **0** | allow — matches, fix did not become a blanket deny |

`PermissionError`/`IsADirectoryError` are `OSError` subclasses, not `FileNotFoundError`, so they hit
the bare `except OSError: pass` and leave `prior = None` → denied. The broken symlink also lands in
`except OSError: pass` (its `open()` raises `FileNotFoundError`, but the inner `os.path.lexists` guard
is true for a dangling symlink, since the link itself exists — so `prior` stays `None`, correctly
refused). Shipped regression test now carries `digest-unreadable` (directory-in-place, expects
`"cannot be read safely"` in stderr) alongside the pre-existing `digest-clobber`/`digest-append`/
`digest-clobber-red`; full suite: `10/10 FEAT-50 artifact-integrity cases passed`.

*Noise, not a finding:* both fixture runs print `check-domain: the main_session.writes exclusion list
was unreadable (...)` — that's `approval_guard`'s own pre-existing, unrelated diagnostic firing because
my minimal test manifest has no `main_session:` key; it only `return`s (never gates) and is untouched
by this fix.

## Finding 2 (HIGH, code quality) — CLOSED (spot-checked; primary owner is code-reviewer)

`code-grade.py --json` on both files:

| function | before (reported) | after (measured) |
|---|---|---|
| `run_feat50_checkout_binding` | grade 1: cyc 11 / cog 9 / ABC 59.6 | **grade 4, PASS**: cyc 1 / cog 0 / ABC 16.1 |
| `run_feat50_artifact_integrity` | grade 1: cyc 17 / cog 14 / ABC 85.8 | **grade 4, PASS**: cyc 1 / cog 0 / ABC 20.0 |

Diff is a pure extraction into named helper functions/module constants; no assertion was weakened —
`digest-unreadable` and the `bash-feature-checkout-shared` case were *added*, not removed, and the
mutant anchors (`source.count(call) != 2`, the `mutant_between` markers) were updated to match the new
call count rather than loosened. A pre-existing, untouched `run_t14` (same file, not named in any
finding, not touched by `dca2d3d..HEAD`) still grades FAIL at cyc 8/ABC 51 — out of this cycle's scope.

## Task 3 — outcome-branch sweep (the defect class finding 1 belongs to)

**`bash-write-guard.sh`** (`verdict["outcome"]`):

| outcome | reached only when write is allowed to land? | `feature_checkout_guard` runs? | agrees with `check-domain.sh`? |
|---|---|---|---|
| `out_of_place_worktree` (+ unparsed) | no — `deny()` exits 2 unconditionally | n/a (already refused) | yes, same shape refusal |
| `allow` / `not_a_domain_question` | yes | **yes** (pre-existing, `:781`) | yes |
| `shared` | yes | **yes** (this fix, `:785`) | yes |
| final fallthrough (target outside domain) | no — `deny()` exits 2 | n/a (already refused) | yes |

**`check-domain.sh`** (`_verdict["outcome"]`):

| outcome | write lands? | `feature_checkout_guard` runs? |
|---|---|---|
| `out_of_place_worktree` | no — `sys.exit(2)` | n/a |
| `not_a_domain_question` | yes, but `rel is None` by construction (`classify()` only returns this when `base is None`, i.e. the target resolves inside NO base) — a feature-artifact path (`.harness/*/features/*/...`) can never carry this outcome, since `select_base` matches "inside `abs_root`" before anything else | no call, but structurally unreachable for a feature path — not a gap |
| `allow` | yes | **yes** (pre-existing, `:876`) |
| `shared` | yes | **yes** (pre-existing, `:881`) |
| final fallthrough (deny) | no — `sys.exit(2)` | n/a |

No sibling gap: every branch that lets a write land either already denies main-checkout writes by a
different mechanism or calls `feature_checkout_guard`. `not_a_domain_question` is theoretically reachable
with `rel` still resolving to a feature path only through a symlink escape (raw path textually inside
root, `real()`-resolved target outside it) — that shape is pre-existing on both routes, untouched by
this diff, and matches the already-disclosed REQ-03 sibling-worktree residual category; not re-reported
as new.

## Task 4 — changed-lines fail-open audit (`dca2d3d..7505b87`, both scripts only)

Only two hunks change production code in this cycle (verified via `git diff --stat`; the rest is test
refactor + already-reviewed doc/plan/BRIEF files unchanged since `dca2d3d`):

- `bash-write-guard.sh:785` — one added line, no new `except`/fallback/silent return. Calls a
  pre-existing `feature_checkout_guard` whose own `except Exception: return` absorb-on-bug behavior was
  already in scope of the prior review cycle, not new here.
- `check-domain.sh:1140-1158` — new `except FileNotFoundError` / `except OSError: pass` pair, audited
  above (task 1/finding 3 table): every OSError variant other than a proven-absent path now denies;
  no new silent-allow path introduced.

No new secret/credential-shaped string anywhere in `dca2d3d..HEAD` (`git diff | grep -iE
'password|secret|token|api[_-]?key|BEGIN (RSA|OPENSSH|PGP)|AKIA'` → no matches).

## Open questions

- Q1 (non-blocking): pinned sha in the dispatch (`7505b87681c8d8007a2677381313581f61faf1b0`) doesn't
  exist in the repo; I reviewed worktree HEAD `7505b8739fd19a68601a27898d880fc719962712` instead
  (matching commit message, matching diff content). Worth fixing the dispatch's sha for the next
  reviewer's copy-paste.

## Fixture cleanup

All fixtures were built under `mktemp -d` / `/tmp/feat50sec/`; nothing under the worktree's source
tree was touched or left behind. No project-wide test suite was run — only the two named single-file
regression scripts (`test-bash-write-guard.py`, `test-check-domain.py`) and the single-function
`code-grade.py --json` filter.
