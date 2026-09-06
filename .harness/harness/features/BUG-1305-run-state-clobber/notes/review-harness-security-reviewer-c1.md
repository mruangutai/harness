# Security review — BUG-1305-run-state-clobber — c1 — pinned `dc0e0313`

## BLUF

One HIGH finding, measured and reproduced live against the pinned code: **a directory-level Bash
`rm -rf` or `mv` targeting the run directory itself destroys or relocates the write-once witness
`.run-identity.json` (and `state.yaml`/`digest.md` beside it) with zero refusal from any guard.**
All four file-level routes SC-13 actually pins (Bash write, Bash removal-by-name, Write, Edit — all
of the *filename* `.run-identity.json`) are correctly closed; I verified each. The gap is a route
SC-13's four cases never enumerate: a directory-level operation whose target string never contains
the protected basename at all. This is not a new mechanism — it is the same pre-existing gap that
already lets `state.yaml`/`digest.md` be destroyed this way — but this diff is the one that promises
the witness "is protected like the checkpoint it witnesses… on the same three surfaces" and is
"never rewritten or removed", and that promise is false for this route. No injection, YAML-load,
secret-exposure, or shell-interpolation defect found elsewhere in the diff.

## Scope

In scope: `.claude/skills/harness/bin/{run_identity.py (new), check-domain.sh, bash-write-guard.sh,
check-state.sh, harness_boundary.py, validate-digest.py}`. `.claude/skills/harness-team/SKILL.md` and
the touched test files carry no security surface (doctrine text / test fixtures) — read, not audited
further. Confirmed the file set with `git diff --name-status origin/main...dc0e0313`; no file present
in the diff falls outside the dispatch's named list.

## Method

All file content read via `git show dc0e0313:<path>`, never the working tree. Behavioral claims below
were **executed**, not inferred: `.claude/skills/harness/bin/{bash-write-guard.sh,check-domain.sh,
harness_boundary.py,run_identity.py,check-state.sh,validate-digest.py}` in this worktree are
byte-identical to the pinned blobs (`diff <(git show dc0e0313:<path>) <path>`, all six empty) — that
was verified before any test execution, so running the working copy is running the pinned commit.
I fed crafted PreToolUse payloads to `bash-write-guard.sh` on stdin; the script only parses the
payload string and never executes the modeled command, so no repository state was touched.

## Findings

### SEC-01 (high) — directory-level Bash rm/mv on a run directory bypasses every witness/checkpoint guard

**Where:** `.claude/skills/harness/bin/bash-write-guard.sh`, the `for name, paths in findings:` loop
(:~875) and `_run_artifact_guard` (:784-800 at the pin) — the guard only matches an *exact basename*
(`RE_RUN_IDENTITY`, `RE_RUN_DIGEST`, `RE_STATE_YAML`, all anchored `...runs/[^/]+/<name>$`). `rm`'s
own target-extraction (`trailing_files`) and `mv`'s (`trailing_files(args)[-1:]`) report whatever
path was actually typed; a directory has no basename match against any of the three patterns, so
`_run_artifact_guard` returns silently and the write proceeds to `harness_boundary.classify`, which
judges only "is this path in my domain" — true for any agent whose domain includes
`.harness/*/features/**` (every orchestrator and lead is granted exactly this, per
`.harness/team-config.yaml`) — with no distinction between "delete a file" and "delete a directory."

**Reproduced (payload piped to the pinned, verified-identical script, no file touched):**
```
{"agent_type":"harness-orchestrator","harness_feature":"BUG-1305-run-state-clobber",
 "tool_input":{"command":"rm -rf .harness/harness/features/BUG-1305-run-state-clobber/runs/simplify-eng"}}
→ exit 0, no stderr
```
Same result for `mv <run-dir> <run-dir>-old` (exit 0, no stderr). Control cases, same script, same
session, prove the mechanism is live and not a fluke: a *file-level* `rm` of `.run-identity.json` →
exit 2 named-witness refusal; a *file-level* `rm` of `state.yaml` → exit 2 digest/state refusal; an
out-of-domain `rm` of `src/whatever.py` → exit 2 domain refusal. Alternate-case
`.RUN-IDENTITY.JSON` (darwin case-insensitive-filesystem spelling) is also correctly refused — that
specific bypass is closed by the `re.IGNORECASE` flag on `RE_RUN_IDENTITY`.

