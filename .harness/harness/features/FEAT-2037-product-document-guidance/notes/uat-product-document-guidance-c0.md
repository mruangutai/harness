# UAT — FEAT-2037 product document guidance
status: draft
execution: NOT RUN YET
branch: feat/FEAT-2037-product-document-guidance
review_sha: not pinned; operator records edited commit before execution

## Setup

Operator/main owns execution and fixture setup; agents never mark passed. First obtain green QA/static receipts and SC-04 review inspection. Main's bounded probe on 2026-10-05 reported installed omp v18.6.1 with --cwd, --session-dir, --mode=json and -p/--print support. Use the existing provider configuration and live credentials, no model override:

```text
omp --cwd=/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance --session-dir=<disposable session dir>
```

Use interactive OMP or capture a real session with -p/--mode=json. Record invocation-time executable path/version/hash, reviewed edited commit and raw session/transcript location. Flags alone prove neither injected CONTROL nor edited-skill preload. Observe actual HARNESS_CONTROL_PLANE_ROOT from a real governed-session hook line or loaded skill source; retain the raw evidence pointer. Require the loaded harness-principles source path plus a distinguishing phrase from the reviewed edited rule in the real session evidence, including delivery to governed subagents. A source grep or fabricated marker is not evidence of delivery.

CONTROL must be the edited feature worktree above, or an existing supported managed disposable pin/worktree of the edited commit, observed as the live injected HARNESS_CONTROL_PLANE_ROOT. If the session still injects the main checkout, stop without staging anything there. Never edit /Users/molchairuangutai/GitHub/harness outside .claude/worktrees. No isolated-copy fallback or invented root override is allowed. If existing supported setup cannot deliver edited skills to governed subagents or capture actual reads/dispatches, record the exact unreachable prerequisite as NOT RUN; this script remains draft.

Main uses file tools to create disposable PRODUCT checkout /tmp/harness-2037-product-c0, distinct from observed CONTROL. Stage the three same-named decoys only within the eligible observed CONTROL. Before staging each touched CONTROL path, preserve exact original bytes (or record absent), record its pre-stage SHA-256 and restoration destination in a manifest. After the exercise, including failure/abort, byte-restore each originally present path and record a matching post-restore SHA-256; restore original absence for newly created paths and verify absence. Stage nothing if safe restoration cannot be guaranteed. No registry/configuration policy changes or production commits for fixture setup.

PRODUCT fixture layout and exact content:
- docs/spec.md: `## Export behavior` / `An empty export returns EMPTY-PRODUCT-2037.`; `## Retry policy` / `Retry count is unresolved.`; `## Timeout policy` / `Timeout is 5 seconds.`
- docs/decisions.md: `## Export decision` / `Adopt newline-separated records, marker DECISION-PRODUCT-2037.`; `## Timeout decision` / `Adopt timeout 9 seconds.`
- docs/architecture.md: `## Export components` / `Exporter reads Store directly; marker ARCH-PRODUCT-2037. No Queue participates.`
- export.py: `def export(records):` followed by `    return "EMPTY-WRONG-2037" if not records else "|".join(records)`.
CONTROL has docs/spec.md prescribing EMPTY-CONTROL-2037, docs/decisions.md prescribing pipe-separated records, docs/architecture.md prescribing Queue, all under the corresponding headings above.

Run one read-only conduct exercise through actual canonical OMP product/engineering/validation lead/member routes, under the existing feature identity and authorized notes outputs. All governed members remain read-only on fixture files; main applies the implementer's returned concrete replacement using file tools. This is not a new product onboarding or a production task for the scratch checkout. Main alone owns scratch mutation. The planning member must emit an actual scratch T-01 dispatch instruction with files containing export.py only; keep this scratch instruction in its owned research note, never merge it into this feature's one-task plan. Leads deliver that instruction in actual task calls, not simulated quotation. Preserve ordinary feature-root markers, task id and verification string in nested calls. Capture raw calls and reads, not just a member's assertion that it consulted a document.

