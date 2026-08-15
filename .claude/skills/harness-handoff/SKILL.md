---
name: harness-handoff
description: The universal return contract and output discipline for every harness agent — the three-part VERDICT/DIGEST/artifact return, BLUF writing, pointers not payloads, and when to decide versus ask. Loaded by all 16 agents at every spawn.
user-invocable: false
---

# Handoff

**Handoff is by file path, never by conversation.** You have a fresh context; the agent after you will
too. Write a durable artifact, return a compact signal.

## Your return — three parts, always

````
```yaml
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: <one line, the conclusion — not what you did>
  <your role's fields — see your role rule>
  open_questions:
    - { id: Q1, question: "<text>", blocking: true|false }
  files_touched: [<paths>]        # [] if you changed none
  expertise_update: [<ops>]       # [] except under a distillation dispatch (harness-expertise)
artifact: <path to what you wrote>
```
````

**The ```` ```yaml ```` fence is part of the return, not documentation formatting.** Emit it, and emit
the closing fence. Your return is a YAML document — `VERDICT:` a scalar, `DIGEST:` a mapping,
`artifact:` a scalar — and the fence is what tells the validator where it starts and stops instead of
making it guess from indentation in your prose. You may write prose before or after the fence; the
fenced block is what gets parsed (DEC-172).

| VERDICT | Means |
|---|---|
| `PASS` | done. May carry advisory notes |
| `FAIL` | a gate failed. Retrying or looping back is meaningful |
| `BLOCKED` | cannot proceed. Looping back is futile — escalate |
| `ESCALATE` | needs the tier above (lead → orchestrator → user) |

**These tokens and field names are a contract, not a style.** The runner routes on exact values.
`PASSED`, `severity: medium` instead of `med`, `matrix_ok: "mostly"` — each silently misroutes.
**Every field is required.** Say "nothing" with an explicit `[]` — or `none` for a scalar that is
genuinely inapplicable — never by leaving the key out. An absent field is ambiguous (none found, or
never looked?); an empty one asserts you looked. `bin/validate-digest.py` checks this, and a
violation becomes `BLOCKED (contract violation)`.

**Never invent a verdict.** If you cannot determine one, return `BLOCKED` and say why.

## Writing the artifact

- **BLUF.** Lead with the conclusion or recommendation. Not "I explored X, then Y."
- **Claims plus pointers, never payloads.** "Auth is JWT (`auth/mw.ts:42`)" — never pasted code. The
  reader can open the file; they cannot un-read a wall of it.
- **Call out open questions explicitly.** They are the next agent's to-do list.
- **Bounded — about one screen.** The cap forces you to prioritise. Length is the enemy of signal.

Your artifact is read by the *consumer* of your work. The orchestrator reads only your VERDICT and
DIGEST, so anything the routing decision depends on must be in the DIGEST, not buried in the artifact.

**Where your artifact goes — check your own domain FIRST, and use what you already own.** Most
personas hold a per-feature `notes/` path named for their role: pm writes `notes/research-*.md` or
`notes/uat-*.md`, qa writes `notes/qa-*.md`, each reviewer writes `notes/review-<self>-*.md`, the
visual designer writes under `notes/mockups/` or `notes/prototypes/`. **If you own such a path, your
artifact goes there and you write no receipt.** A dispatch that names a receipt path for you does not
override this — the guard will deny it, correctly (#216).

The receipt is the fallback for the personas that own no other per-feature path — the five engineers
and the documentor. Only those six write
`.harness/harness/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>.md`. **Not your observations log.**
That log is the Expertise hot layer — it is never injected into any spawn, so anything a successor
must read is lost there. Use it only for lessons about *how you work*.

## Decide or ask — scoped by reversibility

| The decision is | Do this |
|---|---|
| cheap and reversible — naming, local structure, test shape | **decide.** Record it in the DIGEST |
| expensive or hard to reverse — schema, API contract, new dependency | **ask** via `open_questions` |
| changes scope, the goal, or an approved decision | **always ask.** It is not yours |

You are not blocked while a question is outstanding: raise it, do what you can, and return. A member
never waits on a human — questions travel up and answers come back down.

## Consulting decisions — cited is a floor, never a ceiling

Decisions named in your dispatch are the **minimum**, not the set. The same framing the qa gate uses
for the test matrix: you may add what the work clearly warrants, never drop below.

**Never read an authority file whole.** Read its index, then open only the entries that bear on your
task — a row is an open-or-skip filter, so open the entry before acting on it.

**Go broader when any of these fires:** (1) a cited decision references an uncited one — the
reference graph is dense, so following it is a lookup, not a judgement call; (2) you are about to
judge something the citations do not cover; (3) your own Expertise implies a rule they omit;
(4) "surely this was decided already" fires.

Nobody who dispatched you can be sure they named every decision that bears on your work — their
framing is a hypothesis, and it is the input most likely to be wrong.

## Red flags

| Thought | Reality |
|---|---|
| "I'll paste the file so they have context" | They have the path. Payloads crowd out signal |
| "I'll describe my process so they can follow it" | They need your conclusion, not your journey |
| "The verdict is unclear, I'll say PASS with caveats" | An unclear verdict is `BLOCKED`. Never guess |
| "I'll use a clearer field name" | Field names are a contract. Clarity is not yours to improve |
| "I should ask about this to be safe" | Reversible? Decide, and record it. Asking has a real cost |
| "I'll just fix this other thing while I'm here" | Out of scope is out of scope. Note it instead |
