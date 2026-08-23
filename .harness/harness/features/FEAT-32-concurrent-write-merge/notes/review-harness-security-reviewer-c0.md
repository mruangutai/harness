# Security review — FEAT-32, review_sha 5107efb (base 12c66b3)

## BLUF

The headline exploit goal — get an approval signature onto disk as a governed agent, without the
main session — **did not succeed against any payload I could construct**, including every attack
shape named in the dispatch. D-10's two-limb Edit guard and the load-bearing
`main_session.writes` record held. No governed agent can write or edit `.harness/team-config.yaml`
itself (tested all 16 personas × Write/Edit). The registry-fuzzing surface (dispatch-guard.sh /
validate-digest.py / inflight_registry.py) fails open loudly on every corrupt input I fed it,
matching its documented D-07/D-09 posture, with one real but low-severity gap: a poisoned
`started_at` in the future creates a **permanent** single-flight block with no auto-heal. Two
further info-level hardening notes on `harness_merge.py`'s lock/tempfile handling. Nothing here
rises to must-fix.

## 1. The approval-forgery attack (D-10, the headline)

Built a live fixture harness (`_approval_root`/`_fire_edit`/`_fire_write`, mirroring
`test-check-domain.py`'s T-14 fixtures) and ran the real `check-domain.sh` as `harness-pm` and
`harness-orchestrator`. Every payload below was **denied, exit 2**, with stderr naming the
fragment (`check-domain.sh:508` `approval_guard`, `check-domain.sh:409` `_approval_entries`,
`:462` `_yaml_key_range`, `:475` `_heading_range`, `:552` Edit branch Limb A, `:611` Limb B):

- Boundary-spanning `old_string` (starts in the blank line *before* `approval:`, ends inside
  `status: pending`, deliberately outside `on_disk_block` so Limb A's substring test can't see
  it) — denied by **Limb B**: any `new_string` that still leaves `approval:` recognizable to a
  YAML reader necessarily contains a line that starts with the literal `approval:`/`## Approval`,
  which Limb B checks independent of position in the file. Confirmed this is structural, not
  incidental: I could not construct a resulting-valid-document edit where the key survives but
  neither limb fires.
- Second/duplicate `approval:` block injected far from the tracked range (after the last task) —
  denied (Limb B is position-independent).
- Empty `old_string` with an injecting `new_string` — denied (Limb B still fires).
- CRLF-normalized on-disk file, plain `status:` edit — denied (Limb A, text-based, is
  line-ending agnostic).
- `..`-traversal path and a differently-named symlink pointing at the same `plan.yaml` — both
  resolve via `harness_boundary.real()` to the canonical path and are denied identically to the
  direct path.
- `## Approval` heading boundary-span and a heading-level shift (`## Approval` → `### Approval`)
  on BRIEF.md — both denied.
- `replace_all` sweep, mid-line-start evasion, block-introduction at column zero — the plan's own
  5a–5e cases; re-ran the full suite (`test-check-domain.py`): **28/28 pass**, including case 9
  (dropping the `main_session.writes` entry stops the denial — the record is genuinely
  load-bearing) and case 14 (asserted against the **real** `.harness/team-config.yaml`, not a
  fixture).

**One un-demonstrated residual, named as a hypothesis, not a finding:** neither limb parses YAML
merge keys/anchors. If an `approval:` mapping were ever written as `<<: *ref` with `ref` defined
outside the tracked block range, editing the anchor's definition would change the resolved value
without a line starting with `approval:` ever appearing in the edit. No template or existing
plan.yaml in this repo writes approval this way, so this is reachability-closed today — see
open_questions Q1.

## 2. Who may edit team-config.yaml (D-10's own residual)

Ran `check-domain.sh --resolve .harness/team-config.yaml` → `NOBODY`. Then fired real Write **and**
Edit payloads at `.harness/team-config.yaml` as all 16 rostered personas
(`harness-orchestrator` … `harness-validator-lead`) — **every one exits 2** with "may not write
.harness/team-config.yaml" (`check-domain.sh` domain_check, not the approval_guard). No governed
agent can disarm the load-bearing record through the guarded Write/Edit path. The only remaining
route is #627 (bash-write-guard's allow-by-omission for a `python3` CLI invocation), which is
explicitly out of scope by D-08 and whose own destination refusal is the accepted mitigation — not
re-filed.

## 3. Registry fuzzing (dispatch-guard.sh / validate-digest.py / inflight_registry.py)

Fed `.harness/.inflight-claims.json` truncated/corrupt JSON, a non-dict top level, a non-list
claim value (string and dict), a non-numeric `started_at`, a directory at the registry path, an
unwritable `.harness/` dir, a symlink at the registry path, a 5.8 MB / 100k-entry file, and a
persona name containing backticks/shell metacharacters — through the **real** `dispatch-guard.sh`.
Every case is caught by the try/except at `dispatch-guard.sh`'s claim block and **exits 0** with a
named-exception stderr line ("claim step failed (...) — passing through, the dispatch is NOT
blocked"), matching D-07's fail-open-but-loud posture exactly. No shell/eval/format-string
interpolation anywhere in these three files (grepped). Persona name with backticks lands inertly
as a JSON string key — no execution. The symlink case: confirmed `os.replace()` replaces the
symlink's own directory entry rather than following it — after the run the registry path holds a
regular file with the claim, and the symlinked-to file is untouched.

**One real, low-severity gap:** `inflight_registry._expire` computes `now - started_at > TTL`, so
a claim with `started_at` set far in the future (e.g. year 5138) never expires. Demonstrated:
registry `{"harness-pm": [{"started_at": 99999999999.0, ...}]}` → `dispatch-guard.sh` exits **2**,
"BLOCKED - single-flight (harness-pm)", indefinitely — every future `harness-pm` dispatch from
that checkout is refused until an operator manually runs `release-all` (named in the refusal) or
hand-edits the file. Since a persona's own claim-write already goes through this same code path
(`inflight_registry.claim`), this is reachable by an ordinary bug (bad system clock, clock skew)
as well as deliberately. Rated low, not med/high: it requires the write capability the dispatch
already grants every governed agent by design (Bash), and the guard's own error message names the
recovery command. See open_questions Q2.

## 4. harness_merge.py — lock and atomic-replace

- **Atomicity / no orphaned tempfile**: `locked_update` writes to a `tempfile.mkstemp()` sibling
  and `os.replace()`s it onto the destination; a `BaseException` during write/replace removes the
  tempfile in a `finally`-equivalent (`harness_merge.py:139`). `transform()` (where a
  `MergeRefusal` is raised) runs *before* the tempfile is created, so a refusal never touches disk.
  Confirmed by reading; matches the docstring's claim.
- **Permission mode**: demonstrated live — `mkstemp` creates its file at `0600`; `os.replace`
  swaps the inode, so the *first* write through this core to a file that previously had broader
  permissions (e.g. `0664`) **silently narrows it to `0600`**. Direction is fail-safe (narrows,
  never broadens access), so this is not a disclosure — flagged info-level only. See
  open_questions Q3.
- **Lock-file symlink**: `_acquire_flock` opens `<path>.lock` with plain `O_CREAT|O_RDWR`, no
  `O_NOFOLLOW`. An actor who already has write access to the same directory (baseline capability
  for any governed agent inside `.harness/`) could alias two files' locks via a symlink, causing
  cross-file lock contention/timeouts (`MergeRefusal(6)`) between unrelated merges — never
  corruption, since no bytes are ever written to the lock fd and the actual content write goes
  through `os.replace(tmp_path, path)`, which replaces `path`'s own directory entry regardless of
  what it points to. Info/low: same-privilege actor, worst case is a transient timeout.
- **TOCTOU on `require_destination`**: its `realpath` check happens once, then the *resolved*
  path (not the raw argument) is what's passed into `locked_update` (confirmed in
  `plan-merge.py:342`), and the eventual write is via `os.replace` on that resolved path — which
  never re-resolves or follows a symlink placed there afterward. No redirection window found.

## 5. Root-probe regression (the old `.harness`-directory bug)

Grepped all eight in-scope files for a directory-based `.harness` existence check. Both
`dispatch-guard.sh`'s and `validate-digest.py`'s root walks explicitly check
`os.path.isfile(.../.harness/team-config.yaml)` — the FILE, not the directory — each with an
inline comment citing the prior $HOME-resolution defect by name. No regression.

## 6. Data exposure

Every new stderr/stdout line added by this diff was inspected. Refusal messages print loaded
approval-mapping values (status/approved_by/date), glob strings, and file paths — no credentials,
tokens, or unrelated file content. Absolute paths do include the local username as an incidental
path segment; this is a pre-existing pattern in `check-domain.sh` (not introduced by this diff)
and stays inside the acting agent's own session, never a shared artifact. Not a finding.

## Findings summary

| # | Where | STRIDE | Severity | Status |
|---|---|---|---|---|
| 1 | `inflight_registry.py` `_expire` (no bound on `started_at`) | DoS | low | demonstrated |
| 2 | `harness_merge.py` `locked_update` (mkstemp mode 0600) | (info, fail-safe direction) | info | demonstrated |
| 3 | `harness_merge.py` `_acquire_flock` (no O_NOFOLLOW on `.lock`) | DoS (cross-file lock alias) | info | reasoned + partially tested |
| 4 | D-10 approval guard, all limbs | Tampering/EoP | — | **held**, no finding |
| 5 | `.harness/team-config.yaml` self-disarm | EoP | — | **held**, no finding |

## must_fix

None.

## open_questions

- Q1 (non-blocking): should a template lint reject YAML anchors/merge keys (`<<`, `&`, `*`) inside
  the `approval:` mapping, foreclosing the one un-demonstrated theoretical evasion of the D-10 Edit
  guard named in §1?
- Q2 (non-blocking): should `inflight_registry.py` clamp or reject a `started_at` greater than
  `now` (+ small clock-skew allowance), so one bad write can't create a claim that never expires?
- Q3 (non-blocking): should `harness_merge.locked_update` preserve the destination's existing file
  mode across the mkstemp/os.replace cycle, given it currently silently narrows it to 0600 on
  first touch?

## Files read (no source edits made)

`.claude/skills/harness/bin/check-domain.sh`, `dispatch-guard.sh`, `validate-digest.py`,
`harness_merge.py`, `inflight_registry.py`, `plan-merge.py`, `.harness/team-config.yaml`,
`.harness/harness.json`, `.gitignore` (no gitignore-relevant surface in this diff),
`.harness/harness/features/FEAT-32-concurrent-write-merge/plan.yaml` (D-04, D-10),
`.claude/skills/harness/bin/test-check-domain.py` (T-14 fixtures, reused for live payloads).
