# Code Review — FEAT-41-one-station-vocabulary — cycle 2 (re-review at re-pin)

Reviewed `7c4f0bd..39477a502cd6726f01ad403dbdb4222c26969d2e` inside the worktree, confirmed by
`pwd`/`git rev-parse --show-toplevel`. HEAD (`9a9f5ce`) is one commit past the pin
(`re-pin review_sha`, touches only `feature.json`) — no source difference, so all `grep`/`sed`
line-number citations below were read from the live working tree and are valid at review_sha
(spot-checked several against `git show <sha>:<path>` during the diff walk).

**BOTH STAGES RAN, UNCONDITIONALLY, IN ORDER.** Stage 1 (spec compliance) completed in full
before Stage 2 began; Stage 2 (code quality, explicit file set + fail-open + mutation hunt) is
independent of Stage 1's outcome, per this cycle's dispatch.

**VERDICT: FAIL.** Two HIGH findings, both newly surfaced this cycle by diffing the full range
rather than trusting the handoff's framing: **NEW-1** (BUG-1030's non-terminal station was
silently destroyed, inconsistent with BUG-1071/#1079's deliberate preservation) and the
**re-confirmed carried security finding** (station-verb identity binding, reproduced live). All
four of cycle 1's findings are genuinely CLOSED and mutation-proven, including two by mutations I
built myself. Two of cycle 1's MEDs get a partial-closure correction (`_I` patterns) and a
process-gap note (`_t09_case_fold`'s missing reason).

---

## Cycle 1 closures — CLOSED/OPEN, anchor, mutation result

### H-01 (high) — check-domain.sh symlink route — **CLOSED, mutation-proven independently**

Anchor: `check-domain.sh:1487` (`_MAX_HOPS = 8`), `:1490` (`_route_candidates`), `:1508`
(`_plan_route`), `:1516` (`_reached_plan = ...`), PRE denial at `:1517`, POST at `:1570`
(`_rel = next((c for c in _route_candidates(target) if has_shape_rules(c)), _norm(target))`).

I built my own mutated copy of check-domain.sh reverting exactly the H-01 diff (both the PRE
condition and the POST `_rel` line), pointed at the real bin dir for its sibling imports, and ran
it against a from-scratch `$TMPDIR` fixture (not `test-check-domain.py`, per the suite-ownership
constraint):
- **PRE**, symlink `notes/innocent.md -> ../plan.yaml`: real hook exit 2, DENIED, message names
  the resolved plan path; my mutant (H-01 reverted): exit 0, ALLOWED. Negative control (symlink
  to an ordinary file): both real and mutant correctly ALLOW — the mutation does not become a
  deny-everything guard.
- **POST**, illegal station (`Sideways`) landed through the same link: real hook exit 2, names
  `Sideways`; mutant: exit 0, silent. Both checkpoints discriminate on this mutation.

**(a) Is the fix additive?** Yes, by construction, not just by argument. `_route_candidates`
always includes `_norm(path)` as its first candidate — byte-identical to the old single check —
so nothing previously DENIED can become ALLOWED. For the converse (a legitimate write wrongly
newly denied): a non-symlink path makes `os.path.islink(cur)` false on the first iteration, so
`_route_candidates` returns exactly `[_norm(path)]`, identical to pre-fix behaviour — I confirmed
this holds through 3-hop and 8-hop symlink chains resolving to an *ordinary* file, both correctly
ALLOWED on both the real hook and negative-control fixtures. No false denial found on any
legitimate route.

**(b) Is readlink-walking (not realpath) correct?** Verified by construction, not accepted from
the commit. This workstation is darwin and `/var` is genuinely a symlink to `/private/var`
(`os.path.islink('/var') == True`), and `tempfile.mkdtemp()` (used by every fixture, including
production `$TMPDIR`-rooted checkouts) lands under `/var/folders/...`. I built a second mutant
substituting `os.path.realpath` for the readlink walk and ran it against the identical
symlink-to-plan.yaml fixture: **it returned exit 0 (ALLOWED) — the case stays RED with a realpath
fix in place**, exactly as the commit claims, because `CLAUDE_PROJECT_DIR` carries the `/var/...`
spelling while `realpath()` returns `/private/var/...`, and `_norm`'s `os.path.relpath` against
two different root spellings produces a path that matches no `SHAPE_PATTERNS` entry. Converse
(does readlink-walk miss anything realpath would catch): readlink-walking only resolves the
*final path component* being a symlink (`os.path.islink(cur)` on the whole joined path); it does
**not** walk symlinked ancestor directories. This is the "symlinked parent dir" sub-question the
dispatch assigns to security; I did not duplicate that probe.

**(c) The hop cap: what happens at it, and is a legitimate deep chain refused?** `_MAX_HOPS = 8`.
I built chains of 3, 8, and 9 hops. A 3-hop and an exactly-8-hop chain resolving to plan.yaml are
both correctly DENIED (cap covers 8 hops fully); a 3-hop chain resolving to an ordinary file is
correctly ALLOWED (no false denial for a legitimate deep-but-finite chain within the cap). **A
9-hop chain resolving to plan.yaml is ALLOWED — exit 0, no stderr — the cap fails OPEN, silently,
beyond 8 hops.** A self-referential 2-link loop terminates cleanly (exit 0, no hang) — the cap
does its job against a loop. **No test anywhere exercises the hop-cap boundary or a symlink
loop** — I grepped `test-check-domain.py` for `_MAX_HOPS`, `MAX_HOPS`, `hop`, and `symlink loop`:
zero hits; the only `os.symlink` call sites are `_t09_symlink`'s four single-hop cases. The
cap's behaviour is pinned by code only, not by any test.

- **Finding H-01-a (low, non-blocking):** the >8-hop fail-open is real but requires an attacker
  to already have write access to construct an 8+ level symlink chain under `.harness/` before
  any of these gates would matter — a materially harder precondition than the single-symlink
  case H-01 closes. `check-domain.sh:1487-1506`. BLOCKS: no.
- **Finding H-01-b (med, non-blocking):** the hop-cap boundary (8 exactly, 9 exceeds) and the
  loop-termination guarantee are both unpinned by any test — a future edit to `_MAX_HOPS` (e.g.
  a well-meaning "raise the cap" or "lower it for performance") would not redden anything.
  `test-check-domain.py:2684-2780` (`_t09_symlink`). BLOCKS: no.

### H-02 (high) — plan-sign-gate.py line continuation — **CLOSED, probed independently**

Anchor: `plan-sign-gate.py:116` (`CONTINUATION`), `:119` (`as_bash_reads_it`), `:130`
(`denies`, calls it on line 1 unconditionally, including recursively at every `depth`).

**Layering judgement:** adopting bash's view *before* lexing, once, ahead of both the token
scanner and the raw-text fallback, is the right call — not a second parser that can drift from
bash, but a narrow, single-purpose normalisation (strip exactly `\<newline>` / `\<CRLF>`) applied
uniformly before either scanner runs. Because `as_bash_reads_it` sits at the top of `denies` and
`denies` recurses on itself (`eval`/`bash -c` sub-commands), the rejoin also applies at every
recursion depth — no depth-dependent asymmetry.

**Adjacency probe, against a fake `plan-merge.py` in `$TMPDIR` and REAL `bash -c`, comparing the
production gate's verdict to what bash actually executes** (12 cases; full transcript in
`/tmp/feat41review/h02_probe.py` + `h02_probe2.py`, not committed):

