# Handoff — FEAT-03-subissue-mirror, plan → build — written at 1ce886a, seq-2 (supersedes seq-1)

## Next

**Wait for the user's signature, then start the build phase.** Both `## Approval` blocks are
`status: pending` (BRIEF.md:203, PLAN.md:504) — an unapproved artifact stops a build mission at step 0.
On signature, build T-01..T-08 in PLAN order; PLAN's `## Preconditions` (:39-57) must be read FIRST —
one precondition is already satisfied (pycache ignore) and one is an **outstanding main-session
pre-ship edit** (`.claude/skills/harness/SKILL.md:137,144`, SC-13's subject) no agent domain covers.
**T-08 is owned by harness-documentor, a PRODUCT squad member** — route it laterally through
product-lead, not eng-lead (Q8). Fix cycle 1 is closed; `cycles_used: 1` of 10.

## Trust

- BRIEF.md (203 lines, 9 REQ, **13** SC) and PLAN.md (504 lines, D-01..D-06, T-01..T-08, new
  `## Preconditions`) repaired; both `## Approval` `status: pending` — grep of both — verified-at 1ce886a
- All six `must_fix` resolved; eng-lead's per-id `defect_verdicts` in
  `runs/2026-07-31-04-eng/digest.md` — that file is the receipt, not this note — verified-at 1ce886a
- **SC-06's four absence-greps genuinely fail today**, so they can only pass after T-02:
  `"-F", f"sub_issue_id=` ×1, `"-F", f"issue_id=` ×1, `"--jq", ".id"` ×2, `/parent"` ×1 in
  `wayfind.py` — ran `grep -cF` on each — verified-at 1ce886a
- **SC-06's second half passes VACUOUSLY today and that is correct:**
  `grep -cE 'parent_args|blocked_by_args' gh-sync.py` is **0** — a regression guard on builders T-02
  creates, not an absence-grep proving a change. Do not "fix" it — ran it — verified-at 1ce886a
- Budget raised by the user 40 → 120 (`harness.json:234`, rationale `:237`, commit 1ce886a); ~$87
  spent, all in planning — `git show` + per-agent snapshot deltas — verified-at 1ce886a, approximate
- Tree clean, nothing pycache tracked or untracked (`git status --porcelain` empty) — verified-at 1ce886a
- seq-1's Trust claims still hold (`test-gh-sync.py` exit 0 with both contract-encoding assertions
  live; `test_kinds.unit.detect` matches zero files; `deploy.sh` copies `bin/` as a directory;
  `check-docs.sh` exits 0): af2159e..1ce886a touches only `.gitignore`, the gitignore snippet, one
  removed `.pyc`, `harness.json`'s `budgets` block, `.harness/logs/` and FEAT-03's own artifacts —
  re-pinned by **diff intersection**, not by re-running — verified-at 1ce886a
- Mirror invariants are provable only against the fake `gh` (`github.sync: false`, `repo: null`); the
  live API path rides on DEC-168's measured probe — UNVERIFIED at this sha (inherited)

## Dead ends

- **Path-level greps for SC-06** — unsatisfiable and self-voiding: the retained list GETs
  (`wayfind.py:113`, `:117`) and the extracted writes build the identical endpoint string.
  Discriminate on payload/lookup only — BRIEF SC-06:75-89 — source: MF-1, closed this cycle
- **The `ticket` dry-run print at `wayfind.py:262-263`** — stays verbatim; it is why the `-F` checks
  are scoped to the argv form, not the bare `sub_issue_id=` substring — BRIEF SC-06:88-89
- **`grep -- '--jq .id'`** — zero matches, passes vacuously; the source carries the two-argv-item
  form. Recorded in PLAN as a documented false green — source: MF-1
- **Merging T-05+T-06 / any change to the task count** — held at 8 deliberately; the current
  decomposition is the premise of the signature. A merge is a `D-NN` — source: orchestrator, this cycle
- **Feature B, both halves of the razor** — extracting the `blocked_by` write and the parent read is
  IN; `gh-sync.py` *calling* either is OUT — BRIEF `## Out of scope`, pinned by SC-06 — source: grilling
- **Re-probing closure semantics**, and **asserting on `sub_issues_summary` right after a write**
  (eventually consistent) — DEC-168 — source: grilling `## Facts I verified`
- **Retrofitting FEAT-01/FEAT-02/kaya's FEAT-03** — new features only — BRIEF `## Constraints`
- **visual-designer / ui-reviewer, and renaming the feature id** — no visual surface, no DESIGN.md,
  prototype gate re-confirmed NO — `feature.yaml skipped_segments`, Q4, Q6

## Working set

- `.harness/features/FEAT-03-subissue-mirror/PLAN.md` (read `## Preconditions` first)
- `.harness/features/FEAT-03-subissue-mirror/BRIEF.md`
- `.harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-04-eng/digest.md`
- `.claude/skills/harness/bin/{gh-sync.py,wayfind.py,test-gh-sync.py}`
