# Security Review — BUG-276 expertise-merge-duplicate-id — c0

## BLUF
PASS. Genuine but narrow security surface (Tampering on a local memory-integrity guard); the
fix closes it correctly with no new bypass, no partial-write window, and no disclosure issue.
severity_max: info.

## Scope reasoning
This is a local python3 CLI mutating files on disk under `.harness/*/expertise/`, invoked by
other agents (not network-facing, no auth boundary of its own). The relevant trust boundary is
Integrity/Tampering (STRIDE) on the Expertise memory layer: this tool exists specifically to stop
silent loss (DEC-95), so a hole in ITS OWN guard is the live axis, not injection/auth/secrets.
I scoped IN on that axis and checked it concretely rather than declining outright (O-06/O-07).

## What I checked
1. **New guard's call site and ordering** — `_check_proposal_duplicate_ids` (expertise-merge.py:118-131)
   is invoked as the first line of `compute_union` (:144), which itself runs inside
   `cmd_apply`'s `transform` closure (:511-547). `harness_merge.locked_update` (harness_merge.py:121-147,
   unchanged by this diff) calls `transform(base)` **before** any tempfile is created (:143 `mkstemp`
   comes after the `transform` call at :142). So a MergeRefusal(11) raised by the new check aborts
   before any file — temp or final — is touched: no half-written artifact, no window, confirmed by
   reading the exact statement order, not inferred from the docstring alone.
2. **Absent-destination path** (`base_bytes=None`) — `cmd_apply`'s `transform` builds `base_sections={}`
   in that branch (:513-515) and still calls `compute_union` unconditionally, so the guard fires
   identically whether the destination file pre-exists or not — matches integration case
   `case_duplicate_proposal_ids` (c) which exercises exactly this (`tests/integration/test-expertise-merge.py`,
   new case 27).
3. **Guard-bypass-by-normalization concern** — traced the equality used by the new check
   (`eid in seen`, a plain Python string `set`, expertise-merge.py:128) against the equality used
   everywhere else duplicate/ambiguous ids are judged in this file: `_check_base_ambiguity`
   (`_base_matches`, string `==`), `compute_union`'s pre-existing base/prop merge (`dict` keyed by
   the same raw string), and `_check_proposal_ambiguity` (`(section, target)` tuple in a `set`).
   All of them key off the exact strings `SECTION_RE`/`ENTRY_RE` capture (`\w+` for section,
   `[A-Za-z]{1,3}-\d+` for id) with no `.lower()`/`.strip()`/normalization anywhere in the module.
   The new guard uses the identical equality semantics as the rest of the file, so there is no NEW
   asymmetry (e.g. `P-01` vs `p-01`, or trailing-whitespace-in-id) it could be fooled by that the
   pre-existing checks were not already equally exposed to. Not a finding — consistent trust model,
   not a regression.
4. **Message content / disclosure** — the AMBIGUOUS TARGET line (expertise-merge.py:124-126) echoes
   only `section` and `id`, both already constrained to `\w+` / `[A-Za-z]{1,3}-\d+` by the parser
   before they ever reach this code; it never echoes the duplicated entry's free-text body. Printed
   to stdout (cmd_apply) — a local CLI's own stderr/stdout, not a network response — so there is no
   secret/content-disclosure vector here, and nothing broader than what the pre-existing CONFLICT
   message (exit 7, unchanged) already prints (which does include entry text, but that path is out
   of this diff).
5. **DoS/resource exhaustion** — the new check is a single pass per section building one `set`,
   O(n) in entry count; no nested loop, no regex backtracking hazard beyond the pre-existing
   `SECTION_RE`/`ENTRY_RE`, both anchored and linear. `--entries -` reads all of stdin into memory
   (pre-existing, unchanged), bounded only by process memory — not a new DoS surface introduced by
   this diff.
6. **Path/destination handling** — untouched by this diff. `require_expertise_destination` /
   `harness_merge.require_destination` (realpath-resolved tail match) is pre-existing code this
   diff does not modify; not re-audited here beyond confirming the diff doesn't touch it.

## Findings
None at info-or-above requiring a fix. This diff is a net integrity improvement: it closes a
first-wins ambiguity window (BUG-276) that previously let a proposal silently apply garbage state
with no test coverage. Tests (`test-expertise-ops.py` case u23, `test-expertise-merge.py` case 27
a/b/c) exercise both same-text and different-text duplicate ids, and both existing- and
absent-destination paths — matches what I'd want to see for an integrity guard.

## Threat model
- boundary: proposal (stdin `--entries`) → merged Expertise file write. stride: Tampering.
  mitigated: true (this diff's own fix; verified above, not merely read).
- boundary: refusal path → partial/half-written file. stride: Tampering/DoS-adjacent.
  mitigated: true (transform-before-mkstemp ordering in harness_merge.py, pre-existing,
  confirmed by reading `locked_update`).
- boundary: refusal message → stdout/stderr content disclosure. stride: Information disclosure.
  mitigated: true (message fields are regex-constrained, never carry entry text).

## Not re-litigated
D-07 (silent-drop in parse/render), D-09 (no exit-11 doc row in harness-distill SKILL.md), D-04
(check-expertise.sh untouched), D-05 (exit codes 10/12 absent from docstring), case27b — all
signed dead ends, out of scope, not raised here.

## Open questions
None blocking.
