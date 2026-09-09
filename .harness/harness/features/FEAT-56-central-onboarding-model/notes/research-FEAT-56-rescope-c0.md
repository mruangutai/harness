# Re-scope proposal — FEAT-56 · operator UAT FAIL of 2026-09-08

**BLUF — recommended shape: REVISE FEAT-56 IN PLACE as a two-SKILL split (`harness-init` keeps
Track A, a new `harness-add-repo` skill takes Track B), and do NOT build a command surface for it —
because the onboarding instruction of record is a *skill*, skills already load provider-neutrally
under OMP, and minting a `.claude/commands/harness-add-repo.md` door would deliver exactly the
Claude-Code-only shape the operator just rejected.** The missing `/harness-*` door layer is real,
pre-dates this feature, and belongs to a successor (§2, Q1).

All anchors read at HEAD `cd680240` of `feat/FEAT-56-central-onboarding-model` in this worktree.

---

## 1. What the operator is and is not rejecting

| Part of the ruling | Status | Consequence here |
|---|---|---|
| The central onboarding model (fleet registration + central tree + one product-resident file) | **CONFIRMED** | DEC-220 stands; every delivered task stands (§6) |
| A Claude-Code-only implementation | **REJECTED** | binds the *kind* of artifact the split produces (§3) |
| One combined command doing both bootstrap and registration | **REJECTED** | binds the split itself; kills SC-09 as written |

### Every SC, graded

| SC | Grade | Note |
|---|---|---|
| SC-01 ordered central-model statement in `harness-init/SKILL.md` | **survives-amended** | the ordered markers live in Track B prose (`SKILL.md:8-11`, `:245-247`), which moves; re-point the subject blob to `.claude/skills/harness-add-repo/SKILL.md` and re-run T-01's block there |
| SC-02 per-clone install strings verbatim | **survives-unchanged** | Track A stays in `harness-init` (`SKILL.md:53`, `:87`); `test-hooks-install.py` keeps its subject. Met, not re-proved |
| SC-03 six executable sites state the central model | **survives-amended** | add one clause: each remedy must name the door that actually does the job (registration remedies → `harness-add-repo`). Today `check-state.sh:111` and `:2436` say "control-plane clone" where the shipped skill now says "this harness checkout" — inherited drift |
| SC-04 fifteen docs state onboarding as registration + one file | **survives-amended** | same fifteen files, plus the new skill; three of the fifteen are command files whose prose names the wrong door once split |
| SC-05 `--check-product-configs` names an unreachable member | **survives-unchanged** | `factory_config.py:328,478`; 18/18 unit checks. Untouched by both rejections |
| SC-06 unit suite exit 0 | **survives-unchanged** | standing gate |
| SC-07 integration suite exit 0 | **survives-unchanged** | standing gate |
| SC-08 `check-omp-port.py` ok + `check-instruction-paths.py` 0 violations | **survives-amended** | the new skill enters `MAIN_SESSION_ONLY` (`check-instruction-paths.py:14-18`); the criterion must assert 0 violations *with the new skill present*, otherwise the split is ungated |
| SC-09 operator confirms `harness-init` is the procedure they would run to onboard the next repository | **dies** | false by construction after the split: `harness-init` no longer onboards a repository. Replaced by two uat criteria, one per door |
| SC-10 `templates/team-config.yaml` parses as YAML | **survives-unchanged** | met, delivered |

Five unchanged (SC-02, 05, 06, 07, 10) need **no re-proving**; four amended re-cite rather than
rebuild; one dies.

## 2. What provider-neutral onboarding costs, measured

Confirmed by listing, not re-litigated: `.omp/` holds `config.yml agents extensions providers` —
no `commands/`. `.claude/commands/` holds exactly `harness.md`, `harness-plan.md`,
`harness-ship.md`, `harness-grilling.md`.

**Reading (c) holds — provider-neutral *onboarding* is already delivered by the OMP port and needs
documenting, not building.** The grounds, each measured:

- Onboarding's instruction of record is a **skill**, not a command: there is no
  `.claude/commands/harness-init.md` and never was (`git ls-files .claude/commands` returns four
  files, none of them init).
- Skills load provider-neutrally today. `.claude/skills` is the real directory and `.agents/skills`
  a symlink to it, asserted by `check-omp-port.py:125-133`. This very OMP session, running with
  `.omp/config.yml` `disabledProviders: [claude]`, resolved its skills from
  `/Users/molchairuangutai/GitHub/harness/.agents/skills/…/SKILL.md`. Model neutrality is likewise
  delivered: `.omp/providers/anthropic.yml` and `openai.yml` map the four roles, and
  `check-omp-port.py:84` refuses any agent whose `model` is not a provider-neutral alias.