**Attacker scenario:** any harness agent holding an ordinary write grant on a feature (an
orchestrator or lead is enough — this is not a privilege-escalation, it is the ordinary domain every
orchestrator already carries for `.harness/*/features/**`) issues `rm -rf` or `mv` on a *sibling run
directory under the same feature* — plausible as routine "clean up an old run" tidying, or as a
confused/prompt-injected agent — and destroys or relocates another run's `state.yaml`, `digest.md`
**and** the witness that REQ-02's whole detection design depends on, in one call, with no stderr, no
exit-2, and nothing left for `check-state.sh`'s new INV-36 to report (the directory is gone; INV-36
only judges directories that still exist). This is the exact Mode-A harm BUG-1305 was opened for —
one run's durable record destroyed by another write — reached by a route neither REQ-01/REQ-02 nor
SC-13's four named cases (Bash write-to-name, Bash removal-by-name, Write, Edit) considered, because
all four are keyed on the file's own basename appearing literally in the command.

**Not the already-accepted residual:** the shared context's signed residual list covers a foreign run
that *copies* the witness's `run_uid` into its own checkpoint (forgery, still leaves a record behind)
and the first-write legacy window (no witness minted yet). Neither describes outright directory
deletion of an *already-witnessed* run's entire record with nothing surviving to inspect. This is a
distinct mechanism.

**Pre-existing, not a regression — reproducible from the diff alone, no need to run the pre-change
copy:** the diff never touches the `for name, paths in findings:` loop, `trailing_files`'s `rm`/`mv`
handling, or `harness_boundary.classify`. `state.yaml` and `digest.md` were exposed to the identical
directory-level bypass before this feature; this diff extends the *same* unprotected shape to the new
witness rather than closing it. What makes it this feature's finding rather than a pure backlog note:
REQ-02's entire value proposition — "the witness… needs no memory of the incident" — is void wherever
this route is used, and SC-13's own text claims the witness is "protected… on the same three surfaces
that already protect `state.yaml`" as if that were sufficient; it silently inherits every gap those
two files already had.

**Remedy:** `_run_artifact_guard` (and/or `harness_boundary.classify`) needs a directory-shaped rule:
refuse an `rm`/`rmdir`/`mv`-source whose target, once trailing-slash-normalized, is a run directory
itself (`^\.harness/[^/]+/features/[^/]+/runs/[^/]+/?$`) or any ancestor of one, mirroring the
existing basename patterns but matching the *directory*, not the file. This is a real code change
across `bash-write-guard.sh` (new pattern + a "does this path recurse into a run dir" check ahead of
`classify`) and its test suite (`tests/**/test-bash-write-guard.py`) — not a comment fix, not a
one-liner, and not something to slip in as a drive-by edit under DEC-174's main-session-direct rule
without its own task and tests.

