# Ship review — FEAT-69

FEAT-69 is acceptance-ready. Validation c1 passed all five readers at review SHA `bec83b523a7a1e071988aedfb7c85babd6389c42`; immutable implementation pin `db488aa7c78e392c788bd5839a43ebf4ba562ea1` meets SC-01 through SC-04, and c0 findings VAL-01 and VAL-02 are closed. No must-fix or open question remains.

## Definition of done, graded

| Perspective | Signed definition | Verdict | Discharged by | Evidence |
|---|---|---|---|---|
| operator | I can rely on the hyphenated entry retaining its complete observable contract: normalized baseline-versus-immutable-pin exit status, stdout, and stderr bytes agree for full-table output, `--list`, every owning check-state suite, and both structural-lock clean-tree runs. The proof is reproducible from clean detached checkouts, records raw evidence, and cannot claim receipts existed before the pin they evaluate. | met | SC-02, SC-04 | `notes/research-FEAT-69-long-file-check-state-package-goalcheck-validate-c1.md`; `notes/clean-pin-byte-receipts.generated.md`; `notes/amendments-2-full-table-scope.md` |
| code maintainer | I find a thin `check-state.py` entry over an importable `check_state/` package whose context, table, runner, and invariant families have explicit ownership without moving discretion out of the table. Every function on that full surface meets code grade 4 or better, and the package-aware structural lock still follows transitive calls, declared reads, authority, module-body, no-reparse, broad-catch, and reads-family rules rather than going vacuously green at an import boundary. | met | SC-01, SC-03 | `notes/research-FEAT-69-long-file-check-state-package-goalcheck-validate-c1.md`; `notes/review-harness-qa-c1.md`; `notes/red-first-receipts.md` |

## Run record

No report round was spawned. This briefing was assembled from the four recorded run digests:

- `runs/plan-product/digest.md` — PASS: a four-task plan discharged both perspectives at plan exit; all four panel findings were applied before signature.
- `runs/validate-validator/digest.md` — FAIL: c0 found VAL-01 in SC-02 measurement scope and VAL-02 in SC-03 fail-first evidence.
- `runs/fix-c0-main-direct/digest.md` — PASS: evidence-only fixes applied the operator's SC-02.scope ruling and added the discriminating SC-03 red-first receipt without changing the implementation pin.
- `runs/validate-c1-validator/digest.md` — PASS: qa, code, security, UI, and goal-check all passed; unit 43/43 and integration 71/71 passed; every SC is met and `must_fix` is empty.

## Validation conclusion

- VAL-01 is closed: the operator ruled the measurement fixed, not five lines waived. Full-table comparison now covers every feature except FEAT-69's own record and reports `All identical (normalised): **yes** (13/13).`, exact lines `none`, with no live divergence.
- VAL-02 is closed: the pin routes suite under baseline `check-plan-routes.py` exits 1 with exactly 25 uncaught mutant checks, including all required FEAT-69 mutants; the pin suite passes.
- T-04's exact `verify:` command and exit-0 output are retained in `notes/clean-pin-byte-receipts.md`.
- Security found no exploitable regression. UI correctly scoped out after a 56-object census found no rendered or interactive surface.

## Open questions and escalations

Open questions: none.

Resolved escalations: VAL-01 was resolved by the operator's `SC-02.scope` amendment in `notes/amendments-2-full-table-scope.md`; VAL-02 was resolved by the committed SC-03 fail-first receipt. No unresolved escalation remains.

UAT: not required; the signed BRIEF declares only automated and inspection verification, and validation found no user-facing UI surface.

## Spend

- Recorded runs: 4
- Wall-clock minutes: 69
- Rework: 35 minutes, 1 recorded fix round
- Tokens: 396790
- Cycles used: 2 of 10
- Judgements: 7

## Amendments

| At | Decision | Reason | Overruled |
|---|---|---|---|
| `2026-09-28T20:31:47.196363+00:00` | `T-03.files` | INV-27's coupled-reader row for the features-path join moved with the join into `check_state/ctx.py`; its fixture row moved with it after the first full-table baseline diff. | no |
| `2026-09-28T20:48:11+00:00` | `T-01.intent` | Amendment 1 corrected the baseline SHA to `a726bad8`; `e6f8493b` predates INV-49. | no |
| `2026-09-28T20:48:15+00:00` | `T-04.verify` | Amendment 1 corrected the baseline SHA to `a726bad8`; `e6f8493b` predates INV-49. | no |
| `2026-09-28T21:52:08+00:00` | `SC-02.scope` | Full-table byte identity is measured over every feature except this feature's own record; the operator ruled the measurement fixed, with no per-line ruling. | no |

Overrule rate: 0/4.

## Proposed backlog

| ID | Nature | Residual finding | Source |
|---|---|---|---|
| B-1 | chore | Split the long fixture orchestration in `tests/unit/test-check-skill-refs.py:52-104` so each future scanner fixture computes and asserts its own case-specific findings value. This is a medium maintainability advisory, not an acceptance defect. | `runs/validate-c1-validator/digest.md` ADV-01 |

Anything not listed above is intentionally not proposed for backlog.