- **The documenting is not cosmetic.** ~20 documents tell the operator to type `/harness-init`
  (`check-state.sh:111`, `check-domain.sh:385`, `upgrade-config.py:6`, `README.md`, `SPEC.md`,
  `BUILD.md`, `org.html:286`, templates …). That slash spelling resolves to **no command in either
  surface** — Claude Code has no such file, and OMP would not see it if it did. The revision
  replaces slash spellings with "load the `harness-init` / `harness-add-repo` skill".

**What is NOT delivered, and is not onboarding's to fix:** the four existing doors are invisible
under OMP. `.omp/config.yml` disables the `claude` discovery provider, and disabling it "also drops
Claude-discovered MCP servers, commands, skills, hooks, tools, and settings"
(`omp://context-files.md:206,209`); OMP reads slash commands from `<root>/commands/*.md`
(`omp://config-usage.md`, §6 scope-specific loading), i.e. `.omp/commands/*.md`, which does not
exist; and `.omp/extensions/harness-hooks.ts` registers no command. So `/harness`, `/harness-plan`,
`/harness-ship`, `/harness-grilling` are Claude-only today.

**Cost of closing that gap (reading (b), if the operator wants it): 14 files**, or 16 if the
`.claude/` side is generated rather than symlinked — 4 canonical `.omp/commands/*.md`, the
`.claude/commands` adapter surface (1 symlink, or 4 generated files + a `sync-command-adapters.py`
and its test), `bin/check-omp-port.py` + `tests/integration/test-check-omp-port.py` (parity
assertion), `bin/check-instruction-paths.py` (its `scope()` at `:45-59` does not scan commands
today) + `tests/unit/test-no-distribution.py:77-83` (the four-doors assertion reads
`.claude/commands`), and 4 doc files (`DECISIONS.md` + `DECISIONS-INDEX.md` for the new home,
`SPEC.md`, `org.html` doors table). Unlike agents, commands carry no frontmatter, so no format
transformation is needed and the symlink shape is the honest one. **This is a successor feature, not
part of the re-scope** — it touches every door equally and none of them is onboarding.

## 3. The command split, concretely

The seam is already cut: `## Track A — bootstrap this harness checkout` (`SKILL.md:48`, steps 1/5/9
at `:53`, `:161`, `:185`, plus `## --upgrade` at `:209`) and `## Track B — register a repository
into this configured fleet` (`:239`, steps 2/3/4/6/7/8 at `:245`, `:284`, `:292`, `:324`, `:335`,
`:408`).

- **`harness-init` retains:** the preflight (`:30`), Track A, `--upgrade`, the Red flags table
  (`:419`). It becomes only "configure this harness checkout".
- **`harness-add-repo` takes:** the three-things opening paragraph (`:8-17`), Track B in full, and
  the one-file rule. Name accepted — no source convention forces another: the directory convention
  is `harness-<verb-phrase>` (`harness-init`, `harness-grilling`, `harness-wayfinding`,
  `harness-add-repo` fits) and `check-instruction-paths.py:30-31` globs `harness-*`.
- **Kind: a SKILL, not a command, and not both.** A command file is Claude-only (§2), so a
  `.claude/commands/harness-add-repo.md` would re-commit the rejected shape; a skill is reachable
  under every provider today. Owner: the main session — no agent domain grants it
  (`check-domain.sh --resolve .claude/skills/harness-add-repo/SKILL.md` → `NOBODY`, exit 0),
  so it is a declared `main-session-direct` task under DEC-179/DEC-174.

**Referencing sites the new name breaks** (method: `notes/research-FEAT-56-init-audit.md` item 3):

