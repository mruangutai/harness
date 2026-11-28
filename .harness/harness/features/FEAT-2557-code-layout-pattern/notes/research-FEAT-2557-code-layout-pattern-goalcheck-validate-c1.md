# Goal-check — FEAT-2557 validate cycle 1 (r-20261127-1-validate-validator)

**BLUF: PASS.** At pin `5c600680e7f46af124fa3281392fa7b25623e982` (base `cf7b422b`), all three
perspectives are discharged, SC-01..SC-06 are met, D-01 → DEC-259 landed as recorded, and all six
`keep` rows still hold. There are two low, non-gating findings: the Layout section carries no
DEC-259 pointer, which DEC-158 move 1 asks for, and DEC-149 has drifted, a defect this feature did
not introduce. Every read below used `git show <pin>:<path>`. The worktree HEAD equals the pin,
and none of the five files has uncommitted changes.

## Perspectives

- **code maintainer: pass.** Carried by SC-01, SC-03 and SC-04. The skill's `## Layout — where a split lands` gives the language-neutral rule, `bin/LAYOUT.md` gives the Python mechanics and both examples, and the AGENTS.md map row and Conventions bullet lead to both.
- **reader: pass.** Carried by SC-02. The `## Applying it` layout bullet names five finding shapes and, for the Harness control plane, the AGENTS.md project map entry, so a reviewer can point at a written rule.
- **operator: pass.** Carried by SC-05 and SC-06. DEC-259 records the convention, its FEAT-69/70 provenance, FEAT-71's removal of the note and the three homes. The non-feature diff is exactly the five files.

## SCs (all `verify: inspection`)

| SC | Verdict | Evidence at pin |
|---|---|---|
| SC-01 | met | SKILL.md `## Layout — where a split lands`. Reads diverge, with a cite to "`harness-craft` › delete-first, 'Put it where its inputs are'". Entry stays put and thin ("only parses and dispatches. No logic stays behind"). Twin package, never flat prefixed siblings. Modules named by reads, not `utils`/`helpers`/`common`, short nouns (`orders/refund`). One home per domain. Moves code unchanged, migrates callers, no re-export shim. "Size is judged in review, never capped". No `bin/`, `.py` or `__init__` in the section. Matches every item in the grilling note's `## Settled` |
| SC-02 | met | SKILL.md `## Applying it`, last bullet "eng-lead at architecture review, code-reviewer at stage two — layout". It names all five findings and the `bin/` check against "the layout entry in AGENTS.md's project map" |
| SC-03 | met | `bin/LAYOUT.md` (21 lines) has a scope line, an Entry/Package table with 2 rows and 2 columns, Naming (hyphenated entry, underscore package, empty `__init__.py`), The entry (docstring, bootstrap, `sys.path`, imports what it dispatches) and Flat modules (`harness_boundary.py`, `harness_merge.py`). It has no "A split" section, catalogue, grade, DEC-174, test-forking, scanner or FEAT text. Every file it names exists at the pin, both `__init__.py` files are 0 bytes, `plan-merge.py` has `sys.path.insert(0, BIN_DIR)` plus `from plan_merge.* import cmd_*`, and `check-state.py` has `from check_state import runner` |
| SC-04 | met | AGENTS.md `## Project map` row "Code layout of Harness `bin/` (entry plus package)" sits after Remaining build ledger. The `## Conventions` first bullet matches the exact text. The LAYOUT.md path occurs once (`grep -cF` = 1) |
| SC-05 | met | DECISIONS.md `## DEC-259 —` (pin line 8758): Chose, Over, Because (FEAT-69 `d8b139de`, FEAT-70 `a98451c5`, FEAT-71 `a41f7cfc`), Tradeoff, Record (D-01, signer). The DECISIONS-INDEX row `DEC-259 @8758 … :: A long file splits…` has a hand-written ruling. `gen-decisions-index.py --stdout` equals the pinned index. `check-decision-anchors.py` reports 25 anchors, 0 failed |
| SC-06 | met | `git diff --name-only cf7b422b <pin>` outside the feature dir lists exactly the five files. `delete-first.md` is unchanged (`git diff --quiet` exit 0). No hook, gate, validator, schema or test file changed |

## Decision dispositions (DECISIONS.md at the pin)

| Row | Verdict | Evidence |
|---|---|---|
| D-01 → DEC-259 | met | Heading at pin line 8758 matches D-01's choice and because. The Record names D-01 |
| DEC-149 keep | met | Clause at 3465 (in section 3462). Added as a section of the existing skill, with no new skill |
| DEC-235 keep | met | Clause at 8000 (in section 7992). The skill stays the folded home; delete-first is cited, not edited |
| DEC-158 keep | met (with a low finding) | Clause at 3804 (in section 3791). History and provenance appear only in DEC-259, and LAYOUT.md and the skill carry none. See F-1 for the pointer half of move 1 |
| DEC-202 keep | met | Clause at 6317 (in section 6282). AGENTS.md gains one pointer row and one pathless bullet, with nothing copied |
| DEC-179 keep | met | Clause at 4851 (in section 4845). T-01 is a declared main-session step, with its order written in the intent |
| DEC-205 keep | met | Clause at 6710 (in section 6708). The DECISIONS.md diff is a pure append; no entry is amended or struck |

## Findings (T-01 owns all five files)

- **F-1 · substance · low · T-01.** DEC-158 move 1 is "Rule + one-clause why + DEC pointer", but the
  new `## Layout` section and its Applying-it bullet point nowhere to DEC-259. Failure scenario: a
  specialist is told "flat prefixed siblings" is a finding and asks why there is no lint. The skill
  gives no route to DEC-259's Over and Because, so they re-propose a cap. Mitigation: the skill's
  other sections also omit DEC pointers, and a grep of DECISIONS-INDEX finds DEC-259. This is
  advisory and does not gate.
- **F-2 · substance · low · T-01 (adjacent; not introduced here).** DEC-149's body says "Doers
  receive it through dispatch prompts, not preload". At the pin, five doers (ai-, backend-, data-,
  frontend-dev and dev-ops) plus product-lead autoload `harness-codebase-design` (`.omp/agents/*.md`).
  DEC-259's Because states the true current fact, so the record now holds two contradictory
  statements. Failure scenario: an auditor trusting DEC-149 drops the skill from a doer's autoload.
  Under DEC-205 this calls for a rewrite of DEC-149 in a separate change. Backlog it; it does not
  gate this feature.

## Notes

- `check-skill-weight.py` at the pin reports eng-lead at 5178 words, up from 4931 at `cf7b422b`,
  against a 5500 cap. It exits 0. This is a non-gating note.

## Principles applied

- Weakest sufficient specification (rule 6, harness-principles): only signed criteria are graded,
  and F-1 and F-2 stay advisory.
