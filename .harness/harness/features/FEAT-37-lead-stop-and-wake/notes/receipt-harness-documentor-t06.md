# T-06 receipt — DEC-199's once-only bound corrected in place

**T06_PASS.** `indexdiff=0 bound=0`. Also green after the edit: `--self-check`, `--group playbook`,
`--group coverage`, and `--group bound` with no `--only` (both sites, six cases).

## What changed

One hunk in `.harness/harness/docs/DECISIONS.md`, inside DEC-199 only (heading located by text at
line 6836; entry ends at the next level-two heading, `## DEC-200`). No amendment heading, no dated
note, no reference to the correction having happened — the entry reads in one voice, present tense.

- The three falsified sentences now carry the measured bound inside the same sentence as the
  once-only phrasing: at most once **per consecutive stop sequence**, **re-firing on each later
  wake** while a child is still live. Graded green as `case_occurrence_DECISIONS.md_{6869,6871,6873}`.
- The residual sentence is now honest: an *immediate* second identical return still ships; the
  refusal re-fires only on a later wake.
- One new paragraph subsumes the supporting record in the entry's voice — mechanism (no hook-side
  state: `validate-digest.py:908` returns early on `stop_hook_active`,
  `inflight_registry.py:187` `live_children` only expires stale claims), the discriminating
  evidence compressed to the clause that does the work (two refusals naming different child sets;
  bare pointer `agent-a89be3fd837d1b779`), the consequence, and the one surviving pointer.
  Forensic detail, the platform's block cap, and any statement about the editing were cut per the
  task's survives-or-cut calls.

DEC-201, occurrences 5–8, the merge core, the single-flight registry and the #551 false-reporting
analysis are untouched (`git diff` contains zero `DEC-201` lines).

## Index

**No hand edit.** The committed row at `DECISIONS-INDEX.md:217` asserts no bound — it reads the
locked merge core, single-flight-per-checkout, and #551's dispatch cause closing while its
false-reporting consequences do not. The plan's reading was correct; there was nothing to fix.
Regeneration ran and is required: it moved DEC-200/201/202/203's anchors by +10 and the generator
retagged DEC-199 `brief` → `state` from the new body text. Summary text unchanged.

## One false-at-HEAD claim in the intent, corrected rather than written

The intent's pointer clause says "`inflight_registry.py`'s refusal message **and
`.claude/skills/harness/SKILL.md`** state the same bound." SKILL.md does not.
`grep -nEi 'single-flight|fires at most once|fires once|stop sequence' .claude/skills/harness/SKILL.md`
exits 1 at HEAD `1449c66` — `c5e59aa` deleted that paragraph, exactly as this plan's own D-11
records. I wrote the true form: the pointer names `inflight_registry.py` alone. Its refusal message
at `inflight_registry.py:339-340` does carry the corrected bound (T-04), so that half is verified,
not assumed.
