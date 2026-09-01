# QA gate — BUG-1128-plan-amend-verb — panel c3 — review_sha `20775866`

**BLUF: FAIL.** All three FEAT-46 targets round-trip byte-identical (identity replace, then a
real non-identity replace touching exactly the named field). All author evidence claims
reproduce exactly (244/0, run-unit-tests.sh 0 FAIL, check-state.sh's one violation is INV-29 on
BUG-1129, not this feature's). Cycle 1's decisive gap — `_verify_amend`'s value comparison, the
keystone that demotes wrong-field writes to refusals — is **now pinned**: `case_amend_v3_identity_check_is_live`
fails when the comparison is mutated out. But my own, independently-derived mutation table finds
one **surviving mutant on the load-bearing under-lock hash re-check** (`plan-merge.py:1281`) —
the SAME gap cycle 0's panel found, unfixed and unpinned three cycles later — plus two narrower,
fail-closed `_trim_tail`/`_render_field` edge-case gaps, plus the carried, already-known
`case_amend_refuses_an_unknown_key` vacuity.

## Job 1 — FEAT-46 acceptance: does it do the real job?

Copied `FEAT-46-decision-standard/plan.yaml` (2490 lines) to a scratch `.harness/harness/features/…`
path under `/tmp/qa-c3-scratch/` (never touched the tracked worktree; confirmed via
`git status --porcelain` at the end — only sibling reviewers' artifacts present, nothing of
mine). Ran real `amend` against the COPY for `decisions:D-05.because`, `decisions:D-14.because`
(`--key decisions`), `tasks:T-01.verify` (`verify: |` block).

**Methodology note, disclosed because it produced a false negative on the first pass.** My
first attempt reconstructed the captured `--show` value with `stdout.split("\n")` +
`"\n".join(...)`, which silently drops the value's own final `\n` whenever it lines up with the
`sha256:` line boundary — a bug in the harness script, not the tool. That version reported
`T-01.verify`'s identity replace as **REFUSED** (rc=5, value one byte short). Rewritten to slice
on `stdout.rfind("sha256: ")` instead (preserving every byte before that marker, matching what
`test-plan-merge.py`'s own `case_amend_n3_show_round_trips_into_value_file` does via
`splitlines()` + per-line `"\n"` re-append) — all three targets round-trip clean:

| target | captured sha256 | identity replace rc | struct-identical (`yaml.safe_load` before==after) | byte-identical (raw file) |
|---|---|---|---|---|
| `decisions:D-05.because` | `32f1422c…` | 0 | **True** | **True** |
| `decisions:D-14.because` | `48219d6c…` | 0 | **True** | **True** |
| `tasks:T-01.verify` (`verify: \|` block) | `f1b91e9f…` | 0 | **True** | **True** |

Then a real **non-identity** replace of `D-05.because` (new value, real hash from the identity
run): rc=0, `diff` shows **exactly one hunk** — the `because:` line — every other line, including
sibling `D-06`, byte-identical. `yaml.safe_load` confirms the new value lands exactly.

**The `--show → --value-file` round trip N3 was written for works, for all three of FEAT-46's
own staged targets, byte-identical.**

## Job 2 — author's evidence, verified literally

| claim | author said | observed at `20775866` |
|---|---|---|
| `test-plan-merge.py` | 244 PASS / 0 FAIL | **matches** — exit 0, 244 PASS lines, 0 FAIL lines |
| `run-unit-tests.sh` (full) | exit 0, 0 FAIL lines | **matches** — exit 0, `grep -c '^FAIL'` → 0 across 3829 lines |
| `check-state.sh` | exactly one violation, `INV-29` on `BUG-1129-validate-handoff-sweep` | **matches, first run** — `VIOLATION INV-29` naming `BUG-1129-validate-handoff-sweep` exactly, nothing else. I created no scratch worktree this cycle (mutation testing used a `PLAN_MERGE_BIN`-env-var copy under `/tmp`, per cycle 2's precedent and the dispatch's own instruction not to touch git worktrees), so there is no self-caused pollution to disclose or re-run past |

## Job 3 — vacuity audit of every `case_amend_*`

**Verified by mutation this cycle** (my own mutants, §Job 4 below; each named case is the ONLY
one that fails for its targeted mutant unless noted):

- `case_amend_v1_block_scalar_body_is_not_scanned_for_keys` — caught by M4, M5
- `case_amend_v2_identity_replace_of_a_block_field_round_trips` — caught by M4, M5, M7
- `case_amend_v3_identity_check_is_live` — **caught by M1** (removing `_verify_amend`'s value
  comparison). This was cycle 1's N2 finding (vacuous, tautological guard, SyntaxError-discriminating
  mutant). The case was rewritten this cycle to call `_verify_amend` directly — **it is no
  longer vacuous.** The keystone is pinned now.
