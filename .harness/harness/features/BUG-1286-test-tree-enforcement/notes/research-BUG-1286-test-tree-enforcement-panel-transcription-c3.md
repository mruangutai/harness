# Panel record transcribed — BUG-1286-test-tree-enforcement — cycle 3

**BLUF: the cycle-3 panel record is on disk as `plan.yaml`'s TOP-LEVEL `panel:` key, written once
through `plan-merge.py set-panel` (exit 0). All nine digest findings are present with nine distinct
`PF-` ids, `severity_max: med`, and `disposition: open` on every one — nothing was resolved, nothing
was re-severitied, and no task, decision, REQ or SC text moved. `approval:` is untouched
(`status: pending`, no `rulings`) and the station is still `plan`. Three findings a reader flagged as
actionable-before-signature are raised as open questions, never applied.**

Source: `notes/review-plan-panel-c3.md` (byte-identical tracked copy of
`runs/2026-09-04-08-validator/digest.md`; `runs/2026-09-04-07-validator` is the same single run's
unusable first digest and is not cited). Each `summary:` is the digest's own field carried verbatim —
no markdown emphasis or backticks were present in any of the nine, so nothing was stripped and no
wrapping collapsed. Verified programmatically: the `(reader, severity, summary)` triple list in
`panel.findings` equals the digest's `findings:` list in digest order, byte for byte.

## The nine findings — id, severity, reader, source line in review-plan-panel-c3.md

| id | sev | reader | source |
|---|---|---|---|
| `PF-b1381e1d1016bfebf6d3364eddb5ef59` | low | scope | :15 — T-03 `--against` output contract silent on the row/TOTAL block |
| `PF-5504924547ecd6b632f6cb1f10246055` | med | scope | :16 — D-05's accepted archival landmine |
| `PF-806758dcc7e53f9217d3bfa230b272bf` | low | should-not-exist | :17 — accept the D-05 coupling at low |
| `PF-3d6c9ec01bf1eda038fda9b7703e22d6` | info | scope | :18 — SC-06 exact equality acceptable |
| `PF-8f95b3a90e31a1ceeabab4fa860c1c7c` | info | should-not-exist | :19 — SC-06 equality grader should stand |
| `PF-43252b3fa6f8521818b37a4681924e4a` | info | scope | :20 — harness.json detect residual: disclosure sufficient |
| `PF-093f4650a55ddd59ad77f704d7101d5f` | low | should-not-exist | :21 — unit.detect residual should not end at disclosure |
| `PF-d33300cef5eb898cfa0a971c791c8107` | info | should-not-exist | :22 — build the repository-wide clause |
| `PF-ae6d643363371bf038d536934837962a` | info | should-not-exist | :23 — keep T-03's `--against` mode |

Multiset: 1 med, 3 low, 5 info. `severity_max: med`. Every id computed with `panel_findings.py id`
over the exact stored string, and re-verified after the write both through the module and through
nine fresh CLI invocations.

## Readers — three entries, none skipped, none carrying a `reason`

- `should-not-exist` / `fable-advisor` / `ran` (digest :11, :69)
- `scope` / `harness-code-reviewer` / `ran` (digest :12, :70)
- `goalcheck` / `harness-pm` / `ran`, with a `note:` recording that it ran in a separate product
  segment outside this team's two panel steps and its findings were applied in the plan-fix cycles
  rather than transcribed here. Lead decision: `check-state.sh:533` grades all three readers at
  signature, and a goal-check genuinely ran (`notes/research-…-goalcheck-plan-c1.md`, `-c2.md`, the
  c3 sc06-grader-closure note). The note is what keeps the record honest about which segment.

## Corroboration — cross-referenced, never merged

Six of the nine are three independent double-sightings, each side keeping its own severity. Recorded
both ways: a `corroborates:` list on each of the six entries and a `cross_references:` sequence.

- D-05 archival coupling — `PF-5504…` (med, scope) + `PF-8067…` (low, should-not-exist). The
  med/low split stands unreconciled by design.
- SC-06 exact-equality grader — `PF-3d6c…` (scope) + `PF-8f95…` (should-not-exist).
- harness.json / `unit.detect` residual — `PF-4325…` (scope) + `PF-093f…` (should-not-exist).
- Recorded explicitly as **not** a pair: `PF-b138…` and `PF-ae6d…` both concern `--against`, but one
  is an output-contract ambiguity and the other a keep-or-strike judgement.

## Adequacy — what the panel could not establish (digest :26–:27)

1. SC-06's unrebound two-finding baseline was not re-measured by any reader; scope traced the
   rebound one-element result by hand but no reader re-ran the c3 prototype.
2. SC-02's test-first red proof is ungradable at plan phase by construction.

## The five checks, as run from the worktree root

1. `yaml.safe_load` loads. `sorted(doc.keys())` =
   `['approval','decisions','feature','lanes','panel','schema','source_issues','status','tasks']`;
   `doc['approval']` = `{'status': 'pending'}`; `panel` nested in approval = `False`.
2. `approval.status` = `pending`; `'rulings' in approval` = `False`; top-level `status` = `plan`.
3. `len(findings)` = 9, distinct ids = 9, severities = `{'low': 3, 'med': 1, 'info': 5}`,
   dispositions = `{'open'}`, any `resolved_by` = `False`. Stored ids match both the module
   recomputation (0 mismatches) and the CLI (`True`).
4. `CLAUDE_PROJECT_DIR=<tree> check-plan-routes.py <plan.yaml>` → `OK T-01`…`OK T-05`,
   `0 violation(s) across 1 plan(s)`, exit 0.
5. `diff /tmp/plan-bug1286-pretranscription.yaml plan.yaml` → `112a113,234`: **added-only**, 122 `>`
   lines, 0 `<` lines. Nothing but the `panel:` insertion. All five tasks still carry 11 keys each.

## Open questions — reported, not applied

- Q1 (`PF-b138…`, low, scope): T-03's `intent:` needs one clause stating the row block and `TOTAL`
  line print unconditionally and that `MISSING`/`EXTRA` plus the exit code are additive under
  `--against`. Without it a spec-compliant implementation can fail T-04's own `verify:`. This is the
  only actionable-before-signature item, it is a pm edit, and it is deliberately **not** made here.
- Q2 (`PF-5504…`/`PF-8067…`, med/low): D-05's archival blast radius — accept as a standing
  operational landmine, or warn before archiving a `DOCUMENTED_EXCEPTIONS` path? Only the main
  session can accept the risk, via `sign-approval --overrule`.
- Q3 (`PF-4325…`/`PF-093f…`, info/low): the `unit.detect` residual — operator sign-off by name, or a
  follow-up ticket after ship? An in-scope fix would edit harness.json, which SC-14 freezes.
