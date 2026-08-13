# Observations — harness-documentor — FEAT-16

- 2026-08-12 (T-10): `gen-decisions-index.py` amendment placement is by DEC number in the `###`
  heading, but the DECISION body is split at the next `##`, so an amendment appended at EOF would be
  swallowed into the LAST decision's body and corrupt its computed `refs:`/`[tags]`. Amendments go
  inline inside their parent's section — DEC-174 am.2 before `## DEC-175`, DEC-186 am.1 before
  `## DEC-187`. That contradicts the "append at EOF to keep `@line` anchors stable" instinct: anchor
  churn in the regenerated index is expected output, not drift.
- 2026-08-12 (T-10): the index ruling cap (30 words, 20-non-ws-char floor) is asserted only in
  `test-gen-decisions-index.py`, and adding a required phrase to an existing ruling can blow it.
  Both rows here landed at 29 and 24 words — measured with `len(text.split())` before writing, not
  after.
- 2026-08-12 (T-10): found a live stale claim OUT of my task's bounds — `docs/harness/SPEC.md:425`
  says onboarding a repo is "one edit … `- name` (with its `default_branch`)", which `load_fleet`
  now rejects (a `repos[]` entry with no `board:` raises). Flagged as an open question rather than
  fixed, because T-10's intent forbids other prose changes in that file.
