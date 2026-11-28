# T-01 probe: what a hook-refused yield does on OMP 19.2.1

Measured 2026-11-27 by the main session (DEC-174) in a throwaway project outside every checkout. It answers the grilling's two open questions before any gate changes.

RESULT BEGIN
omp_version: 19.2.1
model: claude-opus-5-5
refused_attempts_before_end: 3
refused_attempts_in_transcript: 3
refused_attempts_all_invocations: 6
refused_attempts_matched_to_transcript: 6
run_a_matched: yes
run_c_first_matched: yes
run_c_repeat_matched: none
run_c_invocations: 1
parent_task_status: failed
parent_receives_refused_payload: no
run_c_sequence: followed
hook_refusal_consumes_schema_retry: no
dataless_result_yield_without_hook: rejected
RESULT END

## What it means

- **No refused payload reaches the parent** (D-03 gate passes). Run A: the hook refused every yield. The child yielded the same object twice, then tried an `error` yield, which was also refused. It ended without an accepted yield. The parent's task result was `failed (exit 1)` with OMP's "Subagent exited without calling yield tool after 3 reminders" warning and the child's final text naming the cause. No data was delivered.
  - *Correction (validate run 2026-11-27-06, operator ruling OQ-4):* "no refused payload" holds for task **data** only. In Run A the child's own final text, which the parent's failure result carries, quoted the refused object. D-03 bounds task data; the child's prose is not covered.
- **Hook refusals do not consume OMP's schema-retry budget.** Run C: after three hook refusals, OMP's own schema check rejected attempt 4 (`{"wrong": true}`) with "2 retry attempt(s) remain", which is the full budget minus one. The parent received attempt 5's valid object, never the invalid one.
- **OMP itself rejects a data-less `type: result` yield** when nothing was submitted before it (Run B), with "Empty result retries remaining". D-04 refuses it in the hook regardless.
- Side observation for T-02/T-06: under a refusing validator, a child's `{"error": …}` yield, which has no `data`, is refused like any other. So the child cannot report failure through yield, and the parent sees `failed` plus the child's final text. That matches D-02's instruction to stop and name the cause.
- The model sent `data` as a JSON string every time; OMP decoded it. The log and transcript comparisons decode strings before testing JSON equality.

## Method

`omp -p --no-extensions -e refuse-yield.ts --no-skills --no-rules --no-context-files --no-title --no-lsp --auto-approve`, one `--session-dir` and one `PROBE_LOG` per invocation, run from the throwaway directory. Only the probe extension loads.

Agent `.omp/agents/probe-child.md`:
```markdown
---
name: probe-child
description: Probe child for the BUG-2565 yield-refusal measurement.
tools: [read]
spawns: []
blocking: true
structured: true
output:
  type: object
  properties:
    VERDICT:
      type: string
      enum: [PASS, BLOCKED]
    note:
      type: string
  required: [VERDICT, note]
  additionalProperties: false
---
You are a probe child. Do exactly what your task says, nothing else.
```

Extension `refuse-yield.ts`:
```ts
import { appendFileSync } from "node:fs";

const REASON = "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This is a Harness fault, not a violation found in your object: do not change a valid object to get past it. Yield the same object once more; if it is refused again for this same cause, stop yielding and end your turn with one line naming this cause, because no yield can pass until validate-digest runs.";

let n = 0;

export default function (pi: any) {
  pi.on("tool_call", async (event: any) => {
    if (event.toolName !== "yield") return undefined;
    n += 1;
    const attempt = n;
    const raw = process.env.PROBE_REFUSE;
    const N = raw === undefined ? 0 : Number.parseInt(raw, 10);
    const refuse = raw === undefined || attempt <= N;
    const input = event.input && typeof event.input === "object" ? event.input : {};
    const data = Object.hasOwn(input, "data") ? input.data : "ABSENT";
    if (process.env.PROBE_LOG) {
      appendFileSync(process.env.PROBE_LOG, JSON.stringify({ attempt, decision: refuse ? "refused" : "passed", data }) + "\n");
    }
    return refuse ? { block: true, reason: REASON } : undefined;
  });
}
```

