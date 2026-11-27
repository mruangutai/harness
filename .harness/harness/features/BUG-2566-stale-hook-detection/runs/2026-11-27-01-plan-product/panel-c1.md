# Plan panel fan-in — BUG-2566 cycle 1

All three readers ran. Findings below are transcribed at each reader's own severity and kind;
reader notes: `notes/review-harness-code-reviewer-plan-c1.md`, `notes/review-harness-ui-reviewer-plan-c1.md`;
fable-advisor has no write grant, so its findings reach disk only here.

## Host assessment for apply (dispositions are pm's to execute; severities are not revised)

- **code-reviewer #2 and ui-reviewer #1 are one defect** (schema directory hashed as one key, so the
  refusal cannot name the changed file). Fix in T-01: per-file entries for the schema directory;
  state what is named when the whole directory is removed.
- **code-reviewer #1 (merge order)**: the ordering is settled above this run — grilling "builds stay
  sequential", dispatch "treat its changes as landing first". Keep 2565-first as an explicit plan
  decision the operator signs; delete every "either merge order works" claim; make the precondition
  grep match only the live import (it must not self-match new fingerprint code on a resumed build).
- **code-reviewer #3 (non-regular entry hang)**: fix in T-01 (skip/record non-regular entries without reading).
- **code-reviewer #4 (DEC-204)**: add a `decisions_affected` amend row for DEC-204 with successor D-02
  and give a task DECISIONS.md in `files:`; record keeps the reviewer named (DEC-100, DEC-202, DEC-237, DEC-251) if they are affected.
- **code-reviewer #5 (SC-04 mutant evidence)**: schedule the mtime-mutant run in T-01.
- **code-reviewer #6 (proportionality, scope task)**: pm's to trim at apply.
- **fable-advisor #1 and #2 contradict operator-settled scope** (grilling §Settled: "the two extension
  modules … plus the digest schema directory"; dispatch constraint: "covers exactly"). pm must NOT drop
  either entry. Keep them in the plan; carry both as non-blocking signature questions with the reader's
  evidence (post-2565 hook never reads schemas/digest; digest-schema.ts permanently absent).
- **fable-advisor #3 (BLOCKED-yield carve-out)**: operator constraint is "every governed tool call refused".
  Keep D-02; record the DEC-204 amendment (above) and surface the carve-out as a signature question (merges with pm's Q-02).

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: plan scope and architecture read, cycle 1; verdict FAIL with 6 findings
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: should-not-exist read, cycle 1; 3 findings, no mission-scope objection
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Mode A read, in scope (operator-facing refusal text); verdict FAIL with 1 finding
  findings:
    - reader: code-reviewer
      summary: T-01 cannot build before BUG-2565 despite claiming either merge order works.
      severity: high
      kind: substance
      why: The current base contains the live named digest-schema.ts import, so plan.yaml:66 stops the build. If only the stop is removed, plan.yaml:86 replaces or removes a required module before import. The grep can also match the new fingerprint reference on a resumed build.
    - reader: code-reviewer
      summary: T-01 cannot name changed schema files in the refusal.
      severity: high
      kind: substance
      why: A common.json change or extra.json addition alters only the directory-key hash in plan.yaml:73–76; the formatter can name only the directory, while SC-01 and plan.yaml:87 require the changed relative path.
    - reader: code-reviewer
      summary: A non-regular schema entry can hang the OMP process and stop Main recovery.
      severity: med
      kind: substance
      why: The synchronous directory walk reads every name without checking file kind; reading a FIFO can wait indefinitely at import or preflight, so unchecked Main calls cannot progress.
    - reader: code-reviewer
      summary: The decisions record omits the held-run yield contract changed by D-02.
      severity: med
      kind: substance
      why: DEC-204:6608 leaves BLOCKED yield as the held-run exception; stale held runs now cannot use it. Amend the clause to state precedence, not strike the otherwise-live rule. Record keeps for DEC-100, DEC-202, DEC-237 and DEC-251.
    - reader: code-reviewer
      summary: The task does not schedule SC-04’s timestamp-mutant evidence.
      severity: med
      kind: substance
      why: The plan schedules only a run against the old hook; those tests can fail because the new export is missing without proving that they distinguish timestamp comparison from content hashing.
    - reader: code-reviewer
      summary: T-01 exposes unused fingerprint internals and gates on the export.
      severity: low
      kind: proportionality
      scope: task
      why: Planned callers use only staleHookRefusal and registerHarnessHooks. Keeping hashing and formatting private lets the fingerprint representation change without forcing an unnecessary public interface change.
    - reader: ui-reviewer
      summary: T-01 reports the schema directory instead of the changed, added, or removed schema file.
      severity: med
      kind: substance
      why: plan.yaml:73–76 hashes the schema directory into one compare key and prints only changed keys; BRIEF.md:32–40 and plan.yaml:87 require each refusal to name the changed path relative to the loaded checkout.
    - reader: should-not-exist
      summary: "Drop (or re-decide with the operator) the schemas/digest directory in the fingerprint: after the mandated 2565-first ordering, the loaded hook never reads it."
      severity: med
      kind: substance
      scope: task
      why: Every runtime use of the schema directory (DIGEST_SCHEMA_DIR at harness-hooks.ts:807, 815, 848) is deleted by BUG-2565 and T-01 blocks on the pre-2565 hook, so the running process never consults schemas/digest; schema regeneration then refuses every governed call fleet-wide (false positive) while a .omp/agents frontmatter edit goes undetected (false negative).
    - reader: should-not-exist
      summary: The digest-schema.ts fingerprint entry guards a state the plan's own precondition makes unreachable; three SC-01 cases test it.
      severity: low
      kind: substance
      scope: task
      why: T-01's precondition means 2566 never lands before 2565, so digest-schema.ts is permanently absent once this code loads; the entry is a tripwire for one filename while any other new module in .omp/extensions stays undetected, and three test cases exercise unreachable states.
    - reader: should-not-exist
      summary: D-02's removal of the BLOCKED-yield exception (unlike BUG-1898's held-run gate) strands every in-flight subagent the moment staleness trips, with no operator decision recorded.
      severity: low
      kind: substance
      scope: task
      why: The held-run gate (harness-hooks.ts:1755) exempts yield so a stopped agent can still terminate and record why; under D-02 every specialist's yield, including VERDICT BLOCKED, is refused with a remedy only the operator can perform, stranding completed work in transcripts.
```
