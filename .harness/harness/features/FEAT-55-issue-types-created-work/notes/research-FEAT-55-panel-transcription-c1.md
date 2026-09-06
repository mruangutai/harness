# Panel transcription — FEAT-55 cycle 1

**All seven findings of run `2026-09-04-11-validator` are now in `plan.yaml`'s `panel:` key, verbatim,
with machine-computed ids. One `high` finding is `awaiting_user` and gates the signature; the other six
are `batched_to_signature_review`. Nothing was adjudicated, softened, merged, renumbered or dropped.**

`plan.yaml` sha256: `ddcdd313…f30a26` before → `04f45dbe36fe3482dc900da6f694b5a67efcba18b27a3dc2a0a146307af81277` after.

## The ids — computed, never typed

Every id came from `panel_findings.py id --reader <r> --summary <s>`, driven by a script over
`yaml.safe_load` of `runs/2026-09-04-12-product/panel-source.yaml`; no summary string passed through a
human edit. Order is the source's order.

| # | id | reader | severity | disposition |
|---|---|---|---|---|
| 1 | `PF-f1031f76b4537f1cd9b60ddc0559b7d1` | scope | **high** | `awaiting_user` |
| 2 | `PF-1286544c197d1b0eb4a9b0dc8e1234dc` | should-not-exist | med | `batched_to_signature_review` |
| 3 | `PF-610431f7d96408d23666cc4e60071501` | should-not-exist | med | `batched_to_signature_review` |
| 4 | `PF-452948136bf467869d223e027191ae49` | scope | med | `batched_to_signature_review` |
| 5 | `PF-e27f1c3018b6b8477547a1b028607f96` | should-not-exist | low | `batched_to_signature_review` |
| 6 | `PF-0c12a033f69bb6bc60b8f96134f94fd0` | should-not-exist | low | `batched_to_signature_review` |
| 7 | `PF-9a71cb9a0c590b06b890ff1517b80385` | should-not-exist | info | `batched_to_signature_review` |

Finding 1 is the REQ-07 single-route refusal-coverage gap. Only an `approval.rulings` entry written by
the main session (`sign-approval --overrule PF-f1031f76b4537f1cd9b60ddc0559b7d1:<reason>`) can accept its
risk; no lead and no pm tier may.

## Verification, all from the file on disk after the write

- `set-panel` printed `PANEL cycle 1 -> <plan.yaml>` and `APPLIED <plan.yaml>`, exit 0. It was the only
  write route — no Edit, no Write, no redirect.
- `yaml.safe_load` loads the plan; `panel.last_run == "2026-09-04-11-validator"`; `panel.cycle == 1`
  and is an `int`; `severity_max: high`; 2 readers (`fable-advisor`/`should-not-exist`/`ran`/`none`,
  `harness-code-reviewer`/`scope`/`ran`/`none` — neither skipped); 7 findings.
- **Re-derivation:** every stored id re-computed from the STORED `reader` + `summary` matches the
  stored id, and each is 35 chars. Every stored `summary`, `why`, `severity`, `reader` compares `==`
  to the source object; `must_fix` (2) and `fix_order` (4) compare `==` to the source lists.
- Dispositions: 1 `awaiting_user` + 6 `batched_to_signature_review`, no third value, none `dismissed`.
- Untouched: `approval: {status: pending}`, top-level `status: plan`, 12 tasks, 20 decisions.
- `check-plan-routes.py <plan.yaml>` → `0 violation(s)`, exit 0 (the T-12 line is the expected DEC-174
  main-session-direct deviation, not a failure).
- **BRIEF.md byte-unchanged**, verified by `sha256sum` before and after this run:
  `e9ca35e413fc3b0cfbe23cd58956eaea43a66270d4424dd1a27961967dd2607d` both times. The `git show HEAD:`
  route was unavailable — `git status --porcelain` reports the whole feature directory as untracked
  (`??`), so there is no HEAD blob to compare against; the sha256 pair is the method used.
- No formatter, linter or project suite was run. The panel value file lived at
  `/tmp/feat55-panel-c1/panel.yaml` (transient scaffolding; the durable record is the plan key).

## Open questions

- **Q1 (non-blocking):** repo-tier expertise suggests recording a `panel.transcription_rule` alongside
  the findings so a later reader can tell whether a summary was normalized before hashing. Not written
  here: the dispatch pins the panel shape exactly, and the risk does not arise this cycle because every
  summary compares byte-equal to the source. Worth deciding as a schema question, not a FEAT-55 edit.
