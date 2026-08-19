# QA gate — FEAT-27, full feature, pinned `252fa72`

**VERDICT: PASS.** Tree identity holds exactly (`HEAD == 252fa72`, `git diff --stat 252fa72` over
every graded file is empty). Every task's matrix obligation is discharged with re-run evidence, not
carried testimony where I could re-derive cheaply. T-01's `config`/T-04–T-06's `docs` → `[]` are real,
not apologised-for. T-07's `logic` → `unit` is satisfied, with its own guard-mutant reproduced by me
independently. SC-02 and SC-07, unassessable last round, are now assessed — both hold, both with a
disclosed gap. The could-not-fail census confirms the four known items and finds no more within the
two files swept.

## 1. Matrix, per task, per kind

| Task | change_type | Obligation | Command | rc | Result |
|---|---|---|---|---|---|
| T-01 | config | `[]` | n/a — real outcome, not a gap | — | discharged by design |
| T-02, T-03 | logic, cross_module | `unit`; `unit`+`integration` | carried from `2117a46` gate (6 SCs mutation-proven) | 0 | files unchanged since `2117a46` (`git diff --stat` empty for both test files and both scripts under test) — re-established below, not re-derived |
| T-04 | docs | `[]` | n/a | — | discharged by design; T-04's own `verify:` re-run below as corroboration |
| T-05 | docs | `[]` | n/a | — | discharged by design; T-05's own `verify:` re-run below |
| T-06 | docs | `[]` | n/a | — | discharged by design; T-06's own `verify:` re-run below |
| **T-07** | **logic** | **unit** | `run-unit-tests.sh --kind unit` | **0** | `PASS test-inject-expertise.py`, 19/19, 0 FAIL lines in full captured output |

**Full-suite re-run, this session, at `252fa72`:**
- `--kind unit`: exit 0. 17/17 `test-*.py` scripts report `PASS <name>`, `grep -c '^FAIL '` = 0 over
  the whole captured output (905 lines, read in full — `tail` alone loses `test-board-station.py`'s
  own 8-case block above the final script's output).
- `--kind integration`: exit 0. 12/12 scripts `PASS`, `grep -c '^FAIL '` = 0.
- T-07's `verify:`, run **verbatim** against the dispatch's carried text: exit 0, `PASS
  test-inject-expertise.py`, no `^FAIL `, `def case13` present, `os.symlink` present. Matches
  `plan.yaml:735-743` exactly — no mismatch to report.

`matrix_ok: true`.

## 2. SC-01..SC-11 adequacy

| SC | Method | Evidence |
|---|---|---|
| SC-01 | bound (mutation, carried) | `test-inject-expertise.py:84-105` case1; unchanged since `2117a46` per `git diff --stat 2117a46 252fa72` (append-only, +25/-0, all of it case13) |
| SC-02 | bound by an executing assertion, **standing-suite gap disclosed** | T-01's own `verify:` (`plan.yaml:110-125`), re-run by me this session: `ALL-GRANTS-OK`, exit 0, all 16 agents' repo-tier and craft `--resolve` checks pass. **Gap**: this loop lives only in the task's one-shot `verify:`, not in `test-check-domain.py` — nothing in `run-unit-tests.sh` re-runs it, so a future regression on any of the 16 grants is not caught by the standing suite |
| SC-03 | rests on inspection (by design) | T-04's `verify:` re-run by me: `MIGRATION-OK`. It checks all 16 adjudicated entries (11 moved + 5 stayed) but as one combined presence-and-absence boolean per entry, not the 32 separately-reported assertions SC-03's text describes — corroborating, not a literal match to the SC's own phrasing |
| SC-04 | bound (mutation, carried) | `test-check-expertise.py` `run_extra` case1 + case2's 9 non-FEAT token classes; file unchanged since `2117a46` (`git diff --stat` empty) |
| SC-05 | bound (mutation, carried) | `run_extra` case6 (abspath) |
| SC-06 | bound (mutation, carried, both clauses) | case3 (no-repo-tier) + case5b (bad agent_type) |
| SC-07 | bound by an executing assertion | T-04's `verify:`, re-run by me: `check-expertise.sh .harness/expertise/` → 15 `OK` lines (+6 non-blocking `ADVISORY`s, expected per D-03); `check-expertise.sh .harness/harness/expertise/` → 6 `OK` lines. Each file named individually, matching SC-07's own wording exactly |
| SC-08 | rests on inspection (by design) | T-05's `verify:` (`DOCS-OK`) + T-06's `verify:` (`SKILLS-OK`), both re-run by me; plus my own `grep -nE 'expertise/<repo>|\*\*/expertise'` over all four named files — zero matches. Establishes the two admissible forms are present and the forbidden third form is absent in all four; does not establish every *other* prose sentence in the four files is accurate, which inspection by construction cannot |
| SC-09 | bound (mutation, carried) | case7a |
| SC-10 | bound (mutation, carried) | case1 |
| SC-11 | bound (mutation, reproduced by me independently) | case13, reproduced on a scratchpad copy (§4 below): unmutated 19/19; single-line-deleted mutant 18/19 with case13 the sole FAIL |

## 3. Fixture refresh — did it weaken anything?

**No.** Three questions, all independently checked, not accepted on say-so:

1. `test-harness-yaml.py:192,195` still read `assert list(mine) == expected_mine` / `assert
   list(shared) == expected_shared` — exact ordered equality, confirmed by reading the lines myself.
2. I independently re-derived all six expected `COLLECT_FIXTURE` entries **from `.harness/team-config.yaml`
   directly** (not from the parser), by `grep`-locating each of the six agents' repo-tier grant line
   and reading its surrounding domain block in full: `harness-orchestrator` (line 32),
   `harness-pm` (98), `harness-documentor` (131), `harness-backend-dev` (171), `harness-dev-ops`
   (215), `harness-eng-lead` (300). Every item, in order, in all six fixture lists matches the
   manifest's domain-block order exactly (the manifest's trailing `{ path: ".", read: true }` is
   correctly excluded — `mine` is upsert-only). **The eng lead's claimed positions (32, 98, 131, 171,
   215, 300 → fixture lines 40, 57, 76, 94, 112, 126) are confirmed, not merely accepted.**
