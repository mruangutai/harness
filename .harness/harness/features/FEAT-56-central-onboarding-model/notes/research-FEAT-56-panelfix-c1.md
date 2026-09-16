# FEAT-56 — cycle-1 panel fix and panel record — evidence

**BLUF. All six `must_fix` are CLOSED in `plan.yaml`, the three advisories are dispositioned as the
lead ruled, and the whole cycle-1 panel is transcribed at `panel.cycle: 1` with 34 findings — 13
carried forward byte-identical, 9 cycle-1 panel findings, 8 dismissed leads and the goal-check's 4.
No open finding is `high` or `unrated`. `approval:` is untouched at `pending`. No production file was
edited and nothing was committed.** Writes: 6 `plan-merge.py amend`, 1 `apply` (D-12), 1 `set-panel`,
1 `BRIEF.md` edit.

| finding | severity/reader | closed by | how |
|---|---|---|---|
| R1 | high · scope | T-10 | `verify` bans `steps? [4-9]` and the compound form, plus three `### N.` heading positives so the ban cannot be satisfied by an unnumbered document; `intent` states the three-step structure as a correctness bound |
| R2 | med · should-not-exist | T-10 + T-11 | T-11 KEEP (d) with positive `IS a grilling` and a ban on `seed the repository's own`; T-10 keeps the note but bans the flattened control-plane clause |
| R3 | med · should-not-exist | T-10 + T-11 | `:427`/`:429` re-partitioned to harness-init in BOTH intents; T-11 greps both rows positively, T-10 bans both |
| R4 | med · should-not-exist | T-11 (+ D-12) | D-12 records the runtime-conditional floor; T-11 `intent` implements it, `verify` bans the unconditional STOP and requires the conditional wording |
| R5 | med · scope | T-11 | `! grep -qF 'anywhere but the control plane'` |
| R6 | low · should-not-exist | T-17 | pin moved to `12f74ea8`; the merge-base is named as forbidden and no `4b5dbb23` string remains in the task |
| R7 | low · should-not-exist | T-14 | one `intent` clause: byte-exact banner, reconcile by re-authoring T-13's four files, never by weakening `--check` |
| R8 | low · scope+s-n-e | — open | assessed, not acted; `depends_on` untouched; reason in the finding summary |
| R9 | low · scope+s-n-e | — open | stated in `BRIEF.md ## Verification gaps`; no SC added or altered |

## R4 — the decision, recorded as the lead ruled it

D-12 (`dec: DEC-83`): the preflight KEEPS the 2.1.217 floor but as a check **conditional on the
runtime in use** — hard STOP under Claude Code, no stop under any other runtime; `harness-add-repo`
carries no provider CLI check at all. I did **not** overturn it and hold no primary-source evidence
that would: `.claude/skills/harness-init/SKILL.md:40` states its own reason as "below the floor for
the spawn env vars", and `DECISIONS-INDEX.md:94` shows DEC-83 is the explicit spawn-depth setting —
a Claude Code mechanism. The `because` names both costs so a non-author operator can rule either way
at signature.

## Evidence 1 — both amended verifies run VERBATIM against the current tree, RED

Run through `plan-merge`-loaded text (so the string graded is the one on disk), `cwd` = worktree:

```
==================== T-10 verify (verbatim) — 30 lines   -> EXIT: 1
==================== T-11 verify (verbatim) — 35 lines   -> EXIT: 1
```

Both load as literal `|` blocks (30 and 35 lines survive `safe_load`). Runner:
`/tmp/feat56-panelfix/runverify.py`.

**T-10's whole verify is red at conjunct 2 (`test -f`), because the file does not exist yet — so the
new conjuncts are never reached in that run and its exit code proves nothing about them.** They are
graded below, per site.

## Evidence 2 — R1 per site, and the correct repointed wording ADMITTED

