# Observations — harness-orchestrator — BUG-1898-inflight-claim-lifecycle

- 2026-09-25: A lineage oracle that collects every prefix descendant but validates only rows whose immediate lexical parent is governed is fail-open for deeper descendants; selection, persona/parent validation, settlement, and no-row checks must use one identity set.
