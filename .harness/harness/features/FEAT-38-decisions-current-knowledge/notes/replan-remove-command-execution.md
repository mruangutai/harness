# Replanning handoff — remove command execution from the claims checker

**Status: NOT IMPLEMENTED. This note specifies; it changes no code and no plan.** The operator ruled
that no document-driven subprocess risk is acceptable and selected **REMOVE COMMAND EXECUTION**.
That is new scope against an approved plan, so it needs plan and acceptance updates and fresh
security validation before anyone writes a line.

FEAT-38 stays **blocked**. No PR, no merge, no ship.

---

## BLUF — the redesign is small, and the measurement is why

**All eleven live claim markers are `grep` against one named file.** Ten are
`grep -F <literal> <path>`; the eleventh is a capped line count. **Not one of them needs a
subprocess, a shell, or `git`.** Measured at `48bbe7e` — the full list is
`git show 48bbe7e:.harness/harness/docs/DECISIONS.md | grep -n '<!-- claim:'`.

So the replacement is not a reduction in capability. A declarative, in-process assertion vocabulary
covers 11 of 11 markers with **zero** execution surface, and deletes the entire apparatus that the
RCE fix had to build: `ALLOWED_FIRST_TOKENS`, `ALLOWED_GIT_SUBCOMMANDS`, the pager-option rule, the
grep file/device-option rule, the git global-option position rule, `_subprocess_env()`'s ambient-config
neutralisation, and the 10-second timeout.

**The strategic point for the brief:** the current design's safety rests on an allowlist that must
stay ahead of every future `git` release. The proposed design has nothing to keep ahead of, because
it never builds an argv from document text at all. That is a different KIND of assurance, not a
stronger version of the same one.

---

## The proposed design — assert, do not execute

Replace `<!-- claim: <command> :: <expected substring> -->` with a marker naming an **assertion kind**,
a **target path** and an **expected value**. Two kinds cover every live marker:

| Kind | Covers | Semantics |
|---|---|---|
| `contains` | 10 of 11 | read the target file, assert the literal appears in it |
| `max_lines` | 1 of 11 | assert the target file's line count is at or below a bound |

The checker resolves the target path, **reads it**, and compares. No `subprocess`, no `shlex`, no
`shell=True`, no argv assembled from the document. Path resolution must be bounded to the repository
(reuse `harness_boundary`, which is already imported) so a marker cannot name `/etc/passwd` or a path
outside the tree — **that is the one residual risk in the new design and it is an arbitrary-file-READ,
not an execution.** Name it explicitly in the brief rather than letting a reviewer discover it.

Keep the properties that made the current checker honest and that a redesign silently loses:
- **Print the number of markers examined.** A checker that passes over zero markers is
  indistinguishable from one that works. This is the specific way the mechanism dies quietly.
- **A malformed marker is an error, never a non-marker** — keep `CLAIM_LOOKALIKE_RE`.
- **Exit 2 for an unreadable target**, never exit 0. An empty result and a successful result must not
  look the same.
- **Refuse an unknown assertion kind** rather than skipping it. A refusal that skips is a hole that
  looks like a pass.

### One defect to fix while the format is open, not to carry forward

The current expected-value comparison is a **substring** match. On the numeric marker
(`grep -c -m 81 -e "" CLAUDE.md :: 12`) that is only safe by accident — the `-m 81` cap bounds the
output to `[0, 81]`, so `"12"` cannot match a larger number. Remove the accident: `max_lines` should
compare **integers**, not substrings. Do not port substring semantics onto a numeric assertion.

---

## Blast radius — everything that asserts the executing design

Five tracked files outside the feature dir reference the checker
(`git grep -ln check-decision-claims 48bbe7e`):

| File | What must change |
|---|---|
| `.claude/skills/harness/bin/check-decision-claims.py` | the redesign itself |
| `.claude/skills/harness/bin/test-check-decision-claims.py` | 17 marker occurrences; the `python3`-is-refused case becomes an unknown-kind case |
| `.claude/skills/harness/bin/run-unit-tests.sh` | registration only — name may stay if the script keeps its name |
| `.harness/harness.json` | registration only — same |
| `.harness/harness/docs/DECISIONS.md` | 11 markers rewritten to the new grammar, **plus the prose below** |

**Three prose surfaces state the executing design as current truth and become FALSE on the day the
code changes:**

1. **`DEC-205` rule 6b** — states the marker grammar and *"the checker refuses any command whose first
   word is not git or grep and never invokes a shell"*. Authored by T-03.
