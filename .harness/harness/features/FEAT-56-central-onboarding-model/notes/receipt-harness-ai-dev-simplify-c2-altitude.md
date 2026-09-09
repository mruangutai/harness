# Receipt — harness-ai-dev — FEAT-56 simplify-c2 ALTITUDE (cycle 2)

## BLUF
Two verbatim-duplicate blocks between `harness-init` and `harness-add-repo` are the strongest
findings (dev-ops delegation bullets, ~25 lines; the technical-interview block). SPEC.md restates
the two-artifact split three times at the same altitude. DEC-220 names a compensating control for
its first accepted residual but not its second. All findings resolve to NOBODY/documentor —
`lane: report-only` throughout, nothing applied.

## Surfaces read
- **Read in full**: `.claude/skills/harness-init/SKILL.md` (279 ln), `.claude/skills/harness-add-repo/SKILL.md` (185 ln), `.omp/commands/harness.md`, `.omp/commands/harness-plan.md`, `.harness/harness/docs/DECISIONS.md` new entries (DEC-220, DEC-221 — only two new entries found, not three; see note below).
- **Sampled**: `.harness/harness/docs/SPEC.md` diff (onboarding sections only, via grep+diff), `.harness/harness/docs/DECISIONS.md` full diff stat.
- **Skipped for budget**: `.omp/commands/harness-grilling.md`, `.omp/commands/harness-ship.md` (diff stats show additive/small, not onboarding-split-shaped); `.harness/harness/docs/BUILD.md`, `DECISIONS-INDEX.md`, `org.html`; the six templates (git diff shows **no template files changed** in this range — nothing to compare there, so item 3's template leg is empty by inspection, not by skip).
- **Note on item 4**: the assignment cites "three new DECISIONS entries" but `git diff 4b5dbb23..HEAD -- .harness/harness/docs/DECISIONS.md` shows only two new `## DEC-` headings added (DEC-220, DEC-221); a third bullet (`cli_min_version`) is an addition to an existing entry's band table, not a new entry. Reporting what I found rather than searching further for a third that the stat does not show.

## Pairs considered and dismissed
- `.omp/commands/harness.md` §0 Gate (routing table: which skill/door to open) vs `harness-init`/`harness-add-repo` preflight sections (whether that skill itself can proceed). Different altitude: the door decides *which* skill to enter; the skill's own preflight decides whether *it* can proceed. Not a duplicate — **leave**.
- `.claude/commands/*.md` vs `.omp/commands/*.md`: byte-identical apart from a generated-file banner (`diff` confirms). This is the settled generated-adapter model — **leave**, out of scope by design.

## Findings

### F1 — dev-ops delegation bullets duplicated verbatim (~25 lines) between init and add-repo
- file: `.claude/skills/harness-init/SKILL.md:162-190` ("### 4. Delegate detection to `dev-ops`")
- file: `.claude/skills/harness-add-repo/SKILL.md:89-116` (unnumbered continuation of "### 2. Interview — technical")
- summary: both blocks carry the identical 7-bullet dev-ops contract (verify every `cmd` by running it; never invent a plausible command; surface every `cmd: null` as a DECISION; delete the `_reason`; keep worktree/vendor dirs in `exclude`; report source layout; check team conventions) word-for-word, differing only in one clause about where `test_kinds` lands (control-plane `harness.json` vs. the fleet member's own `harness.json` under `workspace_root`).
- cost: any future edit to the dev-ops contract (e.g. an eighth bullet, a wording fix to the DEC-163 clause) must be made in both files by hand; nothing enforces the second edit, so the two will drift the first time either skill is touched alone.
- alternative: designate `harness-init:162-190` the authority (it is read first in the onboarding sequence and the fuller of the two). Replace `harness-add-repo:89-116` with:
  `Spawn harness-dev-ops with the answers. It follows the same dev-ops contract as harness-init step 4 (harness-init SKILL.md, "Delegate detection to dev-ops") — verify every cmd, never invent one, surface every null as a DECISION, keep worktree/vendor dirs excluded, report source layout — with one difference: it writes test_kinds into the fleet member's own harness.json in its checkout under workspace_root; the main session lands that file through step 1, rather than into the control plane's own harness.json.`
- lane: report-only (both files resolve to NOBODY/documentor)
- severity: high
- recommendation: fold-in

### F2 — "Interview — technical" batched-question block duplicated near-verbatim
- file: `.claude/skills/harness-init/SKILL.md:153-161` ("### 3. Interview — technical")
- file: `.claude/skills/harness-add-repo/SKILL.md:81-88` ("### 2. Interview — technical")
- summary: identical `AskUserQuestion` batch (project type, frontend/backend framework, user-facing UI) restated in both; init additionally explains *why* the UI question matters (one extra sentence).
- cost: a fourth interview question added to one flow (e.g. by a future decision) has no forcing function to reach the other; the two batches silently diverge on what onboarding asks.
- alternative: keep the bullet list only in `harness-init:153-161`. Replace `harness-add-repo:81-88` bullets with:
  `Same three questions as harness-init step 3 ("Interview — technical") — project type, frontend/backend framework, user-facing UI.`
- lane: report-only
- severity: medium
- recommendation: fold-in

### F3 — SPEC.md restates the two-artifact split three times at the same altitude
- file: `.harness/harness/docs/SPEC.md:134-137` (unlabeled prose paragraph, "Onboarding is two skills, not a team...")
- file: `.harness/harness/docs/SPEC.md:444-447` ("**Onboarding a repository is three things, in order (DEC-220):**")
- file: `.harness/harness/docs/SPEC.md:462-464` ("**Onboarding is two skills (DEC-221).**")
- summary: same architecture-doc, same reader (someone reading SPEC.md to understand onboarding), same depth of detail (which files land where, in what order), stated three separate times rather than once with two backward pointers.
- cost: SPEC.md is the "spec is authority" surface; a future SPEC edit to the split's shape (e.g. a fourth thing landed) has three sites to update in one file and nothing flags a missed one.
- alternative: keep the fullest statement at `SPEC.md:444-447` (cites DEC-220 directly, most complete) as authority. Collapse `134-137` to: `Onboarding is two skills, not a team (§3) — see "Onboarding a repository is three things" below.` Collapse `462-464` to: `Onboarding is two skills (DEC-221) — see above.`
- lane: report-only (SPEC.md resolves to documentor)
- severity: medium
- recommendation: fold-in

### F4 — DEC-220's second accepted residual has no compensating control named at the point of record
- file: `.harness/harness/docs/DECISIONS.md:6999-7001`
- summary: the entry's first residual (registering before config lands) names its control in the same sentence — `factory_config.py --check-product-configs` names the failure, "a check that is OPERATOR-RUN, with no standing invariant behind it." The second residual two sentences later — "nothing grades a fleet member's remote config on every run, and a member whose `harness.json` is deleted after onboarding stays invisible until the next build against it" — has no control named at all, not even an operator-run one.
- cost: a reader of this decision cannot tell whether this residual is genuinely uncontrolled or whether the control is assumed-obvious (e.g. "the next build against it" is itself the control); the ALTITUDE rubric ("a residual accepted without its compensating control named is a finding") treats this as a real gap, not stylistic.
- alternative: name the control explicitly, e.g. append: "The compensating control is the same `--check-product-configs` operator-run check, plus the fact that a deleted `harness.json` fails the *next* build closed rather than silently — there is no periodic drift check between builds." If that is not in fact the control, the entry should say what is.
- lane: report-only (DECISIONS.md resolves to documentor)
- severity: medium
- recommendation: briefing-row

## What did not make it in
Items 2 (four `.omp/commands` doors) beyond `harness.md`/`harness-plan.md`, and item 3's template leg (no templates changed in-range), were sampled/inspected but not exhaustively read — see "Surfaces read" above for exact boundary.
