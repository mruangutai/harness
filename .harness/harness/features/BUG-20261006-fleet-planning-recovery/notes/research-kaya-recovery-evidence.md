# T-03 — Kaya authentic capture receipt (#2157)

Captured 2026-11-07 by the main session (DEC-174 main-session-direct), under the operator directive recorded verbatim in `notes/operator-ship-directive-2026-11-07.md`.

## Preconditions

- **Repair tooling is reviewed, tested and installed.** PR #2177 (T-01/T-02) was squash-merged as `4a05030d401593003209f525fd06e00802eccd36` with all CI checks green. The main checkout was fast-forwarded to that commit, which is the owner installation.
- **Authorization.** The operator directive authorizes capture and recovery. Advisor ruling KayaBlockersAdvisor set the order: tooling PR first, then capture and recovery inside the Kaya planning worktree, landed as one green corpus PR.

## Capture mechanism, and a deviation from the literal task text

#2157 says to read the Kaya record "from the main corpus". On `main`, the Kaya corpus contained none of the historical feature files, so there was nothing there to read. The authentic record existed only in the Kaya planning worktree `.claude/worktrees/harness/FEAT-01-kaya-platform`. Under FEAT-1559, that worktree is the record's own home, not a sibling read from this repair checkout.

That worktree committed the record byte for byte as commit `70da6e14c8d674238b1e4a5336a7378b0b12f4c7` on `feat/FEAT-01-kaya-platform` (author Mike Ruangutai, 2026-11-07). Nothing was regenerated, rewritten, or copied from this checkout. Run digests are gitignored, so the evidence-bound digests were force-added.

## Captured originals (sha256 at 70da6e14)

| Path (feature-relative) | sha256 |
|---|---|
| feature.json | 986da0d21828e4f492857f215d9f548f7eb78f885b54dd215c6d257a4ab4b471 |
| plan.yaml | 1c5d6bfbace6034faebb291fa18b63a42446831b86715258f8722ae32c5fb462 |
| BRIEF.md | f44cb28b5d50d80daefe38231711e4d0850e743ce31ccc750421d5e708b49be2 |
| STATE.md | 5ff2f99108a0ff75f71e430799c045575f7153874030020c70fc07c1709eb7a7 |
| notes/approval-2026-10-05.md | 3eb33e14811933abfa4d74525831beaafa551d3b8fb431a110739d8e0c681eac |
| runs/2026-10-05-2-plan-product/state.yaml | 36e7b842de69b5095a293e446efc08133f34c6320befb40dc5aca7b65f570e66 |
| runs/2026-10-05-2-plan-product/digest.md | 94d6f194c2159f19f1b2f4c50b6617043f26c22ff029b0fe040f6a85f98ba40f |
| runs/2026-10-05-6-plan-product/state.yaml | 7d2f507e693e4919218d8d278f5efa03da8a07cb4e2b9e978049f073d7dc0291 |
| runs/2026-10-05-6-plan-product/digest.md | b8792f929c02fa39ce33dacd49910b74f18f57fd2f06615caf7e36bad269ae22 |
| runs/2026-10-05-3-simplify-eng/state.yaml | 0ace14cf8d3c61be374257e58440d63a65bcaa5e3421bb47a261715f90773f9d |
| runs/2026-10-05-3-simplify-eng/digest.md | d0e28f4d9a801e073c2835ec80d692ddd4b469d84eb52a90563e8703804910de |

## Captured state as observed (not corrected at capture)

- **Binding.** `factory.repo` is `mruangutai/kaya`.
- **Wrong-repository receipt.** In mruangutai/harness: milestone 100, parent #2116, and T-01..T-10 as #2117..#2126, all CLOSED NOT_PLANNED. `build_entry` is `opened`, and there is no `github.repo`. Harness #14 is unrelated (CLOSED COMPLETED) and was not touched.
- **Kaya repository.** Kaya #14 is OPEN and in Plan on project 9. Kaya had no milestones before recovery.
- **Ledger.** `cycles_used` is 1. Plan status is `ready`. The build has not started: runs 4 and 7 are squad engineering with `code_grade: n_a`.
- **Check-state findings before recovery** (installed tooling, `check-state.py --feature FEAT-01-kaya-platform`, exit 1):
  - A DEC-156 digest-contract violation for `2026-10-05-3-simplify-eng`.
  - INV-37: no usable Build-entry receipt (no matching provenance).
  - INV-26 CANNOT VERIFY for #2116..#2126, which are not on the Kaya board.
