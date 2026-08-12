# Observations — harness-validator-lead — FEAT-14

- 2026-08-12 (run panel2-validator): I named reviewer artifact paths as
  `notes/review-code-reviewer-panel2.md` and `notes/review-security-reviewer-panel2.md`. The domain
  guard permits only `notes/review-harness-<agent-name>-*.md` — the full agent name, `harness-`
  prefix included. Both reviewers hit the denial and correctly wrote to the guard-permitted path
  instead of working around it, then said so in their returns. Cost: nothing this time, because both
  reported the correction. It would have cost a lookup if either had stayed silent. When I write an
  artifact path into a dispatch, spell the agent name exactly as the `subagent_type`.

- 2026-08-12 (run panel2-validator): requiring each reviewer to QUOTE the verifying command and its
  output per finding, stated as "a finding without one will be dropped rather than promoted", worked
  — both returns carried line-anchored evidence and the code reviewer volunteered the bound on its
  own finding (CI's un-stamped sweep limits the exposure window to local-and-interactive) rather
  than leaving it at worst case. I hold no `Bash`, so without that clause in the prompt I would have
  been choosing between promoting unverified premises and re-dispatching.

- 2026-08-12 (run panel2-validator): a reviewer's returned `reviewed:` range silently differed from
  the range I dispatched — I asked for `1bdfe3f..HEAD`, the code reviewer reported
  `1bdfe3f..3abaedd` (the pinned review_sha). The gap was the state-only commits, and this feature's
  subject IS execution-state files, so "state-only" was not self-evidently out of scope. Check the
  returned range against the dispatched range before collating; nothing else surfaces the mismatch.

- 2026-08-12 (run panel2-validator): I nearly shipped "both reviewers reported
  `git status --porcelain` clean". Only the security reviewer did; the code reviewer reported a
  read-only method (`git show <sha>:<path>`, no edits) which is a different claim. The two reports
  differed and my sentence had flattened them. Also nearly shipped a rule-15 charge against a
  `factory_decompose.py` docstring that, read from its first line rather than from my offset, is a
  function contract with an over-broad closing clause — not a false claim in a shipped document. I
  withdrew the argument in the digest rather than deleting it, so the reasoning is on the record.
