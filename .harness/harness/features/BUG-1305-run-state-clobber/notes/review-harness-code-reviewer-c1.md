# Code review — BUG-1305-run-state-clobber — review-c1 — pinned dc0e0313

**BLUF: one demonstrated HIGH fail-open — an Edit that CREATES `.run-identity.json` where none
exists is not refused by `check-domain.sh` (exit 0, proven live) — gates this review under
`advisory_unless_high`. Everything else (all seven REQs, all thirteen SCs, the mechanical grade)
checks out. Two Stage-1 evidence-quality gaps found and one independently RESOLVED by me in the
same pass (SC-09/SC-07's "control-plane root" pin ran over the wrong tree, but I re-ran it over the
real one and it is clean). One Stage-2 maintainability note. All findings below are ship-rulable
without further build cycles except the HIGH, which needs either a small code fix or an explicit
operator risk acceptance — both of which cost nothing to write down now.**

All source read via `git show dc0e0313:<path>`, never the working tree. Diff scope confirmed via
`git diff --name-status origin/main...dc0e0313` against the Contract's file list — no extra files.

## Stage 1 — spec compliance

Read `BRIEF.md` REQ-01..REQ-07/SC-01..SC-13, `plan.yaml`'s T-01/T-02/T-03/T-05/T-06/T-09 intents,
all six `research-BUG-1305-plan-fix-c*.md` notes, and every named evidence artifact
(`redproof-BUG-1305.md`, `regression-delta-BUG-1305.md`, `probe-notebookedit-BUG-1305.md`,
`qa-testmatrix-c1.md`, `qa-regate-sc01-c10.md`). Every REQ traces to shipped code; nothing is scope
creep; the two ANSWERED adversarial questions from the dispatch:

- **Neither compare skipped, no write refused by both.** `check-domain.sh`'s `RE_STATE_YAML` PRE
  branch (:1603-1707) parses the prior ONCE (`prior_doc`/`prior_exc`), computes `prior_has_uid`, and
  routes exactly one of the two compares: witness `conflict()` when `not prior_has_uid` (absent,
  zero-byte, unparseable, or parses with no/empty `run_uid`), the `uid_conflict()` ladder when it
  parses WITH one. Traced every branch by hand; the mutually-exclusive `prior_has_uid` gate means no
  input reaches neither, and no input reaches both.
