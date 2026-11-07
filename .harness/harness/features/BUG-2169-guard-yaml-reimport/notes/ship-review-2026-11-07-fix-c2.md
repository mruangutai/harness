# Ship review - BUG-2169-guard-yaml-reimport

**Recommendation: ship.** The dispatch guard keeps a trusted system-wide PyYAML across its two
import phases instead of half-re-importing its C module, the refusal advice installs PyYAML
where the guard looks, and CI is back on the runner image's single PyYAML. Every success
criterion is met at the final tip; no must-fix remains. Merge is yours.

review_sha: `a48a725e16321d3a3f9ef142a0b95e2e19a4de5e` (feature.json). Base `c4e8bbc8`
(origin/main). Branch `feat/BUG-2169-guard-yaml-reimport`, not pushed; no PR yet.

## Definition of done - by perspective

| Perspective | SCs | Final (fix c2) |
|---|---|---|
| operator (fleet owner) | SC-01, SC-02 | met - starts succeed on one system-wide PyYAML with and without its C loader; every advice branch fails on the old advice at base and passes at tip, on the Ubuntu 26.04 image |
| CI | SC-03 | met - `tests.yml` is a clean revert of #2168; no forced second install |
| code maintainer | SC-04, SC-05 | met - fail-first and fixed receipts preserved; isolation plants discriminate (mutant red); `worktree_terminal.py` fallback kept and documented |

## What landed (7 code/test/doc files, +264 / -50)

- `dispatch-guard.py`: keep `yaml`/`yaml.*` only when every loaded module resolves inside the
  policy path and outside the distrusted roots; otherwise purge the whole package.
- `harness_yaml.py`: `install_command()` - apt on Debian/Ubuntu system python3; pip
  `--break-system-packages` without `--user` on Homebrew, with Homebrew's PEP 668 warning;
  plain pip otherwise. `INSTALL_COMMAND = install_command()`.
- `checkout-prereqs.md`: prints `INSTALL_COMMAND` instead of the retired `--user` line.
- `worktree_terminal.py`: docstring only. `.github/workflows/tests.yml`: revert of #2168.
- Tests: `test-lead-start-preflight.py` (single install, four plant spellings, per-platform
  advice), `test-check-domain-grant.py` (SC-08 and D-14a assert the real commands).
- Two ledgered files-only amendments (grant test, prereqs doc); signed hashes unchanged.

## How validation went

| Run | Result | Findings |
|---|---|---|
| validate c0 at 6c896d98 | FAIL | F-1 D-14a still pinned `pip install`; GC-01 non-C-loader start unproven, advice not red at base |
| fix c1 at 90caccaf | FAIL | F-1, GC-01(a) resolved; GC-01(b) Homebrew/generic/warning red only on the Mac |
| fix c2 at a48a725e | PASS | all resolved; full unit (57 files) and integration (84 files) kinds green |

Security and UI passed every round. Two med grade-2 test-complexity findings accepted with
written reasons (`notes/build-evidence-2026-11-07.md`).

## Spend and judgements

4 runs, 48 wall-clock minutes; 2 rework rounds / 38 minutes against your raised ruling of
2 / 90 (`notes/operator-rework-raise-2026-11-07.md`). `cycles_used: 1` - fix c1's return
reported 0 and was recorded as given. Tokens are measured for the intake run only.

**Every run is recorded BLOCKED / refused-return.** Each lead returned a valid object, but
the host never appended it to `digest.md` (#2171), so close-run could not accept it. The real
verdicts (FAIL, FAIL, PASS) live in each run's prose report and the tracked reader notes
`notes/*-c0/c1/c2.md`. Pruning at ship keeps only PASS-recorded validate runs, so the run
directories will go; the notes stay.

## Before merge

- Push the branch and open the PR with this note as its body; CI on ubuntu-26.04 now runs the
  image's own PyYAML, so a green CI is itself SC-03/SC-04 evidence.
- After merge, `gh-sync.py ship` from the main checkout moves #2169, #2175, #2176 to Done.

## Proposed backlog

| ID | Nature | Finding |
|---|---|---|
| B-1 | bug | `feature_schema.py:59-60` jsonschema advice and three test bail-out messages still say `--user`; isolated hooks importing `feature_schema` likely cannot see a per-user jsonschema [inference, not measured] |
| B-2 | chore | `gh-sync.py status review` rewrites `plan.yaml` after the pin, so INV-33 marks the pin stale by construction; the procedure needs a repin step or the station write excluded from the comparison |
| B-3 | chore | `feature-record.py close-run` resolved a relative `--digest` against the cwd at the validate stage - fixed on main by #2177 (merged into this branch before push); not filed |
