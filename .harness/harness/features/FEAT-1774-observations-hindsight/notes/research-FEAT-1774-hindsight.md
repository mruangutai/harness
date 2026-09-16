# Research — FEAT-1774 Hindsight observation retention

## Existing seams

- `.claude/skills/harness/bin/observations-merge.py` is the sole observation writer. `cmd_apply` computes `added` records inside `harness_merge.locked_update`; retaining those records inside the transform before it returns preserves the required disk-after-memory ordering and leaves disk unchanged when retention raises.
- Observation identity already uses whitespace-normalized bullet text. Live retention and backfill can share a document identity derived from repo, feature, agent, and that normalized text without changing disk deduplication.
- `tests/integration/test-observations-merge.py` already drives the CLI as a subprocess against legal feature paths. A standard-library HTTP fixture can observe request bodies and inject success, rejection, and unavailable-server outcomes without a live Hindsight service.
- `.omp/config.yml` is already enforced by `check-omp-port.py` and its integration test, so the memory selection belongs in the existing config/checker seam rather than a second validator.

## External contract

- Hindsight retains with `POST /v1/default/banks/{bank_id}/memories`; a request accepts multiple `items`. Each item supports raw `content`, `context`, ISO `timestamp`, arbitrary string `metadata`, and `document_id`. Reusing a document ID performs an idempotent replace. Synchronous responses report `success`, `bank_id`, and `items_count`. Source: https://hindsight.vectorize.io/developer/api/retain
- OMP supports `memory.backend: hindsight`. `HINDSIGHT_API_URL`, `HINDSIGHT_API_TOKEN`, and `HINDSIGHT_BANK_ID` override `hindsight.apiUrl`, `hindsight.apiToken`, and `hindsight.bankId`; the URL default is `http://localhost:8888`, the default bank is `omp`, and `hindsight.scoping: global` uses that bank without tags. Sources: https://github.com/can1357/oh-my-pi/blob/main/docs/environment-variables.md and https://github.com/can1357/oh-my-pi/blob/main/packages/coding-agent/src/hindsight/bank.ts
- OMP defaults both automatic recall and automatic retention on. This feature disables both so explicit observation dual-write is the only retention path and skill-directed recall is the only Harness recall policy. Source: https://github.com/can1357/oh-my-pi/blob/main/docs/environment-variables.md

## Resolved details

- Retain the raw bullet record verbatim; do not prepend the Markdown title. Put provenance in metadata: `agent`, full `feature` identifier, repository segment, and observation `date`.
- Do not force Hindsight's extracted world/experience classification. The retain API accepts raw content and performs extraction; the Harness contract owns provenance, not the server's inferred memory type.
- Use a SHA-256 document ID over a versioned encoding of repo, feature, agent, and the existing normalized record key. The same function is used by live append and backfill.
- Use synchronous `async=false` requests and require both an HTTP success and response `success: true`. Exit 10 is reserved for Hindsight configuration, transport, protocol, or retain failures; diagnostics never print the bearer token.
- Backfill scans `.harness/*/features/{FEAT,BUG}-*/observations/harness-*.md` beneath an explicit control-plane root and sends the same items. Reruns are safe because document IDs upsert.
- Distillation uses two explicit recall queries: one naming the agent across repositories and one naming both agent and current repository segment. The canonical DIGEST has no new field for this evidence, so the existing `headline` reports `recalled/accepted` counts for each source.