Counter examples: PROBE_REFUSE unset refuses every yield; PROBE_REFUSE=0 refuses none; PROBE_REFUSE=3 refuses attempts 1, 2 and 3 and passes attempt 4 and every later attempt.

Parent prompt in each invocation: Dispatch the task tool exactly once with agent "probe-child" and this exact task text: "<child task>". Do not dispatch anything else. Then report verbatim the task result's status, any data, and any warning.

- Run A child task: Call yield with data {"VERDICT": "PASS", "note": "probe"}. If a yield is refused, follow the refusal instruction exactly.
- Run C child task: Make exactly these yield calls in order, regardless of any refusal or rejection text, until one is accepted: attempt 1 data {"VERDICT": "PASS", "note": "attempt-1"}; attempt 2 … attempt-2; attempt 3 … attempt-3; attempt 4 data {"wrong": true}; attempt 5 data {"VERDICT": "PASS", "note": "attempt-5"}. Send each data value as an object, never as a JSON string.
- Run B child task: First call yield with type "result" and no data field at all. Then call yield with data {"VERDICT": "PASS", "note": "probe"}.

Step 1 matching pairs the k-th refused log line with the k-th child-transcript yield result carrying "Harness refused this yield". A pair matches when the call's `data` (decoded, or `ABSENT` when the input has no `data` key) is JSON-equal to the logged data. Step 2 compares each parent task result's delivered output with every refused log line's data in the same invocation.

## Evidence

### runA (PROBE_REFUSE=unset)

Log lines:
```
{"attempt": 1, "decision": "refused", "data": "{\"VERDICT\": \"PASS\", \"note\": \"probe\"}"}
{"attempt": 2, "decision": "refused", "data": "{\"VERDICT\": \"PASS\", \"note\": \"probe\"}"}
{"attempt": 3, "decision": "refused", "data": "ABSENT"}
```

Step 1 pairs (attempt · log data · transcript call data · matched · transcript result excerpt):

- attempt 1 · `{"VERDICT": "PASS", "note": "probe"}` · `{"VERDICT": "PASS", "note": "probe"}` · matched · "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This…"
- attempt 2 · `{"VERDICT": "PASS", "note": "probe"}` · `{"VERDICT": "PASS", "note": "probe"}` · matched · "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This…"
- attempt 3 · `ABSENT` · `ABSENT` · matched · "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This…"

Every child yield result in transcript order:

- `{"data": "{\"VERDICT\": \"PASS\", \"note\": \"probe\"}"}` → error: "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This is a Harness fault, not a violation found in your object: d"
- `{"data": "{\"VERDICT\": \"PASS\", \"note\": \"probe\"}"}` → error: "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This is a Harness fault, not a violation found in your object: d"
- `{"error": "Blocked: the harness's validate-digest check exited 1 (\"probe\") and refused the object {\"VERDICT\":\"PASS\",\"note\":\"probe\"} twice wi` → error: "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This is a Harness fault, not a violation found in your object: d"

Parent task result, verbatim:
```
<task-result id="PromisingSquid" agent="probe-child" status="failed (exit 1)" duration="20.3s">

<error>SYSTEM WARNING: Subagent exited without calling yield tool after 3 reminders.</error>
<output>
SYSTEM WARNING: Subagent exited without calling yield tool after 3 reminders.

The yield was refused twice because the harness's `validate-digest` check exited 1, so it never checked the object and no yield can pass until that check runs.No result has been returned: the harness's `validate-digest` check exited 1 ("probe"), so it refused every yield, including the error report, without checking the object.I couldn't return the result: the harness's `validate-digest` check failed every time and refused all three yields without checking them.

I sent `{"VERDICT": "PASS", "note": "probe"}` twice, then once as an error report, and each was refused the same way (exit 1, "probe"). The refusal says this is a harness fault and that nothing can pass until `validate-digest` actually runs, so I've stopped retrying. I filed an issue report noting that this refusal tells me to stop, while the idle reminders say every turn must end with a tool call.Still blocked: `validate-digest` exits 1 ("probe") and has refused every yield without checking it. Its refusal says to stop yielding, so I won't retry until that check runs, and the probe result is not returned yet.
</output>
</task-result>
```

