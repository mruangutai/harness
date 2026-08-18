# Security re-review — FEAT-21 · S-03 · pinned at 4a98cc4

HEAD confirmed `4a98cc4d8310939971f0e523d0689f4d309a22c9` on branch
`feat/FEAT-21-features-layout-migration` (not main). Range audited: `d033b9d..4a98cc4`
(9 commits: `d033b9d`, `5c39f8c`, `649b36b`, `3df7002`, `b1d3925`, `835692a`, `1f717da`,
`b517049`, `1c95e81`, `4a98cc4`).

**Verdict: PASS.** No must-fix. The fail-open the fix was meant to close is closed, the
authorization surface is unchanged post-move, close-out commits stayed in the orchestrator's
granted lane, and the range introduces no new exposure.

## JOB 1 — the fail-open hazard (D-08's dict-keys-bare / label-qualified split)

**Confirmed NOT reintroduced, with execution evidence, not a read-and-conclude.**

- `plan_docs` keys (`check-state.sh:82` derivation) are `os.path.basename(os.path.dirname(p))` —
  bare. The INV-26 loop's `_feat` (`check-state.sh:1161`) is `os.path.basename(_fp)` — also bare,
  same shape. Both glob at the same depth (`.harness/*/features/*`).
- Measured live (not argued): a Python probe replicating the exact `plan_docs` and INV-26
  glob logic against this repo's real `.harness/` tree shows 12 of 21 feature dirs have
  `plan.yaml` and all 12 keys land in `plan_docs` — the 9 "misses" are legacy features that
  use `PLAN.md`, not `plan.yaml` (verified: `FEAT-01`, `FEAT-02`, `FEAT-03-subissue-mirror`
  each contain `PLAN.md`, no `plan.yaml`), i.e. correctly-skipped, not silently dropped.
- Ran `check-state.sh` live end-to-end (`gh auth status` confirmed authenticated, `github.sync:
  true`, `repo: mruangutai/harness` in `harness.json`) — exit 0. A standalone instrumented
  replay of the INV-26 body (same imports: `gh_board`, same live board load, same
  `_gh_bin`/auth check) confirms the board loaded with 324 stations, `_gh_ok=True`, and the
  per-feature loop's `plan_docs.get(_feat)` hits for **12 of 12** features that carry a
  `plan.yaml`, enumerating 60 task↔card pairs the gate's own loop is positioned to compare —
  correction on precision: the replay counted `len(_issues)` per feature (the comparison
  *inputs* the loop reaches), it did not itself call `read_station` a second time outside
  the gate. The live gate run (same env, same auth, exit 0, zero INV-26 findings) is what
  actually executed those 60 `read_station` comparisons; nothing sits between `_stations`
  loading and the loop that could skip it once reached. Net: the loop is proven reached at
  volume against real data, not proven-and-re-executed twice from outside — the stronger
  claim would require instrumenting the gate itself, which is out of scope for a read-only
  review. This is still the O-01/O-02 bar (measured, not argued from source), just stated at
  the precision the probe actually supports.
