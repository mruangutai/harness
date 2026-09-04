# Goal-check retake — FEAT-52 — eight criteria, graded at `review_sha 1497d104` (HEAD `638046a0`)

## BLUF

**FAIL — one substantive blocker survives, and it is B1 unchanged.** Seven of the eight retaken
criteria are now met on substance; the eighth (SC-03/04/05/06/11 as a family) rests on carriers the
runner still refuses to reach **in the committed tree**. The remediation moved the two test files by
**ADDING copies under `tests/integration/` and deleting the `bin/` originals only in the working
tree — the deletions are uncommitted**:

```
git status --porcelain
 D .claude/skills/harness/bin/test-anchor-directions.py
 D .claude/skills/harness/bin/test-check-instruction-paths.py
git ls-tree -r --name-only 1497d104 | grep test-anchor-directions
  .claude/skills/harness/bin/test-anchor-directions.py      <- still present
  tests/integration/test-anchor-directions.py
```

`suite_layout.violations()` run over a tree materialised **from `1497d104`** returns exactly the two
pre-remediation messages (`test-shaped file remains under bin: …`). `run-unit-tests.sh` reads the
filesystem and exits 2 before any test (`:34-43`), so in CI or any fresh clone of this branch **no
kind runs at all**. Locally `--check-layout` exits 0 only because of the uncommitted deletion — the
exact tree-versus-ref trap the last two cycles were graded on. The `bin/` blobs are also **stale**:
`bin/test-check-instruction-paths.py` is the 84-line pre-remediation copy, missing SC-06's restored
half, while `tests/integration/` carries 96 lines.

**Fix is one commit: `git rm` the two `bin/` paths, then re-pin `review_sha` to it.** No content
changes are needed; every assertion already passes.

## Verdicts

| SC | Verdict | Evidence at `1497d104` |
|---|---|---|
| SC-03 | **not_met (B1 only)** | five separate `scope contains …` assertions present and green (`tests/integration/test-check-instruction-paths.py:70-72`); carrier unreachable in the committed tree |
| SC-04 | **not_met (B1 only)** | `test-anchor-directions.py` 7/7, exit 0, run with `HARNESS_REVIEW_SHA=1497d104` and again at default; rows S1-S5 each read via `git show <ref>:<path>` |
| SC-05 | **not_met (B1 only)** | inline `:1:`, fenced `:3:`, `2 violation(s)`, exit 1 — green; carrier unreachable |
| SC-06 | **not_met (B1 only)** | discriminating half RESTORED (`:74-84`): `product_cwd` temp checkout, `not os.path.exists(product_path)` conjoined with `isfile(debug_path)` and a content read. Substance proven |
| SC-09 | **met** | `DECISIONS-INDEX.md:214` ruling written (`Two anchors, not one: …`); `test-gen-decisions-index.py` 12 ok, exit 0 — B4 closed. Contract at `harness-handoff/SKILL.md:62-66` |
| SC-11 | **not_met (B1 only)** | row `SC-11 S2 write observations` green; whole-scope row green (`scanned N file(s), 0 violation(s)`); carrier unreachable |
| SC-12 | **met** | `test-inject-expertise.py:249-252` now asserts `.omp/agents/harness-qa.md:1` in the drifted context alongside both count lines; 21/21, exit 0 — B3 closed |
| SC-14 | **met** | four per-file findings at the pin: `harness-product-lead.md:92`, `harness-eng-lead.md:110`, `harness-validator-lead.md:138`, `harness-orchestrator.md:157`, plus `harness-handoff/SKILL.md:66` |

B5 (orphaned pin) is **closed**: `1497d104` is an ancestor of `HEAD` and on the branch, so the
`git show <review_sha>:<path>` criteria grade a commit that will merge.

## The one substantive blocker

**B1 — the DEC-213 violation is uncommitted-fixed, i.e. not fixed.** Everything else in this retake
is evidence-complete. Nothing about the five affected criteria's *content* is deficient.

## Advisory, non-gating

- `test-anchor-directions.py:15` defaults `REF` to `HEAD`, not to `feature.json review_sha`. The two
  coincide in content today, so no grade turns on it, but a qa run without the env var grades HEAD
  while the criterion mandates the pin.
- SC-06's `product_cwd` is an empty temp dir joined with the relative path rather than a `chdir`.
  Measurement is equivalent; the criterion's wording says "process working directory set to".
- SC-05's fenced fixture line is `.claude/agents/harness-pm.md`; the criterion says two relative
  `.harness/` paths. Both shapes are exercised, which is the criterion's stated purpose.
- The next commit deletes test carriers, so `review_sha` moves again — re-pin, do not re-grade
  content.

## Open question — approval, not a retry

The signed BRIEF declares `evidence: unit` for SC-03, SC-04, SC-05, SC-06, SC-11 (and SC-01, SC-02,
SC-12). **All eight carriers now live under `tests/integration/`**, and under DEC-213 the directory
IS the kind, so the declared label is false for all eight. The relocation was correct — each carrier
executes a real script subprocess — so the label, not the location, is what is wrong. Re-labelling a
signed criterion is not a pm write. Amend the BRIEF to `integration` for those eight, or reject the
relocation; I will not soften the label silently.
