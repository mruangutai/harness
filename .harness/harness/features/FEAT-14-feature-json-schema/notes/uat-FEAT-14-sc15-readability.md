# UAT — FEAT-14 SC-15 — the execution-state file reads as state, in one screen

**Status: ready.** Only the operator can mark it passed. Time to run: about two minutes.

## The criterion, verbatim

> SC-15: The operator, reading the eleven-key file for a mature feature, can tell within one screen
> what state the feature is in — the file reads as execution state, not as a record of what agents
> had on their minds. `verify: uat`

## The file to open

```
.harness/features/FEAT-11-graphql-field-resolve/feature.json
```

**Why this file.** Four reasons, each measured at `cf15660`:

1. **It is the sharpest before/after in the corpus.** Its pre-migration `feature.yaml` carried
   **32 top-level keys**; the file today carries **10**. Twenty-two keys went to
   `notes/receipt-feature-key-drop.md` (`git show acd5d2f^` for the old file).
2. **It is mature.** 16 runs, `cycles_used: 11` against `max_total_cycles: 12` — the state has a
   real answer, not a trivial one.
3. **It is mid-flight, not finished.** `status: "Review"`. A `Done` feature makes the question
   free; a feature in Review is the read that actually has to work.
4. **The operator is already in this feature for SC-10** — the FEAT-11 receipt spot-check opens the
   companion file in the same directory.

**One honest caveat, so the read is not a surprise:** SC-15 says "the eleven-key file". **No file in
the corpus carries eleven keys** — the schema's optional `factory` block is present in zero of the
seventeen, so the maximum instance is ten. FEAT-11 is at that maximum. This is a wording gap in
SC-15, not a defect in the file (SC-01 requires no key *outside* the eleven, and that holds).

## The question to answer — one, and only one

Open the file. Do not open the plan, the digests, `STATE.md`, or the receipt.

> **Reading only this file, and reading it once: what state is FEAT-11 in, and how much of its
> budget has it spent?**

Answer it out loud before scrolling back. Then check yourself against the file:

| What you should have been able to say | Where it is |
|---|---|
| It is in **Review** | `status` |
| On branch `feat/FEAT-11-graphql-field-resolve`, no PR open yet | `branch`, `pr: null` |
| **11 of 12** rework cycles spent — nearly exhausted | `cycles_used`, `max_total_cycles` |
| **16 of 20** runs, and the last one passed | `runs` length + last `verdict`, `max_total_runs` |
| Mirrored to GitHub: milestone 5, parent issue 214 | `github` |

## The verdict you record

- **met** — you answered the question in one pass, without scrolling for context or reading prose
  to work out what a field meant.
- **not_met** — you had to open another file, re-read, or reconstruct the state from narrative.
  If so, name the field that made you do it; that is the fix.

**Do not grade the file on completeness.** "I would also like to know X" is a request for a twelfth
key and is out of scope here — SC-15 asks only whether what is present reads as state.
