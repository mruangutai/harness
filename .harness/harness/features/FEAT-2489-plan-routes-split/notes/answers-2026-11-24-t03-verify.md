# T-03 verify defect ruling — FEAT-2489 — 2026-11-24

Ruled by fable-advisor (AdvisorE2d_T03Verify).

- **Defect:** T-03.verify's `count('exit=') == 3` can never pass, because T-02's signed CLI lines carry `old_exit=`/`new_exit=`.
- **Fix:** amend only T-03.verify, replacing that clause with a count of lines that start with `exit=`.
- **Signature:** stands (DEC-23).

## Full ruling (verbatim)

All claims verified against the worktree. Measured facts:

- **Receipt** (`FD/notes/red-t03-stale-inventory.txt`): `.count('exit=')` = **19** — 8 `CLI …` lines × 2 (`old_exit=`, `new_exit=`) + 3 trailer lines (`exit=1`, `exit=2`, `exit=1` at receipt lines 169/176/511). Zero other lines contain `exit=`. The proposed replacement clause evaluates to exactly **3** against the committed receipt.
- **Clause** confirmed verbatim at `plan.yaml:454` inside the `if stale:` branch; `/tmp/e2-verify-T-03.sh` matches the plan's verify.
- **T-02's signed format** confirmed at `plan.yaml:397`: every cli_equivalent check prints `CLI STATE:LABEL argv=REPR old_exit=N new_exit=N mapped=N`. (One brief correction: it's 8 CLI lines — only the cli_equivalent checks print one, not all 9 equivalence checks — hence 16+3=19, not 18+3. Conclusion unchanged.)
- **T-03 intent** (`plan.yaml:503`) does require "the three whole outputs, each followed by exit=CODE" — so the substring-count clause contradicts the same task's own intent; unsatisfiable by construction, confirmed.
- **DEC-23** (`docs/DECISIONS.md:259-273`): a departure from a signed task's `verify` is governed by the ledger, one amendment judgement per changed field, "never by a fresh signature." `plan_merge/amend.py:233` lists `verify` in `LEDGERED_FIELDS`; `--reason` is mandatory (amend.py:250). Heavy precedent in FEAT-2488.
- **T-04 unaffected**, confirmed: `plan.yaml:551` does `suites.count('exit=0') == 3` on a **splitlines() list** — exact whole-line element match, so CLI lines (which start `CLI ` and merely contain `old_exit=0`) can never inflate it; `plan.yaml:550` `final[-1] == 'exit=0'` is likewise an exact last-line match.

---

**Authority.** DEC-23 (`DECISIONS.md:259-273`) + `plan_merge/amend.py:233,250`: `verify` is a ledgered amendable field of a signed task; one amendment judgement, signature stands, no approval reset (sole `reset` assignment is amend.py:163 per the FEAT-2488 c2 ruling precedent). AdvisorE2b_Signoff governs; this is the ledgered judgement.

**Gap.** T-03.verify's receipt clause `read().count('exit=') == 3` (plan.yaml:454) counts substrings, but T-02's signed CLI trailer (plan.yaml:397) embeds `old_exit=`/`new_exit=` in each of the 8 cli_equivalent lines the whole-output receipt must carry (T-03 intent, plan.yaml:503). Measured: 19 hits. The clause contradicts the same plan's signed intents — a verify drafting defect, not a build defect. The build (3b6f2a42) and every other evidential clause of T-03.verify hold as reported; I re-ran the counts, not the suites [the suite/audit results themselves: verified against the committed receipt, not re-executed].

**Ruling.** Amend **T-03.verify only**, via `plan-merge.py amend --key tasks --field verify` with `--show`/`--expect-sha256` discipline. Replace the receipt clause at plan.yaml:454 with exactly:

```
sum(1 for l in open('.harness/harness/features/FEAT-2489-plan-routes-split/notes/red-t03-stale-inventory.txt').read().splitlines() if l.startswith('exit=') and l[5:].lstrip('-').isdigit()) == 3
```

This checks the intent's literal shape — three outputs, each followed by a line `exit=CODE` — and is immune to the CLI trailer by line anchoring (no checker line starts with `exit=`; CLI lines start `CLI `, echoed output is `| `-prefixed, diff lines sit under `--- diff` headers per T-02's signed format). Both alternatives are correctly rejected: stripping CLI lines falsifies "whole outputs"; reformatting the checker reopens signed, committed T-02.

Amendment reason (233 chars):

> T-02's signed CLI lines carry old_exit=/new_exit=, so the whole-output receipt holds 19 'exit=' substrings and count('exit=')==3 is unsatisfiable by construction. Replaced with a line-anchored count of the three exit=CODE trailer lines.

**Constraints.**
1. One field, one task, one judgement; the signature stands (DEC-23). No re-sign, no approval reset, no touch to T-03.intent, files, SCs, or decisions.
2. Change nothing else in the verify — the live-run asserts (t.returncode==1, a.returncode==2, fails ⊆ the two canonical keys) already pin the exit values the trailers mirror, so the shape-only receipt check is the weakest sufficient clause; do not "strengthen" it to exact trailer values in the same amendment.
3. After the amend, re-run the amended verify once end-to-end and record exit 0; do not rewrite the receipt — it is correct as committed.
4. T-04 needs no amendment (plan.yaml:550-551 verified exact-line matches); do not touch it.