2. **`D-10` in `plan.yaml`** — the plan decision carrying the same allowlist rationale.
3. **`DECISIONS.md:6290`** — the marker `ALLOWED_FIRST_TOKENS = {"git", "grep"}`, which is
   **self-referential**: it asserts the existence of the very constant the redesign deletes. It will
   go red on the first run after the change, and it is the one marker that must be removed rather
   than translated.

**Plan and acceptance artifacts requiring re-approval** — all approval-gated, none of them mine:

| Artifact | Why it moves |
|---|---|
| `BRIEF.md` REQ-08 | states the executable-claims mechanism |
| `BRIEF.md` SC-09 | its verification is *"runs every claim marker … and exits 0; and when the expected result of DEC-181's `CLAUDE.md` 80-line budget marker is changed to 81, it exits non-zero"* — the mutation still works under the new design, but the wording names a run |
| `plan.yaml` D-10 | the safety boundary is restated, not merely tightened |
| `plan.yaml` T-03, T-20, T-21 | the convention, the checker, the markers |
| `plan.yaml` T-18, T-19 | registration, only if the script is renamed |

---

## Backlog rows this ruling settles

From `notes/ship-review-2026-08-29-18.md` — carry these into the replan rather than filing them:

- **B-8 (hardening the executing checker) becomes MOOT.** Clearing `GIT_CONFIG_*`, routing `git grep`
  through the file-option check, refusing option-like tokens in every position — all describe an
  execution path being deleted. **Do not implement B-8 and then delete it.**
- **B-11 (`ALLOWED_GIT_SUBCOMMANDS` carries no claim marker) becomes MOOT** — the constant goes.
- **B-10 (the DEC entry understates D-10's boundary) is SUPERSEDED** — that prose is being rewritten
  wholesale, not patched.
- **B-9 (sweep the rest of `bin/` for the same shape — any script building an argv from document or
  config text) SURVIVES and is now MORE important**, not less. The ruling is about a class of risk,
  and nobody has checked whether the claims checker was the only instance.

---

## Fresh security validation the replan must require

The redesign is a security change, so the panel must grade the new design on its own terms rather
than re-running the old vectors — that is what caught the last one. Three things to demand:

1. **Prove the executing path is GONE, not merely unreachable.** `grep` for `subprocess`, `shlex`,
   `shell=`, `Popen` in the checker and assert zero. Dead code left in is how a mechanism revives.
2. **Prove the checker can still REDDEN.** Mutate a live marker's expected value and observe a
   non-zero exit naming that marker. An all-green checker is not evidence of an absent defect, and
   this feature has already shipped two gates that passed while discovering nothing.
3. **Probe the residual read surface.** A marker naming a path outside the repository, a symlink
   escaping it, and a `..` traversal — each must be refused, and refused by *position and shape*
   rather than by a blacklist of prefixes.

---

## Open questions for the operator

- **Q1.** Does the marker mechanism survive at all, or does the ruling extend to removing executable
  claims entirely? This note assumes it survives in non-executing form. If it does not, T-20, T-21,
  REQ-08, SC-09 and `DEC-205` rule 6b are deletions rather than rewrites, and the anchor checker
  (T-17) is unaffected either way.
- **Q2.** Are the two assertion kinds (`contains`, `max_lines`) the whole vocabulary, or should the
  replan allow a third for a claim no current marker makes? The measured answer is that two suffice
  today; adding more in anticipation is structure nobody has earned.
- **Q3.** Does the checker keep its filename? Keeping it makes T-18/T-19 untouched; renaming it to
  something that does not say "claims run commands" is clearer but widens the diff.

---

## What was NOT done, and why

**The three operator-signed `verify:` amendments (T-10, T-15, T-19) were NOT applied.** The dispatch
was skipped before it made any edit, so there is no half-applied state — `plan.yaml` is untouched and
`git diff` on it is empty.

I judged the signature no longer coherent to apply as a unit, and it is a unit:

- **T-15 and T-10's amendments are unaffected** by this ruling and remain correct as signed.
- **T-19's is entangled.** The block it amends asserts `PASS test-check-decision-claims.py`, and
  T-18's asserts that script's registration in `harness.json`. Both are in the redesign's blast
  radius, so applying the amendment now writes gate text the replan immediately rewrites.

Applying two thirds of one signature and deferring the third splits it, and the split is exactly the
kind of half-landing that goes unnoticed because each task's own gate stays green. **The signature is
preserved, not withdrawn** — the exact replacement text is still in
`notes/research-verify-block-defects.md`, unmodified, and the replan must carry all three.

**This is a judgement call and it is cheap to reverse.** If the operator wants the three applied to
the current plan regardless, it is one dispatch to `harness-pm` and roughly one run.
