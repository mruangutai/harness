# Ship review — FEAT-56, the central onboarding model (issue #206)

**Recommendation: ship, once you have run the UAT.** Nine of the ten success criteria are met at
`review_sha` `e6261060`; the tenth, SC-09, is your hand-test and is the only thing outstanding. The
qa gate is green, the review panel passed with no gating finding, and every advisory finding worth
taking was taken rather than deferred.

**No report round was spawned.** This is assembled by reading the run digests off disk, per DEC-69.
The files it is built from, all under
`.harness/harness/features/FEAT-56-central-onboarding-model/`:
`notes/research-FEAT-56-init-audit.md`, `notes/research-FEAT-56-goalcheck-plan-c0.md`,
`notes/research-FEAT-56-goalcheck-ship-c0.md`, `notes/qa-FEAT-56.md`, `notes/uat-FEAT-56.md`,
the four `notes/review-*-c0.md`, `runs/2026-09-08-01-plan-advisor-validator/digest.md`,
`runs/2026-09-08-02-plan-panel-validator/digest.md`,
`runs/2026-09-08-03-review-validator/digest.md`, `runs/2026-09-08-simplify-eng/digest.md`,
and the seven task run digests.

## What #206 turned out to be

The ticket's diagnosis was right and half its prescription was dead. `harness-init` really did still
tell its reader that onboarding runs inside a product repository and copies `.harness/` into it. But
three of the issue's premises had been overtaken since it was filed on 2026-08-10:

- **Its item 2 — create `.harness/products/<name>/` — is not built.** A `fable-advisor` consult ruled
  it already satisfied in substance by DEC-174, which puts a member's config in that member's own
  repository, read from its default branch. You struck that same placement yourself on 2026-08-18
  (#336 on #493). Building it would have made a file nothing reads.
- **Its row 8, "map the codebase", is void.** That tier was retired on 2026-08-24.
- **Its stated conflict — DEC-187's per-project test matrix being "aspirational" — was already
  closed** by FEAT-24. kaya-ai carries its own 13 KB `harness.json` on `master` today.

What survived is the address change, and that is what shipped: onboarding is now **land the
repository's own `harness.json` on its default branch, register it in `fleet.yaml`, create its
central tree under `.harness/<segment>/`** — in that order, because reversing it has no symptom but
an unattributed `FleetError` mid-build. `DEC-220` records it, and records the `#203`-versus-`#206`
reconciliation in favour of rewrite, which #206 explicitly asked for before either was picked up.

## What each squad did

**Product** (`runs/plan-audit-product/digest.md`, `runs/2026-09-08-02-plan-draft-product/digest.md`,
`runs/2026-09-08-07-goalcheck-ship-product/digest.md`). Re-graded all nine of #206's audit rows at
HEAD and found one naming a step that no longer exists and three "Dead" grades wrong. Wrote the
brief and the eight-task plan. At the ship goal-check it re-ran every criterion at the moved pin
rather than inheriting a grade, and caught REQ-03 passing in letter while four live comment strings
still asserted the retired model. The documentor swept SPEC, BUILD, both READMEs, `org.html` and
wrote DEC-220.

**Engineering** (`runs/2026-09-08-01-t04-eng/digest.md`, `runs/2026-09-08-t03-eng/digest.md`,
`runs/2026-09-08-simplify-eng/digest.md`, `runs/2026-09-08-06-fix-code-eng/digest.md`). One piece of
new code in the whole feature: `factory_config.product_config_report()` and
`--check-product-configs`, which names a fleet member whose config has not landed, with an
18-case suite. Corrected the six `bin/` sites that told a user to run `/harness-init` to repair a
product-side path. The simplify pass found and fixed a `--repo` branch that resolved an entry, threw
it away, then re-derived the same rule with a different spelling.

**Validation** (`notes/qa-FEAT-56.md`, `runs/2026-09-08-03-review-validator/digest.md`). The qa gate
FAILED first time on a real regression — the rewritten skill had reintroduced a literal token the
distribution sweep forbids — and passed after. The panel graded the three criteria no runner can
reach with full citation sets: 6 of 6 for SC-03, 15 of 15 for SC-04. Its two `med` findings were a
routing table stating two of three conditions, and a test suite that could not tell `except
FleetError` from `except Exception` — the second proved by mutation, not argued.

## What you must do

**SC-09, the UAT, at `notes/uat-FEAT-56.md`.** About ten minutes. You read the rewritten
`harness-init` as if onboarding one concrete new repository and answer five yes/no questions: is the
ordering rule clear and does the document say why reversing it fails silently; does anything ask you
to write a file into the product repo that the factory will not read; does it tell you what to do
between registration and the first commit, including when you cannot push to the default branch;
would you know to run `--check-product-configs` and what to do on exit 2; is it clear step 1's
prerequisites are this clone's. It ends in a line you fill in.

The main session declined to answer it on your behalf, correctly.

## What this feature cannot prove

**No runner grades an instruction being FOLLOWED.** `harness-init` is prose executed by you and by a
model. The suite proves the ordered markers, the command strings a test reads out of it, and that
the gates around it stay green. Whether the procedure actually onboards a repository rests on your
UAT and on nothing else. There has been no dry run against a real new repository, and that is stated
in the brief's own `## Verification gaps` rather than discovered later.

**REQ-05 has no standing invariant behind it, by design.** `check-state.sh` never reads a member's
config from its remote, so a member whose config is deleted after onboarding stays invisible until
the next build. `--check-product-configs` is operator-run. DEC-220 now says so.

## Budget

Nine rework cycles of ten, and twenty runs against an informational budget of twenty. The runs count
is at its tripwire, so: each run resolved a specific issue and advanced a criterion — three plan
cycles closing panel and goal-check findings, seven task runs, and a validate phase that found and
fixed real defects. The cycle count is high because the gates kept catching things, which is the
gates working. It is one short of the hard bound, so a further fix loop would need your decision.

## Proposed backlog

Unstruck rows become issues on your acceptance. **Anything not listed here dies silently.**

| ID | Nature | What |
|---|---|---|
| B-1 | chore | `tests/unit/test-fleet-product-config.py`: the `len(report) != len(fleet["repos"])` half of the exit guard is untested. The panel ranked it last — the branch is unreachable through the public surface today, so a test demonstrates rather than protects. |
| B-2 | chore | The pilot product's four committed `.harness/` subtrees in kaya-ai — `team-config.yaml`, `expertise/`, `features/`, `codebase/` — are read by nothing. Out of scope here by your ruling: removing them is a write into a product repo no domain grants, and `team-config.yaml` is `harness_boundary.MARKER`, so deleting it from a default branch is not reversible by a later cycle. |
| B-3 | chore | `<control-plane>/.harness/kaya-ai/` does not exist, so `features_root('mruangutai/kaya-ai')` points at nothing and kaya's FEAT-01..03 sit orphaned in the product repo. |
| B-4 | enhancement | Nothing gates a rotted `file:line` citation in docs. The documentor found `harness_boundary.py:158` wrong inside DEC-220's own paragraph while `check-instruction-paths.py` passed, and the review panel itself made two anchor-drift errors it had to self-correct. |
| B-5 | enhancement | The trust delegation is now disclosed but has no decision of its own: landing `harness.json` on a product's default branch gives whoever can push that branch control of what the factory reads for that member. pm flagged it as emergent and stopped rather than adopting it. |
| B-6 | bug | Subagent returns intermittently arrive as `failed (exit 1)` with "called yield with null data" while a well-formed VERDICT/DIGEST block is present in the final turn. Hit at least three times this feature; routing on the exit code alone would have re-spent each spawn. |
| B-7 | bug | `harness-code-reviewer`'s return carried no VERDICT while its artifact was complete; one re-prompt recovered it. A channel that drops the verdict but keeps the artifact defeats `validate-digest.py` on the parent's side. |
| B-8 | chore | Plan task T-06's title still says "regenerating the omp adapter"; it is the Claude adapter that is regenerated. No gate reads the title. |
| B-9 | chore | Plan task T-03's intent names `tests/fixtures/prior-check-domain.sh.fixture`; the file is at `tests/integration/fixtures/`. Text only — the fixture was untouched either way. |
| B-10 | chore | `BUILD.md` carries two differently-worded counts at `@104` and `@399/@401` for different subjects. Each is internally consistent; neither was changed. |
| B-11 | enhancement | `--repo` narrows `declared` to the requested member, so a single-repo exit 0 is not a fleet-wide all-clear. The skill says so; nothing enforces it. |
| B-12 | bug | `check-state.sh` INV-29 reports six standing worktrees for features that already reached a terminal state, none of them this feature's. |
| B-13 | chore | T-06's verify does not run `check-instruction-paths.py`, which is how that task landed four unanchored paths that a later task's gate caught. Task verifies for instruction-file surfaces should include the scanner.