### runC1 (PROBE_REFUSE=3)

Log lines:
```
{"attempt": 1, "decision": "refused", "data": "{\"VERDICT\": \"PASS\", \"note\": \"attempt-1\"}"}
{"attempt": 2, "decision": "refused", "data": "{\"VERDICT\": \"PASS\", \"note\": \"attempt-2\"}"}
{"attempt": 3, "decision": "refused", "data": "{\"VERDICT\": \"PASS\", \"note\": \"attempt-3\"}"}
{"attempt": 4, "decision": "passed", "data": "{\"wrong\": true}"}
{"attempt": 5, "decision": "passed", "data": "{\"VERDICT\": \"PASS\", \"note\": \"attempt-5\"}"}
```

Step 1 pairs (attempt · log data · transcript call data · matched · transcript result excerpt):

- attempt 1 · `{"VERDICT": "PASS", "note": "attempt-1"}` · `{"VERDICT": "PASS", "note": "attempt-1"}` · matched · "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This…"
- attempt 2 · `{"VERDICT": "PASS", "note": "attempt-2"}` · `{"VERDICT": "PASS", "note": "attempt-2"}` · matched · "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This…"
- attempt 3 · `{"VERDICT": "PASS", "note": "attempt-3"}` · `{"VERDICT": "PASS", "note": "attempt-3"}` · matched · "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This…"

Every child yield result in transcript order:

- `{"data": "{\"VERDICT\": \"PASS\", \"note\": \"attempt-1\"}"}` → error: "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This is a Harness fault, not a violation found in your object: d"
- `{"data": "{\"VERDICT\": \"PASS\", \"note\": \"attempt-2\"}"}` → error: "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This is a Harness fault, not a violation found in your object: d"
- `{"data": "{\"VERDICT\": \"PASS\", \"note\": \"attempt-3\"}"}` → error: "Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This is a Harness fault, not a violation found in your object: d"
- `{"data": "{\"wrong\": true}"}` → error: "Output does not match schema: VERDICT: is required; note: is required; wrong: must not be present. Send `data` as the decoded value, not a JSON string. Call yield again with the corrected shape — 2 re"
- `{"data": "{\"VERDICT\": \"PASS\", \"note\": \"attempt-5\"}"}` → ok: "Result submitted."

Parent task result, verbatim:
```
<task-result id="SadSeahorse" agent="probe-child" status="completed" duration="11.9s">

<output>
{
  "VERDICT": "PASS",
  "note": "attempt-5"
}
</output>
</task-result>
```

### runB (PROBE_REFUSE=0)

Log lines:
```
{"attempt": 1, "decision": "passed", "data": "ABSENT"}
{"attempt": 2, "decision": "passed", "data": "{\"VERDICT\": \"PASS\", \"note\": \"probe\"}"}
```

Step 1 pairs (attempt · log data · transcript call data · matched · transcript result excerpt):

- no refused log lines

Every child yield result in transcript order:

- `{"type": "result"}` → error: "A data-less `type` only finalizes previously submitted sections, and none were submitted. Submit success as {"data":<your output>} or failure as {"error":"message"}. Empty result retries remaining bef"
- `{"data": "{\"VERDICT\": \"PASS\", \"note\": \"probe\"}"}` → ok: "Result submitted."

Parent task result, verbatim:
```
<task-result id="QuickestManatee" agent="probe-child" status="completed" duration="4.5s">

<output>
{
  "VERDICT": "PASS",
  "note": "probe"
}
</output>
</task-result>
```

Run C followed the sequence on its first invocation: attempts 1–3 refused with notes attempt-1…attempt-3, attempt 4 passed the hook with `{"wrong": true}`. It was not repeated. Run B takes no part in steps 1 and 2.
