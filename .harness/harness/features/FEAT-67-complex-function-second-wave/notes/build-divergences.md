# FEAT-67 — build divergence ledger

Base `00c7219e4026081e70614647f3f98726afb2c381`. Every owning-suite comparison is exit status +
stdout bytes + stderr bytes, after replacing each checkout's own absolute root with `<checkout>`
on both sides (the ruled normalisation; FEAT-66 D-09) — three `ok` lines in
`test-validate-digest.py` print the agent file's absolute path.

## Output divergences

None. 11/11 owning suites identical to the baseline at every production commit
(`b8eabf48`, `d99eea6a`, `107f7c58`) and after the simplify apply; the clean-pin receipt
(`notes/clean-pin-byte-receipts.md`) is the one that counts.

## Structural decisions (not output divergences; recorded so review need not re-derive them)

- D-01 `check-omp-port.check` — seven ordered check functions, not five: the AGENTS.md,
  config, agent-file, provider, skills-symlink, extension and door blocks each append to
  `errors` independently, and the grilling's "five" undercounted the symlink and door blocks.
  `CHECKS` is the tuple, `check` concatenates in tuple order. `provider_file_errors` returns
  the read error alone where the inline `try` covered the whole block — the only statement
  that could raise `ArtifactAccessError` was the load, so the set of messages per file is
  unchanged. `config_errors` and `agent_file_errors` grade exactly 2 (the grader's exception).
- D-02 `approval_guard` — the per-entry context is an immutable namedtuple
  (`_GovernedFragment`) built once per matching grant; `deny_fragment`, an inline closure
  rebuilt per entry, is the module-level `_deny_fragment(fragment, why)`. The tool's rule is
  selected once before the grant loop (simplify fold-in S1/A1): the inline form re-tested
  `_tool` per entry and, for a tool with no rule, exhausted the loop deriving contexts nothing
  read — no output on that path, so the early return is output-identical. `_edit_introduce_limb`
  grades exactly 2; splitting its per-line body would land at 3, which the bar rejects.
- D-03 `approval_guard` — the `denied_a` flag is gone (simplify S2): `_deny_fragment` ends in
  `sys.exit(2)`, so the flag was `False` on every path that reached limb B. Pre-existing dead
  logic that the decomposition had given a name; removed rather than documented.
- D-04 `parse_digest` — `_next_field` returns `len(body)` as the next cursor on a dedent below
  the base indent, which is the `break`; every other skip returns `i + 1`. `_block_list_step`
  returns `(cur, cur_is_brace, item_indent)` and appends a closed entry to `items` in place —
  the one in-place channel; altitude finding A3 (return the closed entry instead) is a backlog
  row, not applied, because it reshuffles a signed boundary for no behaviour gain.
- D-05 `tests/unit/test-code-grade.py` — the stale `("validate-digest.py", "parse_digest"): 1`
  self-grading exemption is removed (FEAT-66 MF-04 precedent: an allowlisted grade that no
  longer matches fails the unit kind).
- D-06 `import collections` added to check-domain.py as its own line after the existing
  import line (the namedtuple context needs it).

## Simplify pass (four read-only scouts, one per angle; applied before the pin)

Applied:
- S1/A1 — rule selected once before the grant loop; `_apply_fragment_rule` and its boolean
  protocol deleted.
- S2 — `denied_a` and `_edit_overlap_limb`'s unreachable `return True`s removed.
- S3/A2 — two plain guards (`entries is None`, `disk is None`) instead of one ternary `None`.
- S4 — the three FEAT-67 driver comments reduced to the one fact each that the code does not
  show (order is the contract; only Write/Edit have a rule; helpers return value + cursor).
  The feature tag stays: new facts carry the feature id (repo rule).

Applied then reverted under the one-fix ceiling:
- S5 — folding `_inline_value` into `_next_field` took `_next_field` to grade 3 (cognitive);
  reverted. `_inline_value` stays as the two-line dispatch.

Skipped (reason):
- R1 — append `runtime_pin_errors`/`runtime_probe_errors` to `CHECKS` and reduce `main()`:
  changes `check()`'s return (the suite calls it) and edits `main`, both outside SC-03's "only
  the three functions". → backlog.
- R2 — one `_key_token(line)` for `_signature_child_keys` and `_edit_introduce_limb`: the two
  spellings are NOT byte-equivalent (`"key :"` → `"key "` on one side, `"key"` on the other),
  so unifying is a behaviour change on a malformed-line edge. Real drift risk in a bypass-
  sensitive limb. → backlog.
- A3 — `_block_list_step` returns the closed entry: signed-boundary reshuffle. → backlog.
- A4 — `agent_files_errors` vs `agent_file_errors` one-character names: leave (reader's own
  verdict).
- Efficiency: empty return.
