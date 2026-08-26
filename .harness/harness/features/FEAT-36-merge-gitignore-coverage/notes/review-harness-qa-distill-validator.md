# Distillation blocked: three accepted craft rules cannot be applied

All three digest-skim candidates pass the six-spawn durability test and belong to craft Expertise; no repository-specific rule qualified. The mandated merge tool refused their union proposal because `Patterns` is already at its 15-entry cap and the proposal would contain 17 entries. No Expertise file changed.

## Source assessment

- Observations: `observations/harness-qa.md` is absent; accepted 0, rejected 0.
- Digest-skim: accepted 3, rejected 0, applied 0.
  - Aggregate gates: **accept**. Require non-zero discovery and execution counts for every required kind plus explicit absence of misconfiguration and kind drift; it sharpens existing P-13's count-evidence rule.
  - Python mutation bytecode: **accept**. Equal-size, same-timestamp mutations can reuse bytecode and invalidate an isolated controlled probe; disable bytecode writing in child processes.
  - Preservation criteria: **accept**. Assert both the requested target transition and byte-identical preservation of a pre-existing caller fixture; target-only evidence misses collateral mutation.

## Curation and counts

Craft before/after: Patterns 15/15, Gotchas 15/15, Outcomes 10/10, Open 1/1. Repository before/after: Patterns 0/0, Gotchas 4/4, Outcomes 0/0, Open 0/0.

No current entry is demonstrated stale. The intended curation ops were:

1. `replace P-13 (Patterns)`: `WHEN reporting a green aggregate gate DO state per-required-kind non-zero discovery/execution counts and no misconfiguration/kind drift; never treat a raw aggregate total or matching baseline count as coverage without a named test.`
2. `replace P-03 (Patterns)`: `WHEN a criterion requires a requested target change while preserving caller state DO assert both the target transition and byte-identical preservation of a pre-existing caller fixture — target-only evidence can pass after collateral mutation.`
3. `replace G-06 (Gotchas)`: `WHEN a controlled Python mutation probe changes source at equal size within one timestamp tick DO disable bytecode writes in isolated children — reused bytecode can execute the baseline and invalidate the probe.`

The mandated `expertise-merge.py apply` supports union addition only, not those replacement operations. It refused before mutation with `CAP EXCEEDED section=Patterns cap=15 union_size=17` (exit 8). This is a merge-tool cap refusal, not a domain-hook refusal; no alternate write was used.

## Receipts and verification

Exact intended Expertise ops: the three `replace` operations above. Exact successfully applied Expertise ops: `[]`. Changed Expertise files: `[]`. Per-file `check-expertise.sh` output: none required or run, because no Expertise file changed. No formatter, linter, build, or project-wide test ran.

## Canonical handoff

Escalate to the validator lead: either extend `expertise-merge.py` with lock-safe replace/drop support or provide an approved curation mechanism, then apply the three accepted craft entries and run `check-expertise.sh .harness/expertise/harness-qa.md`. The repository tier remains unchanged.
