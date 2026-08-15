# Goal-check c1 — FEAT-05 PyYAML file parsers — at `b3aa413`

**The blocker is closed. SC-04 is met, SC-03 is met, SC-14 is met on a stricter loader. 13 of 14
SCs met. The one thing still below the line is SC-02, and it never hinged on the fallback** — it is
bookkeeping (two unrecorded run dirs), not a parser defect. Verdict `FAIL` on that one criterion,
because looping back is meaningful: record or prune the two dirs and it flips.

Bookkeeping: `feature.yaml:7` pins `review_sha: f0a3831`, not `b3aa413` as the dispatch says.
`b3aa413` changes only that scalar, so no code differs and no verdict moves.

## SC table

| SC | verify | verdict | evidence |
|---|---|---|---|
| SC-01 | automated | **met** (carried) | untouched by `f0a3831`/`b3aa413`; `test-check-state.py` green in the 12-suite run. |
| SC-02 | inspection | **partial — unchanged, and it never hinged on the fallback** | Re-measured at HEAD: `check-state.sh` exit **0**, **41** notes = **39** "referenced but its dir is absent" + **2** "run dir exists on disk but feature.yaml does not record it" (FEAT-05's own `2026-08-03-01-validator`, `-05-validator`). Byte-identical to cycle 0. SC-02's stated shape is "INV-8 notes about pruned run dirs **only**"; two orphan notes are a different invariant. The load-bearing half (exit 0, zero violations) holds. The cycle-0 remedy — record or prune — was not done. |
| SC-03 | inspection | **met** (re-checked) | Full census re-run over the six named scripts at HEAD. `check-state.sh` **7** (`:63 :64 :67 :93 :95 :106` markdown; `:501` over parsed dict keys) — the approval-Q2 answer key exactly. `gh-sync.py` 6 (markdown + `:264` over parsed keys + `re.escape`), `upgrade-config.py` **0**, `check-domain.sh` **7, all over `rel` (a path string) or glob compilation — zero over YAML content**, `bash-write-guard.sh` 4 (heredoc/paths/globs), `cost-report.py` 2 (`:114` path, `:196` the `^cost:` **writer**, sanctioned by D-04). The cycle-0 exception, `check-domain.sh:319`'s `re.findall` over `content`, is **gone**. |
| SC-04 | inspection | **met** (re-checked, see the two clause rulings below) | `check-domain.sh:327` is now bare `if _no_parser: sys.exit(0)`. No `re.` call anywhere in the six scripts touches `.yaml` file content. Nothing was moved: `f0a3831` is net −16 lines of code and adds no scan elsewhere (`git show --stat`), and I read every `_no_parser` site rather than grepping for regex. |
| SC-05 | automated | **met** (re-checked) | `test-check-domain.py` 11/11 + 27/27 at HEAD; `fire()` inherits env, bare `python3`, no `PYTHONPATH` override. Re-checked because `f0a3831` edited this file. |
| SC-06 | automated | **met** (carried) | `bash-write-guard.sh` and its test untouched by both commits. |
| SC-07 | inspection | **met — the cycle-0 blemish is now resolved, verified not accepted** | `harness-init/SKILL.md:49` "there is no line-scan fallback anywhere in `bin/`" and `CLAUDE.md:19` are **true at HEAD**: the only surviving parser branches are `check-domain.sh:257` `if not _no_parser: domain_check()` (skip), `:327` `sys.exit(0)` (skip), `bash-write-guard.sh:292` `sys.exit(0)` (skip). All three **stop work**; none does the work a second way. I read all three bodies. |
| SC-08 | automated | **met** (re-checked) | `test-check-domain.py:304,308` still asserts the install command on the parsed `systemMessage` channel, not merely stderr. Green at HEAD. |
| SC-09 | uat | **met — the pass still stands** (carried, with reason) | `harness_yaml.py` is **not in the `f0a3831` diff**, so `require_or_bootstrap`, `_marker_path` and `_resolve_identity` are byte-identical to what I diffed in cycle 0. The expiry mechanism U-05 exercised is untouched. No re-run required. |
| SC-10 | automated | **met** (carried) | `test-harness-yaml.py` untouched, green in the 12-suite run. |
| SC-11 | inspection | **met** (carried) | `test-gh-sync.py` untouched by both commits; the cycle-0 label-vs-invocation audit stands. |
| SC-12 | automated | **met** (re-checked) | `run-unit-tests.sh` at HEAD: exit **0**, **12 PASS**, **0 FAIL**, 0 MISCONFIGURED, 0 skip lines. ≥ the 9-suite baseline. |
| SC-13 | inspection | **met** (carried) | The only `.harness` change since cycle 0 is one scalar (`review_sha`), which is not a run id. The run inventory is unchanged — corroborated by the check-state re-run producing the identical 41 notes. Cycle 0's honest limit (FEAT-03/04's "before" side is a post-repair baseline) still applies. |
| SC-14 | automated (unit) | **met — and the cycle-0 hole is genuinely closed** | Gate now calls `harness_yaml.load_file`. 10/10 checks pass, 12 files scanned, 6 negative fixtures. I re-derived the loader claim rather than accepting it: `safe_load` **ACCEPTS** both `cost: 1\ncost: 2` and the nested `cost:` duplicate while `harness_yaml` raises `DuplicateKeyError` on each — so the two new fixtures pin the loader swap specifically, and would have gone RED under the old gate. |

