# Observations — harness-pm — FEAT-22-docs-layout-migration

- 2026-08-15: proving a multi-grep `verify:` block against a mutated file via
  `bash -c "$BLOCK" bash <(sed ... file)` is INVALID. Process substitution is a one-shot stream: the
  first grep consumes it and every later grep in the block reads empty, so absence checks pass
  spuriously and presence checks fail spuriously. My first discrimination ladder for T-03 reported
  ":111 fails" on all five variants for exactly this reason and had to be discarded. Fix used: one
  fresh `<(...)` per grep, plus a whole-block `bash -n` for syntax. A real temp file was not an
  option — bash-write-guard blocks redirects outside the pm domain, and it matches the literal
  string, so `$D/x` is denied even when `$D` expands into the domain.
- 2026-08-15: `../../../.claude` does NOT contain `-> ../../.claude` as a substring even though it
  does contain `../../.claude`. Anchoring the negative grep on the `-> ` prefix is what makes a
  climb-count assertion possible at all; without the anchor the correct fix trips its own guard.
