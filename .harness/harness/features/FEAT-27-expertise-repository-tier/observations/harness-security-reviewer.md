# Observations — harness-security-reviewer — FEAT-27

- 2026-08-19: First security pass on FEAT-27 (`b4659cd..9b929de`, review_sha `9b929de`). The
  `^harness-[a-z0-9-]+$` regex plus quoting closes path traversal/glob/command injection via
  `agent_type` for real (character-class argument, not convention) — verified by tracing all 5 uses
  of `$agent` in `inject-expertise.sh`, all quoted, none reach eval/subprocess. Validation
  (`:21-29`) runs before any path variable is assigned (`:31-33`, `:68`) — no build-before-validate
  ordering bug. `team-config.yaml`'s 16 new `.harness/*/expertise/harness-<self>.md` grants do not
  widen cross-agent write power — `harness_boundary.py:glob_to_re` maps bare `*` to `[^/]*`
  (single path segment, verified not to cross `/`), and the agent-name field of every grant line is
  a literal string, so each agent can only ever write its own name's file under any one repo
  segment.
- 2026-08-19: The real open item is cross-repository Expertise bleed — `inject-expertise.sh` globs
  and injects EVERY `.harness/<segment>/expertise/<agent>.md` on every spawn with no way to know
  which repo the spawn serves (proven live by `test-inject-expertise.py` case2, two segments fire
  at once). This is not undiscovered — `plan.yaml` D-01 names it explicitly, including the
  unbounded-aggregate-size cost, and defers a fix to "unit 7" as a signed, approved decision. Rated
  `med` not `high` on precondition-absent grounds: only one real segment ("harness", self-
  referential) exists in the shipped tree today; "kaya" is fixture-only. Worth a future reviewer
  re-checking severity once a second, genuinely distinct repository segment goes live — that is the
  trigger that would make this exploitable rather than theoretical.
- 2026-08-19: `check-expertise.sh`'s repository-token advisory scan (issue 340) is structurally
  incapable of gating — appended to a separate `advisories` list never read by
  `sys.exit(1 if failed else 0)`. Confirmed by reading control flow, not by re-running the suite
  (O-01 in my own craft Expertise: re-running an already-green suite is confirmatory, not
  identity-level evidence).
- 2026-08-19: Orchestrator's own carried Expertise entry (moved from `OQ-02` to
  `.harness/harness/expertise/harness-orchestrator.md` O-01 verbatim) already documents that no
  Expertise file has lineage protection — the sole control against content-level (semantic) poisoning
  of any Expertise file, craft or repository tier, is human PR review. Repository tier multiplies
  the number of such self-writable, per-spawn-injected files per agent from 1 to 1+N without closing
  that gap. Not new, but the blast radius grew — worth remembering for the next feature that adds
  another writable per-spawn-injected surface.
