# SIMPLIFY — ALTITUDE angle — FEAT-38-decisions-current-knowledge

Diff `7ebfc9e..384b800`. Read-only. One finding rises above the bar; two are advisory
backlog rows.

## Q1 — Right home? `check-decision-anchors.py` / `check-decision-claims.py` as standalone scripts

**`leave`.** Correct as is; folding either into `gen-decisions-index.py` would break more than
it fixes:

- The generator's exit code today means exactly one thing — "the committed index disagrees
  with what regeneration would produce" (or an ORPHAN row). Anchor rot and claim failure are a
  *different question with a different remedy*: re-run the generator fixes index drift; it does
  nothing for a citation that names a file the tree no longer has. One exit code carrying both
  meanings would teach an operator to reflexively regenerate on red, which silently does not
  address rot.
- `gen-decisions-index.py`'s model (`parse_decisions`/`build_index`) only ever computes
  **heading line numbers** for the index's own `@<line>` token. It never scans free-text
  `` `file:line` `` citations anywhere in decision bodies — a structurally unrelated artifact.
  Folding anchor-checking in would force every `--stdout` preview call (today a pure
  string-transform, no subprocess) to also shell out to `git ls-files` and stat every cited
  file's line count — coupling a lightweight preview path to filesystem/subprocess cost it does
  not need today.
- This feature's own T-06/T-10 just *removed* generator-computed machinery (supersession,
  amendments) in favor of plain prose + small standalone checkers (`gen-decisions-index.py`
  diff, lines `-149..+8`). Folding a new compute-heavy check back into the generator reverses
  the exact simplification this diff just made.

## Q2 — One authoritative statement per rule, or several that can drift?

| Rule | Sites | Authoritative | Drift? |
|---|---|---|---|
| Decision heading grammar | `gen-decisions-index.py:28` `^##\s+(DEC-(\d+))\b` (feeds parsing/refs/tags/freshness); `check-decision-claims.py:50` `^##\s+(DEC-\d+.*)$` (feeds only the heading *label* printed on a claim failure) | `gen-decisions-index.py:28` | **Yes — two independent regex literals for the same grammar.** Currently equivalent in what they match, but nothing ties them together (see finding F-2). |
| `DECISIONS.md`/docs-dir location | `gen-decisions-index.py:24-25`, `check-decision-anchors.py:39-40`, `check-decision-claims.py:47-48` — three literal `os.path.join(".harness","harness","docs")` + `"DECISIONS.md"` pairs, each commented "mirrors gen-decisions-index.py's own constants exactly" | `gen-decisions-index.py:24-25` | **Yes — three copy-pasted literals, comment-asserted equal, nothing tests it** (see finding F-3). |
| Legal index tags | `gen-decisions-index.py:31-56` `TOPIC_VOCAB` | same, single site | No — one statement, not restated anywhere else I found. `leave`. |
| What makes an index row stale | Documented once, in `gen-decisions-index.py`'s own module docstring (`--stdout \| diff -`); not restated in `harness.json`, `.github/workflows/tests.yml`, or `run-unit-tests.sh` | same, single site | No duplicate statement — but see **F-1**: the *rule* is single-sourced, the *enforcement* of the analogous rule for the two new checkers does not exist as a standing gate at all. |

Note: `check-decision-anchors.py`'s "anchor" (a `` `file:line` `` citation in prose) and the
index row's `@<line>` token are two *different* concepts sharing one English word. Not a
duplicate statement of one rule — no drift risk — but worth a naming callout if a future reader
conflates them. Not filed as a numbered finding (naming is the Simplification reader's angle,
not mine).

## Q3 — Wiring altitude (per new script, cited to the array)

- `test-check-decision-anchors.py` — **executed.** `run-unit-tests.sh:31` (`INTEGRATION_SCRIPTS`),
  run via the loop at `run-unit-tests.sh:150` (`python3 "$BIN_DIR/$s"`). Also present in
  `harness.json:119`'s `integration.detect` glob (classification only, not execution).
- `test-check-decision-claims.py` — **executed.** Same array (`run-unit-tests.sh:31`), same loop,
  same `harness.json:119` detect entry.
- `check-decision-anchors.py` itself (the checker, not its test) — **never executed by the
  runner.** It is not a member of `UNIT_SCRIPTS` or `INTEGRATION_SCRIPTS` (only `test-*.py` names
  populate those arrays; the drift detector at `run-unit-tests.sh:61` only globs `test-*.py`
  under `BIN_DIR`, so the checker itself is structurally ineligible for that list). Its only
  callers are its own test (against a **synthetic** fixture, per `test-check-decision-anchors.py`'s
  own docstring) and manual runs recorded in receipts.
