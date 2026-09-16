# Security review c3 — FEAT-56-central-onboarding-model @ 44351432

## Headline
PASS. F2 (the circular-delegation bug) and F4 (the wrong banner path) are both confirmed correctly
closed at the pin, with no new injection, path-traversal, secret-disclosure, or auth surface
introduced by the fix commit. F3's fail-closed behaviour is confirmed by its own test. One
pre-existing, unchanged-by-this-diff observation (symlink following in the adapter generator) is
carried forward from the c2 review with the same non-gating conclusion, re-verified by
reproduction. One new advisory: no mechanical check protects against a *future* regression to F2's
shape.

## Method
Every file read via `git show 44351432:<path>`, plus `git show 44351432 -- <path>` to isolate what
this commit actually touched (as opposed to pre-existing code). Grepped for
`shell=True|os\.system|eval\(|exec\(` and for secret/absolute-home-path patterns across all nine
files via `git show`-sourced content (not the worktree, to avoid any read-cache staleness).
Reproduced the symlink-read behavior of `sync-command-adapters.py` against a scratch tree built and
torn down entirely inside a single `python3` invocation (the bash write-guard correctly refuses
shell-level redirects/`rm` for this read-only role).

## Per-file coverage
| file | task | lane | looked for | result |
|---|---|---|---|---|
| `.claude/skills/harness/bin/sync-command-adapters.py` | T-14 | team (backend-dev\|dev-ops) | path derivation, traversal/symlink escape, subprocess/eval, what the 24-line diff actually changed | see findings F-1 (carried forward), no new issue in the diff itself |
| `tests/integration/test-sync-command-adapters.py` | T-14 | team (backend-dev\|dev-ops\|qa) | subprocess `shell=True`, temp-fixture path handling, no symlink test case | clean; confirms subprocess is list-argv only |
| `tests/integration/test-check-omp-port.py` | T-14 | team (backend-dev\|dev-ops\|qa) | subprocess safety, `importlib` module load of a hardcoded first-party path (not attacker input) | clean |
| `.omp/commands/harness-plan.md` | T-13 | main-session-direct (NOBODY) | delegation target text, injected instruction content | now reads `.omp/commands/harness.md` — F2 confirmed closed |
| `.omp/commands/harness-ship.md` | T-13 | main-session-direct (NOBODY) | same | same — F2 confirmed closed |
| `.claude/commands/harness.md` | T-13 | main-session-direct (NOBODY) | banner path correctness, byte-parity with canonical | banner fixed (F4); body byte-identical to `.omp/commands/harness.md` from line 2 on |
| `.claude/commands/harness-plan.md` | T-13 | main-session-direct (NOBODY) | same | banner fixed; body byte-identical to canonical |
| `.claude/commands/harness-ship.md` | T-13 | main-session-direct (NOBODY) | same | banner fixed; body byte-identical to canonical |
| `.claude/commands/harness-grilling.md` | T-13 | main-session-direct (NOBODY) | same | banner fixed; body byte-identical to canonical |

Byte-parity verified programmatically (`git show` both sides, split adapter on first `\n`, compare
remainder to canonical) — all four MATCH. Secret/credential/absolute-home-path grep across all nine
files: 0 hits. `shell=True`/`os.system`/`eval`/`exec` grep across the three Python files: 0 hits
(the three `subprocess` hits in the two test files are all list-argv `subprocess.run([sys.executable,
...])`, no shell).

## Findings

**F-1, carried forward, low, non-gating.** `sync-command-adapters.py:26-38`
(`canonical_paths`/`expected_adapters`) follows symlinks: `path.is_file()` and `path.read_text()`
dereference a symlink, and `canonical_paths()`'s glob (`harness-*.md`) admits any filename matching
that pattern, not only the four required doors. Reproduced: placing
`.omp/commands/harness-zzz-exfil.md` as a symlink to an arbitrary file and running `--apply`
writes that file's bytes verbatim into a newly tracked `.claude/commands/harness-zzz-exfil.md`
(banner + content), e.g. a local `.env` reproduction copied `SECRET_API_KEY=...` straight through.
Confirmed via `git show 44351432 -- .claude/skills/harness/bin/sync-command-adapters.py` that this
commit's 24-line diff touches only the banner string and adds `missing_required_doors` — the
read/glob logic is byte-for-byte unchanged from what c2's review (Surface 3) already assessed and
dismissed on the same reasoning I independently re-derived: creating the symlink already requires
the same `.omp/commands/**` write access (main-session-direct / NOBODY lane) that running `--apply`
itself assumes, so no privilege is gained across the boundary that matters in this deployment model.
Not introduced by this diff, not re-opened by it. File: `sync-command-adapters.py`. Task: T-14.
Lane: team (harness-backend-dev | harness-dev-ops).

**F-2, new observation, low, advisory, non-gating.** Nothing in the test suite or in
`check-omp-port.py` asserts the *delegation text* inside `harness-plan.md`/`harness-ship.md` —
only door existence (`check-omp-port.py:168-171`) and adapter byte-parity
(`sync-command-adapters.py --check`, T-13's verify) are checked. A future hand-edit that
reintroduces F2's shape (pointing back at `.claude/commands/harness.md`) would pass every existing
gate silently, since the adapter would still byte-match its own canonical source and the door would
still exist. This fix cycle got the text right (confirmed above), but the fix has no regression
guard. File: none single — spans `.omp/commands/harness-plan.md`, `.omp/commands/harness-ship.md`,
and whichever test file would carry the assertion. Task: none (no task in `plan.yaml` owns a
content-level delegation check). Lane: `tests/**` is team (harness-backend-dev | harness-dev-ops |
harness-qa) — a fix here is buildable by the team, not a NOBODY-lane item, so this is a real backlog
item rather than an operator-only decision.

## Threat model
| boundary | stride | mitigated |
|---|---|---|
| `.omp/commands/**` canonical door content read into generated `.claude/commands/**` adapters | Tampering / Information Disclosure (symlink dereference) | true — precondition-absent: exploiting it needs the same NOBODY-lane write access that legitimately runs `--apply` |
| adapter regeneration banner/path correctness (F4) | Tampering (operator following a dead instruction) | true — banner now names the real script path, confirmed by diff |
| door delegation direction (F2) | Tampering (dependency pointing the wrong way) | true for this commit's content; false for future regressions — no mechanical text check exists (F-2) |
| `--check`'s required-door set (F3) | Denial of Service (silent gate bypass via paired deletion) | true — `case_missing_required_door_fails` proves fail-closed |

## Open questions
None blocking.

## Non-goals honored
F1's complexity grade and the integration test matrix are out of this role's scope and were not
re-derived here; `harness-code-reviewer` and `harness-qa` own those respectively.
