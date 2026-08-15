# Security review — FEAT-21 precommit — authorization coherence at the new layout

Target: `git diff HEAD` at `ea937b1` on `feat/FEAT-21-features-layout-migration`, uncommitted.
Ground-pin confirmed: HEAD `ea937b17e132fdcc7780cbb5a65ab579eb57bb7d`, `.harness/features` absent.

## BLUF

The move from `.harness/features/` to `.harness/harness/features/` is mechanically coherent across
every grant and gate I could exercise, with **one real gap**: `branch-create-gate.sh` hardcodes the
literal segment `harness` instead of the wildcard/derived pattern every sibling gate adopted. It
fails *closed* (denies), so it is not a security regression today, but it silently defeats this
migration's own stated purpose (multi-repo hosting) the first time a second repo is onboarded, and
the script already holds the data (`$REPO` = `mruangutai/harness`) to derive the segment correctly
instead of hardcoding it. **Advisory, does not block T-09.**

## A. Positive resolves — measured, `check-domain.sh --resolve`

| Path (new layout) | Verbatim answer | Expected |
|---|---|---|
| `.../FEAT-21.../notes/receipt-harness-backend-dev-r1.md` | `harness-backend-dev` / `harness-orchestrator` | match |
| `.../FEAT-21.../observations/harness-qa.md` | `harness-orchestrator` / `harness-qa` | match |
| `.../FEAT-21.../plan.yaml` | `harness-orchestrator` / `harness-pm` | match |
| `.../FEAT-21.../runs/2026-08-14-1-validator/state.yaml` | `harness-orchestrator` / `harness-validator-lead` | match |
| `.../FEAT-21.../notes/review-harness-security-reviewer-2026-08-14-precommit.md` | `harness-orchestrator` / `harness-security-reviewer` | match |

No positive resolve came back NOBODY or over-broad; each names exactly the intended agent plus
the orchestrator (which holds `.harness/*/features/**` for its own bookkeeping).

## B. Negative resolves — measured

| Path | Verbatim answer | Expected |
|---|---|---|
| legacy-shape `.harness/features/FEAT-21.../plan.yaml` | `NOBODY` | NOBODY (T-02 intent held) |
| product-shaped `src/app/whatever.ts` | `NOBODY` | NOBODY |
| `.harness/team-config.yaml` | `NOBODY` | NOBODY |
| `.claude/agents/harness-orchestrator.md` | `NOBODY` | NOBODY |
| cross-segment `.harness/otherrepo/features/FEAT-99-x/plan.yaml` | `harness-orchestrator` / `harness-pm` | grantable — **this is D-01's accepted cost, not a finding** |

## C. Shape-sweep regexes (`RE_FEATURE_JSON`, `RE_STATE_YAML`, `RE_HANDOFF`, `RE_STATE_MD`)

`git diff` for `check-domain.sh` is exactly the mechanical anchor-preserving rewrite:
`^\.harness/features/[^/]+/...` → `^\.harness/[^/]+/features/[^/]+/...` — `^`/`$` anchors intact,
`[^/]+` used (never `.*`), one inserted segment, nothing else touched (34-line diff, verified in
full). Isolated regex probes (positive/negative/traversal/extra-segment attempts) all matched
design intent — no anchor lost, no over-match beyond the accepted D-01 segment wildcard. Confirmed
at execution level, not just by reading: `python3 .claude/skills/harness/bin/test-check-domain.py`
→ **14/14 pass**, and its fixtures exercise these four routes at the literal new-layout shape
(`.harness/harness/features/FEAT-X/...`, lines 224/383/1001/1404 of the test file).

## D. `bash-write-guard.sh` and `branch-create-gate.sh`

