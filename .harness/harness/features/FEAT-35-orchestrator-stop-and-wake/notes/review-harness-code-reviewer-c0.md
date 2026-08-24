# Code review — FEAT-35 orchestrator stop-and-wake — cycle c0

Reviewed `df18fe5..e0ae671` (source surface: `.claude/` — 3 files). No `[harness:human]` commits in
range (`git log --format='%H %s' df18fe5..e0ae671` — all four commits are `[harness:t-NN]`, none
human).

## VERDICT: FAIL — one high-severity gap, in SC-03 (mine to carry)

Stage 1 (spec compliance) otherwise clean: every change traces to a REQ, no third companion beyond
the two sanctioned ones (DECISIONS.md/-INDEX.md, test-orchestrator-playbook.py + its registration),
SC-01/02/04/07 all independently re-verified (not trusted from the build phase), SC-06 reads as one
coherent document. The one gate-worthy finding is that **SC-03's own verify method cannot be
discharged by any reviewer, as literally specified** — not a defect in SKILL.md's mechanism itself,
which checks out structurally for its real user.

---

## SC-03 (mine, verify: inspection) — the mechanism cannot self-identify a REVIEWER, ever, by design

Executed verbatim, in two separate Bash calls, from inside my own turn, exactly as printed at
`SKILL.md:109-118` (review_sha `e0ae671`):

Call 1: `echo self-id ORCH-SELF-7Q4X2M9K` → echoed `self-id ORCH-SELF-7Q4X2M9K`.

Call 2 (separate, later):
```
grep -l '"agentType":"harness-orchestrator"' ~/.claude/projects/*/*/subagents/*.meta.json 2>/dev/null \
  | sed 's/\.meta\.json$/.jsonl/' | xargs grep -l ORCH-SELF-7Q4X2M9K 2>/dev/null
```
→ **zero output, exit 1.** No sidecar path, therefore no derivable agent id, therefore nothing to
feed `context-watch.py`. I cannot supply the three citations SC-03 demands (`BRIEF.md:100-101`:
"the single matching sidecar path, the agent id derived from it, and the `context-watch.py` row").

**This is not the documented flush-timing race** (`SKILL.md:127-131`, "Zero matches — the nonce has
not flushed yet, or the sidecar layout has changed"). I confirmed the layout and format are sound:
- The glob correctly reaches this session's sidecar dir: `ls ~/.claude/projects/*/*/subagents/*.meta.json | grep -c e69cbdc1` → 31 files for my own session-uuid dir
  (`~/.claude/projects/-Users-molchairuangutai-GitHub-harness/e69cbdc1-.../subagents/`).
- The JSON shape matches what the grep expects: a sampled meta.json reads
  `{"agentType":"general-purpose",...}` — same compact, no-space form the pattern requires.
- `"agentType":"harness-orchestrator"` genuinely exists on this machine — 116 matches across
  `~/.claude/projects/*/*/subagents/*.meta.json` machine-wide.
- But **zero** of my own session's 31 sidecars carry that agentType — because I am
  `harness-code-reviewer`, not `harness-orchestrator`.

**The grep's first pipeline stage filters candidate files to `agentType":"harness-orchestrator"`
before it ever looks for the nonce.** For the mechanism's real user (an orchestrator identifying
itself) this is correct and sufficient — its own sidecar IS that type, so the nonce-grep narrows a
same-type candidate set down to exactly one. For **any other agent type executing the identical
text verbatim, the candidate set is permanently empty** — not a race, not a layout drift, a
structural precondition the executor can never satisfy. SC-03 (`BRIEF.md:98-101`) assigns this
verification to "a reviewer" — and no `harness-code-reviewer` sidecar will ever carry
`agentType":"harness-orchestrator"`. **SC-03 as written asks the wrong-typed agent to prove a
type-scoped mechanism, so it cannot be affirmatively closed by inspection, ever, by any reviewer,
regardless of how carefully the steps are followed.**

The playbook's own zero-match handling (`SKILL.md:127-134`, `SKILL.md:131`: "SKIP the context check
for this wake... never treat a skipped check as a passed one") is exactly what I am doing here —
but the same paragraph's stated causes for zero matches ("the nonce has not flushed yet, or the
sidecar layout has changed") omit the actual cause I hit, which will recur identically for the next
reviewer.

