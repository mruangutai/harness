# Receipt — simplify-append-eng · ALTITUDE angle (harness-ai-dev)

**BLUF:** Empty findings. The post-append readability check sits at the right depth; recommendation: **leave**.

## Reading
- Rule: "the appended record must be the one the durable reader selects". It is enforced in `_append_record` (`.claude/skills/harness/bin/validate-digest.py:1864-1867`) by asking the canonical reader (`_last_record` -> `digest_record.last_fenced_mapping`, :1843-1848) over `text + suffix` BEFORE `target.write`. The check borrows the reader's authority and adds no second fence parser, so there is one authoritative statement and no drift surface.
- Home: `_append_record` is the only place holding both the existing bytes and the exact suffix. A pre-validation seam (e.g. in `check_artifact_file`) has neither, so the check could only live earlier by duplicating the dump. Not a bolt-on to a caller.
- Deeper alternatives all hit settled scope: a live fence parser, closing prose fences, or rewriting history. These are excluded by DEC208/DEC237 and the dispatch.
- Residual: the refusal covers any case where the reader cannot expose `obj`, not only open fences. The message names the open-fence cause, which is the realistic one. Accepted; the guard is the reader's own verdict.
- Guidance: the four SKILL lines (`.claude/skills/harness-handoff/SKILL.md` ~:43-45) are the agent-side counterpart of the refusal, in the contract's own home. They state no rule the validator does not enforce. Leave.
- Tests: three cases in `_append_rule_cases` (`tests/integration/test-validate-digest.py` ~:1586-1592) cross the same writer seam (exit code, bytes unchanged). Leave.

## Findings
None.

| Item | Disposition |
|---|---|
| Check placement in `_append_record` | leave |
| Reuse of `_last_record` as the single authority | leave |
| SKILL guidance lines | leave |
| Refusal message names only open-fence cause | leave |

## Principles applied
- Delete First (read): put it where its inputs are. The check stays in the writer and adds no parser or layer.
