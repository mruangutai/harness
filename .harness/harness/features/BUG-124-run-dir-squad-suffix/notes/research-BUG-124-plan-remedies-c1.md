# BUG-124 · plan cycle 1 · the five remaining panel remedies are applied

**All five landed. The plan is internally consistent, still parses, still carries `approval: pending`
and `status: plan`, and NO anchored literal-slug run-dir path survives in `BRIEF.md`, `plan.yaml` or
`STATE.md`.** Nothing was committed. One BRIEF.md success criterion was added (SC-09) and one line of
SC-01 was re-spelled; no other criterion changed.

## What landed, per finding

| # | finding | landed in | edit |
|---|---|---|---|
| 1 | residual high class (BRIEF SC-01) | `BRIEF.md` SC-01, line 65 only | anchor re-spelled `[.]harness/…/runs/eng-t01/digest.md` per D-05. Wording, `verify:`, `evidence:` untouched |
| 2 | `PF-05e45a58…` med | `plan.yaml` **T-01 `verify:` + T-01 `intent` TESTS** | live `len(g) == 3` → `g and all("/runs/" in x for x in g)`; live exact-forms list → `f and all(x.startswith("<task-or-purpose>-"))`. TESTS paragraph: live-count sentence → "every run-dir glob the live manifest yields contains /runs/"; live-forms sentence → exact assertion moved onto the synthetic invented-squad manifest, plus a new **DO NOT PIN THE LIVE MANIFEST** paragraph naming REQ-04 as the reason |
| 3 | `PF-64c48fa9…` med | `plan.yaml` **T-02 `intent`** (3 places) + **D-03 `because`** + `BRIEF.md` **SC-09** | derivation now (i) parses once through `harness_yaml.load_str` with no try/except, so it **exits non-zero on a broken derivation** while a grant-less manifest still exits 0 empty; (ii) its status crosses as `HARNESS_RUN_DIR_DERIVED`; (iii) THE CHECK prints **two non-interchangeable SKIPPED texts** (manifest declares no run-dir write grant / vocabulary derivation failed); (iv) new lettered case **(i)** after (h) exercises a garbage manifest and asserts each case carries its own text and not the other; (v) RED PROOF extended with the collapse-the-two-lines mutation. Fail-open behaviour unchanged — REQ-05 stands |
| 4 | `PF-4f1b6dc3…` med | `plan.yaml` **T-03 `verify:` + T-03 `intent`** | verify now binds the CLAIM: six required strings — `dispatch-guard.sh refuses`, `matches no run-dir write grant`, `at exit 2`, `and a compliant form`, `not on ownership by the dispatched persona`, literal `[.]harness/` — matched after `tr -s ' \t\n' ' '` so markdown wrapping cannot break a phrase. Intent's sentence one was amended so it literally contains all five prose strings, and a WHY THE VERIFY IS PHRASE-EXACT paragraph tells the doer not to reword without editing the task |
| 5 | `PF-6e184d4c…` low | `plan.yaml` **T-02 `intent`** | citation corrected at source: `check-domain.sh:103` runs `python3 -c` with `sys.path.pop(0)` feeding the program on stdin, and `:125` does `sys.path.insert(0, _bin_dir)` with `_bin_dir` from `sys.argv[3]`; the intent now says there is no `sys.path.insert(0, sys.argv[1])` at 103 and to copy the pop-then-insert-an-argument pair. Re-confirmed by reading the file |

D-03's `because` gained the orchestrator measurement dated **2026-09-07 at 6d969ed3** verbatim in
substance (`import yaml` succeeds under `/opt/homebrew/bin/python3`, `/usr/bin/python3` and
`PATH=/usr/bin:/bin python3`; `python3 -I -c "import yaml"` fails), and states the consequence: the
panel's blocking Q1 is **answered** and F-4 is an observability defect, not a dead gate.

## BRIEF.md changes — exactly two

- **SC-01, line 65 only**: `[.]harness/harness/features/<feat>/runs/eng-t01/digest.md`. Everything
  else about SC-01 is byte-identical.
