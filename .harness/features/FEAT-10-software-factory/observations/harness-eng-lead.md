# Observations — harness-eng-lead — FEAT-10-software-factory

- 2026-08-09 (w2-eng): A dispatch framed the T-03 `GH` contradiction as a choice between adding a
  public accessor to `factory_gh.py` and routing every caller through its public functions. Reading
  the module's public surface FIRST (`grep '^(def |class )' factory_gh.py`) showed the second option
  was free rather than a compromise: the sixteen exported functions cover every call T-04 and T-05
  make, T-02 touches gh at all, and T-06 shells `git` through its own seam. The framing had also
  overstated the exposure — none of the four `intent:` blocks names `GH`; the contradiction is
  confined to T-03's own prose. Generalises: a contradiction handed to you as a decision is a
  hypothesis about the code, and it is cheaper to check than to arbitrate.

- 2026-08-09 (w2-eng): The operator asked for a test-summary retrofit "if it is cheap." Rather than
  relay the conditional, I measured it — `test-factory-cli.py` and `test-factory-gh.py` each had
  exactly one `check()` helper and one `FAILS += 1` site — and shipped the measurement plus an
  explicit STOP CONDITION inside ONE dispatch (T-02's, the first), so two members could never edit
  the same two files. The member reported the stop condition did not fire. Folding a cross-cutting
  chore into the first serialized step is what keeps it from becoming a shared-file collision.

- 2026-08-09 (w2-eng): T-04 and T-06 BOTH wrote implementation before the test, self-caught before
  execution, deleted and restarted correctly. Same persona, same wave, two occurrences — that reads
  as a property of the dispatch, not of the member. My dispatches put "You are building test-first"
  in the first line but then buried the RED-first requirement behind a 200-line verbatim `intent:`
  block. Next wave: put the RED-first requirement immediately BEFORE the intent block, or ask for
  the observed RED output as a named deliverable the way the verify output already is.

- 2026-08-09 (w2-eng): The T-05 dispatch had to close a hole the plan's `intent:` left open — the
  blocker gate must read `.harness/features/<FEAT>/plan.yaml` but the intent never says where the
  features root comes from, and a cwd-relative default is exactly the SC-08 defect a SIBLING task's
  intent spends twenty lines on. A defect the plan spells out for one task and omits for another is
  the shape worth scanning for before dispatch: read the tasks as a set, not one at a time.

- 2026-08-09 (w2-eng): Counting trap, still live and now with a near-miss. Wave 1 recorded that
  `test-check-plan-routes.py` emits column-0 `PASS case_NN_…` lines, so a naive `^PASS` grep reports
  76 for an integration run that executes 13 files. `test-factory-gh.py` independently happens to
  carry 76 checks. Two unrelated 76s, one of them the documented artifact — when repeating any 76
  on this feature, say which measurement it is.
