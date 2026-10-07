# Recording the panel — `record-panel` writes it from the lead's digest

Read this in the plan team's `apply` step, when the panel lead's digest has landed and the
findings have to reach `plan.yaml`. The rule lives in `harness-spec-driven` (never transcribe a
panel by hand, never edit a finding's severity); this is the procedure. Evidence and history:
DEC-228, DEC-229.

```bash
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/plan-merge.py record-panel \
  --file <plan.yaml> --digest <lead digest.md> --cycle N
```

It writes the top-level `panel` key from the lead's fenced DIGEST block — the LAST fenced yaml block
in the digest.md that loads to a mapping (a later block is a correction; unfenced text is refused):
one `panel.readers` entry
for EVERY named reader, `skipped` ones included with the persona and the lead's reason, every
finding with its `kind` and severity carried byte for byte. A run whose only work is copying one
file into another is the zero-value run FEAT-59 removed (DEC-229) — the verb does the copy.

Dispositions are written with `plan-merge.py set-panel`, and only in the template's shape: a
finding carries `id severity reader kind summary disposition`, plus `scope` on a proportionality
finding and `resolved_by` on a resolved one, and nothing else. Every panel verb, `sign-approval`
and INV-32 refuse any other key or value (#2095); a rationale goes in a feature note, not on the
finding.

- A `form` finding you fixed in the same run stays present with disposition `resolved` and
  `resolved_by: T-NN`, naming a task in this plan.
- A `substance` finding re-gates only the tasks it names.
- The operator's overrule belongs in `approval.rulings`; that is the main session's write
  (`sign-approval --overrule`), never pm's, and never a disposition. `sign-approval` refuses
  while a high, critical or unrated finding is open without one.

After recording, run `plan-merge.py check --file <plan.yaml> --root <checkout>` (plus
`--code-root <code worktree>` for a served repository's plan) and fix every FAIL line before the
plan goes for signature.
