# Research — FEAT-15 — domain enforcement across two roots

**BLUF.** The fix is buildable, the seam for testing it already exists, and one thing blocks
signature: under prefix inference there is **no way to express harness's own `docs/**`,
`README.md` or `.github/**`**, so the fix revokes live routes and turns a required CI check red.
That is Q1, and only the operator can settle it.

Measured at `06ae963` unless stated.

---

## 1. Issue #239, first comment — the operator's revised scope, transcribed verbatim

> **Revised scope, replacing the three items in the body:**
>
> 1. `check-domain.sh` learns a SECOND base: `workspace_root` from `.harness/factory/fleet.yaml`. A
>    target under `<workspace_root>/<repo>/` is made relative to that repo root and matched against the
>    product-shaped globs.
> 2. Outside-root becomes a decision, not a silent return, for paths under a known product workspace.
>    `/tmp` and anything outside both bases keep today's no-verdict behaviour — the reasoning in that
>    comment is sound and `bash-write-guard.sh:211` agrees.
> 3. Domain entries carry which base they resolve against, so `.harness/**` never accidentally matches
>    inside a product checkout and `src/**` never accidentally matches inside harness.
>
> Item 3 is what stops the fix from creating the mirror-image bug. Harness has its own `src/` and
> `docs/`, which is the ONLY reason the product globs appear to work today.

The same comment also states the architecture (harness is the control plane and the only place agents
run; product repos carry no harness; the factory clones into `workspace_root/<repo>` and lands
remotely), downgrades root cause 3 to not-a-defect, and records that `workspace_root` was briefly set
to `/Users/molchairuangutai/GitHub` and reverted. The second comment splits the
`factory_workspace` refusal guard out as #240.

---

## 2. Glob ownership — the operator's enumeration confirmed, and it is exactly two personas

Every product-shaped glob in `.harness/team-config.yaml`, with its owner:

| glob | owner | live files in the harness repo? |
|---|---|---|
| `docs/**` | harness-documentor | **yes** |
| `README.md` | harness-documentor | **yes** |
| `.github/**` | harness-dev-ops | **yes** |
| `Dockerfile` | harness-dev-ops | no |
| `src/**` | harness-backend-dev | no |
| `src/**/prompts/**`, `evals/**` | harness-ai-dev | no |
| `src/**/schema*`, `supabase/migrations/**` | harness-data-engineer | no |
| `web/src/**` | harness-frontend-dev | no |
| `tests/**`, `web/src/**/*.test.*` | harness-qa | no |

Only documentor and dev-ops have a live harness-repo file reachable **only** through a
product-shaped glob. backend-dev and dev-ops keep `.claude/skills/harness/bin/**` (a `.claude/`
prefix, so control-plane), which is how this repo's source is actually written; qa's harness tests
live in that same bin directory. **The operator's finding is correct and complete.**

## 3. The crux — expressibility. Verdict: NOT expressible, and it has live teeth

Under ruling 1 the base is selected by the glob's own prefix, and the control-plane prefixes are
exactly `.harness/` and `.claude/`. Harness's own docs live at `docs/`, its readme at `README.md`,
its CI at `.github/`. None of those can be written with a control-plane prefix, and no per-entry tag
is available (declined). **There is therefore no manifest entry that says "harness's own `docs/**`".**

This is not theoretical. `check-plan-routes.py` resolves task routes through
`check-domain.sh --resolve`, and at `06ae963` it reports, over live (non-shipped) plans:

- FEAT-12 (BUILDING) T-12 `README.md`, `docs/harness/SPEC.md`, `docs/harness/BUILD.md`; T-14
  three `docs/harness/*.md` — both `execution_mode: team`, granted to harness-documentor.
- FEAT-14 (planning) T-09, T-10 — four more `docs/harness/*` paths, same shape.
- FEAT-10 T-09 likewise.

If the resolver adopts prefix inference, each of those flips from `OK ... granted to
harness-documentor` to `VIOLATION ... ungranted (NOBODY)`, the checker exits non-zero, and the
`integration` CI job — a **required check on `main`** (DEC-183) — goes red while FEAT-12 is mid-build.
Leaving the resolver alone instead is worse: the plan checker would keep saying documentor owns
`docs/**` while the hook blocks it at build time, which is the exact failure the checker exists to
prevent.

