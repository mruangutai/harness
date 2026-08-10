# Grilling — end copy-based distribution (issue #203) — 2026-08-10

## Destination

`deploy.sh` and every copy it made are gone. This repo is the only place harness tooling exists,
and a product repo reaches it by being checked out by the factory — never by holding a copy of it.

## Settled

- **The global install is deleted — already done, ahead of this ticket.** 21 skills, 16 agents and
  8 commands removed from `~/.claude/` on 2026-08-10. Backups at
  `~/.harness/global-harness-skills-backup-2026-08-10.tgz` and
  `~/.harness/global-harness-agents-commands-backup-2026-08-10.tgz`. What remains for the ticket is
  `deploy.sh` itself, kaya, and the reference sweep.
- **Delete `deploy.sh` and its tests.**
- **Delete `~/.harness/registry.json`** with its only writer. Verified zero readers.
- **Delete `kaya-ai/.claude/skills/harness*/`** — 21 directories including a 37-file `bin/`.
- **KEEP `kaya-ai/.harness/expertise/`, `codebase/` and `features/`.** Operator ruling. They are the
  only record of what the factory learned on kaya, they are not reproducible, and `deploy.sh` never
  wrote them. They move to a permanent central location later, as separate work. Also keep
  `harness.json` and `team-config.yaml` — project config, never distributed.
- **Add `mruangutai/kaya-ai` to `fleet.yaml`** with `default_branch: master`. Without it kaya
  appears in no list at all once the registry is gone.
- **Kaya is worked on only through the factory.** Sessions opened directly in `~/GitHub/kaya-ai`
  will have no harness tooling, and that is the intended end state of ending distribution. Symlinks
  were rejected: a per-repo install step is a thinner `deploy.sh`, not an alternative to it.
- **#203 lands BEFORE #206.** Both rewrite `harness-init`; #203 clears the dead distribution surface
  first so #206 starts from a smaller file.
- **Sweep the stale references:** `.claude/commands/harness-deploy.md`, `README.md:80` and `:94`
  (both still document `~/.gsd/harness-registry.json`), and `harness-init/SKILL.md`, which copies
  the `team-config.yaml` template.

## Not yet specified

- Where kaya's `expertise/`, `codebase/` and `features/` eventually live. The constitution
  (`docs/principles.md`, rule 1) puts them in a central store keyed by project and seat; nothing has
  decided the concrete layout, and this ticket deliberately does not.

## Out of scope

- Moving kaya's accumulated knowledge anywhere. Deferred by operator ruling.
- Anything `harness-init` does beyond the reference sweep — that is #206.
- Deleting kaya's `.harness/` state of any kind.

## Facts I verified (so pm does not re-derive them)

At `aa18302`, on 2026-08-10.

- `deploy.sh` ships **three** things, not one: skills, agents and slash commands. The command half
  is deliberate — DEC-161, after kaya ran three features on free-form prompts because `/harness*`
  was never shipped. Derivation is at `deploy.sh:52-60`.
- **`~/.harness/registry.json` has zero readers.** `deploy.sh:46` writes it; no code consults it.
  `check-plan-routes.py:457` only *mentions* it in a comment explaining why the probe must be a
  filename — the real probe is `team-config.yaml` at `:468`.
- **`registry.json` and `fleet.yaml` are disjoint.** The registry holds one local path
  (`/Users/molchairuangutai/GitHub/kaya-ai`); the fleet holds one GitHub slug
  (`mruangutai/harness`). Different key types, no entry in common. The fleet does not absorb the
  registry by default.
- **kaya's remote is `mruangutai/kaya-ai` and its default branch is `master`**, not `main`.
- kaya carries **21** `harness*` skill directories and a **37**-file `harness/bin/`.
- The global copy was **stale, not merely redundant**, which is this ticket's argument demonstrated:
  `harness-wayfinding` and `harness-grilling` were last written Jul 31, while the repo changed them
  on 2026-08-09 in `c5597be`. The global text lacked the one-door-per-job framing for ten days and
  nobody noticed until it was diffed.
- The global `bin/` never held any `factory_*.py`, so the factory has never run outside this repo.
