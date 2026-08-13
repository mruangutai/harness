# Grilling — #206, harness-init for the central model — 2026-08-12

Run in the main session. The output is decisions, not a plan.

**READY FOR pm as of 2026-08-13.** The one condition this artifact set — FEAT-16 builds first — is
met: FEAT-16 merged as `f01b7b6`. The facts below were re-derived at `862d270` and **four had moved
again**; read `## Fact refresh` before `## Facts I verified`, which it corrects.

## Destination

A repository can be **registered** with the factory and **configured centrally** — an entry in
`.harness/factory/fleet.yaml` plus `.harness/products/<name>/harness.json`, with config resolution
reading that file instead of this repository's own. Nothing else about onboarding moves in this
effort.

Reaching the end looks like: point the factory at `mruangutai/kaya-ai`, and the test matrix that
applies is kaya's, not harness's.

## Settled

- **Scope is registration plus central config only.** → The interview, `dev-ops` detection, domain
  seeding, the BRIEF and the codebase map keep their current addresses and re-home in a later
  effort. Named cost, accepted: a registered product is configured but not described — no detected
  test commands, no codebase map.
- **`harness-init`'s SKILL.md is rewritten in this effort, not deferred.** → Steps 1, 2 and 9 (the
  eight prerequisites, the `.harness/` scaffold, the restart warning) are deleted. Fleet
  registration becomes the new first step. Steps 3-8 keep their current wording until they actually
  move. Named cost, accepted: the skill then describes a HYBRID — its first step central, its later
  steps still writing into the product — and half-migrated prose can read worse than plainly stale
  prose. Taken deliberately over leaving the page instructing a reader to do a thing the factory no
  longer does.
- **`mruangutai/kaya-ai` gets a real product config in this effort.** → Not fixtures alone. A
  mechanism with zero real consumers has never been run against anything, and kaya is the only
  product that can prove the resolution works against a repository that is not this one.
- **FEAT-16 builds before #206 is planned.** → See `## Sequencing`.

## Settled later — the operator's rule for what `harness.json` IS (2026-08-13)

Ruled during FEAT-18's signature conversation, recorded here because **this effort is what implements
it**, and the operator declined a `DECISIONS.md` entry on the ground that #206's planning will state
it more precisely than a standalone record could.

> **`harness.json` holds harness RUNTIME metadata. Project, repo and GitHub data belongs with the
> product — `fleet.yaml` is the more accurate place for project-level data.**
>
> **`harness.json` and `fleet.yaml` today hold redundant data, and that redundancy is the defect.**

**The tree already half-agrees, which is what makes this a migration rather than a preference.**
Measured at `2ccd7f0`:

| Key in `.harness/harness.json` | Whose data is it? |
|---|---|
| `github` — `{sync: true, repo: "mruangutai/harness"}` | **repo data.** Already misfiled by this rule |
| `test_matrix`, `_matrix_provenance` | **project data** — what tests THIS project requires |
| `test_kinds` | **project data** — the commands THIS project can run |
| `commit_attribution`, `dirty_tree_whitelist` | mixed; decide per key |
| `budgets`, `gates`, `log_retention_days`, `schema_version`, `cli_min_version` | runtime metadata — these STAY |

So the rule does not merely justify moving `test_matrix`; **it names `github` as a third thing to
move**, which this artifact's fog section did not previously contemplate.

**The obstacle this rule runs into, measured and recorded rather than assumed.**
`mruangutai/harness` is **deliberately absent** from `fleet.yaml`, and the absence is the mechanism.
The file states it was measured both ways on a harness checkout under the factory workspace: with the
entry present `--resolve` returned **NOBODY**; with it absent `--resolve` **exits 2**. Louder, not
quieter. **So "move harness's own project data into `fleet.yaml`" requires giving harness a
`fleet.yaml` entry, which makes a guard quieter — the direction this repo normally refuses.**

One nuance that narrows it: that measurement was taken on a checkout **inside** `workspace_root`. The
live checkout at `~/GitHub/harness` is unaffected either way. The entry would only change what
happens when the factory builds harness itself.