Each conjunct of the plan's own `verify` text run SEPARATELY (a chained run stops at the first
failure), `F` bound to a scratch document; harness `/tmp/feat56-panelfix/prove_t10.py`, base document
`scratch/good.md` — a full harness-add-repo shaped as T-10's intent prescribes.

```
--- good: whole verify exit 0; failing conjuncts: 0
--- bad_r1_site251: whole verify exit 1; failing conjuncts: 1
      RED  ! grep -qE 'steps? [4-9]' "$F"
--- bad_r1_site290: whole verify exit 1; failing conjuncts: 1
      RED  ! grep -qE 'steps? [4-9]' "$F"
--- bad_r1_compound: whole verify exit 1; failing conjuncts: 1
      RED  ! grep -qE 'steps? [1-9] and [4-9]' "$F"
--- bad_r1_unnumbered: whole verify exit 1; failing conjuncts: 3
      RED  grep -qE '^### 1\.' "$F"   RED  '^### 2\.'   RED  '^### 3\.'
--- bad_r2_grilling: whole verify exit 1; failing conjuncts: 1
      RED  ! cat "$F" | tr '\n' ' ' | grep -qF 'for the control plane its domain description'
--- bad_r2_note_gone: whole verify exit 1; failing conjuncts: 1
      RED  grep -qF 'IS a grilling' "$F"
--- bad_r3_rows: whole verify exit 1; failing conjuncts: 2
      RED  ! grep -qF "I'll point ai-dev at" "$F"
      RED  ! grep -qF 'The agent got blocked' "$F"
```

- **site `:251`** — mutant carries the shipped wording "fill `test_kinds` in step 4 and the GitHub
  block in step 7": RED.
- **site `:290`** — mutant carries "decides whether step 7 runs at all": RED.
- **admits the correct wording** — `good.md` repoints `:251` to "in step 2 and ask the GitHub
  question in step 3" and `:290` to "dev-ops needs it to judge a null ui runner", and the WHOLE
  T-10 verify exits **0** on it, including `check-instruction-paths.py` and the `DB < FL < SG`
  ordering conjuncts. The ban set is therefore satisfiable, not merely fireable.
- **the honesty positive** — deleting the step numbers from the headings (`bad_r1_unnumbered`)
  satisfies every ban and still fails, which is what the three `### N.` positives are for.

## Evidence 3 — T-11's seven new conjuncts, today and under mutation

`/tmp/feat56-panelfix/prove_t11.py`, `prove_t11b.py`. Against today's tree:

```
  exit 1  ! grep -qF 'anywhere but the control plane' "$F"          <- R5, RED today (:279)
  exit 1  ! grep -qF "seed the repository's own" "$F"               <- R2, RED today (:27)
  exit 1  ! grep -qF 'Stop; the depth setting will not take' "$F"   <- R4, RED today (:40)
  exit 1  cat "$F" | tr '\n' ' ' | grep -qF 'only when running under Claude Code'   <- R4, RED today
  exit 0  grep -qF 'IS a grilling' "$F"                             <- R2 KEEP positive
  exit 0  grep -qF "I'll point ai-dev at" "$F"                      <- R3 KEEP positive
  exit 0  grep -qF 'The agent got blocked' "$F"                     <- R3 KEEP positive
```

**Stated plainly, because the dispatch asked for RED on all of them: four of the seven are RED today
and three cannot be.** A KEEP guard asserts content that is present today and must SURVIVE the cut,
so it is green today by construction; its discrimination is against the cut, not against the current
file. Proven against mutants instead:

```
whole-range-cut mutant (:25-28 note and :239-418 Track B deleted):
  exit 1  grep -qF 'IS a grilling' "$F"
rows-handed-to-T-10 mutant (:427 and :429 removed):
  exit 1  grep -qF "I'll point ai-dev at" "$F"
  exit 1  grep -qF 'The agent got blocked' "$F"
D-12 rewritten :40 bullet (wraps across three lines):
  exit 0  ! grep -qF 'Stop; the depth setting will not take' "$F"
  exit 0  cat "$F" | tr '\n' ' ' | grep -qF 'only when running under Claude Code'
```

