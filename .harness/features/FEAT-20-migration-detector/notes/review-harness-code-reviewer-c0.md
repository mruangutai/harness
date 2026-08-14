# Code review — FEAT-20-migration-detector — c0

**VERDICT: PASS with notes.** Stage 1 (spec compliance) clean: every changed line traces to a
`REQ`/`D`, no scope creep, no omission, and details match pinned values (output-contract strings,
exit-code contract, D-01's reader/surface partition, D-04's applicability gate). Stage 2 found one
real coverage gap, demonstrated empirically, and three lower-severity notes. Nothing gates:
`must_fix: []`, `severity_max: med`.

Reviewed: `88b1182..ea476fd`. `human_commits_in_scope: []` — all six commits are `FEAT-20`/`[harness:t-NN]`
tagged main-session or handoff commits; no `[harness:human]` since the pin.

## Stage 1 — spec compliance

Traced every hunk in the 8 named files against BRIEF REQ-01..08 and D-01..D-04, plus `plan.yaml`
T-01..T-04 intent (which is unusually prescriptive — verbatim output strings, numbered fixture cases
pinned by number in three documents). No violation found:

- `layout_migration.py`: `SURFACES` enum matches D-01 exactly (features/docs, no more); `READER_TABLE`
  has exactly the 7 rows D-01 names, none of the explicitly-excluded readers (`gh-sync.py`,
  `branch-create-gate.sh`, `validate-feature-json.py`, `factory_claim.py`, gitignore, prose) — grepped
  the module for all four names, zero hits. D-03's CANNOT_VERIFY/MIXED/CLEAN predicate order and the
  non-empty-reader-set precondition are implemented as specified (`layout_migration.py:200-227`). D-04's
  marker-first applicability gate is first in `scan()` (`layout_migration.py:191-193`), before any
  surface is judged. Output-contract strings (`examined …`, `layout: …`, the `NOT APPLICABLE:` literal,
  the five `[form]` tags) match the pinned text in T-01's intent byte-for-byte.
- `test-layout-migration.py`: all 16 plan-mandated cases present, unrenumbered, plus case 17
  (D-04/enum-table Q3) and case 18 (exit-code contract for T-02), both correctly appended rather than
  inserted. Fixtures are `tempfile.TemporaryDirectory`-scoped throughout (SC-11).
- `check-state.sh` INV-27 (`check-state.sh:1256-1319`): imports the two exposed functions, never
  shells out to the CLI (confirmed — no `subprocess`/`Popen` reference to `layout_migration.py`
  anywhere in the block); failed import is `bad.append`ed (`check-state.sh:1267-1271`), never a silent
  skip; the scan-time exception is separately caught and also appended (`check-state.sh:1273-1278`).
- `test-check-state.py` case_x (x.1)-(x.5): covers exactly the five fixtures T-02 mandates (reddens,
  cannot-judge, applicable-clean asserting INV-27 *absence*, no-marker, unimportable).
