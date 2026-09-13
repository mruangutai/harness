# Recording the panel — `record-panel` writes it from the lead's digest

Read this in the plan team's `apply` step, when the panel lead's digest has landed and the
findings have to reach `plan.yaml`. The rule lives in `harness-spec-driven` (never transcribe a
panel by hand, never edit a finding's severity); this is the procedure. Evidence and history:
DEC-228, DEC-229.

```bash
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/plan-merge.py record-panel \
  --file <plan.yaml> --digest <lead digest.md> --cycle N
```

It writes the top-level `panel` key from the lead's fenced DIGEST block: one `panel.readers` entry
for EVERY named reader, `skipped` ones included with the persona and the lead's reason, every
finding with its `kind` and severity carried byte for byte. A run whose only work is copying one
file into another is the zero-value run FEAT-59 removed (DEC-229) — the verb does the copy.

Dispositions:

- A `form` finding you fixed in the same run stays present with disposition `resolved` and
  `resolved_by: T-NN`.
- A `substance` finding re-gates only the tasks it names.
- The operator's overrule belongs in `approval.rulings`; that is the main session's write
  (`sign-approval --overrule`), never pm's.

After recording, run `plan-merge.py check --file <plan.yaml> --root <checkout>` and fix every
FAIL line before the plan goes for signature.
