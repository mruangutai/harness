# Plan panel — cycle 6 — scope (harness-code-reviewer) — FEAT-48-parallel-safe-suite

Reviewed at `047f6914` (working tree clean, confirmed via `git status --porcelain` and
`git rev-parse HEAD` at dispatch time). Worktree used exclusively:
`.claude/worktrees/harness/FEAT-48-parallel-safe-suite`.

**Would I sign this plan at `047f6914`? YES**, with one new low/med-grade documentation finding
(the D-10 tooling-capability claim, below) that the operator should see but that gates nothing.

**Did the rebase falsify anything? YES — one sentence.** D-10's claim that `plan-merge.py amend`
"refuses a list field" is now stale: the rebase pulled in `--yaml-value` (commit `b1e346c6`,
absent at `2a5cbada`/`38dd3622`, present at `a93a1df9`/`8ca95d65`), which CAN grow a list field.
Every other sentence I re-derived held. Detail below.

**Satisfiability sweep: 0 strictly unsatisfiable, 0 under-specified** (down from cycle 5's
honest union of "0, 1"). T-03's amendment closes the one under-specified case.

---

## 1. Grading the rebase

I independently re-ran or re-derived every orchestrator measurement rather than adopting it:

| claim | my measurement | match |
|---|---|---|
| 60 discovered test files | `find` with D-03's exact prunes → **60** | ✅ |
| 193 DECISIONS.md headings, last DEC-210 | `grep -c '^## DEC-'` → **193**, tail → `DEC-210` | ✅ |
| all 193 carry the em-dash | `grep -c '^## DEC-[0-9]* — '` → **193** | ✅ |
| `run-unit-tests.sh` serial loop, one occurrence | `grep -n '"\${SCRIPTS\[@\]}"'` → **line 148, sole hit** (distinct from `ALL_SCRIPTS`/`UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`, all present at :49-51,:58,:64,:99-100) | ✅ |
| no 9th live-tree mutation site (`test-quarantine.py`) | Read the file: `HERE`/`__file__` builds only the CLI-under-test path (read-only subprocess target); every fixture write goes through `fixture_root()` → `tempfile.mkdtemp(prefix="quarantine-test-")` at `test-quarantine.py:93`. Zero live-tree writes. | ✅ |
| T-02 derivation post-amend | Executed the actual `absorbed`/`run_set` code from `plan.yaml:467-475` against the live tree → `absorbed=['.../test-bash-write-guard.py']`, `run_set=['test-bash-write-guard.py','test-check-state.py','test-feature-worktree.py']` | ✅ |
| `check-plan-routes.py` 7 DEVIATION / 0 VIOLATION / exit 0 | Ran it → identical 7 lines (T-01,T-02,T-03,T-04,T-05,T-06,T-07), 0 violations, exit 0 | ✅ |
| paragraph counts preserved (8/18/10/17/5) | Extracted raw indented blocks from `git show 8ca95d65:...` and `047f6914:...` for D-10.because, T-01/T-02/T-03/T-07.intent, split on blank lines → **8→8, 18→18, 10→10, 17→17, 5→5** exactly | ✅ |

All six confirmed independently. All still-present hazard sites re-verified by direct read (not
grep-only, since one grep hit — `test-check-domain.py:2373-2376` — is a **false positive**: it
already copies into a tempdir via `shutil.copytree` before mutating, i.e. it is NOT a live-tree
hazard; this is exactly the trap D-10 built the census procedure to avoid). The real sites remain
present, unmoved in shape, after the rebase: `test-check-domain.py:1480` (SITE A), `:3276-3289`
(SITE B, `_feat50_mutant_between`, writes into `HERE`); `test-check-state.py:2241,:2377,:3286,:3591`;
`test-feature-worktree.py:583-585`; `test-bash-write-guard.py:891-903`.

### Finding — D-10's tool-capability claim is falsified by the rebase

