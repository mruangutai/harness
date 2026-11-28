# Grading changed Python — `code-grade.py` over the pinned range

Read this in Stage 2 when the pinned range contains a changed Python path. The rule lives in
`harness-code-review` § Grade changed Python (a `SEVERITY: high` record is a high finding, a
gated grade-2 function is a med finding that never blocks, you do not set `code_grade`); this is
the procedure. Evidence and history: DEC-209.

Run the grader against the pinned review, never `HEAD`:

```sh
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/code-grade.py \
  --base "$(git merge-base origin/main "$review_sha")" \
  --head "$review_sha"
```

A `SEVERITY: high` finding names file, line, qualified name, the three numbers and the driver
metric. A grade-2 finding carries a written answer to each `REASON REQUIRED` line. A record with
no `SEVERITY:` line is not a finding.

`validate-digest.py` recomputes `code_grade` over
`merge-base(<default branch>, review_sha)..review_sha` and names the expected value when it
refuses. Run the grader to cite records and reason about grade 2. `n_a` means
no changed Python path in that range; a range whose only Python change is a deletion is `pass`.
