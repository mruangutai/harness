# Plan-phase review — grading the plan before there is a SHA

Read this when your dispatch names no `review_sha` and `feature.json` carries none. The rule
lives in `harness-code-review` § Before there is a SHA (`reviewed: plan:<path>`,
`code_grade: n_a`); this is the procedure. Evidence and history: DEC-207, DEC-176.

While `approval.status` is pending and `feature.json` has no `review_sha`, the target is the plan
(DEC-207): grade `BRIEF.md` and `plan.yaml` as the specification — never a diff — and write

```yaml
reviewed: plan:<path-to-plan.yaml>
code_grade: n_a
```

`validate-digest.py` accepts this form only under those preconditions — a pending approval and no
pinned `review_sha` for this feature. Findings enter the one batched signature review (DEC-176),
never a separate pre-signature fix dispatch.
