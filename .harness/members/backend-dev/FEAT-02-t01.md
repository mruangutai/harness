# FEAT-02 T-01 — echo-shadowing regression cases (RED)

**BLUF: RED state proven and committed at `6546b1dbf2dbb352ca6d6cab483062e66cadaf9c`.**
Four cases appended to `.claude/skills/harness/bin/test-validate-digest.py`;
`validate-digest.py` untouched. Suite exits 1 with exactly the new
defect-capturing cases failing; all 36 pre-existing cases pass (25 CLI + 9
hook + 2 template).

## Per-case pre-fix status

| Case | Pre-fix | Why |
|---|---|---|
| (1) "echo shadow: valid real FAIL after a template echo still validates" | ok (green) | By design (PLAN T-01): echo validates trivially pre-fix; case pins post-fix routing |
| (2) "echo shadow: missing matrix_ok ... not masked by the echo" | FAIL — got PASS, no `matrix_ok` mention | Echoed complete qa block shadows the real return |
| (3) "echo shadow: lead roll-up must read the real members, not the echo" | FAIL — got PASS, no "worst" mention | Echoed all-PASS lead block shadows; roll-up never sees the FAIL member |
| (4) [hook] "missing matrix_ok behind an echo is exit 2" | FAIL — exit 0, empty stderr | Hook mode inherits the same first-match anchors |

## Implementation notes for T-02

- Per advisory A-1, echo blocks are FILLED, schema-valid, PASS-shaped per
  persona (`QA_ECHO`, `LEAD_ECHO` constants) — a bare-placeholder echo is
  rejected on missing fields pre-fix and would not reproduce the defect.
- A-3 confirmed: the suite's mentions check lowercases both sides
  (`test-validate-digest.py`, run_cli_cases/run_hook_cases), so case (3)'s
  `mentions="worst"` matches the validator's "WORST".
- Pre-fix binary verified byte-identical to HEAD's validate-digest.py at
  `/tmp/validate-digest-prefix.py` (A-2 satisfied for now; regenerate from
  this commit's parent if lost).

## T-02 verify gate (unchanged from PLAN)

Post-fix: suite exits 0; and
`VALIDATE_DIGEST_BIN=/tmp/validate-digest-prefix.py ./test-validate-digest.py`
must fail with exactly cases (2)-(4).