**Ship ruling:** this can be ruled at ship **only if the operator explicitly accepts it as a named
residual**, the same way REQ-01 names its "foreign run copies the run_uid" residual in prose the
operator signed. It should not ship silently: SC-13's and REQ-02's language ("protected… on the same
three surfaces", "needs no memory of the incident") reads as a stronger guarantee than the code
delivers, and a future reader citing SC-13 as proof the witness cannot be destroyed would be relying
on a false premise. If the operator does not want to carry that residual, it is a genuine follow-up
task, not something fixable by a code comment at this pin.

## Findings considered and dismissed

- **YAML deserialization of an attacker-controlled prior `state.yaml`:** `harness_yaml.load_str` uses
  a `_StrictSafeLoader` subclassing `yaml.CSafeLoader`/`yaml.SafeLoader` — no `yaml.load`/`FullLoader`/
  `UnsafeLoader` anywhere in the touched files. No object-construction RCE surface. Dismissed.
- **Shell injection via `run_id`/`feature`/`squad`/`host`/`run_uid`:** every `subprocess.run` call in
  the five touched scripts uses list-form argv with fixed or git-controlled arguments (`git -C
  <root> ...`); none of the seed fields or the minted `run_uid` reach a shell string or an argv
  built from user-authored content. `run_identity.py`'s `conflict`/`uid_conflict` only format these
  values into Python f-strings for stderr text (`{value!r}`), never into a command. Dismissed.
- **`check_artifact_file`'s new candidate-root path join (`validate-digest.py:_durable_artifact_candidates`):**
  a lead's own `artifact:` line is joined, unsanitized, against up to three roots (feature root, owner
  root, and a new `_script_checkout_root()`), so a `../`-laden `artifact:` value can walk outside all
  three. This exact join-without-sanitization shape (`os.path.join(base, path)`, `os.path.isabs(path)`
  short-circuiting to an absolute read) is unchanged from the pre-diff code — the diff only added the
  third candidate root and turned "not found" from fail-open (`return 0`) to fail-closed (`return 2`)
  **once a candidate run directory already resolves**. The new fail-closed branch cannot be reached by
  a bogus traversal path (its dirname won't exist under any of the three roots), so the diff does not
  worsen reachability of the traversal; it is still gated on `norm(agent) == "lead"`, i.e. it can only
  affect a lead's own SubagentStop validation of its own claimed artifact, not another agent's file.
  Rated info, pre-existing, and not this feature's to fix. Recorded rather than dropped in case a
  later reviewer re-raises it.
- **`record_seed`'s check-then-write (`os.path.exists` then `os.replace`) is not atomically
  write-once:** true, but the only window in which two writers can race it is the first-landing window
  before any witness exists — which is precisely the already-disclosed, operator-signed "first-write
  window" residual (constraint list item 4). Not a new finding.
- **Shape-phase `RE_RUN_IDENTITY` fails open to an unmatchable regex if `harness_boundary` fails to
  import:** deliberate and consistent with the pre-existing pattern for every other shape pattern in
  this file (documented in-file: "shape phase's import… must stay ABSORBING… governed domain writes
  still fail closed on the same missing module in `_run_domain`"). Not new, not this diff's call to
  reverse. Dismissed.
- **Refusal message content:** every new refusal names the disagreeing field, the recorded value, or
  the exact path to act on, and nothing more (no session ids, no credentials, no unrelated file
  contents). Judged adequate.

## Threat model

| boundary | STRIDE | mitigated |
|---|---|---|
| Bash write/removal of `.run-identity.json` by basename | T (Tampering) | true |
| Write/Edit of `.run-identity.json` by basename, any content | T | true |
| Edit reconstruction ambiguity (old_string absent/non-unique) on the witness | T | true (Edit tool's own match-uniqueness refuses it; pre-existing mechanism, same as state.yaml/digest.md) |
| darwin case-insensitive alternate spelling of the witness | T | true |
| Bash directory-level rm/mv reaching the witness without naming it | T, R (Repudiation — the forensic trail itself is destroyed) | **false** — SEC-01 |
| Attacker-controlled prior `state.yaml` parsed via `harness_yaml.load_str` | T (malicious YAML) | true (safe loader only) |
| Seed fields / run_uid interpolated into a shell or subprocess call | I/E | true (no such sink found) |
| Lead's own `artifact:` claim path traversal in validate-digest.py | I (info disclosure of an out-of-tree file's structural errors) | true — pre-existing, unchanged reachability, scoped to the lead's own claim |

## Open questions

- None blocking. SEC-01's ship-ruling is stated above as an explicit operator decision, not a
  question needing an answer before this note can close.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Directory-level Bash rm/mv on a run directory bypasses every witness/checkpoint guard (SEC-01, high) — reproduced live; everything else audited is closed or pre-existing/dismissed."
  in_scope: true
  scope_reason: "Diff adds security guard scripts (write-once witness, refusal ladders) whose entire purpose is preventing tampering with another run's durable record — squarely Tampering/Repudiation STRIDE surface even with no network exposure."
  severity_max: high
  findings: 1
  must_fix: ["SEC-01: directory-level Bash rm/mv reaching the run directory bypasses the witness/checkpoint guards entirely (bash-write-guard.sh _run_artifact_guard + harness_boundary.classify); requires a directory-shaped pattern, not a comment fix — ship only with explicit operator acceptance as a named residual, or a follow-up task."]
  threat_model:
    - { boundary: "Bash write/removal of .run-identity.json by basename", stride: "T", mitigated: true }
    - { boundary: "Write/Edit of .run-identity.json by basename", stride: "T", mitigated: true }
    - { boundary: "Edit reconstruction ambiguity on the witness", stride: "T", mitigated: true }
    - { boundary: "darwin case-insensitive alternate spelling of witness path", stride: "T", mitigated: true }
    - { boundary: "Bash directory-level rm/mv reaching the witness without naming it", stride: "T,R", mitigated: false }
    - { boundary: "attacker-controlled prior state.yaml parsed via harness_yaml.load_str", stride: "T", mitigated: true }
    - { boundary: "seed fields / run_uid interpolated into shell or subprocess", stride: "I,E", mitigated: true }
    - { boundary: "lead's own artifact: claim path traversal in validate-digest.py", stride: "I", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1305-run-state-clobber/.harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-security-reviewer-c1.md
```
