# Receipt — dev-ops diagnosis — BUG-1305 (read-only)

## BLUF

**Mode A (clobber), most-probable mechanism, MEDIUM-HIGH confidence:** the #1106/#1124 run-identity
guard compares `str(prior_run_id) != str(new_run_id)` (`check-domain.sh:1567`) and ALLOWS the write
whenever the two strings are equal — but the playbook's own naming rule (`SKILL.md:272-274`,
`<task-or-purpose>-<squad>`) mandates a slug with **no uniqueness enforcement**, and if `run_id` is
seeded from that same slug (the natural implementation; not directly confirmed since the BUG-1286
run dirs are gone), two genuinely different runs choosing the same slug produce string-equal
`run_id`s and the guard treats the second as a legitimate upsert of the first — the exact clobber
symptom. **Named alternative I cannot rule out:** the `_no_parser` fail-open (`check-domain.sh:1475`)
— a bootstrap/no-PyYAML session skips the identity check entirely. Evidence cannot discriminate
between the two; naming both per dispatch instruction, not resolving in my own favour.

**Detection: prevention-only, no detection today.** `check-state.sh`'s INV-15/16 sweep validates a
state.yaml's *own* shape (whitelisted keys, digest existence) but asserts nothing about whether its
`run_id`/content actually belongs to the run that currently occupies the directory. A clobber that
already happened is invisible to every existing invariant.

**Mode B, HIGH confidence:** the digest content-guard (#1058) *is* enforced on the Edit route too —
**`check-domain.sh`'s own inline comment at line 1236-1238 ("intentionally Write/PRE-only… Edit and
Bash carry no complete incoming payload") is STALE and WRONG**, contradicted by its own runtime at
lines 1905-1923 (Edit reconstruction for `RE_RUN_DIGEST`/`RE_STATE_YAML`/`RE_HANDOFF`) and confirmed
by probe below. `bash-write-guard.sh`'s docstring (`:747-748`, "The Write and Edit routes… compare a
proposed write against… PRIOR content") is the one the runtime agrees with. **The un-repairable
digest is better explained by the durable-digest check's own documented fail-open** than by this
guard: `validate-digest.py:check_artifact_file` (`:1496-1500`) validates a lead's *written file* from
the SubagentStop hook, but explicitly fails open — logs and returns 0 — whenever it "cannot be
located or read" (worktree/cwd drift), naming `check-state.sh` INV-15 as "the deterministic backstop
that runs from repo root and cannot be fooled" (`validate-digest.py:1538-1541`). That backstop is
never wired to any hook (`.claude/settings.json` registers no automatic caller for `check-state.sh`;
repo Expertise G-01 already records this as manual-only). Sampling (below) shows the artifact-less
digest population is dominated by **format non-compliance** (never wrote the line at all), not by
truncated/refused repair attempts — so the specific B-11 record is *consistent with* the fail-open
mechanism but not provably caused by it; the file itself is gone (gitignored, worktree removed) so
this cannot be confirmed directly.

---

## A. Run-state clobber — every write route to `state.yaml`

| # | Route | Verdict | Citation / probe |
|---|---|---|---|
| 1 | `Write` | **Refused** on identity mismatch/malformed/missing-run_id prior; allowed as upsert when `run_id`s match | `check-domain.sh:1439-1596` (esp. `:1567` compare) |
| 2 | `Edit` | **Refused**, same identity/shape checks as Write — content is reconstructed from `old_string`/`new_string` against the on-disk prior *before* the identity compare runs | `check-domain.sh:1905-1923` reconstructs; `:1439` re-checks the reconstructed `content`. No separate probe run for state.yaml (digest.md probed instead, same code path) |
| 3 | `NotebookEdit`/`MultiEdit` | **Covered**, not a gap. Settings.json's matcher `"Write\|Edit"` is unanchored; the harness's own tooling models the host's matcher as `re.search` (`merge-settings.py:151-176`, esp. `:176 return bool(rx.search(tool))`) — `re.search("Write\|Edit","NotebookEdit")` matches on the `"Edit"` substring. `check-domain.sh` already branches on `notebook_path` (`:357-358`) and treats `NotebookEdit` as a named-target Edit-like route (`:1930-1932`). `MultiEdit` is not a live Claude Code tool in this install (no references found outside `merge-settings.py`'s `_TOOL_NAMES` set) — moot. **I could not independently verify the host's actual matcher algorithm** (it lives in the Claude Code binary, not this repo) — this conclusion rests on the repo's own tested assumption (`test-merge-settings.py`), not a first-party host spec. Flagged as `open_questions` Q1. |
| 4 | `Bash` (redirect, `python3 -c`, `tee`, `mv`, `cp`) | **Refused, unconditionally, any checkout** | `bash-write-guard.sh:744-767` (`_run_artifact_guard`), matched *before* the DEC-153 worktree carve-out (`:781-786`) via `_worktree_stripped` (`:729-741`) |
| 5 | Write/Edit from **inside a worktree path** | **Not defeated** — `check-domain.sh`'s `_norm` (`:1063-1090`) resolves the path through `harness_boundary.checkout_relative`, stripping the worktree prefix before matching `RE_STATE_YAML`; this is the FEAT-30 T-04 fix, whose own comment (`:1066-1084`) documents the prior bug (a two-level worktree layout matched nothing) as already closed | `check-domain.sh:1063-1090`, `harness_boundary.py:114+` |
| 6 | Payload with **no `agent_type`** | **Still refused** — the domain (who-may-write) phase is skipped (`_domain_phase = _governed and not _post`, `:328`), but the shape/identity phase is **not** gated on `_governed` by explicit design: `"the shape phase runs for EVERY writer including the main session, because the no-agent_type carve-out is the _governed FLAG and not an exit"` | `check-domain.sh:1360-1364` |
| 7 | Session with **no PyYAML importable** | **Allowed (fail-open), by deliberate documented tradeoff** — `if _no_parser: return out` (bare early return, no identity check performed) | `check-domain.sh:1454-1476`, esp. the `1471` comment explaining the tradeoff (earlier detection given up, not correctness — `check-state.sh` catches the shape violation at next entry, but **not** a clobber, since no invariant checks clobber post-hoc) |
| 8 | **Slug reuse** with a genuinely different run whose `run_id` string happens to equal the prior's | **Allowed as upsert** — the only identity check is `str(prior_run_id) != str(new_run_id)` (`:1567`); no check binds `run_id` to anything besides itself (not to a timestamp, PID, or session token). The playbook's `<purpose>-<squad>` naming rule (`SKILL.md:272-274`) is explicitly **not** unique per cycle. **This is the leading Mode-A candidate.** |