- `case_amend_v4_unparseable_base_refuses_cleanly` — caught by M15 (confirmed the case uses the
  real sha256, not a dummy one — a dummy-hash variant would be vacuous, per cycle 1's own
  disclosure; the real fixture is not)
- `case_amend_n5_do_no_harm_branch_is_live` — caught by M11 (branch removed) and M12 (branch's
  *condition* inverted to always-enforce, which breaks nearly every other case since most
  fixtures are schema-invalid — confirms the do-no-harm direction is pinned too)
- `case_amend_n1_adjacent_comment_and_blank_survive` — caught by M6, M3b
- `case_amend_n1b_a_comment_inside_a_block_body_is_CONTENT` — caught by M2, M5, M7, M9
- `case_amend_n3_show_round_trips_into_value_file` — caught by M4, M5, M7
- `case_amend_duplicate_id_is_refused` — caught by M14

**Vacuous, confirmed by mutation — unchanged, carried from cycle 0 and cycle 1:**

- `case_amend_refuses_an_unknown_key` — M13 (the entire `AMENDABLE_KEYS` gate replaced with
  `if False:`) leaves the suite at **0 FAIL**. `approval:` remains structurally unreachable
  through `_item_range` (flat mapping, no `- id:` line) regardless of the gate, so the case's
  refusal comes from a different code path and proves nothing about the allowlist itself. Same
  defect, same evidence, three cycles running.

**Read only, not independently mutated this session** (content-asserted — not
substring/exit-code-only — and consistent with cycle 0/1's own mutation-cross-checked adequacy
table, which found each of these bound and non-overlapping):
`case_amend_show_reports_block_and_hash`, `case_amend_replaces_a_multiline_decision_field`,
`case_amend_refuses_a_stale_hash`, `case_amend_requires_the_hash`,
`case_amend_refuses_absent_id_and_lists_what_is_there`, `case_amend_refuses_absent_field`,
`case_amend_preserves_comments_elsewhere`, `case_amend_value_round_trips_through_yaml`,
`case_amend_value_yes_stays_a_string`.

## Job 4 — independent mutation table (own mutants, never reused the author's six)

Method: copied `plan-merge.py` alone to `/tmp/qa-c3-mut/base.py`, mutated, ran `test-plan-merge.py`
with `PLAN_MERGE_BIN=<mutant>` and `PYTHONPATH` pointed at the real `bin/` dir (no worktree
created or removed). Every mutant compile-checked (`python3 -m py_compile`) before running;
none discarded.

