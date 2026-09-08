# ALTITUDE read — FEAT-56 simplify pass

**Verdict up front:** one real fold-in (a drifted, duplicated predicate across two commands),
everything else checked and left. `_check_product_configs`'s home matches the codebase's own
established convention. No undocumented residual found. No rule found living only in one
command/prompt with no authority backing it.

## Per-file altitude bucketing (every file in `git diff 4b5dbb23..HEAD` that states the model)

| Bucket | Files | Role |
|---|---|---|
| **skill** (authoritative procedure) | `.claude/skills/harness-init/SKILL.md` | The one place the full ordered procedure lives |
| **templates** (schema/scaffold) | `.claude/skills/harness/templates/{harness.json, team-config.yaml, README.md, BRIEF.md}` | Self-documenting artifact comments + the templates-dir index |
| **commands** (session-entry routing prose) | `.claude/commands/{harness.md, harness-plan.md, harness-grilling.md}` | What the main session reads at `/harness*` entry |
| **agent instructions** (persona prompt, mirrored across two runtimes = one logical bucket item) | `.claude/agents/harness-dev-ops.md` + `.omp/agents/harness-dev-ops.md` | `.omp` is canonical, `.claude` is a generated adapter (`sync-agent-adapters.py`) |
| **operator/reference docs** | `.harness/README.md`, `.harness/harness/docs/{SPEC.md, BUILD.md, DECISIONS.md, DECISIONS-INDEX.md, org.html}`, root `README.md`, `.claude/skills/harness/references/github-mirror.md` | Living spec, historical build ledger, decision log + its index, rendered org chart, repo intro, GH-mirror reference |
| **code** (not prose, judged for home only) | `.claude/skills/harness/bin/factory_config.py` (`product_config_report`, `_check_product_configs`) | Sole behaviour change in the diff |

## Findings

### F1 — `.claude/commands/harness.md:11-15` vs `.claude/commands/harness-plan.md:18-20`
**Summary:** both commands independently restate the "route to `/harness-init`" predicate, and
they have already drifted to different completeness.
**Cost:** `harness.md`'s Gate (step 0) tests **two** conditions — "this clone has no `.harness/`
at all" or "the repository being worked is not in `.harness/factory/fleet.yaml`". `harness-plan.md`'s
Target-state bullet tests **three** — not registered in `fleet.yaml`, **or** its `harness.json` not
readable at its `default_branch`, **or** its central tree absent. A repository that is
fleet-registered, has its central tree, but whose `harness.json` never landed reads as "proceed"
under `harness.md`'s Gate (both its conditions are false) while `harness-plan.md`'s own bullet
would route the same repository to `/harness-init`. `harness-plan.md` explicitly says "Read
`harness.md` and follow it with mission: plan. The differences:" — so its bullet is supposed to be
a delta on top of the Gate, not a second, independently-derived spelling of the same underlying
test. Any future change to "what counts as onboarded" (a fourth condition, a relaxed one) is now
two hand-edits, and the two are already out of sync.
**Alternative:** make `harness.md`'s Gate the single authoritative statement of the full
three-condition test (the superset `harness-plan.md` already has), and change
`harness-plan.md:18-20` to read "...or route to `/harness-init` per the Gate check in step 0
above" — deleting its own re-derivation of the condition list.
**applicable: false** — both files are under `.claude/commands/**`, which `check-domain.sh
--resolve` resolves to NOBODY; this squad may not write either. Remedy given above is precise
enough to apply without re-deriving this analysis.
**fold-in**

### F2 — Is `_check_product_configs`'s home right? (assignment item 1)
**Summary:** `_check_product_configs` and `product_config_report` live in `factory_config.py`
beside the `product_config`/`board_for`/`_main()` they extend.
**Checked:** every sibling CLI module in `.claude/skills/harness/bin/` — `factory_claim.py`,
`factory_decompose.py`, `factory_land.py`, `factory_workspace.py` — colocates its own
`_main()`/`argparse` dispatch with its own logic functions in the same file; there is no separate
"CLI layer" module anywhere in this bin/ directory. `factory_config.py`'s new flag follows the
one-file-per-tool convention every other `factory_*.py` module already uses. It is not bolted onto
a caller; it is the established home.
**applicable: true** (in-domain, `bin/**`), but no change needed.
**leave**

### F3 — Accepted residual named without its compensating control? (assignment item 2)
**Checked:** `BRIEF.md`'s "Verification gaps" section names the residual explicitly —
"`check-state.sh` deliberately makes no network call, so no every-run invariant can grade a fleet
member's remote `harness.json`. REQ-05 is discharged by an operator-run check (SC-05), which means
a member whose config is deleted after onboarding stays invisible until the next build." The
control (`--check-product-configs`, operator-run) is named alongside the gap, not left implicit.
Cross-checked all seven docs (`SPEC.md`, `BUILD.md`, `DECISIONS.md`'s DEC-220, `DECISIONS-INDEX.md`,
`org.html`, root `README.md`, `.harness/README.md`) for any place that describes
`--check-product-configs` as running automatically or continuously rather than as an
operator-invoked command — none found; every mention (`SPEC.md:446-447`, `DECISIONS.md:6991-6992`)
frames it consistently with the BRIEF. `plan.yaml`'s D-04 decision states the same ordering
rationale. No violation.
**leave**

### F4 — Any rule stated only in one command/prompt, needing an authority file? (assignment item 3)
**Checked:** `.claude/commands/harness-grilling.md`'s new clause ("the answers seed the
repository's own `harness.json` — which must land on its default branch") restates a rule that is
independently authored in `DECISIONS.md`'s DEC-220 and in `SPEC.md §2.4`'s "Onboarding a repository
is three things" section — it is not an orphan rule invented only in this command's prose.
**leave**

### F5 (checked, not raised as a finding) — `.harness/README.md:251` vs `.harness/harness/docs/org.html:463`
Both tables gained the same one-clause fact this diff introduces ("`team-config.yaml` is
control-plane-only"). `org.html` is a **hand-maintained, ungenerated** static rendering with no
script or template producing it (confirmed: no `git grep -l "org\.html"` hit under
`.claude/skills/harness/bin/`, no build step references it) — this is a pre-existing,
previously-reviewed structural characteristic of the repo (see prior-feature receipts under
`FEAT-08`/`FEAT-22` observations), not something introduced by this diff, and a static HTML chart
cannot practically "point at" a markdown table instead of rendering the fact itself. Different
medium serving a different audience (visual quick-reference vs textual reference) — by-design
altitude difference, not same-altitude redundancy.
**leave**

## Non-findings, checked and clean
- `DECISIONS.md`'s DEC-220 entry vs `DECISIONS-INDEX.md`'s one-line index row for it: the
  established full-entry-plus-index-synopsis convention (identical to every other `DEC-NN`), not a
  new duplication.
- `templates/harness.json`'s `_template` comment vs `templates/README.md`'s table row for
  `harness.json`: self-documenting-artifact-comment (ships with the instantiated file, read by the
  operator instantiating it) vs directory index (read by an engineer browsing `templates/`) —
  different audiences, established pattern.
- `.claude/agents/harness-dev-ops.md` vs `.omp/agents/harness-dev-ops.md`: confirmed
  mechanically generated, not hand-duplicated — `sync-agent-adapters.py --check` exits 0 clean on
  this diff, `.omp` is canonical and `.claude` is its generated adapter (docstring, lines 3-5).
- `SPEC.md` vs `BUILD.md`: living behaviour spec vs append-only historical build ledger —
  different purpose, by-design altitude difference, not the same rule restated at the same level.

```yaml
VERDICT: PASS
DIGEST:
  headline: one drifted-predicate fold-in between two commands; everything else at the right depth
  angle: altitude
  findings:
    - file: ".claude/commands/harness.md:11-15 and .claude/commands/harness-plan.md:18-20"
      line: "harness.md:11-15 / harness-plan.md:18-20"
      summary: two commands independently restate the "route to /harness-init" predicate and have already drifted (2 vs 3 conditions)
      cost: "a repo that is fleet-registered and has its central tree but whose harness.json never landed reads as onboard-proceed under harness.md's Gate while harness-plan.md's own bullet would route it to /harness-init; any future condition change is two hand-edits, already out of sync"
      alternative: "make harness.md's Gate (step 0) the single authoritative 3-condition statement; change harness-plan.md:18-20 to read '...or route to /harness-init per the Gate check in step 0 above' and delete its own re-derivation of the condition list"
      applicable: false
      recommendation: fold-in
    - file: ".claude/skills/harness/bin/factory_config.py"
      line: "448-491"
      summary: "_check_product_configs colocated with product_config_report and _main() in factory_config.py"
      cost: "none — matches the one-file-per-tool convention every sibling factory_*.py module (factory_claim.py, factory_decompose.py, factory_land.py, factory_workspace.py) already uses"
      alternative: "none needed"
      applicable: true
      recommendation: leave
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-ai-dev-simplify-altitude.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model/.harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-ai-dev-simplify-altitude.md
```