- **SC-01(b)/(c) both routes, SC-01(d)/(e) silent — all confirmed in the test bodies.**
  `_bug1305_marker_foreign_refusals` (Write+Edit, absent prior), `_bug1305_identity_refusal_cases`
  (`different minted uid is refused`/`...Edit is refused` = (b) both routes; `modal collision Write
  omitting uid`/`...Edit removing uid` = (c) both routes), `_bug1305_identity_allow_cases`
  (`recovering owner with absent/zero-byte checkpoint remains allowed` = both (d) halves,
  `DEC-154 resumed owner ... across sessions` = (e)). SC-01(f) precedence: both halves present, one
  in each test file (`run_id disagreement keeps Issue 1124 precedence` in T-09's suite, `witness
  outranks legacy run_id ladder` in T-02's).
- **REQ-06/SC-06.** The false `"intentionally Write/PRE-only"` sentence is gone; the replacement at
  `check-domain.sh:~1291` states plainly "fires on Write and Edit ... Bash ... refused outright ...
  POST is too late to refuse" — accurate, and matches the four SC-05 cases. One residual echo, see F-03.
- **REQ-05/T-06.** All four cases present (`digest Edit append repair remains allowed`, `digest Edit
  insertion is refused with append-at-end route`, `cross-run digest replacement remains refused`,
  `digest Write append remains allowed`) — matches the spec's four cases exactly.
- **T-05/SC-04 fail-closed.** `check_artifact_file` → `_durable_artifact_candidates` (three roots,
  first-file-wins) → `_missing_durable_artifact` (return 0 iff no root resolved at all, else 2). All
  six spec'd test cases present in `test-validate-digest.py`.
- **Cycle-11 refactor read as new work.** `uid_conflict`'s extraction into `_minted_uid` is
  behavior-preserving by hand-trace (the `""`-vs-`None` filtering moves earlier but the observable
  branching is identical). `run_bug1305_marker_cases`' six-way split preserves every one of the 14
  original assertions (enumerated and matched one-for-one). `test-check-state.py`'s nested-`build`
  extraction is a pure two-function split, same operations same order. No behavior lost.

### Findings

**F-01 (severity: med → resolved by me in this pass, not a live defect) — SC-09/SC-07's
"control-plane root" pin was captured over the wrong tree; substance re-verified clean.**
`notes/regression-delta-BUG-1305.md`'s `## Suite results` records `bash
.claude/skills/harness/bin/check-state.sh: exit 0 ... no INV-36/run-identity finding` with no
`HARNESS_PROJECT_DIR` override and no absolute path shown. `check-state.sh`'s root resolves via
`harness_boundary.resolve_root(bin_dir)`, which derives from **where the script itself lives**
unless overridden — i.e. from the worktree, not `/Users/molchairuangutai/GitHub/harness`. I counted:
worktree `.harness` tree = 19 `runs/*/state.yaml`; the real control-plane root = 356 (BRIEF's cited
"630 ... and grows continuously" is from an earlier day, consistent with continuous growth). SC-09's
fifth pin and SC-07's mirror sentence both explicitly require the run be over "this machine's own
control-plane root" — the note shows no evidence it was. **I ran it myself, live, over
`/Users/molchairuangutai/GitHub/harness`: `bash .claude/skills/harness/bin/check-state.sh 2>&1 | grep
-c INV-36` → `0`, exit `0`.** The mechanism is correct; the artifact's own evidence just isn't what it
claims to be. Ship-rulable: yes — no code change, and my own re-run is now on the record; the
operator can accept it in place of a note re-capture, or ask for one more (cheap) command run.

**F-02 (severity: med) — SC-11's probe note fails its own literal FAILS-if.**
`notes/probe-notebookedit-BUG-1305.md` records `route_reachable: no` / `guard_fires: n_a` with a
prose paragraph and **no verbatim command, no verbatim output** for either line. SC-11's text: "each
with the verbatim command and output that produced it... FAILS if ... a recorded answer has no
command and output beside it." Literally true here — narrative only. The underlying conclusion (this
OMP host's tool inventory has no NotebookEdit) is plausible and I have no reason to doubt it, but the
artifact doesn't meet its own falsifiability bar. Ship-rulable: yes, no code change — either the
operator accepts the substance as-is, or someone appends one command+output pair (e.g. a grep of the
host's tool manifest, or an attempted NotebookEdit payload and its rejection) to the same note.

**F-03 (severity: low, advisory only) — a residual echo of the retired "PRE-only" phrasing.**
`check-domain.sh:1240`: `"RE_RUN_DIGEST stays out because its content comparison is PRE-only."` This
is a DIFFERENT, TRUE claim (why `RE_RUN_DIGEST` is excluded from `SHAPE_PATTERNS`/`SWEEP_GLOBS` — the
POST sweep genuinely never re-checks it, confirmed: `has_shape_rules()` excludes `RE_RUN_DIGEST`, so
the POST "elif target:" branch exits before ever calling `shape_problems()` for a digest path) — not
the retracted claim about which TOOL ROUTES the guard covers (Write vs. Edit), which is what REQ-06
targeted and which the actual guard-adjacent comment at :1291 states correctly. Not a real SC-06
violation on inspection, but the word "PRE-only" recurring in the same file after this feature spent
a whole REQ retracting exactly that phrase is worth a wording pass so a future skim-reader doesn't
conflate the two. Ship-rulable: yes, pure wording.

## Stage 2 — code quality / fail-open hunt

**F-04 (severity: HIGH, must_fix) — an Edit that CREATES `.run-identity.json` is not refused.
Demonstrated live, not inferred.**

`check-domain.sh`'s PRE Edit-reconstruction path (`_edit_reconstructed_content`, used for
`RE_RUN_DIGEST`/`RE_STATE_YAML`/`RE_RUN_IDENTITY`/`RE_HANDOFF` at :2036-2058) does
`open(absolute_path).read()` and, on `except OSError: return None` — which is exactly what
`FileNotFoundError` is — the caller does `if _content is None: sys.exit(0)`, **skipping
`shape_problems()` entirely.** T-02's own spec is explicit: the witness guard "refuses ANY Write or
Edit whose target matches it ... Refuse WHETHER OR NOT the file exists on disk: no governed tool
write ever legitimately produces this file ... a Write that CREATES a false witness in a directory
holding none is as bad as one that overwrites a true one." Write is correctly covered (it always
builds `targets` unconditionally, so `shape_problems()` always sees it — confirmed via the existing
`"Write creating false witness is refused"` case, which passes). **Edit is not.** I proved it:

```
root, state = m._bug1124_state_fixture()          # fresh run dir, NO .run-identity.json
identity = m._bug1305_marker_path(state)
r = m._fire_digest_edit(root, identity, "{}", '{"run_id": "forged"}')
# r.returncode == 0
```
Exit 0 — confirmed directly against the pinned hook, not inferred. `bash-write-guard.sh`'s Bash route
is unaffected (`_run_artifact_guard` matches on path alone, no existence check, so Bash creation is
still refused). Only the PRE **Edit** route has the gap. It is new to this feature: state.yaml's
identical "file absent → pass-through" behavior is BENIGN there (an absent prior is explicitly
legitimate per SC-01(d)), but the witness is the one artifact this feature says must be refused
**regardless of whether it exists** — the first time this shared helper's blind spot has real
consequence.

**Failure scenario:** an Edit tool call targeting `.run-identity.json` in a run directory that has
never been governed-write-minted (i.e. before or instead of its own first POST landing — exactly the
"first-write window" this feature already names as residual elsewhere) is not refused by this hook.
If the underlying Edit tool can be made to target a path that does not yet exist — **unmeasured
here, same category of uncertainty this feature explicitly measured for NotebookEdit (SC-11) but did
not for this** — a writer could plant a forged witness (`run_id`, `run_uid`, any seed field) in a
directory that never had one, which REQ-02's detection and every future `conflict()`/`uid_conflict()`
call would then trust as ground truth. **Spec violation, kind: mismatch** — T-02's own intent text
("refuses ANY Write or Edit ... regardless of whether the file exists") is not what the code does.

**Remedy, exact:** check `RE_RUN_IDENTITY.match(_norm(target))` before (or independently of)
`_edit_reconstructed_content` in the `not _post` Edit branch, and refuse unconditionally on a match —
the witness rule never needed reconstructed *content* in the first place (it denies on path alone in
`shape_problems()`), so it does not need the reconstruction helper's existence check to succeed.

**Ship-rulability — genuinely mixed, stated honestly:** if Claude Code's Edit tool cannot be invoked
against a nonexistent path at the tool level (plausible — this is the same "before it reaches
Harness" host property SC-11 measured for NotebookEdit, and the pre-existing state.yaml/digest.md
Edit-reconstruction code has relied on exactly this same assumption, silently, since #1106), this gap
is dormant and the operator can rule to accept it as a disclosed residual, same shape as the
already-accepted forgery residual in REQ-01. If that assumption doesn't hold, it is live and needs
the one-line fix above. Either way it costs nothing to decide now: **this is the one finding I would
not let ship silently** — not because the fix is expensive, but because the asymmetry with Write
(which IS covered, and IS tested) means a reader who checks only the test suite will believe the
witness is fully closed on both routes when it is not.

**F-05 (severity: med, advisory) — an undocumented, currently-harmless asymmetry between the two
new identity compares' `_post` handling.**

The ladder's `uid_conflict` compare is explicitly suppressed during POST: `uid_reason = None if _post
else run_identity.uid_conflict(prior_doc, doc)` (:~1695), with the design comment "POST is not a
write-refusal route." The pre-ladder seed-field `conflict(marker, doc)` compare (:~1630-1650) has
**no analogous `_post` guard** and can still `out.append(...); return out` (→ `sys.exit(2)`) during
POST processing. I traced every path this could matter (fresh directory: witness is created from the
same `doc` inside the same POST call, so it trivially agrees; pre-existing directory: PRE has already
vetted the identical inputs before the write could ever land) and found **no case where this produces
a wrong result today** — every write that reaches POST has already passed the identical check at PRE.
But the invariant that makes this safe ("POST re-checks the same inputs PRE already checked") is
nowhere stated, unlike the sibling `uid_conflict` guard which explains itself. A future change to how
`doc` or `marker` is derived at POST time (e.g. if either is re-read fresh rather than reused) could
silently start emitting a misleading "write refused" message for a write that has *already landed* —
exactly the failure mode T-02's own intent explicitly worried about for the mint block ("nothing here
exits non-zero") but did not extend to this compare. Ship-rulable: yes, no test currently fails; a
one-line comment (or an explicit `if not _post:` matching the sibling guard's shape) is the
recommended, not required, remedy.

**Considered and dismissed:**
- `check-state.sh:1502-1514`'s redundant `_uid_reason` guard (the `bad.append` not gated on
  `if _uid_reason:`) — already found and correctly triaged as an APPLY candidate, NOT applied, in
  `notes/receipt-harness-backend-dev-simplify-simplification-c1.md`. I confirmed it independently:
  the outer `if` guarantees `uid_conflict` never returns `None` at the point it's called, so there is
  no current behavioral consequence — only a future-maintenance risk the simplify pass already
  recorded. Not re-raising as a new finding.
- `run_identity.conflict()`'s `recorded is not None` guard reads the string `"None"` (from
  `str(doc.get(k))` when `doc[k]` is Python `None`) as a *present* value, not absent — a checkpoint
  that explicitly writes `run_id: null` would witness-record the string `"None"` rather than a
  skippable absence. This is exactly what T-01's literal spec asks for (`str(doc.get(k)) if key in
  doc else None`), has no realistic trigger (no lead writes an explicit YAML null for a seed field),
  and is not worth a finding.

## Mechanical code grade

`python3 .claude/skills/harness/bin/code-grade.py --base 4b0d04e9 --head 27507695` → **exit 0**, 50
records reported, matching the established baseline exactly. `code_grade: grade_2` — no grade-1
record and no production function below its grade-4 bar exists; seven grade-2 records survive, each
independently re-verified against the tool's own output (not assumed from the dispatch):

| Function | File:line | Cyc/Cog/ABC | Touched by this diff? | Why acceptable at grade 2 |
|---|---|---|---|---|
| `main` | `tests/integration/test-check-domain.py` | 4/10/45.0 | Yes — 3 lines net-consolidated to 1 (`run_bug1305_cases()`) | **Independently re-graded at base 4b0d04e9: 4/10/44.2, grade 2.** Same band before and after — this diff did not worsen it, it is the pre-existing accumulator-function floor (dozens of unrelated `fails += run_X()` lines going back years). Correctly excluded from the tool's own diff report (new-or-worsened only); I confirm by direct computation, not by trusting the dispatch. |
| `_write_while_sweep_reads_fifo` | `test-check-domain.py:1044` | 8/16/23.8, driver cognitive | No — new in the base..head range but from an earlier, unrelated commit on this branch (BUG-1304-era sweep-race work; git log shows `test(harness): make sweep race proof deterministic` etc. predating BUG-1305's own commits) | Not BUG-1305's own code; a race-condition fixture with many sequential setup/assert steps, a known accepted shape for this suite. |
| `run_bug1305_digest_repair_cases` | `test-check-domain.py:3878` | 4/5/31.5, driver abc | Yes — T-06's own test function | ABC-driven fixture/assert accumulator (four sequential digest-repair scenarios in one function); splitting would fragment the shared `prior`/`artifact` fixture across four functions for no readability gain, per the simplify receipt's own conclusion on this exact shape. |
| `_bug1305_identity_refusal_cases` | `test-check-domain.py:4978` | 11/5/27.2, driver cyc+abc | Yes — T-09's own test function | Five sequential refusal-case constructions + assertions; same fixture-per-case shape as its siblings. |
| `case_bug1305_run_identity_invariant` | `test-check-state.py:4560` | 12/7/35.3, driver cyc+abc | Yes — T-03's own test function; its nested `build` (line 4562) was a grade-1 HIGH blocker, now extracted to grade 5 | The OUTER function (six fixture-tree constructions X/V/Y/Z/L/W plus two full-run assertions) was already grade 2 pre-refactor and stays so; only its worst-offending nested closure needed extraction to clear the build gate. |
| `case_uid_mint_and_injection` | `tests/unit/test-run-identity.py:64` | 5/4/38.7, driver abc | Yes — T-01's own test function | ABC-driven (mint-shape assert, injection-preserves assert, no-replace assert, no-newline assert, missing-file assert — five behaviors of one primitive tested together, matching this file's own case-per-topic convention, not case-per-assertion). |
| `case_seed_conflict_guards` | `tests/unit/test-run-identity.py:86` | 6/4/26.1, driver abc | Yes — T-01's own test function | Same shape: the run_id-first guard, the squad guard, and the two born-null cases are one coherent topic (the write-once seed's null-tolerance), deliberately kept together per T-01's own instruction to build the marker "through record_seed rather than by hand." |

All seven are TEST code (bar 3, not production bar 4); grade 2 never blocks the build per the
grading skill's own rule, and each has a reason above naming the function.

## Fail-open enumeration (as asked)

- `check-domain.sh` `if _no_parser: return out` — DEC-171 bootstrap-grant fail-open. Correct as-is,
  operator-ruled, out of scope for this feature to reverse.
- `run_identity.record_seed`/`inject_uid` — best-effort `except Exception/OSError: return
  False`/`pass`. Intentionally fail-open by spec: a witness recording failure must never break a
  legitimate write. Correct.
- `validate-digest.py._missing_durable_artifact` — fails OPEN only when no candidate root resolves at
  all; fails CLOSED once a directory resolves but the file is absent. Correctly asymmetric, matches
  T-05 spec exactly, verified against all six test cases.
- `check-domain.sh`'s digest-guard `prior is None` branch (unreadable prior) — fails CLOSED
  (refuses). Correct.
- `_edit_reconstructed_content`'s `except OSError: return None` → caller `sys.exit(0)` — **fails
  OPEN, and for `.run-identity.json` specifically this is wrong; see F-04.** For state.yaml/digest.md
  it is benign (an absent prior is legitimately unprotected there).

## Verdict basis

`must_fix: [F-04]`, `severity_max: high` → gates under this repo's `advisory_unless_high` review
policy. Every other finding (F-01, F-02, F-03, F-05) is advisory, ship-rulable with no further build
cycle, and I have already done the one piece of remediation available to a read-only reviewer for
F-01 (re-running the check over the real control-plane root and recording the clean result here).
