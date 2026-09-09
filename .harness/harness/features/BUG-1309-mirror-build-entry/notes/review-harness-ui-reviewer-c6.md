# UI Review (Mode B) — merge-gate.py operator-facing messages — cycle 6

review_sha 894adc0f08c71c108ef8432f1f7a3cc8a2a763c0. No DESIGN.md exists under this feature dir
(confirmed: `ls .harness/harness/features/BUG-1309-mirror-build-entry/` — only BRIEF.md, STATE.md,
feature.json, plan.yaml, notes/, observations/, runs/). Visual/dark-light/a11y axes: N/A, no rendered
surface. In scope per dispatch: the CLI/hook text surface (stdout deny JSON `permissionDecisionReason`,
stderr allow-with-explanation lines). All messages below were EXECUTED against the live script at the
pinned path via constructed `/tmp/mgc6*` fixtures + stdin JSON, not read off the format strings.

## Headline
Every DENY names something (a feature id, or literally none via one pre-existing internal-exception
fallback). No DENY at this pin is the scan-wide "malformed record" sentinel that named nothing — that
one is confirmed gone (diff vs 894adc0f^ removes `unusable`/the "could not evaluate **a** feature's..."
branch entirely). One placeholder-naming DENY remains reachable, but it is **unchanged code inherited
from the parent commit**, not something this pin's decision-table rewrite touched or introduced.

## Message table (all captured live; ROOT=`/tmp/mgc6` unless noted)

| # | Trigger | Rendered literal | Names actionable? | Next-command correct? |
|---|---|---|---|---|
| 1 | non-merge command | *(silent — no stdout, no stderr, exit 0)* | n/a | n/a |
| 2 | `github.sync` falsy | *(silent)* | n/a | n/a |
| 3 | unreadable `harness.json` / unparsable stdin (outer `except Exception: return`) | *(silent)* | n/a | n/a |
| 4 | matched branch owns no usable record, gh not needed/succeeded | *(silent — ALLOW)* | n/a | n/a |
| 5 | matched record, `build_entry` in {opened, not-applicable, recovered-terminal}, gh not needed/succeeded | *(silent — ALLOW)* | n/a | n/a |
| 6 | gh resolution fails (`GH_BIN=/nonexistent/gh`) AND (no record OR record held) | stderr: `merge-gate: could not verify this merge - the head branch could not be resolved through gh ([Errno 2] No such file or directory: '/nonexistent/gh') and the local branch main owes no build-entry receipt; allowing it, because GitHub is a mirror and never a gate (DEC-138).` | names the gh error + local branch; ALLOW so no command needed | n/a |
| 7 | matched record, feature dir basename in `BUILD_ENTRY_ERA_EXEMPT` | stderr: `merge-gate: BUG-1030-stale-anchor-write-hazard predates the build-entry receipt (feature_schema.BUILD_ENTRY_ERA_EXEMPT), so this merge is allowed. Its terminal receipt is created only by an explicit operator-approved gh-sync.py recover-terminal /private/tmp/mgc6/.harness/repo-a/features/BUG-1030-stale-anchor-write-hazard --yes.` | YES — names feat + full realpath | YES — verified `gh-sync.py --help` lists `recover-terminal <dir> ... --yes` |
| 8 | matched record owes receipt, `recovery_command_for` → `recover-terminal` | stdout JSON deny: `merge-gate: FEAT-200-owing records github.build_entry=absent, so no Build entry receipt exists for it. This merge is denied until python3 .claude/skills/harness/bin/gh-sync.py recover-terminal /private/tmp/mgc6/.harness/repo-a/features/FEAT-200-owing --yes records one.` | YES | YES |
| 9 | matched record owes receipt, `recovery_command_for` → `open` (plan.yaml status not review/done, no done tasks) | stdout JSON deny: `... This merge is denied until python3 .claude/skills/harness/bin/gh-sync.py open /private/tmp/mgc6/.harness/repo-a/features/FEAT-500-open-recovery records one.` | YES | YES — `open` correctly omits `--yes` |
| 10 | matched record owes receipt AND `github.repo` not pinned (D-09) | stdout JSON deny: `merge-gate: FEAT-200-owing records github.build_entry=absent, and this project has github.sync true with github.repo NOT pinned, so the mirror records nothing here and no receipt can ever be written for it (D-09). NO COMMAND CLEARS THIS BY ITSELF. Pin github.repo in /tmp/mgc6-unpinned/.harness/harness.json to the value of gh repo view --json nameWithOwner -q .nameWithOwner, or set github.sync to false, and then re-run the Build entry.` | YES — names feat, exact file, exact remediation | YES — both remedies are real, runnable commands |
| 11 | internal exception raised **before** `feat_dir` is resolved (constructed: `os.getcwd()` raised because cwd was rmdir'd out from under the process, in-process repro via `runpy`) | stdout JSON deny: `merge-gate: could not evaluate this feature's Build-entry receipt, so this merge is denied. Repair the feature record and re-run the merge.` | **NO** — "this feature" is the literal placeholder seed, not an identifier | NO command given at all ("repair the feature record" is not a command) |
| 12 | internal exception raised **after** `feat_dir` resolved (e.g. inside `recovery_command_for`) | read-not-observed | n/a | n/a — see reasoning below |

Fixture provenance: #6/#7 forced via `GH_BIN=/nonexistent/gh`; #7's exempt id is a real entry from
`feature_schema.BUILD_ENTRY_ERA_EXEMPT`; #9's `plan.yaml` has `status: planning`, `tasks: []`; #10 used
a separate `/tmp/mgc6-unpinned` tree with `github.repo: ""`; #11 used a driver script
(`/tmp/mgc6-race/driver.py`) that `os.chdir()`s into a directory then `os.rmdir()`s it before
`runpy.run_path`-ing the gate in-process, so `os.getcwd()` inside `head_branch(...)`'s argument list
raises `FileNotFoundError` while `feat` is still the seed value.

## Direct answers to the panel's question

**(a) Can an unattributable record still influence the outcome?** Re-derived the same four
validator-lead-verified cases (t-ok ALLOW, scratch-branch ALLOW, t-owing DENY naming FEAT-9302-owing,
gh-unreachable ALLOW-with-DEC-138) plus rows 6–11 above; a non-dict/unparsable record is skipped by
`feature_for`'s own `except`/`isinstance` guard before any deny/allow decision reads it — no message
in this table is reachable through an unusable record. No.

**(b) Can a DENY still name nothing an operator can act on?** Yes — row 11, constructed and captured
live. **But this is not new at this pin.** `git show 894adc0f^:.claude/skills/harness/bin/merge-gate.py`
shows the identical `feat = "this feature"` seed and the identical outer `except Exception: deny(f"...
{feat}'s Build-entry receipt...")` at the parent commit — untouched by this pin's diff, which only
touched `feature_for()`'s return shape and its call site (`git diff 894adc0f^..894adc0f` confirms: the
sole change removes the `unusable` flag and the "could not evaluate **a** feature's..." scan-wide
sentinel branch; the exception-fallback block is not in the diff hunk at all). Per this role's
convention for a pre-existing, untouched sibling defect (Expertise P-11/G-11): reported as a **non-gating
advisory**, not a must-fix for this diff. It answers the panel's literal question honestly but should
not be scored against the decision-table rewrite under review.

Row 12 (exception after `feat_dir` resolved) is effectively unreachable by construction, not merely
untested: every call after `feat_dir` is assigned either can't raise (`os.path.basename`,
`isinstance`, dict `.get`, string formatting) or already owns its own internal `try/except`
(`feature_schema.recovery_command_for` catches its own `Exception` around the `plan.yaml` load and
falls back to `"recover-terminal"`). I did not find an input that reaches the outer handler with `feat`
already resolved to a real id; naming it unreachable rather than merely unobserved.

