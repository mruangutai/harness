# QA distillation — FEAT-2458-shape-stamp-sweep

**BLUF:** 5 ops applied, net +1 entry. Craft: 3 replaces (P-02, P-09, P-14) sharpen existing rules in full sections. Repository `harness`: replace G-13, add G-15. Every applied op passed check-expertise. No suite was run and no diff was reviewed.

## Receipts
- Craft: batch `a62b70631ee48de46f18a260f6a3dc0d395130e929db819ee2949cee2e0f8793` → `.harness/expertise/harness-qa.md`. Counts before→after: Patterns 15→15, Gotchas 15→15, Outcomes 10→10, Open 1→1.
- Repository (harness): batch `64c836f8a187d67f59ef7bbaf0e6416428db7e25ea767de1dd2a0aa8c5b5441c` → `.harness/harness/expertise/harness-qa.md`. Counts before→after: Patterns 0→0, Gotchas 14→15, Outcomes 0→0, Open 0→0.
- Receipt: `.harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/expertise-receipt-dbb2bef79a883750d7b938f60a623d6bb146ae67c4ff2384501c6862bf8d6f55.json`

## Candidate judgments
1. **Fixture id containing the asserted token: accepted** → craft `replace P-02`. Merged into the substring-vacuity rule, which now also covers text the fixture supplies itself. The section was full, so no new entry was added.
2. **Pre-fix tests on the same mutant as a control arm: accepted** → craft `replace P-09`. One control-arm rule now covers both the neutered-effect arm and the pre-fix-tests arm.
   - **Write-guard half: accepted as repository-tier** → `replace G-13`. A variable-target `rm` is blocked too, and a python/shutil driver works. The guard belongs to this repository, so it is not craft.
3. **Flag-gated case registry: accepted twice.**
   - The general form → craft `replace P-14`: a test the kind's cmd never reaches is not evidence. That covers both a glob match without list membership and a flag-gated registry.
   - The repository fact → `add G-15`. Re-checked at main `86ce6ba`: only `tests/integration/test-check-plan-routes.py:2475` references `--canonical-reader-self-test`. `.github/workflows/tests.yml:243` runs `--canonical-reader-audit`. The fact still holds.
- **Skim-only: `bool(reason)` weakening missed by a PASS-name-set comparison: rejected.** The same-name assertion-weakening class is already covered by craft G-06 (redo proofs after a rewrite) and P-09 (control-arm discrimination). The patterns and gotchas sections are full, and no weaker entry was found to displace.

## Principles applied
- None: no leaf was read for this distillation.