- `.github/workflows/tests.yml` Layout gate (`:185-233`): copies the Plan-route gate's full pattern —
  `|| true` on the grep (load-bearing under `bash -e`), three distinct `::error::` messages, all three
  counts checked (not two), `exit "$rc"` propagates both 1 and 2. Does **not** repeat the false
  "asserted by a `.py` case" claim next to Plan-route gate (per T-03's explicit prohibition) — confirmed
  byte-unchanged at that comment block, pre-existing GitHub issue #279, out of scope here as instructed.
- `docs/harness/DECISIONS.md` DEC-194 and `DECISIONS-INDEX.md`: all five T-04-mandated verbatim phrases
  present (`per coupled surface`, `cannot-verify, never clean`, `form agreement, never per-site
  completeness`, `inside the same atomic commit that migrates it`, `layout migration` in the index
  line); `gen-decisions-index.py --stdout` diff-clean against the committed index (this is literally
  T-04's own `verify:` gate, and I re-ran the same command it specifies).
- `SC-10` (closed file set): `git diff --name-only 88b1182..ea476fd` outside
  `.harness/features/FEAT-20-migration-detector/` = exactly the 8 `lanes:` files plus
  `.harness/notes/research-FEAT-20-migration-detector.md` (pre-existing per-feature bookkeeping, not a
  shipped surface). Matches QA's own citation independently reproduced.

**SC-09 (verify: inspection) — confirmed with citation.** `tests.yml:205-207` fails the step on a
missing summary line, `:210-213` on a missing examined line, `:228-230` on any of the three counts
reading zero, `:233` propagates the detector's own exit code (`exit "$rc"`) so both 1 and 2 fail.

**SC-10/SC-11 (verify: inspection) — confirmed with citation.** SC-10 above. SC-11: every
non-real-root fixture across both test files is built inside `with tempfile.TemporaryDirectory() as
tmp:` (`test-layout-migration.py` cases 2-18; `test-check-state.py` case_x's `build()` helper takes
`tmp` from the same idiom); case 1 is the sole exception and it only *reads* `REPO_ROOT`, never writes.

## Stage 2 — code quality

### F1 (med) — the evidence-count arithmetic has no discriminating test; demonstrated by perturbation

`layout_migration.py`'s `_evidence()` (features branch line ~146, docs branch line ~156) computes
`return shapes, len(legacy) + len(migrated)`. The verdict (CLEAN/MIXED/CANNOT_VERIFY) is driven
entirely by `shapes` (a set, built from the truthiness of the raw glob lists) — never by the summed
count `n`. `n` only feeds the printed `feature_dirs`/`doc_roots` numbers in the `examined …` line.

**What I ran, precisely** (not "the shipped suite passes on the mutant" — narrower than that): I wrote
a mutant copy of the module (`+ len(migrated)` deleted from both branches) into the scratchpad and ran
a 4-case subset of the real suite — case 1 (real root), case 6 (fully migrated), cases 7/8 (sanctioned
intermediates) — against it. All four still assert exactly what they assert today and all four pass
green. I did not execute cases 14/15 against the mutant; by inspection, case 14 never reaches
`_evidence` at all (the marker-absent early return in `scan()` fires first), and case 15 uses the
default all-legacy fixture (`build(tmp, marker=True)`), so its non-zero-count assertion is satisfied
entirely by the `legacy` addend the mutation didn't touch. I then added one additional, non-shipped
probe case against the same mutant — a fully-migrated fixture, same shape as case 6 — and it failed:
the printed line reads `examined 0 feature dir(s), 0 doc root(s), 7 reader file(s)` while the surfaces
correctly report `CLEAN — evidence migrated`. Confirms the count is genuinely wrong under the mutation
and that no case in the shipped 18 would have caught it — grepped `test-layout-migration.py` for every
`m.group(`/`s.group(` reference: only lines 171/172/174 (case 1, real root, legacy-only today), 289
(case 14, zero-count branch), and 298 (case 15, all-legacy) touch a count group. None exercises a
fixture where `len(migrated)` is the only non-zero addend.

**This is not fail-open and does not gate today.** Verdicts read `shapes`, never `n`, so exit codes
stay correct under this mutation — CLEAN stays CLEAN, MIXED stays MIXED. The failure direction is the
opposite: a count regression here would ship green today (the harness tree is still all-legacy, so
`len(migrated)` is always 0 in practice and the bug is inert) and would first manifest as a **CI
false-FAIL** — `tests.yml:219-230`'s zero-count branch would misfire "discovery did not run" on a
tree that is genuinely, correctly CLEAN, once the real repository's evidence shifts from legacy to
migrated. Session entry (`check-state.sh`) is unaffected either way — INV-27 never reads the counts.
The exposure window is precisely units 3 through 7 of map #336, the sequence this detector exists to
protect, and it stays latent until exactly the moment case 1 runs against a migrated real root.

**Does not re-litigate already-ruled item 4.** That ruling's chain (`n==0 ⇒ shapes empty ⇒
CANNOT_VERIFY ⇒ exit 2 ⇒ reddens case 1`) holds only because, under an *unmutated* module, `n` and
`shapes` are computed from the same underlying evidence and move together. This mutation breaks that
coupling on purpose: `shapes` is built from `if legacy:`/`if migrated:` truthiness checks on the raw
glob lists, entirely untouched by the arithmetic change to `n`. The implication chain the ruling relies
on does not reach this case.

**Same class, folded in rather than filed separately:** `reader_files += sum(1 for _p, f in readers if
f != "unreadable")` (`layout_migration.py:199`) has the identical shape — no case asserts the exact
`reader_files` count on a fixture holding an unreadable reader (case 10 asserts only the exit code and
the `[unreadable]` tag), so the `!= "unreadable"` exclusion is also unproven by any assertion.

**Remedy, stated not prescribed:** append (never renumber) a case asserting `examined` counts against a
fully-migrated or split-evidence fixture, and one asserting the exact `reader_files` count with an
unreadable reader present.

### F2 (low) — DEC-194 overclaims "every finding names the reader path"; traced to the plan, not the documentor

`docs/harness/DECISIONS.md`'s DEC-194 states "Every finding names the reader path with the form it
matched" as a universal. Two of the four CANNOT_VERIFY causes — `no-evidence` and `no-rows` — have no
reader to name by design (`layout_migration.py`'s `render()` explicitly gives them their own wording
instead: "no evidence of either shape under …" / "no reader rows for this surface"), so the sentence is
false as a universal against the code it describes. This is **not documentor drift**: the sentence is
transcribed close to verbatim from `plan.yaml` T-04's mandated substance
(`plan.yaml:663-665`), while the same plan's T-01 intent (`plan.yaml:364-367`) is the one that
specifies the two no-file causes that falsify it. The plan text itself is internally inconsistent; the
documentor correctly reproduced what was handed to them. `kind: mismatch, path:
docs/harness/DECISIONS.md, ref: D-03`. No behavior is affected — this is prose only.

### F3 (low) — blame-selection logic is duplicated, not shared, across the two call sites

`layout_migration.py:render()` (`:250-256`) and `check-state.sh`'s INV-27 block (`:1291-1295`) each
independently recompute "which readers are responsible for a MIXED verdict" from the same
`SurfaceReport.readers` list, via near-identical but hand-copied list comprehensions (confirmed
extensionally equal today: for a MIXED surface, `neither`/`unreadable` readers can never appear
because those causes force CANNOT_VERIFY earlier in `scan()`, so the two comprehensions' visible
difference — INV-27's checks `f == "both"` only, `render()` checks `f in (both, neither,
unreadable)` — is currently a no-op). The structured `Result`/`SurfaceReport` T-01 exposes carries no
pre-computed "blame subset," so a future edit to one selection rule (e.g., widening what counts as
"responsible" for a MIXED surface) can drift from the other without either test suite noticing, since
each suite only exercises its own call site's rendering.

### F4 (info) — cause priority can mask a co-occurring second cause within one CANNOT_VERIFY surface

`scan()`'s cause order is unreadable > neither > no-evidence > no-rows (first match wins,
`layout_migration.py:203-214`). If a surface has both an unreadable reader and a separate reader
carrying neither form, the report — at both call sites — names only the unreadable one; the neither
reader surfaces only on a subsequent run after the first is fixed. This is a narrower instance of the
per-file-not-per-site residual bound the module already documents and signs (D-03), not a new class of
gap, and no SC requires multi-cause reporting within one surface. Noted for completeness, not
actionable.

## Cleared checks (verified, not left as an assumption)

- **`# balance:` comment claim, verified against `test-check-plan-routes.py:1136-1145` (`case_20`'s
  `logical_lines()`):** it joins physical lines by counting `(`/`[`/`)`/`]` on the raw text, uncorrected
  for string-literal content — confirms the claim that unbalanced parens inside a `READER_TABLE`
  pattern string would merge logical lines and hide the module's marker probe from that case. (In
  practice `layout_migration.py` isn't even in `case_20`'s scope today — none of its lines pair
  `.harness` with one of that case's PREDICATE substrings — so the comment guards against a future
  edit, not a live coupling; still, the mechanism it describes is real.)
