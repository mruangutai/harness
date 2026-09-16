## BUG-1290 · panel-recheck — VERDICT: PASS

**BLUF: all four claims confirmed by measurement. No new crit/high finding.** `plan.yaml` and
`BRIEF.md` are byte-unchanged (sha256 identical before/after this run; `git status --porcelain`
shows no path under `features/BUG-1290-factory-claim-repo-root/` as modified — only the
untracked feature dir and an unrelated grilling note appear, both pre-existing `??`).

### CLAIM 1 — PANEL-01 closed — **confirmed**

- (a) `check()` prints `f"FAIL  {name}"` (`test-factory-integration.py:74-81`, two spaces,
  confirmed by reading the function body). Case (H)'s real call is
  `check("(H) claim against the two-board fleet exits 0", ...)` at `:1264-1265` (not `:1266-1267`
  as the upstream panel-digest/product-digest chain cites — a pre-existing 2-line anchor drift
  that originates in my predecessor's panel note, not in `plan.yaml`; `plan.yaml`'s own PANEL-01
  summary cites `:1245-1246`, which is exact). The marker string itself is byte-identical to
  `plan.yaml` T-02's `verify:` grep target. Not gating — noted as a low, non-blocking citation
  defect in the *notes* chain, not in the plan.
- (b) Case (H)'s fixture line (`:1246`) sits in `tests/integration/test-factory-integration.py`,
  T-02's sole `files:` entry, and T-02 `intent:` step 2 explicitly instructs `:1245-1247`. Confirmed.
- (c) Traced: after T-02, both (F) and (H) fixtures resolve under `REPO`'s own segment (`widget`).
  After a correct T-03, `factory_config.features_root("acme/widget")` also resolves to the
  `widget` segment, so case (H)'s claim finds its plan, `check(...)` passes (`ok`, not `FAIL`), the
  file's single `FAILS` counter stays at the count contributed by unrelated cases, and
  `sys.exit(1 if FAILS else 0)` exits 0 — T-03's `&&`-chained verify goes green on this fixture.
  Confirmed.

### CLAIM 2 — the inventory — **confirmed**, with one low-severity citation gap

Re-ran the grep myself (`re.search(r'\.harness', line)` over every line, not the two known
numbers): **24 hits**, not the ~19 pm's prose individually names:
`27, 30, 31, 429, 534, 536, 538, 539, 542, 697, 880, 882, 1246, 1404, 1405, 1452, 1453, 1495,
1496, 1506, 1558, 1559, 1608, 1609`.

Exactly two are hardcoded features-root fixture joins — `:882` (F) and `:1246` (H) — both inside
T-02's `files:`/`intent:`. Every remaining hit is out of scope and **none would redden any task's
verify after a correct build**:
- `534, 536, 538, 539, 542` — `make_root()`'s docstring + `HARNESS_PROJECT_DIR`/marker-probe body
  (`docs/SPEC.md`, `team-config.yaml`) — no features-root join, never read by `_BlockerCache`.
- `697` — a comment referencing `.harness/harness.json`, prose only.
- `1404/1405, 1452/1453, 1495/1496, 1558/1559, 1608/1609` — five paired writes of a case's own
  `.harness/harness.json` (read remotely via `factory_gh.file_at_ref`, never through
  `features_root`/`segment_of`).
- `1506` — already on the `widget` segment, drives `board_lifecycle.py audit`, not `claim`.
- `27, 30, 31, 429` — module/file-level prose.

**Omission found:** pm's inventory (`plan.yaml` T-02 `intent:` and the pm research note) does not
individually cite `534, 536, 697`, or the second line of each `.harness.json`-write pair
(`1405, 1453, 1496, 1559, 1609`) — 8 hits absent from the written list. None is a third fixture
join; each falls cleanly into a category pm already names by reason (marker-probe docstring,
harness.json write, prose). Confirmed by inspection of each line's text — no path-join through
`".harness", <var>, "features"` appears anywhere outside `:882`/`:1246`. **Low severity, non-gating**
— the scope determination (exactly 2 joins) is correct; only the written enumeration's granularity
is short of exhaustive.

### CLAIM 3 — A-01 closed — **confirmed**

- (a) Read `layout_migration.py:92-96` verbatim (not retyped from memory): legacy row at `:93`
  `r'"\.harness", "features"'`, migrated row at `:94` `r'"\.harness", [^,)]+, "features"'`.
  Probe (`python3 -c`): the paren-free join text `".harness", seg, "features"` matches migrated,
  not legacy; the parenthesised `".harness", segment_of(repo_name), "features"` matches **neither**.
  Confirmed — T-03's paren-free local is what keeps the row live.
- (b) T-04's probe control strings `L = os.path.join(H, ".harness", "features")` and
  `M = os.path.join(H, ".harness", seg, "features")`, tested against the same two real row
  patterns: legacy matches L, legacy misses M, migrated matches M — full ladder holds. Confirmed.
- `factory_config.py` anchors also re-verified: `_BIN_DIR` at `:37`, `harness_boundary` import at
  `:34`, matching D-01's citation exactly.

### CLAIM 4 — transcription faithful — **confirmed**

`plan.yaml:116-261` diffed against `runs/2026-09-05-06-validator/digest.md` and the predecessor
note: `last_run`, `cycle: 1`, `team: plan-panel`, `verdict: FAIL`, `code_grade: n_a`,
`send_backs: 0` all match. Both readers present, `status: ran` for both (`harness-code-reviewer`/
`scope`, `fable-advisor`/`should-not-exist`) — neither skipped, `fable-advisor`'s literal
`verdict: 7 findings` preserved (not normalised to PASS/FAIL). All 9 findings present
(PANEL-01, A-01, PANEL-02, A-P1, A-P2, P3-merged, T05-mechanism, A-D03, A-D04), each with
id/severity/reader/summary/disposition; PF- ids present and stable (not recomputed by me, per
dispatch). The 7 dismissed findings all carry their reader's own reasoning, not a bare verdict word
— no dismissal reads as upgraded to a fix. A-01 severity stays `med` (its reader's rating);
`record_notes` discloses the lead's must_fix ranking separately from severity, the reviewer's
`none`→`info` normalisation on the T-05-mechanism entry, and the "PANEL-03 (P2)" mislabel plus "P2
rests on `should-not-exist` alone" — all three disclosures present verbatim.

### New crit/high findings

`[]` — none. The one gap found (Claim 2's incomplete written enumeration) and the one anchor-drift
found (Claim 1a's `:1266-1267` vs. real `:1264-1265`) are both low-severity, non-behavioral, and
do not change any task's `verify:` outcome on a correct build.
