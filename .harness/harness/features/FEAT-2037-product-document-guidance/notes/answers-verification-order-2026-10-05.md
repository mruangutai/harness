# Operator approval — verifier ordering

Date: 2026-10-05. Author: main session, recording the actual question/answer from this conversation.

Question: “The signed task requires passed UAT before completion, but Harness requires completed tasks before the review that makes UAT ready. May I correct that ordering without changing any acceptance criteria?”

Operator selected **Correct verification order**: “T-01 completes on the prescribed static checks; SC-04 remains independently reviewed, and all 27 live UAT assertions remain mandatory before shipping. Re-sign the amended verifier.”

Authorized change: amend only T-01's build verification ordering in plan.yaml. Its literal verifier must be the existing prescribed static commands and expected exit-zero outcomes, not passed UAT as a pre-review prerequisite. Retain live conduct, independent SC-04 review, operator-only UAT judgment and all original SCs as feature acceptance gates after build. No change to task intent, files, traces, change_type, routing, product-root consultation, read-before-answer, assertion strength or rework ruling (one round, 45 minutes). Preserve the live UAT script's 27 assertions and draft/not-run status.

Main may re-sign this narrowly amended plan against this explicit approval. This grants no production edits to specialists, no enforcement/runtime/schema/test changes, no PR or merge permission, and no authorization to fabricate observation, task verification, QA or UAT pass.
