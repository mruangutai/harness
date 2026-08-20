# M-13. D-08's baseline was falsified three minutes after it was written. Scope it to FEAT-30.

**Measured twice this run, same command, same checkout:**

    FACTORY_GH=/nonexistent/gh .claude/skills/harness/bin/check-state.sh

    07:41  2 VIOLATIONs — unapproved BRIEFs in FEAT-26 and FEAT-28
    08:07  3 VIOLATIONs — the same two, plus FEAT-31-orchestrator-context-watch

Nothing about FEAT-30 changed between those runs. The main session started another flow, and its
unapproved BRIEF is a third violation.

**So D-08 as written — "check-state.sh reports exactly TWO VIOLATIONs" — is already false, and any
SC-09 `verify:` asserting a violation COUNT will fail for reasons that have nothing to do with this
feature.** It is the same defect class the send-back addendum names: a bare number is unfalsifiable.
A count over a whole-repository scan is worse than unfalsifiable — it is a shared mutable global,
and this repository runs concurrent flows by design, which is the very thing FEAT-30 is building.

**The fix, and it is one clause:** scope the assertion to this feature. Either

    no VIOLATION line whose text contains FEAT-30

or the set difference against the baseline captured at the start of the task, with the foreign
flows named. Both are stable under another flow appearing; a count is not.

**The suite half of D-08 is fine as written** — `--kind unit` and `--kind integration` at zero FAIL
and zero ERROR lines is a property of this checkout's code, not of other flows' approval state.

**FEAT-30's own plan.yaml with `approval.status: pending` produces NO violation**, confirmed in the
08:07 run. That is correct for a plan mission: producing the artifact for signature IS the mission.
