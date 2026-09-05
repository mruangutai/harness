# Observations - harness-orchestrator

- 2026-09-05: BUG-1306 — a test suite's own hermeticity can be mutation-tested WITHOUT editing the file: test-plan-merge.py honours PLAN_MERGE_BIN, so a /tmp wrapper that re-injects HARNESS_AGENT_TYPE and re-execs the real tool reproduced the pre-fix red (exit 1, 17 failing checks) against the SHIPPED bytes. qa had declined the mutation check because it could not edit the file; the indirection was available the whole time.
- 2026-09-05: BUG-1306 — that wrapper must handle BOTH entry shapes. test-plan-merge.py:1672 and :1925 load CLI in-process with importlib.spec_from_file_location, so a wrapper that unconditionally runpy's the real tool raises SystemExit(2) inside the SUITE process: zero PASS lines, usage on stderr, and it looks exactly like a broken fix rather than a broken probe.
- 2026-09-05: BUG-1306 — the pin/station ordering is a two-commit dance. INV-33 byte-compares plan.yaml at review_sha against disk, so every plan write (set-task-station done) must land BEFORE the pin; and the pin's own value is the hash of that commit, so feature.json needs a second commit after it. plan.yaml identical across both keeps INV-33 quiet.
- 2026-09-05: BUG-1306 — re-measured the worktree handoff-pointer defect rather than inheriting it: the Write of notes/handoff-build.md was refused with "brief-sc:SC-04 is unresolved in <MAIN>/.harness/harness/features/<FEAT>/BRIEF.md". Path-carrying pointers work; and an `approval:` pointer at a heading whose body has no `status:` line returns None from _satisfied_approval, which is what keeps the all-satisfied refusal from firing once the real approval reads approved.
- 2026-09-05: BUG-1306 — check-state.sh INV-35 is line-based and misreads a multi-line single-quoted YAML flow scalar as an unquoted one; plan.yaml:112's ` #1103` parses intact under safe_load. Verified before treating the red gate as work, which would have meant editing an approval-gated file for nothing.
- 2026-09-05 (BUG-1306, validate): `finding:PATH#F-NN` is unusable as a handoff authority in this
  repo. `handoff_done_when.py:14` compiles `FINDING_RE = ^finding:(.+)#(F-\d+|PF-\d+)$`, so the id
  must be pure digits — but every real finding id here is non-numeric (`F-INFO-01` in the c0 code
  review, `PF-15e50cd4137f8309fac4057506bd40a5` in plan.yaml's panel). Combined with the known
  worktree defect that kills pathless `plan-task:`/`brief-sc:` pointers, the ONLY binding authority
  available from a worktree is `approval:<path>#<heading with no `status:` line>` — a heading whose
  body has no status returns None from `_satisfied_approval`, which counts as not-satisfied and so
  binds. `#Success Criteria` works; `#Approval` alone does not, because it reads `approved` and the
  gate then says the block binds nothing.
- 2026-09-05 (BUG-1306, validate): to prove a test suite CAN report red without writing to the repo,
  read the pinned source, string-replace the line under test, and `exec(compile(mut, <original
  abspath>, "exec"), {"__file__": <original abspath>, "__name__": "__main__"})`, catching SystemExit
  for the exit code. Keeping the original `__file__` preserves every `os.path.dirname(__file__)`
  root resolution the file does, which a temp-dir copy breaks. `git status` stayed clean.
- 2026-09-05 (BUG-1306, validate): qa reported the `unit` kind "satisfied" for a bugfix by reasoning
  that the diff had no unit-testable surface, never executing it — matrix_ok true on an inherited
  kind. Running it myself cost 5 seconds and 27 files. A gate-only panel step will substitute
  argument for execution when the argument is good; the required-kind list is the thing to check
  against what actually ran, not the verdict.
- 2026-09-05 (BUG-1306, delta validation): the INV-35 false positive was closed by REWORDING the
  data, not by fixing the line-based checker — the issue reference `#1103` became `issue 1103` in
  one panel `consequence` string. It works and check-state now exits 0, but the checker will
  false-positive on the next quoted continuation line carrying an issue reference, and the plan
  lost its issue hyperlink to buy the green. Name it as a workaround in the briefing so nobody
  reads it as a checker fix.
- 2026-09-05 (BUG-1306, delta validation): when an owner re-pins after touching an approval-gated
  artifact, the cheap decisive check is `git rev-parse` of the SHA-and-path pair at EVERY pin the
  feature has had — blob-object equality across five pins settles "the reviewed code is unchanged"
  in one call, where a diff settles it only pairwise and a re-run of the suite proves nothing about
  the pin at all.
