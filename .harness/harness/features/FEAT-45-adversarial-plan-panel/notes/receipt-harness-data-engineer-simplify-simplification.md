# SIMPLIFICATION angle — FEAT-45-adversarial-plan-panel

Read-only pass over `git diff 1d3e5db..HEAD` (41 files, +3256/-135) per
`harness-simplify`'s SIMPLIFICATION section. No worktree writes made.

## Conclusion

Three doctrine-surface findings: the panel's "how a reader's return gets shaped into
`panel.findings`" behavior is spelled out in full independently in two places, one of
them a comment nobody executes; the "why content hash not sequential id" narrative is
independently re-derived in two files instead of pointed at; and "who may write
`approval.rulings`" is asserted near-identically in four files with no shared anchor.
No code-surface (redundant conjunct / narrating comment / over-complex pipeline)
findings — the new Python (`panel_findings.py`, `check-state.sh`'s INV-32 block,
`test-plan-panel.py`) is lean and each conjunct/branch tests something distinct. All
three findings are flag-only: every touched file they name resolves to NOBODY on the
grant map for this run.

## What I examined

- `panel_findings.py` in full (61 lines) — hashing, CLI, docstring.
- `check-state.sh`'s INV-32 block in full (lines 122–186 of the diff) — every
  conjunct in every `if`, the readers/rulings/findings loops.
- `plan-panel.yaml` in full (62 lines) — both reader prompts, `on_fail` blocks, the
  trailing comment block.
- `test-plan-panel.py` in full (295 lines) — all 8 numbered check groups.
- The doctrine hunks in `harness/SKILL.md` ("The plan phase" section),
  `.claude/commands/harness-plan.md` (Target-state bullet), `harness-spec-driven/SKILL.md`
  ("The panel result" section), `templates/plan.yaml` (`approval`/`panel` block), and
  both `harness-validator-lead.md` files ("Hosting plan-panel" section).
- Grepped the whole diff for change-narrating comment patterns (`now `, `changed to`,
  `T-NN added`) — the one repo-adjacent hit (`test-harness-yaml-corpus.py`'s
  `TEAMS_EXPECTED` comment) follows the pre-existing, repo-wide FEAT-NN/T-NN
  provenance-comment convention (seen in dozens of files: `harness_boundary.py`,
  `check-domain.sh`, `gh-sync.py`, etc.) and states a present rule plus its
  decision citation (D-15), not a bare change narration — not new complexity, so not
  flagged.
- Confirmed the two `harness-validator-lead.md` files (`.claude/agents/`,
  `.omp/agents/`) carry identical body prose by pre-existing repo convention (every
  one of the 16 dual-host agent adapters does this) — that duplication is not
  something this diff introduces, so I did not flag it as new complexity, and I treat
  the pair as one authoring source below.

## Findings

### 1. `plan-panel.yaml`'s trailing comment restates the lead's hosting behavior that `harness-validator-lead.md` already specifies

- **file**: `.claude/skills/harness/teams/plan-panel.yaml`
- **line**: 55–61 (`# The lead's consolidated digest transcribes...` through
  `...that loop applies only to an invalid reader return.`)
- **summary**: The full transcription/skip-recording behavior contract for the
  hosting lead is written out a second time, near-verbatim, in a YAML comment; the
  first copy is `harness-validator-lead.md`'s "Hosting plan-panel" section (`.claude/agents/harness-validator-lead.md:97-116`, mirrored in `.omp/agents/`), which is
  the file actually loaded into the lead's context at dispatch. The YAML comment is
  not loaded by anything — it exists only for a human reading the team file.
- **cost**: Two files specify the same behavior (de-dup key, `severity_max`
  roll-up, "never assign a PF- id", the exact skip-recording literal `status
  skipped`). A future change to any of these — e.g. the de-dup key, or the skip
  wording `check-state.sh` reads back — edited in `harness-validator-lead.md` and not
  mirrored into the comment leaves the comment describing behavior the lead no
  longer has, misleading the next person who reads the team file to understand what
  the lead does.
- **alternative**: Replace the comment block with a one-line pointer — "The lead's
  transcription and skip-recording behavior is specified once, in
  `harness-validator-lead.md`'s 'Hosting plan-panel' section — not restated here" —
  and keep only the sentence that documents the YAML's own semantics (`on_fail`
  never halts).
- **appliable**: false — `.claude/skills/harness/teams/plan-panel.yaml` resolves to
  NOBODY on the grant map for this run; backlog row only.