**pm must resolve this as a named decision in the BRIEF**, not absorb it. There is no obviously right
answer: reversing DEC-174 am.1, a third config location, or harness being the one repo whose project
data legitimately stays local are all live, and the choice is the operator's at signature.

**Immediate consequence, already taken:** FEAT-18 keeps its three board keys
(`owner`, `number`, `station_field`) in `harness.json` for now, with the placement recorded in its
plan as knowingly temporary and pending this migration. The operator chose that over moving one key
ahead of the rest.

### The same question one level down: how much of the board's SHAPE is prescribed?

Raised by the operator in the same conversation. **Not *which file* holds project config, but *how
much of it is config at all*.**

**What is already prescribed, and correctly.** DEC-192 fixes the six station values —
`Backlog, Plan, Ready, Building, Review, Done` — as the board's column names, byte for byte and case
sensitive, with no alias table and no translation function. **FEAT-18's D-05 therefore declares NO
`stations` mapping**: it measured board 3 and found exactly those six. `fleet.yaml` carries a
`stations:` mapping only because a **product** board is foreign and may name its columns anything.
**That asymmetry is sound and should survive this effort.**

**What is still declared, and whether each earns its place:**

| Key | Verdict |
|---|---|
| `number` | **earns it.** Nothing else in the tree identifies harness's board |
| `owner` | **redundant — derivable.** `github.repo` is `mruangutai/harness`; the owner is the segment before the slash. It restates data two lines above it in the same file. Only a board owned by a different account than its repo would need it, which is not the case and is a strange thing to build for |
| `station_field` | **arguably redundant, and it is the interesting one.** DEC-192 prescribes the six *values*; nothing prescribes the *field name* holding them. `Status` is GitHub's default and is renameable |

**Why `station_field` is more than a tidiness question.** FEAT-16's ship review already recorded that
five of its criteria are *"correct today and guarded by nothing — if anyone renames a station on
board 2 or 3, this feature's central promise breaks and no gate anywhere will say so."* A pinned
field name is the same shape: **a string that goes stale silently.** Prescribing `Status` the way
DEC-192 prescribes the six values — and failing loudly on a board that does not carry it — converts a
silent staleness into a loud one, which is the direction this repo consistently chooses.

**For pm:** decide as a named BRIEF decision **per key**, not for "board config" as a block. The
three keys have three different arguments and a single ruling on all of them will be wrong about at
least one.

## Not yet specified

- **How a factory worker's session finds its product's config.** The worker stands in
  `workspace_root/<product>`, a checkout carrying no `.harness/` at all, so resolution has to reach
  back into the harness repository keyed by something. The fleet `name` is the obvious key and is
  not yet a decision.
- **Whether `harness-init --upgrade` applies to a product config or only to this repository's own.**
  `upgrade-config.py` merges `harness.json` deterministically today and would need to know which one.
- **Whether a product's domain globs are part of "configured".** The destination says config, and
  `team-config.yaml` lives solely in harness (operator ruling, 2026-08-09) — but nothing yet says
  whether a product's own paths are described there, or later, or never.
- **What the per-product path actually is.** `#206` proposes `.harness/products/<name>/`, and a fleet
  `name` is `owner/repo`, which contains a separator. Not sharp enough to be a question yet.

## Out of scope

- Re-homing the interview, `dev-ops` detection, domain seeding, the BRIEF and the codebase map. In
  scope for the central model as a whole; out of scope for this effort by the destination above.
- Deleting `templates/`. `#203` closed without removing it, and nothing here depends on its fate.

## Facts I verified (so pm does not re-derive them)

Every anchor in issue #206's body was re-derived at `b6f2c80`. **Most had rotted:**

| #206 says | At `b6f2c80` |
|---|---|
| `harness-init/SKILL.md` is 276 lines | **286** — `wc -l` |
| four anchored regexes at `check-domain.sh:572-575` | moved to **`:650-653`**, still `[^/]+`, still cannot cross a segment |
| CI assertions at `tests.yml:134-141` | that range is now the `check-plan-routes.py` step |
| `deploy.sh` exists | **absent** — `ls` fails |