| id | unit / line | mutation | result |
|---|---|---|---|
| M1 | `_verify_amend` (:361) | remove the `if item.get(field) != want: raise` value comparison | **CAUGHT** — 2 FAIL (V3 case) |
| M2 | `_trim_tail` (:1064) | ignore `comments_are_document`, always trim trailing `#` | **CAUGHT** — 2 FAIL (N1b) |
| M3 | `_trim_tail` (:1061) | stop trimming a trailing **blank** line for a **block** scalar only | **SURVIVES — 0 FAIL** |
| M3b | `_trim_tail` (:1061) | stop trimming a trailing blank line for a **plain** scalar (dispatch's own ask) | **CAUGHT** — 2 FAIL (N1) |
| M4 | `_find_field_line` (:1109-1112) | remove the block-scalar skip entirely | **CAUGHT** — 4 FAIL (V1, V2, N3) |
| M5 | `_block_scalar_end` (:1036) | indent comparison `<=` → `<` | **CAUGHT** — 5 FAIL (V1, V2, N1b, N3) |
| M6 | `_plain_scalar_end` (:1123) | boundary comparison `<=` → `<` | **CAUGHT** — 2 FAIL (N1) |
| M7 | `_render_field` (:1165-1173) | remove block-header reuse, route everything through `_field_lines` | **CAUGHT** — 3 FAIL (V2, N1b, N3) |
| M8 | `_render_field` (:1168) | remove the trailing-newline strip before `body.split("\n")` | **SURVIVES — 0 FAIL** |
| M9 | `_dedent_value` (:1086) | `body_indent = len(indent) + 2` → `+ 1` | **CAUGHT** — 3 FAIL (N1b, N3) |
| M10 | `transform`, under-lock hash re-check (:1281-1283) | disable (`if False:`) | **SURVIVES — 0 FAIL** |
| M11 | do-no-harm branch (:1301-1305) | replace whole branch with `pass` | **CAUGHT** — 2 FAIL (N5) |
| M12 | do-no-harm condition (:1301) | invert to always-enforce regardless of base validity | **CAUGHT** — 14 FAIL (widely, most fixtures are schema-invalid) |
| M13 | `cmd_amend`, `AMENDABLE_KEYS` gate (:1238) | disable (`if False:`) | **SURVIVES — 0 FAIL** (= Job 3's carried finding) |
| M14 | `_sole_item` (:337-340) | remove duplicate-id check | **CAUGHT** — 3 FAIL |
| M15 | `transform`, base-parse try/except (:1263-1268) | remove; `base_doc = None` | **CAUGHT** — 3 FAIL |

### Surviving mutants — what each means

**M10 is the decisive finding.** `plan-merge.py:1281`'s own comment calls this "the check that
is actually load-bearing" — it closes the read-to-write TOCTOU window the pre-lock check cannot.
Disabling it entirely leaves all 244 assertions green. **This is the identical gap cycle 0's
panel found** (qa-c1.md item 2: "Under-lock hash re-check … replaced with `if False:`: exit 0, 0
FAIL … A regression here … would ship green") **and it has never been remediated in three
cycles.** Every fix since has addressed content/location/boundary correctness (V1-V4, N1-N5);
none has touched concurrent-write coverage. A regression that silently trusted only the pre-lock
hash — exactly the TOCTOU shape #628 exists to prevent — would ship green today.

**M3 and M8 are a narrower, related pair, both fail-closed, not corrupting.** Live-reproduced
against the M3/M8 binaries directly (not via the suite): a `verify: |` block whose body is
followed by a blank line before the next sibling field —
```
verify: |
  do stuff

status: ready
```
— under M3, `--show` reports the value WITH the trailing blank line (`'do stuff\n\n'`), which
does not match what `yaml.safe_load` actually returns (`'do stuff\n'`, YAML `|` clip-chomping
strips it); an identity write is then correctly **refused** by `_verify_amend` (fail-closed).
Under M8 (multi-line block value, no trailing blank), an identity replace SUCCEEDS at exit 0 and
`_verify_amend`'s value check passes — but the on-disk file gains a spurious blank line inside
the block body that clip-chomping normalizes away on reload, so byte-identity of the FILE (not
just the reloaded VALUE) after an identity replace is unpinned. Neither is corruption of the
reloaded document; both are gaps in `_trim_tail`/`_render_field`'s blank-line handling that
`_verify_amend`'s value-only check cannot see, by the same structural reason N1 named for
comments. Not reproduced against FEAT-46's real content (Job 1's targets have no such shape).

**M13 is the already-known, carried, non-blocking finding** — see Job 3.

## Verdict basis

The dispatch's acceptance bar: *"VERDICT FAIL if any surviving mutant leaves a real guarantee
unpinned or any FEAT-46 target does not round-trip."* FEAT-46's three targets round-trip
byte-identical. But M10 leaves a real guarantee — the concurrent-write compare-and-swap the
verb's own docstring calls load-bearing — completely unpinned, for the third cycle running.
**FAIL.**

## Open questions for the panel/lead

1. **M10 (high).** Recommend a direct case analogous to `case_amend_v3_identity_check_is_live`:
   call `transform` (or exercise it via a real concurrent-write repro — write the file with a
   stale-relative-to-lock content between the unlocked read and the locked write) and assert the
   under-lock recheck refuses. `case_concurrency_real` already does this for `apply`; `amend` has
   no analogue.
2. M3/M8 (low, fail-closed): worth a fixture with a trailing blank line inside/after a block
   body if the panel wants `_trim_tail`/`_render_field`'s blank-line handling pinned at the same
   rigor as its comment handling; not blocking on their own, same class as cycle 1's H3/H4/H5.
3. M13 / `case_amend_refuses_an_unknown_key` (carried, non-blocking): still recommend a fixture
   with an `- id:`-shaped item under a disallowed key, so the case discriminates the allowlist
   itself rather than `_item_range`'s incidental refusal.