## Silent exits
Rows 1–5 are genuinely silent (verified zero bytes on both stdout and stderr, exit 0). Rows 1–3 are
gate-disabled/misconfigured states where fail-open-and-say-nothing matches this feature's own signed
DEC-138 framing ("GitHub is a mirror and never a gate") and prior panel-approved policy — not flagged.
Rows 4–5 are the **healthy/common-case ALLOW** paths (no record owed, or receipt already held) with a
successful or unnecessary gh lookup — every ordinary passing merge takes one of these two silent
branches. Printing an explanation on every clean merge would be pure noise; this is the expected
"silent on success" shape for a pre-merge hook and is not a gap.

## Wording consistency (acceptance point 4)
The same concept — "a Build entry receipt exists / is owed" — is rendered in **three different
surface forms** across the emitted messages: lowercase-hyphenated `build-entry receipt` (rows 6, 7),
capitalized-no-hyphen `Build entry receipt` / `Build entry` (rows 8–9, 10), and capitalized-hyphenated
`Build-entry receipt` (row 11, matching the module docstring). This is cosmetic — no message is
ambiguous about what it means — but it is a real, checkable inconsistency an operator grepping logs
for one exact phrase would trip over. Not gating (pure wording, no functional effect); noted per the
explicit acceptance-criteria ask, not filed as `must_fix`.

The three DENY *categories* (owed-receipt row 8/9, config-unpinned row 10, could-not-evaluate row 11)
are worded distinctly enough to pick the right remedy: row 10 explicitly says `github.repo NOT pinned`
and `NO COMMAND CLEARS THIS BY ITSELF`; rows 8/9 give a single concrete command; row 11 gives no
command (see above) but is at least framed differently ("could not evaluate" vs "records
github.build_entry=..."), so it isn't confusable with the other two even though it is not actionable
on its own terms.

## Verdict rationale
No `must_fix`. The scan-wide "names nothing" sentinel (cycle 5) is confirmed removed. The one
placeholder-naming DENY that remains is proven pre-existing and outside this diff's hunk. The
recovery commands (both `recover-terminal --yes` and `open`) were checked against `gh-sync.py --help`'s
usage line and are runnable as printed. Wording-consistency finding is advisory only.
