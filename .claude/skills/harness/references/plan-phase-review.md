# Plan-phase review — grading the plan before there is a SHA

Read this when your dispatch names no `review_sha` and `feature.json` carries none. The rule
lives in `harness-code-review` § Before there is a SHA (`reviewed: plan:<path>`,
`code_grade: n_a`); this is the procedure. Authority: DEC-228.

While `approval.status` is pending and `feature.json` has no `review_sha`, the target is the plan
(DEC-228): grade `BRIEF.md` and `plan.yaml` as the specification — never a diff — and write

```yaml
reviewed: plan:<path-to-plan.yaml>
code_grade: n_a
```

`validate-digest.py` accepts this form only with pending approval, no pinned `review_sha`, and a
plan belonging to the checkout branch under review. `patch` has no pre-build panel; on `plan`,
the scope reader joins the panel after pm's draft and before pm's apply in the same plan run.
pm applies the findings there and records the panel with `plan-merge.py record-panel`, then
runs `plan-merge.py check`; never open a separate pre-signature fix loop (DEC-228).