### 2. The "content hash, not sequential id" rationale is independently re-derived in `templates/plan.yaml`'s comment instead of citing `panel_findings.py`

- **file**: `.claude/skills/harness/templates/plan.yaml`
- **line**: 34–37 (`# Only the main session may add approval.rulings...` through
  `...so an old ruling stops applying and the operator is asked again.`)
- **summary**: The causal chain — reworded finding → new content-hash id → stale
  override → operator asked again — is written out in full here, and again, in
  different words, in `panel_findings.py`'s module docstring (lines 8–13), which
  explicitly declares itself "THE ONE PLACE" a finding's identity and its rationale
  live.
- **cost**: If the rationale is ever refined (e.g. the failure direction the
  docstring calls "deliberate and closed" is reopened, or the truncation length
  changes), the template's comment has no link back to the source of truth and can
  quietly drift into a claim the code no longer makes — a template comment is read
  by whoever authors a plan by hand and is trusted at face value, unlike a docstring
  a plan author is unlikely to open.
- **alternative**: Shorten the template comment to the operational fact a plan
  author needs ("`approval.rulings` entries are main-session-only and must name a
  current `PF-` id or `check-state.sh` refuses it as a stale override") and drop the
  re-derivation of *why* it is a content hash, pointing instead to
  `panel_findings.py`'s docstring for that.
- **appliable**: false — `.claude/skills/harness/templates/plan.yaml` resolves to
  NOBODY on the grant map for this run; backlog row only.

### 3. "Only the main session may write `approval.rulings`" is asserted in four places with no shared anchor

- **file**: `.claude/skills/harness/templates/plan.yaml` (line 34, adjacent to the
  pre-existing DEC-120 citation two lines above it at line 33's block); also
  `.claude/skills/harness/SKILL.md:113`, `.claude/skills-spec-driven` — i.e.
  `.claude/skills/harness-spec-driven/SKILL.md:114-115`, and
  `.claude/agents/harness-validator-lead.md:115-116` (mirrored in `.omp/agents/`).
- **line**: see above (4 distinct sites, one per file).
- **summary**: The same ownership rule — `approval.rulings` is written by the main
  session alone, never pm, never the validator lead — is spelled out independently
  in four files. Only the `templates/plan.yaml` copy sits next to the DEC-120
  citation that is the actual authority for "main-session-only"; the other three
  restate the rule with no citation at all, so a reader of any of those three has no
  way to find why it is true or to know if it has since changed.
- **cost**: A rule with no named authority repeated in three uncited copies is the
  drift risk this angle exists to catch: if DEC-120 is ever amended or superseded,
  three files carry the old rule with nothing that would surface the need to revisit
  them, and each restatement is a place the next edit can silently diverge from the
  other three.
- **alternative**: Keep the DEC-120-anchored statement in `templates/plan.yaml` as
  the authority; have the other three cite it by decision id (`DEC-120`) rather than
  restating the rule prose, the way the surrounding `approval` block already does
  for the `status` field two lines above.
- **appliable**: false — all four files (`templates/plan.yaml`, `harness/SKILL.md`,
  `harness-spec-driven/SKILL.md`, both `harness-validator-lead.md` copies) resolve to
  NOBODY on the grant map for this run; backlog row only.

No regex/anchor findings this pass — I did not flag any conjunct in `check-state.sh`'s
INV-32 block or any pattern in `test-plan-panel.py`/`test-harness-yaml-corpus.py`, so
the counter-input requirement does not apply.

## Explicitly not flagged, and why

- No conjunct in INV-32 (`check-state.sh` lines 122–186) is redundant — every `or`
  and every combined boolean tests a distinct, independently-failing condition (panel
  presence vs. `last_run` vs. `findings` shape; `who` vs. `date` format; reader status
  vs. skip-detail completeness). Removing any of them narrows what the invariant
  catches.
- No finding here proposes deleting or weakening any assertion — all three are
  "consolidate the prose to one authority" proposals on documentation, not on test or
  gate logic, and all three are explicitly marked backlog-only regardless since none
  resolve to a grantable owner this run.
- Did not flag the two reader prompts inside `plan-panel.yaml` restating "`unrated` is
  gating-equivalent to high" once each — the two readers are independent sub-agent
  dispatches that share no context, so each needs its own copy of the instruction;
  this is not the same failure mode as findings 1–3, where the same reader (a human
  editing the template, or the hosting lead) would see the restatement twice.

artifact: this file