**Probe corroborating routes 1/2 (digest.md, same code path as state.yaml's Write/PRE and Edit
reconstruction):** built a synthetic root under `$TMPDIR` (`.agents/skills/harness/bin/` copies of
`check-domain.sh`+`harness_boundary.py`+`harness_yaml.py`, `.harness/team-config.yaml` copied
verbatim from the worktree for a parseable manifest — read-only copy, not a repo write) with a
`.harness/synthproj/features/ZZ-PROBE/runs/probe-run-1-validator/digest.md` prior. Three PreToolUse
payloads run against `bash check-domain.sh`:
- `Write` with content not extending the prior → `exit=2`, `"run digest already holds a recorded
  digest; this Write would replace rather than extend it."`
- `Edit` (`old_string="VERDICT: PASS"`, `new_string="VERDICT: PASS\nartifact: notes/original.md"` —
  an insertion *before* the rest of the file, so the reconstructed content does not start with the
  prior) → **`exit=2`, identical denial message** — proves Edit is content-checked, not route-denied.
- `Edit` (`old_string`=the file's own last line, `new_string`=last line + a genuinely appended line —
  pure append, reconstructed content *does* start with the prior) → **`exit=0`** — a same-run repair
  that only appends (e.g., adding a missing `artifact:` line at the very end) is the one legitimate
  self-repair route that survives the guard.

Synthetic fixture and probe artifacts deleted after use; `$TMPDIR` removed. No `.harness/**/runs/**`
directory outside `$TMPDIR` was touched.

---

## B. False digest-write refusal — characterisation

1. **Same-run correction via Edit:** refused whenever the fix is not a pure append (probe above,
   test 2). Allowed when the fix is a pure append (probe test 3) — inserting a missing `artifact:`
   line **at the end** of the file is therefore an open repair route today; fixing a mistyped
   `VERDICT:` mid-file, or re-ordering/replacing existing lines, is not.
2. **Comment contradiction, resolved by probe:** `check-domain.sh:1236-1238` ("intentionally
   Write/PRE-only") is **the wrong one** — `bash-write-guard.sh:747-748` ("The Write and Edit routes
   in check-domain.sh compare…") is what the runtime does, per probe. Repair routes: **Edit** (open,
   append-only), **a new run directory** (open, always — `state.yaml`'s message and the digest
   guard's both say "write this cycle's [record] into a run directory of its own"), **Bash** (closed,
   unconditionally, `bash-write-guard.sh:744-767`).
