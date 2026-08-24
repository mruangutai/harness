# FEAT-35 — validate phase review

## Conclusion

**The rewrite is sound and should merge.** Nothing in the code under review is defective. All five
operator questions are answered and their consequences are on disk. What remains is one signature
and one short verification run, in that order.

Six of seven success criteria are met, each re-verified by the panel against both `569d417` and the
pinned `e0ae671` rather than taken from the build phase. The seventh, SC-03, was unclosable as
written; it has been amended and now needs one reviewer run to be graded at all.

**The most valuable finding is not a blocker and is deliberately not fixed here.** Four of the eight
assertions in the new regression test bind exact strings, so a future edit reintroducing stay-alive
behaviour in different words — "Await the team digest" — passes all eight green while the defect is
fully restored. That is filed as #804 with the ask attached: decide whether those assertions are
warranted at all before reaching for a better pattern, because a test that cannot fail on the case
it guards is worse than none — it reads as coverage.

## How this was assembled

**No report round was spawned.** Drawn entirely from run digests on disk:

- `runs/2026-08-23-01-product/digest.md` — PASS, plan signable in 5 tasks
- `runs/2026-08-23-02-product/digest.md` — PASS, consolidated revision, T-05 relaned to eng
- `runs/t04-product/digest.md` — PASS, DEC-201 landed, T-04 gate printed T-04-PASS
- `runs/t05-eng/digest.md` — PASS, test proven both directions, 9 named failures at `569d417`
- `runs/2026-08-24-01-product/digest.md` — PASS, DEC-201 control sentence corrected
- `runs/2026-08-24-01-validator/digest.md` — BLOCKED, the reviewer panel
- `runs/2026-08-24-02-product/digest.md` — PASS, `source_issues` added to the plan
- `runs/2026-08-24-03-product/digest.md` — PASS, SC-03 amended

`review_sha` is `e0ae671526978a2f8982de1c94121d836b97d098`, reviewed against `df18fe5`. Source
surface: 3 files, +201/-7. The tree was clean at the pin throughout and HEAD never moved.

## Success criteria — final state

| SC | Verdict | Basis |
|----|---------|-------|
| SC-01 | met (re-confirmed at `a2a373b`) | code-reviewer re-ran both SHAs; assertions fail at `569d417`, pass at `e0ae671` |
| SC-02 | met (re-confirmed) | both tokens present; no threshold line says refuse/blocked/prevented |
| SC-03 | **Clause A met; Clause B yours** | split by verifier after three failures; Clause A cited to c2, Clause B rests on your live-orchestrator measurements no agent can vouch for |
| SC-04 | met (re-confirmed) | no `phase:` write instruction; phase-exit paragraph names `status:` |
| SC-05 | **partial** | see the obligation below |
| SC-06 | met (RE-GRADED at `a2a373b`) | steps 3-7 graded with `file:line`; no surviving stay-alive instruction |
| SC-07 | met | `gen-decisions-index.py --stdout \| diff -` clean; DEC-201 row at `DECISIONS-INDEX.md:219` |

## SC-05 — the post-merge obligation, on the record

**What SC-05 exists to measure:** whether a stopped orchestrator actually survives a child running
past the 600s watchdog. The whole feature rests on it. If a stopped parent does not survive, this
change removes a noisy death and leaves a silent one.

**What was measured:** an orchestrator stopped, waited 1057.1s (`15:34:10.019Z` → `15:51:47.145Z`),
was woken, and continued — 0 Bash calls made to stay alive, not killed, closing with its own text.

**What was NOT measured:** that the rewritten playbook *causes* that behaviour. The run followed a
dispatch-level override, because a spawned agent loads skills from the main checkout while the
rewrite sits in the worktree. The gap is unsatisfiable before merge by construction.

**Obligation.** One orchestrator round-trip over 600s under the MERGED skill, no override in its
dispatch, measured the same way: longest survived gap, stall-call count, killed-at-600s.
**Owner: the main session, on the next feature that runs a build or validate phase** — that run
supplies the evidence for free; no dedicated run is needed.

## What remains, in order — REVISED after three SC-03 runs

0. **Commit the uncommitted `SKILL.md` nonce fix and RE-PIN `review_sha`.** The pin holds the
   defect (`e0ae671` greps 2 for `7Q4X2M9K`; working tree greps 0). Every verdict currently
   describes text that would not merge. Then re-confirm SC-01/02/04 and re-grade SC-06, whose c0
   certification covers the edited region.
1. **Rule on SC-03's third clause** — the `context-watch.py` row is unreachable by any reviewer.
   Drop it, accept the tool's rejection as fail-closed evidence, or re-spec onto `--warn-for`.
   My read and the c2 lead's agree: accept the rejection; a tool refusing an id it cannot vouch
   for is the safety property working, not a gap.
