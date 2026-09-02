# Cycle 5 re-plan — the census shape, and what it changed

**The census is now a PROCEDURE, not a list.** `D-10` defines the fix scope as *every live-tree
mutation site the census scan reports at build time*, and states that no count or file list
anywhere in the plan defines that scope. The enumeration was the defect: three sites, then four
(FEAT-45 `70fd441`), then eight (FEAT-50/BUG-1071 on the rebase) — three rewrites of one list on a
branch whose subject is that the shared tree moves underneath a running suite.

**The derivation, in one line:** list every `test-*.py` under `.claude/skills/harness/bin`,
snapshot `(size, mtime_ns)` of that directory, run each file with a thread polling `os.listdir`,
re-snapshot, print `SITE <file> <basename>` per pair. Deterministic (every site creates its mutant
unconditionally), no grep pattern to get wrong, no taint model to reimplement. Cost ~250s serial,
which is why it is a build-time procedure and **not** a verify block.

**Why derived was unavoidable and not merely tidier:** two of the eight basenames embed
`os.getpid()` — `.feat50-bash-write-guard-<pid>.sh`, `.feat50-check-domain-<pid>.sh`. No fixed
basename list could ever have named them.

**Dated, non-binding observation at `2a5cbada` (2026-09-01), derived at source:** 8 sites in 4
files. `test-check-state.py` ×4 (`:2241`, `:2377`, `:3286`, `:3591`), `test-feature-worktree.py`
×1 (`:583`), `test-bash-write-guard.py` ×1 (`:898`), `test-check-domain.py` ×2 (`:1473` the
`feature_schema.py` overwrite, `:3285` the `_feat50_mutant_between` helper with two callers).

**Boundary:** the scan's file set is bounded by the `.claude/skills/harness/bin/**` lanes glob, so
adding a file needs no lanes row. D-03's walk is repo-wide, so a site *outside* the glob has no
lanes row and is an **escalation to the operator**. All 59 discovered test files are under the glob
at this tip — vacuous today, stated because FEAT-47 moves the tree.

**Allowlist still refused (D-04).** Derivation makes the SET open; it does not make any member
optional. That distinction is written into D-10 so the shape change is not read as a softening.

## Per-id consequence

| id | change | why |
|---|---|---|
| **D-10** | `choice` + `because` rewritten: derived scope, derivation procedure, dated non-binding observation, boundary + escalation, allowlist refusal restated, two-instrument division | the governing decision |
| **T-01** | `title`, `intent`, `verify` | now owns **both** `test-check-domain.py` sites; `verify` gained a bin-directory `appeared` poll so SITE B is actually proven |
| **T-02** | `title`, `execution_reason`, `intent`, `verify` | site list deleted; owns the **second** `test-check-state.py` mutant (`case_inv32_era_guard_is_load_bearing`, called unconditionally at `:4317`); `verify` reads its own `files:` out of `plan.yaml` and runs them **concurrently** (33.6s + 5.7s measured serially, 60s budget) |
| **T-07 (new)** | added by `apply` | `test-bash-write-guard.py`. See the tooling blocker below |
| **T-03** | `intent` | **no scan or assertion change needed** — see below |
| **T-04** | `intent` | "T-02's four sites" → the derived set |
| **T-05** | `intent`, `verify` | 190/DEC-207 → 192/DEC-209 dated; DECISIONS entry must now carry `"derived and not enumerated"` and `os.getpid()`, both added to the verify's `need` list |
| **T-06** | `intent`, `verify` | SC-02 control route |
| **D-01, D-09, D-11** | `because` | stale/undated anchors and "T-02's four sites" |

**What I deliberately left, with the reason.** T-02's verify **mechanism** was already derived — it
polls for what *appeared* rather than matching basenames, and D-10's own text already said a new
site "reddens it on its own". That is kept unchanged in substance. What failed was the enumeration
*around* it: the four-item site list in the intent and the two-file run set the verify iterated by
literal name. So the list went and the poll stayed.

**T-03 (step 5, explicit): its scan and its assertions are unchanged, and its `verify:` needed no
edit.** Its ten historical anchors are read out of `git show ea6f51f` — a pinned tree — so they
cannot rot; its `discovered >= 50` floor holds at 59; and its live-tree `returncode == 0` **becomes
satisfiable** once T-01, T-02 and T-07 land, verified by walking each of the 8 sites against T-03's
taint rule (each is `open(p, "w")` on a name joined onto `HERE`/`dirname(SCRIPT)`/`__file__` →
flagged). Nothing else is needed. Three additions to its `intent:` only: it is named the
**completeness instrument**, the 58→59 count is dated and marked non-binding, and the "live tree is
THIRTEEN" paragraph is replaced — the live finding count is now asserted nowhere.

