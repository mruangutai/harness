# Operator answers — 2026-09-15-t03-final-eng

## All-role manifest domains

Question: `harness_boundary.run_dir_grant_globs` must inspect run grants across every named role, while the signed `manifest_domains(path, agent)` accessor exposes one role. Should the existing accessor support aggregation, should a second all-role accessor be added, or should this reader be exempted?

Answer: Generalize the existing `manifest_domains` accessor. `agent=None` means aggregate the write-domain globs of every named role into the first returned tuple; shared write-domain globs remain the second returned tuple. Existing agent-specific callers and behavior remain unchanged. Do not add a second accessor, retain raw parsing, or add an exemption.

The board-lifecycle fixture repairs identified during T-03 are implementation work within T-03 and require no separate scope decision.

Approved by: mruangutai
Date: 2026-09-14