3. The fixture pins 6 of 16 agents. The other 10's repository-tier grants are asserted by
   `test-harness-yaml.py`, **not at all** for list-equality/ordering — but T-01's own `verify:` (§1,
   re-run by me: `ALL-GRANTS-OK`) checks `--resolve` correctness for all 16, including the 10
   unfixtured ones. That is real, narrower coverage (resolves-to-the-right-agent) rather than none,
   but it is not the same claim as `COLLECT_FIXTURE`'s (exact domain-list equality and order), and
   it is not standing-suite protected (same gap as SC-02 above — it is a task verify, not a
   registered test).

## 4. Could-not-fail census

**Swept thoroughly**: `test-inject-expertise.py` (all 13 cases) and `test-check-expertise.py` (base
`case()` list lightly, `run_extra` — this feature's own T-03 addition — thoroughly). **Not swept**:
every other test file in the tree; out of bound per the dispatch's own scope limit.

**Method check (required before trusting a clean read on anything else): does my method flag a KNOWN
instance?** Yes — reading `test-inject-expertise.py:281` directly shows `"Traceback" not in stderr"`
in case11, and independently reproducing T-07's own guard-removal mutant (§4 below) shows that
mutant's stderr contains no "Traceback" substring at all (it's bash runtime noise, not a Python
exception) — so the same weak pattern that is census item 4 is confirmed vacuous under that mutant by
direct reproduction, not by re-reading the claim. Method validated.

**Result: exactly the four known items, no more found in the two files swept.**

1. case12's four hostile values — confirmed still vacuous (files unchanged since `2117a46`, where I
   mutation-tested this directly last round; not re-run this round per the dispatch's citation
   instruction).
2. `test-check-expertise.py` case2's `FEAT-\d+` sub-case — confirmed structurally, this round, by
   reading `check-expertise.sh:45`: `FEATURE_TOKEN_RE = re.compile(r"\bFEAT-\d+\b|\bT-\d+\b|#\d+\b")`
   independently catches `FEAT-12` as a hard violation regardless of whether `REPO_TOKEN_RE`'s
   `FEAT-\d+` sub-pattern ever fires — checked that none of the other 9 token classes (`DEC-\d+`,
   `INV-\d+`, `.harness/`, `.claude/`, `check-*.sh`, `factory_*.py`, `gh-sync`, `harness.json`,
   `team-config`) overlaps `FEATURE_TOKEN_RE`'s pattern, so only the `FEAT-12` case is vacuous — a
   per-assertion finding, not a generalisation across the loop's 10 sub-cases.
