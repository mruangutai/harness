# Goal-check c17 — SC-04 and SC-11 at `94b5e465d498a9943890734223e69c390b0a77ad`

**BLUF. SC-11 = MET. SC-04 = UNMET** — not on behaviour, on evidence: three of its ten clauses have
**no integration case that asserts them** (clause g entirely, clause h for three of its four noise
kinds, clause a for its "names the feature" half). Each is *work undone* (O-07: a case can be
written), not an unmeetable criterion. The c15 blocker — the detached-value global class, form 16
`git --exec-path <p> merge <branch>` — is **resolved**: `--attr-source` (the measured c15 escape) now
denies, and real git never reaches `merge` on a bare `--exec-path`, so the residual parse is
unreachable. Nothing was fixed, softened or waived here.

## Commands run

| command | result |
|---|---|
| `git -C <wt> rev-parse HEAD` | `94b5e465…` before and after this check — HEAD did not move |
| `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-merge-gate.py` (worktree root) | **exit 0**, 34 `ok`, **0 `FAIL`** (grepped the `FAIL ` prefix, per G-08), final line `ALL PASSED` |
| `env -u HARNESS_AGENT_TYPE python3 /tmp/mgprobe17.py /tmp` (throwaway, `/tmp` only) | parser probe, output below |
| `git --exec-path status` (in `/tmp`) | printed `/Library/.../git-core` and **did not run `status`** |

Test source graded at the pin: `git show 94b5e465…:tests/integration/test-merge-gate.py` (200 lines).

## SC-11 — MET

Each of the three named cases observed **individually** in the run output (not a file-global grep):

```
32:ok    T-05 merge --abort on an owing branch allows
33:ok    T-05 merge --continue on an owing branch allows
34:ok    T-05 merge --quit on an owing branch allows
```

Each is its own tuple driven through `check()` with `r.returncode == 0 and d is None` — exit 0, no
`permissionDecision` object (`test-merge-gate.py:191-198` at the pin).

**Discrimination against `git show e374c9a2:.claude/skills/harness/bin/merge-gate.py`: CITED, NOT
RE-RUN BY ME.** The per-case measurement is `notes/qa-c17.md:50-63` — a three-row table, one row per
case name, each recording *reddens at `e374c9a2`: yes (old code denies)*, taken by qa's own re-run
against a scratch bin. `notes/review-harness-qa-c17.md:42-44` corroborates the pass at the pin;
`notes/review-harness-code-reviewer-c17.md:76-84` corroborates that each case exists separately.
Only `qa-c17.md` carries per-case discrimination numbers.

## SC-04 — UNMET

| # | clause | integration case carrying it | verdict |
|---|---|---|---|
| a | single-owner deny reason names the feature **and** the re-run command | `T-05 non-era absent build_entry denies` asserts `"gh-sync.py open" in reason` | **UNMET (half)** — see gap A |
| b | allow for `opened`, `not-applicable`, `recovered-terminal` | `T-05 opened allows`, `T-05 not-applicable allows`, `T-05 recovered-terminal allows` (exit 0, `d is None`) | MET |
| c | era-exempt allowed, exit 0, no permission decision | `T-05 era-exempt absent build_entry allows`, `T-05 era-exempt recovery-required allows` | MET |
| d | ≥2 valid attributable records → DENY | `T-05 duplicate valid records claiming the branch deny naming both` | MET |
| e | every claimant named, stable order | same case: both ids in `reason`, and `reason == repeated_reason` across two runs | MET (note 1) |
| f | no re-run/receipt command on the ambiguity deny | same case: `"gh-sync.py" not in reason` | MET |
| g | ambiguity deny reached even when a claimant **is** era-exempt | **none** | **UNMET** — gap B |
| h | one owner + noise (unreadable / malformed / non-object / different-branch) changes no verdict | `T-05 unrelated non-object feature record does not block healthy merge` and `T-05 single owner plus unrelated malformed record still allows` — **both fixtures are byte-identical** (`json.dump([])`, i.e. non-object) | **UNMET (1 of 4)** — gap C |
| i | a branch no valid record claims is ALLOWED while such a record exists | `T-05 branch matching no feature allows`; `T-05 no-record branch ignores unrelated malformed record` | MET |
| j | `gh` cannot resolve head → allow, one stderr line | `T-05 gh outage with no matching feature allows` (`d is None and "could not verify" in r.stderr`) | MET (note 2) |

**Gap A.** No case asserts the feature id *inside a single-owner receipt deny*.
`T-05 recovery-required denies` asserts only `"recovery-required" in reason`; `T-05 non-era absent
build_entry denies` only the command. `T-05 empty plan fails closed` does assert
`"FEAT-9001-fixture-non-era" in reason`, but that is the fail-closed exception deny
(`merge-gate.py:194`), a different string that carries **no** re-run command. The behaviour is
correct — `merge-gate.py:192` interpolates both — but SC-04's declared method is `automated`, and no
automated assertion covers the conjunction.

**Gap B.** Both duplicate fixtures are `FEAT-9001-fixture-non-era` and `FEAT-9002-fixture-duplicate`
(`test-merge-gate.py:149-162`); `feature_schema.BUILD_ENTRY_ERA_EXEMPT` contains only `BUG-*` ids
(`feature_schema.py:226-…`), so neither claimant is era-exempt. The ordering the clause demands holds
in source (ambiguity at `merge-gate.py:172`, era gate at `:179`) — that is **inspection**, not the
`automated` evidence SC-04 declares.

**Gap C.** Of the four noise kinds the clause enumerates, only *non-object* is exercised. No case
writes an **unreadable** record (the `OSError` arm of `feature_for`, `merge-gate.py:138`), none writes
**malformed JSON text** (the `JSONDecodeError` arm), and none puts a **different-branch** record
alongside a live owner. Per P-04, part of an enumeration is not the enumeration.

Note 1 — the case asserts run-to-run invariance (the criterion's stated purpose), not sortedness
itself; sorting is at `merge-gate.py:173`. Note 2 — the case asserts the stderr *content*, not that
it is exactly one line.

## The c15 residual — closed

c15 graded SC-04 UNMET on form 16 (`notes/research-BUG-1309-goalcheck-c15.md:3-11,53-59`). At this pin:

```
None                         git --exec-path /usr/lib/git-core merge feature/test
('git', 'feature/test')      git --attr-source HEAD merge feature/test    <- c15 ALLOW, now denies
('git', 'feature/test')      git --work-tree /tmp merge feature/test
('git', 'feature/test')      git --git-dir | --namespace | --config-env | --super-prefix | -C ... merge feature/test
```

The detached-value class is covered by cases `T-05 git --work-tree global flag merge is still
detected`, `T-05 git -C global flag merge is still detected`, `T-05 git -c config global flag merge
is still detected` and `T-05 global --attr-source before merge is still detected` (run lines 22-24,
30). `--exec-path` alone still parses to `None`, but `git --exec-path status` prints the exec path
and never runs the subcommand — real git never merges on that input, so it is not an escape.
Independently confirmed by `notes/review-harness-code-reviewer-c17.md:27-32`. **Form 16 is not a
live SC-04 gap and Q1 of the c15 note is answered.**

## Drift

The c15 note records `27 ok` for this suite; the pin yields `34 ok` (+50/−26 on the bed across
`e374c9a2..94b5e465`). Content-anchored on case names throughout, per the drift rule; no criterion
graded on a count.

## Non-modification

`plan.yaml`, `BRIEF.md`, `feature.json`, `STATE.md`, the UAT script, all source and all tests are
**unmodified by me**. `git status --porcelain` shows the same 3 modified + 5 untracked feature-note
paths before and after (none of them mine except this file); HEAD is `94b5e465…` unchanged. The only
files I wrote are this note and `/tmp/mgprobe17.py`.

## Open question

- **Q1 (blocking the ship decision, not SC-10).** SC-04 is UNMET on evidence with correct behaviour
  underneath. The budget is exhausted, so the operator chooses: accept the three assertion gaps with
  a recorded ruling (the behaviour is inspected-correct at `merge-gate.py:172/179/192` and
  `:138`), or carry them as a follow-up bug for the missing cases. Not mine to decide, and I did not
  soften the grade.
