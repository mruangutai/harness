# Grilling — #206, harness-init for the central model — 2026-08-12

Run in the main session. The output is decisions, not a plan: the operator ruled that FEAT-16 builds
first, so **pm is not to be handed this yet** (see `## Sequencing`).

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

## Sequencing — why this does NOT go to pm yet

**FEAT-16 (signed, idle, eleven tasks, architecture review PASS) also edits `fleet.yaml` and
`factory_config`.** The operator ruled it builds first. Planning #206 on top of a fleet schema that
is about to change is planning against a moving target — the same reason FEAT-16 itself waited for
FEAT-14's `feature.json` to settle.

**So: build FEAT-16, then re-read this artifact, then plan #206.** Re-check the fleet facts above
before handing them to pm; the whole first half of this section exists because #206's own body was
trusted for five days after it stopped being true.
