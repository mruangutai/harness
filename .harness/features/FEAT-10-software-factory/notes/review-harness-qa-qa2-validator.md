# Re-resolve of the qa test-matrix gate — FEAT-10 — second pass, S-01

**VERDICT: PASS.** The first run's BLOCKED was a config defect — `functional.cmd: null` bound by
the matrix's `always` lists for `api`/`cross_module` — and DEC-187 removed `functional` from those
`always` lists, retaining it in `test_kinds` as `status: excluded, signed: DEC-187`. Under DEC-187
rule 1 that makes `functional` a soft skip, never selected. `unit` and `integration` are both
required (unchanged from the first run) and both genuinely green.

**Note on artifact path:** the dispatch specified
`notes/receipt-harness-qa-qa2-validator.md`, but `check-domain.sh` blocked that write — my
manifest permits only `notes/qa-*.md` and `notes/review-harness-qa-*.md` for this agent. Writing
here instead, a distinct filename from the first run's `review-harness-qa-qa-validator.md` (not
overwritten, not touched).

## Diff assessed

Working tree vs `review_sha` f9488a2 (HEAD; the diff is entirely uncommitted/untracked, confirmed
via `git status --porcelain`). Same as the first run, plus T-08's landed change: `check-state.sh`
(INV-24) and `test-check-state.py`, both `M` in `git status`.

## Classification (derived from the diff myself, not adopted from the first run's artifact)

I independently re-derived the same 11 logical groups the first run named and confirm them —
`factory_gh.py`/`factory_workspace.py` = `api` (external `subprocess.run` to `gh`/`git`);
`factory_decompose.py`/`factory_claim.py`/`factory_land.py` = `cross_module` (compose
`factory_config`+`factory_gh`+`factory_cli`+`harness_yaml`); `factory_cli.py`/`factory_config.py`
= `logic`; `run-unit-tests.sh` = `scaffolding`; `.harness/harness.json` = `config`;
`docs/harness/DECISIONS*.md` = `docs`. Added for this run: `check-state.sh` (T-08, INV-24) =
`logic` — `unit` always, no new kind requirement it wasn't already binding.

`_matrix_provenance` at `harness.json:79-101` — verified myself against
`.claude/skills/harness/templates/harness.json`: template's `api` was `always: [unit, functional]`,
`cross_module` was `[unit, functional, integration]`, `feature` was `[unit, functional,
integration]`. `removed: [functional], added: []` is accurate for all three entries. Confirms the <!-- ok-stale -->
orientation note; not re-derived from a different source, same conclusion.

## Per-kind resolution

| Kind | Required by | State | cmd | Exit | Named-test result |
|---|---|---|---|---|---|
| `unit` | every group (`api`, `cross_module`, `logic`) | **satisfied** | `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 10/10 registered `UNIT_SCRIPTS` PASS, 0 FAIL. Includes all 7 new factory unit tests (`test-factory-cli.py`, `test-factory-gh.py`, `test-factory-config.py`, `test-factory-workspace.py`, `test-factory-decompose.py`, `test-factory-claim.py`, `test-factory-land.py`) |
| `integration` | `cross_module`×3 and `feature`-shaped groups (`always`) | **satisfied** | `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 14/14 registered `INTEGRATION_SCRIPTS` PASS, 0 FAIL, including `test-factory-integration.py` and T-08's `test-check-state.py` (8 named `(s) INV-24` cases, all `ok`) |
| `functional` | api×2 + cross_module×3 in the OLD matrix; **removed** from both `always` lists under DEC-187 | **not selected — soft skip** | `null`, `status: excluded`, `excluded_because` real, `signed: DEC-187` | n/a | n/a — rule 1: excluded + signed decision id means neither `cmd` nor `detect` is read. Not a finding |
| `component`, `ui`, `eval`, `typecheck` | not required — no `frontend`, no `ai_behavior` change_type in this diff; `typecheck` is not present in `test_matrix` at all | not selected — soft skip | `null`, `status: unresolved` | n/a | rule 3: no change_type present in this diff puts these in an `always`/`when` list that fires, so `cmd`/`detect`/`status` are not read and they are not findings. **Correction to my own first pass**: `typecheck` is not-selected because no matrix entry ever names it (rule 3), not because the diff has no `.ts`/`.tsx` — it does: `.claude/skills/harness/bin/omp-reviewer-guard.check.ts` is untracked in this tree, but is unrelated OMP-porting scope, not FEAT-10's (see note below), and even if it were FEAT-10's, `typecheck` still would not bind since no `always`/`when` selects it |

