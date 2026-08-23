# Ruling applied — T-13 intent and SC-13 (FEAT-32)

**Applied, nothing re-opened.** Three phrasing edits landed under the existing approval; no
approval block, no `status:`, no SC-14, no code file touched.

## 1. T-13 intent — the count is now a floor, not a total

`plan.yaml` T-13 item 4 (`intent:`) no longer says "SEVEN … as seven, not four". It instructs the
documentor to write **"at least eight occurrences measured as of this commit, and the mechanism
fired again during the build of its own fix"**, names occurrences 5–8 as products of this feature's
own runs, and says explicitly why a bare total is unwritable: the count has already moved
four → seven → eight and `DECISIONS.md` has no propagation checker (DEC-188), so a bare integer
becomes a false statement nothing detects.

## 2. Occurrence 8 added

Run dir `runs/2026-08-21-2-product/digest.md:28`. Claim, now measured rather than argued: a lead
force-closed with a member in flight has **no honest word available**, because the digest validator
ranks only `PASS`, `FAIL`, `ESCALATE`, `BLOCKED` — `.claude/skills/harness/bin/validate-digest.py:703`,
verified at source in this worktree (`:705` is `worst, worst_src = None, None`, unrelated; `:702` is
also wrong and both had been written down). Occurrence 7 measured that the mechanism *permits* a
false verdict; occurrence 8 measures that it *demands* one. Occurrences 5–7 stay pinned to
`2026-08-21-1-product`, untouched.

`notes/research-FEAT-32-operator-request.md:26` corrected from `:705` to `:703`.

## 3. The brief/plan disagreement is now stated in the plan

T-13's intent carries one paragraph saying `BRIEF.md:16` stays at "seven measured occurrences"
because the operator declined to reset the brief's approval for prose, that the disagreement is
therefore deliberate, and that neither document is to be edited to match the other.

## 4. SC-13 — the YAML entry-point split, recorded as a known limitation

Added as a sixth statement in SC-13's enumeration, in the criterion's own voice: `plan-merge.py:37`
imports stdlib `yaml` while `harness_yaml.py` raises `DuplicateKeyError` at any depth; measured on a
`plan.yaml` with a duplicated `status:` key, `safe_load` accepts and keeps the last value,
`harness_yaml.load_str` rejects naming line and column, and the identical document without the
duplicate is accepted by both (the control). Accepted because it **fails closed and loudly**; the
code fix is a follow-up outside FEAT-32 (the coordinator files it).

## 5. The self-count, enumerated at source

SC-13's list before this edit held **five** semicolon-delimited clauses, not six: (1) a wait is
impossible, `stop_hook_active` reason; (2) a second identical return ships anyway; (3) an orphaned
child of an interrupted parent is unreachable; (4) the identity limit as a bound on every CLI;
(5) #627, #560, #605 out of scope with #627 named. The trailing "a record naming four of the six
fails" was already false before this edit. Resolved by **removing the integers entirely** — it now
reads "a record that names every statement but one still fails" — for the same reason ruling 1
rests on: the statement count will move again and no checker would catch a stale number.

## Verification

- `yaml.safe_load` parses `plan.yaml`; tasks **17**, decisions **10**; statuses `{done, pending}` unchanged.
- `check-plan-routes.py` exit **0** (6 pre-existing DEVIATION lines, 0 violations — unchanged by this run).
- `BRIEF.md` diff is one hunk, `@@ -338,3 +338,12 @@` — SC-13 only. Line 16 byte-identical to `b013dde`.
- Both approval blocks byte-identical to `b013dde`. SC-14 region byte-identical.
</content>
</invoke>
