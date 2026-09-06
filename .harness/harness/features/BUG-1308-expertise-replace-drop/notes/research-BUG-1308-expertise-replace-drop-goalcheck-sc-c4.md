# Goal-check delta (final) — BUG-1308 — SC-01..SC-12 at review_sha `b70d57b4`

**All twelve criteria are MET at `b70d57b464743034231fed3d18227a17faae2ed4`. The feature's goals are
met at that commit — yes.** No criterion unmet, none undeterminable, none unmeetable as written.
Nothing routed back; **no `must_fix`**. Two advisories and the standing backlog restatement only.

**No prior verdict was carried forward.** Every automated criterion was run at this pin. Content read
with `git show b70d57b4:<path>` (G-15); `git diff --stat b70d57b4 -- <graded files>` is empty, so the
worktree copy of `expertise-merge.py`, `harness_merge.py`, both test files, `harness-distill/SKILL.md`
and `DECISIONS-INDEX.md` **is** the pinned content — invocations against the worktree are invocations
against the pin. `HARNESS_AGENT_TYPE` cleared for every suite run (O-01). HEAD sits one commit later
at `ac6c9c5b` (a plan.yaml re-pin); no graded file differs.

## 1. Suites at the pin

| Suite | Command (from worktree root) | Exit | `^FAIL ` | Files |
|---|---|---|---|---|
| unit | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | **0** | **0** | 28 |
| integration | same, `--kind integration` | **0** | **0** | 46 |

Counted with `grep -c '^FAIL '`, never a tail read (G-08). Named files run directly:
`tests/integration/test-expertise-merge.py` exit 0 / 211 PASS / 0 FAIL (cases 1–26);
`tests/unit/test-expertise-ops.py` exit 0 / 112 PASS / 0 FAIL (u1–u22);
`tests/integration/test-gen-decisions-index.py` exit 0 / 0 FAIL.

**Independent probe** — `/tmp/bug1308_probe_c4.py`, outside the repo, temp roots created and removed
per case, `--ops` always a FILE PATH, never a real Expertise file: **53/53**. It re-derives SC-01,
02, 03, 04 (all four conditions), 05, 08, 12 (all three shapes) and the VL-06 class from the CLI
rather than from the suite.

## 2. The twelve, at `b70d57b4`

| SC | Verdict | Declared method | Command run | Observed |
|---|---|---|---|---|
| SC-01 | **MET** | automated / integration | `python3 tests/integration/test-expertise-merge.py`; probe | case11 ×6 PASS; probe: exit 0, `REPLACED P-07`, Patterns 15, `P-07` still 7th, carries `NEWTEXT_C4` |
| SC-02 | **MET** | automated / integration | same | case12 ×8 PASS; probe: exit 0, `DROPPED G-03`, `- G-03:` absent, survivors `[G-01,G-02,G-04,G-05]` |
| SC-03 | **MET** | automated / integration | same | case13 ×7 PASS; probe: exit 10, `MISSING TARGET section=Patterns id=P-99 reason=…`, sha256 equal |
| SC-04 | **MET** (4/4 clauses) | automated / unit+integration | both files; probe | clause table below |
| SC-05 | **MET** | automated / integration | same | case15 ×3 PASS; probe: valid+valid+refusable → exit 10, sha256 byte-identical to pre-invocation |
| SC-06 | **MET** | automated / integration | integration file | exit 0, all pre-existing cases pass; case16 re-asserts exit 7 CONFLICT and exit 8 CAP EXCEEDED; `git diff origin/main -- .claude/skills/harness/bin/expertise-merge.py \| grep -c '^-[^-]'` = **0** |
| SC-07 | **MET** | automated / unit | `python3 tests/unit/test-expertise-ops.py` | exit 0; u10 PASS ×2: `compute_union returns non-empty conflicts` and `merged Patterns still carries OLD text at index 6` |
| SC-08 | **MET** | automated / integration | integration file; probe | case11/case12/case19 `check-expertise.sh` exit 0; probe re-ran the checker on its own replace- and drop-produced files, exit 0 both |
| SC-09 | **MET** | automated / integration | integration file | case17 ×11 PASS — anchor matches the real SKILL.md exactly once, real file clean, copies (a)/(b) redden the FIRST direction only, (c) the SECOND only |
| SC-10 | **MET** | automated / integration | `git show b70d57b4:.harness/harness/docs/DECISIONS-INDEX.md`; `python3 tests/integration/test-gen-decisions-index.py` | `DEC-219` row at `:219`; phrase `replace and drop through the ops subcommand` count **1**; generator test exit 0 |
| SC-11 | **MET** | automated / integration | integration file | case18 ×5 PASS; **2.05s** hold, neither child exited; both exit 0 after release; census = original eight + `P-09` + `P-10`; `P-07` carries child B's marker |
| SC-12 | **MET** (3/3 clauses) | automated / unit+integration | both files; probe | clause table below |

