# Panel fan-in — BUG-2565 plan, cycle 1

Reader wave over pm's landed draft (one turn). All three readers ran; severities and kinds are the readers' own, transcribed unchanged. Reader notes: `notes/review-harness-code-reviewer-plan-c1.md`, `notes/review-harness-ui-reviewer-plan-c1.md`; fable-advisor has no write grant, so its findings (with full `why`) live only here and at agent://FeministCod.FitSeahorse.

fable-advisor `why` text, verbatim summary for apply:
- dual drift checker: byte-level `gen-agent-output.py --check` (SC-07) and structural `agent_output_errors` (T-04) can disagree on a structure-preserving YAML reformat; grilling settled the drift check in check-omp-port.py alone.
- T-01 Run B: T-02 adds D-04 unconditionally; the probe note / T-01 intent should say Run B documents rather than gates.
- D-04 keep: harness-hooks.ts:1897-1898 pass-through relies on strict mode that frontmatter cannot set.
- T-06 extras keep: SPEC.md:1333-1337, harness-team SKILL.md:95 and the DEC-100 clause are live stale text.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: "FAIL, severity_max high: 2 high substance, 1 med substance, 1 med form; note notes/review-harness-code-reviewer-plan-c1.md"
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: "PASS, severity_max low: 1 low proportionality scope task, 3 info substance (two endorse keeping D-04 and T-06 extras); no write grant, findings carried in this fan-in"
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: "PASS, self-scoped out (mode A, in_scope false): plan touches no user-facing surface; note notes/review-harness-ui-reviewer-plan-c1.md"
  findings:
    - reader: harness-code-reviewer
      summary: "T-01 can pass without observing a refused yield or detecting its payload in the parent result."
      severity: high
      kind: substance
    - reader: harness-code-reviewer
      summary: "T-04's proposed Python equality admits type-changing frontmatter drift."
      severity: high
      kind: substance
    - reader: harness-code-reviewer
      summary: "T-02 and T-03 do not yet pin several promised failure behaviors."
      severity: med
      kind: substance
    - reader: harness-code-reviewer
      summary: "T-06 omits DEC-202's affected clause and leaves stale sibling wording in the named docs."
      severity: med
      kind: form
    - reader: should-not-exist
      summary: "gen-agent-output.py --check is a second home for the drift check the grilling settled into check-omp-port.py alone"
      severity: low
      kind: proportionality
      scope: task
    - reader: should-not-exist
      summary: "T-01 Run B measures a question (dataless_result_yield_without_hook) whose answer changes nothing in the build"
      severity: info
      kind: substance
    - reader: should-not-exist
      summary: "D-04 should stay: the pass-through it deletes is verifiably broken by the frontmatter route"
      severity: info
      kind: substance
    - reader: should-not-exist
      summary: "T-06's extra sites should stay: SPEC §8.3, harness-team SKILL and the DEC-100 amend are live stale text, not padding"
      severity: info
      kind: substance
  severity_max: high
```
