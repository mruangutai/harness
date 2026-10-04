# Grilling — OMP write hook judges internal URIs as checkout files (#2003) — 2026-10-03

## Destination
Governed agents under OMP can write `agent://<id>` (messaging) and `xd://report_issue` (defect
reports), and every other write is judged exactly as today.

## Mission
mission: patch
reason: cause known (`preDomain` forwards every write/edit path to check-domain.py); diff bounded to the OMP adapter and its unit test; it narrows an existing check and adds no interface, schema or enforcement surface.
confirmed-by: operator

## Settled
- How does the hook treat a path with a URI scheme? → An allowlist. Only allowlisted schemes skip the file-domain check; every other scheme is refused by name with a clear message, so a new scheme fails closed.
- Which `xd://` devices pass? → Only `xd://report_issue`. Every other device (`ast_edit`, `lsp`, `recall`, …) stays refused, now with a by-name message.
- So the allowlist is exactly `agent://` and `xd://report_issue`.
- Any who-may-message-whom rule for `agent://`? → No; out of scope.
- Does `edit` get the same rule? → Yes. One scheme decision for write and edit, so edit is not the way around it.

## Not yet specified
- none

## Out of scope
- An `agent://` messaging policy: a deliberate rule of its own, later.
- Resolving file-backed schemes (`conflict://`, `local://`, `vault://`, `ssh://`) to real paths: refused by name instead. Resolving them would couple the hook to OMP's URI resolution.
- Read-only `xd://` devices (`lsp`, `recall`, `reflect`) for governed agents.
- The Claude Code host, which has no internal URIs.

## Facts I verified (so pm does not re-derive them)
- `.omp/extensions/harness-hooks.ts` `preDomain()` (line 265) sends write `input.path` and every `extractEditPaths()` path to `check-domain.py` as `tool_input.file_path`, with no scheme check. The post-write path (lines 305-319) does the same for `--post`. Checked at e0bb9814.
- `check-domain.py` has no `scheme://` handling: grep for `://` in it finds nothing.
- `conflict://N` rewrites conflict blocks inside a real checkout file. That is why a blanket scheme skip would be a bypass.
- Seen in the field: FEAT-495's code reviewer (review4) and security reviewer were both refused on `agent://Main` and `xd://report_issue`. Related symptom issues: #1706, #1571, #963.
- DEC-174: the adapter is part of the active enforcement path, so the build is main-session-direct.
