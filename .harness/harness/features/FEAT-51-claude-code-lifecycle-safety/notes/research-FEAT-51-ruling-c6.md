# Ruling c6 — the fail-open task and the third panel reader

**Both rulings applied in ONE single-shot recreate. Every acceptance gate passes.** `plan.yaml` grew
exactly two hunks (`24a25,27`, `1062a1066,1235`; **173 added lines, 0 removed**); `BRIEF.md` gained
SC-13 only. All seven panel findings are byte-identical to the pre-change file and still
`disposition: open`; `resolved_by` occurs **0** times; no `approval` key; `## Approval` still
`status: pending`.

## Ruling 1 — T-10

- **id** `T-10`, `traces: [REQ-03, REQ-04]` (confirmed at `BRIEF.md:37-40` — REQ-03 no replacement
  parent dispatched into a live child's write; REQ-04 a live child's canonical writes quarantined).
- `change_type: cross_module`, `execution_mode: main-session-direct`, `depends_on: [T-03, T-07, T-09]`,
  `status: ready`.
- **files** (all four already in `lanes.rows`, all `main-session-direct`):
  `test-check-domain.py`, `test-plan-sign-gate.py`, `check-domain.sh`, `plan-sign-gate.py`.
- **verify** (literal `|`, 8 lines): six `grep -q` of the new label strings — three per test file,
  including each surface's `NEGATIVE CONTROL:` — then `python3 test-check-domain.py &&
  python3 test-plan-sign-gate.py`.

**Decision I took, and it is the one to challenge if any.** The two source files are in `files:` for
one bounded reason: T-03/T-07 place the `try` around the *import* with the registry calls written
after it, and that reading is ambiguous in their prose. If the handler encloses only the import, the
raising-call case is unreachable and the operator's ruling is undeliverable. T-10's intent permits
exactly one source edit — widening the **same existing** `try` to enclose `canonical_artifact` and
`orphan_write` — and forbids everything else (no new handler, no message change, no posture change).
A no-op if the landed code already encloses them.

## The mechanism, and how it was measured (2026-09-01, main checkout `2e2e45d2`)

`git hash-object` over `check-domain.sh`, `test-check-domain.py`, `plan-sign-gate.sh`,
`plan-sign-gate.py`, `test-plan-sign-gate.py`, `inflight_registry.py`, `harness_boundary.py`,
`harness_merge.py` is **identical at `ad93d43e`, at `2e2e45d2` and in the working tree**. Anchors hold.

- **Case A, the call raises** — the registry **path is a DIRECTORY**. `REGISTRY_REL`
  (`inflight_registry.py:33`) joined by `_registry_path` (`:39`), read by every predicate through
  `_update_registry` (`:82-97`) → `harness_merge.locked_update`. **Ran it:**
  `live_claim(root, "harness-pm")` raised `IsADirectoryError [Errno 21]` and it propagated out.
  Undone per case (own throwaway root, `shutil.rmtree` in `finally`). Uses the **real** module, so the
  real call site is exercised.
- **Two candidates measured and REJECTED, recorded in the intent so nobody retries them:** a
  *malformed* registry does **not** raise (prints `is corrupt or unparseable, treating as empty`,
  returns `(None, 0)` — T-02 specified behaviour); `.harness` at `0o500` does **not** raise either.
- **Case B, module unimportable** — `shutil.copytree(bin_dir, copybin)`, `os.remove` of
  `copybin/inflight_registry.py`, fire the **copied** hook directly. Reaches the import:
  `check-domain.sh:102` puts its own dir on `PYTHONPATH` and `:125` inserts it at `sys.path[0]`; the
  in-tree idiom at `test-check-domain.py:2370-2377` already proves a module in the copy dir is the one
  the copied hook imports, and `:1676-1703` (#556) proves nothing outside it can. For
  `plan-sign-gate.sh`: `_selfbin` at `:53`, `resolve_root` honours `HARNESS_PROJECT_DIR` when the
  override carries `MARKER` = `.harness/team-config.yaml` (`harness_boundary.py:41,64-68`), which both
  `test-plan-sign-gate.py:36 _root()` and T-07's `_qroot` write; `:60` execs the `.py` from the copy dir.
  **Ran it:** copy + no `inflight_registry.py`, and copy + raising stub, both returned the **same**
  verdict as the real hook (exit 0, empty stderr) on a governed in-domain write.
- **A trap found and written into the intent:** re-pointing the *whole* suite via `CHECK_DOMAIN_BIN`
  at a copy takes it from 251 ok / 0 FAIL to **250 ok / 1 FAIL** (`schema/a CRASHING schema module
  DENIES the write…`, which builds its own mutant relative to the real `HOOK`). Per-case direct fire
  has no such effect. The plan-sign surface is safe either way (45 ok / 0 FAIL through
  `PLAN_SIGN_GATE_BIN` at a copytree copy, with and without the module).
- **Two assertions per fail-open case** (exact exit `0`, never "not 2"; plus the stderr diagnostic),
  and **one negative control per surface** (healthy registry + live orphan claim → still exit 2).

## Ruling 2 — the third reader, as written

```yaml
    - reader: goalcheck
      status: ran
      persona: harness-pm
