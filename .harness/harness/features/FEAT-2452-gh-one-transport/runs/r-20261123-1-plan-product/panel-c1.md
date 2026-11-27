# FEAT-2452 independent plan panel — cycle 1

Scope requests three substance repairs and two form repairs; advisor requests two task-only proportionality trims. No mission downgrade. Scope note: `notes/review-harness-code-reviewer-plan-c1.md`; design note: `notes/review-harness-ui-reviewer-plan-c1.md` (both under this feature). Advisor findings transcribed from its terminal return. The DEC-138 literal implementation conflict is a nonblocking question for PM disposition/host escalation, not permission to amend settled policy. The run exit digest adds goalcheck to this roster.

```yaml
DIGEST:
  severity_max: high
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: Reviewed pending draft scope, traceability, architecture and governing decisions; repairs recorded below.
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: Independently challenged unnecessary work; mission proportionate, two task-level trims.
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Self-scoped out after reviewing transport and existing CLI handling; no visual or interaction surface, DESIGN.md or prototype required.
  findings:
    - kind: substance
      scope: none
      severity: high
      reader: scope
      summary: T-02/T-03 need a safe and discriminating caller-level single-override red run
      why: T-01’s factory-only override works at baseline. Removing the second pin in the mirror fixture leaves the old executable resolving gh from inherited PATH; on a credentialled host the red run can reach live GitHub, and SKIP/0 alone cannot prove confinement. Use only FACTORY_GH plus an offline fallback sentinel, and assert the caller and telemetry transcript.
    - kind: substance
      scope: none
      severity: med
      reader: scope
      summary: T-04 must distinguish an HTTP 404 process failure from a status-zero strict-JSON failure
      why: If gh exits 0 with malformed JSON and an HTTP 404 marker in stderr, marker-only classification can suppress the typed decode failure and expose blocked work. Require a completed nonzero process and explicit HTTP 404 before treating the result as absence.
    - kind: substance
      scope: none
      severity: med
      reader: scope
      summary: T-02 must migrate two stale recovery test patches and verify mirror telemetry after cutover
      why: test-gh-sync-open.py:602,636 patch the deleted module GH attribute, not a GH_SYNC_GH environment assignment. Left unchanged, they error before exercising durable intent. Move both to FACTORY_GH; bind the mirror telemetry assertion in test-gh-cost-log.py to T-02 or the final cumulative unit gate because T-01 observes the old wrapper.
    - kind: form
      scope: none
      severity: med
      reader: scope
      summary: Decision dispositions omit DEC-220 and DEC-167 and do not account for DEC-138’s explicit implementation clause
      why: T-02 changes failure interpretation at DEC-220’s pending-create/Build-entry interface; T-04 moves DEC-167’s parent lookup and mandatory gist write. Both policies stay and warrant keep rows. DEC-138’s present-tense gh_bin() location and separate-runner text at DECISIONS.md:3133–3140 must be accounted for, not silently bypassed by quoting only its best-effort clause.
    - kind: form
      scope: none
      severity: low
      reader: scope
      summary: T-05 should name the live probe receipt and distinguish capability readback from SKIP/0
      why: The registered default read-only probe exits zero both after an authenticated capability read and when auth or the query fails. Record CAPABILITY PRESENT or CAPABILITY ABSENT for pinned github.repo; a SKIP is not live evidence.
    - kind: proportionality
      scope: task
      severity: low
      reader: should-not-exist
      summary: Divergence (e)'s planned realization already exceeds its settled cost-free bar — a dual-spelling 422 matcher ("already exists" text plus structured "already_exists") and a five-scenario regression matrix in T-02 for an unreported behavior
      why: >-
        The grilling settled (e) as precision, first to cut, keep only if it costs nothing at the seam. The verified cost-free form exists in-tree: create_ref's local case-insensitive "422" AND "already exists" conjunction over captured streams (factory_gh.py:1080-1088). T-02 goes beyond that precedent by also accepting the structured already_exists spelling "when present" and mandating 422-existing lookup/success, 422-other-validation, 401, network, and launch-failure-no-lookup regressions — the largest new-test cluster in T-02 — while simultaneously removing today's transient-failure recovery via title lookup (gh-sync.py milestone path, facts :1181-1199). Nobody has reported the current lookup as a defect. Consequence: implementer and QA hours on a cosmetic narrowing, plus a matcher coupled to gh's error-body spelling that invites growth whenever that spelling drifts. The need for a second spelling is itself the cost signal: recommend the implementer treat it as the trigger for the already-sanctioned cut lever (keep current lookup behavior, drop (e) and its matrix) rather than widening the matcher. [unverified: actual gh 422 body spelling across versions]
    - kind: proportionality
      scope: task
      severity: info
      reader: should-not-exist
      summary: T-05's instruction to fold issue 893/1542/13 "repaired evidence" into github-mirror.md embeds changelog material in a living, agent-loaded policy reference
      why: >-
        SC-06's caller-to-failure-policy table is current policy and belongs in the reference, but T-05's intent additionally directs including "the issue 893 single-override closure and issues 1542/13 repaired evidence in the policy explanation." Repaired-issue provenance belongs in the feature ship record and commit trail; in the reference it is historical narrative that charges every future agent loading github-mirror.md context for facts that change no behavior, and that goes stale the moment a later feature touches the same paths. The qualifier "where relevant" gives the documentor no concrete stopping rule. Consequence: permanent reference bloat and drift risk in a reviewable instruction surface. Recommend confining the reference to current policy rows and recording issue-closure evidence in the feature notes/ship record only; the T-05 verify assertions do not require the issue numbers in the reference, so this trim costs nothing.
```
