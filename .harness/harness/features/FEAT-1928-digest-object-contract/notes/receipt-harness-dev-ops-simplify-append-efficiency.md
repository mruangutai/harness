# Receipt — simplify-append-eng · EFFICIENCY angle (harness-dev-ops)

**BLUF: no findings.** The pre-write visibility check adds one in-memory re-scan of a single digest.md per lead return, off any hot path. Read-only; no measurements run (timings below are inference).

## Cost grounded in code
- `validate-digest.py:1858-1865` (`_append_record`): `text` is read once (previously `_last_record(target.read())`, same single read — no added I/O). New work: `suffix` build (`safe_dump` of one object), `text + suffix` (one string copy), and a second `_last_record` call.
- `digest_record.py:33-66`: `_fenced_blocks` is one linear `splitlines` pass with a regex per non-fence line; `last_fenced_mapping` iterates `reversed(blocks)` and returns on the first YAML mapping. With the valid suffix last, only the appended block is YAML-parsed; earlier blocks are never loaded. So the added cost is a second linear line scan, not a second full YAML load. [INFERENCE] sub-millisecond to low ms for a digest of hundreds of lines.
- Runs only on the non-idempotent path: `if last == obj: return None` (1862) precedes it, so unchanged-object retries pay nothing extra. Invoked once from `check_artifact_file` (1837) per lead return, not per write or session entry.
- Refusal path occurs before `target.write`, so no wasted write/flush/rollback.

## Not flagged (deliberate)
- Two scans of the same text (pre-existing `_last_record(text)` + new `_last_record(text+suffix)`): could be fused, but only by duplicating parser logic in a boundary function for a negligible saving; contrary to delete-first.
- Test additions (`test-validate-digest.py` three cases in `_append_rule_cases`): same-mechanism cases in an existing table, no new suite run. Full-suite runs are boundary evidence, not waste.
- Handoff SKILL.md: four guidance lines, no runtime cost.

## Principles applied
- Delete First (`references/delete-first.md`, read this run): declined a fused-scan alternative since it would add parser-aware code at the boundary.
