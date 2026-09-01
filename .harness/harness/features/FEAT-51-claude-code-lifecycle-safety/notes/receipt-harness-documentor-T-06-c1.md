# Receipt — T-06 — DEC-210 recorded, index regenerated

**PASS.** `DEC-210` is appended last in `.harness/harness/docs/DECISIONS.md` (68 lines, at :6489),
its index row is hand-ruled and carried through a second generation, and T-06's `verify:` exits 0.
All ten claim groups were checked against the tree at HEAD `f260b5f`; none required an escape.
`DEC-210` was free on both this branch and `main`'s tip.

## Verify output — exit 0

T-06's `verify:` run verbatim from the worktree root. Clauses 1–2 (last-entry greps for
`plan-sign-gate.sh` and `plan-merge.py`), clause 3 (`DEC-210` in the index) and clause 4
(`--stdout | diff -q`) produced no output, which is their pass condition; clause 5 printed:

```
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_refs_graph_omits_ids_with_no_live_heading
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
ok - test_committed_index_matches_a_fresh_regeneration
ok - test_committed_index_is_complete_and_within_budget
ok - test_orphaned_ruling_is_reported_not_silently_dropped
ok - test_root_resolves_through_harness_boundary_not_the_retired_variable
ok - test_no_amendment_construct_survives_in_the_authority
===== VERIFY EXIT=0 =====
```

Clauses 1–2 verified as matching **inside DEC-210's own body**, not elsewhere: within the awk-isolated
last-entry buffer, `plan-sign-gate.sh` at buffer lines 23 and 30, `plan-merge.py` at 24, 31 and 50.
The buffer's line 1 is `## DEC-210 — …`, confirming DEC-210 is the last entry.

Baseline before any edit: clause 1 matched 0 times, clause 3 matched 0 times, clause 4 already clean.
The task was not pre-landed.

## Claim-by-claim provenance

All paths relative to the worktree root. Anchored on names, not line numbers, where the name is stable.

| # | Claim | Checked at |
|---|---|---|
| 1 | Three answers; `SUSPENDED` only in `hook_mode`, not in `VERDICTS` | `.claude/skills/harness/bin/validate-digest.py` — `hook_mode()` at :1565; suspension branch :1662–1680; refused terminal verdict :1711–1727; `VERDICTS = {"PASS","FAIL","BLOCKED","ESCALATE"}` at :35. `SUSPENDED` occurs only at :1662 and :1704, both inside `hook_mode` |
| 2 | A suspension does not release the parent's claim | same file: accepted suspension `return 0` at :1680 sits **ahead of** `_reg.release(...)` at :1687; comment :1682–1683 states it |
| 3 | WRITE boundary, not a kill; `notes/`, `observations/`, `runs/` untouched | `.claude/skills/harness/bin/check-domain.sh:1683–1703`; the branch keys on `inflight_registry.canonical_artifact`, whose `_CANONICAL_ARTIFACT_RE` (`inflight_registry.py:24-26`) full-matches the four artifact paths only, so any other path returns `None` |
| 4 | Four canonical artifacts, two registered gates named by script | `CANONICAL_ARTIFACTS` at `inflight_registry.py:23`. Registration read from `.claude/settings.json`: `check-domain.sh` PreToolUse matcher `Write|Edit`; `plan-sign-gate.sh` PreToolUse matcher `Bash`. Verbs: `MUTATING_VERBS` at `plan-sign-gate.py:34`, `ADOPT_TOOL`/`ADOPT_VERB` at :35/:39, decision at :318–319 |
| 5 | `plan.yaml` covered by the Bash half; FEAT-41 denial is separate and keeps its message | `check-domain.sh` — plan.yaml editor-route denial header at :1529, its `sys.exit(2)` at :1678; the quarantine branch begins at :1683, i.e. **after** it, so the denial fires first |
| 6 | Not covered: `quarantine.py discard`; generic Bash write in-domain | `plan-sign-gate.py:36-38` records discard's deliberate omission and the `rm -rf` reasoning. `bash-write-guard.sh:18` — "in-domain and unparseable pass". `check-domain.sh` PreToolUse registration is `Write|Edit` only (`.claude/settings.json`). Plan decisions `D-18`, `D-19` carry the same statement; D-19's `because` also notes a `harness-dev-ops` exemption in `bash-write-guard.sh` |
| 7 | Adoption and discard are the only explicit acts; plan.yaml adoption via locked union | refusal text `plan-sign-gate.py:412-413` and `check-domain.sh:1700-1701` both say adoption is the resumed parent's act; `plan-sign-gate.py:402-406` distinguishes the adopt tool. DEC-199 named for the locked union |
| 8 | One shared sandbox glob, not twelve grants | `.harness/team-config.yaml:79`, under `shared:` (:77). `grep -c 'features/\*/quarantine'` = **1** |
| 9 | OMP unchanged; boundary fires only on non-`omp` runtime | `inflight_registry.py` — `orphan_write` :291-314, gate is `has_compatibility_claim and not writer_is_live` where `has_compatibility_claim` is `any(claim.get("runtime") != "omp" …)` at :304-306; `_expire` :215-220 keeps OMP claims on process ownership (`_omp_claim_live`), never on the clock; `_visible` :257 retains the session filter for non-OMP only |
| 10 | Honest bound: no durable child owner, TTL 1200s, fails safe | `inflight_registry.py:29` `CLAIM_TTL_SECONDS = 1200`, with the comment at :27-28 stating Claude Code exposes no durable child-process owner and FEAT-37 shortened it to one PM cycle; TTL expiry applies only on the non-OMP branch at :221 |