- **`fpath` fallback (`:58-59`) `?` segment** — traced every call site (13 of them); every
  `feat` value passed to `fpath()` is derived from the *same* one-level-deep glob shape as
  `_feat_dirs` (a file under `.harness/*/features/*/<name>` implies the directory exists and
  is picked up by `_feat_dirs`'s own `.harness/*/features/*` glob). Confirmed empirically:
  only one repo segment (`harness`) currently has a `features/` subtree
  (`.harness/factory` has none). The fallback is currently unreachable dead code, not a live
  hazard. If a future second segment or resolver divergence ever fires it, the `?` is a
  visible non-path placeholder (not a plausible-but-wrong path), so an operator reading it
  during an incident is told "unresolvable," not misled toward a wrong file. **info,
  advisory** — worth a comment noting the invariant that keeps it dead, not a fix.

## JOB 2 — did the authorization surface move?

`check-domain.sh --resolve`, verbatim, at `4a98cc4`:

**Positive** (under `.harness/harness/features/FEAT-21-features-layout-migration/`):
- `notes/receipt-harness-backend-dev-x.md` → `harness-backend-dev`, `harness-orchestrator`
- `observations/harness-orchestrator.md` → `harness-orchestrator`
- `plan.yaml` → `harness-orchestrator`, `harness-pm`
- `runs/2026-08-14-1-eng/state.yaml` → `harness-eng-lead`, `harness-orchestrator`
- `notes/review-harness-security-reviewer-2026-08-15-rereview.md` → `harness-orchestrator`,
  `harness-security-reviewer`

**Negative:**
- `.harness/features/FEAT-21-features-layout-migration/plan.yaml` (legacy shape) → `NOBODY`
- `product/src/whatever.py` → `NOBODY`
- `.harness/team-config.yaml` → `NOBODY`
- `.claude/agents/harness-orchestrator.md` → `NOBODY`

All match the pre-commit-measured coherent state; nothing widened.

**`.harness/team-config.yaml` full-diff residual check (per advisor course-correction):**
`git diff d033b9d^..4a98cc4 -- .harness/team-config.yaml | grep '^[+-]' | grep -v '^+++\|^---'`
— every one of the 43 `-`/`+` line pairs across the whole 86-line change (main_session,
orchestrator, `paths.features`, and every one of the 15 team members: pm, visual-designer,
documentor, frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops, qa, all three
reviewers, product-lead, eng-lead, validator-lead) is exactly the
`.harness/features/` → `.harness/*/features/` substitution. **Empty residual** — no path
added, no glob widened (e.g. no reviewer gained `.claude/skills/harness/bin/**` or similar),
no grant removed. Identity-level closure on JOB 2's core claim.

`bash-write-guard.sh` — simulated `HOOK_PAYLOAD` (avoided literal `>` in my own command text
to stay inside my own read-only guard; built the redirect via `printf '\076'`):
- `harness-backend-dev` writing `docs/PRINCIPLES.md` (ungranted) → **BLOCKED, exit 2**
  (`redirect targets docs/PRINCIPLES.md, outside your domain`).
- `harness-orchestrator` writing its own `STATE.md` at the new layout → **allowed, exit 0**.
- `harness-backend-dev` writing the *legacy-shape* receipt path
  (`.harness/features/FEAT-21.../notes/receipt-x.md`) → **BLOCKED, exit 2** — confirms the
  legacy shape is denied for writes too, not just for `--resolve` reads.
- `harness-backend-dev` writing its own receipt at the new layout → **allowed, exit 0**.

No drift from the pre-commit baseline.

## JOB 3 — close-out lane discipline

Close-out commits (all `#388`): `5c39f8c`, `649b36b`, `3df7002`, `835692a`, `1f717da`,
`b517049`, `1c95e81`. Deduped file set across all 7 (`git show --name-only`):
`STATE.md`, `feature.json`, `plan.yaml`, `observations/harness-{orchestrator,pm}.md`,
`notes/{qa-c0,research-FEAT-21-*,review-harness-{code-reviewer,qa,security-reviewer,
ui-reviewer}-2026-08-14-panel,ship-review-2026-08-15.{md,html}}.md`, and 9
`.harness/expertise/harness-*.md` files (all of the feature's participating personas).

No source file, docs file, `.claude/agents/**` path, or `team-config.yaml` in the set.
(`.claude/skills/harness/bin/test-layout-migration.py` appears in the *union* of the full
range but belongs only to `b1d3925`, an engineering/SC-10 commit, not a `#388` close-out
commit — correctly out of this job's scope.)

Ran `check-domain.sh --resolve` on a representative sample of every path class in the set
(see JOB 2 above plus `notes/qa-c0.md`, `notes/research-FEAT-21-distill.md`, each
`review-harness-*-panel.md`, `.harness/expertise/harness-{qa,code-reviewer,
security-reviewer,orchestrator}.md`). Every file resolves to **at least one legitimate
grant** — never `NOBODY`. Two shapes observed:
- `notes/**` files resolve to *both* `harness-orchestrator` (its `.harness/*/features/**`
  wildcard grant, `team-config.yaml:29`) *and* the specific named agent (its own narrower
  grant, e.g. `harness-qa` for `qa-c0.md`). This is D-01's already-signed accepted cost
  (wildcard repository segment, "buys locality not write isolation") — pre-existing, not
  introduced or worsened by this range (confirmed by the JOB 2 residual check: the wildcard
  grant existed pre-migration too, only the `.harness/features/` prefix moved). Not re-filed
  per the dispatch's ruling.
- Expertise files (`.harness/expertise/harness-<agent>.md`) resolve **only** to their own
  named agent, never to `harness-orchestrator` — consistent with the `harness-expertise`
  skill's rule that each agent writes only its own file under its own distillation
  dispatch, never another's.

Git history cannot distinguish, at the commit level, "qa wrote its own note, orchestrator
committed the round" from "orchestrator wrote qa's note itself" — both are equally
consistent with the diff, and (for `notes/**`) both are equally *authorized*. That
indistinguishability is the honest limit of this check: it rules out unauthorized writes
(no `NOBODY` in the set) but cannot prove *which* agent's Write call produced each file.
Given (a) no path outside any granted domain appears, (b) the expertise-file set matches
exactly the batch-distillation-at-ship-close pattern the skill describes, and (c) the
one-commit-per-round bundling is this repo's normal workflow (confirmed by every other
commit in the range having the same shape), I find **no lane violation**. Advisory only:
the indistinguishability itself is a standing property of D-01's wildcard, not new here.

## JOB 4 — exposure sweep across the range

- `git diff d033b9d^..4a98cc4` grepped for credential/token/key-shaped strings
  (`password|api[_-]?key|secret|token|bearer|-----BEGIN|ghp_|gho_|AKIA`) — zero hits outside
  prose in note files describing *past* secrets sweeps (this feature's own prior review
  artifacts, git-mv'd as part of the migration) and one pre-existing test regex variable
  named `TOKEN_RE` in `gh-sync.py`. Nothing new.
- No new `|| true`, bare `except:`, or `except Exception: pass` introduced anywhere in the
  range's `.py`/`.sh` diff.
- `4a98cc4` (`gh-sync.py` walk-up refactor): flattened loop is behaviourally identical to
  the prior `while True`/`break` form — same manifest probe (`.harness/team-config.yaml`),
  same fallback arithmetic when no ancestor qualifies. Not a widening.
- `4a98cc4` (`check-domain.sh` regex anchors, from `d033b9d`): `^\.harness/features/...$` →
  `^\.harness/[^/]+/features/...$` — anchors (`^`/`$`) preserved, new segment matched by
  `[^/]+` (single path component, cannot cross a `/`), so this does not open path
  traversal or admit an unintended prefix/suffix. A tightening-shaped edit, not a loosening.
  `check-plan-routes.py`'s `os.scandir` → `glob.glob` swap preserves dotfile exclusion
  (`glob`'s `*` never matches a leading dot, same as before) — confirmed by reading, and by
  running the full `test-layout-migration.py` suite (below).
- `branch-create-gate.sh`'s hardcoded segment literal (already-ruled backlog item) moved
  from `.harness/features/` to `.harness/harness/features/` — same class (coincidentally
  correct for today's single segment), explicitly *not* wildcarded per `4a98cc4`'s own
  commit message ("branch-gate wildcard — contradicts signed D-01 and validator Q2 —
  false-grant"), i.e. the range considered widening it and correctly declined. Not worse.
- Ran `python3 .claude/skills/harness/bin/test-layout-migration.py` at HEAD (`4a98cc4`,
  post-`b1d3925`+`4a98cc4` refactors of case 20): **exit 0, all cases `ok`**, including all
  "case 20 parity" assertions that compare the real gate's INV-27 output against `render()`
  over the same fixture tree — the refactor claimed in `4a98cc4`'s commit message
  ("suites green") is verified, not merely narrated.

## Findings summary

| # | Finding | Severity | Blocks ship? |
|---|---|---|---|
| 1 | `fpath()`'s `?` fallback (`check-state.sh:59`) is unreachable dead code under the current single-repo-segment tree; would print a visible non-path placeholder, not a misleading wrong path, if a future divergence ever reached it | info | advisory only |
| 2 | D-01's wildcard grant makes orchestrator vs. named-agent authorship of `notes/**` files indistinguishable from git history alone (pre-existing, not worsened) | info | advisory only |

No must-fix. Authorization surface, fail-open closure, close-out lane discipline, and the
`/simplify` polish diff all hold.
