# STATE

## Current

- feature: FEAT-14-feature-json-schema · phase **build** · status in_progress
- branch `feat/204-feature-json-schema` · HEAD `b3055ec` · `review_sha` pinned `3d37762`
- cycles_used **5** of 10 · runs 8 of 20 · `check-state.sh` rc 0, **zero violations**

**Segment 1 is COMPLETE and committed.** T-01 (schema artifact, `feature_schema` module, thin CLI,
19-case unit suite) and T-03 (jsonschema in CI, unit suite + corpus sweep wired into the required
`integration` job) both landed and passed their own `verify:` clauses at exit 0. The blocking qa gate
returned `matrix_ok: true`, `must_fix: []`. Five mutants proved the load-bearing assertions can go
red; all restored byte-identical.

**E1, found at collation, fixed and committed.** T-01's mandated jsonschema guard tripped
`test-harness-yaml.py`'s one-guarded-import assertion, reddening the required `integration` context.
That assertion was **broader than the decision it encodes** — FEAT-05 D-12 (`PLAN.md:229`) is scoped
to `import yaml`, not to guarded imports in general — so no signed decision was contradicted and it
was an execution-time fix, not a re-plan. It is now two assertions: exact-set on yaml-guarded files
(D-12 at full strength) and a **subset** cap over the sanctioned dependency-policy modules, pre-sized
to include the guard T-06 adds to `check-domain.sh`. Subset, not equality, is load-bearing: equality
sized to today's two would go red at layer 0 with nothing driving. I proved all six directions myself.

### The next action is LAYER 0 — batch A, and it is not mine to run

Six of twelve tasks are DEC-174 `main-session-direct` and interleave on the critical path, so this
feature cannot finish in one orchestrator session. Batch A is **T-02 → T-04 → T-06 → T-07 → T-12**,
dependency-ordered and runnable in one turn. Full conditions ride the return; the load-bearing ones:

- **Run `gh-sync.py open <feature-dir> --parent 204` FIRST, before T-04.** It never opened — the
  environment classifier denied it here (a DEC-138 SKIP, never a gate). After T-05 it is radioactive
  until T-08 lands: it hardcodes `feature.yaml`, reads a missing file as an EMPTY record, and re-files
  existing issues. External damage no `git reset` undoes.
- **Re-confirm no other writer is active immediately before T-04 and again before T-08.** Verified
  idle at `1bdfe3f`; the corpus mutates mid-session, so this is a continuous condition.
- **FEAT-14's own row in T-04's table is STALE and the RULE governs.** The table reads `in_progress /
  plan → Plan` from `a29ad06`; I moved this feature to `phase: build` this session, so T-04's own rule
  — *"in_progress with old phase build is Building"* — places it at **`Building`**. T-04 says apply
  the rule to the glob's contents when you run, not only to the seventeen rows.
- **After T-06 lands, re-run `--kind integration` before starting T-07.** T-06 adds an
  `except ImportError` to `check-domain.sh`; the E1 subset already permits it, and this proves it.
- Today's `check-state.sh` violation set is **0**, the strongest possible T-04 baseline.

### Carried into segment 2 (T-05, T-11) — do not lose these

- **G1 — an approved-SC coverage gap, test-only fix, no plan change.** SC-02 requires a failing
  fixture at **each of three nesting levels**; the `factory` and `factory.edges` levels have NONE.
  The schema is correct (`feature-schema.json:90`, `:100`) and nothing holds it there. `factory`
  appears in zero feature files, so fixture coverage is the only coverage it will ever get — the
  identical argument the operator made for `Backlog`/`Ready`. Add the fixtures to
  `test-validate-feature-json.py`, already in T-01's `files:`. Folded into segment 2, no own spawn.
- G4 — the `.json`-holding-valid-YAML rejection is the one assertion whose liveness rests on reading
  rather than falsification. Mutate it in segment 2.

## Open Questions

- Q1 non-blocking, **measured false three ways** (eng-lead, qa, and me): `tests.yml:110-114` claims
  `test-check-plan-routes.py case 25` asserts the Plan-route step is present and unneutered. No such
  test exists — zero hits in that file. T-03's approved intent repeats the false claim, and T-03 has
  now added a second CI step with the same deletion hole and no claimed guard at all — the step
  carrying REQ-06's only mechanical proof. No task's `files:` authorizes the fix. Briefing row.
- Q2 non-blocking: the guarded-import needle is the literal `except ImportError` and misses
  `except (ImportError, ...)` and `except ModuleNotFoundError`. **Pre-existing**, not a regression.
- Q3 non-blocking: possible Bash-route hole in the write guard — an `Edit` was denied where a
  byte-identical `Bash` mutation went through. Surfaced through a validator-lead process error, not
  normal operation; likely FEAT-17-guard-boundaries' territory. T-06 builds on this hook.
- Q4 non-blocking: `test_exactly_one_guarded_import_in_the_tree` now misstates its own contract (two
  guarded imports today, three after T-06). Kept deliberately — `test-harness-yaml.py:9` pins nine
  test names to FEAT-05's PLAN, so a rename breaks a documented correspondence.
- Q5 non-blocking: two agents wrote `runs/e1fix-eng/digest.md` concurrently; one had its Write
  rejected as stale and preserved the other's prose. Shared run artifacts have no concurrency guard.
- Q6 non-blocking, carried: `validate-digest.py:182`'s orchestrator digest enum stays OUT of scope
  (D-13) — it carries `blocked` while the six board columns have no `Blocked`. Confirm the boundary.
- Q7 non-blocking, carried: BRIEF SC-08 carries one clause twice; SC-07's prose says "exits non-zero"
  where its test asserts exactly 3. Both are wording tightenings, neither a defect.
