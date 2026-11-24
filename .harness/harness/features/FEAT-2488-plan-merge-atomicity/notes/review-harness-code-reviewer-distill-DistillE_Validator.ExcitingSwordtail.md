# Code-reviewer distillation

Three craft replacements applied. No repository-tier changes, diff review, or suite run.

| Candidate | Disposition | Evidence |
|---|---|---|
| 1. Probe the class and its boundary | Applied as **P-08**, replacing the generic omission prompt. Replaying the original failure is not class closure. | `review-harness-code-reviewer-c2.md` through `-c5.md` distinguish closed stream objects, buffered shutdown, missing streams at exec, and a fault beyond the stdio-state boundary. |
| 2. Route adjacent terminal findings | Applied as **O-04**, replacing generic class labeling. Report consequence separately from membership, with trigger reachability, line provenance, and same-trigger baseline behavior. | The final review raised C1 as high; `answers-2026-11-24-validate-c4-ship.md` routed it to backlog: both streams were healthy, the trigger was opt-in, the faulting line was unchanged, and the pin avoided base's torn pair. |
| 3. Pin the process environment | Applied as **G-07**, replacing a deletion-sweep reminder already covered elsewhere. Measure the real child's exit through shutdown with defaults restored; test supported overrides separately. | `review-harness-code-reviewer-c3.md` records rc 120 with `PYTHONUNBUFFERED` absent versus rc 0 with the shell's inherited override. `-c4.md` records closure with the override removed. |

Batch `0a48582775fb0360aa339befc4fc4fbd4614a0d257dd3aa898467c4f03309189`; receipt `expertise-receipt-b2abd4a72a8e674f078dc1f48b4eb514b26b45b9d883f1493425254afe84c5ec.json`.

Craft counts before → after: Patterns 15 → 15; Gotchas 15 → 15; Outcomes 10 → 10; Open 0 → 0.

Open questions: none.