Integration's requirement fires concretely via `api`'s `when: touches_db_or_external` — `factory_gh.py`
and `factory_workspace.py` are classified `api` precisely because every function shells out to `gh`
or `git`, so the predicate is true and `integration` is required for them independently of the
`cross_module` `always` list already requiring it for the other three groups.

Both commands run by me, verbatim, exit status captured directly (not relayed): `run-unit-tests.sh
--kind unit` → exit 0 (10/10 registered files PASS — a file count, not a total case count); 
`run-unit-tests.sh --kind integration` → exit 0 (14/14 registered files PASS — likewise a file
count).

**Denominator note (my own P-04):** `config`, `docs` and `scaffolding` all carry `always: []` in
the matrix. The `.harness/harness.json` edit that unblocks this gate, and the
`docs/harness/DECISIONS*.md` and `run-unit-tests.sh` changes, are themselves bound by zero required
kinds — advisory, not a finding; the gate's floor for THIS diff rests entirely on the 5 api/cross_module
groups plus T-08's logic group.

**Scope note — files present but outside FEAT-10's inventory.** The working tree also carries
`gen-omp-agents.py`, `omp-reviewer-guard.check.ts`, `test-gen-omp-agents.py`,
`test-omp-reviewer-guard.py` and a `.omp/` directory. Two of the four are registered in
`INTEGRATION_SCRIPTS` and passed (`test-gen-omp-agents.py`, `test-omp-reviewer-guard.py`, both
shown green in the integration run above). These are not part of the dispatch's FEAT-10 file
inventory and I did not classify or gate them as FEAT-10 diff — noting their presence so a reader
diffing the full tree does not read them as an omission from my 11 groups.

## Findings and gaps carried forward (informational only, not new)

- All open_questions raised by the first run (Q1 factory_land.py:77 fail-open, Q2 duplicate
  gh-error predicate, Q3/Q4/Q5 minor items) are unchanged by this config fix — they are code/review
  findings, not test-matrix findings, and are out of my scope per the dispatch. Not re-raised here;
  see `runs/qa-validator/digest.md`.
- SC evidence table carries forward from the first run's 20-row mapping in
  `notes/review-harness-qa-qa-validator.md` (read-only, not re-derived in full by me per dispatch
  scope), with **one update that is mine to supply**: SC-06 ("The state check fails when a feature
  records a claimed issue in a repository the fleet file does not list", `verify: automated,
  evidence: integration`, BRIEF.md:214-216) was the sole SC with no evidence in the first run
  because it traced to T-08/INV-24, then withheld under DEC-174. T-08 has since landed. SC-06 is now
  **satisfied**: `.claude/skills/harness/bin/test-check-state.py:851` — case `"an UNLISTED
  repository is a violation naming the repo"` — invokes `check_state` against a `feature.yaml` whose
  factory block records a repo the fleet does not list, asserts the resulting output contains a
  line naming `INV-24` and the offending repo, and it ran green in this pass (case group `(s)`, 8/8
  ok, confirmed in the integration output above).

## Coverage gaps (Phase 1 expectations)

None new. This is a gate re-resolution against an unchanged code diff (plus T-08) — the matrix
floor is met and no Phase-1-derived expectation is unmet by this pass; the first run's own
coverage_gaps carry forward unchanged (see its digest).

## cycles_used

0 — this run issued no send-backs.