- **SC-09 added** (`verify: automated  evidence: integration`): the skip reason is distinguished —
  each case asserts its own text present and the other absent. It is produced by **T-02 cases (e) and
  (i)**, and T-02 already traces REQ-05, so `traces:` needed no change and no new REQ was invented.

## Verification run (working tree, nothing committed)

- `harness_yaml.load_plan` parses: 3 tasks, 5 decisions; every task carries
  `id`/`verify`/`intent`/`change_type`/`traces`. `approval: {status: pending}`, `status: plan`.
- T-01/T-02/T-03 `verify:` are all literal `|` block scalars (checked by reading the scalar-style
  character out of the raw file, not the loaded value).
- Detector simulation (anchor on literal `.harness/`, slug class `[A-Za-z0-9._-]+`) over all three
  documents: **0 non-compliant sites.** Only anchored hit anywhere is `STATE.md`'s
  `runs/panel-record-product`, which is compliant. Positive control passes (a raw
  `runs/eng-t01` path is seen; the `[.]` form is not), so the clean result is not an empty search.
- T-01's `verify:` inner python program compiles and contains zero apostrophes.
- T-03's new `verify:` proven discriminating on a temp arm: FAILS on the pre-change tree (all six
  strings missing), PASSES on a copy carrying only the prescribed sentences **hard-wrapped mid-phrase**,
  and reddens again when the exit code is slipped to 1, and when the compliant-form clause is dropped.
- `check-plan-routes.py <plan>`: `0 violation(s) across 1 plan(s)`.
- Route used for every plan.yaml write: `plan-merge.py amend --expect-sha256 --value-file`, six
  amends, each exit 0. `apply` was not usable here — it exits 7 CONFLICT on a changed value, and all
  five remedies change existing values rather than adding ids. The `panel:` block, `approval:` and
  `status:` were not written by any of them.

## Open, for the tier above

- Panel dispositions still read `open` for the five findings remedied here. pm does not own
  `disposition:`/`resolved_by:` transcription in this batch (the dispatch forbids touching them), so
  the panel/lead must flip `PF-05e45a58…`, `PF-64c48fa9…`, `PF-4f1b6dc3…`, `PF-6e184d4c…` to
  `resolved` with `resolved_by: T-01/T-02/T-03` before signature, or the plan reads as carrying four
  live med/low findings.
- T-02 now specifies a second parse of `team-config.yaml` inside the derivation subprocess. That is
  deliberate (it is the only thing that makes breakage observable, since `run_dir_grant_globs` never
  raises) and it is one small file read per governed dispatch.

## GC1-N2 closed — SC-01 is no longer self-refuting (BRIEF.md only)

SC-01 kept the escaped trigger path (it is a quotation, so D-05 applies) and gained one clause
saying so: the `[.]` is the D-05 escape, the producing case restores the real `.harness/` anchor
with the `q.replace("[.]", ".")` idiom the plan's own `verify:` lines already use, and it is the
restored path the prompt carries. The slug `eng-t01`, the exit-2 assertion, the stderr assertion and
the `verify: automated        evidence: integration` line are byte-identical; no other criterion was
touched (`BRIEF.md:64-70`).

- Detector simulation re-run over `BRIEF.md` (anchor literal `.harness/`, repo/feature/slug class
  `[A-Za-z0-9._-]+`, compliance = trailing `-product|-eng|-validator`): **0 non-compliant sites.**
  Positive control on `runs/goalcheck-plan-product/digest.md` reports its 1 known BAD site
  (`eng-t01`, line 11), so the clean result is not an empty search. The added clause's bare
  `.harness/` carries no `/runs/` segment and is invisible to the pattern.
- `git diff` for `BRIEF.md` shows two hunks: SC-01's body (this edit plus the earlier escape
  re-spelling) and the SC-09 addition made earlier this cycle. The three other modified paths in
  `git status` — `feature.json`, `plan.yaml`, `observations/harness-pm.md` — predate this edit and
  were not opened by it. `approval: status: pending`, `status: plan`, nothing committed.