3. `inject-expertise.sh`'s `[ -r ]` documented half (non-matching glob) — established last round,
   script byte-identical this round (confirmed).
4. case11's `"Traceback" not in stderr` — confirmed vacuous under the T-07 guard-removal mutant by
   direct reproduction this round (§ above), not by re-reading the claim.

**New-behaviour check on case13 itself (this round's own addition), per-assertion, not
generalised:** of case13's four plan-level assertions (exit 0 · header+body present · kaya absent ·
stderr empty), **only the last two discriminate** the guard-removal mutant; the first two are inert
under it (script has no `set -e`, so its trailing `exit 0` always fires; the harness-tier loop
iteration is untouched by removing the guard on the *kaya* iteration). Inert is not the same claim as
vacuous-in-general — assertions 1 and 2 are legitimate regression pins for other mutants (e.g. a
crash, or a mutant that broke the good entry's rendering); they are just not what reddens *this*
mutant. Reported per-assertion, not carried over from case12's fully-vacuous shape.

**Not swept this round**: the base `case()` list in `test-check-expertise.py` (pre-existing B-10, not
part of this feature) and every other test file in the tree — bounded per the dispatch.

## 5. T-07's specific question: what does case13 actually pin?

Reproduced the eng squad's claim myself on a scratchpad copy (`Write`-tool copy of
`inject-expertise.sh`, confirmed byte-identical to the real file by `diff` before mutating; mutant
built by removing exactly the line `[ -r "$f" ] || continue`, confirmed by `diff` — one line, no
more).

- Unmutated, `INJECT_EXPERTISE_BIN=<scratchpad orig>`: **19/19**, all PASS.
- Mutated, `INJECT_EXPERTISE_BIN=<scratchpad mutant>`: **18/19**, case13 the sole FAIL.
  `checks=[True, True, True, False, False]` — the Python-level `checks[3]` (`"kaya" not in ctx`)
  and `checks[4]` (`stderr == ""`) flip; `checks[0..2]` (exit 0, repo header present, repo body
  present) do not. Full `ctx` under the mutant literally contains a phantom
  `## Your Expertise — kaya repository (repository tier)` header with an empty body, and `stderr`
  carries two `head: ... No such file or directory` lines plus one `[: : integer expected` bash
  arithmetic error — no "Traceback" substring anywhere.

**Confirms the eng squad's claim exactly** (18/19, two assertions flip: the kaya header and
stderr-empty) — I did not repeat it, I reproduced it.

**Does case13 pin the guard's UNSPECIFIED duty (exists-and-unreadable) rather than the documented
half (non-matching glob)?** Yes. The fixture's `.harness/kaya/expertise/harness-qa.md` is a real
dangling symlink — bash's glob **matches** it by name (it exists as a directory entry), so this is
not the non-matching-glob case the segment filter at `inject-expertise.sh:75-77` already covers
independently. `[ -r ]` here is doing the only guarding: following the symlink to a target that does
not exist, which `-r` correctly reports false for.

**Which of case13's four assertions discriminate, which are inert:** only "kaya absent from ctx" and
"stderr empty" discriminate this mutant. "exit 0" and "header+body present" are inert under it (see
§4) — not useless in general, just not the reason this specific mutant reddens.

**Is `stderr == ""` (not "no Traceback") the strength that does the work?** Yes, directly confirmed:
the mutant's stderr contains zero occurrences of "Traceback" (it is bash-native error output, not an
uncaught Python exception), so a `"Traceback" not in stderr` form — the same weak shape as census
item 4 — would have stayed green under exactly the mutant SC-11 requires case13 to catch. The exact
`stderr == ""` comparison is load-bearing, not stylistic.

## Coverage gaps (net across both rounds)

- SC-02 / T-01's 10 non-fixtured repository-tier grants: automated and passing, but living only in a
  one-shot task `verify:`, not in the standing `run-unit-tests.sh` suite — a future regression on any
  of the 16 grants (or the 10 not covered by `COLLECT_FIXTURE`) will not be caught automatically.
- `[ -r ]` guard's *documented* half (non-matching glob) — still unpinned as its own case (carried
  from the T-02/T-03 round; T-07 pinned the *other* half, deliberately, per its own intent text).
