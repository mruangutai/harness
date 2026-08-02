# PENDING DEC — advisor disclosure (staged, NOT yet in the authority)

**Why this is here and not in `DECISIONS.md`:** FEAT-04's `test-gen-decisions-index.py` hardcodes the
authority's counts (170 raw `## DEC-` matches, 169 fence-guarded distinct). Appending a decision
mid-build makes them 171/170 and fails a test on a running feature. So the text is staged here and
lands **with FEAT-04's own regeneration**, in one commit that appends the entry, regenerates the
index, writes the new row's ruling, and re-pins the two counts — which is exactly the standing
obligation FEAT-04 introduces (its Q2). First real exercise of that rule.

Number is provisional: whatever is next when it lands.

---

## DEC-1NN — The advisor is the org's only turn-level independent reviewer; its influence gets disclosed

The user observed that nearly every agent calls the `advisor` tool and asked whether it is needed.
Two facts, both verified:

- It is attached by a **user-level setting** — `advisorModel: opus` at `~/.claude/settings.json:112`
  — not by the harness. **Zero agents declare it in `tools:`.** DEC-155 noted this and called it
  outside the org's authority; that was right about the *setting* and wrong about the *discipline*.
- **Its spend is invisible to the meter.** No `advisor` row exists in any `cost-report.py` block; the
  recorded names are the 16 harness agents plus `Explore`, `fork`, `general-purpose`, `Plan`. Every
  call forwards the agent's full transcript to Opus, and none of it is attributed. Part of every
  reported overrun — FEAT-03's 3.0x, FEAT-04's plan phase at budget — is unattributed by
  construction.

**Considered and rejected: make the LEAD the advisor.** The user's proposal — the lead already holds
the context, so a member should ask it. It fails twice:

1. **Mechanically.** Members hold `[Read, Glob, Grep, Edit, Write, Bash]`; **no agent holds
   `SendMessage` or `Agent`**, so there is no synchronous upward channel by design. A member's only
   route to its lead is its return, so "ask the lead" costs a full spawn round-trip — return with
   `open_questions`, lead reads, re-dispatch — one cycle per question, against an advisor's
   near-zero latency.
2. **Structurally.** The lead authored the dispatch: it chose the approach, wrote the anchors, framed
   the problem. It cannot audit its own framing. The org says so about itself in four Expertise
   entries by different agents — product-lead P-01 *"pre-argued framing is the least trustworthy
   input a lead receives"*, P-03, P-06, G-03. And the one advisor catch on record is exactly that
   class: *"the advisor caught that I had never re-read `statementsFixture.ts`"* (kaya pm, OBS-02) —
   an omission the lead would likely have shared, because the lead handed the anchors down.

**So the advisor's differentiation is real and specific: independence from the dispatch chain.** The
validator squad supplies that at the **run** level; the advisor supplies it at the **turn** level,
where the org has no other mechanism at all. It is kept.

**The defect is not its existence, it is its invisibility.** Everything else in this org passes state
by file path and records what changed a decision; advisor advice is neither recorded nor gated, so a
load-bearing catch is indistinguishable from the agent having thought of it alone. **The rule: an
agent whose decision or verdict changed because of advisor input says so in its DIGEST**, naming what
changed. Same provenance discipline as DEC-138 am.6 — free to comply with, and it turns a fourth
reviewer from invisible into auditable.

**Not decided, deliberately: whether to keep it on.** No cost decision should be made while the meter
is blind. Open questions for whoever picks this up: can `advisorModel` be scoped to the main session
only, and what does one call actually cost? Answer those before trading away catches that have
provably worked.