**T-06 (SC-02 control, `PF-2781572957dd1fed4`).** The safe third shape is named: `iso =
isolated_bin(tempfile.mkdtemp())`, write `git show ea6f51f:…/test-check-domain.py` into it, run it
there. The pre-fix probe derives its target from `dirname(realpath(__file__))`, so inside the copy
it breaks the **copy's** module. The intent now forbids the live route explicitly and says a zero
control is fixed at the poll, never by moving onto the live tree. A new required line `control
method: isolated bin copy` and a new verify leg make the `int(ctrl[0]) > 0` leg reachable by the
route the task text now names — the panel's A2 gap.

## Blockers and reportables

1. **No verb edits a list field.** `amend` exits 4 on `files:`/`depends_on:` ("apply's job"),
   `apply` exits 7 on any existing id whose value differs. **Measured, both.** Consequences: the
   `test-bash-write-guard.py` site could not join T-02's `files:` → **T-07**; and T-03's
   `depends_on:` cannot be widened to name T-07 → the ordering is carried as an **instruction** in
   T-03's and T-07's `intent:` (*"if you reach T-03 with T-07 unlanded, return BLOCKED"*) plus a
   D-10 paragraph. This is the same class of gap as the `panel:` key.
2. **#1053 `## Scope` still reads "Folded into FEAT-47"** (cycle-4 F-06). Outside my writable
   domain; the orchestrator owns issue text.

## Smoke test

T-07's authored verify, run verbatim against the **unfixed** tree: exit **1**,
`appeared ['.feat50-bash-write-guard-45032.sh'] moved [] red_case 1`. A working positive control,
and it confirms the `bash-feature-checkout-red` case-name grep. Every verify block in the plan
`ast.parse`s clean. `check-plan-routes.py`: **0 violations**, 7 DEVIATION lines (the DEC-174
carve-outs).

## No SC moved, and none needs to

Checked all ten against the derived census. **SC-03** is the one that could have collided and does
not: its ten anchors are pinned to `ea6f51f`, and its live-tree zero *is* the derived criterion —
an outcome, not an enumeration. **SC-02** does not say where the pre-fix control runs, so the
isolated route satisfies it as written. **SC-01** is narrower than T-01's now-widened work, which
is fine: an SC grades an outcome, not a task's file list, and SITE B is covered by SC-03 and SC-10.
`BRIEF.md` changed in exactly two places, both wording repairs inside stated requirements: the
settled FEAT-47 question retitled and rewritten as a record, and the `## Verification gaps` bullet
extended with the `control method:` line T-06's verify now enforces.

## Anchor audit — how I checked, not that I did

