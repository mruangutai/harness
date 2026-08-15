# FEAT-15 domain-product-base — mutation and coverage probe

Gate check: `git merge-base HEAD main` = `812294854160002065a92417761509a3c995e732`, matches
`review_sha` line 2. Proceeded. `check-domain.sh` at e057525 is byte-identical to the current
worktree (`diff` exit 0), so all measurements below are against the live tree.

## (1) Mutants — scratch copy only, never the repo

Methodology note: a naive `cp` of `bin/` alone breaks `ROOT` derivation (`test-check-domain.py`'s
`ROOT = HERE/../../../..`) and several live-tree cases (T-04 LIVE-tree resolve, `(h)` hook-path
case) fail for reasons unrelated to any mutation. Fixed by reconstructing the directory depth in
scratch (`.../repo-mut/.claude/skills/harness/bin/`) with `.harness`, `docs`, `README.md`,
`.github` **symlinked** (read-only) back to the real repo, and running from `repo-mut/` (not from
inside `bin/` — cwd affects relative-path resolution in the hook). Confirmed unmutated copy green:
98/98, exit 0. Confirmed no contamination of the real repo (`git status`/`git diff --stat` clean
on `.harness`, `docs/harness/SPEC.md`, `README.md`, `.github` throughout).

- **(a) `:244` product-base target-side test → `is_control_plane_target` — KILLED.**
  Contrary to the dispatch's hypothesis. `<workspace>/widget/docs/guide.md` DID redden:
  `C product base: ... README 0, docs/guide.md 2, .github 0 (all want 0)`. Also killed
  `(f)`/`(g)` PAIRs and the T-04 resolve PAIR. **This is the gating result: REQ-06/SC-13's
  product half is measurably covered, not vacuous as the dispatch worried.**
- **(b) `:582` delete `_glob_filter` from `applicable_shared` — SURVIVED**, as hypothesized. All
  eight `shared:` entries are dependency manifests with no control-plane first segment; no fixture
  or live manifest falsifies the filter's removal.
- **(c) `:637` `_shared_advertise` → `[]` in the harness-base branch — SURVIVED**, as hypothesized.
  Nothing asserts the advertised-shared-list text.
- **(d) `:243` `max(..., key=len)` → `next(...)` — SURVIVED**, as hypothesized. No fixture nests one
  declared repo's checkout under another's path.
- **(e) `HARNESS_CONTROL_PLANE` widen `docs/harness/**` → `docs/**` — KILLED**, by
  `C harness base: docs/harness/** was NOT widened to docs/**`. Verified the assertion fires
  against `DOC` — the same persona granted `docs/harness/guide.md` above — never against `OPS`
  (the `.github/**` persona); confirmed by reading `test-check-domain.py:719-729`.
- **(f) own choice — SURVIVED.** Inverted the `if base == _abs_root:` branch that selects which
  globs are advertised in the `Permitted for you:` rejection line (line 632). Exit codes are
  unaffected, so the full suite stays green; **no automated test asserts the content of
  `Permitted for you:`** (`grep -c "Permitted for you"` on the test file = 0), and SC-12 is
  `verify: inspection` only. This is a real gap the plan's three-case summary does not name: a
  regression that only miswords the advertised-domain line in the harness base ships silently.

## (2) Pair C vacuity

Pair C's product-base half (`test-check-domain.py:731-739`) asserts **exactly three exit-0s**
(`widget/README.md`, `widget/docs/guide.md`, `widget/.github/workflows/ci.yml`), each fired with
the persona that IS granted that path. **No exit-2 assertion exists in Pair C's own fixture/
manifest on the product side** — no attempt, e.g., to fire `OPS` (granted only `.github/**`)
against `widget/docs/guide.md` and expect refusal. In isolation, Pair C alone cannot distinguish
"product base correctly matched" from "product base branch unreached, fell through to no-verdict
exit 0." This is a real adequacy gap in Pair C specifically — separate from whether mutant (a)
survived (it didn't: Pair C did catch that particular defect, because the mutant produced a wrong
exit-2, not because Pair C has a negative control). The suite's overall protection against a
silently-permissive product base comes from Pair A / SC-01 elsewhere, not from Pair C.

## (3) SC-07 enumeration

`git diff 812294854160002065a92417761509a3c995e732..e0575259cac0694d6452f54c9ca52d664c6f07c5 --
.claude/skills/harness/bin/test-check-domain.py`, scanned for every removed/changed `case`/`t12`/
`fleet_case`/`check` line carrying an exit-code literal:

