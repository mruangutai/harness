# FEAT-53 UI contract review — plan cycle 8

## Verdict

**FAIL.** The accepted prototype is sufficient for the prototype gate, and DESIGN.md is unusually concrete and checkable, but the common bundle is not a coherent build contract. The plan still gives builders mutually exclusive pre-ruling UI instructions, while DESIGN.md follows the accepted prototype. DESIGN.md also does not specify the work-list zero-result or request-failure surfaces.

## Findings

1. **substance · high · reader: ui-reviewer** — The plan can rebuild the accepted dashboard into an obsolete composition because its client tasks contradict DESIGN.md and the accepted prototype. **Consequence:** different builders can conform to different signed instructions and ship either attention-first versus KPI-first ordering, a 3×3/spanning KPI grid versus the accepted 4+3 grid, retired `series-1…3` tokens versus KPI identity tokens, and inline sourcing copy versus InfoDisclosure. Evidence: `plan.yaml:519`, `plan.yaml:1199`, `plan.yaml:1230-1232`, `plan.yaml:1936` conflict with `DESIGN.md:163-165`, `DESIGN.md:271-278`, `DESIGN.md:303-314`, `DESIGN.md:387`, `DESIGN.md:403-408`, and the accepted prototype (`src/ui.jsx:325-329`, `src/layout.css`, `observed-1440.png`). The operator-intent record and BRIEF also retain attention-first wording (`grilling-work-dashboard-2026-09-15.md:104-108`; `BRIEF.md:95-101,395-399`) while the accepted prototype and DESIGN put Repository KPIs first and the Status shortcuts at the start of Work List. **Required correction:** reconcile the build-task text and acceptance wording to one hierarchy and one tile/token/disclosure contract, using the immutable accepted prototype as the visual reference; do not modify prototype bytes.

2. **substance · med · reader: ui-reviewer** — DESIGN.md does not define the observable work-list state when filters return zero items or the rendered request/source-failure state. **Consequence:** a compliant implementation may leave an empty table/kanban frame or expose framework-default error output, producing an unreviewable and potentially inaccessible dead end even though `REQ-20` requires a specific visible source error. DESIGN specifies loading only as “a skeleton in the eventual shape” (`DESIGN.md:344-347`) and exhaustively defines KPI absence states, but gives no zero-result work-list copy, reset action/focus outcome, error container, heading, announcement, retry/recovery behavior, or preservation of existing rows. Long reason/path behavior is only partially bounded by wrapping/contained overflow (`DESIGN.md:281-285`). **Required correction:** add checkable zero-result and request/source-error contracts, including message, available recovery action, focus/live-region behavior, and whether stale/partial content remains visible.

## Prototype gate

End-user interaction **requires a prototype**: URL-owned selectors, in-place Status filtering, Kanban/Table switching, inline expansion, disclosure focus management, route focus landing, Back restoration, and pointer-versus-keyboard focus visibility cannot be judged from static prose alone. The existing accepted high-fidelity prototype **satisfies that gate** for the approved dark-only surface. Its README records real-browser observation at 1440×1000 and 1920×1080; both screenshots show the constrained desktop composition; source covers the three product routes plus a fixture-only state gallery. Prototype bytes are immutable. Rendered-size/layout beyond the two supplied observations remains a human/UAT responsibility.

## Accessibility and theme assessment

- Keyboard order, `:focus-visible`, pointer suppression, route-title landing, selector restoration, Back restoration, disclosure semantics, chart text equivalents, status icon-plus-label encoding, and non-colour state carriers are concrete and checkable in DESIGN C-3.
- Accessibility is otherwise strong, but finding 2 leaves error/empty-state announcement and recovery unspecified.
- Dark/light parity is **not applicable**, not omitted: the operator-set contract is explicitly dark-only (`DESIGN.md:10,76-78,374-376,577-586`; fixed by `src/main.jsx`). The dark palette includes measured contrast ratios. Requiring a light counterpart would reopen an approved scope decision.

## States assessed

Specified: loaded; skeleton loading with no partial chart mount; KPI/trend no-record and pre-capability absence; unavailable versus measured zero; unattributed data; active elapsed; partial/all-unmeasured token coverage; horizontal table overflow; responsive KPI/panel layouts; filter selection; inline expansion; route transitions; focus restoration.

Unspecified: zero work-list results; request/API/source failure presentation and recovery; exact handling of exceptionally long status reasons and filesystem paths.

## Plausible concerns assessed and dismissed

- **Prototype needed?** Yes, and satisfied as above; no new prototype is required.
- **Light theme absent:** dismissed because dark-only is an explicit operator ruling and plan constraint, not accidental parity drift.
- **Status conveyed by colour alone:** dismissed; work surfaces require Astryx icon, printed label, and reason, with hue restricted to shortcut labels.
- **Token gaps shown as zero:** dismissed; S-7 pins mixed and all-unmeasured behavior and forbids dollar cost.
- **Wrong routes or hidden `/work`:** dismissed in DESIGN/router/README; product routes are exactly `/`, `/kpi/$n`, `/work/$id`; the fixture route is explicitly non-product and unnavigable.
- **Repository filter duplicated:** dismissed; prototype and DESIGN keep it in the shared header only.
- **Prototype plural copy “1 Items”:** observed in both screenshots and `src/ui.jsx:168`, but dismissed as a prototype-fixture copy blemish rather than a contract finding because the prototype is operator-accepted/immutable and DESIGN does not require that literal.
- **Screenshot-only layout confidence:** bounded, not overclaimed; supplied observations cover 1440 and 1920, while later shipped UI still requires UAT.

## Inspection record

Inspected the exact common bundle: `BRIEF.md`, `plan.yaml`, `DESIGN.md`; operator intent `.harness/notes/grilling-work-dashboard-2026-09-15.md`; prototype `README.md`, `observed-1440.png`, `observed-1920.png`, `package.json`, `.gitignore`, `vite.config.js`, `index.html`, `package-lock.json`, `.smoke/smoke.js`, `dist/index.html`, `dist/assets/index-LDjg9Bo3.js`, `dist/assets/index-_XzjF1xX.css`, `src/smoke.jsx`, `src/layout.css`, `src/ui.jsx`, `src/router.jsx`, `src/theme.js`, `src/fixture.js`, and `src/main.jsx`. No implementation outside that bundle was reviewed. No validation command, build, formatter, linter, or test was run.
