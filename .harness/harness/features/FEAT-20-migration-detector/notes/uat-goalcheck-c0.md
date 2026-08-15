# Goal-check — FEAT-20-migration-detector — c0 (pin `434307a`)

**The feature's goal is substantively delivered: 14 of 15 SCs met, verified by me at `434307a`.
SC-10 is UNMET as written** — the feature's diff modifies 19 `.harness/` bookkeeping paths that its
text forbids. No shipped code is wrong; the criterion is unmeetable by any feature in this harness.
That one ruling needs the operator, so this returns ESCALATE rather than PASS.

## What I re-ran, and where the evidence comes from

Every `verify: automated` SC is bound to case output I produced at `434307a`, not to qa's bindings
at `11cb644`. Both suites re-run by me, in this tree, at the pin:

- `run-unit-tests.sh --kind unit` → exit 0; `PASS test-layout-migration.py`; all 18 case labels `ok`.
- `run-unit-tests.sh --kind integration` → exit 0; `PASS test-check-state.py`; `(x.1)`–`(x.5)` all `ok`.
- I read the **assertion bodies** for every SC-bearing case in `test-layout-migration.py` and
  `test-check-state.py:case_x`, not the labels (P-09). Each label names the verb it actually invokes.
- Live detector on the real root: `python3 .claude/skills/harness/bin/layout_migration.py .` →
  exit 0, `examined 20 feature dir(s), 1 doc root(s), 7 reader file(s)`, `layout: 2 surface(s) clean,
  0 mixed, 0 cannot-verify`.

**The SHA gap is closed.** `git diff --name-only ea476fd..434307a` → **7 paths, all bookkeeping**
(`STATE.md`, `feature.json`, four `notes/review-*.md`, `observations/harness-validator-lead.md`).
**None of the 8 source files moved since the panel ran.** `git status --porcelain` over those 8 paths
is empty, so the bytes I tested are the pinned bytes.

## The three rulings

### Ruling 1 — SC-10: REJECT the source-files-only reading as a reading of the text. SC-10 is unmet as written.

Re-derived at the pin: `git diff --name-only 88b1182..434307a` = **27 paths** — the 8 in the closed
set, and **19 under `.harness/`** (BRIEF, plan.yaml, STATE.md, feature.json, research note, 5 receipts
/handoffs, 5 review notes, 2 observations logs, qa-c0). `git diff --diff-filter=R --name-status
88b1182..434307a` is **empty — nothing moves**, which is SC-10's second sentence and it is met.

SC-10 says "No file outside [the six categories] is modified by this feature." 19 files outside them
were modified. The reading qa applied and the validator lead upheld — that SC-10 bounds only the
shipped surface — is the right *intent* and the right thing to sign, but it is not what the sentence
says, and I will not record it as met on a reading the text does not carry (rule 15, P-05).

**What actually holds:** the shipped surface is exactly the 8 files the `lanes:` block enumerates,
all 8 appear in the diff, nothing outside them is code, and there are zero renames. The purpose of
SC-10 — detector only, no layout change — is fully satisfied.

**What breaks:** as written, this criterion forbids the harness's own per-feature bookkeeping, which
every feature necessarily writes. No feature can ever meet it literally, so leaving it unadjudicated
means every future goal-check re-discovers the same unmet SC. **Recommendation to the operator:**
sign the shipped-surface reading as the recorded ruling and leave the brief's text standing (a signed
brief is amended by re-signature, not by record correction — G-11). The alternative, amending SC-10's
wording, is a re-plan and changes no shipped code. Q1, blocking.

### Ruling 2 — the universal in the approved plan is false, but no SC turns on it. RECOMMEND narrowing both places.

`plan.yaml`'s decision prose and `docs/harness/DECISIONS.md` DEC-194 both assert "**Every finding**
names the reader path with the form it matched." False as written: `check-state.sh:1313-1318` emits
the `no-evidence` and `no-rows` causes with **no reader path** — correctly, because those two causes
have no reader to name — and `layout_migration.py:render()` (lines 256-259) does the same.

