{
  "feature_id": "FEAT-01-kaya-platform",
  "authorized_by": "operator (mruangutai), main OMP session",
  "authorized_on": "2026-11-07",
  "directive": "review these three ticket: #2172 #2173 #2174 ... once done, let's tackle them one at at time. i want you to fix each one, defer to the advisor for questions, and take each to a clean and green merge.",
  "effect_definitions": [
    "https://github.com/mruangutai/harness/issues/2172",
    "https://github.com/mruangutai/harness/issues/2173",
    "https://github.com/mruangutai/harness/issues/2174"
  ],
  "repair_feature": "BUG-20261006-fleet-planning-recovery (T-03 #2157, T-04 #2158, T-05 #2159)",
  "origin": "Authentic Kaya planning record committed byte-for-byte in its own planning worktree at 70da6e14 (feat/FEAT-01-kaya-platform), never read from the repair checkout",
  "canonical_repository": "mruangutai/kaya",
  "originals": {
    "feature.json": "986da0d21828e4f492857f215d9f548f7eb78f885b54dd215c6d257a4ab4b471",
    "plan.yaml": "1c5d6bfbace6034faebb291fa18b63a42446831b86715258f8722ae32c5fb462",
    "notes/approval-2026-10-05.md": "3eb33e14811933abfa4d74525831beaafa551d3b8fb431a110739d8e0c681eac"
  },
  "effects": [
    {
      "effect": "record-refusal",
      "run_id": "2026-10-05-3-simplify-eng",
      "digest": {"path": "runs/2026-10-05-3-simplify-eng/digest.md", "sha256": "d0e28f4d9a801e073c2835ec80d692ddd4b469d84eb52a90563e8703804910de"},
      "by": "operator",
      "reason": "Ledger BLOCKED refused lead return: prose-only digest without the required structured mapping (DEC-156). Preserve bytes, BLOCKED verdict and 0 cycles; successor 2026-10-05-4-simplify-eng is not retroactive acceptance (#2174)."
    },
    {
      "effect": "record-cycle-evidence",
      "run_id": "2026-10-05-2-plan-product",
      "digest": {"path": "runs/2026-10-05-2-plan-product/digest.md", "sha256": "94d6f194c2159f19f1b2f4c50b6617043f26c22ff029b0fe040f6a85f98ba40f"},
      "cycles_used": 0,
      "by": "operator",
      "reason": "Original FAIL is a worst-member roll-up with no send-back; its digest reports cycles_used 0 and states 'No send-back occurred; cycles_used 0' (#2173)."
    },
    {
      "effect": "record-cycle-evidence",
      "run_id": "2026-10-05-6-plan-product",
      "digest": {"path": "runs/2026-10-05-6-plan-product/digest.md", "sha256": "b8792f929c02fa39ce33dacd49910b74f18f57fd2f06615caf7e36bad269ae22"},
      "cycles_used": 1,
      "by": "operator",
      "reason": "Original FAIL roll-up; its digest reports cycles_used 1 for one designer-owner send-back: 'Seven actual member executions including one designer-owner send-back: cycles_used=1' (#2173)."
    },
    {
      "effect": "recover-mirror",
      "from_repo": "mruangutai/harness",
      "to_repo": "mruangutai/kaya",
      "mode": "full",
      "plan_sha256": "1c5d6bfbace6034faebb291fa18b63a42446831b86715258f8722ae32c5fb462",
      "by": "operator",
      "reason": "Approval transaction mirrored into mruangutai/harness (milestone 100, parent 2116, tasks 2117-2126, all closed not_planned; Harness #14 unrelated and untouched). No implementation started: full replacement in mruangutai/kaya from the unchanged signed plan, projecting signed source #14 (#2172)."
    }
  ]
}