- **Enum/table both directions hold:** table→enum via `validate_table()` (case 17, `LayoutTableError`
  raised and caught by INV-27's own `try/except Exception` around `scan()`, so a corrupted table is a
  loud violation, never a crash of the whole gate); enum→table via the fixed `SURFACES` iteration plus
  the `no-rows` CANNOT_VERIFY branch (case 16).
- **CI propagates exit 2, not just exit 1:** `tests.yml:233`, `exit "$rc"` where `rc` is the detector's
  raw exit code, unconditionally forwarded once the three guard branches pass.
- **`validate_table` runs before the marker check, always** — a corrupted table is caught regardless of
  applicability, not gated behind D-04's branch.

## Open questions

- Q1 (non-blocking): this role's `bash-write-guard` blocked every redirect/cp/write inside the
  scratchpad path the dispatch names as writable, not just repo paths — the perturbation demonstration
  above had to go entirely through the `Write` tool instead of the shell redirects the dispatch's SHELL
  NOTE describes. Worth a look if future dispatches expect scratchpad shell writes to work for this role.

```yaml
VERDICT: PASS
DIGEST:
  headline: Spec compliance clean across all 8 files; one demonstrated med-severity coverage gap (evidence-count arithmetic untested under migrated-only evidence) plus three low/info notes, none gating.
  severity_max: med
  findings: 4
  must_fix: []
  spec_violations: []
  reviewed: "88b1182..ea476fd"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "bash-write-guard blocked scratchpad shell writes (redirect/cp) for this role, contrary to the dispatch's SHELL NOTE; demonstration had to route through the Write tool instead. Is scratchpad meant to be shell-writable for harness-code-reviewer?", blocking: false }
  files_touched: [.harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-c0.md]
  expertise_update: []
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-c0.md
```
