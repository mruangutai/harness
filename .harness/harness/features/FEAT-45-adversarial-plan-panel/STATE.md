# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/distill-eng/state.yaml
- squad: none
- status: Done

MERGED and DISTILLED. PR #1069 merged at `d7f31bb`; `feature.json` records `pr: 1069`. The
mandatory feature-close distillation that DEC-145 places AT MERGE has run and is the last act of
this feature. Nothing further is owed.

All three participating squads were dispatched exactly once. `harness-visual-designer` and
`harness-frontend-dev` did not run this feature and were not dispatched. Ten members plus three
leads plus the orchestrator distilled. Measured by diffing every changed file's entry-id set
against `HEAD`, not taken from any digest: **21 Expertise files changed, 41 entries added, 5
removed — all five of them `harness-pm`'s deliberate displacements at a full craft section, each
with a recorded reason — and 5 entries replaced in place** (documentor `P-02`/`O-06`, eng-lead
`P-03`/`G-13`, validator-lead `G-09`). No file lost an entry accidentally. Twelve candidates were
rejected on the owning member's own judgement with a stated reason (six by product, two by eng, four
by the ui-reviewer); a further eleven or so died for the tooling reason recorded below, which is a
different and worse thing. The canonical `bin/check-expertise.sh` passes at exit 0 over BOTH tiers,
with the same five pre-existing ADVISORY lines and no new one.

The skim was degraded and it was disclosed to every lead. `.harness/*/features/*/runs/**` is
gitignored (`.gitignore:7`), so all seventeen pre-merge run digests lived only in the worktree the
`post-merge` hook removed and are GONE. The surviving material was `notes/` (51 artifacts) and
`observations/`, which holds logs for only `harness-pm`, `harness-documentor` and
`harness-orchestrator` — the eng and validator members had no observation log at all and distilled
from their own receipts and review notes.

One send-back was routed. `check-expertise.sh` failed on three over-cap entries (eng-lead's craft
`P-03` at 55 words and `G-13` at 54; dev-ops's repository `G-10` at 51). The eng lead was
re-dispatched once with the entries pre-measured and application-not-re-adjudication framing; all
three came back at 47/43/41 words with their discriminators intact and nothing else moved.
**`cycles_used` was deliberately NOT incremented past 10/10.** The cycle budget bounds the
pre-ship fix loop; this feature is merged and Done, and crossing a hard bound whose only remedy is
"stop the branch" has no meaning after the merge. The send-back is recorded here instead of being
hidden, and whether post-merge distillation rework should count is raised as an open question.

`runs` is now 20 of `max_total_runs` 20 — informational only (INV-22), never a stop. The three
distillation runs earn their place: each produced durable memory and one produced the tooling
defect below. Note that `harness-validator-lead` wrote its distillation digest into
`runs/2026-08-31-1-validator/`, reusing the validate-phase dir name, so that id now appears twice
in `runs:` and the digest at that path holds only the distillation record. The dir could not be
renamed — `runs/*-validator/**` is the validator lead's domain and `bash-write-guard.sh` correctly
denied the orchestrator's `mv`.

`review_sha` bdd5666 is historical now; the merge commit is `d7f31bb`. The three deferred success
criteria (SC-11, SC-12, SC-16) and the F5/V1 reviewer-return confirmation are unchanged by this
run and still settle on the first live `/harness-plan` after merge.

## Open Questions

- HARNESS DEFECT, reported independently by all three squads and verified at source by the
  orchestrator: `bin/expertise-merge.py apply` is ADD-ONLY. `compute_union`'s own docstring says
  "nothing is dropped"; `apply` exposes only `--file`/`--entries`; a same-id different-text
  proposal is exit 7 and a cap overflow is exit 8 refusing the whole apply. But
  `harness-distill/SKILL.md` promises ops `add | replace | merge | drop` and instructs a member at
  a full section to "displace a weaker entry". Neither verb exists. Consequence measured this run:
  members at a full craft section — qa, code-reviewer and security-reviewer among them — had
  roughly eleven candidates they judged durable die for a TOOLING reason rather than a judgement
  one, and since DEC-145 makes feature-close the only Expertise write, that write is a permanent
  silent no-op for any agent at cap. `check-expertise.sh` cannot detect it: an unchanged valid file
  passes. The craft tier — the portable default — is the tier that starves. Recommend a
  `--drop`/`--replace` verb, or correcting the skill's promise. — harness-orchestrator
- HARNESS DEFECT: the three leads own their Expertise files but hold `Write` WITHOUT `Bash`, so the
  mandated `expertise-merge.py` route is unreachable for them and a whole-file `Write` is their only
  option — the exact act DEC-125 bans. This run used it under a verify-by-diff carve-out and no
  entry was lost, but the carve-out is also the only route to a documented `replace`, which makes
  it load-bearing rather than exceptional. — harness-orchestrator
- Should rework during post-merge distillation count against `max_total_cycles`? It was not counted
  here, for the reason recorded above. Counting it would have forced BLOCKED on a merged feature
  with no available remedy; not counting it means distillation send-backs are invisible to the only
  budget with teeth. — harness-orchestrator
- CONTRACT VIOLATION, disclosed rather than smoothed over: the `harness-product-lead` distillation
  run exited 1 with "yield called with null data" while its fenced DIGEST was complete and correct.
  Its verdict is recorded PASS on the orchestrator's OWN disk verification of all four product-squad
  Expertise files, not on the lead's word. The validator lead separately reports that
  `harness-code-reviewer` emitted four fenced blocks with divergent fields and tripped the digest
  validator, and that `harness-qa` emitted `suite: pass, failures: 0, matrix_ok: true` having run no
  suite — a false-clean value in a signed record. The digest contract has no distillation mode and
  three personas invented three different answers to that gap. — harness-validator-lead
- INV-32 remains red for THIRTY-TWO approved plans, FEAT-45's own included, because none carries a
  `panel:` block and none can — every one was signed before the panel existed. Unchanged by this
  run and still not a defect; carried forward because 32 permanent VIOLATION lines at every session
  entry is signal dilution nobody has quantified for the operator. — harness-orchestrator
- Every other residual from this feature is a GitHub issue (B-2..B-16, #1054..#1068) and is tracked
  there, not here.
