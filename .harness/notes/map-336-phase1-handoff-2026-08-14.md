# Phase 1 hand-off — map #336, snapshot 2026-08-14

Grilling artifact for the plan flow (DEC-164/165). Source of truth: issues #336, #339, #344, #356.

## Map #336 body (frontier empty, 18/18 resolved)

## Destination

**One repository is fully operable from harness, and the layout supports N of them.** Both, not one
then the other — the operator ruled that explicitly after being offered the split.

Concretely: point the factory at `mruangutai/kaya-ai` and it works end to end — kaya's cards move on
board 2, qa applies kaya's test matrix, agents carry kaya's expertise, and kaya's features live under
its own path — while every control-plane file stays in harness. **A criterion proves it against the
real repository, not a fake `gh`.** And `.harness/<repo>/` scopes features, expertise, codebase,
notes and docs, with harness itself one repository among them.

## Notes

**This map was PROMOTED, not charted cold.** It began as `/harness-plan` on issue #206, which
produced FEAT-19 — a planned, reviewed, **unsigned** BRIEF and `plan.yaml`. During the operator's
review pass the scope grew five times in one sitting, then a grilling was opened and itself outgrew
one sitting. Nothing was dispatched on the revision; nothing was signed.

**The two stores the settled decisions live in — this map indexes them, never copies them:**

- `.harness/features/FEAT-19-central-product-config/notes/answers-2026-08-13-revision.md` — ten
  answers, A-01..A-10, marked SUPERSEDED-as-instruction but VALID-as-record.
- `.harness/notes/grilling-central-product-config-2026-08-12.md` — the original grilling. **Its
  destination sentence is now FALSE** ("nothing else about onboarding moves in this effort"). Read it
  for facts, not for scope.

**Measured surfaces at `63b83c7`, so no ticket re-derives them:**

| Surface | Size |
|---|---|
| `.harness/features` references | 1499 across 284 files; **206 in code/config** |
| `docs/harness` references | 620 across 161 files |
| `FEAT-NN` citations outside any repo folder | **352** — logs 242, DECISIONS.md 91, SPEC 12, BUILD 6, index 1 |
| Expertise files holding both layers mixed | 10 |

**Three of the four DEC-174 carve-out scripts are in the docs-migration surface** —
`check-domain.sh`, `check-state.sh`, plus `harness_boundary.py`, which DEC-193 names as the one
shared rule. Every one of those edits is main-session-direct by rule.

## Decisions so far

Carried in from the two stores above. Each is settled; none is a ticket.

- **Destination is BOTH** — one repo operable AND the layout for N. Operator overruled the split.
- **A-01/A-02** — the Goal covers the board and the issue mirror, not the test matrix alone. D-06
  takes option B. `gh-sync.py` resolves repo and board through `factory_config`, which already
  exposes `board_for` and `board_station` and is already used by three factory tools.
- **A-03** — harness keeps reading its own `harness.json`. That is D-01, not an inconsistency.
- **A-04 FLIPPED** — a live kaya run is now IN scope, as the only thing that can prove the
  destination.
- **A-05/A-10** — expertise moves to `.harness/<repo>/expertise/<agent>.md` in **two layers**: craft
  carries across repositories, repository facts do not.
- **A-06** — T-04 corrects all four false rows in `.harness/README.md`.
- **A-07** — the layout gains a repository level: `.harness/<repo>/features/<FEAT>/`. Chosen over
  `features/<product>/` because one segment at the top scopes four things, not one. **The forced
  constraint: writes are granted by GLOB, and a glob cannot read `feature.json`'s `factory.repo`
  field — so per-product write isolation is only reachable through the path.**
- **A-08** — harness gets a real `fleet.yaml` entry, AND the stale-checkout diagnostic gets its own
  signal. Re-measured at `63b83c7`, probe reverted byte-identical: absent → `BLOCKED … belongs to no
  repository declared in fleet.yaml`; present → `NOBODY`. The loss is **diagnosis, not permission**.
  DEC-174 am.1 is amended, not struck.
- **A-09** — budget raised to fit the re-scoped work; the five spent cycles are NOT reset.
- **Segment rule** — reuse `factory_config.workspace_path`'s rule: the name after the owner, so
  `mruangutai/kaya-ai` → `kaya-ai`. It is the one place that derivation lives and the checkout
  already uses it.
