# UI Review — Cycle 3 — FEAT-45-adversarial-plan-panel — pin `d78f393`

## BLUF
Mode B. No UI surface in this diff — **measured**, not predicted. `in_scope: false`. Additionally
audited the one adjacent surface named in dispatch (operator-facing validator rejection text): the
new/rewired messages are actionable; nothing gates.

## Census (the required measurement)
`git diff --stat main...d78f393` / `git diff --name-only main...d78f393` (three-dot, merge-base
`ba338d8`): **71 files changed**, 7931 insertions(+), 152 deletions(-).

Extension breakdown across all 71 files:

| ext | count |
|---|---|
| .md | 55 |
| .py | 8 |
| .yaml | 3 |
| .ts | 2 |
| .sh | 2 |
| .json | 1 |

**User-facing-surface extensions (.tsx/.jsx/.css/.html/.svelte/.vue): 0 files.** No rendered UI
component, stylesheet, or markup exists in this diff.

**`DESIGN.md` for this feature: does not exist.** Checked two ways — `find` under
`.harness/harness/features/FEAT-45-adversarial-plan-panel` for `DESIGN.md` (no match) and
`git show d78f393 --stat --name-only | grep -i design` (no match). This feature never produced a
design contract, consistent with it being validator/hook/spec plumbing with no rendered surface
(c0/c1/c2 UI reviews reached the same conclusion — this is the fourth consecutive cycle with an
identical, re-measured result).

The 55 `.md` files are almost entirely per-feature process records (BRIEF, STATE, receipts, review
notes, plan.yaml) — narrative content this role's remit explicitly does not extend to (P-03: markdown
is only in-scope when it specifies spacing/colour/states/interaction for a *rendered* surface, which
none of these do).

**Verdict on self-scope: OUT.** PASS with `severity_max: n/a`... except the one adjacent surface my
dispatch explicitly hands down (below), which I did audit.

## Adjacent surface: operator-facing rejection message text (in remit per dispatch)

Working tree confirmed byte-identical to the pin for `validate-digest.py`
(`diff <(git show d78f393:…/validate-digest.py) …/validate-digest.py` — empty). Line numbers below
are against the pin.

### 1. `_skipped_member_error`'s new persona restriction — `validate-digest.py:944-946`
> `"only the optional fable-advisor may be recorded as skipped; mandatory members must carry their verdict."`

**Judgement: adequate, not a defect.** It states the rule (fable-advisor only) and the remedy in the
same sentence ("mandatory members must carry their verdict" — i.e., dispatch/re-dispatch the member
and transcribe its actual verdict, don't mark it skipped). This is measurably *better* than the
carried-forward M7 shape (states fact, no remedy) — it does state a remedy, just a terse one.
**BACKLOG (improvement, not gating):** could be more concrete ("re-run the member and report its
verdict" vs. the current implicit phrasing), but a reader can act on it as written.

I also checked whether this restriction is itself a behavioral regression (dispatch's suspicion #1):
it is not, by design — `BRIEF.md:164` and `SC-17` (`BRIEF.md:178-183`) both establish
`fable-advisor` as *the one optional reader*; every other panel member (`harness-qa`,
`harness-code-reviewer`, `harness-security-reviewer`, `harness-ui-reviewer`) is documented as
mandatory and must carry a verdict, never `skipped`. The restriction enforces the documented
contract rather than narrowing past it. [Demonstrated: read BRIEF.md directly, not inferred.] I note
for the code/security lens (not mine to rule on) that `check-state.sh`'s separate INV-32 check
(`check-state.sh:230-241`, unchanged this diff) accepts `status: skipped` from **any** persona with
persona+reason as a `warn`, not restricted to `fable-advisor` — that check operates on a different
artifact (`plan.yaml`'s `panel.readers`, at plan-review time) than `_skipped_member_error` (the
lead's own build-panel digest `members:` field), so this is not necessarily an inconsistency, but I
flag it as an open question for the code-reviewer/security-reviewer lens since it is a cross-schema
behavioral question outside mine.

### 2. `_branch_corroboration_error` — reused unchanged, newly wired into the plan-review path (F1) — `validate-digest.py:816-823`
> `"code_grade cannot be bound to review_sha: this feature's recorded branch (%r) does not match the current checkout's branch (%r) — the digest's artifact: line must name the feature actually under review in this checkout, not another shipped feature's notes/ path."`

**Judgement: good, actionable.** Names the two mismatched values and tells the reader exactly what
to fix (point `artifact:` at the feature actually under review). This message text is unchanged by
F1 — F1 only added a second call site (`_pending_plan_review_error`, line 928) — so it is not new
prose to grade fresh, but it is now reachable from a second path and reads correctly there too.

### 3. `inflight_registry.feature_root` path (`_hook_feature_dir`, `validate-digest.py:1359-1370`) — no distinct message
`_hook_feature_dir` swallows every exception (registry import failure, lookup failure) and returns
`None` with **no operator-facing text of its own**. On `None`, `validate()` falls through to its own
`_resolve_feature_dir`/`_root_or_none()`, which — for an unmerged feature whose `feature.json` does
not exist under the owner root — eventually surfaces the **pre-existing** `_read_review_sha` message:
`"code_grade cannot be bound to review_sha: {fj_path} could not be read ({e}), so the claim is not
trusted."` This message states the fact but not the remedy (same shape as carried-forward M7). It is
untouched by this diff (not new text), so per this role's convention I do not file a fresh remedy
against it — noting it only as a pre-existing, non-gating gap that a reader landing here via the new
registry path will also hit. **BACKLOG, not mine to fix** (P-11: an untouched pre-existing sibling
message is not this cycle's remedy scope).

I also checked (dispatch suspicion #2) whether the registry-lookup-failure path fails closed on
honest work: `inflight_registry.feature_root` (unchanged by this diff — confirmed via
`git diff main...d78f393 -- .../inflight_registry.py`, empty) already degrades gracefully to
`owner_root` on any internal exception or on no worktree match, which is the *same* value
`_hook_feature_dir`'s own outer `except Exception: return None` fallback effectively reproduces via
`validate()`'s independent `_root_or_none()` call. No new closed-failure mode was introduced by
wiring this in — the fallback the registry already had is the same fallback the caller falls back to
on total failure. [Demonstrated: read both functions directly.]

## Findings summary

| # | Finding | Gate? | Why |
|---|---|---|---|
| 1 | No UI surface in diff (measured) | n/a — correctly scoped out | 0/71 files carry a user-facing extension; no DESIGN.md exists |
| 2 | `_skipped_member_error` fable-advisor-only message could name a more concrete remedy | **BACKLOG** | already states a remedy, just terse; not a defect |
| 3 | Pre-existing `_read_review_sha` message states fact, not remedy, now also reachable via the new registry path | **BACKLOG** | text untouched by this diff; same shape as carried-forward M7, not new scope |

**No `must_fix` items. `severity_max: low`** (advisory polish only, per dispatch's own steer that
message-text notes are almost certainly backlog).

## Open questions
- Whether `check-state.sh` INV-32's persona-agnostic skip-acceptance (`plan.yaml` panel-reader
  records) and `validate-digest.py`'s `fable-advisor`-only skip restriction (lead digest `members:`
  records) are two intentionally-different schemas for two different moments in the workflow, or
  should converge — this is a cross-schema behavioral question for the code-reviewer/security-reviewer
  lens, not mine to rule on.
