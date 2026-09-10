# EFFICIENCY angle — FEAT-58-corpus-outside-worktree plan draft

## Conclusion

No wasted-minutes work found. The plan is disciplined about fixture use — 16 of 19 tasks route
every automated assertion through `f58_sparse_fixture`, the three real-repo touches the dispatch
named (T-10 Part 3, T-11, T-19b) are exactly the ones that need to be real, and two more real-repo
touches I found on my own read (T-01's baseline suite run, T-09 verify's `--check`) are also
structurally necessary, not accidental. Two low-severity findings below, both explicitly cheap in
absolute terms — I'm reporting them because the dispatch asked me to quantify the repeated-tree
construction and the redundant `--check` call, not because either is a real cost problem. Three
things I checked and expected to cost something turned out cheap; I say so below rather than
manufacturing findings around them.

**Sizing commands run** (read-only, not a suite run):
`git ls-files .harness/harness/features | wc -l` → 3334; `git ls-tree -d --name-only HEAD | wc -l`
→ 8; `ls tests/unit/test-*.py | wc -l` → 36; `ls tests/integration/test-*.py | wc -l` → 68. No test
suite was executed — full-suite execution is out of scope for this pass and I did not run one.

## 1. Fixture import discipline, task by task

| Task | Routes through fixture? | Verdict |
|---|---|---|
| T-01 | No — runs the two REAL live suites at the owner root | **Legitimate, not flaggable.** The task's whole purpose is to capture the pre-change failing set of THIS repo's THIS-moment suites (REQ-05/SC-14); a synthetic fixture cannot stand in for "what does this checkout's test suite say today." Not one of the dispatch's three named exemptions, but structurally forced the same way they are. |
| T-02 | N/A — this task builds the fixture | Fine |
| T-03 | Yes (`f58_sparse_fixture`); unit half uses canned data, no git | Fine |
| T-04 | Yes | Fine |
| T-05 | Yes | Fine |
| T-06 | Yes, plus a real-repo `grep` of tracked `bin/`+`hooks/` files to prove a chosen fixture dirname isn't hardcoded anywhere | **Real touch, but justified and cheap** — a static grep over a few dozen files, no worktree, no corpus read. Not flagged. |
| T-07 | Yes | Fine |
| T-08 | Yes (unit: canned; integration: fixture) | Fine |
| T-09 | Unit: explicitly canned rows ("never this repository's real records, which T-11 grades instead"). **Verify line**: `feature-index.py --check` runs against the REAL 79-record corpus | **Real touch not named in the dispatch's exemption list** — see EFF-1 below. Necessary (it's validating the artifact this task itself commits) but duplicates T-10 Part 3's real-data check. |
| T-10 | Parts 1–2: fixture. Part 3: named exemption (real 79 records) | Fine, as briefed |
| T-11 | Named exemption (the real-data act) | Fine, as briefed |
| T-12 | No test of its own (wiring only) | Fine |
| T-13 | Yes | Fine |
| T-14 | Yes (host-scale 3337/3807 figures cited as prose only, never asserted) | Fine |
| T-15 | Yes | Fine |
| T-16 | Yes | Fine |
| T-18 | Yes | Fine |
| T-19 | Fixture at the OWNER ROOT (not a worktree) for (a)/(c)/(d); clause (b) reads pre-change `check-state.sh` via `git show <merge-base>:...` — the dispatch's named exemption | Fine, as briefed. Note: T-19 does **not** build any worktree (correcting a premise in my own dispatch — see §3) |
| T-20 | No test file — a `git diff --name-only` over the real commit range | **Real touch, structurally required.** This audits the real repository's own history; there is no fixture equivalent for "what did this feature's commits touch." Not a `tests/` assertion, so outside D-11's stated scope anyway. |

Net: no task reaches for the real checkout where a fixture would have done the job. T-01/T-06/T-20
touch real state because their job IS to observe real state; T-09's verify is the one avoidable
real-repo duplication, costed in EFF-1.

## 2. Runtime per `verify:` (all 19)

Fixture is bounded under 100 tracked files (T-02 self-check) with a five-feature depth, so every
`git init`/`worktree add`/`sparse-checkout apply`/`merge`/`rebase` in these tests runs against a
repo three orders of magnitude smaller than the real corpus (3334 tracked feature files today).
None of the 19 approach "minutes"; only T-01 is a live real-suite run.