## REQ coverage — both cycle-0 partials re-derived

REQ-02 (SC-01), REQ-03 (SC-07), REQ-04/05 (SC-08, SC-09), REQ-06 (SC-10), REQ-07 (SC-02, SC-13):
traced, unchanged from cycle 0.

- **REQ-08 — now MET.** Cycle 0 held it partial solely on SC-14(b). The duplicate class is really
  covered: measured, `safe_load` accepts both new fixtures and `harness_yaml` rejects both.
- **REQ-01 — MET, by an explicit carve-out, not by omission.** Cycle 0 held it partial on two
  counts. `check-domain.sh:319` is gone. The survivor, `cost-report.py:196`'s `^cost:` splice, is
  carved out by **D-04 (writers stay line-based)** plus the BRIEF `## Approval` note's **Q1
  ruling**, in which the user recorded that `cost-report.py` parses nothing into values and stays
  in scope as a *writer*. REQ-01's clause bites on **read** paths, and there are none left. Had the
  user ruled the other way this would still be partial — the carve-out is the reason, so it is
  cited rather than assumed.

## The two SC-04 clause rulings, written down rather than assumed

Cycle 0's finding turned on rejecting a reinterpretation of a signed constraint invented in the
commit that needed it. These two are reinterpretations too, so the reasons go on the record.

1. **Clause 3, "no branch selected on parser availability," read literally is violated five times
   at HEAD** — and must be, because REQ-05, SC-08 and the Constraints **mandate** a one-session
   bootstrap escape, and no escape can exist without branching on parser availability. Clause 3
   cannot be read to forbid what other signed clauses require. The governing sentence is SC-04's
   own first line: *no second parse path for the same data*. All five branches skip; none parses.
   This is compelled by the signature, not carved out of it.
2. **`check-domain.sh:284-294`, the `feature.yaml` line/comment budget, is note-not-violate.** It
   is a text scan of YAML content with no `re.` call — proof that a regex census alone is not
   sufficient evidence, which is why I read the branches. It extracts **no values**, runs
   **unconditionally** (not under `_no_parser`), and predates `f0a3831`. Not a second parse path.

## Can the three new assertions pass while their claim is false? — partly, and here is where

The question was asked because six of this feature's non-discriminating tests were the author's.
Answer: the trio is sound, but **only one of the three pins the removal**, and there is one real
residual.

- **`grant: a malformed state.yaml is ALLOWED` (`rbad.returncode == 0`) is the discriminator.**
  Under `fire_noyaml` (PYTHONPATH-shadowed `yaml`), exit 0 on that path is reachable *only* via
  `if _no_parser: sys.exit(0)`. Re-add any fallback and this case goes RED. It is the regression
  guard on the ruling.
- **`with a parser, the shape gate still BLOCKS` is NOT a discriminator for the removal** — it held
  before the fallback existed, while it existed, and after. It is a regression guard on the
  parser-present path, which is worth having, but it does not pin `f0a3831`. Its stderr assertion
  does discriminate against a *domain* denial: `DEC-154` appears at `check-domain.sh:336` and
  `:360` only, both inside the shape gate; the sibling `deny()` at `:276` prints DEC-150.
- **The residual, measured not inferred.** A duplicate-key finding renders as
  `('.harness/probe.yaml', "duplicate key 'cost' — …")` — **file and key, no line:column**. SC-14
  requires "naming file, line and column", and corpus case 7 asserts the message shape only against
  a flow-comment fixture, whose `problem_mark` survives. So the newly-covered duplicate class is
  detected but under-diagnosed. Non-blocking; SC-14 stays met. Closing it means carrying the
  offending key node's mark into `DuplicateKeyError`.
- The negative cases assert `len(nb) == 1`, not the error *type*. That is tolerable only because
  corpus case 1 (12 real files parse) and case 6 (a well-formed file is NOT flagged) fail loudly if
  the loader starts erroring on everything. Noted so nobody deletes either.

## What still gates, and what would settle it

- **SC-02 — the only thing below met.** Record the two FEAT-05 run dirs in its `feature.yaml`, or
  prune them. Either makes the output match the stated shape. This is bookkeeping and was already
  named in cycle 0; it is not a parser defect and it never was.
- **Unverifiable from where I sit: nothing this cycle.** Q4 stands — `harness-pm` cannot write a
  scratch tempdir from Bash (`> $TMP/...` is refused by the write guard). It did not bind here: the
  loader comparison ran in-memory via a heredoc and the fixture scans ran inside the test's own
  `tempfile.mkdtemp`. It would bind on any check needing a persistent on-disk fixture tree.

## Process notes

- `f0a3831` is a code change to the enforcement layer landing **after** all four review artifacts
  and after qa-c1 — the fifth such commit in this feature. It carries regression tests (green), but
  no independent eyes. That is a ship-decision input, not an SC.
- `check-docs.sh` exits **0** and now has nothing to catch: the two "no line-scan fallback"
  sentences it failed to flag in cycle 0 are true at HEAD.
- `feature.yaml:11` records `cost_usd: 240.82` against a signed, unraised `per_feature_usd: 120`.
  Reported, not gated (DEC-134) — flagged here because the BRIEF's budget line is now stale.