| Site | What breaks |
|---|---|
| `bin/check-instruction-paths.py:14-18` | `MAIN_SESSION_ONLY` tuple — add `"harness-add-repo"` or the anchor rule scans it (`_skill_docs`, `:28-34`) |
| `bin/check-omp-port.py:97-103` | validates every agent's `autoloadSkills` against `.agents/skills/<name>/SKILL.md`; any agent that autoloads the new skill must exist before the assertion runs |
| `bin/check-state.sh:111, 287, 408, 2375, 2436` | four `/harness-init` remedies + the "control-plane clone" wording; the registration-shaped ones re-point |
| `bin/check-domain.sh:385` | fail-open remedy names the door |
| `bin/upgrade-config.py:6, 192, 236` | docstring + two remedies |
| `bin/gh-sync.py:256` | `github.repo` skip message |
| `bin/layout_migration.py:123` | `MARKER` applicability rationale |
| `.omp/agents/harness-dev-ops.md:53` + generated `.claude/agents/harness-dev-ops.md` | "During `/harness-init` you determine…" — Track B step 4; regenerate with `bin/sync-agent-adapters.py --apply` |
| `.omp/agents/harness-visual-designer.md:42` + its `.claude/` adapter | Track B step 8 design pass |
| `.claude/commands/harness.md:13`, `harness-plan.md:19`, `harness-grilling.md:7` | routing prose: "not onboarded" routes to the wrong door once split |
| `.claude/skills/harness-grilling/SKILL.md:23` | one clause |
| `.harness/harness/docs/org.html:286` (owner cell) and the doors table at `:328-334` | skill/door inventory |
| `README.md:192`, `.harness/README.md`, `SPEC.md`, `BUILD.md` | onboarding narrative names one door |
| `templates/README.md`, `templates/harness.json:2`, `templates/team-config.yaml:3`, `templates/BRIEF.md`, `references/github-mirror.md` | template surface |
| `DECISIONS.md` + `DECISIONS-INDEX.md` | new entry, by amendment; regenerate the index (`gen-decisions-index.py`) |
| `tests/integration/test-hooks-install.py:265` | `case_commands_verbatim_in_skill` reads `harness-init/SKILL.md` — safe (Track A stays), but the case must be re-anchored if step numbering changes |
| `tests/integration/test-post-merge-sweep.py:783-785`, `bin/post-merge-sweep.sh:68-69` | cite `SKILL.md:73/:78`; Track B's removal is below those lines, so they survive — re-anchor to headings anyway |
| `tests/integration/test-layout-migration.py:250-254` | onboarded-product fixture premise, already amended once |

`.harness/harness/features/**` occurrences are record; DEC-188 forbids editing them.

## 4. Recommendation on shape

**Revise FEAT-56 in place.** Reasons, weighing the three facts:

- The operator **confirmed the goal**, so the problem statement, DEC-220 and all six REQs stand. The
  re-scope changes *how many doors the instruction of record has*, not what onboarding is.
- The delivered work passes every gate and the panel returned `must_fix: []`, and an in-place
  revision **keeps** it: five SCs stay met untouched, four are re-cited over moved prose, one dies.
  Nothing is reverted.
- The split runs along a seam that already exists in the shipped file, and its blast radius (§3) is
  the *same set of files* T-05/T-06/T-07 already swept. Doing it in place pays that sweep once.

**Rejected option — ship the delivered central model now and open a successor — and its cost.** It
requires the operator to withdraw their own binding "do not ship", because SC-09 is FAIL and no
honest record can call a feature shipped on a failed uat. Worse, it merges a `harness-init` whose
Track B is precisely what the successor deletes: the fifteen-file documentation inspection (SC-04)
and the six executable-site sweep (SC-03) would both be paid a **second** time, over the same files,
inside two months of each other. That is the expensive option, not the safe one.

The 11-of-11 cycle cap is spent either way; neither option is free of a budget raise. It argues for
choosing the shape that pays the doc sweep once.

## 5. Approval requirements — operator actions, in order

1. **Reset both approval fragments to pending** (only the main session may write them):
   - `…/features/FEAT-56-central-onboarding-model/plan.yaml` — the `approval:` mapping at lines 3-6
     (`status: approved`, `approved_by: molchairuangutai`, `date: '2026-09-08'`).
   - `…/features/FEAT-56-central-onboarding-model/BRIEF.md` — `## Approval` at lines 177-181.
   The signature covers the OLD eight-task set and must not carry onto the revised one.
