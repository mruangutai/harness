# UI Review — BUG-1309-mirror-build-entry — review-c0 (Mode B)

## Verdict: PASS (scoped out of rendered-UI audit; refusal-message usability audit performed per dispatch)

## Census (measured at pin `6f64a21c5df24f8dd17c4f1bcf2c93e10563cf24`, diff base `6ad7233f`)

- `git diff --name-only 6ad7233f..6f64a21c` → **77 files changed**.
- Extension census (`sed -E 's/.*(\.[a-zA-Z0-9]+)$/\1/' | sort | uniq -c`):
  `52 .md, 14 .py, 4 .json, 3 .sh, 2 .yaml, 2 .ts` — **zero** html/css/scss/tsx/jsx/vue/svelte/less
  hits.
- No `DESIGN.md` exists for this feature (`glob` on the feature dir returned no match); no
  `notes/mockups/**` or `notes/prototypes/**` either — no approved visual reference to audit
  against.
- The two `.ts` files: `tests/unit/omp-hooks.test.ts` (test) and `.omp/extensions/harness-hooks.ts`
  (hook registration). Diffed the latter directly — the entire BUG-1309 delta there is one line
  adding `merge-gate.sh` to the `PreToolUse` policy chain; no string/text/rendering change.
- Grepped the two touched doctrine docs (`github-mirror.md`, `SKILL.md`) for spacing/colour/contrast/
  theme language — no hits (the one regex hit was a false positive on issue number `#671`, not a
  hex colour). The 52 `.md` files are process artifacts (receipts, research notes, BRIEF/STATE,
  DECISIONS, SKILL doctrine) — none specifies spacing, colour, or interaction state for a rendered
  surface.
- Confirmed the working tree is not ahead of the pin except for the pin-bookkeeping commit itself
  (`git diff 6f64a21c..HEAD` touches only `feature.json`) — so this census is against the reviewed
  commit, not a later or stale copy.

**Conclusion: this diff has no rendered UI surface.** CLI/hook/doctrine change, as the dispatch
expected. Accessibility and dark/light-theme parity are **not applicable** — no colour, no markup,
no theme-able surface exists in this diff; confirmed by grep, not assumed (no ANSI/colour-code
usage found in any of the three files carrying the new refusal text either).

## Refusal-message audit (the one in-lane consideration per dispatch)

Traced every new operator-facing refusal/notice this feature adds, checking whether each names the
concrete recovery command (not just the triggering fact), and whether it composes
`feature_schema.recovery_command_for()`'s output into something copy-paste runnable.

| Site | Message | Actionable? |
|---|---|---|
| `merge-gate.py` deny — receipt owed | Builds `command_line` from `recovery_command_for(feat_dir)` + `os.path.realpath(feat_dir)` (+ `--yes` when `recover-terminal`) and embeds it in the denial text | **Yes** — copy-paste runnable |
| `merge-gate.py` deny — repo unpinned | Names the exact `gh repo view --json nameWithOwner -q .nameWithOwner` fallback and the `harness.json` path to edit | **Yes** |
| `merge-gate.py` era-exempt notice | `recover-terminal {realpath(feat_dir)} --yes` | **Yes** |
| `check-state.sh` INV-37 (both branches) | `gh-sync.py open {_fp37}` / `gh-sync.py recover-terminal {_fp37} --yes`, path adjacent to command in both | **Yes** |
| `gh-sync.py` `_build_entry_preflight` refuse — entry absent, command=="open" | `Run gh-sync.py open {realpath(feat_dir)} first.` | **Yes** |
| `gh-sync.py` `_build_entry_preflight` refuse — entry absent, command=="recover-terminal" | `Run gh-sync.py recover-terminal {realpath(feat_dir)} --yes.` | **Yes** |
| `gh-sync.py` `_build_entry_recovery_notice` — **non-exempt**, entry=="recovery-required" | `"...for {realpath(feat_dir)}; Build proceeds, the MERGE is refused until gh-sync.py open records opened"` | **Finding — see below** |

### Finding UI-1 (severity: low)

`gh-sync.py:_build_entry_recovery_notice`, non-exempt branch (the plain `print` right after the
`if feature_id in feature_schema.BUILD_ENTRY_ERA_EXEMPT:` early return) states the fact and names
the remedy subcommand (`gh-sync.py open`) but — unlike every other refusal/notice site in this same
feature — does **not** append the feature-dir path to that command. The path only appears earlier in
the same sentence (`"...recovery-required for {realpath(feat_dir)}; ..."`), not adjacent to the
command the operator is meant to run.

**Concrete failure scenario:** an interrupted `gh-sync.py open` (e.g. `gh auth status` fails
mid-run) records `build_entry: recovery-required` on a non-era-exempt feature. The orchestrator
later runs `cmd_start_task` for that feature's next task; `_build_entry_preflight` calls this notice,
which prints to stderr: `"gh-sync: build entry is recovery-required for /abs/path/to/feat; Build
proceeds, the MERGE is refused until gh-sync.py open records opened"`. Build proceeds (correct,
non-blocking), but the operator monitoring stderr sees a bare `gh-sync.py open` with no path
argument — they must manually re-parse the sentence and splice the earlier path into the command
themselves, rather than getting a copy-pasteable line as they would from every sibling site in this
same file (`_build_entry_preflight`'s two `refuse()` branches, three lines above in the same
function's control flow, both append the path directly). Non-blocking (Build isn't gated on this
message), so severity stays low, not med/high — but it is an inconsistency within a change whose
entire stated purpose is legible, actionable refusal text.

No other gaps found in this audit. `feature_schema.recovery_command_for` is real, correctly resolves
`open` vs `recover-terminal` off `plan.yaml` status/task-done state (era-exempt shortcut checked
first), and its output IS surfaced to the human at every other refusal site.

## Accessibility / theme parity

Not applicable — no rendered surface, no colour, no theme in this diff. (The one `colors = {...}`
dict found via grep is GitHub Issues label hex colours in a pre-existing, untouched-by-this-feature
labelling helper — a third-party surface this feature does not modify.)

## Open questions
None.
