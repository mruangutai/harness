# Build ruling by delegated authority — FEAT-2397 T-05 — 2026-11-22 — stale spots outside the list

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorC8StaleSpots`). Raised by the T-05 builder.

**Gap.** Two stale spots sit outside T-05's file list:
1. `BUILD.md:948` cites DEC-111, which T-05 struck (successor DEC-233).
2. `.harness/team-config.yaml:96,163` and `templates/team-config.yaml:82,131` still carry
   `provision:` values saying "NOT a Claude capability" and "Claude Code plugin — available".
   SPEC §3.1/§3.2 now say "host integration" and "host capability".

**Ruling: A, narrowed.**
- **BUILD.md: no edit.** Line 948 sits in the `## Critical files` table, inside the declared
  historical boundary ("§0b onward", BUILD.md:21-23). A reader following DEC-111 lands on the
  strike record naming DEC-233; repointing would falsify history.
- **team-config: reword the four `provision:` values** as recorded deviations in T-05.
  `provision:` is a parsed value that no script consumes, but dev-ops reads it at init, and the
  template seeds it into every new project.
  - Change only those four strings, matching SPEC §3. Keys, structure, domains and rules stay
    unchanged, and no new DEC is created.
  - The rows are recorded in `notes/t05-doctrine.md` with the same successor as the SPEC
    §3.1/§3.2 edits.
- **Validate disclosure (required).** The `.harness/team-config.yaml` edit makes
  `test-check-plan-routes.py` red in this linked worktree (owner-manifest DEVIATION against the
  control plane). That is the intended detector under the FEAT-2337 GC-03 ruling and backlog
  #2387. Clone and CI runs are green. The template edit needs no disclosure.