2. ~~**Re-sign both artifacts at 2026-08-24.**~~ DONE. Covers exactly three edits: `source_issues`, the
   DEC-200→DEC-201 id correction, and the SC-03 amendment. Nothing else rode on it — I verified the
   amendment touched SC-03 only and left `## Approval` byte-unchanged at `2026-08-23`.
2. **Then grade SC-03** — one reviewer run against the amended criterion. It is deliberately not
   done yet: verifying against unsigned criterion text would be void if the wording changes at
   signature. This is the last open gate.
3. Commit, PR (body takes `Closes #751` from `gh-sync.py closes`), merge, acceptance, `ship`.

## Resolved this phase

**`source_issues` is fixed end to end.** It was absent from `plan.yaml` entirely, so
`gh-sync.py closes` printed nothing and #751 plus #798-#802 would have survived the merge exactly as
FEAT-33's did. pm added `source_issues: [751]`; I re-ran `gh-sync.py open` to refresh the mirror
because `closes` reads `feature.json`, not the plan; `closes` now prints `Closes #751`.

**`parent_origin` stays `None`** — the instruction to write `created` was withdrawn. `gh-sync` sets
`created` only where it runs `gh issue create` itself (`:751`); #751 was authored by `mruangutai`
before any harness command, which is the adopted branch (`:742`). Writing `created` would have armed
`cmd_abandon` to close the operator's own ticket as `not_planned` and label it `abandoned`.

**`matrix_ok` remains FALSE, accepted explicitly** on the basis that the BRIEF disclosed the gap
before signature. It is not recorded as true.

**`base` could not be pinned into `feature.json`** — `additionalProperties: false`, validator returns
`undeclared key 'base' at /`. It lives in `STATE.md` and the handoff instead.

## Proposed backlog

| ID | Finding | Nature |
|----|---------|--------|
| B-1 | Assertions 1, 2, 7, 8 in `test-orchestrator-playbook.py` bind literal strings; a reworded stay-alive instruction passes all eight green — **now on #804** | bug |
| B-2 | `SKILL.md:156` is an orphaned fragment contradicting `:154-155` on whether budget exhaustion halts the loop. Pre-existing, byte-identical at `569d417:93` | chore |
| B-3 | `validate-digest.py` never checks that a **member's** artifact path exists — only a lead's (DEC-156). A ui-reviewer reported a file that was not on disk | bug |
| B-4 | No `eval` runner exists, so `ai_behavior` changes have no binding automated gate | enhancement |
| B-5 | `parent_origin` semantics are a trap: "a human created the issue" reads as `created` but means `adopted` | chore |
| B-6 | `feature.json` cannot hold the review base sha; every reviewer needs it and it travels only by prose | enhancement |
| B-7 | Run `2026-08-24-01-product` completed at 06:41 and was never added to `runs:`; its send-back went uncounted | bug |
| B-8 | `harness-team` seeded a colliding run id because `Glob` on `runs/*` matches files, not directories, clobbering a `state.yaml`. `runs/` is gitignored, so there is no recovery | bug |
| B-10 | `SKILL.md:105-107` says handing off "stops being optional" at 2x the threshold — a mandate DEC-198 does not license, three lines after "the decision is yours". Not a gate; nothing enforces it | chore |
| B-11 | Approval dates are day-granular, so a same-day amendment after signature is invisible to the record. Bit this feature twice | enhancement |
| B-9 | **Reported by pm, unverified by me:** `bash-write-guard.sh` coverage is redirect-shaped, not write-shaped — it blocked a heredoc redirect to an out-of-domain path while a `python3 -c open(path,'w')` in the same tool ran unchecked. Nothing was evaded; the write performed was in-domain. Whoever tickets this should verify it before acting | bug |

Already ticketed, cited not re-filed: **#803**, **#804**, **#805**, **#806**, **#808**.

## Two corrections to my own record

I was initially skeptical of the pm lead's self-reported clobber of
`runs/2026-08-24-01-product/state.yaml`. Checking timestamps showed the lead was accurate and I was
wrong: `digest.md` (06:41) predates the reconstructed `state.yaml` (07:10), so a real unrecorded run
did exist there. It reported its own error unprompted and I should not have leaned toward doubt
before measuring. The deliverable survives; only per-step sequencing metadata was lost, honestly
labelled `RECONSTRUCTED`.

The product lead also overturned its own member twice this phase — correcting pm's
`needs_approval: false` and refusing pm's `sc_status` entry for a criterion nothing had executed.
Both corrections were right.

## Budget

`cycles_used` 4 of 10 — two from the build phase, one for the DEC-201 run's uncounted send-back, one
for the panel's ui-reviewer send-back. 8 runs against an informational bound of 20; each resolved
something and none repeated another's work.
