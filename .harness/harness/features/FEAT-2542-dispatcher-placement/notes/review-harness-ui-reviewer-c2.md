# FEAT-2542 — CLI refusal review, panel c2

**PASS — T-01's c1 high substance finding (OQ-1) is closed.** All 22 refusal fixtures passed; all 30 printed command invocations reached the intended disposable registry. No new findings in the changed CLI text.

**Provenance.** Worktree HEAD was `a69f1367922f8f3cc61bcc0eb40fa1b1f57cf1bd`; ran the guard and registry files extracted directly from review pin `2ec0916f8bf6b5d10607e36486ccbeb959ca4822` under `mktemp`, not from HEAD or via the live dispatch hook. Each row below was run twice: with spaces in the fixture root and with spaces plus a literal apostrophe. The latter also exercised spaces and apostrophes in the runtime ID and release feature. `/bin/sh -c` received the exact stderr line; only the ambiguous command's operator placeholders were filled, with shell-quoted values. The command environment pointed at a separate decoy registry containing a claim with the same ID.

| Guard refusal (all exit 2) | Copied commands and evidence, in both path variants |
|---|---|
| `not-found` | Inspect **2**; reports the intended owner root, not the decoy's matching claim. |
| `unreadable`: owner, or linked registry beside a readable match | Inspect **2** in each; names the exact corrupt fixture file. |
| `ambiguous` | Inspect **2**, names both fixture roots; list **0** at each root shows its distinct claim; release **0** removes only the selected linked claim. |
| `persona-mismatch` | Inspect **0**, finds the mismatched claim in its linked root; release **0** removes only that linked claim. |
| `registry-error`: named `UnreadableRegistry`, named `OSError`, pathless `OSError` | Inspect **0** in each, returns the intended owner claim. Fault injection was guard-import-only; these runs prove command routing, not reproduction of the injected exception by the registry CLI. |
| `unreadable`: null with matching or mismatched persona; empty feature | Inspect **0** in each, returns the actual fixture row and its null or empty feature. The guard text identifies the root and malformed row, says to repair in place and never delete, and emits neither a release line nor `--feature None`. |

Inspect/list left fixture and decoy registry bytes unchanged. Both releases left the owner and decoy byte-identical and removed the target from its linked registry. Every command matched the exact shell-quoted argv with `python3` and the resolved sibling script, alone on a four-space-indented line after a colon, with no adjoining prose punctuation (`dispatch-guard.py:764–809,826–859`; amended `plan.yaml:262–271`; SC-02, `BRIEF.md:71–81`). Every Inspect block ended on its own line with the exact narrowed sentence: “A governed lead's dispatch is placed by its own runtime claim (DEC-258); a placement that cannot be established is refused, never silently rebound to the declared feature.”

Open questions: none. Graphical accessibility, theme, focus and layout do not apply to this stderr-only review; terminal wrapping was not assessed.