### SC-04 — four conditions, each graded on its own

| Clause | Verdict | Evidence at the pin |
|---|---|---|
| duplicate id already in the file | MET | case14(b) ×6; probe: exit 11, `AMBIGUOUS TARGET section=Patterns id=P-04 reason=the id appears 2 times…`, sha256 equal |
| two ops naming one section+id | MET | case14(c) ×6; probe: exit 11, `…id=P-01 reason=two ops in one proposal name this target`, sha256 equal |
| `section` absent → exit 12 naming key + index | MET | u13 + case20(a) ×6; probe: `MALFORMED OPS op index=0: missing required key section`, sha256 equal, following `apply --entries` exit 0 |
| `section` empty → exit 12 naming key + index | MET | u13 + case20(b) ×6; probe: same line, sha256 equal, following `apply --entries` exit 0 |

### SC-12 — three shapes, each graded on its own

| Clause | Verdict | Evidence |
|---|---|---|
| CLI, drop-low + replace-high, file order | MET | case19 ×7; probe: exit 0, sequence `P-02,P-03,P-04,P-05`, `- P-05: MARKER_C4` last among survivors, marker count 1 |
| resolver, same two ops REVERSED, identical result | MET | u11 forward and reversed with the explicit identity assertion; probe re-ran the reversal at the CLI: identical sequence |
| two drops at distinct original indices | MET | u12 ×2; probe: exit 0, surviving sequence `P-02,P-03,P-05` |

## 3. Regression statement for the two new commits — none

**`a737eb9d` (target-grammar gate, all three verbs).** `_validate_target_grammar`
(`expertise-merge.py:191-203` at the pin) round-trips `target` through `ENTRY_RE` itself via the
synthetic line `f"- {target}: x"` and requires `match.group(1) == target`; no second grammar literal
exists, so it cannot drift from the parser (the VL-05 lesson applied).

I enumerated **every** `target` literal in both shipped test files at the pin plus every target my
probes use: `P-01 P-02 P-04 P-05 P-07 P-08 P-99 G-02 G-03 G-08 G-09 P-16 P-98 X-01` — all match
`^[A-Za-z]{1,3}-\d+$`. The only non-matching ones are the two the gate is *supposed* to refuse
(`PPPP-1`, `P-01: fake prefix`) and the `\N{...}`-forged targets of case22/u18, which assert exit 12.
**No criterion and no shipped fixture depends on a target the new gate refuses.** Re-derived
independently: each of the two malformed targets refuses at exit 12 `MALFORMED OPS` under **all three
verbs** with sha256 unchanged (6/6), and a well-formed `add G-09` still exits `0 ADDED`.

**`b70d57b4` (SPEC §5.3 + eight citation edits).** Its diff touches `.harness/harness/docs/SPEC.md`,
`feature.json`, two notes and one observations file. **No criterion grades any of them** — SC-09
reads `.claude/skills/harness-distill/SKILL.md`, which is byte-unchanged across `5942e34e..b70d57b4`,
and SC-10 reads `DECISIONS-INDEX.md`, likewise unchanged. Zero criterion surface.

## 4. FOR THE OPERATOR — emergent criteria, RECOMMENDED, NOT ADOPTED

**I have not touched `BRIEF.md`.** Adoption is the operator's call. The c3 recommendation **stands,
and VL-06 adds a second one** — I recommend **two criteria, not one**. Rationale: they cover
different REQs by different mechanisms (cap arithmetic vs. key integrity), and folding them into one
criterion is exactly the clause-collapse that let VL-05 and VL-06 each ship invisible (P-04, P-13).
Both would grade **MET** at `b70d57b4` today, so neither changes a verdict — their value is that the
surfaces become *graded* rather than *incidentally covered*.