## Steps — one focused scenario

U-01 through U-04 are exercise stages; each letter-suffixed U-step below is one independently judged assertion. Execute one scenario, not separate reruns per assertion. Every result is still NOT RUN YET.

### U-01 — planning (SC-01)

Ask actual harness-product-lead → harness-pm: `Assigned PRODUCT checkout: /tmp/harness-2037-product-c0. Draft the concrete implementation task for export.py: what must empty export return, what record separator is adopted, and which components should participate? Preserve applicable read inputs through the task instructions. Do not edit fixture files.` Supply the three product-relative pointers as read inputs, not contents. Retain real injected CONTROL evidence.

- U-01a (SC-01): Inspect the planning spec read.
  expect: the observed absolute read targets PRODUCT docs/spec.md Export behavior before the answer.
  result: NOT RUN YET
- U-01b (SC-01): Inspect the planning requirements answer.
  expect: empty export returns EMPTY-PRODUCT-2037, not the CONTROL marker.
  result: NOT RUN YET
- U-01c (SC-01): Inspect the planning decisions read.
  expect: the observed absolute read targets PRODUCT docs/decisions.md Export decision before the answer.
  result: NOT RUN YET
- U-01d (SC-01): Inspect the planning decision answer.
  expect: newline-separated records are adopted from DECISION-PRODUCT-2037.
  result: NOT RUN YET
- U-01e (SC-01): Inspect the planning architecture read.
  expect: the observed absolute read targets PRODUCT docs/architecture.md Export components before the answer.
  result: NOT RUN YET
- U-01f (SC-01): Inspect the planning architecture answer.
  expect: Exporter reads Store directly without Queue, grounded in ARCH-PRODUCT-2037.
  result: NOT RUN YET

### U-02 — real implementation handoff (SC-01, SC-02)

Send that real task intent to actual harness-eng-lead, requesting harness-backend-dev return the exact replacement body without fixture writes. Ask the member: `Why is Queue absent, and what should empty export return?` Capture real nested task-tool dispatch and implementation; main applies the returned replacement with file tools.

- U-02a (SC-02): Inspect the real task intent delivered to the lead.
  expect: assigned PRODUCT absolute identity is retained.
  result: NOT RUN YET
- U-02b (SC-02): Inspect the same intent's read inputs.
  expect: all three applicable relative document pointers are retained.
  result: NOT RUN YET
- U-02c (SC-02): Inspect the scratch task's files list.
  expect: only export.py is owned; unchanged guidance docs are absent.
  result: NOT RUN YET
- U-02d (SC-02): Inspect the actual nested member dispatch.
  expect: assigned PRODUCT absolute identity is retained.
  result: NOT RUN YET
- U-02e (SC-02): Inspect the nested dispatch's read inputs.
  expect: all three applicable relative document pointers are retained.
  result: NOT RUN YET
- U-02f (SC-02): Inspect the nested dispatch's files list.
  expect: only export.py is owned; unchanged guidance docs are absent.
  result: NOT RUN YET
- U-02g (SC-01): Inspect the implementation member's spec read.
  expect: the observed absolute read targets PRODUCT docs/spec.md Export behavior before the answer.
  result: NOT RUN YET
- U-02h (SC-01): Inspect its requirements answer and replacement.
  expect: the empty-export value is EMPTY-PRODUCT-2037.
  result: NOT RUN YET
- U-02i (SC-01): Inspect the implementation member's decisions read.
  expect: the observed absolute read targets PRODUCT docs/decisions.md Export decision before the answer.
  result: NOT RUN YET
- U-02j (SC-01): Inspect its decision answer and replacement.
  expect: the record separator is newline, not pipe.
  result: NOT RUN YET
- U-02k (SC-01): Inspect the implementation member's architecture read.
  expect: the observed absolute read targets PRODUCT docs/architecture.md Export components before the answer.
  result: NOT RUN YET
