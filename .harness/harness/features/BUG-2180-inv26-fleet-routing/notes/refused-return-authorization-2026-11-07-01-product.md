{
  "feature_id": "BUG-2180-inv26-fleet-routing",
  "authorized_by": "operator (mruangutai) standing directive 2026-11-07, recorded verbatim in BUG-20261006-fleet-planning-recovery notes/operator-ship-directive-2026-11-07.md; advisor ruling Inv26RoutingAdvisor",
  "authorized_on": "2026-11-07",
  "observed": {
    "run_id": "2026-11-07-01-product",
    "return": "harness-product-lead returned VERDICT PASS by final-message object twice (initial return and requested re-yield); the yield hook never appended a durable record (#2171), so runs/2026-11-07-01-product/digest.md holds the lead's prose only",
    "validator": "validate-digest.py harness-product-lead <verbatim returned object> exited 1: undeclared digest key(s): 'amendments' — the digest contract is closed",
    "work_verified_on_disk": "BRIEF.md (46 lines, approval pending, SC-01..SC-04) and plan.yaml (one task T-01, main-session-direct, approval pending) exist; check-plan-routes 0 violations and plan-merge check 2 anchors 0 failures per the pm receipt notes/research-inv26-patch-intake.md",
    "precedent": "BUG-2161 and BUG-2169 closed undeclared-key lead returns with --refused-return after verifying the work on disk (#2171)"
  },
  "effects": [
    {
      "effect": "record-cycle-evidence",
      "run_id": "2026-11-07-01-product",
      "digest": {"path": "runs/2026-11-07-01-product/digest.md", "sha256": "4bb8a2361fcecfea98e9eebf0f95b28a607882a298e15107f8ab3e6bb43e87cb"},
      "cycles_used": 0,
      "by": "operator",
      "reason": "First-pass patch intake with no send-back; the lead's digest states 'Cycles used: 0.'"
    }
  ]
}
