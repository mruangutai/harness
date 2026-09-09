# Operator intent of record — GitHub issue #206 (mruangutai/harness)

Filed 2026-08-10. Title: "Rewrite harness-init for the central model: register in fleet.yaml, write
product config centrally". Captured verbatim below by the orchestrator on 2026-09-08 as the
plan-panel's `intent_path`. This is a transcript, not an amendment: nothing here has been edited,
and where the tree has since moved on, the goal-check note records the divergence rather than this
file.

---

`harness-init` is written to run **inside a target project** and write that project's `.harness/`. The operator ruled on 2026-08-09 that harness is the control plane: `team-config.yaml` lives **solely in harness** and is distributed nowhere. The skill has to change address.

## Audit of the nine steps, at HEAD

`.claude/skills/harness-init/SKILL.md` is 276 lines.

| Step | Line | Fate under the central model |
|---|---|---|
| 1. Install the eight prerequisites | :38 | **Dead.** No agent is rooted in a product repo, so it needs no hooks |
| 2. Scaffold `.harness/` from templates | :80 | **Dead.** This is the `cp` at :84-85 that #168 was about |
| 3. Technical interview | :97 | **Re-homes** to `.harness/products/<name>/` |
| 4. `dev-ops` detects `test_kinds.cmd` | :105 | **Re-homes** |
| 5. Seed the domain manifest | :133 | **Re-homes** |
| 6-7. BRIEF, then the approval gate | :154, :164 | **Re-homes** |
| 8. Map the codebase | :179 | **Re-homes.** This is INV-14/19/20's subject |
| 9. Verify and warn about the restart | :211 | **Dead** with 1 and 2 |

Three steps die. Six change where they write. **The skill does not shrink to "add the repo to `fleet.yaml`"** — that becomes its new first step, and the other six still have to produce the knowledge that makes a product buildable.

## What replaces it

Run in the harness repo, against a repo being added:

1. Add the repo to `.harness/factory/fleet.yaml` — `name` and `default_branch`. Verified reversible: `factory_config.repo_entry` returns the whole dict and neither rejects nor strips unknown keys, so relationship-level fields can be added later without a schema bump.
2. Create `.harness/products/<name>/` and write that product's `harness.json`.
3. Run the interview and `dev-ops` detection against a checkout, writing centrally.
4. Map the product's codebase into a per-product location.

## This overturns a planning ruling from the same session

FEAT-10's planning recorded "**No product level in `.harness/`**" as settled, with a measured cost for the alternative: 473 references across 152 files; 40 live and 22 template domain globs that `upgrade-config.py:11-21` refuses to rewrite by design; four anchored regexes at `check-domain.sh:572-575` whose `[^/]+` cannot cross a path segment; CI assertions at `tests.yml:134-141`; and no layout-migration machinery. It also cited DEC-95 — "`.harness/` is per-worktree state, not per-repository state."

**The operator has overturned that ruling.** Those costs are now the work, not an argument against it. They are listed here so nobody re-derives them.

## The conflict this resolves

DEC-187 was signed on 2026-08-09: the test matrix is **per-project**, and a kind with no runner is excluded by decision. That requires a per-product config. Today there is one `.harness/harness.json`, describing this repo, whose matrix excludes `functional` because this repo has no service surface. Point the factory at a product with a real API and it inherits that exclusion silently. `.harness/products/<name>/harness.json` is what makes DEC-187 true rather than aspirational.

## Dependencies and related

- **#205** — factory worker writes to `workspace_root` are ungoverned. A product's domain globs are meaningless until that predicate is decided.
- **#203** — removes `deploy.sh`, `templates/` and (as scoped) `harness-init`. **These two issues disagree**: this one rewrites `harness-init`, #203 deletes it. Reconcile before either is picked up.
- **#168** — closed as unreachable on the assumption that onboarding is dead. If the rewrite happens, the template's parse error at line 28 may become live again depending on what the new scaffold copies.
- **#189** — cited during planning as settling per-product `.harness/`. It is **closed with an empty body** (the stub `<the decision this resolves>`). Nothing was recorded there; do not treat it as prior art.
