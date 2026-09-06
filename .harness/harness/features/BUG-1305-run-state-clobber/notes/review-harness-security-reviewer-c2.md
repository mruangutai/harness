# Security countersign — BUG-1305-run-state-clobber — c2 — pinned `e77b30ca`

## BLUF

**The recorded residual is accurate and complete. No understatement found.** The four axes below are
answered against the exact paragraph in `BRIEF.md` REQ-02 headed "ACCEPTED RESIDUAL — directory-level
removal (issue #1376)", read at the pin. I am countersigning, not re-litigating: this is my own
cycle-1 finding (SEC-01) being checked against what was actually recorded and against the one code
change in this delta relevant to my surface. Nothing here reopens `must_fix`.

## Method

All content read via `git show e77b30ca:<path>` or `git diff dc0e0313 e77b30ca -- <path>`, never the
working tree, per constraint. The one glob/dotfile behavior claim in axis 1 was confirmed with a
throwaway `bash -c` probe against `/tmp` (outside the repo, outside any guarded domain — this agent's
own bash-write-guard denies writes anywhere under the repo, confirmed live when I first tried the
probe against a repo-relative path and got refused, which is itself a small piece of corroborating
evidence that the guard's write-domain check is unconditionally active for this role).

## Axis 1 — Mechanism and blast radius

The recorded mechanism is accurate: `bash-write-guard.sh`'s `_run_artifact_guard` (unchanged at this
pin, confirmed by diff below) matches only an exact basename against `RE_RUN_IDENTITY`/`RE_RUN_DIGEST`/
`RE_STATE_YAML`; a directory-level `rm -rf <run-dir>` or `mv <run-dir> <dest>` never presents a
matching basename, so the guard is silent and all three files travel with the directory. The
enumerated blast radius (`state.yaml`, `digest.md`, `.run-identity.json`) is correct for the two
literal forms named (`rm`, `mv`) applied to the whole directory — this is exactly what my cycle-1
reproduction fired (`rm -rf .../runs/simplify-eng`, exit 0, all three destroyed together).

One sub-case worth naming but NOT an understatement: `rm -rf <run-dir>/*` (wildcard-of-contents rather
than the directory itself) does NOT reach `.run-identity.json` under default bash glob rules — `*`
does not match a dotfile unless `dotglob` is set (confirmed live: `globtest/*` expanded to
`normal.txt` only, never `.witness`, in an unrelated `/tmp` probe). That variant destroys `state.yaml`
and `digest.md` while leaving the witness intact — a *milder* outcome than the paragraph's worst case,
not a worse one, and it is still caught by the same "narrow rm/mv matching would still miss other
filesystem deletion routes" concession already in the text (a wildcard target is just another shape
the basename matcher doesn't recognize). It does not change blast radius upward and does not belong in
`must_fix`; recorded under "Noticed" below.

## Axis 2 — Routes

"Bash-only" is correct, and necessarily so: `rm`/`mv` are shell commands, and no other governed tool
(Write, Edit, NotebookEdit) accepts a directory as its target — those tools write named files, not
directory trees, so there is no non-Bash governed route that reaches a whole-directory removal. The
concession that narrow `rm`/`mv` matching "would still miss other filesystem deletion routes" is
adequate as stated: it correctly scopes the open question to *other shapes of the same Bash mechanism*
(e.g. `rsync --delete`, `find -delete`, a wildcard as above), not to a different tool. I found no
governed non-Bash route into directory-level destruction.

## Axis 3 — Pre-existing-ness

Verified unchanged at the pin, not merely asserted. `git diff dc0e0313 e77b30ca` on
`bash-write-guard.sh` touches only the docstring and the `deny()` message string inside
`_run_artifact_guard`; the `if harness_boundary.RE_RUN_IDENTITY.match(rel): deny(...)` condition and
every other regex branch are byte-identical to the cycle-1 pin. The directory-level bypass is exactly
as reachable, on exactly the same three files, as it was for `state.yaml`/`digest.md` alone before
this feature — this feature extends the *same* unprotected shape to the new witness rather than
altering it.

Does the record convey the Repudiation angle my cycle-1 note flagged? The ACCEPTED RESIDUAL paragraph,
read in complete isolation, states *mechanism* (which three files, by which two commands, without
naming a protected path) but does not itself restate *why* losing the witness is worse than ordinary
data loss. That restatement is not missing from the document, though: it is the immediately preceding
sibling bullet in the same REQ-02 section, "The witness is protected like the checkpoint it
witnesses," which says explicitly that a destructible witness "would turn an accepted UNDETECTED
clobber into an UNDETECTABLE one with the forensic trail erased" — the exact consequence, in the exact
words. The two bullets sit adjacent in one continuous requirement, and a reader who reads REQ-02 in
document order gets the full picture without inference. I judge this adequate: a BRIEF is read as a
requirement, not atomized into a single bolded sub-bullet cited out of its own section. This is not an
enlargement and not an omission — it is a reasonable choice not to repeat, three sentences later, a
consequence the paragraph immediately above it already states.

## Axis 4 — Understatement test

If an operator read *only* the ACCEPTED RESIDUAL paragraph (skipping its own immediately preceding
sibling bullet), they would correctly learn that a directory-level `rm`/`mv` defeats the guard and
names the affected files — they would not, from that one paragraph alone, learn *why* that specifically
matters more than ordinary data loss. But nothing downstream of this paragraph asserts or implies the
witness is otherwise indestructible, and the paragraph's own closing sentence ("This acceptance does
not claim the witness is indestructible") forecloses exactly that misreading. **Answer: nothing.** An
operator reading the paragraph in the context it was written in (as REQ-02's second sub-bullet,
directly under the sentence that states the consequence) would not wrongly believe anything is safe
that is not. The record is accurate and complete.

## Verify the F-04 fix did not move my surface

Confirmed. The only change relevant to any route I audited in cycle 1 is in `check-domain.sh`'s PRE
branch (`check-domain.sh:2039-2046` at the pin): an `Edit` whose target matches `RE_RUN_IDENTITY` is
now denied by path alone, ahead of and independent from `_edit_reconstructed_content` — closing the
cycle-1 F-04 gap where a nonexistent target caused `_edit_reconstructed_content` to return `None` via
its `except OSError: return None` branch and fall through to `sys.exit(0)`. This is a strict narrowing
of what is *permitted* (an Edit that creates the witness now exits 2, where it exited 0 before) and
touches nothing my SEC-01 finding depends on: `_run_artifact_guard` in `bash-write-guard.sh`, the
directory-vs-basename matching that produces SEC-01, and `check-domain.sh`'s unconditional
`if RE_RUN_IDENTITY.match(rel): deny(...)` reporting branch (`check-domain.sh:1318`, unchanged) are
untouched by this diff. Confirmed by test: `tests/integration/test-check-domain.py`'s new
`create_edit` case in `_bug1305_marker_file_protection` asserts `returncode == 2` for exactly the
create-via-Edit case that previously exited 0 (diff shown, not re-executed — the dispatch's provenance
list already reports this test green in the delivered suite run). No refusal I audited in cycle 1 was
weakened; the F-04 fix widened nothing SEC-01 touches and narrowed nothing else in scope here.

## Noticed, out of this dispatch's scope

- The `rm -rf <dir>/*` dotglob asymmetry from axis 1: worth a one-line addition to issue #1376's own
  scope note when that issue is worked (it changes which of the three files survive a "clean up the
  old run" style command, not whether the directory-level bypass exists), but it is not a defect in
  the accepted residual as recorded and I am not proposing BRIEF text for it.

## Remedy

None. Nothing in the record understates the exposure; no proposed text follows.

## Threat model (countersign scope only)

| boundary | STRIDE | mitigated |
|---|---|---|
| Directory-level Bash rm/mv reaching the witness without naming it (SEC-01) | T,R | false — accepted residual, issue #1376, unchanged at this pin |
| Edit creating `.run-identity.json` where none exists (F-04) | T | true — fixed this delta, verified by diff + test |
| BRIEF's ACCEPTED RESIDUAL paragraph vs. actual measured mechanism | (documentation accuracy, not STRIDE) | true — accurate and complete in its own section context |

## `git status --porcelain`

```
(no output — clean before this write)
```

## What my verdict does NOT license

This countersign does not re-clear SEC-01 for ship on its own, does not certify that issue #1376 is
unnecessary, and does not certify anything about the *other* three panel readers' surfaces (F-04's
full Edit-route behavior beyond the one path I checked, SC-13's QA evidence, or code quality). It
certifies exactly one thing: the accepted-residual paragraph, as written, does not hide a larger
exposure than what cycle-1 already measured and what the operator already signed.

```yaml
VERDICT: PASS
DIGEST:
  headline: "SEC-01 residual as recorded in BRIEF REQ-02 is an accurate, complete statement of the measured exposure; no understatement; F-04 fix verified not to touch SEC-01's mechanism."
  in_scope: true
  scope_reason: "Countersign of a prior high-severity security finding's recorded acceptance text, plus verification that this delta's one code change did not widen or narrow any route this role audited in cycle 1 — squarely this role's continuing surface."
  severity_max: none
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "Directory-level Bash rm/mv reaching the witness without naming it (SEC-01)", stride: "T,R", mitigated: false }
    - { boundary: "Edit creating .run-identity.json where none exists (F-04)", stride: "T", mitigated: true }
    - { boundary: "BRIEF ACCEPTED RESIDUAL paragraph vs measured mechanism", stride: "n/a", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1305-run-state-clobber/.harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-security-reviewer-c2.md
```
