# BRIEF — FEAT-1774 Observations in Hindsight

## Problem

Harness observations are durable on disk but isolated inside one feature tree. A distilling agent can therefore miss lessons it recorded on earlier features or in another repository, while bypassing the disk log to gain broader recall would weaken the committed, reviewable record that gates and audits rely on.

## Done when — by perspective

**operator** — I can rely on every successfully appended observation being both committed to its disk log and available for later shared recall, with a visible failure instead of a half-complete disk write when shared memory is unavailable.

**code maintainer** — I can trace every retained observation to its agent, feature, repository, and date, rerun the historical migration safely, and keep every gate, test, and CI reader on the existing disk record.

**orchestrator** — I can rely on a distilling agent considering both its cross-repository history and the current repository's history before it curates Expertise, without removing that agent's judgment about what deserves promotion.

## Success criteria

- SC-01 (operator): Applying a distinct observation retains the raw bullet synchronously in the untagged shared Hindsight bank with agent, feature, repo, and date metadata and a stable document identity, then writes the normal on-disk union.
  verify: automated        evidence: integration
- SC-02 (operator): If Hindsight is unreachable or rejects the retain, observations-merge exits with its dedicated retention-failure code and leaves the destination log byte-identical; a disk-duplicate record makes no retain request.
  verify: automated        evidence: integration
- SC-03 (code maintainer): The backfill discovers the existing observation corpus, applies the same content, metadata, and stable document identity as live appends, and a second run is safe because the server receives idempotent upserts rather than duplicate documents.
  verify: automated        evidence: integration
- SC-04 (operator): The committed OMP configuration selects Hindsight at http://localhost:8888 with bank ID omp, global untagged scope, and automatic recall and retain disabled, contains no API token, and its checker rejects drift from that contract.
  verify: automated        evidence: integration
- SC-05 (orchestrator): At the pinned review SHA, harness-distill requires the agent to issue one persona-named cross-repository recall and one persona-and-repository-named recall before judging Expertise, and to report recalled and accepted counts for each source in its canonical headline. Inspection must cite the ordered procedure from both recall calls through the first Expertise judgment rather than infer order from literal presence; a recall failure remains visible and gateable through the existing digest verdict, headline, and open-questions contract without suppressing the authoritative disk evidence or prescribing one fixed blocking verdict.
  verify: inspection
- SC-06 (code maintainer): At the pinned review SHA, harness-expertise says both that mid-run recall is available when prior work resembles the current task but is not prescribed, and that observations enter Hindsight only through observations-merge.py rather than the retain tool.
  verify: inspection
- SC-07 (code maintainer): At the pinned review SHA, the feature changes no gate, test, or CI reader to consume Hindsight as authority; observations-merge still writes the disk log and Hindsight remains an additional recall surface.
  verify: inspection

## Verification gaps

none

## Constraints

- observations-merge.py remains Python standard-library only and preserves its locked, order-preserving disk union; Hindsight retention runs within that locked transaction before new bytes are returned.
- HINDSIGHT_API_URL and HINDSIGHT_API_TOKEN are runtime environment overrides; the committed default URL is local, no token is committed, and the writer and OMP configuration use the single bank ID omp without a writer-only bank selector.
- The shared bank is omp, global, and untagged; repository provenance belongs in metadata, not a hard recall filter.
- Disk observation logs remain the authoritative, committed record for every gate, test, and CI reader. Hindsight is permanent granular recall, while Expertise remains the curated layer.
- The already-operated local Docker Hindsight service at http://localhost:8888 is a present-machine prerequisite: its container must mount persistent storage at /home/hindsight/.pg0, report database-backed readiness through /health/ready, and accept a synchronous retain to bank omp before fail-closed observation appends are enabled. A second-machine rollout remains blocked until the separately operated VPS and Tailscale prerequisite exists.
- DEC-23 SUPPLIES the choice-versus-observation boundary; DEC-145 SUPPLIES the hot observation and curated Expertise layers; DEC-199 SUPPLIES the locked union writer and normalized record identity; DEC-202 SUPPLIES OMP as the canonical memory integration surface.

## Out of scope

- Mirroring Expertise, plans, briefs, feature state, run logs, or any artifact other than observation bullets into Hindsight.
- Moving gates, tests, CI, or audit readers from disk to Hindsight, or retiring the disk observation logs.
- Decisions tiering or mirroring; issue #1775 owns that work.
- A mandatory recall at every task start, a repository-hard-filtered recall tool, or a separate bin recall script.
- Provisioning a VPS, Tailscale networking, or a second-machine Harness installation.

## Approval

status: pending
approved-by:
date:
