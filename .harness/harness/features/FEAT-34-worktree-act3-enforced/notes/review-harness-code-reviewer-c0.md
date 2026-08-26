# Code review — FEAT-34, `review_sha` 513c4a46e34cbe327d96922c01cebdd18e85d62e

Stage 1 (spec compliance) then Stage 2 (quality), against the pin, per `harness-code-review`.
All citations `git show 513c4a4:<path>` unless noted. Weighted the hand-written
`main-session-direct` surface (T-06..T-12) first, per dispatch.

## VERDICT: FAIL — one must_fix (high)

---

## MUST_FIX — high

### F1. INV-29's printed removal command is broken for any short-named worktree — REQ-02

`check-state.sh:1320-1328` composes the remediation command from `_r29["feature_id"]`:

```
bad.append(_head29 + " Remove it with `python3 .claude/skills/harness/bin/feature-worktree.py
remove --repo %s --id %s` (path: %s)." % (_r29["repo"], _r29["feature_id"], _r29["path"]))
```

For the SHORT-NAME-PREFIX-MATCHES-EXACTLY-ONE case, `worktree_terminal.py:249,273-277` sets
`feature_id = resolved_id` — the **full landed directory name**, not the worktree's own on-disk
directory name. `feature-worktree.py:207` (`dest = dest_for(owner_root, segment, args.id)`) does
a **literal** join with no prefix resolution (`dest_for`, `feature-worktree.py:56-59`), so GATE 1
(`feature-worktree.py:211-214`) tests `os.path.exists(dest)` against a path built from the FULL
name. When the worktree's real directory is the short name, that path does not exist and GATE 1
fails: `feature-worktree: remove: not a linked worktree of <owner_root>: <dest>`, exit 3.

**Concrete scenario.** A worktree on disk at `.claude/worktrees/harness/FEAT-SHORT` whose landed
directory on the default branch is `FEAT-SHORT-named-in-full` (status `Done`) — exactly the
fixture `test-check-state.py`'s `case_inv29` group (f.3) builds
(`wt_short = _i29_wt(r, "FEAT-SHORT")` against `_i29_land(r, "FEAT-SHORT-named-in-full", ...)`,
`test-check-state.py:2521` at the pin). INV-29 correctly fires (REQ-06/SC-05 clause (c) is met on
that half) and prints: `` `... feature-worktree.py remove --repo harness --id
FEAT-SHORT-named-in-full` `` (path: `.../FEAT-SHORT`). An operator or the main session runs that
exact command as instructed. `dest_for` builds
`.claude/worktrees/harness/FEAT-SHORT-named-in-full`, which does not exist, and the command exits
3 with "not a linked worktree" — a message that reads as though the worktree the invariant just
named does not exist, even though it plainly does under its short name. The commit stays blocked
(INV-29 keeps firing) and the printed remedy is not the fix.

`post-merge-sweep.sh:150` gets this right: `wt_id = os.path.basename(path.rstrip(os.sep))`,
derived from the record's own `path`, never from `feature_id` — and it is that `wt_id` that gets
passed to `--id` (`post-merge-sweep.sh` `_handle_record`, further down). INV-29's composition is
inconsistent with the hook's own, correct pattern for the identical case.

**Why the shipped, green suite does not catch it.** `test-check-state.py`'s message-content group
(`case_inv29` group (b), `:2385-2410` at the pin) grades the composed command string, but its
fixture uses `wt = _i29_wt(r, "FEAT-T29")` against `_i29_land(r, "FEAT-T29", ...)` — an EXACT
match, where `feature_id == wt_id` and the bug cannot show. Group (f.3), the one fixture that
actually exercises the short-name/full-landed-name mismatch, only asserts `len(_i29_for(out,
wt_short)) == 1` (one line fires) — it never inspects the command the line carries. No case
anywhere in the diff composes and *checks* the remediation command for a worktree whose `feature_id`
differs from its own path basename.

**Fix shape** (not prescribing, since this is read-only territory): use
`os.path.basename(_r29["path"].rstrip(os.sep))` for `--id`, exactly as `post-merge-sweep.sh:150`
already does, rather than `_r29["feature_id"]`.

---

## Findings — ranked, none gating alone

### F2. T-12's per-clone step is still prose the reader is trusted to follow — med, not must_fix

T-12's own intent text (`plan.yaml`) is explicit: "write it as commands the main session
actually runs, never as prose the reader is trusted to follow." The delivered
`harness-init/SKILL.md` step 2 reads: **"Unset, or already `.claude/skills/harness/hooks`? Set
it, and say which of the two you found:"** followed by two commands — a narrated conditional, not
an executable branch. `test-hooks-install.py`'s own header says so outright: *"harness-init/
SKILL.md's 'per-clone step' (T-12) is prose, not a script"* (`test-hooks-install.py:4`), and its
`run_setup_step()` (`:192-206`) is an **independent Python re-implementation** of the same
conditional (`if found in ("(unset)", TARGET): ...`), not an execution of the documented prose.
`case_commands_verbatim_in_skill()` (`:229-238`) only checks that the two literal command
strings appear verbatim in the file — it does not, and structurally cannot, verify the
*conditional wording around them* is still correct.

**Concrete scenario.** A later edit to `harness-init/SKILL.md`'s step 2/3 wording — say, the
"or already `.claude/skills/harness/hooks`" qualifier is dropped so the prose now reads as an
unconditional write — leaves both literal command strings untouched. `case_commands_verbatim_in_skill`
still passes (strings present); every SC-08/SC-13 case still passes (they run
`run_setup_step()`'s own hard-coded conditional, independent of the prose). A main-session agent
later following the now-wrong prose would silently overwrite an operator's own `core.hooksPath`
in a real clone — REQ-13's central promise — while the automated suite stays green throughout.

This is plan-sanctioned as a compromise (T-13's intent text: "Because it lives in a SKILL.md
rather than a script, invoke the same command sequence the skill states...") — the signed plan
already accepted that a prose procedure cannot be fully machine-verified. I am not marking it
must_fix on that basis, but it is worth surfacing plainly: nothing in this suite protects the
prose's *logic*, only its literal command substrings, and REQ-13's silent-overwrite guarantee
ultimately depends on an unverified paragraph.

### F3. R1 — plan.yaml's T-04 case (f) prose is wrong; the code is right

`plan.yaml`'s T-04 intent (case f) reads: *"An unresolved record - a short-named worktree
matching no landed directory - is printed and its worktree is left standing."* Per T-01's own
signed algorithm (`plan.yaml` T-01 intent, and `worktree_terminal.py:236-244` at the pin), a
short-named worktree matching **zero** landed directories is `exempt_absent`, never `unresolved` —
T-01's own words: *"A prefix matching ZERO landed directories... is exempt_absent, never
unresolved."* T-04's case-(f) label describes exactly that zero-match shape and calls it
unresolved — inconsistent with the algorithm it itself depends on.

The delivered code is correct and self-aware of the discrepancy. `test-post-merge-sweep.py`'s
`case_unresolved_left_standing` (`:517-543` at the pin) builds the real unresolved-producing
shape — an **ambiguous** prefix matching **two** landed directories
(`FEAT-40-amb-one`/`FEAT-40-amb-two`, worktree `FEAT-40`) — and its comment states outright: *"not
a 'genuinely absent' name, which classifies exempt_absent and is a DIFFERENT class the sweep
silently skips."* `test-worktree-terminal.py`'s `case_classify` (`:102`, `:141-143`) asserts the
identical predicate at the library level.

I also checked the half of R1 that follows if the code *had* been wrong: whether SC-05 clauses
(c)/(d) — `test-check-state.py`'s `case_inv29` group (f.3)/(f.4) — actually discriminate the
over-suppression bug, or pass for the wrong reason. They discriminate correctly: (f.3) is a
short name matching exactly **one** landed directory (`worktree_terminal.py:248-249`), which
correctly resolves to `terminal` and fires; (f.4) is an unparseable landed `feature.json`, which
correctly resolves to `unresolved` and fires. Both exercise the real predicates SC-05 needs.

Verdict: `plan.yaml`'s T-04 case (f) description is the wrong artifact, not the shipped test or
the library. No behavior is affected — low/med severity, a documentation defect in a signed plan
that could mislead a future reader auditing coverage, not a code defect. (Recovery of the
original, reportedly-overwritten T-04 receipt was attempted per the dispatch:
`git log --all --oneline -- ".../notes/receipt-harness-backend-dev-T-04*.md"` shows only the two
commits that make up this diff — no earlier version is reachable in this repository's refs, so
the "overwritten by re-dispatch" history could not be recovered and is reported as such.)

### F4. R2 — the known stale citation has company; full enumeration attached

Confirmed the digest's L1 finding stands: `check-state.sh:1209` — *"exactly as INV-25 at :1109 and
INV-26 at :1203"* — `:1109` is right, `:1173` (cited separately at `:1314`) is right, `:1203` is
wrong: that line sits inside INV-29's own comment block; INV-26's `CANNOT RUN` append is actually
at `:1363` (160 lines later — the size of the INV-29 block inserted above it). Already filed at
low severity, backlog; not repeating it as new.

**Sweeping for the same class per the residual's instruction turned up two more, in the same
comment block**, that L1 did not cover (L1 only checked check-state.sh's own citations of
check-state.sh/INV-25/INV-26; these cite a *different* file):

- `check-state.sh:1262` — *"(worktree_terminal.py:202-206)"* for the WORKTREES_SEGMENT-mismatch
  record. The actual dict literal is at `worktree_terminal.py:211-214`
  (`records.append({"path": path, "feature_id": None, "klass": "unresolved", ...})`); `:202-206`
  lands inside a comment two paragraphs earlier ("...D-10/T-01 rework)." through a blank line and
  `dirty = _is_dirty(path)`). Off by ~9 lines.
- `check-state.sh:1263` — *"the fleet-load record (:303-306)"*. The actual literal is at
  `worktree_terminal.py:311-314` (`records.append({"path": factory_config.FLEET_PATH, ...})`);
  `:303-306` lands inside the `classify_all` docstring's closing paragraph. Off by ~8 lines.

**Full enumeration of every other line-number citation added by this diff, checked individually
(none exhaustively grepped — each opened and read at the pin):**

| Citation (as written) | Where cited | Verified against | Result |
|---|---|---|---|
| `INV-25 at :1109` | `check-state.sh:1209` | `check-state.sh:1109` (`INV-25 CANNOT RUN` append) | correct |
| `INV-25's precedent at :1173` | `check-state.sh:1314` | `check-state.sh:1173` ("NO REMOVAL GUIDANCE HERE") | correct |
| `SAME RESOLUTION AS INV-26 at :1371` | `check-state.sh:1596` | `check-state.sh:1371` (`_gh_bin = os.environ.get("FACTORY_GH")...`) | correct |
| `check-state.sh:1117-1135` | `worktree_terminal.py:81` | porcelain parse block, `check-state.sh:1117-1135` | correct |
| `check-state.sh:1138-1143` | `worktree_terminal.py:202`, and `post-merge-sweep.sh:83` | "THE BASE IS DERIVED ONCE..." comment, `check-state.sh:1138-1143` | correct |
| `check-state.sh:1173` | `post-merge-sweep.sh:145` | as above | correct |
| `factory_config.py:46` | `worktree_terminal.py:120` | `harness_root()`'s `_BIN_DIR` derivation, `factory_config.py:46` | correct |
| `feature-worktree.py:287` | `worktree_terminal.py:164` | `r = _run_git(["rev-parse", f"{default_branch}:{rel}"], owner_root)`, `feature-worktree.py:287` | correct |
| `harness-init SKILL.md:73/:78` | `post-merge-sweep.sh:75` | `:73` is the `git config core.hooksPath ...` command, `:78` is the relative-path rationale | correct |
| `worktree_terminal.py:202-206` | `check-state.sh:1262` | actual record at `:211-214` | **stale**, ~9 lines |
| `worktree_terminal.py:303-306` | `check-state.sh:1263` | actual record at `:311-314` | **stale**, ~8 lines |
| `INV-26 at :1203` | `check-state.sh:1209` | actual at `:1363` | **stale** (already filed, L1) |

Three of twelve added citations are stale, all in comments (no behavioral effect), all clustered
around the two insertion points (INV-29's own block, and the discriminator comment inside it) —
consistent with the digest's diagnosis that INV-29's insertion shifted downstream references and
the citations were written against a pre-insertion snapshot. Severity low, same bucket as L1 —
backlog, not must_fix; grouped here as one item since it is the same defect class and the same
remedy (re-derive line numbers before the next edit touches this block).

---

## Stage 1 — spec compliance, otherwise clean

Traced REQ-01..REQ-13 and D-01..D-11 against the diff. Every touched surface maps to a task; no
scope creep found (`worktree_terminal.py`'s `_repo_arg_for_segment` duplication into
`post-merge-sweep.sh` is flagged in the prior digest as D1/low and is a plan-level question, not
this pass's to relitigate). SC-01 through SC-16 verified at the level `verify: inspection` or
`verify: automated` calls for; the one exception is F1 above, which SC-01's own fixture does not
exercise and F3 above (T-04 case f) turned out to concern the plan, not the code.

INV-30's offline-silent posture (`check-state.sh:1544-1636`) matches INV-26's established pattern
exactly and is signed as deliberate (BRIEF `## Added verification gaps`) — not re-filed, per
dispatch.

## Stage 2 — code quality

`worktree_terminal.py` reads as a deep module (three-name interface — `CLASSES`/`classify`/
`classify_all` — over enumeration, path-splitting, fleet resolution, landed-blob reads and
classification), consistent with the prior digest's architecture read (L4); did not re-derive that
independently in depth given the time budget and the digest's citation trail already checked out
on spot inspection (`test-worktree-terminal.py:677`'s one private-helper call, `_import_factory_config`,
is a counterfactual-stub test, not a seam violation).

## Not re-raised, per dispatch

- `classify_all` -> `classify` in INV-29 fails SC-04's case (e) alone (mutation-proven).
- INV-30 keyed on status alone passes SC-12 (a), fails (b) (mutation-proven).
- Digest `runs/2026-08-24-03-eng/digest.md`'s seven consolidated findings (D1-D7, L1-L5):
  cited, not repeated, except where noted above (L1 confirmed and extended as F4).

```yaml
VERDICT: FAIL
DIGEST:
  headline: "INV-29's printed removal command is wrong for any short-named worktree (uses the resolved landed feature_id, not the worktree's own path-basename id, for --repo/--id), so feature-worktree.py's own literal-path GATE 1 rejects the exact command the invariant hands the operator — untested because SC-01's message case uses an exact-named worktree and SC-05's short-named case never inspects the command"
  severity_max: high
  findings: 4
  must_fix:
    - "check-state.sh:1320-1328 composes `--id` from `_r29['feature_id']` (the resolved LANDED name) instead of `os.path.basename(_r29['path'])` (the worktree's own directory name, as post-merge-sweep.sh:150 correctly does); for a short-named worktree matching exactly one landed directory (worktree_terminal.py:249,273-277) the two differ and the printed `feature-worktree.py remove --id <landed-name>` fails feature-worktree.py's GATE 1 (dest_for's literal join, feature-worktree.py:56-59,207,211-214) with 'not a linked worktree', exit 3 — REQ-02's 'the exact command that removes it' is violated in exactly the scenario SC-05 clause (c) was added to cover."
  spec_violations:
    - { kind: mismatch, path: .claude/skills/harness/bin/check-state.sh, ref: REQ-02 }
  reviewed: "9165162be80e6b39055cff6b989227ce1b875172..513c4a46e34cbe327d96922c01cebdd18e85d62e"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "F1 (must_fix): confirm the fix is to derive --id from os.path.basename(record['path']) rather than record['feature_id'] in check-state.sh's INV-29, matching post-merge-sweep.sh:150's existing pattern, and add a message-content assertion to test-check-state.py's short-named case (f.3) so this class cannot regress silently again.", blocking: true }
    - { id: Q2, question: "F2 (not must_fix): harness-init/SKILL.md's per-clone step remains prose a reader must interpret, contrary to T-12's own stated instruction to avoid that; test-hooks-install.py works around it with an independent re-implementation of the conditional rather than exercising the documented text. Accept as a known, plan-sanctioned gap, or tighten the prose into an unambiguous script block?", blocking: false }
    - { id: Q3, question: "F3: plan.yaml's T-04 case (f) intent text misdescribes the unresolved predicate (says 'no landed directory' / exempt_absent's condition, should say 'ambiguous prefix, matches more than one'). The shipped code and tests are correct. Worth a plan.yaml correction for future readers, or leave as a known stale label?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/review-harness-code-reviewer-c0.md
```
