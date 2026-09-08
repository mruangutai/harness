# Security Review — BUG-201-depends-on-integrity — c1

**VERDICT: PASS.** No exploitable security surface. This is a same-privilege diagnostics
improvement: the only new/changed sinks for the interpolated text are local `stderr`/`print`
streams read by the same actor who authored the plan content, never a cross-trust-boundary
artifact (GitHub issue/PR/comment, CI-parsed log line, or structured stdout payload).

## Scope decision (measured)

Census of the 3 named production files + 6 test files, all in scope for a look:

- `harness_yaml.py` `_validate_plan_depends_on` (new, ~30 LOC) — pure validation, no I/O,
  raises `PlanSchemaError` (a `YamlParseError` subclass). Traced.
- `factory_claim.py` — `_BlockerCache.plan_error`/`_plan`, `_blocker_gate`'s new `bad_plan`
  arm, `_blocker_reason_text`'s new arm. Traced end to end (below).
- `gh-sync.py` — `refuse(msg, stream=None)` widened to accept a stream; `_projected_for` and
  `_status_plan_doc` now print the validator's `str(exc)` on `refuse`/stderr instead of
  swallowing to `{}`/`None`. Traced end to end (below).

**Sink trace — where does the newly-printed text go?**
- `factory_claim.py:_blocker_reason_text` → consumed at `factory_claim.py:382-386` only as
  (a) a `print(..., file=sys.stderr)` skip line, or (b) `factory_cli.refuse(...)` →
  `factory_cli.fail` → `print(..., file=sys.stderr)` then `sys.exit(2)`. Grepped every caller
  of `factory_cli.refuse`/`fail`/`message`/`body` (`factory_cli.py:32-96`): all print to
  `sys.stderr`, never build a `gh` argv, never touch the one stdout JSON payload the winner
  path emits (`factory_claim.py` §7, unreached once a candidate is gated).
- `gh-sync.py:refuse` → `print(f"gh-sync: REFUSED — {msg}", file=stream)` + `sys.exit(2)`;
  `_status_plan_doc`'s new line is a bare `print(..., file=sys.stderr)`. Neither function is
  on a path that builds a `gh issue comment`/`gh pr comment`/milestone-body argv — grepped
  `gh_issues.py`, `gh_board.py`, and every `cmd_*` in `gh-sync.py` for a call built from
  `_projected_for`'s or `_status_plan_doc`'s return value beyond the station-map dict itself;
  none forward the exception text anywhere.
- CI (`.github/workflows/tests.yml`) never invokes `factory_claim.py` or `gh-sync.py` — only
  `check-plan-routes.py`, `check-instruction-paths.py`, `layout_migration.py`, `check-state.sh`.
  So none of this diagnostic text reaches an Actions log line or a `::error::` annotation that
  another automation greps.

**Conclusion:** the "newly surfaced text" is local, human-facing `stderr` only. No new
listener reads it.

## Findings

None at med/high/critical. One **info**-level observation, not gating:

- `harness_yaml.py:~415` (`_validate_plan_depends_on`) builds `pairs = ", ".join(f"{tid} to
  {entry}" ...)` from `str(entry)` where `entry` is an un-typed `depends_on` list element —
  YAML permits it to be a multi-line string, a mapping, or contain control/ANSI bytes. That
  string eventually reaches a single `print(..., file=sys.stderr)` line in `gh-sync.py`/
  `factory_claim.py`, so a crafted `depends_on` value could span visual lines in the
  operator's terminal. This is **not a privilege boundary crossing**: writing `depends_on` in
  `plan.yaml` already requires the same commit/write access as reading the diagnostic output
  it would corrupt (same actor, same trust level — P-02), and no downstream consumer parses
  these lines by position/count (confirmed above — no CI grep, no structured payload). Sole
  actionable improvement would be `repr()`-style quoting in the join for terminal hygiene;
  not worth gating.

## Boring checks, confirmed negative

- No new dependency (no new `import` lines beyond `os` in `factory_claim.py`, already
  imported).
- No new subprocess/shell call in any of the three files (grepped the diffs; `refuse()`'s
  widening only adds a `stream` kwarg to an existing `print`).
- YAML loader unchanged — `_validate_plan_depends_on` runs post-parse, on the already-loaded
  `dict`; `harness_yaml.load_file`/`load_str` untouched by this diff.
- No auth/secret path touched — grepped the full 3-file diff for token/secret/credential
  shaped strings; none present.
- No new file write — `_validate_plan_depends_on` is read-only; the two `gh-sync.py` sites
  changed only add a `print`, no new `open()`/write.
- Absolute filesystem paths in the new `bad_plan` messages are not a new leak: the pre-diff
  `no_plan` case already interpolated the same `plan_path` into an identical-shaped stderr
  line (`factory_claim.py:194-197`, unchanged by this diff).

## Threat model

| boundary | STRIDE | mitigated |
|---|---|---|
| plan.yaml content → CLI stderr diagnostic | Information disclosure | true — sink stays local, single-actor, traced above |
| plan.yaml content → GitHub-facing artifact (issue/PR/comment) | Tampering / spoofed record | true — no code path forwards the new text there (traced) |
| plan.yaml content → CI-parsed log line | DoS / spoofed gate result | true — CI never invokes these two tools |

## Open questions

None blocking.
