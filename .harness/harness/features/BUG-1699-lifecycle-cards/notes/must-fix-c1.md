# Must-fix routing — BUG-1699-lifecycle-cards — c1

Raised by pinned validation `2026-09-16-07-validate-validator` against `ed64ea9cc4ef92e3e54adfa0849a0147230b480b`. Operator rulings are authoritative at `notes/answers-validation-c0-2026-09-16.md`. Main's direct repairs and evidence landed at `37d846da62bd2e1d88a5406956482398d17bdca5` and `notes/receipt-main-direct-validation-c1.md`.

## Owning dev: harness-backend-dev — T-01

1. **CR-01 · substance · high.** Refactor `.claude/skills/harness/bin/gh_board.py#project` into coherent helpers until the mechanical production risk grade is 4 or better. Preserve its interface and all signed lifecycle projection behavior. The pre-fix mechanical grade is the failing proof: grade 3, cyclomatic 9, cognitive 10, ABC 16.3.
2. **CR-02 · substance · high.** Split `tests/integration/test-check-state-inv26.py#_inv26_fixture` by concern until the mechanical test risk grade is 3 or better. Preserve every existing fixture scenario and focused gate. The pre-fix mechanical grade is the failing proof: grade 1, cyclomatic 14, cognitive 21, ABC 47.9.
3. **QA-03 · form · high · T-01 portion.** Add an explicit criterion-by-criterion fail-first table to the fix receipt for every automated SC carried by T-01. Cite the exact test and an actual failing pre-fix run/receipt path for each row; reconstruct against the pre-T-01 source when historical evidence is absent. Do not claim one generic INV-26 red result covers unrelated criteria. Main's receipt already supplies the direct T-02/T-03/T-04 red evidence; do not rewrite it.

Test-first applies to every substance change. Run the exact signed T-01 gate and the mechanical Python risk grade. Commit only the T-01-owned source/test changes plus the fix receipt; do not edit `feature.json`, `plan.yaml`, `STATE.md`, validator notes, or Main's receipt.

## Combined-tip re-verification set

After the T-01 commit, the validator readers must verify all original findings over the resulting tip:

- QA-01 narrow unit failure: resolved by Main at `37d846da` and covered by 75/75 OMP hook checks with a 73-pass/2-fail pre-fix receipt.
- QA-02 T-04 factory case-L regression: resolved by Main at `37d846da`; factory integration is 131/131 and board-lifecycle focused checks pass.
- QA-03: Main's receipt supplies T-02/T-03/T-04 historical red evidence; the T-01 dev receipt must complete the remaining per-SC rows.
- QA-04, prospectively classified `substance` and owned by T-02/T-03: resolved by Main's execution-bound zero-network negative control at `37d846da`.
- CR-01 and CR-02: must be resolved by this T-01 dev step and mechanically regraded.
- Q4 runtime return contract: repaired by Main at `37d846da`; its focused OMP evidence must be rechecked. A fresh canonical three-perspective goalcheck is still required after the fixed tip is pinned; the fix team does not replace it.

Security and UI must inspect only the fix delta and self-scope honestly. Any new unowned finding is a scope change; do not silently assign it.
