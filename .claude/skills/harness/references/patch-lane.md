# The patch lane — one intake run writes both artifacts

Read this when the grilling artifact's `## Mission` reads `patch`, before you write the BRIEF.
The rule lives in `harness-brief` step 7; this is the procedure. Evidence and history: DEC-225,
DEC-228, DEC-139.

When the mission is `patch`, the whole intake is ONE product run and you write both artifacts
in it:

- **The BRIEF, in at most 120 lines**, same shape, no section skipped: Problem; the perspectives
  that actually judge a bug fix (usually `end user` or `operator`, plus `code maintainer` for the
  regression test); SCs that discharge them — the failing-then-passing test is the natural
  `automated` one; Verification gaps; Constraints; Out of scope; Approval pending. The bound is
  the point: a patch whose brief needs more than 120 lines was mis-judged, and you say so rather
  than trim.
- **`plan.yaml` with exactly one task**, `T-01`: `execution_mode: team`, `execution_agent` the
  owning dev, `files:` the ones the grilling named, `traces:` every SC, `change_type: bugfix`
  unless the grilling says otherwise. The lane itself is not yours to record: `feature.json` is
  the orchestrator's domain, and it wrote `mission: patch` from the grilling's `## Mission` block
  before it dispatched you (playbook step 1).

No panel and no goal-check run read the patch intake; it is gated at qa and review on the diff,
not at plan on a document (DEC-225, amending DEC-139). After signature the orchestrator runs
build → validate → ship. If, while writing, the diff turns out unbounded or a new public interface
appears, that is a `plan` mission wearing the wrong label: return it with the reason instead of
writing a 120-line plan.