| construct | gate | real bash reaches `sign-approval` as argv | note |
|---|---|---|---|
| `\<LF>` continuation | DENIED (2) | yes | the fixed case |
| `\<LF>` inside an `apply` call | ALLOWED (0) | no | negative control holds |
| `\<CRLF>` continuation | **DENIED (2)** | **no** (bash treats `\r` literal, `\n` as a real separator; real bash gets `command not found`) | **over-denial, see below** |
| `\<TAB><LF>` continuation (tab *before* the `\`) | DENIED (2) | yes | correct |
| `\<TAB>` then LF (tab *inside* the escape) | ALLOWED (0) | no | correctly not a continuation |
| double `\<LF>\<LF>` | DENIED (2) | yes | correct |
| `$IFS`-word-splitting | ALLOWED (0) | **yes, reaches** | **disclosed, pre-existing gap** — the module's own docstring: "a binary produced only by shell expansion... is invisible here... NOT a security boundary" |
| quoted newline inside a single-quoted `--note` | ALLOWED (0) | no | correct, no false positive |
| `;` inside a double-quoted string | ALLOWED (0) | no | correct |
| `\<LF>` literally preserved inside single quotes | ALLOWED (0) | no (bash itself preserves it) | correct, the blind regex substitution is inert inside quotes since it never crosses a quote boundary |
| `$(command substitution)` | ALLOWED (0) | **yes, reaches** | **disclosed, pre-existing gap**, same class as `$IFS` |
| bash variable holding the verb | ALLOWED (0) | **yes, reaches** | **disclosed, pre-existing gap**, this is the module's own `$P` example |

**Finding H-02-a (low, non-blocking):** `CONTINUATION = re.compile(r"\\\r?\n")` treats
`\<CR><LF>` as equivalent to bash's `\<LF>` continuation; real bash does not (a bare `\r` is a
literal character, and the following `\n` is a genuine command separator). I confirmed this
produces one over-denial: `plan-merge.py \<CR><LF>sign-approval` is DENIED by the gate but would
actually fail with "sign-approval: command not found" in real bash — never a real signing
attempt. I also confirmed the safe direction holds: the identical construct wrapping a legitimate
`apply` call (`plan-merge.py \<CR><LF>apply --file x --proposal y`) is **ALLOWED** by the gate
(the substitution is applied uniformly, so `apply` still lands adjacent to the tool after the
strip) — no false denial of a working command was found; only a command that would already fail
in real bash gets mis-labelled. `plan-sign-gate.py:116`. BLOCKS: no.

The three "disclosed gaps" rows are not new — they match the module's own docstring exactly
("What survives this gate, stated rather than implied... a PreToolUse hook is never given [the
shell's expansion]"). Reported per the dispatch's request to independently verify each
construct's reach, not as a new finding.

### MED — `_I` case-fold patterns — **PARTIALLY OPEN, not fully closed as claimed**

Anchor: `check-domain.sh:1037` (`RE_STATE_YAML`), `:1045` (`RE_CLAUDE_MD`), `:1046`
(`RE_STATE_MD`), `:1038` (`RE_FEATURE_JSON`), `:1083` (`SHAPE_PATTERNS`, six patterns total, all
`_I`); `test-check-domain.py:2782` (`_t09_case_fold`, `_FOLD_ROWS` at `:2773`).

**Dispatch-required re-run, on a DIFFERENT pattern than QA's (`RE_FEATURE_JSON`):** I mutated
`RE_STATE_MD` to drop `_I`, and independently confirmed via a hand-built `$TMPDIR` fixture driving
the real hook: canonical `STATE.md` over budget denies on both real and mutant; folded `State.md`
over budget denies on the real hook, **ALLOWS on the mutant (exit 0)** — exactly one row reds.
The independence check (folded `Feature.json`, a *different* pattern, over budget) still denies
on **both** real and mutant — confirming the mutation is scoped to the one pattern, not several.

**But `_FOLD_ROWS` only covers three of the five remaining patterns** — `RE_FEATURE_JSON`,
`RE_HANDOFF`, `RE_STATE_MD` — leaving **`RE_STATE_YAML` and `RE_CLAUDE_MD` completely untested**
for case-fold behaviour, the identical shape of the original cycle-1 finding. I confirmed via
`grep` that neither `test-check-domain.py` nor any other test file mentions a folded spelling
("Claude.md", "State.yaml") anywhere — zero hits — and then independently built mutants
dropping `_I` from each: **`RE_CLAUDE_MD` mutant: folded `Claude.md` over the 80-line budget goes
from DENIED (real) to ALLOWED, exit 0, no stderr (mutant). `RE_STATE_YAML` mutant: folded
`State.yaml` carrying an illegal key goes from DENIED-naming-the-key (real) to ALLOWED, exit 0
(mutant).** Both are exactly as "inert" today as `RE_FEATURE_JSON` was before this cycle's fix —
the closure commit's framing ("table-driven, one row per pattern") is not accurate; it closed 3
of 5, not 5 of 5.

**Finding MED-1 (med, non-blocking on its own, but the cycle-1 MED is not fully discharged):**
`check-domain.sh:1037,1045` — `RE_STATE_YAML` and `RE_CLAUDE_MD`'s `_I` flags remain
unreachable-by-test dead coverage, confirmed by mutation (both silently sail through when
disabled). CLAUDE.md is the file preloaded into every session, and its own comment block
(`check-domain.sh:1394-1420`) singles it out as "the widest blast radius in the repo" — the case
for closing this gap is stronger for `RE_CLAUDE_MD` than for the three patterns that did get
closed. BLOCKS: no (matches cycle 1's own med, non-blocking), but I do not concur this cycle-1
item should read as fully CLOSED; it is **OPEN, 3/5 closed**.

### MED — `_verify_signature` reachability — **CLOSED, and the forcing case is honest**

Anchor: `plan-merge.py:271` (`_verify_signature`), `:833` (`cmd_sign_approval.transform`, calls
it at `:864`); `test-plan-merge.py:745`
(`case_f02_verify_signature_is_not_dead_code`... — actually the added case at line 839 in the
diff is named `case_f02_verify_signature_is_not_dead_code`; the code-grade record at line 745 is
a *different*, pre-existing gated function, see the code_grade section below).

I built three variants of `plan-merge.py` and ran all three against the exact forcing fixture
(duplicate `approved_by: null` / `approved_by: stale-signer`), via my own driver, not
`test-plan-merge.py`:

| variant | exit | plan written? | stderr names both values |
|---|---|---|---|
| REAL (fixed) | 5 | no (unchanged) | yes — "asked for: 'Mike Ruangutai'", "reloads as: 'stale-signer'" |
| MUTANT: `_verify_signature` disabled (early `return`, QA's original mutation) | 0 | **yes** — writes a plan whose first `approved_by` line reads "Mike Ruangutai" but whose SECOND, un-deduplicated `approved_by` line still reads "stale-signer" | n/a |
| STUB: `_verify_signature` unconditionally refuses with a generic, non-dynamic message | 5 | no | **no** — missing both dynamic values |

This independently reproduces the "0 → 3 failures" claim (my three checks map onto the commit's
three `check()` calls) and **directly answers the dispatch's honesty question**: a naive
always-refuse stub does NOT pass this case, because it lacks the dynamically-computed `want`/
`got` values the real comparison loop produces — the case discriminates against both the
fail-open direction (the original gap) and a naive fail-closed stand-in.

**One residual worth naming, not gating:** the ONLY way I could find to reach
`_verify_signature`'s comparison loop — in this fixture, in QA's mutation, and by re-reading
`cmd_sign_approval.transform:833-863` — is a **pre-existing duplicate key** in the base plan's
approval block, which the splice loop (line ~855, "if m and m.group(2) not in written") only
replaces on its *first* occurrence and blindly copies through any later duplicate. No test
anywhere reaches this comparison loop via a *hostile signer value* (colon, newline, etc.) — those
are all caught one layer earlier by `_field_lines` (confirmed independently in cycle 1's own
review). If `_field_lines`'s escaping were ever weakened for one value class in the future, this
new test would not catch it; it only pins the duplicate-key path. Non-blocking — `_field_lines`
already has its own dedicated hostile-value tests (cycle 1, item 2).

---

## Stage 1 — spec compliance

REQ-01..REQ-07 and D-01..D-16 read against the diff and against `plan.yaml`. All 12
main-session-direct tasks plus T-15's documentor lane match DEC-174's carve-out as the BRIEF
states it. D-01 (T-13 struck, plan-merge.py keeps its name), D-15 (T-15 lane ratified,
operator-worded, not self-amended), D-16 (T-18 struck, INV-33 renumber, FEAT-45 precedence
verified at source) are each honoured exactly as their own text states — no drift found.

**SC-01..SC-14:** consistent with QA's independently-re-run cycle-2 survey
(`notes/qa-FEAT-41-c2.md:§9`), which I spot-checked rather than re-derived wholesale (SC-11's
serial-run guarantee and SC-10's `test-gh-sync.py` standalone run are QA's exclusive lane per the
suite-serialization constraint). SC-05/SC-12 confirmed **struck and recorded, not deleted**, in
`BRIEF.md` — the text is present, marked "STRUCK on 2026-08-30 with T-13", matching PRINCIPLES
rule 15.

### The BUG-1055 migration — argument sound, but its own file citation is missing

**Ruling: the argument is sound** (a shipped feature's terminal fact is carried by the merge and
the closed PR, so a redundant `status` key on a *terminal* record is correctly deletable, matching
T-07's own precedent for FEAT-01 and nine siblings), **but no task's `files:` list authorises
touching `BUG-1055-code-grade-absent-path/feature.json`** — I grepped `plan.yaml` for `BUG-1055`
and `BUG-1071`: zero hits in any task's `files:`. This is the same shape as cycle-0's F5
(9 untraced files, accepted non-blocking) and as T-07's *original* batch of nine migrations,
which cycle-1's own reviewer already found unattributable-from-the-diff-alone and declined to
escalate. **Was writing another feature's records this feature's business?** Yes, on the
strength of T-07's own standing verify assertion
(`plan.yaml:840`, `grep -l '"status"' .harness/harness/features/*/feature.json ; test $? -eq 1`)
— that line is a tree-wide invariant this feature committed to holding at every review_sha, not a
one-time migration, so a violator surfacing via rebase is squarely within the task that owns the
invariant, even though the specific path was never individually listed. Consistent disposition
with cycle-0/1: **non-blocking, same traceability-gap class, not new.**

### SC-08 / BUG-1071 / issue #1079 — literal FAIL confirmed, re-derived survey holds — but the survey has a real gap

**SC-08's literal text is FALSE, as written, at this pin** — recorded separately from any
reading under which it is acceptable, per the dispatch: `BUG-1071-inv32-era-guard/feature.json`
carries `"status": "Review"` and no `plan.yaml` exists to hold that fact instead.

**Re-derived independently** (not accepted from the handoff or from QA's note):
```
total feature dirs:                 48
dirs WITH plan.yaml:                35   (0 carry status — verified directly, not inferred)
dirs WITHOUT plan.yaml:              13, of which:
  1 has no feature.json at all      (PR-922-omp-supervision — review notes only, not a
                                      "feature" in SC-08's sense, correctly outside its scope)
  1 carries status="Review"          (BUG-1071 — the sole disclosed, filed exception, #1079)
  11 carry no status                 (9 × FEAT-01..09, all frozen "Done" before deletion,
                                       terminal — plus BUG-1055, migrated this cycle, terminal —
                                       plus BUG-1030, see below)
```
This matches the "35 / 10-plus-1 / BUG-1071-alone" shape once `BUG-1055` (this cycle's addition)
and `PR-922` (not a feature.json holder) are correctly excluded — **the counts hold.**

**But the survey's premise — "BUG-1071 is the sole exception" — is not accurate, and I did not
accept it as given.**

### NEW-1 (high, must_fix) — BUG-1030's non-terminal station was destroyed, not preserved

`git diff 7c4f0bd..39477a502cd6726f01ad403dbdb4222c26969d2e -- .harness/harness/features/BUG-1030-stale-anchor-write-hazard/feature.json`
shows `"status": "Review"` deleted in commit `a8a8944` (T-07's *original* migration, in scope for
this pin), with no replacement anywhere: `BUG-1030-stale-anchor-write-hazard` is plan-less (no
`plan.yaml`), so after this deletion **no file in the repository records its station.**

`BUG-1030` is structurally identical to `BUG-1071` — plan-less, and its `status` was a
**non-terminal** vocabulary word (`Review`, not `Done`/`abandoned`) — but unlike `BUG-1071`, it
was silently swept into the same batch as the nine genuinely-terminal `FEAT-01..09` directories
(all of which I independently confirmed carried `"status": "Done"` before deletion — a clean,
uniform, terminal signal that BUG-1030 does not share). No GitHub issue was filed for it (unlike
`BUG-1071`/#1079), no `D-NN` records it, and it is absent from every review artifact I could find
(`grep -rn "BUG-1030"` across all of FEAT-41's `notes/` returns exactly one hit, in QA's own
cycle-2 survey, which lists it among the "carry none" group without flagging that its *prior*
value was non-terminal). `BUG-1030`'s current `feature.json` (`runs`: BLOCKED then FAIL,
2026-08-30, `pr: null`, no `github` field, 8 of 10 cycles unused) shows no evidence it was ever
formally judged abandoned — it reads as stalled, not closed.

**Failure scenario:** an operator or agent trying to determine whether `BUG-1030` still needs
attention has zero signal — not "Review" (destroyed), not a plan.yaml station (never existed),
not a closed-issue/PR marker (`pr: null`). This is exactly the failure mode SC-08's own carve-out
for `BUG-1071` exists to prevent, applied inconsistently to a sibling directory the migration
never individually examined. `REQ-06` ("a feature's station is recorded in exactly one file") is
now violated in the strict sense for this one feature: it is recorded in *zero* files. Anchor:
`.harness/harness/features/BUG-1030-stale-anchor-write-hazard/feature.json`, commit `a8a8944`.
**BLOCKS: yes** — recommend either filing an issue for `BUG-1030` matching `#1079`'s treatment
(if it is genuinely still open) or an operator determination that it was already abandoned,
recorded the same way `#1079` was.

I did not find a third instance of this pattern among the other ten plan-less dirs — all nine
`FEAT-01..09` carried `Done` uniformly (re-verified by diff, not assumed).

### Cycle-0 F-09 / F5 traceability gap — re-checked, narrowed but not closed, and one new instance

Re-running the sweep this cycle's diff touches: `check-domain.sh`, `plan-sign-gate.py`, and both
their test files are all named in T-09's and T-08's `files:` lists (`plan.yaml:1051-1053`,
`:979-982`) — **no scope creep on the H-01/H-02 fix commits.** The BUG-1055 feature.json edit and
the newly-discovered BUG-1030 deletion (from `a8a8944`, in scope for this pin) are **not** named
by any task — same class as cycle-0's original nine, **widened by one** (BUG-1030 was already
missing before, I am only newly flagging it; BUG-1055 is a genuinely new instance added this
cycle). Net: **persisted, not narrowed, not newly regressed by cycle-2's own fix commits.**

---

## Stage 2 — code quality

### plan-merge.py's VERBS table — still honest, unchanged this cycle

`plan-merge.py:894-925`. All five verbs (`apply`, `add-tasks`, `set-task-station`,
`set-feature-station`, `sign-approval`) register through the **one** loop at `:910-916`, which
calls `p.add_argument(flag, required=True, ...)` uniformly for every argument of every verb — no
per-verb override exists, so a verb silently gaining an optional argument would require editing
this shared loop, which would be visible in any diff touching it. Not touched by any of cycle-2's
fix commits. Per the Dead End ("do not add a `required` column"), a violation would be a finding,
not a redesign question — none found. `files:` for T-03 (which owns `plan-merge.py`) is
unaffected this cycle.

### `worktree_terminal.classify` — fail-safe on every input, one low-severity precision note

`worktree_terminal.py:289-350` (`_resolve_landed`) and `:353-392` (`_landed_station_record`).
Every ambiguous or unreadable path — unresolved worktree segment, unresolvable default branch,
unreadable landed-features listing, ambiguous id prefix, unreadable landed `feature.json`,
unreadable/unparseable landed `plan.yaml` — returns `klass: "unresolved"`, never `"terminal"`.
The **only** path to `"terminal"` is the single narrow condition at `:389`:
`if (station[0] if station else "") == "done":`. This correctly biases toward the safe direction
(never-reclaimed over wrongly-reclaimed) and the module's own extensive commentary states this
intent explicitly.

**Finding (low, non-blocking):** `:389`'s check is a *prefix* match on the first
whitespace-split token (`.split()`), not an exact match on the full value — `"done later"` would
satisfy `station[0] == "done"` even though the full field value is not `"done"`. Currently
unreachable: the sole writer (`plan-merge.py set-feature-station`) validates against the closed
six-word vocabulary before writing a bare scalar, and T-09 has closed the hand-edit route going
forward — this could only fire against a plan.yaml pre-dating T-09's enforcement. `BLOCKS: no`.

### `_record_station` / `_commit_terminal_station` asymmetry — still correct, held by a test not just a comment

`gh-sync.py:571-624` (`_record_station`, both failure branches print `gh-sync: FAILED —
...`) and `:649-696` (`_commit_terminal_station`, failure branches print `gh-sync: WARNING -
station committed nowhere` / `gh-sync: WARNING - station recorded but NOT committed`). Neither
file is touched by any cycle-2 commit — confirmed unchanged, and I independently re-read both
bodies rather than trusting cycle 1's transcription. **Is a later "consistency fix" guarded, or
only commented?** `test-gh-sync.py:3163-3168` (`T-10: with NO git repository the station commit
fails LOUDLY... "WARNING" in bothN`) and `:3186-3196` (both gate literals absent) pin the
*positive* presence of "WARNING" and the *absence* of "SKIP"/"FAILED" — someone "reconciling"
`_commit_terminal_station`'s wording to match `_record_station`'s "FAILED" would redden both
checks. Not merely comment-held. No exact-text pin exists for the two full sentences (only the
word "WARNING" and the two forbidden literals), which is a looser pin than it could be but is
sufficient to catch the specific regression named in the Dead End.

### INV-33 vs FEAT-45's INV-32 — no cross-match, unchanged from cycle 1

`check-state.sh:264` (`# INV-32 BEGIN (FEAT-45 T-07)`) through roughly `:390`, and `:488`
(`# INV-33: a pin that is STALE...`) through `:558` — disjoint, non-overlapping line ranges,
re-confirmed by grep at this pin. Not touched by cycle-2's fix commits (neither `check-state.sh`
nor `test-check-state.py` appear in `707b547`/`5dc5374`/`542e888`/`39477a5`'s diffs). No sign of
a shared fixture path or message collision. Cycle 1's finding stands, unchanged.

### `code_grade` — re-run myself against the new grader, at merge-base

```
python3 .claude/skills/harness/bin/code-grade.py --base 7c4f0bd \
  --head 39477a502cd6726f01ad403dbdb4222c26969d2e
```
Located the new location myself (`code-grade.py` now wraps a library module `code_grade.py`,
both under the same `bin/` directory — "moved upstream" is confirmed, not assumed). **Exit 0.
Zero `SEVERITY: high`. `code_grade: pass`** (no gated record blocks the build) **with 8 gated
grade-2 records, `code_grade: grade_2` for those 8, never `fail`:**

| function | file:line | reason |
|---|---|---|
| `_verify_spliced` | `plan-merge.py:313` | unchanged from cycle 0/1's accepted reasoning — one cohesive "does the splice reload as the merge we reported" invariant; splitting fragments it across files |
| `_task_status_line` | `plan-merge.py:678` | unchanged — must scope a task's own `status:` line against sibling tasks and nested `verify:` prose at arbitrary indent; the branching *is* the correctness requirement |
| `cmd_sign_approval.transform` | `plan-merge.py:833` | unchanged reasoning; the correctness gap this function once carried (F1/cycle-0) is independently closed (`_field_lines` + `_verify_signature`, both re-verified above) |
| `denies` | `plan-sign-gate.py:130` | unchanged reasoning (recursive shell-boundary walk, inherently branchy); line moved 103→112→130 as H-02 added one call to `as_bash_reads_it`, same function, same shape |
| `_t09_symlink` | `test-check-domain.py:2684` | reason supplied in commit `707b547`: straight-line fixture setup for H-01's four cases, ABC-driven by assertion-call count, splitting would manufacture helpers and scatter one route's evidence |
| `case_set_task_station_one_line` | `test-plan-merge.py:625` | unchanged from cycle 0/1 — test function, ABC driven by assertion-call count, not real complexity |
| `case_f02_sign_approval_cannot_write_an_unparseable_signature` | `test-plan-merge.py:745` | unchanged from cycle 1 — same class, test-loop ABC |
| **`_t09_case_fold`** | **`test-check-domain.py:2782`** | **no reason was ever supplied in commit `5dc5374`** (contrast with `_t09_symlink`'s explicit paragraph in the sibling commit `707b547`) — see finding below |

**Finding (med, non-blocking, process gap):** `_t09_case_fold` (`test-check-domain.py:2782`)
is a newly-gated grade-2 record with no accompanying written reason anywhere in its introducing
commit, unlike its sibling `_t09_symlink` in the immediately preceding commit. My own read of the
function supports the grade-2 acceptance (table-driven over `_FOLD_ROWS`, 3 rows × 2 spellings ×
paired assertions, ABC-driven by the same "many fixture/assert calls, no real branching" shape
as `_t09_symlink`) — I am **supplying** the reason the process should have recorded: this is a
deliberate table-driven test, splitting it per-row would fragment the discriminator-pairing
invariant its own comment explains across many functions. `BLOCKS: no`, but flagging the process
gap since the protocol requires a written answer per gated record.

### Cycle-0's surviving findings, re-measured at this pin

- **F-13 / check-plan-routes.py's top-level-status VIOLATION line — still standing, unchanged.**
  `check-plan-routes.py:386`: `f"VIOLATION top-level status {feature_station!r} is not one of..."`
  carries no task id, no feature id, no path — unlike every sibling finding in the same file,
  which at least carries `{tid}`. `findings` is one flat list accumulated across every plan in a
  multi-plan sweep and printed with no per-plan grouping (`:896-913`) — so in a sweep examining
  more than one plan, this specific message cannot be attributed to a feature if more than one
  plan carries the same illegal value simultaneously. Not touched by any commit in this range.
  `low`, non-blocking, unchanged from cycle 0.

---

## Carried finding — station-verb identity binding — **RE-MEASURED, REPRODUCES, confirmed omission not a decision**

Built an end-to-end `$TMPDIR` probe (not a unit test) with a fixture whose only domain grant is
`harness-frontend-dev: { path: frontend/**, upsert: true }` — nothing under
`.harness/harness/features/FEAT-VICTIM/` — and fired the *actual* `bash-write-guard.sh` (the
PreToolUse Bash hook) with the exact payload it would receive for:
```
python3 .../plan-merge.py set-feature-station --file <victim's plan.yaml> --station done
```
**`bash-write-guard.sh` returned exit 0, no stderr — did not see it as a write at all.** Read its
detection logic directly (`bash-write-guard.sh:407-524`): the `findings` list is only ever
populated by `sed -i`/`perl -i`, `tee`, `mv`/`cp`, `rm`, `sponge`, `awk -i`, or a bare shell
redirect — invoking an arbitrary program that performs its own internal file writes (like
`plan-merge.py`) matches none of these, so `if not findings: sys.exit(0)` (`:644`) fires before
the domain-check code beneath it is ever reached. **I then ran the actual command: exit 0,
`plan-merge.py` reports `STATION ... -> done` and `APPLIED ...`, and the victim's `plan.yaml`
genuinely changed from `status: building` to `status: done`.** No error, no denial, at any layer.

`plan-sign-gate.py`'s own docstring (`:19-21`) states this explicitly as intentional scope, not
an oversight for *that* gate specifically: "IT DENIES ONE VERB, NOT THE TOOL... `set-task-station`
and `set-feature-station`... stay open — T-05's playbook names them and T-09's shape gate leaves
them as plan.yaml's only writer." **This is true and correctly describes `plan-sign-gate.py`'s
own scope — but nothing else fills the gap it leaves.** I grepped `plan.yaml`'s D-01..D-16 for
any decision addressing caller-identity binding on `set-feature-station`/`set-task-station`:
**zero hits.** D-07 explicitly justifies `sign-approval`'s *own* new gate; no equivalent decision
exists, or was ever needed, for the other two verbs. **Confirmed: an omission, not a recorded
decision.**

**Finding (high, must_fix from a code-correctness angle — severity is primarily security's call,
reported here as independently re-measured fact):** any of the 16 harness personas, with Bash
access to a completely unrelated feature, can flip any *other* feature's `plan.yaml` station to
any legal value, undetected by every write-domain gate this feature and its predecessors built.
`BLOCKS: yes` (pending reconciliation with the security reviewer's own probe, per the dispatch's
instruction not to duplicate their matrix — I report the fact and my own severity read, not a
final disposition).

---

## Digest of every finding, ranked

| id | severity | file:line | BLOCKS |
|---|---|---|---|
| NEW-1 | **high** | `BUG-1030-stale-anchor-write-hazard/feature.json` (deleted in `a8a8944`) | **yes** |
| carried-security | **high** | `bash-write-guard.sh:407-524,644`; `plan-merge.py` `set-feature-station`/`set-task-station` | **yes** |
| MED-1 | med | `check-domain.sh:1037,1045` (`RE_STATE_YAML`, `RE_CLAUDE_MD`) | no |
| H-01-b | med | `check-domain.sh:1487`; `test-check-domain.py:2684` | no |
| `_t09_case_fold` reason | med | `test-check-domain.py:2782` | no |
| H-01-a | low | `check-domain.sh:1487-1506` | no |
| H-02-a | low | `plan-sign-gate.py:116` | no |
| `worktree_terminal` prefix match | low | `worktree_terminal.py:389` | no |
| F-13 | low | `check-plan-routes.py:386` | no |
| traceability (BUG-1055/BUG-1030) | low | n/a (data files, not source) | no |

## Unexamined

- Cycle 1's own carried gap (no cross-mutation proof that INV-32 and INV-33's assertions cannot
  pass on each other's fixture output) — I re-confirmed the blocks are disjoint by line range but
  did not attempt the cross-mutation myself; QA's cycle-2 note (`notes/qa-FEAT-41-c2.md:§10`)
  names this as still open too.
- The full `check-state.sh`/`test-check-state.py` suite run — QA's exclusive lane; I read the
  specific INV-32/33 sites rather than executing anything.
- `worktree_terminal.py`'s `_hook_feature_dir`/`inflight_registry` mechanism (origin/main code,
  D-16's own framing scopes this to security).
- The "symlinked parent directory" sub-question of H-01, explicitly delegated to security by this
  cycle's dispatch — not probed here.
- A fourth or later instance of the BUG-1030 pattern beyond the 13 plan-less directories surveyed
  — I checked all 13 by name; none besides BUG-1030 showed a pre-deletion non-terminal value.

## Open questions

- Is `BUG-1030-stale-anchor-write-hazard` genuinely still open (needs `#1079`-style treatment) or
  was it already abandoned by the time of migration? This is an operator determination, not
  mine — I can only confirm the record of its prior non-terminal station no longer exists
  anywhere. (blocking: yes — gates NEW-1)
- Does the security reviewer's own re-measurement of the carried station-verb-identity finding
  agree with mine (exit 0, plan.yaml genuinely rewritten, no gate at any layer)? I did not
  coordinate results before writing this. (blocking: no — my own finding stands regardless)

```yaml
VERDICT: FAIL
DIGEST:
  headline: Both stages ran; all four cycle-1 findings independently mutation-proven CLOSED, but two new HIGHs surfaced by diffing the full range — a sibling non-terminal feature.json (BUG-1030) was silently destroyed the same way BUG-1071 was deliberately preserved, and the carried station-verb identity-binding gap reproduces live end-to-end.
  severity_max: high
  findings: 10
  must_fix:
    - "BUG-1030-stale-anchor-write-hazard's non-terminal feature.json status (Review) was deleted by commit a8a8944 with no plan.yaml, no issue, no D-NN — its station is now recorded in zero files, inconsistent with BUG-1071/#1079's deliberate preservation of the identical shape"
    - "plan-merge.py's set-feature-station/set-task-station verbs are reachable via an ordinary Bash call with no caller-identity or per-feature domain binding at any layer (check-domain.sh never sees Bash; bash-write-guard.sh's pattern list does not cover program invocations that write internally) — reproduced live: an unrelated agent's fixture flipped a victim feature's station to done, exit 0, plan.yaml genuinely rewritten"
  spec_violations:
    - { kind: omission, path: "BUG-1030-stale-anchor-write-hazard/feature.json", ref: "REQ-06 (station recorded in exactly one file — now recorded in zero)" }
    - { kind: omission, path: "plan-merge.py (set-feature-station, set-task-station)", ref: "REQ-05 (no decision authorizes the identity gap; D-07 covers sign-approval only)" }
  reviewed: "7c4f0bd..39477a502cd6726f01ad403dbdb4222c26969d2e"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Is BUG-1030-stale-anchor-write-hazard genuinely still open (needs #1079-style disclosure/issue) or was it already abandoned when migrated — an operator determination I cannot make from the record alone", blocking: true }
    - { id: Q2, question: "Does the security reviewer's independent re-measurement of the carried station-verb identity finding agree with mine (exit 0 end-to-end, no gate at any layer)?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-41-one-station-vocabulary/notes/review-harness-code-reviewer-c2.md
```
