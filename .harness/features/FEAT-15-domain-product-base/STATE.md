# STATE

## Current

- feature: FEAT-15-domain-product-base — domain enforcement across the factory's two roots (#239)
- mission: plan. Terminus is the operator's signature; both artifacts are `pending` and I marked
  neither approved.
- phase: plan, revision complete. Two runs, both PASS, zero send-backs across both.
- tree: branch `chore/203-end-copy-distribution` at `96d5d5c`; `main` is `278de74`. This feature's
  artifacts are UNTRACKED files in that branch's working tree. No branch created — the operator
  creates one at signature.
- run: `.harness/features/FEAT-15-domain-product-base/runs/2026-08-10-02-plan-product/state.yaml`
- squad: product (plan-feature, then revise-plan)
- status: awaiting-user
- inputs: `.harness/notes/grilling-domain-product-base-2026-08-10.md` and the operator's ruling at
  `notes/answers-2026-08-10-01-plan-product.md` — the ruling file is the authority for the revision.
- artifacts: `BRIEF.md`, `plan.yaml`. Five tasks, every one `execution_mode: main-session-direct`
  with an `execution_reason`, under the DEC-174 carve-out. No build squad was spawned and no task
  dispatches an agent at `check-domain.sh`.
- the ruling folded in: Q1 → option (c). Prefix inference stands; four harness paths
  (`docs/harness/**`, `docs/PRINCIPLES.md`, `README.md`, `.github/**`) are named explicitly and
  resolve against BOTH bases. The accepted cost — one more place to remember, no detection
  machinery — is carried in the BRIEF by the operator's instruction.
- gates I ran myself: `check-plan-routes.py` on the revised plan → five advisory DEVIATION lines,
  `0 violation(s)`, exit 0. The carve-out markers survived rather than being stripped to go green.
- Q2 is CLOSED by measurement, not assertion. Simulating option (c)'s rule through
  `check-plan-routes.py`'s own parser (only `resolve_agents` swapped): `0 violation(s)` across the
  nine plans it discovers, and ZERO paths lose their grant. The documentation tasks in FEAT-12 and
  FEAT-14 that option (a) would have orphaned resolve to `harness-documentor` again. No sequencing
  dependency on either feature was added. Method and three caveats are in the answers file.

## Open Questions

- **Q7 (for signature).** The classifier is TARGET-keyed, not glob-keyed. A glob-keyed one cannot
  express the ruling: `team-config.yaml` grants documentor `docs/**` and contains no
  `docs/harness/**` entry anywhere, so two of the operator's four named paths would have nothing to
  match against. Verified by me — grep for `docs/harness` in the manifest returns nothing. This is
  also the semantics my Q2 measurement was taken under. product-lead's flag stands: reversing it is
  a re-plan, not a revision.
- **Q8 (non-blocking).** The four named paths match anchored against the base-relative target, so
  `README.md` never means `docs/README.md`. This is the clause that stops the closed list widening.
- **Q10 (non-blocking, prose only — recommend deleting the number, not correcting it).** BRIEF.md
  line 137 says "all five in-root allow assertions"; product-lead counted six; I counted four. Three
  readers, three numbers, from the same file. The cause is that "in-root allow assertion" does not
  pin its counting rule: exit-0 expectations on a product-shaped target under `allowed/**` gives
  four (test-check-domain.py lines 102, 284, 315, 380 — line 323 expects exit 2 and is a DENY),
  while counting fire-sites or t12 cases gives other answers. **The dispositions and the gate clause
  are correct and product-lead verified them; only the tally is unreliable.** A number nobody can
  reproduce is not evidence, so the cheapest honest fix at signature is to strike the count rather
  than replace it with a fourth one.
- **Q3 (backlog).** `harness.json`'s unit detect glob claims `test-check-domain.py`, but
  `run-unit-tests.sh` executes it from `INTEGRATION_SCRIPTS`, so `--kind unit` reports green without
  running a case. Pre-existing; every SC correctly names `evidence: integration`.
- **Q4 (ticket).** `bash-write-guard.sh` keeps its own outside-repo rule and is out of scope, so a
  Bash-route write into a product checkout stays ungoverned after this ships.
- **Q5 (disclosure).** No UAT criterion: an honest UAT needs a real product checkout under
  `workspace_root`, which has never existed. The plan inspects the refusal text instead.
- **Q6 (disclosure).** No design pass, no prototype, no UI review — a write-guard shell hook has no
  end-user interactive surface. The architecture review was skipped per my dispatch scope.
  Overridable in either direction.
