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

Every record the tool marks `SEVERITY: high` — below its bar and not grade 2, whatever its grade —
is a **high** finding naming file, line, qualified name, the three numbers and the driver metric,
reported as `code_grade: fail`. Every gated grade-2 function is a **med** finding with a written
answer to each `REASON REQUIRED` line, reported as `code_grade: grade_2`; grade 2 never blocks. A
record with no `SEVERITY:` line is not a finding.

**You do not set `code_grade`.** `validate-digest.py` recomputes it over
`merge-base(<default branch>, review_sha)..review_sha` and refuses a digest that disagrees, naming
the expected value (DEC-209). Run the grader to cite records and reason about grade 2. `n_a` means
no changed Python path in that range; a range whose only Python change is a deletion is `pass`.