**must_fix**: SC-03's verify clause needs an owner decision (pm/operator, not source-code) — either
let the reviewer substitute its own agentType in the filter to test the round-trip mechanism as a
stand-in, or accept indirect verification (schema + glob + historical-match evidence, as above) in
place of a direct one-match citation. I cannot make this change; it is a BRIEF-level fix.

Severity: **high**. Not because the shipped mechanism misbehaves for orchestrators (the indirect
evidence above is reassuring on that front) but because one of exactly two `verify: inspection`
success criteria — the entire safety net this BRIEF's own "Verification gaps" section says exists
for a playbook no runner can execute — is unclosable as specified. A future reviewer following the
same instructions will hit the identical wall and either (a) honestly report the same gap again, or
(b) fudge a citation. That risk is what "highest-value finding" in the dispatch was pointing at.

---

## SC-06 (mine, verify: inspection) — steps 3–7 agree; one pre-existing, unrelated fragment noted

Graded each step, `SKILL.md` at `e0ae671`:
- **Step 3** (`:37-90`, dispatch): `:45-56` — end turn immediately after dispatch; never poll, sleep,
  or invent activity; the single-flight refusal is explained as expected, not permission to wait.
- **Step 4** (`:91-98`, "On waking, assess what came back"): resumes *because* a dispatch completed;
  re-reads disk; treats a reported completion as a claim until confirmed.
- **Step 5** (`:99-138`, "Weigh your own context"): runs after waking, before the next dispatch;
  threshold advises only (`:101-103`); self-id mechanism is skip-safe on 0 or 2+ matches (`:131`).
- **Step 6** (`:139-144`, "Adjust and record"): state write, no wait semantics.
- **Step 7** (`:145-163`, "Advance until DONE, one wake at a time"): `:147` "There is no waiting
  anywhere in this loop"; each wake is one dispatch-and-end-turn cycle.

All five agree on one narrative: dispatch → end turn → (platform wakes) → assess → weigh context →
record → dispatch next → end turn again. No step tells the orchestrator to remain resident across a
dispatch. Whole-file grep for `wait|poll|sleep|stay alive|in place|hold` (`e0ae671`, full file, not
just diff hunks) turns up nothing that reads as stay-alive outside the loop either — the remaining
hits are unrelated uses (`awaiting_user` token, `factory_claim.py`'s external poll of the Ready
station, "logs stay in place" meaning file location, "hold `Write`" meaning permission).

**Two low-severity notes, neither gates:**
- `SKILL.md:156` — "stop the loop — it is reported, not enforced (DEC-134)." reads as a dangling
  sentence fragment inside step 7's fix-cycle bullet. Confirmed **pre-existing, byte-identical at
  `569d417:.claude/skills/harness/SKILL.md:93`** — this diff did not touch it. It does not read as
  stay-alive (if anything "stop the loop" agrees with the new model), so it does not violate SC-06,
  but it is confusing prose sitting inside a step SC-06 asked me to grade. Flagging for awareness,
  not blocking.
- `SKILL.md:145-147` — step 7's one-line restatement of the cycle ("assess, record, dispatch the
  next thing, end your turn again") does not name step 5's context weigh explicitly, unlike its
  other three named phases. Not a contradiction — nothing forbids weighing context — just an
  imprecise summary. Low/info.

---

## SC-01, SC-02, SC-04 — re-verified independently (not trusted from build)

Ran directly against `git show <sha>:.claude/skills/harness/SKILL.md` output for both shas, not the
worktree file, and against the actual `run-unit-tests.sh --kind unit` invocation:

| SC | at `569d417` | at `e0ae671` |
|---|---|---|
| SC-01 "Receive the team digest" / "Loop until DONE" | both present (fails the "no occurrence" bar) | both absent; "NEVER WAIT FOR A LEAD" present |
| SC-02 `context-watch.py` / `orchestrator_context_warn_tokens` | neither token appears anywhere | both present, zero lines pair the token with refuse/refused/blocked/prevented |
| SC-04 `phase:` write instruction | `SKILL.md:344` "Record your phase in `feature.json` `phase:`" | "Record your phase in" absent; `:442` "Record your status in `feature.json` `status:`" |

