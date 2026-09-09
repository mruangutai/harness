# Goal-check — FEAT-56 plan vs issue #206 (plan phase, cycle 0)

**BLUF — does this plan deliver the operator's stated intent? YES for the address change, NO for two
of #206's explicit instructions.** All six REQs are traced, all nine SCs are reachable, and every
surviving step of the skill has a stated destination. Two clauses of the issue are discharged by
nothing: **#168's template parse error (which is LIVE today, not "may become live")**, and #206's
**"reconcile #203 before either is picked up"** — zero references to either issue exist in `BRIEF.md`
or `plan.yaml`. Graded against issue body at `gh issue view 206`, plan/BRIEF at `4b5dbb23`.

## Trace table — every distinct clause of #206

| # | Issue clause | Discharged by | Grade |
|---|---|---|---|
| P1 | Skill runs inside a target project and writes its `.harness/`; team-config lives solely in harness; "the skill has to change address" | REQ-01, T-01 preamble + step 2, T-05 item 3 | DELIVERED |
| P2 | "SKILL.md is 276 lines" (and its nine `:NN` anchors) | 370 lines at `4b5dbb23`; re-graded in `notes/research-FEAT-56-init-audit.md:19-31` | STRUCK (stale claim) |
| S1 | Step 1 install eight prerequisites — **Dead** | NARROWED to control-plane clone: D-02, REQ-02, T-01 step 1 | DELIVERED (narrow, ruled) |
| S2 | Step 2 scaffold `.harness/` from templates (`cp` ×2) — **Dead** | REPLACED: T-01 step 2a-e; team-config `cp` dies, harness.json lands on default branch | DELIVERED |
| S3 | Step 3 technical interview — **Re-homes** | T-01: "UNCHANGED"; answers' destination set by step 4/2a | PARTIAL |
| S4 | Step 4 `dev-ops` detects `test_kinds.cmd` — **Re-homes** | T-01 step 4 (both destinations), T-06 item 4+5 (agent files) | DELIVERED |
| S5 | Step 5 seed the domain manifest — **Re-homes** | T-01 step 5 NARROWS to the control plane only; product gets none (#495 unbuilt) | PARTIAL |
| S6 | Steps 6-7 BRIEF then approval gate — **Re-homes** | T-01 steps 6, 7 → `features_root()` central tree; product `github` block in the product's own harness.json | DELIVERED |
| S7 | Step 8 map the codebase (INV-14/19/20) — **Re-homes** | Tier retired 2026-08-24 (`BUILD.md:208`); BRIEF Non-goals; HEAD's step 8 is the design pass (T-01 step 8) | STRUCK (row void) |
| S8 | Step 9 verify + restart warning — **Dead with 1 and 2** | NARROWED: T-01 step 9 keeps `check-state.sh`/`merge-settings --check` for this clone, adds the fleet check | DELIVERED (narrow) |
| C1 | "Three steps die, six change where they write" | Zero die (1, 2, 9 all survive); four of six change destination; audit `:23,:24,:27,:31` | STRUCK (falsified) |
| C2 | "The skill does not shrink to add the repo to `fleet.yaml`" | T-01 keeps all nine steps, `--upgrade`, red flags; fleet registration is one sub-step (2c) | DELIVERED |
| W1 | Replace-item 1: add repo to `factory/fleet.yaml` (`name`, `default_branch`), extensible later | T-01 step 2c; `lanes` row main-session-direct for fleet.yaml | DELIVERED |
| W2 | Replace-item 2: create `.harness/products/<name>/` + that product's harness.json | STRUCK by plan-phase advisor ruling (`runs/2026-09-08-01-plan-advisor-validator/digest.md:3-18`), D-01, BRIEF Constraints | STRUCK |
| W3 | Replace-item 3: run interview + `dev-ops` detection against a checkout, **writing centrally** | T-01 steps 3, 4: written in the checkout, then landed on the product's default branch (DEC-174 — a central copy is read by nothing) | PARTIAL (central write struck for harness.json) |
| W4 | Replace-item 4: map the product's codebase into a per-product location | Tier retired; `.harness/<segment>/codebase/` has no resolver (digest `:70`) | STRUCK |
| C3 | "Overturns FEAT-10's *no product level in `.harness/`*; the 473-ref/152-file costs are now the work" | Already discharged: `.harness/<segment>/` exists and three resolvers commit to it (`factory_config.features_root`, `layout_migration` READER_TABLE, `inject-expertise.sh:108`) | DELIVERED (pre-existing) |
| C4 | DEC-187 conflict: one harness.json describing this repo; a product "inherits this exclusion silently" | Structurally prevented by T-01 step 2a (template ships every `cmd: null` and a `test_matrix` that keeps `functional`; the control plane's excludes it) + T-07 new DEC entry | PARTIAL (no gate asserts it) |
| D1 | #205 — factory writes to `workspace_root` ungoverned | Premise closed: #205 closed in favour of #103, #103 closed, product checkouts governed (digest `:53-55`) | STRUCK |
| D2 | #203 — "these two issues disagree; reconcile before either is picked up" | **Nothing.** Zero matches for `203` in `BRIEF.md` or `plan.yaml`; reconciliation exists only in a run digest | **MISSING** |
| D3 | #168 — template parse error "may become live again" | **Nothing.** T-05 edits the header only; no task touches line 28 | **MISSING** |
| D4 | #189 — closed with an empty body; do not treat as prior art | Zero matches for `189` in BRIEF/plan; authority is #336 + DEC-174 instead | DELIVERED |

**Consequences of the non-DELIVERED rows.** D3: every `/harness-init --upgrade` on the control plane
already prints `THE SHIPPED TEMPLATE … does not parse … This is a harness bug` and then
`schema_version 1 -> None`, instructing the operator to set their own version to `None` — measured by
running `upgrade-config.py . --check` at `4b5dbb23`; after this feature T-01 step 2 still instantiates
the control plane's own `team-config.yaml` from that file. D2: `harness-init` survives at 370 lines
against a closed issue that scoped its deletion, so the next backlog scan re-suggests deleting it and
re-litigates this feature. S3: `SKILL.md:164` tells the operator the UI answer "decides whether step 7
runs" — step 7 is the approval gate; the design pass is step 8 — so a UI product's design pass can be
skipped. S5: a served product gets no domain manifest, so a product-serving agent is governed only by
repo-agnostic central globs. W3/C4: nothing automated proves a newly onboarded product's matrix is its
own rather than a copy of this repo's.

## The five questions

**1. #168 and the dead template — EDIT is right, DELETE is wrong, but the plan is incomplete.**
`templates/team-config.yaml` has **4 references**, 2 of them live consumers:
`upgrade-config.py:227` reads it by path and compares `schema_version` (fixture proof:
`tests/integration/test-upgrade-config.py:198-207`), `templates/README.md:10` documents it,
`harness-init/SKILL.md:146` is the dying `cp`, and `.harness/logs/2026-08-10.md:79` is record. T-01
also makes it live *by plan* (the control plane instantiates its own from it). So it is not dead code.
But T-05 item 3 says "keep the file loadable by `yaml.safe_load`" — a **false premise**: it does not
load at `4b5dbb23` (`ParserError` at line 28 col 11, `main_session.writes` flow sequence broken by an
inline `##` comment) — and T-05's `verify:` never loads it. Same argument for the other four templates:
none is orphaned — `harness.json` (two destinations + `upgrade-config` + `test-suite-layout.py:111`),
`BRIEF.md` (T-05, instantiated per feature), `settings.snippet.json` (`SKILL.md:43` step 1, which
survives), `gitignore.snippet` (`merge-gitignore.sh:26`). *Disposition: keep the file, and add to T-05
that line 28 is repaired (quote the two `## Approval` scalars) with `yaml.safe_load` in its verify.*

**2. The knowledge the six surviving steps must produce — all six destinations are stated.**
Interview (T-01 step 3), `test_kinds` detection (step 4, both destinations named), domain description
(step 5, control plane only, with the `glob_to_re` reason), BRIEF (step 6 → `features_root()`),
approval + mirror/board (step 7 → the product's own harness.json), design pass (step 8 → central
`DESIGN.md`), plus `<segment>/expertise/` (step 2e) — which *is* read: `inject-expertise.sh:108` globs
`.harness/*/expertise/`, so the advisor's open Q3 premise (`:64` flat tier only) is stale.
*Disposition: no MISSING destination; step 5's narrowing and step 3's stale "step 7" pointer are the
only defects, both PARTIAL.*

**3. REQ-05 vs the issue's complaint — the report catches only the narrower case.**
`product_config` (`factory_config.py:279-324`) reads and parses; T-04's report records `ok/detail` from
exactly that. So it catches *unreadable / unparsable / not-a-mapping* — a config that **exists but
carries harness's own exclusions reports `ok`**. The issue's stated failure is prevented instead by
construction (template instantiation, item C4 above), not by SC-05. Widening it would cost a content
assertion the report cannot make cheaply: it would have to know the product's real surfaces, i.e. run
`dev-ops` detection in a checkout — a network+execution step, whereas `--check-product-configs` is one
`gh` read. *Disposition: accept the narrow report; record in the plan that the inheritance case is
carried by T-01 step 2a and by no gate.*

**4. The eight-prerequisite narrowing — all three grounds hold at HEAD, and T-01 is specific enough.**
`check-state.sh:844` (INV-9, platform prerequisites, DEC-100) grades this clone's settings entries;
`check-state.sh:2431-2440` (INV-31) states in terms *"The setup step lives in
`.claude/skills/harness-init/SKILL.md`, and an already-onboarded clone NEVER RE-RUNS IT"*;
`tests/integration/test-hooks-install.py:265` `case_commands_verbatim_in_skill` asserts three literal
command strings out of `SKILL_MD` (`:53`). T-01 says "KEEP, NARROWED (do not delete it)", names the
three strings verbatim, forbids editing the test, and runs it in `verify:`. *Disposition: narrowing is
correctly specified; no change needed.*

**5. Coverage arithmetic — no orphans in either direction.**
REQ-01→T-01; REQ-02→T-01; REQ-03→T-02; REQ-04→T-05,T-06,T-07,T-08; REQ-05→T-01,T-04; REQ-06→T-03. All
eight tasks trace ≥1 REQ. SC-01,02,09→T-01; SC-03→T-02; SC-04's fifteen files = T-05(4)+T-06(3)+T-07(7)+T-08(1),
all fifteen present; SC-05→T-04; SC-06/07→suite (T-02,T-03,T-04); SC-08→T-06+T-02. Every
`verify: automated` names an active non-null kind in `.harness/harness.json`: `unit`
(`run-unit-tests.sh --kind unit`) for SC-05/06, `integration` (`--kind integration`) for SC-02/07/08.
No SC rests on a null kind (`component`, `ui`, `eval`, `typecheck`, `functional` all `cmd: null`).
*Disposition: coverage passes; no orphan to report.*