| Task | Verify shape | Est. cost | Basis |
|---|---|---|---|
| T-01 | Both live suites, owner root, 104 existing test files today (36 unit + 68 integration), via `run_pool.py` at 2–8 workers | **Unmeasured, plausibly tens of seconds** — the ONE deliberate full-suite boundary run in the plan | **NOT waste.** SC-14 requires a real pre-change failing SET; nothing else can produce it. I did not run this suite (prohibited by my scope) and the plan's own note format doesn't ask T-01 to record wall time — that's a reasonable omission, not a finding. |
| T-02 | 1 fixture build + 1 worktree + teardown | <1s | ~6 git calls (init/config/commit) + 1 worktree add |
| T-03 | unit (pure, no git) + integration: fixture + 6 broken-tree worktrees + idempotence run (2 repairs) | ~2–4s | ~7 worktree constructions |
| T-04 | fixture + 6 broken-tree rebuilds, each with before/after manifest+skip-bit capture | ~2–3s | 6 worktree constructions, no git operation heavier than `worktree add`/`ls-files -t` |
| T-05 | 1 sparse worktree + repair, per-path `os.path.isdir` checks | <1s | file-stat bound, not git-call bound |
| T-06 | fixture + new tracked dir + new worktree + real-repo grep | ~1s | 1 worktree, cheap grep |
| T-07 | fixture + worktree + 4 guard-hook subprocess invocations (2 refusal + 2 positive control) | ~1–2s | guard scripts are the heaviest single call here (~0.1–0.3s each), still sub-second aggregate |
| T-08 | unit (pure) + integration: 1–2 worktrees, one instrumented `open`/`glob` run | ~1s | instrumentation adds tracing overhead, not git cost |
| T-09 | unit (canned, <0.05s) + `feature-index.py --check` over real 79 records | <1s | one `git ls-files` + up to 79 small file reads; see EFF-1 |
| T-10 | integration ×2: 3 worktrees (deny/allow/inside-worktree) + real-data `--check` (no-op + mutated-copy) | ~2s | |
| T-11 | real-data read at `review_sha` (`git show` per record) + in-memory injection | <1s | single pass over 79 records, no worktree |
| T-12 | no own test; verify calls T-16's `test-hooks-install.py` | same as T-16's Part 2 | (sequencing note, not an efficiency cost — out of this angle) |
| T-13 | 2–3 worktrees (harness route, hooks-disabled route, bare `git worktree add`) | ~1.5–2s | |
| T-14 | 2 full scenario runs (post-change + pre-change repro): worktree, cross-branch commit, merge | ~2s | fixture-scale merge is cheap; the real 3337-line host cost this test exists to guard against is NEVER reproduced in the fixture, by design |
| T-15 | 2 scenario runs: worktree, commit, rebase, with/without hook | ~2s | same shape as T-14 |
| T-16 | unit (static, <0.1s) + integration: 3 shims × 2 conditions (missing-delegate / intact) = 6 git operations (checkout/merge/rebase) | ~3–4s | heaviest single integration file, still low single digits |
| T-18 | 2 audit runs (full checkout + sparse worktree) + 1 discrimination rerun | ~1.5s | |
| T-19 | owner-root: full materialisation + 2 audit runs (pre/post-change via `git show`) + `--verify` no-op + 3 hook-inertness operations (checkout/merge/rebase) ×2 (installed + discrimination-marker) | ~3–4s | no worktree built (see §1 table) |
| T-20 | one `git diff --name-only` over the pinned range | <0.5s | pure git plumbing over one feature's own commit range |

Aggregate: excluding T-01, the whole plan's new/changed `verify:` commands add on the rough order
of **30–40 total `git worktree add`-scale constructions** and on the order of a few hundred git
subprocess invocations spread across ~14 separate integration-test files, run independently
(parallelizable, and each already sub-5s on its own). This is not minutes, and it is not
concentrated on any single gate.

## 3. Repeated work across tasks

**T-03 vs T-04 — quantified, as asked.** T-03's `tests/integration/test-worktree-state.py`
constructs the six broken trees (wrong cone, skip-bits cleared, symlink absent, symlink
mistargeted, >1 feature dir, dirty tree) to assert `--verify`'s exit codes. T-04's
`test-worktree-state-norepair.py` constructs the **same six** broken trees again, independently,
to assert manifest-equality before/after `--verify`. That's 12 broken-tree constructions total for
6 distinct scenarios — 6 of them paid twice. Cost: ~6 extra fixture+worktree builds, roughly
**2–3 extra seconds of wall time total**, paid across two separately-run `verify:` commands, never
concurrently and never on a hot path. This is cheap in absolute terms; I'm reporting it because
asked to, not because it moves any runtime budget. Whether the two tasks *should* share one
construction pass is a SIMPLIFICATION-angle judgement (T-04 is deliberately its own task so a
repair gate can't quietly launder its own failure) — not mine to resolve. See EFF-2.

**Hook-install repetition — checked, and it's cheap.** T-13, T-14, T-15, T-16, and T-19 each
independently install T-12's three hook shims into a fixture's `core.hooksPath` (one `git config`
write + copying/linking 3 small files). Five occurrences, but each is on the order of single-digit
milliseconds — a git-config write and three file copies, not a worktree build. I priced this
suspecting it might be a real repeated-setup cost and it isn't: **under ~50ms total across all
five occurrences.** Not an efficiency finding. (T-19, unlike the other four, never builds a
worktree — its hook-inertness clause (d) runs checkout/merge/rebase at the owner root, not inside
a linked worktree — correcting a premise in my own dispatch.)

## 4. The index artifact — not a hot path, checked

`merge-gate.py` is registered on the `Bash` matcher in `.claude/settings.json`, i.e. it runs on
**every** Bash tool call, not only merges. But `main()` short-circuits at line 161 —
`if not github.get("sync") or not merge_ref(command): return` — before touching `feature_for()` or
the index at all. `merge_ref()` is a pure string/token check with no I/O. So T-10's index read only
executes when the Bash command actually parses as a merge (`git merge`/`gh pr merge`), which is
rare relative to total Bash calls, not per-session and not per-write.

When it does run, T-10's change makes this **cheaper than today**, not more expensive: today's
`feature_for()` globs and reads potentially many `feature.json` files; after T-10 it opens and
`json.load()`s a single 5848-byte file (measured, 79 rows). One file read, no loop over 79 files.

Nothing in the plan wires automatic regeneration (`feature-index.py` default/write mode) into any
hook or session-entry path — grepped the whole `.claude/skills` tree for callers of
`feature-index`, found none outside this plan's own task text. The generator is a build-time /
verify-time step only (T-09's own verify, T-10 Part 3's freshness test), never invoked on a request
path. I expected to find a hot-path cost here and didn't; saying so rather than inventing one.

## 5. The fixture's own bound — checked, right-shaped

T-02's `--self-check` bound (tracked file count `< 100`) is a strong discriminator against the
#1526 shape specifically: the real corpus this feature concerns itself with is **3334 tracked
files today** (measured, `git ls-files .harness/harness/features | wc -l`) — over 33× the fixture's
ceiling. A fixture that accidentally copied real content, even partially, would blow past 100
immediately; there's no plausible near-miss. The five-fake-feature-dir design plus the
`.agents`→`.claude` symlink (needed as T-05's two-spellings subject) puts the fixture's actual
tracked-file count in the range of roughly 15–30 files by my read of T-02's own build list, so the
100-file ceiling has generous headroom (4–6×) above what the fixture is expected to contain, while
still sitting nowhere near the real corpus's scale. Right instrument for what it defends against;
not tight, not slack in a way that weakens the guard. Not a finding.

## Findings

- **EFF-1** — severity: `low` — lands on: `T-09`, `T-10`
  Summary: T-09's own `verify:` and T-10 Part 3's `test-feature-index-regen.py` both invoke
  `feature-index.py --check` against the real 79-record corpus; the freshness proof is paid twice.
  Cost: 2 invocations instead of 1, each ~0.2–0.5s (one `git ls-files` + up to 79 small file
  reads) — under 1s of duplicated work total, not concentrated on any hot path.
  Alternative: T-09's verify could stop at its unit test (canned rows) and let T-10 Part 3 own the
  sole real-data freshness assertion, since T-09 already declares its unit test never touches real
  records "which T-11 grades instead" — the same separation-of-concerns move could apply to the
  `--check` call. Flagged as cost-only per my angle; whether to actually merge these two checks is
  a call for `harness-pm` / the SIMPLIFICATION reader, not me.

- **EFF-2** — severity: `low` — lands on: `T-03`, `T-04`
  Summary: T-04 rebuilds all six broken trees that T-03's own integration test already constructs,
  for the same six scenarios.
  Cost: 6 duplicated fixture+worktree constructions, roughly 2–3 extra seconds of total wall time,
  paid across two independently-run `verify:` commands (never concurrently, never hot-path).
  Alternative: a shared helper in `f58_sparse_fixture` that returns the six pre-built broken trees
  once, consumed by both T-03's assertions and T-04's before/after manifest capture — but this
  trades off against T-04's deliberate independence (so a repair path can't quietly launder its own
  gate's failure), which is a SIMPLIFICATION-angle call, not mine. Reporting the cost only, as
  asked.

No other findings. The plan's fixture discipline, verify-time cost, and the one new tracked
artifact (the index) are all sound on efficiency grounds.
</content>
<parameter name="i">Writing efficiency angle receipt for FEAT-58 plan simplify pass