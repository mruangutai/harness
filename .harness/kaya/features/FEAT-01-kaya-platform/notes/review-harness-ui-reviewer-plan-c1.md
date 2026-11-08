# Design plan review — FEAT-01 — c1

**FAIL — the static landing is in scope and needs a small checkable document/accessibility contract, not a full product UI. prototype_needed: false.**

Reviewed: plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml. Mode A; code_grade: n_a. Inputs: current unsigned BRIEF/plan, redraft research receipt, original grilling intent, and Kaya binding docs at the supplied code baseline. No implementation, runtime, approval or visual proof is claimed.

## Prototype ruling and proportionality

No end-user browser interaction workflow exists: T-07 (`plan.yaml:214-228`) explicitly excludes client state, chat input, login and generative UI. The operator does interact with README commands and the authenticated API; those are the platform command loop, not an end-user visual interaction design. T-08/T-10 specify command modes, results, safe failures and restart instructions. A high-fidelity visual prototype/user interaction approval is therefore unnecessary for this fixed scope; this is a design-reader ruling, not acceptance of PM's proposed exemption by default. If browser controls or a browser workflow are added, this ruling no longer applies and prototype/user approval is required before building that interaction.

Mission proportionality: the settled plan lane is justified by a new application, authorization boundary and persistent provider/database integration. No task/mission over-build finding: no chat/financial/worker expansion, second visual system or empty packages is proposed. Kaya DEC-012/013 and ARCHITECTURE.md:194-198 distinguish platform integration from later browser chat; do not force Astryx/chat scaffolding into a native static document. Any custom presentation must remain within the accepted visual system, not introduce a replacement.

## Finding — med · substance · scope none

**T-07 and its T-02 render checks leave the static landing's accessibility, theme treatment and overflow acceptance unspecified.** `plan.yaml:228` requires a meaningful heading, explanation and README guidance; T-02's page/layout tests (`plan.yaml:150`) check content/metadata and absence of chat/secrets. BRIEF SC-01 (`BRIEF.md:17`) checks serving the page; SC-08 checks actual render assertions. None specifies semantic document structure/language, native versus authored color treatment in light/dark preferences, or readable reflow. A page made of generic containers, fixed-width guidance or fixed light foreground on a dark background could satisfy those current tests. This is a pre-build contract gap, not an observed shipped accessibility failure.

**Must fix within existing scope:** add a concise static-document baseline to T-07, mirror semantic assertions in T-02, and add rendered acceptance to SC-01 UAT. Specify document language, a main landmark and a single descriptive top-level heading; keep README guidance explicit without inventing a browser route. Declare native/system-color presentation with no custom visual kit, or a small approved-system treatment whose colors have both theme counterparts and WCAG AA text contrast. Define readable wrapping/no horizontal content overflow at narrow viewport and enlarged text. If guidance is a link, pin a real destination, descriptive accessible name and native visible keyboard focus; otherwise explicitly make it plain text instruction. Component tests cover actual semantics/content; operator UAT covers reflow and both color preferences. No separate full DESIGN.md, new presentation dependency, interactive states or extra prototype task is required.

## States, limits and opens

Static content has no item collection, asynchronous browser loading, provider-error panel or state-flip focus management; these are legitimately not applicable. Missing-settings/provider/storage/auth failures belong to the API/CLI contracts already specified, not a landing status dashboard. Only long-content/narrow-width/enlarged-text and theme treatment remain unspecified for this surface. No existing DESIGN.md or prototype was found in the feature search.

Accessibility and theme parity are not certified: there is no implementation yet. Rendered-size/layout not verifiable from source — human or UAT check required. No builds/tests/linters/formatters/live probes were run. Open questions: none. PM can apply this bounded substantive finding in the current reader wave; no form-only re-review is requested.