- 1c's suffix-hygiene regex (`case12`) — still zero discriminating coverage (carried, unchanged).
- `test-check-expertise.py` case2's `FEAT-\d+` sub-case — still vacuous, one of ten, not fixed
  (test-authoring change, outside this gate's remit).

None of these gate this segment: SC-11 (T-07's own SC) is fully met, and the two carried gaps sit
outside every currently-defined SC's text, same ruling as the prior round.

## Boundaries observed

No source or test file was written or edited. All mutation probes ran on scratchpad copies at
`/private/tmp/claude-501/.../scratchpad/probes2/`, built via the `Write` tool (the `bash-write-guard`
denies `cp`/redirect into scratchpad from Bash — logged as an observation). Nothing committed or
staged. `check-expertise.sh` was run read-only over both tiers as part of re-running T-04's `verify:`
— the six craft `ADVISORY` lines it prints are D-03's adjudicated-craft entries working as designed,
not a violation.

---

# Cycle 2 — could-not-fail census re-derived

**Cycle 1's `matrix_ok: true` and its SC-01..SC-11 read stand, are not redone.** Cycle 1's "exactly
the four known items" claim on the census does not stand — this round finds two more items **inside
the same file cycle 1 declared swept**, both confirmed at source with one-line-diffed mutants on
scratchpad copies (`cp`-then-diffed against the real files first, per rule). One prior item (item 4)
is refuted as could-not-fail on remeasurement against its own intended mutant, and a narrower, real
gap sits beside it.

## N-1 — CONFIRMED. Global tier reachable by no case in the suite.

`fresh_home()` (`test-inject-expertise.py:57-58`) returns an empty tempdir; grepped the whole file for
any `write(os.path.join(home` — zero hits. So `inject-expertise.sh:98-101`'s glob-tier branch
(header, `cap_body "$glob" 150`) is dead code as far as this suite is concerned.

**Measured:** mutated `:100`'s budget `150 → 77` (one line, diffed clean against the real file
first). Full suite: **19/19**, unaffected. Confirmed unpinned.

This is `T-02`'s own new call site (three `cap_body` sites total: `:100` unpinned, `:104` pinned by
case8, `:115` pinned by case7a) — a gap in a task this feature itself added, not inherited debt.

**Category: (b) — shipped code no assertion reaches.** No existing assertion can be pointed at; the
remedy is a new case writing under `home`, not a stronger existing check.

## N-2 — CONFIRMED. case2's ordering assertion (`:123`) cannot fail against removal of the manual sort.

`inject-expertise.sh:82-92`'s explicit re-sort is provably redundant for case2's fixture: bash glob
expansion already returns `.harness/*/expertise/harness-qa.md` matches in collation order — verified
directly (not inferred) by globbing a scratch `kaya`+`harness` pair, independent of the hook: glob
returned `harness` before `kaya` with no sort involved.

**Measured:** built a mutant with `:82-92` replaced by unsorted natural-insertion indices (diff
confined to exactly that block, confirmed). Full suite: **19/19**, case2 included. Confirmed the
~10-line sort is pinned by nothing — case2 cannot distinguish "sorted" from "naturally already in
order because bash's glob happens to collate this way for two ASCII names."

**Category: (a) — an assertion that cannot redden.** case2's ordering checks (`:123`) exist and run,
but the fixture (two segments already in alphabetical glob order) can never exercise the sort's actual
job. The remedy is a stronger fixture — segment names that are *not* already in glob/collation order
relative to each other for the platforms this runs on (or an explicit non-alphabetic ordering probe) —
not a new case.

## N-3 — CONFIRMED, narrow. case9a's ordering clause degenerates vacuously when headers are absent; the rest of the suite still catches header removal.

`test-inject-expertise.py:225-233`: `header_positions` is a filtered comprehension
(`if ctx.find(h) != -1`); `order_ok = index_idx != -1 and all(index_idx > p for p in
header_positions)`. `all()` over `[]` is `True`.

**Measured:** mutant replacing all three header `printf`s (`:99`, `:103`, `:114`) with `true` (diff
confined to exactly those three lines). Full suite: **13/19**. case1, case2, case3, case10, case11,
case13 all correctly redden on header *absence* (each asserts header presence directly). **case9a
stays green** — its two checks (`index_hdr in ctx`, `INDEX BODY TEXT in ctx`) don't touch header
presence at all, and its ordering clause goes vacuously true.

