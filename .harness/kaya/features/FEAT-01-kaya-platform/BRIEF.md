# BRIEF — FEAT-01-kaya-platform Local platform setup

## Problem

Kaya has binding product documents but no runnable application, workspace manifest, or verification runners at code baseline 6303f9f. The operator cannot reproduce a local starting point, obtain a real agent response, or establish that operational state reaches the intended hosted database safely. Subsequent features would otherwise inherit an unverified platform.

## Done when — by perspective

**operator** — I can start from a fresh clone, follow one documented setup sequence, and get a real answer locally. I can observe that the answer's operational state survives restarting the application in the intended hosted project, with failures reported honestly rather than disguised as success.

**code maintainer** — I can reproduce the supported runtime and dependencies, identify the server boundary and operational data ownership, and run meaningful checks before extending the platform. The setup documents tell me what was actually exercised and do not claim that later product features or production operation already work.

## Success criteria

- SC-01 (operator): From a fresh clone at review_sha, the README sequence with its exact Node and pnpm versions and privately supplied settings succeeds: pnpm install --frozen-lockfile, pnpm typecheck, pnpm lint, pnpm test, pnpm build, and pnpm dev. localhost:3000 serves the static Kaya platform landing page with English document language, one main landmark and one descriptive h1 identifying Kaya local platform. The rendered document explains the API/command loop and refers to the repository README as plain text, with no link to an unserved README URL. In both light and dark schemes, native/system colours or approved-system counterparts provide WCAG AA text contrast (4.5:1 normal text, 3:1 large text). At a 320 CSS-pixel viewport and at 200 percent enlarged text, content remains readable and wraps without horizontal document scrolling. The operator records observed versions, command exits and these rendered checks; DOM assertions alone do not prove contrast or overflow.
  verify: uat
- SC-02 (operator): pnpm smoke:live sends an authorized request through the local Next.js route into Mastra and Anthropic and reports PASS only for a nonempty real provider response and an independently recalled, newly stored user/assistant exchange. It reports a safe thread UUID and model identifier without credentials. No canned answer, provider substitution, or mocked network counts; provider/database failures exit nonzero.
  verify: uat
- SC-03 (operator): After stopping and restarting pnpm dev, pnpm smoke:readback <thread-id-from-SC-02> retrieves the saved exchange from Kaya hosted Postgres, including the prior probe nonce, without generating another model response. A missing/mismatched exchange fails nonzero; the probe does not accept process-local state as persistence.
  verify: uat
- SC-04 (operator): pnpm smoke:supabase proves privileged server connectivity to the intended Kaya project and that the mastra schema is unavailable through its Data API. It distinguishes the specific unexposed-schema rejection from permission, authentication, missing-relation, and network errors, and verifies SQL schema/table/default privileges deny PUBLIC, anon, and authenticated. Generic failures do not count as success.
  verify: uat
- SC-05 (code maintainer): Inspection using git show <review_sha>:<path> for .env.example, .gitignore, apps/web server/Mastra entry points, route, Next configuration, and their tests establishes server-only guards, ignored private settings, no secret in client configuration, and denial of missing/wrong bearer authorization before external calls. Behavioral tests cover each missing setting, malformed requests, wrong authorization, provider/database failure, and value redaction; QA supplies red-first and green receipts, not merely test discovery. No real credential is committed, logged, or returned.
  verify: inspection
