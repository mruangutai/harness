# Observations — harness-validator-lead — FEAT-21

- 2026-08-15: I named the wrong file in a dispatch. The coordinator's brief said "case 20 lifecycle
  (TemporaryDirectory, imports hoisted, helper inlined)" without naming a file; I filled the gap
  with `test-check-plan-routes.py` because I knew that file has a `case_20`. The refactor is
  actually in `test-layout-migration.py` — BOTH files carry a case numbered 20, and
  `test-check-plan-routes.py`'s was untouched by `4a98cc4`. code-reviewer caught it, said it is
  "exactly how a lead could misverify", and reviewed the right file anyway. Lesson: when a dispatch
  hands down a refactor description without a path, resolve the path from the commit's own diff
  (`git show --stat <sha>`) before writing the prompt — an inherited framing plus my own recall of a
  similarly-named symbol is how a confident wrong anchor gets manufactured. Costs one Grep; I did
  not spend it.

- 2026-08-15: code-reviewer's DIGEST scalar disagreed with its own findings table — table carried
  B-4 at `med`, the `severity_max:` field said `low`. I reported `med` off the table. Worth
  remembering that a member's summary scalar and its own body can diverge, and the body is the
  evidence; routing on the scalar alone would have understated the round.

- 2026-08-15: two rounds in a row, the gating-adjacent findings (B-4 segment readability guard, B-5
  branch-gate segment) were both invisible to every green gate for the SAME reason — no fixture
  stages two repository segments. Members had to hand-build a two-segment tree to see them. When a
  feature's stated purpose is X and no fixture exercises X, that absence is itself the adequacy
  finding, and it recurs until someone lands the fixture.

- 2026-08-15: polling a `Glob` for a member's artifact path is a poor wait primitive — the artifact
  lands only at the very end of a member's run, so dozens of polls returned nothing while three
  members worked for 10-16 minutes each. The completion notification is the real signal. Cheap
  lesson: after dispatching, do lead-tier reading that does not duplicate members (the SC list, the
  decision record, prior-round digests) instead of polling.