**No SC is unmet by this.** SC-14 reads "each reader **it names** carries the form it matched" and
SC-15 reads "the same form alongside **each reader path it names**" — both conditional on a reader
being named, and both hold at every branch that names one (`render()` lines 260-267; `check-state.sh`
MIXED at 1298-1301, `unreadable` at 1303-1307, `neither` at 1308-1312). BRIEF's own D-03 is already
correct too: "**Every named reader** carries the form it matched."

**Recommendation:** narrow the universal in **both** DEC-194 and `plan.yaml` to BRIEF D-03's existing
wording — the correct form is already written one document away. Both, not one: a docs-only fix leaves
the approved plan contradicting the code. The task set is untouched, so this is prose correction plus
a re-signature of the plan's decision text, not a re-plan of work. It should land before units 3-7
cite DEC-194 as their maintenance contract. I did not edit either file. Q2, non-blocking.

### Ruling 3 — regression-pinning is a NEW criterion. BRIEF never stated it. Do not adopt it silently.

BRIEF.md:20-24's subject is the **detector** reddening under perturbation of the **tree**: "…reddens
on the mixtures that indicate a migration went half-done. It is proven able to redden by perturbation
before it lands." REQ-07 operationalises exactly that — "Each failure mode has a sandboxed fixture
that shows the detector actually reddening on it" — and those fixtures exist and were exercised
(cases 2, 3, 4, 5a, 5b, 9, 10, 11, 12, 13, 16; `(x.1)`, `(x.2)`, `(x.5)`).

Sensitivity of the **suite** to mutation of the **detector's own code** is a different property. No
SC states it. Both named surviving mutations sit outside every SC's demand: the unrendered INV-27
cause branches (`no-evidence`/`no-rows`) are not required by SC-08, which asks only for *a* tree the
detector cannot judge (covered by `(x.2)`); and `+ len(migrated)` in `_evidence()` is invisible to
SC-01 and SC-12, neither of which pins an exact count.

**Ruling: new criterion, not an existing one.** It changes what "done" means, so it is the operator's
call. **Recommendation:** do not reopen FEAT-20 for it. Take it as a follow-up dispatch — integration
cases for the two unrendered INV-27 causes, and one count-sensitive `_evidence()` case — which
converts both named mutations into reddening tests and merges with qa's existing Q1. Q3, non-blocking.

## REQ coverage — all 8 traceable to shipped code

- REQ-01 → `layout_migration.py:209-211` (MIXED) + `render()` 260-267; `check-state.sh:1298-1301`.
- REQ-02 → live run on the real root exits 0, CLEAN both surfaces; unit case 15.
- REQ-03 → unit case 6.
- REQ-04 → unit cases 7, 8.
- REQ-05 → `exit_code()` 222-233 (2 outranks 1); `check-state.sh:1302-1318`; unit cases 9-13, 16;
  integration `(x.2)`, `(x.5)`.
- REQ-06 → `check-state.sh` INV-27 at session entry; `.github/workflows/tests.yml:185-232` in job
  `integration` (the only job in the file, and the required check per DEC-183).
- REQ-07 → 20 `tempfile.TemporaryDirectory` fixtures in `test-layout-migration.py`, red and green.
- REQ-08 → `layout_migration.py:182-183` marker branch; unit cases 14, 15; integration `(x.4)`.

## SC verdicts — all 15, each by its own declared method