- **reader**: scope
- **severity**: med
- **pointer**: `plan.yaml:215-217` (D-10.because, unamended by cycle 6); `.claude/skills/harness/bin/plan-merge.py` (no match anywhere for the quoted string "a list or mapping field would need its structure rewritten, which is apply's job")
- **why**: D-10 states, in the present tense and with no dating hedge (unlike every numeral around it): *"plan-merge.py amend refuses a list field (measured, exit 4: 'a list or mapping field would need its structure rewritten, which is apply's job')."* I grepped the current tool for that exact string — zero matches. Tracing the actual exit-4 site (`plan-merge.py:1409-1411`, inside `_amend_show`) shows a **different** message, reachable only under `--show`. More importantly, `git log -S'yaml-value' -- plan-merge.py` shows `--yaml-value` (commit `b1e346c6`, "Allow structured plan field amendments") is **absent** at `2a5cbada` and `38dd3622` (D-10's own authoring point and the plan's pre-rebase base) and **present** at `a93a1df9`/`8ca95d65` — i.e. the rebase itself introduced it. With `--yaml-value`, `amend` CAN replace a list/dict field wholesale (`plan-merge.py:1498-1504`), which is precisely the route the cycle-6 Advisor consult (`runs/2026-09-01-08-validator/digest.md`, Q1) constructs and names verbatim (`amend --key tasks --id T-02 --field files --yaml-value`) before recommending against using it. **Consequence**: a reader of `plan.yaml` alone — without the advisor consult digest — is told a capability doesn't exist when it does, and told a receipt (a quoted exit-4 message) that no longer appears anywhere in the tool. This does not change the plan's shape (see §6: the *reason to keep T-07* survives on other grounds — replace-not-append — argued correctly in the consult), so it is not gating. But it is a plan sentence that reads as true and is not.

---

## 2. Satisfiability sweep — 0 unsatisfiable, 0 under-specified