**Category: (a) — an assertion that cannot redden**, scoped precisely: case9a's *ordering clause
specifically*, not case9a as a whole (its other two checks are fine) and not the suite as a whole
(headers-absent is already caught elsewhere). The remedy is narrow: case9a's ordering check should
assert header presence as a precondition of the ordering claim, or read `checks=[True,True]` plus
`order_ok` separately in the report the way it already prints `order_ok` — the data is there, the
gate on it is just permissive.

## N-4 — CONFIRMED. case5's stderr assertions are immune to either single-line mutation alone; this is defense-in-depth, not a pin on either line.

Two independent one-line mutants, each diffed clean against the real file before running:

- Removed `try:`/`except Exception: print("")` only (`:15-18` → bare `print(json.load(...))`),
  `2>/dev/null` left in place at `:19`. Full suite: **19/19**. case5a/case5b green.
- Removed only `2>/dev/null` at `:19`, try/except left in place. Full suite: **19/19**. case5a/case5b
  green.

Neither single mutation reddens case5's stderr checks. This matches your cycle-1-round-1 finding that
removing *both* together reddened case5b — consistent, and now isolated to show it takes both. **Which
one:** it is genuinely both-must-fail, not asymmetric — under try/except-only-removed, the exception is
caught by the shell's own `2>/dev/null` before it reaches Python's stdout; under redirect-only-removed,
try/except catches the exception in Python before anything reaches stderr. Two independent guards, each
sufficient alone in its own failure mode, so removing either one leaves the other standing.

**Category: not a could-not-fail item.** It is real defense-in-depth — each single line is
individually redundant *given the other*, but no test exists that isolates one from the other, so
neither line is individually "pinned" as its own unit. This does not belong in the census as
currently scoped (the census as briefed is about assertions/code that cannot fail at all); flagging it
here as a **finding**, not a census entry: if a future refactor drops one guard, this suite gives no
signal until the second is also gone.

## Census item 4 re-examined, per your instruction — REFUTED as could-not-fail; a narrower real gap replaces it

**Measured against case11's own stated intent** (a tripwire for a successor adding a YAML parse
dependency, `plan.yaml:327-332`): added an unsuppressed
`python3 -c 'import yaml,sys; yaml.safe_load(open(sys.argv[1]))' "$root/.harness/team-config.yaml"`
right after `root=` is set (one line, diffed clean). Ran case11 on the real fixture (its
deliberately-broken `team-config.yaml`).

**Result: case11 REDDENS.** `checks=[True, True, True, True, True, False]` —
`"Traceback" not in stderr` flips. Actual stderr:
`Traceback (most recent call last): ... ModuleNotFoundError: No module named 'yaml'` (case11's `HOME`
is neutralized to a fresh tempdir per the suite's own design, `:13-17` of the test file's docstring,
so the real machine's user-site `yaml` package isn't on `sys.path` in that subprocess — a second,
accidental way this exact mutant fires, on top of the YAML content being unparseable). Either way: an
uncaught Python exception, a real traceback, case11 catches it.

**Your objection to the cycle-1 inference is correct and now measured, not just argued: item 4 is not
a could-not-fail assertion.** It is vacuous only under the *unrelated* T-07 guard-removal mutant
(bash-native stderr, no Python invoked on that path) — staying green there is not vacuity, exactly as
you say. **Item 4 is REMOVED from the census entirely** — it belongs in neither category (a) nor (b);
it is a working assertion.

**The narrower weakness is real and independently confirmed.** Built a second mutant: a *shell*-based
stand-in for a successor reading YAML without Python (`grep`+`cat` producing
`cat: .../nonexistent-shell-error-trigger.yaml: No such file or directory` on stderr, no `2>`
suppression). Ran case11: **stays green** — `"Traceback" not in stderr` is true, because the string
literally isn't a traceback. This is a real, live gap: `"Traceback" not in stderr` catches a
Python-based successor, misses a shell-based one; `stderr == ""` would catch both. **Confirmed, both
parts** — the eng squad's proposed remedy (`stderr == ""`) is right, but for the reason you named
(shell-parsers don't traceback), not the reason item 4 was originally filed under (case11 supposedly
never reddens at all — it does, for Python).

## `stderr == ""` claim, restated to what was actually measured