3. **Split, with counts and method:** re-derived population (method below) = 38 `digest.md` files
   with no `^artifact:` line, out of 598 digest.md files across 612 run directories. Sampled by
   inspecting line count + presence of a `VERDICT:`-shaped block: **0/38 under 10 lines** (no
   candidate looks truncated by length); **~32/38 carry no `VERDICT:`/`DIGEST:` block at all** —
   these are older-format, prose-only team/squad digests (sampled 4 by hand: FEAT-45, FEAT-08, all
   67-109 lines of complete-looking prose) — i.e., **format non-compliance** ("never wrote the
   line"), not an interrupted repair. Only ~7/38 have a `VERDICT:`-shaped block yet still omit
   `artifact:`. **The specific B-11 record (`2026-09-05-02-validator`) is not in this population — it
   was gitignored and the worktree removed, so it cannot be sampled directly.** I am not claiming
   causation for that specific file; the general population argues for non-compliance as the more
   common explanation, but cannot rule out the fail-open mechanism for that one record.
4. **Durable-digest grading, run against a real example and a synthetic fixture:**
   `python3 .agents/skills/harness/bin/validate-digest.py lead <digest.md>` — run against
   `.harness/harness/features/FEAT-08-remove-cost-tracking/runs/s2-eng/digest.md` (a real,
   pre-existing, un-modified file — read-only):
   ```
   VERDICT: BLOCKED (contract violation)
     - no artifact: path.
   exit=1
   ```
   Re-run against a synthetic `$TMPDIR` fixture missing every field: same `no artifact: path.` plus
   ten more `missing '<field>'` lines, `exit=1`. **This CLI path is never invoked automatically** —
   the automatic check is the SubagentStop hook (`validate-digest.py --hook`, registered in
   `.claude/settings.json:69-78` for matcher `harness-.*`), whose `check_artifact_file` function
   explicitly **fails open, loudly** when the file "cannot be located or read: a hook whose cwd
   drifts (worktrees, unset CLAUDE_PROJECT_DIR) must not block a legitimate lead on our own
   resolution bug" (`validate-digest.py:1496-1500`), and names `check-state.sh` INV-15 as the
   backstop. **`check-state.sh` is registered nowhere in `.claude/settings.json`** — it is
   manual-only (repo Expertise `harness-dev-ops` G-01 already records this).

---

## C. Remedy options (not a recommendation)

**Mode A:**
- *Derive `run_id` from something collision-resistant* (session/PID/monotonic timestamp) instead of
  trusting the author-chosen slug. Surface: `check-domain.sh`'s seed-time convention + whatever seeds
  `state.yaml` first (harness-team skill). Discriminator: `run_id` uniqueness becomes structural, not
  author-discipline. Could be wrong: existing tooling that reads/reports `run_id` as the human-legible
  slug (digests, `check-state.sh` messages) would need updating everywhere it is treated as
  display text. Regression-testable without the real hook: yes — unit-test `run_id` generation in
  isolation.
- *Add post-hoc clobber detection to `check-state.sh`* — e.g. hash the first-write state or track a
  monotonic write counter separately from `run_id`, and flag a directory whose current content
  disagrees with its own history. Surface: new INV in `check-state.sh`. Discriminator: needs a
  side-channel record outside `state.yaml` itself (the clobbered file is definitionally silent about
  its own history). Could be wrong: the side-channel itself becomes another file to keep consistent,
  another spot to be forgotten. Regression-testable without the real hook: yes, pure file-fixture unit
  test.
- *Enforce slug uniqueness at the guard*, refusing a **second** `state.yaml` write under a slug this
  feature has already used with a *different* actual identity signal (e.g. session id in the payload,
  if the host ever supplies one). Surface: `check-domain.sh:1439+`. Discriminator: needs an identity
  signal independent of `run_id` — none currently exists in the hook payload. Could be wrong: no such
  signal may be available from the host at all, making this option currently unimplementable.

**Mode B:**
- *Wire `check-state.sh` (or its INV-15 check alone) into a hook* — e.g. `SubagentStop` for leads, or
  a periodic/`/harness`-entry trigger. Surface: `.claude/settings.json` + extracting INV-15 into a
  standalone callable (it already loads `validate-digest` as a module, `check-state.sh:1406-1421`).
  Discriminator: none needed — it already "cannot be fooled" per its own docstring. Could be wrong:
  cost — INV-15 currently amortizes one Python interpreter over the *whole* run corpus at each
  invocation; running it per-SubagentStop reintroduces the per-spawn cost this file's own comment
  says it eliminated (`:1407-1410`). Regression-testable without the real hook: yes, call the
  extracted function directly against a fixture tree.
- *Make `check_artifact_file`'s fail-open path louder* — currently it's a stderr print with no
  operator-visible durable record; a fail-open occurrence could append a note to a durable log
  instead of only printing to a transient hook stderr stream. Surface: `validate-digest.py:1538-1541`.
  Discriminator: "the path could not be resolved" is already detected, only not persisted. Could be
  wrong: risks becoming exactly the kind of narrative-log noise DEC-145 struck. Regression-testable:
  yes, unit test the new logging call with a mocked unresolvable path.
- **What identity a `digest.md` write carries that could distinguish same-run correction from
  cross-run clobber:** none today beyond the file's own byte-prefix (`#1058`'s compare) — no run id,
  persona, or header is checked against the *directory's* recorded identity the way `state.yaml`'s
  `run_id` is (`check-domain.sh:1499-1507`'s own comment explains this asymmetry: digest is
  legitimately append-only within a run, so a prefix check was chosen over an identity check).
  `validate-digest.py`'s contract (`:1133+`) requires `VERDICT`/`DIGEST:`/`artifact:` fields but none
  of them names the *run*; `harness-team` skill's return template (§10.4, referenced at
  `validate-digest.py:1552-1554`) likewise carries no run identifier field.