```

No `reason`. The two existing entries, `last_run: plan-panel-validator` and `cycle: 5` untouched.

## SC-13 — exact text is `BRIEF.md:196-214`

Graded at the reviewed sha via `git show <review_sha>:` on both test files. **Reddening mutations named
in the criterion:** (a) delete the two cases from **either one** file → `not_met` even though the other
file is green; (b) keep only the exit code, dropping the stderr half → `not_met`, because exit `0` alone
cannot separate a deliberate fall-through from a swallow; (c) bare `except` body that prints nothing →
the four stderr assertions red; widen the handler → both negative controls return exit 0.
`verify: automated`, `evidence: integration` — verified myself, not taken on faith: `integration` is
`status: active` with `cmd .agents/skills/harness/bin/run-unit-tests.sh --kind integration`, its
`detect` names **both** files, and both are in `run-unit-tests.sh` `INTEGRATION_SCRIPTS` (D-09).

## Gate results — exact

| # | Gate | Result |
|---|---|---|
|1|`plan-merge.py apply`|`APPLIED <abs path>`, **exit 0** |
|2|`check-plan-routes.py <abs plan>`|`0 violation(s) across 1 plan(s)`, **exit 0**. 5 DEVIATION lines (T-01, T-02, T-07, T-09, **T-10**) — the DEC-174 carve-out |
|3|`yaml.safe_load`|`safe_load OK`, exit 0 |
|4|panel|readers **3**, all `ran`, personas `fable-advisor / harness-code-reviewer / harness-pm`, each exactly `{persona, reader, status}`; findings **7**; dispositions `['open']`; `resolved_by` **0**; F-1 and VL-1 dicts identical to `/tmp/plan.pre.c6.yaml`; **all seven** identical |
|5|counts|tasks **10**, statuses `['ready']`; decisions **17**, identical; `status: plan`; `source_issues [280, 551]`; `lanes` identical (object equality **and** no diff hunk inside `62-131`); `approval` absent; BRIEF `status: pending` |
|6|REQ↔task|7/7 covered: 01←T-05; 02←T-01,T-06; 03←T-03,T-05,**T-10**; 04←T-02,T-03,T-07,T-08,T-09,**T-10**; 05←T-04,T-06,T-07,T-08,T-09; 06←T-01,T-05; 07←T-02,T-06. No task with empty `traces`, no trace citing a non-REQ. 13 SCs |
|7|T-10 `verify` verbatim, loaded from the plan|**exit 1**, empty stdout and stderr; each of the six greps individually exit 1 (`inflight_registry` occurs 0 times in `test-check-domain.py`, `test-plan-sign-gate.py`, `plan-sign-gate.py`). Tail conjuncts green today: 251 ok/0 FAIL and 45 ok/0 FAIL, both exit 0. The six greps are the whole discriminator and run first |
|8|`diff` vs pre-change|only `24a25,27` and `1062a1066,1235` — **173 added, 0 removed** |

## Write route

`plan.yaml` was byte-copied with `shutil.copy2` (never a YAML dumper) to `/tmp/plan.pre.c6.yaml` and to
`notes/plan-proposal-ruling-c6.yaml`; both edits spliced as **text** into the proposal via `python3`
heredoc through Bash — the known `check-domain.sh` gap that denies Edit/Write of a
`notes/plan-proposal-*.yaml` path, same route as cycles 4 and 5; canonical removed with `os.remove`
(absolute path); recreated with `plan-merge.py apply`. Applied file `diff`s **IDENTICAL** to the
proposal. `BRIEF.md` was a normal Edit.

## Open

- Nothing blocking. SR-2 stays `open` by instruction; T-10 is the coverage that answers it, and the
  disposition is the operator's call, not mine.
