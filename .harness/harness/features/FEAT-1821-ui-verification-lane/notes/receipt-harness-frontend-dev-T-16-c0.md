# T-16 receipt — Capture publish traces

T-16 now records Playwright traces for every execution and publishes only manifest-listed, valid replayable ZIP traces through the reporter.

## TDD fail-first evidence

Before production changes, ran:

```sh
node --experimental-strip-types --test .claude/skills/harness/bin/dashboard/client/ui-reporter.probe.spec.ts
```

Exit status: `1`

Verbatim failure summary:

```text
ℹ tests 8
ℹ suites 0
ℹ pass 7
ℹ fail 1
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0

✖ traced record requires a trace attachment
AssertionError: expected /missing trace for desktop-1440\/C1-HEADER-GEOMETRY/; reporter errors contained only missing-record and incomplete-accounting failures.
```

## Signed verification

Ran exactly:

```sh
node --experimental-strip-types --test .claude/skills/harness/bin/dashboard/client/ui-reporter.probe.spec.ts
```

Exit status: `0`

Verbatim final TAP summary:

```text
✔ missing record
✔ duplicate
✔ mismatched title
✔ empty WebP
✔ parser error
✔ reporter error
✔ incomplete accounting
✔ traced record requires a trace attachment
▶ trace attachment failures are named
  ✔ duplicate
  ✔ empty
  ✔ non-ZIP
  ✔ mismatched check
  ✔ mismatched project
✔ trace attachment failures are named
✔ publishes only manifest-listed traces
ℹ tests 15
ℹ suites 0
ℹ pass 15
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 1687.53175
```

The parser-error probe intentionally emits its copied fixture's missing-DESIGN traceback while asserting that reporter failure is serialized; the command nevertheless exited `0`.

## Scope and evidence

- `playwright.config.ts` sets `use.trace: 'on'`.
- `ui-manifest.ts` consumes `traced_check_ids` from the normalized manifest.
- `ui-reporter.ts` validates one native Playwright `trace` attachment per traced applicable record, distinguishes missing/duplicate/empty/non-ZIP/mismatched-check/mismatched-project failures, copies valid ZIP bytes to the required repository-relative path, and omits trace fields/publication for non-listed records.
- `ui-reporter.probe.spec.ts` uses a valid empty ZIP archive (EOCD bytes), verifies distinct committed paths for all applicable selected trace records, and verifies raw non-listed trace attachments are not published.

Files touched:

- `.claude/skills/harness/bin/dashboard/client/playwright.config.ts`
- `.claude/skills/harness/bin/dashboard/client/ui-manifest.ts`
- `.claude/skills/harness/bin/dashboard/client/ui-reporter.ts`
- `.claude/skills/harness/bin/dashboard/client/ui-reporter.probe.spec.ts`

No formatter, linter, build, project-wide suite, sibling proof, prohibited path, dependency, `.gitignore`, FEAT-53 production/source/dist, governance, predicate, or inspection-semantics change was used.
