{
  "feature_id": "BUG-2181-board-item-add",
  "authorized_by": "operator (mruangutai) directive 2026-11-08: 'start issue://2181. take it to green and clean merge. defer to advisor for questions'; advisor ruling Inv26RoutingAdvisor (2026-11-08)",
  "authorized_on": "2026-11-08",
  "observed": {
    "run_id": "2026-11-08-01-product",
    "return": "harness-product-lead returned VERDICT PASS by final-message object and wrote a fenced record to runs/2026-11-08-01-product/digest.md; both carry an undeclared DIGEST key 'amendments' (empty list)",
    "validator": "validate-digest.py harness-product-lead <verbatim returned object> exited 1: undeclared digest key(s): 'amendments' — the digest contract is closed; the fenced record in digest.md fails identically",
    "work_verified_on_disk": "BRIEF.md (43 lines, approval pending, SC-01..SC-03) and plan.yaml (one task T-01, main-session-direct, approval pending) exist; check-plan-routes 0 violations",
    "precedent": "BUG-2180 run 2026-11-07-01-product closed the same undeclared-key return with --refused-return (#2171)"
  },
  "effects": [
    {
      "effect": "record-cycle-evidence",
      "run_id": "2026-11-08-01-product",
      "digest": {"path": "runs/2026-11-08-01-product/digest.md", "sha256": "0c64a7f412f92bddf85815a6fcf5f139112372a13dacdd6bdd166045c5f67578"},
      "cycles_used": 0,
      "by": "operator",
      "reason": "First-pass patch intake with no send-back; the returned digest reports cycles_used 0."
    }
  ]
}