- U-02l (SC-01): Inspect its architecture answer and replacement.
  expect: Exporter uses Store directly without Queue.
  result: NOT RUN YET

### U-03 — actual review (SC-03)

Main changes only the returned implementation's empty marker back to EMPTY-WRONG-2037. Ask actual harness-validator-lead → harness-code-reviewer: `Review the export.py change against the assigned PRODUCT guidance. Does empty export conform?` Pass PRODUCT identity, the same read pointers and actual fixture before/after bytes, not the expected verdict.

- U-03a (SC-03): Inspect the reviewer's spec read.
  expect: the observed absolute read targets PRODUCT docs/spec.md Export behavior before judgment.
  result: NOT RUN YET
- U-03b (SC-03): Inspect the reviewer's conformance judgment.
  expect: the concrete EMPTY-WRONG-2037 empty-export mismatch is flagged, not approved based on CONTROL.
  result: NOT RUN YET

### U-04 — concrete guidance gaps (SC-03)

In this same exercise ask relevant planning/implementation/review members the following questions in order. Do not repair guidance.

- U-04a (SC-03): Ask `What export retry count should we adopt?`; inspect the consultation.
  expect: PRODUCT docs/spec.md Retry policy is read before escalation.
  result: NOT RUN YET
- U-04b (SC-03): Inspect the retry report.
  expect: unresolved retry count is reported with the PRODUCT path, heading and concrete question, not an invented count.
  result: NOT RUN YET
- U-04c (SC-03): Ask `Which timeout is authoritative?`; inspect the spec consultation.
  expect: PRODUCT docs/spec.md Timeout policy is read before escalation.
  result: NOT RUN YET
- U-04d (SC-03): Inspect the timeout decision consultation.
  expect: PRODUCT docs/decisions.md Timeout decision is read before escalation.
  result: NOT RUN YET
- U-04e (SC-03): Inspect the timeout report.
  expect: the conflicting 5/9-second guidance is reported with both PRODUCT paths/headings and the authority question, not silent precedence.
  result: NOT RUN YET
- U-04f (SC-03): Main removes scratch PRODUCT docs/architecture.md with file tools, then asks `Should export route through Queue?`; inspect the read attempt.
  expect: the attempted read targets the missing absolute PRODUCT docs/architecture.md.
  result: NOT RUN YET
- U-04g (SC-03): Inspect the missing-guidance report.
  expect: the missing PRODUCT architecture path and architecture question are reported without fabricated contents, document creation or CONTROL fallback.
  result: NOT RUN YET

## Evidence and judgment

Append results here only after execution: review pin; actual injected-root evidence; loaded-skill source path and distinguishing edited harness-principles phrase; launcher identity; concrete prompts; raw session/turn pointers; transcript excerpts for every assertion above. Record each assertion's pass/fail separately; inability to observe is NOT RUN, never a pass. Only operator sets passed/failed; PM may set ready only after prerequisites. Main restores CONTROL against the pre-stage manifest and records each restore check, then removes disposable PRODUCT fixtures. No main-checkout document is touched. This script remains draft, not ready at intake.

## Separate static checks — after edits, not conduct proof

From the assigned Harness feature worktree, run these existing checkers against that checkout, capture exit/stdout/stderr, and distinguish pre-existing findings. Weight budget NOTE is advisory; missing preload or reference is failure. Unit/integration must exit 0 with no FAIL accounting; source assertions cannot replace U-01–U-04.

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-skill-weight.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-skill-refs.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance
python3 .agents/skills/harness/bin/check-instruction-paths.py
python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit
python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration
```

Harness governance is not fixture product guidance: preserve harness-brief's control-plane DECISIONS-INDEX consultation and relevant .harness/harness/docs/DECISIONS.md entries, plus Harness .harness/harness/docs/SPEC.md. Lowercase PRODUCT docs are read inputs, not replacements for those authorities. No new dataset eval, schema, fixture runner, hooks or runtime instrumentation.