- `check-decision-claims.py` itself — **never executed by the runner**, same reasoning. Only its
  test calls it, and only against a synthetic fixture (`test-check-decision-claims.py`'s own
  docstring: "never against the live document").

So: the runner proves the checker *logic* (each behavior, each exit code, the refusal path) but
never proves the checker *finds anything wrong in the actual `.harness/harness/docs/DECISIONS.md`*
on any registered, automated cadence. See F-1.

## Q4 — Accepted residuals

**F-1 (BLOCKING → `briefing-row`).** DEC-205 states, as the rule's own compensating control:
"A checker re-runs every marker in the suite, so the claim fails when the tree moves under it"
(`DECISIONS.md:6285`). This is not true of the wiring as built. "The suite" (`run-unit-tests.sh`)
only re-runs `test-check-decision-claims.py` and `test-check-decision-anchors.py`, and both of
those exercise their checker exclusively against **synthetic fixtures written to a tempdir**
(explicit in both files' module docstrings) — never against the live
`.harness/harness/docs/DECISIONS.md`. No script in `UNIT_SCRIPTS`, `INTEGRATION_SCRIPTS`,
`check-state.sh`, or `.github/workflows/tests.yml` invokes either checker with no `--file` (i.e.
against the real document) as part of any automated gate. Contrast with the generator's own test
suite one file over: `test-gen-decisions-index.py` copies the **real** `DECISIONS.md` into its
tempdir fixtures (`shutil.copy(REAL_DECISIONS, …)`, lines 159/782/804) and directly opens
`gdi.DECISIONS_PATH` for structural assertions (line 837) — an established sibling pattern the
two new checkers' tests do not follow.
  - **Cost, concretely:** a future edit that rots a `` `file:line` `` citation, or breaks an
    `ALLOWED_FIRST_TOKENS`-style claim marker, produces a fully green `run-unit-tests.sh` and a
    fully green CI. The only way either kind of rot is ever caught is a human choosing to run
    `check-decision-anchors.py` / `check-decision-claims.py` by hand — exactly what two
    documentor receipts in this feature did once, manually, during authoring (T16, T21), and
    exactly the failure mode DEC-205 says these two checks exist to close.
  - **Alternative:** add one registered gate that runs each checker with no `--file` against the
    live document and asserts exit 0 — e.g. a small integration test alongside
    `test-gen-decisions-index.py`'s live-copy pattern, registered in
    `INTEGRATION_SCRIPTS` and `harness.json`'s `integration.detect`, the same two-site pattern
    T-18 already used to register the unit-test wrappers.
  - Filed as `briefing-row`, not `fold-in`: closing it needs a new test file plus two-site
    registration (mirroring T-17/T-18's own task shape) — more than the apply step's one-fix
    ceiling should absorb here, and it deserves its own verify block rather than riding on this
    pass.

**F-2 (advisory → `briefing-row`).** `check-decision-claims.py:50`'s `HEADING_RE` independently
restates the heading grammar that `gen-decisions-index.py:28` already parses authoritatively, to
label which `## DEC-N` heading precedes a failed claim marker. No test ties the two patterns
together. Cost: low — today they agree, and a mismatch would only degrade an error-message label,
never the exit code. Alternative: import (or otherwise share) `gen-decisions-index`'s `HEADING_RE`
instead of re-declaring it.

**F-3 (advisory → `briefing-row`).** `DOCS_DIR`/`DECISIONS_REL_PATH` is spelled out as an
independent literal in three files (`gen-decisions-index.py:24-25`,
`check-decision-anchors.py:39-40`, `check-decision-claims.py:47-48`), each with a
"mirrors ... exactly" comment but no import and no test enforcing the mirror. Cost: a future docs
reorg needs three synchronized edits; missing one fails loudly (`sys.exit(2)`, unreadable target)
rather than silently, bounding the blast radius, but it's still three places to remember instead
of one. Alternative: both checkers import the path constant from `gen-decisions-index` instead of
re-declaring it.

## Priority for the apply step (ceiling of one fix)

**F-1 first.** It is the only finding that is *wrong in the tree as it stands* — a signed
decision's stated compensating control does not exist in automation — versus F-2/F-3, which are
merely improvable duplication with bounded, loud failure modes. F-1 is filed as `briefing-row`
rather than an immediate apply because its fix is a new test file plus two-site registration, not
a single-file edit; F-2/F-3 are also `briefing-row` and smaller than F-1, so none of the three is
recommended for this pass's one-fix apply.