| Kind | Case | Before | After |
|---|---|---|---|
| expectation change | `a shared path is allowed and serialized` → renamed `a shared path in the harness base is now REFUSED (product-shaped target)`, `<ROOT>/package.json` | exit 0 | exit 2 |
| path repair (expectation unchanged, exit 0) | `SC-05 pair: permitted allowed AND forbidden blocked, one manifest` | `allowed/thing.md` | `.harness/allowed/thing.md` |
| path repair (expectation unchanged, exit 0) | `the marker self-unlinks once PyYAML imports again` | `allowed/d.md` | `.harness/allowed/d.md` |

Exactly these three; no other removed line in the diff carries an exit-code literal — confirmed by
grepping the diff for `^-.*case(|t12(|fleet_case(|check(` patterns, which returns only the
`package.json` line. No regression beyond the three named changes.

## (4) Attack #5 — `shared:` narrowing cost, measured

Reconstructed both SHAs' `check-domain.sh` via `git show`, alongside unchanged (confirmed
byte-identical across the range) `harness_yaml.py`/`factory_config.py`/`factory_cli.py`. Ran
`--resolve <path>` for every one of the 534 files in `git ls-files` under both versions, with
`CLAUDE_PROJECT_DIR=<real repo root>` and stdin closed, diffing `(stdout, exit code)` pairs.

**Result: 0 diffs across 534 tracked files.** The affected set is empty — confirmed, not argued.
SC-11's claim ("no live harness file loses a route") holds as measured at e057525.

## (5) Suite and matrix

- `python3 .claude/skills/harness/bin/test-check-domain.py` at e057525: **exit 0**, 98/98.
- `bash .claude/skills/harness/bin/run-unit-tests.sh` (no `--kind`, the full run) at e057525:
  **exit 0**, includes `test-check-domain.py`'s 98 cases plus `test-factory-integration.py`
  (97/97) and `test-no-distribution.py`.
- **Confirmed, not just repeated from the BRIEF:** `bash .claude/skills/harness/bin/run-unit-tests.sh
  --kind unit` exits 0 (`ALL PASS`) and its output contains **zero** mention of check-domain —
  `test-check-domain.py` is claimed by `harness.json`'s `unit` detect glob
  (`.claude/skills/harness/bin/test-*.py`) but is actually run only under `--kind integration`'s
  `INTEGRATION_SCRIPTS` bucket. `--kind unit` alone would report green on this feature without
  executing a single FEAT-15 case. This is a pre-existing, already-flagged harness.json
  detect/runner disagreement (not introduced by this feature) — confirmed live rather than
  assumed.
- Matrix: T-01..T-04 declare `test_kinds: [unit, integration]`, `change_type: cross_module`. Each
  task's own `verify:` (`python3 .../test-check-domain.py`) is what actually exercises the change
  and it passes. The `unit` label is nominal only — real coverage lives under `integration`,
  matching every SC's declared `evidence: integration`. T-05 (`change_type: docs`, `test_kinds: []`)
  verified via `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md`: ran clean, no diff.

## SC evidence

- SC-01/02/03: `test-check-domain.py` PAIR A/B, `(f)`/`(g)`/`(h)` fleet cases — all named above.
- SC-04: `(i) a path under workspace_root for an undeclared repo is refused, naming the fleet`.
- SC-05/SC-06: `(a)+(b) PAIR` / `(c)` fleet cases.
- SC-07: enumerated above — the diff table.
- SC-09: `T-04 resolve PAIR` case.
- SC-10: `run-unit-tests.sh` exit 0, confirmed above.
- SC-13: Pair C — but see the vacuity finding in (2): the product-base assertions inside Pair C
  are exit-0-only and cannot alone rule out a NO-VERDICT product branch; mutant (a) happened to be
  caught, but not by a negative control within Pair C itself.
- SC-08, SC-11, SC-12: `verify: inspection` — not exercised by an automated test; SC-12's message
  content specifically has zero automated coverage (see mutant (f)).

## Coverage gaps (Phase-1 vs Phase-2 delta)

- No automated assertion on refusal message content (`Permitted for you:` line) — SC-12 relies
  entirely on inspection, and mutant (f) shows a real regression in that text ships silently.
- Pair C carries no negative control on the product side (finding (2)).
- `--kind unit` false-green confirmed live, not merely repeated from the BRIEF.

None of these are new regressions introduced by this diff; all are pre-existing or
inspection-only gaps, consistent with what the BRIEF's own "Verification gaps" section already
disclosed — confirmed here rather than assumed.