**Recommendation (Q1, blocking, operator's call — ruling 1 is not re-opened here).** Extend the
*inference rule*, not the schema: treat a glob written with an explicit `harness:` prefix
(`harness:docs/**`) as control-plane, and add three such entries — `harness:docs/**` and
`harness:README.md` for documentor, `harness:.github/**` for dev-ops. It keeps the base inferred from
the prefix, costs three entries rather than 84, and no future entry has to remember a tag. The
alternative — accept the revocation — moves every harness doc and CI edit into the main session.

## 4. Testability seam — it EXISTS. No task needed to create it

- `check-domain.sh` takes `root` from `CLAUDE_PROJECT_DIR` when `.harness/team-config.yaml` is
  readable under it; `test-check-domain.py`'s `fixture()`/`fire()` already build such a root in a
  tempdir and pass it through the environment. A fixture root can therefore carry its own
  `.harness/factory/fleet.yaml` declaring a repo whose name is **not** `harness` (e.g. `acme/widget`)
  and a `workspace_root` in the same tempdir. Nothing has to exist on disk for the base comparison —
  the branch is a path comparison, not a stat.
- **The import-time trap is real and confirmed.** With `CLAUDE_PROJECT_DIR=/tmp/fakeroot239`,
  `import factory_config` prints `factory_config: CLAUDE_PROJECT_DIR=... has no readable
  docs/harness/SPEC.md — IGNORING it and using /Users/molchairuangutai/GitHub/harness` and sets
  `FLEET_PATH` to the **live** repo's fleet. Two consequences the plan handles: the hook must never
  read `factory_config.FLEET_PATH` (it must pass `<root>/.harness/factory/fleet.yaml` explicitly),
  and the import must be lazy with its stderr captured, or the notice reaches the agent on every
  governed write from a fixture root.
- `workspace_path()` is called, never restated: `factory_config.workspace_path(fleet, name)` for each
  `fleet["repos"][].name`.
- `test-check-domain.py` is already registered in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS`, so no
  new file and no new registration (G-08 does not fire).

## 5. Fail-closed repair path — confirmed, no deadlock

`.claude/skills/harness/bin/check-domain.sh --resolve .harness/factory/fleet.yaml` prints `NOBODY`
at `06ae963`. The fleet declaration is in no agent's domain, and the main session is exempt from the
domain phase — the same reasoning the existing unparseable-manifest branch states for
`team-config.yaml`. So the only party who can repair a broken fleet is the one this guard never
governs. DEC-171's one-session bootstrap escape is **not** the mechanism here: it covers a missing
PyYAML, not a malformed file, and it must not be spent on this.

## 6. Absent vs unparseable — the distinction needs code, not luck

`harness_yaml.load_file` wraps `OSError` into `YamlParseError`, so a **missing** fleet raises the same
exception class as a corrupt one. Without an explicit existence test first, "absent" silently becomes
fail-closed and every project without a factory is bricked. Assert both halves in one paired fixture,
the shape the existing `SC-05 pair` case uses.

## 7. Where the fleet is read — once per hook invocation, before the outside-root branch

Ruling 3 says an unparseable fleet fails closed on **every** write, including writes inside `root`.
A read gated on "this target looks like a workspace path" satisfies the letter of the workspace case
and violates the ruling. So: one read, at the top of the domain check, before the `commonpath`
branch and before any glob match. Per-invocation, not per candidate path (the worktree strip yields
up to two candidates from one target).

## 8. Baselines, recorded with their sha and condition

- `python3 .claude/skills/harness/bin/test-check-domain.py` → exit 0, "32/32 post-mode cases passed"
  at `06ae963`, working tree as found.
- `python3 .claude/skills/harness/bin/check-plan-routes.py` (no args, all live plans) → **exit 0** at
  `06ae963`. `DEVIATION` lines do not increment the violation counter; only `VIOLATION` does.
- `check-domain.sh --resolve .claude/skills/harness/bin/check-domain.sh` → `harness-backend-dev`,
  `harness-dev-ops`. Both carve-out files are granted, so a `main-session-direct` task naming them
  draws `DEVIATION`, exit 0 — not `VIOLATION`. The marker stays.
- `check-plan-routes.py` on this feature's own `plan.yaml` → five `DEVIATION` lines,
  `0 violation(s)`, **exit 0**, every carve-out marker intact.
- `check-state.sh` → **exit 1 at `06ae963`, BRIEF pending, `feature.yaml` absent (the
  orchestrator's file, not pm's)**. Both findings are expected at this phase.

## 10. What prefix inference does to the existing suite — measured, not counted by grep

All eight entries under `shared:` in `.harness/team-config.yaml` — `package.json`,
`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `pyproject.toml`, `uv.lock`,
`requirements.txt`, `tsconfig.json` — carry no control-plane prefix, so prefix inference makes every
one of them product-only. In the harness repo they stop being serialized-allow and become refusals.
**None of those eight files exists in this repo** (checked with `ls`), so the consequence is latent
rather than live — but `test-check-domain.py`'s case asserting `<ROOT>/package.json` exits 0 flips to
2. It is the same inexpressibility as Q1 wearing different clothes.

**How the affected set was enumerated (cycle 1 correction).** A grep of `test-check-domain.py` for
product-shaped path fragments is the wrong instrument and under-counts: whether a case flips depends
on the **glob that grants it**, which lives in a manifest, not in the test's path literal —
`allowed/thing.md` contains no product-shaped fragment and flips anyway. The measurement instead
resolves, for every in-root assertion that expects an allow, which manifest glob grants it today and
whether that glob's first segment is `.harness` or `.claude`. Two manifests only: the live
`.harness/team-config.yaml` and the file's `FIXTURE_MANIFEST`. The search set is finite and provably
complete because in-root the applicable set narrows from `globs` to `cp_globs ⊆ globs`: narrowing is
monotone, so the only possible in-root flip is `0 → 2`, and no case expecting a refusal can flip.

Result, measured at `96d5d5c` (script: reuse of `check-domain.sh`'s own `glob_to_re`/`matches` over
`harness_yaml.manifest_domains`) — **five** in-root allow assertions lose their grant:

| assertion | granted today by | disposition |
|---|---|---|
| `documentor writing docs/` (live) | `docs/**` | expectation changes to 2 |
| `a shared path is allowed and serialized` (live, `package.json`) | `shared: package.json` | expectation changes to 2 |
| `(h) no --resolve: an in-domain Write still exits 0` (live, `docs/harness/SPEC.md`) | `docs/**` | **path changes** to `.harness/README.md`, expectation stays 0 |
| `SC-05 pair: permitted allowed AND forbidden blocked, one manifest` (fixture) | `allowed/**` | **path changes** to `.harness/allowed/thing.md`, expectation stays 0 |
| `the marker self-unlinks once PyYAML imports again` (fixture) | `allowed/**` | **path changes** to `.harness/allowed/d.md`, expectation stays 0 |

The last three are each one half of a deliberate pair — an allow asserted beside a refusal. Flipping
the allow makes both halves assert 2, which a block-all guard passes, destroying exactly the
discriminating power SC-01/SC-02/SC-03 are built on. So the repair is the path, never the
expectation, and `FIXTURE_MANIFEST` gains one control-plane entry (`.harness/allowed/**`) in T-01 to
grant the two fixture paths.

Three adjacent hazards were checked and are clear. (1) The bootstrap-grant cases (`fire_noyaml`,
`allowed/a.md` and friends) never reach the partition: `check-domain.sh` calls `domain_check()` under
`if _run_domain and not _no_parser`. (2) The `--resolve` cases (a), (b) and (c) are all granted by
control-plane globs (`.harness/harness.json` → `harness-dev-ops`;
`.claude/skills/harness/bin/**` → `harness-backend-dev` and `harness-dev-ops`;
`.claude/skills/harness-spec-driven/SKILL.md` → nobody), so their agent counts are unchanged.
(3) Every post-mode case is either `.harness/`-prefixed or fired without an `agent_type`, and the
domain phase is `_governed and not _post`, so none of them is governed by this change.

A sixth site is created by this plan rather than found in the tree: T-01's new case (a), the
no-fleet-file allow. It is authored on `.harness/allowed/x.md` from the start, because written on
`allowed/x.md` it would pass at T-01 and collapse the (a)/(b) pair at T-02.

## 9. Grammar note — the carve-out marker in plan.yaml

The dispatch specifies the marker as `execution_mode: main-session-direct — reason: carve-out (...)`,
which is FEAT-07's pre-DEC-182 markdown grammar. In a `plan.yaml` that string is unloadable: a plain
scalar with a second `": "` fails `safe_load`, and `harness_yaml.load_plan` requires
`execution_mode` to be one of two bare tokens. The marker is therefore rendered as the two sibling
keys the template mandates, with the reason preserved word for word:

```
execution_mode: main-session-direct
execution_reason: carve-out (check-domain.sh is named in CLAUDE.md's DEC-174 list)
```

## Open questions

- **Q1 (blocking).** Section 3. Harness's own `docs/**`, `README.md` and `.github/**` are
  inexpressible under prefix inference; the fix revokes documentor's and dev-ops's routes to live
  files and turns a required CI check red. Operator's call before signature.
- **Q2 (not blocking).** `harness.json`'s `unit` detect glob (`...bin/test-*.py`) claims
  `test-check-domain.py`, but `run-unit-tests.sh` runs it from `INTEGRATION_SCRIPTS`. Every SC here
  names `evidence: integration`, which is the bucket that actually executes it. The detect/runner
  disagreement is pre-existing and belongs in the backlog.
- **Q3 (not blocking).** `bash-write-guard.sh` has its own outside-repo rule and is untouched here,
  so a Bash-route write into a product checkout stays ungoverned after this fix. Out of scope by the
  grilling; worth a ticket.
