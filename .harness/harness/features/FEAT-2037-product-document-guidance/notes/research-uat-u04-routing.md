# Export routing — scratch research

## Exact answer for verbatim relay

Cannot determine whether export should route through Queue from the assigned product guidance. /tmp/harness-2037-product-c0/docs/architecture.md is missing, and neither docs/spec.md § Export behavior nor docs/decisions.md § Export decision specifies routing. Obtain product architectural guidance or an adopted routing decision before choosing Queue or bypassing it.

## Evidence and guidance gaps

- Missing: /tmp/harness-2037-product-c0/docs/architecture.md; the product docs directory lists only spec.md and decisions.md. Unanswered question: should export route through Queue, and what component relationships govern that route?
- Available but insufficient for routing: /tmp/harness-2037-product-c0/docs/spec.md:3–5 (§ Export behavior) requires EMPTY-PRODUCT-2037 for an empty export; /tmp/harness-2037-product-c0/docs/decisions.md:3–5 (§ Export decision) adopts newline-separated records with marker DECISION-PRODUCT-2037. Neither section defines a route or Queue's role.
- Unresolved: /tmp/harness-2037-product-c0/docs/spec.md:7–9 (§ Retry policy) explicitly leaves retry count unresolved. Unanswered question: what retry count applies? This does not establish a Queue routing requirement.
- Conflict: /tmp/harness-2037-product-c0/docs/spec.md:11–13 (§ Timeout policy) states 5 seconds, while /tmp/harness-2037-product-c0/docs/decisions.md:7–9 (§ Timeout decision) adopts 9 seconds. Unanswered question: which timeout governs? No precedence inferred; this conflict does not settle routing.

## Disposition

Routing recommendation is blocked on missing product guidance. No product files, plans, briefs or run state were changed; no builds, lint, tests or formatters were run, and no assertion is marked passed. Harness documents were not used as product guidance.
