# Expertise — harness-security-reviewer

## Patterns

- **P-01** — This codebase has no network, database, or browser surface. The only place untrusted
  input crosses a boundary is the **hook payload**: `.claude/skills/harness/bin/*.{py,sh}` registered
  in `settings.snippet.json` read JSON on stdin and parse **agent-authored text**
  (`last_assistant_message`) or agent-supplied tool params. Start every audit at the hook scripts and
  at what they do with payload-derived strings; everything else in the repo is Markdown.

## Gotchas

- **G-01** — Hook exit codes: **only `exit 2` blocks.** Any other non-zero exit is a *non-blocking*
  error and execution proceeds (DEC-100; `check-domain.sh:13-14` carries the verified comment). So an
  uncaught exception in a hook does **not** wedge the agent — it silently disables the gate for that
  invocation. When auditing a hook, rate crashes as fail-open (control bypass), not as DoS, and check
  whether the script wraps its own logic in `try/except` rather than only its payload parse.
