# SC-07 append visibility rework

Independent integrated PM/lead judgement marks SC-07 partial: an unfinished human-prose fence can hide the validator's appended mapping. This is T-02's existing durable-readability boundary, not a new success criterion or a severity rewrite. Main elects one source rework under DEC-174; prior panel PASS and medium finding remain historical truth.

Hypothesis: `_append_record` reports success without checking that the canonical historical reader selects the prospective appended object. An open preceding fence consumes its opening `yaml` fence as body text and its closing fence as the prior block's close, leaving no current readable mapping (or the older mapping selected). Falsification would be the canonical reader selecting the new object for both reproduced open-fence forms.

RED: `python3 tests/integration/test-validate-digest.py --only run_lead_append_cases` exited 1, 22/24 passing. Both new open-fence cases returned exit 0 and changed bytes despite expected refusal/byte preservation. Closed prose fences still passed. No production edit preceded these failures.

Fix contract: build the exact prospective suffix with the existing safe dumper; require the existing canonical `last_fenced_mapping` selection of old bytes plus suffix to equal the validated object before writing. Otherwise refuse with an actionable prose-fence message, leaving every byte intact. Do not repair/close user prose, change the historical reader, restore live text parsing, or weaken assertions. Existing identical-object idempotency remains unchanged.

GREEN: the same append group passed 24/24; the complete pool passed all 120 files with eight workers in 142.13 seconds (`artifact://803`). No assertion was removed or weakened. A separate actual CLI smoke reproduced refusal without byte changes, appended only the missing prose closing fence, retried successfully, and confirmed the canonical durable reader selected the exact yielded object.

Current-file pre-cutover grading: `_append_record` CC6 / cognitive6 / ABC13.2, grade4 (production bar4); `_append_rule_cases` CC1 / cognitive0 / ABC25.5, grade3 (test bar3). No new grade-2 reason is required. One source rework, not a retry of a failed reader transport.