> **SC-13 (proposed) (REQ-03, cap preservation under adversarial text):** No `ops` operation can
> leave a section over its cap, whatever text an op carries. For every character `str.splitlines()`
> treats as a line boundary — the set derived at test time **from `str.splitlines()` itself, never a
> hardcoded character list** — an `ops` proposal whose `entry` or whose `target` embeds that
> character exits 12 with `MALFORMED OPS`, the file's sha256 is unchanged, and the file re-parsed by
> `parse_expertise` holds no section with more entries than its `CAPS` value. The at-capacity
> variant is exercised explicitly: the same proposal against a section already holding its cap
> re-parses at exactly the cap, never cap+1.
> **verify: automated        evidence: unit, integration**

> **SC-14 (proposed) (REQ-01, REQ-02, REQ-05, target identity):** No `ops` operation can write a
> line the tool's own parser cannot address as the id the op named. For every verb — `add`,
> `replace`, `drop` — a `target` that `ENTRY_RE` does not parse back out **equal to the target
> verbatim** exits 12 with `MALFORMED OPS` naming the offending target, and the file's sha256 is
> unchanged. Both failure shapes are exercised: a target `ENTRY_RE` does not match at all
> (`PPPP-1`), and a target embedding a shorter valid id that `ENTRY_RE` *does* match while capturing
> less than the whole target (`P-01: fake prefix`). The grammar is asserted **by round-trip through
> `ENTRY_RE`, never by a re-typed character class**, so the check cannot drift from the parser. And
> the no-lockout consequence is asserted directly: after a refused colon-prefix `add`, a legitimate
> `replace` of the embedded id exits **0, not 11**.
> **verify: automated        evidence: unit, integration**

Would-be evidence today: SC-13 → case21, case22, u17, u18. SC-14 → case23, case25 (incl. its
`a following legitimate replace of P-01 exits 0, not 11`), case26, u19–u22.

## 5. Unmet criteria, and non-gating findings

**Unmet: none.** No owning task id, no code-vs-tests routing required.

| # | Finding | Class | Nature | Rationale |
|---|---|---|---|---|
| N-1 | `_validate_target_grammar` runs **before** the `section` checks in `_validate_target_section`, so an op malformed in both keys reports `target` and never mentions `section`. No SC clause depends on it (SC-04's fixtures use a well-formed `P-01`), and the exit code is 12 either way. | advisory | chore | message precedence only; no behaviour or criterion changes |
| N-2 | `_reject_multiline` still keeps the narrower `"\n" in value or "\r" in value` branch above the `splitlines()` check; its own docstring says it never fires on its own. | advisory | chore | dead branch invites a future reader to believe the alphabet is two characters (carried from c3) |
| N-3 | No criterion covers REQ-03 clause 2 or the target-identity surface (§4). Remedy is the operator adopting SC-13/SC-14 — the tests already exist. | advisory | enhancement | grading-coverage gap, not a code or test gap |
| N-4 | Restated so it is not re-raised: SPEC §5.3 *apply-side* citation drift, the `EXPERTISE_MERGE_BIN` override in both suites, `cmd_ops` raising `FileNotFoundError` on a missing `--ops` path, the runner's caller-dependent discovery count, and the absence of a shipped gate binding Expertise id uniqueness. | backlog | bug/chore | pre-existing and already accepted; none is a ship blocker |

## 6. Proof nothing was changed

`git status --porcelain` from the worktree root at the end of grading — two entries, both paths I
own: this artifact, and one appended bullet in my own observations log (written through
`observations-merge.py apply`, never a read-then-write):

```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-pm.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c4.md
```

HEAD unmoved at `ac6c9c5b`. No commit, no formatter, no linter, no `git checkout`/`git stash`.
`BRIEF.md`, `plan.yaml`, `STATE.md`, `feature.json` untouched; the c2/c3 notes untouched; no
`notes/review-*.md` touched. The probe lived under `/tmp` and removed every temp root it made.

## 7. Open questions

- **Q1 (non-blocking, harness process; re-raised, now observed three times):** when a panel finding
  falsifies a REQ and the fix lands, no step turns that finding into a criterion. VL-01 → VL-05 →
  VL-06, each on a surface no SC names. For the harness owner: should a REQ-falsifying panel finding
  require a proposed SC alongside the fix?