| SC | method | verdict | evidence at `434307a` |
|---|---|---|---|
| SC-01 | automated/unit | met | `test-layout-migration.py` case 1, 4 assertions all `ok`: exit 0, feature-dir count > 0, reader-file count > 0, X+Y+Z == 2 |
| SC-02 | automated/unit | met | case 2 `ok` — split FEATURES evidence, `code == 1` and a line carrying both `features` and `MIXED` |
| SC-03 | automated/unit | met | case 3 `ok` — migrated evidence, one legacy reader, `code == 1`, line names `team-config.yaml` and carries `[legacy]` |
| SC-04 | automated/unit | met | case 4 `ok` — split DOCS evidence, `code == 1`, line carries `docs` and `MIXED` |
| SC-05 | automated/unit | met | case 6 `ok` — both surfaces migrated, every reader migrated, `code == 0` |
| SC-06 | automated/unit | met | cases 7 and 8 both `ok` — FEATURES-migrated/DOCS-legacy and its mirror, `code == 0` each |
| SC-07 | automated/unit | met | case 9 `ok` (`code == 2`, `[neither]`, file named, distinct from 0 and 1) with case 18's `exit_code` trichotomy 0/1/2 asserted in one case |
| SC-08 | automated/integration | met | `test-check-state.py` `(x.1)` reddening tree → exit 1 + INV-27; `(x.2)` unjudgeable → exit 1 + CANNOT VERIFY; `(x.3)` applicable clean → **no** INV-27 line. All fixtures, not the live tree |
| SC-09 | inspection | met | `.github/workflows/tests.yml:190` runs the detector; `:232` `exit "$rc"` propagates exit 1 and 2; `:203-206` fails the step on a missing `layout:` summary; `:209-212` fails on a missing `examined` line. Step is in job `integration`, the only job in the file (`:32`) |
| SC-10 | inspection | **unmet** | `git diff --name-only 88b1182..434307a` = 27 paths: 8 in the closed set, **19 under `.harness/`**, 0 renames. Shipped surface and "nothing moves" both clean; the sentence as written is not. See Ruling 1 |
| SC-11 | inspection | met | 20 `tempfile.TemporaryDirectory` fixtures in `test-layout-migration.py`; the only real-tree touch is case 1's read-only `scan(REPO_ROOT)`. I bracketed `git status --porcelain` around a full re-run of **both** suites: `diff` exit 0, byte-identical, twice |
| SC-12 | automated/unit | met | case 14 `ok` twice — pinned `NOT APPLICABLE: no harness control-plane marker at ` literal, and all 6 trailer numbers `== {0}`; case 15 `ok` — same fixture plus the marker gives CLEAN with non-zero counts, so 14 passes on the marker, not on an empty scan. `check-state.sh` silence proven by integration `(x.4)` |
| SC-13 | automated/unit | met | case 16 `ok` — docs rows dropped → `code == 2`, `no reader rows for this surface`, and a `docs` line still printed; plus case 1's `X+Y+Z == 2` for the summary-accounting clause on the real repository |
| SC-14 | automated/unit | met | case 3 `ok` (`[legacy]` on migrated evidence — FINISH) and case 5b `ok` (`[migrated]` on legacy evidence — REVERT). Both directions, same suite. Conditional wording holds at `render()` 260-267 |
| SC-15 | automated/integration | met | `(x.1)` `ok` — the INV-27 line names `gen-decisions-index.py`, carries `[migrated]`, and ends with the remedy (`atomic commit`, `check-state.sh:1289-1290`) |

## Open questions

- **Q1 (blocking).** The brief's closed-set criterion forbids the harness's own bookkeeping, which
  every feature necessarily writes — so no feature can meet it literally. Sign the shipped-surface
  reading as the recorded ruling (brief text stands), or amend the criterion in a re-plan. No shipped
  code changes either way. Recommendation: sign the reading.
- **Q2 (non-blocking).** The approved plan and DEC-194 both claim every finding names a reader path;
  two cause branches correctly name none. Narrow both to the brief's existing "every **named** reader"
  wording before units 3-7 lean on DEC-194.
- **Q3 (non-blocking).** Regression-pinning against code mutation is a criterion the brief never
  stated. Recommend a follow-up dispatch, not a reopen.

## What I did not do

No file fixed, no `plan.yaml` or `BRIEF.md` edit, no `DECISIONS.md` edit, no commit. This note is the
only file I wrote.
