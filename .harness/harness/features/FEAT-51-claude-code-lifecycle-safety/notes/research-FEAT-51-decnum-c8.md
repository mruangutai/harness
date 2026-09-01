> **Read the cycle-2 section before trusting any number here.** Cycle 1 was sent back for one defect —
> T-08's `verify:` had two greps for three required tests — and cycle 2 fixed it in three anchored edits.
> Superseded cycle-1 claims are marked inline.

# FEAT-51 plan cycle 8 — DEC-209 → DEC-210 renumber, and SC-09's last clause closed

**BLUF.** `plan.yaml` was recreated through one `plan-merge.py apply` remove-then-apply cycle. Every
`DEC-209` token outside the two frozen `panel.findings` summaries is now `DEC-210`; T-06's next-free-number
paragraph is re-anchored to main's tip `0bc57c88` and carries the new, routable escape clause; T-06's
`verify:` now greps `DEC-210` and is RED against the current tree; and T-08 gains a third test that grades
SC-09's `DECISIONS-INDEX.md`-ruling clause. Task set, decision set, requirements and the panel record are
untouched. Both approvals remain absent/pending (there is no `approval:` key — the standing defect recorded
in the file header comment, `plan.yaml:7-19`).

## Numbers, all measured

| Measurement | Value |
|---|---|
| `grep -c 'DEC-209' plan.yaml` | **2** — `plan.yaml:38` and `plan.yaml:43`, the two frozen panel summaries |
| `grep -c 'DEC-210' plan.yaml` | **18** = 7 `dec:` pointers + 11 in-value tokens |
| `dec: DEC-210` pointer lines | **7** — `:150 :154 :158 :166 :190 :208 :212` (D-01, D-02, D-03, D-05, D-11, D-15, D-18) |
| `grep -c 'DEC-209' BRIEF.md` | **0** — confirmed by my own grep, not assumed |
| Parsed tasks | **9** — T-01..T-08, T-10 |
| Parsed decisions | **16** — D-01..D-15, D-18 |
| `status` / `approval` key | `plan` / absent |
| `panel.findings` equality | `yaml.safe_load(pre)['panel'] == yaml.safe_load(post)['panel']` → **True** (whole `panel`, not just `findings`) |
| Byte-diff applied vs proposal | ran `diff` (exit 0) and `cmp` → **BYTE IDENTICAL** |
| T-06 amended `verify:` verbatim | **exit 1**; first conjunct fails — the `awk … DECISIONS.md \| grep -q 'plan-sign-gate\.sh'` last-entry conjunct (individually measured `c1=1`, `c2=1`, `c3=1`) |

Both `verify:` values remain literal `|` block scalars (`plan.yaml:593`, `plan.yaml:849`); `safe_load` returns
5 and 3 newlines respectively, which a folded scalar could not produce. **Superseded in cycle 2: T-08's is
now 4 newlines** (a third grep was added); T-06's 5 is unchanged.

## What changed, by anchor

- **T-06 intent head** (`plan.yaml:600-608`) — renumbered to `DEC-210`, re-measured at `0bc57c88`, and it
  identifies the taken predecessor as *BUG-1081's entry recording that mechanical code-grade state is computed
  by the digest gate and not trusted from the reviewer*. **The literal string `DEC-209` is deliberately not
  emitted** — the acceptance count of 2 governs over the obvious phrasing, per the dispatch's hard constraint.
  The escape clause is the verbatim replacement: next free number, used in `DECISIONS.md`,
  `DECISIONS-INDEX.md` and the T-08 constant, reported as an open question, and **do NOT edit `plan.yaml`**.
  The eight content bullets, the refs sentence and the regeneration paragraph (`:610-652`) are byte-identical.
- **T-06 verify** (`plan.yaml:596`) — `grep -q 'DEC-210' … DECISIONS-INDEX.md`. All four other conjuncts,
  including cycle 7's two `awk … last-region` conjuncts, are byte-identical.
- **T-08** — title, `QUARANTINE_DEC = "DEC-210"` (`:880`), and every prose token renumbered. TWO → **THREE**
  module-level tests (`:866`), **register ALL THREE** in `TESTS` (`:869`). The "both tests" wording that now
  had three referents was narrowed to "the two region tests" (`:883-888`).
- **New third test** (`plan.yaml:917-932`) — `test_dec_210_index_row_names_the_compatibility_host_in_the_ruling`:
  reads the index through the existing module constant `REAL_INDEX`
  (`test-gen-decisions-index.py:25`), locates the row with `ROW_RE`, the generator's own grammar bound at
  `:43` (written `:39` in cycle 1 — wrong, corrected in cycle 2), matches `group(1) == QUARANTINE_DEC`, and asserts the literal `Claude Code` in `group(2)` — which
  **is** the text after ` :: `, so the ruling-half split is the grammar's, not a second one. Goes red when the
  host name is absent from the ruling half or present only in the generated left half. FAILS LOUDLY when no
  row parses, matching the fail-loudly rule the other two already state. This closes SC-09's clause "its
  `DECISIONS-INDEX.md` row names the compatibility host in the hand-written ruling half"
  (`BRIEF.md:146`), which no T-06 conjunct and no T-08 assertion graded before.
- **Identifier rename** (lead decision, applied): `test_dec_209_*` → `test_dec_210_*` in **5** places —
  2 in T-08's `verify:` greps (`:850`, `:851`) and 3 in prose (`:898`, `:907`, and the new `:917`). These do
  not match the literal `DEC-209`, so the counts above are unaffected.