`DEC-174`'s citation was re-grounded rather than transcribed: its ruling is that hooks, validators and
gate scripts are changed **directly**, not executed through the harness (`DECISIONS.md:4271`, ruling at
:4305-4308, layer table row 3 at :4299). The entry therefore cites it for the layer these three scripts
belong to and their per-gate test scripts — `test-check-domain.py`, `test-plan-sign-gate.py`,
`test-validate-digest.py`, all present under `.agents/skills/harness/bin/` — and **not** for
route-completeness, which DEC-174 does not say.

## Index

`refs:` computed by the generator from the entry body: `DEC-174 DEC-182 DEC-199 DEC-201 DEC-204`
— exactly the five required. Tags `[plan,domain,gates,state]`. Anchor `@6490`.
Hand-written ruling is 28 words / 153 non-whitespace characters, inside the
20-char floor and 30-word cap that only `test-gen-decisions-index.py` asserts. Index is 210 lines
against a 260-line budget. Because DEC-210 is the last entry, no later row's anchor shifted, so the
index diff is a single added line.

Generation order followed exactly: append → generate (row appeared as `⚠ RULING PENDING`) → hand-write
the ` :: ` tail → generate again. Second run carried the ruling forward and left `--stdout | diff -q`
clean.

## Files touched

`.harness/harness/docs/DECISIONS.md` (+68), `.harness/harness/docs/DECISIONS-INDEX.md` (+1), and this
receipt. `plan.yaml` was already modified at spawn and is not mine. Nothing committed; HEAD unmoved at
`f260b5f`.

**One incident, recorded because the record must be honest.** The first attempt at the DECISIONS.md
append landed in the **main checkout**, not this worktree: the edit used a repo-relative path and the
process cwd is the main checkout, while the two copies of `DECISIONS.md` were byte-identical so the
content-derived snapshot tag matched in both and gave no signal. Detected by the generator writing no
DEC-210 row, then by `git status` in both trees. The misplaced block was one clean 68-line insertion at
:6489 with main otherwise clean, so it was cut back out by exact range; `git diff --stat` on main's
`.harness/harness/docs/` now emits zero bytes. Every subsequent file operation used an absolute path.
