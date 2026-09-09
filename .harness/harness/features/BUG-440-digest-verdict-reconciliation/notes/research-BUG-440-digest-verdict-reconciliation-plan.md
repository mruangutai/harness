# Research — BUG-440 digest verdict reconciliation — plan input

**The contracted check is buildable as one insertion into the INV-15 branch, it is reachable, and it
turns the operator's state gate RED on day one with exactly 4 findings.** Everything below is
measured at `772790be52774eafe2971f9c44400e18b2d54275` unless stated.

## The measurement that shapes the plan

Run over the CONTROL-PLANE root (`/Users/molchairuangutai/GitHub/harness`), joining every
`feature.json` `runs[].id` to `runs/<id>/state.yaml`, filtering to `status: complete` and
`host` in the three leads, and comparing tail-anchored digest `VERDICT:` to `runs[].verdict`:

- 344 `runs[]` entries have a matching `state.yaml`; 298 are complete + lead-hosted + carry a
  `digest.md`; **all 298 pass `validate("lead", ...)`** — so "structurally valid" excludes nothing
  in practice and INV-15 is green on the corpus today.
- **4 mismatches**, and they are the defect the ticket describes:
  - `FEAT-25-claim-feature-root/runs/2026-08-19-6-distill-validator` — json `PASS`, digest `FAIL`
  - `FEAT-22-docs-layout-migration/runs/2026-08-16-15-distill-product` — json `INCOMPLETE`, digest `PASS`
  - `FEAT-22-docs-layout-migration/runs/2026-08-16-15-distill-validator` — json `INCOMPLETE`, digest `PASS`
  - `FEAT-07-verify-teeth-batch-probe/runs/goalcheck-product` — json `FAIL`, digest `ESCALATE`
- `INCOMPLETE` is not in `validate-digest.py`'s `VERDICTS` (`validate-digest.py:35`), so exact
  string equality is the right comparison and needs no extra branch to catch it.

**Consequence the operator must sign, not discover:** auto-repair is out of scope (grilling
"Out of scope"), so `/harness` entry is red until a human reconciles those 4 records. Disclosed in
BRIEF `## Constraints`; a reconciliation follow-up is an open question, not a task here.

## Run directories are untracked, which changes where evidence lives

The BUG-440 worktree's feature tree has **zero** `runs/*` directories (`FEAT-22` `feature.json`
lists 23 run ids, `runs/` is empty). Run state is per-checkout and untracked. So: the new check
cannot be graded against the real corpus from the build worktree, the positive fixture must be
**synthetic**, and no live lead digest is available to copy in a worktree.

## Where the code goes, and the two structures it must not disturb

- Host it in the existing INV-15 branch (`check-state.sh:1516-1535`) — `complete`, `_host in LEADS`,
  `digest.md` present and `_vd_mod.validate("lead", text)` empty are all already computed there. The
  digest text is already read for `validate()`; **reuse the local, do not re-read the file.**
- The `feature.json` `runs:` parse is a separate earlier loop (`check-state.sh:643-652`) whose
  comment pins `runs` as a 3-tuple because INV-7 and INV-22 unpack exactly three. The new check
  therefore needs **its own** side structure, exactly as `code_reviewing_runs` does at :644.
- Key that structure on the **feature directory path** (`os.path.dirname(fy)`), not the bare feature
  name: the INV-15 loop's glob is `H + "/*/features/*/runs/*/state.yaml"`, so two repos under one
  control plane could carry the same feature name.
- Join key: run-directory basename == `feature.json` `runs[].id`. Confirmed as the live convention
  (`FEAT-25`/`FEAT-22`/`FEAT-07` matches above were found by exactly that join).

## Tail-anchored semantics: there is no function to call

`validate-digest.py` inlines the two-step idiom **four** times (`:1155-1157`, `:1488-1490`,
`:1593-1595`, `:1795-1796`) and exports no extractor. Reuse is therefore: byte-identical regexes
cited to `validate-digest.py:1155-1160`, and the legal token set taken from `_vd_mod.VERDICTS`
rather than restated. A shared helper in `validate-digest.py` would be the deeper fix and is
**outside** BUG-440's approved surface — raised as an open question.

`validate("lead", ...)` rejects a digest with no `VERDICT:` line (`:1161-1162`) and one whose token
is outside `VERDICTS` (`:1163-1164`), so a structurally valid digest always yields a parseable,
legal token: **no unparseable branch is needed.** The dispatch's reading is confirmed.

## Test and verify mechanics, measured

- Baseline: `python3 tests/integration/test-check-state.py` exits 0, 216 lines, 0 `FAIL`, **51.9s**.
  Too close to the 60s bar for a task `verify:` under concurrent load, so the task verifies the ONE
  new case by importing the file and calling it: measured **0.58s** (proven by running the existing
  `case_bug1305_run_identity_invariant` through the same invocation — `exec_module` does not run
  `main()`, which is `__main__`-guarded at `:4789`). The full file is the qa gate's job.
- Fixture idiom to copy: `_bug1305_invariant_scaffold` / `_bug1305_invariant_feature`
  (`test-check-state.py:4502-4557`), one tree carrying every case, `run(tmp)` for exit+output.
- Red proof: `isolated_bin(dest_root)` (`isolated_bin.py:8-14`) copies the whole bin tree, so the
  pre-change `check-state.sh` runs with its sibling imports intact; point `CHECK_STATE_BIN`
  (`test-check-state.py:22`) at that copy. Never write the mutant into the live bin dir.
- New cases must be folded into `main()`'s final `and` conjunction (`:4775-4784`) or they are
  never run.

## Open questions

- Q1 (non-blocking): the 4 live mismatches — does the operator want a reconciliation ticket?
- Q2 (non-blocking): a 5th copy of the tail-anchor idiom vs. one shared extractor in
  `validate-digest.py` (out of this bug's surface).
- Q3 (non-blocking): `INV-37` is free — no match for `INV-37` or `INV-38` in `check-state.sh` or
  `tests/`; only those two files carry invariant numbers at all.
