# Panel transcription — BUG-285-yaml-loader-pin — cycle 0

BLUF: **The cycle-0 plan panel is now on the record.** `plan.yaml`'s top-level `panel:` key carries
both readers as `status: ran` and the single `info` finding as `PF-2242299b369215b13ad577fe4279d52e`,
`disposition: open`. `approval:` is untouched and still `status: pending`. Nothing was re-judged: no
severity changed, no dismissal re-litigated, no finding added. Send-backs on this transcription: 0.

Plan: `.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml`
Value route: `plan-merge.py set-panel --value-file <tempdir>/panel.yaml`, exit 0. Its stdout:

```
PANEL cycle 0 -> …/features/BUG-285-yaml-loader-pin/plan.yaml
APPLIED …/features/BUG-285-yaml-loader-pin/plan.yaml
```

## What landed

- `last_run: 2026-09-09-01-planpanel-validator` (the run DIRECTORY name), `cycle: 0` (int).
- `readers:` two entries, both `status: ran`, neither carrying `reason` (required only when
  skipped): `should-not-exist`/`fable-advisor` and `scope`/`harness-code-reviewer`. Both are
  recorded because a findings list alone cannot tell a reader that ran cleanly (`scope`, 0 findings)
  from one that never ran. Source: run `state.yaml` (both steps `status: complete`, both `PASS`) and
  the digest's readers table.
- `findings:` one entry — `severity: info` carried verbatim from the reader, `reader:
  should-not-exist`, `disposition: open`. `disposition: open` is the schema's enum, not a downgrade
  of the lead's "accept, non-gating": accepting the risk requires an `approval.rulings` entry, which
  only the main session may write. No `resolved_by`, because nothing resolved it.
- No `dismissed:` key — the template declares none. **The four assessed-and-dismissed items are read
  in the run digest**, `runs/2026-09-09-01-planpanel-validator/digest.md`, section
  `### Assessed and dismissed` and again in its appended `DIGEST: … panel.dismissed` block
  (author-and-grader identity D-02; T-01 `intent:` over-specification; `lanes.rows[0].surface`
  breadth; REQ-04/SC-05 vs the delete-don't-re-pin rule).

## The finding id — recomputable

- Helper: `.agents/skills/harness/bin/panel_findings.py id --reader should-not-exist --summary '<s>'`.
- Algorithm (`panel_findings.py:23-33`): `PF-` + first **32** hex chars of
  `sha256(reader + "\n" + normalize_summary(summary))`; `normalize_summary` lowercases, collapses
  each whitespace run to one space and strips the ends. A content hash, so a reworded finding gets a
  new id and a stale operator ruling stops applying.
- Hashed: `reader = should-not-exist`; `summary` = the digest's `panel.findings[0].summary` taken
  **verbatim from the appended YAML block**, extracted by `yaml.safe_load` rather than retyped, so
  the em-dash and every character survive. Result `PF-2242299b369215b13ad577fe4279d52e`.
- Re-derived AFTER the merge from the summary as it reads in `plan.yaml`: identical (MATCH).
  `set-panel` re-emitted the summary as a double-quoted scalar with `\u2014` for the em-dash — a
  representation change only; the loaded string is byte-identical to the digest's, which is why the
  hash still matches.

## Nothing else moved

Baseline: `plan.yaml` is untracked at `7e0c2ec1`, so the baseline is a tempdir copy,
sha256 `f53a9212039aac2fa4c71fd729cc3ee13a759c56e9ecf93c2ad5b76d1cb262c2`.

- `diff baseline post-merge` → one purely additive hunk, the 19-line `panel:` block after line 32.
- `approval:` `{status: pending}` before and after; no `rulings` key gained.
- T-01's `verify:` (68 chars) and `intent:` (6055 chars) block scalars compare **equal** to the
  baseline's, loaded and compared as strings — not eyeballed.
- Every non-`panel` top-level key structurally identical.
- Tempdir removed; `git status --porcelain` shows only the untracked feature directory.

## Discrepancies in the record — reported, not resolved

1. **`PF-` id length: 8 hex vs 32 hex.** The upstream instruction described the id as `PF-` plus
   eight hex characters, quoting `templates/plan.yaml:76`'s illustrative `PF-0123abcd`. The
   executable convention is 32 (`panel_findings.py:29-33`), matching the landed ids in
   `.harness/harness/features/BUG-124-run-dir-squad-suffix/plan.yaml`. I followed the helper. The
   template's example is a doc defect worth a one-line fix so it stops seeding the wrong rule.
2. **Two wordings of the same finding inside the digest.** The `## Findings` table (`digest.md:29`)
   writes the summary with arrows and backticks and no terminal period; the appended
   `panel.findings[0].summary` writes it with the word "to", no backticks and a period. Same claim,
   different bytes — and because the id is a content hash, the two would hash differently. I used
   the appended YAML block, as dispatched and as the lead labelled it ("transcribable form"). Not
   mine to reconcile.
3. **`check-plan-routes.py` exit code, still open (lead's Q1).** The panel dispatch records exit 0
   with one `DEVIATION`; `notes/research-BUG-285-goalcheck-plan-c2.md` `## Advisory` records exit 1.
   Untouched by this run; it is one command for the operator before signing.

## For the operator, at signature

The finding is a proportionality note, not a defect: SC-03's mutation probe buys a one-off
demonstration rather than durable coverage, and its delivery chain (note → orchestrator's pathspec
commit → `git show <review_sha>:` grading) is the likeliest source of a false `not_met` at build
time. It sits at `disposition: open` and will stay open unless an `approval.rulings` entry accepts
its risk — that write is the main session's.