The last pair is the admits-the-correct-wording half for R4: the prescribed rewrite turns both
conjuncts green, so the guard is satisfiable and the phrase survives line wrapping.

## Evidence 4 — the panel record

```
$ python3 -c "...print(p['cycle'],sorted(...),[r['status']...],len(p['findings']),d['approval'])"
1 ['goalcheck', 'scope', 'should-not-exist'] ['ran', 'ran', 'ran'] 34 {'status': 'pending'}
```

```
ID CHECK over 34 findings: PASS — every id recomputes
UNIQUE IDS: True
OPEN FINDINGS (15) — severities: ['info', 'low']
OPEN high/unrated: NONE
RESOLVED without resolved_by: []
TASKS: 17 | approval: {'status': 'pending'} | approval.rulings present: False
D ids: D-01..D-12          T-17 mentions 4b5dbb23: False
```

- **All 13 carried findings verified against `panel_findings.finding_id(reader, summary)` BEFORE the
  replacement was built, and all 13 verified.** None had to be recomputed; each was carried as the
  exact dict already on disk, `resolved_by` included.
- Every new id was computed by the module (`build_panel.py` imports `finding_id`), never typed.
- `panel.transcription_rule` records the one normalization: the two findings both readers raised are
  filed under the reader the digest ranks first (`scope`) and name the second reader inline, and the
  two open findings carry the lead's disposition reason — both required by the dispatch, and both
  change the summary, hence the id, relative to the digest's own text.
- The goal-check's four findings are `reader: goalcheck`, `severity: unrated`, `resolved`, with
  `resolved_by` read from `runs/2026-09-08-replanfix-c1-product/digest.md`: F1 → `T-10, T-11`,
  F2 → `T-11`, F3 → `T-15`, F4 → `T-10`.

```
$ python3 .claude/skills/harness/bin/check-plan-routes.py <plan.yaml>
0 violation(s) across 1 plan(s)      exit=0
```

## Source re-derivations (not adopted from the digest)

- `git show 12f74ea8:.claude/skills/harness-init/SKILL.md | grep -c` → `Track B` **2**,
  `factory/fleet.yaml` **2**. Same greps at `4b5dbb23` → **0** and **0**. R6's pin is correct and the
  merge-base really would grade vacuously.
- `.claude/skills/harness-init/SKILL.md` in the worktree still carries the panel's anchors at the
  cited lines: the grilling note `:25-28`, the preflight `:30-46` with `claude --version` at `:34`
  and the STOP at `:40`, `:175`/`:178` `# SEED` rules, `:251`, `:279-282`, `:290`, Red flags
  `:419-434` with `:427` and `:429`.
- Heading shape checked before writing R1's positives: the file uses `### N.` numbered headings and
  `###` unnumbered ones for the mirror and board subsections, so `^### [4-9]\.` cannot collide with
  a moved subsection.

## Open questions for the operator (nothing here blocked this cycle)

1. **Q3 carried, still unanswered** — does REQ-09 gain one `uat` clause (operator opens an OMP
   session, confirms `/harness-plan` resolves from `.omp/commands/`)? It is the only method that can
   see a wrong canonical root. Not added: a new criterion is a scope change. The gap is now written
   into `BRIEF.md ## Verification gaps`.
2. **D-12 is a scope decision against the governing intent**, not a doc edit. The operator can rule
   the other way at signature; both costs are written into the entry.
3. **Q4 from the panel is a harness defect, not a plan finding** — a plan-phase review has no diff to
   pin, so the `scope` reader was forced to bind `reviewed:` to a stale `base..review_sha` range. It
   is recorded here only so it is not lost; it belongs to the harness owner.