- **The 18 existing features all move.** One shape, no exception.
- **`codebase/` and `notes/` go per repository. `logs/` stays global.** `members/` is deleted —
  legacy FEAT-02 files, absent from the layout table.
- **Docs move to `.harness/<repo>/docs/`** — `DECISIONS.md`, `DECISIONS-INDEX.md`, `SPEC.md`,
  `BUILD.md`. **`docs/PRINCIPLES.md` stays global** as the craft layer, by the same rule as
  expertise.

- **ONE ISSUE WRITER — REVERSED, 2026-08-14 (#349).** The consolidation of `gh-sync.py` and
  `factory_decompose.py` is NOT happening: #348's own resolution showed the merge requires
  `mruangutai/harness` in `fleet.yaml` or an INV-24 rewrite, the fleet ruling went the other way,
  and the rewrite was declined. **The two writers stay separate, each with its own exit contract.**
  DEC-186 D-12's two-issues-per-task hazard IS fenced by keeping harness out of `fleet.yaml`,
  pinned by the absence test. The one real survivor — INV-26's mirror-never-ran clause falsely
  firing on factory-published features — is fixed in PR #359.
- **FOLD `fleet.yaml` INTO `harness.json`** (operator, 2026-08-14). One config record per repository,
  one writer, `workspace_root` the candidate for the only global key. Research #347.
- **Either placement is acceptable for a product's config** (operator, 2026-08-14): read from the
  product's own checkout, or `.harness/products/<name>/harness.json` centrally in harness. The
  decision is open and #347 must report the trade honestly rather than assume the central one.

- **PLACEMENT: CENTRAL** (operator, 2026-08-14). A product's config lives at
  `.harness/products/<name>/harness.json` inside harness, not in the product's own checkout.
  Clone-independent, and it resolves to `NOBODY` so only the main session can author it. **Cost
  accepted and recorded: no `upgrade-config.py` path, so a product config will drift from the
  template.**
- **FORCED, not chosen — `repos[].name` and `workspace_root` CANNOT move** (research #347).
  `harness_boundary.resolve_fleet` computes a base for every declared repo before it can classify any
  path, including **uncloned** repos, and nothing is cloned today. `fleet.yaml` survives as the fleet
  declaration whatever #350 decides. Only the board and the test config were ever movable.
- **One writer is COUPLED to A-08, not merely compatible** (research #348) — and that coupling is
  what killed it when A-08 reversed: see the ONE ISSUE WRITER reversal above. INV-26's lane-blind
  clause got its own fix instead (PR #359).

- **NO VALUE APPEARS IN BOTH FILES** (operator, 2026-08-14). `fleet.yaml` and `harness.json` are each
  domain-specific to their own responsibility. This is the rule the rest of the config decisions
  derive from, and it replaced the "fold everything into one file" framing.
  - **`fleet.yaml` = the fleet declaration** — which repositories the factory serves and where
    checkouts go: `repos[].name` and `workspace_root`, nothing else.
  - **`harness.json` = that repository's own configuration** — `board`, `test_matrix`, `test_kinds`,
    `github.sync`/`repo`, `gates`, `budgets`, and `default_branch`.
  - `default_branch` moving is BEYOND the original fold proposal. It looked immovable because
    `factory_claim` and `factory_land` read it before any clone exists — but central placement makes
    it readable without a clone, so the line is responsibility, not availability.
- **Every board declares its stations** (#350). Harness's hidden DEC-192 default goes, and
  `gh_board.derive_station`'s hardcoded `"Building"`/`"Review"` literals go with it.
- **An incomplete board config is a LOUD error, not a mode** (#350). `load_board`'s silent `None` —
  station writes skipped, INV-26 vacuous, nothing said — is removed. Keeping it would reintroduce the
  class FEAT-18 exists to remove.
- **FEAT-19 D-04 is REVERSED deliberately** (#350), and by its own reasoning: it objected to one board
  declared in two files with nothing checking agreement. That is answered by having one declaration,
  not by preserving the split.

- **A-07's JUSTIFICATION IS UNFINISHED — do not cite it as settled** (operator challenge,
  2026-08-14). A-07 argued the repository must be in the path because "writes are granted by GLOB and
  a glob cannot read `feature.json`'s `factory.repo` field, so per-product write isolation is only
  reachable through the path." **That is true but insufficient.** The path makes isolation possible;
  delivering it also needs the GRANT to name the repository — and #346 ruled `team-config.yaml`
  forced global. One global file gives one grant set per agent, so each becomes either
  `.harness/*/features/**`, which isolates nothing, or a hardcoded repo that grows a line per
  repository forever in a hand-edited shared file. **`harness_boundary.glob_to_re` supports only
  `**`, `*`, `?` and literals — no placeholder, no variable**, so `.harness/${repo}/features/**` is
  not expressible. Research #351. **The layout still buys locality, per-repo config resolution,
  expertise and the codebase map; it does not buy write isolation on its own.**

- **PER-REPOSITORY WRITE ISOLATION IS BUILDABLE — measured 2026-08-14, #351.** The write guard
  receives **`agent_id`**: distinct per agent (`a7a524467978f772e` vs `ad05adbb7f8d6eb5d` on two
  concurrent agents), stable across that agent's fires, present in BOTH `SubagentStart` and
  `PreToolUse`, and **identical to the id the `Agent` tool returns to the spawner**. So the channel
  is complete end to end. Record `agent_id -> repo` at spawn; the guard extracts the repo segment
  from the target path, which `classify` already computes as part of `rel`. **This closes A-07's
  unfinished justification.** Failure must be loud: an `agent_id` with no recorded repo exits 2.
- **`session_id` and `cwd` are NOT usable, measured.** `session_id` is identical for every agent (the
  main session). `cwd` was the harness root for both agents, so it identifies no product;
  position-derivation answers "which checkout is this session rooted in", which in the observed shape
  is always harness. `prompt_id` is shared across concurrent agents in one turn.
- **A RECORDED MEASUREMENT IN THIS TREE IS STALE, and nothing detected it** (#351).
  `FEAT-05/notes/receipt-main-session-q4-session-identity.md` records the PreToolUse payload as three
  keys with `session_id=None`, measured over 21 fires and corroborated twice. **At HEAD it carries
  twelve, including `agent_id`, `cwd`, `session_id` and `transcript_path`.** The runtime changed
  under a recorded fact. This is the #247 defect class reached through a receipt rather than prose,
  and it is the second instance found today.

- **SALVAGED FROM FEAT-19, which is retired unbuilt** (#338). Four of its six decisions are dead;
  these two survive on their own evidence and are carried here so no planner reopens them:
  - **D-03 — kaya's test kinds ship `unresolved`, and DEC-187 closure is enforced at the first
    factory run, not signed at approval.** Nobody has run kaya's commands from here, so marking any
    kind `active` would be the unverified claim DEC-187 exists to stop.
  - **D-07 — the config resolver's flag is `--which-config`, never `--resolve`.**
    `check-domain.sh --resolve` already answers a DIFFERENT question in a DIFFERENT shape — which
    agent owns a path, as plain text including the literal `NOBODY`. A second `--resolve` returning
    JSON about which config applies is a homonym.
  - Also carried: the engineering-review finding that **`load_fleet()` called with no argument reads
    the live repo's `fleet.yaml`, because `FLEET_PATH` binds at import** — so every fixture test
    written that way passes for the wrong reason. It applies to any new caller.
- **`Abandoned` is a status now** (#338). The enum had no terminal state for a feature planned and
  never built; all 18 features on disk were `Done`. Added to `feature-schema.json` and to the four
  places terminality is tested. It is terminal like `Done`, but asserts **no seam was crossed** — so
  no handoff notes, and its BRIEF need never be approved. FEAT-19 is the first.

- **RULED by the operator, 2026-08-14 (#355): HARNESS IS NOT FACTORY-DEVELOPED, AND IS NOT IN
  `fleet.yaml`.** Harness develops itself as it does today — main session, live checkout, DEC-174 by
  hand. **A claimable ruling was made earlier the same day and REVERSED within the hour**, once the
  cost ledger was priced; see #355 for both. Operator: *"moving harness to factory seems like more
  trouble than it's worth."*
  - **The reason is cost, not principle.** Claimable bought consistency, not capability — the
    factory's one unique offer is the atomic claim, which pays only with several agents on a shared
    queue, and harness has none. Against it: #357 (28,462 lines across 290 files, or a
    `select_base` change sanctioning a third unwatched checkout), #358's five items, a staleness
    contract, DEC-174 am.3, a DEC-193 amendment, and inverting an absence test.
  - **Nothing changes in the tree.** `fleet.yaml` is unchanged with its absence comment intact,
    `test-no-distribution.py case3_absence_harness_is_not_a_fleet_member` keeps passing, **DEC-174
    am.1 and DEC-193 stand unamended** — am.1's own reversal condition (*"if harness ever wants
    factory-style parallel dispatch"*) has not been met, so nothing is struck. **The fleet list does
    not split**; it keeps meaning one thing because harness is not on it.
  - **#357 and #358 close unbuilt.** Their measurements stay on those tickets.
  - **Accepted cost, stated rather than argued away: the merged issue ledger (#348) loses its
    route.** INV-24 hard-violates without a fleet-declared repo, so one ledger across `gh-sync.py`
    and `factory_decompose.py` required `mruangutai/harness` in `fleet.yaml`. Consolidation either
    finds another way to satisfy INV-24 or does not happen. **This supersedes the coupling recorded
    above under research #348.**
  - **Survives and is NOT closed: #356** (a factory worker cannot write its own receipt or
    observation — product-independent, required before the factory's first real run) and **#218**
    (`harness-qa` cannot author a test here; #357 would have closed it as a side effect and now
    does not).


  - **The fleet list means two things today**: repositories harness knows about, and repositories
    the factory may claim. Claim and workspace read the same list, which is why one entry granted
    both. **They are two different facts and are split.**
  - Candidate: harness IS on the roster — so the merged ledger satisfies INV-24 with no exception, and
    harness is described exactly like every other repository. That is where consistency pays:
    `harness.json`, board, test matrix, expertise layers, `.harness/<repo>/` are all statements
    ABOUT a repository, and harness is one.
  - Candidate: harness is NOT claimable. The factory is the mechanism by which the control plane acts on a
    product; harness going through it is the control plane treating itself as its own object.
  - **The tree already drew this line three times, on evidence:** DEC-174 carves out the four gate
    scripts because green gates cannot vouch for the code producing them; `.claude/agents/**` is
    deliberately unowned because an agent editing agent definitions is self-modification; DEC-193
    fixes where harness may write itself and the factory workspace is not among them. This is **one
    rule applied twice**, not a fourth exception.
  - IF taken, DEC-193 would stand unamended — two locations, no third. The stale-checkout
    diagnostic survives intact for genuinely undeclared checkouts. The harness-base-anywhere rule
    explored under #345 is **not built** — it was the answer to a problem this split removes.
  - **Measured while deciding:** neither lane is in use. `.claude/worktrees/` does not exist,
    `git worktree list` shows one checkout, no feature carries a factory block. The factory's one
    unique offer is the atomic claim (`factory_claim.py:353` — the server's `create_ref` return
    decides ownership), which is worth having only with several agents pulling from a shared queue.
    Harness has no such concurrency today.
  - **Open for whoever builds it:** how claimability is expressed, and every factory tool honouring
    it. Miss one and the hole reopens silently.

**Two corrections the main session made while recording these, both verified:**

- **`.harness/harness.json` is per repository, and each lives IN ITS OWN REPO** — kaya's is on kaya's
  `master`, not inside harness. That is a DIFFERENT design from FEAT-19's central
  `.harness/products/<name>/`. The tree already has the first.
- **Kaya's own `harness.json` is PRE-FEAT-18 and stale.** It pins `project_id`, `status_field` and
  `in_progress_option` — the exact flat keys D-05 killed, because a wrong pinned id does nothing at
  all, silently. `fleet.yaml`'s kaya entry is the modern by-name shape. **The two records are not
  near-identical; one is current and one is stale.** Any consolidation lands on the by-name shape.

## Not yet specified

- How much of this lands as one release versus a sequence, and in what order. The migrations are
  independently breaking and nothing has been said about which goes first.
- What "operable" covers beyond board, tests, config and expertise — the operator's phrase was
  "operate whatever is necessary in that repo", which is wider than anything enumerated here.
- Whether a second product would surface a rule this map settles for one.

## Out of scope

- Re-homing the onboarding interview, `dev-ops` detection, domain seeding and the BRIEF. In scope
  for the central model as a whole; past this destination.
- Deleting `templates/`.
- Cloning, running or testing kaya's own **code**. The live proof exercises the factory against kaya,
  not kaya's test suite.





## #339 resolution (release shape) — as amended 2026-08-14

## Resolution — a detector first, then a sequence of features under this effort.

### The shape

**Unit 0 — the migration detector — lands BEFORE anything moves.** `#344` established that no
mechanism in the tree can detect a partial migration: `check-state.sh`'s fourteen discovery globs
return nothing and it reports a healthy tree, while CI's plan-route guard is defeated by exactly the
shape a repo segment produces (`examined > 0, plans == 0`, a case its own comment names as uncaught).
So every intermediate state in any sequence would hide its own mistakes.

The detector must **fail loud on a half-migrated tree** and be **proven able to redden by
perturbation before it lands**. A check that cannot fail is issue #148, already open on this board,
and shipping one here would be the same defect inside the fix for it.

### The sequence, in dependency order

| | Unit | Depends on |
|---|---|---|
| 0 | **The migration detector** | — |
| 1 | A-08 fleet entry + replacement stale-checkout signal (#345) | — |
| 2 | One issue writer (#348, #349) | **1** — INV-24 needs a fleet-declared `repo` |
| 3 | Layout migration: features into `.harness/<repo>/` | **0** |
| 4 | Docs migration into `.harness/<repo>/docs/` | **0** |
| 5 | Config split: board and `default_branch` into `harness.json` (#350) | **3** |
| 6 | Expertise re-home + craft/repo split (#340) | **3** |
| 7 | Repo-aware write grants via `agent_id` (#351) | **3, 5** |
| 8 | Live kaya proof | **5**, ideally **2** |
| 9 | Small independents — `gh-sync.py:729`, `branch-create-gate.sh:77`, `validate-feature-json.py`, `factory_claim.py:43`, gitignore, prose | anytime |

### Two constraints that hold whatever order is chosen

**Unit 3 is ONE COMMIT.** The grants in `team-config.yaml`, `check-domain.sh`'s four shape regexes
and its `SWEEP_GLOBS`, `check-plan-routes.py`'s discovery, and the physical move are mechanically
coupled — `check-plan-routes.resolve_agents` shells out to `check-domain.sh --resolve`, which reads
`team-config.yaml` and calls `harness_boundary.matches`. Split them and you get either a tree where
every write is denied, or — worse and undetectable — a tree whose shape gate is silently off.
`check-state.sh`'s glob block lands with or before it, because it is the only thing that would report
a partial move at all.

**Unit 4 is its own atomic unit** and has no ordering tie to unit 3. `factory_config._PROBE`,
`harness_boundary.HARNESS_CONTROL_PLANE` and `gen-decisions-index.DOCS_DIR` must move together, or
root resolution silently picks a different checkout than the classifier is judging against.

### The carrier

**Each unit becomes its own feature, planned from this map.** That matches what the harness is built
to run, keeps each brief and plan reviewable, and means a failure in one unit does not stall the
others. A single feature with a raised budget would produce a plan whose review is the same problem
as reviewing one enormous PR.

**FEAT-19 is replanned or retired as part of this** — that is #338, which this unblocks.

### What made one landing wrong

Roughly 800 code sites across two migrations, plus a config split, a writer merge and a new guard
mechanism, in one review surface. That is the point where review stops being real, and this project
has already recorded what happens then: on 2026-08-03 all four gates passed while four `.harness`
YAML files did not parse.


---

Sequence amended by the fleet ruling (#355 final) and #349's no-merge resolution, 2026-08-14:

- **Unit 1 is DEAD** — harness gets no `fleet.yaml` entry; the stale-checkout diagnostic stays as is.
- **Unit 2 is DEAD** — the writers stay separate (#349). Its INV-26 survivor landed independently as PR #359.
- **Unit 8's 'ideally 2' clause is void** with it; the kaya proof depends on 5 alone.
- Units 0, 3, 4, 5, 6, 7, 9 stand unchanged, same dependency order. **Unit 0 — the migration detector — is first**, and is the next feature to plan.
- The #356 path convention (anchor five relative-path families + a check) rides with unit 3, whose surface it shares.
