# Security review c2 — FEAT-56-central-onboarding-model @ 9768681c

## Headline
No new high/critical exposure introduced by this diff. One pre-existing, low-reachability
identity-confirmation gap in `harness-add-repo/SKILL.md` is carried forward unchanged from the
pre-split file (not a regression from the split). Everything else audited is clean, verified by
reading the actual bytes at `9768681c`, not by inference.

## Surface 1 — `.claude/skills/harness-add-repo/SKILL.md` (NEW), privileged operation
Read in full via `git show 9768681c`. Also diffed against the pre-split combined file
(`git show 12f74ea8:.claude/skills/harness-init/SKILL.md`, its old "Track B") to separate
split-introduced defects from carried-forward ones.

- **Ordering (D-04, settled):** not relitigated.
- **No secret/token/private-path is ever instructed to be written.** Grepped the full file for
  `token|secret|credential|password` — zero matches. The only content landed on the third-party
  default branch is `.harness/harness.json` (test_kinds commands, `github.repo`/`sync`/`board`
  — all non-secret, operator-visible values).
- **FINDING (low, pre-existing — not introduced by this diff).** Step 1 ("Land `harness.json`,
  then register the repository") lands a commit on a third-party repository's default branch and
  then writes a permanent fleet-membership entry, guarded only by prose in the Preflight section:
  "confirm push access... before proceeding" / "know the candidate repository's default branch."
  No command is specified to pin the repository's identity before this irreversible action. Contrast
  with the SAME document's step 3 (GitHub-mirror pinning, a strictly lower-consequence decision):
  there, the skill mandates running `gh repo view --json nameWithOwner -q .nameWithOwner`,
  showing the result, and getting explicit confirmation, specifically because "a fork or renamed
  remote would publish to the wrong org silently." No equivalent command-backed check exists for
  the step-1 target. `factory_config.py --check-product-configs` (the step-4 verification) only
  proves the *registered* name resolves to *a* valid `harness.json` — it cannot detect that the
  operator registered the wrong owner/repo, since a fork with its own committed `harness.json`
  would also pass.
  - Verified this gap **pre-dates the split**: the old combined `harness-init/SKILL.md`
    (`12f74ea8`, former "Track B") has the identical step-2 content and no preflight/identity-check
    section before it either — the new file's whole "Preflight — stop if any of these fails"
    block is itself new and net-additive, not a regression. This is carried forward, unchanged.
  - Threat: name confusion / fork-vs-upstream / org typo → operator lands the control-plane's
    config commit and grants ongoing config-read trust (`product_config` reads that repo's
    default branch forever) to the wrong repository. Actor is the *operator following the skill*,
    not a remote attacker — STRIDE: Spoofing of repository identity. Human-in-the-loop is the only
    compensating control, and it is exactly the control the doc itself distrusts one paragraph
    later for a smaller decision.
  - Severity: **low**. Not med/high because (a) pre-existing and unchanged by this diff — not a
    regression to gate on; (b) irreversible but the actor is a cooperating operator with a plain
    revert path (drop the fleet.yaml entry, revert/PR-close the harness.json commit); (c) it is
    advisory-only prose executed by a human, not an automated/attacker-reachable path.
  - Writability lane: `.claude/skills/harness-add-repo/**` resolves **NOBODY / main-session-direct**
    (`.claude/**` outside `harness/bin/`). Not in `must_fix`; recorded for the operator/backlog.

## Surface 2 — `factory_config.py::product_config_report()` / `--check-product-configs`
Read the full file at `9768681c`, plus `factory_gh.py::file_at_ref` and `GhError`/`run_gh`.
- Remote content handling: `raw = factory_gh.file_at_ref(...)` → `json.loads(raw)` only. No
  `eval`, no `pickle`, no YAML with unsafe loader, no path-join built from the remote document's
  contents (`_PRODUCT_CONFIG_PATH` is a hardcoded literal, never derived from the fetched doc).
  Treats remote content as data, never as code or a path component — correct.
- Failure-detail leakage: every `FleetError`/`GhError` message is built exclusively through
  `factory_cli.body(what, value, next_step)`; `value` is always `repo_name`, the fixed
  `.harness/harness.json` path, or `ref` (the declared `default_branch` from `fleet.yaml`,
  operator-authored, not secret). `GhError.__str__` never includes `stdout`/`stderr` (those are
  kept as attributes for a debugger, never interpolated into the message) — so a `gh` auth/rate
  failure cannot leak a token through `product_config_report()["members"][*]["detail"]`, which is
  the one value this new report writes to stdout via `factory_cli.payload`.
- Shell safety: `run_gh` calls `subprocess.run([gh] + list(args), ...)` — list-form argv, no
  `shell=True`; `repo_name`/`ref` land inside an f-string URL path segment for `gh api`, not a
  shell command line, so no injection vector.
- **No finding.** Assessed and dismissed.

## Surface 3 — `sync-command-adapters.py` (NEW) + `check-omp-port.py` door block
Read both files in full at `9768681c`, plus their new test (`tests/integration/test-sync-command-adapters.py`).
- `canonical_paths()` uses a **non-recursive** `canonical_dir.glob("harness-*.md")` plus one
  literal `harness.md` — cannot descend into subdirectories, so no crafted nested path is ever
  enumerated.
- Every write/unlink target is built from `adapter_dir / name` where `name` is `Path.name` (the
  final path component only, from a real directory entry) — a `.glob()` result's `.name` can
  never contain `/`, so `adapter_dir / name` can never resolve outside `adapter_dir` (no `../`
  traversal, no absolute-path override).
- Stale-adapter removal (`actual_names - set(expected)`) is itself bounded to
  `adapter_dir.glob("harness*.md")` — `--apply` can only ever create/overwrite/delete filenames
  matching that pattern inside `.claude/commands/`, never anything else on disk.
- Threat model note: the only "input" here is bytes already committed to the same repository by
  whoever can push it — there is no untrusted-vs-trusted boundary crossed (both `.omp/commands/`
  and `.claude/commands/` are first-party, same-repo). A symlink under `.omp/commands/` pointing
  outside the repo would have its target's bytes copied into a committed adapter file, but
  creating that symlink already requires the same repo-write access the tool itself needs — no
  privilege gained.
- `check-omp-port.py`'s new block is purely additive (four `is_file()` existence checks + one
  `subprocess.run([...,"--check"])` call, diffed line-by-line against base) — no new attack
  surface of its own.