## Cycle 1 — T-08 `verify:` NOT extended (WRONG, sent back; see cycle 2)

Cycle 1 reasoned: `main()` at `test-gen-decisions-index.py:887` iterates `TESTS` **and nothing else**, and
the new test is registered in `TESTS`, so the existing tail conjunct already executes the new assertion and
a grep would be redundant. **That reasoning is sound and answers the wrong question.** `verify:` does not
exist to RUN the assertion; it exists to go RED when the task was not done. With only two greps,
`harness-dev-ops` could omit `test_dec_210_index_row_names_the_compatibility_host_in_the_ruling` entirely,
both greps still pass, the suite still exits 0, and T-08 is green with SC-09's index-ruling clause ungraded
— the exact "green before the task runs, can never go red" defect this cycle exists to remove. Corrected in
cycle 2 below. Recorded honestly rather than overwritten.

## Method / recovery

Anchored-substring transform, `/tmp/feat51_c8_transform.py`: each anchor asserted to occur exactly once
(`sub1`), the frozen panel region split off at `\nlanes:\n` and never touched, then a global tail replace.
Backup at `/tmp/feat51-plan-c8-backup.yaml`, proposal at `/tmp/feat51-plan-c8-proposal.yaml` (no `approval:`
key). `rm` by absolute path, then ONE `apply`; nothing went wrong mid-cycle, so the backup was not used.

## Cycle 2 — the send-back, and the three edits that answer it

**BLUF.** T-08's `verify:` now carries THREE greps plus the suite, so omitting any one of the three
registered tests turns the gate red. Exactly three regions of `plan.yaml` changed; the other ~1113 lines are
byte-identical to the cycle-1 file.

| Edit | Anchor | Change |
|---|---|---|
| 1 | `plan.yaml:852` (new line) | third conjunct `grep -q 'def test_dec_210_index_row_names_the_compatibility_host_in_the_ruling' .agents/skills/harness/bin/test-gen-decisions-index.py &&`, placed after the two existing greps and before the suite tail, same `.agents/skills/...` prefix |
| 2 | `plan.yaml:946` | `The two greps are therefore the whole discriminator` → `The three greps …`. Nothing else in the baseline paragraph moved: it still says the block exits 1 because the FIRST grep fails and the tail conjunct alone exits 0 printing eleven ok lines, still anchored at `ad93d43e`, not re-measured at a new sha |
| 3 | `plan.yaml:926` | `ROW_RE … bound at :39` → `:43`. Verified at source: `test-gen-decisions-index.py:43` is `ROW_RE = gdi.ROW_RE` |

### Evidence, all measured

| Measurement | Value |
|---|---|
| `diff` cycle-1 backup vs new `plan.yaml` | **10 diff lines, exactly 3 hunks** — `851a852`, `925c926`, `945c946`. No other hunk |
| `grep -c 'DEC-209' plan.yaml` | **2**, at lines **38 and 43** (the two frozen panel summaries) |
| `grep -c 'DEC-210' plan.yaml` | **18**, unchanged from cycle 1 — **not 19**. The new line's only identifier is the lowercase `test_dec_210_index_row_names_the_compatibility_host_in_the_ruling`, which does not contain the literal `DEC-210`, so it adds no matching line. `grep -c` counts lines, and no line's DEC-210 content changed |
| `yaml.safe_load` | clean; **9** tasks T-01..T-08, T-10; **16** decisions D-01..D-15, D-18; `status: plan`; `approval` key **absent** |
| Parsed `panel` vs backup | `post['panel'] == pre['panel']` → **True** |
| T-08 `verify:` scalar | literal `|`; `safe_load` returns **4 newlines / 4 non-blank lines** — three greps + the suite. A folded `>` could not produce interior newlines |
| T-08 `verify:` run VERBATIM at repo root | **exit 1**, no output. First failing conjunct is **c1**, the `test_dec_210_entry_names_both_enforcement_points` grep. Individually: c1=1, c2=1, c3=1, c4=0. All three functions are absent from the tree, as they must be before T-08 runs |
| Byte-diff applied file vs proposal | `cmp` → **BYTE IDENTICAL** (ran it) |
| `check-plan-routes.py <this plan>` | **exit 0**, 0 violations; 5 DEVIATION lines are the expected DEC-174 carve-outs, unchanged from cycle 1 |

### Method

`/tmp/feat51_c8b_transform.py`: backup to `/tmp/feat51-plan-c8b-backup.yaml`, each of the three anchors
asserted to occur **exactly once** (the script exits non-zero on any other count), replace, proposal to
`/tmp/feat51-plan-c8b-proposal.yaml` asserting no top-level `approval:` key, `os.remove` of the absolute
`plan.yaml`, ONE `plan-merge.py apply`, then `cmp`. Nothing failed mid-cycle, so the backup was not used and
`plan.yaml` was never left absent or partial beyond the single remove-then-apply step.

## Open questions

- **Q1 (non-blocking, reported for override):** the `test_dec_209_*` → `test_dec_210_*` rename was applied as
  the lead directed. It is reversible and the greps and prose moved in lockstep, so nothing is inconsistent.
  I have no evidence against it — a guard named for BUG-1081's shipped decision would be the same misdirection
  the amendment removes.
- **Q2 (non-blocking):** `DEC-210` is free at `0bc57c88` but this plan is not yet approved, so another feature
  may take it before T-06 runs. That residual risk is exactly what the new escape clause routes, and the
  clause now tells the documentor to report rather than to edit `plan.yaml`.