Cycle 1 wrote: `stderr == ""` "is load-bearing, not stylistic" and a weaker form "would have stayed
green under exactly the mutant SC-11 requires case13 to catch." **That overstates what the
measurement showed.** The measurement (§5, cycle 1) is `checks=[True, True, True, False, False]` —
`checks[3]` (`"kaya" not in ctx`) *and* `checks[4]` (`stderr == ""`) both flip. Since `checks[3]`
alone flips `all(checks)` to `False`, **case13 fails this specific mutant with or without the stderr
check** — `stderr == ""` is redundant *for this mutant*, not load-bearing for it.

**Precise version:** `stderr == ""` is not required to catch the T-07 guard-removal mutant (`checks[3]`
already does). It earns its place for a *different, real* class: any mutant that produces stderr noise
(shell errors, warnings, non-fatal noise) **without** also leaking a phantom kaya header — e.g. a
future change that adds a diagnostic `echo` to the guard path, or a partial fix that silences the leak
but leaves noisy `[: integer expected`-style output behind. Against *that* class, `stderr == ""` is the
only clause in case13 that would catch it, and `"Traceback" not in stderr` would not (same class of
gap as item 4/case11, above — non-Python stderr noise). So: real value, wrong justification. The
correction: `stderr == ""` in case13 guards a **different, unexercised** failure mode than the one
cited, not the T-07 mutant itself.

## Corrected census — final

Six items total, split by category as requested. "Four" was **not** right: the method that produced
"four, no more found" missed two items inside the one file it declared thoroughly swept (N-1, N-2), and
one of the original four (item 4 / case11-Traceback) does not belong in the census at all — it
reddens under its own intended mutant. Net: 4 (original) − 1 (item 4, refuted) + 2 (N-1, N-2) + 1
(N-3, narrower/scoped) = **6** confirmed could-not-fail items, plus one finding (N-4) that is
defense-in-depth, not miscoverage, and does not belong in the census as scoped.

**(a) an assertion that exists and runs, but cannot redden against the failure it claims to guard:**
1. case12's four hostile `agent_type` values — vacuous (carried from prior rounds, mutation-tested
   directly at `2117a46`, unchanged since).
2. `test-check-expertise.py` case2's `FEAT-\d+` sub-case — vacuous; `FEATURE_TOKEN_RE` independently
   catches the violation regardless of `REPO_TOKEN_RE`'s overlapping sub-pattern (`check-expertise.sh:45`).
3. case2's segment-ordering assertion (`test-inject-expertise.py:123`) — **new this round (N-2)**:
   cannot fail against removal of `inject-expertise.sh:82-92`'s manual sort, because the fixture's two
   segment names are already in bash glob/collation order.
4. case9a's ordering clause (`test-inject-expertise.py:233`) — **new this round (N-3)**: degenerates
   vacuously (`all()` over `[]`) when all three Expertise headers are absent; scoped to the ordering
   clause only — case9a's other two checks, and five other cases in the suite, do catch header
   removal.

**(b) shipped code that no assertion reaches at all:**
5. `inject-expertise.sh:98-101`'s `[ -r ]`-guarded documented half (non-matching glob) — carried,
   unchanged since prior rounds.
6. `inject-expertise.sh:98-101`'s glob-tier branch as a whole (header text, `cap_body "$glob" 150`) —
   **new this round (N-1)**: unreachable because no test ever writes under `home`.

**Removed from the census:** case11's `"Traceback" not in stderr` (former item 4) — refuted; it
reddens under a Python-based YAML-parse mutant matching its own stated intent. Replaced in spirit by
a narrower, confirmed finding: the same assertion misses a *shell*-based equivalent, which
`stderr == ""` would catch.

**Finding, not a census entry:** case5's stderr checks (`:162-163`) are immune to either single-line
guard removal alone (try/except, or `2>/dev/null`) but do catch both removed together — genuine
defense-in-depth, flagged so a future single-guard regression isn't assumed caught.

## Method note

Cycle 1's sweep of `test-inject-expertise.py` read every case's assertions but did not, for each
assertion, ask "what is the smallest single-line mutation this specific clause cannot see" before
moving to the next case — N-1 and N-2 both required tracing a data source (an unwritten `home` var; a
fixture whose two names happen to already collate correctly) back through the script, not just
reading the assertion text. That is the gap in method, not a missed grep.