- **No finding.** Assessed and dismissed. (Lead 2's question — whether this gate would have
  caught the `disabledProviders:[claude]` door-invisibility bug in its *original* state — is a
  verification-completeness question with no trust boundary or exploit behind it; out of scope
  for this role, not declined for lack of looking.)

## Surface 4 — T-02 message-only edits: `gh-sync.py`, `check-state.sh`, `check-domain.sh`, `upgrade-config.py`, `layout_migration.py`
Diffed every hunk at `-U6`/`-U8`/`-U16` context against `4b5dbb23` and read every changed line.
- All five files: **every changed line is inside a `print(...)`/`.append(...)` string literal or a
  `#`-comment/docstring.** No `if`/`elif`/`else`/`sys.exit`/`return`/`raise` line touched anywhere
  in the five diffs.
- `check-domain.sh`'s fail-open branch (`if not os.access(manifest, os.R_OK): print(...);
  _run_domain = False`) — the condition, the assignment, and the guarding `if _run_domain:` two
  lines below are byte-identical before and after. The edit only expands the printed sentence.
  Confirmed this is the *only* hunk in the file.
- **No finding.** Assessed and dismissed — confirms the dispatch's own framing.

## Surface 5 — `cli_min_version` removal (D-13, settled) across five config files
Diffed all five files (`-U4`) against base.
- Confirmed the **only** functional key removed anywhere is `cli_min_version`; every other change
  is a `_note`/`_template`/`_panel_era_start_note`/`_handoff_done_when_baseline_note` doc string
  or comment-line rewording. No `domain`/`writes`/`hooks`/board/grant key was added, removed, or
  reordered in `.harness/harness.json`, `.harness/team-config.yaml`, or their templates.
- **Assessed-and-dismissed incidental observation, not a finding:** `.claude/skills/harness/templates/team-config.yaml`'s
  `main_session.writes: [...]` flow-sequence gained quotes around each entry in the same commit.
  Verified empirically (`yaml.safe_load`) that the **unquoted** form — present, unchanged, at base
  `4b5dbb23` — is invalid YAML: the unquoted ` ## Approval` sequence starts a comment that
  swallows the rest of the line *including the closing `]`*, so `harness_yaml.load_file` would
  raise a hard `ParserError` on this **template** file (not the live `.harness/team-config.yaml`,
  which already used the safe quoted block-list form and was never affected). That parse failure
  is exactly what `upgrade-config.py`'s "THE SHIPPED TEMPLATE ... does not parse" branch exists to
  report — a loud, fail-closed, pre-existing correctness bug, not a silent permission widening.
  This diff's incidental quoting fixes it as a byproduct of the adjacent edit. No security action
  needed.
- **No finding for the settled removal.** D-13 not relitigated.

## Threat model
| boundary | stride | mitigated |
|---|---|---|
| harness-add-repo landing a commit on a third-party default branch | Spoofing (repo identity) | false — human-mediated only, pre-existing gap |
| factory_config.py remote `harness.json` read (no disk fallback) | Tampering / Information Disclosure | true — json-only parse, no path-join, no leak in error text |
| sync-command-adapters.py file generation into `.claude/commands/` | Tampering (path escape) | true — non-recursive glob, `.name`-only targets, same-repo trust |
| check-domain.sh fail-open-without-manifest branch | Elevation of Privilege | true — control flow byte-identical to base, message-only edit |
| team-config.yaml / harness.json grant and hook keys | Tampering | true — diffed; only `cli_min_version` removed, no adjacent key changed |

## Open questions
None blocking.
