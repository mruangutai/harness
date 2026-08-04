# Delta re-review — harness-backend-dev — FEAT-06 AMF fixes

**BLUF: all six AMF findings landed correctly. No must_fix. All of pm's exit-code claims
reproduce independently. One clarification worth flagging as advisory, not blocking (Check B).**

## Per-AMF verdict

| AMF | Verdict | Anchor re-grepped |
|---|---|---|
| AMF-1 | **landed** | `PLAN.md:366` renders `receipt-harness-{{persona}}-{{task_id}}-c{{cycle}}.md`; matches grants at `team-config.yaml:144/158/171/184/199` (all confirmed by grep, exact line numbers). `{{cycle}}` present, satisfying DEC-117. Old execution-time hedge replaced by header clause (e) at `PLAN.md:395-400`, which STATES the answer ("no precedent exists") rather than deferring to execution time. |
| AMF-2 | **landed** | `PLAN.md:281,296,322` — panel step output is `review-harness-qa-c{{cycle}}.md`; `team-config.yaml:227` grant confirmed (`review-harness-qa-*.md # Q6`). Segment's `qa-c{{cycle}}.md` name is explicitly preserved and distinguished in prose at `:293-300`, plus a verify conjunct at `:322` closing the silent-overwrite failure mode. |
| AMF-3 | **landed** | `review.yaml:5,8,19` (current repo file, T-02 not yet executed) are exactly the lines PLAN.md:302-311 describes as brought into scope: `:8` "Three independent reviewers…" → "Four"; `:19` ("All three have depends_on: []") → "All four" — confirmed by `grep -n "All three" review.yaml` → line 19 exactly; `:5` ("fourth dispatched step") reworded to "a synthesis step". Protect list at `:312-314` explicitly carves these three out. |
| AMF-4 | **landed** | `grep -n "ALTERNATIVE branch" PLAN.md` → 0 hits (exit 1). `grep -in "do not do both" PLAN.md` → 0 hits (exit 1). `PLAN.md:275-276` (T-02, on the LEAVE list) still reads "…see D-08's flip-delta" and the flip-delta block it points at is intact at `PLAN.md:127-180` (confirmed present, not touched) — no dangling reference. T-08(b) at `PLAN.md:595-602` carries all three live elements as one coherent paragraph: widen `:1978` to `{code ∥ qa ∥ security ∥ ui}`, keep the `qa →` segment clause, add the two-jobs distinguishing clause — the stale conditional sentence is gone and nothing was left half-finished. **All remaining case-insensitive `alternative branch` hits accounted for:** `:132,159,169,176-177` sit inside D-08's own flip-delta/rationale block (`:127-181`), whose stated job is recording the counterfactual — annotation-class, same as the pre-cleared `:270-271`/`:462-465`; `:507` is T-07 check(1)'s pre-cleared contingent annotation; `:766` is Assessment-section rationale prose. None is an imperative action instruction like the deleted one. |
| AMF-5 | **landed** | See Check A/B/measurement below — full detail there. Window predicate (8-line, three tokens qa/validator/loop_back + separate `test_matrix >=1` grep) is identically named at all four sites. |
| AMF-6 | **landed** | See Check A below. `PLACEHOLDER_UNSET = ("none", "null", "n/a")` specified as an **ordered tuple in the correct order** at `PLAN.md:234`; needle construction at `PLAN.md:523` uses `json.dumps` (corrected from the arch review's own defective `repr` remedy, documented at `:524-527`). |

## Check A — PLACEHOLDER_UNSET type and order

`PLACEHOLDER_UNSET` **does not exist yet in the shipped codebase** — T-01/T-07 are pending PLAN
tasks, not yet executed, so `import harness_yaml; harness_yaml.PLACEHOLDER_UNSET` raises
`AttributeError` today. This is expected (plan-phase review, not post-build). What is checkable is
the PLAN's own specification:

```
$ python3 -c "import sys; sys.path.insert(0,'.claude/skills/harness/bin'); import harness_yaml, json; print(type(harness_yaml.PLACEHOLDER_UNSET)); print(', '.join(json.dumps(x) for x in harness_yaml.PLACEHOLDER_UNSET))"
AttributeError: module 'harness_yaml' has no attribute 'PLACEHOLDER_UNSET'
```

```
$ grep -rn '"none", "null", "n/a"' .claude/skills/harness/bin/ | wc -l
1
```
(found at `validate-digest.py:472` — the sole current occurrence, as a plain literal inline, not a
module constant).

**The literal definition in PLAN.md (`:234`):** `PLACEHOLDER_UNSET = ("none", "null", "n/a")` —
a **tuple** (ordered), in the **exact order** the needle constructor at `:523` needs
(`json.dumps` over each element, joined `", "`) to render the byte-identical string
`"none", "null", "n/a"`. Not a `set`. This is landed correctly, not landed-but-defective.

**Measured, not just inspected** — the type/order claim closed empirically against the PLAN's own
literal tuple, since the module attribute doesn't exist yet to import:
```
$ python3 -c 'import json; print(", ".join(json.dumps(x) for x in ("none","null","n/a")))'
"none", "null", "n/a"
```
Byte-identical to the grep hit at `validate-digest.py:472` (`"none", "null", "n/a"`, same
comma-space separator, same order).

## Check B — the four AMF-5 sites, quoted side by side

1. **`PLAN.md:535-546` (T-07 check 8):** "`.claude/skills/harness/SKILL.md` contains at least one
   occurrence of `test_matrix`, AND all three of `qa`, `validator` and `loop_back` occur **within
   one window of 8 consecutive lines** of that file... Do NOT assert a single physical LINE and do
   NOT try to detect paragraphs."
2. **`PLAN.md:711-719` (T-11 intent):** "The `loop_back`, `validator`, `test_matrix` and `qa`
   tokens must all appear **inside this one passage, not scattered across the file.** T-07 check
   (8) and this task's verify test a window of **8 consecutive lines**... Write the passage as one
   contiguous block."
3. **`PLAN.md:728-733` (T-11 verify):** `grep -c -i 'test_matrix' … returns >= 1` (separate
   conjunct) AND a python one-liner: sliding 8-line window, `all(k in window for k in
   ('qa','validator','loop_back'))`.
4. **`BRIEF.md:196-207` (SC-14):** "`grep -c -i 'test_matrix'` … returns ≥ 1, and the same passage
   names `qa`, `validator` and `loop_back` … 'The same passage' means a window of 8 consecutive
   lines … the three tokens must co-occur inside one such window anywhere in the file. It is
   deliberately not 'the same physical line'."

**Discriminator applied, as instructed.** SC-14 (site 4) names **8** and the **same three-token
window** (`qa`, `validator`, `loop_back`) with `test_matrix` asserted separately — matching sites 1
and 3 exactly. Site 2 (T-11 intent, `:711`) names a **four-token superset** ("must all appear
inside this one passage") as writer-facing prose guidance. Per the discriminator: since SC-14
matches the three-token gate, the four-token intent language at `:711` is a **writer-facing
instruction stricter than the gate** (asking the author to keep all four tokens, including
`test_matrix`, together as good practice) — it fails safe (a passage satisfying the four-token
instruction trivially satisfies the three-token gate plus the separate `test_matrix` grep). **This
is advisory prose, not a must_fix.** No two-descriptions-inside-the-fix defect.

## AMF-5(b) — RED/GREEN re-measured independently

**Measurement hygiene.** `git status --porcelain -- .claude/skills/harness/SKILL.md` → empty.
`diff <(git show 635ef14:.claude/skills/harness/SKILL.md) .claude/skills/harness/SKILL.md` →
identical. Working tree is `635ef14` for this file; no unstaged-edit risk.

**RED** — exact invocation and observed exit code, run by me, not inherited:
```
$ python3 -c "import sys; ls=open('.claude/skills/harness/SKILL.md').read().splitlines(); W=8; sys.exit(0 if any(all(k in '\n'.join(ls[i:i+W]) for k in ('qa','validator','loop_back')) for i in range(len(ls))) else 1)"
exit=1
$ grep -c -i 'test_matrix' .claude/skills/harness/SKILL.md
0
```

**Independent per-token counts** (`grep -o -i <tok> SKILL.md | wc -l`, at `635ef14`):
`qa: 0`, `loop_back: 0`, `validator: 2`, `test_matrix: 0`. So the falsifiability claim (0 for
`qa`/`loop_back`/`test_matrix`) holds — `validator` is NOT 0 (see robustness judgement below).

**GREEN** — I wrapped T-11's prescribed passage (`PLAN.md:705-710`) independently, at 95 cols,
using `textwrap.fill` (not pm's scratch file, not reused from context above), and inserted it into
a fresh scratchpad copy of `SKILL.md` (`/private/tmp/.../scratchpad/SKILL-backend-dev-green.md`,
never in the repo tree) immediately after step 3's INV-6 sentence (line 39):
```
$ python3 -c "import sys; ls=open('<scratch>/SKILL-backend-dev-green.md').read().splitlines(); W=8; sys.exit(0 if any(all(k in '\n'.join(ls[i:i+W]) for k in ('qa','validator','loop_back')) for i in range(len(ls))) else 1)"
exit=0
$ grep -c -i 'test_matrix' <scratch>/SKILL-backend-dev-green.md
1
```
My independent wrap produced 6 lines (not identical text to pm's wrap, same content, different
break points): line0 `qa,validator` / line1 `test_matrix` / line2 `—` / line3 `loop_back` / line4
`validator` / line5 `—`. GREEN confirmed on a wrapping I generated myself, independent of pm's.

**The GREEN is self-sufficient — it does not lean on the pre-existing `validator` at line 39.**
I inserted immediately after line 39 for convenience, which happens to sit next to one of the
file's two pre-existing `validator` occurrences. But the window is satisfied WITHIN the inserted
passage alone: my line0 already carries both `qa` and `validator`, and line3 (3 lines later)
carries `loop_back` — span 4, entirely inside the 8-added-line passage. In the real post-T-06 file,
T-06's ~12 lines will sit between line 39 and this passage, pushing the old `validator` at line 39
outside any 8-line window that also reaches the passage — so the passage cannot depend on that
pre-existing token, and mine doesn't.

## Window robustness judgement

- **Wide enough for reflow?** Measured minimum required span in my own wrap: lines 0→3 (`qa` at
  line0, `loop_back` at line3) = **4 lines**. Matches the digest's independently-reported 4-line
  span for pm's wrap. Window is 8, giving 2x margin either wrap.
- **Narrow enough that tokens can't co-occur accidentally?** Since `qa` and `loop_back` are BOTH
  **0 occurrences anywhere in `SKILL.md` at `635ef14`**, no pre-existing 8-line window — or any
  window of any width — can satisfy the three-token predicate before this passage is added,
  regardless of size. So the concern about accidental co-occurrence via substring matches
  (`qa` matching `harness-qa`, `validator` matching `validator-squad`) does not create a false
  positive here, because two of the three tokens are wholly absent pre-edit.
- **Which token actually carries the discrimination?** `validator` is NOT the discriminating
  token — it already occurs twice pre-edit (`SKILL.md:39` itself, i.e. literally at the insertion
  point, and `:213` elsewhere) and is nearly free once any prose near step 3 mentions the validator
  squad at all. **`qa` and `loop_back` are what carry the discrimination** — both are hard zeros
  today and only this specific passage introduces them together. A future editor must not remove
  the explicit `qa`/`loop_back` tokens from the passage on the assumption `validator` alone
  suffices — it does not.

Predicate is expressible both as the `python3 -c` one-liner (`verify:` line, confirmed at both
T-07 check 8 and T-11 verify) and as a described assertion inside `test-team-catalog.py` (T-07
check 8 prose, `PLAN.md:535-546` — file itself is pending, not yet written, consistent with
plan-phase). The untouched `grep -c -i 'test_matrix' >= 1` conjunct is intact and separate at both
sites (`PLAN.md:535`, `:726`).

## Advisory-coupling check (T-08(b) / check (9))

T-08(b)'s two-jobs clause as prescribed (`PLAN.md:598-602`) is prose: "the segment writes and runs
tests and enforces the `test_matrix` hard gate with `loop_back` to dev; the panel step is the same
persona in gate-only mode, re-running the matrix over the pinned `review_sha` and authoring
nothing." No second `{…∥…}` group — only the one `{code ∥ qa ∥ security ∥ ui}` group at `:1978`
prescribed by (a). Check (9) at `PLAN.md:555-561` is unaffected. Still advisory, not blocking.

## Criterion-layer greps (independent, not pm's table)

- `qa-c` → one hit, `BRIEF.md:25`, describing the pre-fix historical shipped state
  (`notes/qa-c0.md`, `qa-c1.md`) — correct, unchanged, not a restated criterion.
- `review-harness-qa` → **zero hits in BRIEF.md**. No SC names the panel's new filename at all.
- `Three`/`three` → all hits are either the Problem-section's pre-fix account (unchanged, correct),
  "three-descriptions problem" phrasing (different referent), or fixture/file counts — none assert
  a superseded review.yaml step count as target state.
- `review.yaml` text → `BRIEF.md:149-150` (SC-04) and `:210` (SC-15) both reference `review.yaml`
  in its POST-fix four-element form; `:30` and `:39,48` are Problem-section pre-fix descriptions.
- SC-04 asserted id set (`BRIEF.md:149-150`): `{code, qa, security, ui}` — the four-element set,
  confirmed verbatim.

No criterion elsewhere restates a superseded shape for AMF-2 or AMF-3.

## `git status --porcelain`

```
 M .harness/logs/2026-08-04.md
?? .harness/features/FEAT-06-team-layer-inv6/
?? .harness/notes/perf-review-agent-workflow-2026-08-04.md
```
Identical to the pre-dispatch state (verified before I began). I made no repo-tree edits; all
scratch work (`SKILL-backend-dev-green.md`) lives under
`/private/tmp/claude-501/.../scratchpad/`, never copied into the repo.
