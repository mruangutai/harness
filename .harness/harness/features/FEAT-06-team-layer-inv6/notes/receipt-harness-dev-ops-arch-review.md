# Receipt — harness-dev-ops — S-1 repo-state verification at 635ef14

Read-only sweep. Repo HEAD confirmed `635ef147e9a003fbea6745443311fafb1d5f1970`. Working tree has
unrelated dirty files (`.harness/logs/2026-08-04.md` modified, this feature's own untracked dir,
and an untracked perf note) — none touch a path this sweep checks, so working-tree reads were used
throughout (no `git show` needed).

## A — receipt path grants (FALSIFIES the PLAN's premise)

| id | result | observed |
|---|---|---|
| A1 | VERIFIED | `team-config.yaml` has exactly 5 `receipt-*` grants, one per **FULL** agent name: :144 `receipt-harness-frontend-dev-*.md`, :158 `receipt-harness-backend-dev-*.md`, :171 `receipt-harness-ai-dev-*.md`, :184 `receipt-harness-data-engineer-*.md`, :199 `receipt-harness-dev-ops-*.md` |
| A2 | FALSIFIED (the PLAN's SHORT-form premise) | `receipt-dev-ops-T-01.md` (SHORT) matches **none** of the 5 grants — the pattern literally requires the `receipt-harness-` prefix. `receipt-harness-dev-ops-T-01.md` (FULL) **does** match the :199 grant. The PLAN's template renders `{{persona}}` from the SHORT list (`personas: [frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops]`), which produces exactly the non-matching form. |
| A3 | VERIFIED | `check-domain.sh:228-229` (glob match → allow), `:231-236` (shared match → allow, warn), `:242-248` (no match → BLOCKED, `sys.exit(2)`, prints permitted globs). An unmatched path under `.harness/features/*/notes/` is **BLOCKED**, not allowed — there is no notes/-wide catch-all grant observed in A1. |
| A4 | VERIFIED, but not as asked — no `outputs:`/artifact field exists in either file | Both `.harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-09-eng/state.yaml` and `.../2026-07-31-10-eng/state.yaml` record `persona:` per step but **no output/artifact path at all** (fields present: `id, persona, depends_on, mutates_repo, dispatched_at, completed_at, status, verdict, cycles, members_spawned, note`). Where persona appears it is the **FULL** agent name (`harness-dev-ops`, `harness-backend-dev`), never the short form. No cycle marker on any artifact path either, because no artifact path is recorded here. |

**A is the load-bearing finding**: the PLAN's template renders paths that do not match any existing
grant, and the enforcement hook blocks unmatched paths outright (not a soft warning). Whether this is
a bug in the PLAN's template or a needed grant addition is an architecture call, not mine.

## B — qa artifact-path collision

| id | result | observed |
|---|---|---|
| B1 | VERIFIED | Actual `qa*` files under `.harness/features/*/notes/`: `FEAT-03-subissue-mirror/notes/qa-FEAT-03-c0.md`, `FEAT-04-decisions-index/notes/qa-matrix-c1.md`, `FEAT-05-pyyaml-file-parsers/notes/qa-c0.md`, `FEAT-05-pyyaml-file-parsers/notes/qa-c1.md` (plus `FEAT-02/notes/qa-FEAT-02.md`, outside the requested three but present). **Zero** `review-harness-qa-*` files exist anywhere in the repo. |
| B2 | VERIFIED, but `review.yaml` has no `qa` step | Its 3 steps are `code`, `security`, `ui` — none named `qa`. Outputs: `:26` `review-harness-code-reviewer-c{{cycle}}.md`, `:40` `review-harness-security-reviewer-c{{cycle}}.md`, `:53` `review-harness-ui-reviewer-c{{cycle}}.md`. A `qa` step, if it exists, is defined elsewhere (not in `review.yaml`). |
| B3 | VERIFIED | `team-config.yaml:226` `{ path: .harness/features/*/notes/qa-*.md, upsert: true }` (comment: "assessments; the 3 reviewers each own one, qa owned none"), `:227` `{ path: .harness/features/*/notes/review-harness-qa-*.md, upsert: true }` (comment `# Q6`). Both grants exist, distinctly, one line apart. |

## C — T-10's hard-coded deletion claim

| id | result | observed |
|---|---|---|
| C1 | VERIFIED | `grep -rn 'gate-probe' .claude/ \| wc -l` → **3**, all three in **one file**: `.claude/skills/harness/teams/gate-probe.yaml` (lines 21, 43, 45 — `name: gate-probe`, and two comment-string mentions of the `# gate-probe:` PR-comment token). |
| C2 | VERIFIED — no hits anywhere else | `gate-probe` appears in none of `docs/harness/SPEC.md`, `check-docs.sh`, `run-unit-tests.sh`, or any file under `.claude/skills/harness/bin/`. |
| C3 | VERIFIED | `ls -1 .claude/skills/harness/teams/` → exactly 2 files: `gate-probe.yaml`, `review.yaml`. |

## D — placeholder-vocabulary single-source claim

| id | result | observed |
|---|---|---|
| D1 | VERIFIED | 1 match: `validate-digest.py:472` — `if field in NULLABLE and isinstance(val, str) and val.lower() in ("none", "null", "n/a"):` |
| D2 | VERIFIED — no such constant exists in `harness_yaml.py` | Module-level constants found: `INSTALL_COMMAND` at `:293`; import guard at `:17-20` (`try: / import yaml / except ImportError: / yaml = None`). No placeholder-vocabulary constant (`none`/`null`/`n/a` or similar) defined anywhere in `harness_yaml.py` — grep for the literal returns zero hits in that file. |
| D3 | VERIFIED | `:24` `PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}" python3 - "$root" <<'PY'`; `:27` `import harness_yaml`; `:136-141` the `val(k)` helper (`def val(k): ... v = doc.get(k); return None if v is None else str(v)`); `:156` `if any(sq == "validator" for _, sq, _ in runs) and not val("review_sha"):` |
| D4 | VERIFIED | `:472` quoted above under D1; `:46` `NULLABLE = {"branch", "blocked_on", "briefing",` (opens the set, DEC-173 additions continue on following lines); `:728` `if __name__ == "__main__":` |
| D5 | VERIFIED — no precedent exists | Searched all 12 `test-*.py` scripts for subprocess/grep-the-repo patterns: none invoke `grep` as a subprocess against repo files for a self-referential literal. `test-gh-sync.py` and `test-upgrade-config.py` contain the word "grep" but only inside embedded shell fixture strings / prose comments, not as a self-scan. **No existing test establishes a pattern for grepping the repo for a literal the test itself contains** — this would be new territory, not precedent-backed. |

## E — corpus gate and unit runner

| id | result | observed |
|---|---|---|
| E1 | VERIFIED | `run-unit-tests.sh:6` `SCRIPTS=(...)` includes both `"test-harness-yaml-corpus.py"` and `"test-check-state.py"` (12 entries total). `:9-22` is the drift detector: any `test-*.py` under `BIN_DIR` not in `SCRIPTS` → `exit 2` "MISCONFIGURED". |
| E2 | VERIFIED, minor line offset from claim | `scan()` def starts `:55` (not 56) with docstring `:56` and body `:57-58` — functionally as claimed. Call sites (`grep -n 'scan('`): `:55` (def), `:110`, `:138`, `:144`, `:149`. `check(...)` calls: `:111` `check(f"every .harness YAML parses ({n} files scanned)", not bad, ...)`, `:113-114` `check("the corpus is not empty (a glob that matches nothing passes vacuously)", n > 0, f"scanned {n} files under {os.path.join(REPO, '.harness')}")`. `_fixture` helper `:82-88` (claim said 83-86; body is 83-88, def line 82). |
| E3 | VERIFIED | `load_file(path)` defined at `:205` in `harness_yaml.py`; duplicate-key rejection happens in the custom loader's `_construct_mapping` (`:146-150`, raising `DuplicateKeyError` at `:149` on a repeated key), which `load_str` (called by `load_file`) uses via `_StrictSafeLoader`. |
| E4 | VERIFIED — both team YAML files currently FAIL `harness_yaml.load_file` | Ran `harness_yaml.load_file()` directly (read-only import, no write): `.claude/skills/harness/teams/review.yaml` → `YamlParseError` at `:26:33` "expected ',' or ']', but got '{'"; `.claude/skills/harness/teams/gate-probe.yaml` → `YamlParseError` at `:32:37` "expected ',' or ']', but got '{'". **Neither is covered by the corpus gate** — `scan()` only globs under `<root>/.harness/**`, and these team files live under `.claude/skills/harness/teams/`, outside that glob. The corpus test currently gives no signal on these two files. |
| E5 | VERIFIED | `test-check-state.py:152-153` states the pre-fix failure mode (INV-6/7/8 failed open at exit 0); `:160-167` is the temp-root mechanism: `tempfile.TemporaryDirectory()`, builds `<tmp>/.harness/features/FEAT-TEST/`, writes `harness.json` and `feature.yaml` fixtures, then `run(tmp)`. |

## F — contract check

| id | result | observed |
|---|---|---|
| F1 | VERIFIED | `gates.qa_gate: "blocking"`. `test_matrix`: `logic: {"always": ["unit"]}`, `config: {"always": []}`, `docs: {"always": []}`, `bugfix: {"always": ["unit"], "when": [{"kind": "__bug_class__", "if": "match_bug_class"}]}`. `test_kinds` entries with `cmd: null` (6 of them, all tagged `"unset — dev-ops has not run detection yet"`): `functional`, `integration`, `component`, `ui`, `eval`, `typecheck`. |

## Bottom line

- **A is the finding that most directly bears on the PLAN**: SHORT-form persona rendering produces
  receipt paths that no grant matches, and unmatched paths are hard-blocked (exit 2), not soft-warned.
- **B's premise holds** — both grants (`qa-*.md` and `review-harness-qa-*.md`) exist distinctly, one
  line apart, but no `qa` step currently exists in `review.yaml`, so which step (if any) is meant to
  target the second grant is not resolved by what's on disk today.
- **C is confirmed as stated** — `gate-probe` is fully contained to its own team file; nothing else
  references it.
- **D1–D4 confirmed**; **D5 found no precedent** for a self-referential repo-grep test — if the PLAN
  proposes one, it would be a new pattern, not an established one.
- **E4 is a new finding, not asked for by name in the brief's framing but load-bearing**: both
  `review.yaml` and `gate-probe.yaml` currently fail to parse via `harness_yaml.load_file`, and the
  corpus gate does not see either file because its glob is scoped to `.harness/`, not
  `.claude/skills/harness/teams/`.