---

## D. Deterministic regression cases (proposed, not written)

| Fixture | Invocation | Expected | Suite location |
|---|---|---|---|
| Two `state.yaml` writes, same `run_id` string, different `feature`/`squad`/`host` payload data | `check-domain.sh` PreToolUse Write, second write | Currently: **allowed** (the gap) — a fix should **deny** or otherwise flag | `tests/integration/test-check-domain.py` (existing state.yaml identity cases already live there per the file's naming — `test-check-domain.py:3057+` shows sibling plan.yaml route cases in this file) |
| `state.yaml` Edit reconstructing a mismatched `run_id` (not just Write) | `check-domain.sh` PreToolUse Edit | **Deny**, same message class as Write | `tests/integration/test-check-domain.py` |
| Digest Edit that is a pure append inserting a missing `artifact:` line at file end | `check-domain.sh` PreToolUse Edit | **Allow** (already true today — a regression guard, not a new behavior) | `tests/integration/test-check-domain.py` |
| Lead return whose `artifact:` path cannot be resolved (simulated worktree/cwd drift) reaching `check_artifact_file` | `validate-digest.py --hook`, unresolvable path | **Exit 0, fail-open, with the stderr note naming INV-15 as backstop** (documents existing behavior as a regression guard) | `tests/unit/test-validate-digest.py` (module-level function, no hook end-to-end needed) |
| `check-state.sh` INV-15 given a run dir whose digest lacks `artifact:` | direct script run against fixture `.harness` tree | **Reports the violation** (already true — proves the backstop itself, independent of wiring) | `tests/integration/test-check-state.py` (per this repo's directory-decides-which-script-executes convention; a fixture `.harness` tree plus a full script invocation is integration-shaped, not unit) |

All four are unit-or-integration by the existing directory split; none requires writing a test file
here (dispatch is diagnosis-only).

---

## Re-derived counts (my own, independent of the dispatch's prior figures)

```
RUNDIRS=$( (compgen -G ".harness/*/features/*/runs/*" ; \
            compgen -G ".claude/worktrees/*/*/.harness/*/features/*/runs/*") 2>/dev/null | sort -u )
```
- Glob matches: **614** (2 are `.DS_Store` files, not dirs) → **612 real run directories**
  (dispatch claimed 608 — **disagreement, reported, not resolved in my favour**: 4 more than claimed;
  possibly a different glob base or a run created after the prior measurement).
- `digest.md` files present: **598**; missing a `^artifact:`-anchored line: **38**
  (dispatch claimed 37 — **disagreement of 1**, same caveat).
- `state.yaml` files: **575**; parsed as a dict with a `run_id` disagreeing with its own directory
  name: **0** (dispatch claimed 0 — **matches**).

## git status (verbatim, run at end)

Worktree:
```
?? .harness/harness/features/BUG-1305-run-state-clobber/
```
Main checkout: unchanged from the pre-run baseline I captured at the start of this session (same six
untracked paths plus the one pre-existing modified file under `FEAT-47-tests-layout`, none touched by
me).

## Open questions

- Q1 (non-blocking): whether Claude Code's real PreToolUse matcher uses `re.search` (as this repo's
  own `merge-settings.py` assumes and tests) or a stricter anchor — I could not verify the host's
  actual algorithm from this repo; if it is stricter, route 3 (`NotebookEdit`) is an unguarded gap
  rather than covered.
- Q2 (non-blocking): whether `run_id` is in fact seeded from the directory slug in the live team
  orchestration code path (I inferred this from the naming convention and the identity-compare
  semantics, but did not find the exact seeding call site — the BUG-1286 incident's actual run
  directories are gone, so I cannot confirm this was the mechanism rather than the `_no_parser`
  fail-open).
- Q3 (non-blocking): whether the specific B-11 digest was ever the target of a denied repair attempt,
  versus simply never repaired — unknowable now that the file is gone; the general population sample
  argues for "never repaired" as more common but cannot settle this one instance.