**Two dependency claims are dead, and one of them changes what the issue is.**

- **`#203` is CLOSED** (2026-08-11). The issue says "#203 deletes `harness-init`, this one rewrites
  it — reconcile before either is picked up." `#203` closed having removed `deploy.sh` and having
  left `templates/` and `harness-init` standing. **There is nothing left to reconcile.**
- **`#205` is CLOSED.** The issue calls it a blocker: "a product's domain globs are meaningless
  until that predicate is decided."
- `#168` and `#189` are both closed. `#189` is still the empty stub the issue describes, and is
  still not prior art.

**Facts about the tree that the issue does not mention:**

- **`mruangutai/kaya-ai` is ALREADY registered in `fleet.yaml`** with `default_branch: master`. The
  new model's step 1 already exists for the one product that has it. What is missing is its config
  and the resolution that reads it.
- `mruangutai/harness` is **deliberately absent** from `repos:`, and the file says why — the absence
  is what keeps harness developing itself in the harness base (DEC-174 am.1). Re-adding it is a
  decision, not a convenience.
- `.harness/products/` **does not exist**. `.harness/` holds `expertise`, `factory`, `features`,
  `harness.json`, `logs`, `members`, `notes`, `README.md`, `team-config.yaml`.
- `templates/examples/harness.kaya-ai.json` exists and is the only onboarded reference. It carries a
  known defect: its `bugfix.always` is `["__bug_class__"]`, a predicate placeholder in no
  `test_kinds`, so kaya's bugfix type can never resolve, and `unit` was dropped from it.
- `.harness/harness.json` has 15 top-level keys, including `github`, `budgets` and `gates` — so
  "product config" is not only the test matrix, and which keys are per-product is part of the fog
  above.

## Fact refresh at `862d270` — read THIS table, not the one above

The artifact instructed a re-check once FEAT-16 landed. It landed (`f01b7b6`). **Four more facts
moved**, and the pattern is the point: this issue's anchors rot about once a week.

| The table above says | At `862d270` |
|---|---|
| four anchored regexes at `check-domain.sh:650-653` | **gone entirely.** FEAT-17 moved the boundary rule out of the embedded Python into `harness_boundary.py`; workspace resolution is now `resolve_fleet` (`:125`) and `select_base` (`:169`), and no `[^/]` anchor survives in either file |
| `templates/examples/harness.kaya-ai.json` | the path is **`.claude/skills/harness/templates/examples/`** — `templates/` at the repo root does not exist |
| `.harness/harness.json` has 15 top-level keys | **16** |
| a `repos:` entry carries `name` and `default_branch` | **`name`, `default_branch`, `board`** — FEAT-16 gave each repository its own board, and a leftover top-level `board:` is now rejected |

**Unchanged and re-measured:** `harness-init/SKILL.md` is 286 lines; `.harness/products/` still does
not exist; `mruangutai/kaya-ai` is still the only `repos:` entry and `mruangutai/harness` is still
deliberately absent; kaya's `bugfix.always` is still `["__bug_class__"]`.

**What FEAT-16 changed for this effort:** the fleet schema is now settled and per-repository, so the
moving target the sequencing section names is stationary. A per-product config file is the second
thing a `repos:` entry points at, alongside the board it already carries.

## Sequencing — SATISFIED. FEAT-16 shipped; this is now plannable

**The condition, and why it existed.** FEAT-16 also edited `fleet.yaml` and `factory_config`. The
operator ruled it builds first, because planning #206 on top of a fleet schema that was about to
change is planning against a moving target — the same reason FEAT-16 itself waited for FEAT-14's
`feature.json` to settle.

**FEAT-16 shipped on 2026-08-12 (`f01b7b6`, 12 of 13 criteria).** The schema is stationary. The
paragraph below is kept as the record of why this artifact sat for a day; it is no longer an
instruction.

~~So: build FEAT-16, then re-read this artifact, then plan #206.~~ Re-check the fleet facts above
before handing them to pm; the whole first half of this section exists because #206's own body was
trusted for five days after it stopped being true.
