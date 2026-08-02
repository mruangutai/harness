# FEAT-02 T-02 — tail-anchor validate() at the last VERDICT line (GREEN)

**BLUF: Fix landed at `d9b16e5323526d6f02228b48652ded84328a40cb`; both verify
gates hold.** 10 lines added to `validate()` in
`.claude/skills/harness/bin/validate-digest.py` — slice `text` from the last
`^\s*VERDICT:` match before any check; no anchor → whole-text behavior
unchanged. Comment records the WHY (echo-shadowing, BUILD task 22 follow-up).

## Verify gate

1. Fixed validator: `test-validate-digest.py` exit **0** — 28/28 CLI,
   10/10 hook, 2/2 template (36 pre-existing + 4 T-01 cases all green).
2. Pre-fix validator (`VALIDATE_DIGEST_BIN=/tmp/validate-digest-prefix.py`,
   verified byte-identical to `6546b1d^` via git): exit **1**, failing
   EXACTLY the T-01 defect cases —
   - (2) "echo shadow: missing matrix_ok in the real block is not masked by the echo"
   - (3) "echo shadow: lead roll-up must read the real members, not the echo"
   - (4) "[hook] echo shadow [hook]: missing matrix_ok behind an echo is exit 2"
   Case (1) green pre-fix by design (PLAN T-01); no other case affected.

## Hook semantics

`hook_mode()` untouched — the three fail-open pass-throughs (non-harness
agent_type, stop_hook_active, empty message) sit outside `validate()` and the
slice happens inside it, per review-arch.md. Stdlib only; no other file changed.