I swept all seven `verify:` blocks (T-01 through T-07; T-07's is "retained for the record" but is
itself satisfiable — it is structurally identical to T-01's ownership-check shape).

- **T-01**: `crash`/`untouched` string-match assertions align exactly with the case-naming
  instructions in intent (2b "named so it reads as a control", 2d "phrased … the case name must
  contain the words 'never written'"). `appeared` stays empty by construction since SITE B moves
  into a tempdir copy, never `b`. Satisfiable.
- **T-02**: derivation code (`:467-475`) matches all four amended prose sites verbatim in
  substance (see §3b). `absorbed` truthy is guaranteed by T-07. Satisfiable.
- **T-03**: **was** cycle 5's one under-specified block — `len(disc)==1` (`:630`) versus intent's
  "print them in both modes" (`:706`, pre-amend) conflicting with the in-file self-test cases that
  also scan fixture tempdirs (`:756-786`). The amendment at `:706-709` adds the missing
  architectural constraint: the print happens exactly once per invocation, at the CLI entry point,
  and the in-file self-test cases call the scan function directly, bypassing the print. This is a
  genuine two-layer design (inner `scan()`, outer printing wrapper) a faithful implementation can
  build — not a restatement of the old sentence. **F-05 is CLOSED BY FIX, not merely reworded**:
  the new text supplies the missing disambiguating mechanism, which the old text did not have in
  any form.
- **T-04**: block-header/PASS/FAIL/summary-line format checks all trace to intent's literal
  contract text (`"----- <basename> …"`, `"PASS <basename>"`, `"pool: <n> workers, <k> files…"`).
  Satisfiable.
- **T-05**: phrase-presence + word-floor + index-regen check; independent of amends. Satisfiable.
- **T-06**: literal-substring and regex checks against `run-unit-tests.sh` and the measurements
  note; independent of amends; `BIN_DIR`, the drift detector (`run-unit-tests.sh:60-74`), and
  `--check-kinds` (`:39`) all still exist in the shape the plan assumes. Satisfiable.
- **T-07**: retained-for-record; same ownership-check shape as T-01, never dispatched.
  Satisfiable in principle.

---

## 3. Grading the three amends at source

**(a) T-03's print-contract sentence — CLOSES F-05, does not merely restate it.** See §2. The
three conflicting anchors goalcheck named (`:601`→now `:630` `len(disc)==1`; `:667`→now `:706`
"both modes"; `:749-786`→now `:756-786` fixture-tempdir self-tests) are now reconciled by an
explicit two-layer contract, not by relaxing the verify block.

**(b) The four derivation-prose sites now agree with the code AND with each other.** Code at
`plan.yaml:472-473`: `absorbed -= {f for x in T if x["id"] != "T-02" and x.get("status") !=
"abandoned" for f in x["files"]}` — excludes T-02 itself from the subtraction. (Note: the shared
context cited this at `:466-467`; it is actually at `:472-473` at this tip — a ~6-line drift, minor,
does not change the substance.) All four amended prose sites now read, word-for-word in structure:
*"minus the files of every OTHER still-live task — [task]'s own files: are excluded from that
subtraction"* (D-10 twice, at `:203-207` and `:220-224`; T-02.intent at `:512-516`; T-07.intent at
`:1329-1333`). Consistent with each other and with the code.

**(c) T-01's figure is now labelled to D-10's own standard.** `plan.yaml:385-388`: "Measured cost,
a DATED and NON-BINDING observation re-measured at 8ca95d65 on 2026-09-01 (D-10): 25 to 42ms across
three runs, copying the 146 files copytree sees under that directory." Matches the
sha+date+DATED/NON-BINDING+D-10-citation pattern used throughout D-10. Confirmed.

---

## 4. The 146-vs-117 question — ruled

**They do NOT count the same thing, and the plan's own phrasing invites a reader to think they
do.**

I measured directly with `git ls-tree -r` at both shas:

| sha | direct-under-bin, tracked (D-01/D-11's method) | total tracked incl. `fixtures/` |
|---|---|---|
| `ccf674a` | **117** | 121 |
| `8ca95d65` | 122 | **126** |

D-01 (`:44`, "Measured cost of the copy at ccf674a: 44ms for 117 files") and D-11 (`:296`, "bin/
holds 117 files at ccf674a") both match **117 = tracked files directly under `bin/`, excluding
`fixtures/`**, exactly.

T-01's "146 files copytree sees" is, by its own label, whatever `shutil.copytree` — deliberately
built with "no mode, no filter, no cache argument" (`:390-391`) — traverses: `fixtures/` PLUS
`__pycache__`, which is untracked, ephemeral bytecode-cache state that depends on what has been
imported in that exact working directory at that exact moment, not a property of the git tree.
Current-tip measurement: 126 tracked (incl. `fixtures/`) + 22 files actually present under
`__pycache__` right now ≈ 148, consistent with "126-ish tracked + ~20 pycache ≈ 146" at 8ca95d65.
Real tracked-file growth `ccf674a`→`8ca95d65` is **117→122 (+5)**, not the ~29 the raw 117-vs-146
juxtaposition suggests.

**The problem**: `plan.yaml:387-388` says the new figure "replaces an unlabelled 48ms-for-111-files
figure … since D-11 records the directory at 117 files at ccf674a" — this sentence puts the two
numbers side by side as if updating the same metric, without ever stating that `copytree` counts a
strictly larger, non-reproducible set (fixtures + ephemeral bytecode cache) that "holds N files"
never meant. A reader cannot tell them apart from the text alone; they must independently reason
about `shutil.copytree`'s traversal semantics and remember that `__pycache__` is untracked. This is
covered by the finding in §1 in spirit but is a distinct defect — logged separately since it
concerns measurement methodology, not tool capability.

- **reader**: scope · **severity**: low · **pointer**: `plan.yaml:385-388` vs `:44`, `:296` · **why**: a future auditor comparing "117 at ccf674a" to "146 at 8ca95d65" will read ~29 files of unexplained growth and go looking for it in the wrong place (sibling merges) when ~20 of it is `__pycache__` noise that a repeat run of the same measurement, seconds later, could report differently again. Not gating — neither figure is load-bearing on any `verify:` block — but it undermines the very "re-derive rather than trust it" discipline D-10 is trying to teach, because a reader who DOES re-derive will get a number that doesn't reconcile with either historical figure for reasons the plan never explains.

---

## 5. Cycle-4 gating high — re-verified independently at this tip

`PF-58719ff7b430616b91b5a7cfe49bde10` ("three unowned live-tree mutation site groups") —
**re-verified CLOSED**, not on cycle 5's word. Both `test-check-domain.py` and `test-check-state.py`
are in the rebase's changed-file set, so I did not accept the prior closure:

1. Re-read all four hazard-bearing files at the current tip (§1) — every site cycle 5 named is
   still present, same shape, same file.
2. Re-ran T-02's actual derivation code (§1) — `run_set` still includes all three files T-02 must
   own (`test-check-state.py`, `test-feature-worktree.py`, `test-bash-write-guard.py` via
   `absorbed`).
3. T-01's `files:` still names `test-check-domain.py` and `isolated_bin.py` (`plan.yaml:339-340`).
4. Confirmed via the D-03 census walk that **every** discovered test file (60/60) still lives under
   `.claude/skills/harness/bin/**` — the lanes glob — so nothing escaped ownership into an
   unresolved lane.
5. Confirmed the one NEW test file the rebase actually added (`test-quarantine.py`) carries zero
   live-tree writes (§1).

Ownership in this plan is per-FILE (via `files:`/derived `run_set`), not per-line, so line-anchor
drift inside an already-owned file does not reopen this finding — only a hazard appearing in a file
NO task owns would. I found none. **Closure holds, independently re-derived.**

---

## 6. The `abandoned` idiom — ruling

**I accept the Advisor's cycle-6 disposition (keep T-07, patch `gh-sync.py` separately) as sound,
and it is NOT gating — but it is not closed either; it is correctly still open, tracked outside
this plan.**

The reasoning that makes "grow T-02's files: instead" a non-solution is airtight and I re-derived
it myself in §1: `amend --yaml-value` **replaces** a field; it has no delete verb. Every
dissolution variant still leaves T-07's task entry in `plan.yaml` — `check-plan-routes.py` would
still emit its DEVIATION line for it (I reconfirmed: still 7 lines including T-07, `exit 0`),
`gh-sync.py`'s `all(status=="done")` gate (`:1152`, cited in the cycle-5 digest and unchanged by
this rebase — `plan-merge.py`, not `gh-sync.py`, was in the rebase's file list) would still refuse
on T-07's `abandoned` status, and `build.yaml`'s `steps_from` would still need to skip it by
convention. Growing `files:` adds redundancy (the file would then be named in two places) without
fixing any of the three tooling gaps S1/A2 actually named. The one-line `gh-sync.py`
`finished_stations()` fix is the correct remedy because it fixes the ROOT (three tools not
understanding `abandoned` as "absorbed, still load-bearing") rather than papering over one
consequence.

**My ruling**: this stays **open**, correctly — it is explicitly a cross-repo dependency
(`gh-sync.py` must be patched before FEAT-48 reaches review station) that **nothing in FEAT-48's
plan tracks**, exactly as the cycle-6 validator-lead flagged in the advisor digest's "my addition."
It is not a defect in THIS plan's shape (the plan cannot fix a bug in `gh-sync.py`), so it does not
gate signature. It is a genuine operational risk the operator should carry forward: if the
`gh-sync.py` fix does not land before FEAT-48 reaches review station, `gh-sync status review` will
exit 2 for this feature's entire life and the operator hand-syncs. Severity **med**, not high — the
fallback (hand-sync) is known-good and named.

---

## 7. Cycle-5's 16 findings — disposition

| # | reader | sev | c5 summary (abbrev.) | disposition | file:line (now) |
|---|---|---|---|---|---|
| 1 | goalcheck | med | no criterion fails if #1053's symptom persists | **still open, mitigated** — Advisor Q2 shows SC-05's ten `--kind all` runs DO exercise `test-gh-sync.py` (`run-unit-tests.sh:31`, `INTEGRATION_SCRIPTS`), so F-07's literal "no criterion fails" is too strong; but whether #1053 formally *closes* on FEAT-48 remains an explicit operator call (Advisor Q6) | `BRIEF.md:127-131`; `run-unit-tests.sh:31` |
| 2 | goalcheck | low | `os.getpid()` census drift, two doers see different SITE text | still open, unaddressed | `plan.yaml:180` (was `:167`) |
| 3 | goalcheck | low | chmod/utime-only or subdir site is census-invisible, scan-visible | still open, unaddressed | `plan.yaml:161-165`-equiv, `:185` (boundary clause) |
| 4 | goalcheck | low | 250s census over live tree, sibling-agent edit fabricates SITE line | still open, unaddressed | `plan.yaml:169` |
| 5 | goalcheck | low | T-03 `discovered` contract under-specified | **CLOSED BY FIX** — see §2, §3a | `plan.yaml:630` (`len(disc)==1`), `:706-709` (fix), `:756-786` |
| 6 | goalcheck | low | ea6f51f control run pastes a FileNotFoundError traceback | still open, unaddressed | `test-check-domain.py:1770`-equiv; T-06 SC-02 leg |
| 7 | goalcheck | low | #1053 `## Scope` still "Folded into FEAT-47" | still open — outside plan's write authority (issue body, operator hand-fix) | issue #1053 body; `BRIEF.md:213-224` |
| 8 | goalcheck | low | 5.3x headline vs. 120s/247s = 2.06x acceptance | still open, unaddressed | `BRIEF.md:139-146` |
| 9 | goalcheck | low | 48ms-for-111-files carries no sha/date | **CLOSED BY FIX, but see new finding §4** — the amend added a sha+date, satisfying the literal ask, but introduced a methodology ambiguity (146 vs 117 count different things) that the fix itself does not disambiguate | `plan.yaml:385-388` |
| 10 | code-reviewer | med | T-07 supersession not mechanically uniform (`check-plan-routes.py` DEVIATION, no `build.yaml` status filter) | **still open — accepted disposition, see §6.** Advisor Q1: keep, route fix to `gh-sync.py` (untracked cross-repo dependency) | `plan.yaml:1264` (T-07); `check-plan-routes.py` run live: still 7 DEVIATION incl. T-07, exit 0 |
| 11 | code-reviewer | low | T-02's declared `files:` understates touch scope (will also edit `test-bash-write-guard.py`) | still open, unaddressed (confirmed: `plan.yaml:461-462` still names only 2 files; the 3rd arrives only via derivation) | `plan.yaml:461-462` |
| 12 | code-reviewer | low | #1053 Scope stale, outside write authority | still open, same as #7, corroborated | issue #1053 body |
| 13 | code-reviewer | info | orchestrator's T-07-mention count off by one (7 not 8) | **closed/moot** — reconfirmed 7 mentions at this tip too (`grep -n T-07`); purely a correction of an external count, not a plan defect | `plan.yaml:213,219,222,533,655,658,1264` |
| 14 | should-not-exist | low | `abandoned` idiom collides with factory-wide "dropped" meaning; `gh-sync.py` cost | **still open — accepted disposition, see §6** | `gh-sync.py:1147-1154`; `plan.yaml:1264-1265`-equiv |
| 15 | should-not-exist | info | census-shape verdict: right shape, not relocation of rot | closed/moot — a positive assessment, reaffirmed by the fifth-rot test passing for real this cycle (§1) | `plan.yaml:146`-equiv; `:472-473` |
| 16 | should-not-exist | info | T-02's self-referential verify: `yaml.safe_load` not the strict loader; `absorbed` non-empty hardwires T-07 | still open, unaddressed (confirmed: `plan.yaml:468` still `yaml.safe_load(open(p))`) | `plan.yaml:468` (`safe_load`); `:492`-equiv (`absorbed and ...`) |

**Net**: 1 closed by fix outright (#5), 1 closed by fix with a caveat that reopens a related but
distinct low (#9 → §4), 2 closed/moot as non-defects (#13, #15), 2 still-open-but-accepted
dispositions carried forward by design (#10, #14, §6), 9 still open unaddressed (#1–4, 6–8, 11, 12,
16) — none of the 9 gate; all are low or the one already-mitigated med (#1).

---

## Severity max and gate

`severity_max: med` (the D-10 tool-capability finding, §1, and the accepted-but-open `abandoned`
disposition, §6). `must_fix: []`. Nothing here is `high` or `unrated`. **PASS with notes.**

## SEC-01

`validate-digest.py harness-code-reviewer` refuses every `code_grade` value (`n_a` included) and
refuses the key's omission, while `feature.json` has no pinned `review_sha` (INV-6, DEC-207: no
`review_sha` exists in plan phase and none can be pinned). This is a known harness defect, sixth
consecutive cycle. One terminal-yield attempt will be made; on refusal this artifact stands as the
record and the refusal is reported to `Feat48PlanReview.PlanPanelC6` by hub, verbatim.