2. **Decide the goal-statement change (approval-gated, SPEC 4.4).** Current, `BRIEF.md:21-23`:
   *"Onboarding a repository means three things and nothing else: register it in
   `.harness/factory/fleet.yaml`, stand up its central per-segment tree under
   `<control-plane>/.harness/<segment>/`, and land exactly ONE file — `harness.json` — on that
   repository's own default branch, where `product_config` reads it."*
   Proposed replacement: *"Onboarding a repository means three things and nothing else, in this
   order: land exactly ONE file — `harness.json` — on that repository's own default branch, where
   `product_config` reads it; register it in `.harness/factory/fleet.yaml`; stand up its central
   per-segment tree under `<control-plane>/.harness/<segment>/`. The instruction of record is two
   skills, not one command: `harness-init` configures this harness checkout, `harness-add-repo`
   registers a repository into its fleet. Both are skills, loadable under any model provider; no
   onboarding step lives in a Claude-Code-only command file."*
   (The reordering also repairs a live inconsistency: the current goal lists registration first,
   while D-04 and the shipped skill land the config first — `SKILL.md:247`.)
3. **Raise `max_total_cycles` from 11 to 22.** Derivation, not a guess: the revision sketches
   **7 tasks** — (T-09) split the skill in two, (T-10) `MAIN_SESSION_ONLY` + gate wiring, (T-11) the
   five executable-site door corrections, (T-12) the two agent definitions + adapter regeneration,
   (T-13) the doc/template/command-prose sweep and de-slashing, (T-14) the DECISIONS entry + index,
   (T-15) test re-anchoring plus one integration case asserting Track A is absent from
   `harness-add-repo` and Track B absent from `harness-init`. The measured rate on this feature is
   11 cycles for 8 tasks = 1.375; 7 × 1.375 ≈ 10, rounded to 11 of headroom → **22 total**.
4. **Rule on the door layer (Q1).** If the operator wants a *typed* `/harness-add-repo` in OMP, §2's
   14-file command re-home becomes a precondition and the cycle figure in (3) rises; if not,
   the re-scope ships two skills and the door gap goes to a successor feature.
5. **Order the panel re-run.** Full plan panel over the revised task set — all three readers
   (`should-not-exist`, `scope`, `goalcheck`), because every task id is new. Ship panel: `qa` and
   `code-reviewer` mandatory; `ui-reviewer` required because `org.html`'s owner cell and doors table
   change; `security-reviewer` may be recorded `skipped` with the reason "no credential, network or
   auth surface in the revised diff" — the validator lead's call, transcribed either way.
6. **Confirm the two replacement uat criteria** at signature: one that `harness-init` alone reads as
   "configure this checkout" with no registration step, one that `harness-add-repo` alone reads as
   the procedure to add a repository. SC-09 as written is retired.

## 6. What must not be lost

| Delivered artifact | Pointer |
|---|---|
| DEC-220 — onboarding is fleet registration plus one product-resident file | `.harness/harness/docs/DECISIONS.md` DEC-220 heading; index row in `DECISIONS-INDEX.md` |
| `product_config_report()` and `--check-product-configs` | `.claude/skills/harness/bin/factory_config.py:328` (report), `:449-478` (CLI guard, exit 2) |
| Its 18-case suite | `tests/unit/test-fleet-product-config.py` — 18/18 at the pin |
| Six corrected `bin/` sites | `check-instruction-paths.py:12-15`, `check-state.sh:111`, `check-domain.sh:385`, `upgrade-config.py:6`, `gh-sync.py:256`, `layout_migration.py:123` |
| The fifteen-file documentation sweep | enumerated in `BRIEF.md:116-124`, cited one-per-file in `notes/research-FEAT-56-goalcheck-ship-c0.md` §SC-04 |
| Four retired per-product-install claims | `check-state.sh:373-374`, `templates/harness.json:5`, `.harness/harness.json:4`, `.harness/harness.json:6` (`_handoff_done_when_baseline_note`) |
| Repaired team-config template (parses as YAML) | `.claude/skills/harness/templates/team-config.yaml` — SC-10 |
| The Track A/Track B seam itself | `harness-init/SKILL.md:48` and `:239` — the split reuses it rather than re-cutting it |

Nothing above is reverted by this proposal.

## Open questions

- **Q1 (blocking):** does "provider-neutral onboarding" require a *typed door* (`/harness-add-repo`
  in OMP), or is a provider-neutral skill sufficient? §2 measures that skills already are;
  §5 action 4 is the ruling.
- **Q2 (non-blocking):** the four existing doors are invisible under OMP (§2). Successor feature, or
  live with skill-triggered invocation? 14 files if built.
- **Q3 (non-blocking):** the three stale `copied into every onboarded project` residues and the
  `control-plane clone` / `this harness checkout` vocabulary drift (`check-state.sh:111`, `:2436`) —
  fold into T-13, or leave as the follow-up chore the goal-check already recorded?
