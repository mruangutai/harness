# T-04 — Kaya ledger recovery (#2158; closes the defects reported as #2173 and #2174)

Executed on 2026-11-07 by the main session (DEC-174), inside the Kaya planning worktree `.claude/worktrees/harness/FEAT-01-kaya-platform`, using the installed tooling. The tooling is PR #2177, `4a05030d`, and then BUG-2180, PR #2184, `88f1c4c2`.

## Separate authorization

`.harness/kaya/features/FEAT-01-kaya-platform/notes/research-fleet-planning-recovery-authorization.md` (sha256 `a6ec5e0986310e1025ea2dcedfb4b7ec65205b27e72a3bac31adbe6fad3d0df2`) is strict JSON scoped to `FEAT-01-kaya-platform`. It names the operator directive, the effect definitions (#2172–#2174), and the original hashes, and lists four exact-subject effects:
- `record-refusal` for run 3;
- `record-cycle-evidence` for run 2 (0) and run 6 (1);
- `recover-mirror` (full, mruangutai/harness → mruangutai/kaya, plan_sha256 `1c5d6bfb…`).

## Before (installed tooling, `check-state.py --feature FEAT-01-kaya-platform`, exit 1)

- DEC-156 digest-contract VIOLATION for `runs/2026-10-05-3-simplify-eng/digest.md`: no fenced YAML mapping. This is #2174.
- INV-37: no usable receipt. INV-26 CANNOT VERIFY for #2116–#2126 (the wrong repository). The INV-7 cycle-attribution rows for runs 2 and 6 were reported as "historical cycle attribution without evidence" notes. This is #2173.

## Commands (all exit 0, `--by operator`, `--evidence notes/research-fleet-planning-recovery-authorization.md`, `--yes`)

1. `feature-record.py record-refusal --file <feature.json> --id 2026-10-05-3-simplify-eng --digest runs/2026-10-05-3-simplify-eng/digest.md --reason "…"`, which printed `RECORDED record-refusal run '2026-10-05-3-simplify-eng'`.
2. `feature-record.py record-cycle-evidence … --id 2026-10-05-2-plan-product --digest runs/2026-10-05-2-plan-product/digest.md`, which printed `RECORDED`.
3. `feature-record.py record-cycle-evidence … --id 2026-10-05-6-plan-product --digest runs/2026-10-05-6-plan-product/digest.md`, which printed `RECORDED`.
4. Replay of commands 1 and 3: exit 0, and feature.json was byte-identical (`e4af31de…` both before and after).

## After

| Run | Verdict (unchanged) | cycles_used (unchanged) | New provenance |
|---|---|---|---|
| 2026-10-05-2-plan-product | FAIL | 0 | `cycle_evidence` {operator-history, digest `94d6f194…`, authorization `a6ec5e09…`} |
| 2026-10-05-3-simplify-eng | BLOCKED | 0 | `refusal` {operator-history, digest `d0e28f4d…`, authorization `a6ec5e09…`} |
| 2026-10-05-6-plan-product | FAIL | 1 | `cycle_evidence` {operator-history, digest `b8792f92…`, authorization `a6ec5e09…`} |

- The feature `cycles_used` stays 1, so the residual is 0. No verdict, digest byte or count was rewritten. All three digest hashes are unchanged from the T-03 capture.
- `check-state.py --feature FEAT-01-kaya-platform` after recovery, with local gh authenticated, exits 0 with no violation from INV-7, INV-15, INV-37, INV-39, INV-40 or INV-46. The DEC-156 violation is gone. Run 3 now shows the note "refused completion; BLOCKED, not an accepted return". The 2026-10-04/05 runs that carry no evidence remain notes (historical cycle attribution without evidence), not violations.

## Negative controls (throwaway copy outside the repo, then discarded)

- An authorization claiming run 2 = 1 against its digest's 0 was refused: `REFUSED: historical cycle attribution contradicts the authentic digest count` (exit 2).
- After recording, a refused digest altered by one byte failed `verify_evidence_ref` with `evidence hash does not match the recorded artifact`.

## Landing status

The recovered record was committed in the Kaya planning branch as `a2dec663`.

The first CI run on PR #2189 failed in the Repository-state gate: `INV-37 FEAT-01-kaya-platform: invalid authoritative repository binding: product config unreadable … gh api contents failed`. CI has no gh token, and DEC-221 required an unresolvable bound target to fail closed. On 2026-11-08 the operator decided that CI need not verify gh-dependent state. DEC-221 was amended, and BUG-2190 (#2190, PR #2205, `b5d65c34`) made INV-37 check a bound target locally when gh is unauthenticated.

PR #2189 then passed CI, including the Repository-state gate, and landed on main as `30c06581`. On the main checkout, `feature.json` is `900d8fb9…` and `plan.yaml` is `1c5d6bfb…`, both unchanged. `check-state.py --feature FEAT-01-kaya-platform` exits 0 there. SC-08 remains user-executed.
