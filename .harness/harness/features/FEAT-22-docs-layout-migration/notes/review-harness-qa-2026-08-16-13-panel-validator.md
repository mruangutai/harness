# QA gate — FEAT-22 · panel `qa` · extension pass · pinned e26e628

**VERDICT: PASS**, with one **medium** finding (J3) that changes the risk framing of an already-
accepted residual, and confirmation that T-07's plan-text defect (flagged in run 12) is cosmetic
— its substance holds.

This is an **extension** of run 12 (`notes/review-harness-qa-2026-08-16-12-qa-validator.md`), which
already PASSED the full matrix (unit exit 0/15 scripts/707 assertions, integration exit 0/12
scripts/652+ assertions) and probes 1–3. **Not re-run here.** This pass covers only the three
unprobed items the dispatch named.

## J1 — `test-gen-decisions-index.py` reshape, mutation pair (PRIMARY)

Baseline: `python3 test-gen-decisions-index.py` at HEAD → exit 0, 9/9 `ok`, 0 `FAIL`.

Both mutations built via in-memory `exec` of a modified source string (never a disk write — no
working-tree edit, confirmed by `git status --porcelain` at the end, clean).

**Mutation A — perturb the single shared `DOCS_DIR` constant** (`.harness/harness/docs` →
`.harness/harness/docs-WRONG`). Applied to `DOCS_DIR = os.path.join(...)` at line 23, confirmed
unique before mutating. Ran three of the derived tests directly against the mutated module:

| test | result |
|---|---|
| `test_row_per_distinct_dec_matches_authority` | **FAIL** — `FileNotFoundError` on the moved `REAL_DECISIONS` |
| `test_committed_index_matches_a_fresh_regeneration` | **FAIL** — `REAL_INDEX not found` |
| `test_committed_index_is_complete_and_within_budget` | SKIP (returns `True`) — this is the pre-existing, already-ruled `:361-363` FAIL / `:399-401` SKIP asymmetry (MF-2, file-absence-only skip predicate), not a new gap |
| `test_preserves_hand_written_rulings_by_dec_number` | **FAIL** — `generator exited 1: ... DECISIONS.md not found` — this is the **tmp-side** derivation (`make_authority`'s `docs_dir = os.path.join(tmp, DOCS_DIR)`, line 95), a distinct code path from the two `REAL_*` reads above |

Three of four reddened on the shared-constant move; the fourth's non-reddening is the accepted,
already-documented asymmetry, not new information. Between them these four cover **both** classes
of site the constant feeds — the two `REAL_DECISIONS`/`REAL_INDEX` reads and the tmp-side
`make_authority` join. **The shared constant is still live and load-bearing on every site class** —
moving it does not silently pass anywhere.

**Mutation B — perturb one derived site in isolation** (`REAL_DECISIONS` only, `DECISIONS.md` →
`DECISIONS-WRONG.md`, `DOCS_DIR`/`REAL_INDEX` untouched):

| test | result |
|---|---|
| `test_row_per_distinct_dec_matches_authority` | **FAIL** — `FileNotFoundError` on the renamed file |
| `test_committed_index_matches_a_fresh_regeneration` | **ok** — unaffected, as expected |
| `test_committed_index_is_complete_and_within_budget` | **ok** — unaffected, as expected |
| unperturbed control, same load mechanism | **ok** |

**Conclusion: the reshape did NOT trade five pinned sites for one unpinned one.** Mutation A shows
the shared constant is discriminating across both site classes it feeds (direct `REAL_*` reads and
the tmp-side `make_authority` join). Mutation B shows the one derived site it isolates
(`REAL_DECISIONS`) still reddens *independently* when only its own literal changes, and does not
spuriously redden sites it doesn't touch (`REAL_INDEX`-dependent tests stayed green). This is a
genuine mutation-proven result, not a reasoned one (O-03) — five named tests were run in-process
across the two mutations, covering four of the five derivation sites directly (`REAL_DECISIONS` ×2
read sites, `REAL_INDEX` ×1, tmp-side `DOCS_DIR` join ×1); the fifth derivation site (line 164's
tmp `docs_dir` inside `test_row_per_distinct_dec_matches_authority`) is covered transitively by
mutation A's first result, not isolated independently.

## J2 — execute plan.yaml:927's T-07 check, the intended form

| command | exit | meaning |
|---|---|---|
| `grep -n 'docs/harness' .harness/expertise/harness-backend-dev.md` | **1** | no match — clean |
| `grep -n 'docs/harness' .harness/expertise/harness-documentor.md` | **1** | no match — clean |
| `bash check-expertise.sh <both files, with args>` | **0** | `OK` on both |
| `bash check-expertise.sh` (argumentless, as `plan.yaml:927` literally invokes it) | **2** | `usage: check-expertise.sh <file-or-dir> ...` |

Confirms the dispatch's source reading exactly: `check-expertise.sh` with no argv exits 2, always,
regardless of tree state. **T-07's substance holds** — both files are genuinely clean and the
check, run with its intended arguments, is genuinely green. The plan-text defect (`plan.yaml:927`
omits the two file arguments) is **cosmetic**: the task's outcome is real and verified independently
here; the verify clause as literally written could never have confirmed it. This routes as a
plan-text correction, not as a re-open of T-07's deliverable — the risk this posed to the whole
gate (T-07 might have shipped broken) does not materialize.

## J3 — `test-check-domain.py:789`'s refused-direction `--resolve` case: rots QUIETLY, not loudly

Mechanism, established structurally then confirmed live:

1. Grepped the full file for every `r_live`/live-tree resolve assertion: **exactly one**
   (`:796-803`), and it asserts only the **positive** direction — `.harness/harness/docs/SPEC.md`
   resolves to `harness-documentor`. No live-tree assertion checks that any path is *refused*.
2. Every refusal-direction assertion in the suite (case (h) `:605`, T-04 resolve PAIR `:778-787`,
   case (i) `:611-622`, `(c) NOBODY` `:893-894`) runs against a **synthetic fixture**
   `team-config.yaml`, never the committed live one.
3. `ROOT` in `test-check-domain.py` (`:19`) is **hardcoded** to the real repo root with no env-var
   escape — unlike `HOOK`, which honors `CHECK_DOMAIN_BIN`. There is no way to point the existing
   live-tree case at an alternate team-config.yaml without editing the test file itself.
4. **Live reproduction, no working-tree write:** copied `.harness/team-config.yaml` into a scratch
   root, broadened harness-documentor's grant from `.harness/*/docs/**` to `.harness/**` in the
   copy only, then ran the real, unmutated `check-domain.sh --resolve` against it:
   - `.harness/harness/docs/SPEC.md` → `harness-documentor` (unchanged, sanity check)
   - `.harness/random-unowned-file.txt` → **`harness-documentor`** under the broadened grant
   - same path against the real, unmutated live root → **`NOBODY`** (control)

   The over-grant is real and reproducible. Because of point 3, **no test in the current suite can
   observe it** — the one live-tree assertion only checks one already-granted path, not any
   negative case, and it structurally cannot be repointed at a scratch config to catch a
   regression class like this.

**Finding, severity medium:** the accepted residual (missing direct refused-direction assertion)
is not merely thin — it is **structurally unwitnessable** by the current test architecture for any
regression confined to `.harness/team-config.yaml`'s live content (as opposed to `check-domain.sh`
itself, which fixture-based tests do cover). A glob broadened by accident on the live manifest —
exactly the shape of change this feature's own T-02 made — would pass this suite silently. This
elevates run 12's framing of the residual from "one assertion thin" to "this specific regression
class has zero live-tree coverage, by design of `ROOT`'s hardcoding." Not blocking this gate (the
residual was already ruled accepted), but the risk characterization changes and belongs in the
next plan revision that touches `test-check-domain.py`.

## DEC-174 — no fix drafted

`check-domain.sh` was read and run (unmutated) against a scratch copy of `team-config.yaml`; never
edited, not even transiently. No change is proposed to either enforcement-layer file here — the J3
finding is about test *coverage*, not about `check-domain.sh`'s own logic, so it does not trigger
the carve-out routing.

## Probe hygiene

All J1/J3 mutations ran via in-memory `exec` or against scratch-directory copies
(`/private/tmp/claude-501/.../scratchpad/probe-root/`). `check-expertise.sh` (J2) and
`check-domain.sh` (J3 control run) were executed, never edited. `git status --porcelain` at the end
of this run shows no change to any source, test, or carve-out file — the only new file is this
note and its paired observations entry, both inside qa's own domain.

## Findings summary

| id | severity | blocking | summary |
|---|---|---|---|
| J1 | — | no | mutation pair PASSED on both axes — reshape sound, no new finding |
| J2 | low | no | T-07 substance verified green; plan-text verify clause is cosmetically broken (already known from run 12) |
| J3 | medium | no (residual already accepted; risk framing changes) | the missing refused-direction assertion is structurally un-probable against live data, not just thin — a live team-config.yaml over-grant would pass silently |

No fix cycle spent.