- SC-06 (code maintainer): Inspection using git show <review_sha>:<path> for workspace manifests, TypeScript configuration, application modules, and test configuration establishes the binding docs/ARCHITECTURE.md Source organization: private root, apps/web, apps/* and packages/* workspace globs, one lockfile, shared strict tsconfig.base.json, app/server/mastra separation, colocated unit/component tests, subsystem __tests__ integrations, and only cross-boundary scenarios in root tests/e2e. There are no empty feature/package scaffolds, app imports into packages, dependency cycles, Turbo/Nx adoption, or package-src aliases bypassing declared exports.
  verify: inspection
- SC-07 (code maintainer): Inspection using git show <review_sha>:<path> for Mastra composition, memory/storage adapter, operational SQL, and their tests establishes explicit PostgresStore schemaName mastra, real conversation memory, server-lifetime/HMR-safe client ownership, certificate verification and bounded pooling. The GET readback path does not call a model. QA exercises schema selection, lifecycle reuse, memory/resource scoping and failure propagation; SC-03 supplies the separate live restart outcome. No financial tables or crash-recovery/exactly-once claims are added.
  verify: inspection
- SC-08 (code maintainer): Inspection using git show <review_sha>:<path> for exact manifests/lockfile, runners, test suites, and .harness/harness.json establishes executable unit, functional, integration, component, and typecheck commands with detect/exclude patterns selecting the actual workspace tests once in their intended kind. Real behavioral assertions, nonzero assertion failure, and zero-selection failure are demonstrated for activated test runners; typecheck demonstrably rejects an actual TypeScript error. QA proves failing states before accepting production behavior. Final pnpm verify:platform exercises all offline suites, typecheck, lint, build, and the real local unauthenticated boundary, without assuming hosted credentials or unfinished successor files.
  verify: inspection
- SC-09 (code maintainer): Inspection using git show <review_sha>:README.md, git show <review_sha>:docs/PLATFORM.md, and git show <review_sha>:docs/platform-compatibility.md finds one complete fresh-clone sequence, the five approved setting names without values, exact pinned and actually exercised versions distinguished from candidates, connection/network/TLS prerequisites, safe success/failure output, schema setup and restart probes, and truthful limits of platform evidence. The instructions do not use latest initialization or authorize a full chat implementation.
  verify: inspection

## Verification gaps

- At code baseline 6303f9f, unit, functional, integration, component, ui, eval, and typecheck all have null cmd. Existing functional/integration detection points to obsolete root tests directories. SC-05 through SC-08 therefore use pinned inspection with required future QA receipts, not unsupported automated claims. T-01 supplies real tooling, T-02 supplies behavioral tests before production, and T-09 serially cuts over the product configuration only after the suites and application exist. Required kinds remain BLOCKED until that cutover and real assertion-failure/zero-selection demonstrations; inspection alone does not waive those implementation gates.
- Component applies to the static page/layout in SC-01 and SC-06/08 and is activated with real render assertions. ui remains null: no interactive user flow is delivered, and HTTP/API probes under tests/e2e are not a browser UI suite. eval remains null: SC-02 proves provider integration, not model-quality/extraction accuracy. These are not unsigned exclusions or invented passing runners; #7 retains the remaining verification gaps.
- T-02 is an intentionally red test-delivery task: its MANUAL verification means QA must inspect and record concrete pre-production behavioral assertion failures before dependents are released, not demand a green cumulative suite from unbuilt production. This carries the fail-first portion of SC-05/07/08 until their implementation gates and final QA receipts exist. Import/command failures alone are not acceptable evidence.
- Live Anthropic access/billing, hosted database connectivity, network reachability and Data API exposed-schema configuration cannot be certified by metadata, offline tests, or a client constructor. SC-01 through SC-04 require the operator personally and remain not_met until user-executed UAT. No live proof is claimed during planning.
- This feature delivers complete project-confirmed Mastra bootstrap, not a general migration-execution contract for Kaya #8.

## Constraints

- Kaya DEC-002 SUPPLIES Mastra inside Next.js server routes; DEC-010 SUPPLIES the existing hosted Kaya Supabase project and @mastra/pg PostgresStore in a separate non-public schema; DEC-011 SUPPLIES Next.js, TypeScript, pnpm and exact package pins. Anthropic and mission plan are operator-settled, not open questions.
- Kaya DEC-000 BLOCKS inherited retired-product requirements; DEC-008 SUPPLIES the authoritative product docs; DEC-009 BLOCKS reopening accepted technologies. docs/ARCHITECTURE.md Source organization is binding, including server-only guards and acyclic dependency direction. A packages/* glob does not require an empty package; create an @kaya/* library only for real behavior/boundary, not speculative financial rules.
- Kaya DEC-012/013 SUPPLY the later chat integration and generative presentation contract. This feature supplies a static server-rendered page and local API/command loop, not chat authorization, streaming, generative renderers, AI Elements, or a parallel AI SDK agent backend. Proposed prototype treatment: no visual prototype for this static/API-only surface; the design reviewer decides whether a prototype is needed before signature.
- Only ANTHROPIC_API_KEY, SUPABASE_PROJECT_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_DB_URL, and KAYA_API_STUB_TOKEN are application setting names. Commit names/empty examples only; local values remain ignored/server-only. The local bearer token is a bounded platform-probe boundary, not the future account/resource authorization model owned by #2.
- Research candidates are Next 16.3.8, @mastra/core 1.74.0, @mastra/memory 1.35.0, @mastra/pg 1.29.0, @ai-sdk/anthropic 3.0.103, @supabase/supabase-js 2.117.2, pg 8.23.1, Node 24 LTS, pnpm 11.2.2 and claude-sonnet-5-5. T-01 must inspect exact-release engine/peer/API constraints and pin compatible supporting packages; installation, compilation, tests and live UAT establish compatibility, not candidate metadata. An integration failure stops affected work within the accepted stack.
- Proposed local connection contract: direct Postgres 5432 where reachable, or the same Kaya project's session pooler 5432 when required by an IPv4-only network. Connection details come privately from that project's dashboard; do not guess credentials or silently fail over. Transaction 6543, global pooling and production recovery remain outside this feature. Verify TLS certificates; make no financial table/access-policy changes.
- Harness DEC-179 requires every exact file route to resolve at plan time; DEC-221 forbids copying the central team manifest into Kaya. Shared/ungranted root configuration, apps/web package/Next/TypeScript configuration, .env.example, and product .harness/harness.json are explicitly serialized main-session-direct tasks. Every implementation edit stays inside the assigned Kaya CODE worktree. Disjoint task file ownership, declared depends_on, predecessor-only local gates, and red-first tests constrain dispatch.
- No approval, panel, mirror, build-entry, product install/build/test, deployment, or credential read is authorized by this planning run. BRIEF and plan remain pending; only main may record an operator signature. Earlier failed research/run receipts remain historical evidence, not current proof.

## Out of scope

- Gmail retrieval, extraction, financial tables, login screens/full chat UI, deployment, queues, and background workers — beyond platform setup; owned by subsequent Kaya work.
- Replacing accepted technologies or closing unrelated spikes wholesale — not authorized by this platform plan.

## Approval

status: pending
approved-by:
date:
