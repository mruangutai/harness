# UI Reviewer — Mode B built-surface audit — FEAT-45-adversarial-plan-panel — cycle 0

review_sha: d0ebbe6f361d8084176bee27202b1a3b9e005947 (diff 1d3e5db..d0ebbe6)

## Census (looked, not predicted)

**DESIGN.md:** absent for this feature. Checked directly:
`git ls-tree -r d0ebbe6 | grep -i DESIGN.md` returns only `.claude/skills/harness/templates/DESIGN.md`
(the template, untouched by this diff) and four other features' own `DESIGN.md`s — none for
`FEAT-45-adversarial-plan-panel`. `git show d0ebbe6:.harness/harness/features/FEAT-45-adversarial-plan-panel/`
lists BRIEF.md, STATE.md, feature.json, notes/, observations/, plan.yaml — no DESIGN.md. Fact, not a
finding: a doctrine-only feature has no rendered surface a DESIGN.md would specify.

**Rendered-UI extension census:** `git diff --name-only 1d3e5db..d0ebbe6 | grep -Ei
'\.(html|css|scss|tsx|jsx|vue|svelte|less)$'` — zero hits over all 41 changed files (`git diff --stat`
counts 41, one more than the dispatch's stated 40; not investigated further, immaterial to scope).
Confirms this repo's convention (project Expertise P-01): no rendered UI, ever.

**Operator-facing textual surface examined** (per dispatch framing — commands and skill doctrine ARE
the operator interface here):
- `.claude/commands/harness-plan.md` — the panel's one mention, folded into the existing "Target
  state" bullet.
- `.claude/skills/harness/SKILL.md` — new "## The plan phase" section (29 lines), sequencing
  prose and reader/skip semantics.
- `.claude/skills/harness-spec-driven/SKILL.md` — new "## The panel result" section (pm's
  transcription contract, disposition/severity rules).
- `.claude/skills/harness/templates/plan.yaml` — new `panel:` block with inline comments, the
  literal shape the operator reads at signature.
- `.claude/skills/harness/teams/plan-panel.yaml` — the two validator-squad reader prompts (operator
  never reads this directly, but its prompt text is what a reader's `summary`/`why` will echo into
  the digest the operator DOES read).
- `.claude/skills/harness/bin/check-state.sh` INV-32 (new, 66 lines) — the actual printed CLI text
  (`VIOLATION`/`note` lines) an operator sees at every `/harness` step-0 gate run.
- Both `harness-validator-lead.md` copies (`.omp/` canonical, `.claude/` generated) — agent
  instruction prose, not primary operator surface, checked for wording that would leak into what
  the lead ultimately reports (found none of concern; verified the two copies are in sync on the
  new "Hosting plan-panel" section).
- DECISIONS.md / DECISIONS-INDEX.md DEC-206/207 — read for terminology cross-check only.

Not reviewed as UI (data/bookkeeping, no design contract applies): `plan.yaml`/`BRIEF.md`/
`STATE.md`/`feature.json` for FEAT-45 itself, all `notes/`, `receipts/`, `observations/` files,
`panel_findings.py` (prints one id string, no formatting concerns), the `test-*.py` files
(developer-only), `sync-agent-adapters.py`, `run-unit-tests.sh`.

## Findings

### F1 (carried forward from Mode A cycle 0, `low`, non-gating) — the live withhold message still
doesn't spell out the remedy mechanics in the two files an operator's own reading lands on

My own prior Mode A note (`notes/review-harness-ui-reviewer-plan-c0.md`, review_sha `1d3e5db`) flagged
this as `med`/non-gating and explicitly did not require a build task to close it. Checked whether it
closed anyway: it did not, fully. `.claude/commands/harness-plan.md:20` and
`.claude/skills/harness/SKILL.md:86-113` (`git grep -n "stale\|content-hash\|reworded"` over both
files returns zero hits) state that a high/critical/unrated finding "withholds presentation until
resolved or the operator records an overrule" and that only `approval.rulings` records an overrule,
but never state that *resolving* means a build task sets the finding's `disposition` to `resolved`,
nor explain the stale-override renaming mechanic in the doctrine prose itself.

Partial improvement over the Mode A baseline, worth recording: the runtime message now self-explains
where it fires. `check-state.sh:203-206` (`INV-32 ... STALE OVERRIDE {fid}: a reworded finding gets a
NEW content-hash id, so the old ruling stopped applying and the operator is asked again`) closes the
specific "operator doesn't know WHY the id changed" gap Mode A flagged — this text exceeds what T-07's
spec required. The plain non-stale withhold message
(`check-state.sh:229-231`, `finding {fid} is {severity} and remains open without an operator
overrule`) still states only the fact, not the remedy.

Concrete scenario: an operator who reads only `harness-plan.md` and `SKILL.md` (the doctrine, not the
templates or check-state.sh source) before their first signature knows a `high` finding blocks them
and that overruling writes `approval.rulings`, but not that "resolved" requires a task, or where
`disposition` lives. Non-blocking: no REQ/SC promises this text, Mode A already accepted the gap as
mitigated by the orchestrating LLM's in-conversation explanation, and `approval.rulings` — the
higher-stakes half of the two remedies — IS now named in `SKILL.md`.

### Confirmed closed — Mode A cycle 0's F2 (SC-11 zero-findings ambiguity)

`BRIEF.md` diff (`git diff 1d3e5db..d0ebbe6 -- .../BRIEF.md`, SC-11) adds exactly the missing rule:
"**The zero-findings case is graded, not skipped:**... an empty list, explicitly reported as empty
with the reader named, IS 'earned its spawn' and passes... It fails only if the reader's return is
missing from the digest altogether, or the reader returned findings the operator judges to be
padding." This directly closes the pass/fail-undefined gap. No residual finding.

## Terminology / vocabulary cross-check (no findings)

Severity vocabulary (`info|low|med|high|critical` plus sentinel `unrated`) is byte-identical across
`templates/plan.yaml`, `teams/plan-panel.yaml`, `SKILL.md`, `harness-spec-driven/SKILL.md`,
`check-state.sh`, both `harness-validator-lead.md` copies, and `DECISIONS.md` DEC-206/207 — grepped
for synonym drift (`medium`, `severe`, `urgent`, `blocker`, `priority`) across every touched doctrine
file; the two `medium` hits are both `thinking-level: medium` frontmatter, unrelated to severity.
`awaiting_user` reuses the harness's pre-existing orchestrator status enum
(`harness-orchestrator.md:121`), not a new synonym. `DEC-206`'s `refs:  ::` (empty refs, double
space) matches the established index convention for every other zero-ref entry (DEC-01, DEC-02, …
grepped and confirmed) — not a formatting defect.

## Accessibility / theme parity

Not applicable in the WCAG-contrast/colour-only-meaning sense: every touched surface is plain
text/YAML/markdown/shell stdout. Grepped all six operator-facing files for ANSI escape sequences and
emoji — zero hits; `check-state.sh` distinguishes severity by the words `VIOLATION` and `note`, never
by colour. No markdown tables appear inside any new diff hunk (existing tables in `SKILL.md`/
`harness-spec-driven/SKILL.md` are untouched by this diff), so no table/plain-text-reader survival
risk was introduced. This is a source-level judgment; there is no rendered surface for a human to
misread, so "does it render" doesn't apply here the way it would for a graphical UI.

## Verdict basis

`must_fix: []`, `severity_max: low` — below the `>= high` gate. `VERDICT: PASS`.
