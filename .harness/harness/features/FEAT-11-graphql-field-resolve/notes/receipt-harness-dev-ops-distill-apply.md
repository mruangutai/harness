# Receipt — harness-dev-ops — distill-apply (read-only expertise check)

BLUF: `check-expertise.sh` exits 1 (non-zero, expected). One FAIL, on
`harness-documentor.md`. No failure line names `harness-eng-lead.md`.

## Command

```
.claude/skills/harness/bin/check-expertise.sh .harness/expertise/
```

## Verbatim stdout+stderr

```
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-dev-ops.md
FAIL .harness/expertise/harness-documentor.md
  - line 43: G-04 is 53 words — cap is 50; a rule, not a story
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```

## Exit code

`exit=1` (captured via `echo "exit=$?"` immediately after the run, output
redirected to a file first — not through a pipe, per Expertise gotcha G-02
which flags `${PIPESTATUS[0]}` as unreliable under this tool's default zsh).

## Does any failure line name `harness-eng-lead.md`?

**No.** The only `FAIL` line names `.harness/expertise/harness-documentor.md`,
with detail `- line 43: G-04 is 53 words — cap is 50; a rule, not a story`.
This matches the pre-existing, already-confirmed backlog item cited in the
dispatch (G-04, 53 words vs 50-word cap). `harness-eng-lead.md` reports `OK`.

## Scope note

No files under `.harness/expertise/` were edited. This receipt is the only
file written.
