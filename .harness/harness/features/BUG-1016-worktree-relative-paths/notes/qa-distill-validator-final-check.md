# QA final check — validator lead distill (BUG-1016)

BLUF: PASS. check-expertise exit 0; all four landed entries match receipts verbatim; lead grants resolve. No edits made; cycles_used stays 0.

## check-expertise.py (exact command, four files)
Exit **0**.
- harness-code-reviewer.md: OK
- harness-security-reviewer.md: OK; ADVISORY :19 G-01 names 'DEC-100' (pre-existing, not a landed entry)
- harness-ui-reviewer.md: OK
- harness-pm.md: OK; ADVISORY :3 P-01 names '.harness/' (pre-existing)

## Per-section entry counts (Python)
| file | Patterns | Gotchas | Outcomes | Open |
|---|---|---|---|---|
| harness-code-reviewer | 15 | 15 | 10 | 0 |
| harness-security-reviewer | 15 | 15 | 10 | 0 |
| harness-ui-reviewer | 15 | 15 | 10 | 0 |
| harness-pm | 15 | 15 | 10 | 0 |

## Landed entries vs receipts
Live entry text found verbatim in its receipt: G-04 code-reviewer (review-harness-code-reviewer-distill-validator.md), P-15 security (review-harness-security-reviewer-distill-validator.md), G-15 UI (review-harness-ui-reviewer-distill-validator.md), O-14 pm (research-...-goalcheck-distill-validator.md). All four match.

## Lead grants (check-domain.py --resolve)
- .harness/expertise/harness-validator-lead.md -> harness-validator-lead, exit 0
- .harness/harness/expertise/harness-validator-lead.md -> harness-validator-lead, exit 0