**`bash-write-guard.sh`** (unmodified in this diff — it delegates to `team-config.yaml` via
`harness_boundary`/`harness_yaml`, which is why it needed no edit). Exercised live at the new
layout:
- ungranted write (reviewer role, any path) → `BLOCKED`, exit 2
- in-domain write (`harness-pm` → new-layout `plan.yaml`) → allowed, exit 0
- legacy-shape write (`harness-pm` → old-layout `plan.yaml`) → `BLOCKED`, exit 2 (grants don't widen to accept both shapes, confirmed live)
- out-of-domain product write → `BLOCKED`, exit 2

**`branch-create-gate.sh`** — both the deny path (nonexistent flow) and the allow path (existing
flow at new layout, `FEAT-18-board-truth`) proved via
`python3 .claude/skills/harness/bin/test-branch-create-gate.py` → **8/8 pass**, including
`ALLOW: a branch naming a flow that DOES exist on disk` and `DENY: a branch naming a flow that does
not exist on disk`. Functionally correct **for this repo**.

**Finding SEC-01 (low, advisory, does not block T-09):** `branch-create-gate.sh:77-78` hardcodes
the literal segment `harness` (`ls -d "$root/.harness/harness/features/${flow}"*`) rather than the
wildcard/derived pattern every other touched enforcement path uses
(`check-domain.sh`'s `[^/]+`, `check-state.sh`/`check-plan-routes.py`/`validate-feature-json.py`'s
glob `*`, `.gitignore`'s `*`, every `team-config.yaml` grant's `*`). It happens to be correct today
only because this repo's own segment name (derived elsewhere in the codebase from
`harness.json`'s `github.repo`, per `layout_migration.py:144-161 _declared_segments`) is coincidentally
also the literal string `harness`. The script already extracts `$REPO` = `mruangutai/harness` two
lines above (for the `gh issue view -R "$REPO"` call) — the segment is `${REPO##*/}`, derivable from
data it already holds, rather than hardcoded. Two ways this bites, both DoS-shaped (fails closed,
not open):
1. **The stated purpose of this migration** — "so one machine can host several onboarded repos" —
   is exactly the scenario this hardcoding breaks: a second onboarded repo's flow branches would
   always be denied (`ls` finds nothing under the wrong segment), even with a valid `plan.yaml`.
2. The script's own header cites DEC-138 ("a fork or renamed remote must not verify against the
   wrong repo") for the *issue-number* path (form 2) but the *flow-id* path (form 1) doesn't apply
   the same discipline — a repo rename or fork changes `$REPO` but not this literal, so the two
   forms could silently diverge.

Not exploitable by an attacker (no escalation, no data exposure — it only ever makes the gate
stricter than intended), and `test-branch-create-gate.py`'s existing fixtures only run against this
repo's own `harness` segment so they can't catch the divergence. Recommend: replace the literal with
`${REPO##*/}` (or a wildcard `*`, matching the rest of the diff's accepted D-01 cost) before or
alongside the unit-7 multi-repo work; not worth blocking this commit over.

## E. Widened exposure / secrets sweep

- No `|| true`, `--ignored`, or silently-swallowed failure introduced anywhere in the diff (grep
  swept the full diff).
- No credential-, token-, or secret-shaped string introduced (grep swept the full diff, docs and
  workflow included per Expertise P-14).
- `.github/workflows/tests.yml`'s three `.harness/features/` literals remaining are all inside
  comments describing a **historical, pre-move measurement at 62fef85** ("Not a live hole today"
  correctly re-annotated "as of 62fef85, pre-move") — no live CI step executes against the legacy
  path; the one live diagnostic string (line 171) was updated to `.harness/*/features/`. Sanctioned.
- Sanctioned legacy-literal survivors named in the dispatch (harness-init/SKILL.md, templates,
  check-plan-routes.py's four historical comments, FEAT-99-x display literal, the three
  M-is-asserted literals, unit-9 files, gen-decisions-index.py/harness_boundary.py, docs/**) —
  spot-checked a sample (`test-validate-feature-json.py:281`'s `FEAT-99-x`, the three
  `tests.yml` comment literals) and all are prose/comments, not live logic. Not re-filed.

## Threat model

| Boundary | STRIDE | Mitigated |
|---|---|---|
| Agent write path → `team-config.yaml` grant resolution | Elevation of privilege (writing outside declared domain) | Yes — measured live, both shapes |
| Agent write path → shape-sweep budget enforcement (feature.json/state.yaml/STATE.md/handoff) | Tampering (silent budget-enforcement bypass) | Yes — regexes anchor-correct, execution-tested |
| Branch creation → work-tracking gate | Denial of service (legitimate work blocked) | Partially — correct today, latent gap for future multi-repo onboarding (SEC-01) |
| CI backstop (`validate-feature-json.py`, `check-plan-routes.py`) → schema/route enforcement | Tampering (green-over-nothing) | Yes — both pass 0-file-swept trap avoided, tested |

```yaml
VERDICT: PASS
DIGEST:
  headline: "Grants and gates moved coherently to the new layout; one hardcoded (not wildcarded) segment in branch-create-gate.sh is a latent multi-repo gap, fails closed, advisory only."
  in_scope: true
  scope_reason: "Diff rewrites every write-grant and enforcement-path regex/glob in the authorization surface (team-config.yaml, check-domain.sh, check-state.sh, check-plan-routes.py, validate-feature-json.py, branch-create-gate.sh, .gitignore) — a PreToolUse gate's matching surface is exactly this role's domain."
  severity_max: low
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "agent write -> team-config.yaml grant resolution", stride: E, mitigated: true }
    - { boundary: "agent write -> shape-sweep budget enforcement", stride: T, mitigated: true }
    - { boundary: "branch creation -> work-tracking gate", stride: D, mitigated: false }
    - { boundary: "CI backstop -> schema/route enforcement", stride: T, mitigated: true }
  open_questions:
    - { id: Q1, question: "Should branch-create-gate.sh's flow-existence check derive its segment from $REPO (${REPO##*/}) or a wildcard, ahead of unit-7's multi-repo work, rather than the literal 'harness' it carries today?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-security-reviewer-2026-08-14-precommit.md
```