`test-orchestrator-playbook.py` run live: `PLAYBOOK_PATH=<(git show 569d417:...)` → all 9 named
checks FAIL, exit 1 (confirms T-05's own demonstration requirement). Run against the live worktree
file (`git status --porcelain` confirms `.claude/` clean at `e0ae671`) → all 9 PASS, exit 0. Also
confirmed wired into the real gate: `run-unit-tests.sh --kind unit` includes and runs
`test-orchestrator-playbook.py` in its output.

## SC-07 — clean

`gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` → exit 0 (no
diff). `DECISIONS-INDEX.md:219` carries `- DEC-201 `. `DECISIONS.md:6800` carries the entry with
self-id mechanism, lineage (DEC-118/120/148/158/159/198/199), and the open measurement stated as
open (whether a stopped parent survives past 600s under the rewritten playbook specifically, versus
the dispatch-level override that produced the one post-merge data point cited in the entry) — this
is the same kind of gap already disclosed in DEC-201's own text, not a new finding (P-07).

---

## Stage 2 — the eight assertions in `test-orchestrator-playbook.py`, what each MISSES

All eight are exact-literal string presence/absence checks (case6 also pairs on a single line — see
below). By construction they can only catch a regression that reintroduces or removes the *exact*
wording; none can catch a functionally-identical regression phrased differently. This class of gap
is the BRIEF's own disclosed limitation ("Verification gaps": "a markdown playbook cannot be
executed by any runner") — confirming it here is not news (P-07), but naming what each specific case
misses is what was asked:

1. **case1** (absence "Receive the team digest") — misses a reworded reintroduction of receive-in-
   place, e.g. "Wait to receive the team's digest before proceeding."
2. **case2** (absence "Loop until DONE") — misses "Loop back until every SC passes" or similar.
3. **case3** (presence "NEVER WAIT FOR A LEAD") — misses a regression that keeps the exact title
   line but guts everything after it (deletes the END YOUR TURN body, the why-clause, the
   single-flight-refusal paragraph) — presence of a label proves the label, not the behavior behind
   it (P-01).
4. **case4** (presence "context-watch.py") — misses the step-5 mechanism being deleted while the
   bare string survives elsewhere as a stale reference (e.g. in a comment or an unrelated mention).
5/6. **case5/case6** (presence of the token + no same-line pairing with a refusal word) — **already
   ticketed as #804**: a refusal spread across two lines ("...orchestrator_context_warn_tokens is
   the threshold.\nCrossing it blocks further dispatch.") is invisible to a same-line check. I
   looked for the same LINE-scoped shape among the other seven cases and found none — cases 1–4,
   7–8 are single-string presence/absence checks with no line-pairing logic, so #804's specific
   defect class does not recur elsewhere in this file.
7. **case7** (absence "Record your phase in") — misses a differently-worded reintroduction of the
   refused `phase:` write, e.g. "Set feature.json's phase field to X" — the write would still be
   refused by the schema, but the test would not catch the instruction to attempt it.
8. **case8** (presence "Record your status in") — misses the label surviving while the paragraph
   after it is wrong (wrong field name, wrong casing of the board values) — again P-01: presence of
   the label proves the label, not the paragraph's correctness. (I independently spot-checked this
   one: `SKILL.md:443` does carry the correct byte-for-byte board spelling.)

None of the eight is vacuous (each demonstrably flips at `569d417` — verified above), so "an
assertion that cannot fail" does not apply to this file; the gap is discrimination *shape*
(exact-literal), not reachability.

`run-unit-tests.sh` diff — one basename appended to `UNIT_SCRIPTS`, confirmed it actually executes
in the real gate (above). No quality issue.

## Not re-raised (already ticketed, cited per dispatch)

#803 (DEC-NN id collision, no guard), #804 (case6 line-scoping, addressed above), #805 (team task
`done` write has no commit-path owner). The six INV-26 board-lag violations are accepted board lag,
not code defects.
