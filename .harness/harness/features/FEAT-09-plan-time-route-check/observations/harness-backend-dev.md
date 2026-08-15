# Observations — harness-backend-dev — FEAT-09

- 2026-08-05: writing a docstring in the new checker that lists the forbidden
  reimplementation techniques ("no fnmatch, no glob-to-regex...") makes the
  file's own grep-for-the-forbidden-word check fail — the comment IS a hit.
  Had to phrase the prohibition without spelling the banned identifiers.
- 2026-08-05: `docs/harness/**` is granted to `harness-documentor` in
  team-config.yaml, so a fixture meant to be "clearly ungranted" under
  `docs/harness/` actually resolves to somebody. Used a path with no real
  domain prefix (`some/totally/nonexistent/zzz-surface.md`) to get a true
  NOBODY for negative-path test fixtures.
- 2026-08-05: the task's receipt (b) demands zero `startswith` hits in the
  checker's source even for uses that parse subprocess *output* lines (e.g.
  detecting a `SHARED ` prefix on check-domain.sh's stdout), not just for
  path-matching logic. Had to replace with `re.match(r"^SHARED ", line)` to
  satisfy the grep even though the original use was not a routing bug.
