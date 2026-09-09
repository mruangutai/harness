# Research — FEAT-56 plan `decisions:` → DECISIONS.md trace audit

**BLUF.** Two mis-maps found and corrected, both confirmed against primary source before amending:
D-08 pointed at DEC-221 (fleet registration) when its subject is the two-skill split — now DEC-222;
D-01 pointed at DEC-174 (self-hosting carve-out) when DEC-221 is the entry that literally strikes
issue 206 item 2 — now DEC-221. **D-08's mis-mapping PREDATED the merge.** Pre-renumber the pair was
DEC-220 (fleet registration) / DEC-221 (two skills), and D-08 carried `dec: DEC-220` — already the
wrong entry. The renumber's mechanical +1 moved it to DEC-221 and thereby **preserved** a pre-existing
error; it did not create it. This is not renumber fallout, and no renumber check could have seen it:
occurrence counts, index diffs and anchor checks were clean throughout because every citation pointed
at an entry that *exists*. None of them can see whether it is the RIGHT entry — the third instance of
that class in this integration (docs citations, two test-file citations, now the plan's own trace).

**Independent verification.** I read D-08's `choice`/`because` in plan.yaml and the `## DEC-221`
(DECISIONS.md:7022-7054) and `## DEC-222` (:7056-7090) headers, `**Chose:**`, `**Over:**` and
`**Because:**` paragraphs in the **worktree's** DECISIONS.md — the copy that carries DEC-221/DEC-222 —
not the main checkout's. I did not rely on the dispatch's or the lead's claim for either amendment.

**The "predated the merge" claim is git-verified, not inferred.** At HEAD (`bb39d5c4`)
`git show HEAD:.harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml` carries
`dec: DEC-220` for D-08 — the renumber to DEC-221 is itself still uncommitted in this tree. And at
that same HEAD, `DECISIONS.md` contains **two** `## DEC-220` headers ("Build entry opens the mirror…"
and "Onboarding is fleet registration plus one product-resident file"), which is the id collision the
renumber existed to fix, while the two-skill split sat at `## DEC-221`. So the committed pointer was
ambiguous between two entries and matched D-08's subject under neither reading. The error is
pre-merge; the renumber's +1 only carried it forward.

## Audit — every non-`none` `dec:`

| plan D-NN | plan decision's subject | named entry's subject | verdict |
|---|---|---|---|
| D-01 (was DEC-174) | issue 206 item 2 not built; no central `.harness/products/` tree; a central config would be read by nothing | DEC-174: self-hosting stops at the enforcement layer — plan-but-don't-execute guard changes | **DID NOT COVER** → amended to DEC-221, which *chose* ".harness/products/ is created nowhere" (:7026-7027), whose `Over:` strikes "issue 206 item 2's central `.harness/products/<name>/harness.json`" (:7036-7037), and whose `Because:` restates D-01's own clause — "`product_config` reads a member's config from the remote at its `default_branch` with no disk fallback, so a central copy would be read by nothing" (:7044-7045). DEC-174 is a *referenced* authority in DEC-221's `Record:` (:7054), never D-01's subject |
| D-08 (was DEC-221) | onboarding becomes two artifacts: `harness-init` keeps Track A + `--upgrade`, new `harness-add-repo` takes Track B minus steps 6-8 | DEC-221: onboarding **is** fleet registration plus one product-resident file | **DID NOT COVER** → amended to DEC-222, "Onboarding is two skills: `harness-init` configures a checkout, `harness-add-repo` registers a repository" (:7056), whose `Chose:` names the same Track A / Track B seam and the same removal of the BRIEF/approval/design steps (:7058-7068), and which says of the predecessor "DEC-221 fixed what registration *is* but left it inside a skill whose other half configures a checkout" (:7085-7086) |
| D-09 → DEC-120 | first-BRIEF, approval and design leave onboarding; a configured member with no BRIEF routes to `/harness-plan` | DEC-120: the orchestrator becomes a spawned agent, the main session becomes the user channel | **DOES NOT COVER the choice** — DEC-120 supplies only the supporting premise (which tier holds the user channel, so who may take an approval). The entry that actually *records* D-09 is DEC-222: `Chose:` ":7066-7068" ("Those three are `/harness-plan`'s work… routes to `/harness-plan`, never back into onboarding") and `Over:` ":7078-7079". **Not amended** — outside my authorization; raised as Q1 |
| D-10 → DEC-06 | `harness-add-repo` is a skill, no command door; DEC-06 is NOT re-decided | DEC-06: crews live under `.claude/skills/`, the runner is a skill not a command (:90-99) | **COVERS.** D-10 is a deliberate conform-and-do-not-reopen pointer, and DEC-222 independently confirms "DEC-06 is **not overturned** here… only its distribution premise expired, when `deploy.sh` was deleted in commit 45859123" (:7086-7088). Note: D-10's *new* content (premise expired, conclusion survives on new ground) is recorded in DEC-222, so this pointer is correct but partial by design |
| D-12 → DEC-83 | `harness-init`'s preflight carries no Claude CLI version check at all; the floor leaves the preflight entirely | DEC-83 (as amended in this worktree): nesting default is 3, plus the amended bullet "No `cli_min_version` is declared in any configuration file… The 2.1.217 floor stands as the documented compatibility fact… **consulted by a reader rather than enforced by a gate**" (:977-981) | **COVERS**, by the "enforced by a gate" clause — that is exactly the enforcement point D-12 severs — and by the band table (:960-964) plus ":981" tying the floor's original reason to the spawn env vars, which is D-12's stated ground. Coverage is by clause, not by the bullet naming the preflight |
| D-13 → DEC-83 | `cli_min_version` removed from all five config sites; DEC-83 amended to match; the band table survives | same amended DEC-83 bullet, which enumerates the config sites — `.harness/harness.json`, `.harness/team-config.yaml`, and the three templates (:977-979) — and preserves the band table (:960-964) | **COVERS**, squarely; this is the promotion target of D-13 |

**Two entries at DEC-83 is legitimate.** Both genuinely bear on it, and they bear on *different clauses
of the same amended bullet*: D-13 on the site enumeration (:977-979), D-12 on the "enforced by a gate"
clause (:980-981). The operator ordered DEC-83 amended by D-13 itself, so the single entry absorbing
both is the recorded intent, not duplication.

## Amendments made — two, separately revertible

1. **D-08** `dec:` DEC-221 → DEC-222. `plan-merge.py amend --key decisions --id D-08 --field dec`,
   compare-and-swap on `102a4f84a5577232a10f5d4e46b3b3262d78330678d41f80961190ed84c0ef25`.
2. **D-01** `dec:` DEC-174 → DEC-221. Same verb, CAS on
   `6cb8c1ca8955905912aa2c464833bdaaaf6579c880782a66b4f10c6a4793bedc`. Confirmed by my own read of all
   three texts (D-01's `choice`/`because`; DECISIONS.md:7024-7027, :7036-7037, :7044-7045 for DEC-221;
   :4306-4348 for DEC-174 — its subject is hooks/validators/gate scripts and nothing in it touches
   product config placement). Revert this one alone by amending D-01 back to `DEC-174`.

`approval:` block bytes unchanged: sha256
`d9c217c0ff1a78ec4bde611a6c95888a4093b267e8bb213ad8563bda5bccb1f8` before and after both amendments;
`approved / molchairuangutai / 2026-09-09`. Nothing else in plan.yaml was touched, no commit was made.

## Does anything now map to DEC-221?

**Yes — D-01 does, after amendment 2.** Before it, nothing did, and that hole was the visible symptom
of the same single error: DEC-221's plan-side origin is D-01, and D-08 had been sitting in its slot.
So the answer to "is a missing DEC-221 mapping a GAP or CORRECT?" resolves to neither: it was an
artifact of the mis-map, now closed. No plan decision was invented to fill it.

## Open questions

- **Q1 (non-blocking):** D-09's `dec: DEC-120` names the supporting premise rather than the entry that
  records the choice (DEC-222, :7066-7068 / :7078-7079). Correcting it would put a third plan decision
  on DEC-222; leaving it keeps a pointer that is defensible but weaker than the others. Needs the
  lead's or operator's call — outside my dispatch authority.
- **Q2 (non-blocking):** the inverse class exists too. **D-11** (canonical command-door root is
  `.omp/commands`, `.claude/commands` holds generated adapters) carries `dec: none`, yet DEC-222's
  `Chose:` records exactly it (:7069-7071) and its `Over:` records the rejected symlink (:7075-7077).
  A promoted decision reading `none` is invisible to the same audits that missed D-08.
- **Q3 (harness defect, non-blocking):** no existing check can catch this class. Every renumber and
  citation check verifies that a cited id *exists*; none verifies that it is the *right* entry. A
  subject-match check — compare a plan decision's `choice` against its `dec:` entry's header — is the
  missing gate, and it would have caught all three instances in this integration.

## Verification

All three run inside the worktree, 2026-09-09, after both amendments. Output verbatim.

**1. Trace and approval** — `env -u HARNESS_AGENT_TYPE python3 -c "import yaml;d=yaml.safe_load(open('.harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml'));print([(x['id'],x.get('dec')) for x in d['decisions']]);print(d['approval'])"`

```
[('D-01', 'DEC-221'), ('D-02', 'none'), ('D-03', 'none'), ('D-04', 'none'), ('D-05', 'none'), ('D-06', 'none'), ('D-07', 'none'), ('D-08', 'DEC-222'), ('D-09', 'DEC-120'), ('D-10', 'DEC-06'), ('D-11', 'none'), ('D-12', 'DEC-83'), ('D-13', 'DEC-83'), ('D-14', 'none')]
{'date': '2026-09-09', 'approved_by': 'molchairuangutai', 'status': 'approved'}
```

D-08 at DEC-222, D-01 at DEC-221, approval still `approved / molchairuangutai / 2026-09-09`. The
`approval:` block's own bytes are byte-identical before and after both amendments: sha256
`d9c217c0ff1a78ec4bde611a6c95888a4093b267e8bb213ad8563bda5bccb1f8` on both reads.

**2. Route check** — `python3 .claude/skills/harness/bin/check-plan-routes.py`, that relative path,
run from inside this worktree (an absolute path into the main checkout grades the wrong tree and
reports a false all-clear). **Exit 1, exactly 1 violation** — the D-14-accepted owner-manifest
deviation, unchanged by this work.

```
scanning /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model/.harness/*/features/*/{plan.yaml,PLAN.md}
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
DEVIATION /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model/.harness/team-config.yaml differs from /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml; routes were resolved against the owner manifest because that is what the hook consults
OK T-04 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-01: declared main-session-direct (.claude/skills/harness-init/SKILL.md ungranted)
OK T-02 granted to harness-backend-dev, harness-dev-ops
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-05: declared main-session-direct (.claude/skills/harness/templates/README.md, .claude/skills/harness/templates/harness.json, .claude/skills/harness/templates/team-config.yaml, .claude/skills/harness/templates/BRIEF.md ungranted)
OK T-06: declared main-session-direct (.claude/commands/harness.md, .claude/commands/harness-plan.md, .claude/commands/harness-grilling.md, .claude/agents/harness-dev-ops.md, .omp/agents/harness-dev-ops.md ungranted)
OK T-07 granted to harness-documentor
OK T-08: declared main-session-direct (.claude/skills/harness/references/github-mirror.md ungranted)
OK T-09 granted to harness-backend-dev, harness-dev-ops
OK T-10: declared main-session-direct (.claude/skills/harness-add-repo/SKILL.md ungranted)
OK T-11: declared main-session-direct (.claude/skills/harness-init/SKILL.md ungranted)
OK T-12: declared main-session-direct (.claude/commands/harness.md, .claude/commands/harness-plan.md, .claude/commands/harness-ship.md, .claude/commands/harness-grilling.md, .claude/skills/harness-grilling/SKILL.md, .claude/skills/harness/templates/README.md, .claude/skills/harness/templates/harness.json, .claude/skills/harness/templates/team-config.yaml, .claude/skills/harness/templates/BRIEF.md, .claude/skills/harness/templates/PLAN.md, .claude/skills/harness/templates/DESIGN.md, .claude/skills/harness/references/github-mirror.md ungranted)
OK T-13: declared main-session-direct (.omp/commands/harness.md, .omp/commands/harness-plan.md, .omp/commands/harness-ship.md, .omp/commands/harness-grilling.md, .claude/commands/harness.md, .claude/commands/harness-plan.md, .claude/commands/harness-ship.md, .claude/commands/harness-grilling.md ungranted)
OK T-14 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-15: declared main-session-direct (.omp/agents/harness-dev-ops.md, .omp/agents/harness-visual-designer.md, .claude/agents/harness-dev-ops.md, .claude/agents/harness-visual-designer.md ungranted)
OK T-16 granted to harness-documentor
OK T-17 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-18 granted to harness-dev-ops
OK T-19: declared main-session-direct (.harness/team-config.yaml, .claude/skills/harness/templates/harness.json, .claude/skills/harness/templates/team-config.yaml, .claude/skills/harness/templates/examples/harness.kaya-ai.json ungranted)
OK T-20 granted to harness-documentor
1 violation(s) across 5 plan(s)
examined 87 feature dir(s); 82 skipped as shipped
```

**3. Working tree** — `git status --porcelain`

```
 M .harness/README.md
 M .harness/harness/docs/BUILD.md
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/docs/SPEC.md
 M .harness/harness/docs/org.html
 M .harness/harness/features/FEAT-56-central-onboarding-model/observations/harness-documentor.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/observations/harness-pm.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
 M README.md
 M tests/integration/test-check-state-records.py
 M tests/integration/test-onboarding-split.py
 M tests/unit/test-no-distribution.py
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-deccite-eng.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-rehome-eng.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-documentor-renumber-product.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-pm-renumber-product.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/research-FEAT-56-d08-dec-trace-audit.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/research-t03-verify-amend.md
```

Mine are exactly three: `plan.yaml` (two `dec:` lines, via `plan-merge.py amend`), this notes file,
and `observations/harness-pm.md` (appended through `observations-merge.py`, which merges under a
lock). **Untouched by me — sibling squads' uncommitted work:** `.harness/README.md`,
`docs/BUILD.md`, `docs/DECISIONS-INDEX.md`, `docs/DECISIONS.md`, `docs/SPEC.md`, `docs/org.html`,
`README.md`, `observations/harness-documentor.md`, `tests/integration/test-check-state-records.py`,
`tests/integration/test-onboarding-split.py`, `tests/unit/test-no-distribution.py`, the four
`receipt-*.md` files and `notes/research-t03-verify-amend.md`. `plan.yaml`'s diff against HEAD also
carries one sibling line — T-03's `verify` at line 903, the FixT03Verify amend — which is theirs and
which I did not touch. Nothing was committed; HEAD is still `bb39d5c4`.
