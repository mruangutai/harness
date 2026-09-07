# Panel rulings applied — BUG-151 — cycle 1 (plan drafting, unsigned)

**Both rulings are in the plan and the panel is transcribed. `approval.status` stays `pending`,
`status: plan`, no new task ids, no source code touched.** The layout-gate question was **CHECKED**,
not merely specified: `run-unit-tests.sh --check-layout` exits 0 with
`tests/integration/_bug151_baseline.py` present.

## What changed

- **D-01** — `choice` no longer defers to a measurement: the safeguard asserts **agreement of
  zeroness** (printed column-0 FAIL with returned total 0 is a failure; non-zero total with no
  printed FAIL is equally a failure), and strict per-block equality is explicitly **not** adopted.
  `because` now carries the settling reason (exit-code equivalence of the two candidate invariants,
  plus the 4-of-24-block sample being the very false-alarm risk it was hedging against) and cites
  `runs/plan-validator/digest.md` for the full argument.
- **T-01** — now purely **additive**. Deleted: old STEP 0 (baseline), its whole recovery apparatus
  (dirty-file conditional, sibling copy, sha-through-receipt hand-off, pre-edit ordering
  constraint), and old STEP 1 (the probe measurement, `/tmp/bug151_probe.py`, its table, and the
  "pm amends D-01 with the measurement" DIGEST obligation). Remaining steps renumbered 1–4. Case
  **(f)** is now unconditional — two column-0 FAIL lines with total 1 MUST yield `None`, named
  `two-printed-one-counted-agrees-on-zeroness` so the tolerance reads as deliberate. Old STEP 4's
  dangling "the invariant D-01 resolved to in step 1" is replaced by the predicate stated outright.
- **T-02** — step 8(a) only. It now owns the **entire** SC-03 equality in one place: `git show
  6d969ed3:tests/integration/test-check-domain.py` into `tests/integration/_bug151_baseline.py`
  (sibling, not `/tmp`, because the module anchors ROOT off its own `__file__`; not `test-*` because
  the runner globs that prefix), layout gate confirmed 0, both `ok`-name sets collected and asserted
  EQUAL with 0 column-0 FAIL lines and exit 0 from both runs, sibling deleted and `git status
  --porcelain` clean. `depends_on: [T-01]` and steps 1–7 are unchanged. One consequential tidy in
  8(b): "reachable the same way T-01's probe was" pointed at a construct this run deleted, so it now
  says "importlib-loading the REAL file by path" with the same `__file__` caveat.
- **BRIEF SC-03** — reworded only: the pre-change set is "recovered from the pinned commit
  `6d969ed3` and run as a sibling copy inside `tests/integration/`, not read out of the working
  tree", and "both halves are taken together, in one task". No REQ/SC added, renumbered or moved.
- **`panel:`** — `last_run: plan-validator`, `cycle: 0`, **both** readers at `status: ran`
  (`should-not-exist`/`fable-advisor`, `scope`/`harness-code-reviewer` — the latter's zero findings
  are recorded by its reader row alone), two findings at the reader's own severities (med, low),
  both `disposition: resolved`, `resolved_by: T-01` and `T-02`. A `transcription_rule` records that
  both summaries were reworded off the digest headings, so their PF ids differ from ids computed
  from the heading text.

## Evidence

| call | exit | new sha256 of the amended value |
|---|---|---|
| `amend decisions D-01.choice` | 0 | `7934252d4ba1996d8d8cda0525ac17ddc874dba412140921145e090ef1a77282` |
| `amend decisions D-01.because` | 0 | `a4eed85a8900b1597290633f7a975aec0a295b52e0ac80fce7287e72a72ea633` |
| `amend tasks T-01.intent` | 0 | `aadb47972a59ee83d26573181a47317199d463a3a0466e4930d64c64508cfc85` |
| `amend tasks T-02.intent` | 0 | `aedb5f0740e260e94403599075cb432dda481ddf7bda991c670d9752ce867652` |
| `set-panel` | 0 | n/a (`PANEL cycle 0 ->`, reload confirmed) |

- Acceptance 1 prints, exit 0:
  `pending plan ['T-01', 'T-02'] ['D-01', 'D-02'] plan-validator 2 [('PF-cf17fd813d058340727a00b9a33886cd', 'med', 'resolved', 'T-01'), ('PF-009cd606d15c7da41e40a02e87ad8b39', 'low', 'resolved', 'T-02')]`
- Greps over plan.yaml: `red measurement` **0**, `bug151_probe` **0**, `only obtainable now` **0**,
  `STRICT EQUALITY` **0**, `T-01's receipt` **0**. **`STEP 1` = 1** — see the conflict below.
- T-01 `intent` line count **85 → 56**; still contains `_AggTee`, `_aggregation_verdict`,
  `run_bug151_selfcheck_cases` and cases (a)–(f) (each verified present).
- Layout gate, CHECKED in the worktree: scratch `tests/integration/_bug151_baseline.py` created →
  `.claude/skills/harness/bin/run-unit-tests.sh --check-layout` → **exit 0, no output**; the flag is
  real (`run-unit-tests.sh:20,33-45` runs `suite_layout.violations` before the early exit). Scratch
  removed; `git status --porcelain` shows only the pre-existing untracked feature dir.
- `check-plan-routes.py <plan.yaml>` → `0 violation(s)`, exit 0.

## The one thing I could not satisfy literally

Acceptance 2 requires the string `STEP 1` to be absent, while change 1 requires the surviving steps
to be renumbered into a clean sequence. Any 1-based sequence reintroduces the token, so the two are
mutually exclusive. I renumbered (substance) and left `STEP 1 -- write the regression cases FIRST`.
The red measurement itself is verifiably gone: no `red measurement`, no `bug151_probe`, no
`STRICT EQUALITY`, no probe table, no D-01 measurement obligation. `probe` occurs once in
plan.yaml — inside the panel finding's own summary, which is a record, not an instruction.
