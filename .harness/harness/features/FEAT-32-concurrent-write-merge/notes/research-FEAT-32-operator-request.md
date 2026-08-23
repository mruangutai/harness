# FEAT-32 — three things need your signature

**What this is:** three small corrections to text you already signed for FEAT-32 (the concurrent-write
feature). None of them changes what the feature does. Each one changes a sentence you signed, which is
why they come to you rather than being fixed quietly. They are batched into one request on purpose.

**Recommendations up front:**

| # | Item | Recommendation | Do-nothing available? |
|---|---|---|---|
| 1 | A count in the brief says "seven"; it is eight | Change it to eight | Yes, but the record is wrong |
| 2 | The new lock files would get committed to git | Add one line to `.gitignore` | **No** |
| 3 | Two different YAML readers disagree about what a valid plan file is | Record it as a known limitation, fix it later | **No** |

---

## 1. The brief says "seven measured occurrences". There are eight.

**What breaks.** `BRIEF.md:16` and the plan's T-13 both count occurrences of a recurring defect
(issue #551) and say seven. A later independent measurement found eight. Nothing in the code is
wrong — the number in the record is.

**Why we are confident.** Two independent kinds of evidence. The eighth case is written up by an
author with no stake in the file under suspicion (`runs/2026-08-21-2-product/digest.md:28`), and its
central claim — that the mechanism *demands* a false verdict — was then measured directly against the
validator rather than argued: `bin/validate-digest.py:703` accepts only `PASS`, `FAIL`, `ESCALATE`,
`BLOCKED`, and test digests using `none` or `unknown` were rejected naming exactly that list, while
`PASS` and `BLOCKED` were rejected only for an unrelated missing field. That last pair is the control
— it shows the rejection was about the verdict word, not a broken test.

**Cost to fix.** One word in the brief and one in the plan's T-13 notes.

**Cost of not fixing.** The record understates a recurring problem by one case, and the next person to
count it gets a different answer than the signed document. Low risk, but the record is the thing every
later decision reads.

**Recommendation:** change it to eight.

---

## 2. The new lock files would be committed to the repository. **There is no do-nothing option here.**

**What breaks.** The feature introduces lock files so two writers cannot clobber each other. Four
places create them, and none of them is currently excluded from git — so they would get committed,
and a stale committed lock is exactly the thing that wedges a later write.

**Cost to fix.** One line: `.harness/**/*.lock`. It goes on an existing pending task (T-11, which
already exists to keep the claim registry out of git), and that task's check widens slightly to cover
locks as well as the registry.

**Scope, confirmed exactly.** The four lock locations are the plan file, the per-agent observations
log, both tiers of the expertise files, and the in-flight claims file. All four sit under `.harness/`,
so that single line covers precisely them and nothing else. No collateral.

**Cost of not fixing.** This is the item with no third option. If you decline the `.gitignore` line,
the locks ship uncovered, and the feature's own "here is what we did NOT fix" list (SC-13) has to gain
a statement saying so — which is itself a change to signed text and comes straight back to you.
Declining costs a signature too; it just buys a worse outcome for the same price.

**Recommendation:** add the line.

---

## 3. Two YAML readers disagree about what a valid plan file is. **There is no do-nothing option here either.**

**What breaks.** The harness has one strict, shared YAML reader that rejects a plan file with a
duplicated field. The new plan-merge tool reads YAML with the plain standard library instead, which
*accepts* a duplicated field and silently keeps the last value. So the merge tool can accept a
malformed proposal and write it into a real plan file — and then every other tool in the harness, and
both write-blocking hooks, refuse that file.

**Why it is not urgent.** It fails **closed and loudly**. Nothing is silently corrupted, the signature
block is untouched, and it takes an agent emitting malformed YAML in the first place to trigger. The
damage is a plan file that needs a hand-edit, and confusion about which tool was at fault — the merge
reports success and the *next* tool reports the breakage.

**Why it is not already covered by your signature.** The signed instruction for that task says PyYAML
"is REQUIRED — import it plainly", citing a decision (DEC-171 amendment 1) about the library being a
required dependency rather than an optional one. I checked that decision at source: it is entirely
about the dependency being present, and says nothing about how strictly to parse. So it does not
forbid a stricter reader — but it does not mandate one either, and adding one raises questions your
signed text does not answer, chiefly whether the tool should also start refusing plan files that are
already on disk. That is a real trade-off, so it is yours.

**Cost to fix properly.** A follow-up issue outside FEAT-32: make the merge tool use the shared strict
reader, and decide the on-disk-file question. Small, but it is new work on a task already marked done,
on a feature currently mid-build.

**Cost of not fixing.** Two things, and neither is free:
- The feature ships with a known unfixed limitation, so its "what we did NOT fix" list (SC-13) needs a
  seventh statement — a signed-text change. Same shape as item 2.
- A sentence in already-shipped code is now false. `bin/harness_yaml.py:4-6` states that every other
  module reads YAML through it and never directly. I checked: apart from test files, the new merge tool
  is the only module in the tree that breaks that, so the sentence was true before this feature and is
  false now. Nothing in the harness detects a false statement left standing, so it stays false until
  someone fixes it by hand. One sentence.

**Recommendation:** record it (the seventh statement plus the corrected sentence) and raise the code
fix as a follow-up issue outside FEAT-32. Do not hold the feature for it.

---

## What I am asking you to do

Approve or refuse each of the three. If you approve all three, the changes are: one word in the brief,
one word in the plan, one line in `.gitignore`, one added statement to the feature's limitations list,
one corrected sentence in a code comment, and one new follow-up issue. No behaviour changes.

Not in this request, and not reopened: the SC-14 baseline and the 221 figure — you already declined to
overturn those.

---

*Filename note: this was requested as `operator-request-FEAT-32.md`. The domain guard grants my role
only `notes/research-*.md`, so it is filed here instead of working around the hook.*
