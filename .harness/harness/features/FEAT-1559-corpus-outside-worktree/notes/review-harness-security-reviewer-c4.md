# Security review — c4

**PASS — no new actionable security finding; raw-byte repair protection and owner-read identity survive isolated probes.** Review pin `35587d8dfbf9178e21410c201601f7137fbfbbd6`; full range `e8d868f78a6ec43880598af5c5873f5daa8ba985..35587d8dfbf9178e21410c201601f7137fbfbbd6`; delta `6c11ab626ed568236978b1640928162b8cf0139f..35587d8dfbf9178e21410c201601f7137fbfbbd6`. `bin/` below means `.claude/skills/harness/bin/` at this immutable pin.

## Scope and boundaries

Re-censused all 97 changed paths: production corpus readers, permission gates, repair and hooks are IN (Tampering, attribution, protection of work); tests/fixtures are evidence; feature records, decisions and guidance are authority/documentation inputs. No browser/rendered UI, dependency addition, network/SSRF, spreadsheet export or new credential surface. Full-diff credential-pattern sweep found only the unrelated `TOKEN` regex, no credential-shaped match (raw diff `artifact://2086`). Read BRIEF, plan task/decision lanes, fix receipt, prior security reviews and ship-review backlog; the receipt was not accepted as proof.

- **Owner reads / T-01,T-03:** `feature_corpus.py:155-216,252-301,328-376` resolves owner checkout, checks tracked/reached directory names, retains segment-qualified population, and keeps absent active records checkout-local by identity. Ruling B excludes sibling providers. `factory_claim.py:84-95,106-109,159-163` routes both plan and issue-map reads through the same resolver. No new owner-write grant: `digest_destination.py:24-36` remains local; `harness_boundary.linked_worktrees` normalizes pointer ownership without introducing git subprocesses on governed write paths.
- **Gate decisions / T-02,T-03:** `merge-gate.py:202-216,276-287` turns corpus/layout failures into deny and counts distinct directory owners; `check_state/corpus.py:80-119` examines structural findings even when dirty wins exit priority. Dirty-only silence is not permission or proof of convergence.
- **Repair / T-01,T-04:** `worktree-state.py:164-233,299-327` compares raw contents and index type before any sparse mutation; regular-to-link mismatch cannot qualify as removable B. `os.fsencode(readlink(...))` retains invalid target bytes. argv lists and quoted hook paths introduce no shell interpolation.

## Independent seven-fix assessment

| Fix | Evidence at pin | Clearance |
|---|---|---|
| 1 owner corpus factory lookup | `FactoryClaim.test_a_landed_plan_and_issue_map_are_read_from_a_sparse_worktree` | exercised PASS |
| 2 no-filter hash/type mismatch | lossy-clean-filter regression PASS; independent regular tracked BRIEF replaced by symlink to `bad-ff` (hex `6261642dff`) returned 8, `repaired=False`, snapshot equality true | exercised PASS; link bytes preserved |
| 3 mode120000 readlink hashing | unchanged-link B and retargeted-link C regressions PASS; independent tracked target `target-ff` hashed exactly equal to index | exercised PASS, including invalid target byte |
| 4 C-quoted directory decoding | non-ASCII cone regression PASS; direct escaped quote/backslash/tab/UTF-8-octal roundtrip equality true | exercised PASS |
| 5 detached branch fallback | branch-named mid-rebase regression PASS; `feature_corpus.py:97-131,487-524,647-663` statically gives planning identities fallback branch and pins directory-only identity | rebase exercised; bisect conflict probe NOT executed |
| 6 missing active directory stays local | `CrossCheckoutReads.test_a_missing_active_directory_is_missing_not_a_landed_copy` (directory and branch identities) | exercised PASS |
| 7 quiet dirty and hooks | ordinary-work regression PASS for post-checkout/post-rewrite; all three pinned hooks pass `--quiet-dirty` and require nonempty output to print repair failure; CLI retains exit8 | two hooks exercised; post-merge static only |

Eight selected regression cases ran, not entire files/suites: 5 repair/identity cases (5.922s), 2 corpus cases (1.273s), 1 quiet-hook case (1.146s); all exited 0. The two independent byte probes and quote roundtrip also exited 0. Fixture context teardown removed private synthetic owners/worktrees. Source stayed read-only; no full suite, build, lint or formatter ran. These are current-state discriminators, not a historical fail-first claim. Pinned AGENTS/harness/verification guidance and README retain absolute landed reads, active writes, structural refusal/recovery and clone-local hooks configuration.

## Capability limit and cleanup

**Open SEC-C4-Q1 (nonblocking):** the requested BISECT_START-versus-directory/pin adversarial probe was refused before execution by the live Bash write guard because its disposable metadata setup used Python `open`. No bypass/retry through another writer was attempted. Recommend QA/main exercise that one case with its authorized disposable fixture; static code inspection and exercised rebase evidence do not prove the bisect precondition. Quoted-path proof covers decoder semantics, not every filesystem-byte pathname.

Existing #2107/#2108 and B-1..B-9 are not refiled, regraded or claimed fixed. SC-10/T-06 remains deferred to #2101 with the HEAD-era precondition; hardlink strengthening remains excluded. Managed helper created the exact pin with key `FEAT-1559-corpus-outside-worktree / validate-c3-validator / harness-security-reviewer-c4`; matching-key removal exited 0 before this report. No full clone created; no sibling checkout touched. Source files changed: none.
