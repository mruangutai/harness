# Panel record + advisory fold — BUG-442 — c0

**BLUF: both writes landed and revalidated. `plan.yaml` now carries the c0 panel (PASS, `must_fix: []`,
both readers `ran`) and T-01's three advisories are folded. `approval.status` is still `pending`;
the plan is unsigned and ready for the operator's signature.** Two deviations from the dispatch were
forced by the tooling and by a self-defeating instruction — both are recorded below, neither is
blocking.

## What is in `plan.yaml` now

Top-level `panel:` at `plan.yaml:29`, a **sibling** of `approval:` (`:3-4`), not nested.
`last_run: 2026-09-07-03-validator`, `cycle: 0`, transcribed from
`runs/2026-09-07-03-validator/digest.md` — the `-02` run was not read for content and not touched.

Both readers appear with `status: ran` and **neither carries `persona`/`reason`**, which the template
(`templates/plan.yaml:70-74`) requires only for a skip. `should-not-exist` / fable-advisor returned an
**empty findings list as a result** — it reproduced the M1 mutant landing rc=0 on the live tree
(digest `:42`) — so it is recorded as a reader that ran, never as a skip.

| PF- id | sev | disposition |
|---|---|---|
| `PF-eec88a681bbcecaea01bbe3a96006ece` | `med` | `resolved`, `resolved_by: T-01` — absolute `verify:` paths |
| `PF-069ce9cf7ae78da5ea431b12becc2753` | `med` | `resolved`, `resolved_by: T-01` — inherited `BUG442_MUTANT_CHILD` |
| `PF-a78628c47bc51834ac364dfadbcf2e75` | `low` | `resolved`, `resolved_by: T-01` — `main()` misdescribed |
| `PF-049c59c515c538bc41da6616176f8987` | `info` | `open`, no `resolved_by` — census is a feature, recorded non-action |

Severities are the **reader's own**. Finding 1 stays `med`: the lead upheld it over pm's earlier
"advisory" after corroborating the relative-path convention itself (digest `:76-81`). Not downgraded.

## Deviation 1 — the id recipe, and it is not cosmetic

The dispatch specified typed 8-hex ids from `sha256(reader|severity|summary)`. **I used the canonical
computer instead:** `python3 .claude/skills/harness/bin/panel_findings.py id --reader <r> --summary <s>`,
which yields `PF-` + the first **32** chars of `sha256(reader + "\n" + normalize_summary(summary))`
(`panel_findings.py:28-33`), severity **excluded** from identity.

Why: `panel_findings.py` is by its own docstring "the ONE place a panel finding's identity is
computed, so the validator lead, pm and check-state.sh cannot disagree", and `harness-spec-driven`
says compute every id with it and never type one. A hand-typed id is not reproducible by
`sign-approval --overrule PF-ID`, which refuses an id absent from `panel.findings`
(`plan-merge.py:295-299`), nor by check-state INV-32 (`check-state.sh:514-517`). Including severity
would also have re-hashed finding 1 the moment the lead upheld `med` over "advisory" — making the
lead's own ruling rewrite the id. The template's `PF-0123abcd` is an 8-hex illustration the shipped
tool does not produce.

## Deviation 2 — the dictated guard assertion is unbuildable, so I hardened it differently

The dispatch asked for `assert 'BUG442_MUTANT_CHILD' not in os.environ` placed **before any mutant is
built**. The child inherits that variable, so the assertion fires **in the child**: the child then
fails its own test and the clean-unmutated `child.returncode == 0` control can never pass. Measured
both ways — probe transcript in this session, reproducible from the snippet at `plan.yaml:160-169`:

| environment | dictated bare assert | what T-01 now specifies |
|---|---|---|
| clean parent | proceeds | proceeds to the ladder |
| genuine child | **assertion fires — breaks the ladder** | returns, no recursion |
| leaked stale value in parent | fires | **fires loudly** |

An inherited-env marker cannot by itself distinguish a leaked parent from a child. T-01 now makes the
marker unforgeable: the child is invoked with `BUG442_MUTANT_CHILD` set to the **same fresh
`TemporaryDirectory` path** as `HARNESS_PROJECT_DIR`, and recognises itself by the two agreeing
(`plan.yaml:152-174`). Child-side early return preserved; parent-side absence asserted loudly. Exact
assertion and message text are written into the intent verbatim, so the implementer copies rather
than designs. **Residual, stated honestly:** a leaked value that exactly equalled this run's fresh
temp path would still skip — unreachable in practice, and it replaces a failure mode that fired on
any stale `1`.

## The other two folds

- **`verify:`** (`plan.yaml:79-82`) — four absolute worktree paths gone, all relative, still a literal
  `|` block (DEC-182: a folded `>` would make a lead's verbatim string mismatch the member's parsed
  value and block a correct task). The third grep is dropped as implied by the bare suite's rc.
  The **first two greps stay** — a test never registered in `TESTS` cannot fail the suite, so its
  `ok` line is the only proof it ran. Three-space `ok   ` spelling and `^...$` anchors preserved,
  confirmed at `tests/integration/test-harness-yaml.py:892-904`.
- **`main()` rationale** (`plan.yaml:201-208`) — corrected: `main()` wraps EACH test in its own
  try/except, so one failure never makes the others print FAIL. The consequence that matters is kept
  and sharpened: that is exactly *why* the control discriminates, since a genuine red shows
  `ok   test_bare_date_scalar_stays_str` **alongside** the witness's FAIL, while an import-time or
  whole-file parse failure shows neither. The assertion itself is untouched.

## Receipts — both writes revalidated on reload

```
PANEL cycle 0 -> .../plan.yaml            (set-panel,  exit 0)
APPLIED .../plan.yaml
AMENDED tasks:T-01.verify                 (amend,      exit 0)
APPLIED .../plan.yaml
AMENDED tasks:T-01.intent                 (amend,      exit 0)
APPLIED .../plan.yaml
```

**Route note:** the dispatch's `apply --proposal -` for T-01 **cannot work** — `apply` refuses with
**exit 7 CONFLICT** when an id exists in the base with a different value (`plan-merge.py:729-743`); it
unions new ids, it does not replace fields. Demonstrated (exit 7, plan unmodified), then done with the
`amend` verb under `--expect-sha256`, which is the declared route for revising an existing value and
preserves the original `|` scalar form.

Unchanged and confirmed by re-read: `approval:` (`:3-4`, still `pending`), `status: plan` (`:5`),
D-01..D-03 (`:16,20,24`), one task only (`T-01` at `:69`), and T-01's `id`, `title`, `traces`,
`change_type`, `execution_mode`, `execution_agent`, `depends_on`, `status`, `files`.
`check-plan-routes.py` on this plan: `OK T-01`, 0 violations, exit 0.

## Open questions

- **Q1 (non-blocking):** the dispatch's 8-hex `reader|severity|summary` id recipe conflicts with the
  shipped `panel_findings.py`. I used the tool. If the operator wants the typed form, the four ids
  above change and any later `--overrule` must use whichever form is on disk.
- **Q2 (non-blocking):** T-01's guard now differs from the dictated assertion, for the measured reason
  in Deviation 2. Flagging because the departure was from an explicit instruction, not because the
  design is in doubt.