Regex-swept every `file.ext:NNN` and bare `:NNN` in the plan **excluding the `panel:` block**
(cycle 4's record, untouched). 14 surviving anchor lines, each resolved to one of three states:
pinned to an immutable sha (T-03's `want` set and its historical paragraph, both `git show
ea6f51f`), explicitly dated + marked non-binding with its durable identifier named (D-01 `:125`,
D-09 `:147-157`, T-04 `:60-74`, T-01's blanket sentence, T-03's blanket sentence), or structural
(`four-levels-up`). Every numeral likewise: 58→59 dated, 190/DEC-207→192/DEC-209 dated, "four
sites" removed from D-11 and T-04, "the ten"/"thirteen" removed from T-03. Re-derived at
`2a5cbada` myself: 59 test files, 192 headings last DEC-209, `run-unit-tests.sh` loop at 147-157,
`harness_boundary.py` resolvers at 44/53/84. The `test-check-domain.py` false-positive anchors
(`:1772`, `:1778`) had **already drifted two lines** against the ccf674a figure they cite — which
is why T-03's blanket sentence names them as illustration.

## Stations

All seven tasks and the feature stay at `plan`. No `set-task-station` or `set-feature-station` was
run. `approval.status` remains `pending`; `panel.cycle` remains 4; `panel:` untouched.

## Closing pass — T-07 collapsed into T-02, the ordering hole closed by an edge

**Supersedes `## Stations` above.** That section recorded this cycle's first pass, when all seven
tasks were at `plan`. T-07 is now `abandoned`. Everything else it says still holds: `approval.status`
is `pending`, `panel.cycle` is 4, `panel:` untouched.

**The hole is now structural.** The live DAG is a total order — T-01 → T-02 → T-03 → T-04 → T-06 →
T-05, one task per ready wave — so no two tasks can ever be siblings in a wave and no ordering needs
a sentence to hold it. T-03's `depends_on: [T-01, T-02]` was already on disk; what changed is that
T-02 now owns every site T-03's live-tree zero must not see, so the edge is sufficient. The prose
instruction *"if you reach this task with T-07 unlanded, return BLOCKED"* is gone from T-03's intent.

**The substantive half was the verify, not the sentence.** Striking T-02's exclusion line alone would
have been cosmetic: T-02's `verify:` built `run_set` from `t["files"]`, the write-once pair
`plan-merge.py` cannot grow, so the pre-fix positive control would never have gone red on the
`test-bash-write-guard.py` site. The block now derives its run set from plan.yaml's **ownership
graph** instead: this task's `files:`, plus the files of every task whose station is `abandoned` and
whose `depends_on` names T-02, minus the files of every still-live task. No third filename is spelled
anywhere in the block, and T-01's `test-check-domain.py` is excluded by the subtraction rather than by
being left out of a list. `absorbed` being non-empty is an assertion, so the derivation cannot
silently narrow back to two files.

**Why no new D-NN.** The commitment — a superseded task is stationed `abandoned` and its files are
absorbed by the task its `depends_on` names — is recorded inside D-10, which already owned "ownership
is split by file, and T-07 exists for a tooling reason". Under the DEC-149 bar it is not separately
hard to reverse and carries no trade-off independent of D-10. One entry, one home.

**How coverage was confirmed — read back, not assumed.** The amended block was extracted from
plan.yaml on disk and executed:

- Derivation prologue re-executed from the stored value: `run_set` is the three files,
  `absorbed = ['.claude/skills/harness/bin/test-bash-write-guard.py']`, `missing []`.
- Whole block run verbatim under `bash -c` in a synthetic root (the live `bin/` was never touched):
  RED when the absorbed stub drops `.feat50-bash-write-guard-<pid>.sh` — exit 1, that basename under
  `appeared`; GREEN when it writes nothing — exit 0. That is the proof the absorbed file is actually
  executed, not merely listed.
- Two guards, on mutated copies of the plan: un-abandon T-07 → `absorbed` empty → exit 1; let a live
  task claim the file → subtracted → `absorbed` empty → exit 1.

**T-07 mentions.** 19 before, 8 after. Every survivor is historical or self-describing: three in
D-10's supersession paragraph, one in T-02's intent ("cycle 4 carved it out as T-07; that task is
abandoned"), two in T-03's intent recording what the prose used to do, one in T-07's own superseded
intent, and the `- id: T-07` key itself. None orders work. D-11's `because` lost its
`T-01, T-02 and T-07 remove` enumeration in the same pass.

**T-07's retained `verify:`** is a single-file instance of the same ownership check. The one assertion
it carried that T-02's does not is the `bash-feature-checkout-red` ok-line; T-02 subsumes it into
"every file in the run set exits 0". Encoding the case name in T-02 would have re-created the
enumeration D-10 abolishes.

**No REQ orphaned.** Verified at source: T-07 traces `[REQ-01]`, and T-01, T-02 and T-04 all still
carry `REQ-01` in `traces:`. The blocking branch did not fire.

**Gates at this tip.** `check-plan-routes.py <plan>`: 7 DEVIATION, 0 VIOLATION, exit 0 — unchanged
from before the edit; every deviation is the expected DEC-174 carve-out. T-02's machine-field budget
is 47 of 50 after the longer verify, T-04 the plan's worst at 50.

**One tool defect worth raising.** `plan-merge.py amend --show` flattens a folded `>` scalar to one
line per paragraph **and drops the blank separators**, so feeding `--show` output straight back
through `--value-file` collapses a multi-paragraph folded value into a single paragraph. It happened
to D-10's `because` on the first attempt; I re-split on the section openers and re-amended, and the
eight paragraphs are back. Any future amend of a folded field has the same trap.

## Cycle 6 — the three Advisor amends, applied

**All three landed; nothing else in the plan changed.** A field-by-field diff of `HEAD:plan.yaml`
against the working copy reports exactly five changed fields — `D-10.because`, `T-01.intent`,
`T-02.intent`, `T-03.intent`, `T-07.intent` — and no other key, task, decision, `verify:`, `files:`,
`status:`, `depends_on:`, `panel:` or `approval:` value differs. Base tip `8ca95d65`, tree otherwise
clean apart from the pre-existing untracked `notes/panel-value-c5.yaml`.

**Amend A — T-03's print contract (goalcheck F-05).** One sentence appended to the "TWO LINES THE RUN
MUST PRINT" paragraph: the pair is printed exactly once per process invocation, for the one scan that
invocation was asked to run (live-tree walk or `--scan-dir`, never both), and the in-file self-test
cases call the scan function directly and print neither line. `T-03.verify` untouched, so
`len(disc)==1` stays discriminating rather than being relaxed.

**Amend B — T-01's unlabelled numeral (goalcheck F-10). I re-measured rather than attributed.** The
48ms/111-files figure could not be attributed honestly: no cycle records the sha it was taken at, and
D-11's 117-at-`ccf674a` shows it was already stale, so inventing a sha for it would have been a
fabricated label. Re-measured here at `8ca95d65` on 2026-09-01: `shutil.copytree` of
`.claude/skills/harness/bin` costs 25-42ms across three runs and copies 146 files (126 excluding
`__pycache__`; copytree copies the caches too, which is why 146 is the number the function pays for).
The sentence now carries the sha, the date, the D-10 non-binding marker, the superseded figure and a
re-derive instruction — the house style D-01's twin figure at `:44` already sets.

**Amend C — the derivation prose, four sites, one wording.** D-10's formula said the derived set
subtracts "the files of every still-live task"; the code at `plan.yaml:466-467` excludes the task
itself (`x["id"] != "T-02"`). That divergence is what put a false premise into a dispatch brief and
cost part of a consult to disprove. All four sites — re-derived, now at `:210`, `:226`, `:510-511`,
`:1323-1324` — read "minus the files of every OTHER still-live task" plus "the task's own `files:`
are excluded from that subtraction", worded consistently. T-07's `intent:` is safe to amend: the
derivation block reads `status`, `depends_on` and `files` only (`:464-467`), never `intent`.

**Paragraph counts, before and after, re-read from disk after each amend** (raw block bodies, split
on blank lines): `D-10.because` 8 to 8, `T-01.intent` 18 to 18, `T-02.intent` 10 to 10,
`T-03.intent` 17 to 17, `T-07.intent` 5 to 5. No folded scalar collapsed — `D-10.because`'s LOADED
value also still carries its 8 paragraph openers, checked against `git show HEAD:` of the same field.
I avoided the `--show` flattening trap entirely: value files were extracted as RAW dedented block
bodies through `plan-merge.py`'s own `_item_range`/`_field_block` locators, edited textually, and fed
back; `--show` output was used for nothing but the sha256.

**Every `plan-merge.py` invocation, all exit 0, no refusals.** Five `--show` reads (`D-10.because`
`65b59d86...`, `T-01.intent` `b96bf281...`, `T-02.intent` `ec012c8a...`, `T-03.intent` `6be45c2f...`,
`T-07.intent` `2b28b201...`), then five `amend --expect-sha256 <that sha> --value-file <path>`
writes, each printing `AMENDED <key>:<id>.<field>` / `APPLIED <plan>`.

**Gates after the change.** `check-plan-routes.py <plan>`: exit 0, `grep -c DEVIATION` = 7,
`grep -c VIOLATION` = 0 — unchanged. `yaml.safe_load`: approval `pending`/`None`/`None`, feature
status `plan`, `panel.cycle` 4, T-07 still `abandoned` with `depends_on: [T-02]`, T-02's `files:`
still exactly `test-check-state.py` and `test-feature-worktree.py`.

**The one regression these amends could plausibly cause is excluded.** T-02's own derivation block
(`plan.yaml:459-470`) re-run against the amended plan:
`run_set ['test-bash-write-guard.py', 'test-check-state.py', 'test-feature-worktree.py']`,
`absorbed ['.claude/skills/harness/bin/test-bash-write-guard.py']` — non-empty, so T-02's positive
control still reaches the superseded file.

**Untouched, deliberately.** T-07's shape, T-02's `files:`/`verify:`, every `verify:` block, the
`panel:` key (cycle 4's record, replaced by a separate `set-panel` dispatch), `approval:`,
`BRIEF.md`, `feature.json`, `STATE.md`. No new task, no new decision. No re-dating of 59 to 60 or
192/DEC-209 to 193/DEC-210: those are correctly-dated stale observations, which is what D-10 intends.
