# Research — FEAT-58 — conforming N-13 to the operator's withdrawal (cycle 9)

**Done. N-13's `intent` no longer instructs the withdrawn cycle-8 red proof; the three staging
paragraphs are replaced by one PROHIBITION paragraph carrying the reason, and nothing else in
`plan.yaml` moved.** Written through `plan-merge.py amend --key tasks --id N-13 --field intent`
with `--expect-sha256 e944412b…857bfc6e` (compare-and-swap). New field sha256 of the value:
loaded-intent hash `499c8ce1388d…` (was `87cab02b298d…`).

## Authority

`notes/answers-operator-c9.md` Q1: the cycle-8 instruction to stage the pre-fix
`feature.json`-keyed derivation and record clause 1 reddening on 89-versus-79 "is **wrong and is
hereby withdrawn**"; the pre-fix staging yields `MISSING=[]` / `UNEXPECTED=10` arithmetically,
which clause 1 as PP-03 loosened it *tolerates*; following it would be "an invitation to record a
false red, which is the one outcome worse than no proof at all". Same file: PP-03 and PP-04 were
"each individually correct rulings … that turn out to be jointly unsatisfiable".

## What was removed (3 consecutive paragraphs, end of PART 1)

(a) `THE RED PROOF FOR PART 1, AND IT IS A PASSING CONDITION OF THIS TASK (finding PP-04, operator
ruling Q4)…would be the fourth instance of that pattern.` — removed deliberately: it made a red
proof a *passing condition*, so leaving it would gate N-13 on a proof it no longer instructs.
(b) the staging instruction, whose key sentence was: *"Run PART 1's assertions ONCE against a
STAGED copy of check-state.sh carrying the PRE-FIX feature.json-keyed derivation — git ls-files
over .harness/\*/features/\*/feature.json … and record under the literal heading PART 1 RED PROOF
in your receipt … that clause 1 REDDENED naming the mismatch between the directory count and the
record count (89 versus 79 …). … This task does not pass until that heading exists with a verdict
under it."*
(c) `THE STAGING SPELLING IS CONSTRAINED…asserts the discard notice is absent.` — existed only to
spell (b)'s staging.

**Kept verbatim:** PART 1's four named assertions, `THE TEN RECORD-LESS DIRECTORIES…`, `COST:…`,
all of PART 2, the announced skip, and the discrimination clauses.

## What replaced them

One paragraph, same register, opening `NO RED PROOF LIVES IN THIS TASK, AND ADDING ONE IS
PROHIBITED.` It states the five required facts: no red proof and no staged copy here and none to
be added; the withdrawn cycle-8 instruction named precisely (`ls-files` over
`.harness/*/features/*/feature.json`, the `PART 1 RED PROOF` heading, the 89-versus-79 mismatch)
with its withdrawal cited to `notes/answers-operator-c9.md` Q1; why it cannot work
(`MISSING` empty / `UNEXPECTED` ten arithmetically — 89 dirs, 10 record-less per issue 1640, 79
records bijecting — tolerated by clause 1 under PP-03 and ruled non-gating by N-06 PART 1, so a
FALSE RED); the operator's PP-03/PP-04 jointly-unsatisfiable framing; and the pointer that the
discriminating assertion lives in **N-14** (name-set equality against
`os.listdir(<owner_root>/.harness/harness/features)`, MISSING-producing mutation at N-14 RUN B,
closing H-01 and M-01). Full text: read the field with
`plan-merge.py amend … --id N-13 --field intent --show`.

## Orphan check — clean, no second edit needed

Re-read the whole amended field. Every surviving hit of `feature.json-keyed`, `ls-files`
(first hit), `PART 1 RED PROOF`, `89 versus 79`, `HARNESS_PROJECT_DIR=<owner_root>` is inside the
new PROHIBITION paragraph. The three other `HARNESS_PROJECT_DIR` mentions are PART 1's
*strip-the-override* clauses about the authoritative run — independent of the staging and still
correct. The second `ls-files` hit is PART 2's `git ls-files | grep -c gitconfig` measurement.
The pre-existing `RE-DERIVE, NEVER PIN: no census figure — not 89, not 79` line is a prohibition,
not an instruction. No clause points at "the red proof above" or the removed receipt heading.

## Untouched set, verified at source after the write

- `approval:` byte-identical (canonical hash `18ca8813…785081` before and after), `status:
  approved`, **7 rulings**.
- feature `status: ready`; 13 task ids `N-01..N-10, N-12, N-13, N-14`; 17 decisions.
- Per-task `intent` hashes identical for all twelve other tasks; only N-13 changed.
- `git -C <wt> diff -U0` on the plan: the only hunk at N-13's intent is `@@ -3697,32 +3697,22 @@`.
  The other two hunks (`status: plan → ready` at line 3, and N-14's 164-line addition) predate
  this write — the file was already ` M` before it — and are a sibling's work.
- `check-plan-routes.py <this plan>` exits 0, `0 violation(s)`; the DEVIATION lines are the
  expected DEC-174 main-session-direct carve-outs on every task, unchanged by this edit.
- Field still a literal `|` block at the original 6-space indent, wrapped to the field's existing
  width (max line 87 incl. sub-indented assertion lines, as before).

## Open questions

- **Q1 (non-blocking, do not act):** N-14's intent contains `The staging spelling is the surviving
  one N-13 and N-02 already use`. N-14 is **self-contained** — it spells the staging itself in
  full (copy the whole `.claude/skills/harness/bin` directory, real copies not symlinks, point at
  the subject with `HARNESS_PROJECT_DIR`), so the clause reads as provenance, not as a
  dependency. N-02's spelling also survives. The one now-counterfactual reference is N-14's
  `If you find the cycle-8 note, or N-13 PART 1's RED PROOF paragraph, telling you to stage…` —
  that paragraph no longer exists, but the sentence is conditional and its prohibition remains
  correct, so it misleads nobody. Advisory only; N-14 was not touched.
